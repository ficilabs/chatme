"""ChatBot module for handling conversations with LLM."""
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from config import LLM_MODEL, LLM_BASE_URL, SYSTEM_PROMPT


class ChatBot:
    """A chatbot class that manages conversations with an LLM."""
    
    def __init__(self, model: str = LLM_MODEL, base_url: str = LLM_BASE_URL, 
                 system_prompt: str = SYSTEM_PROMPT):
        """
        Initialize the ChatBot with an LLM and system prompt.
        """
        self.llm = ChatOpenAI(model=model, base_url=base_url)
        self.system_prompt = system_prompt
        self.conversation_history = []
    
    def chat(self, user_input: str) -> str:
        """
        Send a message and get a response while maintaining conversation history.
        
        Args:
            user_input: The user's message
            
        Returns:
            The assistant's response
        """
        # Add user message to history
        self.conversation_history.append(HumanMessage(content=user_input))
        
        # Create messages list with system prompt
        messages = [SystemMessage(content=self.system_prompt)] + self.conversation_history
        
        # Get response from LLM
        response = self.llm.invoke(messages)
        
        # Add assistant response to history
        self.conversation_history.append(response)
        
        return response.content
    
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []
    
    def get_history(self) -> list:
        """
        Get the conversation history.
        
        Returns:
            List of messages in the conversation history
        """
        return self.conversation_history
