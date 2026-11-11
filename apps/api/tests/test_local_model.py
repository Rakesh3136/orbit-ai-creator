import json
from io import BytesIO
import pytest

from aimn_api.local_model import LocalModelError, generate_script


def test_local_model_is_disabled_by_default(monkeypatch):
    monkeypatch.delenv("AIMN_LLM_PROVIDER", raising=False)
    assert generate_script("A topic") is None


def test_local_ollama_response_is_validated(monkeypatch):
    monkeypatch.setenv("AIMN_LLM_PROVIDER", "ollama")
    # Use a real context-manager response object for the adapter contract.
    class Response(BytesIO):
        def __enter__(self): return self
        def __exit__(self, *args): self.close()
    monkeypatch.setattr("aimn_api.local_model.urlopen", lambda request, timeout: Response(
        json.dumps({"response": json.dumps({
            "title": "Draft title", "hook": "Hook", "body": "Body", "conclusion": "End"
        })}).encode()
    ))
    assert generate_script("A topic")["title"] == "Draft title"


def test_local_model_rejects_unknown_provider(monkeypatch):
    monkeypatch.setenv("AIMN_LLM_PROVIDER", "paid-api")
    with pytest.raises(LocalModelError, match="hosted providers"):
        generate_script("A topic")


def test_local_model_rejects_incomplete_json(monkeypatch):
    monkeypatch.setenv("AIMN_LLM_PROVIDER", "ollama")
    class Response(BytesIO):
        def __enter__(self): return self
        def __exit__(self, *args): self.close()
    monkeypatch.setattr("aimn_api.local_model.urlopen", lambda request, timeout: Response(
        json.dumps({"response": json.dumps({"title": "Only title"})}).encode()
    ))
    with pytest.raises(LocalModelError, match="exactly"):
        generate_script("A topic")
