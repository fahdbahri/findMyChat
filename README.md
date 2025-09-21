# Semantic Search Histiry Chat


### Platform where you can search all over your messages in one place (Gmail, Telegram)

#### The idea is to be able to search across all of your messages using human like typing and the platform being able to understand it.

#### Your phone, email and your messages are being encrypted.

## The Architecture


<img width="7630" height="4853" alt="findChat" src="https://github.com/user-attachments/assets/74a591eb-f9c8-494d-bf9a-d7c7b8b8b521" />



## 🚀 Local Development Setup

This project has two main parts:

- **Frontend (React app)** – for the UI
- **Backend (FastAPI + Celery + Redis + Vault + Elasticsearch)** – for the core logic and workers

### 1️⃣ Clone the repository

```bash
git clone https://github.com/fahdbahri/findMyChat.git
cd findMyChat/src
```

Your structure should look like this:
```bash
src/
 ├── backend/
 └── frontend/
```
2️⃣ Environment Variables

Frontend (frontend/.env)
```bash
Copy code
VITE_REACT_APP_CLIENT_ID=<google-oauth-client-id>
VITE_API_URL=http://localhost:8000   # or production API URL
```
Backend (backend/.env)
```bash
GOOGLE_CLIENT_ID=<your-google-client-id>
GOOGLE_CLIENT_SECRET=<your-google-client-secret>
TELEGRAM_API_ID=<your-telegram-api-id>
TELEGRAM_API_HASH=<your-telegram-api-hash>
GEMINI_API_KEY=<your-gemini-api-key>

# Vault
GOOGLE_APPLICATION_CREDENTIALS=/vault/config/vault-sa.json   # for auto-unseal
VAULT_ADDR=http://vault:8200
VAULT_API_ADDR=http://vault:8200
VAULT_TOKEN=<vault-root-token>

# Services
ELASTICSEARCH_URL=http://elasticsearch:9200
CELERY_BROKER_URL=redis://redis:6379
CELERY_RESULT_BACKEND=redis://redis:6379

# Optional
CLOUDFLARED_TOKEN=
```

3️⃣ Start the Backend (Docker Compose)
Move into the backend folder and run:

```bash
cd backend
docker build -t backendsearch:latest .
docker compose up --build
```

This will start:

```bash
Elasticsearch (port 9200)

Kibana (port 5601) – optional UI for Elasticsearch

Vault (port 8200) – for secure encryption of emails/phone numbers

Redis – for caching sessions & Celery broker

Backend (FastAPI) (port 8000)

Celery workers – one for Gmail, one for Telegram
```

You can verify services with:
```bash
docker ps
```

4️⃣ Start the Frontend (React)
Move into the frontend folder and run:

```bash
cd frontend
npm install
npm run dev
```

This starts the React app (default on http://localhost:5173).

Make sure the VITE_API_URL in your frontend/.env points to the backend (http://localhost:8000).

5️⃣ Access the App

```bash
Frontend: http://localhost:5173

Backend API: http://localhost:8000/docs (FastAPI Swagger UI)

Kibana: http://localhost:5601

Vault: http://localhost:8200
```

🛠️ Tech Stack
Frontend: React + Vite

Backend: FastAPI + Celery

Vector Search: Elasticsearch

Embeddings/AI: Transformers + Gemini

Security: Vault (encryption & token management)

Infra: Redis (cache + broker), Docker Compose

🔒 Notes on Security
Phone number & email are encrypted using Vault and never decrypted back.

Login works by hashing the email and comparing with stored hash.

Chat messages (Telegram/Gmail) are decrypted only in real time for semantic search.
