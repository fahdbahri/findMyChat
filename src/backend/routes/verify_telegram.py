import os
import asyncio
import redis
import json
import uuid
import redis
from fastapi import APIRouter, BackgroundTasks, WebSocket, WebSocketDisconnect
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import APIRouter
from telethon import TelegramClient
from telethon.sessions import StringSession
from services.process_telegram import fetch_telegram_messages
from services.models import store_user_phone

load_dotenv()

router = APIRouter(prefix="/auth/telegram")

api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")

redis_client = redis.Redis(host="redis", port=6379, db=3)


class PhoneRequest(BaseModel):
    phone: str


class ConfirmRequest(BaseModel):
    user_id: str
    session_id: str
    code: str


@router.post("/start")
async def telegram_start(data: PhoneRequest):

    session_id = str(uuid.uuid4())
    print(f"Telegram API ID: {api_id}")
    print(f"Telegram API Hash: {api_hash}")
    print(f"Phone number: {data.phone}")
    client = TelegramClient(StringSession(), api_id, api_hash)
    await client.connect()
    result = await client.send_code_request(data.phone)
    phone_code_hash = result.phone_code_hash
    string_session = client.session.save()
    session_data = {
        "phone": data.phone,
        "session_string": string_session,
        "phone_code_hash": phone_code_hash,
    }
    redis_client.setex(f"telegram_session:{session_id}", 600, json.dumps(session_data))

    await client.disconnect()
    return {"status": "code_sent", "session_id": session_id}


@router.post("/confirm")
async def telegram_confirm(data: ConfirmRequest, background_tasks: BackgroundTasks):

    try:

        session_json = redis_client.get(f"telegram_session:{data.session_id}")
        if not session_json:
            return {"status": "error", "error": "Session not found"}

        session_data = json.loads(session_json)

        print(f"User id: {data.user_id}")
        print("Confirm request received")
        print(f"Phone number: {session_data['phone']}")
        print(f"OTP code: {data.code}")

        await asyncio.sleep(3)

        client = TelegramClient(
            StringSession(session_data["session_string"]), api_id, api_hash
        )
        await client.connect()
        if not (await client.is_user_authorized()):

            await client.sign_in(
                phone=session_data["phone"],
                code=data.code,
                phone_code_hash=session_data["phone_code_hash"],
            )
            session_string = client.session.save()
            print(f"Session string: {session_string}")
            store_user_phone(session_data["phone"], data.user_id)
            background_tasks.add_task(
                fetch_telegram_messages, data.user_id, session_string
            )
            redis_client.delete(f"telegram_session:{data.session_id}")
            await client.disconnect()
            return {
                "status": "authinticated",
                "redirect_url": f"http://ai-find-chat.vercel.app/loading?user_id={data.user_id}",
            }

        print(f"user_id: {data.user_id}")

    except Exception as e:
        print(f"Telegram error: {e}")
        print(f"Telegram error")


@router.websocket("/task-status")
async def task_status(ws: WebSocket):
    await ws.accept()
    pub_sub = redis_client.pubsub()
    pub_sub.subscribe("task_updates")

    try:
        while True:
            msg = pub_sub.get_message(ignore_subscribe_messages=True)
            if msg:
                print(msg["data"].decode())
                await ws.send_text(msg["data"].decode())
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    finally:
        pub_sub.close()
