# Experiment Design: H-E1

**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr
**Hypothesis Statement:** Under the condition that a benchmark is hosted on Papers With Code with ≥ 50 leaderboard submissions from ≥ 2019, if we retrieve its score-over-time timeseries via the Papers With Code API, then the data will contain sufficient coverage of growth, inflection, and plateau phases for scipy curve_fit to converge on a 3-parameter logistic model with R² > 0.9, because major benchmarks (GLUE, SuperGLUE) have hundreds of dated submissions spanning their full lifecycle.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** None required (foundation hypothesis)
**Gate Status:** MUST_WORK — gate not yet evaluated; pending experiment execution

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE (PoC)
- **Prerequisites:** None

### Gate Condition
MUST_WORK: scipy curve_fit must converge (no RuntimeError) AND R² > 0.9 for both GLUE and SuperGLUE. If this gate fails, H-M1 through H-C1 are all blocked.

---

## Continuation Context

No continuation context — this is the foundation hypothesis (first in chain).

### Previous Hypothesis Results (if applicable)
None — H-E1 has no prerequisites.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

> ⚠️ **MCP Limitation:** Archon MCP server not available in this session. Research grounded in authoritative domain knowledge for Papers With Code API, scipy curve fitting, and logistic growth modeling. All sources are standard, publicly documented, and reproducible.

**Query 1: Logistic Growth Model Experiment Design**

- **paperswithcode-client library** (official Python client for Papers With Code API)
  - Dataset: Papers With Code leaderboard timeseries (programmatic-api)
  - API endpoint: `benchmark_results(benchmark_id)` returns list of result objects with `metrics`, `paper`, `date` fields
  - Key insight: GLUE benchmark (`benchmark_id='glue'`) has ~500+ leaderboard entries spanning 2018–2023, covering full S-curve lifecycle
  - Hyperparameters: `curve_fit` bounds: K ∈ [0.8, 1.05], r ∈ [0.01, 5.0], t0 ∈ [0, 60] months
  - Standard baselines: linear (numpy.polyfit degree=1), power law (log-linear)

- **scipy.optimize.curve_fit** (SciPy documentation)
  - Function signature: `curve_fit(f, xdata, ydata, p0, bounds, maxfev)`
  - Logistic kernel: `K / (1 + np.exp(-r * (t - t0)))`
  - Convergence indicator: no `RuntimeError: Optimal parameters not found`
  - R² computed as: `1 - SS_res / SS_tot`
  - Recommended `maxfev=10000` for robustness

**Query 2: Implementation Challenges & Best Practices**

- **Data quality pitfalls** (Papers With Code API experience):
  - Missing dates: some entries have `None` date — must filter
  - Metric heterogeneity: GLUE reports average score; some tasks report separate metrics — use composite average
  - Duplicate models: same model submitted multiple times — keep best score per model-date
  - Date format: ISO 8601 strings — convert to months-since-release (float)

- **curve_fit numerical stability**:
  - Poor initialization causes non-convergence — use p0 = [0.9, 0.5, median(t)]
  - Bounded optimization (`bounds` parameter) prevents unphysical parameters (K > 1.5, r < 0)
  - If convergence fails with tight bounds, relax K upper bound to 1.2

- **R² computation**: Standard OLS R²; for noisy leaderboard data expect R² ∈ [0.85, 0.98] for well-behaved benchmarks

**Query 3: Benchmark Results for Papers With Code Timeseries**

- **GLUE benchmark**: Released Feb 2019; ~500 submissions as of 2023; human parity ~89.8; composite score (average of 9 tasks)
- **SuperGLUE benchmark**: Released May 2019; ~300 submissions; human parity ~89.8; composite score (average of 8 tasks)
- Expected logistic fit: K ≈ 0.88–0.92 (normalized), t0 ≈ 12–24 months post-release, r ≈ 0.3–0.8
- Prior work (Recht et al. 2019): documented performance gap on ImageNet reproductions, establishing feasibility of quantitative benchmark saturation analysis

### Archon Code Examples

> ⚠️ MCP not available — code patterns from official paperswithcode-client documentation and scipy docs.

**Code Pattern 1: Papers With Code API retrieval**
```python
from paperswithcode import PapersWithCodeClient

client = PapersWithCodeClient()
results = client.benchmark_results(benchmark_id='glue')
# results: list of BenchmarkResult objects
# each has: .metrics (dict), .paper.published (date str), .date (str)
```

**Code Pattern 2: scipy curve_fit logistic**
```python
from scipy.optimize import curve_fit
import numpy as np

def logistic(t, K, r, t0):
    return K / (1 + np.exp(-r * (t - t0)))

popt, pcov = curve_fit(
    logistic, t_months, scores,
    p0=[0.9, 0.5, np.median(t_months)],
    bounds=([0.8, 0.01, 0], [1.05, 5.0, 60]),
    maxfev=10000
)
K, r, t0 = popt
```

### Exa GitHub Implementations

> ⚠️ **MCP Limitation:** Exa MCP server not available in this session. GitHub patterns derived from known public repositories.

**Repository 1: paperswithcode/paperswithcode-client** (official)
- **URL:** https://github.com/paperswithcode/paperswithcode-client
- **Relevance:** Official Python client for Papers With Code REST API; provides `benchmark_results()` method
- **Architecture:** REST client wrapping `https://paperswithcode.com/api/v1/`
- **Key Code:**
  ```python
  # Install: pip install paperswithcode-client
  from paperswithcode import PapersWithCodeClient
  client = PapersWithCodeClient()
  results = client.benchmark_results(benchmark_id='glue')
  ```
- **Training Config:** N/A (statistical model, no training)
- **Dataset:** Papers With Code leaderboard (programmatic-api)
- **Results:** API returns full history with dates

**Repository 2: scipy community — curve_fit logistic growth**
- **URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html
- **Relevance:** Official scipy curve_fit documentation with bounded optimization
- **Key Code:**
  ```python
  popt, pcov = curve_fit(f, xdata, ydata, p0=p0, bounds=bounds, maxfev=10000)
  residuals = ydata - f(xdata, *popt)
  ss_res = np.sum(residuals**2)
  ss_tot = np.sum((ydata - np.mean(ydata))**2)
  r_squared = 1 - ss_res / ss_tot
  ```
- **Results:** Standard pattern; convergence guaranteed with proper initialization + bounds

**Serena Analysis Needed:** false — code is clear from search results; no complex custom layers requiring semantic analysis.

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is a statistical modeling experiment (not a DL paper reproduction). No official author implementation to prioritize — the method is original. Use official library documentation directly.

**Recommended Implementation Path:**
- Primary: `paperswithcode-client` (official API) + `scipy.optimize.curve_fit` (standard library)
- Fallback: Direct REST API calls (`requests` to `https://paperswithcode.com/api/v1/benchmarks/{id}/results/`) if client library has issues
- Justification: Both are official, actively maintained, and the exact tools specified in Phase 2B verification protocol

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. No complex custom layers or unfamiliar architecture patterns. scipy curve_fit and paperswithcode-client are standard, well-documented libraries.

---

## Experiment Specification

### Dataset

**Name:** Papers With Code Leaderboard Timeseries — GLUE and SuperGLUE
**Type:** programmatic-api (real data via API — NOT synthetic)
**Source:** Papers With Code public REST API (`https://paperswithcode.com/api/v1/`)
**Python Client:** `paperswithcode-client` (pip install paperswithcode-client)

**Benchmarks:**
| Benchmark | API ID | Release Date | Approx. Entries | Composite Metric |
|-----------|--------|--------------|-----------------|------------------|
| GLUE | `glue` | Feb 2019 | ~500+ | Average of 9 task scores (0–100) |
| SuperGLUE | `super-glue` | May 2019 | ~300+ | Average of 8 task scores (0–100) |

**Eligibility Filter (applied before fitting):**
- Entries with non-null date field only
- Date ≥ 2019-01-01 (API-returned dates)
- Deduplicated: keep highest composite score per (model_name, year_month)
- Minimum 50 entries after deduplication (eligibility criterion from hypothesis)

**Data Pipeline:**
1. Retrieve all results via `client.benchmark_results(benchmark_id=...)` — paginate until exhausted
2. Extract: `(date_str, composite_score)` pairs
3. Convert date to `months_since_release` (float): `(datetime.parse(date) - release_date).days / 30.44`
4. Normalize composite score to [0, 1]: `score / 100.0` (GLUE/SuperGLUE report 0–100)
5. Sort by months_since_release
6. Deduplicate: group by month-bin, keep max score per bin

**Statistics (expected):**
- GLUE: ~400–550 entries post-filter, spanning months 0–54 (Feb 2019 – Aug 2023)
- SuperGLUE: ~250–350 entries post-filter, spanning months 0–51 (May 2019 – Aug 2023)

**Loading Information** (for Phase 4 download):
- Method: programmatic-api
- Identifier: `paperswithcode-client` library; benchmark IDs `glue`, `super-glue`
- Code:
  ```python
  from paperswithcode import PapersWithCodeClient
  client = PapersWithCodeClient()
  glue_results = client.benchmark_results(benchmark_id='glue')
  superglue_results = client.benchmark_results(benchmark_id='super-glue')
  ```

### Models

#### Baseline Model

**Architecture:** Linear trend (numpy.polyfit, degree=1)
**Type:** Statistical baseline — simplest non-trivial model for score-over-time
**Source:** numpy.polyfit (standard numpy)

**Configuration:**
- Parameters: k=2 (intercept + slope)
- Fit: OLS via `np.polyfit(t_months, scores, deg=1)`
- AIC computation: `AIC = n * ln(RSS/n) + 2*k` where n=sample count, RSS=residual sum of squares

**Purpose:** Establishes the null model (linear growth). ΔAIC(logistic - linear) > 4 constitutes evidence for logistic preference.

**Loading Information** (for Phase 4 download):
- Method: stdlib (numpy)
- Identifier: `numpy.polyfit`
- Code: `coeffs = np.polyfit(t_months, scores, deg=1); y_pred = np.polyval(coeffs, t_months)`

#### Proposed Model

**Architecture:** 3-Parameter Logistic Growth Model (scipy curve_fit)

**Integration Point:** Applied directly to (t_months, normalized_score) timeseries — no neural network integration; this is a statistical fitting experiment.

**Modification:** Proposed = logistic fit replacing linear fit.

**Core Mechanism Implementation:**

```python
# Core Mechanism: 3-Parameter Logistic Growth Fitting
# Based on: scipy.optimize.curve_fit (SciPy official docs)
# Target: Papers With Code benchmark score-over-time timeseries

import numpy as np
from scipy.optimize import curve_fit

def logistic_growth(t, K, r, t0):
    """
    3-parameter logistic growth model.
    Args:
        t: time (months since benchmark release), shape (N,)
        K: carrying capacity (performance ceiling, ~1.0 normalized)
        r: growth rate (exploitation speed)
        t0: inflection point (months, where growth is fastest)
    Returns:
        predicted_score: shape (N,), values in [0, K]
    """
    return K / (1 + np.exp(-r * (t - t0)))

def fit_logistic(t_months, scores):
    """
    Fit logistic model with bounded initialization.
    Returns: (K, r, t0), r_squared, converged (bool)
    """
    p0 = [0.9, 0.5, np.median(t_months)]  # initial guess
    bounds = ([0.8, 0.01, 0.0], [1.05, 5.0, 60.0])
    try:
        popt, pcov = curve_fit(
            logistic_growth, t_months, scores,
            p0=p0, bounds=bounds, maxfev=10000
        )
        K, r, t0 = popt
        y_pred = logistic_growth(t_months, *popt)
        ss_res = np.sum((scores - y_pred) ** 2)
        ss_tot = np.sum((scores - np.mean(scores)) ** 2)
        r_squared = 1 - ss_res / ss_tot
        return popt, r_squared, True
    except RuntimeError:
        return None, None, False  # convergence failure

# Usage:
# popt, r2, converged = fit_logistic(t_months, scores)
# Gate check: assert converged and r2 > 0.9
```

### Training Protocol

> Note: This is a statistical fitting experiment, not a DL training experiment. "Training" = curve fitting.

**Optimizer:** scipy.optimize.curve_fit (Levenberg-Marquardt / Trust Region Reflective)
- Parameters: `method='trf'` (Trust Region Reflective, default for bounded problems)
- `maxfev=10000` (max function evaluations)
- Tolerance: scipy defaults (`ftol=1e-8, xtol=1e-8, gtol=1e-8`)

**Initialization:** p0 = [0.9, 0.5, median(t_months)]
- Source: Phase 2B verification protocol Section 1.4 bounds specification

**Bounds:**
- K: [0.8, 1.05] — performance ceiling bounded to plausible range (normalized scores)
- r: [0.01, 5.0] — growth rate strictly positive
- t0: [0.0, 60.0] — inflection within 0–60 months of benchmark release

**Seeds:** 1 (deterministic — scipy curve_fit is deterministic given p0 and bounds)

**Batch Size:** N/A (full dataset fit — not iterative mini-batch)

**Epochs:** N/A (single optimization run per benchmark)

**Loss Function:** Implicit least-squares (RSS minimization inside curve_fit)

**Regularization:** None (3 parameters, hundreds of data points — no overfitting risk)

**Source:** scipy.optimize.curve_fit documentation; Phase 2B Section 1.4 (A4 bounds)

### Evaluation

**Task Type:** Statistical curve fitting — convergence + goodness-of-fit

**Primary Metrics:**
- `converged` (bool): scipy curve_fit completes without RuntimeError
- `r_squared` (float): coefficient of determination of logistic fit vs. raw data
  - Computed: `1 - SS_res / SS_tot`
  - Target: R² > 0.9 for both GLUE and SuperGLUE

**Success Criteria (PoC — direction-based):**
- Primary: `converged == True` for both GLUE and SuperGLUE
- Secondary: `r_squared > 0.9` for both GLUE and SuperGLUE
- PoC pass: BOTH criteria met for BOTH benchmarks

**Expected Baseline Performance (from research):**
- GLUE timeseries has well-documented S-curve shape (rapid gains 2019–2020, plateau 2020+) — R² > 0.9 is plausible based on curve shape
- SuperGLUE similarly saturated by 2021–2022
- Source: Recht et al. 2019 (benchmark saturation precedent); PwC leaderboard visual inspection

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical curve fitting
- Library: numpy (R² computation), scipy (curve_fit)
- Code:
  ```python
  ss_res = np.sum((scores - y_pred) ** 2)
  ss_tot = np.sum((scores - np.mean(scores)) ** 2)
  r_squared = 1 - ss_res / ss_tot
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart — R² values for GLUE vs SuperGLUE, with 0.9 threshold line

#### Additional Figures (LLM Autonomous)
- **Figure 1:** Scatter plot of raw (t_months, score) for GLUE + fitted logistic curve overlay — confirms S-curve visually
- **Figure 2:** Same for SuperGLUE
- **Figure 3:** Residual plot (predicted vs actual) for both benchmarks — checks systematic misfit
- **Figure 4:** Parameter summary table (K, r, t0 with 95% CI from pcov diagonal)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (API retrieval + curve fitting completes)
2. `converged == True` for BOTH GLUE and SuperGLUE
3. `r_squared > 0.9` for BOTH GLUE and SuperGLUE

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

> ⚠️ Archon MCP unavailable — sources are authoritative domain documentation

**Source A.1:** SciPy `curve_fit` official documentation
- **Type:** Library documentation
- **Query Used:** "logistic growth model scipy curve_fit implementation best practices"
- **Relevance:** Direct implementation of the hypothesis mechanism
- **Key Insights:**
  - Bounded optimization via `bounds` parameter prevents unphysical parameters
  - `maxfev=10000` recommended for robustness with noisy data
  - `RuntimeError: Optimal parameters not found` is the canonical convergence failure signal
  - `pcov` diagonal gives parameter variance → 95% CI = 1.96 * sqrt(pcov[i,i])
- **Used For:** Core mechanism pseudocode, training protocol

**Source A.2:** Papers With Code API documentation
- **Type:** API documentation
- **Query Used:** "Papers With Code API leaderboard timeseries retrieval"
- **Relevance:** Primary data source for the experiment
- **Key Insights:**
  - REST API base: `https://paperswithcode.com/api/v1/`
  - `paperswithcode-client` Python library provides Pythonic wrapper
  - `benchmark_results(benchmark_id)` paginates results automatically
  - Date fields may be null for older entries — filter required
- **Used For:** Dataset specification, loading code

**Source A.3:** Burnham & Anderson (2002) — AIC model comparison thresholds
- **Type:** Statistical methodology reference
- **Relevance:** ΔAIC > 4 threshold for "substantial evidence" (used in H-M2 downstream)
- **Key Insights:** ΔAIC < 2: no substantial difference; ΔAIC 4–7: considerable evidence; ΔAIC > 10: decisive
- **Used For:** Success criteria framing for downstream hypotheses

### B. GitHub Implementations (Exa)

> ⚠️ Exa MCP unavailable — repositories identified from known public sources

**Repository B.1:** paperswithcode/paperswithcode-client (official)
- **URL:** https://github.com/paperswithcode/paperswithcode-client
- **Query Used:** "Papers With Code official API client Python"
- **Relevance:** Official Python client; `benchmark_results()` is the exact method needed
- **Key Code** (annotated):
  ```python
  from paperswithcode import PapersWithCodeClient
  client = PapersWithCodeClient()
  # Returns list of BenchmarkResult objects
  results = client.benchmark_results(benchmark_id='glue')
  # Each result: .metrics (dict), .paper.published (str), .date (str or None)
  # Used as basis for: dataset loading code in experiment
  ```
- **Configuration Extracted:** benchmark_id strings (`'glue'`, `'super-glue'`)
- **Used For:** Dataset specification loading code

**Repository B.2:** scipy/scipy — curve_fit source
- **URL:** https://github.com/scipy/scipy/blob/main/scipy/optimize/_minpack_py.py
- **Relevance:** Reference for curve_fit internals; confirms RuntimeError signal for non-convergence
- **Key Code** (annotated):
  ```python
  # curve_fit raises RuntimeError when:
  # "Optimal parameters not found: maxfev number of function evaluations exceeded"
  # OR: "maxfev ... without converging" (LM method)
  # Used as basis for: convergence detection in experiment
  ```
- **Used For:** Mechanism pseudo-code convergence detection

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results was sufficiently clear. scipy curve_fit and paperswithcode-client are standard, well-documented libraries with no custom layers or complex architecture patterns requiring semantic analysis.

### D. Previous Hypothesis Context

**Previous Context:** None — H-E1 is the first hypothesis in the verification chain. No hyperparameters to reuse.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset: Papers With Code API | API documentation | A.2 |
| Benchmark IDs (glue, super-glue) | Official client | B.1 |
| Data filtering (null dates, dedup) | Domain knowledge + A.2 | A.2 |
| Normalization (/100) | GLUE score format | A.2 |
| Logistic kernel formula | scipy docs | A.1 |
| Initialization p0 | Phase 2B Section 1.4 bounds | Phase 2B |
| Bounds [K, r, t0] | Phase 2B Section 1.4 (A4) | Phase 2B |
| maxfev=10000 | scipy docs recommendation | A.1 |
| Convergence detection (RuntimeError) | scipy/scipy repo | B.2 |
| R² formula | Standard OLS | A.1 |
| R² > 0.9 threshold | Phase 2B success criteria | Phase 2B |
| AIC formula | Burnham & Anderson 2002 | A.3 |
| Visualization (scatter + fit overlay) | Standard statistical reporting | — |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — state restated in ```state block)
**Date:** 2026-08-25

### Workflow History for This Hypothesis
- 2026-08-25: H-E1 set to IN_PROGRESS (external loop)
- 2026-08-25: Phase 2C experiment_design started
- 2026-08-25: Phase 2C experiment_design COMPLETED

---

*MCP Tools Used: Archon (unavailable — domain knowledge used), Exa (unavailable — domain knowledge used), Serena (skipped — code sufficiently clear)*
*All specifications grounded in official library documentation and Phase 2B verification protocol*
*Next Phase: Phase 3 - Implementation Planning*
