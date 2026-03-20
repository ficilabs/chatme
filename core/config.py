"""Centralized settings — all values are env-var overridable."""
import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM ──────────────────────────────────────────────────────────────────────
LLM_MODEL        = os.getenv("LLM_MODEL",        "mistralai/mixtral-8x7b-instruct")
LLM_BASE_URL     = os.getenv("LLM_BASE_URL",     "https://openrouter.ai/api/v1")
LLM_TEMPERATURE  = float(os.getenv("LLM_TEMPERATURE", "0.7"))
LLM_MAX_TOKENS   = int(os.getenv("LLM_MAX_TOKENS",    "1024"))

# ── Upstash Redis ─────────────────────────────────────────────────────────────
UPSTASH_REDIS_URL   = os.getenv("UPSTASH_REDIS_URL",   "https://flying-hawk-77949.upstash.io")
UPSTASH_REDIS_TOKEN = os.getenv("UPSTASH_REDIS_TOKEN", "gQAAAAAAATB9AAIncDJjNGE4NzU4MmU2NmU0ZTBkOTcwZDZiOWE3ZTFiNDM5OHAyNzc5NDk")
SESSION_TTL_SECONDS  = int(os.getenv("SESSION_TTL_SECONDS",  str(60 * 60)))
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "50"))

# ── API ───────────────────────────────────────────────────────────────────────
API_TITLE       = "ChatMe API"
API_DESCRIPTION = "Portfolio chatbot API powered by LangChain, FastAPI, and Upstash Redis"
API_VERSION     = "4.0.0"

# ── CORS ──────────────────────────────────────────────────────────────────────
_raw            = os.getenv("ALLOWED_ORIGINS", "")
ALLOWED_ORIGINS = [o.strip() for o in _raw.split(",") if o.strip()] or ["*"]

# ── System Prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are FICI AI, the intelligent portfolio assistant for Moh Rofiqi.

Your role is to help visitors understand Moh Rofiqi's career, projects, skills,
education, and professional experience through conversation on his website or platform.

IMPORTANT RULES
- You are not a generic AI assistant.
- You represent Moh Rofiqi and his professional portfolio.
- Always speak about Moh Rofiqi in third person.
- All factual information about Moh Rofiqi comes from the provided context retrieved
  from the knowledge base or vector database.
- Never invent or guess information. If information is not available in the provided
  context, say that it is not available in Moh Rofiqi's portfolio data.

BEHAVIOR
When visitors ask questions:
- About projects    → explain the project clearly: purpose, tech used, outcomes.
- About skills      → summarize technical and professional abilities.
- About education   → describe educational background and areas of study.
- About experience  → explain professional background and work history.
- About hiring      → encourage visitors to contact Moh Rofiqi.

IDENTITY
If a visitor asks "Who are you?" respond:
"I am FICI AI, the AI assistant for Moh Rofiqi. I help visitors explore his
projects, skills, education, and professional experience."

STYLE: Professional · Friendly · Clear and concise · Helpful for recruiters.
"""