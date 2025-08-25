import os
import json
import redis
from celery import chord
from dotenv import load_dotenv
from pydantic import BaseModel
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from sentence_transformers import SentenceTransformer
from .celery_config import celery_app
from .models import store_messages
from .vault_encryption import batch_encrypt


BATCH_SIZE = 500
EMBEDDING_BATCH = 64

model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

redis_client = redis.Redis(host="redis", port=6379, db=3)


class Messages(BaseModel):
    user_id: str
    messages: list[str]


load_dotenv()


api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")


@celery_app.task(bind=True, queue="telegram_process")
def process_telegram_messages(self, batch: dict):

    batch = Messages(**batch)

    if not batch.messages:
        return {"status": "error", "error": "No message found"}

    try:
        encrypted = batch_encrypt(batch.messages, "chat-msg")

        vectors = model.encode(
            batch.messages, batch_size=EMBEDDING_BATCH, show_progress_bar=False
        )

        docs = [
            (batch.user_id, encrypted[i], vectors[i].tolist())
            for i in range(len(batch.messages))
        ]

        print(f"Batch processing completed: {len(batch.messages)} messages processed")

        print(f"Storing messages...")

        store_messages(docs)

        print(f"Messages stored successfully")

        return {"status": "success"}
    except Exception as e:
        print(f"Batch processing failed: {e}")
        self.retry(exc=e, countdown=60)


@celery_app.task(bind=True, queue="telegram_process")
def telegram_done(self, results, user_id: str):
    print(f"Telegram processing done for user {user_id}")
    redis_client.publish(
        "task_updates",
        json.dumps({"user_id": user_id, "task": "telegram", "status": "SUCCESS"}),
    )


async def fetch_telegram_messages(user_id: str, session_string: str):

    print(f"Fetching messages for user {user_id}")

    messages = []

    async with TelegramClient(
        StringSession(session_string), api_id, api_hash
    ) as client:

        async for dialog in client.iter_dialogs():
            if dialog.is_user or dialog.is_group or dialog.is_channel:
                async for message in client.iter_messages(dialog.id, limit=100):
                    if hasattr(message, "text") and message.text:
                        messages.append(message.text)

    chunks = [messages[i : i + BATCH_SIZE] for i in range(0, len(messages), BATCH_SIZE)]

    group_tasks = [
        process_telegram_messages.s({"user_id": user_id, "messages": chunk})
        for chunk in chunks
    ]

    chord(group_tasks)(telegram_done.s(user_id))

    return {"status": "processing_started"}
