from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["https://ai-find-chat.vercel.app"]

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from routes import verify_gmail, verify_telegram, search

app.include_router(verify_gmail.router)
app.include_router(verify_telegram.router)
app.include_router(search.router)
