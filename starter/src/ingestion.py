"""Read and normalize source data while preserving source traceability."""
import re
import unicodedata
from pathlib import Path
from typing import Any

from .models import DocumentPage


def load_text(path: Path, document_id: str, source: str,
              metadata: dict[str, Any] | None = None) -> DocumentPage:
    """Load one non-paginated text source as a traceable content unit.

    Sherlock Holmes files are stories/novels rather than PDFs. ``page=1`` is a
    compatibility value for the starter data contract; ``unit_id`` and the
    source path in metadata identify the actual source unit.
    """
    raw = path.read_text(encoding="utf-8-sig")
    details = dict(metadata or {})
    details.setdefault("unit_id", document_id)
    details.setdefault("source_path", source)
    return DocumentPage(
        document_id=document_id,
        source=source,
        page=1,
        text=normalize_text(raw),
        metadata=details,
    )


def load_pdf(path: Path, document_id: str, source: str) -> list[DocumentPage]:
    """TODO: extract each physical page; keep its page number and source.

    Detect and record pages with no text. OCR, when needed, is a separate step.
    """
    raise NotImplementedError("TODO: load_pdf")


def normalize_text(text: str) -> str:
    """Normalize Unicode and line whitespace while keeping paragraph breaks."""
    text = unicodedata.normalize("NFC", text.replace("\r\n", "\n").replace("\r", "\n"))
    paragraphs = []
    for paragraph in re.split(r"\n\s*\n", text):
        cleaned = re.sub(r"[\t\f\v ]+", " ", paragraph)
        cleaned = re.sub(r" *\n *", " ", cleaned).strip()
        if cleaned:
            paragraphs.append(cleaned)
    return "\n\n".join(paragraphs)
