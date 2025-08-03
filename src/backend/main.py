from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from routes import verify_gmail, verify_telegram
app.include_router(verify_gmail.router)
app.include_router(verify_telegram.router)


