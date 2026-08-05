"""
engine/parsing/loader.py

Loads a PDF and extracts text preserving page + block structure,
so downstream chunking can stay heading/paragraph-aware and
citations can point to an exact page.
"""

import fitz  # PyMuPDF
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class TextBlock:
    """One block of text as PyMuPDF sees it (roughly a paragraph)."""
    text: str
    page_number: int          # 1-indexed, human-friendly
    block_index: int          # order of block within the page
    bbox: tuple                # (x0, y0, x1, y1) - useful later for tables/layout


@dataclass
class ParsedDocument:
    document_id: str
    filename: str
    blocks: list[TextBlock] = field(default_factory=list)

    @property
    def full_text(self) -> str:
        return "\n\n".join(b.text for b in self.blocks)


def _normalize(text: str) -> str:
    """
    Normalizes a block's text for repetition comparison. Strips
    whitespace and digits (page numbers change per page, e.g.
    'Page 3' vs 'Page 4', but the surrounding text is identical) so
    near-identical repeated headers/footers still match.
    """
    collapsed = " ".join(text.split())
    return "".join(ch for ch in collapsed if not ch.isdigit()).strip().lower()


def load_pdf(filepath: str, document_id: str | None = None) -> ParsedDocument:
    """
    Extracts text from a PDF, block by block, with page numbers attached.

    We use block-level extraction (not raw page.get_text()) because
    it gives us natural paragraph boundaries for free, which the
    chunker in Stage 2 will rely on.

    Header/footer detection: rather than filtering by position alone
    (which wrongly drops one-off titles near the top of page 1), we
    filter only short top/bottom blocks whose (digit-stripped) text
    repeats across multiple pages - that repetition is the actual
    signature of a running header/footer, e.g. a page number or a
    running title bar.
    """
    path = Path(filepath)
    if document_id is None:
        document_id = path.stem

    doc = fitz.open(filepath)
    total_pages = doc.page_count

    # Pass 1: collect every candidate block, and separately tally how
    # many distinct pages each normalized short top/bottom text appears on.
    raw_blocks = []  # list of (page_number, block_index, text, bbox, is_top_or_bottom)
    repeat_counts: dict[str, set[int]] = {}

    for page_number, page in enumerate(doc, start=1):
        page_height = page.rect.height
        # get_text("blocks") returns list of tuples:
        # (x0, y0, x1, y1, text, block_no, block_type)
        blocks = page.get_text("blocks")

        for block_index, b in enumerate(blocks):
            x0, y0, x1, y1, text, *_ = b
            text = text.strip()
            if not text:
                continue

            is_top_or_bottom = y0 < 40 or y1 > page_height - 40
            raw_blocks.append((page_number, block_index, text, (x0, y0, x1, y1), is_top_or_bottom))

            if is_top_or_bottom and len(text) < 60:
                key = _normalize(text)
                repeat_counts.setdefault(key, set()).add(page_number)

    # A block counts as a real header/footer only if its normalized text
    # shows up on multiple pages (or on every page, for single/short docs).
    # Threshold: appears on at least 2 pages if the doc has 2+ pages.
    repeat_threshold = 2 if total_pages > 1 else 999  # single-page docs: never filter
    header_footer_keys = {
        key for key, pages in repeat_counts.items() if len(pages) >= repeat_threshold
    }

    # Pass 2: build final block list, dropping only confirmed repeats.
    parsed = ParsedDocument(document_id=document_id, filename=path.name)
    for page_number, block_index, text, bbox, is_top_or_bottom in raw_blocks:
        if is_top_or_bottom and len(text) < 60:
            if _normalize(text) in header_footer_keys:
                continue

        parsed.blocks.append(
            TextBlock(
                text=text,
                page_number=page_number,
                block_index=block_index,
                bbox=bbox,
            )
        )

    doc.close()
    return parsed


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python loader.py <path_to_pdf>")
        sys.exit(1)

    result = load_pdf(sys.argv[1])
    print(f"Document: {result.filename} ({result.document_id})")
    print(f"Total blocks extracted: {len(result.blocks)}")
    print("\n--- First 3 blocks ---\n")
    for b in result.blocks[:3]:
        print(f"[Page {b.page_number}, block {b.block_index}]")
        print(b.text[:200])
        print("---")