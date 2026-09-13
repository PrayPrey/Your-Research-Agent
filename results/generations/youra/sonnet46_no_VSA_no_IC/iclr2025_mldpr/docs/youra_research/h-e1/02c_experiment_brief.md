# Experiment Design: H-E1

**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr
**Hypothesis Statement:** Under PwC N=111 benchmark data, PELT change-point detection on linearly detrended residual CoV sorted by paper_count detects a statistically significant structural break (paper_count*), confirmed by permutation test p < 0.05 and paper_count* ∈ [10, 120].
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** N/A (H-E1 is root hypothesis — no prerequisites)
**Gate Status:** MUST_WORK (permutation p < 0.05 AND paper_count* ∈ [10, 120])

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (root hypothesis)

### Gate Condition

MUST_WORK: Permutation test p < 0.05 AND paper_count* ∈ [10, 120].
- FAIL action: STOP pipeline; publish null result (H0 supported: rho=−0.28 smooth monotonic is the best description)

---

## Continuation Context

First hypothesis in chain — no continuation context.

### Previous Hypothesis Results (if applicable)

None — H-E1 is the foundation hypothesis. All downstream hypotheses (H-M1, H-M2, H-M3) depend on paper_count* produced here.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Assessment:** Archon KB does not contain domain-relevant content for PELT change-point detection or PwC benchmark analysis. All queries returned HuggingFace diffusion model content (similarity ~0.28–0.42). No usable findings extracted.

**Queries executed:**
- Query 1: "PELT change-point detection experiment design" → irrelevant (diffusion models)
- Query 2: "change-point detection implementation challenges best practices" → irrelevant
- Query 3: "benchmark saturation CoV analysis" → irrelevant

### Archon Code Examples

**Assessment:** No relevant code examples found in Archon KB for this domain.

**Queries executed:**
- "PELT ruptures change-point PyTorch" → irrelevant (AnimateDiff pipeline benchmarking)
- "permutation test statistical significance Python" → irrelevant (Python version display, incidence matrix)

**Conclusion:** Archon KB is specialized for image generation/diffusion models. All experiment specifications derived from Exa GitHub search (authoritative source: deepcharles/ruptures + scipy documentation).

### Exa GitHub Implementations

**Query 1: ruptures PELT — Author's Official Implementation**

**Repository 1:** deepcharles/ruptures (⭐ 2K)
- **URL:** https://github.com/deepcharles/ruptures
- **Relevance:** PRIMARY — the canonical PELT change-point detection library used in H-E1 protocol
- **Architecture:** Off-line penalized change-point detection with L2 cost function
- **Key Code:**
  ```python
  import ruptures as rpt

  # Fit PELT with L2 cost (mean-shift detection)
  algo = rpt.Pelt(model="l2", min_size=3, jump=1).fit(signal)
  bkps = algo.predict(pen=bic_penalty)
  # bkps is a list of breakpoint indexes (last = n_samples by convention)
  ```
- **BIC Penalty Formula (from author's Issue #4 + Discussion #166):**
  ```python
  # For L2 cost with Gaussian signal:
  T = len(signal)
  sigma = signal.std()
  bic_penalty = sigma**2 * np.log(T)  # 1D signal, d=1
  ```
- **Elbow method for penalty tuning:**
  ```python
  pen_values = np.logspace(0, 3, 10)
  algo = rpt.Pelt(model="l2", min_size=3).fit(signal)
  bkps_list = [algo.predict(pen=p) for p in pen_values]
  # inspect where number of breakpoints stabilizes
  ```
- **Key findings:**
  - `min_size=3` recommended (per VPWBS arXiv:1906.11364 for N~100)
  - `jump=1` for small signals (N=111) — no subsampling
  - L2 cost detects mean shifts in residual CoV after detrending
  - BIC tends to underpenalize — elbow/sensitivity range [1,50] needed

**Repository 2:** scipy (permutation_test + bootstrap)
- **URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html
- **Relevance:** Permutation test for H-E1 validation and bootstrap CI for paper_count*
- **Key Code:**
  ```python
  from scipy.stats import permutation_test, bootstrap

  # Permutation test: shuffle paper_count labels, rerun PELT
  # Statistic: number of change-points detected (or position of first bkp)
  def pelt_statistic(cov_vals, paper_counts):
      sorted_idx = np.argsort(paper_counts)
      signal = cov_vals[sorted_idx]
      # detrend
      residuals = detrend_ols(signal, paper_counts[sorted_idx])
      algo = rpt.Pelt(model="l2", min_size=3, jump=1).fit(residuals)
      bkps = algo.predict(pen=bic_penalty)
      return bkps[0] if len(bkps) > 1 else len(signal)  # first breakpoint index

  # Bootstrap CI for paper_count*
  res = bootstrap((cov_array,), lambda x: pelt_statistic(x, paper_counts),
                  n_resamples=1000, method='percentile', confidence_level=0.95)
  ```

**Query 2: PwC data loading — existing codebase**

**Repository (local archive):** existing h-e1/code/ingest_pwc.py
- **URL:** Local codebase (confirmed working from H-E1 v2)
- **Relevance:** HIGHEST — exact data loading pipeline already exists; reuse directly
- **HuggingFace identifier:** `pwc-archive/evaluation-tables`
- **Key Code:**
  ```python
  from datasets import load_dataset
  ds = load_dataset("pwc-archive/evaluation-tables", split="train")
  # derive.py: compute_result_cov() produces result_CoV per benchmark
  # paper_count derived from len(unique paper_titles) per benchmark
  ```
- **N=111 benchmarks:** benchmarks with paper_count >= MIN_PAPERS (confirmed working)

**Serena Analysis Needed:** false — code is clear from Exa + existing archive

### 🎯 Implementation Priority Assessment

**CRITICAL: For statistical analysis experiments, data pipeline takes priority over model implementation**

Baseline experiment uses existing `ingest_pwc.py` + `derive.py` pipeline (confirmed working from archive).

**Recommended Implementation Path:**
- Primary: Reuse existing `ingest_pwc.py` / `derive.py` from archive (confirmed working, returns N=111 benchmarks with CoV + paper_count)
- Fallback: Fresh load from `pwc-archive/evaluation-tables` on HuggingFace
- Justification: Archive pipeline confirmed working; avoids re-implementing ingestion logic

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. ruptures PELT API is clean and well-documented. scipy permutation_test and bootstrap are standard. Existing archive pipeline (ingest_pwc.py, derive.py) provides working data loading.

---

## Experiment Specification

### Dataset

**Name:** PwC Leaderboard Benchmark Data — CoV + paper_count series
**Type:** standard (real data from paperswithcode/paperswithcode-data, 932 stars)
**Source:** HuggingFace dataset `pwc-archive/evaluation-tables`
**N:** 111 benchmarks (benchmarks with paper_count ≥ MIN_PAPERS and CoV computable from ≥ 3 result rows)
**Variables:**
- `paper_count`: count of unique papers per benchmark (integer, range ~5–500+)
- `result_CoV`: coefficient of variation of metric_value per benchmark (float, computed by `derive.py::compute_result_cov()`)
- `residual_CoV`: OLS-detrended CoV (CoV regressed on paper_count; residuals used as PELT input)

**Preprocessing:**
1. Load `pwc-archive/evaluation-tables` via HuggingFace datasets
2. Filter: benchmarks with ≥ 3 result rows for CoV computation
3. Filter: benchmarks with ≥ MIN_PAPERS unique paper titles
4. Compute `result_CoV = std(metric_value, ddof=1) / mean(metric_value)` per benchmark
5. Fit OLS: `result_CoV ~ paper_count`; extract residuals → `residual_CoV`
6. Sort `residual_CoV` ascending by `paper_count` → PELT input series

**Splits:** Not applicable — N=111 is the full analysis set (no train/val/test split; this is a statistical analysis, not a supervised ML task)

**Path specification:** `programmatic-api` — load from HuggingFace at runtime; reuse existing `ingest_pwc.py`

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `pwc-archive/evaluation-tables`
- Code: `load_dataset("pwc-archive/evaluation-tables", split="train")`

### Models

#### Baseline Model

**Architecture:** OLS Linear Regression (CoV ~ paper_count, no change-point)
**Type:** Statistical model (scipy.stats.linregress / statsmodels OLS)
**Source:** scipy.stats, statsmodels — standard library

**Configuration:**
- Model: `CoV = β₀ + β₁ * paper_count + ε`
- Fit: OLS via `scipy.stats.linregress(paper_count, result_CoV)`
- Output: residuals (used as PELT input), rho, R²
- Baseline performance from prior work: rho=−0.28, R²≈0.08 (explains ~8% variance)
- Interpretation: smooth monotonic trend model (null hypothesis H0)

**Loading Information** (for Phase 4 download):
- Method: scipy stdlib (no download needed)
- Identifier: `scipy.stats.linregress`
- Code: `from scipy.stats import linregress; slope, intercept, r, p, se = linregress(paper_count, cov)`

#### Proposed Model

**Architecture:** Baseline (OLS detrending) + PELT Change-Point Detection

**Core Mechanism Implementation:**

```python
# Core Mechanism: PELT Change-Point Detection on Residual CoV
# Based on: deepcharles/ruptures (2K stars, arXiv:1801.00826)
# Reference: Killick et al. (2012) JASA 107(500):1590-1598

import numpy as np
import ruptures as rpt
from scipy.stats import linregress

def run_pelt_changepoint(paper_counts: np.ndarray,
                          cov_values: np.ndarray,
                          pen_range: tuple = (1, 50),
                          n_pen: int = 20,
                          min_size: int = 3) -> dict:
    """
    Args:
        paper_counts: (N,) array of paper counts per benchmark
        cov_values:   (N,) array of CoV values per benchmark
    Returns:
        dict with keys: paper_count_star, breakpoint_idx, pen_used, n_bkps
    """
    # Step 1: Sort by paper_count ascending (required for cross-sectional series)
    sort_idx = np.argsort(paper_counts)
    sorted_pc = paper_counts[sort_idx]
    sorted_cov = cov_values[sort_idx]

    # Step 2: OLS detrend to remove global monotonic component
    slope, intercept, _, _, _ = linregress(sorted_pc, sorted_cov)
    residual_cov = sorted_cov - (slope * sorted_pc + intercept)

    # Step 3: BIC penalty + elbow sweep for robustness
    T = len(residual_cov)
    sigma = residual_cov.std(ddof=1)
    bic_pen = sigma**2 * np.log(T)  # L2 cost BIC formula (1D)

    pen_values = np.logspace(np.log10(pen_range[0]),
                              np.log10(pen_range[1]), n_pen)
    algo = rpt.Pelt(model="l2", min_size=min_size, jump=1).fit(residual_cov)
    bkps_list = [algo.predict(pen=p) for p in pen_values]

    # Step 4: Select pen via elbow (stability across range)
    pen_used = bic_pen  # primary; elbow as sensitivity check
    bkps = algo.predict(pen=pen_used)

    # paper_count* = paper_count at breakpoint index
    bkp_idx = bkps[0] - 1 if len(bkps) > 1 else None
    paper_count_star = sorted_pc[bkp_idx] if bkp_idx is not None else None

    return {
        "paper_count_star": paper_count_star,
        "breakpoint_idx": bkp_idx,
        "pen_used": pen_used,
        "n_bkps": len(bkps) - 1,  # last element = n_samples by convention
        "residual_cov_sorted": residual_cov,
        "sorted_paper_counts": sorted_pc,
    }

# Integration: Standalone analysis function (no neural network integration)
```

### Training Protocol

**Note:** H-E1 is a statistical analysis, not a supervised ML training experiment. No optimizer, learning rate, or epochs apply. The "training protocol" is the statistical analysis pipeline.

**Analysis Protocol:**

**Step 1 — Data Loading:**
- Library: HuggingFace `datasets`
- Code: `load_dataset("pwc-archive/evaluation-tables", split="train")`
- Reuse: existing `ingest_pwc.py::fetch_pwc_benchmarks()` and `derive.py::compute_result_cov()`
- **Source:** Archive codebase (confirmed working)

**Step 2 — OLS Detrending:**
- Library: `scipy.stats.linregress`
- Input: `(paper_count, result_CoV)` pairs, N=111
- Output: `residual_CoV` (remove global rho=−0.28 trend)
- **Source:** Phase 2B verification protocol + scipy docs

**Step 3 — BIC Penalty Tuning:**
- Formula: `pen = σ² * log(T)` where σ = std(residual_CoV), T = N
- Sensitivity sweep: `np.logspace(0, np.log10(50), 20)` → elbow plot
- **Source:** ruptures Issue #4 (author Charles Truong); Discussion #166

**Step 4 — PELT Detection:**
- Library: `ruptures` (deepcharles/ruptures, 2K stars)
- Config: `rpt.Pelt(model="l2", min_size=3, jump=1).fit(residual_cov_sorted)`
- Call: `.predict(pen=bic_pen)` → list of breakpoint indexes
- **Source:** deepcharles/ruptures pelt.py (Killick et al. 2012)

**Step 5 — Permutation Test (p-value):**
- Library: `scipy.stats` (manual loop preferred for transparency)
- N_permutations: 1000
- Statistic: position of first detected breakpoint (paper_count index)
- Null: shuffle `paper_count` labels (randomize assignment), rerun PELT
- p-value: fraction of null-distribution statistics ≤ observed statistic
- **Source:** scipy.stats.permutation_test documentation; RESPERM paper (Konczak 2022)

**Step 6 — Bootstrap CI for paper_count*:**
- N_resamples: 1000
- Method: percentile bootstrap (resample benchmarks with replacement)
- CI: 95% (check width ≤ 20 papers for reliability)
- **Source:** scipy.stats.bootstrap documentation

**Step 7 — Piecewise Linear Regression F-test (independent check):**
- Library: `statsmodels`
- Model: piecewise linear regression at detected paper_count*
- Test: F-test for improvement over single linear model
- **Source:** Phase 2B verification protocol

**Seed:** 42 (single fixed seed for permutation and bootstrap sampling)

### Evaluation

**Task Type:** Statistical hypothesis test (binary pass/fail gate)

**Primary Metrics:**

| Metric | Definition | Success |
|--------|-----------|---------|
| `permutation_p` | Fraction of 1000 null-permutation PELT runs detecting breakpoint ≤ observed | < 0.05 |
| `paper_count_star` | paper_count value at detected breakpoint (sorted_pc[bkp_idx]) | ∈ [10, 120] |

**Secondary Metrics (not gating):**

| Metric | Definition | Goal |
|--------|-----------|------|
| `bootstrap_ci_width` | 95% CI upper − lower for paper_count* | ≤ 20 papers |
| `n_bkps_detected` | Number of PELT-detected breakpoints | 1 (parsimony) |
| `piecewise_f_p` | F-test p-value for piecewise regression improvement | < 0.05 (independent confirmation) |

**Success Criteria (PoC — EXISTENCE):**
- **PASS:** `permutation_p < 0.05` AND `paper_count_star ∈ [10, 120]`
- **FAIL → STOP:** publish null result; H0 (smooth monotonic rho=−0.28) is supported
- PoC success = mechanism detectable + plausible range (no statistical test beyond permutation)

**Expected Baseline Performance (from prior work):**
- OLS linear model: rho=−0.28, R²≈0.08 (H-E1 v2 confirmed)
- No prior work has applied PELT to this series → no expected paper_count* range from literature

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical hypothesis testing
- Library: `scipy.stats` (permutation, bootstrap); `statsmodels` (OLS, piecewise regression)
- Code: `from scipy.stats import linregress, permutation_test, bootstrap; import statsmodels.api as sm`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing `permutation_p` vs threshold 0.05, and `paper_count_star` vs range [10, 120]

#### Additional Figures (LLM Autonomous)

Based on this statistical analysis, the following figures are most informative:

1. **CoV vs paper_count scatter** with detected breakpoint paper_count* marked (vertical dashed line), OLS trend line overlaid
2. **Residual CoV series** (sorted by paper_count) with PELT segmentation displayed (alternating shading for pre/post regimes)
3. **Permutation null distribution** histogram showing null breakpoint positions, with observed paper_count* marked
4. **Bootstrap CI plot** for paper_count* (distribution of 1000 bootstrap estimates + 95% CI bounds)
5. **Penalty sensitivity** plot: number of breakpoints detected vs penalty value (log scale), showing stability at BIC penalty

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (full pipeline: ingest → derive → detrend → PELT → permutation test)
2. `permutation_p < 0.05` AND `paper_count_star ∈ [10, 120]`

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | PELT is applicable to 1D residual CoV series of length N=111 (confirmed: min_size=3 ≤ N/3) | TRUE |
| Mechanism Isolatable | Baseline (OLS only, no PELT) vs. proposed (OLS + PELT) can be run independently; permutation null provides explicit mechanism-off distribution | TRUE |
| Baseline Measurable | OLS linear model (rho=−0.28, R²=0.08) is the confirmed baseline; measurable from derive.py output | TRUE |

### Architecture Compatibility Check

**Statistical analysis — no neural network architecture.** PELT requires:
- 1D input signal (residual_CoV after OLS detrending): ✅ produced by existing derive.py
- N ≥ min_size * 2 (N=111 >> 6): ✅
- Signal must have finite variance (result_CoV is bounded 0-∞, but finite for N=111 filtered benchmarks): ✅
- L2 cost function: appropriate for mean-shift detection in residual series: ✅

**Incompatible scenarios:**
- If N < 10 after filtering: FAIL early (insufficient data for min_size=3)
- If all CoV values are identical (zero variance): FAIL early (no signal for PELT)

> ⚠️ If N < 10 after filtering, Phase 4 MUST fail early with clear error message.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"PELT detected {n} breakpoint(s) at index {bkp_idx} → paper_count* = {val}"` | `pipeline.py:run_pelt_changepoint()` |
| Output Value | `paper_count_star` is not None and ∈ [10, 120] | `results dict["paper_count_star"]` |
| Metric Delta | `permutation_p < 0.05` (null has no consistent breakpoint, observed does) | `evaluate.py:run_permutation_test()` |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(results: dict) -> tuple[bool, dict]:
    """Verify PELT change-point detection mechanism actually fired."""
    indicators = {
        "pelt_detected_breakpoint": results.get("n_bkps_detected", 0) >= 1,
        "paper_count_star_in_range": (
            results.get("paper_count_star") is not None and
            10 <= results["paper_count_star"] <= 120
        ),
        "permutation_p_significant": results.get("permutation_p", 1.0) < 0.05,
    }
    all_pass = all(indicators.values())
    if not all_pass:
        print(f"MECHANISM VERIFICATION FAILED: {indicators}")
    else:
        print(f"MECHANISM VERIFIED: paper_count* = {results['paper_count_star']}, p = {results['permutation_p']:.4f}")
    return all_pass, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| No breakpoint detected | `n_bkps_detected == 0` or `bkps == [N]` | FAIL: PELT returns no internal break; H0 supported |
| paper_count* out of range | `paper_count_star < 10 or > 120` | FAIL: boundary artifact, not regime shift |
| p ≥ 0.05 | `permutation_p >= 0.05` | FAIL: not statistically significant; H0 supported |
| N too small | N < 10 after filtering | FAIL EARLY: insufficient data |
| Zero signal variance | `residual_cov.std() == 0` | FAIL EARLY: degenerate input |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | n_bkps_detected ≥ 1 | `results["n_bkps_detected"]` |
| Effect Measurable | paper_count* is not None | `results["paper_count_star"] is not None` |
| Hypothesis Supported | permutation_p < 0.05 AND paper_count* ∈ [10, 120] | Primary gate metrics |

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Assessment:** No relevant sources found in Archon KB for this domain. All queries returned HuggingFace diffusion model content (similarity 0.28–0.42, irrelevant). Archon KB is specialized for image generation. Zero sources used from Archon for specifications.

### B. GitHub Implementations (Exa)

**Repository 1:** deepcharles/ruptures (⭐ 2,000)
- **URL:** https://github.com/deepcharles/ruptures
- **Query Used:** "ruptures PELT change-point detection Python implementation GitHub"
- **Relevance:** PRIMARY — canonical PELT library; exact implementation used in H-E1 protocol
- **Key Code (annotated):**
  ```python
  # From src/ruptures/detection/pelt.py (master branch)
  # PELT algorithm: O(CKN) average complexity (Killick et al. 2012)
  algo = rpt.Pelt(model="l2", min_size=3, jump=1).fit(residual_cov)
  # model="l2": L2 cost function (sum of squared residuals) — detects mean shifts
  # min_size=3: minimum segment length (per VPWBS recommendation for N~100)
  # jump=1: no subsampling (important for N=111 — don't miss breakpoints)
  bkps = algo.predict(pen=bic_penalty)
  # Returns: list of breakpoint indexes, last element = N (convention)
  # paper_count* = sorted_paper_counts[bkps[0] - 1]
  ```
- **BIC Penalty (from author Issue #4):**
  ```python
  # For L2 cost, Gaussian signal assumption:
  bic_penalty = sigma**2 * np.log(T)  # sigma = residual std, T = N=111
  ```
- **Configuration Extracted:** min_size=3, jump=1, model="l2", pen=BIC
- **Their Results:** N/A (library, no benchmark results)
- **Used For:** Core mechanism pseudo-code (Step 3 in analysis protocol), penalty specification

**Repository 2:** scipy/scipy — permutation_test + bootstrap
- **URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html
- **Query Used:** "permutation test change-point detection bootstrap confidence interval Python scipy"
- **Relevance:** Steps 5–6 of analysis protocol (significance testing, CI estimation)
- **Key Code (annotated):**
  ```python
  # scipy.stats.bootstrap for paper_count* CI
  # n_resamples=1000, method='percentile', confidence_level=0.95
  # Resample benchmarks WITH replacement, rerun PELT each time
  # CI width check: upper - lower <= 20 papers (reliability criterion from Phase 2B)
  ```
- **Configuration Extracted:** n_resamples=1000, method='percentile', seed=42
- **Used For:** Permutation test (Step 5), Bootstrap CI (Step 6)

**Repository 3:** Local archive — ingest_pwc.py + derive.py
- **URL:** docs/youra_research/_archive/20260821T055106_routing_recovery/h-e1/code/
- **Query Used:** codebase search via Bash
- **Relevance:** HIGHEST — existing working data pipeline; confirmed N=111 benchmark output
- **Key Code (annotated):**
  ```python
  # ingest_pwc.py: loads pwc-archive/evaluation-tables from HuggingFace
  ds = load_dataset("pwc-archive/evaluation-tables", split="train")
  # → DataFrame: name, paper_count, year_introduced, dataset_name, task_name

  # derive.py: compute_result_cov() — produces result_CoV per benchmark
  def cov(vals):
      vals = vals.dropna()
      if len(vals) < 3: return float("nan")
      return vals.std(ddof=1) / vals.mean()  # unbiased std / mean
  ```
- **Used For:** Dataset loading specification (Step 5a-b), confirming N=111 is achievable

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results (ruptures + scipy) and existing archive was sufficiently clear. No complex unfamiliar architecture patterns requiring semantic analysis.

### D. Previous Hypothesis Context

**Previous Context:** None — H-E1 is the first hypothesis in the verification chain (root node). No prior validation reports to inherit from.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset: pwc-archive/evaluation-tables | Local archive | ingest_pwc.py (confirmed working) |
| N=111 benchmark size | Phase 2B plan | 02b_verification_plan.md §1.3 |
| CoV computation (ddof=1) | Local archive | derive.py::compute_result_cov() |
| OLS detrending (baseline) | Phase 2B plan | 02b_verification_plan.md §2.2 H-E1 protocol step 2 |
| PELT model="l2" | GitHub Exa | deepcharles/ruptures (B.1) |
| min_size=3 | Phase 2B plan + ruptures docs | 02b_verification_plan.md + centre-borelli docs |
| jump=1 | ruptures docs | PELT docs (small N=111, no subsampling) |
| BIC penalty formula | GitHub Exa | ruptures Issue #4, Discussion #166 (B.1) |
| pen sensitivity [1,50] | Phase 2B plan | 02b_verification_plan.md §2.2 H-E1 step 3 |
| Permutation test N=1000 | Phase 2B plan | 02b_verification_plan.md §2.2 H-E1 step 5 |
| Bootstrap CI N=1000 | Phase 2B plan | 02b_verification_plan.md §2.2 H-E1 step 5 |
| Success: p < 0.05, paper_count* ∈ [10,120] | Phase 2B plan | 02b_verification_plan.md §2.2 H-E1 success criteria |
| paper_count* CI width ≤ 20 | Phase 2B plan | 02b_verification_plan.md §4.1 Risk R2 mitigation |
| Piecewise regression F-test | Phase 2B plan | 02b_verification_plan.md §2.2 H-E1 protocol step 5 |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — not written directly)
**Date:** 2026-08-21

### Workflow History for This Hypothesis

- 2026-08-21T09:40:09Z: H-E1 set to IN_PROGRESS (external loop starting Phase 2C → 3 → 4)
- 2026-08-21: Phase 2C experiment_design.status = COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code — no domain match), Exa (GitHub — ruptures, scipy, local archive)*
*All specifications grounded in researched implementations: deepcharles/ruptures (2K★), scipy official docs, confirmed working local pipeline*
*Next Phase: Phase 3 - Implementation Planning*
