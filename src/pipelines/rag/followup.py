"""
Follow-up questions: "tell me more", "who made it?", "what about the second one?".

Why (2026-10-11): after "who is Raiden?" was answered, "tell me more" was refused. Every question was searched on its
own, and "tell me more" has nothing in it to search for: no chunk clears the floor, so the model is never even asked.

What this does, without an extra model call (on a CPU every call costs seconds, ADR-015):

  * is_follow_up() decides whether a question leans on the one before it: it has no content words of its own
    ("tell me more", "why?"), it opens like a continuation ("what about ...", "and ..."), or it has a pronoun
    ("it", "they", "she") and at most two content words.
  * resolve() gives the question to SEARCH with: the previous turn's search question, plus this question's own content
    words when it has any ("what about rule 3?" after "lab rules" searches "lab rules rule 3"). A new number or name
    replaces the earlier one ("what about rule 3?" after "lab rule 2" searches "lab rule rule 3"). The prompt still
    shows the question as typed, with the earlier exchange above it (prompt.py) so the model knows what "it" is.

A question that stands on its own is searched exactly as before, and gets no earlier conversation in its prompt.
"""

from __future__ import annotations

import re

from src.pipelines.rag.lexical import content_tokens, name_phrases

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
    if not own:
        return previous_search
    # A follow-up that names a new detail asks about it INSTEAD of the old one: "what about rule 3?" after "lab rule 2"
    # searches rule 3, not rules 2 and 3; "what about Mr. V. Sharma?" after "who is Dr. S. Rao?" drops Rao. Numbers
    # replace numbers and a name replaces a name; every other earlier word stays, as the topic.
    names = name_phrases(question)
    previous_tokens = content_tokens(previous_search)
    new_numbers = [token for token in own if token.isdigit()]
    old_numbers = [token for token in previous_tokens if token.isdigit()]

    # Case 1: Numeric replacement - "what about rule 3?" after "tell me lab rule no. 2"
    # Replace the old number(s) with the new number in the previous search
    if new_numbers and old_numbers:
        replacement = new_numbers[0]
        kept = previous_search
        for old_number in old_numbers:
            # Canonicalize "rule no. 2" to "rule 3" as part of the
            # replacement, so the historical reference cannot dilute lexical
            # matching with the old wording.
            kept = re.sub(
                rf"\bno\.\s*{re.escape(old_number)}(?![a-z0-9])",
                replacement,
                kept,
                flags=re.IGNORECASE,
            )
            kept = re.sub(
                rf"(?<![a-z0-9]){re.escape(old_number)}(?![a-z0-9])",
                replacement,
                kept,
                flags=re.IGNORECASE,
            )
        # Also add any non-numeric content from the follow-up question
        kept_tokens = set(content_tokens(kept))
        added = [token for token in own if not token.isdigit() and token not in kept_tokens]
        return re.sub(r"\s+", " ", f"{kept} {' '.join(added)}").strip()

    # Case 2: Name phrase replacement - "what about Mr. V. Sharma?" after "Who is Dr. S. Rao?"
    if names:
        drop: set[str] = set()
        for phrase in name_phrases(previous_search):
            drop.update(phrase)

        kept = previous_search
        for word in drop:
            kept = re.sub(rf"(?<![a-z0-9]){re.escape(word)}(?![a-z0-9])", " ", kept, flags=re.IGNORECASE)
        kept = re.sub(r"(?:^|\s)[.,;:]+(?=\s|$)", " ", kept)
        added = [" ".join(phrase) for phrase in names]
        # Add non-name tokens from the follow-up question
        added += [t for t in own if not any(t in phrase for phrase in names)]
        return re.sub(r"\s+", " ", f"{kept} {' '.join(added)}").strip()

    # Case 3: No numbers or names to replace - just append new content words
    # e.g., "what about rule 3?" after "tell me lab rules" -> "tell me lab rules rule 3"
    kept_tokens = set(content_tokens(previous_search))
    added = [token for token in own if token not in kept_tokens]
    return re.sub(r"\s+", " ", f"{previous_search} {' '.join(added)}").strip()
