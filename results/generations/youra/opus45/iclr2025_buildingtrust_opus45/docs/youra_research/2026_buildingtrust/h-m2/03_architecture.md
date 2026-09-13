# Architecture: H-M2
# Percentile-Normalized Monotonicity Attenuation

**Version:** 1.0
**Date:** 2026-03-24
**Hypothesis ID:** h-m2
**Type:** MECHANISM
**Gate:** MUST_WORK

Applied: bootstrap-CI-logistic-regression (scipy.stats.zscore + sklearn.LogisticRegression + sklearn.utils.resample)
Applied: flat-module-layout (mirrors h-m1 code structure)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code (read via direct file access; Serena project activation not available)
**Analyzed Path**: `docs/youra_research/20260323_buildingtrust/h-m1/code/`
**Findings**: H-M1 uses flat layout (config.py, data_loader.py, analysis.py, visualize.py, report.py, run_experiment.py). Config resolves H-E1 cache via `HYPOTHESIS_DIR.parent / "h-e1" / "cache"`. Data loader reads `.npy` files from `h-e1/cache/{family}/`. H-M2 reuses same flat layout and same H-E1 path resolution.

---

## File Organization

```
h-m2/
  code/
    config.py           - constants, H-E1 path resolution, output paths
    data_loader.py      - load/validate H-E1 .npy arrays per family
    analysis.py         - zscore norm, logistic regression, bootstrap CI, diff test, 2x2 analysis
    visualize.py        - bar chart, bootstrap histograms, logistic curves, forest plot
    report.py           - YAML results, gate eval, 04_validation.md
    run_experiment.py   - main orchestrator
    tests/
      __init__.py
      test_analysis.py
  figures/              - output PNGs (dpi=300)
  experiment_results.yaml
  04_validation.md
```

---

## Module Definitions

### Config (`code/config.py`)

**Dependencies**: pathlib

```python
SEED: int = 42
BOOTSTRAP_N: int = 1000
FAMILIES: list[str] = ["qwen", "mistral"]
GATE_TYPE: str = "MUST_WORK"
P_VALUE_THRESHOLD: float = 0.05
LR_C: float = 1e6
LR_MAX_ITER: int = 1000

CODE_DIR: Path = Path(__file__).parent
HYPOTHESIS_DIR: Path = CODE_DIR.parent
H_E1_CACHE_DIR: Path = HYPOTHESIS_DIR.parent / "h-e1" / "cache"

FIGURES_DIR: Path = HYPOTHESIS_DIR / "figures"
RESULTS_YAML: Path = HYPOTHESIS_DIR / "experiment_results.yaml"
VALIDATION_MD: Path = HYPOTHESIS_DIR / "04_validation.md"

def ensure_directories() -> None: ...
```

---

### DataLoader (`code/data_loader.py`)

**Dependencies**: config, numpy, pathlib

```python
def load_family_arrays(
    family: str,
    cache_dir: Path = None,
) -> dict[str, np.ndarray]:
    """
    Load base/instruct margins and correctness arrays for one family.
    Returns: {base_margins, base_correctness, inst_margins, inst_correctness}
    Reads from H_E1_CACHE_DIR/{family}/*.npy (same naming as h-m1)
    """
    ...

def validate_arrays(
    arrays: dict[str, np.ndarray],
    expected_n: int = 14042,
) -> None:
    """Raise ValueError if shapes mismatch, wrong N, non-binary correctness, non-finite margins."""
    ...

def load_all_families(
    families: list[str] = None,
    cache_dir: Path = None,
) -> dict[str, dict[str, np.ndarray]]:
    """Returns {family: arrays_dict} for each family in FAMILIES."""
    ...
```

---

### Analysis (`code/analysis.py`)

**Dependencies**: config, numpy, scipy.stats, sklearn.linear_model, sklearn.utils

```python
def zscore_normalize(margins: np.ndarray) -> np.ndarray:
    """scipy.stats.zscore; returns zeros if std=0 (constant margins edge case)."""
    ...

def compute_beta_percentile(
    margins: np.ndarray,
    correctness: np.ndarray,
) -> float:
    """
    Fit LogisticRegression(solver='lbfgs', C=LR_C, max_iter=LR_MAX_ITER)
    on zscore_normalize(margins). Returns coef_[0][0].
    """
    ...

def bootstrap_beta(
    margins: np.ndarray,
    correctness: np.ndarray,
    n_iterations: int = BOOTSTRAP_N,
    seed: int = SEED,
) -> np.ndarray:
    """
    Bootstrap resampling using sklearn.utils.resample.
    Returns: (n_iterations,) array of beta values.
    """
    ...

def compute_bootstrap_ci(
    betas: np.ndarray,
    alpha: float = 0.05,
) -> tuple[float, float, float]:
    """Returns (beta_mean, ci_lower_2.5, ci_upper_97.5) via percentile method."""
    ...

def bootstrap_difference_test(
    base_margins: np.ndarray,
    base_correctness: np.ndarray,
    inst_margins: np.ndarray,
    inst_correctness: np.ndarray,
    n_iterations: int = BOOTSTRAP_N,
    seed: int = SEED,
) -> dict[str, float]:
    """
    Paired bootstrap: resample same indices for base and instruct per iteration.
    Computes delta_beta = beta_base - beta_instruct per sample.
    Returns: {delta_beta_mean, delta_ci_lower, delta_ci_upper,
              p_value (proportion Δβ <= 0), effect_size (Δβ_mean / pooled_std)}
    """
    ...

def run_2x2_analysis(
    arrays_by_family: dict[str, dict[str, np.ndarray]],
) -> dict[str, dict[str, float]]:
    """
    Compute beta_percentile per (family x model_type) cell.
    Returns: {family: {base: float, instruct: float}}
    Falls back to 1x2 if prompt_format unavailable.
    """
    ...

def analyze_family(
    family: str,
    arrays: dict[str, np.ndarray],
) -> dict:
    """
    Full per-family pipeline: zscore -> beta -> bootstrap_beta -> CI -> diff test -> gate.
    Returns structured dict: {family, base_beta, base_ci, inst_beta, inst_ci,
                               delta_beta, p_value, effect_size, gate_pass}
    gate_pass: beta_instruct < beta_base AND p_value < P_VALUE_THRESHOLD
    """
    ...
```

---

### Visualize (`code/visualize.py`)

**Dependencies**: config, numpy, matplotlib, pathlib

```python
def plot_gate_metrics(
    family_results: dict[str, dict],
    figures_dir: Path = None,
) -> str:
    """Bar chart: beta_percentile base vs instruct per family with 95% CI error bars. Returns path."""
    ...

def plot_bootstrap_distributions(
    family_results: dict[str, dict],
    figures_dir: Path = None,
) -> str:
    """Overlaid histograms of bootstrap beta distributions (base vs instruct) per family."""
    ...

def plot_logistic_curves(
    family_results: dict[str, dict],
    arrays_by_family: dict[str, dict],
    figures_dir: Path = None,
) -> str:
    """Pr(correct) vs z-score(margin) sigmoid curves for each condition."""
    ...

def plot_forest(
    family_results: dict[str, dict],
    figures_dir: Path = None,
) -> str:
    """Forest plot: delta_beta effect sizes with 95% CIs per family."""
    ...

def save_all_figures(
    family_results: dict[str, dict],
    arrays_by_family: dict[str, dict],
    figures_dir: Path = None,
) -> list[str]:
    """Run all figure generators. Returns list of saved file paths."""
    ...
```

---

### Report (`code/report.py`)

**Dependencies**: config, yaml, pathlib, datetime

```python
def evaluate_gate(family_results: dict[str, dict]) -> str:
    """Returns 'PASS' if all families gate_pass=True, else 'FAIL'."""
    ...

def save_experiment_results_yaml(
    family_results: dict[str, dict],
    gate_result: str,
    output_path: Path = None,
) -> None:
    """Write experiment_results.yaml with beta values, CIs, p-values, effect sizes, gate."""
    ...

def generate_validation_report(
    family_results: dict[str, dict],
    gate_result: str,
    output_path: Path = None,
) -> None:
    """Write 04_validation.md: markdown summary table + gate pass/fail section."""
    ...
```

---

### RunExperiment (`code/run_experiment.py`)

**Dependencies**: config, data_loader, analysis, visualize, report, logging, argparse

```python
def main(families: list[str] = None) -> None:
    """
    1. ensure_directories()
    2. load_all_families()
    3. validate_arrays() per family
    4. analyze_family() per family
    5. run_2x2_analysis()
    6. save_all_figures()
    7. evaluate_gate() + save_experiment_results_yaml() + generate_validation_report()
    8. Log gate result; exit 0 if PASS, 1 if FAIL
    """
    ...

if __name__ == "__main__":
    # argparse: --families qwen mistral
    ...
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual H-M1 Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| H-E1 cache path pattern | `HYPOTHESIS_DIR.parent / "h-e1" / "cache"` | `h-m1/code/config.py` line 27 |
| load_family_arrays pattern | mirrored directly | `h-m1/code/data_loader.py` |
| validate_arrays pattern | mirrored directly | `h-m1/code/data_loader.py` |

**Verified from**: `h-m1/code/config.py` and `h-m1/code/data_loader.py` (actual implementation)

**Cache file naming (verified from h-m1 data_loader):**
- Files live in `h-e1/cache/{family}/`
- Glob `*.npy`; stem containing `instruct`/`chat` -> instruct variant; else base
- Stem containing `margin` -> margins array; `correct` -> correctness array

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | h-m2/code/ structure, config.py with H-E1 paths, ensure_directories | 5 | 1+1+1+2 |
| A-2 | Data Loader | load_all_families(), validate_arrays(), integrity check 14042 samples | 7 | 2+2+1+2 |
| A-3 | Zscore + Beta | zscore_normalize() (std=0 guard), compute_beta_percentile() | 8 | 2+2+2+2 |
| A-4 | Bootstrap CI | bootstrap_beta(), compute_bootstrap_ci() with seed and percentile method | 9 | 2+2+3+2 |
| A-5 | Difference Test | bootstrap_difference_test(): paired Δβ, p-value, effect_size | 11 | 3+2+4+2 |
| A-6 | Family Pipeline | analyze_family() integrating A-3/A-4/A-5; gate_pass logic | 8 | 2+3+2+1 |
| A-7 | 2x2 Analysis | run_2x2_analysis(), main effect + fallback to 1x2 | 9 | 2+2+3+2 |
| A-8 | Gate Metrics Plot | plot_gate_metrics() bar chart with CI error bars (REQUIRED figure) | 7 | 2+1+2+2 |
| A-9 | Additional Figures | plot_bootstrap_distributions(), plot_logistic_curves(), plot_forest() | 11 | 3+2+3+3 |
| A-10 | Results Reporting | evaluate_gate(), save_experiment_results_yaml(), generate_validation_report() | 8 | 2+2+2+2 |
| A-11 | Orchestrator | run_experiment.py main(), argparse, logging, end-to-end wiring | 9 | 2+3+2+2 |
| A-12 | Unit Tests | test_analysis.py: zscore edge case, beta correctness, CI bounds, gate logic | 7 | 2+2+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-4, A-5, A-7, A-9, A-11], Low(4-8): [A-1, A-2, A-3, A-6, A-8, A-10, A-12]

---

## Notes for Phase 4 Coder

- H-E1 cache path resolution: `HYPOTHESIS_DIR.parent / "h-e1" / "cache"` (verified from h-m1/code/config.py)
- Array file glob: `h-e1/cache/{family}/*.npy`; use stem to detect variant and type (same logic as h-m1 data_loader)
- `zscore_normalize`: check `np.std(margins) == 0` before dividing; return `np.zeros_like(margins)` if constant
- Bootstrap difference test: resample SAME indices for base and instruct per iteration to preserve pairing
- Gate requires BOTH families pass: `beta_instruct < beta_base` AND `p_value < 0.05`
- No GPU required; expected runtime <5 min CPU with BOOTSTRAP_N=1000
- FAMILIES = ["qwen", "mistral"] only (llama excluded, gated in H-E1)
- Python deps: numpy, scipy, scikit-learn, matplotlib, pyyaml (no seaborn required)
