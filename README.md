# Mnemosyne V2 - Multi-Source Retrieval & Intelligent Research Assistant

## Project Vision

Mnemosyne is an AI-powered document intelligence platform inspired by NotebookLM. It allows users to upload, organize, search, and interact with information spread across multiple sources instead of relying on a single document.

Unlike a traditional chatbot, Mnemosyne's primary objective is **knowledge retrieval grounded in user-provided data**. Every response should be traceable to one or more sources.

---

# Goal

Build a Retrieval-Augmented NLP system that can:

- Search across multiple uploaded documents simultaneously
- Search structured datasets
- Search external APIs (future)
- Retrieve the most relevant information
- Generate grounded answers using retrieved context
- Cite the exact source(s) used
- Maintain conversation context

The Python application (Streamlit) acts as the interface while the NLP engine acts as the brain.

---

# High Level Architecture

```
                User Question
                      │
                      ▼
             Query Processing Layer
                      │
         ┌────────────┼────────────┐
         │            │            │
         ▼            ▼            ▼
   Keyword Search  Semantic Search Metadata Filter
         │            │            │
         └──────┬─────┴────────────┘
                ▼
        Candidate Document Retrieval
                │
                ▼
         Ranking / Re-ranking
                │
                ▼
       Context Construction Engine
                │
                ▼
        Response Generation Model
                │
                ▼
      Answer + Source Citations
```

---

# Core Objectives

## 1. Document Understanding

The system should understand multiple document types.

Supported formats:

- PDF
- DOCX
- TXT
- Markdown
- HTML
- CSV
- JSON

Future:

- PowerPoint
- Excel
- Images (OCR)
- Audio transcription

---

## 2. Document Parsing

Each uploaded document is converted into a unified internal representation.

Example

```python
Document
    ├── metadata
    ├── pages
    ├── sections
    ├── paragraphs
    ├── tables
    ├── images
    └── extracted text
```

---

## 3. Intelligent Chunking

Documents should not simply be split every N words.

Instead:

- preserve headings
- preserve paragraphs
- preserve table boundaries
- preserve code blocks
- preserve lists

Each chunk contains

```
chunk_id

document_id

page_number

section

text

metadata
```

---

# Search Engine

The search engine is composed of multiple retrieval methods.

---

## Stage 1 — Keyword Search

Traditional lexical retrieval.

Possible algorithms:

- BM25
- TF-IDF
- Inverted Index

Purpose

Good for:

- exact phrases
- filenames
- variable names
- IDs
- dates

---

## Stage 2 — Semantic Search

Convert every chunk into embeddings.

Possible embedding models:

- BAAI/bge-small-en
- e5-base
- Instructor
- MiniLM
- Jina Embeddings

Store vectors in

- FAISS
- Chroma
- Qdrant

Purpose

Find similar meaning even if wording differs.

Example

User:

```
How is authentication handled?
```

Document

```
Users login using JWT tokens.
```

Semantic search should retrieve this.

---

## Stage 3 — Metadata Filtering

Before semantic retrieval, optionally filter by

- filename
- author
- tags
- upload date
- project
- document type

---

## Stage 4 — Hybrid Search

Final score

```
Hybrid Score

=

Keyword Score

+

Semantic Score

+

Metadata Score
```

Hybrid retrieval generally performs much better than using only one search method.

---

# Ranking Pipeline

Retrieved chunks should be re-ranked.

Possible methods

Cross Encoder

```
Question

+

Candidate Chunk

↓

Relevance Score
```

Top-ranked chunks become the context.

---

# Context Builder

Instead of feeding isolated chunks,

merge nearby chunks.

Example

```
Chunk 34

Chunk 35

Chunk 36
```

↓

```
Combined Context
```

Avoid

- duplicate information
- repeated paragraphs
- overlapping chunks

Maximum context size should be configurable.

---

# Response Generation

The generation model should only answer using retrieved context.

Prompt

```
Question

+

Retrieved Context

↓

Answer
```

Important rules

If the answer is absent

Return

"I couldn't find this information in your uploaded sources."

Never hallucinate.

---

# Source Attribution

Every answer should cite its source.

Example

```
Authentication uses JWT.

Source:
API_Design.pdf
Page 12
Section Authentication
```

If multiple sources contributed

```
Sources

1.
Backend.pdf
Page 5

2.
Requirements.docx
Section Login
```

---

# Multi-Document Reasoning

The model should compare information across documents.

Example

Question

```
What changed between Version 1 and Version 2?
```

The engine should

Retrieve

```
Version1.pdf

Version2.pdf
```

Then compare

instead of answering from only one document.

---

# Conversation Memory

Maintain session context.

Example

User

```
Explain OAuth.
```

Later

```
Summarize that.
```

Later

```
Compare it with JWT.
```

The model should understand references.

---

# Planned Source Types

## Local Files

- PDFs
- Word
- Markdown
- Text

---

## Structured Data

- CSV
- JSON
- SQLite

---

## APIs

Future

Examples

- Wikipedia
- Arxiv
- PubMed
- GitHub
- StackOverflow

---

## Web Search

Future module

Used only when user explicitly allows internet search.

---

# NLP Components

The project consists of several independent NLP modules.

---

## Query Understanding

Tasks

- Tokenization
- Stopword removal
- Lemmatization
- POS tagging
- Named Entity Recognition
- Intent Classification
- Query Expansion

---

## Retrieval

Tasks

- BM25
- Dense Retrieval
- Hybrid Retrieval
- Vector Search

---

## Ranking

Tasks

- Cross Encoder Re-ranking
- Similarity Scoring
- Duplicate Removal

---

## Response Generation

Tasks

- Prompt construction
- Context compression
- Citation generation
- Hallucination prevention

---

# Suggested Project Structure

```
nlp/

│

├── preprocessing/
│       tokenizer.py
│       cleaner.py
│       chunker.py
│       metadata.py
│
├── embeddings/
│       encoder.py
│       vector_store.py
│       indexer.py
│
├── retrieval/
│       bm25.py
│       semantic.py
│       hybrid.py
│       reranker.py
│
├── generation/
│       prompt_builder.py
│       response_generator.py
│       citations.py
│
├── conversation/
│       memory.py
│       history.py
│
├── pipelines/
│       indexing_pipeline.py
│       search_pipeline.py
│
└── utils/
```

---

# Development Phases

## Phase 1

✅ Document parsing

✅ Chunking

✅ Metadata extraction

---

## Phase 2

✅ BM25 search

✅ Semantic embeddings

✅ FAISS index

---

## Phase 3

✅ Hybrid retrieval

✅ Re-ranking

---

## Phase 4

✅ Context builder

✅ Citation engine

---

## Phase 5

✅ Local LLM integration

or

✅ API-based LLM integration

---

## Phase 6

✅ Conversation memory

✅ Multi-document reasoning

---

## Phase 7

✅ Web/API connectors

✅ Knowledge graph

✅ Cross-source synthesis

---

# Future Enhancements

- OCR for scanned PDFs
- Image understanding
- Table-aware retrieval
- Graph-based knowledge extraction
- Citation confidence scoring
- Document summarization
- Automatic topic clustering
- Research notebook generation
- Timeline extraction
- Knowledge graph visualization
- Cross-document contradiction detection
- Incremental indexing for newly uploaded files
- Multilingual document retrieval
- Voice queries
- Agentic workflows for multi-step research tasks

---

# End Goal

Mnemosyne should evolve into a **local-first, explainable, multi-source research assistant** that enables users to search, compare, and reason across diverse knowledge sources. Every answer should be grounded in retrieved evidence, accompanied by precise citations, and capable of synthesizing information from multiple documents without inventing unsupported facts.