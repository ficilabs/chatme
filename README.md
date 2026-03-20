# ChatMe API v4

Portfolio chatbot API powered by **LangChain**, **FastAPI**, and **Upstash Redis**.

## Project Structure

```
chatme/
├── main.py                   # App init, middleware, router registration (~50 lines)
├── chatbot.py                # Stateless LLM wrapper (LangChain)
│
├── core/
│   ├── config.py             # All settings (env-var overridable)
│   ├── session_store.py      # Upstash Redis store + in-memory fallback
│   └── dependencies.py       # FastAPI Depends() providers
│
├── routers/
│   ├── chat.py               # POST /chat  GET /history  POST /clear
│   ├── session.py            # GET /session  DELETE /session
│   └── health.py             # GET /  GET /stats
│
├── schemas/
│   └── chat.py               # All Pydantic request/response models
│
├── services/
│   └── chat_service.py       # Business logic (LLM call, session ops, hooks)
│
├── tests/
│   └── test_chat_service.py  # Unit + API smoke tests
│
├── nginx/
│   └── nginx.conf            # Rate limiting, TLS, CORS headers
│
├── Dockerfile                # Multi-stage production build
├── docker-compose.yml        # API + Nginx stack
├── requirements.txt
└── .env.example
```

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
# Fill in OPENAI_API_KEY, UPSTASH_REDIS_URL, UPSTASH_REDIS_TOKEN
```

### 3. Run (development)
```bash
python main.py
# or
uvicorn main:app --reload
```

### 4. Run (production)
```bash
docker compose up -d --build
```

API available at `http://localhost:8000`  
Swagger docs at `http://localhost:8000/docs`

---

## API Endpoints

| Method   | Path       | Description                              |
|----------|------------|------------------------------------------|
| `GET`    | `/`        | Health check + Redis status              |
| `GET`    | `/stats`   | Active sessions, store type              |
| `POST`   | `/chat`    | Send message, get reply                  |
| `GET`    | `/history` | Get conversation history                 |
| `POST`   | `/clear`   | Clear history, keep session alive        |
| `GET`    | `/session` | Session metadata                         |
| `DELETE` | `/session` | Delete session permanently               |

All session endpoints require `X-Session-Id` header.  
`POST /chat` creates a new session automatically if no header is sent.

---

## Session Flow

```
1. POST /chat  (no header)
   → Response: { "response": "...", "session_id": "abc-123" }

2. POST /chat  (X-Session-Id: abc-123)
   → Bot remembers previous messages

3. GET /history  (X-Session-Id: abc-123)
   → Full conversation log

4. DELETE /session  (X-Session-Id: abc-123)
   → Session removed from Redis
```

---

## How to Add a New Feature

### Add a new endpoint
1. Create `routers/your_feature.py` with an `APIRouter`
2. Add business logic in `services/your_service.py`
3. Add schemas in `schemas/your_schema.py`
4. Register in `main.py`: `app.include_router(your_feature.router)`

### Swap the LLM
Edit `chatbot.py` — `ChatService` and all routers are unaffected.

### Add RAG retrieval
In `services/chat_service.py`, the `send_message()` method has a marked
hook comment — inject your retriever there. Nothing else needs to change.

### Add authentication
Create a `core/auth.py` with a `Depends()` function, then add it to any
router that needs protection. The service layer stays untouched.

---

## Running Tests

```bash
pytest tests/ -v
```