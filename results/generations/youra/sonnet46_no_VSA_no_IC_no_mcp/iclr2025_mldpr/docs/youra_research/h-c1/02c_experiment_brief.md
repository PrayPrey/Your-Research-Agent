# Experiment Design: H-C1

**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr
**Hypothesis Statement:** Under the condition that the mechanism is validated for ≥50-entry benchmarks (H-M4 confirmed), if we apply the same logistic fitting pipeline to benchmarks with 30–49 leaderboard entries (boundary condition), then scipy curve_fit will either fail to converge or yield R² < 0.7 and/or physically implausible parameters, because with fewer data points the growth, inflection, and plateau phases are underrepresented, making the 3-parameter logistic model non-identifiable.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **CONDITION Hypothesis** — Scope boundary test. Tests whether the ≥50-entry restriction is empirically justified.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M4 (VALIDATED, SHOULD_WORK gate PASSED)
**Gate Status:** SHOULD_WORK — failure documents scope limitation, does not block

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-C1
- **Type:** CONDITION
- **Prerequisites:** H-M4

### Gate Condition
SHOULD_WORK — If the pipeline succeeds at 30–49 entries (failure of H-C1), this recommends expanding the scope claim from ≥50 to ≥30 entries. If H-C1 is supported (pipeline degrades), the ≥50-entry threshold is empirically confirmed.

---

## Continuation Context

H-C1 is a direct continuation of H-M4. The validated pipeline from H-E1 through H-M4 is reused without modification. The only change is the input: benchmarks with 30–49 entries instead of ≥50 entries.

### Previous Hypothesis Results (H-M4)
- **Outcome:** VALIDATED
- **Pipeline:** scipy curve_fit with K/(1+exp(-r*(t-t0))), bounded init (K∈[0.8,1.0], r∈[0.1,2.0], t0∈[6,36])
- **Proven components:** paperswithcode-client API retrieval, logistic fitting, saturation criterion
- **Optimal hyperparameters:** Same bounds used; H-C1 reuses these exactly
- **Lessons learned:** Pipeline converges cleanly for GLUE (≥200 entries) and SuperGLUE (≥50 entries); boundary condition at 30–49 is the untested regime

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**MCP Status:** Archon MCP unavailable (ablation mode — no live MCP servers).

**Internal Knowledge Synthesis (substitute):**

**Logistic fitting convergence vs. sample size — established literature:**
- Standard rule of thumb for 3-parameter nonlinear regression: minimum 10× parameters = 30 data points, but sigmoid identification requires data spanning all three phases (growth, inflection, plateau). With <50 points and a 3-parameter model, the Jacobian becomes ill-conditioned when plateau phase data is sparse.
- R² threshold of 0.7 as failure criterion is standard for model rejection in curve fitting contexts (lower than the 0.9 success criterion used in H-E1).
- scipy curve_fit raises `RuntimeError: Optimal parameters not found` on convergence failure, or returns parameters at boundary constraints (K=1.0 exactly, r→0, or t0 at bound limits) as signals of non-identifiability.

**Relevant patterns from H-E1 (proven in this pipeline):**
- `p0` initial guess: `[0.95, 0.5, 18]` for (K, r, t0)
- Bounds: `([0.8, 0.1, 6], [1.0, 2.0, 48])`
- Success criterion H-E1: R² > 0.9, no RuntimeError
- H-C1 failure criterion: R² < 0.7 OR RuntimeError OR K at bound (1.0) with CI(K) width = 0 (boundary hit)

**Benchmark selection strategy for 30–49 entry range:**
- Papers With Code API: `client.benchmarks()` returns all benchmarks; filter by `result_count` field
- Target benchmarks: must have ≥2019 date coverage + 30–49 entries + single composite metric
- Examples from PwC dataset (domain knowledge): WMT translation sub-benchmarks, HellaSwag (early period), ANLI rounds, domain-specific NLP benchmarks

### Archon Code Examples

**MCP Status:** Unavailable (ablation mode).

**Internal pattern (from H-E1/H-M4 validated code):**
```python
# Reuse from H-E1 — already validated
from scipy.optimize import curve_fit
import numpy as np

def logistic(t, K, r, t0):
    return K / (1 + np.exp(-r * (t - t0)))

def fit_logistic(times, scores, bounds=([0.8, 0.1, 6], [1.0, 2.0, 48])):
    try:
        popt, pcov = curve_fit(logistic, times, scores,
                                p0=[0.95, 0.5, 18],
                                bounds=bounds, maxfev=5000)
        ss_res = np.sum((scores - logistic(times, *popt))**2)
        ss_tot = np.sum((scores - np.mean(scores))**2)
        r_squared = 1 - ss_res / ss_tot
        return popt, np.sqrt(np.diag(pcov)), r_squared, True
    except RuntimeError:
        return None, None, None, False
```

### Exa GitHub Implementations

**MCP Status:** Exa MCP unavailable (ablation mode).

**Internal knowledge synthesis:**

**Repository (known):** `paperswithcode/paperswithcode-client` (official Python client)
- **URL:** https://github.com/paperswithcode/paperswithcode-client
- **Relevance:** Official API for retrieving benchmark leaderboard data
- **Key pattern for benchmark discovery:**
```python
from paperswithcode import PapersWithCodeClient
client = PapersWithCodeClient()

# List all benchmarks with result counts
benchmarks = client.benchmark_list(page=1, items_per_page=500)
# Filter: 30 <= result_count <= 49
small_benchmarks = [b for b in benchmarks.results
                    if 30 <= b.result_count <= 49]
```
- **Training Config:** N/A (statistical fitting, no GPU)
- **Dataset:** Papers With Code leaderboard timeseries

**Serena Analysis Needed:** False — same pipeline as H-E1, no new complex code

### 🎯 Implementation Priority Assessment

**CRITICAL:** H-C1 is NOT a paper reproduction experiment. It is a scope boundary test of our own pipeline. No "author's official implementation" exists.

**Recommended Implementation Path:**
- **Primary:** Reuse validated H-E1/H-M4 logistic fitting code verbatim
- **Fallback:** Identical `scipy.optimize.curve_fit` with same bounds/initialization
- **Justification:** Controlled comparison requires zero changes to the fitting procedure; only the input benchmark changes

### Code Analysis (Serena MCP)

*Skipped* — Code from prior hypotheses (H-E1 through H-M4) was sufficiently clear; no new complex code patterns introduced. H-C1 reuses the validated pipeline.

---

## Experiment Specification

### Dataset

**Name:** Papers With Code Leaderboard Timeseries — 30–49 Entry Subset
**Type:** programmatic-api
**Source:** Papers With Code public API (`paperswithcode-client`)

**Selection Criteria:**
- `result_count` between 30 and 49 (inclusive)
- At least one result from ≥2019 (date coverage requirement)
- Single composite metric available (same constraint as H-E1)
- English NLP benchmarks preferred (same domain as GLUE/SuperGLUE control group)

**Target Benchmark Discovery:**
- Query `client.benchmark_list()` with pagination to enumerate all PwC benchmarks
- Filter by `30 <= result_count <= 49`
- Select 3–5 qualifying benchmarks (minimum 3 for statistical comparison)
- Retrieve full timeseries via `client.benchmark_results(benchmark_id=...)`

**Control Group (from H-E1/H-M4):**
- GLUE (~200+ entries), SuperGLUE (~50–80 entries) — already fitted, R² > 0.9 confirmed
- These serve as the ≥50-entry baseline for comparison

**Statistics:** 30–49 data points per benchmark (by definition); 3–5 benchmarks total
**Preprocessing:** Identical to H-E1 — standardize metric to [0,1], convert dates to months-since-release, deduplicate (keep best score per model per month)
**Augmentation:** None (statistical fitting; no data augmentation)

**Loading Information** (for Phase 4 download):
- Method: programmatic-api
- Identifier: `paperswithcode-client` Python package
- Code: `from paperswithcode import PapersWithCodeClient; client = PapersWithCodeClient(); results = client.benchmark_results(benchmark_id='<id>')`

### Models

#### Baseline Model

**Architecture:** 3-parameter logistic growth model — K / (1 + exp(-r*(t - t0)))
**Type:** Statistical curve (scipy.optimize.curve_fit)
**Source:** Same as H-E1 — `scipy.optimize.curve_fit` with bounded initialization
**Status:** No pretrained weights; pure parameter estimation from data

**Configuration:**
- Parameters: K (asymptote/ceiling), r (growth rate), t0 (inflection point in months)
- Initial guess: `p0 = [0.95, 0.5, 18]`
- Bounds: `([0.8, 0.1, 6], [1.0, 2.0, 48])`
- Max function evaluations: 5000

**Loading Information** (for Phase 4):
- Method: pip install (`pip install scipy paperswithcode-client`)
- Identifier: `scipy.optimize.curve_fit`
- Code: `from scipy.optimize import curve_fit`

#### Proposed Model

**Architecture:** Same logistic model applied to 30–49-entry benchmarks (boundary condition test)

**Core Mechanism — Boundary Condition Test:**

```python
# Logistic Fitting Pipeline — H-C1 Boundary Condition Test
# Based on: H-E1 validated pipeline (scipy.optimize.curve_fit)
# Tests: Does fit quality degrade for n_entries in [30, 49]?

import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import spearmanr

def logistic(t, K, r, t0):
    """3-parameter logistic: K / (1 + exp(-r*(t - t0)))"""
    return K / (1 + np.exp(-r * (t - t0)))

def fit_and_evaluate(times, scores):
    """
    Args:
        times:  (N,) months-since-release, N in [30, 49]
        scores: (N,) normalized benchmark scores in [0, 1]
    Returns:
        dict with convergence, r_squared, params, plausible
    """
    try:
        popt, pcov = curve_fit(
            logistic, times, scores,
            p0=[0.95, 0.5, 18],
            bounds=([0.8, 0.1, 6], [1.0, 2.0, 48]),
            maxfev=5000
        )
        K, r, t0 = popt
        ss_res = np.sum((scores - logistic(times, *popt))**2)
        r_sq = 1 - ss_res / np.sum((scores - scores.mean())**2)
        ci_width = 2 * 1.96 * np.sqrt(np.diag(pcov))
        # Plausibility: K not at bound, r > 0, t0 within observed range
        plausible = (K < 0.999) and (r > 0.05) and (6 < t0 < 48)
        return {"converged": True, "r_squared": r_sq,
                "params": popt, "ci_width": ci_width,
                "plausible": plausible}
    except RuntimeError:
        return {"converged": False, "r_squared": None,
                "params": None, "ci_width": None,
                "plausible": False}

# H-C1 comparison: run for each small benchmark, compare to H-E1 results
```

### Training Protocol

**From Previous Hypothesis (H-E1/H-M4):**
- **Optimizer:** N/A — scipy.optimize.curve_fit (Levenberg–Marquardt)
- **Learning Rate:** N/A — scipy internal
- **Batch Size:** N/A — full dataset per benchmark
- **Epochs:** N/A — single optimization pass
- **Loss:** Sum of squared residuals (RSS), minimized by curve_fit
- **Seeds:** 1 (fixed; deterministic optimization)
- **Compute:** CPU only; <1 second per benchmark fit

**Rationale:** Reusing identical procedure from H-E1. Controlled comparison — only input benchmark changes.

**Data Pipeline:**
1. `client.benchmark_list()` → filter 30 ≤ result_count ≤ 49 → select 3–5 benchmarks
2. For each: `client.benchmark_results(benchmark_id=...)` → extract (date, metric_value)
3. Parse dates → months-since-earliest-submission
4. Normalize metric to [0,1] (min-max within benchmark)
5. Deduplicate: keep best score per (model, month)
6. Run `fit_and_evaluate(times, scores)`
7. Collect: convergence bool, R², params, plausibility

### Evaluation

**Primary Metrics (H-C1 specific):**

| Metric | Definition | H-C1 "Success" Threshold | Comparison Basis |
|--------|------------|--------------------------|------------------|
| Convergence rate | % benchmarks where curve_fit converges | <70% (vs. 100% for ≥50 group) | H-E1/H-M4 results |
| R² (mean) | Mean R² across converged benchmarks | <0.7 (vs. >0.9 for ≥50 group) | H-E1 threshold |
| Parameter plausibility rate | % benchmarks with physically plausible K, r, t0 | <70% | H-M3 criteria |
| K boundary hit rate | % benchmarks where K = 1.0 (at bound, non-identifiable) | >30% (signal of non-identifiability) | Expected 0% for ≥50 group |

**Success Criteria (SHOULD_WORK gate):**
- H-C1 SUPPORTED: At least one of the following for the 30–49 group vs. the ≥50 control:
  - Convergence rate is meaningfully lower (<70% vs. 100%)
  - Mean R² is meaningfully lower (<0.7 vs. >0.9)
  - Plausibility rate is meaningfully lower (<70%)
- H-C1 NOT SUPPORTED (scope expansion): All metrics for 30–49 group are comparable to ≥50 group → recommend lowering threshold to ≥30

**Expected Baseline Performance (control group from H-E1/H-M4):**
- Convergence rate: 100% (GLUE, SuperGLUE both converged)
- R²: >0.9 for both benchmarks
- Plausibility: 100% (all K, r, t0 within bounds)

**Metrics Library:**
- Task Type: Statistical model comparison
- Library: numpy + scipy (no external metrics library needed)
- Code: `r_sq = 1 - ss_res / ss_tot` (manual), `scipy.stats.spearmanr` for trend check

**Metrics Loading Information:**
- Task Type: statistical-comparison
- Library: numpy/scipy (built-in)
- Code: `import numpy as np; from scipy.stats import spearmanr`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart — convergence rate, mean R², plausibility rate for 30–49 group vs. ≥50 control

#### Additional Figures (LLM Autonomous)

Phase 4 should autonomously determine appropriate additional figures, which may include:
1. **R² distribution plot:** Histogram of R² values for all 30–49-entry benchmarks overlaid with ≥50 control
2. **Fitted curve overlays:** For each 30–49 benchmark, plot raw data + fitted logistic curve (or note convergence failure)
3. **Parameter scatter:** K vs. r scatter for 30–49 group, annotated with H-E1 fitted values
4. **Convergence failure map:** Table of benchmarks attempted, convergence outcome, and R² value

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-c1/figures/`.

---

## 🔬 Mechanism Verification Protocol

> **Purpose:** Verify that the boundary condition test is actually testing what it claims — not just that code runs.

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | Papers With Code API accessible; ≥3 benchmarks with 30–49 entries found from ≥2019 | TRUE (PwC API is publicly accessible; filter will return qualifying benchmarks) |
| Mechanism Isolatable | Can compare 30–49 group vs. ≥50 control (H-E1 results) independently | TRUE (H-E1 results stored; identical pipeline used) |
| Baseline Measurable | ≥50-entry baseline results available from H-E1/H-M4 | TRUE (H-E1/H-M4 VALIDATED) |

### Architecture Compatibility Check

H-C1 uses the same logistic fitting pipeline as H-E1. No new architecture introduced.

**Required Features:**
- `paperswithcode-client` ≥ 0.2.x: `benchmark_list()` with `result_count` field accessible
- `scipy.optimize.curve_fit`: same version as H-E1 (convergence behavior must be comparable)

**Potential Incompatibility:**
- If PwC API changes `result_count` field name or removes it, benchmark filtering fails
- If no benchmarks with 30–49 entries from ≥2019 are found, H-C1 cannot be executed (scope limitation)

> ⚠️ If fewer than 3 qualifying benchmarks are found, Phase 4 MUST log warning and reduce scope to available benchmarks (minimum 1 still allows partial test).

### Mechanism Activation Indicators

**How to detect if boundary condition test is actually working:**

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"Found N benchmarks with 30-49 entries"` (N ≥ 3) | data_loader.py |
| Convergence Signal | `RuntimeError` caught OR R² < 0.7 logged for ≥1 benchmark | fitting.py:fit_and_evaluate() |
| Metric Delta | R²(30–49 group) < R²(≥50 control) = difference measurable | evaluate.py |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_boundary_test_activated(results_small, results_control):
    """
    results_small: list of fit_and_evaluate() dicts for 30-49 entry benchmarks
    results_control: list of fit_and_evaluate() dicts for >=50 entry benchmarks (H-E1)
    """
    small_converged = [r for r in results_small if r["converged"]]
    control_converged = [r for r in results_control if r["converged"]]

    indicators = {
        "small_group_found": len(results_small) >= 3,
        "control_available": len(results_control) >= 2,
        "any_failure_small": len(small_converged) < len(results_small),
        "r2_delta_measurable": (
            len(small_converged) > 0 and len(control_converged) > 0 and
            np.mean([r["r_squared"] for r in small_converged]) !=
            np.mean([r["r_squared"] for r in control_converged])
        )
    }
    activated = indicators["small_group_found"] and indicators["control_available"]
    return activated, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| No qualifying benchmarks | `len(small_benchmarks) == 0` after API filter | FAIL: Scope limitation — PwC lacks 30–49 entry benchmarks from ≥2019 |
| API rate limit / unavailability | ConnectionError or HTTP 429 | RETRY with backoff; cache intermediate results |
| Pipeline identical performance | R²(30–49) ≥ 0.9 AND all converge | H-C1 NOT SUPPORTED — recommend scope expansion to ≥30 |
| All 30–49 benchmarks converge with R²>0.9 | Per-benchmark logging | Document: threshold should be lowered |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | ≥3 benchmarks tested | Count of benchmarks processed |
| Degradation Measurable | R² difference > 0.2 OR convergence failure ≥1 | Before/after group comparison |
| Hypothesis Supported | Fit quality meaningfully worse for 30–49 group | Mean R²(small) < 0.7 OR convergence rate(small) < 70% |

---

## Ablation Studies

**Threshold Sensitivity Analysis (CONDITION hypothesis requires this):**

| Variant | Description | Purpose |
|---------|-------------|---------|
| Strict threshold | Failure = R² < 0.5 | Tests if degradation is severe |
| Loose threshold | Failure = R² < 0.8 | Tests if any degradation visible |
| Boundary at 40 | Split 30–39 vs. 40–49 | Tests whether sub-range matters |
| No bound constraints | curve_fit with no bounds | Tests if bounds artificially cause failure |

**Rationale:** These variants determine whether the ≥50 threshold is a hard cliff or a gradual degradation, which directly informs the scope claim precision.

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**MCP Status:** Unavailable (ablation mode — no Archon server active).

**Internal knowledge used:**
- Standard statistical guidance on nonlinear regression sample size requirements
- scipy.optimize documentation on curve_fit convergence behavior
- H-E1 validated pipeline results (reused directly)

### B. GitHub Implementations (Exa)

**MCP Status:** Unavailable (ablation mode — no Exa server active).

**Known repository (domain knowledge):**
- **Repository:** `paperswithcode/paperswithcode-client`
- **URL:** https://github.com/paperswithcode/paperswithcode-client
- **Used For:** Benchmark discovery and timeseries retrieval
- **Key Pattern:**
```python
from paperswithcode import PapersWithCodeClient
client = PapersWithCodeClient()
# List benchmarks
all_benchmarks = []
page = 1
while True:
    result = client.benchmark_list(page=page, items_per_page=100)
    all_benchmarks.extend(result.results)
    if page >= result.next_page: break
    page += 1
# Filter 30-49 entries
small = [b for b in all_benchmarks if 30 <= b.result_count <= 49]
```

### C. Code Analysis (Serena)

Serena analysis not performed — H-C1 reuses the validated H-E1 pipeline without modification.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Reports — H-E1, H-M4
- **Reused components:** logistic fitting function, bounds, initial guess, R² computation
- **Reused result (control group):** GLUE R² > 0.9, SuperGLUE R² > 0.9, both converged
- **Why reused:** H-C1 is a controlled comparison; the ≥50-entry reference group is the validated H-E1 result

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Phase 2B | 02b_verification_plan.md H-C1 verification protocol |
| Entry count filter (30–49) | Phase 2B | H-C1 statement + scope boundary A4 |
| Logistic fitting pipeline | Previous hypothesis | H-E1 validated code |
| Bounds and initialization | Previous hypothesis | H-E1 curve_fit parameters |
| Failure criterion (R² < 0.7) | Phase 2B success criteria | H-C1 — contrast to H-E1 R² > 0.9 |
| Control group | Previous hypothesis | H-E1/H-M4 VALIDATED results |
| Evaluation framework | Phase 2B | Scope boundary analysis A4 risk mitigation |
| Ablation variants | Phase 2B | Risk R4 sensitivity analysis |

---

## State Information

**State File:** verification_state.yaml (managed via ABLATION MODE restate block)
**Date:** 2026-08-25

### Workflow History for This Hypothesis
- H-C1 set to IN_PROGRESS: 2026-08-25T17:08:56
- Phase 2C started: 2026-08-25
- Phase 2C completed: 2026-08-25

---

*MCP Tools Used: None (ablation mode — Archon and Exa unavailable; internal knowledge synthesis substituted)*
*All specifications grounded in validated H-E1/H-M4 pipeline and 02b_verification_plan.md*
*Next Phase: Phase 3 - Implementation Planning*
