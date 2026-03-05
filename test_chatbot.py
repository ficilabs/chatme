"""
Unit tests for the ChatBot class.
Run with: python -m pytest test_chatbot.py
"""
import pytest
from chatbot import ChatBot


def test_chatbot_initialization():
    """Test ChatBot initialization."""
    bot = ChatBot()
    assert bot.conversation_history == []
    assert bot.system_prompt is not None


def test_chat_adds_to_history():
    """Test that chat messages are added to history."""
    bot = ChatBot()
    initial_length = len(bot.conversation_history)
    
    # Send a message (will need API key)
    # response = bot.chat("test message")
    
    # After chat, history should have at least 2 messages (user + assistant)
    # assert len(bot.conversation_history) > initial_length


def test_clear_history():
    """Test clearing conversation history."""
    bot = ChatBot()
    bot.clear_history()
    assert bot.conversation_history == []


def test_get_history():
    """Test getting conversation history."""
    bot = ChatBot()
    history = bot.get_history()
    assert isinstance(history, list)
    assert history == []


if __name__ == "__main__":
    print("Run with: python -m pytest test_chatbot.py -v")
