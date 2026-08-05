"""
engine/pipelines/indexing_pipeline.py

Ingests one or more PDFs into the vector store: parse -> chunk ->
embed -> store, per file. Built so the PyQt upload flow can call
this directly with whatever files the user selects, and so one
bad/corrupt file doesn't take down the whole batch.
"""

import hashlib
from pathlib import Path

try:
    from ..parsing.loader import load_pdf
    from ..parsing.chunker import chunk_document
    from ..embeddings.encoder import embed_chunks
    from ..embeddings.vector_store import add_chunks, delete_document
except ImportError:
    # allows running this file directly for quick testing
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "parsing"))
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "embeddings"))
    from loader import load_pdf
    from chunker import chunk_document
    from encoder import embed_chunks
    from vector_store import add_chunks, delete_document

SUPPORTED_EXTENSIONS = {".pdf"}  # extend as DOCX/TXT/MD loaders get added


def _make_document_id(filepath: Path) -> str:
    """
    Builds a stable, collision-resistant document_id from the
    filename plus a short hash of the file's contents. Using
    content (not just the name) means two different files named
    "notes.pdf" get distinct IDs, while re-uploading the exact same
    file re-uses the same ID (so upsert overwrites cleanly instead
    of duplicating).
    """
    content_hash = hashlib.sha1(filepath.read_bytes()).hexdigest()[:8]
    safe_stem = "".join(c if c.isalnum() or c in "-_" else "_" for c in filepath.stem)
    return f"{safe_stem}_{content_hash}"


def ingest_file(filepath: str) -> dict:
    """
    Ingests a single file. Returns a status dict:
      { "filename": ..., "document_id": ..., "status": "ok"|"error",
        "chunk_count": int, "error": str|None }

    Never raises - callers (like ingest_files) can loop over many
    files and this failing on one won't crash the batch.
    """
    path = Path(filepath)
    result = {
        "filename": path.name,
        "document_id": None,
        "status": "error",
        "chunk_count": 0,
        "error": None,
    }

    if not path.exists():
        result["error"] = "File not found."
        return result

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        result["error"] = f"Unsupported file type '{path.suffix}'. Only PDF is supported right now."
        return result

    try:
        document_id = _make_document_id(path)
        result["document_id"] = document_id

        # if this exact file was ingested before, clear its old chunks
        # first so re-uploads don't accumulate stale duplicates under
        # a slightly different chunking pass
        delete_document(document_id)

        parsed = load_pdf(str(path), document_id=document_id)
        chunks = chunk_document(parsed)

        if not chunks:
            result["error"] = "No extractable text found in this PDF (it may be scanned/image-only)."
            return result

        texts = [c.metadata["text_with_heading"] for c in chunks]
        vectors = embed_chunks(texts)
        add_chunks(chunks, vectors)

        result["status"] = "ok"
        result["chunk_count"] = len(chunks)

    except Exception as e:
        result["error"] = str(e)

    return result


def ingest_files(filepaths: list[str]) -> list[dict]:
    """
    Ingests multiple files sequentially, one at a time. Returns a
    list of per-file result dicts (see ingest_file). Sequential
    (not parallel) on purpose - embedding is CPU-bound on this
    hardware, and running several at once would just fight over
    the same cores without a real speedup.
    """
    return [ingest_file(fp) for fp in filepaths]


def ingest_directory(dir_path: str) -> list[dict]:
    """Ingests every supported file found directly inside a folder (non-recursive)."""
    folder = Path(dir_path)
    filepaths = [
        str(p) for p in sorted(folder.iterdir())
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    return ingest_files(filepaths)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python indexing_pipeline.py <file1.pdf> [file2.pdf ...]")
        sys.exit(1)

    results = ingest_files(sys.argv[1:])

    print(f"\nIngested {len(results)} file(s):\n")
    for r in results:
        if r["status"] == "ok":
            print(f"  OK   {r['filename']}  ({r['chunk_count']} chunks)  -> document_id={r['document_id']}")
        else:
            print(f"  FAIL {r['filename']}  -> {r['error']}")