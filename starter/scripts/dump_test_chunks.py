import sys
import json
import csv
from pathlib import Path

traces = []
with open("starter/results/test_traces.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        traces.append(json.loads(line))

for i, t in enumerate(traces):
    print("=" * 80)
    print(f"Index {i+1}: Question {t['question_id']} | Strategy {t['strategy']}")
    print(f"Question: {t['question']}")
    print(f"Expected Answer: {t['expected_answer']}")
    print(f"Gold: {t['gold_source_id']} [{t['gold_char_start']}:{t['gold_char_end']}]")
    print(f"Filter Applied: {t.get('filter_applied')}")
    print(f"Automated evaluation: Hit@1={t['hit_at_1']}, Evidence Hit@3={t['evidence_hit_at_3']}")
    for hit in t["hits"]:
        print(f"\n--- Rank {hit['rank']}: {hit['chunk_id']} ---")
        print(f"Source: {hit['metadata'].get('source')} | doc_id: {hit['metadata'].get('document_id')} | chars: [{hit['metadata'].get('char_start')}, {hit['metadata'].get('char_end')}]")
        print(f"gold_source_match: {hit.get('gold_source_match')} | gold_evidence_match: {hit.get('gold_evidence_match')}")
        print("CHUNK TEXT:")
        print(hit['text'])
    print("\n")
