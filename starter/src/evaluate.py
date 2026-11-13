"""Run one fixed benchmark split and save top-3 traces plus metrics."""
import argparse
import csv
import json
from pathlib import Path
from typing import Any

from .embeddings import MyEmbedder
from .evaluation import evaluate_query, summarize
from .store import ChromaStore


def load_questions(path: Path, split: str) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        questions = [row for row in csv.DictReader(stream) if row["split"] == split]
    if not questions:
        raise ValueError(f"No questions found for split={split!r} in {path}")
    for question in questions:
        question["gold_char_start"] = int(question["gold_char_start"])
        question["gold_char_end"] = int(question["gold_char_end"])
        if question["evidence_checked"].lower() != "true":
            raise ValueError(f"Evidence has not been checked for {question['question_id']}")
    return questions


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=("dev", "test"), default="dev")
    args = parser.parse_args()

    starter_dir = Path(__file__).resolve().parents[1]
    data_dir = starter_dir / "data"
    results_dir = starter_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    questions = load_questions(data_dir / "benchmark_questions.csv", args.split)
    embedder = MyEmbedder("all-MiniLM-L6-v2")
    store = ChromaStore(starter_dir / "chroma_db", dimensions=embedder.dimensions)

    traces = []
    for question in questions:
        query_vector = embedder.embed_query(question["question"])
        for strategy in ("A", "B", "C"):
            applied_filter = None
            if strategy == "C" and question.get("filter_field"):
                applied_filter = {question["filter_field"]: question["filter_value"]}
            hits = store.search(strategy, query_vector, top_k=3, filters=applied_filter)
            evaluated = evaluate_query(question, hits)
            evaluated.update({
                "strategy": strategy,
                "embedding_model": embedder.model_name,
                "filter_applied": applied_filter,
            })
            traces.append(evaluated)
        print(f"[{args.split}] {question['question_id']} retrieved for A/B/C")

    trace_path = results_dir / f"{args.split}_traces.jsonl"
    with trace_path.open("w", encoding="utf-8", newline="\n") as stream:
        for trace in traces:
            stream.write(json.dumps(trace, ensure_ascii=False) + "\n")

    summary = summarize(traces)
    summary_path = results_dir / f"{args.split}_retrieval_metrics.csv"
    if summary:
        with summary_path.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(summary[0]))
            writer.writeheader()
            writer.writerows(summary)

    print(f"Saved full traces: {trace_path}")
    print(f"Saved retrieval metrics: {summary_path}")
    for row in summary:
        print(
            f"{row['strategy']} {row['split']}: "
            f"Hit@1 {row['hit_at_1_count']}/{row['question_count']}; "
            f"Evidence Hit@3 {row['evidence_hit_at_3_count']}/{row['question_count']}"
        )


if __name__ == "__main__":
    main()
