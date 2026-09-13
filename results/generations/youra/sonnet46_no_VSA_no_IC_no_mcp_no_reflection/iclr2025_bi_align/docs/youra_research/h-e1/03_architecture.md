# Architecture: H-E1
# Behavioral Proxy Signal Detection in Human-AI Interaction Logs

**Hypothesis:** H-E1 (EXISTENCE / FOUNDATION)
**Date:** 2026-08-31
**Type:** Statistical data analysis — no neural network

Applied: Standard data analysis pipeline pattern

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field project; no existing codebase to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch

---

## File Organization

```
h-e1/
├── code/
│   ├── data_loader.py        # WildChat + LMSYS loaders
│   ├── proxy_computation.py  # 3 proxy calculations
│   ├── statistical_analysis.py  # Mann-Kendall tests + success eval
│   ├── visualization.py      # 4 figures
│   └── main.py              # Orchestration + results.json
├── figures/
├── results/
└── requirements.txt
```

---

## Module Definitions

### DataLoader (`code/data_loader.py`)

**Dependencies:** datasets, pandas

```python
def load_wildchat(date_start: str = "2023-01", date_end: str = "2024-12") -> pd.DataFrame:
    # Returns DataFrame[hashed_ip, monthly_bin, prompt, turn_count, model]
    ...

def build_cohort(df: pd.DataFrame, min_bins: int = 3) -> pd.DataFrame:
    # Filter to hashed_ip appearing in >= min_bins distinct monthly bins
    # Returns DataFrame[hashed_ip, monthly_bin, prompt, turn_count]
    ...

def load_lmsys(date_start: str = "2023-01", date_end: str = "2024-12",
               min_votes_per_bin: int = 100, top_n_models: int = 5) -> pd.DataFrame:
    # Returns DataFrame[monthly_bin, model_a, model_b, winner]
    ...
```

---

### ProxyComputation (`code/proxy_computation.py`)

**Dependencies:** pandas, numpy, data_loader

```python
CORRECTION_MARKERS: list[str]  # ["actually", "that's wrong", ...]

def compute_token_series(cohort_df: pd.DataFrame) -> dict[str, float]:
    # monthly_bin -> mean prompt_token_count (len(prompt.split())*1.3)
    ...

def compute_correction_series(cohort_df: pd.DataFrame) -> dict[str, float]:
    # monthly_bin -> mean correction_freq per session
    ...

def compute_entropy_series(lmsys_df: pd.DataFrame) -> dict[str, float]:
    # monthly_bin -> mean Shannon entropy across top-5 model pairs
    ...
```

---

### StatisticalAnalysis (`code/statistical_analysis.py`)

**Dependencies:** numpy, scipy.stats

```python
def run_mann_kendall(series: dict[str, float]) -> tuple[float, float]:
    # Returns (tau, p_value) via scipy.stats.kendalltau
    ...

def evaluate_success(results: dict[str, tuple[float, float]],
                     p_threshold: float = 0.05,
                     effect_threshold: float = 0.2) -> dict:
    # Returns {proxy: {tau, p, abs_tau, pass}, overall_pass: bool, n_passing: int}
    ...
```

---

### Visualization (`code/visualization.py`)

**Dependencies:** matplotlib, pandas

```python
def plot_tau_bar(results: dict, outdir: str) -> None:
    # Figure 1: bar chart of tau values; significance markers; tau=0 line
    ...

def plot_time_series(token_series: dict, correction_series: dict,
                     entropy_series: dict, outdir: str) -> None:
    # Figure 2: monthly mean per proxy with trend line
    ...

def plot_pvalue_heatmap(results: dict, outdir: str) -> None:
    # Figure 3: p-value heatmap 3 proxies x datasets
    ...

def plot_cohort_diagnostics(cohort_df: pd.DataFrame, lmsys_df: pd.DataFrame,
                             outdir: str) -> None:
    # Figure 4: cohort size histogram + LMSYS vote count per bin
    ...
```

---

### Main (`code/main.py`)

**Dependencies:** all modules above, json, pathlib

```python
def main() -> None:
    # Orchestrates full pipeline; saves results/results.json; generates all figures
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E1 | Environment Setup | requirements.txt; verify HuggingFace access; directory structure | 5 | 1+1+1+2 |
| E2 | WildChat Loader + Cohort | load_wildchat + build_cohort; 2023-2024 filter; ≥3 bin cohort logic | 12 | 3+2+4+3 |
| E3 | Proxy Computation | token_series, correction_series (marker list), entropy_series | 10 | 3+2+3+2 |
| E4 | LMSYS Loader + Entropy | load_lmsys; top-5 model filter; ≥100 votes/bin; Shannon entropy | 11 | 3+2+3+3 |
| E5 | Mann-Kendall Analysis | run_mann_kendall x3; evaluate_success; p<0.05 + |τ|>0.2 checks | 9 | 2+2+3+2 |
| E6 | Visualization | 4 figures; matplotlib; save to figures/ | 8 | 2+2+2+2 |
| E7 | Orchestration + Results | main.py pipeline; results.json; run end-to-end test | 7 | 2+1+2+2 |

**Total complexity:** 62
**Distribution:** High(10-13): [E2, E3, E4], Medium(7-9): [E5, E6, E7], Low(4-6): [E1]

---

## Requirements (`requirements.txt`)

```
datasets>=2.14.0
pandas>=1.5.0
numpy>=1.24.0
scipy>=1.11.0
matplotlib>=3.7.0
```
