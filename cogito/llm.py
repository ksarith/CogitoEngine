"""LLM provider layer.

Stdlib-only HTTP so the core package has no hard runtime dependency beyond
PyYAML. Three provider families are supported out of the box:

- openai     -> POST {base}/chat/completions   (env: OPENAI_API_KEY)
- mistral    -> OpenAI-compatible              (env: MISTRAL_API_KEY)
- anthropic  -> POST {base}/v1/messages        (env: ANTHROPIC_API_KEY)

Every call returns an LLMResponse that carries provenance (provider, model)
because a chain of prompts is not a chain of custody until you record who
said what.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request

REFUSAL_MARKER = "[REFUSAL]"

_MARKUP_PREFIX = re.compile(r"^[\s>*_`#~-]+")


def is_refusal(text: str) -> bool:
    """True if the output begins with the refusal marker.

    Prefix-only per contract section 4, but tolerant of leading whitespace,
    markdown emphasis/quote/heading characters and letter case
    ('**[refusal]** ...'). Refusals without the marker, or after a preamble
    line, are NOT detected (Unknown CE-U05).
    """
    head = _MARKUP_PREFIX.sub("", text)
    return head[: len(REFUSAL_MARKER)].upper() == REFUSAL_MARKER


class LLMError(RuntimeError):
    """Raised when a provider call fails. Never swallowed: caller decides."""


class LLMResponse:
    """A model reply plus provenance.

    model is the model the provider REPORTED serving (the requested model if
    the response names none); requested_model is what was asked for. They
    differ under aliases such as '-latest'. base_url and temperature record
    what was actually called and how.
    """

    def __init__(self, text: str, model: str, provider: str, raw: dict | None = None,
                 *, requested_model: str | None = None, base_url: str = "",
                 temperature: float | None = None):
        self.text = text
        self.model = model
        self.provider = provider
        self.raw = raw or {}
        self.requested_model = requested_model or model
        self.base_url = base_url
        self.temperature = temperature

    def __repr__(self) -> str:  # pragma: no cover - debug sugar
        return f"LLMResponse(provider={self.provider!r}, model={self.model!r}, chars={len(self.text)})"


DEFAULT_BASES = {
    "openai": "https://api.openai.com/v1",
    "mistral": "https://api.mistral.ai/v1",
    "anthropic": "https://api.anthropic.com",
}

DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "mistral": "mistral-small-latest",
    "anthropic": "claude-haiku-5-5",
}

ANTHROPIC_VERSION = "2023-06-01"


def _post(url: str, headers: dict, payload: dict, timeout: int = 120) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")[:500]
        raise LLMError(f"provider returned {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise LLMError(f"network error: {exc}") from exc


def call_llm(
    prompt: str,
    system: str | None = None,
    *,
    provider: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    temperature: float = 0.2,
) -> LLMResponse:
    """Call a chat model and return an LLMResponse with provenance.

    provider defaults to $COGITO_PROVIDER, then "mistral".
    api_key defaults to the provider's standard env var.
    """
    provider = (provider or os.environ.get("COGITO_PROVIDER") or "mistral").lower()
    if provider not in DEFAULT_BASES:
        raise LLMError(f"unknown provider {provider!r}; expected one of {sorted(DEFAULT_BASES)}")
    model = model or os.environ.get("COGITO_MODEL") or DEFAULT_MODELS[provider]
    base = (base_url or os.environ.get("COGITO_BASE_URL") or DEFAULT_BASES[provider]).rstrip("/")

    if provider == "anthropic":
        key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise LLMError("ANTHROPIC_API_KEY not set")
        payload: dict = {"model": model, "max_tokens": 4096, "temperature": temperature,
                         "messages": [{"role": "user", "content": prompt}]}
        if system:
            payload["system"] = system
        data = _post(f"{base}/v1/messages",
                     {"x-api-key": key, "anthropic-version": ANTHROPIC_VERSION}, payload)
        text = "".join(block.get("text", "") for block in data.get("content", []))
    else:
        key = api_key or os.environ.get(f"{provider.upper()}_API_KEY")
        if not key:
            raise LLMError(f"{provider.upper()}_API_KEY not set")
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        data = _post(f"{base}/chat/completions",
                     {"Authorization": f"Bearer {key}"},
                     {"model": model, "temperature": temperature, "messages": messages})
        text = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")

    if not text.strip():
        raise LLMError(f"provider {provider} returned empty content")
    reported = data.get("model")
    return LLMResponse(text=text,
                       model=reported if isinstance(reported, str) and reported else model,
                       provider=provider, raw=data, requested_model=model,
                       base_url=base, temperature=temperature)
