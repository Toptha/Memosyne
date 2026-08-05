"""
engine/embeddings/encoder.py

Wraps a sentence-transformers embedding model. Runs on CPU by
design - the GPU is reserved for the Ollama LLM (Phi-3.5-mini),
and bge-small-en-v1.5 is light enough that CPU embedding is fast
enough for chunk-level indexing and query embedding.
"""

from sentence_transformers import SentenceTransformer

_MODEL_NAME = "BAAI/bge-small-en-v1.5"

# BGE models are trained to expect this prefix on QUERIES (not on
# the documents/chunks being indexed) - it measurably improves
# retrieval quality for this model family. Leave chunk text unprefixed.
_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(_MODEL_NAME, device="cpu")
    return _model


def embed_chunks(texts: list[str]) -> list[list[float]]:
    """
    Embeds a batch of chunk texts (documents being indexed).
    No query prefix - only queries get that treatment.
    """
    model = _get_model()
    vectors = model.encode(
        texts,
        batch_size=16,
        show_progress_bar=len(texts) > 20,
        normalize_embeddings=True,  # cosine similarity via dot product
    )
    return vectors.tolist()


def embed_query(query: str) -> list[float]:
    """
    Embeds a single user query. Applies the BGE query prefix,
    which measurably improves retrieval relevance for this model.
    """
    model = _get_model()
    vector = model.encode(
        _QUERY_PREFIX + query,
        normalize_embeddings=True,
    )
    return vector.tolist()


if __name__ == "__main__":
    sample_chunks = [
        "The introduction states the purpose and general problem of the study.",
        "This section analyses existing research and publications on the topic.",
    ]
    vectors = embed_chunks(sample_chunks)
    print(f"Embedded {len(vectors)} chunks, each of dimension {len(vectors[0])}")

    q_vec = embed_query("What does the introduction cover?")
    print(f"Query embedding dimension: {len(q_vec)}")