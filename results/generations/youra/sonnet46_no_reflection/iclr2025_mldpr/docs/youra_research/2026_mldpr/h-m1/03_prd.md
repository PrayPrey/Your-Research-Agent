# Product Requirements Document: H-M1
# BCBHS: Submission Count → Score Compression Causal Mechanism (MECHANISM PoC)

**Hypothesis ID:** H-M1
**Date:** 2026-05-19
**Author:** Anonymous
**Phase:** 3 - Implementation Planning
**Source:** Phase 2C Experiment Brief (02c_experiment_brief.md)

---

## 1. Executive Summary

This experiment validates the first causal link in the BCBHS chain: that cumulative submission count Granger-causes score variance compression in ML benchmark leaderboards. Under benchmarks with ≥20 submissions and ≥2 years history, we test whether score variance in top-k models falls below 1.5σ_measurement for ≥2 consecutive quarters as submission count grows. Two complementary tests are used: Spearman ρ (co-occurrence) and Granger causality (temporal precedence). This is a MUST_WORK hypothesis — failure blocks H-M2, H-M3, H-M4. Prerequisites: H-E1 COMPLETED (PASSED).

---

## 2. Problem Statement

H-E1 confirmed that domain-specific H_d signals discriminate saturated vs. healthy benchmarks (p<0.0001, |d|>5 in all 3 domains). However, the causal mechanism driving signal emergence is unconfirmed. H-M1 tests the foundational causal link: **does submission count accumulation cause score variance compression?**

### 2.1 Success Criteria (Gate Condition)

**PASS (primary):** Spearman ρ > 0.4 AND p < 0.05 (co-occurrence confirmed)
**PASS (secondary):** Granger causality p < 0.05 at lag=2 in panel-level test (causal direction confirmed)
**GATE:** At least ONE of primary OR secondary must PASS to proceed to H-M2
**FAIL:** Both Spearman ρ ≤ 0.4 AND Granger p ≥ 0.05 at all lags → EXPLORE alternative compression thresholds

---

## 3. Functional Requirements

### FR-1: Data Pipeline — PWC Quarterly Panel Construction

**Source:** `pwc-archive/evaluation-tables` (HuggingFace) — reuse H-E1 pipeline
**Filter criteria:**
- ≥20 submissions per benchmark
- ≥8 quarterly time points (≥2 years history)
- Domains: CV + NLP (tabular as validation via H-E1 OpenML reuse)
- Time range: 2018–2025

**Implementation:**
```python
from datasets import load_dataset
import pandas as pd

pwc_eval = load_dataset("pwc-archive/evaluation-tables", split="train")

def compute_quarterly_panel(pwc_eval_df, min_submissions=20, min_quarters=8):
    """Build per-benchmark quarterly panel: submission_count, score_variance_top10."""
    pwc_eval_df['quarter'] = pd.to_datetime(pwc_eval_df['evaluated_on']).dt.to_period('Q')
    panels = []
    for bm_id, bm_df in pwc_eval_df.groupby(['task', 'dataset']):
        if len(bm_df) < min_submissions:
            continue
        qdf = bm_df.groupby('quarter').agg(
            submission_count=('model', 'nunique'),
            score_var_top10=('score', lambda x: x.nlargest(10).var())
        ).reset_index()
        if len(qdf) < min_quarters:
            continue
        qdf['benchmark_id'] = str(bm_id)
        qdf['cumulative_count'] = qdf['submission_count'].cumsum()
        panels.append(qdf)
    return pd.concat(panels, ignore_index=True)
```

**Expected output:** 200–500 qualifying benchmarks; ≥200 (benchmark × quarter) panel rows

### FR-2: σ_measurement Estimation

Estimate per-benchmark measurement noise from repeated model submissions (same model, same benchmark, different dates):

```python
def estimate_sigma_measurement(pwc_eval_df):
    """Estimate σ_measurement per benchmark from repeated submissions."""
    repeated = pwc_eval_df.groupby(['task', 'dataset', 'model'])['score'].std()
    return repeated.groupby(['task', 'dataset']).mean().rename('sigma_meas')
```

**Fallback:** If benchmark has no repeated submissions, use cross-benchmark σ_measurement median.

### FR-3: Compression Detection

Apply 1.5σ threshold for ≥2 consecutive quarters to define compression events:

```python
def flag_compression(panel_df, sigma_map, threshold=1.5, min_consecutive=2):
    """Flag quarters where score_var_top10 < threshold * sigma_measurement."""
    merged = panel_df.merge(sigma_map, on=['task', 'dataset'], how='left')
    merged['compressed'] = merged['score_var_top10'] < threshold * merged['sigma_meas']
    merged['compression_event'] = (
        merged.groupby('benchmark_id')['compressed']
        .transform(lambda s: s.rolling(min_consecutive).min().fillna(0))
    )
    return merged
```

**Expected:** 30–80 compression events across the panel.

### FR-4: Baseline Model — Spearman ρ Correlation

Test monotonic co-occurrence between cumulative submission count and compression indicator:

```python
from scipy.stats import spearmanr

def compute_spearman_baseline(panel_df):
    """Spearman ρ between cumulative_count and compression_event across all observations."""
    valid = panel_df.dropna(subset=['cumulative_count', 'compression_event'])
    rho, p_val = spearmanr(valid['cumulative_count'], valid['compression_event'])
    return {'rho': rho, 'p_value': p_val}
```

**Target:** ρ > 0.4, p < 0.05

### FR-5: Proposed Model — Granger Causality Test

Per-benchmark Granger causality test with ADF stationarity pre-check:

```python
from statsmodels.tsa.stattools import grangercausalitytests, adfuller

def test_granger_causality(benchmark_panel, max_lag=4):
    """
    Test: does cumulative_count Granger-cause score_var_top10?
    Returns dict of p-values per lag (key = lag number).
    """
    ts = benchmark_panel[['score_var_top10', 'cumulative_count']].dropna()
    if len(ts) < max_lag + 5:
        return None  # insufficient data
    # Stationarity check + differencing
    for col in ts.columns:
        if adfuller(ts[col])[1] > 0.05:  # non-stationary
            ts[col] = ts[col].diff()
    ts = ts.dropna()
    gc_res = grangercausalitytests(ts, maxlag=max_lag, verbose=False)
    return {lag: gc_res[lag][0]['ssr_ftest'][1] for lag in range(1, max_lag + 1)}
```

**Primary test:** lag=2 (2-quarter causal delay); report all lags 1–4.

### FR-6: Panel-Level Granger Aggregation

Aggregate per-benchmark Granger results to panel level:

```python
def aggregate_granger_panel(granger_results, target_lag=2):
    """Aggregate per-benchmark Granger p-values."""
    valid = {bm: res for bm, res in granger_results.items() if res is not None}
    p_vals_lag2 = [res[target_lag] for res in valid.values() if target_lag in res]
    return {
        'n_benchmarks_tested': len(valid),
        'n_significant_lag2': sum(p < 0.05 for p in p_vals_lag2),
        'pct_significant_lag2': sum(p < 0.05 for p in p_vals_lag2) / len(p_vals_lag2) if p_vals_lag2 else 0,
        'min_p_lag2': min(p_vals_lag2) if p_vals_lag2 else None,
        'median_p_lag2': sorted(p_vals_lag2)[len(p_vals_lag2)//2] if p_vals_lag2 else None,
    }
```

### FR-7: Reverse Causality Check

Also test compression → submission_count direction to confirm causal direction:

```python
def test_reverse_causality(benchmark_panel, max_lag=4):
    """Test: does compression_event Granger-cause cumulative_count? (Should be p >= 0.05)"""
    ts = benchmark_panel[['cumulative_count', 'compression_event']].dropna()
    if len(ts) < max_lag + 5:
        return None
    gc_res = grangercausalitytests(ts, maxlag=max_lag, verbose=False)
    return {lag: gc_res[lag][0]['ssr_ftest'][1] for lag in range(1, max_lag + 1)}
```

### FR-8: Mechanism Activation Verification

```python
def verify_mechanism_activated(panel_df, granger_results, spearman_result):
    """Verify H-M1 causal mechanism is actually tested and significant."""
    rho, rho_p = spearman_result['rho'], spearman_result['p_value']
    indicators = {
        "panel_constructed": len(panel_df) >= 200,
        "sufficient_benchmarks": len([r for r in granger_results.values() if r is not None]) >= 30,
        "spearman_computed": rho is not None,
        "granger_computed": len(granger_results) > 0,
        "spearman_significant": rho > 0.4 and rho_p < 0.05,
        "granger_significant_lag2": any(
            v.get(2, 1.0) < 0.05
            for v in granger_results.values()
            if v is not None
        )
    }
    activated = (
        indicators["panel_constructed"] and
        indicators["sufficient_benchmarks"] and
        (indicators["spearman_significant"] or indicators["granger_significant_lag2"])
    )
    return activated, indicators
```

### FR-9: Visualization

**Required (mandatory):**
- Gate Metrics Comparison: bar chart of Spearman ρ and Granger p-value at lag=2 (target vs. actual)

**Additional (autonomous):**
1. Scatter plot: cumulative submission count vs. compression indicator per benchmark (colored by domain)
2. Lag profile plot: Granger causality p-value at lags 1–4 quarters
3. Time-series overlay: example benchmark showing submission count growth (top) and score variance decline (bottom)
4. Compression event distribution: histogram of first compression quarter relative to cumulative submission count threshold
5. Reverse causality comparison: bar chart of Granger p-value (forward vs. reverse direction)

**Output directory:** `h-m1/figures/`

---

## 4. Data Specification

### 4.1 Primary Dataset

| Dataset | Source | Method | Domain |
|---------|--------|--------|--------|
| PWC Evaluation Tables | `pwc-archive/evaluation-tables` (HuggingFace) | `load_dataset()` | CV + NLP |

### 4.2 Minimum Sample Requirements

- Qualifying benchmarks: ≥50 with full quarterly time series (≥8 quarters)
- Panel rows: ≥200 (benchmark × quarter) observations
- Granger-testable benchmarks: ≥30 (sufficient length for maxlag=4)
- Compression events: ≥30 (expected 30–80 based on H-E1 saturation labeling)

### 4.3 Panel Schema

| Column | Type | Description |
|--------|------|-------------|
| benchmark_id | str | (task, dataset) composite key |
| quarter | Period | Quarterly period (e.g., 2022Q1) |
| submission_count | int | Unique model submissions in quarter |
| cumulative_count | int | Total submissions from benchmark start |
| score_var_top10 | float | Variance of top-10 model scores in quarter |
| sigma_meas | float | Per-benchmark measurement noise estimate |
| compressed | bool | score_var_top10 < 1.5 × sigma_meas |
| compression_event | float | Rolling 2-quarter compression indicator |

### 4.4 Data Reuse from H-E1

- Data pipeline reuses H-E1 `pwc-archive/evaluation-tables` loading code
- Panel construction logic extends H-E1 quarterly aggregation
- σ_measurement estimation: new component (H-M1 specific)
- Controlled variables: benchmark_age, domain_type inherited from H-E1

---

## 5. Non-Functional Requirements

### 5.1 Performance

- **Expected runtime:** 20–60 minutes (HuggingFace API data loading is bottleneck)
- No GPU required — pure statistical analysis
- Single CPU sufficient

### 5.2 Reproducibility

- Fixed seed: `np.random.seed(42)`
- All data loaded via versioned HuggingFace archive
- Results logged to CSV for reproducibility

### 5.3 Infrastructure (FULL tier — standard)

- Config: argparse or simple dataclass
- Logging: print statements + CSV output
- Testing: smoke test (run completes without error)
- No WandB, no complex YAML config system required

---

## 6. Success Criteria

### 6.1 MUST_WORK Gate (Primary)

| Criterion | Threshold | Test |
|-----------|-----------|------|
| Spearman ρ | > 0.4, p < 0.05 | Co-occurrence confirmed |
| Granger causality | p < 0.05 at lag=2 | Causal direction confirmed |
| Gate rule | At least ONE must PASS | Proceed to H-M2 |

### 6.2 Mechanism Activation (Prerequisite)

- ≥200 panel rows (benchmark × quarter observations)
- ≥30 valid Granger-testable benchmarks
- ≥30 compression events detected
- Both Spearman and Granger computed without error

### 6.3 PoC Pass Condition

1. Code runs without error
2. Panel constructed with ≥200 rows and ≥30 valid benchmarks
3. Spearman ρ > 0.4 AND p < 0.05 (co-occurrence), OR Granger causality p < 0.05 at lag=2

---

## 7. Dependencies

### 7.1 Python Packages

```
datasets>=2.0.0          # HuggingFace datasets (PWC archive)
statsmodels>=0.14.0      # grangercausalitytests, adfuller
scipy>=1.9.0             # spearmanr
numpy>=1.21.0            # Array operations
pandas>=1.3.0            # Dataframe, Period, groupby
matplotlib>=3.4.0        # Visualization
seaborn>=0.11.0          # Visualization
```

### 7.2 External Repositories

| Repository | URL | Purpose |
|------------|-----|---------|
| pwc-archive/evaluation-tables | HuggingFace dataset | PWC leaderboard panel data (reuse H-E1) |

### 7.3 Install Notes

- No GPU required; no special environment beyond standard data science stack
- HuggingFace `datasets` library handles PWC archive download
- statsmodels: `pip install statsmodels>=0.14.0`

---

## 8. File Structure

```
h-m1/
├── 02b_context.md                # Phase 2B context
├── 02c_experiment_brief.md       # Phase 2C input
├── 03_prd.md                     # This document
├── 03_architecture.md            # Phase 3 Architecture
├── 03_logic.md                   # Phase 3 Logic
├── 03_config.md                  # Phase 3 Config
├── 03_tasks.yaml                 # Phase 4 task list
├── code/
│   ├── data_pipeline.py          # FR-1: PWC quarterly panel construction
│   ├── sigma_estimation.py       # FR-2: σ_measurement estimation
│   ├── compression_detector.py   # FR-3: compression flagging
│   ├── spearman_baseline.py      # FR-4: Spearman ρ baseline test
│   ├── granger_causality.py      # FR-5, FR-6, FR-7: Granger tests
│   ├── evaluate.py               # FR-8: mechanism activation + gate check
│   ├── visualize.py              # FR-9: all figures
│   └── run_experiment.py         # Entry point
└── figures/
    ├── gate_metrics.png
    ├── scatter_submission_compression.png
    ├── lag_profile.png
    ├── timeseries_overlay.png
    ├── compression_distribution.png
    └── reverse_causality.png
```

---

## 9. Out of Scope

- Domain-specific signal computation (H-M2 scope)
- Cox proportional hazards modeling (H-M3 scope)
- Lead time prediction (H-M4 scope)
- Any neural network training
- OpenML tabular panel construction (used from H-E1 as validation only)
- ConStat NLP contamination (H-E1 scope; not needed for submission count causal test)

---

## 10. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| PWC API offline (July 2025) | Use HuggingFace archive `pwc-archive/evaluation-tables` |
| Insufficient Granger-testable benchmarks (<30 with ≥8 quarters) | Report as low-power preliminary result; still compute Spearman ρ |
| Non-stationarity after first-order differencing | Apply log-transform before differencing; report as limitation |
| Very sparse σ_measurement (no repeated submissions) | Use cross-benchmark median σ_measurement as fallback |
| Reverse causality confound | Always test compression→count direction; report asymmetry |

---

*Generated by Phase 3 Implementation Planning (BMAD BMM unavailable — direct generation from Phase 2C brief)*
*stepsCompleted: [prd]*
