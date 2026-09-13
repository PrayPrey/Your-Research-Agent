# Product Requirements Document: h-m2

**Hypothesis:** h-m2  
**Type:** MECHANISM  
**Date:** 2026-08-25  
**Author:** Anonymous

---

## Executive Summary

Implement statistical analysis pipeline to validate task-dependent variance in execution-human feedback correlation. Extends h-e1 validated correlation measurement infrastructure with ANOVA and variance analysis across three code generation datasets (HumanEval, MBPP, SWE-bench) representing task types with varying specification completeness.

**Core Hypothesis:** Execution feedback quality as intent proxy depends on test coverage of intent dimensions. Tasks with complete specifications (competitive programming) show strong execution-human correlation (>0.8), while underspecified tasks (realistic software) show weak correlation (<0.5).

---

## Problem Statement

### Research Question

Does execution feedback correlation with human judgment vary systematically by task type, with correlation magnitude determined by specification completeness?

### Context

- **Prerequisite Results:**
  - h-e1: Correlation measurement infrastructure validated (all correlations significant p<0.05)
  - h-m1: Specification completeness determines test-intent capture (SWE-bench 2.3× more missed intent dimensions vs HumanEval)

- **Gap:** No quantitative validation of predicted correlation pattern across task spectrum (competitive → basic → realistic)

### Success Impact

Validates core mechanism linking specification completeness to execution feedback quality, enabling:
- Principled selection of feedback modality by task type
- Foundation for h-m3 (adaptive feedback routing)
- Evidence for paper claim: execution feedback insufficiency in underspecified domains

---

## Functional Requirements

### FR-1: Data Loading and Validation

**Requirement:** Load h-e1 collected feedback data (execution, AI, human ratings) for all three datasets.

**Inputs:**
- h-e1 feedback cache: `{research_folder}/.data_cache/feedback/h-e1/`
- Per-dataset files: `{dataset}_exec.npy`, `{dataset}_ai.npy`, `{dataset}_human.npy`

**Outputs:**
- Validated feedback arrays (exec_scores, ai_scores, human_ratings) per dataset
- Data integrity check: matching sample counts, no missing values

**Acceptance Criteria:**
- All three datasets loaded without error
- Sample counts match h-e1 collection (HumanEval: 164, MBPP: 500, SWE-bench: 300)
- No NaN/Inf values in feedback arrays

---

### FR-2: Correlation Computation per Dataset

**Requirement:** Compute execution-human Pearson correlation coefficient for each dataset.

**Inputs:**
- `exec_scores[dataset]`: Execution feedback (binary pass/fail converted to 0/1)
- `human_ratings[dataset]`: Human ratings (1-5 scale, mean of 3 raters)

**Processing:**
```python
from scipy.stats import pearsonr

for dataset in ["HumanEval", "MBPP", "SWE-bench"]:
    r, p = pearsonr(exec_scores[dataset], human_ratings[dataset])
    correlations[dataset] = {"r": r, "p": p}
```

**Outputs:**
- Per-dataset correlation coefficients (r) with p-values
- 95% confidence intervals via bootstrap (1000 iterations)

**Acceptance Criteria:**
- Correlation computed for all three datasets
- All p-values < 0.05 (statistical significance)
- Bootstrap CI non-overlapping for HumanEval vs SWE-bench

---

### FR-3: ANOVA Test for Task-Dependent Variance

**Requirement:** Test whether correlation varies significantly across task types using one-way ANOVA.

**Inputs:**
- Correlation coefficients: r_humaneval, r_mbpp, r_swebench

**Processing:**
```python
from scipy.stats import f_oneway

# Bootstrap to generate correlation distributions
corr_distributions = {
    dataset: [pearsonr(resample(exec), resample(human))[0] for _ in range(1000)]
    for dataset in datasets
}

f_stat, p_anova = f_oneway(
    corr_distributions["HumanEval"],
    corr_distributions["MBPP"],
    corr_distributions["SWE-bench"]
)
```

**Outputs:**
- F-statistic
- p-value (threshold: <0.05)

**Acceptance Criteria:**
- ANOVA p < 0.05 (statistically significant variance)

---

### FR-4: Effect Size Computation

**Requirement:** Compute effect size as absolute correlation difference between competitive (HumanEval) and realistic (SWE-bench) tasks.

**Inputs:**
- r_humaneval, r_swebench

**Processing:**
```python
effect_size = abs(correlations["HumanEval"]["r"] - correlations["SWE-bench"]["r"])
```

**Outputs:**
- Effect size value (threshold: >0.3)

**Acceptance Criteria:**
- Effect size > 0.3 (medium to large effect)

---

### FR-5: Variance Decomposition

**Requirement:** Compute between-task and within-task variance to validate variance criterion.

**Inputs:**
- Correlation values per dataset
- Bootstrap distributions per dataset

**Processing:**
```python
import numpy as np

# Between-task variance
between_var = np.var([
    correlations["HumanEval"]["r"],
    correlations["MBPP"]["r"],
    correlations["SWE-bench"]["r"]
])

# Within-task variance (mean across datasets)
within_vars = []
for dataset in datasets:
    bootstrap_samples = [pearsonr(resample(exec), resample(human))[0] for _ in range(1000)]
    within_vars.append(np.var(bootstrap_samples))
within_var = np.mean(within_vars)

variance_ratio = between_var / within_var
```

**Outputs:**
- Between-task variance
- Within-task variance (mean)
- Variance ratio (threshold: ≥2.0)

**Acceptance Criteria:**
- Between-task variance ≥ 2× within-task variance

---

### FR-6: Visualization Generation

**Requirement:** Generate three required figures for validation report.

**Figure 1: Correlation by Task Type (Mandatory)**
- Bar chart: execution-human correlation for each dataset
- Error bars: 95% bootstrap confidence intervals
- Horizontal lines: predicted thresholds (0.8, 0.5)
- Save: `{hypothesis_folder}/figures/correlation_by_task.png`

**Figure 2: Correlation Heatmap**
- 3×3 grid: datasets (rows) × correlation pairs (columns)
- Color scale: Pearson r value (-1 to 1)
- Annotate cells with r values
- Save: `{hypothesis_folder}/figures/correlation_heatmap.png`

**Figure 3: Variance Decomposition**
- Bar chart: between-task variance (single bar) vs within-task variance (mean, error bars)
- Horizontal line: 2× within-task threshold
- Save: `{hypothesis_folder}/figures/variance_decomposition.png`

**Acceptance Criteria:**
- All figures generated and saved
- Figures readable (axis labels, legends, titles)
- Figure paths returned in validation results

---

### FR-7: Validation Report Generation

**Requirement:** Generate 04_validation.md report with pass/fail status and evidence.

**Inputs:**
- Correlation values, p-values, confidence intervals
- ANOVA results (F-statistic, p-value)
- Effect size
- Variance ratio
- Figure paths

**Processing:**
- Check primary criteria: ANOVA p < 0.05 AND effect size > 0.3
- Check secondary criteria: variance ratio ≥ 2.0
- Determine overall pass/fail status

**Outputs:**
- `04_validation.md` with:
  - Results summary table (correlation per dataset)
  - Statistical test results (ANOVA, effect size, variance ratio)
  - Pass/fail status with evidence
  - Figure references

**Acceptance Criteria:**
- Report includes all required sections
- Pass/fail status matches criteria
- Figure paths valid

---

## Non-Functional Requirements

### NFR-1: Reproducibility

**Requirement:** All statistical computations must be reproducible with fixed random seed.

**Implementation:**
```python
import numpy as np
np.random.seed(42)
```

**Acceptance Criteria:**
- Bootstrap results identical across runs with same seed
- Variance values stable to 4 decimal places

---

### NFR-2: Performance

**Requirement:** Analysis completes within 5 minutes on standard hardware.

**Constraints:**
- Bootstrap iterations: 1000 per dataset (3000 total)
- No GPU required (CPU-only statistical analysis)

**Acceptance Criteria:**
- Total runtime < 5 minutes on CPU-only system

---

### NFR-3: Data Integrity

**Requirement:** Validate h-e1 feedback data integrity before analysis.

**Checks:**
- No missing values (NaN/Inf)
- Sample counts match expected (HumanEval: 164, MBPP: 500, SWE-bench: 300)
- Human ratings in valid range (1-5 scale)
- Execution scores binary (0 or 1)

**Acceptance Criteria:**
- All integrity checks pass
- Error raised if any check fails (fail-fast)

---

## Dependencies

### Prerequisite Hypotheses

- **h-e1 (VALIDATED):** Feedback data collection pipeline, correlation computation infrastructure
- **h-m1 (VALIDATED):** Specification completeness construct validity

### Required Data

- h-e1 feedback cache:
  - `{research_folder}/.data_cache/feedback/h-e1/humaneval_exec.npy`
  - `{research_folder}/.data_cache/feedback/h-e1/humaneval_ai.npy`
  - `{research_folder}/.data_cache/feedback/h-e1/humaneval_human.npy`
  - (same for mbpp, swebench)

### External Dependencies

- `scipy` (>=1.9.0): Statistical functions (pearsonr, f_oneway)
- `numpy` (>=1.23.0): Array operations, variance, bootstrap
- `matplotlib` (>=3.5.0): Figure generation
- `seaborn` (>=0.12.0): Heatmap visualization

---

## Success Criteria

### Primary (MUST_WORK Gate)

1. **ANOVA Significance:** p < 0.05
2. **Effect Size:** |r_HumanEval - r_SWE-bench| > 0.3
3. **Code Execution:** No runtime errors

### Secondary (Evidence Quality)

4. **Variance Ratio:** Between-task ≥ 2× within-task
5. **Predicted Pattern Match:**
   - HumanEval: r > 0.8
   - MBPP: 0.6 < r < 0.8
   - SWE-bench: r < 0.5

### Validation Pass Condition

Primary criteria met → PASS (gate satisfied)  
Primary criteria failed → FAIL (gate unsatisfied, blocks h-m3)

---

## Out of Scope

- Model training (h-m2 is statistical analysis only)
- New data collection (reuses h-e1 feedback data)
- Qualitative analysis (covered by h-m1)
- Metric development (uses standard Pearson correlation, ANOVA)

---

## Technical Notes

### Data Reuse from h-e1

h-m2 analysis pipeline loads pre-collected feedback data from h-e1 validation. No new model inference or human rating collection required.

**h-e1 Data Collection Summary:**
- Execution feedback: Test suite pass/fail (binary)
- AI feedback: Reward model scores (continuous 0-1)
- Human feedback: 3 raters per sample, 5-point scale (1=poor, 5=excellent), mean aggregation
- Inter-rater reliability: Cohen's kappa = 0.72 (substantial agreement)

### Statistical Analysis Pipeline

```python
# High-level pipeline
def validate_h_m2():
    # Step 1: Load h-e1 feedback data
    data = load_h_e1_feedback()
    
    # Step 2: Compute correlations per dataset
    correlations = {}
    for dataset in ["HumanEval", "MBPP", "SWE-bench"]:
        r, p = pearsonr(data[dataset]["exec"], data[dataset]["human"])
        ci = bootstrap_ci(data[dataset]["exec"], data[dataset]["human"])
        correlations[dataset] = {"r": r, "p": p, "ci": ci}
    
    # Step 3: ANOVA test
    f_stat, p_anova = anova_test(correlations)
    
    # Step 4: Effect size
    effect_size = abs(correlations["HumanEval"]["r"] - correlations["SWE-bench"]["r"])
    
    # Step 5: Variance decomposition
    variance_ratio = compute_variance_ratio(correlations)
    
    # Step 6: Generate figures
    generate_figures(correlations, variance_ratio)
    
    # Step 7: Validation report
    generate_report(correlations, p_anova, effect_size, variance_ratio)
```

---

## Appendix: Experiment Brief Reference

**Source:** `h-m2/02c_experiment_brief.md`  
**Specification Level:** 1.5 (Concrete + Pseudo-code)  
**Gate Type:** MUST_WORK  
**Prerequisites:** h-e1 (VALIDATED), h-m1 (VALIDATED)
