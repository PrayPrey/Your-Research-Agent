# H-M3 Architecture: OLS Regression on Divergence Gap Series

**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr
**Hypothesis:** H-M3 — Linear regression slope significance test on Coste et al. divergence gap series

Applied: standalone experiment pattern (mirror H-M2 structure, no cross-imports)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code (H-M2 actual implementation analyzed manually)
**Analyzed Path**: `docs/youra_research/h-m2/code/`
**Findings**: H-M2 uses dataclass config with yaml override, flat src/ layout (data/, analysis/, visualization/, reporting/), main.py orchestrates all steps, sys.exit(0/1) on gate result. H-M3 mirrors this exactly, replacing normalizer with regression module.

---

## File Organization

- `code/`
  - `main.py` — orchestrator
  - `config.py` — ExperimentConfig dataclass + load_config
  - `config.yaml` — path overrides (optional)
  - `src/`
    - `data/loader.py` — load h_m2_normalized_gap.csv
    - `analysis/regression.py` — OLS fit + bootstrap CI + gate check + mechanism verify
    - `visualization/plots.py` — 4 required figures
    - `reporting/reporter.py` — print_report + save_results

---

## Modules

### ExperimentConfig (`code/config.py`)

**Dependencies**: stdlib only (dataclasses, pathlib, yaml)

```python
@dataclass
class ExperimentConfig:
    input_csv_path: str = "docs/youra_research/h-m2/results/h_m2_normalized_gap.csv"
    figures_dir: str = "docs/youra_research/h-m3/figures"
    results_dir: str = "docs/youra_research/h-m3/results"
    results_filename: str = "h_m3_results.json"
    figure_dpi: int = 150
    n_boot: int = 10_000
    random_seed: int = 42

    def validate(self) -> None: ...

    @property
    def results_json_path(self) -> str: ...

def load_config(path: str = "config.yaml") -> ExperimentConfig: ...
```

---

### DataLoader (`code/src/data/loader.py`)

**Dependencies**: pandas, pathlib

```python
def load_dataset(csv_path: str) -> tuple[np.ndarray, np.ndarray]:
    """
    Returns: (kl_values, gap_values) — both shape (10,)
    Asserts: file exists, shape == (10, 2), no NaN
    """
    ...
```

---

### RegressionAnalysis (`code/src/analysis/regression.py`)

**Dependencies**: scipy.stats, statsmodels.api, numpy

```python
def fit_ols_regression(
    kl_values: np.ndarray,
    gap_values: np.ndarray,
    n_boot: int = 10_000,
    seed: int = 42,
) -> dict:
    """
    Returns: slope, intercept, r_squared, p_value, std_err,
             t_stat, ci_parametric, ci_bootstrap, n
    """
    ...

def check_gate(results: dict) -> tuple[bool, str]:
    """slope > 0 AND p < 0.05 AND R² > 0.5. Returns (pass, reason)."""
    ...

def verify_mechanism_activated(results: dict) -> tuple[bool, dict]:
    """Checks n==10, slope not NaN, p valid, R² valid, CI computed."""
    ...
```

---

### Plots (`code/src/visualization/plots.py`)

**Dependencies**: matplotlib, numpy, pathlib

```python
def plot_gate_metrics(results: dict, figures_dir: str, dpi: int) -> Path: ...
def plot_regression_scatter(kl, gap, results: dict, figures_dir: str, dpi: int) -> Path: ...
def plot_residuals(kl, gap, results: dict, figures_dir: str, dpi: int) -> Path: ...
def plot_bootstrap_histogram(results: dict, figures_dir: str, dpi: int) -> Path: ...
```

---

### Reporter (`code/src/reporting/reporter.py`)

**Dependencies**: json, pathlib, numpy

```python
def print_report(results: dict) -> None: ...
def save_results(results: dict, out_path: str) -> None: ...
```

---

### Main (`code/main.py`)

**Dependencies**: all src modules, argparse, sys

```python
def main() -> None:
    # 1. load_config
    # 2. load_dataset → (kl_values, gap_values)
    # 3. fit_ols_regression → results
    # 4. verify_mechanism_activated(results)
    # 5. check_gate(results) → gate_pass, gate_reason
    # 6. plot_* × 4
    # 7. print_report, save_results
    # 8. sys.exit(0 if gate_pass else 1)
    ...
```

---

## External Dependencies (Base Hypothesis)

H-M3 is standalone — no imports from H-M2 code. Dataset only is reused via file path.

| Resource | Path |
|----------|------|
| Input CSV | `docs/youra_research/h-m2/results/h_m2_normalized_gap.csv` |

**Verified from**: `docs/youra_research/h-m2/code/src/config.py` — `gap_csv = "h_m2_normalized_gap.csv"` under `results_dir = "docs/youra_research/h-m2/results"`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project setup | Scaffold code/ layout, config.py, config.yaml, dirs | 5 | 1+1+1+2 |
| A-2 | Data loader | load_dataset with assertions (file, shape, NaN) | 6 | 1+1+2+2 |
| A-3 | OLS regression | fit_ols_regression: scipy linregress + statsmodels CI | 10 | 3+2+3+2 |
| A-4 | Bootstrap CI | 10k-iteration bootstrap inside regression module | 9 | 2+1+4+2 |
| A-5 | Mechanism verify + gate | verify_mechanism_activated + check_gate | 7 | 2+2+2+1 |
| A-6 | Visualization | 4 figures (gate bar, scatter+CI, residuals, bootstrap hist) | 10 | 2+2+3+3 |
| A-7 | Reporter | print_report + save_results (JSON) | 5 | 1+1+1+2 |
| A-8 | Main orchestrator + exit code | Wire all modules, sys.exit(0/1) | 6 | 1+2+1+2 |

**Distribution**: High(9-10): [A-3, A-4, A-6], Medium(6-8): [A-2, A-5, A-8], Low(4-5): [A-1, A-7]
