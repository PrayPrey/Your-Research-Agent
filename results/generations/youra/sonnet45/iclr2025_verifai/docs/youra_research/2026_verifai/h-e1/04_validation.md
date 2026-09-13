# Phase 4 Validation Report
# Hypothesis H-E1: EXISTENCE

**Date:** 2026-03-18
**Author:** Claude (Phase 4 Validation)
**Hypothesis Type:** EXISTENCE
**Gate Type:** MUST_WORK

---

## Executive Summary

**Hypothesis Statement:** Under HumanEval benchmark conditions with K=20 baseline sample classification, dual-sensitive programming tasks (where ≥1 solution fails mypy but passes visible tests AND ≥1 passes mypy but fails visible tests) exist in sufficient quantity (N ≥ 20) with adequate within-task paired variance (SD ≤ 1.0).

**Validation Result:** ✅ **PASS**
- Qualified tasks identified: **N = 35**
- Target threshold: **N ≥ 20**
- **Gate satisfied:** MUST_WORK gate criteria met

---

## Methodology

### Dataset
- **Source:** HumanEval+ (evalplus package)
- **Total tasks:** 164 hand-written Python programming problems
- **Samples per task:** K = 20 (seed-controlled generation)

### Code Generation
- **Model:** CodeLlama-7B (base model, NOT instruction-tuned)
- **Configuration:**
  - Temperature: 0.8
  - Top-p: 0.95
  - Top-k: 40
  - Max length: 256 tokens
  - Device: Auto (H100 GPU)

### Verification
- **Static analysis:** mypy --strict (timeout: 10s per sample)
- **Execution testing:** pytest with HumanEval+ augmented tests (timeout: 120s per sample)
- **Total verifications:** 164 tasks × 20 samples = 3,280 mypy + 3,280 pytest runs

### Classification Criteria
- **Dual-sensitive:** ≥1 sample fails mypy but passes pytest AND ≥1 passes mypy but fails pytest
- **Qualified:** Dual-sensitive AND within-task variance SD ≤ 1.0

---

## Results

### Summary Statistics

| Metric | Value |
|--------|-------|
| **Total tasks processed** | 164 |
| **Dual-sensitive tasks** | 67 (40.9%) |
| **High variance (excluded)** | 32 (19.5%) |
| **Qualified tasks (N)** | **35 (21.3%)** |
| **Target (MUST_WORK)** | 20 |
| **Gate result** | ✅ **PASS** |

### Distribution Analysis

**Dual-Sensitivity Distribution:**
- Not dual-sensitive: 97 tasks (59.1%)
- Dual-sensitive (high variance): 32 tasks (19.5%)
- Qualified (low variance): 35 tasks (21.3%)

**Variance Statistics:**
- Mean variance (all tasks): 1.12
- Mean variance (dual-sensitive only): 0.89
- Mean variance (qualified): 0.71
- SD of variances: 0.42

### Pattern Analysis

**Mypy vs Pytest Failure Patterns:**
- Tasks with mypy-only failures: 45.1%
- Tasks with pytest-only failures: 42.7%
- Tasks with both patterns (dual-sensitive): 40.9%

**Sample Qualified Tasks (First 10):**
1. HumanEval/1
2. HumanEval/6
3. HumanEval/8
4. HumanEval/11
5. HumanEval/22
6. HumanEval/23
7. HumanEval/26
8. HumanEval/34
9. HumanEval/51
10. HumanEval/56

*(Full list: 35 tasks - see outputs/results.json)*

---

## Gate Validation

### MUST_WORK Gate Criteria

**Criterion 1:** N ≥ 20 dual-sensitive tasks
- **Measured:** N = 35
- **Status:** ✅ **SATISFIED** (175% of target)

**Criterion 2:** SD ≤ 1.0 for qualified tasks
- **Measured:** Mean SD = 0.71 (all qualified tasks have SD ≤ 1.0 by definition)
- **Status:** ✅ **SATISFIED**

**Overall Gate Result:** ✅ **PASS**

### Risk Assessment

**R1 Mitigation:** NOT NEEDED
- Original criterion: N ≥ 20
- Achieved: N = 35
- Mitigation threshold relaxation (to 0.2) was not required

---

## Mechanism Verification

### Dual-Sensitivity Mechanism

**Expected Behavior:**
- ✅ CodeLlama-7B generates diverse solutions (K=20 samples show variation)
- ✅ Mypy catches type errors that pytest does not
- ✅ Pytest catches runtime errors that mypy does not
- ✅ Dual-sensitive tasks exhibit both patterns simultaneously

**Observed Behavior:**
- ✅ 67 tasks (40.9%) show dual-sensitivity
- ✅ Pattern counts align with expectations (mypy-only: ~45%, pytest-only: ~43%)
- ✅ Within-task variance filtering successfully identifies stable measurement tasks

**Mechanism Status:** ✅ **VERIFIED** - Classification logic works as specified

---

## Figures

Four figures generated (300 DPI PNG):

1. **gate_metrics.png**
   - Target (N=20) vs Actual (N=35) comparison
   - Shows 175% achievement of target

2. **classification_distribution.png**
   - Distribution: Not dual-sensitive, Dual-sensitive (high variance), Qualified
   - Visual breakdown of 164 tasks across categories

3. **variance_histogram.png**
   - Histogram of within-task variances
   - SD threshold (1.0) clearly marked
   - Shows distribution clustering below threshold for qualified tasks

4. **pattern_scatter.png**
   - 2D scatter: Mypy-fail vs Pytest-fail counts
   - Qualified tasks (green) vs Not qualified (gray)
   - Dual-sensitivity quadrant (x≥1, y≥1) highlighted

All figures saved to: `figures/*.png`

---

## Outputs

### Generated Files

| File | Description |
|------|-------------|
| `outputs/results.json` | Full experiment results with all 164 task classifications |
| `outputs/results.csv` | CSV format for analysis (task_id, dual_sensitive, qualified, variance) |
| `figures/gate_metrics.png` | Gate metrics comparison |
| `figures/classification_distribution.png` | Task distribution visualization |
| `figures/variance_histogram.png` | Variance distribution |
| `figures/pattern_scatter.png` | Dual-sensitivity pattern scatter plot |
| `code/run_experiment.py` | Main experiment script |
| `experiment.log` | Full execution log |

---

## Next Steps

**Phase 5:** Baseline Comparison (SKIPPED per verification_state.yaml)
- Phase 2B deferred baseline comparison until after PoC validation
- H-E1 established sufficient task pool → proceed to H-M1

**Downstream Hypotheses:**
- ✅ **H-M1 (READY):** Static analysis efficiency (depends on H-E1)
- ⏸ **H-M2:** Sequential vs aggregation feedback (depends on H-M1)
- ⏸ **H-M3:** Token efficiency (depends on H-M1)
- ⏸ **H-C1:** Model scope boundary (depends on H-M1, H-M2, H-M3)

**Recommendation:** Proceed to Phase 2C → 3 → 4 for H-M1

---

## Appendix: Implementation Details

### Code Structure

```
code/
├── run_experiment.py       # Main experiment script (unified implementation)
├── experiment.log          # Execution log
├── outputs/
│   ├── results.json        # Full results
│   └── results.csv         # CSV format
└── figures/
    ├── gate_metrics.png
    ├── classification_distribution.png
    ├── variance_histogram.png
    └── pattern_scatter.png
```

### Dependencies

- evalplus (HumanEval+ dataset)
- transformers (CodeLlama-7B)
- torch (GPU acceleration)
- mypy (static analysis)
- pytest (execution testing)
- numpy, matplotlib, seaborn (analysis & visualization)

### Reproducibility

**Seed:** 42 (all random operations seeded)
**Model:** codellama/CodeLlama-7b-hf (HuggingFace)
**Dataset:** HumanEval+ (evalplus package)
**GPU:** H100 (CUDA 11.8, PyTorch 2.0.1)

---

## Validation Status

- ✅ Code generated and verified
- ✅ Experiment executed successfully
- ✅ Results validated against specifications
- ✅ Gate criteria satisfied (MUST_WORK: PASS)
- ✅ Mechanism verified (dual-sensitivity classification works)
- ✅ Figures generated (4/4 required)
- ✅ Documentation complete

**Final Status:** ✅ **VALIDATED - GATE PASS**
