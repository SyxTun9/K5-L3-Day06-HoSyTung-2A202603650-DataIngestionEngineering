import sys
import json
import csv
from pathlib import Path

sys.path.insert(0, str(Path("starter").resolve()))
from src.ingestion import normalize_text

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

# Verify each chunk against file on disk
all_metadata_checks = []

for t in traces:
    qid = t["question_id"]
    strat = t["strategy"]
    q = questions[qid]
    applied_filter = t.get("filter_applied")
    for hit in t["hits"]:
        rank = hit["rank"]
        cid = hit["chunk_id"]
        meta = hit["metadata"]
        text = hit["text"]
        
        # Check source file on disk
        source_rel = meta.get("source")
        source_path = Path(source_rel)
        file_exists = source_path.exists()
        
        # Check text slice
        slice_matches = False
        norm_slice_len = 0
        if file_exists:
            raw_text = source_path.read_text(encoding="utf-8-sig")
            norm_doc = normalize_text(raw_text)
            c_start = int(meta.get("char_start", -1))
            c_end = int(meta.get("char_end", -1))
            extracted_slice = norm_doc[c_start:c_end]
            slice_matches = (extracted_slice == text)
            norm_slice_len = len(extracted_slice)
        
        # Check unit_id
        unit_id_matches = (meta.get("unit_id") == meta.get("document_id"))
        
        # Check filter compliance
        if applied_filter:
            # check if meta matches applied_filter
            filter_ok = all(meta.get(k) == v for k, v in applied_filter.items())
        else:
            filter_ok = None # N/A
            
        all_metadata_checks.append({
            "qid": qid,
            "strategy": strat,
            "rank": rank,
            "chunk_id": cid,
            "file_exists": file_exists,
            "slice_matches": slice_matches,
            "unit_id_matches": unit_id_matches,
            "page": meta.get("page"),
            "filter_applied": applied_filter,
            "filter_ok": filter_ok,
            "meta": meta
        })

print("\n--- METADATA VERIFICATION RESULTS ---")
all_files_exist = all(x["file_exists"] for x in all_metadata_checks)
all_slices_match = all(x["slice_matches"] for x in all_metadata_checks)
all_unit_ids_match = all(x["unit_id_matches"] for x in all_metadata_checks)
print(f"All 45 source files exist: {all_files_exist}")
print(f"All 45 character slices match chunk text exactly: {all_slices_match}")
print(f"All 45 unit_ids match document_id: {all_unit_ids_match}")

for x in all_metadata_checks:
    if not (x["file_exists"] and x["slice_matches"] and x["unit_id_matches"]):
        print(f"Mismatch in {x['qid']} {x['strategy']} rank {x['rank']}: file_exists={x['file_exists']}, slice={x['slice_matches']}, unit={x['unit_id_matches']}")
    if x["filter_applied"]:
        print(f"Filter check: {x['qid']} {x['strategy']} rank {x['rank']}: filter={x['filter_applied']}, filter_ok={x['filter_ok']}")
