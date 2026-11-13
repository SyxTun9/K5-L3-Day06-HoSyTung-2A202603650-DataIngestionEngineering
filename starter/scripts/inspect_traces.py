import json
from pathlib import Path

traces_path = Path("starter/results/test_traces.jsonl")
with traces_path.open("r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        data = json.loads(line)
        print(f"=== Trace {i+1}: Q={data['question_id']}, Strat={data['strategy']} ===")
        print(f"Question: {data['question']}")
        print(f"Expected Answer: {data['expected_answer']}")
        print(f"Gold: doc={data['gold_source_id']}, chars=[{data['gold_char_start']}, {data['gold_char_end']}]")
        print(f"Filter Applied: {data.get('filter_applied')}")
        print(f"Hit@1: {data['hit_at_1']}, Evidence Hit@3: {data['evidence_hit_at_3']}")
        for hit in data["hits"]:
            meta = hit.get("metadata", {})
            print(f"  Rank {hit['rank']}: chunk_id={hit.get('chunk_id')}")
            print(f"    doc_id={meta.get('document_id')}, source={meta.get('source')}, page={meta.get('page')}, unit_id={meta.get('unit_id')}, doc_type={meta.get('document_type')}")
            print(f"    chars=[{meta.get('char_start')}, {meta.get('char_end')}]")
            print(f"    source_match={hit.get('gold_source_match')}, evidence_match={hit.get('gold_evidence_match')}")
            snippet = hit.get("text", "")[:150].replace("\n", " ")
            print(f"    text_snippet: {snippet}...")
