"""Configuration module for the ChatBot application."""
from dotenv import load_dotenv

load_dotenv()

# LLM Configuration
LLM_MODEL = "mistralai/mixtral-8x7b-instruct"
LLM_BASE_URL = "https://openrouter.ai/api/v1"

# System Prompt
SYSTEM_PROMPT = """You are a helpful and friendly AI assistant. 
You provide clear, concise, and accurate responses.
Always be respectful and professional."""

# API Configuration
API_TITLE = "ChatBot API"
API_DESCRIPTION = "A simple chatbot API powered by LangChain and FastAPI"
API_VERSION = "1.0.0"
