# H-M2 Logic: Domain-Specific Degradation Signal Leading Indicator Analysis

**Hypothesis ID:** H-M2
**Date:** 2026-05-19
**Phase:** 3 - Implementation Logic

Applied: incremental-statistical-pipeline-pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual code via direct file read (Serena project selector unavailable for this project)
**Analyzed Path**: `docs/youra_research/20260519_mldpr/h-m1/code/`
**Relevant Symbols**:
- `load_pwc_raw() -> DataFrame[task, dataset, model, evaluated_on, score, domain, quarter]`
- `compute_quarterly_panel(pwc_raw, min_submissions=20, min_quarters=8) -> DataFrame[benchmark_id, task, dataset, quarter, submission_count, cumulative_count, score_var_top10]`
- `flag_compression(panel_df, sigma_map, threshold=1.5, min_consecutive=2) -> DataFrame + [sigma_meas, compressed, compression_event]`
- `summarize_compression(panel_df) -> dict{'n_compression_events', 'n_qualifying_benchmarks', 'pct_compressed'}`
- `get_sigma_map(pwc_raw) -> Series` indexed by `(task, dataset)`, name=`sigma_meas`
- **CRITICAL**: compression column is `compression_event` (float 1.0), NOT `compression_flag`

---

## External Dependencies API (Base Hypothesis)

Signatures verified from `/docs/youra_research/20260519_mldpr/h-m1/code/` actual implementation:

```python
# From: h-m1/code/data_pipeline.py (ACTUAL CODE)
def load_pwc_raw() -> pd.DataFrame:
    """Returns: DataFrame[task, dataset, model, evaluated_on, score, domain, quarter]"""

def compute_quarterly_panel(
    pwc_raw: pd.DataFrame,
    min_submissions: int = 20,
    min_quarters: int = 8,
) -> pd.DataFrame:
    """Returns: DataFrame[benchmark_id, task, dataset, quarter, submission_count,
                          cumulative_count, score_var_top10]"""

# From: h-m1/code/compression_detector.py (ACTUAL CODE)
def flag_compression(
    panel_df: pd.DataFrame,
    sigma_map: pd.Series,          # Series indexed (task, dataset), name='sigma_meas'
    threshold: float = 1.5,
    min_consecutive: int = 2,
) -> pd.DataFrame:
    """Returns: panel_df + [sigma_meas, compressed, compression_event]
    NOTE: compression column = 'compression_event' (float 1.0), NOT 'compression_flag'
    """

def summarize_compression(panel_df: pd.DataFrame) -> dict:
    """Returns: {'n_compression_events': int, 'n_qualifying_benchmarks': int, 'pct_compressed': float}"""

# From: h-m1/code/sigma_estimation.py (ACTUAL CODE)
def get_sigma_map(pwc_raw: pd.DataFrame) -> pd.Series:
    """Returns: Series indexed (task, dataset), name='sigma_meas'"""
```

**Import pattern (verified):**
```python
import sys, os
_HM1_CODE = os.path.join(os.path.dirname(__file__), '..', '..', 'h-m1', 'code')
sys.path.insert(0, os.path.abspath(_HM1_CODE))
from data_pipeline import load_pwc_raw, compute_quarterly_panel
from compression_detector import flag_compression, summarize_compression
from sigma_estimation import get_sigma_map
```

---

## DataFrame Schemas

### panel_df (extended from H-M1)

| Column | Type | Source |
|--------|------|--------|
| benchmark_id | str | H-M1 |
| task | str | H-M1 |
| dataset | str | H-M1 |
| domain | str | H-M1 (cv/nlp/tabular/other) |
| quarter | str (Period) | H-M1 |
| submission_count | int | H-M1 |
| cumulative_count | int | H-M1 |
| score_var_top10 | float | H-M1 |
| compression_event | float | H-M1 flag_compression() |
| hd_cv | float | H-M2 hd_signals |
| hd_nlp | float | H-M2 hd_signals |
| hd_tabular | float | H-M2 hd_signals |

### onset_df (per domain)

| Column | Type | Description |
|--------|------|-------------|
| benchmark_id | str | Benchmark key |
| lead_months | float or None | Months H_d precedes collapse; None=censored |
| onset_observed | bool | True if H_d exceeded threshold before collapse |
| domain | str | cv/nlp/tabular |

### collapse_df

| Column | Type | Description |
|--------|------|-------------|
| benchmark_id | str | Benchmark key |
| collapse_quarter | str | First quarter of confirmed collapse |

---

## A-1: Data Pipeline Setup [Complexity: 8, Budget: 2]

**Applied**: Standard H-M1 reuse pattern

### API Signatures

```python
# data_pipeline.py

DOMAIN_THRESHOLDS: dict[str, float] = {'cv': 0.5, 'nlp': 0.3, 'tabular': 0.90}

def load_hm1_panel(
    min_submissions: int = 20,
    min_quarters: int = 8,
    hm1_code_path: str = '../h-m1/code',
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load H-M1 raw + panel with compression flags.
    Returns: (pwc_raw, panel_df) where panel_df has compression_event column
    """

def filter_compressed_benchmarks(
    panel_df: pd.DataFrame,
    min_quarters: int = 8,
) -> pd.DataFrame:
    """Filter to benchmarks with compression_event == 1.0 and >= min_quarters quarters.
    Returns: filtered panel_df subset
    """

def extend_panel_with_hd(
    panel_df: pd.DataFrame,
) -> pd.DataFrame:
    """Add hd_cv, hd_nlp, hd_tabular columns via hd_signals.compute_all_hd_signals().
    Returns: panel_df + [hd_cv, hd_nlp, hd_tabular]
    """
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | H-M1 reuse + filter | load_hm1_panel, filter_compressed_benchmarks |
| L-1-2 | H_d column extension | extend_panel_with_hd dispatch |

---

## A-2: H_d Signal Computation [Complexity: 14, Budget: 4]

**Applied**: block-bootstrap-kendall-tau pattern, rolling-variance signal pattern

### API Signatures

```python
# hd_signals.py

DOMAIN_THRESHOLDS: dict[str, float] = {'cv': 0.5, 'nlp': 0.3, 'tabular': 0.90}

def compute_robustness_gap_cv(
    panel_df: pd.DataFrame,
    benchmark_id: str,
    rolling_quarters: int = 4,
) -> pd.DataFrame:
    """Rolling std of score_var_top10 as CV robustness gap proxy.
    Returns: DataFrame[quarter, hd_cv]  # rows = quarters for this benchmark
    """

def compute_contamination_nlp(
    panel_df: pd.DataFrame,
    benchmark_id: str,
) -> pd.DataFrame:
    """Normalized absolute deviation from baseline score as NLP contamination proxy.
    Returns: DataFrame[quarter, hd_nlp]
    """

def compute_kendall_tau_tabular(
    panel_df: pd.DataFrame,
    benchmark_id: str,
    bootstrap_iters: int = 100,
    seed: int = 42,
) -> pd.DataFrame:
    """Block-bootstrapped Kendall tau rank correlation for tabular benchmarks.
    Returns: DataFrame[quarter, hd_tabular]  # scalar tau broadcast to all quarters
    """

def compute_all_hd_signals(
    panel_df: pd.DataFrame,
    bootstrap_iters: int = 100,
    seed: int = 42,
) -> pd.DataFrame:
    """Dispatch per-domain H_d signals for all benchmarks; merge back to panel.
    Returns: panel_df + [hd_cv, hd_nlp, hd_tabular]
    """
```

### Pseudo-code: Block-bootstrapped Kendall tau

```
compute_kendall_tau_tabular(panel_df, benchmark_id, bootstrap_iters=100, seed=42):
  bm_data = panel_df[benchmark_id].sort_values('quarter')
  rng = np.random.default_rng(seed)
  taus = []
  for _ in range(bootstrap_iters):
    idx = rng.choice(len(bm_data), size=len(bm_data), replace=True)
    sample = bm_data.iloc[idx]
    tau, _ = scipy.stats.kendalltau(sample['quarter'].rank(), sample['score_var_top10'])
    taus.append(tau)
  mean_tau = np.mean(taus)
  bm_data['hd_tabular'] = mean_tau  # scalar broadcast
  return bm_data[['quarter', 'hd_tabular']]
```

### Pseudo-code: compute_all_hd_signals dispatch

```
compute_all_hd_signals(panel_df):
  results = []
  for bm_id, bm_data in panel_df.groupby('benchmark_id'):
    domain = bm_data['domain'].iloc[0]
    if domain == 'cv':
      sig = compute_robustness_gap_cv(panel_df, bm_id)
      bm_data = bm_data.merge(sig, on='quarter', how='left')
    elif domain == 'nlp':
      sig = compute_contamination_nlp(panel_df, bm_id)
      bm_data = bm_data.merge(sig, on='quarter', how='left')
    elif domain == 'tabular':
      sig = compute_kendall_tau_tabular(panel_df, bm_id)
      bm_data = bm_data.merge(sig, on='quarter', how='left')
    results.append(bm_data)
  merged = pd.concat(results)
  # Fill missing domain columns with NaN
  for col in ['hd_cv', 'hd_nlp', 'hd_tabular']:
    if col not in merged.columns:
      merged[col] = np.nan
  return merged
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | CV signal | compute_robustness_gap_cv (rolling std) |
| L-2-2 | NLP signal | compute_contamination_nlp (normalized deviation) |
| L-2-3 | Tabular signal | compute_kendall_tau_tabular (block-bootstrap tau) |
| L-2-4 | Dispatch | compute_all_hd_signals (loop + merge) |

---

## A-3: Collapse Event Detection [Complexity: 12, Budget: 2]

**Applied**: expanding-apply + consecutive-flag pattern

### API Signatures

```python
# collapse_detector.py

def detect_collapse_events(
    panel_df: pd.DataFrame,
    tau_threshold: float = 0.90,
    min_consecutive: int = 2,
) -> pd.DataFrame:
    """Identify collapse: expanding Kendall tau > tau_threshold for >= 2 consecutive quarters.
    Returns: DataFrame[benchmark_id, collapse_quarter]
    """

def apply_r1_mitigation(
    panel_df: pd.DataFrame,
    collapse_df: pd.DataFrame,
    min_events: int = 20,
    lower_tau: float = 0.85,
) -> tuple[pd.DataFrame, float]:
    """If len(collapse_df) < min_events, re-detect with lower_tau threshold.
    Returns: (collapse_df, tau_used)
    """
```

### Pseudo-code: detect_collapse_events

```
detect_collapse_events(panel_df, tau_threshold=0.90, min_consecutive=2):
  collapse_records = []
  for bm_id, bm_data in panel_df.groupby('benchmark_id'):
    bm_sorted = bm_data.sort_values('quarter')
    # Expanding Kendall tau against position index
    tau_vals = bm_sorted['score_var_top10'].expanding().apply(
      lambda x: kendalltau(range(len(x)), x)[0] if len(x) > 2 else 0.0
    )
    bm_sorted['collapse_flag'] = (tau_vals > tau_threshold).astype(float)
    consecutive = bm_sorted['collapse_flag'].rolling(min_consecutive).min()
    if (consecutive == 1.0).any():
      collapse_q = bm_sorted[consecutive == 1.0]['quarter'].min()
      collapse_records.append({'benchmark_id': bm_id, 'collapse_quarter': collapse_q})
  return pd.DataFrame(collapse_records)  # columns: [benchmark_id, collapse_quarter]
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Collapse detection | detect_collapse_events (expanding tau + consecutive) |
| L-3-2 | R1 mitigation | apply_r1_mitigation (lower threshold if < 20 events) |

---

## A-4: Temporal Analysis + KM [Complexity: 15, Budget: 4]

**Applied**: Kaplan-Meier censored-survival pattern for lead-time estimation

### API Signatures

```python
# temporal_analysis.py
from lifelines import KaplanMeierFitter

DOMAIN_THRESHOLDS: dict[str, float] = {'cv': 0.5, 'nlp': 0.3, 'tabular': 0.90}

def compute_signal_onset_times(
    panel_df: pd.DataFrame,
    domain: str,                      # 'cv' | 'nlp' | 'tabular'
    compression_mask: pd.Index,       # benchmark_ids with compression_event == 1.0
    collapse_df: pd.DataFrame,        # columns: [benchmark_id, collapse_quarter]
) -> pd.DataFrame:
    """Find first quarter H_d exceeds domain threshold; compute lead_months to collapse.
    Returns: DataFrame[benchmark_id, lead_months, onset_observed, domain]
    Notes:
    - lead_months = (collapse_quarter_period - onset_quarter_period).n * 3
    - onset_observed = False if no threshold crossing OR no collapse (censored)
    - Censored cases: lead_months = None
    """

def run_temporal_ordering_test(
    onset_df: pd.DataFrame,
    min_lead_months: int = 12,
) -> dict:
    """KM estimator fit + fraction_leading computation.
    Returns: {
      'fraction_leading': float,      # fraction with onset_observed AND lead_months >= min_lead_months
      'median_lead_months': float,    # KM median survival time
      'km_estimator': KaplanMeierFitter,
      'n_events': int,
      'n_censored': int,
    }
    """

def compute_onset_for_all_domains(
    panel_df: pd.DataFrame,
    collapse_df: pd.DataFrame,
    compression_mask: pd.Index,
) -> dict[str, pd.DataFrame]:
    """Run compute_signal_onset_times for each of cv, nlp, tabular.
    Returns: {'cv': onset_df, 'nlp': onset_df, 'tabular': onset_df}
    Skips domain if hd_{domain} column all-NaN; logs warning.
    """
```

### Pseudo-code: Signal onset detection

```
compute_signal_onset_times(panel_df, domain, compression_mask, collapse_df):
  hd_col = f'hd_{domain}'
  threshold = DOMAIN_THRESHOLDS[domain]
  compressed_panel = panel_df[panel_df['benchmark_id'].isin(compression_mask)]
  onset_records = []

  for bm_id, bm_data in compressed_panel.groupby('benchmark_id'):
    bm_sorted = bm_data.sort_values('quarter')

    # Check collapse record
    collapse_row = collapse_df[collapse_df['benchmark_id'] == bm_id]
    if collapse_row.empty or hd_col not in bm_sorted.columns:
      onset_records.append({'benchmark_id': bm_id, 'lead_months': None,
                            'onset_observed': False, 'domain': domain})
      continue

    collapse_q = collapse_row['collapse_quarter'].iloc[0]

    # Find first quarter H_d exceeds threshold (first quarter only — signal onset)
    onset_mask = bm_sorted[hd_col] > threshold
    if not onset_mask.any():
      onset_records.append({'benchmark_id': bm_id, 'lead_months': None,
                            'onset_observed': False, 'domain': domain})
      continue

    onset_q = bm_sorted[onset_mask]['quarter'].iloc[0]  # first crossing

    # Lead time: (collapse_period - onset_period) * 3 months per quarter
    try:
      lead_months = (pd.Period(collapse_q, 'Q') - pd.Period(onset_q, 'Q')).n * 3
    except Exception:
      lead_months = None

    onset_observed = lead_months is not None and lead_months >= 0
    onset_records.append({'benchmark_id': bm_id, 'lead_months': lead_months,
                          'onset_observed': onset_observed, 'domain': domain})

  return pd.DataFrame(onset_records)
```

### Pseudo-code: Kaplan-Meier lead time

```
run_temporal_ordering_test(onset_df, min_lead_months=12):
  observed = onset_df[onset_df['onset_observed'] == True]
  T = onset_df['lead_months'].fillna(0).clip(lower=0)
  E = onset_df['onset_observed'].astype(int)

  kmf = KaplanMeierFitter()
  kmf.fit(T, event_observed=E, label='lead_time')

  fraction_leading = 0.0
  if len(observed) > 0:
    fraction_leading = (observed['lead_months'] >= min_lead_months).mean()

  return {
    'fraction_leading': fraction_leading,
    'median_lead_months': kmf.median_survival_time_,
    'km_estimator': kmf,
    'n_events': int(E.sum()),
    'n_censored': int((E == 0).sum()),
  }
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Onset computation | compute_signal_onset_times per domain |
| L-4-2 | Lead month delta | Period subtraction + months conversion |
| L-4-3 | KM fit | KaplanMeierFitter.fit(T, E) + median |
| L-4-4 | Domain orchestration | compute_onset_for_all_domains loop |

---

## A-5: Statistical Tests [Complexity: 12, Budget: 2]

**Applied**: Mann-Whitney U greater alternative + sklearn AUC pattern

### API Signatures

```python
# statistical_tests.py
from scipy.stats import mannwhitneyu
from sklearn.metrics import roc_auc_score

def run_mann_whitney_test(
    panel_df: pd.DataFrame,
    domain: str,
    compressed_ids: pd.Index,
) -> dict:
    """Mann-Whitney U: H_d magnitude higher in compressed vs. non-compressed benchmarks.
    Returns: {'mw_stat': float, 'mw_p_value': float, 'domain': str,
              'n_compressed': int, 'n_non_compressed': int}
    """

def compute_auc_comparison(
    panel_df: pd.DataFrame,
    domain: str,
    collapse_df: pd.DataFrame,
    lead_months: int = 24,
) -> dict:
    """AUC of H_d(t-lead_months) vs H_d(t) predicting collapse within lead_months window.
    Returns: {'auc_lead': float, 'auc_concurrent': float, 'domain': str, 'lead_months': int}
    Notes:
    - collapse_label = 1 if benchmark has collapse_quarter in collapse_df (binary per benchmark)
    - auc_lead: H_d signal from quarters at t-lead_months offset
    - auc_concurrent: H_d signal at current quarter t
    - Uses per-benchmark mean H_d to avoid temporal leakage
    """

def run_all_statistical_tests(
    panel_df: pd.DataFrame,
    collapse_df: pd.DataFrame,
    compressed_ids: pd.Index,
) -> dict:
    """Run MW + AUC for cv, nlp, tabular.
    Returns: {'cv': {'mw': dict, 'auc': dict}, 'nlp': {...}, 'tabular': {...}}
    Skips domain if insufficient data (< 5 samples); logs warning.
    """
```

### Pseudo-code: AUC comparison (concurrent vs leading)

```
compute_auc_comparison(panel_df, domain, collapse_df, lead_months=24):
  hd_col = f'hd_{domain}'
  collapsed_ids = set(collapse_df['benchmark_id'].unique())

  # Per-benchmark: mean H_d signal (proxy for signal level)
  bm_stats = panel_df.groupby('benchmark_id')[hd_col].mean().reset_index()
  bm_stats.columns = ['benchmark_id', 'hd_mean']
  bm_stats['collapse_label'] = bm_stats['benchmark_id'].isin(collapsed_ids).astype(int)

  # For lead: use mean H_d of first half of quarters (t-lead proxy)
  first_half = panel_df.groupby('benchmark_id').apply(
    lambda g: g.nsmallest(max(1, len(g)//2), 'quarter')[hd_col].mean()
  ).reset_index(name='hd_early')
  lead_stats = bm_stats.merge(first_half, on='benchmark_id')

  valid = lead_stats.dropna(subset=['hd_mean', 'hd_early', 'collapse_label'])
  if valid['collapse_label'].nunique() < 2:
    return {'auc_lead': np.nan, 'auc_concurrent': np.nan, 'domain': domain, 'lead_months': lead_months}

  auc_concurrent = roc_auc_score(valid['collapse_label'], valid['hd_mean'].fillna(0))
  auc_lead = roc_auc_score(valid['collapse_label'], valid['hd_early'].fillna(0))
  return {'auc_lead': auc_lead, 'auc_concurrent': auc_concurrent, 'domain': domain, 'lead_months': lead_months}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Mann-Whitney U | compressed vs non-compressed H_d magnitude |
| L-5-2 | AUC comparison | t-lead vs t concurrent, all domains |

---

## A-6: Ablation Variants A1-A5 [Complexity: 13, Budget: 2]

**Applied**: config-driven ablation dispatch pattern

### API Signatures

```python
# ablation.py

ABLATION_VARIANTS: dict = {
    'A1': {'description': 't-24mo offset', 'lead_months': 24, 'use_compression_filter': True},
    'A2': {'description': 't-12mo offset', 'lead_months': 12, 'use_compression_filter': True},
    'A3': {'description': 't offset (concurrent)', 'lead_months': 0, 'use_compression_filter': True},
    'A4': {'description': 'compression-filtered only', 'lead_months': 24, 'use_compression_filter': True},
    'A5': {'description': 'all benchmarks', 'lead_months': 24, 'use_compression_filter': False},
}

def run_ablation_variant(
    panel_df: pd.DataFrame,
    collapse_df: pd.DataFrame,
    variant_key: str,                   # 'A1'|'A2'|'A3'|'A4'|'A5'
    compressed_ids: pd.Index,
) -> dict:
    """Run single ablation variant; returns aggregated metrics across domains.
    Returns: {
      'variant': str,
      'description': str,
      'lead_months': int,
      'use_compression_filter': bool,
      'domain_results': {domain: {'fraction_leading': float, 'auc': dict}},
      'domains_passing': int,           # domains with fraction_leading >= 0.60
    }
    """

def run_all_ablations(
    panel_df: pd.DataFrame,
    collapse_df: pd.DataFrame,
    compressed_ids: pd.Index,
) -> list[dict]:
    """Run A1-A5; returns list of per-variant metric dicts.
    Returns: list of dicts from run_ablation_variant
    """
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Single variant | run_ablation_variant (filter + onset + KM + AUC) |
| L-6-2 | All variants | run_all_ablations (A1-A5 loop) |

---

## A-7: Evaluate + Gate Check [Complexity: 10, Budget: 2]

**Applied**: 5-indicator activation check + SHOULD_WORK gate pattern

### API Signatures

```python
# evaluate.py

def verify_mechanism_activated(
    onset_df: pd.DataFrame,
    km_results: dict,
    results: dict,
) -> tuple[bool, dict]:
    """Check 5 mechanism activation indicators.
    Returns: (all_activated: bool, indicators: dict[str, bool])
    Indicators: onset_df_populated, collapse_events_found (>=20),
                lead_time_computed, km_fitted, fraction_computed
    """

def check_gate_condition(
    domain_km_results: dict[str, dict],   # {domain: km_result_dict}
    stat_results: dict,
    min_fraction: float = 0.60,
    min_domains: int = 2,
) -> tuple[bool, dict]:
    """SHOULD_WORK gate: fraction_leading >= 0.60 in >= 2 domains.
    Returns: (gate_passed: bool, gate_details: dict)
    gate_details includes per-domain fraction, passing domains list, mw_p_values
    """

def save_results(
    results: dict,
    results_json: str,
    results_csv: str,
) -> None:
    """Persist results dict to JSON + flattened CSV."""
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Mechanism check | verify_mechanism_activated (5 indicators) |
| L-7-2 | Gate + save | check_gate_condition + save_results |

---

## A-8: Visualization [Complexity: 11, Budget: 2]

**Applied**: matplotlib/seaborn figure-per-function pattern

### API Signatures

```python
# visualize.py
import matplotlib.pyplot as plt
import seaborn as sns

def plot_gate_metrics(
    domain_results: dict,            # {domain: {'fraction_leading': float}}
    output_dir: str,
    threshold: float = 0.60,
    filename: str = 'gate_metrics_fraction_leading.png',
) -> None:
    """Bar chart: fraction_leading per domain vs. 0.60 threshold line. [MANDATORY]"""

def plot_km_curves(
    domain_onset_dfs: dict,          # {domain: onset_df}
    output_dir: str,
    filename: str = 'km_lead_time_curves.png',
) -> None:
    """KM survival curves per domain on single axes; censoring marks shown."""

def plot_signal_timeline(
    panel_df: pd.DataFrame,
    collapse_df: pd.DataFrame,
    benchmark_ids: list[str],
    output_dir: str,
    filename: str = 'signal_emergence_timeline.png',
) -> None:
    """Aligned time series for representative benchmarks; vertical collapse line."""

def plot_auc_comparison(
    auc_results: dict,               # {domain: {'auc_lead': float, 'auc_concurrent': float}}
    output_dir: str,
    filename: str = 'auc_comparison.png',
) -> None:
    """Grouped bar chart: auc_lead vs auc_concurrent per domain."""

def plot_mann_whitney_boxplot(
    panel_df: pd.DataFrame,
    compressed_ids: pd.Index,
    output_dir: str,
    filename: str = 'mann_whitney_boxplot.png',
) -> None:
    """Side-by-side boxplot: H_d magnitude compressed vs. non-compressed per domain."""

def generate_all_figures(
    panel_df: pd.DataFrame,
    collapse_df: pd.DataFrame,
    domain_onset_dfs: dict,
    domain_km_results: dict,
    stat_results: dict,
    ablation_results: list[dict],
    compressed_ids: pd.Index,
    output_dir: str,
) -> None:
    """Orchestrate all 5 figure outputs."""
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | Gate + KM figures | plot_gate_metrics, plot_km_curves |
| L-8-2 | Timeline + AUC + boxplot | plot_signal_timeline, plot_auc_comparison, plot_mann_whitney_boxplot |

---

## A-9: Entry Point + Config [Complexity: 9, Budget: 2]

**Applied**: argparse-over-dataclass config pattern

### API Signatures

```python
# run_experiment.py

CONFIG: dict = {
    "seed": 42,
    "min_submissions": 20,
    "min_quarters": 8,
    "tau_threshold": 0.90,
    "min_consecutive": 2,
    "min_lead_months": 12,
    "min_collapse_events": 20,
    "domains": ["cv", "nlp", "tabular"],
    "domain_thresholds": {"cv": 0.5, "nlp": 0.3, "tabular": 0.90},
    "bootstrap_iters": 100,
    "significance_level": 0.05,
    "gate_fraction_threshold": 0.60,
    "gate_min_domains": 2,
    "hm1_code_path": "../h-m1/code",
    "output_dir": "../figures",
    "results_json": "outputs/results.json",
    "results_csv": "outputs/results.csv",
    "figure_dpi": 150,
}

def parse_args(config: dict, args=None) -> dict:
    """Override CONFIG with CLI args; return merged config dict."""

def main(args=None) -> None:
    """11-step orchestration:
    1. np.random.seed(seed); sys.path inject hm1_code_path
    2. load_hm1_panel() -> (pwc_raw, panel_df)
    3. extend_panel_with_hd(panel_df) -> panel_df
    4. detect_collapse_events(panel_df) -> collapse_df; apply_r1_mitigation()
    5. compressed_ids = panel_df[panel_df['compression_event']==1.0]['benchmark_id'].unique()
    6. compute_onset_for_all_domains() -> domain_onset_dfs
    7. run_temporal_ordering_test() per domain -> domain_km_results
    8. run_all_statistical_tests() -> stat_results
    9. run_all_ablations() -> ablation_results
    10. verify_mechanism_activated() + check_gate_condition()
    11. generate_all_figures(); save_results()
    """
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | Config + argparse | CONFIG dict + parse_args |
| L-9-2 | main() orchestration | 11-step pipeline wiring |

---

## Budget Summary

| Task | Complexity | Budget | Subtasks Used |
|------|-----------|--------|---------------|
| A-1 Data Pipeline | 8 | 2 | 2/2 |
| A-2 H_d Signals | 14 | 4 | 4/4 |
| A-3 Collapse Detector | 12 | 2 | 2/2 |
| A-4 Temporal Analysis + KM | 15 | 4 | 4/4 |
| A-5 Statistical Tests | 12 | 2 | 2/2 |
| A-6 Ablation | 13 | 2 | 2/2 |
| A-7 Evaluate | 10 | 2 | 2/2 |
| A-8 Visualization | 11 | 2 | 2/2 |
| A-9 Entry Point | 9 | 2 | 2/2 |
| **Total** | | **22** | **22/22** |

Note: Budget column shows subtask count allocated (not complexity budget units). Total 22 subtasks allocated across 9 modules.
