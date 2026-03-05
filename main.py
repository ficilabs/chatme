"""FastAPI application for the ChatBot."""
import uuid
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
from chatbot import ChatBot
from config import API_TITLE, API_DESCRIPTION, API_VERSION

# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION
)

# Session store: maps session_id -> ChatBot instance
sessions: dict[str, ChatBot] = {}


def get_or_create_session(session_id: Optional[str]) -> tuple[str, ChatBot]:
    """
    Get existing session or create a new one.

    Args:
        session_id: Optional session ID from request header

    Returns:
        Tuple of (session_id, ChatBot instance)
    """
    if session_id and session_id in sessions:
        return session_id, sessions[session_id]

    # Create new session
    new_id = str(uuid.uuid4())
    sessions[new_id] = ChatBot()
    return new_id, sessions[new_id]


# Request/Response Models
class MessageRequest(BaseModel):
    """Request model for chat messages."""
    message: str


class MessageResponse(BaseModel):
    """Response model for chat messages."""
    response: str
    session_id: str


class HistoryResponse(BaseModel):
    """Response model for conversation history."""
    history: list
    session_id: str


# Health check endpoint
@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "ChatBot API is running"}


# Chat endpoint
@app.post("/chat", response_model=MessageResponse, tags=["Chat"])
def chat(
    request: MessageRequest,
    x_session_id: Optional[str] = Header(default=None)
):
    """
    Send a message to the chatbot and get a response.
    Provide X-Session-Id header to continue an existing conversation.
    If omitted, a new session is created automatically.

    Args:
        request: The message request containing the user's message
        x_session_id: Optional session ID from request header

    Returns:
        The chatbot's response along with the session_id to use in future requests

    Raises:
        HTTPException: If the message is empty
    """
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    session_id, chatbot = get_or_create_session(x_session_id)

    try:
        response = chatbot.chat(request.message)
        return MessageResponse(response=response, session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


# Clear history endpoint
@app.post("/clear", tags=["Chat"])
def clear_history(x_session_id: Optional[str] = Header(default=None)):
    """
    Clear the conversation history for a session.
    If no session ID is provided, does nothing.
    """
    if not x_session_id or x_session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    sessions[x_session_id].clear_history()
    return {"message": "Conversation history cleared", "session_id": x_session_id}


# Get history endpoint
@app.get("/history", response_model=HistoryResponse, tags=["Chat"])
def get_history(x_session_id: Optional[str] = Header(default=None)):
    """Get the conversation history for a session."""
    if not x_session_id or x_session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    history = sessions[x_session_id].get_history()
    formatted_history = [
        {
            "role": "user" if msg.__class__.__name__ == "HumanMessage" else "assistant",
            "content": msg.content if hasattr(msg, "content") else str(msg)
        }
        for msg in history
    ]
    return HistoryResponse(history=formatted_history, session_id=x_session_id)


# Delete session endpoint
@app.delete("/session", tags=["Chat"])
def delete_session(x_session_id: Optional[str] = Header(default=None)):
    """Delete a session and free its memory."""
    if not x_session_id or x_session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    del sessions[x_session_id]
    return {"message": "Session deleted", "session_id": x_session_id}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)