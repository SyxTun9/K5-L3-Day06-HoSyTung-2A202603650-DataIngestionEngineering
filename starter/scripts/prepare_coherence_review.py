"""Create a fixed 10-position manual chunk-coherence review sheet."""
import csv
import json
from pathlib import Path
import sys

import chromadb

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.ingestion import load_text


def main() -> None:
    starter_dir = Path(__file__).resolve().parents[1]
    project_root = starter_dir.parent
    manifest = json.loads(
        (starter_dir / "data" / "corpus_manifest.json").read_text(encoding="utf-8-sig")
    )
    entries = sorted(manifest["units"], key=lambda item: item["source_id"])[:10]
    client = chromadb.PersistentClient(path=str(starter_dir / "chroma_db"))
    collection_names = {"A": "day6_a", "B": "day6_b", "C": "day6_c"}
    output_path = starter_dir / "results" / "chunk_coherence_review.csv"
    rows = []

    for sample_number, entry in enumerate(entries, start=1):
        source_path = (project_root / entry["source_path"]).resolve()
        doc = load_text(source_path, entry["source_id"], entry["source_path"])
        position = len(doc.text) // 2

        for strategy, collection_name in collection_names.items():
            collection = client.get_collection(name=collection_name)
            records = collection.get(
                where={"document_id": entry["source_id"]},
                include=["documents", "metadatas"],
            )
            candidates = []
            for chunk_id, text, metadata in zip(
                records["ids"], records["documents"], records["metadatas"]
            ):
                start = int(metadata["char_start"])
                end = int(metadata["char_end"])
                distance = 0 if start <= position < end else min(
                    abs(position - start), abs(position - end)
                )
                candidates.append((distance, abs((start + end) / 2 - position), chunk_id, text, metadata))
            if not candidates:
                raise ValueError(f"No stored chunks for {entry['source_id']} in {strategy}")
            _, _, chunk_id, text, metadata = min(candidates, key=lambda item: (item[0], item[1]))
            rows.append({
                "sample_id": f"S{sample_number:02d}",
                "source_id": entry["source_id"],
                "title": entry["title"],
                "sample_char_position": position,
                "sampling_rule": "First 10 source IDs sorted; normalized text midpoint",
                "strategy": strategy,
                "chunk_id": chunk_id,
                "chunk_char_start": metadata["char_start"],
                "chunk_char_end": metadata["char_end"],
                "chunk_text": text,
                "coherence_score_0_1_2": "",
                "reason": "",
                "reviewer": "",
            })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Prepared {len(rows)} review rows ({len(entries)} shared source positions)")
    print(output_path)


if __name__ == "__main__":
    main()
