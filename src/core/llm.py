"""
The one function every track eventually calls to turn a prompt string into
an LLM answer: a thin wrapper around Ollama's local HTTP API.

ADR-002 fixes the model (Llama 3.2 3B Instruct, 4-bit) and the serving
mechanism (`ollama serve` + REST at settings.OLLAMA_HOST, `POST /api/generate`
specifically — never `/api/chat`, since this project sends single-shot
prompts with the retrieved context baked in, not a multi-turn conversation).

`ollama==0.4.4` has been sitting in requirements.txt since Day 4, pinned but
never imported by any code — scripts/verify_setup.py talks to the same HTTP
endpoint via raw urllib instead, deliberately, because that script has to
run *before* requirements.txt can be trusted installed. This module is what
finally exercises the pinned client, now that we're past that bootstrap
concern.
"""

from __future__ import annotations

import ollama

from src.core.config import settings


def generate(prompt: str) -> str:
    """Send `prompt` to the configured Ollama model and return its response
    text.

    Uses `ollama.Client(host=...).generate(...)`, the client's wrapper
    around `POST /api/generate` — the same endpoint ch05 §2.2 documents as
    "what Chapter 10's RAG core calls." `stream=False` so this function
    returns one complete string rather than a generator of tokens; a
    streaming variant is future UI work (Chapter 11), not needed here.

    `options` bounds generation deliberately: `temperature` from
    settings.LLM_TEMPERATURE (already low, 0.1, so answers stay close to
    the retrieved evidence rather than creative); `num_predict` caps how
    many tokens the model can emit, so a degenerate repeating completion
    can't hang the caller forever; `num_ctx` widens Ollama's own default
    (2048) enough to hold TOP_K retrieved chunks plus prompt scaffolding
    (see settings.LLM_NUM_CTX's docstring for the arithmetic).
    """
    client = ollama.Client(host=settings.OLLAMA_HOST)
    try:
        response = client.generate(
            model=settings.OLLAMA_MODEL,
            prompt=prompt,
            stream=False,
            options={
                "temperature": settings.LLM_TEMPERATURE,
                "num_predict": settings.LLM_MAX_TOKENS,
                "num_ctx": settings.LLM_NUM_CTX,
            },
        )
    except Exception as exc:
        raise RuntimeError(
            f"Could not reach Ollama at {settings.OLLAMA_HOST} — "
            f"is `ollama serve` running, and is {settings.OLLAMA_MODEL!r} "
            f"pulled (`ollama pull {settings.OLLAMA_MODEL}`)? "
            f"Underlying error: {exc}"
        ) from exc

    return response["response"]
