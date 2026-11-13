"""Fixed-size and paragraph-aware chunking with stable source positions."""
from .models import Chunk, DocumentPage


def _make_chunk(page: DocumentPage, text: str, start: int, end: int,
                strategy: str, ordinal: int) -> Chunk:
    metadata = dict(page.metadata)
    metadata.update({
        "char_start": start,
        "char_end": end,
        "chunk_strategy": strategy,
    })
    return Chunk(
        chunk_id=f"{page.document_id}:{strategy}:{ordinal:05d}",
        document_id=page.document_id,
        source=page.source,
        page=page.page,
        text=text,
        metadata=metadata,
    )


def _windows(text: str, size: int, overlap: int) -> list[tuple[int, int]]:
    if size <= 0:
        raise ValueError("size must be positive")
    if overlap < 0 or overlap >= size:
        raise ValueError("overlap must be non-negative and smaller than size")
    spans = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        spans.append((start, end))
        if end == len(text):
            break
        start = end - overlap
    return spans


def fixed_size(page: DocumentPage, size: int, overlap: int) -> list[Chunk]:
    """Split into character windows and retain exact source character offsets."""
    return [
        _make_chunk(page, page.text[start:end], start, end, "fixed", i)
        for i, (start, end) in enumerate(_windows(page.text, size, overlap))
    ]


def by_paragraph(page: DocumentPage, max_size: int) -> list[Chunk]:
    """Pack whole paragraphs up to max_size; split only oversized paragraphs."""
    if max_size <= 0:
        raise ValueError("max_size must be positive")

    paragraphs = []
    cursor = 0
    for part in page.text.split("\n\n"):
        start = page.text.find(part, cursor)
        end = start + len(part)
        if part:
            paragraphs.append((part, start, end))
        cursor = end + 2

    spans: list[tuple[int, int]] = []
    group_start = group_end = None
    for paragraph, start, end in paragraphs:
        if len(paragraph) > max_size:
            prefix_length = start - group_start if group_start is not None else 0
            if group_start is not None and prefix_length <= max_size // 3:
                # Attach a short title/heading run to the start of the long paragraph.
                first_end = start + min(len(paragraph), max_size - prefix_length)
                spans.append((group_start, first_end))
                group_start = group_end = None
                consumed = first_end - start
            else:
                if group_start is not None:
                    spans.append((group_start, group_end))
                    group_start = group_end = None
                consumed = 0
            spans.extend(
                (start + consumed + a, start + consumed + b)
                for a, b in _windows(paragraph[consumed:], max_size, 0)
            )
            continue
        proposed_end = end
        if group_start is None:
            group_start, group_end = start, proposed_end
        elif proposed_end - group_start <= max_size:
            group_end = proposed_end
        else:
            spans.append((group_start, group_end))
            group_start, group_end = start, proposed_end
    if group_start is not None:
        spans.append((group_start, group_end))

    return [
        _make_chunk(page, page.text[start:end], start, end, "paragraph", i)
        for i, (start, end) in enumerate(spans)
    ]
