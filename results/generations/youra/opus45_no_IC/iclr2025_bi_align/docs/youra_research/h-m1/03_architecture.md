# Architecture: H-M1 (User Adaptation to AI Patterns)

**Type:** MECHANISM | **Tier:** STANDARD

Applied: No direct KB match for lagged cross-correlation dialogue pattern (searched "DL experiment architecture lagged correlation"); design follows PRD/brief spec directly (statistical pipeline extending H-E1).

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-E1)
**Status:** Only `h-e1/03_architecture.md` spec found; no actual `h-e1/code/` directory exists on disk yet (checked `docs/youra_research/h-e1/`). Treating H-E1 spec as reference since implementation not yet materialized.
**Analyzed Path:** `docs/youra_research/h-e1/` (spec only; no `code/` subfolder present)
**Findings:** No implemented code to verify import paths against. H-M1 will define its own checkpoint loader with fallback to H-E1 spec module names (`bcs.py`, `data.py`) if `h-e1/code/` appears at runtime; otherwise recompute from HF dataset per PRD FR-1.1 fallback.

---

## Module Structure

### config.py (`h-m1/code/config.py`)

```python
BCS_CHECKPOINT_PATH = "h-e1/results/bcs_checkpoint.pkl"
DATASET_FALLBACK = "Anthropic/hh-rlhf"
MIN_ALIGNED_TURNS = 4
MAX_LAG = 3
N_PERMUTATIONS = 1000
SEED = 42
LENGTH_BINS = {"short": (4, 6), "medium": (7, 10), "long": (11, None)}
```

### data.py (`h-m1/code/data.py`)

**Dependencies:** config.py, pickle, datasets (fallback)

```python
def load_checkpoint(path: str) -> dict: ...  # returns {'conversations', 'complexity_data'}
def load_fallback(dataset_name: str) -> list[dict]: ...  # reload + recompute via h-e1 logic
def build_trajectories(checkpoint: dict) -> list[tuple[list[float], list[float]]]: ...  # (user[t], ai[t]) per convo
def filter_min_turns(trajectories: list, min_turns: int = 4) -> list: ...
```

### lagcorr.py (`h-m1/code/lagcorr.py`)

**Dependencies:** config.py, numpy, pandas, scipy.stats

```python
def compute_lagged_correlation(user: list[float], ai: list[float], lag: int = 1) -> tuple[float, float]: ...
def analyze_conversation(user_turns: list[float], ai_turns: list[float], max_lag: int = 3) -> dict[str, dict]: ...
def batch_lag1(trajectories: list[tuple[list[float], list[float]]]) -> list[float]: ...  # per-convo lag-1 r
def batch_multilag(trajectories: list[tuple[list[float], list[float]]], max_lag: int = 3) -> dict[int, list[float]]: ...
```

### baseline.py (`h-m1/code/baseline.py`)

**Dependencies:** config.py, numpy, lagcorr.py

```python
def shuffle_baseline(ai_complexity: list[float], seed: int | None = None) -> list[float]: ...
def run_permutation_test(trajectories: list, n_permutations: int = 1000, seed: int = 42) -> dict: ...
    # returns {'shuffled_lag1_rs', 'null_mean', 'null_p'}
```

### stats.py (`h-m1/code/stats.py`)

**Dependencies:** numpy, scipy.stats

```python
def one_sample_ttest(values: list[float]) -> dict: ...  # {'mean','std','t_statistic','p_value','ci95'}
def cohens_d(values: list[float]) -> float: ...
def check_gate(real_stats: dict, baseline_stats: dict) -> bool: ...  # p<0.05, mean>0, baseline p>0.10
def stratify_by_length(trajectories: list, lag1_rs: list[float], bins: dict) -> dict[str, dict]: ...
```

### visualize.py (`h-m1/code/visualize.py`)

**Dependencies:** matplotlib, seaborn, stats.py

```python
def plot_lag_profile(multilag_results: dict[int, list[float]], save_path: str) -> None: ...
def plot_gate_pvalue(p_value: float, target: float, save_path: str) -> None: ...
def plot_lag1_histogram(lag1_rs: list[float], save_path: str) -> None: ...
def plot_length_scatter(trajectories: list, lag1_rs: list[float], save_path: str) -> None: ...
def plot_shuffled_vs_real(real_rs: list[float], shuffled_rs: list[float], save_path: str) -> None: ...
def plot_length_heatmap(multilag_by_bin: dict, save_path: str) -> None: ...
```

### run_experiment.py (`h-m1/code/run_experiment.py`)

**Dependencies:** all modules above

```python
def main() -> dict: ...  # load -> trajectories -> lag1+multilag -> baseline -> stats -> figures -> gate result
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Checkpoint loading | Load H-E1 pkl checkpoint, fallback reload+recompute path | 8 | 2+2+2+2 |
| M-2 | Trajectory building | Build per-conversation user/ai time series, filter <4 turns | 6 | 1+1+2+2 |
| M-3 | Lagged correlation core | `compute_lagged_correlation` with edge cases (zero var, short len) | 7 | 2+1+3+1 |
| M-4 | Multi-lag batch analysis | Compute lags -3..+3 across full dataset, multiprocessing | 9 | 2+3+3+1 |
| M-5 | Shuffled baseline + permutation test | 1000 shuffles, null distribution, seed=42 | 8 | 2+2+2+2 |
| M-6 | Statistical testing | One-sample t-test, Cohen's d, CI95, gate check | 6 | 1+1+2+2 |
| M-7 | Length stratification | Bin by conversation length, compare adaptation strength | 6 | 1+1+2+2 |
| M-8 | Visualization suite | 6 required/optional figures per brief | 7 | 2+1+1+3 |
| M-9 | End-to-end orchestration + report | Run full pipeline on 26,395 convos, verify gate, save results | 6 | 1+2+1+2 |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M-4], Low(4-8): [M-1, M-2, M-3, M-5, M-6, M-7, M-8, M-9]

---

## External Dependencies (Base Hypothesis)

### Module Paths (Intended, Unverified — No H-E1 code Present)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| BCS checkpoint | N/A (data file, not code) | `h-e1/results/bcs_checkpoint.pkl` |
| BCSComputer (fallback recompute) | `from h_e1.code.bcs import BCSComputer` | `h-e1/code/bcs.py` (spec only, not yet on disk) |
| Conversation loader (fallback) | `from h_e1.code.data import load_conversations` | `h-e1/code/data.py` (spec only, not yet on disk) |

**Verified from:** `h-e1/03_architecture.md` spec (NOT actual code — `h-e1/code/` does not exist yet). Phase 4 Coder must verify these paths at implementation time and use `DATASET_FALLBACK` reload path if H-E1 code/checkpoint is absent.

---

## File Organization

```
h-m1/code/
  config.py
  data.py
  lagcorr.py
  baseline.py
  stats.py
  visualize.py
  run_experiment.py
h-m1/results/
  lag_analysis.pkl
h-m1/figures/
  lag_profile.png
  gate_pvalue.png
  lag1_histogram.png
  length_scatter.png
  shuffled_vs_real.png
  length_heatmap.png
```
