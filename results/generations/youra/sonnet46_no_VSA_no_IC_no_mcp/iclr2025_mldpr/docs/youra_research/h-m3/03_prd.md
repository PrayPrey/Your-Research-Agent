# Product Requirements Document: H-M3

---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7]
hypothesis_id: H-M3
type: MECHANISM
tier: FULL
created_at: 2026-08-25
author: yoon303@ust.ac.kr
---

## 1. Executive Summary

H-M3 validates that the logistic model parameters (K, r, t0) fitted in H-M2 are physically interpretable and plausible. This is a parameter extraction and statistical validation experiment — not a new model training experiment. It reuses the H-M2 logistic fit (scipy.optimize.curve_fit) and adds a parameter extraction layer with 95% confidence interval computation and plausibility gate checks for GLUE and SuperGLUE benchmarks.

**Gate (MUST_WORK):** All three parameters physically plausible for BOTH GLUE and SuperGLUE:
- K ∈ [0.85, 1.0]
- t0_absolute ∈ [6, 48] months since benchmark release
- r > 0
- 95% CI width for t0 < 12 months

**Expected outcome:** PASS (H-M2 already showed K_GLUE=0.8955, r_GLUE=0.2017; K_SuperGLUE=0.8858, r_SuperGLUE=0.1578 — t0_absolute conversion must be verified).

---

## 2. Problem Statement

H-M2 confirmed that the logistic model is AIC-preferred over linear and power law models for both GLUE and SuperGLUE benchmark score-over-time trajectories (ΔAIC_GLUE=−250.5, ΔAIC_SuperGLUE=−194.4). However, a preferred model is only scientifically meaningful if its parameters are interpretable. H-M3 tests whether the fitted logistic parameters encode physically plausible dynamics:
- K (ceiling) must be a valid score ceiling below human-level performance
- r (growth rate) must be positive (scores grew, not shrank)
- t0 (inflection point) must fall within the known rapid-development epoch

---

## 3. Functional Requirements

### FR-1: Data Pipeline (Reuse H-M2)

| ID | Requirement | Source |
|----|-------------|--------|
| FR-1.1 | Retrieve GLUE leaderboard via `paperswithcode-client` | H-M2 reuse |
| FR-1.2 | Retrieve SuperGLUE leaderboard via `paperswithcode-client` | H-M2 reuse |
| FR-1.3 | Apply deduplication (best score per model per month) | H-M2 reuse |
| FR-1.4 | Normalize scores to [0,1] range | H-M2 reuse |
| FR-1.5 | Convert dates to months-since-release (t=0 at benchmark publication) | H-M2 reuse |
| FR-1.6 | GLUE release: April 2018 (t=0); SuperGLUE release: May 2019 (t=0) | H-M3 new |

**Note:** FR-1.1–1.5 are inherited from H-M2 code. FR-1.6 adds absolute date mapping for t0 conversion.

### FR-2: Logistic Fit (Reuse H-M2)

| ID | Requirement | Source |
|----|-------------|--------|
| FR-2.1 | Fit 3-parameter logistic `f(t)=K/(1+exp(-r*(t-t0)))` to GLUE timeseries | H-M2 reuse |
| FR-2.2 | Fit same logistic to SuperGLUE timeseries | H-M2 reuse |
| FR-2.3 | Use bounds: K∈[0.5,1.05], r∈[0.01,3.0], t0∈[−24,72] | H-M2 confirmed |
| FR-2.4 | Use initialization p0=[0.92, 0.15, 12.0] | H-M2 confirmed |
| FR-2.5 | Return both `popt` (fitted params) and `pcov` (covariance matrix) | H-M3 requirement |

**Note:** H-M3 may reuse stored H-M2 results directly from `h-m2/results.json` instead of re-fitting, OR re-run the fit to obtain fresh `pcov`. Either approach is valid.

### FR-3: Parameter Extraction Layer (H-M3 New)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.1 | Extract K, r, t0_relative from `popt` array | Must |
| FR-3.2 | Extract covariance matrix `pcov` (3×3) from curve_fit output | Must |
| FR-3.3 | Compute standard errors: `perr = np.sqrt(np.diag(pcov))` | Must |
| FR-3.4 | Compute 95% CI: `ci_95 = 1.96 * perr` for each parameter | Must |
| FR-3.5 | Convert t0_relative to t0_absolute: `t0_abs = t0_rel + release_offset` | Must |
| FR-3.6 | Handle pcov=inf fallback: switch to bootstrap CI (500 resamples) | Must |

### FR-4: Plausibility Gate Checks (H-M3 New)

| ID | Requirement | Threshold | Priority |
|----|-------------|-----------|----------|
| FR-4.1 | Check K ∈ [0.85, 1.0] for GLUE | Boolean flag | Must |
| FR-4.2 | Check K ∈ [0.85, 1.0] for SuperGLUE | Boolean flag | Must |
| FR-4.3 | Check r > 0 for GLUE | Boolean flag | Must |
| FR-4.4 | Check r > 0 for SuperGLUE | Boolean flag | Must |
| FR-4.5 | Check t0_absolute ∈ [6, 48] months for GLUE | Boolean flag | Must |
| FR-4.6 | Check t0_absolute ∈ [6, 48] months for SuperGLUE | Boolean flag | Must |
| FR-4.7 | Check 95% CI width for t0 < 12 months for GLUE | `2*1.96*perr[2]<12` | Must |
| FR-4.8 | Check 95% CI width for t0 < 12 months for SuperGLUE | `2*1.96*perr[2]<12` | Must |
| FR-4.9 | Document t0 border case if t0_absolute < 6 (explore relaxed threshold [0,48]) | Conditional | Should |

### FR-5: Mechanism Activation Verification (H-M3 New)

| ID | Requirement | Code Location |
|----|-------------|---------------|
| FR-5.1 | Verify popt.shape == (3,) | run.py:verify_mechanism_activated() |
| FR-5.2 | Verify pcov is finite (no inf on diagonal) | run.py:verify_mechanism_activated() |
| FR-5.3 | Verify all plausibility flags are True for BOTH benchmarks | run.py:plausibility_check() |
| FR-5.4 | Log activation indicators (popt_shape_correct, pcov_finite, K_extracted, etc.) | run.py |

### FR-6: Ablation Variants

| ID | Variant | Description |
|----|---------|-------------|
| FR-6.1 | pcov=inf fallback | Bootstrap CI with 500 resamples when pcov diagonal contains inf |
| FR-6.2 | t0 relaxed threshold | If t0_absolute < 6 months, test relaxed [0, 48] threshold with documented justification |
| FR-6.3 | H-M2 stored params vs. re-fit | Option to use stored h-m2/results.json params OR re-run curve_fit fresh |

### FR-7: Visualization

| ID | Figure | Type | Priority |
|----|--------|------|----------|
| FR-7.1 | Gate Metrics Comparison | Bar chart: K, r, t0_absolute vs. threshold bounds for both benchmarks | Must (mandatory) |
| FR-7.2 | Parameter CI Plot | K, r, t0 with 95% error bars for GLUE and SuperGLUE | Should |
| FR-7.3 | Logistic Fit with Parameter Annotations | Scatter + curve annotated with K, t0, r | Should |
| FR-7.4 | t0 Absolute Date Timeline | Calendar date mapping vs. known rapid-growth periods | Should |

All figures saved to `h-m3/figures/`.

---

## 4. Data Specification

**Dataset:** Papers With Code Leaderboard Timeseries (GLUE and SuperGLUE)

| Property | Value |
|----------|-------|
| Source | Papers With Code public API (`paperswithcode-client`) |
| Access | Programmatic API — auto-download |
| GLUE entries | ~200+ entries, 2018–2023 |
| SuperGLUE entries | ~150+ entries, 2019–2023 |
| Minimum entries | ≥50 (confirmed in H-E1) |
| Split | None — full timeseries |
| Preprocessing | Dedup + normalize + month-index (inherited from H-M2) |

**No manual download required** — `pip install paperswithcode-client` provides full API access.

**GLUE reference dates:**
- Benchmark release: April 2018 → t=0 in leaderboard month index
- Expected rapid growth: months 6–48 post-release

**SuperGLUE reference dates:**
- Benchmark release: May 2019 → t=0 in leaderboard month index
- Expected rapid growth: months 6–48 post-release

---

## 5. Non-Functional Requirements

| ID | Requirement | Value |
|----|-------------|-------|
| NFR-1 | Reproducibility | Deterministic (scipy curve_fit is deterministic given same data+init) |
| NFR-2 | Runtime | < 5 minutes total (parameter extraction is trivial) |
| NFR-3 | pcov fallback | Bootstrap CI (500 resamples) if pcov diagonal contains inf |
| NFR-4 | Code location | Extend `h-m2/code/run.py` OR create standalone `h-m3/code/run.py` |
| NFR-5 | Results storage | Save to `h-m3/results.json` |

---

## 6. Success Criteria

**Primary Gate (MUST_WORK):** All 8 plausibility flag checks = True (FR-4.1–4.8) for BOTH benchmarks.

| Criterion | Threshold | Status |
|-----------|-----------|--------|
| K ∈ [0.85, 1.0] — GLUE | K=0.8955 (expected PASS) | TBD |
| K ∈ [0.85, 1.0] — SuperGLUE | K=0.8858 (expected PASS) | TBD |
| r > 0 — GLUE | r=0.2017 (expected PASS) | TBD |
| r > 0 — SuperGLUE | r=0.1578 (expected PASS) | TBD |
| t0_absolute ∈ [6,48] — GLUE | depends on offset (border case) | TBD |
| t0_absolute ∈ [6,48] — SuperGLUE | depends on offset (border case) | TBD |
| CI width t0 < 12 — GLUE | depends on pcov | TBD |
| CI width t0 < 12 — SuperGLUE | depends on pcov | TBD |

**Secondary:** PoC code runs without error; pcov is finite; mechanism activation verified.

---

## 7. Dependencies

### 7.1 Python Packages

```
scipy>=1.7.0
numpy>=1.21.0
matplotlib>=3.4.0
paperswithcode-client>=0.1.0
pandas>=1.3.0
```

### 7.2 External Repositories / References

| Reference | Purpose |
|-----------|---------|
| `h-m2/code/run.py` | Base fitting code to extend |
| `h-m2/results.json` | Stored logistic fit parameters and pcov |
| `scipy.optimize.curve_fit` docs | CI computation from pcov |

### 7.3 Prerequisite Data

| Data | Source | Required |
|------|--------|---------|
| H-M2 fitted params (K, r, t0, pcov) | `h-m2/results.json` | Must exist |
| H-M2 cleaned timeseries | `h-m2/code/run.py` data loading | Reuse |

---

## 8. Out of Scope

- Re-running model comparison (AIC analysis) — that is H-M2, already PASSED
- Training any neural network model
- New benchmark datasets beyond GLUE and SuperGLUE
- Parameter optimization (fit is inherited from H-M2)
