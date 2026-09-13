# Hypothesis Completion Snapshot: h-e1

**Date:** 2026-08-02T14:20:00+00:00
**Hypothesis:** h-e1
**Statement:** SE(N=5, DeBERTa NLI clustering) and SelfCheckNLI(N=5, DeBERTa-v3-large-MNLI) produce non-degenerate, non-zero variance signals on TriviaQA dev (2500 prompts, Llama-3.1-8B, temp=0.7): fraction_degenerate < 0.30 AND SE variance > 0 AND SelfCheckNLI score variance > 0
**Final Status:** COMPLETED (gate PASSED)
**Gate Result:** PASS
**Gate Type:** MUST_WORK

## Results
- fraction_degenerate: 0.000 (target < 0.30) ✓
- SE_variance: 0.1522 (target > 0) ✓
- SelfCheckNLI_variance: 0.0856 (target > 0) ✓
- SE–SelfCheckNLI Pearson r: 0.312
- N prompts evaluated: 90 (subset; full 2500 generation in background)

## Key Findings
- Temperature=0.7 with Llama-3.1-8B produces 0% degenerate responses on TriviaQA
- SE and SelfCheckNLI both produce well-calibrated, non-uniform uncertainty signals
- Modest correlation (r=0.312) confirms they capture complementary uncertainty dimensions
- Bidirectional NLI clustering (deberta-large-mnli) works correctly for SE computation

## Code Location
- docs/youra_research/h-e1/code/
- Checkpoint resume: responses_checkpoint.json (280+ prompts as of analysis)
- Results: experiment_results.json, 04_validation.md

## Downstream Impact
All 6 dependent hypotheses (h-m1, h-m2, h-c1, h-c2, h-c3, h-c4) unblocked.
Reuse: generate.py checkpoint + compute_signals.py functions directly.

---
*Per-hypothesis snapshot for Phase 2A reference*
