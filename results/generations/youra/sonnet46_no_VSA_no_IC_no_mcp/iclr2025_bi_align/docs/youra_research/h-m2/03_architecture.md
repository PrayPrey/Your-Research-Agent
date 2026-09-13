# H-M2 Architecture: Calibration-Alignment Divergence Gap

**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr
**Hypothesis:** h-m2 — normalized RM score minus gold preference rate is strictly positive at high KL levels

Applied: Strategy (normalization pipeline extending h-m1 output)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** patterns found from base code (manual read)
**Analyzed Path:** `docs/youra_research/h-m1/code/`
**Findings:** h-m1 uses `load_dataset` → `run_analysis` → `plot_*` → `print_report/save_results` pipeline with dataclass config; all modules reusable with h-m2-specific analysis layer dropped in.

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_dataset | `from src.data.loader import load_dataset` | `h-m1/code/src/data/loader.py` |
| ExperimentConfig / load_config | `from src.config import load_config` | `h-m1/code/src/config.py` |
| print_report, save_results | `from src.reporting.reporter import print_report, save_results` | `h-m1/code/src/reporting/reporter.py` |

**Verified from:** `docs/youra_research/h-m1/code/` (actual implementation)

**Note:** h-m1 modules are NOT imported directly — h-m2 is a standalone experiment under its own `code/` tree. The patterns are reused, not the import paths.

---

## File Organization

```
docs/youra_research/h-m2/
├── 03_architecture.md          (this file)
├── figures/                    (output figures, auto-created)
├── results/                    (output CSV + JSON, auto-created)
└── code/
    ├── config.yaml             (optional overrides)
    ├── main.py                 (entry point)
    └── src/
        ├── config.py           (ExperimentConfig dataclass)
        ├── data/
        │   └── loader.py       (load h-m1 CSV, validate columns)
        ├── analysis/
        │   └── normalizer.py   (normalize RM, compute gap, run stats)
        ├── visualization/
        │   └── plots.py        (4 required figures)
        └── reporting/
            └── reporter.py     (stdout + JSON + CSV save)
```

---

## Module Definitions

### Config (`src/config.py`)

**Dependencies:** stdlib only (dataclasses, pathlib, yaml)

```python
@dataclass
class ExperimentConfig:
    input_csv_path: str = "../../h-m1/results/h_m1_divergence_curve.csv"
    figures_dir: str = "docs/youra_research/h-m2/figures"
    results_dir: str = "docs/youra_research/h-m2/results"
    results_filename: str = "h_m2_results.json"
    gap_csv: str = "h_m2_gap_curve.csv"
    figure_dpi: int = 150
    high_kl_min_positive: int = 3   # gate threshold

    def validate(self) -> None: ...

    @property
    def results_json_path(self) -> str: ...
    @property
    def gap_csv_path(self) -> str: ...

def load_config(path: str = "config.yaml") -> ExperimentConfig: ...
```

---

### Loader (`src/data/loader.py`)

**Dependencies:** pandas

```python
REQUIRED_COLS = ["kl_budget", "rm_score", "gold_preference"]

def load_dataset(csv_path: str) -> pd.DataFrame: ...
# Validates columns present, no NaN in required cols, N >= 5
```

---

### Normalizer (`src/analysis/normalizer.py`)

**Dependencies:** numpy, scipy.stats

```python
def normalize_rm(rm: np.ndarray) -> np.ndarray: ...
# (rm - rm.min()) / (rm.max() - rm.min()) → shape (N,) in [0,1]

def compute_gap(rm_norm: np.ndarray, gold: np.ndarray) -> np.ndarray: ...
# rm_norm - gold → shape (N,)

def run_gap_analysis(df: pd.DataFrame, high_kl_min_positive: int = 3) -> dict: ...
# Returns:
#   kl, rm, gold, rm_norm, gap (arrays)
#   median_kl, high_kl_mask
#   n_positive_high_kl, rho_gap_kl, p_rho_gap
#   mean_gap_high_kl, max_gap, prop_positive
#   gate_pass (bool)
#   gate_reason (str)
```

---

### Plots (`src/visualization/plots.py`)

**Dependencies:** matplotlib, numpy

```python
def plot_gap_curve(kl: np.ndarray, gap: np.ndarray,
                   high_kl_mask: np.ndarray, figs_dir: str, dpi: int) -> None: ...
# Line/bar chart of gap vs KL; zero line; shaded high-KL region; annotate max_gap

def plot_dual_line(kl: np.ndarray, rm_norm: np.ndarray,
                   gold: np.ndarray, figs_dir: str, dpi: int) -> None: ...
# RM_norm and gold on same [0,1] axis vs KL; shows crossover

def plot_gap_scatter(kl: np.ndarray, gap: np.ndarray,
                     rho: float, high_kl_mask: np.ndarray,
                     figs_dir: str, dpi: int) -> None: ...
# Scatter gap vs KL; high-KL points distinct; annotate Spearman rho

def plot_gate_metrics(results: dict, figs_dir: str, dpi: int) -> None: ...
# Bar chart: n_positive_high_kl vs 3, rho_gap_kl vs 0, prop_positive vs 0.5
```

---

### Reporter (`src/reporting/reporter.py`)

**Dependencies:** json, pathlib, numpy, pandas

```python
def print_report(results: dict) -> None: ...
# Stdout formatted report: gate PASS/FAIL, all metrics

def save_results(results: dict, out_path: str) -> None: ...
# JSON dump (excluding numpy arrays)

def save_gap_curve(df: pd.DataFrame, rm_norm: np.ndarray,
                   gap: np.ndarray, out_path: str) -> None: ...
# CSV: kl_budget, rm_score, rm_norm, gold_preference, gap_norm
```

---

### Main (`main.py`)

**Dependencies:** all src modules

```python
def main() -> None: ...
# load_config → validate → load_dataset → run_gap_analysis
# → 4 plots → print_report → save_results → save_gap_curve
# sys.exit(0 if gate_pass else 1)
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project scaffold | Directory structure, config.yaml, ExperimentConfig dataclass | 5 | 1+1+1+2 |
| A-2 | Data loader | load_dataset with column/NaN validation for h-m1 CSV | 5 | 1+1+1+2 |
| A-3 | Normalization + gap | normalize_rm, compute_gap, run_gap_analysis with gate logic | 9 | 2+2+3+2 |
| A-4 | Visualization | 4 required plot functions (gap curve, dual line, scatter, gate metrics) | 10 | 2+2+3+3 |
| A-5 | Reporting | print_report, save_results JSON, save_gap_curve CSV | 6 | 1+2+1+2 |
| A-6 | Main + integration | main.py wiring all modules; gate exit code; end-to-end test | 7 | 1+2+2+2 |

**Distribution:** VeryHigh(18-20): [] | High(14-17): [] | Medium(9-13): [A-3, A-4] | Low(4-8): [A-1, A-2, A-5, A-6]

---

## Gate Verification Logic

In `run_gap_analysis`:
```python
gate_pass = (n_positive_high_kl >= cfg.high_kl_min_positive) and (rho_gap_kl > 0)
```

Expected values (pre-computed):
- `n_positive_high_kl = 5` (all 5 high-KL gaps > 0) → PASS
- `rho_gap_kl ≈ 1.000` → PASS
- `max_gap ≈ 0.620` at KL=8
- `mean_gap_high_kl ≈ 0.466`
- `prop_positive = 0.70`
