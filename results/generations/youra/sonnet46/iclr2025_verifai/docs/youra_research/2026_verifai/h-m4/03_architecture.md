# Architecture: h-m4
# Difficulty-Stratified ECE + DELTA_ECE Gate + Temperature Scaling Probe

**Date:** 2026-03-18
**Hypothesis:** h-m4 (MECHANISM — Step 4 of 4)
**Gate:** MUST_WORK — DELTA_ECE >= 0.03 in >= 2/3 models, CI excludes zero, persists post-T

Applied: pipeline-results-loader (h-m3 tier CSV + JSON loading patterns reused for data alignment)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/20260316_verifia/h-m3/code/src/h_m3/`
**Findings**: h-m3 uses `src/h_m3/` package structure with `data_loader.py`, `evaluate.py`, `config.py`, `visualize.py`, `run_hm3_ptrue.py`. Data loader supports both wide and long CSV formats; imports from `h_m3.config` for MODEL_SHORT_NAMES. h-m4 is CPU-only statistical analysis — no model loading or GPU code reused.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_tier_assignments | `from h_m3.data_loader import load_tier_assignments` | `h-m3/code/src/h_m3/data_loader.py` |
| filter_hard_easy_tiers | `from h_m3.data_loader import filter_hard_easy_tiers` | `h-m3/code/src/h_m3/data_loader.py` |
| MODEL_SHORT_NAMES | `from h_m3.config import MODEL_SHORT_NAMES` | `h-m3/code/src/h_m3/config.py` |

**Verified from**: `docs/youra_research/20260316_verifia/h-m3/code/src/h_m3/` (actual implementation)

**Note**: h-m4 does NOT import h-m3 package at runtime. The tier loading patterns are replicated in h-m4's own `data_loader.py` with added confidence score and correctness loading. Relative path conventions from h-m3 config (`../../h-m2/results`, `../../h-e1/results`) are preserved in h-m4 config.

---

## File Organization

```
h-m4/
  src/
    data_loader.py         # load + align confidence, tier, correctness data
    evaluate.py            # ECE, DELTA_ECE, bootstrap CI, null baseline, sensitivity
    temperature_scaling.py # fit T*, recompute post-T ECE metrics
    visualize.py           # 6 required figures
    run_experiment.py      # orchestration entry point
    config.py              # constants and path configuration
  tests/
    test_data_loader.py
    test_ece.py
    test_bootstrap.py
    test_temperature.py
  results/
    delta_ece_results.json
  figures/
    fig1_delta_ece_gate.png
    fig2_reliability_diagrams.png
    fig3_temperature_scaling.png
    fig4_null_baseline.png
    fig5_m_sensitivity.png
    fig6_bootstrap_distribution.png
```

---

## Module Definitions

### Config (`src/config.py`)

**Dependencies**: stdlib only

```python
# Constants
MODEL_SHORT_NAMES: dict[str, str]   # full model ID → short name
MODEL_IDS: list[str]                # 3 model IDs
SEED: int = 42
N_BOOT: int = 1000
M_PRIMARY: int = 15
M_SENSITIVITY: list[int] = [10, 15, 20]
DELTA_ECE_THRESHOLD: float = 0.03
MIN_TIER_SIZE: int = 20
HOLDOUT_FRAC: float = 0.2
HARD_THRESHOLD: float = 0.0
EASY_THRESHOLD: float = 0.6

# Path defaults (relative to h-m4/ folder)
DEFAULT_HM3_RESULTS: str = "../h-m3/results"
DEFAULT_HM2_RESULTS: str = "../h-m2/results"
DEFAULT_HE1_RESULTS: str = "../h-e1/results"
DEFAULT_OUTPUT_DIR: str = "results"
DEFAULT_FIGURES_DIR: str = "figures"

@dataclass
class ExperimentConfig:
    hm3_results: str = DEFAULT_HM3_RESULTS
    hm2_results: str = DEFAULT_HM2_RESULTS
    he1_results: str = DEFAULT_HE1_RESULTS
    output_dir: str = DEFAULT_OUTPUT_DIR
    figures_dir: str = DEFAULT_FIGURES_DIR
    seed: int = SEED
    n_boot: int = N_BOOT
    m_primary: int = M_PRIMARY

@dataclass
class FigureConfig:
    figures_dir: str = "figures"
    dpi: int = 150
    fig1_filename: str = "fig1_delta_ece_gate.png"
    fig2_filename: str = "fig2_reliability_diagrams.png"
    fig3_filename: str = "fig3_temperature_scaling.png"
    fig4_filename: str = "fig4_null_baseline.png"
    fig5_filename: str = "fig5_m_sensitivity.png"
    fig6_filename: str = "fig6_bootstrap_distribution.png"
```

---

### DataLoader (`src/data_loader.py`)

**Dependencies**: config, numpy, pandas, json, pathlib

```python
def load_confidence_scores(hm3_results_dir: Path) -> dict[str, dict[str, list[float]]]:
    """Load ptrue_confidence_scores.json.
    Returns: {model_short: {task_id: [c_values]}}
    Raises: FileNotFoundError if missing.
    """
    ...

def load_tier_assignments(hm2_results_dir: Path) -> pd.DataFrame:
    """Load tier_assignments.csv; supports wide format from h-m2.
    Returns: DataFrame[task_id, model_short, tier]
    """
    ...

def load_correctness(he1_results_dir: Path, model_short: str) -> dict[str, int]:
    """Load correctness_{model_short}.json.
    Returns: {task_id: binary_label} where label = int(mean(solutions) > 0)
    Raises: FileNotFoundError if missing.
    """
    ...

def align_model_data(
    confidence: dict[str, dict[str, list[float]]],
    tier_df: pd.DataFrame,
    correctness: dict[str, dict[str, int]],
    model_short: str,
) -> dict[str, dict]:
    """Align c values, tier labels, correctness for one model.
    Returns: {
        "c_hard": np.ndarray, "y_hard": np.ndarray,
        "c_easy": np.ndarray, "y_easy": np.ndarray,
        "n_hard": int, "n_easy": int
    }
    Raises: ValueError if n_hard < MIN_TIER_SIZE or n_easy < MIN_TIER_SIZE.
    """
    ...

def make_holdout_split(
    c_hard: np.ndarray, y_hard: np.ndarray,
    c_easy: np.ndarray, y_easy: np.ndarray,
    holdout_frac: float = 0.2,
    seed: int = 42,
) -> tuple[dict, dict]:
    """Stratified 80/20 split into eval set and T-fitting holdout.
    Returns: (eval_data, holdout_data) each with keys c_hard, y_hard, c_easy, y_easy
    """
    ...
```

---

### Evaluate (`src/evaluate.py`)

**Dependencies**: config, numpy

```python
def compute_ece(
    confidences: np.ndarray,
    labels: np.ndarray,
    M: int = 15,
) -> float:
    """Guo et al. 2017 ECE: sum_m (n_m/n)|acc_m - conf_m|.
    Skips empty bins. Returns NaN if all bins empty (warns caller).
    """
    ...

def compute_tier_ece(
    c_hard: np.ndarray, y_hard: np.ndarray,
    c_easy: np.ndarray, y_easy: np.ndarray,
    M: int = 15,
) -> dict[str, float]:
    """Compute ECE(hard), ECE(easy), DELTA_ECE for one model.
    Returns: {ece_hard, ece_easy, delta_ece}
    """
    ...

def compute_delta_ece_bootstrap(
    c_hard: np.ndarray, y_hard: np.ndarray,
    c_easy: np.ndarray, y_easy: np.ndarray,
    n_boot: int = 1000,
    M: int = 15,
    seed: int = 42,
) -> tuple[float, float, float, float]:
    """Bootstrap 95% CI for DELTA_ECE.
    Returns: (delta_ece_obs, ci_lower, ci_upper, p_value)
      p_value = fraction of boot samples <= 0
    """
    ...

def compute_null_baseline(
    c_hard: np.ndarray, y_hard: np.ndarray,
    c_easy: np.ndarray, y_easy: np.ndarray,
    M: int = 15,
) -> dict[str, float]:
    """Compute ECE for constant confidence = tier accuracy baseline.
    Returns: {null_conf_hard, null_conf_easy, ece_null_hard, ece_null_easy,
              excess_ece_hard, excess_ece_easy}
    """
    ...

def compute_m_sensitivity(
    c_hard: np.ndarray, y_hard: np.ndarray,
    c_easy: np.ndarray, y_easy: np.ndarray,
    m_values: list[int] = [10, 15, 20],
) -> dict[int, float]:
    """DELTA_ECE for each M in m_values.
    Returns: {M: delta_ece}
    """
    ...

def evaluate_gate(
    model_results: dict[str, dict],
    threshold: float = 0.03,
    min_passing: int = 2,
) -> tuple[bool, int]:
    """P1 gate: count models with delta_ece >= threshold AND ci_lower > 0.
    Returns: (gate_pass, n_passing)
    """
    ...

def verify_mechanism_activated(
    ece_hard: float, ece_easy: float, delta_ece: float,
    n_hard: int, n_easy: int,
    ci_lower: float, ci_upper: float,
) -> tuple[bool, dict[str, bool]]:
    """Check all mechanism activation indicators.
    Returns: (all_pass, {data_loaded, ece_computed, delta_nontrivial, ci_computed, effect_measured})
    """
    ...
```

---

### TemperatureScaling (`src/temperature_scaling.py`)

**Dependencies**: config, evaluate, numpy, scipy.optimize

```python
def fit_temperature(
    c_holdout: np.ndarray,
    y_holdout: np.ndarray,
    bounds: tuple[float, float] = (0.01, 10.0),
) -> float:
    """Fit T* on holdout by minimizing binary NLL.
    Uses scipy.optimize.minimize_scalar with method='bounded'.
    Returns: T* (optimal temperature)
    """
    ...

def apply_temperature(
    confidences: np.ndarray,
    T: float,
) -> np.ndarray:
    """Scale confidences by T: c_scaled = clip(c / T, 0, 1).
    Returns: scaled confidence array
    """
    ...

def compute_post_T_metrics(
    eval_data: dict,
    holdout_data: dict,
    M: int = 15,
    n_boot: int = 1000,
    seed: int = 42,
) -> dict[str, float]:
    """Fit T on holdout, apply to eval_data, recompute all ECE metrics.
    Returns: {T_star, post_T_ece_hard, post_T_ece_easy, post_T_delta_ece,
              post_T_ci_lower, post_T_ci_upper, post_T_p_value, gate_p3}
    """
    ...
```

---

### Visualize (`src/visualize.py`)

**Dependencies**: config, numpy, matplotlib, seaborn

```python
def plot_delta_ece_gate(
    model_results: dict[str, dict],
    output_path: Path,
    threshold: float = 0.03,
) -> None:
    """Fig 1: Bar chart DELTA_ECE with 95% CI error bars per model.
    Color: green = PASS, red = FAIL. Dashed lines at y=0 and y=0.03.
    """
    ...

def plot_reliability_diagrams(
    model_eval_data: dict[str, dict],
    model_results: dict[str, dict],
    output_path: Path,
    M: int = 15,
) -> None:
    """Fig 2: 3x2 grid reliability diagrams (model x tier).
    Diagonal = perfect calibration. ECE annotated per subplot.
    """
    ...

def plot_temperature_scaling_effect(
    model_results: dict[str, dict],
    output_path: Path,
) -> None:
    """Fig 3: Before/after T-scaling DELTA_ECE per model.
    T* values annotated on bars.
    """
    ...

def plot_null_baseline_comparison(
    model_results: dict[str, dict],
    output_path: Path,
) -> None:
    """Fig 4: ECE(tier) vs ECE(null_tier) grouped bar per model per tier."""
    ...

def plot_m_sensitivity(
    m_sensitivity_results: dict[str, dict[int, float]],
    output_path: Path,
) -> None:
    """Fig 5: DELTA_ECE vs M in {10,15,20} per model line plot."""
    ...

def plot_bootstrap_distributions(
    bootstrap_samples: dict[str, np.ndarray],
    model_results: dict[str, dict],
    output_path: Path,
) -> None:
    """Fig 6: Bootstrap DELTA_ECE histograms per model.
    95% CI shading; vertical lines at 0 and 0.03.
    """
    ...

def save_all_figures(
    model_eval_data: dict[str, dict],
    model_results: dict[str, dict],
    m_sensitivity_results: dict[str, dict[int, float]],
    bootstrap_samples: dict[str, np.ndarray],
    cfg: FigureConfig,
) -> None:
    """Orchestrate all 6 figure saves."""
    ...
```

---

### RunExperiment (`src/run_experiment.py`)

**Dependencies**: config, data_loader, evaluate, temperature_scaling, visualize, json, pathlib

```python
def save_results(results: dict, output_dir: Path) -> None:
    """Write delta_ece_results.json per FR-8.1 schema."""
    ...

def run_experiment(cfg: ExperimentConfig) -> dict:
    """Full experiment orchestration.
    Steps:
      1. Load confidence scores, tier assignments, correctness labels
      2. Per model: align data, make holdout split
      3. Compute ECE per tier, DELTA_ECE, bootstrap CI
      4. Compute null baseline and excess ECE
      5. Compute M-sensitivity
      6. Fit T*, compute post-T metrics
      7. Evaluate gates P1, P2, P3
      8. Log diagnostics per model
      9. Save results JSON
      10. Generate all 6 figures
    Returns: results dict (gate_overall, per-model metrics)
    """
    ...

def main() -> None:
    """CLI entry point with argparse for path overrides."""
    ...
```

---

## Data Flow

- `run_experiment.py` → `data_loader.py` → aligned `(c_hard, y_hard, c_easy, y_easy)` per model
- → `evaluate.py` → `(ece_hard, ece_easy, delta_ece, ci_lower, ci_upper, p_value, null_metrics, m_sensitivity)`
- → `temperature_scaling.py` → `(T_star, post_T_delta_ece, post_T_ci_lower, gate_p3)`
- → `visualize.py` → 6 figures saved to `figures/`
- → `run_experiment.py` → `results/delta_ece_results.json`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Directory structure, config.py, requirements, path conventions from h-m3 | 6 | 1+1+2+2 |
| A-2 | Data Loader | Load confidence JSON, tier CSV (wide format), correctness JSON; align arrays; holdout split | 11 | 3+3+3+2 |
| A-3 | ECE Core | compute_ece (Guo 2017), compute_tier_ece, compute_delta_ece_bootstrap (1000 samples) | 13 | 3+2+4+4 |
| A-4 | Null Baseline | Tier-null constant calibrator, excess ECE computation, P2 gate logic | 9 | 2+2+3+2 |
| A-5 | M-Sensitivity | compute_m_sensitivity for M in {10,15,20}, report stability | 7 | 2+2+2+1 |
| A-6 | Temperature Scaling | fit_temperature via NLL minimization, apply_temperature, compute_post_T_metrics | 12 | 3+2+4+3 |
| A-7 | Gate Evaluation | P1/P2/P3 gate logic, verify_mechanism_activated, diagnostic stdout logging | 9 | 2+2+3+2 |
| A-8 | Figures 1-3 | DELTA_ECE bar chart, reliability diagrams, temperature scaling effect | 12 | 3+2+4+3 |
| A-9 | Figures 4-6 | Null baseline comparison, M-sensitivity line plot, bootstrap distributions | 10 | 3+2+3+2 |
| A-10 | Results Persistence | FR-8.1 JSON schema, save_results, schema validation | 8 | 2+2+2+2 |
| A-11 | Orchestration | run_experiment main loop, argparse CLI, per-model error handling | 10 | 2+3+3+2 |
| A-12 | Tests | test_ece (unit), test_bootstrap (seed reproducibility), test_temperature, test_data_loader | 11 | 3+2+3+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-3, A-6, A-7, A-8, A-9, A-11, A-12], Low(4-8): [A-1, A-4, A-5, A-10]

---

## Implementation Notes

- All random operations use `np.random.default_rng(seed=42)` for reproducibility
- CodeLlama special case: n_easy=0 on HumanEval — use MBPP-only or combined; warn, do not fail
- ECE NaN (all empty bins): warn and mark model as degenerate, exclude from gate count
- Bootstrap collapse: warn if all 1000 samples identical; suggest alternate seed in warning
- T-fitting divergence: warn and mark P3 result as INCONCLUSIVE for that model
- No GPU — CPU-only; all imports from numpy/scipy/pandas/matplotlib/seaborn only
- Relative paths anchored at h-m4/ folder root matching h-m3 convention
