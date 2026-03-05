"""FastAPI application for the ChatBot."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from chatbot import ChatBot
from config import API_TITLE, API_DESCRIPTION, API_VERSION

# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION
)

# Initialize ChatBot instance
chatbot = ChatBot()


# Request/Response Models
class MessageRequest(BaseModel):
    """Request model for chat messages."""
    message: str


class MessageResponse(BaseModel):
    """Response model for chat messages."""
    response: str


class HistoryResponse(BaseModel):
    """Response model for conversation history."""
    history: list


# Health check endpoint
@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "ChatBot API is running"}


# Chat endpoint
@app.post("/chat", response_model=MessageResponse, tags=["Chat"])
def chat(request: MessageRequest):
    """
    Send a message to the chatbot and get a response.
    
    Args:
        request: The message request containing the user's message
        
    Returns:
        The chatbot's response
        
    Raises:
        HTTPException: If the message is empty
    """
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    try:
        response = chatbot.chat(request.message)
        return MessageResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


# Clear history endpoint
@app.post("/clear", tags=["Chat"])
def clear_history():
    """Clear the conversation history."""
    chatbot.clear_history()
    return {"message": "Conversation history cleared"}


# Get history endpoint
@app.get("/history", response_model=HistoryResponse, tags=["Chat"])
def get_history():
    """Get the conversation history."""
    history = chatbot.get_history()
    formatted_history = [
        {
            "role": "user" if hasattr(msg, "content") and msg.__class__.__name__ == "HumanMessage" else "assistant",
            "content": msg.content if hasattr(msg, "content") else str(msg)
        }
        for msg in history
    ]
    return HistoryResponse(history=formatted_history)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)