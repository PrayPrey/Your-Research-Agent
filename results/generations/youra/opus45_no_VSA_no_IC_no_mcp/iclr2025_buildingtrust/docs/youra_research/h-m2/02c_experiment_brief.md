# Experiment Brief: h-m2 (Pareto-Optimal ECE Analysis)

**Hypothesis ID:** h-m2
**Type:** MECHANISM
**Gate:** SHOULD_WORK
**Date:** 2026-08-28
**Prerequisites:** h-e1 (COMPLETED)

---

## 1. Hypothesis Statement

Pareto-optimal models (no model dominates on both TruthfulQA and AdvGLUE) have significantly lower average ECE than non-Pareto models (t-test p < 0.05).

---

## 2. Data Sources

### 2.1 Primary Data (Reused from h-e1)

| Source | Type | Path | Verified |
|--------|------|------|----------|
| h-e1 scores | derived | `h-e1/code/results/scores.csv` | Yes |
| Model sample | standard | 14 models, 4 families | Yes |

**Available Columns:**
- `model`: HuggingFace model ID
- `family`: Model family (pythia, llama2, mistral, falcon)
- `params`: Parameter count
- `log_params`: Log10(params)
- `truthfulqa_mc1`: TruthfulQA MC1 accuracy
- `advglue_avg`: AdvGLUE average accuracy

### 2.2 Additional Data Required

| Data | Source | Method |
|------|--------|--------|
| ECE values | Compute per model | 15-bin ECE on MMLU logits (or synthetic proxy) |

**Note:** h-m1 has `ece.py` with `generate_synthetic_ece()` that can be reused.

---

## 3. Experimental Design

### 3.1 Step 1: Pareto Frontier Identification

**Algorithm:**
```python
def identify_pareto_optimal(models: pd.DataFrame) -> list:
    """
    Model is Pareto-optimal if no other model has BOTH:
    - higher truthfulqa_mc1 AND
    - higher advglue_avg
    """
    pareto = []
    for i, row in models.iterrows():
        dominated = False
        for j, other in models.iterrows():
            if i == j:
                continue
            if (other['truthfulqa_mc1'] >= row['truthfulqa_mc1'] and
                other['advglue_avg'] >= row['advglue_avg'] and
                (other['truthfulqa_mc1'] > row['truthfulqa_mc1'] or
                 other['advglue_avg'] > row['advglue_avg'])):
                dominated = True
                break
        if not dominated:
            pareto.append(row['model'])
    return pareto
```

**Expected Split:** ~4-6 models on Pareto frontier, ~8-10 non-Pareto.

### 3.2 Step 2: ECE Computation

Reuse h-m1's `compute_ece()` or `generate_synthetic_ece()`:
- 15-bin ECE (standard)
- ECE ∈ [0, 1], lower = better calibration

### 3.3 Step 3: Statistical Test

**Welch's t-test** (unequal variances assumed):
```python
from scipy.stats import ttest_ind

pareto_ece = df[df['model'].isin(pareto_models)]['ece']
non_pareto_ece = df[~df['model'].isin(pareto_models)]['ece']

t_stat, p_value = ttest_ind(pareto_ece, non_pareto_ece, equal_var=False)
```

**Success Criterion:** p < 0.05 AND mean(pareto_ece) < mean(non_pareto_ece)

---

## 4. Success Criteria

| Metric | Threshold | Interpretation |
|--------|-----------|----------------|
| t-test p-value | < 0.05 | Statistically significant difference |
| Mean ECE (Pareto) | < Mean ECE (non-Pareto) | Pareto models better calibrated |
| N (Pareto) | >= 3 | Sufficient sample for comparison |
| N (non-Pareto) | >= 5 | Sufficient sample for comparison |

---

## 5. Implementation Plan

### 5.1 Code Structure

```
h-m2/
├── code/
│   ├── config.py         # Reuse h-e1 MODEL_PARAMS
│   ├── pareto.py         # Pareto frontier identification
│   ├── ece.py            # Copy from h-m1
│   ├── analysis.py       # T-test and statistics
│   ├── visualize.py      # Pareto plot + ECE comparison
│   └── run.py            # Main orchestration
├── figures/
│   ├── pareto_frontier.png
│   └── ece_comparison.png
└── 04_validation.md
```

### 5.2 Dependencies

```
numpy
pandas
scipy
matplotlib
```

### 5.3 Estimated Runtime

~10 seconds (synthetic ECE), ~hours with real MMLU logits.

---

## 6. Baseline Comparison

| Baseline | Description |
|----------|-------------|
| Random split | Compare ECE between random halves of models |
| Size-matched | Control for model size in Pareto/non-Pareto comparison |

---

## 7. Risks & Mitigations

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Small sample size (N=14) | High | Use effect size (Cohen's d) alongside p-value |
| ECE is synthetic | High | Document as PoC; real evaluation needed for publication |
| Pareto frontier too small | Medium | Relaxed criterion if <3 models on frontier |

---

## 8. Research Artifacts

### 8.1 Reused from h-e1

- `h-e1/code/results/scores.csv` - Model scores
- `h-e1/code/config.py` - MODEL_PARAMS, MODELS

### 8.2 Reused from h-m1

- `h-m1/code/ece.py` - ECE computation functions

### 8.3 New Outputs

- `h-m2/figures/pareto_frontier.png` - Scatter with Pareto line
- `h-m2/figures/ece_comparison.png` - Box plot ECE by group
- `h-m2/04_validation.md` - Results report

---

## 9. Verification Protocol

1. Load h-e1 scores (14 models)
2. Identify Pareto-optimal models on (TruthfulQA, AdvGLUE) plane
3. Compute ECE for each model (15-bin)
4. Split into Pareto vs non-Pareto groups
5. Run Welch's t-test on ECE distributions
6. Report: t-statistic, p-value, means, effect size (Cohen's d)
7. Generate Pareto frontier and ECE comparison figures
8. Gate verdict: PASSED if p < 0.05 AND pareto_ece_mean < non_pareto_ece_mean

---

## 10. Expected Outcome

Based on h-m1 mechanism (ECE negatively correlates with both metrics), we expect:
- Pareto-optimal models (high on both metrics) to have lower ECE
- T-test should show significant difference (p < 0.05)
- Effect size (Cohen's d) likely medium to large (|d| > 0.5)

---

*Phase 2C Experiment Design Complete*
*Ready for Phase 3 Implementation Planning*
