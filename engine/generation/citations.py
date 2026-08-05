"""
engine/generation/citations.py

Parses the [1], [2]-style citation markers the LLM was instructed
to use, and maps them back to real chunk metadata (document,
section, page) so the UI can display a proper source list.
"""

import re


def extract_citations(answer_text: str, used_chunks: list[dict]) -> list[dict]:
    """
    used_chunks: the list returned by prompt_builder.build_prompt()
    (each chunk dict has a 'ref_number' matching its [n] label in
    the prompt).

    Returns a list of source dicts, one per DISTINCT [n] the model
    actually referenced in its answer - not every chunk that was
    in context, only the ones cited. Order matches first appearance
    in the answer text.
    """
    cited_numbers = _find_cited_numbers(answer_text)

    ref_lookup = {c["ref_number"]: c for c in used_chunks}

    sources = []
    for n in cited_numbers:
        chunk = ref_lookup.get(n)
        if chunk is None:
            continue  # model hallucinated a ref number that wasn't in context
        sources.append(
            {
                "ref_number": n,
                "document_id": chunk["document_id"],
                "section": chunk.get("section"),
                "page_start": chunk["page_start"],
                "page_end": chunk["page_end"],
                "chunk_id": chunk["chunk_id"],
            }
        )

    return sources


def _find_cited_numbers(answer_text: str) -> list[int]:
    """Finds [n] markers in order of first appearance, deduplicated."""
    matches = re.findall(r"\[(\d+)\]", answer_text)
    seen = []
    for m in matches:
        n = int(m)
        if n not in seen:
            seen.append(n)
    return seen


def format_sources_block(sources: list[dict]) -> str:
    """
    Produces a human-readable 'Sources' block for display below the
    answer, matching the README's citation format.
    """
    if not sources:
        return ""

    lines = ["", "Sources:"]
    for s in sources:
        page_range = (
            f"Page {s['page_start']}"
            if s["page_start"] == s["page_end"]
            else f"Pages {s['page_start']}-{s['page_end']}"
        )
        section = f", Section: {s['section']}" if s.get("section") else ""
        lines.append(f"[{s['ref_number']}] {s['document_id']} - {page_range}{section}")

    return "\n".join(lines)


if __name__ == "__main__":
    fake_answer = "Refunds take 5-7 business days [1]. Returns are allowed within 30 days [2]."
    fake_used_chunks = [
        {"ref_number": 1, "document_id": "policy.pdf", "section": "Refunds", "page_start": 3, "page_end": 3, "chunk_id": "policy_chunk_3"},
        {"ref_number": 2, "document_id": "policy.pdf", "section": "Returns", "page_start": 2, "page_end": 2, "chunk_id": "policy_chunk_2"},
    ]

    sources = extract_citations(fake_answer, fake_used_chunks)
    print(sources)
    print(format_sources_block(sources))