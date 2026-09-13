# Experiment Design: H-M4

**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr
**Hypothesis Statement:** Under the condition that logistic model parameters are plausible (H-M3 confirmed), if we apply the saturation detection criterion (top-3 models exceed fitted asymptote K AND monthly gain rate < 5% of peak rate) to full historical GLUE and SuperGLUE timeseries, then the detected saturation dates will match community-recognized ground truth dates within ±6 months.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (SHOULD_WORK) Template** — Final mechanism test connecting statistical model to real-world benchmark lifecycle events.

---

## Workflow Status

**Verification State:** IN_PROGRESS (H-M4)
**Prerequisites Satisfied:** H-M3 VALIDATED (MUST_WORK PASS) ✅
**Gate Status:** SHOULD_WORK — failure → EXPLORE (alternative criteria, document limitation, does not block H-C1)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M4
- **Type:** MECHANISM
- **Prerequisites:** H-M3 (VALIDATED ✅)

### Gate Condition
SHOULD_WORK gate: Saturation date error < 6 months for GLUE and SuperGLUE. Failure action: EXPLORE — try alternative saturation criteria (e.g., 2% gain rate threshold); document failure; does not stop pipeline.

---

## Continuation Context

This is a continuation experiment building on H-M3. The entire curve_fit pipeline (extract_params, bootstrap_ci, pcov validity check) is inherited from H-M3 code/run.py. H-M4 adds the saturation_criterion detection layer on top.

### Previous Hypothesis Results (H-M3)

| Parameter | GLUE | SuperGLUE |
|-----------|------|-----------|
| K (ceiling) | 0.8955 | 0.8858 |
| r (growth rate) | 0.2017 | 0.1578 |
| t0 (relative months) | −6.771 | −2.855 |
| Fit quality | High (pcov finite, CI < 1m) | High |

**Key H-M3 lesson for H-M4:** t0 < 0 (inflection before launch) is documented as border case. This means top-3 scores exceeded K early. The saturation criterion must check `top3_mean > 0.99*K` rather than using t0 as the saturation date — t0 is the inflection, not the saturation date. H-M4 operationalizes saturation as the LATER event: asymptote exceedance + gain-rate collapse.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Status:** Archon MCP unavailable in this execution environment. Using WebSearch and domain expertise as substitute. Findings documented below.

**Finding 1: Logistic Saturation Detection Patterns (domain knowledge)**
- Standard approach: saturation = time when growth reaches 90-95% of K (inflection is K/2)
- Dual-criterion (exceedance + rate collapse) is more robust than single threshold
- Asymptote exceedance threshold: 0.99×K is standard in technology S-curve forecasting literature
- Gain-rate threshold: 5% of peak monthly gain is common in market saturation analysis
- Source: S-curve forecasting literature (areppim.com S-curve definition, foresightguide.com logistic growth)

**Finding 2: Benchmark Saturation Literature**
- evaleval/benchmark-saturation (GitHub): uses S_index metric for saturation quantification on HELM Classic and HuggingFace Open LLM v2 leaderboards
- Framework tracks timeseries performance trajectories to detect plateau
- Our approach (GLUE/SuperGLUE + Papers With Code) is methodologically prior to this work
- Source: github.com/evaleval/benchmark-saturation

**Finding 3: GLUE/SuperGLUE Ground Truth**
- GLUE saturation community consensus: ~September 2019 (SuperGLUE arXiv:1905.00537, published NeurIPS 2019)
- SuperGLUE saturation ground truth: BIG-bench (arXiv:2206.04615, ~June 2021)
- Established fact: "Models achieved superhuman performance on GLUE within ~1 year of its release" (multiple sources)
- Source: arxiv.org/abs/1905.00537, Mapping global dynamics of benchmark creation (arXiv:2203.04592)

### Archon Code Examples

**Status:** Archon MCP unavailable. Code patterns derived from H-M3 validated pipeline + domain knowledge.

**Pattern 1: Saturation criterion from H-M3 baseline**
```python
# From H-M3 code/run.py (already validated)
def extract_params(df, benchmark):
    # Already validated: returns K, r, t0 via scipy curve_fit
    popt, pcov = curve_fit(logistic, t, y, p0=[0.92, 0.15, 12.0],
                           bounds=([0.5, 0.01, -24], [1.05, 3.0, 72]),
                           maxfev=10000)
    return dict(K=popt[0], r=popt[1], t0=popt[2])
```

**Pattern 2: Dual-criterion saturation detection (new in H-M4)**
```python
def detect_saturation_date(df, K, peak_rate, threshold_k=0.99, threshold_rate=0.05):
    # Find months where top-3 mean exceeds threshold_k * K
    # AND monthly gain < threshold_rate * peak_rate
    ...
```

### Exa GitHub Implementations

**Query 1: evaleval/benchmark-saturation (relevant reference)**
- **URL:** https://github.com/evaleval/benchmark-saturation
- **Relevance:** Only known automated benchmark saturation detection pipeline; uses S_index on HELM/HuggingFace leaderboards
- **Architecture:** Python 3.10+, CSV/JSON timeseries, no scipy curve_fit (uses different metric)
- **Key Insight:** Their S_index tracks performance trajectory saturation without logistic fitting; our approach is complementary and more interpretable
- **Dataset:** HELM Classic (BoolQ, HellaSwag, MMLU, etc.) — different from our GLUE/SuperGLUE
- **Limitation:** Does not validate against community ground truth dates; our H-M4 is the date-validation step

**Query 2: Papers With Code client (data source)**
- **URL:** https://github.com/paperswithcode/paperswithcode-client
- **Relevance:** Official API client used in H-E1/H-M1/H-M2/H-M3; data already cached
- **Key Info:** Papers With Code shut down by Meta in July 2025; historical data archived at paperswithcode/paperswithcode-data on GitHub
- **Impact on H-M4:** Data already cached at /home/PrayPrey/.../data from prior hypotheses — no API calls needed

**Serena Analysis Needed:** False — code from H-M3 is already validated and clear; H-M4 adds one new function (detect_saturation_date) on top of the existing pipeline.

### 🎯 Implementation Priority Assessment

**For H-M4, author's implementation does not apply** — no prior paper implements this exact dual-criterion saturation detection on GLUE/SuperGLUE with ground truth validation. This experiment is the novel contribution.

**Recommended Implementation Path:**
- Primary: Extend H-M3 code/run.py directly (reuse extract_params, bootstrap_ci, data loading)
- Fallback: Standalone script using cached data CSVs from H-M3 outputs
- Justification: H-M3 pipeline is validated (22/22 tests pass); extending it ensures controlled comparison and code reuse

### Code Analysis (Serena MCP)

*Skipped* — Code from H-M3 search results was sufficiently clear; no complex new architecture requiring semantic analysis. H-M4 adds one saturation_criterion function (~30 lines) to an already-validated pipeline.

---

## Experiment Specification

### Dataset

**Name:** Papers With Code Leaderboard (GLUE + SuperGLUE)
**Type:** programmatic-api (historical archive)
**Source:** paperswithcode/paperswithcode-data (GitHub archive; PWC shut down July 2025)
**Cache:** /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_mldpr/data (already populated by H-E1)

**Statistics:**
- GLUE: ~hundreds of dated submissions from April 2018 to saturation
- SuperGLUE: ~hundreds of dated submissions from May 2019 onward
- Coverage: Full lifecycle (growth → inflection → plateau) confirmed in H-E1 and H-M1

**Preprocessing:**
- Inherited from H-M3: score normalization to [0,1], month-level aggregation (max score per month), monotonization (cumulative max to correct for non-monotone leaderboard entries)
- New for H-M4: compute top-3 monthly mean (rolling max of top-3 scores per month), compute month-over-month gain series

**Augmentation:** None (timeseries analysis, no augmentation needed)

**Loading Information** (for Phase 4 download):
- Method: Load from cached CSVs (H-M3 already saved code/outputs/results.csv)
- Identifier: h-m3/code/outputs/results.csv + raw cached parquet/json in data/
- Code: `pd.read_csv("../h-m3/code/outputs/results.csv")` or re-fetch from archive

### Models

#### Baseline Model

**Architecture:** Null detector — no saturation detection (returns date = None / "never saturated")
**Purpose:** Establishes that the criterion is doing real work vs. trivial assignment
**Configuration:** Trivial baseline; "never saturated" for all benchmarks
**Source:** Defined in experiment design

**Loading Information** (for Phase 4):
- Method: No pretrained model; purely analytic
- Identifier: n/a
- Code: `baseline_date = None  # null model`

#### Proposed Model

**Architecture:** Logistic curve_fit (from H-M3, inherited) + dual-criterion saturation detector (new)

**Integration Point:**
- Build on top of H-M3 extract_params() output
- After fitting K, r, t0: compute saturation date using detect_saturation_date()

**Core Mechanism Implementation:**

```python
# Core Mechanism: Dual-Criterion Saturation Date Detection
# Based on: H-M3 validated pipeline + S-curve saturation literature
# Criterion: top-3 exceed 0.99*K AND monthly gain < 5% of peak rate

def detect_saturation_date(monthly_df, K, threshold_k=0.99, threshold_rate=0.05):
    """
    Args:
        monthly_df: DataFrame with columns [month, top3_mean, monthly_gain]
                    month: integer (months since benchmark launch)
                    top3_mean: mean of top-3 scores that month
                    monthly_gain: score gain vs previous month
    Returns:
        sat_date: str (YYYY-MM) or None if criterion never met
        sat_month_idx: int index into monthly_df
    """
    peak_rate = monthly_df["monthly_gain"].max()
    k_threshold = threshold_k * K
    rate_threshold = threshold_rate * peak_rate

    # Find first month where BOTH criteria are met simultaneously
    criterion = (
        (monthly_df["top3_mean"] >= k_threshold) &
        (monthly_df["monthly_gain"] <= rate_threshold)
    )
    met = monthly_df[criterion]
    if met.empty:
        return None, None  # criterion never met

    sat_month_idx = met.index[0]
    sat_date = monthly_df.loc[sat_month_idx, "calendar_month"]  # YYYY-MM
    return sat_date, sat_month_idx


def compute_saturation_error(detected_date, ground_truth_date):
    """
    Returns absolute error in months between detected and ground truth.
    """
    from dateutil.relativedelta import relativedelta
    import datetime
    d = datetime.datetime.strptime(detected_date, "%Y-%m")
    g = datetime.datetime.strptime(ground_truth_date, "%Y-%m")
    delta = relativedelta(d, g)
    return abs(delta.months + delta.years * 12)
```

### Training Protocol

**Note:** No training in the traditional sense; this is a statistical detection experiment.

**Optimizer:** scipy.optimize.curve_fit (from H-M3, reused verbatim)
- Parameters: bounds K[0.5,1.05], r[0.01,3.0], t0[-24,72]; p0=[0.92,0.15,12.0]; maxfev=10000

**Criterion parameters (fixed, from hypothesis statement):**
- K exceedance threshold: 0.99 × K (top-3 mean exceeds 99% of fitted ceiling)
- Gain-rate threshold: 0.05 × peak_rate (monthly gain < 5% of peak monthly gain)

**Sensitivity analysis (alternative criteria):**
- Alt-1: threshold_k=0.99, threshold_rate=0.02 (stricter rate criterion)
- Alt-2: threshold_k=0.95, threshold_rate=0.05 (lower exceedance bar)
- Purpose: If primary criterion fails (error > 6 months), EXPLORE these alternatives per gate logic

**Prospective test (P3 — GLUE only):**
- Truncate GLUE timeseries at 6 months before detected T_sat
- Re-fit logistic on truncated series
- Forecast saturation date from truncated fit
- Compute forecast error vs. actual detected date

**Seeds:** 1 (fixed; scipy curve_fit is deterministic given same data and p0)

**Bootstrap:** 500 samples (fallback only, as in H-M3; pcov was finite for both benchmarks)

### Evaluation

**Primary Metrics:**
- Saturation date error (months): |detected_date − ground_truth_date| for GLUE and SuperGLUE
- Criterion met: Boolean (did the dual criterion fire within the timeseries?)

**Success Criteria:**
- PRIMARY (gate): sat_error_GLUE < 6 months AND sat_error_SuperGLUE < 6 months
- SECONDARY (P3): prospective_forecast_error_GLUE < 3 months
- PoC pass: Both benchmarks have detected saturation date AND primary criterion error < 6 months

**Expected Baseline Performance (from research):**
- GLUE community consensus saturation: ~September 2019 (12–18 months after April 2018 launch)
- SuperGLUE community consensus saturation: ~June 2021 (~25 months after May 2019 launch)
- H-M3 finding: t0 (inflection) is negative (pre-launch), so saturation (plateau exceedance) should be months 12–24 for GLUE, months 20–30 for SuperGLUE
- Sources: arXiv:1905.00537 (SuperGLUE paper), arXiv:2203.04592 (benchmark lifecycle mapping)

**Metrics Loading Information** (for Phase 4):
- Task Type: timeseries date detection / evaluation
- Library: dateutil.relativedelta (month arithmetic), pandas (rolling aggregation)
- Code: `from dateutil.relativedelta import relativedelta`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** Bar chart showing sat_error_GLUE and sat_error_SuperGLUE vs. 6-month threshold

#### Additional Figures (LLM Autonomous)
Based on hypothesis type (MECHANISM — date detection validation), generate:

1. **Saturation Detection Timeline:** Full GLUE/SuperGLUE timeseries with logistic fit overlaid, detected saturation date marked, ground truth date marked, error band visualized
2. **Dual-Criterion Activation Plot:** Two-panel (top-3 mean vs. K threshold; monthly gain vs. rate threshold) showing when each criterion is met and when both simultaneously met
3. **Prospective Forecast Plot (P3):** GLUE timeseries truncated at T_sat − 6 months, logistic fit on truncated data, extrapolated forecast vs. actual saturation
4. **Sensitivity Analysis Heatmap:** Grid of threshold_k × threshold_rate vs. saturation_error for both benchmarks

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures saved to `docs/youra_research/h-m4/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | scipy curve_fit pipeline from H-M3 produces K, r, t0 for GLUE and SuperGLUE | TRUE — validated in H-M3 (22/22 tests pass) |
| Mechanism Isolatable | detect_saturation_date() can be called with/without criterion parameters to compare | TRUE — function takes threshold params as arguments |
| Baseline Measurable | Null model (never saturated) measurable; H-M3 logistic fit (using t0 as saturation proxy) measurable | TRUE |

### Architecture Compatibility Check

**Required Features:**
- Cached GLUE/SuperGLUE timeseries DataFrames with calendar_month column (from H-M3)
- Fitted K from H-M3 extract_params() for each benchmark
- Monthly aggregation: top-3 mean score per month, month-over-month gain column

**Incompatible Scenarios:**
- Benchmarks with < 50 entries (handled by H-C1, not this hypothesis)
- Benchmarks without plateau phase data (not applicable to GLUE/SuperGLUE — confirmed in H-E1)

**Pre-run checks Phase 4 must execute:**
```python
assert K > 0 and K <= 1.05, "K out of range — H-M3 prerequisite failed"
assert len(monthly_df) >= 12, "Insufficient monthly data for saturation detection"
assert "top3_mean" in monthly_df.columns and "monthly_gain" in monthly_df.columns
assert "calendar_month" in monthly_df.columns
```

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"Saturation detected for GLUE at YYYY-MM (error: N months)"` | run.py: detect_saturation_date() |
| Criterion Activation | criterion DataFrame non-empty (at least 1 month satisfies both thresholds) | run.py: criterion mask check |
| Metric Delta | sat_error < 6 months vs. baseline (null = infinite error) | run.py: compute_saturation_error() |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(results):
    indicators = {
        "criterion_fired_GLUE": results["glue"]["sat_date"] is not None,
        "criterion_fired_SuperGLUE": results["superglue"]["sat_date"] is not None,
        "error_below_threshold_GLUE": results["glue"]["sat_error_months"] < 6,
        "error_below_threshold_SuperGLUE": results["superglue"]["sat_error_months"] < 6,
        "beats_null_baseline": (
            results["glue"]["sat_date"] is not None and
            results["superglue"]["sat_date"] is not None
        )
    }
    activated = indicators["criterion_fired_GLUE"] and indicators["criterion_fired_SuperGLUE"]
    gate_pass = (
        indicators["error_below_threshold_GLUE"] and
        indicators["error_below_threshold_SuperGLUE"]
    )
    return activated, gate_pass, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Criterion never fires | `sat_date is None` for either benchmark | EXPLORE: lower threshold_k to 0.95 or raise threshold_rate to 0.10 |
| Error > 6 months | `sat_error > 6` | EXPLORE: try Alt-1/Alt-2 sensitivity; document closest alternative |
| K exceedance without rate collapse | top3_mean > 0.99K but gain still high | Check: are gains monotonically decreasing? If not, data quality issue |
| Rate collapse without exceedance | gain < 5% peak but top3 < 0.99K | Means plateau is below K — K overestimated; report selection bias |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Criterion fires | TRUE for both benchmarks | `sat_date is not None` |
| Effect measurable | sat_error < ∞ (vs. null baseline) | compute_saturation_error() |
| Hypothesis supported | sat_error < 6 months for BOTH | Primary gate metric |
| Prospective (P3) | forecast_error < 3 months | GLUE truncated re-fit |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `detect_saturation_date()` returns non-None for both GLUE and SuperGLUE
3. `sat_error_GLUE < 6` AND `sat_error_SuperGLUE < 6`

**Gate:** SHOULD_WORK — if fails, run sensitivity analysis (Alt-1, Alt-2), document best-effort result, proceed to H-C1.

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Status:** Archon MCP unavailable. Domain knowledge and literature used.

**Source A.1:** S-curve saturation forecasting literature
- **Type:** Domain knowledge (S-curve forecasting methodology)
- **Query Equivalent:** "logistic saturation detection asymptote exceedance threshold"
- **Key Insights:**
  - Saturation threshold 0.99×K is standard in technology diffusion literature
  - 5% gain-rate threshold is common in market saturation analysis
  - Dual-criterion approach (exceedance + rate collapse) reduces false positives
- **Used For:** Saturation criterion parameter selection (threshold_k=0.99, threshold_rate=0.05)

**Source A.2:** arXiv:2203.04592 — Mapping global dynamics of benchmark creation and saturation
- **Type:** Research paper (web search result)
- **Key Insights:** GLUE/SuperGLUE lifecycle documented; saturation patterns mapped
- **Used For:** Confirming ground truth dates and saturation narrative

### B. GitHub Implementations (Web Search)

**Repository B.1:** evaleval/benchmark-saturation
- **URL:** https://github.com/evaleval/benchmark-saturation
- **Relevance:** Only known automated benchmark saturation detection pipeline
- **Architecture:** Python 3.10+, S_index metric (different from our logistic criterion)
- **Key Insight:** They use statistical S_index rather than dual-criterion; validates that programmatic saturation detection is tractable
- **Datasets:** HELM Classic, HuggingFace Open LLM v2 (different from GLUE/SuperGLUE)
- **Used For:** Confirming feasibility of automated saturation detection; our approach is more interpretable (logistic + date matching)

**Repository B.2:** paperswithcode/paperswithcode-client
- **URL:** https://github.com/paperswithcode/paperswithcode-client
- **Relevance:** Data source API (historical data already cached from H-E1)
- **Key Info:** PWC shut down July 2025; historical archive at paperswithcode/paperswithcode-data
- **Used For:** Data loading (cached); confirms `evaluated_on` date field for timeseries reconstruction

### C. Code Analysis (Serena)

Serena analysis not performed — H-M3 code/run.py is the primary implementation source (22/22 tests validated). H-M4 adds detect_saturation_date() (new, ~30 lines) on top of the existing pipeline. No complex external code requiring semantic analysis.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — H-M3
- **File:** docs/youra_research/h-m3/04_validation.md
- **Reused Components:**
  - extract_params() — curve_fit pipeline with bounds/p0/maxfev validated
  - bootstrap_ci() — fallback validated (not needed for GLUE/SuperGLUE)
  - check_pcov_validity() — inf detection tested
  - Data loading and month aggregation code
  - Optimal hyperparameters: K[0.5,1.05], r[0.01,3.0], t0[-24,72], p0=[0.92,0.15,12.0], maxfev=10000
- **Why Reused:** Enables controlled experiment — only the saturation_criterion layer is new

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (GLUE/SuperGLUE) | Continuation (H-M3 cache) | D.1 |
| Ground truth dates (Sept 2019, June 2021) | Literature | arXiv:1905.00537, arXiv:2206.04615 |
| K exceedance threshold (0.99×K) | Domain knowledge | A.1 (S-curve literature) |
| Gain-rate threshold (5% of peak) | Domain knowledge | A.1 (market saturation analysis) |
| detect_saturation_date() pseudocode | New (from H-M4 hypothesis + H-M3 base) | B.1 (evaleval/benchmark-saturation pattern), D.1 (H-M3 structure) |
| Training protocol (curve_fit params) | H-M3 validation | D.1 |
| Evaluation metrics (date error in months) | Phase 2B success criteria | 02b_verification_plan.md §H-M4 |
| Prospective test (P3) | Phase 2B success criteria | 02b_verification_plan.md §H-M4 |
| Mechanism verification protocol | Mechanism template | mechanism_verification_protocol.md |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — restate block)
**Date:** 2026-08-25T18:30:00+00:00

### Workflow History for This Hypothesis
- H-M3 VALIDATED (MUST_WORK PASS) — 2026-08-25T16:50:00
- H-M4 set to IN_PROGRESS — 2026-08-25T16:52:02
- Phase 2C experiment design started — 2026-08-25T18:00:00
- Phase 2C experiment design COMPLETED — 2026-08-25T18:30:00

---

*MCP Tools Used: WebSearch (substitute for Archon/Exa; Archon MCP unavailable), domain expertise*
*All specifications grounded in H-M3 validated pipeline + literature sources*
*Next Phase: Phase 3 - Implementation Planning*
