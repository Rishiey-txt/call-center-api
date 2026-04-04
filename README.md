# Call Center Compliance API

> GUVI × HCL Hackathon — Track 3 Submission

## Description

An intelligent call center analytics API that processes Hindi (Hinglish) and Tamil (Tanglish) voice recordings. The system runs a multi-stage AI pipeline: speech-to-text via OpenAI Whisper, NLP analysis via Gemini 1.5 Flash, SOP compliance scoring, payment intent classification, and transcript indexing via ChromaDB.

## Live API

```
Base URL: https://your-app.up.railway.app
Endpoint: POST /api/call-analytics
Auth:     x-api-key header
```

## Tech Stack

| Component | Technology |
|---|---|
| Web framework | FastAPI (Python 3.11) |
| Async task queue | Celery 5 + Redis |
| Speech-to-Text | OpenAI Whisper (`medium` / `large-v3`) |
| NLP / LLM | Google Gemini 1.5 Flash |
| Vector store | ChromaDB + sentence-transformers multilingual |
| Database | PostgreSQL + SQLAlchemy async |
| Deployment | Railway.app |

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your-username/call-center-api
cd call-center-api
```

### 2. Install dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Set environment variables

```bash
cp .env.example .env
# Edit .env — set API_KEY, GEMINI_API_KEY, DATABASE_URL, REDIS_URL
```

### 4. Start infrastructure (Docker)

```bash
docker-compose up redis postgres -d
```

### 5. Run migrations

```bash
alembic upgrade head
```

### 6. Run the application

```bash
# Terminal 1: FastAPI server
uvicorn src.main:app --reload --port 8000

# Terminal 2: Celery worker (optional with CELERY_TASK_ALWAYS_EAGER=true)
celery -A celery_worker worker --loglevel=info
```
