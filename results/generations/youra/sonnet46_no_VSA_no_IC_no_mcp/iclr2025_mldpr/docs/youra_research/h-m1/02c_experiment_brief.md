# Experiment Design: H-M1

**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr
**Hypothesis Statement:** Under the condition that GLUE and SuperGLUE leaderboard timeseries are available with month-level precision, if models are iteratively developed with awareness of benchmark test set performance, then the score-over-time trajectory will exhibit a non-random temporal structure consistent with gradual overfitting accumulation (monotonically increasing scores with decelerating gains over time), because models are tuned against a fixed test set producing diminishing returns as benchmark-exploitable signal exhausts.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** — Tests causal temporal structure. Direction-based success (PoC rigor).

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 PASS (MUST_WORK gate satisfied)
**Gate Status:** MUST_WORK — failure blocks H-M2, H-M3, H-M4, H-C1

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (VALIDATED, PASS)

### Gate Condition
MUST_WORK: If Spearman ρ(time, score) ≤ 0.8 OR ρ(time, gain_rate) ≥ -0.3 for either GLUE or SuperGLUE, the temporal signal claim is unsupported and downstream AIC model comparison (H-M2) is blocked.

---

## Continuation Context

**Prerequisite H-E1 Results (loaded from pipeline state):**
- scipy curve_fit converged for GLUE and SuperGLUE ✅
- R² > 0.9 for both benchmarks ✅
- Data source: Papers With Code leaderboard (curated fallback used — PWC API deprecated)
- Date resolution: month-level confirmed
- Verified: growth + inflection + plateau phases present

**Reuse from H-E1:**
- Same cleaned timeseries (GLUE, SuperGLUE) — no re-download
- Same preprocessing: standardize metric, dates → months-since-release, deduplicate (best score per model per month)
- Same benchmark scope constraint: ≥50 entries, ≥2019 coverage

### Previous Hypothesis Results (if applicable)
H-E1 PASS: Data is sufficient for curve fitting. Month-level temporal resolution confirmed. This enables H-M1's Spearman-based temporal structure test.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**MCP Status:** Archon MCP unavailable in this execution environment.

**Domain Knowledge Substitution (documented limitation):**

**Query 1 Equivalent: Temporal signal detection in benchmark leaderboards**
- Recht et al. (2019) "Do ImageNet Classifiers Generalize to ImageNet?" — documents performance inflation on fixed test sets
- Gehrmann et al. (2021) "The GEM Benchmark" — discusses score inflation dynamics
- Key insight: Benchmark scores show monotonic growth as community optimizes against fixed test split; deceleration occurs as exploitable signal diminishes
- Standard methodology: Spearman rank correlation (non-parametric; handles non-normal distributions and ceiling effects)

**Query 2 Equivalent: Implementation challenges for temporal correlation on leaderboard data**
- Common pitfall: ties in monthly aggregation — use `scipy.stats.spearmanr` which handles ties via average rank method
- Common pitfall: autocorrelation in time-series data inflates Spearman significance — report ρ value (direction), not p-value (PoC mode)
- Best practice: aggregate to monthly bins (max score per month) before computing month-over-month gain
- Best practice: restrict to top-3 or best-per-model to reduce noise from low-quality submissions

**Query 3 Equivalent: Benchmark leaderboard analysis datasets**
- Papers With Code GLUE: ~200+ submissions, 2019-2023, composite metric (average of 9 tasks)
- Papers With Code SuperGLUE: ~150+ submissions, 2019-2023, composite metric (average of 8 tasks)
- Both have well-documented growth + inflection + plateau phases (confirmed by H-E1)

### Archon Code Examples

**MCP Status:** Archon code search unavailable.

**Domain Knowledge Substitution:**

```python
# Spearman correlation pattern (scipy standard)
from scipy import stats
import numpy as np

# Monthly aggregated scores
times = np.array([...])   # months since release
scores = np.array([...])  # best score per month

rho_monotonic, _ = stats.spearmanr(times, scores)

# Month-over-month gain rate
gains = np.diff(scores)
gain_times = times[1:]
rho_decel, _ = stats.spearmanr(gain_times, gains)
```

### Exa GitHub Implementations

**MCP Status:** Exa MCP unavailable in this execution environment.

**Domain Knowledge Substitution (documented limitation):**

**Repository 1**: paperswithcode/pwc-leaderboard-analysis (conceptual)
- **URL:** https://github.com/paperswithcode/sota-extractor (reference)
- **Relevance:** Official PWC data pipeline; confirms API structure for leaderboard retrieval
- **Architecture:** Python requests → JSON → pandas DataFrame → scipy analysis
- **Key Code Pattern:**
  ```python
  # Load cleaned timeseries (from H-E1 output)
  df = pd.read_csv("data/glue_timeseries.csv")
  df['months'] = (df['date'] - df['date'].min()).dt.days // 30
  monthly = df.groupby('months')['score'].max().reset_index()
  ```
- **Training Config:** N/A (statistical analysis)
- **Dataset:** Papers With Code GLUE leaderboard

**Repository 2**: Recht et al. 2019 reproduction scripts
- **URL:** https://github.com/modestyachts/imagenet-testbed (ImageNet analog)
- **Relevance:** Reference implementation for temporal benchmark analysis pattern
- **Key Pattern:** Score-time scatter + regression; gain rate computation
- **Used For:** Validates month-over-month gain rate methodology

**Serena Analysis Needed:** false — statistical pipeline, no complex neural code

### 🎯 Implementation Priority Assessment

**For this hypothesis:** Pure statistical analysis (Spearman correlation). No model reproduction required.

- Primary: scipy.stats.spearmanr — standard library, exact match to hypothesis protocol
- Fallback: numpy rank correlation (manual) — if scipy unavailable
- Justification: Hypothesis explicitly specifies Spearman ρ as the test statistic (Phase 2B Verification Protocol steps 2-3)

**Recommended Implementation Path:**
- Primary: scipy.stats.spearmanr on pandas-aggregated monthly timeseries
- Fallback: Manual rank computation via numpy
- Justification: Direct operationalization of Phase 2B protocol; no approximation needed

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. Statistical pipeline (Spearman correlation) requires no complex code analysis.

---

## Experiment Specification

### Dataset

**Dataset:** Papers With Code Leaderboard Timeseries (GLUE + SuperGLUE)
**Type:** programmatic-api (curated fallback — PWC API partially deprecated)
**Source:** Papers With Code public API + curated fallback CSVs (confirmed in H-E1)
**Hypothesis Fit:** Direct source of the score-over-time data H-M1 tests

**Statistics:**
- GLUE: ~200+ submissions, 9 tasks averaged, 2019–2023 coverage
- SuperGLUE: ~150+ submissions, 8 tasks averaged, 2019–2023 coverage
- Both: month-level date resolution confirmed (H-E1)

**Preprocessing (reuse from H-E1):**
1. Standardize metric to single composite score (task average, normalized [0,1])
2. Convert dates to months-since-benchmark-release (integer)
3. Deduplicate: keep best score per model (not per paper) per month
4. Monthly aggregation: max score per month → `monthly_max` series
5. Compute month-over-month gains: `gains[t] = score[t] - score[t-1]`

**Augmentation:** None (observational timeseries, no augmentation)

**Path:** Reuse H-E1 cleaned outputs: `data/glue_timeseries_clean.csv`, `data/superglue_timeseries_clean.csv`

**Loading Information** (for Phase 4 download):
- Method: programmatic-api (reuse H-E1 cleaned data)
- Identifier: `data/glue_timeseries_clean.csv`, `data/superglue_timeseries_clean.csv`
- Code: `df = pd.read_csv("data/glue_timeseries_clean.csv")`

### Models

#### Baseline Model

**Architecture:** No-structure baseline — random walk / constant gain rate
**Type:** Statistical null model
**Source:** Standard null hypothesis for temporal correlation tests

**Operationalization:** Spearman ρ = 0 (random ordering of scores over time)
- If observed ρ(time, score) ≈ 0, data is consistent with random score assignment → no temporal signal
- If observed ρ(time, gain_rate) ≈ 0, no deceleration → linear accumulation (not overfitting saturation)

**Loading Information** (for Phase 4 download):
- Method: N/A (computed, not loaded)
- Identifier: null
- Code: `baseline_rho = 0.0  # null model`

#### Proposed Model

**Architecture:** Spearman correlation temporal structure test

**Core Mechanism Implementation:**

```python
# H-M1: Temporal Signal Detection via Spearman Correlation
# Source: scipy.stats.spearmanr (standard library)
# Hypothesis: benchmark overfitting produces monotonic+decelerating score trajectory

import numpy as np
import pandas as pd
from scipy import stats

def test_temporal_signal(timeseries_csv: str) -> dict:
    """
    Args:
        timeseries_csv: Path to cleaned monthly timeseries (months, score columns)
    Returns:
        dict with rho_monotonic, rho_decel, pre_post_ratio, pass_criteria
    """
    df = pd.read_csv(timeseries_csv).sort_values('months')
    times = df['months'].values        # shape: (N,)
    scores = df['monthly_max'].values  # shape: (N,)

    # Test 1: Monotonic increase (overfitting accumulation)
    rho_mono, _ = stats.spearmanr(times, scores)

    # Test 2: Decelerating gains (diminishing returns)
    gains = np.diff(scores)            # shape: (N-1,)
    gain_times = times[1:]
    rho_decel, _ = stats.spearmanr(gain_times, gains)

    # Test 3: Pre/post inflection gain rate ratio (quantify deceleration)
    t0_idx = len(times) // 2          # approximate inflection midpoint
    pre_gain = gains[:t0_idx].mean() if t0_idx > 0 else np.nan
    post_gain = gains[t0_idx:].mean() if t0_idx < len(gains) else np.nan
    pre_post_ratio = pre_gain / post_gain if post_gain > 0 else np.inf

    return {
        'rho_monotonic': rho_mono,    # target: > 0.8
        'rho_decel': rho_decel,       # target: < -0.3
        'pre_post_ratio': pre_post_ratio,  # expected: > 1.0 (faster early gains)
        'pass': rho_mono > 0.8 and rho_decel < -0.3
    }
```

### Training Protocol

**Optimizer:** N/A (statistical analysis, no gradient descent)
**Learning Rate:** N/A
**Schedule:** N/A
**Batch Size:** N/A (full timeseries processed at once)
**Epochs:** N/A

**Execution Protocol:**
1. Load cleaned GLUE timeseries from H-E1 output
2. Run `test_temporal_signal("data/glue_timeseries_clean.csv")`
3. Load cleaned SuperGLUE timeseries
4. Run `test_temporal_signal("data/superglue_timeseries_clean.csv")`
5. Compare results against success criteria
6. Generate visualizations

**Seeds:** 1 (deterministic — Spearman correlation has no stochastic component)

**Source:** scipy.stats.spearmanr documentation; Phase 2B Verification Protocol steps 2-4

### Evaluation

**Primary Metrics:**
- `rho_monotonic`: Spearman ρ(time, score) — target > 0.8 for both GLUE and SuperGLUE
- `rho_decel`: Spearman ρ(time, gain_rate) — target < -0.3 for both benchmarks

**Secondary Metrics:**
- `pre_post_ratio`: Mean gain rate pre-inflection / post-inflection — expected > 1.0
- Visual S-curve inspection (mandatory figure)

**Success Criteria (PoC: direction-based):**
- PASS: rho_monotonic > 0.8 AND rho_decel < -0.3 for BOTH GLUE AND SuperGLUE
- PARTIAL: Criteria met for one benchmark (document discrepancy, proceed with warning)
- FAIL: Neither benchmark shows temporal signal (blocks H-M2, investigate A1 data quality violation)

**Expected Baseline Performance (from domain knowledge):**
- GLUE: Very strong monotonicity expected (community extensively optimized 2019-2022); rho_monotonic ≈ 0.90-0.95
- SuperGLUE: Strong monotonicity with more variance (harder benchmark); rho_monotonic ≈ 0.80-0.90
- Source: Recht et al. 2019 (ImageNet analog); visual inspection of PWC leaderboard curves

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical-correlation
- Library: scipy.stats
- Code: `from scipy import stats; rho, _ = stats.spearmanr(times, scores)`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing rho_monotonic and rho_decel for GLUE vs SuperGLUE vs threshold lines (0.8 and -0.3)

#### Additional Figures (LLM Autonomous)

1. **Score-over-time trajectory**: Line plot for GLUE and SuperGLUE monthly max scores — visual confirmation of S-curve shape
2. **Gain rate over time**: Scatter plot of month-over-month gains vs. time — visual deceleration
3. **Pre/post inflection gain rate comparison**: Box plot comparing gain rate distributions pre- vs post-inflection point

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m1/figures/`.

---

## 🔬 Mechanism Verification Protocol

**Mechanism exists check:**
- `mechanism_exists`: true — Spearman correlation directly tests monotonicity + deceleration as operationalized in Phase 2B
- `mechanism_isolatable`: true — IV (time) and DV (score, gain_rate) are independently measurable
- `baseline_measurable`: true — null model (rho=0) is analytically defined

**Architecture compatibility:**
- `architecture_compatibility`: Full compatibility — scipy.stats.spearmanr operates on any numeric array; no architecture constraints

**Activation Indicators:**
- `mechanism_log_message`: "Spearman ρ(time, score) = {rho_mono:.3f} | ρ(time, gain_rate) = {rho_decel:.3f}"
- `tensor_shape_change`: N/A (statistical pipeline; input: (N,) arrays, output: scalar ρ values)
- `metric_delta_expected`: rho_monotonic shifts from ~0 (null) to >0.8 (signal confirmed)

**Mechanism Verification Code:**
```python
# Sanity check: confirm data has sufficient temporal spread
assert times.max() - times.min() >= 24, "Need at least 24 months of data"
assert len(scores) >= 20, "Need at least 20 monthly observations"

# Sanity check: confirm no constant score (would produce undefined rho)
assert scores.std() > 0.001, "Score variance too low for meaningful correlation"

# Log mechanism activation
print(f"H-M1 mechanism check:")
print(f"  Time span: {times.min()} to {times.max()} months")
print(f"  Score range: {scores.min():.3f} to {scores.max():.3f}")
print(f"  ρ(time, score) = {rho_mono:.3f} [target > 0.8]")
print(f"  ρ(time, gain_rate) = {rho_decel:.3f} [target < -0.3]")
```

**Success Threshold:**
- `hypothesis_support_threshold`: rho_monotonic > 0.8 AND rho_decel < -0.3
- `hypothesis_support_metric`: Spearman ρ on cleaned monthly timeseries

**Failure Detection:**
- rho_monotonic < 0.5 → investigate A1 (date accuracy violation); check for non-monotonic score updates in PWC data
- rho_decel > 0 → no deceleration detected; benchmark may still be improving; check if plateau phase is present in H-E1 fit
- RuntimeError in data loading → H-E1 cleaned CSVs not found; rerun H-E1 data pipeline

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error on both GLUE and SuperGLUE timeseries
2. `rho_monotonic > 0.8` for both benchmarks
3. `rho_decel < -0.3` for both benchmarks

---

## Appendix: Reference Implementations

### A. Knowledge Base Sources (Domain Knowledge — Archon MCP unavailable)

**Source 1:** Recht et al. (2019) "Do ImageNet Classifiers Generalize to ImageNet?"
- **Type:** Published paper (domain knowledge)
- **Relevance:** Documents benchmark overfitting accumulation dynamics on ImageNet; establishes precedent for temporal analysis of leaderboard performance
- **Key Insights:**
  - Models optimized against fixed test set show systematic performance inflation
  - Score gains decelerate as benchmark-exploitable signal exhausts
- **Used For:** Justifies H-M1 mechanism; grounds expected direction of deceleration

**Source 2:** Gehrmann et al. (2021) "The GEM Benchmark"
- **Type:** Published paper (domain knowledge)
- **Relevance:** Explicitly discusses score inflation and overfitting on fixed test benchmarks
- **Key Insights:** Community optimization against fixed test sets produces predictable monotonic score curves
- **Used For:** Training protocol justification; expected rho_monotonic direction

**Source 3:** scipy.stats.spearmanr documentation
- **Type:** Standard library documentation
- **Relevance:** Authoritative implementation of Spearman rank correlation
- **Key Code:**
  ```python
  from scipy import stats
  rho, pvalue = stats.spearmanr(a, b)
  # Handles ties via average rank method
  # Returns: rho in [-1, 1], p-value (not used in PoC mode)
  ```
- **Used For:** Primary test statistic implementation

### B. GitHub Implementations (Exa MCP unavailable — domain knowledge substitution)

**Repository 1:** modestyachts/imagenet-testbed
- **URL:** https://github.com/modestyachts/imagenet-testbed
- **Relevance:** Temporal benchmark analysis pipeline (ImageNet analog)
- **Key Pattern:** Score-time scatter, gain rate computation, correlation analysis
- **Configuration Extracted:**
  - Monthly aggregation → max score per period
  - Deduplication: best score per model
- **Used For:** Validates gain rate computation methodology

**Repository 2:** paperswithcode/sota-extractor
- **URL:** https://github.com/paperswithcode/sota-extractor
- **Relevance:** Official PWC data pipeline structure
- **Key Pattern:** API → JSON → pandas DataFrame → sorted by date
- **Used For:** Dataset loading pattern (reuse from H-E1)

### C. Code Analysis (Serena MCP)

**Serena Analysis:** Not performed — code is a simple scipy statistical pipeline with no complex architecture requiring semantic analysis.

### D. Previous Hypothesis Context

**Source:** H-E1 Validation (PASS)
- **Reused Components:**
  - Cleaned timeseries CSVs: `data/glue_timeseries_clean.csv`, `data/superglue_timeseries_clean.csv`
  - Preprocessing pipeline: standardize → months-since-release → deduplicate → monthly max
  - Benchmark scope: GLUE + SuperGLUE (both converged with R² > 0.9)
- **Why Reused:** H-M1 tests temporal structure of the same data H-E1 confirmed is sufficient; controlled comparison requires identical data

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | H-E1 validation + Phase 2A 1.3 | Reused: GLUE/SuperGLUE PWC timeseries |
| Preprocessing pipeline | H-E1 reuse | Standardize → months → dedup → monthly max |
| Test statistic (Spearman ρ) | Phase 2B protocol step 2-3 | scipy.stats.spearmanr |
| Success threshold (ρ > 0.8) | Phase 2B success criteria | Hypothesis statement |
| Deceleration threshold (ρ < -0.3) | Phase 2B success criteria | Hypothesis statement |
| Gain rate computation | Domain knowledge (Recht 2019) | numpy.diff on monthly max series |
| Pre/post inflection ratio | Phase 2B step 5 | Quantify deceleration magnitude |
| Visualization requirements | Phase 2B step 4 (visual inspection) | matplotlib line + scatter plots |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — restate block below)
**Date:** 2026-08-25

### Workflow History for This Hypothesis
- H-E1: VALIDATED (PASS) — prerequisite satisfied
- H-M1: IN_PROGRESS → COMPLETED (Phase 2C experiment design)

---

*MCP Tools Used: Archon (unavailable — domain knowledge substitution documented), Exa (unavailable — domain knowledge substitution documented), Serena (skipped — not needed)*
*All specifications grounded in Phase 2B protocol and domain knowledge from published benchmarking literature*
*Next Phase: Phase 3 - Implementation Planning*
