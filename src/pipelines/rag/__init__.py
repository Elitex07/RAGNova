"""Chapter 10 — RAG core: retrieval + prompt construction + generation +
citations, orchestrated on top of Chapter 7's `search_text()`."""

from src.pipelines.rag.answer import RagAnswer, answer_query

__all__ = ["RagAnswer", "answer_query"]
