"""
engine/parsing/chunker.py

Takes the TextBlocks produced by loader.py and groups them into
retrieval-ready chunks. Chunking is heading-aware: whenever we hit
a heading block, we start a new chunk and carry the heading along
as context for every block underneath it, until the next heading.

Long sections still get split further so no single chunk blows past
a configurable size limit, but we split on paragraph boundaries
(never mid-sentence) whenever possible.
"""

import re
from dataclasses import dataclass, field

try:
    from .loader import TextBlock, ParsedDocument  # when imported as a package: parsing.chunker
except ImportError:
    from loader import TextBlock, ParsedDocument  # when run directly: python chunker.py


@dataclass
class Chunk:
    chunk_id: str
    document_id: str
    text: str
    page_start: int
    page_end: int
    section: str | None        # nearest heading above this chunk, if any
    metadata: dict = field(default_factory=dict)


# --- heading detection -----------------------------------------------

def _looks_like_heading(text: str) -> bool:
    """
    Heuristic heading check - no font-size info available from the
    loader's blocks, so we rely on textual patterns instead:
      - short line (headings are rarely long sentences)
      - mostly uppercase, OR title-case without ending punctuation
      - doesn't end in a period (headings usually don't)
    """
    stripped = text.strip()
    if len(stripped) == 0 or len(stripped) > 80:
        return False
    if stripped.endswith((".", ",", ";")):
        return False

    words = stripped.split()
    if len(words) > 10:
        return False

    is_upper = stripped.upper() == stripped and any(c.isalpha() for c in stripped)
    is_title_case = stripped == stripped.title()

    # headings sometimes carry a lowercase parenthetical note, e.g.
    # "DISCUSSION (this section is optional, but encouraged)" - check
    # the leading segment before any "(" on its own too.
    lead = stripped.split("(")[0].strip()
    lead_is_upper = lead.upper() == lead and any(c.isalpha() for c in lead) and len(lead) >= 3

    return is_upper or is_title_case or lead_is_upper


# --- paragraph-safe splitting for oversized sections -------------------

def _split_on_sentence_boundary(text: str, max_chars: int) -> list[str]:
    """
    Splits text into pieces <= max_chars, breaking on sentence
    boundaries (never mid-sentence) where possible.
    """
    if len(text) <= max_chars:
        return [text]

    sentences = re.split(r"(?<=[.!?])\s+", text)
    pieces, current = [], ""

    for sentence in sentences:
        candidate = f"{current} {sentence}".strip() if current else sentence
        if len(candidate) > max_chars and current:
            pieces.append(current)
            current = sentence
        else:
            current = candidate

    if current:
        pieces.append(current)

    return pieces


# --- main chunking logic -----------------------------------------------

def chunk_document(
    parsed: ParsedDocument,
    max_chunk_chars: int = 1000,
    min_chunk_chars: int = 100,
) -> list[Chunk]:
    """
    Groups a document's blocks into heading-aware chunks.

    Strategy:
      1. Walk blocks in order. A block that looks like a heading
         becomes the "current section" label and is NOT itself
         emitted as a standalone chunk (it gets prefixed onto the
         next chunk instead, so retrieval keeps the heading as
         context).
      2. Accumulate non-heading blocks under the current section
         until adding another block would exceed max_chunk_chars,
         then flush as a chunk and start a new one.
      3. A single oversized block gets split on sentence boundaries.
      4. Tiny trailing chunks (< min_chunk_chars) get merged into
         the previous chunk instead of staying as their own scrap.
    """
    chunks: list[Chunk] = []
    current_section: str | None = None
    buffer_text = ""
    buffer_page_start: int | None = None
    buffer_page_end: int | None = None
    chunk_counter = 0

    def flush():
        nonlocal buffer_text, buffer_page_start, buffer_page_end, chunk_counter
        if not buffer_text.strip():
            buffer_text = ""
            buffer_page_start = None
            buffer_page_end = None
            return

        # merge into previous chunk if this one is too small to stand alone
        if (
            chunks
            and len(buffer_text) < min_chunk_chars
            and chunks[-1].section == current_section
        ):
            prev = chunks[-1]
            prev.text = f"{prev.text}\n\n{buffer_text}".strip()
            prev.page_end = buffer_page_end
        else:
            chunk_counter += 1
            chunks.append(
                Chunk(
                    chunk_id=f"{parsed.document_id}_chunk_{chunk_counter}",
                    document_id=parsed.document_id,
                    text=buffer_text.strip(),
                    page_start=buffer_page_start,
                    page_end=buffer_page_end,
                    section=current_section,
                )
            )

        buffer_text = ""
        buffer_page_start = None
        buffer_page_end = None

    for block in parsed.blocks:
        if _looks_like_heading(block.text):
            flush()
            current_section = block.text.strip()
            continue

        # oversized single block: split first, flush existing buffer
        if len(block.text) > max_chunk_chars:
            flush()
            pieces = _split_on_sentence_boundary(block.text, max_chunk_chars)
            for piece in pieces:
                chunk_counter += 1
                chunks.append(
                    Chunk(
                        chunk_id=f"{parsed.document_id}_chunk_{chunk_counter}",
                        document_id=parsed.document_id,
                        text=piece.strip(),
                        page_start=block.page_number,
                        page_end=block.page_number,
                        section=current_section,
                    )
                )
            continue

        candidate_len = len(buffer_text) + len(block.text) + 2
        if candidate_len > max_chunk_chars and buffer_text:
            flush()

        if buffer_page_start is None:
            buffer_page_start = block.page_number
        buffer_page_end = block.page_number
        buffer_text = f"{buffer_text}\n\n{block.text}".strip()

    flush()

    # attach a heading-prefixed version for embedding/generation use,
    # while keeping .text as the clean body (metadata carries both)
    for c in chunks:
        c.metadata["text_with_heading"] = (
            f"{c.section}\n{c.text}" if c.section else c.text
        )

    return chunks


if __name__ == "__main__":
    import sys
    from loader import load_pdf

    if len(sys.argv) < 2:
        print("Usage: python chunker.py <path_to_pdf>")
        sys.exit(1)

    parsed = load_pdf(sys.argv[1])
    chunks = chunk_document(parsed)

    print(f"Document: {parsed.filename}")
    print(f"Blocks: {len(parsed.blocks)}  ->  Chunks: {len(chunks)}\n")

    for c in chunks:
        print(f"[{c.chunk_id}] pages {c.page_start}-{c.page_end} | section: {c.section}")
        print(c.text[:150].replace("\n", " "))
        print("---")