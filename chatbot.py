"""
Stateless LLM wrapper.

History is passed in on every call — persistence is handled by
ChatService + SessionStore, not here.
"""
from __future__ import annotations

import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage

from core.config import (
    LLM_MODEL, LLM_BASE_URL, LLM_TEMPERATURE,
    LLM_MAX_TOKENS, SYSTEM_PROMPT, MAX_HISTORY_MESSAGES,
)

logger = logging.getLogger(__name__)


def trim_history(history: list[dict]) -> list[dict]:
    """Drop oldest messages once MAX_HISTORY_MESSAGES is exceeded."""
    if len(history) > MAX_HISTORY_MESSAGES:
        history = history[-MAX_HISTORY_MESSAGES:]
        logger.debug("History trimmed to %d messages", MAX_HISTORY_MESSAGES)
    return history


def build_messages(history: list[dict], system_prompt: str) -> list[BaseMessage]:
    """Convert plain dicts to LangChain message objects."""
    msgs: list[BaseMessage] = [SystemMessage(content=system_prompt)]
    for item in history:
        cls = HumanMessage if item.get("role") == "user" else AIMessage
        msgs.append(cls(content=item.get("content", "")))
    return msgs


class ChatBot:
    def __init__(
        self,
        model:         str = LLM_MODEL,
        base_url:      str = LLM_BASE_URL,
        system_prompt: str = SYSTEM_PROMPT,
    ) -> None:
        self.llm = ChatOpenAI(
            model=model,
            base_url=base_url,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
        )
        self.system_prompt = system_prompt

    async def chat(self, user_input: str, history: list[dict]) -> tuple[str, list[dict]]:
        """
        Send *user_input* with *history* context.
        Returns (reply, updated_history).
        """
        history = trim_history(history)
        history.append({"role": "user", "content": user_input})

        messages = build_messages(history, self.system_prompt)
        logger.debug("Invoking LLM — %d messages in context", len(messages))

        response: AIMessage = await self.llm.ainvoke(messages)
        reply = response.content

        history.append({"role": "assistant", "content": reply})
        return reply, history