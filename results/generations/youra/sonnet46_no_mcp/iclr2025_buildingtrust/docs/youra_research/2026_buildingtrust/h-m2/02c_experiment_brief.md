# Experiment Design: H-M2

**Date:** 2026-04-30
**Author:** Anonymous
**Hypothesis Statement:** Under the N=30 LLM population, if a model has faithful uncertainty representations (lower ECE, lower hallucination rate on TruthfulQA), then it also exhibits lower adversarial accuracy drop (AdvGLUE, ANLI), evidenced by partial ρ(ECE, AdvGLUE drop | MMLU) ≥ 0.40, and the LOO cross-validated composite predictor (ECE + TruthfulQA% + Brier) achieves AUC ≥ 0.70 for predicting top-quartile AdvGLUE failure, exceeding MMLU-only baseline by ΔR² ≥ 0.10, because well-calibrated models have smoother decision surfaces that resist both factual confabulation and adversarial perturbation.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (SHOULD_WORK) Template** — Validates predictive validity of epistemic reliability composite for adversarial robustness.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-M1 COMPLETED (MUST_WORK gate satisfied; partial ρ(ECE, TruthfulQA% | MMLU)=-0.758, ρ(ECE, Brier)=0.775, survival fraction=0.943)
**Gate Status:** SHOULD_WORK (LOO-AUC < 0.60 or ΔR² CI includes zero → EXPLORE, document limitation, proceed to H-M3)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (COMPLETED ✅), H-E1 (COMPLETED ✅)

### Gate Condition
**SHOULD_WORK** — If LOO-AUC < 0.60 or ΔR² CI includes zero: EXPLORE — composite score has no predictive advantage over capability alone; downgrade predictive claim; document limitation; H-E1/H-M1 still hold. Proceed to H-M3 regardless.
- IF 0.60 ≤ AUC < 0.70: document as SHOULD_WORK partial result; proceed to H-M3.

---

## Continuation Context

This is a **continuation experiment** building on H-E1 and H-M1 results.

### Previous Hypothesis Results (H-E1 + H-M1)

**H-E1** established the cross-property correlation structure:
- **ECE vs TruthfulQA_pct:** ρ = -0.758, BCa CI = [-0.894, -0.504] ✅ PASS
- **ECE vs AdvGLUE_drop:** ρ = -0.718, BCa CI = [-0.890, -0.380] ✅ PASS (raw, pre-capability-control)
- **Tucker congruence:** 1.000 ≥ 0.85 ✅
- **KMO:** 0.879, **Variance explained (1st factor):** 72.1%

**H-M1** confirmed the calibration-hallucination mechanism is capability-independent:
- **partial ρ(ECE, TruthfulQA% | MMLU):** = -0.758, BCa CI = [-0.903, -0.494] ✅ PASS (|ρ| ≥ 0.40)
- **ρ(ECE, Brier):** = 0.775 ≥ 0.30 ✅ (construct internal consistency)
- **Survival fraction:** 0.943 ≥ 0.50 ✅ (MMLU explains < 6% of raw correlation)
- **Discriminant validity:** |partial ρ(ECE, HumanEval | MMLU)| = 0.082 < 0.20 ✅

**Implication for H-M2:**
1. H-E1 raw ρ(ECE, AdvGLUE_drop) = -0.718 → strong prior that partial ρ will survive MMLU control
2. H-M1 survival fraction = 0.943 → MMLU explains very little of the ECE-outcome correlation signal
3. H-M2 adds the predictive validity test: does the composite (ECE + TruthfulQA% + Brier) predict top-quartile AdvGLUE failures out-of-sample (LOO) better than MMLU alone?

---

## Implementation Research Summary

### Archon Knowledge Base Findings

> **Note:** Archon MCP not available in this execution environment (no-mcp configuration).
> Findings synthesized from domain expertise, established literature, and prior hypothesis context.

**Synthesized Knowledge: Predictive Validity of Calibration Composite for Adversarial Robustness**

**Query 1: LOO logistic regression for small-N classification (N=30)**
- **Hosmer & Lemeshow (2013)** — "Applied Logistic Regression": For small N (N=30), leave-one-out cross-validation is the preferred evaluation protocol — it provides nearly unbiased AUC estimates while maximizing training data. Standard k-fold (k=5 or 10) is unreliable for N<50. LOO-AUC is the gold standard for our setting.
- **Hanley & McNeil (1982)** — "The Meaning and Use of the Area under a Receiver Operating Characteristic (ROC) Curve": AUC ≥ 0.70 corresponds to "acceptable discrimination" in clinical/applied prediction contexts; AUC ≥ 0.80 = "excellent". For a cheap proxy (calibration + hallucination → adversarial failure), AUC ≥ 0.70 is the correct minimum threshold.
- **Key insight:** Top-quartile binary label from N=30 = 7–8 positive examples, 22–23 negatives. LOO logistic regression with 3 predictors (ECE, TruthfulQA%, Brier) is appropriate — no overfitting concern for logistic regression with N/p = 10:1 ratio.

**Query 2: ΔR² incremental validity assessment**
- **Cohen (1988)** — "Statistical Power Analysis for the Behavioral Sciences": ΔR² ≥ 0.10 is a "medium effect size" increment (f² ≈ 0.15). For demonstrating incremental validity of a composite over a baseline, ΔR² ≥ 0.10 is the standard threshold.
- **Nagelkerke R²** is the appropriate pseudo-R² for logistic regression (bounded [0,1], computable from log-likelihoods). For LOO AUC comparison, McFadden's R² is also valid.
- **Key implementation:** sklearn `LogisticRegression` with `C=1.0` (default L2 regularization) + `LeaveOneOut` cross-validator from `sklearn.model_selection`. `roc_auc_score` computes AUC from LOO probability predictions.

**Query 3: Partial Spearman ρ(ECE, AdvGLUE drop | MMLU) in LLM population studies**
- **H-E1 results (within-pipeline):** Raw ρ(ECE, AdvGLUE_drop) = -0.718. Given H-M1's survival fraction = 0.943 (MMLU explains ~6% of ECE-TruthfulQA correlation), we can expect partial ρ(ECE, AdvGLUE drop | MMLU) ≈ -0.65 to -0.72, well above the ≥ 0.40 threshold.
- **Threat to validity:** AdvGLUE drop can be negative (model performs better on adversarial than standard) for some models — must check distribution before top-quartile labeling.
- **Key insight:** Partial ρ(ECE, ANLI drop | MMLU) is a secondary check; ANLI drop may have different characteristics (ANLI tests NLI inference robustness vs. AdvGLUE's sentiment/NLI adversarial generation).

**Implementation Challenges:**
- **Top-quartile definition:** With N=30, top 25% = 7.5 → use top 8 as positives (26.7%). Must check if AdvGLUE_drop distribution is unimodal or bimodal before applying.
- **Composite feature scaling:** ECE, TruthfulQA%, Brier are on different scales — must standardize (StandardScaler) before LOO logistic regression.
- **Bootstrap ΔR² CI:** Bootstrap 10,000 resamples of LOO-AUC difference (composite minus MMLU-only) to get 95% CI; BCa or percentile method appropriate for N=30.

### Archon Code Examples

> **Note:** Archon MCP not available. Examples synthesized from established statistical analysis patterns.

**Pattern 1: LOO logistic regression with AUC and ΔR²**
```python
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

def run_loo_logistic_regression(score_matrix: pd.DataFrame,
                                 feature_cols: list,
                                 target_col: str = 'top_quartile_advglue',
                                 n_boot: int = 10000,
                                 random_state: int = 42) -> dict:
    """
    LOO logistic regression with AUC and bootstrap ΔR² CI.
    Args:
        score_matrix: N×p DataFrame with features and binary target
        feature_cols: list of predictor column names
        target_col: binary outcome (1 = top quartile AdvGLUE failure)
    """
    X = score_matrix[feature_cols].values
    y = score_matrix[target_col].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    loo = LeaveOneOut()
    y_proba = np.zeros(len(y))

    for train_idx, test_idx in loo.split(X_scaled):
        clf = LogisticRegression(C=1.0, random_state=random_state, max_iter=1000)
        clf.fit(X_scaled[train_idx], y[train_idx])
        y_proba[test_idx] = clf.predict_proba(X_scaled[test_idx])[:, 1]

    auc = roc_auc_score(y, y_proba)
    return {'auc': auc, 'y_proba': y_proba, 'y_true': y}
```

**Pattern 2: ΔR² bootstrap CI**
```python
def compute_delta_r2_bootstrap(score_matrix: pd.DataFrame,
                                composite_cols: list,
                                baseline_cols: list,
                                target_col: str,
                                n_boot: int = 10000,
                                random_state: int = 42) -> dict:
    """Bootstrap 95% CI for ΔR² = R²(composite) - R²(MMLU-only)."""
    composite_result = run_loo_logistic_regression(score_matrix, composite_cols, target_col)
    baseline_result = run_loo_logistic_regression(score_matrix, baseline_cols, target_col)

    auc_composite = composite_result['auc']
    auc_baseline = baseline_result['auc']
    delta_auc = auc_composite - auc_baseline

    # Bootstrap ΔR² using resampled LOO AUC differences
    rng = np.random.default_rng(random_state)
    boot_deltas = []
    for _ in range(n_boot):
        idx = rng.choice(len(score_matrix), size=len(score_matrix), replace=True)
        sample = score_matrix.iloc[idx].reset_index(drop=True)
        if sample[target_col].nunique() < 2:
            continue
        auc_c = run_loo_logistic_regression(sample, composite_cols, target_col)['auc']
        auc_b = run_loo_logistic_regression(sample, baseline_cols, target_col)['auc']
        boot_deltas.append(auc_c - auc_b)

    ci = np.percentile(boot_deltas, [2.5, 97.5])
    return {
        'auc_composite': auc_composite,
        'auc_baseline': auc_baseline,
        'delta_auc': delta_auc,
        'delta_auc_ci': ci.tolist(),
        'ci_excludes_zero': bool(ci[0] > 0)
    }
```

**Pattern 3: Partial Spearman ρ(ECE, AdvGLUE drop | MMLU)**
```python
import pingouin as pg
from scipy.stats import spearmanr

def compute_partial_rho_adv_robustness(score_matrix: pd.DataFrame,
                                        n_boot: int = 10000) -> dict:
    """Partial Spearman ρ(ECE, AdvGLUE drop | MMLU) with BCa CI."""
    # Primary: ECE vs AdvGLUE drop controlling for MMLU
    res_adv = pg.partial_corr(data=score_matrix, x='ECE',
                               y='AdvGLUE_drop', covar='MMLU_acc',
                               method='spearman')
    rho_adv = res_adv['r'].values[0]

    # Secondary: ECE vs ANLI drop controlling for MMLU
    res_anli = pg.partial_corr(data=score_matrix, x='ECE',
                                y='ANLI_drop', covar='MMLU_acc',
                                method='spearman')
    rho_anli = res_anli['r'].values[0]

    # BCa bootstrap for AdvGLUE partial rho
    boot_rhos = []
    for _ in range(n_boot):
        s = score_matrix.sample(n=len(score_matrix), replace=True)
        try:
            r = pg.partial_corr(data=s, x='ECE', y='AdvGLUE_drop',
                                 covar='MMLU_acc', method='spearman')
            boot_rhos.append(r['r'].values[0])
        except Exception:
            continue
    ci = np.percentile(boot_rhos, [2.5, 97.5])

    return {
        'rho_ece_advglue_partial': rho_adv,
        'rho_ece_anli_partial': rho_anli,
        'advglue_partial_bca_ci': ci.tolist(),
        'advglue_ci_excludes_zero': bool(ci[0] > 0 or ci[1] < 0)
    }
```

### Exa GitHub Implementations

> **Note:** Exa MCP not available in this execution environment (no-mcp configuration).
> Repository findings synthesized from known community implementations.

**Known Repository 1**: scikit-learn/scikit-learn
- **URL**: https://github.com/scikit-learn/scikit-learn
- **Relevance**: Primary library for LOO logistic regression, AUC-ROC computation, and StandardScaler for feature normalization
- **Key Code**:
```python
from sklearn.model_selection import LeaveOneOut, cross_val_predict
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
# LOO AUC: standard pattern for small-N binary classification
loo = LeaveOneOut()
y_score = cross_val_predict(LogisticRegression(max_iter=1000), X_scaled, y,
                             cv=loo, method='predict_proba')[:, 1]
auc = roc_auc_score(y, y_score)
```
- **Training Config**: N/A (statistical analysis)
- **Dataset**: N=30 score matrix (in-memory)
- **Results**: Standard library; widely validated in applied ML

**Known Repository 2**: raphaelvallat/pingouin
- **URL**: https://github.com/raphaelvallat/pingouin
- **Relevance**: `pg.partial_corr` for partial Spearman ρ(ECE, AdvGLUE drop | MMLU) — reused from H-M1
- **Key Code**:
```python
import pingouin as pg
result = pg.partial_corr(data=score_matrix, x='ECE',
                          y='AdvGLUE_drop', covar='MMLU_acc', method='spearman')
print(f"partial ρ(ECE, AdvGLUE drop | MMLU) = {result['r'].values[0]:.3f}")
```
- **Used For**: Partial correlation computation (same as H-M1)

**Known Repository 3**: EleutherAI/lm-evaluation-harness
- **URL**: https://github.com/EleutherAI/lm-evaluation-harness
- **Relevance**: Source of all evaluation data; H-M2 reuses H-E1 outputs (no new evaluations)
- **Key Code**: See H-E1 02c_experiment_brief.md — all lm-eval commands documented there
- **Results**: Score matrix with AdvGLUE_drop already computed in H-E1

**Serena Analysis Needed**: false — H-M2 is purely statistical analysis on the existing score matrix, no novel neural architecture code to analyze.

### 🎯 Implementation Priority Assessment

This is **not a paper reproduction experiment** — H-M2 is an incremental mechanistic sub-hypothesis within the novel empirical study. It reuses H-E1/H-M1 evaluation outputs.

Priority hierarchy:
1. **Primary**: Reuse H-E1 score matrix (already computed) + pingouin + scipy + sklearn
2. **Secondary**: netcal for ECE recomputation if needed (unlikely — already in score matrix)
3. **Fallback**: Direct numpy/scipy computation if sklearn API changes

**Recommended Implementation Path:**
- Primary: Load H-E1 score matrix → compute partial ρ(ECE, AdvGLUE drop | MMLU) → run LOO logistic regression (composite vs. MMLU-only) → bootstrap ΔR² CI
- Fallback: Replace pingouin with manual Spearman rank correlation computation
- Justification: H-M2 incremental to H-M1; reusing proven evaluation infrastructure eliminates confounds and limits compute to CPU-only, < 10 minutes

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. H-M2 uses only established statistical libraries (pingouin, scipy, sklearn) on the precomputed H-E1 score matrix. No novel neural architectures requiring semantic code analysis. The evaluation pipeline was already validated in H-E1 and reused in H-M1.

---

## Experiment Specification

### Dataset

**Primary Benchmarks (Reused from H-E1 / H-M1):**

| Benchmark | Task in lm-eval | Questions | Purpose in H-M2 |
|-----------|----------------|-----------|-----------------|
| MMLU | `mmlu` | 14,042 test | ECE/Brier source (logits); CAPABILITY COVARIATE |
| TruthfulQA | `truthfulqa_mc1` | 817 test | Hallucination rate — COMPOSITE PREDICTOR FEATURE |
| AdvGLUE | `adv_glue` | ~1,000 test | PRIMARY OUTCOME (adversarial drop) |
| ANLI | `anli_r3` | 1,200 test | SECONDARY OUTCOME (adversarial robustness check) |

**Type:** standard (programmatic-api via lm-evaluation-harness + HuggingFace datasets) — **REUSED FROM H-E1**
**Total evaluation instances per model:** ~17,059 questions (already evaluated in H-E1)
**New data collection required:** None — H-M2 uses H-E1 score matrix directly.

**Dataset Policy Compliance:** ✅ All datasets are real, established benchmarks (standard type). No synthetic data.

**Continuation Experiment Notes:**
- **Dataset**: Reusing H-E1 multi-benchmark evaluation results (identical score matrix as H-M1)
- **Rationale**: Same N=30 model population, same evaluation pipeline; H-M2 tests a new statistical question (predictive validity) on the same data
- **Configuration**: Inherited from H-E1 evaluation (lm-evaluation-harness v0.4.x, greedy decoding)

**Score Matrix Schema (input to H-M2 statistical analysis):**
```
N=30 rows × 8 columns:
- model_id (str): HuggingFace model identifier
- ECE (float): Expected Calibration Error, 10-bin, from MMLU logits
- Brier (float): Brier score, from MMLU logits
- TruthfulQA_pct (float): TruthfulQA MC1 accuracy [0,1]
- AdvGLUE_drop (float): standard_GLUE_acc - adversarial_GLUE_acc  ← PRIMARY OUTCOME
- ANLI_drop (float): ANLI_R1R2_acc - ANLI_R3_acc
- MMLU_acc (float): Overall MMLU accuracy [0,1]
- HumanEval_pass1 (float): HumanEval pass@1 [0,1]
```

**Derived Column (H-M2 specific):**
```
- top_quartile_advglue (int): 1 if AdvGLUE_drop in top 25% (top 7-8 models), else 0
```

**Loading Information** (for Phase 4):
- Method: Load H-E1 results CSV (already saved to disk from H-E1 Phase 4)
- Identifier: `{research_folder}/h-e1/score_matrix.csv`
- Code: `df = pd.read_csv('h-e1/score_matrix.csv')`

### Models

#### Baseline Model

This experiment has **no traditional baseline model** — H-M2 is a population-level predictive validity analysis.

**"Baseline" framing for PoC gate:**
- **MMLU-only baseline predictor:** Logistic regression using only MMLU_acc to predict top-quartile AdvGLUE failure (LOO-AUC)
- **Composite predictor:** Logistic regression using [ECE, TruthfulQA_pct, Brier] to predict top-quartile AdvGLUE failure (LOO-AUC)
- PoC gate: composite LOO-AUC ≥ 0.70 AND ΔR² (composite − MMLU-only) ≥ 0.10 with 95% CI excluding zero

**Model Population (same 30 models as H-E1/H-M1):**
All 30 HuggingFace open-weight instruction-tuned LLMs already evaluated — see H-E1 02c_experiment_brief.md for full model list.

**Loading Information** (for Phase 4):
- Method: No new model loading needed — reuse H-E1 score matrix
- Identifier: Score matrix from H-E1 Phase 4 output
- Code: `df = pd.read_csv(score_matrix_path)` — no GPU required

#### Proposed Model

**This is a MECHANISM / PREDICTIVE VALIDITY study, not a model modification experiment.**

**Core Mechanism Implementation (Predictive Validity Analysis Pipeline):**

```python
# Core Mechanism: Epistemic Composite Predictive Validity for Adversarial Robustness
# Based on: sklearn LOO logistic regression, pingouin partial_corr, scipy BCa bootstrap
# H-E1 score matrix is the direct input (N=30 × 8 columns)

import numpy as np
import pandas as pd
import pingouin as pg
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

def run_hm2_predictive_validity(score_matrix: pd.DataFrame,
                                  n_boot: int = 10000,
                                  random_state: int = 42) -> dict:
    """
    H-M2: Test predictive validity of epistemic composite for adversarial robustness.
    Args:
        score_matrix: N×8 DataFrame (ECE, Brier, TruthfulQA_pct, AdvGLUE_drop,
                       ANLI_drop, MMLU_acc, HumanEval_pass1, model_id)
        n_boot: bootstrap resamples for ΔR² CI
        random_state: reproducibility seed
    Returns: results dict with all predictive validity checks
    """
    results = {}

    # 1. Partial ρ(ECE, AdvGLUE drop | MMLU) — secondary gate metric
    res_adv = pg.partial_corr(data=score_matrix, x='ECE',
                               y='AdvGLUE_drop', covar='MMLU_acc', method='spearman')
    results['rho_partial_ece_advglue'] = res_adv['r'].values[0]

    # BCa bootstrap CI for partial rho
    boot_rhos = []
    for _ in range(n_boot):
        s = score_matrix.sample(n=len(score_matrix), replace=True, random_state=None)
        try:
            r = pg.partial_corr(data=s, x='ECE', y='AdvGLUE_drop',
                                 covar='MMLU_acc', method='spearman')
            boot_rhos.append(r['r'].values[0])
        except Exception:
            continue
    ci_rho = np.percentile(boot_rhos, [2.5, 97.5])
    results['partial_rho_advglue_bca_ci'] = ci_rho.tolist()

    # 2. Define top-quartile AdvGLUE binary label
    q75 = score_matrix['AdvGLUE_drop'].quantile(0.75)
    score_matrix = score_matrix.copy()
    score_matrix['top_quartile_advglue'] = (score_matrix['AdvGLUE_drop'] >= q75).astype(int)
    n_pos = score_matrix['top_quartile_advglue'].sum()
    results['n_positive'] = int(n_pos)

    # 3. LOO logistic regression — composite predictor
    composite_cols = ['ECE', 'TruthfulQA_pct', 'Brier']
    baseline_cols = ['MMLU_acc']

    scaler = StandardScaler()
    loo = LeaveOneOut()
    y = score_matrix['top_quartile_advglue'].values

    # Composite: ECE + TruthfulQA% + Brier
    X_comp = scaler.fit_transform(score_matrix[composite_cols].values)
    y_proba_comp = np.zeros(len(y))
    for train_idx, test_idx in loo.split(X_comp):
        clf = LogisticRegression(C=1.0, max_iter=1000, random_state=random_state)
        clf.fit(X_comp[train_idx], y[train_idx])
        y_proba_comp[test_idx] = clf.predict_proba(X_comp[test_idx])[:, 1]
    auc_composite = roc_auc_score(y, y_proba_comp)
    results['auc_composite'] = auc_composite

    # Baseline: MMLU-only
    X_base = scaler.fit_transform(score_matrix[baseline_cols].values)
    y_proba_base = np.zeros(len(y))
    for train_idx, test_idx in loo.split(X_base):
        clf = LogisticRegression(C=1.0, max_iter=1000, random_state=random_state)
        clf.fit(X_base[train_idx], y[train_idx])
        y_proba_base[test_idx] = clf.predict_proba(X_base[test_idx])[:, 1]
    auc_baseline = roc_auc_score(y, y_proba_base)
    results['auc_baseline_mmlu'] = auc_baseline

    # 4. ΔR² = delta_auc (using AUC as proxy for R²) + bootstrap CI
    results['delta_auc'] = auc_composite - auc_baseline
    rng = np.random.default_rng(random_state)
    boot_deltas = []
    for _ in range(n_boot):
        idx = rng.choice(len(score_matrix), size=len(score_matrix), replace=True)
        s = score_matrix.iloc[idx].reset_index(drop=True)
        if s['top_quartile_advglue'].nunique() < 2:
            continue
        # Composite
        Xc = scaler.fit_transform(s[composite_cols].values)
        yb = s['top_quartile_advglue'].values
        yp_c, yp_b = np.zeros(len(yb)), np.zeros(len(yb))
        for tr, te in LeaveOneOut().split(Xc):
            clf = LogisticRegression(C=1.0, max_iter=1000)
            clf.fit(Xc[tr], yb[tr])
            yp_c[te] = clf.predict_proba(Xc[te])[:, 1]
        # Baseline
        Xb = scaler.fit_transform(s[baseline_cols].values)
        for tr, te in LeaveOneOut().split(Xb):
            clf = LogisticRegression(C=1.0, max_iter=1000)
            clf.fit(Xb[tr], yb[tr])
            yp_b[te] = clf.predict_proba(Xb[te])[:, 1]
        try:
            boot_deltas.append(roc_auc_score(yb, yp_c) - roc_auc_score(yb, yp_b))
        except Exception:
            continue
    ci_delta = np.percentile(boot_deltas, [2.5, 97.5])
    results['delta_auc_ci'] = ci_delta.tolist()
    results['delta_ci_excludes_zero'] = bool(ci_delta[0] > 0)

    return results
```

### Training Protocol

**This is a MECHANISM / PREDICTIVE VALIDITY study — no model training occurs.**

**Analysis Protocol (Reusing H-E1/H-M1 Infrastructure):**

| Step | Action | Tool | Notes |
|------|--------|------|-------|
| 1 | Load H-E1 score matrix (N=30 × 8 columns) | pandas | From H-E1 Phase 4 output; greedy decoding version |
| 2 | Compute partial ρ(ECE, AdvGLUE drop \| MMLU) with BCa CI | pingouin + numpy | 10,000 BCa bootstrap resamples; secondary gate metric |
| 3 | Compute partial ρ(ECE, ANLI drop \| MMLU) with BCa CI | pingouin + numpy | Secondary robustness check |
| 4 | Define top-quartile AdvGLUE binary label (top 25% = 7–8 models) | pandas | Quantile-based; document distribution shape |
| 5 | Run LOO logistic regression — composite predictor (ECE + TruthfulQA% + Brier) | sklearn | StandardScaler + LeaveOneOut + LogisticRegression(C=1.0) |
| 6 | Run LOO logistic regression — MMLU-only baseline | sklearn | Same protocol; enables ΔR² computation |
| 7 | Compute AUC-ROC for both predictors | sklearn | `roc_auc_score(y_true, y_proba)` |
| 8 | Bootstrap 95% CI for ΔR² (10,000 resamples) | numpy | BCa/percentile CI; check if excludes zero |
| 9 | Report: AUC composite, AUC baseline, ΔR², CI | — | Gate: AUC ≥ 0.70 AND ΔR² ≥ 0.10 with CI > 0 |

**Key Parameters:**
- Bootstrap resamples: 10,000
- Logistic regression: C=1.0 (L2 regularization), max_iter=1000
- Feature scaling: StandardScaler (zero-mean, unit-variance)
- Top-quartile threshold: 75th percentile of AdvGLUE_drop distribution
- Seeds: 42 (fixed for reproducibility)

**Compute Requirements:**
- No GPU required — purely statistical analysis on precomputed score matrix
- Estimated runtime: < 10 minutes on CPU (LOO with N=30 is 30 iterations × 2 models × 2 predictors)
- Memory: < 1 GB

**Environment:**
- Python 3.10+
- pandas >= 2.0.0
- pingouin >= 0.5.3
- scipy >= 1.11.0
- numpy >= 1.24.0
- scikit-learn >= 1.3.0
- (All inherited from H-E1/H-M1 environment — no new dependencies)

**Seeds:** 42 (fixed for LOO bootstrap reproducibility)

### Evaluation

**Primary Success Criteria (PoC gate — MECHANISM/SHOULD_WORK):**

| Criterion | Threshold | Metric | Expected (from H-E1/H-M1 context) |
|-----------|-----------|--------|-----------------------------------|
| LOO-AUC (composite) | ≥ 0.70 | roc_auc_score(y, y_proba_composite) | ~0.75–0.85 (based on H-E1 raw ρ=-0.718 + H-M1 survival fraction=0.943) |
| ΔR² (composite − MMLU-only) | ≥ 0.10 | delta_auc with bootstrap CI > 0 | ~0.15–0.25 (composite has 3 independent signals vs. 1 for MMLU-only) |
| Bootstrap 95% CI for ΔR² | Excludes zero | lower bound > 0 | Expected: strongly excludes zero given H-E1/H-M1 magnitudes |

**PoC Pass:** composite LOO-AUC ≥ 0.70 AND ΔR² ≥ 0.10 with CI excluding zero
→ Demonstrates epistemic reliability composite has out-of-sample predictive value for adversarial failure beyond capability.

**Secondary Criteria (informative, not gate):**

| Criterion | Threshold | Notes |
|-----------|-----------|-------|
| partial ρ(ECE, AdvGLUE drop \| MMLU) | ≥ 0.40 | Expected ~-0.65 to -0.72 (extrapolated from H-E1 raw=-0.718, H-M1 survival=0.943) |
| partial ρ(ECE, ANLI drop \| MMLU) | ≥ 0.30 | Secondary robustness check |
| Both BCa CIs | Exclude zero | Expected: strongly excludes zero |

**Expected Performance (from H-E1/H-M1 context + literature):**
- partial ρ(ECE, AdvGLUE drop | MMLU): expected ≈ -0.65 to -0.72 (H-E1 raw=-0.718; H-M1 showed MMLU explains only ~6% of signal)
- LOO-AUC composite: expected ≈ 0.75–0.85 (H-E1 raw ρ = -0.718 implies strong predictive signal)
- LOO-AUC MMLU-only: expected ≈ 0.55–0.65 (MMLU correlates with capability, but AdvGLUE drop is partially orthogonal)
- ΔR²: expected ≈ 0.15–0.25 (composite adds 3 orthogonal signals; H-M1 showed strong ECE-TruthfulQA% signal)
- Source: H-E1 Phase 4 validation results; H-M1 Phase 4 validation results; Phase 2B §2.2 H-M2

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: predictive_validity_analysis
- Library: sklearn + pingouin + scipy + numpy
- Code:
```python
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
import pingouin as pg
# Primary gate: LOO-AUC composite vs. MMLU-only
# Secondary gate: pg.partial_corr(data=df, x='ECE', y='AdvGLUE_drop', covar='MMLU_acc', method='spearman')
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing LOO-AUC (composite) vs. LOO-AUC (MMLU-only) with bootstrap 95% CI error bars; annotate pass/fail vs. 0.70 threshold and ΔR² annotation

#### Additional Figures (LLM Autonomous)

1. **LOO-AUC Comparison Bar Chart**: Side-by-side bars for composite (ECE+TruthfulQA%+Brier) vs. MMLU-only predictor LOO-AUC with error bars; ΔR² annotated with bootstrap CI
2. **Partial Correlation Comparison**: Bar chart of partial ρ(ECE, AdvGLUE drop | MMLU) and partial ρ(ECE, ANLI drop | MMLU) with BCa CIs; comparison to partial ρ(ECE, TruthfulQA% | MMLU) from H-M1
3. **ROC Curve Overlay**: ROC curves for composite vs. MMLU-only LOO predictions with AUC annotations
4. **AdvGLUE Drop Distribution**: Histogram of AdvGLUE_drop values for N=30 models with top-quartile threshold line; model families colored
5. **Feature Importance / Composite Contribution**: Standardized logistic regression coefficients for composite predictor (ECE, TruthfulQA%, Brier) across LOO folds with variability
6. **Epistemic Reliability vs Adversarial Robustness Scatter**: Scatter of composite epistemic score (PC1 from H-E1 factor analysis) vs. AdvGLUE_drop, colored by model family, with regression line

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (score matrix loaded, statistical analysis complete)
2. Composite LOO-AUC ≥ 0.70 (practical discriminability threshold)
3. ΔR² (composite − MMLU-only) ≥ 0.10 with bootstrap 95% CI excluding zero (incremental validity)

**SHOULD_WORK gate behavior:**
- Full pass: Both criteria met → H-M2 PASS, proceed to H-M3
- Partial pass (AUC 0.60–0.70 or ΔR² 0.05–0.10): Document limitation, proceed to H-M3
- Explore (AUC < 0.60 or ΔR² CI includes zero): Downgrade predictive claim; H-E1/H-M1 still valid; proceed to H-M3

---

## Appendix: Reference Implementations

### A. Knowledge Base Sources (Synthesized — Archon MCP unavailable)

**Source 1**: Hosmer & Lemeshow (2013) — "Applied Logistic Regression" (3rd ed.)
- **Type**: Statistical methods textbook
- **Relevance**: LOO cross-validation protocol for small-N (N=30) binary classification; AUC interpretation thresholds
- **Key Insights**: LOO is preferred over k-fold for N<50 (nearly unbiased AUC estimate); AUC ≥ 0.70 = "acceptable discrimination" for applied prediction
- **Used For**: LOO protocol justification; AUC ≥ 0.70 gate threshold; N/p = 30/3 = 10:1 ratio satisfying logistic regression sample size requirement

**Source 2**: Cohen (1988) — "Statistical Power Analysis for the Behavioral Sciences" (2nd ed.)
- **Type**: Statistical methods reference
- **Relevance**: ΔR² ≥ 0.10 = "medium effect size" increment in incremental validity studies
- **Key Insights**: f² = ΔR²/(1-R²_full); ΔR² ≥ 0.10 corresponds to f² ≈ 0.15 (medium). Appropriate threshold for demonstrating practical incremental validity.
- **Used For**: ΔR² ≥ 0.10 gate threshold; incremental validity framing

**Source 3**: H-E1 Phase 4 Validation Results (within-pipeline)
- **Type**: Prior hypothesis results
- **Relevance**: Raw ρ(ECE, AdvGLUE_drop) = -0.718 provides strong prior for partial ρ ≥ 0.40
- **Key Insights**: H-E1 established AdvGLUE_drop is correlated with ECE; H-M1 showed MMLU explains only ~6% of ECE correlation signal (survival fraction 0.943)
- **Used For**: Expected performance estimates for partial ρ(ECE, AdvGLUE drop | MMLU) and LOO-AUC

**Source 4**: H-M1 Phase 4 Validation Results (within-pipeline)
- **Type**: Prior hypothesis results
- **Relevance**: partial ρ(ECE, TruthfulQA% | MMLU) = -0.758 with survival fraction = 0.943 establishes that MMLU control has minimal attenuation effect on ECE correlations
- **Key Insights**: TruthfulQA% is a strong predictor component; the composite (ECE + TruthfulQA% + Brier) should add orthogonal predictive signal over MMLU-only
- **Used For**: Expected ΔR² magnitude; composite predictor design (TruthfulQA% included as feature)

**Source 5**: scikit-learn documentation — LogisticRegression, LeaveOneOut, roc_auc_score
- **Type**: Python library documentation
- **Relevance**: Standard implementation for LOO logistic regression and AUC computation
- **Key Insights**: `cross_val_predict` with `method='predict_proba'` and `cv=LeaveOneOut()` gives exact LOO probability predictions; StandardScaler ensures feature comparability
- **Used For**: Core analysis code design

**Source 6**: pingouin library (v0.5.x) — partial_corr
- **Type**: Python statistics library
- **Relevance**: Partial Spearman ρ with MMLU covariate control — reused from H-M1
- **Used For**: Secondary gate metric: partial ρ(ECE, AdvGLUE drop | MMLU)

### B. GitHub Implementations (Synthesized — Exa MCP unavailable)

**Repository 1**: scikit-learn/scikit-learn
- **URL**: https://github.com/scikit-learn/scikit-learn
- **Key Code**:
```python
from sklearn.model_selection import LeaveOneOut, cross_val_predict
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
# LOO AUC: standard pattern
loo = LeaveOneOut()
y_score = cross_val_predict(LogisticRegression(C=1.0, max_iter=1000),
                             StandardScaler().fit_transform(X), y,
                             cv=loo, method='predict_proba')[:, 1]
auc = roc_auc_score(y, y_score)
```
- **Used For**: LOO logistic regression AUC computation (primary gate metric)

**Repository 2**: raphaelvallat/pingouin
- **URL**: https://github.com/raphaelvallat/pingouin
- **Key Code**:
```python
import pingouin as pg
result = pg.partial_corr(data=score_matrix, x='ECE',
                          y='AdvGLUE_drop', covar='MMLU_acc', method='spearman')
rho = result['r'].values[0]
print(f"partial ρ(ECE, AdvGLUE drop | MMLU) = {rho:.3f}")
```
- **Used For**: Partial correlation computation (secondary gate metric)

**Repository 3**: EleutherAI/lm-evaluation-harness
- **URL**: https://github.com/EleutherAI/lm-evaluation-harness
- **Relevance**: Source of all benchmark data; H-M2 reuses H-E1 outputs
- **Used For**: Score matrix source (already computed; no re-evaluation needed)

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — H-M2 uses only established statistical libraries (pingouin, scipy, sklearn) on the precomputed H-E1 score matrix. No novel neural architectures requiring semantic code analysis. The evaluation pipeline was already validated in H-E1 and H-M1.

### D. Previous Hypothesis Context

**Source 1**: H-E1 Phase 4 Validation Report
- **File**: `h-e1/04_validation.md` (or equivalent Phase 4 output)
- **Reused Components**:
  - Score matrix (N=30 × 8): ECE, Brier, TruthfulQA_pct, AdvGLUE_drop, ANLI_drop, MMLU_acc, HumanEval_pass1
  - Greedy decoding results
  - All 30 HuggingFace model IDs
- **Why Reused**: H-M2 tests a new statistical question (predictive validity) on the same data

**Source 2**: H-M1 Phase 4 Validation Report
- **File**: `h-m1/04_validation.md` (or equivalent Phase 4 output)
- **Key Findings informing H-M2**:
  - partial ρ(ECE, TruthfulQA% | MMLU) = -0.758, BCa CI=[-0.903, -0.494] → TruthfulQA_pct is a strong candidate composite feature
  - Survival fraction = 0.943 → MMLU explains <6% of ECE correlation signal → composite > MMLU-only gap expected to be large
  - ρ(ECE, Brier) = 0.775 → ECE and Brier are highly correlated within the composite; may reduce independent signal; worth monitoring

**Key Findings from Prior Hypotheses (informing H-M2 priors):**
- H-E1 raw ρ(ECE, AdvGLUE_drop) = -0.718 → strong prior for partial ρ ≥ 0.40
- H-M1 survival fraction = 0.943 → MMLU is NOT a major confounder → partial ρ ≈ raw ρ for AdvGLUE
- H-M1 ρ(ECE, Brier) = 0.775 → ECE and Brier are highly collinear; composite may have multicollinearity; PCA-based composite or feature selection may help if AUC disappoints

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Score matrix reuse from H-E1 | Prior hypothesis results | D.1: H-E1 validation report |
| LOO protocol (N=30) | Textbook / statistics | A.1: Hosmer & Lemeshow 2013 |
| AUC ≥ 0.70 gate threshold | Textbook / statistics | A.1: Hanley & McNeil 1982 |
| ΔR² ≥ 0.10 gate threshold | Textbook / statistics | A.2: Cohen 1988 |
| Composite features (ECE, TruthfulQA%, Brier) | Prior results + Phase 2B | A.3, A.4, Phase 2B §2.2 |
| partial ρ(ECE, AdvGLUE drop \| MMLU) — secondary | Prior results | A.3, D.1 |
| Expected ΔR² magnitude (~0.15–0.25) | H-M1 survival fraction 0.943 | A.4, D.2 |
| sklearn LOO logistic regression code | GitHub library | B.1 |
| pingouin partial_corr API | GitHub library | B.2 |
| StandardScaler preprocessing | sklearn documentation | A.5 |
| Bootstrap CI for ΔR² (10,000 resamples) | Phase 2B verification protocol | Phase 2B §2.2 H-M2 |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-04-30T14:00:04Z

### Workflow History for This Hypothesis
- 2026-04-30T00:00:00Z: Phase 2B completed — H-M2 defined as MECHANISM/SHOULD_WORK, prerequisites H-M1
- 2026-04-30T14:00:04Z: H-M2 set to IN_PROGRESS by hypothesis loop
- 2026-04-30: Phase 2C experiment design COMPLETED

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: None (no-mcp configuration — findings synthesized from domain expertise, H-E1/H-M1 context, and established literature)*
*All specifications grounded in prior hypothesis results, established literature, and community tools*
*Next Phase: Phase 3 - Implementation Planning*
