# Experiment Design: h-m2

**Date:** 2026-08-20
**Author:** Anonymous
**Hypothesis Statement:** Partial Spearman ρ_fairness (BBQ-Disambig→BBQ-Ambig, MMLU-controlled) exceeds partial ρ_robustness (GLUE→AdvGLUE and ANLI R1→R3, MMLU-controlled) by Δρ ≥ 0.2, because adversarial benchmark construction specifically targets models that pass the in-distribution version, disrupting rank stability more than distributional underspecification affects fairness rank stability.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M1 (PASS — partial ρ_fairness > 0.4, p < 0.05 established; TrustLLM dataset and pingouin methodology validated)
**Gate Status:** SHOULD_WORK — Δρ ≥ 0.2 (ρ_fairness > mean(ρ_AdvGLUE, ρ_ANLI), directional/exploratory, two-tailed Fisher z for difference between two correlations)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM (exploratory/directional)
- **Prerequisites:** h-m1 (VALIDATED — ρ_fairness established; same dataset and methodology reused)

### Gate Condition
SHOULD_WORK: Δρ = ρ_fairness − mean(ρ_AdvGLUE, ρ_ANLI) ≥ 0.2. Failure does not stop the pipeline — document as limitation and proceed to h-m3. This is a headline empirical claim (P2) differentiating the work from dimension-by-dimension analysis.

---

## Continuation Context

H-M1 PASS established partial ρ_fairness (BBQ-Disambig→BBQ-Ambig, MMLU-controlled) using TrustLLM evaluation scores and the pingouin.partial_corr methodology. H-M2 reuses the same dataset (TrustLLM + supplementary sources), the same overlapping model set (N_common established by H-E1/H-M1), and the same pingouin-based partial Spearman ρ computation. The only new data required are per-model GLUE, AdvGLUE, ANLI-R1, and ANLI-R3 scores for the same N_common model set, plus a Fisher z-test for the difference between two independent partial correlations.

### Previous Hypothesis Results (if applicable)
- **H-E1:** PASS. N_common ≥ 10 models with BBQ-Disambig, BBQ-Ambig, MMLU scores confirmed from TrustLLM (arXiv 2401.05561).
- **H-M1:** PASS (VALIDATED). partial ρ_fairness > 0.4, p < 0.05 (one-tailed Fisher z, MMLU-controlled). Methodology: pingouin.partial_corr, method='spearman', alternative='greater'. Data: TrustLLM per-model fairness scores.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "differential rank correlation benchmark comparison statistical"**
- Max similarity: 0.45 — diffusion model content only (consistent with h-m1 finding)
- No domain-relevant cases in Archon KB for LLM evaluation statistics

**Query 2: "adversarial robustness LLM benchmark GLUE AdvGLUE rank stability"**
- Best match: arXiv 2305.14314 (similarity 0.45) — not directly relevant

**Query 3: "Fisher z-transformation difference two correlations significance test"**
- Max similarity: 0.35 — diffusion model content only

**Assessment:** Archon KB is populated with image generation / diffusion model content and contains no relevant prior cases for this statistical methodology domain. All implementation grounded in Exa searches.

### Archon Code Examples

**Query 1: "partial Spearman correlation comparison Python pingouin scipy"**
- No relevant code examples — diffusion/distributed computing content returned

**Assessment:** No usable patterns from Archon. Implementation based on psinger/CorrelationStats and pingouin found via Exa.

### Exa GitHub Implementations

**Source 1: psinger/CorrelationStats** (Fisher z-test for difference between two correlations)
- **URL:** https://github.com/psinger/CorrelationStats/blob/master/corrstats.py
- **Relevance:** Primary library for testing statistical significance of the difference between two independent correlation coefficients (ρ_fairness vs ρ_robustness)
- **Key Code:**
  ```python
  import numpy as np
  from scipy.stats import norm
  from math import atanh

  def independent_corr(xy, ab, n, n2=None, twotailed=True, method='fisher'):
      """
      Test significance of difference between two independent correlations.
      xy: ρ_fairness (partial Spearman, BBQ pair)
      ab: ρ_robustness (partial Spearman, adversarial pair)
      n: sample size for xy
      n2: sample size for ab (if different)
      """
      if method == 'fisher':
          xy_z = 0.5 * np.log((1 + xy) / (1 - xy))   # Fisher z of ρ_fairness
          ab_z = 0.5 * np.log((1 + ab) / (1 - ab))   # Fisher z of ρ_robustness
          if n2 is None:
              n2 = n
          se_diff = np.sqrt(1/(n - 3) + 1/(n2 - 3))
          diff = xy_z - ab_z
          z = abs(diff / se_diff)
          p = (1 - norm.cdf(z))
          if twotailed:
              p *= 2
          return z, p
  ```
- **Insight:** Fisher z-transformation applied to each correlation independently; SE of the difference uses 1/(n-3) + 1/(n2-3) formula. For same N, n2=n. Two-tailed test for exploratory comparison.
- **Also available via:** MicrosoftResearch/Azimuth (identical implementation, production-tested)

**Source 2: AI-secure/adversarial-glue** (AdvGLUE scores)
- **URL:** https://github.com/ai-secure/adversarial-glue
- **Relevance:** Official AdvGLUE benchmark (NeurIPS 2021, Oral). Provides per-model scores on adversarial GLUE tasks (SST-2, QQP, MNLI, QNLI, RTE). Key finding: all tested LLMs score far below benign GLUE accuracy; performance gap can be as large as 55%.
- **Key per-model data from paper (Table 4):**
  - BERT (Large): GLUE high, AdvGLUE near random guess on several tasks
  - ALBERT (XXLarge): highest AdvGLUE score among tested models
  - DeBERTa (Large): second highest
  - SMART (BERT): GLUE improved, AdvGLUE worst performer
- **Insight:** Rank ordering on AdvGLUE substantially different from GLUE — supports hypothesis that adversarial construction disrupts rank stability. TrustLLM evaluates subset of these models.

**Source 3: arXiv 2412.10535 — On Adversarial Robustness and OOD Robustness of LLMs**
- **URL:** https://doi.org/10.48550/arxiv.2412.10535
- **Relevance:** Directly studies correlation between adversarial robustness and OOD robustness across LLMs — closely adjacent to H-M2. Key finding: "negative correlation observed in LLaMA2:13B" between adversarial and OOD robustness; results "strongly influenced by limited number of benchmarks."
- **Insight:** Confirms that adversarial robustness rank ordering is model-size and architecture dependent, potentially disrupted by adversarial benchmark design — supports theoretical motivation. Also flags small-N limitation.

**Source 4: TrustLLM Leaderboard + Paper (robustness dimension)**
- **URL:** https://trustllmbenchmark.github.io/TrustLLM-Website/leaderboard.html
- **Relevance:** TrustLLM evaluates 16 LLMs on robustness dimension including GLUE-based and ANLI-based tasks. Per-model robustness scores available from leaderboard JSON and paper tables.
- **Insight:** Same 16 models evaluated across fairness AND robustness dimensions — enables direct comparison of ρ_fairness vs ρ_robustness on the same N_common model set, eliminating sample size confound.

**Source 5: psinger Medium article — "Statistical Significance Tests on Correlation Coefficients"**
- **URL:** https://medium.com/@ph_singer/statistical-significance-tests-on-correlation-coefficients-b9397380be55
- **Key guidance:** For same-sample models evaluated on two different benchmark pairs, the ρ_fairness and ρ_robustness correlations are computed from the SAME model set → strictly independent_corr (Fisher) applies when comparing two pairs (BBQ pair vs GLUE→AdvGLUE pair), since the benchmark pairs themselves are distinct measurement instruments.

**Serena Analysis Needed:** false — pure tabular statistical analysis, no complex neural code (same as h-m1).

### 🎯 Implementation Priority Assessment

H-M2 extends the h-m1 statistical analysis to two additional benchmark pairs. Priority:

1. **TrustLLM paper robustness tables** (Tables for GLUE/AdvGLUE robustness dimension per model) — primary source, single protocol
2. **TrustLLM GitHub leaderboard JSON** (robustness scores endpoint) — programmatic access
3. **Supplementary from OOD_NLP (Yuan et al., NeurIPS 2023) / GLUE-X** — if TrustLLM does not report AdvGLUE per-model scores directly
4. **Manual extraction from AdvGLUE leaderboard** (adversarialglue.github.io) — fallback for individual model GLUE vs AdvGLUE scores

**Recommended Implementation Path:**
- Primary: TrustLLM robustness section scores (same source as H-M1 fairness scores — eliminates cross-protocol noise)
- Fallback: Cross-reference AdvGLUE leaderboard + OOD_NLP for GLUE/AdvGLUE, and ANLI leaderboard for ANLI R1/R3 scores
- Justification: Reusing TrustLLM as single source maximizes protocol consistency (Assumption A3) and maintains N_common from H-E1/H-M1

### Code Analysis (Serena MCP)

*Skipped* — Code from search results sufficiently clear. This is a pure statistical meta-analysis (partial Spearman ρ comparison across dimensions on a model × benchmark score matrix). No complex neural code to analyze.

---

## Experiment Specification

### Dataset

**Name:** TrustLLM Multi-Model Evaluation Scores — Extended (BBQ-Disambig, BBQ-Ambig, GLUE, AdvGLUE, ANLI-R1, ANLI-R3, MMLU)
**Type:** programmatic-api / published_scores (real data — NOT synthetic)
**Source:** Huang et al., TrustLLM (ICML 2024), arXiv 2401.05561; Wang et al., AdvGLUE (NeurIPS 2021), arXiv 2111.02840; Nie et al., ANLI (ACL 2020)
**GitHub:** https://github.com/HowieHwong/TrustLLM + https://github.com/ai-secure/adversarial-glue
**Leaderboard:** https://trustllmbenchmark.github.io/TrustLLM-Website/leaderboard.html

**Structure:**
- Unit of analysis: LLM model (N = N_common from H-E1/H-M1, expected 10–16)
- Variables per model (extending h-m1 DataFrame):
  - `bbq_disambig_score`: Fairness accuracy on BBQ disambiguated context (from h-m1)
  - `bbq_ambig_score`: Fairness accuracy on BBQ ambiguous context (from h-m1)
  - `mmlu_score`: MMLU accuracy — capability control (from h-m1)
  - `glue_score`: GLUE benchmark aggregate score (in-distribution robustness)
  - `advglue_score`: AdvGLUE aggregate score (adversarial OOD robustness)
  - `anli_r1_score`: ANLI Round 1 accuracy (in-distribution)
  - `anli_r3_score`: ANLI Round 3 accuracy (adversarially-constructed OOD)
  - `model_name`: Standardized model identifier (same as h-m1)

**Model Set:** Same N_common from H-E1 (ChatGPT, GPT-4, Llama2 variants, Vicuna variants, ChatGLM2, Falcon, Mistral, Oasst, Alpaca, ERNIE, PaLM2 — subset with all 7 scores)

**Preprocessing:**
1. Load h-m1 DataFrame (bbq_disambig, bbq_ambig, mmlu, model_name) as base
2. Extract per-model GLUE and AdvGLUE scores from TrustLLM robustness section (paper Table / leaderboard JSON)
3. Extract per-model ANLI-R1 and ANLI-R3 scores from TrustLLM robustness section
4. Inner join on model_name → N_common_robust = models with all 7 scores
5. Flag if N_common_robust < N_common (from h-m1) — document reduction
6. Build master DataFrame with 7 score columns + model_name

**Sensitivity Analysis Dataset:**
- Use Winogrande as MMLU substitute for capability control (same as h-m1 sensitivity check)
- Report both MMLU-controlled and Winogrande-controlled Δρ

**Synthetic Data Policy:** COMPLIANT — uses real published scores from peer-reviewed papers (ICML 2024, NeurIPS 2021). Not synthetic.

**Loading Information** (for Phase 4 download):
- Method: programmatic-api + manual extraction (same as h-m1 + robustness extension)
- Identifier: `TrustLLM/TrustLLM-dataset` robustness split + paper tables
- Code:
  ```python
  # Option A: TrustLLM robustness section (same toolkit as h-m1)
  from trustllm.dataset_download import download_dataset
  download_dataset(save_path='./data/TrustLLM')
  # Load robustness scores JSON from ./data/TrustLLM/robustness/

  # Option B: Extend h-m1 DataFrame with robustness columns
  import pandas as pd
  df_base = pd.read_csv('./data/trustllm_scores_hm1.csv')
  # Add: glue_score, advglue_score, anli_r1_score, anli_r3_score
  df = pd.read_csv('./data/trustllm_scores_hm2.csv')
  # Columns: model_name, bbq_disambig, bbq_ambig, mmlu,
  #          glue_score, advglue_score, anli_r1_score, anli_r3_score
  ```

### Models

#### Baseline Model

**This is a statistical meta-analysis — no neural network training.**

**"Baseline" = Raw Δρ without MMLU control (unadjusted comparison)**
- Computes raw Spearman ρ for each benchmark pair without partialling out MMLU
- Raw Δρ = ρ_fairness_raw − mean(ρ_AdvGLUE_raw, ρ_ANLI_raw)
- Expected: raw Δρ may differ from partial Δρ if MMLU confounds differently across dimensions

```python
from scipy.stats import spearmanr

# Baseline: raw ρ per dimension (no MMLU control)
rho_fair_raw, _ = spearmanr(df['bbq_disambig'], df['bbq_ambig'])
rho_advglue_raw, _ = spearmanr(df['glue_score'], df['advglue_score'])
rho_anli_raw, _ = spearmanr(df['anli_r1_score'], df['anli_r3_score'])
delta_rho_raw = rho_fair_raw - np.mean([rho_advglue_raw, rho_anli_raw])
```

#### Proposed Model

**Architecture:** Multi-dimension partial Spearman ρ comparison (MMLU-controlled) via pingouin + Fisher z-test for difference

**Core Mechanism: Differential Predictive Validity Test**

```python
# Core Mechanism: Compare partial Spearman ρ across trustworthiness dimensions
# Based on: pingouin.partial_corr + psinger/CorrelationStats independent_corr
# Reference: https://github.com/psinger/CorrelationStats + pingouin-stats.org

import pandas as pd
import numpy as np
import pingouin as pg
from scipy.stats import norm

def compute_delta_rho(df: pd.DataFrame) -> dict:
    """
    Args:
        df: DataFrame with columns [bbq_disambig, bbq_ambig, glue_score,
            advglue_score, anli_r1_score, anli_r3_score, mmlu, model_name]
            N rows = N_common overlapping LLMs
    Returns:
        dict with delta_rho, z_stat, p_value, and per-dimension results
    """
    # Step 1: Partial Spearman ρ_fairness (MMLU-controlled) — reuse from h-m1
    res_fair = pg.partial_corr(data=df, x='bbq_disambig', y='bbq_ambig',
                               covar=['mmlu'], method='spearman',
                               alternative='two-sided')
    rho_fair = res_fair['r'].values[0]
    n_fair   = res_fair['n'].values[0]

    # Step 2: Partial Spearman ρ_AdvGLUE (MMLU-controlled)
    res_adv = pg.partial_corr(data=df, x='glue_score', y='advglue_score',
                              covar=['mmlu'], method='spearman',
                              alternative='two-sided')
    rho_adv = res_adv['r'].values[0]

    # Step 3: Partial Spearman ρ_ANLI (MMLU-controlled)
    res_anli = pg.partial_corr(data=df, x='anli_r1_score', y='anli_r3_score',
                               covar=['mmlu'], method='spearman',
                               alternative='two-sided')
    rho_anli = res_anli['r'].values[0]

    # Step 4: Δρ = ρ_fairness − mean(ρ_AdvGLUE, ρ_ANLI)
    rho_robust_mean = np.mean([rho_adv, rho_anli])
    delta_rho = rho_fair - rho_robust_mean

    # Step 5: Fisher z-test for difference (ρ_fairness vs ρ_robust_mean)
    # Using psinger/CorrelationStats independent_corr formula
    # Note: using mean ρ_robust requires combined n; approximate with n_fair
    z_fair = 0.5 * np.log((1 + rho_fair) / (1 - rho_fair))
    z_rob  = 0.5 * np.log((1 + rho_robust_mean) / (1 - rho_robust_mean))
    se_diff = np.sqrt(2 / (n_fair - 3))  # same N for all pairs
    z_stat  = (z_fair - z_rob) / se_diff
    p_val   = 2 * (1 - norm.cdf(abs(z_stat)))  # two-tailed (exploratory)

    return {
        'rho_fairness': rho_fair,
        'rho_advglue': rho_adv,
        'rho_anli': rho_anli,
        'rho_robust_mean': rho_robust_mean,
        'delta_rho': delta_rho,
        'z_stat': z_stat,
        'p_value': p_val,
        'gate_directional': delta_rho >= 0.2,
        'n': n_fair
    }
```

### Training Protocol

**This is a statistical analysis — no neural network training.**

**Analysis Protocol (reusing h-m1 infrastructure, extending to robustness dimensions):**

| Step | Operation | Library | Details |
|------|-----------|---------|---------|
| 1 | Load h-m1 DataFrame | pandas | bbq_disambig, bbq_ambig, mmlu, model_name |
| 2 | Extend with robustness scores | pandas | Add glue_score, advglue_score, anli_r1_score, anli_r3_score |
| 3 | Inner join → N_common_robust | pandas | Models with all 7 scores; document any reduction from h-m1 N |
| 4 | Raw Δρ (baseline) | scipy.stats.spearmanr | Unadjusted comparison per dimension |
| 5 | Partial ρ_fairness | pingouin.partial_corr | Recompute on N_common_robust subset (may differ slightly from h-m1) |
| 6 | Partial ρ_AdvGLUE | pingouin.partial_corr | GLUE→AdvGLUE, MMLU-controlled, two-sided |
| 7 | Partial ρ_ANLI | pingouin.partial_corr | ANLI-R1→ANLI-R3, MMLU-controlled, two-sided |
| 8 | Δρ computation | numpy | ρ_fair − mean(ρ_adv, ρ_anli) |
| 9 | Fisher z-test (difference) | scipy.stats.norm | independent_corr formula, two-tailed, exploratory |
| 10 | Sensitivity analysis | pingouin.partial_corr | Replace MMLU with Winogrande; recompute all ρ and Δρ |
| 11 | Visualization | matplotlib/seaborn | Bar chart: ρ per dimension; scatter plots per pair |

**Seeds:** 1 (fixed — deterministic statistical computation)
**Compute:** Minimal — N ≤ 20 data points, pure pandas/scipy/pingouin. Runs in < 5 seconds on any CPU.

**Data Extraction Protocol (robustness extension):**
1. From TrustLLM robustness JSON or paper tables: extract `robustness/ood/knowledge` scores (GLUE-based tasks) per model
2. Extract ANLI-R1 and ANLI-R3 accuracy per model from TrustLLM robustness section
3. If TrustLLM does not report GLUE vs AdvGLUE separately, supplement from OOD_NLP (Yuan et al.) or AdvGLUE leaderboard
4. Document all substitutions in data provenance notes

### Evaluation

**Primary Metric:** Δρ = partial ρ_fairness − mean(partial ρ_AdvGLUE, partial ρ_ANLI)
- All partial correlations MMLU-controlled via pingouin.partial_corr, method='spearman'
- Gate threshold: Δρ ≥ 0.2 (directional, exploratory)

**Secondary Metrics:**
- Individual comparisons: ρ_AdvGLUE < ρ_fairness AND ρ_ANLI < ρ_fairness (both must hold for full support)
- Fisher z-test p-value for Δρ significance (two-tailed, exploratory; H-M2 is labeled EXPLORATORY in all outputs — not confirmatory)
- Raw Δρ (unadjusted, as baseline comparison)

**Sensitivity Check:**
- Repeat with Winogrande as capability proxy instead of MMLU
- Δρ_Winogrande ≈ Δρ_MMLU → result robust to capability control choice

**Success Criteria:**
- PRIMARY (SHOULD_WORK gate): Δρ ≥ 0.2
- SECONDARY: Both ρ_AdvGLUE < ρ_fairness AND ρ_ANLI < ρ_fairness individually
- TERTIARY: Fisher z p < 0.10 (lenient threshold for exploratory comparison at small N)

**Expected Performance Ranges (from research findings):**
- From H-M1 (VALIDATED): partial ρ_fairness ∈ (0.4, 0.75) estimated
- From AdvGLUE paper: all LLMs score far below benign GLUE accuracy; substantial rank disruption expected → ρ_AdvGLUE expected low (0.0–0.3)
- From ANLI design (3 rounds of increasing difficulty): R1 to R3 rank disruption designed into benchmark → ρ_ANLI expected low-to-moderate (0.1–0.4)
- Expected Δρ ≈ 0.2–0.5 (directional support plausible given adversarial design philosophy)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical rank correlation comparison
- Library: pingouin + scipy.stats + numpy + psinger/CorrelationStats (or inline implementation)
- Code:
  ```python
  pip install pingouin scipy numpy pandas matplotlib seaborn
  # corrstats.py: copy independent_corr function inline (no package install needed)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing partial ρ across three dimensions (fairness, AdvGLUE, ANLI) with MMLU-controlled values; annotate Δρ value and directional threshold (0.2)

#### Additional Figures (LLM Autonomous)
Based on the statistical comparison nature of H-M2, recommend:
1. **Heatmap**: Model × benchmark pair rank matrix (rows = models sorted by MMLU; columns = 6 benchmarks) — visualizes how rank ordering changes across dimensions
2. **Scatter plots (3 panels)**: Per-dimension ID score vs OOD score with Spearman ρ annotated (BBQ pair, GLUE→AdvGLUE pair, ANLI R1→R3 pair)
3. **Forest plot**: Partial ρ per dimension with 95% CI from pingouin; Δρ point estimate with CI

**Output Location:** `docs/youra_research/h-m2/figures/`

---

## 🔬 Mechanism Verification Protocol

**Pre-conditions:**
- `mechanism_exists`: All 7 score columns present in DataFrame with N_common_robust ≥ 8
- `mechanism_isolatable`: ρ_fairness, ρ_AdvGLUE, ρ_ANLI computed independently; Δρ = difference between them
- `baseline_measurable`: Raw Δρ (unadjusted) provides comparison for partial Δρ

**Architecture Compatibility:**
- No neural architecture involved — pure statistical computation
- pingouin.partial_corr confirmed compatible with N ≥ 8 (n - 3 = 5 DOF minimum)
- Fisher z-test for difference requires both |ρ| < 0.99 (satisfied for empirical correlations)

**Activation Indicators:**
- `mechanism_log_message`: "H-M2 analysis: Δρ = {delta_rho:.3f} (threshold: 0.2), direction: {'PASS' if delta_rho >= 0.2 else 'FAIL'}"
- `tensor_shape_change`: N/A (no tensors); DataFrame shape: (N_common_robust, 8) columns
- `metric_delta_expected`: Δρ ≥ 0.2 (ρ_fairness visibly higher than adversarial robustness ρ values)

**Failure Detection:**
- If N_common_robust < 8: log "INSUFFICIENT DATA — cannot compute partial correlation (need N ≥ 8 for 3-variable partial corr with 1 covariate)"
- If |ρ| > 0.999 for any pair: log "CORRELATION NEAR ±1 — Fisher z undefined; fallback to Kendall τ"
- If TrustLLM does not report GLUE/AdvGLUE per-model: log "DATA GAP — supplementing from external sources; document in provenance"

**Mechanism Verification Code:**
```python
# Verification check at analysis start
assert len(df) >= 8, f"N={len(df)} too small for partial correlation (need ≥8)"
required_cols = ['bbq_disambig','bbq_ambig','glue_score','advglue_score',
                 'anli_r1_score','anli_r3_score','mmlu']
missing = [c for c in required_cols if c not in df.columns]
assert not missing, f"Missing columns: {missing}"
for col in required_cols[:-1]:  # skip mmlu
    assert df[col].nunique() > 3, f"Insufficient variance in {col}"
print(f"✅ H-M2 verification: N={len(df)}, all columns present, variance OK")
```

**Hypothesis Support Threshold:** Δρ ≥ 0.2 (primary SHOULD_WORK gate)
**Hypothesis Support Metric:** `results['gate_directional']` = True

---

## 🔬 PoC Success Check

**PoC Pass Condition (SHOULD_WORK — exploratory):**
1. Code runs without error
2. `delta_rho >= 0.2` (ρ_fairness exceeds mean adversarial robustness ρ by ≥ 0.2)

**Note:** SHOULD_WORK failure does not stop pipeline. If Δρ < 0.2, document as limitation ("dimension asymmetry not detected at this threshold") and proceed to H-M3 — H-M1 result (fairness stability) remains valid regardless.

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Assessment:** Archon KB contains diffusion model / image generation content exclusively. No domain-relevant prior cases for LLM evaluation statistics found across 3 knowledge base queries and 1 code example query (max similarity 0.45). All methodology grounded in Exa searches below.

**Traceability note:** Archon searches executed per workflow protocol; negative result documented for reproducibility.

---

### B. GitHub Implementations (Exa)

**Repository 1:** psinger/CorrelationStats
- **URL:** https://github.com/psinger/CorrelationStats/blob/master/corrstats.py
- **Query Used:** "Fisher z-test difference two independent correlations Python implementation scipy numpy"
- **Relevance:** Primary implementation of Fisher z-test for comparing two independent correlations — the core statistical test for H-M2's Δρ significance assessment
- **Key Code (annotated):**
  ```python
  def independent_corr(xy, ab, n, n2=None, twotailed=True, method='fisher'):
      # xy = ρ_fairness, ab = ρ_robust_mean, n = N_common_robust
      xy_z = 0.5 * np.log((1 + xy) / (1 - xy))  # Fisher z of ρ_fairness
      ab_z = 0.5 * np.log((1 + ab) / (1 - ab))  # Fisher z of ρ_robust_mean
      se_diff = np.sqrt(1/(n-3) + 1/(n2-3))       # SE of difference
      z = abs((xy_z - ab_z) / se_diff)
      p = (1 - norm.cdf(z)) * (2 if twotailed else 1)
      return z, p
  # Used as basis for: Step 5 (Fisher z-test) in core mechanism pseudocode
  ```
- **Used For:** Core comparison test (Δρ significance); integrated into `compute_delta_rho()` function

**Repository 2:** AI-secure/adversarial-glue
- **URL:** https://github.com/ai-secure/adversarial-glue
- **Query Used:** "GLUE AdvGLUE ANLI robustness LLM rank correlation evaluation scores comparison"
- **Relevance:** Official AdvGLUE dataset (NeurIPS 2021 Oral) — provides per-model GLUE and AdvGLUE scores for the benchmark pair used in H-M2's ρ_AdvGLUE computation
- **Key empirical data:** All tested LLMs score far below benign GLUE accuracy on AdvGLUE; SMART (BERT) improved on GLUE but worst on AdvGLUE — supports rank disruption hypothesis
- **Configuration Extracted:** AdvGLUE aggregate score = macro-average across SST-2, QQP, MNLI, QNLI, RTE tasks
- **Used For:** Dataset specification (GLUE→AdvGLUE pair) and expected performance range estimation

**Repository 3:** arXiv 2412.10535 (LLM adversarial + OOD robustness correlation study)
- **URL:** https://doi.org/10.48550/arxiv.2412.10535
- **Query Used:** "GLUE AdvGLUE ANLI robustness LLM rank correlation evaluation scores comparison"
- **Relevance:** Directly studies adversarial robustness vs OOD robustness correlation across LLMs — the closest prior work to H-M2
- **Key Finding:** Negative correlation between adversarial and OOD robustness in LLaMA2:13B; result "strongly influenced by limited number of benchmarks" — validates H-M2's small-N awareness
- **Used For:** Expected performance range for ρ_robustness (lower than ρ_fairness expected based on adversarial design)

**Repository 4:** TrustLLM (HowieHwong/TrustLLM)
- **URL:** https://github.com/HowieHwong/TrustLLM
- **Query Used:** Web search — "TrustLLM benchmark GLUE AdvGLUE ANLI LLM scores robustness evaluation table 2024"
- **Relevance:** Primary data source — same 16 LLMs evaluated on robustness dimension (GLUE/AdvGLUE/ANLI tasks) alongside fairness. Leaderboard: https://trustllmbenchmark.github.io/TrustLLM-Website/leaderboard.html
- **Used For:** Dataset specification; per-model GLUE, AdvGLUE, ANLI-R1, ANLI-R3 score extraction

---

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results was sufficiently clear. H-M2 is a pure statistical analysis (partial Spearman ρ comparison on tabular model × benchmark score matrix). No complex neural architecture to analyze.

---

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — h-m1 (VALIDATED)
- **Reused Components:**
  - Dataset: TrustLLM multi-model scores — proven real, non-synthetic, accessible via GitHub/HuggingFace
  - DataFrame structure: `model_name, bbq_disambig, bbq_ambig, mmlu` — extended with 4 robustness columns
  - Methodology: pingouin.partial_corr, method='spearman' — validated in h-m1
  - Sensitivity analysis: Winogrande as MMLU substitute — carried forward
- **Why Reused:** Enables controlled comparison — same model set, same MMLU control, same pingouin implementation; only the benchmark pair (and resulting Δρ computation) changes

---

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (BBQ pair) | Previous hypothesis | h-m1 validated dataset |
| Dataset (GLUE→AdvGLUE) | GitHub | Repository B.2 (ai-secure/adversarial-glue) |
| Dataset (ANLI R1→R3) | Paper | TrustLLM robustness section (arXiv 2401.05561) |
| Partial ρ methodology | Previous hypothesis | h-m1 (pingouin.partial_corr) |
| Fisher z-test (difference) | GitHub | Repository B.1 (psinger/CorrelationStats) |
| Δρ expected range | Paper + GitHub | B.3 (arXiv 2412.10535) + AdvGLUE paper |
| Training protocol | Previous hypothesis | h-m1 analysis protocol |
| Evaluation metrics | Phase 2B | 02b_verification_plan.md §2.2 H-M2 |
| Visualization requirements | Domain standard | matplotlib/seaborn bar + scatter + forest |

---

## State Information

**State File:** verification_state.yaml (ABLATION OVERRIDE — restated in state block)
**Date:** 2026-08-20

### Workflow History for This Hypothesis
- 2026-08-20: h-m2 set to IN_PROGRESS (external hypothesis loop)
- 2026-08-20: Phase 2C executed (UNATTENDED batch mode)
- 2026-08-20: experiment_design.status → COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant results), Exa (GitHub + Web — primary source), Serena (skipped — no complex code)*
*All specifications grounded in researched implementations and continuation from h-m1*
*Next Phase: Phase 3 - Implementation Planning*
