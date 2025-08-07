from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from sentence_transformers import SentenceTransformer
from .vault_encryption import batch_encrypt
from .models import store_messages
from .celery_config import celery_app
import os
import time

# Constants
BATCH_SIZE = 1000  # Smaller batches for Celery
EMBEDDING_BATCH = 64  # More conservative for worker memory

model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')

def extract_plain_text(html_content: str) -> str:
    """Extract plain text from HTML content"""
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator="\n", strip=True).replace("\n", " ")


def extract_message(payload):
    """Extract message body from Gmail API payload"""
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain":
                return base64.urlsafe_b64decode(
                    part["body"]["data"].encode("ASCII")
                ).decode("utf-8")
            elif part["mimeType"] == "text/html":
                html = base64.urlsafe_b64decode(
                    part["body"]["data"].encode("ASCII")
                ).decode("utf-8")
                return extract_plain_text(html)
            elif "parts" in part:
                return extract_message(part)
    elif payload.get("body") and payload["body"].get("data"):
        html = base64.urlsafe_b64decode(payload["body"]["data"]).decode()
        return extract_plain_text(html)
    return ""

@celery_app.task(bind=True, queue='gmail_fetch')
def fetch_message_ids(self, access_token: str, user_id: str):
    """Fetch all message IDs and trigger processing tasks"""
    creds = Credentials(token=access_token)
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    
    all_ids = []
    next_page = None
    while True:
        try:
            results = service.users().messages().list(
                userId="me",
                maxResults=500,
                pageToken=next_page
            ).execute()
            all_ids.extend(msg["id"] for msg in results.get("messages", []))
            next_page = results.get("nextPageToken")
            if not next_page:
                break
        except Exception as e:
            print(f"Fetch error: {e}")
            time.sleep(5)
            continue
    
    # Split into chunks and process
    processed_count = 0
    for chunk in [all_ids[i:i+BATCH_SIZE] for i in range(0, len(all_ids), BATCH_SIZE)]:
        processed_count += process_message_batch(service, chunk, user_id)
    
    return {"total": len(all_ids)}

def process_message_batch(service, msg_ids: list[str], user_id: str):
    """Process a batch of messages"""
    
    bodies = []
    for msg_id in msg_ids:
        try:
            msg = service.users().messages().get(
                userId="me",
                id=msg_id,
                format="full",
                metadataHeaders=None
            ).execute()
            body = extract_message(msg.get("payload", {}))
            if 10 < len(body) < 30000:
                bodies.append(body)
        except Exception as e:
            print(f"Failed to process message {msg_id}: {e}")
            continue
    
    if not bodies:
        return {"processed": 0}

    try:
        # Batch encrypt
        encrypted = batch_encrypt(bodies, "chat-msg")
        
        # Batch embed
        vectors = []
        for i in range(0, len(bodies), EMBEDDING_BATCH):
            vectors.extend(model.encode(bodies[i:i+EMBEDDING_BATCH], show_progress_bar=False))
        
        # Prepare data
        batch_data = [(user_id, enc, vec.tolist()) for enc, vec in zip(encrypted, vectors)]
        
        # Store
        if store_messages(batch_data):
            return {"processed": len(batch_data)}
        return {"processed": 0}
        
    except Exception as e:
        print(f"Batch processing failed: {e}")
        self.retry(exc=e, countdown=60)
