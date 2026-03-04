from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

llm = ChatOpenAI(
    model="mistralai/mixtral-8x7b-instruct",
    base_url="https://openrouter.ai/api/v1"
)

system_prompt = """You are a helpful and friendly AI assistant. 
You provide clear, concise, and accurate responses.
Always be respectful and professional."""

# Conversation history for multi-turn conversation
conversation_history = []

def chat(user_input):
    """Send a message and get a response while maintaining conversation history."""
    # Add user message to history
    conversation_history.append(HumanMessage(content=user_input))
    
    # Create messages list with system prompt
    messages = [SystemMessage(content=system_prompt)] + conversation_history
    
    # Get response from LLM
    response = llm.invoke(messages)
    
    # Add assistant response to history
    conversation_history.append(response)
    
    return response.content

# Example conversation
print(chat("siapa kamu?"))
print(chat("apa nama kamu?"))
print(chat("apa yang kami bicarakan tadi?"))