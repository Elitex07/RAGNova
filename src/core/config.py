"""
Central configuration — the one place every track reads shared settings
from, so a value like "which embedding model" or "what chunk size" is
never hardcoded independently in three different files.

Usage, from any track's code:

    from src.core.config import settings
    print(settings.OLLAMA_MODEL)

Design rationale: we use a small dataclass loaded once from environment
variables (via python-dotenv reading .env), rather than a settings library
like Pydantic Settings. Same reasoning as schemas.py's dataclass-over-Pydantic
choice — fewer dependencies, and a beginner team can read every line of what
this does. If the project grows past Day 14, Pydantic Settings' automatic
type coercion and validation would be a reasonable upgrade.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Loads variables from a `.env` file in the project root into the process
# environment, if one exists. Does nothing (silently) if .env is missing —
# which is fine, because every setting below has a sensible default.
load_dotenv()


def _get_float(name: str, default: float) -> float:
    return float(os.environ.get(name, default))


def _get_int(name: str, default: int) -> int:
    return int(os.environ.get(name, default))


@dataclass(frozen=True)
class Settings:
    OLLAMA_MODEL: str = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")
    OLLAMA_HOST: str = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    LLM_TEMPERATURE: float = _get_float("LLM_TEMPERATURE", 0.1)

    TEXT_EMBEDDING_MODEL: str = os.environ.get("TEXT_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    CLIP_MODEL: str = os.environ.get("CLIP_MODEL", "ViT-B-32")
    CLIP_PRETRAINED: str = os.environ.get("CLIP_PRETRAINED", "laion2b_s34b_b79k")
    WHISPER_MODEL_SIZE: str = os.environ.get("WHISPER_MODEL_SIZE", "base")

    CHROMA_PERSIST_DIR: str = os.environ.get("CHROMA_PERSIST_DIR", "./chroma_db")

    CHUNK_SIZE_WORDS: int = _get_int("CHUNK_SIZE_WORDS", 300)
    CHUNK_OVERLAP_WORDS: int = _get_int("CHUNK_OVERLAP_WORDS", 50)
    TOP_K: int = _get_int("TOP_K", 5)


# A single shared instance — import this, don't instantiate Settings()
# yourself, so every track genuinely reads the same values.
settings = Settings()


if __name__ == "__main__":
    # Run `python -m src.core.config` to print the resolved settings —
    # useful for confirming your .env is actually being picked up.
    for field_name in Settings.__dataclass_fields__:
        print(f"{field_name} = {getattr(settings, field_name)!r}")
