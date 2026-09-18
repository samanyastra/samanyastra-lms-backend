def extract_json_text(text: str) -> str:
    """Strip an optional ```json ... ``` (or bare ``` ... ```) fence around a
    model's reply. Claude tends to wrap JSON replies in a markdown fence
    fairly often even when the prompt explicitly says not to, so every call
    site that expects a JSON reply needs this, not just json.loads() on the
    raw text.

    Closes on the fence's first "```", not the string's last — a model that
    appends trailing prose after the closing fence (e.g. a note explaining
    why it declined to fabricate content) would otherwise leave that prose
    stuck to the JSON and break json.loads()."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if "```" in text:
            text = text.split("```", 1)[0]
    elif text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    return text.strip()
