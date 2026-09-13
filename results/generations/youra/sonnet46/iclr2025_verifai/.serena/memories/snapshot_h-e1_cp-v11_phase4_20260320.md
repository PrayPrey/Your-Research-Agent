# Phase 4 Completion: h-e1 (H-AgreePredict-v11)

**Date:** 2026-03-20
**Hypothesis:** h-e1 (EXISTENCE gate)
**Pipeline:** TEST_verifiai/20260316_verifia
**Gate:** MUST_WORK → PASS

## Result

4/5 model-benchmark pairs pass IQR>0.05 AND mean in (0.05, 0.95):
- llama3_humaneval: IQR=0.1427, mean=0.1999 ✅ PASS
- llama3_mbpp: IQR=0.0638, mean=0.0814 ✅ PASS
- deepseek_humaneval: IQR=0.0759, mean=0.1053 ✅ PASS
- deepseek_mbpp: IQR=0.1093, mean=0.1423 ✅ PASS
- codellama_mbpp: IQR=0.0362, mean=0.0522 ❌ FAIL (IQR below threshold)

Overall gate: PASS (4/5 >= 4 required). h-e2 UNBLOCKED (READY).

## Key Finding

A_p (mean pairwise 4-gram Jaccard with brevity penalty) is non-degenerate on EvalPlus. CodeLlama on MBPP+ has lower structural diversity (IQR=0.036) — important covariate for h-e2/m1.

## Archon

Hypothesis task 4a920de8-cece-4d37-86a8-bea0ed6eb3f0 → status=done, title=[VALIDATED] Hypothesis H-E1: EXISTENCE

## Files

- code: h-e1/code/ (data_loader.py, ap_utils.py, gate.py, visualize.py, main.py)
- tests: 48 tests, all pass
- results: h-e1/code/results/gate_result.json (gate_pass=true, n_pairs_passing=4)
- figures: h-e1/figures/ (3 PNG files)
- report: h-e1/04_validation.md
- checkpoint archived: 04_checkpoint_archived_20260320T104500.yaml
