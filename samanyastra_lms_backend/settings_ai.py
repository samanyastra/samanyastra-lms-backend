"""AI ops configuration — AWS Bedrock backend + model registry
(see core/ai_ops/).

Kept separate from settings.py so the AI provider/model config can be
reviewed and changed (e.g. swapping the default model, adding a new alias)
without touching the rest of the Django settings. Imported into settings.py
with `from .settings_ai import *`.
"""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
_env_file = BASE_DIR / ".env"
if _env_file.exists():
    environ.Env.read_env(_env_file)

# ── Backend selection ──
# Which AIWorker implementation core.ai_ops.registry.AIWorkerRegistry builds.
# "bedrock" is the only implementation today; add a branch in registry.py's
# _build() for any future provider and switch this.
AI_BACKEND = env("AI_BACKEND", default="bedrock")

# ── AWS Bedrock ──
AWS_DEFAULT_REGION = env("AWS_DEFAULT_REGION", default="us-east-1")
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default="")

# Model used when AIWorkerRegistry.get() is called with no explicit model/alias.
BEDROCK_MODEL_ID = env(
    "BEDROCK_MODEL_ID",
    default="anthropic.claude-3-5-haiku-20241022-v1:0",
)

# Friendly names → Bedrock model IDs, so callers can request e.g.
# AIWorkerRegistry.get(model="sonnet") instead of hardcoding an ID, and the
# model behind each name can be changed here (or via env) without touching
# call sites — this is the "change model dynamically" lever.
AI_MODEL_ALIASES = {
    "haiku": env("BEDROCK_MODEL_HAIKU", default="anthropic.claude-3-5-haiku-20241022-v1:0"),
    "sonnet": env("BEDROCK_MODEL_SONNET", default="anthropic.claude-3-5-sonnet-20241022-v2:0"),
    "opus": env("BEDROCK_MODEL_OPUS", default="anthropic.claude-3-opus-20240229-v1:0"),
}
