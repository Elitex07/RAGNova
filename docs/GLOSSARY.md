# RAGNova Glossary

Every technical term used in this project, explained simply. Alphabetical. When any chapter uses a word you don't know — look here. If it's missing, add it (that's part of documentation duty).

| Term | Plain-English meaning |
|---|---|
| **ASR** | Automatic Speech Recognition — software that converts spoken audio into text. Whisper is an ASR model. |
| **Chunk / Chunking** | Splitting a long document into small pieces (e.g. ~300 words each) before embedding. Needed because (a) embeddings work better on focused text, (b) the LLM prompt has limited space. |
| **ChromaDB** | An embedded vector database — a Python library that stores vectors and finds nearest neighbors. "Embedded" = runs inside your program, no separate server. |
| **CLIP** | Contrastive Language-Image Pretraining. A model (OpenAI, 2021) that puts images and text into the *same* vector space, enabling text→image search. |
| **Context window** | The maximum amount of text an LLM can read at once (its "working memory"). Local models: typically 4k–128k tokens. Limits how many retrieved chunks we can paste into a prompt. |
| **Cosine similarity** | A number from -1 to 1 measuring how similar two vectors' directions are. 1 = same meaning, 0 = unrelated. The math behind "find nearest vectors." |
| **Cross-modal search** | Searching one modality with another — e.g. finding images using a text query. |
| **Embedding** | A list of numbers (vector) representing the *meaning* of text/image/audio, produced by a neural network. Similar meaning → nearby vectors. |
| **Faster-whisper** | An optimized reimplementation of Whisper that runs faster on CPU. |
| **Hallucination** | When an LLM confidently generates false information. RAG's main enemy. |
| **Indexing** | The offline preparation step: parse files → chunk → embed → store in the vector DB. Done once per file; makes later queries fast. |
| **Inference** | Running a trained model to get outputs (as opposed to training it). |
| **LLM** | Large Language Model — a neural network trained to predict the next word, capable of answering/summarizing/reasoning. |
| **Modality** | A type of data: text, image, audio, video. |
| **Nearest-neighbor search** | Given a query vector, finding the stored vectors closest to it. The core operation of a vector database. |
| **OCR** | Optical Character Recognition — extracting typed/printed text from an image (e.g. reading text in a screenshot). Tesseract is an OCR engine. |
| **Ollama** | A tool that makes downloading and running LLMs locally one command (`ollama run llama3.2`). Exposes a local API our code calls. |
| **Parameters (of a model)** | The learned numbers inside a neural network. "3B model" = 3 billion parameters. More = smarter but heavier. |
| **Prompt** | The full text sent to an LLM: instructions + context + user question. |
| **Quantization** | Compressing a model by storing its numbers with fewer bits (e.g. 4-bit instead of 16-bit). Slight quality loss, huge memory savings — the reason 3B–8B models fit on laptops. |
| **RAG** | Retrieval-Augmented Generation: retrieve relevant chunks from user's files → paste into prompt → LLM generates grounded, cited answer. |
| **Semantic search** | Search by meaning (via embeddings) instead of exact keywords. |
| **sentence-transformers** | A Python library of ready-made text embedding models. We use `all-MiniLM-L6-v2` (384-dim, 80 MB). |
| **Streamlit** | Python library for building web UIs without writing HTML/JS. Our chat interface. |
| **Token** | The unit LLMs read text in — roughly ¾ of a word. "1000 tokens" ≈ 750 words. |
| **Top-K** | Retrieving the K most similar chunks (e.g. top-5) for a query. |
| **Vector** | A list of numbers, e.g. `[0.12, -0.83, ...]`. In this project, always an embedding. |
| **Vector database** | A database specialized in storing vectors and answering nearest-neighbor queries fast. |
| **Whisper** | OpenAI's open-source speech-to-text model. Downloadable, runs offline. |
