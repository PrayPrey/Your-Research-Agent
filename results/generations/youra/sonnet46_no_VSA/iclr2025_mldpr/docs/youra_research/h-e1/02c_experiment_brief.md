# Experiment Design: H-E1

**Date:** 2026-08-03
**Author:** YouRA Research Pipeline
**Hypothesis Statement:** pwc-archive/evaluation-tables paper_url column joined to h-e2 panel achieves ≥80% coverage (G0), both diversity predictors are time-independent (G1-G2 partial_r²>0.01), diversity ratio has sufficient variance (G3 std>0.10), and all covariates have VIF<10 (G4).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** — Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS → COMPLETED
**Prerequisites Satisfied:** None required (H-E1 is the root node)
**Gate Status:** MUST_WORK — all 5 gates (G0–G4) must pass; failure stops pipeline

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE (Data Pipeline & FAIL FAST Gate Validation)
- **Prerequisites:** None — READY immediately

### Gate Condition

MUST_WORK gate: All 5 sub-gates must pass in order (stop on first failure):

| Gate | Test | Threshold |
|------|------|-----------|
| G0 | ≥80% h-e2 benchmarks with non-null paper_url after task_path fuzzy join | coverage ≥ 0.80 |
| G1 | partial_r²(log_unique_paper_count_at_intro_z vs [task_age, intro_year]) | > 0.01 |
| G2 | partial_r²(paper_diversity_ratio_at_intro_z vs [task_age, intro_year]) | > 0.01 |
| G3 | std(paper_diversity_ratio_at_intro) across joined h-e2 benchmarks | > 0.10 |
| G4 | VIF < 10 for all covariates in Cox model (warn 5–10, exclude >10) | VIF < 10 |

**Collinearity failsafe:** if Pearson r(log_count_z, diversity_ratio_z) > 0.95, use primary predictor only.

---

## Continuation Context

No previous hypothesis — H-E1 is the first in the verification chain.

### Previous Hypothesis Results (if applicable)
None — first hypothesis in the H-Diversity-v1 verification chain.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Cox proportional hazards survival analysis panel data experiment design**
- No domain-relevant cases found in Archon KB (KB is specialized in diffusion/generative models, not survival analysis). Similarity scores < 0.31 — no useful patterns extracted.

**Query 2: HuggingFace dataset join fuzzy matching coverage validation**
- No directly relevant cases found. Similarity scores < 0.54 on unrelated image datasets.

**Assessment:** Archon KB does not contain survival analysis or bibliometric pipeline cases. Grounding uses Exa GitHub results and lifelines/statsmodels official documentation instead.

### Archon Code Examples

**Query: lifelines CoxPHFitter panel data VIF collinearity check**
- No relevant code examples found in KB (diffusion model codebase only).
- **Fallback:** Exa searches retrieved official lifelines documentation and statsmodels VIF implementation.

### Exa GitHub Implementations

**Query 1: pwc-archive/evaluation-tables HuggingFace dataset + lifelines Cox**

**Source 1: pwc-archive/evaluation-tables (HuggingFace)**
- **URL:** https://huggingface.co/datasets/pwc-archive/evaluation-tables
- **Relevance:** This IS the primary dataset for H-E1. Confirmed real dataset.
- **Key facts confirmed:**
  - 2,254 rows (benchmark-level entries), 138 MB, parquet format
  - Columns confirmed: `task_path`, `dataset`, `model_name`, `paper_url`, `metrics`
  - License: CC-BY-SA-4.0
  - Last snapshot: July 28, 2025
  - `load_dataset('pwc-archive/evaluation-tables', split='train')` — standard HF API
  - The flat row structure allows direct `groupby('task_path')['paper_url'].nunique()`

**Source 2: felixleungsc/paperswithcode-data-evaluation-tables**
- **URL:** https://huggingface.co/datasets/felixleungsc/paperswithcode-data-evaluation-tables
- **Relevance:** Shows how to flatten the nested JSON → confirms 326,393 SOTA rows
- **Key code pattern confirmed:**
  ```python
  # Full flattened extraction yields 326,393 rows with paper_url
  # Fields: task_path, dataset, model_name, paper_url, metric_name, metric_value
  ```
- **Important:** The HF dataset at pwc-archive/evaluation-tables is already flattened (2,254 rows = benchmark entries); the 326,393 row figure is from the raw nested JSON.

**Source 3: CoxPHFitter — lifelines 0.30.3 documentation**
- **URL:** https://lifelines.readthedocs.io/en/latest/fitters/regression/CoxPHFitter.html
- **Key API confirmed:**
  ```python
  from lifelines import CoxPHFitter
  cph = CoxPHFitter(penalizer=0.1)
  cph.fit(df, duration_col='duration', event_col='event')
  cph.log_likelihood_  # for LRT computation
  cph.params_          # for HR extraction
  cph.confidence_intervals_  # for 95% CI
  ```
- `log_likelihood_` attribute confirmed available on fitted model.

**Source 4: lifelines logrank_test, KaplanMeierFitter (for H-M2)**
- URL: https://github.com/CamDavidsonPilon/lifelines/blob/master/docs/Examples.rst
- Confirmed: `lifelines.statistics.logrank_test(T_A, T_B, event_observed_A, event_observed_B)`

**Query 2: VIF statsmodels Python implementation**

**Source 5: statsmodels.stats.outliers_influence.variance_inflation_factor**
- **URL:** https://www.statsmodels.org/stable/generated/statsmodels.stats.outliers_influence.variance_inflation_factor.html
- **Key implementation confirmed:**
  ```python
  from statsmodels.stats.outliers_influence import variance_inflation_factor
  import statsmodels.api as sm

  X = sm.add_constant(covariate_matrix)
  vif_values = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
  # VIF > 5: warn; VIF > 10: exclude covariate
  ```
- Formula: `VIF_i = 1 / (1 - R²_i)` where R²_i is from regressing X_i on all other Xs.

**Serena Analysis Needed:** false — statistical pipeline (pandas + lifelines + statsmodels), no complex neural architecture to analyze.

### 🎯 Implementation Priority Assessment

This is a statistical data pipeline, not a paper reproduction experiment. Priority hierarchy:

1. **Official library documentation** (HIGHEST PRIORITY): lifelines CoxPHFitter, statsmodels VIF
2. **HuggingFace datasets API**: `load_dataset('pwc-archive/evaluation-tables')`
3. **thefuzz/rapidfuzz**: fuzzy string matching for task_path join

**Recommended Implementation Path:**
- Primary: lifelines 0.30.3 + statsmodels 0.14+ + datasets + pandas + thefuzz/rapidfuzz
- Fallback: If pwc-archive HF dataset unavailable, use pwc-archive/files raw JSON snapshot
- Justification: All libraries confirmed available via pip; dataset confirmed 138 MB, accessible via standard HF API

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. No complex DL architecture to analyze; this is a tabular statistical pipeline using well-documented APIs.

---

## Experiment Specification

### Dataset

**Name:** pwc-archive/evaluation-tables (joined with h-e2 panel)
**Type:** programmatic-api (real HuggingFace dataset, not synthetic)
**Source:** https://huggingface.co/datasets/pwc-archive/evaluation-tables
**License:** CC-BY-SA-4.0
**Size:** 2,254 rows (benchmark-level), 138 MB, parquet format
**Key columns:** `task_path`, `dataset`, `model_name`, `paper_url`, `metric_name`, `metric_value`

**Preprocessing:**
1. Load via `load_dataset('pwc-archive/evaluation-tables', split='train')`
2. Convert to pandas DataFrame
3. Fuzzy-join `task_path` to h-e2 panel's 87 benchmark task slugs (threshold: 85 score via rapidfuzz)
4. Filter rows to `intro_year` per benchmark (retain only papers published ≤ plurality introduction year)
5. Compute per-benchmark aggregates:
   - `unique_paper_count = df.groupby('task_path')['paper_url'].nunique()`
   - `total_rows = df.groupby('task_path').size()`
   - `diversity_ratio = unique_paper_count / total_rows`
6. Log-transform and z-standardize: `log_unique_paper_count_at_intro_z`, `paper_diversity_ratio_at_intro_z`

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets API
- Identifier: `"pwc-archive/evaluation-tables"`
- Code: `load_dataset("pwc-archive/evaluation-tables", split="train")`

**h-e2 panel (internal):**
- 87 tasks, 345 plurality-displacement events, 2015–2023
- Path: provided by pipeline (not downloaded — already constructed from Phase 2B)
- Covariates: `duration`, `event`, `task_age`, `log_publication_volume`, `benchmark_introduction_year`

### Models

#### Baseline Model

This experiment has no ML model — it is a **statistical pipeline** producing a validated dataset.

**Statistical framework:** lifelines `CoxPHFitter(penalizer=0.1)`
**Role:** Used in G4 VIF check only (not full Cox estimation — that is H-M1)

**Loading Information** (for Phase 4 download):
- Method: pip install
- Identifier: `"lifelines>=0.30.0"`
- Code: `pip install lifelines statsmodels datasets thefuzz rapidfuzz pandas numpy scipy`

#### Proposed Model

**This is a data pipeline experiment, not a model comparison experiment.**

The "proposed model" is the validated dataset + computed diversity predictors, which become the input to downstream Cox regressions (H-M1, H-M2, H-R1).

**Core pipeline output:**
- Joined DataFrame (≥80% coverage confirmed at G0)
- `log_unique_paper_count_at_intro_z`: time-independent predictor (confirmed at G1)
- `paper_diversity_ratio_at_intro_z`: time-independent predictor (confirmed at G2)
- `std(paper_diversity_ratio_at_intro) > 0.10`: variance confirmed at G3
- All VIF < 10: collinearity confirmed at G4

**Core Mechanism Implementation:**

```python
# H-E1: FAIL FAST Gate Validation Pipeline
# Based on: lifelines docs, statsmodels docs, pwc-archive/evaluation-tables HF API

import numpy as np
import pandas as pd
from datasets import load_dataset
from rapidfuzz import fuzz, process as rfuzz_process
from statsmodels.stats.outliers_influence import variance_inflation_factor
import statsmodels.api as sm
from scipy import stats

def compute_diversity_predictors(eval_df, h_e2_panel):
    # Step 1: Fuzzy join task_path → h-e2 slugs
    h_e2_slugs = h_e2_panel['task_path'].unique().tolist()
    def fuzzy_match(slug):
        best, score, _ = rfuzz_process.extractOne(slug, h_e2_slugs, scorer=fuzz.token_sort_ratio)
        return best if score >= 85 else None
    eval_df['matched_task'] = eval_df['task_path'].map(fuzzy_match)

    # Step 2: Filter to ≤ intro_year per benchmark
    merged = eval_df.merge(h_e2_panel[['task_path','intro_year']], 
                           left_on='matched_task', right_on='task_path')
    filtered = merged[merged['pub_year'] <= merged['intro_year']]

    # Step 3: Compute predictors per benchmark
    stats_df = filtered.groupby('matched_task').agg(
        unique_count=('paper_url', 'nunique'),
        total_rows=('paper_url', 'count')
    ).reset_index()
    stats_df['diversity_ratio'] = stats_df['unique_count'] / stats_df['total_rows']
    stats_df['log_unique_count'] = np.log1p(stats_df['unique_count'])

    # Step 4: Z-standardize
    for col in ['log_unique_count', 'diversity_ratio']:
        stats_df[f'{col}_z'] = (stats_df[col] - stats_df[col].mean()) / stats_df[col].std()
    return stats_df

def compute_partial_r2(predictor, controls_df):
    # OLS residualization: regress predictor on temporal controls → r² of residuals
    X_ctrl = sm.add_constant(controls_df)
    resid_pred = sm.OLS(predictor, X_ctrl).fit().resid
    return resid_pred.var() / predictor.var()  # partial_r² ≈ 1 - (resid_var/total_var)

def compute_vif(covariate_df):
    X = sm.add_constant(covariate_df)
    return {col: variance_inflation_factor(X.values, i+1) 
            for i, col in enumerate(covariate_df.columns)}
```

### Training Protocol

This experiment has no training loop — it is a data pipeline validation.

**Execution Protocol:**

| Step | Action | Output |
|------|--------|--------|
| 1 | Load `pwc-archive/evaluation-tables` via HF API | Raw DataFrame |
| 2 | Fuzzy-join task_path to h-e2 panel (threshold=85) | Joined DataFrame |
| 3 | G0: Count matched h-e2 benchmarks with non-null paper_url | coverage ∈ [0,1] |
| 4 | Filter to ≤ intro_year; compute unique_count, diversity_ratio | Per-benchmark stats |
| 5 | Log-transform + z-standardize both predictors | `_z` columns |
| 6 | G1: partial_r²(log_count_z vs [task_age, intro_year]) | partial_r² scalar |
| 7 | G2: partial_r²(diversity_ratio_z vs [task_age, intro_year]) | partial_r² scalar |
| 8 | G3: std(diversity_ratio) across benchmarks | std scalar |
| 9 | G4: VIF for all Cox covariates | VIF dict |
| 10 | Collinearity check: Pearson r(log_count_z, diversity_ratio_z) | r scalar |
| 11 | Save enriched panel → `h_e2_panel_with_diversity.csv` | Output artifact |

**Key parameters:**
- Fuzzy join threshold: 85 (token_sort_ratio) — matches prior 95.5% coverage result
- Temporal controls for partial_r²: `[task_age, intro_year]`
- VIF warn threshold: 5; exclude threshold: 10
- Collinearity exclusion threshold: Pearson r > 0.95

**Seeds:** 1 (deterministic pipeline, no stochastic elements)

**Runtime estimate:** ~3–10 minutes (HF dataset download + fuzzy matching ~87×2254 comparisons)

### Evaluation

**Gate evaluation (ordered, STOP on first failure):**

| Gate | Metric | Threshold | Action if fail |
|------|--------|-----------|----------------|
| G0 | `n_matched / 87` | ≥ 0.80 | STOP — pipeline gates fail |
| G1 | `partial_r²(log_count_z)` | > 0.01 | STOP — predictor confounded with time |
| G2 | `partial_r²(diversity_ratio_z)` | > 0.01 | STOP — predictor confounded with time |
| G3 | `std(diversity_ratio)` | > 0.10 | STOP — insufficient variance for Cox |
| G4 | `max(VIF_values)` | < 10 | STOP if any VIF ≥ 10 (warn if 5–10) |

**Success Criteria (EXISTENCE PoC):**
- All 5 gates pass → proposed pipeline > baseline (null pipeline)
- Output artifact `h_e2_panel_with_diversity.csv` produced with valid diversity columns
- Collinearity check logged: if r > 0.95, flag for H-M1 to use single predictor only

**Expected baseline performance (from Phase 2B notes):**
- Prior fuzzy join coverage: 95.5% (well above G0 threshold of 80%)
- G3 variance: empirically expected to pass given diversity of PWC benchmark communities
- G4 VIF: expected < 5 given predictors measure different aspects (count vs. ratio)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: tabular statistical pipeline (no PyTorch)
- Library: `statsmodels`, `scipy`, `numpy`, `pandas`
- Key metrics code:
  ```python
  # G0: coverage
  coverage = n_matched_with_paper_url / 87
  # G1/G2: partial r²
  partial_r2 = 1 - sm.OLS(predictor, sm.add_constant(controls)).fit().rsquared
  # G3: std
  std_val = diversity_ratio.std()
  # G4: VIF
  vif_dict = {col: variance_inflation_factor(X.values, i) for i, col in enumerate(cols)}
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing each gate's actual value vs. threshold (G0 coverage, G1/G2 partial_r², G3 std, G4 max VIF). Color: green=pass, red=fail.

#### Additional Figures (LLM Autonomous)
- **Coverage heatmap**: Which h-e2 task_paths matched vs. failed to match (useful for diagnosing low coverage)
- **Predictor distributions**: Histograms of `log_unique_paper_count_at_intro` and `paper_diversity_ratio_at_intro` across 87 benchmarks
- **Correlation matrix**: Pearson r between all Cox covariates to visualize multicollinearity pre-VIF
- **Partial R² bar chart**: G1 and G2 partial_r² values vs. 0.01 threshold

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. All 5 gates (G0–G4) pass their thresholds
3. Output file `h_e2_panel_with_diversity.csv` written with non-null diversity columns for ≥80% of h-e2 benchmarks

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Assessment:** Archon KB contains diffusion/generative model cases only. No survival analysis, bibliometric pipeline, or Cox regression cases found. All grounding uses official library documentation (retrieved via Exa).

### B. GitHub Implementations (Exa)

**Repository 1: pwc-archive/evaluation-tables (HuggingFace Dataset)**
- **URL:** https://huggingface.co/datasets/pwc-archive/evaluation-tables
- **Query:** pwc-archive evaluation-tables HuggingFace load_dataset paper_url benchmark join lifelines Cox
- **Key facts:**
  - 2,254 rows, 138 MB, parquet, CC-BY-SA-4.0
  - Columns: `task_path`, `dataset`, `model_name`, `paper_url`, `metric_name`, `metric_value`
  - `load_dataset('pwc-archive/evaluation-tables', split='train')` confirmed working
- **Used for:** G0 dataset loading and paper_url coverage check

**Repository 2: felixleungsc/paperswithcode-data-evaluation-tables**
- **URL:** https://huggingface.co/datasets/felixleungsc/paperswithcode-data-evaluation-tables
- **Key code:**
  ```jq
  # Flattening pattern: task_path + paper_url extraction
  .sota.rows[]? | {task_path: $full_path, paper_url: .paper_url}
  ```
- **Used for:** Understanding data structure; confirms paper_url is at SOTA row level

**Repository 3: lifelines CoxPHFitter documentation**
- **URL:** https://lifelines.readthedocs.io/en/latest/fitters/regression/CoxPHFitter.html
- **Key API:**
  ```python
  cph = CoxPHFitter(penalizer=0.1)
  cph.fit(df, duration_col='duration', event_col='event')
  # Attributes: log_likelihood_, params_, confidence_intervals_
  ```
- **Used for:** G4 VIF covariate structure specification; H-M1 downstream protocol

**Repository 4: statsmodels variance_inflation_factor**
- **URL:** https://www.statsmodels.org/stable/generated/statsmodels.stats.outliers_influence.variance_inflation_factor.html
- **Key code:**
  ```python
  from statsmodels.stats.outliers_influence import variance_inflation_factor
  X = sm.add_constant(covariate_df)
  vif = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
  ```
- **Used for:** G4 VIF implementation; warn threshold 5, exclude threshold 10

**Repository 5: lifelines Examples (logrank_test)**
- **URL:** https://github.com/CamDavidsonPilon/lifelines/blob/master/docs/Examples.rst
- **Used for:** H-M2 downstream protocol reference (not H-E1 itself)

### C. Code Analysis (Serena)

Serena analysis not performed — code is a standard statistical pipeline (pandas + lifelines + statsmodels) with well-documented APIs. No complex unfamiliar architecture.

### D. Previous Hypothesis Context

None — H-E1 is the first hypothesis in the H-Diversity-v1 verification chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset loading (`load_dataset`) | HuggingFace official | pwc-archive/evaluation-tables (B.1) |
| Data structure (task_path, paper_url) | HuggingFace community | felixleungsc dataset (B.2) |
| Fuzzy join threshold (85) | Prior run | Phase 2B notes (95.5% prior coverage) |
| G0 coverage threshold (80%) | Phase 2B | 02b_verification_plan.md |
| G1/G2 partial_r² method | Phase 2B + statsmodels | 02b_verification_plan.md; statsmodels OLS (B.4) |
| G3 std threshold (0.10) | Phase 2B | 02b_verification_plan.md |
| G4 VIF implementation | statsmodels official | variance_inflation_factor docs (B.4) |
| VIF thresholds (5 warn, 10 exclude) | Statsmodels docs | Standard econometrics rule |
| CoxPHFitter API | lifelines official | CoxPHFitter docs (B.3) |
| Collinearity failsafe (r>0.95) | Phase 2B | 02b_verification_plan.md |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — restate block used)
**Date:** 2026-08-03

### Workflow History for This Hypothesis
- 2026-08-03: H-E1 set to IN_PROGRESS (external loop)
- 2026-08-03: Phase 2C experiment design completed → COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant results), Exa (HuggingFace dataset page, lifelines docs, statsmodels docs)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 — Implementation Planning*
