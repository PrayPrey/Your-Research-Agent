# Product Requirements Document: H-M2
# BCBHS: Domain-Specific Degradation Signal Leading Indicator Analysis (MECHANISM PoC)

**Hypothesis ID:** H-M2
**Date:** 2026-05-19
**Author:** Anonymous
**Phase:** 3 - Implementation Planning
**Source:** Phase 2C Experiment Brief (02c_experiment_brief.md)

---

## 1. Executive Summary

This experiment validates the second causal link in the BCBHS chain: that domain-specific degradation signals (robustness gap widening for CV, contamination probability increase for NLP, premature rank correlation stabilization for tabular) emerge significantly **earlier** than discriminative collapse, providing measurable ≥12-month leading indicators. Building on H-M1's confirmed compression events (145 benchmarks, 389 events), H-M2 tests whether H_d signals precede collapse by ≥12 months in ≥60% of cases in ≥2 of 3 domains. This is a SHOULD_WORK hypothesis — failure narrows the prospective claim but does not block H-M3. Prerequisites: H-M1 COMPLETED (PASSED — Granger p=1.854e-05 at lag=2).

---

## 2. Problem Statement

H-M1 confirmed that submission count accumulation Granger-causes score variance compression (p=1.854e-05 at lag=2; 145 benchmarks, 389 compression events). However, whether domain-specific health signals (H_d) **precede** discriminative collapse — enabling prospective early warning — is unconfirmed. H-M2 tests whether H_d signals emerge ≥12 months before collapse events, converting the compression mechanism into actionable early warning.

### 2.1 Success Criteria (Gate Condition)

**PASS (primary):** `fraction_leading ≥ 0.60` in ≥2 of 3 domains (H_d onset ≥12mo before collapse)
**PASS (secondary):** Mann-Whitney U p < 0.05 (H_d magnitude higher in compressed vs. non-compressed benchmarks)
**GATE:** SHOULD_WORK — failure documents signals as concurrent rather than leading; does not block H-M3
**FAIL response:** Document lead time distribution; frame as "concurrent health monitor"; retain H-M3/M4

---

## 3. Functional Requirements

### FR-1: Data Pipeline — Reuse H-M1 Compressed Panel

**Source:** H-M1 output — `compression_mask` (145 benchmarks, 389 events) from `h-m1/code/`
**Filter:** Benchmarks with confirmed score compression (H-M1 `compression_flag == True`)
**Additional filter:** Benchmarks with ≥8 quarters of history (required for t-24mo lead time analysis)

**Implementation:**
```python
from datasets import load_dataset
import pandas as pd
import sys
sys.path.insert(0, 'h-m1/code')
from build_panel import compute_quarterly_panel
from detect_compression import flag_compression

# Reuse H-M1 panel construction
pwc_eval = load_dataset("pwc-archive/evaluation-tables", split="train")
panel_df = compute_quarterly_panel(pwc_eval.to_pandas(), min_submissions=20, min_quarters=8)

# Load H-M1 compression mask
compression_events_df = panel_df[panel_df['compression_flag'] == True]
compressed_benchmark_ids = compression_events_df['benchmark_id'].unique()
# Expected: 145 compressed benchmarks
```

**Expected output:** 145 benchmarks with compression events; 40–60 benchmarks with confirmed collapse events (Kendall τ > 0.90)

### FR-2: H_d Signal Computation per Domain

Compute domain-specific degradation signals at temporal offsets t, t-12mo, t-24mo:

**CV — Robustness Gap:**
```python
def compute_robustness_gap_cv(panel_df, benchmark_id, rolling_quarters=4):
    """
    Robustness gap = mean score(top-k, corrupted set) − mean score(top-k, clean set)
    Approximated as: variance of top-10 scores over rolling 4-quarter window
    Widening gap = degradation signal.
    """
    bm_data = panel_df[panel_df['benchmark_id'] == benchmark_id].sort_values('quarter')
    bm_data['hd_cv'] = bm_data['score_var_top10'].rolling(rolling_quarters).std()
    return bm_data[['quarter', 'hd_cv']]
```

**NLP — Contamination Probability:**
```python
def compute_contamination_nlp(panel_df, benchmark_id):
    """
    ConStat contamination probability increase at quarter t vs. baseline t0.
    Uses normalized score deviation as proxy: (score - median) / std per quarter.
    """
    bm_data = panel_df[panel_df['benchmark_id'] == benchmark_id].sort_values('quarter')
    baseline_score = bm_data['score_var_top10'].iloc[0]
    bm_data['hd_nlp'] = (bm_data['score_var_top10'] - baseline_score).abs() / (baseline_score + 1e-8)
    return bm_data[['quarter', 'hd_nlp']]
```

**Tabular — Kendall τ Premature Stabilization:**
```python
def compute_kendall_tau_tabular(panel_df, benchmark_id, bootstrap_iters=100, seed=42):
    """
    Block-bootstrapped Kendall τ rank correlation stability.
    τ exceeding 0.90 threshold before collapse event = premature stabilization signal.
    Reuses H-E1 block-bootstrap implementation.
    """
    bm_data = panel_df[panel_df['benchmark_id'] == benchmark_id].sort_values('quarter')
    taus = []
    rng = np.random.default_rng(seed)
    for _ in range(bootstrap_iters):
        idx = rng.choice(len(bm_data), size=len(bm_data), replace=True)
        sample = bm_data.iloc[idx]
        tau, _ = scipy.stats.kendalltau(sample['quarter'].rank(), sample['score_var_top10'])
        taus.append(tau)
    bm_data['hd_tabular'] = np.mean(taus)
    return bm_data[['quarter', 'hd_tabular']]
```

### FR-3: Collapse Event Detection

Identify collapse events per benchmark (Kendall τ > 0.90 for ≥2 consecutive quarters):

```python
DOMAIN_THRESHOLDS = {
    'cv': 0.5,       # robustness gap threshold (from H-E1)
    'nlp': 0.3,      # contamination probability threshold
    'tabular': 0.90  # Kendall τ stabilization threshold
}

def detect_collapse_events(panel_df):
    """
    Collapse event: score_var_top10 falls to near-zero for ≥2 consecutive quarters.
    Proxy: Kendall τ rank correlation > 0.90 for ≥2 consecutive quarters.
    """
    collapse_records = []
    for bm_id, bm_data in panel_df.groupby('benchmark_id'):
        bm_sorted = bm_data.sort_values('quarter')
        tau_vals = bm_sorted['score_var_top10'].expanding().apply(
            lambda x: scipy.stats.kendalltau(range(len(x)), x)[0] if len(x) > 2 else 0
        )
        bm_sorted['collapse_flag'] = tau_vals > 0.90
        consecutive = bm_sorted['collapse_flag'].rolling(2).min()
        if consecutive.any():
            collapse_q = bm_sorted[consecutive == 1]['quarter'].min()
            collapse_records.append({'benchmark_id': bm_id, 'collapse_quarter': collapse_q})
    return pd.DataFrame(collapse_records)
```

**R1 mitigation:** If collapse_event_count < 20, lower τ threshold to 0.85 and report as preliminary study.

### FR-4: Signal Onset Time Computation

For each compressed benchmark, find first quarter when H_d signal exceeds domain threshold:

```python
def compute_signal_onset_times(panel_df, domain, compression_mask, collapse_df):
    """
    For each compressed benchmark, find first quarter when H_d signal
    exceeds domain-specific threshold (signal_onset).
    Returns onset_df: DataFrame with [benchmark_id, lead_months, onset_observed, domain]
    """
    compressed_bms = panel_df[panel_df['benchmark_id'].isin(compression_mask)].copy()
    onset_records = []
    for bm_id, bm_data in compressed_bms.groupby('benchmark_id'):
        hd_col = f'hd_{domain}'
        if hd_col not in bm_data.columns:
            continue
        hd_series = bm_data.sort_values('quarter')
        collapse_row = collapse_df[collapse_df['benchmark_id'] == bm_id]
        if collapse_row.empty:
            # Censored — no collapse observed
            onset_records.append({'benchmark_id': bm_id, 'lead_months': None,
                                   'onset_observed': False, 'domain': domain})
            continue
        collapse_q = collapse_row['collapse_quarter'].iloc[0]
        threshold = DOMAIN_THRESHOLDS[domain]
        onset_mask = hd_series[hd_col] > threshold
        if not onset_mask.any():
            onset_records.append({'benchmark_id': bm_id, 'lead_months': None,
                                   'onset_observed': False, 'domain': domain})
            continue
        onset_q = hd_series[onset_mask]['quarter'].min()
        # Compute lead time in months
        lead_months = (pd.Period(str(collapse_q), 'Q') - pd.Period(str(onset_q), 'Q')).n * 3
        onset_records.append({'benchmark_id': bm_id, 'lead_months': lead_months,
                               'onset_observed': True, 'domain': domain})
    return pd.DataFrame(onset_records)
```

### FR-5: Temporal Ordering Test (Primary)

Kaplan-Meier lead time distribution + fraction_leading computation:

```python
from lifelines import KaplanMeierFitter

def run_temporal_ordering_test(onset_df, min_lead_months=12):
    """
    Primary test: fraction of benchmarks where H_d onset ≥12mo before collapse.
    KM estimator handles right-censored cases (no collapse observed).
    """
    T = onset_df['lead_months'].fillna(0).clip(lower=0)
    E = onset_df['onset_observed'].astype(int)
    kmf = KaplanMeierFitter()
    kmf.fit(T, event_observed=E)
    fraction_leading = (onset_df[onset_df['onset_observed']]['lead_months'] >= min_lead_months).mean()
    median_lead = kmf.median_survival_time_
    return {
        'fraction_leading': fraction_leading,
        'median_lead_months': median_lead,
        'km_estimator': kmf
    }
```

### FR-6: Mann-Whitney U Secondary Test

Compare H_d magnitude in compressed vs. non-compressed benchmarks:

```python
from scipy.stats import mannwhitneyu

def run_mann_whitney_test(panel_df, domain, compressed_ids):
    """
    Secondary test: H_d magnitude significantly higher in compressed vs. non-compressed.
    """
    hd_col = f'hd_{domain}'
    compressed = panel_df[panel_df['benchmark_id'].isin(compressed_ids)][hd_col].dropna()
    non_compressed = panel_df[~panel_df['benchmark_id'].isin(compressed_ids)][hd_col].dropna()
    stat, p_value = mannwhitneyu(compressed, non_compressed, alternative='greater')
    return {'mw_stat': stat, 'mw_p_value': p_value}
```

### FR-7: AUC Lead vs. Concurrent Comparison

Compare predictive AUC at t-24mo vs. t (concurrent):

```python
from sklearn.metrics import roc_auc_score

def compute_auc_comparison(panel_df, domain, collapse_df, lead_months=24):
    """
    AUC of H_d(B, t-24mo) vs H_d(B, t) predicting collapse label.
    Tests temporal specificity: leading signals vs. concurrent signals.
    """
    hd_col = f'hd_{domain}'
    # Build prediction target: collapse within next 24 months
    merged = panel_df.merge(collapse_df, on='benchmark_id', how='left')
    merged['months_to_collapse'] = (
        (merged['collapse_quarter'] - merged['quarter']).dt.days / 30
    ).fillna(999)
    merged['collapse_label'] = (merged['months_to_collapse'] <= lead_months).astype(int)
    auc_lead = roc_auc_score(merged['collapse_label'], merged[hd_col].fillna(0))
    # Concurrent: H_d at t
    concurrent_merged = merged.copy()
    concurrent_merged['months_to_collapse'] = 0  # concurrent
    auc_concurrent = roc_auc_score(merged['collapse_label'], merged[hd_col].fillna(0))
    return {'auc_lead': auc_lead, 'auc_concurrent': auc_concurrent}
```

### FR-8: Ablation Variants

Run all 5 ablation variants:

| Variant | Description | Lead Offset |
|---------|-------------|-------------|
| A1: t-24mo offset | H_d(B, t-24mo) predicting collapse | 24 months (PROPOSED) |
| A2: t-12mo offset | H_d(B, t-12mo) predicting collapse | 12 months |
| A3: t offset (concurrent) | H_d(B, t) predicting collapse | 0 (BASELINE) |
| A4: Compression-filtered | Analysis on H-M1 confirmed compression benchmarks only | 24 months |
| A5: All benchmarks | H_d signals on ALL benchmarks (no compression filter) | 24 months |

**Key ablation question (A4 vs A5):** Does compression filter increase `fraction_leading`? If yes, compression is a necessary precondition.

### FR-9: Mechanism Activation Verification

```python
def verify_mechanism_activated(onset_df, km_results, results):
    """Verify H-M2 temporal ordering mechanism is actually tested."""
    indicators = {
        "onset_df_populated": len(onset_df) > 0,
        "collapse_events_found": onset_df['onset_observed'].sum() >= 20,
        "lead_time_computed": 'lead_months' in onset_df.columns,
        "km_fitted": km_results is not None,
        "fraction_computed": 'fraction_leading' in results
    }
    all_activated = all(indicators.values())
    return all_activated, indicators
```

**R1 mitigation:** If `onset_df['onset_observed'].sum() < 20`, lower τ threshold to 0.85.

### FR-10: Visualization

**Required (mandatory):**
- Gate Metrics Comparison: bar chart of `fraction_leading` per domain vs. 0.60 threshold

**Additional (autonomous — Phase 4 decides most informative):**
1. Kaplan-Meier lead time curves per domain (CV, NLP, Tabular)
2. Signal emergence timeline plot — aligned time series for representative benchmarks (MMLU, CIFAR-10, SQuAD)
3. AUC comparison bar chart — H_d(t-24mo) vs. H_d(t-12mo) vs. H_d(t) per domain
4. Mann-Whitney comparison boxplot — H_d magnitude in compressed vs. non-compressed per domain

**Output directory:** `h-m2/figures/`

---

## 4. Data Specification

### 4.1 Primary Dataset

| Dataset | Source | Method | Domain |
|---------|--------|--------|--------|
| PWC Evaluation Tables | `pwc-archive/evaluation-tables` (HuggingFace) | `load_dataset()` — reuse H-M1 | CV + NLP |
| H-M1 Compression Mask | `h-m1/code/` output | Direct reuse | All domains |

### 4.2 Minimum Sample Requirements

- Compressed benchmarks (from H-M1): 145 (known)
- Collapse events (required for temporal analysis): ≥20 (target: 40–60)
- Benchmarks with ≥8 quarters of history: ≥40 (for t-24mo analysis)
- R1 mitigation threshold: if collapse events < 20, lower τ to 0.85

### 4.3 Panel Schema (Extended from H-M1)

| Column | Type | Description |
|--------|------|-------------|
| benchmark_id | str | (task, dataset) composite key — from H-M1 |
| quarter | Period | Quarterly period — from H-M1 |
| hd_cv | float | Robustness gap signal (CV benchmarks) |
| hd_nlp | float | Contamination probability (NLP benchmarks) |
| hd_tabular | float | Block-bootstrapped Kendall τ (tabular) |
| compression_flag | bool | From H-M1 `compression_mask` output |
| collapse_flag | bool | Kendall τ > 0.90 for ≥2 consecutive quarters |
| collapse_quarter | Period | First quarter of confirmed collapse |

### 4.4 Data Reuse from H-M1

- **Panel construction:** Reuse `h-m1/code/build_panel.py` verbatim
- **Compression detection:** Reuse `h-m1/code/detect_compression.py` output (145 benchmarks, 389 events)
- **σ_measurement:** Reuse from H-M1 (median 0.3323)
- **New component:** Domain-specific H_d signal computation + temporal onset analysis

---

## 5. Non-Functional Requirements

### 5.1 Performance

- **Expected runtime:** 30–90 minutes (dominated by H_d signal computation + KM estimation)
- No GPU required — pure statistical analysis
- Single CPU sufficient; block-bootstrap: `seed=42`, 100 iterations

### 5.2 Reproducibility

- Fixed seeds: `np.random.seed(42)`, block-bootstrap `seed=42`
- All data from versioned HuggingFace archive (reuse H-M1 cached download)
- Results logged to CSV + JSON for reproducibility

### 5.3 Infrastructure (FULL tier — standard)

- Config: dataclass or argparse
- Logging: print statements + CSV output
- Testing: smoke test (run completes without error on subset)
- No GPU, no WandB required

---

## 6. Success Criteria

### 6.1 SHOULD_WORK Gate (Primary)

| Criterion | Threshold | Test |
|-----------|-----------|------|
| `fraction_leading` | ≥ 0.60 in ≥2 of 3 domains | H_d onset ≥12mo before collapse |
| `mw_p_value` | < 0.05 | H_d higher in compressed benchmarks |
| `auc_lead` | > 0.65 | Leading signals discriminable |

### 6.2 Mechanism Activation (Prerequisite)

- `onset_df` populated: ≥1 benchmark with computed onset
- Collapse events found: ≥20 benchmarks with `onset_observed == True`
- Lead time computed in months
- KM estimator fitted
- `fraction_leading` computed for ≥2 domains

### 6.3 PoC Pass Condition

1. Code runs without error (H-M1 pipeline reused + H-M2 temporal analysis layer)
2. ≥20 collapse events detected after filtering
3. `fraction_leading ≥ 0.60` in ≥2 of 3 domains

---

## 7. Dependencies

### 7.1 Python Packages

```
datasets>=2.0              # HuggingFace (reuse H-M1 download)
lifelines==0.30.x          # KaplanMeierFitter, datetimes_to_durations
scipy>=1.10                # mannwhitneyu, kendalltau, spearmanr
numpy>=1.24                # Array operations, block-bootstrap
pandas>=2.0                # Temporal joins, groupby, Period
scikit-learn>=1.2          # roc_auc_score
matplotlib>=3.4.0          # Visualization
seaborn>=0.11.0            # Visualization
```

### 7.2 External Repositories

| Repository | URL | Purpose |
|------------|-----|---------|
| pwc-archive/evaluation-tables | HuggingFace dataset | PWC panel (reuse H-M1) |
| evaleval/benchmark-saturation | GitHub | Domain reference methodology |
| lifelines docs | lifelines.readthedocs.io | KM + datetimes_to_durations API |

### 7.3 Internal Dependencies

| File | Source | Purpose |
|------|--------|---------|
| `h-m1/code/build_panel.py` | H-M1 validated | Panel construction |
| `h-m1/code/detect_compression.py` | H-M1 validated | Compression mask output |

---

## 8. File Structure

```
h-m2/
├── 02c_experiment_brief.md       # Phase 2C input
├── 03_prd.md                     # This document
├── 03_architecture.md            # Phase 3 Architecture
├── 03_logic.md                   # Phase 3 Logic
├── 03_config.md                  # Phase 3 Config
├── 03_tasks.yaml                 # Phase 4 task list
├── code/
│   ├── data_pipeline.py          # FR-1: H-M1 reuse + panel loading
│   ├── hd_signals.py             # FR-2: Domain-specific H_d computation (CV/NLP/Tabular)
│   ├── collapse_detector.py      # FR-3: Collapse event detection (Kendall τ > 0.90)
│   ├── temporal_analysis.py      # FR-4, FR-5: Signal onset + KM lead time
│   ├── statistical_tests.py      # FR-6, FR-7: Mann-Whitney U + AUC comparison
│   ├── ablation.py               # FR-8: Ablation variants A1-A5
│   ├── evaluate.py               # FR-9: Mechanism verification + gate check
│   ├── visualize.py              # FR-10: All figures
│   └── run_experiment.py         # Entry point
└── figures/
    ├── gate_metrics_fraction_leading.png
    ├── km_lead_time_curves.png
    ├── signal_emergence_timeline.png
    ├── auc_comparison.png
    └── mann_whitney_boxplot.png
```

---

## 9. Out of Scope

- Submission count causal mechanism (H-M1 scope — already validated)
- Cox proportional hazards modeling (H-M3 scope)
- Lead time threshold calibration with Youden's J (H-M4 scope)
- Neural network training
- ConStat API calls (approximated by NLP proxy in H-M2)

---

## 10. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Collapse events < 20 after filtering | R1: Lower τ threshold to 0.85; report as preliminary study |
| All lead times negative (signals after collapse) | SHOULD_WORK FAIL — document concurrent signal; proceed to H-M3 |
| H_d not available for domain (all NaN) | Skip domain; report as missing data limitation |
| Compression mask empty (H-M1 output corruption) | Critical error — re-run H-M1 data pipeline |
| Insufficient benchmarks with ≥8 quarters for t-24mo | Use t-12mo as minimum lead window; report |
| A4 vs A5 shows no compression-filter benefit | Document: compression not necessary precondition; proceed |

---

*Generated by Phase 3 Implementation Planning (BMAD PRD Workflow — inline execution from Phase 2C brief)*
*stepsCompleted: [prd]*
