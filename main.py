from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()

llm = ChatOpenAI(
    model="mistralai/mixtral-8x7b-instruct",
    base_url="https://openrouter.ai/api/v1"
)

system_prompt = """You are ChatMe, a friendly and intelligent AI assistant.
Your name is ChatMe. You were created to help users with all kinds of questions.
IMPORTANT: You MUST always respond in Bahasa Indonesia (Indonesian language). 
Never respond in Dutch, English, or any other language. Only Bahasa Indonesia.
Give detailed, personal, and enthusiastic answers.
Remember the context of previous conversations and refer back to them when relevant."""

# Conversation history for multi-turn conversation
conversation_history = []

def chat(user_input):
    """Send a message and get a response while maintaining conversation history."""
    # Add user message to history
    conversation_history.append(HumanMessage(content=user_input))
    
    # Create messages list with system prompt + full history
    messages = [SystemMessage(content=system_prompt)] + conversation_history
    
    # Get response from LLM
    response = llm.invoke(messages)
    
    # Add assistant response to history
    conversation_history.append(AIMessage(content=response.content))
    
    return response.content

# Example conversation
print("User: siapa kamu?")
print("Bot:", chat("siapa kamu?"))
print()

print("User: apa nama kamu?")
print("Bot:", chat("apa nama kamu?"))
print()

print("User: apa yang kami bicarakan tadi?")
print("Bot:", chat("apa yang kami bicarakan tadi?"))