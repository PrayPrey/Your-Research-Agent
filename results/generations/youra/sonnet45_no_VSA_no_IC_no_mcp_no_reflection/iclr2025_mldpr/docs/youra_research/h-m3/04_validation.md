# Validation Report: h-m3 Citation Velocity Correlation Detector

**Hypothesis ID:** h-m3  
**Type:** MECHANISM  
**Gate Type:** MUST_WORK  
**Date:** 2026-08-28  
**Validator:** Phase 4 Automated Validation

---

## Executive Summary

**Gate Result:** ❌ **FAIL**

**Key Findings:**
- Precision: 0.50 (target: ≥0.80) — **50% below target**
- Recall: 1.00 (target: ≥0.70) — **Exceeds target**
- Sample size: 3 benchmarks (reduced from 15 due to h-m1 data availability)
- False positive: GLUE benchmark (saturation 2018-03, shift 2018-10 = 7 months, exceeds 6-month correlation threshold)

**Verdict:** Citation velocity correlation does NOT achieve required precision for paradigm shift prediction. Detector is overly sensitive, flagging citation spikes that occur >6 months after saturation.

---

## Hypothesis Statement

> Under benchmark leaderboard conditions, IF detected saturation dates (dual-metric) occur >6 months BEFORE external paradigm shift events (GPT-3 2020, ViT 2021, LLaMA 2023), THEN saturation is internal benchmark exhaustion (not external disruption artifact), BECAUSE leading indicators appear before community migration.

**Refined Test:** Citation velocity correlation adds predictive signal beyond saturation detection, achieving >80% precision and >70% recall on benchmark-shift pairs.

---

## Experimental Setup

### Dataset
- **Benchmarks:** 3 cases (imagenet, glue, squad) with h-m1 saturation dates
- **Citation Data:** Synthetic time series with velocity spikes around paradigm shifts
- **Ground Truth:** Binary labels (1 if shift within 6 months of saturation, 0 otherwise)

### Model
- **Baseline:** Saturation-only detector (h-m1)
- **Proposed:** Saturation + citation velocity correlation
- **Detection Logic:** Predict shift if (saturation detected) AND (citation velocity spike in [-3mo, +6mo] window)

### Metrics
- **Precision:** TP / (TP + FP) — detected saturation → actual shift
- **Recall:** TP / (TP + FN) — actual shifts → detected within 6mo
- **Gate Threshold:** Precision ≥0.80, Recall ≥0.70

---

## Results

### Quantitative Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Precision** | 0.50 | ≥0.80 | ❌ FAIL |
| **Recall** | 1.00 | ≥0.70 | ✅ PASS |
| **F1-Score** | 0.67 | — | — |
| **Accuracy** | 0.67 | — | — |

### Confusion Matrix

|  | Predicted: No Shift | Predicted: Shift |
|---|---------------------|------------------|
| **Actual: No Shift** | 1 (TN) | 1 (FP) |
| **Actual: Shift** | 0 (FN) | 1 (TP) |

### Per-Benchmark Results

| Benchmark | Saturation Date | Shift Date | Lead Time (months) | Ground Truth | Prediction | Result |
|-----------|----------------|------------|-------------------|--------------|------------|--------|
| imagenet | 2015-08 | 2015-12 | 4 | 1 (shift) | 1 (shift) | ✅ TP |
| glue | 2018-03 | 2018-10 | 7 | 0 (no shift) | 1 (shift) | ❌ FP |
| squad | 2018-05 | 2019-02 | 9 | 0 (no shift) | 0 (no shift) | ✅ TN |

---

## Analysis

### Success Cases

**ImageNet (True Positive):**
- Saturation: 2015-08
- Paradigm shift: 2015-12 (ResNet, 4 months after saturation)
- Citation velocity spike detected in search window [-3mo, +6mo] = [2015-05 to 2016-02]
- **Correct prediction:** Shift occurred within 6-month correlation threshold

### Failure Cases

**GLUE (False Positive):**
- Saturation: 2018-03
- Paradigm shift: 2018-10 (BERT, 7 months after saturation)
- Citation velocity spike detected in search window [-3mo, +6mo] = [2017-12 to 2018-09]
- **Incorrect prediction:** Shift occurred at 7 months (outside 6-month threshold), but detector flagged velocity spike within 6-month window
- **Root cause:** Detector's search window (+6mo) aligns with spike timing, but ground truth threshold (≤6mo lead time) excludes this case

### Root Cause Analysis

**Precision Failure:**
1. **Window Misalignment:** Detector search window (+6mo) detects spikes that occur DURING the window, but ground truth requires shift COMPLETION within 6mo of saturation
2. **Labeling Logic:** Ground truth: `label = 1 if 0 ≤ shift_date - saturation_date ≤ 6mo`
3. **Detector Logic:** Detector: `spike if max(velocity) > mean+2σ in [saturation-3mo, saturation+6mo]`
4. **Mismatch:** Detector finds spike at 2018-09 (within search window), but shift happened at 2018-10 (7mo from saturation, outside label threshold)

**Statistical Significance:**
- Sample size (n=3) too small for reliable precision estimate
- 95% confidence interval for precision: [0.01, 0.99] (extremely wide)
- Cannot generalize to broader population

---

## Gate Evaluation

### MUST_WORK Gate Criteria

| Criterion | Result | Status |
|-----------|--------|--------|
| Precision ≥0.80 | 0.50 | ❌ FAIL |
| Recall ≥0.70 | 1.00 | ✅ PASS |
| Sample size ≥15 | 3 | ❌ FAIL (data availability) |

**Overall Gate Result:** ❌ **FAIL**

**Reason:** Precision (0.50) falls 50% below target (0.80). False positive rate (50%) indicates detector cannot reliably distinguish true shifts from noise.

---

## Key Findings

1. **Precision Failure:** Citation velocity correlation achieves only 50% precision, indicating high false positive rate
2. **Recall Success:** Detector captures all true shifts (100% recall), but at cost of over-prediction
3. **Window Mismatch:** Detector search window (+6mo) does not align with ground truth labeling threshold (≤6mo lead time)
4. **Sample Size Limitation:** Only 3 benchmarks tested (vs 15-20 target) due to h-m1 data availability
5. **Detector Sensitivity:** 2σ spike threshold may be too lenient, flagging normal citation growth as paradigm shifts

---

## Visualizations

Generated figures (saved to `figures/`):
1. **gate_metrics.png** — Bar chart showing precision/recall vs target thresholds
2. **confusion_matrix.png** — Heatmap of TP/FP/TN/FN distribution
3. **timeline_imagenet.png** — Citation velocity over time with saturation/shift markers
4. **timeline_glue.png** — Citation velocity timeline (shows false positive)
5. **timeline_squad.png** — Citation velocity timeline (true negative)

---

## Recommendations

### For Gate Pass (if hypothesis is refined)

1. **Align Windows:** Match detector search window to ground truth threshold (either both 6mo or both 9mo)
2. **Increase Threshold:** Raise spike threshold from 2σ to 3σ to reduce false positives
3. **Add Temporal Constraint:** Require velocity spike BEFORE shift date (not just within window)
4. **Expand Sample Size:** Acquire citation data for remaining 12 benchmarks to reach statistical validity

### For Future Work

1. **h-m4 (if continuation):** Test citation velocity as early warning signal (relaxed precision, optimized for recall)
2. **Alternative Mechanism:** Investigate community discussion metrics (GitHub stars, paper mentions) instead of citation velocity
3. **Threshold Tuning:** Perform ROC curve analysis to find optimal spike threshold

---

## Reproducibility

### Data Files
- **Input:** 
  - `../h-m1/results/convergence_results.json` (saturation dates)
  - `data/paradigm_shifts.json` (ground truth shifts)
  - `data/citations/*.json` (citation time series)
- **Output:**
  - `results/predictions.csv` (per-benchmark predictions)
  - `results/metrics.json` (precision/recall/confusion matrix)
  - `figures/*.png` (visualizations)

### Code
- **Main:** `code/main_experiment.py`
- **Modules:** `velocity_detector.py`, `correlation_detector.py`, `precision_recall_evaluator.py`, `visualizer.py`

### Run Command
```bash
cd /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet45/TEST_mldrp/docs/youra_research/h-m3/code
python3 main_experiment.py
```

**Exit Code:** 1 (gate failure)

---

## Conclusion

Hypothesis h-m3 **FAILS** MUST_WORK gate. Citation velocity correlation does NOT achieve required precision (0.50 vs 0.80 target) for paradigm shift prediction. The detector exhibits high false positive rate (50%), flagging citation spikes that occur outside the 6-month correlation threshold. Small sample size (3 benchmarks) further limits statistical confidence.

**Recommended Action:** 
- **ROUTE_TO:** REFINEMENT (adjust detector thresholds and window alignment) or SUPERSEDE (test alternative mechanisms)
- **DO NOT PROCEED** to downstream hypotheses without addressing precision failure

---

**Validation Complete:** 2026-08-28  
**Next Step:** Update verification_state.yaml with FAIL verdict and route decision
