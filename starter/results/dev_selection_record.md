# Dev selection record

- Date: 2026-11-13
- Corpus: Sherlock Holmes manifest, 51 source units
- Embedding: `all-MiniLM-L6-v2`, 384 dimensions
- Selection rule: prioritize Evidence Hit@3 on dev; use Hit@1 as the next retrieval tie-breaker. Report metadata-filter compliance separately.
- Dev retrieval results: A = 6/15 Evidence Hit@3 and 2/15 Hit@1; B = 5/15 and 2/15; C = 5/15 and 2/15.
- Candidate selected for the primary configuration: A, because it leads Evidence Hit@3 on dev under the stated rule. The lead is one question in a small sample.
- Filter result: C complied with all 3/3 dev metadata filters. This is useful metadata behavior, but it does not replace evidence retrieval accuracy.
- Freeze: keep A/B/C parameters, embedding model, corpus, and benchmark unchanged for the test run. Do not tune from test results.

## Test results after freeze

- Retrieval: A = 1/5 Hit@1 and 1/5 Evidence Hit@3; B = 0/5 and 0/5; C = 0/5 and 0/5.
- Manual grounding labels (reviewer: Ho Sy Tung): A has three 0s, one 1, and one 2 (mean 0.6/2); B and C each have five 0s (mean 0/2).
- Metadata audit: 15/15 top-3 records per strategy (45/45 total) were marked correct for source and traceable location.
- C filter audit: all three Q18 results obeyed `document_type=story` (3/3 chunks; 1/1 filtered question), but none retrieved the gold Thor Bridge source/evidence.
- Manual chunk coherence: same 10 source units, midpoint positions, reviewer Ho Sy Tung. A = 0/10/0 scores of 0/1/2 (mean 0.0/2); B = 0/4/6 (mean 1.6/2); C = 0/4/6 (mean 1.6/2).
- Interpretation: A performed best on this small held-out set, while absolute retrieval and grounding quality were low. Metadata fields were accurate even when retrieved passages were irrelevant. Do not generalize beyond this corpus and five test questions.
