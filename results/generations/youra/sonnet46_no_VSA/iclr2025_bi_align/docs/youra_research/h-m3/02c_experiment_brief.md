# Experiment Design: H-M3

**Date:** 2026-07-30
**Author:** Anonymous
**Hypothesis Statement:** Under the partial Spearman residuals from H-M2, the partial_rho value for TruthfulQA MC2 × BBQ accuracy will be assignable to one of three pre-specified scenarios: (a) |partial_rho| < 0.20 (independent constructs), (b) partial_rho > 0.40 (scale-free coherence), or (c) partial_rho < -0.20 (scale-masked tradeoff), because these three outcomes exhaustively characterize the possible dimensional relationships between factuality and bias in the alignment-specific benchmark space.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (SHOULD_WORK) Template** — Scenario classification with pre-specified exhaustive outcomes. All three scenarios produce publishable findings.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 (VALIDATED), H-M1 (VALIDATED), H-M2 (VALIDATED — required for partial_rho input)
**Gate Status:** SHOULD_WORK — ambiguous CI does not block pipeline

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Gate:** SHOULD_WORK
- **Prerequisites:** H-M2 (partial_rho + BCa CI required)

### Gate Condition

SHOULD_WORK: partial_rho (TruthfulQA×BBQ from H-M2) is assignable to scenario (a), (b), or (c) based on BCa CI bounds. Gate satisfied even if result is "underpowered" — ambiguous CIs are a valid reportable outcome. Gate FAILS only on code execution error.

---

## Continuation Context

H-M3 is a direct downstream analysis of H-M2. All data preparation (fuzzy join, N≥30 verification, BBQ loading) is already completed and cached by H-E1 and H-M1. The H-M2 experiment produces:
- `partial_rho`: partial Spearman ρ(TruthfulQA_MC2, bbq_accuracy | MMLU)
- `ci_partial`: BCa 95% CI for partial_rho (5000 bootstrap samples, clustered by family)
- `raw_rho`: uncontrolled Spearman ρ for comparison
- `ci_raw`: BCa 95% CI for raw_rho
- `N`: sample size after fuzzy join

H-M3 consumes these outputs from `docs/youra_research/h-m2/code/results/h_m2_results.json`.

### Previous Hypothesis Results (H-M2)
- **Validated:** Partial Spearman + Fisher z difference test executed successfully
- **Output consumed:** `partial_rho`, `ci_partial`, `raw_rho`, `ci_raw`, `N` from h_m2_results.json
- **Continuation protocol:** Reuse all H-M2 hyperparameters (N_bootstrap=5000, seed=42, fuzzy threshold=75)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Note:** Archon KB contains primarily diffusion model papers with no relevance to statistical correlation analysis or LLM benchmark studies. No usable findings extracted.

- **Query 1:** "partial Spearman correlation scenario classification confidence interval assignment" → similarity ~0.31 (diffusion model results)
- **Query 2:** "BCa bootstrap confidence interval overlap test statistical power benchmark correlation" → similarity ~0.32 (diffusion model results)
- **Query 3:** "LLM benchmark correlation analysis Fisher z test Spearman" → similarity ~0.31 (diffusion model results)
- **Code Query:** "pingouin partial_corr spearman BCa bootstrap confidence interval" → diffusion pipeline code only

**Assessment:** Archon KB not indexed for statistical methodology or NLP benchmark analysis. Exa GitHub search provides the relevant implementation patterns.

### Archon Code Examples

No relevant code examples found in Archon KB for this statistical analysis task.

### Exa GitHub Implementations

**Query 1: Partial Spearman + BCa Bootstrap CI**

**Repository 1:** raphaelvallat/pingouin (pingouin-stats.org)
- **URL:** https://github.com/raphaelvallat/pingouin
- **Relevance:** Primary library for partial Spearman and BCa bootstrap CIs
- **Key Code:**
  ```python
  # Partial Spearman correlation controlling for MMLU
  result = pg.partial_corr(
      data=df,
      x="TruthfulQA_MC2",
      y="bbq_accuracy",
      covar=["MMLU"],
      method="spearman"
  )
  partial_rho = result["r"].iloc[0]
  # Returns: n, r, CI95, p-val columns

  # BCa bootstrap CI (standalone)
  ci = pg.compute_bootci(
      x=x, y=y,
      func="spearman",
      method="bca",
      paired=True,
      n_boot=5000,
      seed=42,
      return_dist=True
  )
  ```
- **Used For:** Core partial correlation API; BCa bootstrap CI computation
- **Note:** Already verified and used in H-M2 code. H-M3 reuses this exact API.

**Repository 2:** privong/pymccorrelation
- **URL:** https://github.com/privong/pymccorrelation
- **Relevance:** Bootstrap uncertainty estimation for Spearman rank correlation
- **Key Code:**
  ```python
  from pymccorrelation import pymccorrelation
  res = pymccorrelation(data['x'], data['y'],
                        coeff='spearmanr',
                        Nboot=5000)
  # res[0]: percentiles [16%, 50%, 84%]
  # res[1]: p-value percentiles
  ```
- **Used For:** Alternative BCa approach; confirms N_boot=5000 is standard

**Repository 3:** zeroEQpart (CRAN R package — conceptual reference)
- **URL:** https://doi.org/10.32614/cran.package.zeroeqpart
- **Relevance:** BCa bootstrap test for zero-order vs partial correlation equality (implements exactly our Fisher z conceptual test)
- **Key Insight:** Uses `pzcor(x, y, z, method="pearson", test="eq")` with BCa bootstrap; validates our approach of comparing raw_rho to partial_rho using BCa CI overlap
- **Used For:** Conceptual validation of BCa CI overlap as test criterion

**Query 2: LLM Benchmark Correlation Analysis**

**Repository 4:** siyangwu1/Benchmark-Signature-Repository
- **URL:** https://github.com/siyangwu1/Benchmark-Signature-Repository
- **Relevance:** Cross-model LLM benchmark correlation analysis (32 LLMs × 89 benchmarks)
- **Key Insight:** Uses rank-correlation pre-filtering (Thrush method) + stepwise forward selection; validates cross-model Spearman correlation as meaningful
- **Architecture Pattern:** Per-benchmark analysis pipeline with results matrix storage
- **Used For:** Design pattern for benchmark correlation study structure

**Repository 5:** TristanThrush/perplexity-correlations
- **URL:** https://github.com/TristanThrush/perplexity-correlations
- **Relevance:** LLM benchmark error correlation with pretraining data (32 LLMs)
- **Key Insight:** Cross-LLM Spearman correlation is the standard approach for benchmark co-movement analysis
- **Used For:** Validates observational study design (N~30-50 LLMs is statistically appropriate)

**Serena Analysis Needed:** FALSE — Code from H-M2 codebase is fully understood; no complex external code requires semantic analysis.

### 🎯 Implementation Priority Assessment

H-M3 is a pure statistical analysis downstream of H-M2. No new ML model or complex library implementation is required. Implementation priority:

- **Primary:** pingouin.partial_corr + pg.compute_bootci (already validated in H-M2 codebase)
- **Fallback:** scipy.stats.spearmanr + manual BCa bootstrap (implemented in H-M2 _bca_partial_rho_with_dist)
- **Justification:** H-M2 already implements and validates all required statistical primitives. H-M3 adds scenario classification logic on top of existing H-M2 output.

**Recommended Implementation Path:**
- Primary: Load h_m2_results.json → apply scenario assignment logic → Tier 2/3 if data available
- Fallback: Re-run partial_rho from raw CSV if H-M2 results not available
- Justification: Reusing H-M2 validated output eliminates data re-processing overhead and ensures reproducibility

### Code Analysis (Serena MCP)

*Skipped* — Code from search results and H-M2 codebase was sufficiently clear. H-M2's `analyze.py` implements all required statistical primitives (`compute_partial_spearman`, `_bca_partial_rho_with_dist`, `fisher_z_difference_test`, `compute_bca_cis`). H-M3 adds scenario classification and Tier 2/3 analysis on top.

---

## Experiment Specification

### Dataset

**Primary (Tier 1):** H-M2 results file (inherits H-E1 + H-M1 data)
- **Name:** h_m2_results.json (computed output)
- **Type:** programmatic-api (JSON artifact from H-M2)
- **Source:** `docs/youra_research/h-m2/code/results/h_m2_results.json`
- **Content:** partial_rho, ci_partial, raw_rho, ci_raw, N, family_rhos, weighted_rho, outcome
- **Preprocessing:** None — values already computed and validated by H-M2

**Tier 2 (Optional extension):** HarmBench safety data
- **Name:** HarmBench Table 2 (hardcoded, arXiv:2402.04249)
- **Type:** custom (hardcoded from published paper to avoid URL infrastructure failure)
- **Source:** Hardcoded in experiment code from arXiv:2402.04249 Table 2 (33 models)
- **Content:** model_name, harm_rate (attack success rate) per model
- **Preprocessing:** Inner join with Tier 1 dataset on model_name (fuzzy match if needed); require N_harmbench ≥ 20

**Tier 3 (Optional):** RLHF ΔBBQ sign test data
- **Name:** h-m1 base/chat pairs dataset
- **Type:** programmatic-api (inherited from H-M1)
- **Source:** 321 base/chat model pairs (documented in h-m1 validation report)
- **Content:** ΔBBQ = BBQ(chat) − BBQ(base) for 321 pairs
- **Preprocessing:** Sign extraction: sign(ΔBBQ) for each pair

**Loading Information** (for Phase 4 download):
- Method: JSON file load (Tier 1), hardcoded dict (Tier 2), CSV (Tier 3)
- Identifier: `h_m2_results.json`, hardcoded, `h-m1` CSV path
- Code:
  ```python
  import json
  with open("../h-m2/code/results/h_m2_results.json") as f:
      h_m2 = json.load(f)
  partial_rho = h_m2["partial_rho"]
  ci_partial = h_m2["ci_partial"]  # [lo, hi]
  ```

### Models

#### Baseline Model

**Type:** Observational study — no ML model baseline. The "baseline" is the uncontrolled measurement:
- **raw_rho:** Spearman(TruthfulQA_MC2, bbq_accuracy) without MMLU control (from H-M2)
- **ci_raw:** BCa 95% CI for raw_rho (from H-M2)
- **Source:** h_m2_results.json (precomputed by H-M2)

**Loading Information** (for Phase 4 download):
- Method: JSON key extraction from h_m2_results.json
- Identifier: `h_m2["raw_rho"]`, `h_m2["ci_raw"]`
- Code: `raw_rho = h_m2["raw_rho"]`

#### Proposed Model

**Architecture:** Scenario classification on MMLU-controlled partial Spearman (partial_rho from H-M2)

This is not an ML model — it is a deterministic scenario classification function applied to the H-M2 statistical output.

**Core Mechanism Implementation:**

```python
# Core Mechanism: H-M3 Scenario Classification
# Based on: 02b_verification_plan.md Section 2.2 (H-M3 Verification Protocol)
# and BCa CI from H-M2 compute_bca_cis()

def assign_scenario(partial_rho: float, ci_lo: float, ci_hi: float) -> dict:
    """
    Args:
        partial_rho: MMLU-controlled Spearman rho (from H-M2)
        ci_lo, ci_hi: BCa 95% CI bounds (from H-M2)
    Returns:
        scenario: 'a' | 'b' | 'c' | 'ambiguous'
        narrative: publishable description
        is_ambiguous: True if CI overlaps multiple scenario boundaries
    """
    # Pre-specified scenario boundaries (from Phase 2A / 02b_verification_plan.md)
    SCENARIO_A_BOUND = 0.20   # |partial_rho| < 0.20 → independent constructs
    SCENARIO_B_BOUND = 0.40   # partial_rho > 0.40 → scale-free coherence
    SCENARIO_C_BOUND = -0.20  # partial_rho < -0.20 → scale-masked tradeoff

    # Ambiguity check: CI overlaps 0 AND 0.40 simultaneously
    ci_overlaps_zero = (ci_lo < 0) and (ci_hi > 0)
    ci_overlaps_040 = (ci_lo < 0.40) and (ci_hi > 0.40)
    is_ambiguous = ci_overlaps_zero and ci_overlaps_040

    if is_ambiguous:
        return {"scenario": "ambiguous", "is_ambiguous": True,
                "narrative": "underpowered — scenario unresolvable with current N"}

    # Point estimate scenario assignment
    if abs(partial_rho) < SCENARIO_A_BOUND:
        scenario = "a"
        narrative = "Independent constructs: factuality and bias are orthogonal after scale control"
    elif partial_rho > SCENARIO_B_BOUND:
        scenario = "b"
        narrative = "Scale-free coherence: alignment benchmarks co-move beyond scale"
    elif partial_rho < SCENARIO_C_BOUND:
        scenario = "c"
        narrative = "Scale-masked tradeoff: MMLU control reveals hidden negative alignment relationship"
    else:
        scenario = "ambiguous"
        narrative = "underpowered — partial_rho in grey zone (−0.20, +0.40)"

    return {"scenario": scenario, "is_ambiguous": False, "narrative": narrative}


def tier2_analysis(df_tier1: pd.DataFrame, harmbench_data: dict) -> dict:
    """Tier 2: Partial Spearman for HarmBench pairs if N_harmbench >= 20."""
    harmbench_df = pd.DataFrame(harmbench_data)  # {model_name, harm_rate}
    merged = df_tier1.merge(harmbench_df, on="model_name", how="inner")
    N_harm = len(merged)
    if N_harm < 20:
        return {"tier2_status": "SKIPPED", "N_harmbench": N_harm,
                "reason": f"N={N_harm} < 20 — underpowered"}
    # Compute partial Spearman for TruthfulQA×HarmBench and BBQ×HarmBench
    # [Tier 2 analysis follows same pattern as Tier 1]
    return {"tier2_status": "EXECUTED", "N_harmbench": N_harm}
```

### Training Protocol

**Not applicable** — H-M3 is a pure statistical analysis. No model training, optimizer, or learning rate.

**Execution Protocol:**

```
Seed:          42 (consistent with H-M2 for reproducibility)
N_bootstrap:   5000 (from H-M2, not re-run in H-M3 unless Tier 1 re-execution needed)
Data source:   h_m2_results.json (pre-computed)
Runtime:       ~5 seconds (scenario classification is instantaneous; Tier 2 partial_corr ~2s)
```

**Continuation from H-M2:**
- Reuse: `partial_rho`, `ci_partial`, `raw_rho`, `ci_raw`, `N` from H-M2 results
- Rationale: H-M2 validated computation; re-running would be redundant and inconsistent

### Evaluation

**Primary Metric:** Scenario assignment (categorical: a / b / c / ambiguous)

**Success Criteria:**

| Criterion | Threshold | Action |
|-----------|-----------|--------|
| Scenario assigned (non-ambiguous) | scenario ∈ {a, b, c} | GATE PASS |
| Scenario ambiguous | CI overlaps both 0 and 0.40 | Report "underpowered" — SHOULD_WORK still satisfied |
| Code error | Exception raised | GATE FAIL (only true failure mode) |

**Scenario Outcome Mapping:**

| Scenario | partial_rho range | Narrative | Publishable Framing |
|----------|------------------|-----------|---------------------|
| (a) | \|partial_rho\| < 0.20 | Independent constructs | "Multi-dimensional alignment: factuality ⊥ bias after scale control" |
| (b) | partial_rho > 0.40 | Scale-free coherence | "Coherent alignment signal: co-movement is not purely scale-driven" |
| (c) | partial_rho < -0.20 | Scale-masked tradeoff | "Hidden tradeoff: MMLU masks negative factuality-bias relationship" |
| ambiguous | CI spans multiple scenarios | Underpowered | "N insufficient for scenario resolution; report raw CI range" |

**Secondary Metrics (Tier 2):**
- N_harmbench: count of HarmBench models matched to Tier 1 dataset
- scenario_truthfulqa_harmbench: scenario assignment for ρ(TruthfulQA, HarmBench | MMLU)
- scenario_bbq_harmbench: scenario assignment for ρ(BBQ, HarmBench | MMLU)

**Tertiary Metric (Tier 3, optional):**
- binomtest_p: scipy.stats.binomtest p-value for sign(ΔBBQ) > 0 (RLHF effect on BBQ)
- binomtest_direction: "positive" if p < 0.05 AND k/N > 0.5, "negative" if p < 0.05 AND k/N < 0.5

**Expected Baseline Performance** (from research):
- Raw rho(TruthfulQA, BBQ) ≈ +0.3 to +0.6 (based on H-M1 results and historical AlpacaEval-LC rho=+0.661)
- After MMLU control, partial_rho direction is unknown (this is the PROVE_NEW claim)
- clawrxiv:2603.00394: TruthfulQA loads on PC2 (23.4% variance, orthogonal to PC1 scale) → suggests partial_rho may shift toward scenario (a) or (c)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical classification (observational)
- Library: scipy.stats.binomtest (Tier 3), pingouin (Tier 2), numpy/json (Tier 1)
- Code:
  ```python
  from scipy import stats
  # Tier 3 sign test
  k_positive = np.sum(delta_bbq > 0)
  result = stats.binomtest(k=k_positive, n=321, p=0.5, alternative='two-sided')
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** Scenario assignment summary bar/panel

#### Additional Figures (LLM Autonomous)

Based on the hypothesis structure, the following figures are recommended:

1. **Fig1: Scenario Assignment Panel** (MANDATORY)
   - Horizontal number line showing partial_rho point estimate with BCa 95% CI
   - Color-coded scenario boundaries: scenario (a) region grey, (b) green, (c) red
   - Vertical dashed lines at ±0.20 and +0.40 (scenario boundaries)
   - CI band shading to visualize ambiguity
   - Annotation: assigned scenario label + narrative

2. **Fig2: Pairwise Partial Correlation Matrix** (Tier 1 + Tier 2 combined)
   - Heatmap of partial Spearman rho values for all pairs: {TruthfulQA, BBQ, HarmBench} × {TruthfulQA, BBQ, HarmBench}
   - Color scale: -1 (red) to +1 (green), 0 = white
   - Cell annotations: rho value + scenario label (a/b/c/ambiguous)
   - Stars for significance (p < 0.05)

3. **Fig3: Raw vs Partial Comparison with Scenario Annotation** (extends H-M2 Fig1)
   - Bar chart: raw_rho vs partial_rho with BCa CI error bars (reuses H-M2 code)
   - Horizontal scenario boundary lines overlaid
   - Scenario assignment label annotated on the partial_rho bar

4. **Fig4: Tier 3 RLHF ΔBBQ Sign Test** (if executed)
   - Histogram of ΔBBQ values (321 pairs)
   - Vertical dashed line at 0
   - Annotation: k_positive/N, binomtest p-value, direction

**Output Location:** `docs/youra_research/h-m3/figures/`

> Phase 4 Coder MUST include figure generation logic in experiment code.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | H-M2 results file exists with partial_rho and ci_partial | Must verify at runtime |
| Mechanism Isolatable | Scenario classification can be run without re-computing partial_rho | TRUE — JSON load suffices |
| Baseline Measurable | raw_rho available from same H-M2 results file | TRUE — h_m2["raw_rho"] |

### Architecture Compatibility Check

H-M3 requires no ML model architecture. The "mechanism" is the scenario classification function applied to H-M2 statistical output.

**Required:**
- h_m2_results.json must exist and contain keys: `partial_rho`, `ci_partial` (list [lo, hi]), `raw_rho`, `ci_raw`, `N`
- pingouin ≥ 0.5.0 (for Tier 2 re-analysis if needed)
- scipy ≥ 1.8.0 (for binomtest in Tier 3)

**Incompatible:**
- H-M2 gate FAILED (partial_rho not computed) — H-M3 cannot execute. However, since H-M2 is VALIDATED per pipeline state, this is not a current risk.

> ⚠️ If h_m2_results.json missing or malformed, Phase 4 MUST fail with descriptive error before any analysis runs.

### Mechanism Activation Indicators

**How to detect if mechanism is actually working:**

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "Scenario assigned: [a/b/c/ambiguous] for partial_rho=X.XXXX" | analyze.py:assign_scenario() |
| Output Key | results["scenario"] ∈ {"a", "b", "c", "ambiguous"} | main.py |
| Metric Delta | abs(partial_rho - raw_rho) > 0.001 (MMLU control had effect) | inherited from H-M2 |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(results: dict) -> tuple:
    """Verify H-M3 scenario classification mechanism activated correctly."""
    indicators = {
        "h_m2_loaded": results.get("partial_rho") is not None,
        "scenario_assigned": results.get("scenario") in {"a", "b", "c", "ambiguous"},
        "ci_bounds_valid": (
            results.get("ci_partial") is not None
            and len(results.get("ci_partial", [])) == 2
            and results["ci_partial"][0] < results["ci_partial"][1]
        ),
        "narrative_generated": bool(results.get("narrative")),
    }
    all_ok = all(indicators.values())
    return all_ok, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| h_m2_results.json missing | FileNotFoundError at load | FAIL: "H-M2 must complete before H-M3" |
| partial_rho key absent | KeyError on h_m2["partial_rho"] | FAIL: "H-M2 results malformed" |
| scenario = None | Missing assignment in classify() | FAIL: Classification logic error |
| CI bounds [lo > hi] | Assertion error | FAIL: Bootstrap CI malformed |
| Tier 2 N < 20 | N_harmbench < 20 check | SKIP Tier 2 (not a failure) |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Scenario Assigned | scenario ∈ {a, b, c, ambiguous} | Check results["scenario"] |
| CI Computed | ci_partial is [float, float] | Check len and ordering |
| Hypothesis Supported | non-ambiguous scenario assigned | scenario != "ambiguous" |
| SHOULD_WORK | Any scenario (including ambiguous) with no code error | Gate logic |

- **hypothesis_support_threshold:** scenario ∈ {a, b, c} (non-ambiguous)
- **hypothesis_support_metric:** results["scenario"] and results["is_ambiguous"] == False

---

## Ablation Studies

H-M3 is primarily a scenario classification step, but the following ablation variants test robustness:

### Ablation 1: CI Width Sensitivity
- **Variant A:** Use parametric Fisher CI from pingouin (not BCa bootstrap)
- **Variant B:** Use BCa CI from H-M2 (primary, 5000 bootstrap)
- **What it measures:** Whether scenario assignment is CI-method-dependent
- **Expected:** Same scenario assignment regardless of CI method for large N

### Ablation 2: Scenario Boundary Sensitivity
- **Variant A:** Tighter boundaries (|partial_rho| < 0.15 for (a), > 0.35 for (b), < -0.15 for (c))
- **Variant B:** Wider boundaries (|partial_rho| < 0.25 for (a), > 0.45 for (b), < -0.25 for (c))
- **What it measures:** Robustness of scenario label to boundary choice
- **Expected:** Same scenario label if partial_rho is far from boundaries

### Ablation 3: Tier Analysis Comparison
- **Tier 1:** TruthfulQA × BBQ (primary)
- **Tier 2:** TruthfulQA × HarmBench, BBQ × HarmBench (if N_harmbench ≥ 20)
- **What it measures:** Whether safety dimension (HarmBench) shows same dimensional pattern
- **Expected:** May differ — HarmBench captures adversarial safety, not factuality bias

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Archon KB:** No relevant sources found. KB contains primarily diffusion model papers (HuggingFace diffusers ecosystem, IC-Light, AnimateDiff, UniPC). Similarity scores ≤ 0.32 for all statistical correlation queries.
- **Status:** Not applicable for this hypothesis domain
- **Fallback:** Exa GitHub search and pingouin official documentation used as primary sources

### B. GitHub Implementations (Exa)

**Repository 1:** raphaelvallat/pingouin
- **URL:** https://github.com/raphaelvallat/pingouin / https://pingouin-stats.org
- **Query Used:** "partial Spearman correlation BCa bootstrap confidence interval scenario classification Python"
- **Relevance:** Primary statistical library providing `partial_corr()` and `compute_bootci()` — already validated in H-M2
- **Key Code (annotated):**
  ```python
  # H-M3 reuses this exact API from H-M2:
  result = pg.partial_corr(
      data=df, x="TruthfulQA_MC2", y="bbq_accuracy",
      covar=["MMLU"], method="spearman"
  )  # Returns DataFrame with columns: n, r, CI95, p-val

  # BCa bootstrap CI (standalone, for raw_rho):
  ci = pg.compute_bootci(
      x=x, y=y, func="spearman", method="bca",
      paired=True, n_boot=5000, seed=42
  )  # Returns [lo, hi] numpy array
  ```
- **Used For:** Tier 2 partial correlation re-analysis (TruthfulQA×HarmBench, BBQ×HarmBench)

**Repository 2:** privong/pymccorrelation
- **URL:** https://github.com/privong/pymccorrelation
- **Query Used:** "partial Spearman correlation BCa bootstrap confidence interval scenario classification Python"
- **Relevance:** Alternative BCa bootstrap for Spearman; validates N_boot=5000 standard
- **Used For:** Reference validation of bootstrap approach; confirms 5000 samples is standard for CI stability

**Repository 3:** zeroEQpart R package
- **URL:** https://doi.org/10.32614/cran.package.zeroeqpart
- **Query Used:** Same
- **Relevance:** BCa bootstrap test specifically designed for zero-order vs partial correlation equality (conceptual analog to H-M3 scenario assignment)
- **Key Insight:** BCa CI overlap between raw_rho and partial_rho is a validated inferential approach (Efron 1983)
- **Used For:** Conceptual validation of CI-based scenario classification methodology

**Repository 4:** siyangwu1/Benchmark-Signature-Repository
- **URL:** https://github.com/siyangwu1/Benchmark-Signature-Repository
- **Query Used:** "LLM benchmark correlation analysis Fisher z test Spearman GitHub"
- **Relevance:** Cross-model LLM benchmark correlation study (32 LLMs, 89 benchmarks); validates observational study design
- **Used For:** Design pattern validation — confirms cross-LLM Spearman analysis with N~30 is publishable

**Repository 5:** H-M2 codebase (local, primary reference)
- **URL:** docs/youra_research/h-m2/code/analyze.py
- **Relevance:** Contains all statistical primitives H-M3 builds upon:
  - `compute_partial_spearman()`: pg.partial_corr() wrapper with singular matrix guard
  - `_bca_partial_rho_with_dist()`: Manual BCa bootstrap with jackknife acceleration
  - `compute_bca_cis()`: BCa CI for both raw_rho and partial_rho
  - `compute_family_robustness()`: Per-family Spearman for Llama clustering robustness
- **Used For:** Tier 2 analysis (re-uses load_data + pg.partial_corr pattern); scenario classification consumes outputs

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from H-M2 and pingouin documentation was sufficiently clear for H-M3 design. H-M3 is a thin analysis layer consuming H-M2 output; no complex code structure requiring semantic analysis.

### D. Previous Hypothesis Context

**Source:** H-M2 validated results + H-M2 code (analyze.py)
- **Reused Components:**
  - Statistical results: partial_rho, ci_partial, raw_rho, ci_raw, N (from h_m2_results.json)
  - Code patterns: data loading, pg.partial_corr API usage, BCa bootstrap structure
  - Configuration: N_bootstrap=5000, seed=42, fuzzy threshold=75, n_min=30
- **Why Reused:** H-M3 is definitionally downstream of H-M2 — scenario classification is applied to H-M2 output. Re-computing would be redundant.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Scenario boundaries (a/b/c) | Phase 2A/2B | 02b_verification_plan.md §2.2 H-M3 |
| partial_rho input | H-M2 validated results | h_m2_results.json |
| BCa CI bounds | H-M2 computed | h_m2["ci_partial"] |
| pingouin.partial_corr API | GitHub (Exa) | raphaelvallat/pingouin |
| compute_bootci BCa method | GitHub (Exa) | pingouin-stats.org documentation |
| N_bootstrap=5000 standard | GitHub (Exa) | privong/pymccorrelation |
| Tier 2 HarmBench hardcoded | Phase 2B risk analysis | 02b_verification_plan.md §4 R4 mitigation |
| Tier 3 binomtest | scipy.stats | scipy.stats.binomtest |
| Observational study with N~30 | GitHub (Exa) | siyangwu1/Benchmark-Signature-Repository |
| CI overlap as inferential criterion | CRAN package (Exa) | zeroEQpart (Efron 1983 BCa) |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — managed externally)
**Date:** 2026-07-30

### Workflow History for This Hypothesis
- 2026-07-30: Phase 2C experiment design initiated (IN_PROGRESS)
- 2026-07-30: Step 1 — State validated, H-M3 selected, 02b_context.md JIT-generated
- 2026-07-30: Step 2 — Archon KB searched (no domain-relevant results; KB indexed for diffusion models only)
- 2026-07-30: Step 3 — Exa GitHub searched; pingouin, pymccorrelation, zeroEQpart, H-M2 codebase found
- 2026-07-30: Step 4 — Serena skipped (code sufficiently clear from H-M2 + Exa)
- 2026-07-30: Step 5 — Dataset confirmed: H-M2 results (Tier 1), HarmBench hardcoded (Tier 2), h-m1 pairs (Tier 3)
- 2026-07-30: Step 6 — Experiment specification synthesized: scenario classification + Tier 2/3 analysis
- 2026-07-30: Step 7 — References documented with full traceability matrix
- 2026-07-30: Step 8 — Validation complete; experiment_design.status = COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code — no domain results), Exa (GitHub — 5 relevant repos found)*
*All specifications grounded in H-M2 validated code and pingouin/scipy library documentation*
*Next Phase: Phase 3 - Implementation Planning*
