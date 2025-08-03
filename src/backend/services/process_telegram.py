import os
from dotenv import load_dotenv
from requests import session
from pydantic import BaseModel
from typing import List, Optional
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import asyncpg
from langchain_google_genai import GoogleGenerativeAIEmbeddings


# embedding using langchain
# encrpt the message
# store the message
# use backgroun


class Message(BaseModel):
    message: str
    embedded_message: list


load_dotenv()

google_api_key = os.getenv("GEMINI_API_KEY")
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001", google_api_key=google_api_key
)


api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")


conn = asyncpg.connect(
    host=os.getenv("POSTGRES_HOST"),
    database=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)


async def fetch_telegram_messages(user_id: int, session_string: str):

    print(
        f"Fetching messages for user {user_id} using the sessions string {session_string}"
    )

    async with TelegramClient(
        StringSession(session_string), api_id, api_hash
    ) as client:

        async for dialog in client.iter_dialogs():
            print(dialog)
            if dialog.is_user or dialog.is_group or dialog.is_channel:
                print(dialog.entity)
                async for message in dialog.iter_messages(dialog.id, limit=10):
                    print("printing the messages: {message}")
                    message = Message(
                        message=message.text,
                        embedded_message=embeddings.embed_query(message.text),
                    )
                    print(message)
                    # await store_messages(user_id, message.text, message.embedded_message)


async def store_messages(user_id: int, message: str, embedded_message: list):

    async with conn.cursor() as cur:
        await cur.execute(
            "INSERT INTO messages (user_id, message, embedded_message) VALUES (%s, %s, %s)",
            (user_id, message, embedded_message),
        )

        await cur.commit()
