"""Per-track pipeline code — one subpackage per modality (documents, images,
audio), each importing from src/core/ but never from a sibling pipeline.

See docs/chapters/ch05-environment-setup-and-offline-llm.md §4.4 for why
this directory exists separately from src/core/: code here is one track's
business; code in src/core/ is everybody's.
"""
