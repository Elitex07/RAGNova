"""
Build the real ChromaDB text_index from data/documents/.

Run with:  python scripts/build_index.py

Safe to re-run any time data/documents/ changes: index_documents_directory()
writes via ChromaDB's upsert (add-or-replace-by-id — see vector_store.py's
add_chunks() docstring for why plain add() was tried first and rejected),
so re-running this after editing a source file correctly refreshes that
file's chunks in place rather than either erroring or silently keeping
stale content. A NEW file just adds new chunks. Deleting chroma_db/ first
is only needed for a genuinely from-scratch rebuild (e.g. after changing
CHUNK_SIZE_WORDS, which changes every chunk_id's page-relative numbering).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.config import settings
from src.pipelines.documents.index import index_documents_directory

DOCS_DIR = Path(__file__).resolve().parent.parent / "data" / "documents"


def main() -> None:
    print(f"Indexing {DOCS_DIR} into {settings.CHROMA_PERSIST_DIR} ...")
    count = index_documents_directory(DOCS_DIR)
    print(f"Indexed {count} chunks into text_index.")
    print("\nNext: python scripts/evaluate_retrieval.py")


if __name__ == "__main__":
    main()
