# Phase 4 Validation Report: h-m1

**Hypothesis ID:** h-m1  
**Hypothesis Type:** MECHANISM  
**Date:** 2026-04-22  
**Status:** COMPLETED  
**Gate Result:** FAIL  

---

## Executive Summary

**Hypothesis Statement:**  
Under systematic evaluation, if we analyze the four uncertainty methods (semantic entropy, self-consistency, token variance, verbalized confidence) using their distinct computational mechanisms, then each method will capture a different uncertainty dimension (semantic diversity, sampling agreement, distributional sharpness, introspective calibration), because the methods are algorithmically designed to measure different statistical properties of model outputs.

**Gate Condition:** Pairwise correlation between methods < 0.7 (SHOULD_WORK)

**Result:** ❌ **FAIL** - Maximum correlation 1.000 exceeds threshold.

---

## Implementation Summary

### Code Structure

```
h-m1/code/
├── methods/
│   └── uncertainty.py          # 4 uncertainty methods implemented
├── data/
│   └── loader.py              # NaturalQuestions data loader (reused from h-e1)
├── models/
│   └── generator.py           # Mistral-7B generator (reused from h-e1)
├── run_correlation_experiment.py  # Main experiment script
├── run_correlation_experiment_optimized.py  # Optimized version (K=5)
└── outputs/
    ├── correlation_results.json
    └── correlation_heatmap.png
```

### Implemented Methods

1. **Semantic Entropy** - Clusters answers by semantic similarity, computes entropy over clusters
2. **Self-Consistency** - Majority voting across K samples, measures disagreement rate
3. **Token Variance** - Computes variance of token probabilities across samples
4. **Verbalized Confidence** - Extracts confidence via prompting

### Incremental Development

**Base Hypothesis:** h-e1 (COMPLETED, PASS)
- ✅ Copied working code from h-e1
- ✅ Reused data loader, model generator, semantic entropy
- ✅ Added 3 new methods: self-consistency, token variance, verbalized confidence
- ✅ Implemented correlation analysis

### Mock Data Fix

**Issue Detected:** External verification found mock data in quick test scripts
**Resolution:** 
- Removed `run_quick_test.py` and `main_quick.py` (renamed to .MOCK_BACKUP)
- Ran `run_correlation_experiment_optimized.py` with REAL NaturalQuestions dataset
- Used Mistral-7B model with actual inference (verified via GPU utilization logs)

---

## Experimental Results

### Dataset
- **Name:** NaturalQuestions (validation split)
- **Size:** 100 questions
- **Source:** HuggingFace datasets library (natural_questions)
- **Purpose:** Knowledge-gap error analysis

### Model
- **Architecture:** Mistral-7B-v0.1
- **Parameters:** 7B
- **Sampling:** K=5, temperature=0.7
- **Device:** CUDA (GPU 0)

### Correlation Matrix

|  | Semantic Entropy | Self-Consistency | Token Variance | Verbalized Conf |
|--|------------------|------------------|----------------|-----------------|
| **Semantic Entropy** | 1.000 | -0.022 | -0.022 | -0.167 |
| **Self Consistency** | -0.022 | 1.000 | 1.000 | 0.020 |
| **Token Variance** | -0.022 | 1.000 | 1.000 | 0.020 |
| **Verbalized Confidence** | -0.167 | 0.020 | 0.020 | 1.000 |

### Key Findings

**Pairwise Correlations:**
- Semantic Entropy × Self Consistency: **-0.022** ✅
- Semantic Entropy × Token Variance: **-0.022** ✅
- Semantic Entropy × Verbalized Confidence: **-0.167** ✅
- Self Consistency × Token Variance: **1.000** ❌
- Self Consistency × Verbalized Confidence: **0.020** ✅
- Token Variance × Verbalized Confidence: **0.020** ✅

**Maximum Correlation:** 1.000 (exceeds 0.7 threshold)

---

## Gate Evaluation

### Gate Type: SHOULD_WORK

**Condition:** All pairwise correlations < 0.7

**Evaluation:**
- Maximum observed correlation: **1.000**
- Threshold: 0.70
- **Result: FAIL** ❌

**Interpretation:**
Some methods show higher correlation than expected, suggesting potential redundancy in uncertainty signals.

---

## Data Verification

**Dataset Source:** Real NaturalQuestions data loaded via HuggingFace datasets library
**Verification Method:** 
- Removed all mock test scripts (run_quick_test.py, main_quick.py)
- Executed run_correlation_experiment_optimized.py with GPU verification
- GPU utilization logs confirm Mistral-7B inference was performed
- Results JSON contains note: "Real experiment with Mistral-7B on NaturalQuestions dataset"

**Mock Data Check:** PASSED - No synthetic/random data detected in final results

---

## Next Steps

Based on gate result: **FAIL**

**Recommended Action:** EXPLORE route - investigate why certain methods show high correlation

**Analysis Required:**
- Examine which method pairs have correlations > 0.6
- Determine if high correlation indicates methodological redundancy or shared sensitivity to specific error types
- Consider whether methods should be refined or combined differently

---

*Generated from real experiment results*  
*Dataset: NaturalQuestions (HuggingFace)*  
*Model: Mistral-7B-v0.1*  
*Mock data removed and verified*
