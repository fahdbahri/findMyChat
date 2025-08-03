# services/gmail_tasks.py
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os
import base64
from .celery_config import celery_app
from bs4 import BeautifulSoup
from .vault_encryption import encrypt_value
from services.models import store_message
from googleapiclient.http import BatchHttpRequest
from more_itertools import chunked
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from elasticsearch import Elasticsearch, helpers
from datetime import datetime

load_dotenv()

es = Elasticsearch('http://elasticsearch:9200')

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001", google_api_key=os.getenv("GEMINI_API_KEY")
)


def extract_plain_text(html_content: str) -> str:
    """Extract plain text from HTML content"""
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator="\n", strip=True).replace("\n", " ")


def extract_message_body(payload):
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
                return extract_message_body(part)
    elif payload.get("body") and payload["body"].get("data"):
        html = base64.urlsafe_b64decode(payload["body"]["data"]).decode()
        return extract_plain_text(html)
    return ""


@celery_app.task(name="services.gmail_tasks.fetch_gmail_messages", queue="fetch")
def fetch_gmail_messages(msg_id, access_token, user_id):
    """Main task to fetch all Gmail messages and create processing chunks"""
    try:
        credentials = Credentials(token=access_token)
        service = build("gmail", "v1", credentials=credentials, cache_discovery=False)

        message_ids = []
        next_page_token = None

        # Fetch all message IDs
        while True:
            results = service.users().messages().list(
                userId="me", maxResults=500, pageToken=next_page_token
            ).execute()
            message_ids.extend(results.get("messages", []))
            next_page_token = results.get("nextPageToken")
            if not next_page_token:
                break

        print(f"Found {len(message_ids)} messages for user {user_id}")

        # Process in chunks
        chunks = list(chunked(message_ids, 100))
        for chunk in chunks:
            process_messages.delay(chunk, access_token, user_id)

        return f"Queued {len(chunks)} chunks for processing"
        
    except Exception as e:
        print(f"Error in fetch_gmail_messages: {e}")
        raise


@celery_app.task(name="services.gmail_tasks.process_messages", queue="process")
def process_messages(msg_chunk, access_token, user_id):
    credentials = Credentials(token=access_token)
    service = build("gmail", "v1", credentials=credentials, cache_discovery=False)

    bodies, raw_messages = [], []

    for msg in msg_chunk:
        try:
            message = service.users().messages().get(
                userId="me", id=msg["id"], format="full"
            ).execute()
            body = extract_message_body(message.get("payload", {}))
            if body and 10 < len(body) < 36000:
                encrypted = encrypt_value(body, "chat-msg")
                bodies.append(body)
                raw_messages.append((user_id, encrypted))
        except Exception as e:
            print(f"Error fetching message {msg['id']}: {e}")

    if bodies:
        embedded = embeddings.embed_documents(bodies)
        batch_data = [(uid, enc, emb) for (uid, enc), emb in zip(raw_messages, embedded)]
        store_messages.delay(batch_data)
    else:
        print("No valid messages in this chunk.")


@celery_app.task(name="services.gmail_tasks.store_messages", queue="store")
def store_messages(batch_data):
    """Store processed messages in Elasticsearch"""
    try:
        actions = [
            {
                "_index": "messages_index",
                "_source": {
                    "user_id": user_id,
                    "encrypted_message": encrypted_message,
                    "embeddings": embeddings_vector,
                    "created_at": datetime.utcnow().isoformat()
                }
            }
            for user_id, encrypted_message, embeddings_vector in batch_data
        ]

        if actions:
            helpers.bulk(es, actions)
            print(f"✅ Stored {len(actions)} messages in Elasticsearch")
        else:
            print("No messages to store")
            
    except Exception as e:
        print(f"❌ Bulk index failed: {e}")
        raise
