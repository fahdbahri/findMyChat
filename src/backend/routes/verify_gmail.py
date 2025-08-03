from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import RedirectResponse
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import httpx
import os
from dotenv import load_dotenv
from services.process_gmail import process_gmail
from services.process_telegram import fetch_telegram_messages
import psycopg2
from services.models import hash_email, user_email_lookup, store_user_email
from services.models import setup_indices
from services.vault_encryption import decrypt_value
 

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

router = APIRouter(prefix="/auth/gmail")

router = APIRouter()


@router.get("/auth/callback")
async def auth_callback(code: str, background_tasks: BackgroundTasks):

    token_url = "https://oauth2.googleapis.com/token"


    try:

        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": "http://localhost:8000/auth/callback",
                "grant_type": "authorization_code"
            })

            response.raise_for_status()
            tokens = response.json()

        access_token = tokens['access_token']

        gmail_service = build('gmail', 'v1', credentials=Credentials(access_token))
        user_info = gmail_service.users().getProfile(userId='me').execute()
        user_email = user_info['emailAddress']

        print(f"User email: {user_email}")

        hashed_email = hash_email(user_email)
        print(f"Hashed email: {hashed_email}")

        # creating the database if not exist 
        
        setup_indices()

        
       # get the encrypted email, and phone

        user_id = user_email_lookup(hashed_email)

        print(f"User id: {user_id}")



        if user_id is not None:


            return RedirectResponse("http://localhost:5173/home")


        else:

            store_user_email(hashed_email, user_email)
            user_id = user_email_lookup(hashed_email)

            print(f"User id: {user_id}")

            
            background_tasks.add_task(process_gmail, access_token, user_id)
            print("redirecting to telegram auth")

            return RedirectResponse(f"http://localhost:5173/telegram-auth?user_id={user_id}")
        
    except Exception as e:
        print(e)




