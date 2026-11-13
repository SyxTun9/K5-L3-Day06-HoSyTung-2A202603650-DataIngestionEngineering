import json
import csv
from pathlib import Path

# Load benchmark questions
questions = {}
with open("starter/data/benchmark_questions.csv", "r", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        questions[row["question_id"]] = row

# Load test traces
traces = []
with open("starter/results/test_traces.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        traces.append(json.loads(line))

print(f"Loaded {len(traces)} traces.")

for t in traces:
    qid = t["question_id"]
    strat = t["strategy"]
    q = questions[qid]
    print("=" * 80)
    print(f"[{qid}] [Strategy {strat}]")
    print(f"Question: {t['question']}")
    print(f"Expected Answer: {t['expected_answer']}")
    print(f"Gold Source: {t['gold_source_id']} [{t['gold_char_start']}:{t['gold_char_end']}]")
    print(f"Gold Evidence Quote:\n{q['evidence_quote']}")
    print(f"Filter Applied: {t.get('filter_applied')}")
    print(f"Eval: Hit@1={t['hit_at_1']}, Evidence Hit@3={t['evidence_hit_at_3']}")
    print("-" * 40)
    for hit in t["hits"]:
        rank = hit["rank"]
        cid = hit["chunk_id"]
        meta = hit["metadata"]
        text = hit["text"]
        print(f"Rank {rank}: {cid}")
        print(f"  doc_id={meta.get('document_id')}, unit_id={meta.get('unit_id')}, source={meta.get('source')}, page={meta.get('page')}, type={meta.get('document_type')}")
        print(f"  char_range=[{meta.get('char_start')}, {meta.get('char_end')}] (len={len(text)})")
        print(f"  gold_source_match={hit.get('gold_source_match')}, gold_evidence_match={hit.get('gold_evidence_match')}")
        print(f"  text:\n{text}\n")
