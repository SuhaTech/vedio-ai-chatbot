# Video RAG Chatbot (YouTube + Instagram)

Full-stack RAG chatbot that ingests two URLs (YouTube + Instagram Reel), extracts transcript and metadata, computes engagement rate, stores transcript chunks in a vector DB, and supports streaming comparative chat with memory and citations.

## Stack

- Frontend: React + Vite
- Backend: FastAPI
- Orchestration: LangChain
- Embeddings: OpenAI `text-embedding-3-small`
- Vector DB: ChromaDB (local)
- LLM: OpenAI `gpt-4o-mini`
- Transcript: `youtube-transcript-api` + `yt-dlp` caption fallback

## Features

- Ingest two URLs dynamically (Video A = YouTube, Video B = Instagram)
- Extract metadata:
  - views, likes, comments, creator, follower count, hashtags, upload date, duration
- Compute engagement rate:
  - `(likes + comments) / views * 100`
- Chunk + embed transcript and store in ChromaDB with metadata tags
- Streaming chat responses over SSE
- Source citations in each answer (`video_id` + `chunk_index`)
- Conversation memory across turns (session-based in backend)

## Folder Structure

- `backend/` FastAPI + LangChain + Chroma
- `frontend/` React app with side-by-side cards + chat panel

## Quick Start

## 1) Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Set real keys inside `.env`.

Run backend:

```bash
uvicorn app.main:app --reload --port 8000
```

## 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

Open: `http://localhost:5173`

## API Endpoints

- `POST /api/ingest`
  - body:
  ```json
  {
    "youtube_url": "https://www.youtube.com/watch?v=...",
    "instagram_url": "https://www.instagram.com/reel/..."
  }
  ```

- `POST /api/chat`
  - body:
  ```json
  {
    "question": "Why did video A get more engagement?",
    "session_id": "demo-session"
  }
  ```
  - streaming `text/event-stream` with events:
    - `{ "type": "token", "token": "..." }`
    - `{ "type": "done", "citations": [...] }`

## Important Notes

- Instagram transcripts/captions availability depends on public caption tracks. If unavailable, test with reels that expose captions.
- For production scale, move memory to Redis and vector DB to managed Qdrant/Pinecone.
- Add async ingestion queue (Celery/RQ/SQS workers) for higher throughput.

## Suggested Demo Script

1. Start backend + frontend.
2. Paste one YouTube + one Instagram Reel URL.
3. Show parsed metadata and engagement rates.
4. Ask:
   - Why A performed better than B?
   - Compare first 5 second hooks.
   - Who is creator of B and follower count?
   - Improvements for B based on A.
5. Show citations and multi-turn memory.
