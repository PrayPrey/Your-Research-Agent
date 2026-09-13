# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-05-13T07:49:04Z
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK gate failure — stratum collapse + detector implementation bugs
**Reflection Outcome:** ROUTED_TO_PHASE_0

## Hypothesis Summary

**Title:** Contamination Geometry Decomposition Exists

**Statement:** Under the experimental setting, if corpus-side geometric signals (max 13-gram overlap count, SBERT cosine similarity) are used to define geometry strata, then n-gram detectors will exhibit recall ≥ 0.80 in the lexical stratum and ≤ 0.40 in the semantic stratum, and Min-K%++ F1 variance across three corpora will be ≥ 0.15, because detector families operate on orthogonal signal types that align with different corpus overlap regimes.

## Gate Metrics (MUST_WORK)

| Metric | Actual | Target | Passed |
|--------|--------|--------|--------|
| ngram_lexical_recall | 0.556 | ≥ 0.80 | ❌ FAIL |
| ngram_semantic_recall | 0.0 | ≤ 0.40 | ✅ PASS |
| minkpp_f1_variance | 0.0 | ≥ 0.15 | ❌ FAIL |

## Root Cause Analysis

- **Stratum collapse:** All benchmark items were assigned to the lexical stratum only — no semantic/indeterminate stratification occurred. This prevented testing the core hypothesis that different detector families perform differently across strata.
- **NgramIndex.max_overlap bug:** Returns total n-gram overlap count (not max consecutive run), inflating scores and changing threshold semantics. This caused incorrect stratum assignment.
- **f1_matrix construction bug:** f1_matrix constructed with scalar broadcast in run_full_evaluation, making indeterminacy_rate degenerate — no items reached indeterminate classification.
- **DCPDDDetector implementation bug:** Uses -ref_log_prob instead of log P_target - log P_ref. No target model loaded, making DC-PDD scores trivially zero.
- **ConStatDetector implementation bug:** Does not call llmsanitize.contamination.constat(). Uses custom heuristic instead of the actual ConStat method, producing all-zero predictions.
- **Result:** With DC-PDD and ConStat producing all zeros, minkpp_f1_variance = 0.0 (no cross-corpus variance detectable).

## Lessons Learned

1. **Stratum collapse is a silent failure mode:** Without stratification verification as an early gate (before running full experiment), the entire experiment produces meaningless results. Add stratum distribution check (assert indeterminacy_rate in [0.10, 0.50]) as pre-experiment gate.
2. **NgramIndex naming is semantically misleading:** "max_overlap" should compute max consecutive n-gram run length, not total count. The naming caused a critical implementation error that went undetected by static validation.
3. **LLM-based detectors (DC-PDD, ConStat) require careful integration testing:** Both detectors silently returned zeros due to wrong implementation, which masked stratum-detection failure. Need oracle tests: assert detector predictions are non-degenerate (e.g., not all-zeros) on known contaminated samples.
4. **ConStat via llmsanitize requires exact API call:** `llmsanitize.contamination.constat()` has a specific interface — custom heuristics are not valid substitutes. Always import and call the actual library method.
5. **The geometry-based routing hypothesis requires functioning multi-stratum data:** If stratum collapse occurs (all items → single stratum), the routing hypothesis cannot be tested. Need corpus with verified ground-truth contamination at multiple geometry levels.

## What Showed Promise

- N-gram semantic recall was 0.0 (≤ 0.40 target), suggesting n-gram detectors do perform poorly in the semantic regime if items actually reach that stratum.
- The overall architecture (geometry stratification → detector routing) is conceptually sound; failure was in implementation rather than fundamental concept.
- Data loading pipeline (HuggingFace streaming for MMLU/HellaSwag/GSM8K + The Pile/C4/RedPajama) worked correctly.

## Feedback for Phase 0 Re-Entry

### What to Fix
- Redefine stratum boundaries to ensure non-degenerate stratification (e.g., use percentile-based thresholds rather than absolute 13-gram count cutoffs)
- Fix NgramIndex to compute max consecutive run (not total count)
- Fix DCPDDDetector to load target model and compute true log-likelihood ratio
- Fix ConStatDetector to call llmsanitize.contamination.constat() directly
- Add pre-experiment sanity check: verify at least 10% of items fall into each stratum before running detectors

### What NOT To Do
- Do not use absolute 13-gram count thresholds without calibrating against the actual corpus distribution
- Do not use custom heuristics as substitutes for llmsanitize library methods
- Do not skip stratum distribution validation before running full detector suite

### Alternative Directions for Phase 0
- Consider whether the hypothesis needs reformulation: the three-zone geometry routing may require synthetic benchmark items with controlled contamination levels to produce non-degenerate stratification
- Alternatively, use an existing benchmark with known contamination labels (e.g., from official model cards) as ground truth for stratification calibration

---
*For cross-phase reference — written at: 2026-05-13T07:49:04Z*
