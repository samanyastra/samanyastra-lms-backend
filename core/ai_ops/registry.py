from django.conf import settings

from core.ai_ops.base import AIWorker


class AIWorkerRegistry:
    """The singleton: one AIWorker instance per (backend, model) pair, built
    lazily and reused for the life of the process (a boto3 client is meant to
    be reused, not reconnected per request).

    Callers can switch models at runtime without restarting the process —
    AIWorkerRegistry.get(model="sonnet") and AIWorkerRegistry.get() (the
    settings.BEDROCK_MODEL_ID default) each get their own cached worker, so
    an agent can pick a cheap/fast model for one step and a stronger one for
    another. Adding a provider beyond Bedrock is one new ai_ops/ file + one
    branch in _build() — no call-site changes."""

    _instances: dict[str, AIWorker] = {}

    @classmethod
    def get(cls, backend: str | None = None, model: str | None = None) -> AIWorker:
        backend = backend or settings.AI_BACKEND
        model_id = cls._resolve_model(model)
        key = f"{backend}:{model_id}"
        if key not in cls._instances:
            cls._instances[key] = cls._build(backend, model_id)
        return cls._instances[key]

    @classmethod
    def _resolve_model(cls, model: str | None) -> str:
        """`model` may be a friendly alias (settings.AI_MODEL_ALIASES, e.g.
        "haiku"/"sonnet"/"opus"), a raw provider model ID, or omitted to fall
        back to settings.BEDROCK_MODEL_ID."""
        if not model:
            return settings.BEDROCK_MODEL_ID
        return settings.AI_MODEL_ALIASES.get(model, model)

    @classmethod
    def _build(cls, backend: str, model_id: str) -> AIWorker:
        if backend == "bedrock":
            from core.ai_ops.bedrock import AWSBedrockT2TWorker
            return AWSBedrockT2TWorker(model_id=model_id)
        raise NotImplementedError(f"Unknown AI worker backend: {backend!r}")
