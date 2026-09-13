# Architecture: h-c1

**Type:** EXISTENCE-style simplified statistical analysis (no NN training)
**Applied:** No KB pattern match for psychometrics; used pingouin (standard lib) per PRD research.

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m1 prerequisite)
**Status**: Serena project activation unavailable in this session (no active project registered for this path); analyzed h-m1 code directly via file read instead.
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Findings**:
- h-m1 does **NOT** write `outputs/attribution_scores.npz`. It only computes `results: dict[method][mode] -> np.ndarray` in-memory (`run_experiment.py`) and persists an aggregated `gate_results.json` (interaction matrix of means only, no raw per-probe scores) plus figures.
- **Gap**: PRD/brief assume `h-m1/outputs/attribution_scores.npz` exists with raw per-probe arrays. It does not. `data_loader.py` below implements the NPZ contract as specified, but the Coder must either (a) add an NPZ dump to h-m1's `run_experiment.py` before running h-c1, or (b) treat missing file as a hard error with a clear message pointing to this gap. Do not silently fabricate data.
- h-m1 `cfg.probes_per_mode = 100`, not 1000 as stated in h-c1 PRD — use actual array length from data, don't hardcode 1000.
- Mode name convention differs: h-m1 uses `mem`/`transfer`/`spurious`; PRD/brief use `memorization`/`feature_transfer`/`spurious`. NPZ writer (wherever added) must use full names `memorization`, `feature_transfer`, `spurious` to match this PRD's key format `{method}_{mode}`.

---

## File Structure

- `config.py` — paths, threshold constant
- `data_loader.py` — load + validate NPZ into per-method DataFrames
- `reliability.py` — Cronbach's alpha + item-total correlations + alpha-if-dropped
- `visualization.py` — 3 figures
- `main.py` — orchestrator

---

## Module Interfaces

### config.py

```python
from dataclasses import dataclass

@dataclass
class Config:
    npz_path: str = "../h-m1/outputs/attribution_scores.npz"
    fig_dir: str = "./h-c1/figures"
    results_path: str = "./h-c1/gate_results.json"
    methods: tuple = ("trak", "tracin", "kronfluence")
    modes: tuple = ("memorization", "feature_transfer", "spurious")
    alpha_threshold: float = 0.8
    min_samples: int = 500
```

### data_loader.py (`code/data_loader.py`)

**Dependencies**: config.py, numpy, pandas

```python
def load_attribution_scores(npz_path: str) -> dict[str, np.ndarray]: ...
    # Raises FileNotFoundError with actionable message if npz_path missing
    # (h-m1 does not currently emit this file — see Codebase Analysis)

def validate_scores(scores: dict, methods: tuple, modes: tuple, min_samples: int) -> None: ...
    # Checks all 9 keys "{method}_{mode}" present, no NaN/Inf, len >= min_samples

def build_mode_profile_df(scores: dict, method: str, modes: tuple) -> pd.DataFrame: ...
    # Returns DataFrame: rows=probe pairs, cols=modes (n_probes x 3)
```

### reliability.py (`code/reliability.py`)

**Dependencies**: pingouin, pandas, numpy

```python
def compute_cronbach_alpha(df: pd.DataFrame) -> dict: ...
    # Returns {"alpha": float, "ci_lower": float, "ci_upper": float}
    # Uses pingouin.cronbach_alpha(data=df)

def compute_item_total_correlations(df: pd.DataFrame) -> dict[str, float]: ...
    # Per-mode: corr(mode_col, total_score_excluding_that_mode)

def compute_alpha_if_dropped(df: pd.DataFrame) -> dict[str, float]: ...
    # For each mode, alpha of remaining 2-column df

def analyze_all_methods(profiles: dict[str, pd.DataFrame], threshold: float) -> dict: ...
    # Returns per-method: {alpha, ci_lower, ci_upper, item_total_corr, alpha_if_dropped, pass}
    # Plus top-level "gate_pass": bool (all methods pass)
```

### visualization.py (`code/visualization.py`)

**Dependencies**: matplotlib, seaborn, results dict from reliability.py

```python
def plot_alpha_bar_chart(results: dict, threshold: float, save_path: str) -> None: ...
    # Bar per method, 95% CI error bars, horizontal threshold line at 0.8

def plot_reliability_heatmap(results: dict, modes: tuple, save_path: str) -> None: ...
    # method x mode matrix of item-total correlations

def plot_alpha_if_dropped(results: dict, modes: tuple, save_path: str) -> None: ...
    # grouped bar: per method, alpha-if-dropped per mode vs full alpha
```

### main.py (`code/main.py`)

```python
def main() -> bool: ...
    # 1. cfg = Config()
    # 2. scores = load_attribution_scores(cfg.npz_path); validate_scores(...)
    # 3. profiles = {m: build_mode_profile_df(scores, m, cfg.modes) for m in cfg.methods}
    # 4. results = analyze_all_methods(profiles, cfg.alpha_threshold)
    # 5. plot_alpha_bar_chart / plot_reliability_heatmap / plot_alpha_if_dropped -> cfg.fig_dir
    # 6. dump results to cfg.results_path (json)
    # 7. print PASS/FAIL; return results["gate_pass"]

if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
```

---

## External Dependencies (Base Hypothesis)

| Item | Path | Note |
|------|------|------|
| Attribution scores | `h-m1/outputs/attribution_scores.npz` | **Does not exist yet** — h-m1 only persists `gate_results.json` + figures. Coder must add NPZ export to h-m1 (dict of `{method}_{mode}` -> raw np.ndarray using full mode names) or fail fast with clear error. |
| h-m1 results dict shape | in-memory only, `run_experiment.py:70` `results[method][mode] -> np.ndarray` | Source of truth for what NPZ should contain once exported. |
| h-m1 mode short names | `mem`, `transfer`, `spurious` | Must be renamed to `memorization`, `feature_transfer`, `spurious` in NPZ keys for h-c1 compatibility. |

**Verified from**: `docs/youra_research/h-m1/code/run_experiment.py`, `evaluate.py`, `config.py` (actual implementation, no `outputs/` directory present on disk).

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| C-1 | Fix h-m1 NPZ export | Add NPZ dump of raw per-probe scores (full mode names) to h-m1 run_experiment.py; regenerate if missing | 7 | 2+2+2+1 |
| C-2 | Config + data_loader | Config dataclass, NPZ loading, validation | 5 | 2+1+1+1 |
| C-3 | Reliability core | Cronbach's alpha, item-total corr, alpha-if-dropped | 8 | 3+2+2+1 |
| C-4 | Visualization | 3 figures (bar+CI, heatmap, alpha-if-dropped) | 6 | 2+2+1+1 |
| C-5 | Main orchestration + gate check | Wire modules, save gate_results.json, PASS/FAIL | 4 | 1+1+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [C-1, C-2, C-3, C-4, C-5]
