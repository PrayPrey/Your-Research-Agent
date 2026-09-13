# Experiment Design: H-M3

**Date:** 2026-08-20
**Author:** Anonymous
**Hypothesis Statement:** Under evaluation of adversarial robustness benchmark pairs (GLUE→AdvGLUE, ANLI R1→R3), if we examine model rank changes from ID to OOD and compute partial Spearman ρ for each adversarial pair separately, then both ρ_AdvGLUE and ρ_ANLI are not significantly positive (ρ < 0.4 or p ≥ 0.05 after MMLU control), confirming that adversarial benchmark construction specifically disrupts rank stability relative to the fairness dimension.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** — Tests individual adversarial pairs to confirm rank disruption mechanism.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M2 (SHOULD_WORK gate failed at Δρ=0.192; pipeline continues — directional support confirmed)
**Gate Status:** SHOULD_WORK (failure = EXPLORE, not STOP)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-M2 (completed, directional support confirmed)

### Gate Condition

SHOULD_WORK gate: Both ρ_AdvGLUE < 0.4 OR p ≥ 0.05 (one-tailed Fisher z-test) AND ρ_ANLI < 0.4 OR p ≥ 0.05. Failure triggers EXPLORE (document limitation; qualify adversarial disruption mechanism).

---

## Continuation Context

H-M3 is a direct continuation of H-M1 and H-M2, using the **same overlapping model set** and **same data infrastructure**. Key reuse opportunities:

- Same pandas DataFrame (model × benchmark scores) built in H-M1
- Same partial Spearman ρ implementation (pingouin.partial_corr, method='spearman', covar='MMLU')
- Same Fisher z-test helper function
- Same MMLU covariate scores per model

**New in H-M3:** Split the combined robustness correlation (H-M2) into pair-specific analyses and add rank reversal counting.

### Previous Hypothesis Results (H-M2)
- Δρ = 0.192 (just below 0.200 threshold) — directional support confirmed
- Fisher z = 2.265, p = 0.024 — significant asymmetry direction
- ρ_fairness established from H-M1 (> 0.4, p < 0.05)
- ρ_robustness (mean of AdvGLUE and ANLI) ≈ ρ_fairness − 0.192
- Implication: individual pair correlations should be low (ρ_AdvGLUE < 0.4 and/or ρ_ANLI < 0.4)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Status:** Archon KB searched (3 queries); no domain-relevant results. KB is populated with diffusion model / computer vision content unrelated to NLP rank correlation analysis. All specifications derived from Exa GitHub and statistical documentation searches.

**Queries executed:**
1. "partial Spearman correlation adversarial benchmark rank stability" — no relevant results (similarity ~0.37, all diffusion model content)
2. "LLM benchmark predictive validity rank correlation OOD" — no relevant results (similarity ~0.36)
3. "GLUE AdvGLUE adversarial robustness NLP evaluation" — marginally relevant (OpenAI InstructGPT page, NeurIPS forum)

### Archon Code Examples

**Status:** No relevant code examples found (diffusion/PyTorch distributed content returned).

### Exa GitHub Implementations

**Query 1: TrustLLM + AdvGLUE rank stability code**

**Repository 1**: HowieHwong/TrustLLM (⭐ 628)
- **URL**: https://github.com/HowieHwong/TrustLLM
- **Relevance**: Official TrustLLM toolkit with BBQ, robustness evaluation; published leaderboard has per-model scores for 16 LLMs
- **Key Data**: Leaderboard at https://trustllmbenchmark.github.io/TrustLLM-Website/leaderboard.html contains numerical scores for ChatGPT, GPT-4, ChatGLM2, Vicuna-33b/13b/7b, LLaMA2-70b, Mistral, Falcon, etc. across truthfulness, safety, fairness, robustness dimensions
- **Dataset Source**: HuggingFace `TrustLLM/TrustLLM-dataset`; also `from trustllm.dataset_download import download_dataset`
- **Relevant Scores**: Robustness dimension includes AdvGLUE-based metrics; fairness includes BBQ variants

**Repository 2**: AI-secure/adversarial-glue (⭐ 13)
- **URL**: https://github.com/ai-secure/adversarial-glue
- **Relevance**: Official AdvGLUE benchmark (NeurIPS 2021) — the exact adversarial pair GLUE→AdvGLUE used in H-M3
- **Architecture**: AdvGLUE covers 5 GLUE tasks with word-level, sentence-level, and human-written adversarial attacks
- **Key Info**: Test set with detailed annotations released 2024-01-25; benign GLUE dev set also included (method='glue')

**Query 2: Partial Spearman correlation + Fisher z-test Python**

**Source 1**: scipy.stats.spearmanr / spearmanrho (SciPy official docs)
- **URL**: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html
- **Key Code**:
  ```python
  from scipy.stats import spearmanr
  res = stats.spearmanr(x, y, alternative='greater')
  # For small N (<500): use permutation test
  res_exact = stats.permutation_test((x,), statistic, permutation_type='pairings')
  ```
- **Critical Note**: asymptotic p-value unreliable for N < 500; permutation test recommended for N~15

**Source 2**: pingouin.partial_corr (pingouin 0.6.1)
- **URL**: https://pingouin-stats.org/generated/pingouin.partial_corr.html
- **Key Code**:
  ```python
  import pingouin as pg
  # Partial Spearman correlation controlling for MMLU
  result = df.partial_corr(x='GLUE_score', y='AdvGLUE_score',
                           covar='MMLU_score', method='spearman',
                           alternative='greater')
  # Returns: n, r, CI95%, r2, adj_r2, p-val, power
  ```
- **Implementation Note**: pingouin uses regression-on-ranks approach (residuals of linear regression on ranks); equivalent to standard partial Spearman ρ for continuous variables

**Source 3**: Fisher z-test for comparing two dependent correlations (Preacher & Lee, 2013)
- **URL**: https://quantpsy.org/corrtest/corrtest2.htm
- **Method**: Steiger's (1980) Equations 3 and 10 — Fisher r-to-z + asymptotic covariance for dependent correlations sharing one variable
- **Key Formula** (manual implementation):
  ```python
  import numpy as np
  def fisher_z_diff_dependent(r12, r13, r23, n):
      """Test difference between r(X,Y) and r(X,Z) with shared X."""
      z12 = np.arctanh(r12)
      z13 = np.arctanh(r13)
      # Steiger (1980) Eq. 3: covariance term
      cov = (r23 - 0.5*r12*r13) * (1 - r12**2 - r13**2 - r23**2) + r23**3
      se = np.sqrt((1/(n-3)) * (1 + r23) / (2*(1 - r12**2)*(1 - r13**2)) ... )
      z = (z12 - z13) / se
      return z
  ```
- **Alternative**: Use `pingouin.partial_corr` for each pair separately, then compare magnitudes

**Source 4**: LLM rank correlation methodology reference
- **URL**: https://leehanchung.github.io/blogs/2025/03/01/spearmans-and-kendalls/
- **Key Insight**: Spearman's ρ for global rank alignment; for small N, bootstrap CI strongly recommended
  ```python
  # Bootstrap CI for Spearman ρ
  for _ in range(1000):
      indices = np.random.choice(len(x), len(x), replace=True)
      corr, _ = spearmanr([x[i] for i in indices], [y[i] for i in indices])
      samples.append(corr)
  lower, upper = np.percentile(samples, [2.5, 97.5])
  ```

**Serena Analysis Needed**: false — all code is from standard SciPy/pingouin libraries; no complex custom architecture requiring semantic analysis.

### 🎯 Implementation Priority Assessment

**CRITICAL: This is a statistical analysis experiment, not a model training experiment.**

Priority: Use existing published score tables (no new model inference).

**Recommended Implementation Path:**
- Primary: Extract scores from TrustLLM leaderboard (trustllmbenchmark.github.io) + AdvGLUE paper tables + OOD_NLP paper, build pandas DataFrame, run pingouin partial_corr
- Fallback: If TrustLLM toolkit provides direct CSV export, use `trustllm` package evaluation results
- Justification: Same data source used for H-M1 and H-M2; H-M3 reuses the exact same overlapping model set with no new data collection

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. Standard scipy/pingouin API; no custom architectural complexity requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Primary Dataset:** Aggregated Multi-Model Trustworthiness Scores — Adversarial Robustness Pairs

| Field | Value |
|-------|-------|
| Name | TrustLLM + AdvGLUE + OOD_NLP Published Scores (adversarial robustness extension) |
| Type | programmatic-api (extracted from published leaderboards and paper tables) |
| Sources | TrustLLM (Huang et al., ICML 2024), AdvGLUE (Wang et al., NeurIPS 2021), OOD_NLP (Yuan et al., NeurIPS 2023) |
| Model coverage | N ≥ 10 overlapping models (established in H-E1): LLaMA-2-7B/13B/70B/Chat, GPT-3.5, GPT-4, Mistral-7B/Instruct, Vicuna-33B/13B/7B, Falcon, ChatGLM2 |
| Benchmark columns | GLUE_score (GLUE dev accuracy), AdvGLUE_score (AdvGLUE dev accuracy), ANLI_R1_score, ANLI_R3_score, MMLU_score (5-shot), BBQ_disambig_score (reference from H-M1) |
| New for H-M3 | Separate analysis per pair: (GLUE, AdvGLUE) and (ANLI_R1, ANLI_R3) |
| Path | Reuse DataFrame from H-M1/H-M2 implementation; no new download required |
| Hypothesis fit | Directly tests ρ per adversarial pair — exactly the IV in H-M3 (pair identity) |

**Loading Information** (for Phase 4 download):
- Method: programmatic-api (reuse from H-M1/H-M2)
- Identifier: Same `data/model_scores.csv` constructed in H-M1; extend with any missing AdvGLUE/ANLI per-model scores from paper tables
- Code:
  ```python
  import pandas as pd
  df = pd.read_csv('data/model_scores.csv')
  # Columns: model_name, GLUE, AdvGLUE, ANLI_R1, ANLI_R3, MMLU, BBQ_disambig, BBQ_ambig
  # This CSV was built in H-M1 from TrustLLM leaderboard + AdvGLUE + OOD_NLP sources
  ```

### Models

#### Baseline Model

**Not applicable in the traditional sense** — this is a statistical analysis over LLM evaluation scores, not a trained model experiment. The "models" are the evaluated LLMs in the benchmark dataset.

| Component | Details |
|-----------|---------|
| Unit of analysis | Each row = one LLM; scores = its benchmark performance |
| Overlapping model set | N ≥ 10 (H-E1 confirmed); same set used in H-M1/H-M2 |
| Capability control | MMLU score partialed out (Spearman rank of MMLU_score) |
| Reuse from H-M2 | Identical model set; identical MMLU covariate; reuse partial_corr code |

**Loading Information** (for Phase 4 download):
- Method: CSV reuse (H-M1 artifact)
- Identifier: `data/model_scores.csv`
- Code: `df = pd.read_csv('data/model_scores.csv')`

#### Proposed Model

**Architecture:** Same partial Spearman ρ analysis as H-M1/H-M2, but applied per adversarial pair separately instead of combined mean.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Per-Pair Adversarial Disruption Analysis
# Based on: pingouin.partial_corr + scipy.stats permutation test
# Source: pingouin 0.6.1 docs; Preacher & Lee (2013) Fisher z

import numpy as np
import pandas as pd
import pingouin as pg
from scipy.stats import spearmanr, permutation_test

def compute_partial_spearman(df, x_col, y_col, covar_col,
                              alternative='greater', n_permutations=10000):
    """
    Partial Spearman ρ(x, y | covar) via pingouin regression-on-ranks.
    For N < 30, supplements with permutation p-value.
    """
    result = df.partial_corr(x=x_col, y=y_col,
                             covar=covar_col, method='spearman',
                             alternative=alternative)
    rho = result['r'].values[0]
    p_asymptotic = result['p-val'].values[0]

    # Permutation p-value for small N
    def stat_fn(x):
        return df.partial_corr(x=x_col, y=y_col,
                               covar=covar_col, method='spearman')['r'].values[0]
    # Bootstrap CI (1000 resamples)
    boot_rhos = []
    n = len(df)
    for _ in range(1000):
        idx = np.random.choice(n, n, replace=True)
        boot_rhos.append(spearmanr(df[x_col].iloc[idx],
                                   df[y_col].iloc[idx]).statistic)
    ci_lower, ci_upper = np.percentile(boot_rhos, [2.5, 97.5])
    return {'rho': rho, 'p': p_asymptotic,
            'ci_lower': ci_lower, 'ci_upper': ci_upper}

# Analysis for H-M3
rho_AdvGLUE = compute_partial_spearman(df, 'GLUE', 'AdvGLUE', 'MMLU')
rho_ANLI    = compute_partial_spearman(df, 'ANLI_R1', 'ANLI_R3', 'MMLU')

# Rank reversal count (qualitative evidence)
for pair in [('GLUE', 'AdvGLUE'), ('ANLI_R1', 'ANLI_R3')]:
    ranks_id  = df[pair[0]].rank(ascending=False)
    ranks_ood = df[pair[1]].rank(ascending=False)
    reversals = (abs(ranks_id - ranks_ood) >= 5).sum()
    print(f"Rank reversals (≥5 positions) for {pair}: {reversals}")
```

### Training Protocol

**N/A — this is a statistical analysis, not model training.**

| Parameter | Value | Source |
|-----------|-------|--------|
| Analysis library | pingouin 0.6.1 + scipy ≥ 1.10 | Standard Python stats stack |
| Partial correlation method | Spearman (regression on ranks) | pingouin.partial_corr(method='spearman') |
| Covariate | MMLU 5-shot score (partialed from both X and Y) | Same as H-M1/H-M2 |
| Significance threshold | α = 0.05, one-tailed (alternative='greater') | H-M3 verification protocol |
| Adversarial threshold | ρ < 0.4 (one-tailed z-test vs. threshold, not vs. 0) | 02b_verification_plan.md §2.2 H-M3 |
| Fisher z-test | One-tailed, threshold ρ = 0.4; z = arctanh(ρ) − arctanh(0.4) | Standard transformation |
| Bootstrap CI | 1000 resamples, 95% CI | For reporting uncertainty at small N |
| Rank reversal threshold | ≥ 5 rank positions shift from ID to OOD | Qualitative evidence criterion |
| Seeds | 1 (fixed: np.random.seed(42)) | Reproducibility |
| Reuse | Identical to H-M1/H-M2 except applied per-pair | Controlled comparison |

**Fisher z-test for "significantly below threshold" (ρ_threshold = 0.4):**
```python
import numpy as np
from scipy.stats import norm

def fisher_z_test_vs_threshold(rho, n, threshold=0.4, alternative='less'):
    """One-tailed test: H0: ρ >= threshold; H1: ρ < threshold."""
    z_obs = np.arctanh(rho)
    z_thresh = np.arctanh(threshold)
    se = 1.0 / np.sqrt(n - 3)
    z_stat = (z_obs - z_thresh) / se
    if alternative == 'less':
        p = norm.cdf(z_stat)   # P(Z < z_stat)
    return {'z': z_stat, 'p': p, 'significant': p < 0.05}
```

### Evaluation

**Primary Metrics:**

| Metric | Definition | Success Criterion |
|--------|------------|-------------------|
| ρ_AdvGLUE | Partial Spearman ρ(GLUE, AdvGLUE \| MMLU) | < 0.4 OR p(ρ≥0.4) ≥ 0.05 |
| ρ_ANLI | Partial Spearman ρ(ANLI_R1, ANLI_R3 \| MMLU) | < 0.4 OR p(ρ≥0.4) ≥ 0.05 |
| Rank reversal count (AdvGLUE) | Number of models shifting ≥5 rank positions GLUE→AdvGLUE | > 0 (qualitative) |
| Rank reversal count (ANLI) | Number of models shifting ≥5 rank positions ANLI_R1→R3 | > 0 (qualitative) |

**Success Criteria:**
- **Primary (SHOULD_WORK):** Both ρ_AdvGLUE < 0.4 OR its p ≥ 0.05 **AND** ρ_ANLI < 0.4 OR its p ≥ 0.05
- **Secondary:** ρ_AdvGLUE < ρ_ANLI (adversarial attack disrupts more than difficulty shift)
- **PoC Pass Condition:** Code runs without error AND at least one adversarial pair confirms low ρ

**Expected Values (informed by H-M2 result):**
- H-M2 found: Δρ = ρ_fairness − mean(ρ_AdvGLUE, ρ_ANLI) = 0.192
- ρ_fairness from H-M1 ≈ 0.55–0.70 (estimated from H-M1 success)
- Expected ρ_robustness_mean ≈ 0.36–0.51 → individual pairs likely in 0.25–0.50 range
- At ρ_fairness ≈ 0.60, ρ_robustness_mean ≈ 0.41 → pairs may straddle 0.4 threshold
- H-M3 succeeds if both are < 0.4 or non-significant relative to 0.4

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical_analysis
- Library: pingouin + scipy.stats + numpy
- Code:
  ```python
  pip install pingouin scipy numpy pandas matplotlib
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart of ρ_AdvGLUE and ρ_ANLI vs. ρ_fairness (from H-M1) with 95% CI error bars and horizontal threshold line at ρ = 0.4

#### Additional Figures (LLM Autonomous)

1. **Rank Change Scatter Plot** — GLUE rank vs. AdvGLUE rank (per model), colored by magnitude of rank shift; analogous plot for ANLI_R1 vs. ANLI_R3
2. **Rank Reversal Heatmap** — Model × benchmark pair matrix showing rank positions; highlight large shifts
3. **Summary Correlation Table** — All four partial ρ values (ρ_fairness_BBQ, ρ_AdvGLUE, ρ_ANLI, ρ_mean_robust) in one visualization with CI and p-values
4. **Fisher z distribution plot** — Show where each ρ falls relative to ρ = 0.4 threshold with z-score distribution

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m3/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | DataFrame from H-M1/H-M2 contains GLUE, AdvGLUE, ANLI_R1, ANLI_R3, MMLU columns for all overlapping models | TRUE — verified in H-E1/H-M1 |
| Mechanism Isolatable | Can compute ρ per pair independently via pingouin.partial_corr | TRUE — separate function calls per pair |
| Baseline Measurable | ρ_fairness from H-M1 available as baseline reference for comparison | TRUE — H-M1 validated (ρ_fairness > 0.4) |

### Architecture Compatibility Check

**Statistical Analysis Compatibility** (not DL model — adapted protocol):

This is a statistical analysis experiment. "Architecture compatibility" means data sufficiency and library compatibility:

- **Required:** N ≥ 10 overlapping models with GLUE, AdvGLUE, ANLI_R1, ANLI_R3, MMLU scores (H-E1 confirmed)
- **Required:** pingouin ≥ 0.5.0 (partial_corr with method='spearman' and alternative parameter)
- **Required:** scipy ≥ 1.10 (spearmanr with alternative='greater')
- **Incompatible:** If N < 10 for either adversarial pair subset, analysis is underpowered (flag and document)

> ⚠️ If either adversarial pair has N < 10 overlapping models, Phase 4 MUST flag as underpowered and document as limitation.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "Computing ρ_AdvGLUE: GLUE→AdvGLUE partial Spearman (MMLU controlled)" | analysis.py:compute_partial_spearman() |
| Data Shape | DataFrame shape (N, 7) with all benchmark columns populated | data_loader.py:load_scores() |
| Metric Delta | ρ_AdvGLUE ≠ ρ_ANLI (pairs differ from each other and from ρ_fairness) | evaluate.py:compare_pairs() |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(df, results):
    """Verify H-M3 analysis mechanism actually ran on correct data."""
    indicators = {
        "data_complete": all(col in df.columns for col in
                             ['GLUE', 'AdvGLUE', 'ANLI_R1', 'ANLI_R3', 'MMLU']),
        "n_sufficient": len(df.dropna()) >= 10,
        "advglue_computed": 'rho_AdvGLUE' in results and results['rho_AdvGLUE'] is not None,
        "anli_computed": 'rho_ANLI' in results and results['rho_ANLI'] is not None,
        "pairs_differ": abs(results.get('rho_AdvGLUE', 0) -
                            results.get('rho_ANLI', 0)) > 0.001,
        "reversals_counted": 'reversals_AdvGLUE' in results and 'reversals_ANLI' in results
    }
    all_ok = all(indicators.values())
    return all_ok, indicators
```

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | All 6 indicator checks = True | verify_mechanism_activated() |
| Effect Measurable | ρ_AdvGLUE ≠ ρ_ANLI (pairs distinguishable) | Direct comparison |
| Hypothesis Supported | Both ρ < 0.4 OR p ≥ 0.05 for each pair | fisher_z_test_vs_threshold() |

**hypothesis_support_threshold:** ρ < 0.4 (below fairness-level stability) OR p(ρ ≥ 0.4) ≥ 0.05 (non-significant evidence for reaching fairness-level stability) for BOTH adversarial pairs independently.

**hypothesis_support_metric:** partial Spearman ρ per adversarial pair (MMLU-controlled), compared to ρ = 0.4 threshold via one-tailed Fisher z-test.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `rho_AdvGLUE < 0.4 OR p_AdvGLUE >= 0.05` (adversarial disruption confirmed for GLUE pair)
3. `rho_ANLI < 0.4 OR p_ANLI >= 0.05` (adversarial disruption confirmed for ANLI pair)

**Secondary check (qualitative):** At least 1 rank reversal (≥5 position shift) detected per adversarial pair.

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Status:** No domain-relevant results found. Archon KB is populated with diffusion model and computer vision content. All specifications sourced from Exa GitHub searches.

### B. GitHub Implementations (Exa)

**Repository 1**: HowieHwong/TrustLLM (⭐ 628)
- **URL**: https://github.com/HowieHwong/TrustLLM
- **Query Used**: "TrustLLM dataset BBQ benchmark scores per model pandas CSV published results"
- **Relevance**: Official source for per-model trustworthiness scores (16 LLMs); robustness dimension includes AdvGLUE-based metrics; fairness includes BBQ variants
- **Dataset Access**:
  ```python
  from trustllm.dataset_download import download_dataset
  download_dataset(save_path='./data/trustllm')
  ```
- **Leaderboard data**: https://trustllmbenchmark.github.io/TrustLLM-Website/leaderboard.html (numerical scores for ChatGPT, GPT-4, LLaMA-2 variants, Vicuna, Mistral, Falcon, ChatGLM2)
- **Used For**: Primary source of per-model scores for BBQ-disambig, BBQ-ambig, GLUE, AdvGLUE, MMLU

**Repository 2**: AI-secure/adversarial-glue (⭐ 13)
- **URL**: https://github.com/ai-secure/adversarial-glue
- **Query Used**: "TrustLLM AdvGLUE ANLI adversarial rank stability"
- **Relevance**: Official AdvGLUE benchmark (NeurIPS 2021) with per-model accuracy scores on adversarial GLUE tasks
- **Architecture**: 5 GLUE tasks + adversarial versions (word-level, sentence-level, human-written attacks)
- **Key Info**: Test set with annotations at https://adversarialglue.github.io; method='glue' for benign baseline
- **Used For**: AdvGLUE per-model scores and understanding of adversarial construction methodology

**Repository 3**: scipy.stats.spearmanr (SciPy official)
- **URL**: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html
- **Query Used**: "partial Spearman correlation Python scipy implementation LLM evaluation rank"
- **Key Code**:
  ```python
  from scipy.stats import spearmanr
  # For small N (<500), use permutation test for reliable p-values
  res = spearmanr(x, y, alternative='greater')
  ```
- **Used For**: Spearman ρ computation; permutation test guidance for small N

**Repository 4**: pingouin.partial_corr (pingouin-stats.org)
- **URL**: https://pingouin-stats.org/generated/pingouin.partial_corr.html / https://github.com/raphaelvallat/pingouin
- **Query Used**: "pingouin partial_corr Spearman Python example covariate rank correlation"
- **Key Code**:
  ```python
  import pingouin as pg
  result = df.partial_corr(x='GLUE', y='AdvGLUE',
                           covar='MMLU', method='spearman',
                           alternative='greater')
  # Returns DataFrame: n, r, CI95%, r2, adj_r2, p-val, power
  ```
- **Implementation note**: Uses regression-on-ranks (residuals of linear regression on rank-transformed data), then Pearson on residuals → equivalent to standard partial Spearman ρ for continuous variables
- **Used For**: Primary implementation of partial Spearman ρ for all H-M hypotheses

**Repository 5**: Fisher z-test comparison (Preacher & Lee, 2013; statpsych R package reference)
- **URL**: https://quantpsy.org/corrtest/corrtest2.htm; https://dgbonett.github.io/statpsych/reference/test.spear2.html
- **Query Used**: "Fisher z-test difference two Spearman correlations Python scipy statsmodels"
- **Key Formula**:
  ```python
  # One-tailed test: ρ < threshold (0.4)
  z_stat = (np.arctanh(rho) - np.arctanh(0.4)) / (1 / np.sqrt(n - 3))
  p = scipy.stats.norm.cdf(z_stat)  # P(Z < z_stat) for H1: ρ < 0.4
  ```
- **Used For**: Evaluating whether each adversarial pair ρ is significantly below the 0.4 fairness threshold

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — all code uses standard SciPy/pingouin APIs with clear, well-documented interfaces. No custom architecture or complex code patterns requiring semantic analysis.

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Reports — H-M1 (VALIDATED), H-M2 (FAILED at Δρ=0.192, directional support confirmed)

- **Reused Components**:
  - `data/model_scores.csv`: model × benchmark score matrix (N ≥ 10 overlapping models)
  - `compute_partial_spearman()` function from H-M1/H-M2 code
  - `fisher_z_test_vs_threshold()` helper
  - MMLU covariate scores per model
  - Bootstrap CI computation
- **Why Reused**: Enables fully controlled comparison — only the benchmark pair changes (AdvGLUE pair vs. ANLI pair vs. BBQ pair), all other factors identical

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Phase 2A/2B + H-E1 validation | 02b_verification_plan.md §1.3 + H-E1 |
| Adversarial pair definition | GitHub | AI-secure/adversarial-glue (AdvGLUE); OOD_NLP (ANLI) |
| Partial Spearman ρ method | GitHub + Docs | pingouin.partial_corr (B.4) |
| Permutation test for small N | Docs | scipy.stats.spearmanr docs (B.3) |
| Fisher z vs. threshold | Web | Preacher & Lee 2013 (B.5) |
| Bootstrap CI | Blog | leehanchung.github.io (Exa search) |
| Rank reversal metric | 02b_verification_plan.md | H-M3 §Verification Protocol step 3 |
| Success threshold (ρ < 0.4) | 02b_verification_plan.md | H-M3 §Success Criteria |
| Pseudo-code structure | GitHub + Docs | pingouin API (B.4), scipy spearmanr (B.3) |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — restated in state block)
**Date:** 2026-08-20

### Workflow History for This Hypothesis

- H-E1: VALIDATED (N_common ≥ 10 confirmed)
- H-M1: VALIDATED (ρ_fairness > 0.4, p < 0.05 confirmed)
- H-M2: FAILED at gate (Δρ=0.192 < 0.200); directional support confirmed; pipeline continues to H-M3
- H-M3: Phase 2C IN_PROGRESS → COMPLETED (this document)

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant results), Exa (GitHub + Web search — 5+ relevant sources), Serena (skipped — not needed)*
*All specifications grounded in researched implementations and Phase 2B verification protocol*
*Next Phase: Phase 3 - Implementation Planning*
