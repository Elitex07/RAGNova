"""
Follow-up questions: "tell me more", "who made it?", "what about the second one?".

Why (2026-10-11): after "who is Raiden?" was answered, "tell me more" was refused. Every question was searched on its
own, and "tell me more" has nothing in it to search for: no chunk clears the floor, so the model is never even asked.

What this does, without an extra model call (on a CPU every call costs seconds, ADR-015):

  * is_follow_up() decides whether a question leans on the one before it: it has no content words of its own
    ("tell me more", "why?"), it opens like a continuation ("what about ...", "and ..."), or it has a pronoun
    ("it", "they", "she") and at most two content words.
  * resolve() gives the question to SEARCH with: the previous turn's search question, plus this question's own content
    words when it has any ("what about rule 3?" after "lab rules" searches "lab rules rule 3"). The prompt still
    shows the question as typed, with the earlier exchange above it (prompt.py) so the model knows what "it" is.

A question that stands on its own is searched exactly as before, and gets no earlier conversation in its prompt.
"""

from __future__ import annotations

import re

from src.pipelines.rag.lexical import content_tokens

_PRONOUNS = frozenset("it its they them their theirs he him his she her hers this that these those one".split())
_CONTINUATION = re.compile(
    r"^\s*(and|also|what about|how about|what else|more|elaborate|continue|go on|explain (it|that|more|further)|"
    r"tell me more|say more|any more|anything else)\b",
    re.IGNORECASE,
)


def is_follow_up(question: str) -> bool:
    """True when `question` only makes sense together with the turn before it."""
    if not question.strip():
        return False
    content = content_tokens(question)
    if not content:
        return True
    if _CONTINUATION.match(question):
        return True
    words = set(re.findall(r"[a-z]+", question.lower()))
    return bool(words & _PRONOUNS) and len(content) <= 2


def resolve(question: str, previous_search: str | None) -> str:
    """The question to search with. `previous_search` is what the previous turn searched with (None when there was
    no earlier turn); a question that is not a follow-up is returned unchanged."""
    if not previous_search or not is_follow_up(question):
        return question
    own = content_tokens(question)
    return f"{previous_search} {' '.join(own)}".strip() if own else previous_search
