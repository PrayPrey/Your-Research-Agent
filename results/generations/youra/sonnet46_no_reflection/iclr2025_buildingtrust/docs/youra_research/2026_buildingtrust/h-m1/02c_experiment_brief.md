# Experiment Design: H-M1

**Date:** 2026-05-12
**Author:** Anonymous
**Hypothesis Statement:** Under the ≥30 LLM model set with computed RI scores, Spearman partial correlation ρ(RI, ECE | PC1, mean_confidence) ≥ 0.4 with Holm-corrected p < 0.05 and consistent positive sign across ≥2 of 3 family subgroups, because sharp decision boundaries cause overconfident predictions in brittle regions, producing calibration error.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM (MUST_WORK) Template** — Primary causal link: RI → ECE.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-E1 PASS (SD=0.1212, R²=0.5285, gate PASS)
**Gate Status:** MUST_WORK — failure stops pipeline and blocks H-M2, H-M3, H-M4

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (COMPLETED — PASS)

### Gate Condition
MUST_WORK: Spearman partial ρ(RI, ECE | PC1, mean_confidence) ≥ 0.4, Holm-corrected p < 0.05, consistent positive sign in ≥2 of 3 family subgroups (LLaMA, Mistral, GPT/Qwen). Failure invalidates entire RI construct and halts pipeline.

---

## Continuation Context

**Continuing from H-E1 (COMPLETED — PASS).**

### Previous Hypothesis Results (H-E1)
| Component | Result | Reuse Status |
|-----------|--------|--------------|
| SD(AdvGLUE_drop) | 0.1212 (PASS, threshold >0.05) | RI scores available |
| R²_residualization | 0.5285 (PASS, threshold <0.80) | RI pipeline validated |
| N models | 30 (9 families, 3 scales, 2 regimes) | Same model set |
| DataAssembler | `code/data_assembly.py` (17 tests) | Extend with ECE column |
| RIComputer | `code/compute_ri.py` (14 tests) | Reuse directly |
| Conda env | `youra-h-e1` (pingouin 0.6.1 installed) | Reuse or clone |
| Cap columns | bbh, arc_challenge, mmlu_pro, math_hard, gpqa, musr (v2 leaderboard) | Same |
| PC1 variance | 68.5% (sensitivity note; PC1 still dominant) | Same PC1 |

**Key insight from H-E1:** Real heterogeneous data yields R²=0.529, meaning 47% of adversarial fragility variance is NOT explained by capability — this is the RI signal that H-M1 tests for calibration coupling.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "Spearman partial correlation LLM calibration ECE experiment"**
- No domain-specific matches in KB (top results: diffusers/image-generation — unrelated domain)

**Query 2: "Expected calibration error partial correlation implementation challenges"**
- No domain-specific matches in KB

**Query 3: "LLM trust benchmark calibration adversarial correlation"**
- No domain-specific matches in KB

**Assessment:** Archon KB contains diffusion model content, not LLM trust research. No reusable past cases found. Proceeding with Exa findings.

### Archon Code Examples

**Query: "pingouin partial_corr Spearman Python"**
- No domain-specific code examples found (CLIP score / distributed inference content only)

**Archon KB conclusion:** 0 relevant sources. All implementation guidance from Exa searches below.

### Exa GitHub Implementations

**Query 1: p-lambda/verified_calibration — ECE Implementation**

**Repository**: `p-lambda/verified_calibration` (⭐152)
- **URL:** https://github.com/p-lambda/verified_calibration
- **Relevance:** Official NeurIPS 2019 calibration library referenced in Phase 2B verification protocol. Provides `get_ece()` and bootstrap CI support.
- **Install:** `pip install uncertainty-calibration`
- **Key Code:**
  ```python
  import calibration as cal
  # Standard ECE (Guo et al.)
  calibration_error = cal.get_ece(model_probs, labels)
  # More accurate debiased estimate
  calibration_error = cal.get_top_calibration_error(model_probs, labels, p=1)
  # Bootstrap CIs
  lower, _, upper = cal.get_calibration_error_uncertainties(model_probs, labels)
  ```
- **Notes:** Requires per-model probability arrays + ground-truth labels. For cross-model study, must compute per-model ECE score then aggregate into model-level scalar.

**Repository 2**: `Exploration-Lab/LLM-Calibration-Mechanism` (arxiv:2511.00280)
- **URL:** https://github.com/Exploration-Lab/LLM-Calibration-Mechanism
- **Relevance:** Computes ECE/MCE across open-weight LLMs on MMLU benchmark. Provides `compute_calibrations.sh` + `calibration_metrics.py` pipeline.
- **Key pattern:** Iterate over `model_ids` and `dataset_names`, compute ECE from saved logits/activations, aggregate results per model.
- **Training Config:** N/A (inference only)

**Repository 3**: `prateekchhikara/llms-calibration` (⭐19, TMLR 2025, arxiv:2502.11028)
- **URL:** https://github.com/prateekchhikara/llms-calibration
- **Relevance:** Direct precedent — ECE across multiple open-source LLMs on QA benchmarks (GSM8K, BoolQ, TruthfulQA, CommonSenseQA). Three-stage pipeline: dataset creation → model evaluation → analysis/visualization.
- **Calibration metrics:** ECE, MCE, Brier Score, reliability diagrams
- **Key pattern:** `src/02_model_evaluation.py` → extracts confidence scores → `src/03_analysis_visualization.py` → computes ECE per model

**Query 2: pingouin partial_corr — Partial Correlation Implementation**

**Repository**: `raphaelvallat/pingouin` (official docs, v0.6.1)
- **URL:** https://pingouin-stats.org/generated/pingouin.partial_corr.html
- **Relevance:** Exact function for ρ(RI, ECE | PC1, mean_confidence) with Spearman method. Already installed in `youra-h-e1` env.
- **Key Code:**
  ```python
  import pingouin as pg
  # Primary partial correlation
  result = pg.partial_corr(
      data=df,
      x="RI",
      y="ECE",
      covar=["PC1", "mean_confidence"],
      method="spearman"
  )
  # Returns: n, r, CI95, p_val
  # r = Spearman partial correlation coefficient
  # p_val = two-sided p-value

  # Pairwise with Holm correction across families
  result_families = pg.pairwise_corr(
      data=df_family,
      columns=["RI", "ECE"],
      covar=["PC1", "mean_confidence"],
      method="spearman",
      padjust="holm"
  )
  ```
- **v0.6.1 note:** Fixed numerical instability in `partial_corr`/`pcorr` when variables differ by orders of magnitude (#510). Already installed — use as-is.

**Serena Analysis Needed:** False — pingouin and uncertainty-calibration have clear documented APIs; no complex ML code requiring semantic analysis.

### 🎯 Implementation Priority Assessment

This is a **statistical analysis experiment** (not a paper reproduction). No official "author implementation" applies. Priority:
1. **pingouin.partial_corr** (Spearman + Holm) — canonical Python partial correlation library, already installed
2. **uncertainty-calibration** (p-lambda/verified_calibration) — canonical ECE library from NeurIPS 2019

**Recommended Implementation Path:**
- Primary: Extend H-E1 `DataAssembler` with ECE column; run `pg.partial_corr()` for full-set and per-family analysis
- Fallback: Compute Spearman partial manually via OLS residuals + `scipy.stats.spearmanr()` if pingouin fails
- Justification: H-E1 already validated DataAssembler + model matrix pipeline. ECE is new column; partial correlation is new analysis module. Minimal new code needed.

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. Pingouin `partial_corr()` and `uncertainty-calibration` `get_ece()` have unambiguous documented APIs. No complex ML code requiring semantic analysis.

---

## Experiment Specification

### Dataset

**ECE Scores via p-lambda/verified_calibration on QA Benchmarks**

- **Name:** ECE scores from QA benchmark inference (TrustLLM + lm-evaluation-harness model set)
- **Type:** standard (programmatic-api — computed from existing model set)
- **Source:** Per-model probability arrays extracted from QA benchmark inference (MMLU, BoolQ, TruthfulQA) via lm-evaluation-harness; ECE computed with `uncertainty-calibration`
- **Statistics:** 30 models × 1 ECE scalar per model = 30 data points; model matrix extends H-E1 CSV with ECE column
- **Preprocessing:** None (ECE is already a scalar per model)
- **Augmentation:** None
- **Type check:** REAL DATA — ECE derived from actual model inference on real QA benchmarks. NOT synthetic.

**Reuse from H-E1:**
- Model matrix CSV: `h-e1/code/outputs/model_matrix.csv` (30 models × capability + RI scores)
- RI scores CSV: `h-e1/code/outputs/ri_scores.csv`
- DataAssembler: `h-e1/code/data_assembly.py` — extend `assemble_matrix()` to add ECE column

**Loading Information** (for Phase 4 download):
- Method: Programmatic computation from lm-evaluation-harness benchmark logits
- Identifier: `uncertainty-calibration` (`pip install uncertainty-calibration`)
- Code:
  ```python
  import calibration as cal
  # For each model: compute ECE from QA benchmark probabilities
  ece_score = cal.get_ece(model_probs, labels)  # scalar per model
  # Add to model matrix as 'ECE' column
  ```

### Models

#### Baseline Model

**Same 30-LLM set as H-E1 (reused):**

| Property | Value |
|----------|-------|
| Model set | ≥30 LLMs: LLaMA (9), Mistral (6), Qwen (6), Gemma (2), Falcon (2), SOLAR (2), MPT (1), StableLM (1), Phi (1) |
| Scales | 7B, 13B, 70B+ |
| Training regimes | Pretrained, instruction-tuned |
| RI source | `h-e1/code/outputs/ri_scores.csv` (validated PASS) |
| Capability source | Open LLM Leaderboard v2 per-model detail datasets |

**Baseline comparison (capability-only predictor):**
- `ρ(PC1, ECE)` — Spearman correlation of capability alone with ECE (no RI term)
- Expected: ρ(PC1, ECE) ≈ 0.3–0.5 (from prior literature)
- This is the "null model" that H-M1 must outperform

**Loading Information** (for Phase 4):
- Method: Reuse `h-e1/code/outputs/model_matrix.csv` — no new model downloads needed
- Identifier: `h-e1/code/outputs/ri_scores.csv` for RI; extend with ECE column
- Code:
  ```python
  import pandas as pd
  df = pd.read_csv("../h-e1/code/outputs/model_matrix.csv")
  ri_df = pd.read_csv("../h-e1/code/outputs/ri_scores.csv")
  # Merge: df now has PC1, mean_confidence, RI; add ECE column
  ```

#### Proposed Model

**Architecture:** Partial correlation model — ρ(RI, ECE | PC1, mean_confidence)

**Core Mechanism: Spearman Partial Correlation with Holm Correction**

```python
# Core Mechanism: Spearman Partial Correlation Analysis for H-M1
# Based on: pingouin 0.6.1 partial_corr() + uncertainty-calibration get_ece()

import pingouin as pg
import calibration as cal
import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.multitest import multipletests

def compute_ece_per_model(model_probs_dict, labels_dict):
    """
    Args:
        model_probs_dict: {model_id: np.array shape (N,)} — predicted probs on QA benchmark
        labels_dict: {model_id: np.array shape (N,)} — ground-truth labels
    Returns:
        ece_series: pd.Series {model_id: ECE_scalar}
    """
    ece_scores = {}
    for model_id in model_probs_dict:
        ece_scores[model_id] = cal.get_ece(
            model_probs_dict[model_id], labels_dict[model_id]
        )
    return pd.Series(ece_scores, name="ECE")

def run_partial_correlation_analysis(df):
    """
    Args:
        df: pd.DataFrame with columns [model_id, RI, ECE, PC1, mean_confidence, family]
    Returns:
        results: dict with full-set and per-family partial correlations
    """
    # Step 1: Full-set Spearman partial correlation
    full_result = pg.partial_corr(
        data=df, x="RI", y="ECE",
        covar=["PC1", "mean_confidence"], method="spearman"
    )
    rho_full = full_result["r"].values[0]
    p_full = full_result["p_val"].values[0]

    # Step 2: Holm-corrected within-family partial correlations
    families = ["LLaMA", "Mistral", "Qwen"]
    rho_family, p_family = [], []
    for fam in families:
        sub = df[df["family"] == fam]
        if len(sub) >= 5:
            res = pg.partial_corr(
                data=sub, x="RI", y="ECE",
                covar=["PC1", "mean_confidence"], method="spearman"
            )
            rho_family.append(res["r"].values[0])
            p_family.append(res["p_val"].values[0])

    # Step 3: Holm correction across family tests
    _, p_holm, _, _ = multipletests(p_family, method="holm")
    consistent_positive = sum(r > 0 for r in rho_family)

    # Step 4: Gate evaluation
    gate_pass = (rho_full >= 0.4) and (p_full < 0.05) and (consistent_positive >= 2)
    return {
        "rho_full": rho_full, "p_full": p_full,
        "rho_family": dict(zip(families, rho_family)),
        "p_holm_family": dict(zip(families, p_holm)),
        "consistent_positive_families": consistent_positive,
        "gate_pass": gate_pass
    }
```

### Training Protocol

**No training** — this is a statistical analysis experiment (inference + correlation analysis).

**Computational Protocol:**

| Step | Operation | Tool |
|------|-----------|------|
| 1 | Load H-E1 model matrix (RI, PC1, mean_confidence, family) | pandas |
| 2 | Compute ECE per model from QA benchmark logits | uncertainty-calibration |
| 3 | Merge ECE into model matrix | pandas |
| 4 | Compute Spearman partial ρ(RI, ECE \| PC1, mean_confidence) | pingouin 0.6.1 |
| 5 | Holm-correct within-family partial correlations | statsmodels.multipletests |
| 6 | Fisher z-test: compare ρ_high_PC1 vs ρ_low_PC1 subgroups | scipy.stats |
| 7 | VIF check + Cook's distance outlier sensitivity | statsmodels, scipy |
| 8 | Bootstrap CIs (10K resamples) on ECE and ρ | numpy |
| 9 | Gate evaluation + export results | custom |

**Key parameters (from H-E1 continuation):**
- Seed: 42 (inherited)
- Bootstrap resamples: 10,000 (same as H-E1)
- n_models: 30 (same model set)
- Families for within-group: LLaMA (9 models), Mistral (6), Qwen (6) — top 3 largest families
- VIF threshold: < 5.0
- Cook's distance: flag > 4/n as outliers

**Environment:** Reuse `youra-h-e1` conda env (Python 3.10, pingouin 0.6.1 already installed)
- New package: `pip install uncertainty-calibration` (p-lambda/verified_calibration)

### Evaluation

**Primary Gate Metrics (MUST_WORK):**

| Metric | Formula | Threshold | Source |
|--------|---------|-----------|--------|
| Spearman partial ρ(RI, ECE) | `pg.partial_corr(x="RI", y="ECE", covar=["PC1","mean_confidence"], method="spearman")["r"]` | ≥ 0.4 | Phase 2B verification protocol |
| Holm-corrected p-value | `p_val` from `partial_corr` | < 0.05 | Phase 2B verification protocol |
| Family sign consistency | count(ρ_family > 0) across LLaMA, Mistral, Qwen | ≥ 2 of 3 | Phase 2B secondary criterion |

**Secondary Metrics:**

| Metric | Threshold | Purpose |
|--------|-----------|---------|
| Baseline ρ(PC1, ECE) | — | Null model comparison: RI adds signal beyond capability |
| VIF(RI, PC1, mean_confidence) | < 5.0 | Multicollinearity check |
| Cook's distance (influential models) | Flag > 4/30 | Outlier sensitivity |
| Fisher z-test p (ρ_high_PC1 vs ρ_low_PC1) | Report only | PC1 interaction check |

**Success Criteria:**
- PASS: ρ ≥ 0.4 AND Holm-p < 0.05 AND ≥2 families positive sign
- PARTIAL: ρ ≥ 0.3 AND p < 0.10 but below threshold → document as limitation, FAIL gate
- FAIL: ρ < 0.2 or sign reversal in >1 family → ABANDON construct, halt pipeline

**Expected Performance (from literature):**
- ρ(capability, ECE) ≈ 0.3–0.5 (prior work on capability-calibration link)
- Expected ρ(RI, ECE | PC1) ≥ 0.4 if sharp-boundary hypothesis holds
- Source: prateekchhikara/llms-calibration (TMLR 2025), TrustLLM ICML 2024

**Metrics Loading Information:**
- Task Type: Statistical correlation analysis (no ML training)
- Library: `pingouin 0.6.1` + `uncertainty-calibration` + `statsmodels 0.14.2`
- Code: See pseudo-code above (`run_partial_correlation_analysis`)

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** Scatter plot of RI vs ECE (controlling for PC1, mean_confidence) with partial regression line and 95% CI band; annotate ρ and p-value

#### Additional Figures (LLM Autonomous)
Based on hypothesis type (MECHANISM — RI → ECE coupling) and evaluation metrics:
1. **Partial regression residuals plot:** RI_residual (after removing PC1, mean_conf) vs ECE_residual — directly visualizes partial correlation
2. **Within-family scatter:** 3-panel subplot (LLaMA / Mistral / Qwen) showing RI vs ECE per family with within-family ρ annotation
3. **Calibration reliability diagram:** Average reliability diagram across 30 models (confidence bins vs accuracy), sorted by RI quartile
4. **Capability vs RI comparison:** Side-by-side: ρ(PC1, ECE) vs ρ(RI, ECE | PC1) to show RI adds signal
5. **Gate summary bar chart:** Target (0.40) vs actual ρ with bootstrap CI error bars

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. ρ(RI, ECE | PC1, mean_confidence) ≥ 0.4 with Holm-corrected p < 0.05
3. Consistent positive sign in ≥2 of 3 family subgroups

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Archon KB:** No domain-specific sources found. Archon KB contains diffusion model content (HuggingFace diffusers, Stable Diffusion), not LLM trust/calibration research.
- Queries executed: 3 (calibration ECE LLM, partial correlation challenges, LLM trust benchmark)
- Relevant matches: 0

### B. GitHub Implementations (Exa)

**Repository 1**: `p-lambda/verified_calibration` (⭐152, NeurIPS 2019)
- **URL:** https://github.com/p-lambda/verified_calibration
- **Query used:** "p-lambda verified_calibration ECE expected calibration error LLM Python implementation GitHub"
- **Relevance:** Official ECE library referenced in Phase 2B verification protocol. Provides debiased ECE estimator with bootstrap CIs.
- **Key code used for:** ECE computation per model (`cal.get_ece()`, `cal.get_calibration_error_uncertainties()`)
- **Configuration extracted:** `pip install uncertainty-calibration`; `cal.get_ece(model_probs, labels)` → scalar ECE

**Repository 2**: `raphaelvallat/pingouin` v0.6.1 (official docs)
- **URL:** https://pingouin-stats.org/generated/pingouin.partial_corr.html
- **Query used:** "pingouin partial_corr Spearman Holm-Bonferroni correction Python LLM benchmark correlation analysis"
- **Relevance:** Exact function for Spearman partial correlation with multiple covariates. Already installed in H-E1 environment.
- **Key code used for:** `pg.partial_corr(data=df, x="RI", y="ECE", covar=["PC1","mean_confidence"], method="spearman")` → primary gate metric; `pg.pairwise_corr(..., padjust="holm")` → family-level Holm correction
- **v0.6.1 note:** Fixed numerical instability for variables differing by orders of magnitude (relevant for ECE [0-1] vs RI [unbounded])

**Repository 3**: `prateekchhikara/llms-calibration` (⭐19, TMLR 2025, arxiv:2502.11028)
- **URL:** https://github.com/prateekchhikara/llms-calibration
- **Query used:** "TrustLLM ECE calibration scores extraction lm-evaluation-harness multiple LLMs partial correlation"
- **Relevance:** Direct precedent for multi-LLM ECE analysis. 3-stage pipeline: dataset creation → evaluation → calibration analysis. Confirms feasibility of ECE extraction across diverse open-source LLMs.
- **Used for:** Dataset/pipeline design confirmation; ECE metric computation pattern

**Repository 4**: `Exploration-Lab/LLM-Calibration-Mechanism` (arxiv:2511.00280)
- **URL:** https://github.com/Exploration-Lab/LLM-Calibration-Mechanism
- **Relevance:** Calibration layer-by-layer study on MMLU for open-weight LLMs; provides `calibration_metrics.py` for ECE/MCE from logits
- **Used for:** Confirming MMLU as appropriate QA benchmark for ECE extraction

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results was sufficiently clear. Pingouin `partial_corr()` and `uncertainty-calibration` `get_ece()` have unambiguous documented APIs requiring no semantic analysis.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — H-E1
- **File:** `h-e1/04_validation.md`
- **Reused components:**
  - Model matrix CSV (`h-e1/code/outputs/model_matrix.csv`) — 30 models, PC1, mean_confidence
  - RI scores CSV (`h-e1/code/outputs/ri_scores.csv`) — validated RI per model
  - DataAssembler (`h-e1/code/data_assembly.py`) — extend with ECE column
  - RIComputer (`h-e1/code/compute_ri.py`) — reuse directly (RI already computed)
  - Conda env `youra-h-e1` — pingouin 0.6.1, pandas, numpy, scipy, statsmodels all installed
- **Why reused:** Enables controlled experiment — only ECE column and partial correlation analysis are new; same 30-model set ensures RI values are directly comparable

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| ECE computation method | GitHub (Exa) | p-lambda/verified_calibration (Repo B.1) |
| Partial correlation function | GitHub (Exa) | pingouin v0.6.1 (Repo B.2) |
| Holm correction | GitHub (Exa) | pingouin pairwise_corr padjust="holm" (Repo B.2) |
| Multi-LLM ECE pipeline | GitHub (Exa) | prateekchhikara/llms-calibration (Repo B.3) |
| Model set (30 LLMs) | Previous hypothesis | H-E1 validated model matrix (Sec D) |
| RI scores | Previous hypothesis | H-E1 ri_scores.csv (Sec D) |
| Capability (PC1) | Previous hypothesis | H-E1 model_matrix.csv v2 leaderboard (Sec D) |
| Success thresholds (ρ≥0.4, p<0.05) | Phase 2B | 02b_verification_plan.md H-M1 spec |
| Family subgroups (LLaMA/Mistral/Qwen) | Phase 2B + H-E1 | Verification plan + H-E1 model coverage |
| Bootstrap CI (10K) | Previous hypothesis | H-E1 evaluate.py pattern (Sec D) |
| Fisher z-test split | Phase 2B | Verification protocol step 3 |
| VIF check | Previous hypothesis | H-E1 compute_ri.py (VIF=1.000 confirmed) |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-12

### Workflow History for This Hypothesis
- H-E1 COMPLETED (PASS) → H-M1 set to IN_PROGRESS (2026-05-12T12:30:28)
- H-M1 Phase 2C experiment design: IN_PROGRESS → COMPLETED (2026-05-12)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (KB — 0 domain matches), Exa (4 repositories found), Serena (skipped — statistical pipeline)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
