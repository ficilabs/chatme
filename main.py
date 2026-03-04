from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

load_dotenv()

llm = ChatOpenAI(
    model="mistralai/mixtral-8x7b-instruct",
    base_url="https://openrouter.ai/api/v1"
)

system_prompt = """You are a helpful and friendly AI assistant. 
You provide clear, concise, and accurate responses.
Always be respectful and professional."""

# Initialize conversation memory
memory = ConversationBufferMemory()

# Create conversation chain with memory
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    system_prompt=system_prompt
)

# Chat history for multi-turn conversation
def chat(user_input):
    response = conversation.invoke({"input": user_input})
    return response["response"]

# Example conversation
print(chat("siapa kamu?"))
print(chat("apa nama kamu?"))
print(chat("apa yang kami bicarakan tadi?"))