# Experiment Design: H-M3

**Date:** 2026-08-20
**Author:** Anonymous
**Hypothesis Statement:** Under a panel OLS regression of benchmark scores on cumulative domain exposure fractions (22 domains × 154 checkpoints × 16 model sizes = 2,464 observations) with model-size fixed effects, domain coefficients are benchmark-specific: β_Wikipedia > β_Books for MMLU (p < 0.05, one-tailed) and β_Books > β_Wikipedia for HellaSwag (p < 0.05), with LRT rejecting the shared-β model (FDR q < 0.05 for ≥2 benchmark pairs).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** — Primary quantitative test: panel regression coefficient benchmark-specificity.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 (MUST_WORK, PASSED), H-M1 (MUST_WORK, PASSED), H-M2 (SHOULD_WORK, GATE_FAIL — documented limitation, proceed)
**Gate Status:** SHOULD_WORK — proceed with warning. H-M2 GATE_FAIL due to Books3 zero-variance in 600k-doc H-E1 sample and preliminary P1 direction reversal. H-M3 panel framework uses full 2,464-observation panel (all checkpoints × all model sizes) and is statistically more powerful than pairwise Spearman.

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM — Step 3 of 3 (Primary Quantitative Test)
- **Prerequisites:** H-E1 (PASSED), H-M1 (PASSED), H-M2 (GATE_FAIL / SHOULD_WORK — limitation documented)

### Gate Condition
SHOULD_WORK:
- P1: β_Wikipedia > β_Books for MMLU (p < 0.05, one-tailed)
- P2: β_Books > β_Wikipedia for HellaSwag (p < 0.05, one-tailed)
- P3: LRT rejects shared-β model (FDR q < 0.05 for ≥2 of 6 pairwise benchmark comparisons)

---

## Continuation Context

H-M3 is the culminating test of the domain-exposure → benchmark-specificity causal chain established by H-E1 and H-M1. Key lessons from prior hypotheses:

1. **H-E1 data gap:** The 600k-doc sample used for H-M2 had Books3 zero-variance. H-M3 must use the **full H-E1 output** (all 154 checkpoints × all 16 model sizes), not the subsampled version.
2. **Collinearity risk:** 22 domain exposure fractions sum to 1 (perfect multicollinearity). Must drop one domain (intercept absorbed) or apply PCA if VIF > 10 for any domain.
3. **Temporal autocorrelation:** Cumulative exposure trajectories are highly autocorrelated. Cluster standard errors by model size.
4. **H-M2 directional reversal for 70m:** Preliminary result (N=10) showed ρ(Wikipedia→MMLU) negative. Full panel may differ — this is the test.

### Previous Hypothesis Results
- H-E1: PASSED — ≥10 domains show std(cumulative_exposure_fraction) > 0.001 across 154 checkpoints in ≥8 model sizes. Domain exposure trajectories are measurable.
- H-M1: PASSED — Wikipedia entity density > Books entity density (p < 0.05, η² > 0.1). Cognitive content differences confirmed.
- H-M2: GATE_FAIL (SHOULD_WORK) — P2 untestable (Books3 zero-variance); P1 preliminary failure (70m, N=10). Full eval cache on 5×H100 NVL still running; H-M3 proceeds in parallel.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Assessment:** Archon KB is populated with diffusion model content (HuggingFace diffusers, SDXL, etc.) with no overlap with LLM training analysis or panel econometrics. All query similarity scores were low (0.28–0.47). No relevant findings extracted.

**Queries executed:**
1. "panel regression domain exposure benchmark specificity LLM" → diffusion model results (similarity 0.36)
2. "fixed effects OLS regression panel data implementation challenges" → diffusion model results (similarity 0.35)
3. "Pythia checkpoint benchmark evaluation training dynamics" → train_unconditional.py diffusion results (similarity 0.47)

**Conclusion:** Archon provides no prior implementation cases for this domain. All specifications grounded in Exa/GitHub sources and domain expertise.

### Archon Code Examples

**Assessment:** Code search returned diffusion scheduler and LoRA code with no relevance (similarity 0.28–0.30). No code examples extracted.

**Queries executed:**
1. "panel OLS regression fixed effects statsmodels linearmodels" → diffusion schedulers (similarity 0.28)

### Exa GitHub Implementations

**Query 1: Panel OLS Fixed Effects — linearmodels library**

**Repository 1:** bashtage/linearmodels (⭐ 1,036)
- **URL:** https://github.com/bashtage/linearmodels
- **Relevance:** Primary library for panel data fixed effects regression in Python. Supports entity effects (model-size fixed effects), clustered standard errors by entity, two-way effects.
- **Key Code:**
  ```python
  from linearmodels.panel import PanelOLS
  import statsmodels.api as sm

  # MultiIndex: (entity=model_size, time=checkpoint)
  data = data.set_index(['model_size', 'checkpoint'])

  # Entity fixed effects + clustered SEs by entity
  mod = PanelOLS.from_formula(
      'benchmark_score ~ domain_1 + domain_2 + ... + EntityEffects',
      data
  )
  res = mod.fit(cov_type='clustered', cluster_entity=True)
  print(res.summary)
  ```
- **Key Config:**
  - `entity_effects=True` → model-size fixed effects (eliminates time-invariant scale confounds)
  - `cov_type='clustered', cluster_entity=True` → clustered SEs by model size (handles temporal autocorrelation within model)
  - Time-invariant variables (log(params)) cannot be included when using entity effects — encode as entity dummies pre-demeaning OR use log(params) as between-variation only
- **Used For:** Core panel regression implementation (Steps P1, P2, P3)

**Repository 2:** vincent.codes.finance — Panel OLS Standard Errors Tutorial
- **URL:** https://vincent.codes.finance/posts/panel-ols-standard-errors/index.html
- **Relevance:** Explains when to use `cluster_entity` vs `cluster_time` vs both; warns against using `robust` covariance with entity effects.
- **Key insight:** For our design (large T=154, small N=16), cluster by entity (model size) — this is the autocorrelation source. Do not cluster by time.

**Query 2: lm-evaluation-harness for Pythia checkpoint evaluation**

**Repository 3:** EleutherAI/lm-evaluation-harness (official)
- **URL:** https://github.com/EleutherAI/lm-evaluation-harness
- **Relevance:** Official evaluation tool. Supports Pythia checkpoints via `revision=stepXXX` HuggingFace flag. Covers all 4 target benchmarks.
- **Key Code:**
  ```bash
  # Evaluate single Pythia checkpoint on all target benchmarks
  lm_eval --model hf \
      --model_args pretrained=EleutherAI/pythia-1b,revision=step10000,dtype="float" \
      --tasks mmlu,hellaswag,arc_challenge,winogrande \
      --device cuda:0 \
      --batch_size auto \
      --output_path ./evals/pythia-1b/step10000/
  ```
- **Key Config:**
  - `revision=stepXXXX` selects checkpoint (steps: 1,2,4,8,16,32,64,128,256,512,1000, then every 1000 to 143000)
  - MMLU: `num_fewshot=5`; HellaSwag: `num_fewshot=10`; ARC-Challenge: `num_fewshot=25`; WinoGrande: `num_fewshot=5`
  - `--output_path` saves JSON results for post-processing
  - `--log_samples` saves per-sample outputs for decontamination

**Repository 4:** EleutherAI/pythia (official README)
- **URL:** https://github.com/EleutherAI/pythia
- **Relevance:** Documents all 154 checkpoint steps, benchmark scores available at `evals/pythia-v1/*/*`, dataloader reconstruction script for domain exposure computation.
- **Key insight:** Existing benchmark evals (`evals/` directory) may cover some of the 154 checkpoints — check before rerunning. Dataloader indices available for exposure computation.

**Query 3: VIF diagnostics and LRT**

**Source 5:** statsmodels `variance_inflation_factor`
- **URL:** https://www.statsmodels.org/stable/generated/statsmodels.stats.outliers_influence.variance_inflation_factor.html
- **Code:**
  ```python
  from statsmodels.stats.outliers_influence import variance_inflation_factor
  vif_data = pd.DataFrame()
  vif_data["domain"] = domain_cols
  vif_data["VIF"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
  # Apply PCA if any VIF > 10
  ```

**Source 6:** statsmodels `OLSResults.compare_lr_test`
- **URL:** https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.OLSResults.compare_lr_test.html
- **Code:** `lr_stat, p_value, df_diff = unrestricted_res.compare_lr_test(restricted_res)`
- **Used For:** P3 — LRT rejecting shared-β model vs benchmark-specific-β model

**Serena Analysis Needed:** No — this is a statistical analysis pipeline, not a neural architecture. All code patterns are clear from Exa/GitHub sources.

### 🎯 Implementation Priority Assessment

This is not a paper reproduction experiment — it is an original statistical analysis using EleutherAI's publicly available infrastructure. No single "author implementation" exists.

**Recommended Implementation Path:**
- Primary: linearmodels `PanelOLS` (bashtage/linearmodels v7.0) for panel regression; EleutherAI/lm-evaluation-harness for benchmark evaluation; Pythia dataloader reconstruction for domain exposure
- Fallback: statsmodels OLS with model-size dummies if linearmodels entity_effects creates collinearity issues with log(params) covariate
- Justification: linearmodels is the standard Python library for panel fixed-effects models, directly equivalent to Stata's `xtreg, fe`. The Pythia ecosystem (lm-eval-harness + dataloader scripts) is the only real-data source for domain exposure trajectories.

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. This is a statistical analysis pipeline using standard econometric and evaluation libraries, not a complex neural architecture requiring semantic code analysis.

---

## Experiment Specification

### Dataset

**Primary Dataset:** Pythia Panel Dataset (constructed from existing infrastructure)

This is not a downloadable dataset — it is a panel constructed by combining three data sources:

| Component | Source | Description |
|-----------|--------|-------------|
| Domain exposure trajectories | EleutherAI/pythia dataloader reconstruction | cumulative_domain_fraction[d, model_i, t] for 22 domains × 16 model sizes × 154 checkpoints |
| Benchmark scores | EleutherAI/lm-evaluation-harness + existing pythia evals | score[benchmark, model_i, t] for MMLU, HellaSwag, ARC-Challenge, WinoGrande |
| Model metadata | Pythia paper / HuggingFace model cards | log(params) for 16 model sizes |

**Panel structure:**
- Entities (N): 16 model sizes (70M, 160M, 410M, 1B, 1.4B, 2.8B, 6.9B, 12B + deduped variants)
- Time periods (T): 154 checkpoints per model (steps: 0,1,2,4,8,16,32,64,128,256,512,1000–143000)
- Total observations: 2,464 (16 × 154) per benchmark × 4 benchmarks = 9,856 regression observations total
- Covariates: 22 cumulative domain exposure fractions (sum-constrained → drop 1), model-size fixed effects

**Preprocessing steps:**
1. Reconstruct domain exposure: use Pythia's `indices/` files + pile_metadata to compute cumulative_domain_fraction[d,t] per model. Full H-E1 output (not 600k-doc sample).
2. Apply 13-gram decontamination to benchmark scores (filter contaminated test examples).
3. Filter checkpoints with floor scores (all-benchmark score < 30%) — typically steps 0–512 for small models.
4. Verify ≥100 usable checkpoints per model size remain.
5. VIF check: drop one domain (least informative) to break sum constraint; apply PCA if any VIF > 10.
6. Construct MultiIndex DataFrame (model_size, checkpoint) for linearmodels.

**Data type:** programmatic-api (real data via EleutherAI HuggingFace APIs + existing eval cache)
**Synthetic data:** NOT used — all data is real Pythia training runs and standard benchmark evaluations.

**Loading Information:**
- Method: HuggingFace Hub (Pythia checkpoints) + lm-evaluation-harness CLI
- Identifier: `EleutherAI/pythia-{size}`, revision `step{n}`; existing evals at `evals/pythia-v1/*/*` in EleutherAI/pythia repo
- Code:
  ```bash
  # Check existing evals first (may cover many checkpoints)
  git clone https://github.com/EleutherAI/pythia
  ls pythia/evals/pythia-v1/

  # For missing checkpoints, run lm-eval-harness
  lm_eval --model hf \
      --model_args pretrained=EleutherAI/pythia-1b,revision=step10000,dtype=float \
      --tasks mmlu,hellaswag,arc_challenge,winogrande \
      --num_fewshot 5 \
      --batch_size auto \
      --output_path ./evals/pythia-1b/step10000/
  ```

### Models

#### Baseline Model

**Architecture:** Panel OLS with model-size fixed effects (entity effects), domain exposure covariates only — NO benchmark-specific β (shared-β null model)

This is a statistical model, not a neural network. "Baseline" = constrained (null) model:

```
score(i, t) = α_i + Σ_d β_d × exposure_d(t) + ε_{i,t}
```

Where:
- `α_i` = model-size fixed effect (absorbed by entity demeaning)
- `β_d` = shared domain coefficient (same for all 4 benchmarks — this is H0)
- `exposure_d(t)` = cumulative fraction of tokens from domain d at checkpoint t
- SEs clustered by model size i

**Loading Information:**
- Method: pip install
- Identifier: `linearmodels>=4.0`, `statsmodels>=0.13`
- Code: `pip install linearmodels statsmodels scipy pandas numpy`

#### Proposed Model

**Architecture:** 4 separate Panel OLS regressions, one per benchmark — benchmark-specific β (alternative model H1)

```
score_b(i, t) = α_{b,i} + Σ_d β_{b,d} × exposure_d(t) + ε_{b,i,t}   ∀b ∈ {MMLU, HellaSwag, ARC-C, WinoGrande}
```

Where β_{b,d} are **benchmark-specific** domain coefficients.

**Core Mechanism Implementation:**

```python
# Panel OLS with Model-Size Fixed Effects — benchmark-specific β
# Based on: linearmodels PanelOLS (bashtage/linearmodels v7.0)
# Source: https://github.com/bashtage/linearmodels

import pandas as pd
import numpy as np
from linearmodels.panel import PanelOLS
from statsmodels.stats.outliers_influence import variance_inflation_factor
from scipy import stats

def fit_panel_per_benchmark(panel_df, domain_cols, benchmarks):
    """
    Args:
        panel_df: MultiIndex (model_size, checkpoint) DataFrame
                  columns: domain_1..domain_22, mmlu, hellaswag, arc_challenge, winogrande
        domain_cols: list of 21 domain columns (1 dropped to break sum constraint)
        benchmarks: list of benchmark column names
    Returns:
        dict: benchmark -> PanelOLS result object
    """
    # Step 1: VIF check — apply PCA if max VIF > 10
    X = panel_df[domain_cols]
    vifs = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
    if max(vifs) > 10:
        from sklearn.decomposition import PCA
        pca = PCA(n_components=0.95)  # retain 95% variance
        X_pca = pca.fit_transform(X)
        domain_cols = [f"PC{i}" for i in range(X_pca.shape[1])]
        panel_df[domain_cols] = X_pca

    results = {}
    for benchmark in benchmarks:
        # Step 2: Fit per-benchmark panel OLS with entity fixed effects
        formula = f"{benchmark} ~ " + " + ".join(domain_cols) + " + EntityEffects"
        mod = PanelOLS.from_formula(formula, panel_df)
        # Cluster SEs by model_size (entity) to handle within-model autocorrelation
        res = mod.fit(cov_type='clustered', cluster_entity=True)
        results[benchmark] = res

    return results

def test_p1_p2(results):
    """Test P1: β_Wikipedia > β_Books for MMLU; P2: β_Books > β_Wikipedia for HellaSwag"""
    mmlu_res = results['mmlu']
    hs_res   = results['hellaswag']

    beta_wiki_mmlu  = mmlu_res.params['Wikipedia']
    beta_books_mmlu = mmlu_res.params['Books3']   # or PCA component if VIF triggered
    beta_wiki_hs    = hs_res.params['Wikipedia']
    beta_books_hs   = hs_res.params['Books3']

    # One-tailed t-tests (P1: wiki > books for MMLU)
    # Use Fisher z-test on the coefficient difference / pooled SE
    return {
        'P1_direction': beta_wiki_mmlu > beta_books_mmlu,
        'P2_direction': beta_books_hs > beta_wiki_hs,
    }
```

### Training Protocol

Not applicable — this is a statistical analysis pipeline, not model training. The "training protocol" is the analysis pipeline:

**Analysis Pipeline:**

| Step | Description | Tool | Est. Runtime |
|------|-------------|------|-------------|
| 1 | Reconstruct domain exposure trajectories from Pythia dataloader indices | Python + HuggingFace | 2–4h (one-time) |
| 2 | Check existing eval cache at EleutherAI/pythia `evals/` directory | git/API | 30min |
| 3 | Run missing benchmark evaluations via lm-eval-harness | lm_eval CLI, GPU | 48–120h (5×H100 NVL) |
| 4 | Apply 13-gram decontamination to benchmark scores | custom script | 1h |
| 5 | Filter floor checkpoints (all-benchmark < 30%) | pandas | <1min |
| 6 | VIF diagnostics; apply PCA if needed | statsmodels + sklearn | <1min |
| 7 | Construct MultiIndex panel DataFrame | pandas | <1min |
| 8 | Fit 4× PanelOLS (one per benchmark, entity effects, clustered SEs) | linearmodels | <5min |
| 9 | Test P1 and P2 (one-tailed coefficient comparisons) | scipy | <1min |
| 10 | LRT: fit shared-β pooled model vs 4 benchmark-specific models | statsmodels | <5min |
| 11 | FDR correction on 6 pairwise LRT p-values | statsmodels `multipletests` | <1min |
| 12 | Robustness: within-scale subgroup regressions (70M–400M vs 1B–12B) | linearmodels | <5min |
| 13 | Permutation null (1000 domain label shuffles) | numpy | 1–2h |
| 14 | R² decomposition: domain-only vs scale-only model | linearmodels | <5min |

**Seeds:** Fixed numpy seed = 42 for permutation null.

**Key hyperparameters (benchmark evaluation):**
- MMLU: `num_fewshot=5` (standard)
- HellaSwag: `num_fewshot=10` (standard)
- ARC-Challenge: `num_fewshot=25` (standard)
- WinoGrande: `num_fewshot=5` (standard)
- Batch size: `auto` (lm-eval-harness auto-detection)
- Dtype: `float` (fp32 for reproducibility)

**Source:** EleutherAI/lm-evaluation-harness README (standard few-shot configs); linearmodels docs (clustering specification)

### Evaluation

**Primary Metrics (Tests P1 and P2 — directional):**

| Test | Metric | Direction | Threshold |
|------|--------|-----------|-----------|
| P1 | β_Wikipedia − β_Books for MMLU | > 0 | p < 0.05, one-tailed |
| P2 | β_Books − β_Wikipedia for HellaSwag | > 0 | p < 0.05, one-tailed |

**Secondary Metrics:**

| Test | Metric | Threshold |
|------|--------|-----------|
| P3 | LRT: shared-β vs benchmark-specific-β | FDR q < 0.05 for ≥2 of 6 pairwise benchmark comparisons |
| P4 | Spearman ρ of domain coefficient rankings: small (70M–400M) vs large (1B–12B) | ρ > 0.7 |

**Success Criteria (PoC MECHANISM):**
- PRIMARY PASS: P1 AND P2 confirmed (both p < 0.05, one-tailed)
- SECONDARY: P3 confirmed (LRT, FDR q < 0.05 for ≥2 pairs)
- MINIMUM PASS: P1 OR P2 confirmed — EXPLORE route (scope refinement)

**Failure Responses:**
- P1/P2 fail but P3 passes: EXPLORE — some benchmark pairs differentiate even if Wikipedia/Books directions don't hold; refine scope
- All tests fail: PIVOT — test without temporal autocorrelation correction; if still null, publishable null finding; route to Phase 0
- VIF > 10 for all domains: Apply PCA — PCA components may not be interpretable as Wikipedia/Books; document as limitation

**Expected baseline performance (from Pythia benchmark scores in EleutherAI/pythia repo):**
- Pythia-70M (step143000): MMLU ~26%, HellaSwag ~33%, ARC-C ~22%, WinoGrande ~51%
- Pythia-1B (step143000): MMLU ~29%, HellaSwag ~47%, ARC-C ~26%, WinoGrande ~53%
- Pythia-6.9B (step143000): MMLU ~35%, HellaSwag ~63%, ARC-C ~34%, WinoGrande ~61%

**Metrics Loading Information:**
- Task Type: Statistical hypothesis testing (not classification/generation)
- Library: `scipy.stats` (t-tests, Fisher z), `statsmodels.stats.multitest` (FDR), `linearmodels.panel` (panel regression)
- Code:
  ```python
  from scipy import stats
  from statsmodels.stats.multitest import multipletests

  # FDR correction on LRT p-values
  reject, pvals_corrected, _, _ = multipletests(lrt_pvals, method='fdr_bh')
  n_significant = sum(reject)  # need ≥2 for P3 pass
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart of β_Wikipedia and β_Books coefficients per benchmark (MMLU, HellaSwag, ARC-C, WinoGrande) with 95% CI error bars

#### Additional Figures (LLM Autonomous)
1. **Domain coefficient heatmap**: 22 domains × 4 benchmarks coefficient matrix (rows = domains, columns = benchmarks, color = β magnitude)
2. **P1/P2 directional scatter**: scatter plot of β_Wikipedia vs β_Books per benchmark, with diagonal line (equal coefficients) — hypothesis predicts MMLU above diagonal, HellaSwag below
3. **R² decomposition bar chart**: domain-only R² vs scale-only R² vs full model R² per benchmark
4. **Permutation null distribution**: histogram of permuted |β_Wikipedia − β_Books| difference vs observed (for P1 and P2 separately)
5. **Within-scale subgroup robustness**: coefficient comparison (small vs large model groups) for Wikipedia and Books

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m3/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (panel construction + regression pipeline completes)
2. P1 confirmed: β_Wikipedia > β_Books for MMLU (p < 0.05, one-tailed)
3. P2 confirmed: β_Books > β_Wikipedia for HellaSwag (p < 0.05, one-tailed)

---

## Mechanism Verification Protocol

**Mechanism exists:** YES — panel OLS with entity fixed effects is a standard estimator; domain exposure covariates are real (from H-E1). Mechanism is "benchmark-specific β coefficients emerge from entity-demeaned panel regression."

**Mechanism isolatable:** YES — each benchmark is regressed separately. β coefficients are directly interpretable as marginal effect of domain exposure fraction on benchmark score, conditional on model-size fixed effects.

**Baseline measurable:** YES — shared-β null model (pooled across benchmarks) is directly estimable and LRT-comparable.

**Architecture compatibility:** N/A (statistical model, not neural architecture). linearmodels PanelOLS handles entity effects via within-transformation (group-wise demeaning), not dummy variables — supports 16-entity panel efficiently.

**Pre-conditions to verify:**
1. ≥100 usable checkpoints per model size after floor filtering
2. VIF < 10 for all domain covariates (or PCA applied and documented)
3. lm-eval-harness scores cover all 154 checkpoints for all 16 model sizes
4. Domain exposure fractions computed from full H-E1 output (not 600k-doc sample)

**Mechanism activation indicators:**
- Log message: `"PanelOLS fit complete for benchmark {b}: N={N}, T={T}, R²_within={r2:.4f}"`
- Coefficient sanity check: at least one domain has |β| > 0.001 (non-trivial effect)
- Clustered SE finite and non-zero for Wikipedia and Books3 coefficients

**Failure detection:**
- If all β_d ≈ 0: domain exposure has no predictive power → within-transformation collapsed variance (possible if exposure trajectories are nearly constant after demeaning). Check: compare domain variance before vs after entity demeaning.
- If Books3 β is NaN: Books3 still zero-variance in full dataset (same as H-M2 issue). Must use full 154-checkpoint × 16-model panel, not subsampled.
- If VIF still > 10 after dropping 1 domain: apply PCA, document that Wikipedia/Books direct interpretation is lost; test on PCA components instead.

**Mechanism verification code:**
```python
# Verify panel has adequate within-variation for entity-demeaned regression
def verify_panel_quality(panel_df, domain_cols):
    stats = {}
    for domain in domain_cols:
        grouped = panel_df[domain].groupby(level='model_size')
        within_var = grouped.transform(lambda x: x - x.mean()).var()
        stats[domain] = within_var.mean()
    low_var = [d for d, v in stats.items() if v < 1e-6]
    if low_var:
        print(f"WARNING: Low within-variation domains: {low_var}")
    return stats

# Verify VIF
def check_vif(panel_df, domain_cols, threshold=10):
    X = panel_df[domain_cols].dropna()
    vifs = [variance_inflation_factor(X.values, i) for i in range(len(domain_cols))]
    high_vif = [(domain_cols[i], vifs[i]) for i in range(len(vifs)) if vifs[i] > threshold]
    return high_vif
```

**Success thresholds:**
- P1 hypothesis support: β_Wikipedia − β_Books > 0 for MMLU AND p < 0.05 (one-tailed)
- P2 hypothesis support: β_Books − β_Wikipedia > 0 for HellaSwag AND p < 0.05 (one-tailed)
- Minimum mechanism evidence: |β_Wikipedia| > 1 SE for at least 1 benchmark

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

No relevant sources found. Archon KB populated with diffusion model content (HuggingFace diffusers ecosystem). All specifications grounded in Exa/GitHub sources.

### B. GitHub Implementations (Exa)

**Repository 1:** bashtage/linearmodels (⭐ 1,036)
- **URL:** https://github.com/bashtage/linearmodels
- **Query Used:** "panel OLS fixed effects Pythia checkpoint domain exposure benchmark score Python statsmodels linearmodels"
- **Relevance:** Primary panel regression library for Python; supports entity fixed effects, clustered SEs, 2-way effects
- **Key Code Used:**
  ```python
  from linearmodels.panel import PanelOLS
  # MultiIndex (entity, time)
  mod = PanelOLS.from_formula('score ~ domain_1 + ... + EntityEffects', data)
  res = mod.fit(cov_type='clustered', cluster_entity=True)
  ```
- **Configuration Extracted:** `entity_effects=True`, `cluster_entity=True` for model-size clustering
- **Used For:** Core pseudo-code, training protocol Steps 8/12/14

**Repository 2:** EleutherAI/lm-evaluation-harness (official)
- **URL:** https://github.com/EleutherAI/lm-evaluation-harness
- **Query Used:** "lm-evaluation-harness Pythia checkpoint batch evaluation MMLU HellaSwag ARC WinoGrande"
- **Relevance:** Official benchmark evaluation tool; supports `revision=stepXXX` for Pythia checkpoint selection
- **Key Code Used:**
  ```bash
  lm_eval --model hf \
      --model_args pretrained=EleutherAI/pythia-1b,revision=step10000,dtype=float \
      --tasks mmlu,hellaswag,arc_challenge,winogrande \
      --num_fewshot 5 --batch_size auto \
      --output_path ./evals/pythia-1b/step10000/
  ```
- **Configuration Extracted:** Standard few-shot configs; `--output_path` for result caching
- **Used For:** Training protocol Steps 2/3, evaluation metrics section

**Repository 3:** EleutherAI/pythia (official README)
- **URL:** https://github.com/EleutherAI/pythia
- **Query Used:** (same as above)
- **Relevance:** Documents 154 checkpoint availability, existing `evals/` cache, dataloader reconstruction for domain exposure
- **Key Insight:** Checkpoint steps: 0,1,2,4,8,16,32,64,128,256,512,1000–143000 (every 1k). Existing evals may cover many checkpoints already.
- **Used For:** Dataset specification (panel structure), training protocol Steps 1/2

### C. Statistical Tool Sources (Exa web search)

**Source 4:** statsmodels `variance_inflation_factor`
- **URL:** https://www.statsmodels.org/stable/generated/statsmodels.stats.outliers_influence.variance_inflation_factor.html
- **Query Used:** "VIF multicollinearity PCA panel regression statsmodels"
- **Used For:** VIF check in mechanism verification code; preprocessing Step 6

**Source 5:** statsmodels `OLSResults.compare_lr_test`
- **URL:** https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.OLSResults.compare_lr_test.html
- **Query Used:** "likelihood ratio test panel OLS benchmark-specific coefficients scipy statsmodels"
- **Used For:** P3 test — LRT of shared-β vs benchmark-specific-β model

**Source 6:** vincent.codes.finance — Panel OLS Standard Errors
- **URL:** https://vincent.codes.finance/posts/panel-ols-standard-errors/index.html
- **Used For:** Covariance specification guidance (cluster by entity only, not time, for large-T small-N panel)

### D. Previous Hypothesis Context

- H-E1 (PASSED): Confirmed domain exposure trajectories measurable. Key output: cumulative_domain_fraction[d, model_i, t] for all 22 domains × 16 model sizes × 154 checkpoints. Full output needed for H-M3 (not 600k-doc subsample used in H-M2).
- H-M1 (PASSED): Confirmed Wikipedia entity density > Books entity density (p<0.05). Establishes theoretical basis for expecting β_Wikipedia > β_Books for knowledge-retrieval benchmarks.
- H-M2 (GATE_FAIL, SHOULD_WORK): Books3 zero-variance in subsample; P1 directional reversal for 70m. Lesson: use full H-E1 panel, not subsample.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Panel dataset structure (N=16, T=154) | Phase 2B / Pythia paper | 02b_verification_plan.md §1.3, Repo B.3 |
| Domain exposure computation method | H-E1 output + Pythia dataloader | Repo B.3 (pythia README) |
| Benchmark evaluation tool + configs | GitHub (lm-eval-harness) | Repo B.2 |
| Panel OLS with entity effects | GitHub (linearmodels) | Repo B.1 |
| Clustered SE specification | Tutorial | Source C.6 (vincent.codes.finance) |
| VIF diagnostics | statsmodels docs | Source C.4 |
| LRT (P3 test) | statsmodels docs | Source C.5 |
| FDR correction | statsmodels `multipletests` | Standard library |
| Expected benchmark scores | Pythia evals cache | Repo B.3 (evals/ directory) |
| Few-shot configs (MMLU 5-shot etc.) | lm-eval-harness README | Repo B.2 |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — restated in state block)
**Date:** 2026-08-20

### Workflow History for This Hypothesis
- 2026-08-20T00:00:00Z: Phase 2C experiment design STARTED for H-M3
- 2026-08-20T00:00:00Z: Phase 2C experiment design COMPLETED for H-M3

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant results), Exa (GitHub + web — 6 sources), Serena (skipped — statistical analysis, not neural architecture)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
