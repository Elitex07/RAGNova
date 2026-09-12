"""Track A's document-ingestion pipeline (Chapter 6): PDF and DOCX files in,
real `Chunk` objects out.

Organised by modality (pdf_parser.py / docx_parser.py), not by pipeline
stage, per the Coupling/Cohesion argument in docs/GLOSSARY.md — adding a
third document type later means adding a file here, not editing existing
ones.
"""
