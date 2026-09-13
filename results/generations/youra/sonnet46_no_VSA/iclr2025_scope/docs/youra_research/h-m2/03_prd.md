# Product Requirements Document: H-M2
# Depth-Slope Differential Analysis: MOHAWK-SSM vs LAWCAT on LongBench v2

---
stepsCompleted:
  - Executive Summary
  - Problem Statement
  - Functional Requirements
  - Non-Functional Requirements
  - Data Specification
  - Success Criteria
  - Dependencies
---

## 1. Executive Summary

H-M2 tests a causal mechanism claim: MOHAWK-SSM (bounded-state recurrence) exhibits a significantly steeper accuracy degradation slope with needle depth than LAWCAT (causal Conv1D + GLA) on retrieval-heavy LongBench v2 tasks. This is a **post-hoc statistical analysis** of H-E1 per-example evaluation data — no model training or GPU inference required. The deliverable is a Python statistical analysis pipeline that fits mixed-effects logistic regression per model and computes the β_depth coefficient ratio.

**Gate:** SHOULD_WORK — |β_depth^SSM| ≥ 2× |β_depth^LAWCAT| with non-overlapping 95% CIs.

---

## 2. Problem Statement

**Research Question:** Does SSM bounded-state exponential forgetting produce a measurably steeper depth-accuracy degradation curve than LAWCAT's Conv1D local attention, as predicted by the H-M1 architectural analysis?

**Null Hypothesis (H0):** |β_depth^SSM| / |β_depth^LAWCAT| < 2.0 OR CIs overlap → depth sensitivity is similar across architectures.

**Alternative (H-M2):** |β_depth^SSM| / |β_depth^LAWCAT| ≥ 2.0 AND CIs non-overlapping → SSM exhibits architecture-specific depth penalty.

**Context:** H-M1 confirmed SSD approximation quality is bounded (slope ≤ 0.5); H-E1 produced per-example accuracy data for 503 LongBench v2 questions across MOHAWK-SSM, LAWCAT, Hybrid-4, and teacher LLaMA-3-8B. H-M2 performs statistical analysis on this existing data.

---

## 3. Functional Requirements

### FR-1: Data Loading and Filtering

**FR-1.1: Load H-E1 Per-Example Results**
- Load JSON prediction files from H-E1 evaluation run for two student models:
  - MOHAWK-SSM LLaMA-3-8B
  - LAWCAT LLaMA-3-8B
- Expected format: `[{"_id": str, "domain": str, "pred": str, "answer": str, "context": str, ...}]`
- Load 503 examples per model

**FR-1.2: Filter to Retrieval-Heavy Subset**
- Apply domain filter: `domain in ["Multi-Document QA", "Long Structured Data Understanding"]`
- Expected subset size: ~125–166 examples per model
- Validate: at least 100 examples per model after filtering

**FR-1.3: Load LongBench v2 Reference Data (Fallback)**
- If H-E1 results lack `context` field: load from HuggingFace `"THUDM/LongBench-v2"` for context fields
- Merge on `_id` field
- This is a fallback only — H-E1 data should already contain context

### FR-2: Depth Percentile Computation

**FR-2.1: Keyword-Based Depth Percentile**
- For each example: extract keywords from `question` + `answer` choice
- Search for keyword positions in `context` via `str.find()`
- Compute: `depth_percentile = earliest_keyword_position / len(context)`
- Range: [0, 1]; 0 = answer at end of context, 1 = answer at beginning
- Fallback: if no keyword found, set depth_percentile = 0.5

**FR-2.2: Depth Percentile Validation**
- Assert: `depth_percentile.nunique() > 10` (non-constant)
- Assert: all values in [0, 1]
- Assert: ≥100 samples per model in retrieval subset

**FR-2.3: BM25 Fallback (Optional Enhancement)**
- If substring search yields >50% fallback (depth=0.5) cases, use BM25 scoring for position

### FR-3: Mixed-Effects Logistic Regression

**FR-3.1: Binary Outcome Encoding**
- `correct = int(pred == answer)` per example
- Verify: both classes (0 and 1) present in retrieval subset for each model

**FR-3.2: Primary — rpy2 + lme4::glmer**
- Install check: `rpy2`, R `lme4`, R `lmerTest`
- Formula: `correct ~ depth_percentile + (1|task_id)`, `family = binomial`
- Extract: β_depth coefficient, 95% CI via `confint(model)`, p-value via `lmerTest`
- Apply Holm correction for 2 tests (SSM p-value, LAWCAT p-value)

**FR-3.3: Fallback — statsmodels Linear Mixed Model**
- If rpy2/R unavailable: use `statsmodels.formula.api.mixedlm`
- Formula: `correct ~ depth_percentile`, groups by `task_id`
- Note: linear approximation for binary outcome — flag in output as approximation
- Extract: coefficient, 95% CI from `mdf.conf_int()`

**FR-3.4: Per-Model Regression**
- Fit separate model for MOHAWK-SSM and LAWCAT
- Store: `{model: {beta, ci_low, ci_high, p_value, method}}`

### FR-4: Gate Criterion Evaluation

**FR-4.1: Ratio Computation**
- `ratio = |β_depth^SSM| / max(|β_depth^LAWCAT|, 1e-9)`
- Test: `ratio >= 2.0`

**FR-4.2: CI Non-Overlap Test**
- `overlap = (ssm_ci_high >= lawcat_ci_low) AND (lawcat_ci_high >= ssm_ci_low)`
- Gate passes if: `ratio >= 2.0 AND NOT overlap`

**FR-4.3: Result Classification**
- PASS: ratio ≥ 2.0, CIs non-overlapping
- PARTIAL: ratio ≥ 2.0 but CIs overlap, OR ratio < 2.0 but β_depth^SSM significantly < 0
- FAIL: ratio < 2.0 AND β_depth^SSM not significantly different from β_depth^LAWCAT

### FR-5: Visualization

**FR-5.1: Gate Metrics Bar Chart (Mandatory)**
- Bar chart: |β_depth^SSM| vs |β_depth^LAWCAT| with 95% CI error bars
- Horizontal reference line at 2× |β_depth^LAWCAT|
- Output: `docs/youra_research/h-m2/figures/gate_metrics.png`

**FR-5.2: Depth-Accuracy Scatter (Required)**
- Per-example scatter: depth_percentile (x) vs correct (y, jittered ±0.05)
- Overlaid logistic regression fit curves: MOHAWK-SSM (red), LAWCAT (blue)
- Output: `docs/youra_research/h-m2/figures/depth_accuracy_scatter.png`

**FR-5.3: Binned Accuracy by Depth Quartile (Required)**
- Bar chart: accuracy by quartile [0-25%, 25-50%, 50-75%, 75-100%] for both models
- Output: `docs/youra_research/h-m2/figures/depth_quartile_accuracy.png`

**FR-5.4: Forest Plot (Required)**
- β_depth with 95% CIs for MOHAWK-SSM and LAWCAT
- Ratio annotation
- Output: `docs/youra_research/h-m2/figures/beta_forest_plot.png`

### FR-6: Results Reporting

**FR-6.1: JSON Results File**
- Save full regression results to `docs/youra_research/h-m2/h_m2_results.json`
- Schema:
  ```json
  {
    "gate_pass": bool,
    "ratio": float,
    "mohawk_ssm": {"beta": float, "ci_low": float, "ci_high": float, "p_value": float, "method": str},
    "lawcat": {"beta": float, "ci_low": float, "ci_high": float, "p_value": float, "method": str},
    "sample_sizes": {"mohawk_ssm": int, "lawcat": int},
    "holm_corrected_p_values": {"mohawk_ssm": float, "lawcat": float},
    "depth_percentile_stats": {"mean": float, "std": float, "min": float, "max": float}
  }
  ```

**FR-6.2: Summary Markdown Report**
- Save `docs/youra_research/h-m2/h_m2_summary.md` with regression table, gate verdict, and figure references

---

## 4. Non-Functional Requirements

**NFR-1: Runtime** — Complete in <10 minutes on CPU (statistical analysis only, no GPU)

**NFR-2: Reproducibility** — Deterministic analysis; no random seeds needed (logistic regression is deterministic given data)

**NFR-3: Graceful Fallback** — If rpy2/R unavailable, statsmodels linear fallback with explicit warning in output

**NFR-4: Error Handling** — If H-E1 data file missing or lacks required fields, raise informative error with resolution instructions

**NFR-5: Sample Minimum** — Minimum 100 examples per model in retrieval subset for statistical validity; warn if below threshold

---

## 5. Data Specification

### 5.1 Input Data (from H-E1)

**Primary Input — H-E1 Per-Example Results:**
- Source: H-E1 evaluation run output files
- Expected paths (from H-E1 implementation):
  - MOHAWK-SSM: `docs/youra_research/h-e1/results/mohawk_ssm_predictions.json`
  - LAWCAT: `docs/youra_research/h-e1/results/lawcat_predictions.json`
- Alternative paths (check both): `h-e1/code/results/`, `h-e1/outputs/`
- Fields required: `_id`, `domain`, `pred`, `answer`, `context`

**Fallback Input — LongBench v2 HuggingFace:**
- `load_dataset('THUDM/LongBench-v2', split='train')` — for context field if missing from H-E1
- Merge on `_id`

### 5.2 Reference Data

**LongBench v2 Schema:**
- 503 questions total
- Multi-Document QA: ~125 questions
- Long Structured Data Understanding: ~33 questions
- Retrieval-heavy total: ~158 questions

### 5.3 Preprocessing Steps

1. Load JSON files
2. Filter by domain
3. Compute depth_percentile per example
4. Encode binary `correct` column
5. Assign `task_id` from `sub_domain` or `domain` for random effect grouping

---

## 6. Success Criteria

| Criterion | Threshold | Type |
|-----------|-----------|------|
| Gate pass | ratio ≥ 2.0 AND CIs non-overlapping | Primary |
| β_depth^SSM significantly < 0 | p < 0.01 (Holm-corrected) | Secondary |
| β_depth^LAWCAT near zero | p > 0.05 or |β| < |β_SSM|/2 | Secondary |
| Sample size ≥ 100 per model | after retrieval filter | Data quality |
| Analysis completes without error | N/A | PoC |
| All 4 figures generated | N/A | Visualization |

---

## 7. Dependencies

### 7.1 Python Packages

```
pandas>=1.5.0
numpy>=1.23.0
scipy>=1.10.0
matplotlib>=3.7.0
seaborn>=0.12.0
datasets>=2.14.0       # HuggingFace datasets (fallback context load)
statsmodels>=0.14.0    # Fallback linear mixed model
rpy2>=3.5.0            # Primary: GLMM via lme4 (optional if R available)
```

### 7.2 R Packages (if using rpy2 path)

```r
install.packages(c("lme4", "lmerTest"))
```

### 7.3 External Data Dependencies

- H-E1 evaluation output files (MOHAWK-SSM predictions JSON, LAWCAT predictions JSON)
- LongBench v2 HuggingFace dataset (fallback only)

### 7.4 Reference Repositories

- THUDM/LongBench: official benchmark (data schema reference)
- goombalab/mohawk: MOHAWK evaluation framework (output format reference)
- zeyuliu1037/LAWCAT: LAWCAT evaluation framework (output format reference)

---

## 8. Out of Scope

- Model training or distillation (H-M2 uses H-E1 outputs)
- GPU inference (CPU-only statistical analysis)
- New LongBench v2 evaluation runs (H-E1 data reused)
- Hypothesis H-E1 result generation (prerequisite, already completed)
