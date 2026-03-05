# ChatMe - Chatbot API

A refactored chatbot application built with **LangChain** and **FastAPI**, providing a clean, maintainable, and well-documented API for multi-turn conversations.

## Project Structure

```
chatme/
├── main.py          # FastAPI application with API endpoints
├── config.py        # Configuration and settings
├── chatbot.py       # Core ChatBot logic and conversation management
├── requirements.txt # Python dependencies
└── README.md        # This file
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the root directory with your API credentials:

```env
OPENAI_API_KEY=your_api_key_here
```

### 3. Run the Application

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

### Interactive API Docs
Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints

#### 1. Health Check
```
GET /
```
Check if the API is running.

**Response:**
```json
{
  "status": "ok",
  "message": "ChatBot API is running"
}
```

#### 2. Send a Message
```
POST /chat
```
Send a message to the chatbot and get a response.

**Request:**
```json
{
  "message": "siapa kamu?"
}
```

**Response:**
```json
{
  "response": "Saya adalah asisten AI yang helpful dan friendly..."
}
```

#### 3. Get Conversation History
```
GET /history
```
Retrieve the entire conversation history.

**Response:**
```json
{
  "history": [
    {
      "role": "user",
      "content": "siapa kamu?"
    },
    {
      "role": "assistant",
      "content": "Saya adalah asisten AI..."
    }
  ]
}
```

#### 4. Clear Conversation History
```
POST /clear
```
Clear the conversation history.

**Response:**
```json
{
  "message": "Conversation history cleared"
}
```

## Usage Examples

### Using cURL

```bash
# Health check
curl http://localhost:8000/

# Send a message
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "siapa kamu?"}'

# Get history
curl http://localhost:8000/history

# Clear history
curl -X POST http://localhost:8000/clear
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Send a message
response = requests.post(
    f"{BASE_URL}/chat",
    json={"message": "apa kabar?"}
)
print(response.json())

# Get history
history_response = requests.get(f"{BASE_URL}/history")
print(history_response.json())

# Clear history
clear_response = requests.post(f"{BASE_URL}/clear")
print(clear_response.json())
```

## Architecture

### ChatBot Class (`chatbot.py`)
- Encapsulates all conversation logic
- Manages conversation history
- Provides clean interface for chat operations

### Configuration (`config.py`)
- Centralized configuration management
- Easy to modify LLM settings, prompts, and API settings
- Environment-based configuration support

### FastAPI Application (`main.py`)
- RESTful API endpoints
- Input validation using Pydantic models
- Error handling and HTTP exception management
- Auto-generated API documentation

## Benefits of This Architecture

✅ **Modularity** - Separate concerns (config, chatbot logic, API)  
✅ **Maintainability** - Easy to modify and extend  
✅ **Scalability** - Ready for production deployment  
✅ **Documentation** - Auto-generated API docs with Swagger UI  
✅ **Testing** - Easy to unit test individual components  
✅ **Reusability** - ChatBot class can be used independently  

## Customization

### Change the LLM Model
Edit `config.py`:
```python
LLM_MODEL = "your-model-name"
LLM_BASE_URL = "your-api-base-url"
```

### Modify System Prompt
Edit `config.py`:
```python
SYSTEM_PROMPT = "Your custom system prompt here"
```

### Add More Endpoints
Add new functions in `main.py` with the `@app.get()` or `@app.post()` decorators.

## Technologies Used

- **LangChain** - LLM framework for conversation management
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **python-dotenv** - Environment variable management