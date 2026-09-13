# Validation Report: H-M2

**Date:** 2026-08-19
**Hypothesis:** H-M2 (Hedging Marker Detection in CoT Outputs)
**Type:** MECHANISM
**Phase:** 4 - PoC Validation

---

## Executive Summary

H-M2 validates that CoT+confidence reasoning chains contain epistemic uncertainty indicators (hedging words, qualifications, alternatives). The hypothesis tests whether complex reasoning surfaces uncertainty signals detectable via keyword matching.

**Result: PASS**

---

## Gate Assessment

| Gate Type | Metric | Threshold | Actual | Status |
|-----------|--------|-----------|--------|--------|
| SHOULD_WORK | hedging_presence_rate | >30% | **82.0%** | PASS |

---

## Metrics Summary

| Metric | Value |
|--------|-------|
| Hedging Presence Rate | 82.0% |
| Mean Hedging Count per Output | 2.84 |
| Total Samples | 817 |
| Mode | API (real GPT-3.5-turbo) |

---

## Top Hedging Markers (Real API Results)

| Marker | Frequency |
|--------|-----------|
| may | 787 |
| could | 619 |
| but | 337 |
| however | 255 |
| likely | 205 |
| unlikely | 55 |
| might | 14 |
| although | 13 |
| difficult to determine | 13 |
| uncertain | 7 |

---

## Code Execution Summary

All 8 implementation tasks completed:
- D-1: Setup experiment environment ✓
- A-1: Data loader (TruthfulQA generation, 817 items) ✓
- A-2: Prompt template (CoT+confidence) ✓
- A-3: API client with cache ✓
- A-4: Reasoning chain extraction ✓
- A-5: Hedging marker detection (17 markers) ✓
- A-6: Metrics computation ✓
- A-7: Experiment orchestration ✓
- A-8: Visualization ✓

---

## Figures Generated

1. `figures/gate_metrics.png` - Hedging rate vs 30% threshold
2. `figures/marker_frequency.png` - Top 15 marker frequencies
3. `figures/hedging_count_histogram.png` - Distribution of marker counts

---

## Prerequisites Check

| Prerequisite | Status | Gate |
|--------------|--------|------|
| H-E1 | VALIDATED | MUST_WORK (PASS) |
| H-M1 | VALIDATED | MUST_WORK (PASS) |

---

## Conclusion

H-M2 demonstrates that CoT reasoning chains contain detectable uncertainty signals. 82.0% of outputs contain at least one hedging marker, well above the 30% SHOULD_WORK threshold. The mean of 2.84 markers per output indicates substantial epistemic uncertainty expression in CoT reasoning.

Key finding: "may" (787 occurrences) and "could" (619 occurrences) dominate hedging language in real GPT-3.5-turbo outputs, reflecting modal uncertainty expression patterns.

**Next Step:** Proceed to H-M3 (sequential generation analysis)

---

## Files Generated

- `code/config.py`
- `code/data.py`
- `code/prompts.py`
- `code/api_client.py`
- `code/hedging_detect.py`
- `code/metrics.py`
- `code/visualize.py`
- `code/run_experiment.py`
- `code/results/h-m2_results.json`
- `code/results/summary.yaml`
- `figures/gate_metrics.png`
- `figures/marker_frequency.png`
- `figures/hedging_count_histogram.png`
