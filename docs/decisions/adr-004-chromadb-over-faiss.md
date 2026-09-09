# ADR-004: Use ChromaDB rather than FAISS or Qdrant

## Status
Accepted — Day 4

## Context

Both text and image embeddings (ADR-003) need to be stored and searched by nearest
neighbour. The storage layer is a shared dependency both Track A and Track B code against
from Day 6 onward (Ch4 §4.1), so it must be fixed today, before either pipeline is written.

Requirements, derived from Chapter 1 §1.6.3 and Chapter 1 §1.8 (citation provenance):

- Must persist vectors across application restarts, without a separately administered
  database server — the team is running this on personal laptops, not managed infrastructure.
- Must store arbitrary JSON metadata alongside each vector (source, modality, page,
  timestamp) — this is the mechanism citations depend on.
- Must support two independent collections of different dimensionality (384-d text,
  512-d image — ADR-003), without them interfering.
- Must run acceptably at the project's actual scale: a 50–200 file demo corpus, on the
  order of 10^3–10^4 stored vectors (Ch1 §1.6.1).

## Decision

Use ChromaDB, an embedded vector database that runs as a Python library inside the
application process, with no separate server to install or administer.

## Alternatives considered

1. **FAISS.** Rejected: FAISS is a similarity-search *library*, not a database — it has no
   built-in persistence layer, no metadata storage, and no query-by-metadata capability. All
   three would need to be built by hand on top of it (e.g. a parallel JSON file mapping
   vector IDs to provenance metadata), which is exactly the kind of custom infrastructure
   work a 9-day sprint with a beginner team cannot afford. FAISS's genuine strength — GPU-
   accelerated search at hundreds of millions of vectors [FAISS-GPU] — is irrelevant at our
   scale of 10^3–10^4 vectors, where even brute-force search completes in milliseconds
   (Ch1 §1.6.1).
2. **Qdrant.** Rejected: Qdrant is a genuine vector *database* with metadata filtering, but
   its natural deployment is as a server process (via Docker or a standalone binary) that
   must be started and kept running alongside the application. For a beginner team running
   on personal laptops rather than managed infrastructure, an embedded database that starts
   and stops with the Python process removes an entire category of "is the database running"
   failure mode that a self-managed server introduces.
3. **A hand-rolled flat-file solution** (numpy arrays plus a JSON sidecar for metadata).
   Rejected: reimplements exactly what a vector database exists to provide (indexed search,
   metadata filtering, persistence), for a team whose time is better spent on the four
   ingestion pipelines and the retrieval logic that are the actual subject of this project.
4. **Pinecone or another managed cloud vector database.** Rejected outright on the same
   grounds as ADR-002 — any hosted service is a network dependency, incompatible with
   Objective O6.

## Consequences

**Positive**
+ No server to install, configure, or keep running — appropriate for a beginner team's
  first vector-database experience.
+ Metadata storage and filtering are first-class, directly supporting citation provenance.
+ Two independent named collections map cleanly onto the two-collection design of ADR-003.
+ Uses HNSW internally (Ch1 §1.6.2), giving the team a real, if pedagogically-scaled,
  example of approximate nearest-neighbour search.

**Negative**
− Embedded operation means the database's performance ceiling is tied to the single
  machine running the application; this is a non-issue at project scale but should be
  named honestly as a scalability limitation in the report.
− ChromaDB's ecosystem and community are smaller than FAISS's, so troubleshooting relies
  more on official documentation than on a large body of third-party examples.

**Implications for other components**
- Fixes the API both Track A's retrieval code and Track B's ingestion code call directly.
- Chapter 5 owns the actual collection setup (`text_index`, `image_index`) and the
  contract-test round-trip check specified in Chapter 4 §1.6.

## Revisit if

The corpus grows past roughly 10^5–10^6 vectors, at which point FAISS's GPU-accelerated
search or a properly server-hosted vector database would become the appropriate choice —
well outside this project's stated scope (Ch1 §2.4).

---

*Citation [FAISS-GPU]: Johnson, Douze and Jégou, "Billion-Scale Similarity Search with
GPUs," IEEE Transactions on Big Data, vol. 7, no. 3, 2021. **Verify before use.***
