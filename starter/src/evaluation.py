"""Evidence retrieval metrics and full, auditable retrieval traces."""
from collections import defaultdict
import re
import unicodedata
from typing import Any


def normalize_for_match(text: str) -> str:
    """Match the corpus text normalization while preserving paragraph breaks."""
    text = unicodedata.normalize("NFC", text.replace("\r\n", "\n").replace("\r", "\n"))
    paragraphs = []
    for paragraph in re.split(r"\n\s*\n", text):
        cleaned = re.sub(r"[\t\f\v ]+", " ", paragraph)
        cleaned = re.sub(r" *\n *", " ", cleaned).strip()
        if cleaned:
            paragraphs.append(cleaned)
    return "\n\n".join(paragraphs)


def evaluate_query(question: dict[str, Any], hits: list[dict[str, Any]]) -> dict[str, Any]:
    """Mark exact source/evidence hits; this does not replace manual labels."""
    gold_source = question["gold_source_id"]
    gold_evidence = normalize_for_match(question["evidence_quote"])
    gold_start = int(question["gold_char_start"])
    gold_end = int(question["gold_char_end"])
    annotated_hits = []
    for rank, hit in enumerate(hits, start=1):
        metadata = hit.get("metadata") or {}
        source_match = metadata.get("document_id") == gold_source
        text_match = gold_evidence in normalize_for_match(hit.get("text", ""))
        try:
            offset_match = (
                int(metadata.get("char_start", -1)) <= gold_start
                and int(metadata.get("char_end", -1)) >= gold_end
            )
        except (TypeError, ValueError):
            offset_match = False
        evidence_match = source_match and (text_match or offset_match)
        annotated_hits.append({
            **hit,
            "rank": rank,
            "gold_source_match": source_match,
            "gold_evidence_match": evidence_match,
        })

    hit1 = bool(annotated_hits and annotated_hits[0]["gold_evidence_match"])
    hit3 = any(hit["gold_evidence_match"] for hit in annotated_hits[:3])
    return {
        "question_id": question["question_id"],
        "split": question["split"],
        "question": question["question"],
        "expected_answer": question["expected_answer"],
        "gold_source_id": gold_source,
        "gold_char_start": gold_start,
        "gold_char_end": gold_end,
        "filter_field": question.get("filter_field", ""),
        "filter_value": question.get("filter_value", ""),
        "hits": annotated_hits,
        "hit_at_1": int(hit1),
        "evidence_hit_at_3": int(hit3),
    }


def summarize(traces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate retrieval and C-filter compliance by strategy and split."""
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for trace in traces:
        groups[(trace["strategy"], trace["split"])].append(trace)

    summary = []
    for (strategy, split), rows in sorted(groups.items()):
        total = len(rows)
        hit1 = sum(row["hit_at_1"] for row in rows)
        hit3 = sum(row["evidence_hit_at_3"] for row in rows)
        filter_rows = [row for row in rows if row.get("filter_field")]
        filter_compliant = sum(
            bool(row["hits"]) and all(
                hit.get("metadata", {}).get(row["filter_field"]) == row["filter_value"]
                for hit in row["hits"]
            )
            for row in filter_rows
        )
        summary.append({
            "strategy": strategy,
            "split": split,
            "question_count": total,
            "hit_at_1_count": hit1,
            "hit_at_1_rate": hit1 / total if total else 0.0,
            "evidence_hit_at_3_count": hit3,
            "evidence_hit_at_3_rate": hit3 / total if total else 0.0,
            "filter_question_count": len(filter_rows) if strategy == "C" else "",
            "filter_compliant_count": filter_compliant if strategy == "C" else "",
            "filter_compliance_rate": (
                filter_compliant / len(filter_rows)
                if strategy == "C" and filter_rows else ""
            ),
        })
    return summary
