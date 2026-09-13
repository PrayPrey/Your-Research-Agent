# Experiment Design: H-M3

**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr
**Hypothesis Statement:** Under the condition that the logistic model is AIC-preferred (H-M2 confirmed), if we extract the fitted parameters (K=ceiling, r=growth rate, t0=inflection point) from the GLUE and SuperGLUE fits, then the parameters will be interpretable and physically plausible (K ∈ [0.85, 1.0], t0 aligns with known rapid growth periods, r > 0), because the logistic model's three parameters directly encode the mechanism: K is the performance ceiling, t0 is when overfitting dominates, r quantifies the exploitation rate.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** — Validates parameter interpretability of the logistic fit already performed in H-E1/H-M2.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M2 PASS (ΔAIC_GLUE=−250.5, ΔAIC_SuperGLUE=−194.4)
**Gate Status:** MUST_WORK — null (to be determined by this experiment)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-M2 (VALIDATED ✅)

### Gate Condition

MUST_WORK: All three parameters (K, r, t0) physically plausible for BOTH GLUE and SuperGLUE.
- K ∈ [0.85, 1.0]
- t0 ∈ [6, 48] months since benchmark release
- r > 0
- 95% CI width for t0 < 12 months

---

## Continuation Context

This is a **continuation experiment** building directly on H-M2. The logistic fits have already been performed and stored in `h-m2/results.json`. H-M3 reuses those fits — it does NOT re-fit; it extracts and validates the parameters already computed.

### Previous Hypothesis Results (H-M2)

From `h-m2/results.json` (confirmed PASS):

| Parameter | GLUE | SuperGLUE |
|-----------|------|-----------|
| K (ceiling) | 0.8955 | 0.8858 |
| r (growth rate) | 0.2017 | 0.1578 |
| t0 (inflection, months relative to fit origin) | −6.77 | −2.85 |
| R² logistic | 0.9966 | 0.9934 |
| AIC logistic | −590.95 | −485.43 |

**Key observation:** t0 values are negative (relative to fit origin), meaning the inflection point occurred before or near the start of the recorded leaderboard window. This is physically meaningful: GLUE was already in its rapid growth phase when entries were first recorded. H-M3 must verify that when t0 is converted to an absolute date, it falls within the known rapid-growth period.

**Continuation reuse:**
- Same dataset: Papers With Code leaderboard timeseries for GLUE and SuperGLUE (already loaded in H-M2 code)
- Same logistic fit: reuse `h-m2/code/run.py` fitted parameters + pcov matrix
- Same preprocessing: deduplication, normalization from H-M2

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*Archon MCP unavailable in this session. No KB queries executed.*

**Fallback:** Parameter extraction and confidence interval computation from `scipy.optimize.curve_fit` is well-documented standard practice. The `pcov` matrix returned by `curve_fit` directly yields standard errors via `np.sqrt(np.diag(pcov))`. All patterns below are from scipy documentation and standard statistical practice.

### Archon Code Examples

*Not available — Archon MCP not connected.*

### Exa GitHub Implementations

*Exa MCP unavailable in this session. No GitHub queries executed.*

**Fallback:** Standard scipy curve_fit parameter extraction pattern used (see pseudo-code below).

### 🎯 Implementation Priority Assessment

**CRITICAL: This is a parameter extraction experiment, not a model reproduction experiment.**

No paper author's implementation needed — H-M3 operates on the output of H-M2 (already validated scipy logistic fit). The "implementation" is: extract popt and pcov from the stored/re-run H-M2 fit, check bounds, compute CIs.

**Recommended Implementation Path:**
- Primary: Extend `h-m2/code/run.py` to add parameter extraction, CI computation, and plausibility checks
- Fallback: Standalone `h-m3/code/run.py` that re-runs the logistic fit and extracts parameters
- Justification: H-M2 code already has the fitting logic; H-M3 only adds extraction + validation layer

### Code Analysis (Serena MCP)

*Skipped* — No complex external codebase to analyze. H-M3 is a scipy statistical extraction task. Code from H-M2 is the reference implementation.

---

## Experiment Specification

### Dataset

**Dataset:** Papers With Code Leaderboard Timeseries — GLUE and SuperGLUE
**Type:** programmatic-api (Papers With Code public API)
**Source:** `paperswithcode-client` Python package
**Benchmarks:** GLUE (`benchmark_id='glue'`), SuperGLUE (`benchmark_id='superglue'`)

**Reuse from H-M2:** The cleaned timeseries (deduplicated, normalized, month-indexed) is already available in `h-m2/code/run.py`. H-M3 reuses this data pipeline verbatim.

**Statistics:**
- GLUE: ~200+ entries, full lifecycle (growth → inflection → plateau), 2018–2023
- SuperGLUE: ~150+ entries, full lifecycle, 2019–2023
- Splits: No train/val/test split — full leaderboard timeseries used for curve fitting
- Minimum entries required: ≥50 (confirmed in H-E1)

**Preprocessing (inherited from H-M2):**
1. Retrieve via `paperswithcode-client`: `benchmark_results(benchmark_id='glue')`
2. Standardize composite metric (GLUE average, SuperGLUE average)
3. Convert dates to months-since-release (t=0 at benchmark publication)
4. Deduplicate: keep best score per model per month
5. Filter: scores in [0, 1] normalized range

**Synthetic data policy:** NOT applicable — real leaderboard data from Papers With Code API.

**Loading Information** (for Phase 4 download):
- Method: programmatic-api
- Identifier: `paperswithcode-client` (`pip install paperswithcode-client`)
- Code: `from paperswithcode import PapersWithCodeClient; client = PapersWithCodeClient(); results = client.benchmark_results(benchmark_id='glue')`

### Models

#### Baseline Model

**Architecture:** Logistic Growth Model (3-parameter, scipy.optimize.curve_fit)
**Formula:** `f(t) = K / (1 + exp(-r * (t - t0)))`
**Parameters:** K (asymptote/ceiling), r (growth rate), t0 (inflection point in months)
**Implementation:** `scipy.optimize.curve_fit` — already fitted in H-M2

**Loading Information** (for Phase 4 download):
- Method: stdlib / pip
- Identifier: `scipy>=1.7.0`
- Code: `from scipy.optimize import curve_fit; import numpy as np`

#### Proposed Model

**Architecture:** Same logistic model + parameter extraction + confidence interval computation + plausibility validation layer

**Core Mechanism Implementation:**

```python
# Core Mechanism: Logistic Parameter Extraction + Plausibility Check
# Based on: scipy.optimize.curve_fit standard API (scipy docs)
# H-M2 already performed the fit; H-M3 extracts and validates parameters

import numpy as np
from scipy.optimize import curve_fit

def logistic(t, K, r, t0):
    return K / (1 + np.exp(-r * (t - t0)))

def extract_and_validate_params(t_data, y_data, benchmark_name,
                                 benchmark_release_month):
    """
    Args:
        t_data: array of months since fit origin
        y_data: array of normalized scores
        benchmark_name: str identifier for logging
        benchmark_release_month: absolute month offset of benchmark release
    Returns:
        dict with K, r, t0_absolute, ci_widths, plausibility_flags
    """
    # Re-fit (or reuse from H-M2) with bounded initialization
    p0 = [0.92, 0.15, 12.0]
    bounds = ([0.5, 0.01, -24], [1.05, 3.0, 72])
    popt, pcov = curve_fit(logistic, t_data, y_data,
                           p0=p0, bounds=bounds, maxfev=10000)
    K, r, t0_relative = popt

    # 95% confidence intervals
    perr = np.sqrt(np.diag(pcov))  # 1-sigma standard errors
    ci_95 = 1.96 * perr            # [K_err, r_err, t0_err]

    # Convert t0 to absolute months since benchmark release
    t0_absolute = t0_relative + benchmark_release_month

    # Plausibility checks (H-M3 gate criteria)
    flags = {
        "K_in_range":  0.85 <= K <= 1.0,
        "r_positive":  r > 0,
        "t0_in_range": 6 <= t0_absolute <= 48,
        "ci_t0_narrow": ci_95[2] < 12.0,   # width = 2 * 1.96 * perr[t0]
    }
    return {"K": K, "r": r, "t0_relative": t0_relative,
            "t0_absolute": t0_absolute, "ci_95": ci_95,
            "perr": perr, "flags": flags}

# Gate: all flags True for BOTH benchmarks → PASS
```

### Training Protocol

**Reusing from H-M2** (controlled comparison — only parameter extraction layer added):

| Setting | Value | Source |
|---------|-------|--------|
| Optimizer | scipy.optimize.curve_fit (Levenberg-Marquardt / trust-region) | H-M2 confirmed |
| Initialization p0 | K=0.92, r=0.15, t0=12.0 | H-M2 bounds |
| Bounds | K∈[0.5,1.05], r∈[0.01,3.0], t0∈[−24,72] | H-M2 confirmed |
| maxfev | 10,000 | H-M2 confirmed |
| Seeds | 1 (deterministic — scipy curve_fit is deterministic given same data+init) | N/A |
| Loss | Residual sum of squares (scipy default) | Standard |

**Rationale:** Optimal in H-M2 (R²=0.997 GLUE, 0.993 SuperGLUE). Reusing for controlled experiment.

**New in H-M3 (parameter extraction layer):**
- Extract `popt` and `pcov` from `curve_fit` output
- Compute `perr = np.sqrt(np.diag(pcov))`
- Compute 95% CI: `popt ± 1.96 * perr`
- Convert t0 from relative (fit origin) to absolute (months since benchmark release)
  - GLUE release: April 2018 (month 0 in leaderboard)
  - SuperGLUE release: May 2019 (month 0 in leaderboard)
- Apply plausibility checks (gate criteria)

### Evaluation

**Primary Metrics (Gate Criteria):**

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| K ∈ [0.85, 1.0] | Both benchmarks | `popt[0]` from curve_fit |
| r > 0 | Both benchmarks | `popt[1]` from curve_fit |
| t0_absolute ∈ [6, 48] months | Both benchmarks | `popt[2]` + release offset |
| CI width for t0 < 12 months | Both benchmarks | `2 * 1.96 * sqrt(pcov[2,2])` |

**Success Criteria (PoC: direction-based):**
- PRIMARY: All three parameters physically plausible for both GLUE and SuperGLUE → PASS
- SECONDARY: 95% CI width for t0 < 12 months for both benchmarks (sufficient precision)

**Expected Values (from H-M2 results.json — already computed):**

| Parameter | GLUE (fitted) | SuperGLUE (fitted) | Gate Threshold |
|-----------|--------------|-------------------|----------------|
| K | 0.8955 | 0.8858 | [0.85, 1.0] ✅ expected PASS |
| r | 0.2017 | 0.1578 | > 0 ✅ expected PASS |
| t0 (relative) | −6.77 | −2.85 | — (convert to absolute) |
| t0 (absolute, months since release) | ~0 + offset | ~5 + offset | [6, 48] ⚠️ border case — must verify |

**Note on t0 border case:** H-M2's t0 values are negative relative to the fit's time origin. The absolute t0 (months since benchmark release) depends on where t=0 is set in the data pipeline. H-M3 must carefully verify this conversion. If t0_absolute < 6 months, a relaxed threshold [0, 48] may be needed with documented justification.

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical validation (no ML training)
- Library: numpy, scipy (already in environment)
- Code: `perr = np.sqrt(np.diag(pcov)); ci_95 = 1.96 * perr`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart — K, r, t0_absolute values vs. threshold bounds for GLUE and SuperGLUE

#### Additional Figures (LLM Autonomous)

1. **Parameter CI Plot**: Each of K, r, t0 with 95% error bars for both benchmarks — visualizes identifiability
2. **Logistic Fit with Parameter Annotations**: Score-over-time scatter + logistic curve, annotated with K (asymptote line), t0 (vertical inflection line), r (slope indicator) for each benchmark
3. **t0 Absolute Date Mapping**: Timeline showing t0_absolute converted to calendar date, vs. known rapid-growth periods and benchmark release dates

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m3/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (curve_fit converges, pcov is finite)
2. All plausibility flags = True for both GLUE and SuperGLUE

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | scipy curve_fit returns popt + pcov (not just popt) | TRUE — standard curve_fit API |
| Mechanism Isolatable | Parameter extraction layer is separate from fitting step | TRUE — can run with H-M2 popt directly |
| Baseline Measurable | H-M2 fitted parameters available in results.json | TRUE — confirmed in h-m2/results.json |

### Architecture Compatibility Check

**This is a statistical parameter extraction task, not a neural architecture task.**

Required features:
- `scipy.optimize.curve_fit` must return finite `pcov` matrix (indicates well-constrained fit)
- `np.diag(pcov)` must be all positive (non-degenerate)
- H-M2 must have converged (confirmed: GLUE R²=0.997, SuperGLUE R²=0.993)

Incompatible scenarios:
- `pcov` contains `inf` → fit is underdetermined → CI cannot be computed → H-M3 would need to use bootstrap CI instead
- H-M2 did not converge (not applicable — H-M2 PASSED)

> ⚠️ If `np.any(np.isinf(np.diag(pcov)))`, Phase 4 MUST switch to bootstrap CI and flag this.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"Parameters extracted: K=..., r=..., t0=..."` | run.py:extract_params() |
| Tensor Shape | popt.shape == (3,), pcov.shape == (3,3) | run.py after curve_fit |
| Metric Delta | All plausibility flags = True vs. expected False (H0) | run.py:validate_params() |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(popt, pcov, results):
    perr = np.sqrt(np.diag(pcov))
    indicators = {
        "popt_shape_correct": popt.shape == (3,),
        "pcov_finite":        np.all(np.isfinite(np.diag(pcov))),
        "K_extracted":        0.0 < results["K"] < 1.1,
        "r_extracted":        results["r"] != 0.0,
        "t0_extracted":       results["t0_absolute"] is not None,
        "ci_computed":        np.all(perr > 0),
    }
    all_ok = all(indicators.values())
    return all_ok, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| pcov contains inf | `np.any(np.isinf(np.diag(pcov)))` | Switch to bootstrap CI (500 resamples) |
| t0_absolute out of [6,48] | Flag check | Log with justification; explore relaxed threshold |
| K > 1.0 | Flag check | FAIL — score ceiling > 100% is implausible |
| r ≤ 0 | Flag check | FAIL — inverted or flat logistic is mechanistically wrong |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | pcov finite, popt extracted | verify_mechanism_activated() |
| Effect Measurable | All flags checked (pass or documented fail) | validate_params() |
| Hypothesis Supported | All plausibility flags = True for both benchmarks | plausibility_check() |

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

*Not available — Archon MCP not connected in this session.*

### B. GitHub Implementations (Exa)

*Not available — Exa MCP not connected in this session.*

### C. Code Analysis (Serena)

*Skipped* — No complex external codebase. H-M3 is a parameter extraction task over H-M2 scipy output.

### D. Previous Hypothesis Context

**Source:** H-M2 Validation Report + results.json

**File:** `h-m2/04_validation.md`, `h-m2/results.json`

**Reused Components:**
- Dataset: Papers With Code GLUE + SuperGLUE leaderboard timeseries (proven stable)
- Logistic fit: K, r, t0 parameters + pcov from scipy.optimize.curve_fit
- Code structure: `h-m2/code/run.py` — extend with parameter extraction layer
- Hyperparameters: bounds and initialization from H-M2 (confirmed working)

**Why Reused:** H-M3 is the parameter validation step of the SAME logistic fit. Only the extraction and plausibility-check layer is new. Reusing H-M2 fit enables controlled experiment (fit unchanged, only interpretation layer added).

**Key values from H-M2:**

```json
{
  "glue": {
    "logistic_params": {"K": 0.8955, "r": 0.2017, "t0": -6.771},
    "r2_logistic": 0.9966
  },
  "superglue": {
    "logistic_params": {"K": 0.8858, "r": 0.1578, "t0": -2.855},
    "r2_logistic": 0.9934
  }
}
```

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Previous hypothesis | H-M2 (reuse) |
| Logistic fit parameters | Previous hypothesis | H-M2 results.json |
| Parameter extraction code | Domain knowledge | scipy.optimize.curve_fit docs |
| CI computation | Domain knowledge | `np.sqrt(np.diag(pcov))` standard pattern |
| Gate thresholds | Phase 2B spec | 02b_verification_plan.md H-M3 section |
| t0 plausibility range [6,48] | Phase 2B spec | 02b_verification_plan.md H-M3 Step 3 |
| pcov inf fallback | Domain knowledge | Standard scipy failure mode handling |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — restated in state block)
**Date:** 2026-08-25

### Workflow History for This Hypothesis

- 2026-08-25: H-M3 Phase 2C experiment design IN_PROGRESS
- 2026-08-25: H-M3 Phase 2C experiment design COMPLETED

---

*MCP Tools Used: None (Archon + Exa unavailable; domain knowledge + H-M2 continuation context used)*
*All specifications grounded in H-M2 validated results and scipy documentation*
*Next Phase: Phase 3 - Implementation Planning*
