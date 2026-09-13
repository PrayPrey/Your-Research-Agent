# Experiment Design: h-c1

**Date:** 2026-08-04
**Author:** Anonymous
**Hypothesis Statement:** The capability-alignment relationship is monotonic at population extremes: Dunn post-hoc Q1 vs Q4 Bonferroni-corrected p < 0.05 on LC_winrate across win_rate quartiles. Confirms relationship holds beyond average-level effect.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **CONDITION (Boundary Test) Template** — Tests whether the capability-LC preference effect holds at population extremes, not just on average.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-E1 (PASS), H-M1 (PASS), H-M2 (PASS), H-M3 (PASS)
**Gate Status:** SHOULD_WORK — failure narrows scope only

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-c1
- **Type:** CONDITION (boundary/scope verification)
- **Prerequisites:** h-e1 (PASS), h-m1 (PASS), h-m2 (PASS), h-m3 (PASS)

### Gate Condition

**SHOULD_WORK** — Primary: Kruskal-Wallis p < 0.05 on LC_winrate AND Dunn Q1 vs Q4 Bonferroni-corrected p < 0.05.
Secondary: Monotonic median trend Q1 < Q2 < Q3 < Q4 (not required for gate pass).

Failure action: Document that the capability-alignment relationship holds at the population level (H-E1–H-M3 all PASS) but may not be monotonic at the extremes. Narrow scope accordingly and proceed.

---

## Continuation Context

This is the **fifth and final** hypothesis in the H-BiAlign-v1 verification chain. All four prerequisites have passed:

| Hypothesis | Result | Key Finding |
|------------|--------|-------------|
| H-E1 (MUST_WORK) | PASS | r_partial=0.9851, p=1.69e-170 — capability independently predicts LC preference |
| H-M1 (MUST_WORK) | PASS | \|β_win_std\|=21.34 >> \|β_len_std\|=4.37 — capability dominates verbosity |
| H-M2 (SHOULD_WORK) | PASS | rho_resid=0.9739, p=2.37e-144 — residual capability signal confirmed |
| H-M3 (SHOULD_WORK) | PASS | KW H=22.19, p=5.97e-05, ε²=0.0876 — Δ differs across capability quartiles |

### H-M3 Distinction from H-C1

H-M3 tested KW on **Δ = LC_winrate − win_rate** (alignment gap). The Dunn Q1 vs Q4 on Δ was p=1.0 (non-significant after Bonferroni).

H-C1 tests LC_winrate **directly** — not Δ. Given r_partial=0.9851, LC_winrate should track win_rate extremely closely, making the monotonic quartile test much more likely to pass on LC_winrate than on the composed Δ variable.

### Previous Hypothesis Results
- **H-M3 Quartile Groups:** Q1=56, Q2=56, Q3=55, Q4=56 models (reuse same quartile split)
- **H-M3 Median Δ per quartile:** Q1=2.19, Q2=2.96, Q3=5.43, Q4=0.91 (non-monotonic)
- **Code infrastructure:** Fully reusable from h-e1/h-m1/h-m2/h-m3

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Kruskal-Wallis Dunn post-hoc test quartile comparison**
- Archon KB returned diffusion-model results (no relevant statistical analysis cases)
- Archon KB is populated with image generation research; no prior cases for LLM evaluation statistical analysis
- **Finding:** No Archon KB cases directly applicable — rely on Exa findings and prior hypothesis code

**Query 2: Partial correlation statistical analysis LLM evaluation**
- No relevant Archon KB hits for this statistical domain
- **Finding:** Archon KB not applicable for this purely statistical analysis hypothesis

**Summary:** Archon KB does not contain statistical analysis cases for LLM leaderboard studies. All implementation grounding comes from Exa search results, scikit-posthocs documentation, and the h-m3 prior validation code.

### Archon Code Examples

No relevant code examples found in Archon KB for non-parametric statistical tests. Archon KB is optimized for deep learning implementation patterns.

**Archon Code Summary:** Not applicable — this experiment uses scipy/scikit-posthocs, not PyTorch.

### Exa GitHub Implementations

**Query 1: scikit_posthocs posthoc_dunn Bonferroni correction Python quartile**

**Source 1:** scikit-posthocs official documentation (scikit-posthocs.readthedocs.io)
- **URL:** https://scikit-posthocs.readthedocs.io/en/latest/generated/scikit_posthocs.posthoc_dunn.html
- **Relevance:** Official API documentation for the exact test required by H-C1 verification protocol
- **Key API:**
  ```python
  scikit_posthocs.posthoc_dunn(
      a,                    # list, ndarray, or DataFrame
      val_col=None,         # column name for dependent variable
      group_col=None,       # column name for grouping variable
      p_adjust='bonferroni' # correction method
  ) → DataFrame             # pairwise p-value matrix
  ```
- **Bonferroni:** multiplies raw p-values by m=6 (number of pairwise comparisons for 4 groups). Conservative but standard.
- **Tie correction:** Applied automatically using Glantz (2012) formula.

**Source 2:** Dunn's Post-Hoc Test blog (suchibrata.in)
- **URL:** https://suchibrata.in/blog/statistical-tests/dunns-post-hoc-test
- **Key pattern:**
  ```python
  from scipy import stats
  import scikit_posthocs as sp
  
  # Step 1: Kruskal-Wallis
  H, p_kw = stats.kruskal(*[group_vals for group in groups])
  
  # Step 2: Dunn post-hoc with Bonferroni
  dunn_bonf = sp.posthoc_dunn(df, val_col="lc_winrate", group_col="quartile", p_adjust="bonferroni")
  
  # Step 3: Extract Q1 vs Q4
  p_q1_q4 = dunn_bonf.loc['Q1', 'Q4']
  ```
- **Insight:** Bonferroni is the most commonly reported correction for 4-group comparison (m=6 pairs). Holm is uniformly more powerful but both are supported.

**Source 3:** GitHub - maximtrp/scikit-posthocs (source code)
- **URL:** https://github.com/maximtrp/scikit-posthocs/blob/master/scikit_posthocs/_posthocs.py
- **Key implementation detail:** Uses z-test on rank sums with tie correction:
  ```python
  def compare_dunn(i, j):
      diff = np.abs(x_ranks_avg.loc[i] - x_ranks_avg.loc[j])
      A = n * (n + 1.0) / 12.0
      B = 1.0 / x_lens.loc[i] + 1.0 / x_lens.loc[j]
      z_value = diff / np.sqrt((A - x_ties) * B)
      p_value = 2.0 * ss.norm.sf(np.abs(z_value))
  ```
- **Insight:** The test computes z-statistics on average ranks — robust to distribution assumptions.

**Query 2: AlpacaEval win_rate quartile LC_winrate analysis Python**

**Source 4:** AlpacaEval length_controlled.ipynb (official repo)
- **URL:** https://github.com/tatsu-lab/alpaca_eval/blob/main/notebooks/length_controlled.ipynb
- **Relevance:** Official AlpacaEval analysis confirming the CSV structure and LC win rate computation
- **Key insight:** LC win rate gameability is ~6% vs raw win rate ~21% — confirms LC_winrate is the less-biased metric
- **Spearman correlation with Chatbot Arena:** 0.936 (raw) — LC even higher

**Source 5:** AlpacaEval arXiv paper (Dubois 2024)
- **URL:** https://arxiv.org/html/2404.04475v1
- **Relevance:** Confirms LC_winrate interpretation and correlation structure
- **Key finding:** LC_winrate preserves win-rate properties (symmetric, [0,100] range) while removing length bias

**Serena Analysis Needed:** No — this is a purely statistical analysis using pandas/scipy/scikit-posthocs. No complex ML code requiring semantic analysis.

### 🎯 Implementation Priority Assessment

**CRITICAL: This is a statistical analysis experiment (not paper reproduction)**

This hypothesis tests whether the capability-LC preference relationship is monotonic at population extremes using pre-computed AlpacaEval 2.0 leaderboard data.

**Recommended Implementation Path:**
- Primary: Extend h-m3 code (which already computes quartile splits and Kruskal-Wallis) to test LC_winrate instead of Δ
- Fallback: Fresh implementation using verified scikit-posthocs pattern from Exa documentation
- Justification: H-C1 is nearly identical to H-M3 mechanically — same quartile split, same Kruskal-Wallis + Dunn pipeline — but with LC_winrate as the dependent variable instead of Δ.

### Code Analysis (Serena MCP)

**Skipped** — Code from search results was sufficiently clear. This experiment uses standard statistical libraries (scipy, scikit-posthocs, pandas) with well-documented APIs. No custom PyTorch modules or complex architectures require semantic analysis.

---

## Experiment Specification

### Dataset

**Name:** AlpacaEval 2.0 Leaderboard (pre-computed scores)  
**Type:** standard  
**Source:** https://github.com/tatsu-lab/alpaca_eval  
**Cache path:** docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv  
**N:** N=222 (223 rows after loading; 1 baseline row may be included)  
**Columns required:** `win_rate`, `length_controlled_winrate`, `avg_length`  
**Verified:** True (used in H-E1, H-M1, H-M2, H-M3 — no download needed)  

**Statistics:**
- 222 LLMs from diverse sources (GPT-4, Claude, Llama, Mistral, open-source variants)
- win_rate range: ~5% to ~70% (continuous, human preference fraction)
- length_controlled_winrate range: ~5% to ~68% (GLM-debiased)
- avg_length range: ~500 to ~3000 tokens

**Preprocessing:**
1. Load CSV: `pd.read_csv('docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv')`
2. Drop rows with missing `win_rate`, `length_controlled_winrate`, or `avg_length`
3. Verify N ≥ 200 after cleaning
4. Create quartile column: `df['quartile'] = pd.qcut(df['win_rate'], q=4, labels=['Q1','Q2','Q3','Q4'])`

**No augmentation** — observational analysis, no data generation.

**Loading Information** (for Phase 4 download):
- Method: custom (CSV already present in repo)
- Identifier: `docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv`
- Code: `df = pd.read_csv('docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv')`

### Models

#### Baseline Model

**Name:** N/A — Statistical analysis (no model training)  
**Architecture:** Null model — Kruskal-Wallis under H0: LC_winrate distributions are identical across all four quartiles  
**Description:** The baseline is the null hypothesis that capability quartile does not predict LC_winrate distribution. The KW test directly evaluates this.

**Loading Information** (for Phase 4 download):
- Method: N/A (no model download)
- Identifier: N/A
- Code: N/A

#### Proposed Model

**Architecture:** Baseline + monotonicity test (H-C1 claim)  
The "proposed model" is the alternative hypothesis: H1: LC_winrate distributions differ significantly across capability quartiles AND the Q1 vs Q4 difference is significant after Bonferroni correction.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Quartile Monotonicity Test for H-C1
# Based on: scikit-posthocs documentation + h-m3 prior implementation

import pandas as pd
import numpy as np
from scipy import stats
import scikit_posthocs as sp

def run_hc1_analysis(df):
    """
    H-C1: Tests whether LC_winrate is monotonically higher
    for higher capability quartiles, specifically Q1 vs Q4.

    Args:
        df: DataFrame with win_rate, length_controlled_winrate, avg_length
    Returns:
        dict with kw_stat, kw_p, dunn_q1_q4_p, monotonic, quartile_stats
    """
    # Step 1: Create capability quartiles from win_rate
    df = df.copy()
    df['quartile'] = pd.qcut(df['win_rate'], q=4, labels=['Q1','Q2','Q3','Q4'])

    # Step 2: Extract LC_winrate per quartile group
    groups = [df[df['quartile'] == q]['length_controlled_winrate'].values
              for q in ['Q1', 'Q2', 'Q3', 'Q4']]

    # Step 3: Kruskal-Wallis omnibus test
    kw_stat, kw_p = stats.kruskal(*groups)

    # Step 4: Dunn post-hoc with Bonferroni (6 pairs for 4 groups)
    dunn_result = sp.posthoc_dunn(
        df, val_col='length_controlled_winrate',
        group_col='quartile', p_adjust='bonferroni'
    )
    p_q1_q4 = dunn_result.loc['Q1', 'Q4']

    # Step 5: Check monotonic trend
    medians = df.groupby('quartile', observed=True)['length_controlled_winrate'].median()
    monotonic = all(medians[q1] < medians[q2]
                    for q1, q2 in zip(['Q1','Q2','Q3'], ['Q2','Q3','Q4']))

    return {'kw_stat': kw_stat, 'kw_p': kw_p,
            'dunn_q1_q4_p': p_q1_q4, 'monotonic': monotonic,
            'quartile_medians': medians.to_dict()}
```

### Training Protocol

**No training** — this is a purely observational statistical analysis.

**Analysis Protocol:**
- **Optimizer:** N/A
- **Learning Rate:** N/A
- **Batch Size:** N/A (full dataset, N=222)
- **Epochs:** N/A
- **Loss:** N/A
- **Seeds:** 1 (fixed: `random_state=42` for pd.qcut if needed)

**Statistical Parameters:**
- **Alpha level:** 0.05 (two-tailed)
- **Correction method:** Bonferroni (m=6 pairwise comparisons for 4 groups)
- **Bootstrap:** 1000 resamples for CI on Dunn statistic (secondary robustness check)
- **Quartile definition:** pd.qcut with q=4, equal-frequency bins on win_rate

**Reused from H-M3 (continuation):**
- Same quartile split (pd.qcut, q=4, labels Q1-Q4)
- Same dataset loading and cleaning pipeline
- Same KW + Dunn implementation pattern
- Same figure output directory structure

**Key difference from H-M3:** Dependent variable is `length_controlled_winrate` (not `Δ = length_controlled_winrate − win_rate`).

### Evaluation

**Primary Metrics:**

| Metric | Threshold | Gate |
|--------|-----------|------|
| Kruskal-Wallis p-value | < 0.05 | Required for proceeding to Dunn |
| Dunn Q1 vs Q4 (Bonferroni) | < 0.05 | PRIMARY gate condition |
| Monotonic trend Q1<Q2<Q3<Q4 | True | Secondary (not required for PASS) |

**Secondary Metrics:**
- Effect size: epsilon-squared from KW (ε² = H / (N−1))
- Quartile median LC_winrate for each of Q1, Q2, Q3, Q4
- Dunn full 4×4 p-value matrix (all pairwise comparisons)

**Success Criteria:**
- **PRIMARY (SHOULD_WORK gate):** KW p < 0.05 AND Dunn Q1 vs Q4 Bonferroni p < 0.05
- **FAIL action:** Document as scope limitation — "H-C1 boundary condition not confirmed; relationship holds at population level (H-E1–H-M3) but not at quartile extremes"

**Expected Performance** (from prior pipeline):
- KW on LC_winrate expected to pass (given r_partial=0.9851, LC_winrate is nearly monotone with win_rate)
- Dunn Q1 vs Q4 on LC_winrate expected to be strongly significant (unlike Δ which had p=1.0 due to mathematical composition)
- Epsilon-squared expected ~0.6–0.9 (much larger than H-M3's 0.0876 on Δ, since LC_winrate has less composition noise)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical analysis (non-parametric)
- Library: scipy.stats (kruskal), scikit-posthocs (posthoc_dunn)
- Code:
  ```python
  from scipy import stats
  import scikit_posthocs as sp
  H, p = stats.kruskal(*groups)
  dunn = sp.posthoc_dunn(df, val_col='length_controlled_winrate', group_col='quartile', p_adjust='bonferroni')
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** KW p-value and Dunn Q1 vs Q4 p-value vs 0.05 threshold bar chart

#### Additional Figures (LLM Autonomous)

Based on H-C1 hypothesis structure (quartile monotonicity test):

1. **Boxplot:** LC_winrate distribution per quartile (Q1–Q4) with median lines and individual model points
2. **Dunn Heatmap:** 4×4 pairwise Bonferroni-corrected p-value heatmap (green = significant, red = not)
3. **Monotonicity Plot:** Quartile median LC_winrate with 95% bootstrap CI error bars — shows whether trend is monotonic
4. **Comparison with H-M3:** Side-by-side median bars for Δ (H-M3) vs LC_winrate (H-C1) per quartile to show why H-C1 is a cleaner test

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures saved to `docs/youra_research/h-c1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. KW p < 0.05 AND Dunn Q1 vs Q4 Bonferroni p < 0.05

**Note:** This is a CONDITION/boundary hypothesis. Success confirms monotonicity at extremes. Failure still preserves the main finding (H-E1–H-M3 all PASS).

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Archon KB Findings:** No relevant sources found for statistical analysis of LLM evaluation metrics. Archon KB is populated with deep learning / image generation research. Queries executed:
- "Kruskal-Wallis Dunn post-hoc test quartile comparison" → diffusion model results (similarity ~0.34, not relevant)
- "partial correlation statistical analysis LLM evaluation" → diffusion model results (similarity ~0.45, not relevant)
- "scipy kruskal scipy stats quartile nonparametric test" → PyTorch distributed code (not relevant)

**Conclusion:** Archon KB not applicable for this hypothesis. All implementation grounded in Exa documentation sources.

### B. GitHub Implementations (Exa)

**Repository 1:** scikit-posthocs official documentation
- **URL:** https://scikit-posthocs.readthedocs.io/en/latest/generated/scikit_posthocs.posthoc_dunn.html
- **Query Used:** "scikit_posthocs posthoc_dunn Bonferroni correction Python quartile"
- **Key Code (annotated):**
  ```python
  # Official API signature
  sp.posthoc_dunn(a, val_col='score', group_col='group', p_adjust='bonferroni')
  # Returns: pandas DataFrame (NxN pairwise p-value matrix)
  # Used as basis for: core mechanism pseudo-code Step 4
  ```
- **Configuration Extracted:** p_adjust='bonferroni' (standard for 4-group comparison with 6 pairs)
- **Used For:** Core mechanism implementation, evaluation metrics code

**Repository 2:** scikit-posthocs source code (maximtrp/scikit-posthocs)
- **URL:** https://github.com/maximtrp/scikit-posthocs/blob/master/scikit_posthocs/_posthocs.py
- **Key Code (annotated):**
  ```python
  # Dunn's test implementation — z-score on rank sums with tie correction
  def compare_dunn(i, j):
      diff = np.abs(x_ranks_avg.loc[i] - x_ranks_avg.loc[j])
      A = n * (n + 1.0) / 12.0
      B = 1.0 / x_lens.loc[i] + 1.0 / x_lens.loc[j]
      z_value = diff / np.sqrt((A - x_ties) * B)
      p_value = 2.0 * ss.norm.sf(np.abs(z_value))
  # Used as basis for: understanding what the test computes (rank-sum z-test)
  ```
- **Used For:** Confirming algorithm correctness, understanding tie correction

**Repository 3:** AlpacaEval official repo
- **URL:** https://github.com/tatsu-lab/alpaca_eval
- **Relevance:** Confirms dataset structure and LC win rate computation method
- **Used For:** Dataset specification, confirming column names

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results was sufficiently clear.
All required functions (scipy.stats.kruskal, scikit_posthocs.posthoc_dunn) are well-documented standard library functions with no custom architectures requiring semantic analysis.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Reports — h-e1, h-m1, h-m2, h-m3
- **Files:** docs/youra_research/h-m3/04_validation.md (most relevant predecessor)
- **Reused Components:**
  - Dataset: AlpacaEval 2.0 CSV — proven stable across 4 prior hypotheses
  - Quartile split: pd.qcut(df['win_rate'], q=4, labels=['Q1','Q2','Q3','Q4']) — exact same split
  - KW + Dunn pipeline structure — validated in H-M3
- **Key H-M3 Finding Informing H-C1:**
  - H-M3 Dunn Q1 vs Q4 on Δ: p=1.0 (failed) — but DV was Δ, not LC_winrate
  - H-C1 uses LC_winrate as DV — avoids the mathematical composition issue in Δ

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Prior hypothesis (h-e1 through h-m3) | verification_state.yaml |
| Dataset loading code | Official repo | AlpacaEval GitHub (Exa B.3) |
| Quartile split method | Prior hypothesis | h-m3 04_validation.md |
| Kruskal-Wallis implementation | scipy documentation | scipy.stats.kruskal |
| Dunn post-hoc (Bonferroni) | scikit-posthocs docs | Exa B.1, B.2 |
| Core pseudo-code | scikit-posthocs source + h-m3 prior | Exa B.1, B.2, D.1 |
| Expected performance | H-E1 r_partial=0.9851 + H-M3 contrast | Prior validation reports |
| Visualization design | H-M3 figures + H-C1 distinction | docs/youra_research/h-m3/figures/ |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-04T09:30:00Z

### Workflow History for This Hypothesis

- 2026-08-04T09:24:32Z: H-C1 set to IN_PROGRESS (external loop)
- 2026-08-04T09:30:00Z: Phase 2C experiment design COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant results), Exa (scikit-posthocs docs + AlpacaEval repo), Serena (skipped — standard statistical libraries)*
*All specifications grounded in researched implementations and prior hypothesis results*
*Next Phase: Phase 3 - Implementation Planning*
