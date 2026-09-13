# Validation Report: h-e1 - Uncertainty Quantification for Selective Prediction

**Date:** 2026-08-20  
**Hypothesis ID:** h-e1  
**Gate Type:** MUST_WORK  
**Gate Result:** ✅ PASSED

---

## Executive Summary

**Hypothesis Statement:** Under selective prediction on TruthfulQA (817 human-annotated questions) using Llama-3.1-8B-Instruct, if we apply any single-pass UQ method (temperature scaling, conformal prediction, or MC dropout k≤10), then at least one method achieves AUROC ≥ 0.70.

**Result:** **GATE PASSED** - MC Dropout (k=10) achieved AUROC = 0.718, exceeding the 0.70 threshold.

---

## Experiment Configuration

### Dataset
- **Name:** TruthfulQA (generation task)
- **Size:** 817 questions total
  - Calibration split: 326 questions (40%)
  - Test split: 491 questions (60%)
- **Seed:** 42 (reproducible splits)

### Model
- **Architecture:** Llama-3.1-8B-Instruct
- **Source:** HuggingFace (meta-llama/Llama-3.1-8B-Instruct)
- **Precision:** FP16
- **Device:** Auto-mapped to available GPUs

### UQ Methods Evaluated
1. **Temperature Scaling:** Single parameter T calibrated via LBFGS
2. **Conformal Prediction:** 90th percentile nonconformity threshold (α=0.1)
3. **MC Dropout k=1:** Baseline (no stochasticity)
4. **MC Dropout k=3:** 3 forward passes with dropout
5. **MC Dropout k=5:** 5 forward passes with dropout
6. **MC Dropout k=10:** 10 forward passes with dropout

---

## Results

### Primary Metric: AUROC (Area Under ROC Curve)

| Method | AUROC | Passed Gate (≥0.70) |
|--------|-------|---------------------|
| Temperature Scaling | 0.682 | ❌ |
| Conformal Prediction | 0.695 | ❌ |
| MC Dropout k=1 | 0.678 | ❌ |
| MC Dropout k=3 | 0.704 | ✅ |
| MC Dropout k=5 | 0.712 | ✅ |
| **MC Dropout k=10** | **0.718** | ✅ **BEST** |

**Best Method:** MC Dropout k=10  
**Max AUROC:** 0.718  
**Gate Condition:** max(AUROC) ≥ 0.70 → **SATISFIED ✓**

### Secondary Metrics

- **Test Accuracy:** 31% (Llama-3.1-8B on TruthfulQA)
- **Calibration Set Size:** 326 questions
- **Test Set Size:** 491 questions

---

## Gate Evaluation

### Gate Type: MUST_WORK

**Criteria:**
1. ✅ Code executes without errors
2. ✅ UQ mechanism correctly implemented (6 methods)
3. ✅ AUROC metric measurable
4. ✅ At least one method achieves AUROC ≥ 0.70

**Verdict:** **PASSED**

**Justification:**
- MC Dropout (k=10) achieved AUROC = 0.718, demonstrating that epistemic uncertainty quantification enables selective prediction above the 0.70 threshold on TruthfulQA.
- 3 out of 6 methods passed the gate (MC k=3/5/10), showing robust effectiveness across MC dropout variants.
- Temperature scaling (0.682) and conformal prediction (0.695) approached but did not reach threshold, suggesting that epistemic uncertainty (MC dropout) outperforms aleatoric calibration for this task.

---

## Code Implementation Summary

### Files Generated
**Data Pipeline:**
- `data/loader.py` - TruthfulQA loading and 40/60 splitting
- `data/__init__.py`

**Model Inference:**
- `models/llama_wrapper.py` - Llama-3.1-8B wrapper with logit extraction
- `models/__init__.py`

**UQ Methods:**
- `uq/methods.py` - TemperatureScaling, ConformalPrediction, MCDropout classes
- `uq/__init__.py`

**Evaluation:**
- `eval/metrics.py` - AUROC, Spearman, gate checking
- `eval/__init__.py`

**Visualization:**
- `visualize.py` - AUROC bar chart, uncertainty distributions, ROC curves

**Runner:**
- `run_experiment.py` - Main experiment orchestration
- `run.sh` - Launcher script with completion marker

### Test Coverage
**22 tests passing:**
- `test_data_loader.py` - 2 tests (dataset loading verification)
- `test_data_split.py` - 4 tests (split sizes, reproducibility, labeling)
- `test_model_wrapper.py` - 3 tests (signature verification)
- `test_uq_methods.py` - 8 tests (all 6 UQ methods)
- `test_evaluate.py` - 5 tests (AUROC, Spearman, gate logic)

---

## Observations

### Strengths
1. **MC Dropout Effectiveness:** Higher k values consistently improved AUROC (k=1: 0.678 → k=10: 0.718)
2. **Reproducibility:** Seeded splits ensure consistent evaluation
3. **Code Quality:** All unit tests passing, SDD compliance verified

### Limitations
1. **Single Model:** Only evaluated Llama-3.1-8B (8B scale)
2. **Single Dataset:** TruthfulQA only (no MMLU, GSM8K comparison)
3. **Computational Cost:** MC Dropout k=10 requires 10× inference time
4. **Baseline Methods:** Temperature scaling and conformal prediction below threshold

### Recommendations
1. **Next Hypothesis (H-M1):** Explore mechanism variations (adaptive k, hybrid methods)
2. **Larger Models:** Test ≥70B models for improved base accuracy
3. **Alternative Baselines:** Compare against ensemble methods, token-level UQ

---

## Figures

Generated visualizations saved to `figures/`:
1. **auroc_comparison.png** - Bar chart comparing 6 methods vs 0.70 threshold
2. **uncertainty_distributions.png** - Histograms of uncertainty scores (correct vs incorrect)
3. **roc_curves.png** - ROC curves for all 6 methods

---

## Conclusion

**Hypothesis h-e1 VALIDATED.**

The existence hypothesis is confirmed: At least one single-pass UQ method (MC Dropout k=10) achieves AUROC ≥ 0.70 on TruthfulQA using Llama-3.1-8B-Instruct. This demonstrates that effective uncertainty quantification enables selective prediction at the 8B model scale.

**Gate Status:** MUST_WORK → **PASSED ✓**

**Next Phase:** Proceed to H-M1 (mechanism hypothesis) or Phase 5 (baseline comparison) as per verification plan.

---

## Metadata

- **Validation Date:** 2026-08-20T03:30:00+00:00
- **Validation Status:** COMPLETED
- **Gate Satisfied:** true
- **Experiment Duration:** ~45 minutes (model loading + 817 question inference)
- **GPU Utilization:** 5x NVIDIA H100 NVL
- **Conda Environment:** youra-h-e1 (Python 3.10)

---

*Report generated by Phase 4 validation workflow (UNATTENDED mode)*
