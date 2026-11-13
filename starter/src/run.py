"""Ingest the Sherlock Holmes corpus into the three lab collections.

This phase builds A (fixed chunks), B (paragraph chunks), and C (the same
paragraph chunks with metadata available for filtered retrieval). Benchmark
question loading and evaluation are added in a later lab step.
"""
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

from .chunking import by_paragraph, fixed_size
from .embeddings import MyEmbedder
from .ingestion import load_text
from .store import ChromaStore


def main() -> None:
    starter_dir = Path(__file__).resolve().parents[1]
    project_root = starter_dir.parent
    manifest_path = starter_dir / "data" / "corpus_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    entries = manifest["units"]
    if len(entries) < 30:
        raise ValueError(f"Expected at least 30 content units; found {len(entries)}")

    run_started_at = datetime.now(timezone.utc).isoformat()
    ingest_started = perf_counter()
    embedder = MyEmbedder("all-MiniLM-L6-v2")
    store = ChromaStore(starter_dir / "chroma_db", dimensions=embedder.dimensions)
    totals = {"A": 0, "B": 0, "C": 0}

    for index, entry in enumerate(entries, start=1):
        source_path = (project_root / entry["source_path"]).resolve()
        if not source_path.is_relative_to(project_root) or not source_path.is_file():
            raise FileNotFoundError(f"Manifest source is missing or outside project: {source_path}")
        relative_source = source_path.relative_to(project_root).as_posix()
        document_type = {"stories": "story", "novels": "novel"}.get(
            source_path.parent.name, source_path.parent.name
        )
        doc = load_text(
            source_path,
            document_id=entry["source_id"],
            source=relative_source,
            metadata={
                "unit_id": entry["unit_id"],
                "title": entry["title"],
                "document_type": document_type,
            },
        )
        if len(doc.text) < manifest["unit_requirement_characters"]:
            raise ValueError(f"Source unit is below the character threshold: {entry['source_id']}")

        chunks_a = fixed_size(doc, size=1000, overlap=150)
        chunks_b = by_paragraph(doc, max_size=1000)
        vectors_a = embedder.embed_documents([chunk.text for chunk in chunks_a])
        store.upsert("A", chunks_a, vectors_a)
        totals["A"] += len(chunks_a)
        vectors_b = embedder.embed_documents([chunk.text for chunk in chunks_b])
        store.upsert("B", chunks_b, vectors_b)
        store.upsert("C", chunks_b, vectors_b)
        totals["B"] += len(chunks_b)
        totals["C"] += len(chunks_b)
        print(f"[{index}/{len(entries)}] {entry['source_id']}: A={len(chunks_a)}, B/C={len(chunks_b)}")

    elapsed_seconds = perf_counter() - ingest_started
    print(f"Embedding model: {embedder.model_name} ({embedder.dimensions} dimensions)")
    for strategy, count in totals.items():
        print(f"Collection {strategy}: {count} chunks")
    print(f"Chroma data directory: {starter_dir / 'chroma_db'}")
    print(f"Ingest elapsed: {elapsed_seconds:.1f} seconds ({elapsed_seconds / 60:.1f} minutes)")

    results_dir = starter_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    log_path = results_dir / "ingest_runs.csv"
    log_exists = log_path.exists()
    with log_path.open("a", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=[
            "run_started_at_utc", "source_units", "model", "dimensions",
            "collection_a_chunks", "collection_b_chunks", "collection_c_chunks",
            "elapsed_seconds",
        ])
        if not log_exists:
            writer.writeheader()
        writer.writerow({
            "run_started_at_utc": run_started_at,
            "source_units": len(entries),
            "model": embedder.model_name,
            "dimensions": embedder.dimensions,
            "collection_a_chunks": totals["A"],
            "collection_b_chunks": totals["B"],
            "collection_c_chunks": totals["C"],
            "elapsed_seconds": round(elapsed_seconds, 2),
        })
    print(f"Ingest timing log: {log_path}")


if __name__ == "__main__":
    main()
