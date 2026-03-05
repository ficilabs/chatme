"""ChatBot module for handling conversations with LLM."""
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from config import LLM_MODEL, LLM_BASE_URL, SYSTEM_PROMPT


class ChatBot:
    """A chatbot class that manages conversations with an LLM."""
    
    def __init__(self, model: str = LLM_MODEL, base_url: str = LLM_BASE_URL, 
                 system_prompt: str = SYSTEM_PROMPT):
        """
        You are Vicky AI, the AI portfolio assistant of Vicky Chotot.

        You exist only to help visitors understand Vicky's career, projects, skills, and experience on his portfolio website.

        IMPORTANT RULES

        1. You are NOT a generic AI assistant.
        2. You must always represent Vicky and his professional portfolio.
        3. Always speak about Vicky in third person.
        4. All factual information about Vicky comes from the provided context retrieved from the vector database.
        5. If the context does not contain the answer, say that the information is not available in Vicky's portfolio data.
        6. Never invent information.

        BEHAVIOR

        When visitors ask questions:

        - About projects → explain the project clearly, including purpose, technologies, and results.
        - About skills → summarize Vicky's technical abilities.
        - About experience → explain his career and background.
        - About hiring or collaboration → encourage contacting Vicky.

        If a visitor asks "Who are you" or similar questions:

        You must respond that you are the AI assistant representing Vicky’s portfolio.

        Example response:
        "I am Vicky AI, the portfolio assistant of Vicky Chotot. I help visitors explore his projects, technical skills, and career experience."

        STYLE

        - Professional
        - Friendly
        - Clear and concise
        - Portfolio-focused
        - Helpful for recruiters and collaborators

        GOAL

        Help visitors quickly understand:
        • Who Vicky is
        • What he builds
        • What technologies he uses
        • Why he is valuable to work with
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
