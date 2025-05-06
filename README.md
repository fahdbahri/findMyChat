# AI Podcast Search Engine

A search engine that finds relevant podcast episodes from YouTube based on transcript content.

## Features
- Search YouTube podcast episodes by content (not just titles/metadata)
- Real-time transcript analysis using TF-IDF and cosine similarity
- Embedded video playback for matched results
- SQLite database for caching transcripts

## How It Works
1. **Backend** (Python/Flask):
   - Uses YouTube API to fetch video metadata
   - Extracts transcripts using YouTubeTranscriptAPI
   - Implements search using sklearn's TF-IDF vectorizer and cosine similarity
   - Serves results via REST API (see `backend/app.py` and `backend/youtube_services.py`)

2. **Frontend** (React):
   - Real-time search input with debouncing
   - Displays matching videos with embedded players
   - Clean, responsive UI with dark theme

## Why I Built This
Traditional podcast search only looks at titles/descriptions. This project:
- Enables deep content search within podcast episodes
- Demonstrates practical NLP techniques (TF-IDF, text similarity)
- Provides better discovery for long-form audio content

## Setup
1. Install backend dependencies:
```bash
pip install -r backend/requirements.txt
```

2. Set up frontend:
```bash
cd frontend/podcast
npm install
npm start
```

3. Add YouTube API key to `.env` file

## Tech Stack
- Python (Flask, sklearn)
- React.js
- SQLite
- YouTube Data API