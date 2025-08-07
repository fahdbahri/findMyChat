import os
from dotenv import load_dotenv
from requests import session
from pydantic import BaseModel
from typing import List, Optional
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import asyncpg
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
from sentence_transformers import SentenceTransformer
from .celery_config import celery_app
from .models import store_messages
from .vault_encryption import batch_encrypt

# embedding using langchain
# encrpt the message
# store the message
# use backgroun

BATCH_SIZE = 1000  # Smaller batches for Celery
EMBEDDING_BATCH = 64  # More conservative for worker memory

model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

class Messages(BaseModel):
    user_id: str
    messages: list[str]


load_dotenv()


api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")


@celery_app.task(bind=True, queue='telegram_fetch')
def process_telegram_messages(self, batch: dict):

    batch = Messages(**batch)

    if not batch.messages:
        return {"status": "error", "error": "No message found"}

    try:
        # Batch encrypt
        encrypted = batch_encrypt(batch.messages, "chat-msg")


        vectors = []
        for i in range(0, len(batch.messages), EMBEDDING_BATCH):
            vectors.extend(model.encode(batch.messages[i:i+EMBEDDING_BATCH], show_progress_bar=False))


        print(f"Batch processing completed: {len(batch.messages)} messages processed")

        print(f"Storing messages...")

        store_messages([(batch.user_id, encrypted, vec.tolist()) for vec in vectors])

        print(f"Messages stored successfully")
        return {"status": "success"}
    except Exception as e:
        print(f"Batch processing failed: {e}")
        self.retry(exc=e, countdown=60)





async def fetch_telegram_messages(user_id: str, session_string: str):

    print(
        f"Fetching messages for user {user_id}"
    )

    async with TelegramClient(
        StringSession(session_string), api_id, api_hash
    ) as client:

        async for dialog in client.iter_dialogs():
            if dialog.is_user or dialog.is_group or dialog.is_channel:
                messages = []
                async for message in client.iter_messages(dialog.id, limit=100):
                    if hasattr(message, "text") and message.text:
                        messages.append(message.text)

                for i in range(0, len(messages), BATCH_SIZE):
                    batch = Messages(user_id=user_id, messages=messages[i:i+BATCH_SIZE])
                    process_telegram_messages.delay(batch.dict())


    return {"status": "processing_started"}

                    



