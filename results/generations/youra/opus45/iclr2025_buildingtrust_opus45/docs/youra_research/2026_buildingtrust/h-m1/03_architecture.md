# Architecture Design: H-M1 Conditional Margin Inflation Analysis

**Hypothesis:** H-M1 (MECHANISM)
**Date:** 2026-03-24
**Type:** Statistical reanalysis — no model inference required

Applied: statistical-reanalysis-pipeline pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Analyzed via direct file reads (Serena project selection unavailable; Read tool used as fallback)
**Analyzed Path**: `docs/youra_research/20260323_buildingtrust/h-e1/code/`
**Findings**: H-E1 flat module layout. Cache at `h-e1/cache/{family}/`. `compute_conditional_margins()` in metrics.py returns `{mean_correct, mean_incorrect}`. Local import style via `sys.path.insert`. Results in `h-e1/results/`. Experiment JSON at `h-e1/experiment_results.json`.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual H-E1 Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| compute_conditional_margins | `sys.path` + `from metrics import compute_conditional_margins` | `h-e1/code/metrics.py` |
| compute_auroc_with_ci | `sys.path` + `from metrics import compute_auroc_with_ci` | `h-e1/code/metrics.py` |
| SEED, BOOTSTRAP_N | `sys.path` + `from config import SEED, BOOTSTRAP_N` | `h-e1/code/config.py` |

**Cache file paths (verified from h-e1/code/config.py):**
- `CACHE_DIR = h-e1/cache/`
- Per-family subfolder: `h-e1/cache/{family}/`
- Array files: `{family}_base_margins.npy`, `{family}_base_correctness.npy`, `{family}_instruct_margins.npy`, `{family}_instruct_correctness.npy`

**Verified from**: `h-e1/code/` (actual implementation)

---

## File Organization

```
h-m1/code/
  config.py          - constants, paths, model families
  data_loader.py     - load and validate H-E1 cached arrays
  analysis.py        - conditional margin computation + permutation test
  visualize.py       - all figure generation
  report.py          - results serialization + validation report
  run_experiment.py  - main orchestrator
h-m1/figures/        - output figures
h-m1/experiment_results.yaml
h-m1/04_validation.md
```

---

## Module Definitions

### Config (`h-m1/code/config.py`)

**Dependencies**: pathlib, os

```python
SEED: int = 42
PERMUTATION_N: int = 9999
BOOTSTRAP_N: int = 1000
FAMILIES: list[str] = ["qwen", "mistral"]

# H-E1 cache root (absolute, resolved at import time)
H_E1_CODE_DIR: Path = ...
H_E1_CACHE_DIR: Path = H_E1_CODE_DIR.parent / "cache"
H_E1_RESULTS_JSON: Path = H_E1_CODE_DIR.parent / "experiment_results.json"

# H-M1 output dirs
CODE_DIR: Path = Path(__file__).parent
HYPOTHESIS_DIR: Path = CODE_DIR.parent
FIGURES_DIR: Path = HYPOTHESIS_DIR / "figures"

def ensure_directories() -> None: ...
```

---

### DataLoader (`h-m1/code/data_loader.py`)

**Dependencies**: config, numpy

```python
def load_family_arrays(
    family: str,
    cache_dir: Path,
) -> dict[str, np.ndarray]:
    """
    Returns:
        {
          "base_margins": np.ndarray,     # (N,) float
          "base_correctness": np.ndarray, # (N,) int {0,1}
          "inst_margins": np.ndarray,
          "inst_correctness": np.ndarray,
        }
    """
    ...

def validate_arrays(arrays: dict[str, np.ndarray]) -> None:
    """Raise ValueError if shapes mismatch or values invalid."""
    ...

def load_h_e1_results_json(json_path: Path) -> dict: ...
```

---

### Analysis (`h-m1/code/analysis.py`)

**Dependencies**: config, numpy, scipy.stats

```python
def compute_conditional_stats(
    margins: np.ndarray,
    correctness: np.ndarray,
) -> dict[str, float]:
    """
    Returns:
        mean_correct, mean_incorrect, se_correct, se_incorrect,
        n_correct, n_incorrect
    """
    ...

def run_permutation_test(
    base_margins: np.ndarray,
    base_correctness: np.ndarray,
    inst_margins: np.ndarray,
    inst_correctness: np.ndarray,
    n_resamples: int = PERMUTATION_N,
    seed: int = SEED,
) -> dict[str, float]:
    """
    Returns:
        p_value, statistic (mean_inst_incorrect - mean_base_incorrect)
    """
    ...

def compute_effect_size(
    base_margins_incorrect: np.ndarray,
    inst_margins_incorrect: np.ndarray,
) -> dict[str, float]:
    """
    Returns:
        raw_diff, inflation_ratio, cohens_d
    """
    ...

def compute_bootstrap_ci(
    base_margins_incorrect: np.ndarray,
    inst_margins_incorrect: np.ndarray,
    n_bootstrap: int = BOOTSTRAP_N,
    seed: int = SEED,
) -> dict[str, float]:
    """
    Returns:
        ci_lower, ci_upper (95% CI on mean difference)
    """
    ...

def compute_kl_divergence(
    base_margins: np.ndarray,
    inst_margins: np.ndarray,
    n_bins: int = 100,
) -> float: ...

def analyze_family(
    family: str,
    arrays: dict[str, np.ndarray],
) -> dict:
    """
    Runs full per-family analysis pipeline.
    Returns structured results dict matching experiment_results.yaml schema.
    """
    ...
```

---

### Visualize (`h-m1/code/visualize.py`)

**Dependencies**: config, numpy, matplotlib, seaborn

```python
def plot_gate_metrics(
    family_results: dict[str, dict],
    figures_dir: Path,
) -> str:
    """Bar chart: E[margin|incorrect] base vs instruct per family. Returns path."""
    ...

def plot_kde_distributions(
    family_results: dict[str, dict],
    arrays_by_family: dict[str, dict],
    figures_dir: Path,
) -> str:
    """4-panel KDE: base-correct, base-incorrect, inst-correct, inst-incorrect."""
    ...

def plot_box_plots(
    arrays_by_family: dict[str, dict],
    figures_dir: Path,
) -> str: ...

def plot_inflation_ratios(
    family_results: dict[str, dict],
    figures_dir: Path,
) -> str:
    """Bar chart: correct_ratio vs incorrect_ratio per family."""
    ...

def plot_forest(
    family_results: dict[str, dict],
    figures_dir: Path,
) -> str:
    """Effect sizes with 95% CIs + pooled estimate."""
    ...

def save_all_figures(
    family_results: dict[str, dict],
    arrays_by_family: dict[str, dict],
    figures_dir: Path,
) -> list[str]: ...
```

---

### Report (`h-m1/code/report.py`)

**Dependencies**: config, yaml, pathlib, datetime

```python
def save_experiment_results_yaml(
    family_results: dict[str, dict],
    gate_result: str,
    output_path: Path,
) -> None:
    """
    Writes experiment_results.yaml conforming to PRD schema.
    gate_result: "PASS" | "FAIL"
    """
    ...

def generate_validation_report(
    family_results: dict[str, dict],
    gate_result: str,
    output_path: Path,
) -> None:
    """Writes 04_validation.md markdown report."""
    ...

def evaluate_gate(family_results: dict[str, dict]) -> str:
    """
    Returns "PASS" if all families have gate_pass=True, else "FAIL".
    """
    ...
```

---

### RunExperiment (`h-m1/code/run_experiment.py`)

**Dependencies**: config, data_loader, analysis, visualize, report, logging

```python
def set_seed(seed: int = SEED) -> None: ...

def main(families: list[str] = None) -> None:
    """
    Orchestrates: load -> validate -> analyze -> visualize -> report.
    """
    ...

# if __name__ == "__main__": argparse entry point
```

---

## Data Flow

- `run_experiment.py` calls `data_loader.load_family_arrays()` for each family
- Arrays passed to `analysis.analyze_family()` -> per-family results dict
- Results passed to `visualize.save_all_figures()` and `report.*`
- Gate evaluated in `report.evaluate_gate()` -> PASS/FAIL
- Outputs: `h-m1/experiment_results.yaml`, `h-m1/04_validation.md`, `h-m1/figures/*.png`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Create h-m1/code/ structure, config.py with H-E1 paths, ensure_directories | 5 | 1+1+1+2 |
| A-2 | Data Loader | load_family_arrays(), validate_arrays(), load_h_e1_results_json() | 8 | 2+2+2+2 |
| A-3 | Conditional Stats | compute_conditional_stats(), extract correct/incorrect partitions | 7 | 2+2+2+1 |
| A-4 | Permutation Test | run_permutation_test() with scipy.stats.permutation_test, seed handling | 10 | 2+2+4+2 |
| A-5 | Effect Size + CI | compute_effect_size(), compute_bootstrap_ci(), compute_kl_divergence() | 9 | 2+2+3+2 |
| A-6 | analyze_family() | Integrate A-3/A-4/A-5 into per-family pipeline, gate_pass logic | 8 | 2+3+2+1 |
| A-7 | Gate Metrics Plot | plot_gate_metrics() bar chart with CI error bars (REQUIRED figure) | 7 | 2+1+2+2 |
| A-8 | Additional Figures | plot_kde_distributions(), plot_box_plots(), plot_inflation_ratios(), plot_forest() | 11 | 3+2+3+3 |
| A-9 | Results Reporting | save_experiment_results_yaml(), generate_validation_report(), evaluate_gate() | 8 | 2+2+2+2 |
| A-10 | Orchestrator | run_experiment.py main(), argparse, logging, end-to-end wiring | 9 | 2+3+2+2 |
| A-11 | Tests + Validation | Smoke tests for data loading, analysis output shapes, gate evaluation logic | 7 | 2+2+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-4, A-5, A-8, A-10], Low(4-8): [A-1, A-2, A-3, A-6, A-7, A-9, A-11]

---

## Notes for Phase 4 Coder

- H-E1 cache path resolution: read `h-e1/code/config.py` `CACHE_DIR` at runtime; do NOT hardcode
- H-E1 uses `sys.path.insert(0, str(CODE_DIR))` pattern; H-M1 should do the same for its own imports
- `compute_conditional_margins()` in H-E1 `metrics.py` can be imported directly, or reimplemented locally (recommended for isolation)
- Permutation test on ~14k samples with n_resamples=9999 is CPU-only and completes in < 5 minutes
- Llama family is explicitly skipped (gated in H-E1); FAMILIES config contains only `["qwen", "mistral"]`
- Gate pass requires BOTH families to pass: p < 0.05 AND mean_inst_incorrect > mean_base_incorrect
