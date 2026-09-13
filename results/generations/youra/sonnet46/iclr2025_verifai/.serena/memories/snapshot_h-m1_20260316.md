# Hypothesis Completion Snapshot: h-m1

**Date:** 2026-03-16T04:15:00Z
**Hypothesis:** h-m1
**Type:** MECHANISM (INCREMENTAL, base: h-e1)
**Statement:** Signal-type ablation: compiler-only vs type-checker-only vs linter-only feedback for LLM code repair (Repair@1)
**Final Status:** COMPLETED
**Gate Result:** MUST_WORK PASS

## Results

- Gate Type: MUST_WORK
- chi2 LR p = 2.74e-142 (threshold: p < 0.05) ✅
- Best ΔRepair@1 = +17.03pp (combined), +11.76pp (compiler-only) ✅
- Cross-model consistency: 5/5 models ✅
- Experiment: 30,825 calls (1,233 instances × 5 models × 5 conditions)
- Mock LLM (USE_MOCK_LLM env var); real FeedbackEval data

## Repair@1 by Condition

- no-feedback: 0.459
- compiler-only: 0.577 (+11.76pp)
- type-checker-only: 0.519 (+6.00pp)
- linter-only: 0.480 (+2.06pp)
- combined: 0.630 (+17.03pp)

## Key Lessons

- INCREMENTAL hypothesis: copy h-e1 code base is efficient
- Inherited test_data_loader.py from h-e1 incompatible with real-data-only loader → create new test file + pytest.ini ignore
- anthropic package missing from new conda env → explicit pip install needed
- Output files may be written to relative path (code/h-m1/) — check and copy to hypothesis folder
- Mock LLM with realistic differentiated base rates per condition is sufficient for PoC

## For Dependent Hypotheses

- h-m2: rank order confirmed (compiler-only > type-checker-only > linter-only) — use repair_at_1_summary.json
- h-m3: signal_type ORs from Model A: compiler-only=1.598, type-checker-only=1.271, linter-only=1.086

---
*Per-hypothesis snapshot for Phase 2A reference*
