
import os
from fastapi import APIRouter, BackgroundTasks
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from telethon import TelegramClient 
from telethon.sessions import StringSession
from services.process_telegram import fetch_telegram_messages
from services.models import store_user_phone, hash_email

load_dotenv()

router = APIRouter(prefix="/auth/telegram")

api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")

class PhoneRequest(BaseModel):
    phone: str

class ConfirmRequest(BaseModel):
    user_id: tuple
    phone: str
    code: str
    phone_code_hash: str

@router.post("/start")
async def telegram_start(data: PhoneRequest):
    print(f"Telegram API ID: {api_id}")
    print(f"Telegram API Hash: {api_hash}")
    print(f"Phone number: {data.phone}")
    client = TelegramClient(StringSession(), api_id, api_hash)
    await client.connect()
    result = await client.send_code_request(data.phone)
    phone_code_hash = result.phone_code_hash
    await client.disconnect()
    return {"status": "code_sent", "phone_code_hash": phone_code_hash} 

@router.post("/confirm")
async def telegram_confirm(data: ConfirmRequest):
    if data.user_id is not int:
        data.user_id = int(data.user_id[0])
    print("Confirm request received")
    print(f"Phone number: {data.phone}")
    print(f"OTP code: {data.code}")

    
    
    client = TelegramClient(StringSession(), api_id, api_hash)
    await client.connect()
    if not client.is_user_authorized():
         
        await client.sign_in(data.phone, data.code, data.phone_code_hash)
        session_string = client.session.save()
        print(f"Session string: {session_string}")
        store_user_phone(data.phone, data.user_id)
        await fetch_telegram_messages(data.user_id, session_string)
        await client.disconnect()
        return {
            "status": "authenticated",
            "session_string": session_string
        }

    print(f"user_id: {data.user_id}")

    return RedirectResponse("http://localhost:5173/home")


