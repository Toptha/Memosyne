"""
engine/embeddings/vector_store.py

Wraps Chroma as a persistent local vector store for chunk
embeddings. No separate server needed - Chroma writes to a
folder on disk, so the index survives between app runs.
"""

import chromadb
from pathlib import Path

_DEFAULT_PERSIST_DIR = str(Path(__file__).resolve().parent.parent.parent / "data" / "vector_store")
_COLLECTION_NAME = "mnemosyne_chunks"

_client = None
_collection = None


def _get_collection():
    global _client, _collection
    if _collection is None:
        Path(_DEFAULT_PERSIST_DIR).mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=_DEFAULT_PERSIST_DIR)
        _collection = _client.get_or_create_collection(
            name=_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def add_chunks(chunks: list, embeddings: list[list[float]]) -> None:
    """
    Adds chunks + their precomputed embeddings to the store.

    `chunks` is a list of Chunk objects from chunker.py (needs
    .chunk_id, .text, .document_id, .page_start, .page_end, .section).
    Embeddings must be pre-computed via encoder.embed_chunks() and
    line up 1:1 with `chunks` by index.
    """
    if not chunks:
        return

    collection = _get_collection()

    collection.upsert(
        ids=[c.chunk_id for c in chunks],
        embeddings=embeddings,
        documents=[c.text for c in chunks],
        metadatas=[
            {
                "document_id": c.document_id,
                "page_start": c.page_start,
                "page_end": c.page_end,
                "section": c.section or "",
            }
            for c in chunks
        ],
    )


def query(query_embedding: list[float], top_k: int = 5, document_id: str | None = None) -> list[dict]:
    """
    Returns the top_k most similar chunks to the query embedding.
    Optionally restrict to a single document_id (metadata filter).

    Each result dict has: chunk_id, text, document_id, page_start,
    page_end, section, distance (lower = more similar, since we're
    using cosine distance).
    """
    collection = _get_collection()

    where_filter = {"document_id": document_id} if document_id else None

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_filter,
    )

    output = []
    ids = results["ids"][0]
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for i in range(len(ids)):
        meta = metadatas[i]
        output.append(
            {
                "chunk_id": ids[i],
                "text": documents[i],
                "document_id": meta.get("document_id"),
                "page_start": meta.get("page_start"),
                "page_end": meta.get("page_end"),
                "section": meta.get("section") or None,
                "distance": distances[i],
            }
        )

    return output


def delete_document(document_id: str) -> None:
    """Removes all chunks belonging to a given document (e.g. on re-upload/delete)."""
    collection = _get_collection()
    collection.delete(where={"document_id": document_id})


def count() -> int:
    """Total number of chunks currently stored."""
    return _get_collection().count()


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "parsing"))
    from loader import load_pdf
    from chunker import chunk_document
    from encoder import embed_chunks, embed_query

    if len(sys.argv) < 2:
        print("Usage: python vector_store.py <path_to_pdf> [query]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    test_query = sys.argv[2] if len(sys.argv) > 2 else "What does the introduction cover?"

    parsed = load_pdf(pdf_path)
    chunks = chunk_document(parsed)
    print(f"Parsed {len(chunks)} chunks from {parsed.filename}")

    texts = [c.metadata["text_with_heading"] for c in chunks]
    vectors = embed_chunks(texts)

    add_chunks(chunks, vectors)
    print(f"Stored. Total chunks in index: {count()}")

    q_vec = embed_query(test_query)
    results = query(q_vec, top_k=3)

    print(f"\nTop {len(results)} results for query: '{test_query}'\n")
    for r in results:
        print(f"[{r['chunk_id']}] section: {r['section']} | pages {r['page_start']}-{r['page_end']} | distance: {r['distance']:.4f}")
        print(r["text"][:150].replace("\n", " "))
        print("---")