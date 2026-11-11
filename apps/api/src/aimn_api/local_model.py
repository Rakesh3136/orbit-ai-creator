"""Optional local Ollama adapter. No hosted or paid model provider is supported here."""
from __future__ import annotations

import json
import os
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen


class LocalModelError(RuntimeError):
    pass


def generate_script(topic: str, context: str = "") -> dict[str, str] | None:
    """Generate a bounded draft using a local Ollama server; return None when disabled."""
    provider = os.getenv("AIMN_LLM_PROVIDER", "none").strip().lower()
    if provider in {"", "none", "disabled"}:
        return None
    if provider != "ollama":
        raise LocalModelError("AIMN_LLM_PROVIDER must be none or ollama; hosted providers are not enabled")
    base = os.getenv("AIMN_OLLAMA_URL", "http://ollama:11434").rstrip("/")
    model = os.getenv("AIMN_OLLAMA_MODEL", "qwen2.5:3b").strip()
    if not model or len(model) > 120:
        raise LocalModelError("AIMN_OLLAMA_MODEL must be a valid model name")
    prompt = (
        "Write an original YouTube draft using only the supplied context. "
        "Do not invent citations, statistics, quotes, or claims of verification. "
        "If context is missing, keep claims general and flag uncertainty in the body. "
        "Return JSON only with exactly these string keys: title, hook, body, conclusion. "
        "Aim for a clear, engaging, practical script.\n"
        f"TOPIC: {topic[:180]}\nCONTEXT (unverified unless explicitly sourced): {context[:6000]}"
    )
    payload = json.dumps({
        "model": model, "prompt": prompt, "stream": False, "format": "json",
        "options": {"temperature": 0.7, "num_predict": 1400},
    }).encode("utf-8")
    request = Request(base + "/api/generate", data=payload,
                      headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=180) as response:
            envelope = json.loads(response.read(2_000_000).decode("utf-8"))
        generated = json.loads(envelope.get("response", ""))
    except (URLError, HTTPError, TimeoutError, OSError, UnicodeDecodeError,
            json.JSONDecodeError, AttributeError) as exc:
        raise LocalModelError(f"Local Ollama request failed: {type(exc).__name__}") from exc
    keys = {"title", "hook", "body", "conclusion"}
    if not isinstance(generated, dict) or set(generated) != keys:
        raise LocalModelError("Local model response must contain exactly title, hook, body and conclusion")
    limits = {"title": 180, "hook": 2000, "body": 12000, "conclusion": 2000}
    result: dict[str, str] = {}
    for key, limit in limits.items():
        value = generated.get(key)
        if not isinstance(value, str) or not value.strip() or len(value) > limit:
            raise LocalModelError(f"Local model returned an invalid {key} field")
        result[key] = value.strip()
    return result
