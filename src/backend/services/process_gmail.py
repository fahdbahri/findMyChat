from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from more_itertools import chunked  # pip install more-itertools
from .gmail_tasks import fetch_gmail_messages
from .progress_tracker import progress
import asyncio

BATCH_SIZE = 100  # You can increase this if embedding API allows

async def process_gmail(access_token: str, user_id: int):
    str_user_id = str(user_id)
    credentials = Credentials(token=access_token)
    service = build("gmail", "v1", credentials=credentials, cache_discovery=False)
    
    message_ids = []
    next_page_token = None

    while True:
        results = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: service.users().messages().list(
                userId="me", maxResults=500, pageToken=next_page_token
            ).execute(),
        )
        messages = results.get("messages", [])
        message_ids.extend(messages)
        next_page_token = results.get("nextPageToken")
        if not next_page_token:
            break

    progress[str_user_id] = {"total": len(message_ids), "processed": 0, "done": False}

    chunks = list(chunked(message_ids, BATCH_SIZE))
    for chunk in chunks:
        for message in chunk:
            msg_id = message["id"]
            fetch_gmail_messages.delay(msg_id, access_token, user_id)

