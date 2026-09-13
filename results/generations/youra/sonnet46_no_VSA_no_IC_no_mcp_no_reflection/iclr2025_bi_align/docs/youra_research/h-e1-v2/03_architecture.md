---
title: "Architecture: h-e1-v2 Behavioral Proxy Trend Detection"
hypothesis_id: h-e1-v2
type: EXISTENCE
tier: LIGHT
date: "2026-08-31"
---

Applied: streaming data pipeline pattern
Applied: single-pass aggregation pattern
Applied: strategy pattern (Mann-Kendall variant selection)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing codebase to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; no prior code to reuse or maintain consistency with.

---

## File Organization

```
h-e1-v2/
  code/
    main.py            # entry point, argparse, orchestration
    data_loader.py     # WildChat streaming + LMSYS load with fallback
    cohort_builder.py  # returning-user cohort construction + monthly aggregates
    proxy_computer.py  # Proxy 1 (tiktoken), Proxy 2 (entropy), Proxy 3 (regex)
    stats_tester.py    # Mann-Kendall τ, ACF check, bootstrap CI, gate eval
    visualizer.py      # 4 figures saved to figures/
    smoke_test.py      # minimal smoke test with synthetic data
  results/             # CSV intermediates + results.json
  figures/             # output figures
```

---

## Modules

### DataLoader (`code/data_loader.py`)

**Dependencies**: `datasets`, `pandas`

```python
def load_wildchat(split: str = "train") -> Iterable[dict]: ...
# Returns streaming iterator of raw WildChat records
# Fields used: hashed_ip, timestamp, conversation, toxic

def load_lmsys() -> pd.DataFrame: ...
# Tries lmsys/chatbot_arena_conversations; falls back to lmsys-arena-human-preference-55k
# Normalizes winner: "tie (bothbad)" -> "tie"
# Converts tstamp (Unix float) -> datetime
# Returns DataFrame[model_a, model_b, winner, month]
```

### CohortBuilder (`code/cohort_builder.py`)

**Dependencies**: `DataLoader`, `pandas`, `tiktoken`, `multiprocessing`

```python
def build_wildchat_monthly(
    stream: Iterable[dict],
    date_start: str = "2023-01",
    date_end: str = "2024-12",
    min_bins: int = 3,
    min_cohort_size: int = 50,
    n_workers: int = 4,
) -> pd.DataFrame: ...
# Returns DataFrame[month, prompt_tokens_mean, correction_freq_mean, cohort_size]
# Filters: date range, toxic=False, >=3 monthly bins per hashed_ip, >=50 cohort/bin

def build_lmsys_monthly(
    df: pd.DataFrame,
    top_n_pairs: int = 5,
    min_votes: int = 100,
    date_start: str = "2023-01",
    date_end: str = "2024-12",
) -> pd.DataFrame: ...
# Returns DataFrame[month, model_pair, win_count, lose_count, tie_count]
```

### ProxyComputer (`code/proxy_computer.py`)

**Dependencies**: `tiktoken`, `scipy.stats`, `re`, `pandas`, `numpy`

```python
CORRECTION_REGEX = r'\b(no[,.]|actually[,.]|that\'s wrong|please redo|i meant|wrong[,.])\b'

def tokenize_prompt(text: str, enc) -> int: ...
# Uses cl100k_base tiktoken encoder

def compute_entropy(win: int, lose: int, tie: int) -> float: ...
# scipy.stats.entropy([win, lose, tie], base=2); returns nan if total==0

def correction_freq(conversation: list[dict]) -> float: ...
# Count turns matching CORRECTION_REGEX / total turns; case-insensitive

def proxy2_series(lmsys_monthly: pd.DataFrame) -> pd.Series: ...
# Mean entropy across model pairs per month; index = month
```

### StatsTester (`code/stats_tester.py`)

**Dependencies**: `scipy.stats`, `pymannkendall`, `numpy`

```python
def acf_lag1(series: np.ndarray) -> float: ...
# Returns lag-1 autocorrelation

def mann_kendall(series: np.ndarray) -> dict: ...
# Selects scipy.kendalltau if acf_lag1 <= 0.1, else pymannkendall.hamed_rao_modification_test
# Returns {"tau": float, "p": float, "significant": bool, "method": str}

def bootstrap_ci(series: np.ndarray, time_idx: np.ndarray, B: int = 1000, seed: int = 42) -> tuple[float, float]: ...
# Returns (ci_low, ci_high) for tau at 95% confidence

def evaluate_gate(results: dict) -> dict: ...
# Adds gate_passed (bool) and n_significant (int) to results dict
```

### Visualizer (`code/visualizer.py`)

**Dependencies**: `matplotlib`, `seaborn`, `pandas`, `numpy`

```python
def fig1_gate_summary(results: dict, out_dir: str) -> None: ...
# 3-panel bar chart: tau ± CI, p annotations, PASS/FAIL color, tau=0 dashed line

def fig2_proxy_timeseries(wildchat_monthly: pd.DataFrame, proxy2: pd.Series, results: dict, out_dir: str) -> None: ...
# 3-panel monthly means ± 95% CI + Mann-Kendall trend line overlay

def fig3_cohort_funnel(funnel_counts: dict, out_dir: str) -> None: ...
# Horizontal bar funnel: total -> >=1 bin -> >=3 bins -> analysis cohort

def fig4_lmsys_votes(lmsys_monthly: pd.DataFrame, proxy2: pd.Series, out_dir: str) -> None: ...
# Stacked bar win/lose/tie proportions per month + entropy overlay
```

### Main (`code/main.py`)

**Dependencies**: all modules above, `argparse`, `json`, `pathlib`

```python
def parse_args() -> argparse.Namespace: ...
# --date-start, --date-end, --min-bins, --min-cohort-size,
# --min-votes, --n-workers, --bootstrap-B, --out-dir, --figures-dir, --smoke

def main() -> None: ...
# Orchestrates: load -> cohort -> proxies -> stats -> gate -> serialize -> visualize
```

### SmokeTest (`code/smoke_test.py`)

**Dependencies**: `proxy_computer`, `stats_tester`, `numpy`

```python
def run_smoke_test() -> None: ...
# Synthetic 24-bin increasing series -> asserts tau > 0, p < 0.05
# Synthetic flat series -> asserts gate fails
# Prints PASS/FAIL; exits 1 on failure
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown (Size+Dep+Algo+Integ) |
|----|------|-------------|------------|----------------------------------|
| A-1 | Data Loading | WildChat streaming + LMSYS load with fallback and normalization | 9 | 2+2+2+3 |
| A-2 | Cohort Construction | Returning-user filter (>=3 bins), monthly aggregation, bin size filter, multiprocessing tokenization | 14 | 4+3+3+4 |
| A-3 | Proxy Computation | tiktoken (Proxy 1), Shannon entropy (Proxy 2), correction regex + validation (Proxy 3) | 11 | 3+2+3+3 |
| A-4 | Statistical Testing | Mann-Kendall with ACF-based variant selection, bootstrap CI, gate evaluation | 13 | 3+2+4+4 |
| A-5 | Result Serialization | CSV intermediates + results.json, gate result print to stdout | 6 | 1+2+1+2 |
| A-6 | Visualization | 4 figures with annotations and overlays saved to figures/ | 10 | 3+1+2+4 |
| A-7 | Entry Point + Smoke Test | argparse main.py orchestration + smoke_test.py with synthetic assertions | 7 | 2+2+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-2], Medium(9-13): [A-1, A-3, A-4, A-6], Low(4-8): [A-5, A-7]

**Total complexity**: 70 | **Total tasks**: 7 (within LIGHT tier budget of 4-8)
