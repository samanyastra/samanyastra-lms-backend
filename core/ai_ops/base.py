from abc import ABC, abstractmethod


class AIWorker(ABC):
    """A single "can talk to an LLM" interface, provider-agnostic (Bedrock is
    the first implementation, but not the only one — see ai_ops/registry.py
    for how a new provider or model gets added)."""

    @abstractmethod
    def initialize(self):
        """Lazily set up the underlying client. Safe to call repeatedly."""

    @abstractmethod
    def test_connection(self) -> bool:
        ...

    @abstractmethod
    def invoke(self, prompt: str, max_tokens: int = 2000) -> dict:
        """Returns a normalized {"text": str, "usage": dict, "raw": <provider's
        native response>} regardless of which provider/model is behind it —
        callers should never need to know the provider's response shape.
        `max_tokens` lets a caller ask for a short answer (e.g. a yes/no
        check) instead of always paying for a long one."""
