"""
engine/conversation/memory.py

Tracks conversation history for a single session so the model can
resolve references like "summarize that" or "compare it with JWT"
to what was actually discussed earlier. Kept in-memory and simple
on purpose - one ConversationMemory instance per active chat
session in the UI, not persisted to disk (yet).
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Turn:
    role: str          # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)


class ConversationMemory:
    """
    Holds the back-and-forth for one chat session.

    max_turns caps how many recent turns get passed into the LLM
    prompt - keeps context small (matters on this hardware) while
    still letting the model resolve near-term references. The full
    history is still kept internally in case the UI wants to show
    a scrollback, only what's fed to the model is capped.
    """

    def __init__(self, max_turns_for_context: int = 6):
        self.turns: list[Turn] = []
        self.max_turns_for_context = max_turns_for_context

    def add_user_message(self, content: str) -> None:
        self.turns.append(Turn(role="user", content=content))

    def add_assistant_message(self, content: str) -> None:
        self.turns.append(Turn(role="assistant", content=content))

    def get_context_for_prompt(self) -> list[dict]:
        """
        Returns the most recent turns formatted for prompt_builder's
        conversation_history param: [{"role": ..., "content": ...}, ...]
        """
        recent = self.turns[-self.max_turns_for_context:]
        return [{"role": t.role, "content": t.content} for t in recent]

    def clear(self) -> None:
        """Starts a fresh conversation (e.g. user clicks 'New Chat')."""
        self.turns = []

    def is_empty(self) -> bool:
        return len(self.turns) == 0