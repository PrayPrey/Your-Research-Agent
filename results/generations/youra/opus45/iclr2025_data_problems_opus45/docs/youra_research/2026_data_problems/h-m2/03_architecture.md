# Architecture: H-M2 Deep Network Metric Decoupling

**Date:** 2026-03-26
**Hypothesis:** H-M2 (MECHANISM, INCREMENTAL)
**Gate:** MUST_WORK
**Prerequisites:** H-M1 (VALIDATED), H-E1 (VALIDATED)

Applied: mechanism-verification-incremental (reuse base infrastructure, extend analysis layer)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-E1 and H-M1)
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/20260323_data_problems/h-e1/code/`, `docs/youra_research/20260323_data_problems/h-m1/code/`
**Findings**: H-E1 provides `attribution.py` (TRAK/TracIn/IF/FastIF with `AttributionMethod` ABC), `data.py`, `model.py`, `config.py` (dataclass `ExperimentConfig`). H-M1 provides `metrics_analysis.py` with `compute_rho_r_rho_m`, `build_metrics_dataframe`, R2 regression; `visualize.py` with `plot_gate_metric`; `config.py` with `HM1Config` dataclass. H-M2 reuses all of these directly and adds a thin deep-network wrapper around H-M1's analysis layer.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| AttributionMethod | `sys.path.insert(0, '../../h-e1/code'); from attribution import AttributionMethod, TRAKMethod, TracInMethod, IFMethod, FastIFMethod, BUDGET_MAP` | `h-e1/code/attribution.py` |
| ExperimentConfig | `from attribution import ...; from config import ExperimentConfig` (h-e1) | `h-e1/code/config.py` |
| build_model | `sys.path.insert(0, '../../h-e1/code'); from model import build_model` | `h-e1/code/model.py` |
| get_cifar10_loaders | `from data import get_cifar10_loaders, get_subset_indices` | `h-e1/code/data.py` |
| compute_rho_r_rho_m | `sys.path.insert(0, '../../h-m1/code'); from metrics_analysis import compute_rho_r_rho_m, build_metrics_dataframe, compute_single_error_axis_r2, compute_partial_correlation` | `h-m1/code/metrics_analysis.py` |
| plot_gate_metric | `from visualize import plot_gate_metric` (h-m1) | `h-m1/code/visualize.py` |
| HM1Config | `from config import HM1Config` (h-m1) | `h-m1/code/config.py` |

**Verified from**: `h-e1/code/` and `h-m1/code/` actual implementation.

---

## File Organization

```
h-m2/code/
  config.py           - HM2Config dataclass
  run_experiment.py   - Orchestrator (entry point)
  deep_analysis.py    - Deep network attribution + R2 analysis
  comparison.py       - Convex vs deep comparison logic
  visualize.py        - H-M2-specific figures (extends h-m1/visualize.py)
  results/
  figures/
```

---

## Module Definitions

### HM2Config (`config.py`)

**Dependencies**: standard library only

```python
@dataclass
class HM2Config:
    # Data (matching H-E1/H-M1 exactly)
    data_root: str = './data'
    train_subset_size: int = 5000
    test_subset_size: int = 100
    subset_seed: int = 42

    # External paths
    he1_code_path: str = '../../h-e1/code'
    hm1_code_path: str = '../../h-m1/code'
    he1_checkpoint: str = '../../h-e1/code/checkpoints/model_seed0_final.pt'
    loo_cache_path: str = '../../h-e1/code/results/loo_cache.npy'

    # Experiment
    methods: List[str] = field(default_factory=lambda: ['TRAK', 'TracIn', 'IF', 'FastIF'])
    compute_budgets: List[int] = field(default_factory=lambda: [10, 25, 50, 75, 100])
    seeds: List[int] = field(default_factory=lambda: [0, 1, 2])

    # Gate thresholds
    r2_threshold: float = 0.80       # Must be BELOW this
    partial_corr_threshold: float = 0.85  # Must be BELOW this

    # I/O
    results_dir: str = './results'
    figures_dir: str = './figures'


def get_config() -> HM2Config: ...
```

---

### DeepAttributionAnalysis (`deep_analysis.py`)

**Dependencies**: HM2Config, h-e1/attribution.py, h-e1/model.py, h-e1/data.py, h-m1/metrics_analysis.py

```python
def load_deep_model(cfg: HM2Config, device: str) -> nn.Module:
    """Load trained ResNet-18 from H-E1 checkpoint."""
    ...

def load_loo_cache(cfg: HM2Config) -> np.ndarray:
    """Load (5000, 100) LOO ground truth from H-E1 cache."""
    ...

def compute_deep_attribution_scores(
    cfg: HM2Config,
    model: nn.Module,
    train_loader: DataLoader,
    test_loader: DataLoader,
    device: str,
) -> Dict[str, Dict[int, List[np.ndarray]]]:
    """
    Run all methods x budgets x seeds using H-E1 AttributionMethod subclasses.
    Returns: {method: {budget: [scores_seed0, scores_seed1, scores_seed2]}}
    Each scores array: (5000, 100)
    """
    ...

def build_deep_metrics_df(
    method_scores: Dict[str, Dict[int, List[np.ndarray]]],
    loo_exact: np.ndarray,
) -> pd.DataFrame:
    """
    Delegate to h-m1 build_metrics_dataframe.
    Returns DataFrame[method, budget, seed, rho_r, rho_m, error_norm]
    """
    ...
```

---

### ComparisonAnalysis (`comparison.py`)

**Dependencies**: HM2Config, h-m1/metrics_analysis.py, pandas

```python
def compute_r2_deep(metrics_df: pd.DataFrame) -> Dict[str, float]:
    """
    Delegate to h-m1 compute_single_error_axis_r2.
    Returns: {'r2_rho_r': float, 'r2_rho_m': float, 'r2_avg': float}
    Gate: r2_rho_r < 0.80 OR r2_rho_m < 0.80
    """
    ...

def compute_partial_corr_deep(metrics_df: pd.DataFrame) -> Dict[int, float]:
    """
    Partial correlation corr(rho_r, rho_m | budget) per budget level.
    Delegates to h-m1 compute_partial_correlation.
    Returns: {budget: partial_corr}
    Gate: min value < 0.85
    """
    ...

def load_hm1_baseline() -> Dict[str, Any]:
    """
    Load H-M1 convex results CSV or use hardcoded validated values.
    Returns: {'r2_rho_r': float, 'r2_rho_m': float, 'partial_corr_by_budget': dict}
    """
    ...

def evaluate_gate(
    r2_deep: Dict[str, float],
    partial_corr_deep: Dict[int, float],
    cfg: HM2Config,
) -> Dict[str, Any]:
    """
    Check all gate conditions. Returns pass/fail dict with details.
    SC-2: r2 < 0.80, SC-3: corr < 0.85, SC-4: delta_r2 > 0.15
    """
    ...

def save_results(
    metrics_df: pd.DataFrame,
    r2_results: Dict[str, float],
    gate_results: Dict[str, Any],
    cfg: HM2Config,
) -> None:
    """Save metrics.csv, r2_analysis.csv, comparison.csv."""
    ...
```

---

### Visualize (`visualize.py`)

**Dependencies**: HM2Config, matplotlib, seaborn, pandas, h-m1/visualize.py

```python
def plot_gate_r2_comparison(
    r2_convex: Dict[str, float],
    r2_deep: Dict[str, float],
    cfg: HM2Config,
) -> None:
    """
    Bar chart: R2 convex (H-M1) vs R2 deep (H-M2) for rho_r and rho_m.
    Horizontal line at 0.80. Saves: figures/gate_r2_comparison.png
    """
    ...

def plot_scatter_metrics_vs_error(
    metrics_df: pd.DataFrame,
    cfg: HM2Config,
) -> None:
    """
    2-subplot scatter: rho_r vs error_norm and rho_m vs error_norm.
    Color by method, regression line overlaid.
    Saves: figures/scatter_metrics_vs_error.png
    """
    ...

def plot_correlation_heatmap(
    partial_corr_convex: Dict[int, float],
    partial_corr_deep: Dict[int, float],
    cfg: HM2Config,
) -> None:
    """
    Heatmap of corr(rho_r, rho_m) by budget. Side-by-side convex vs deep.
    Saves: figures/correlation_heatmap.png
    """
    ...

def plot_r2_by_method(
    metrics_df: pd.DataFrame,
    cfg: HM2Config,
) -> None:
    """
    Bar chart of R2 per method. Saves: figures/r2_by_method.png
    """
    ...

def plot_r2_vs_budget(
    r2_convex_by_budget: Dict[int, float],
    r2_deep_by_budget: Dict[int, float],
    cfg: HM2Config,
) -> None:
    """
    Line plot of R2 across budget levels, convex vs deep.
    Saves: figures/r2_vs_budget.png
    """
    ...
```

---

### RunExperiment (`run_experiment.py`)

**Dependencies**: all local modules, HM2Config

```python
def main() -> None:
    """
    Orchestrates full H-M2 pipeline:
    1. Load config, model, data, LOO cache
    2. Compute deep attribution scores (all methods x budgets x seeds)
    3. Build metrics DataFrame
    4. R2 regression analysis
    5. Partial correlation analysis
    6. Compare with H-M1 baseline
    7. Evaluate gate conditions
    8. Save results CSVs
    9. Generate all figures
    10. Print gate pass/fail summary
    """
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Create file structure, config.py, directory scaffolding, verify H-E1/H-M1 paths accessible | 6 | 1+1+2+2 |
| A-2 | Data & Model Loading | Implement load_deep_model (H-E1 checkpoint), load_loo_cache, get_cifar10_loaders wiring in HM2Config context | 8 | 2+2+2+2 |
| A-3 | Attribution Score Computation | Implement compute_deep_attribution_scores using H-E1 AttributionMethod subclasses for 4 methods x 5 budgets x 3 seeds | 14 | 3+3+4+4 |
| A-4 | Metrics DataFrame Builder | Implement build_deep_metrics_df delegating to h-m1 build_metrics_dataframe; validate rho_r, rho_m, error_norm columns | 9 | 2+3+2+2 |
| A-5 | R2 Regression Analysis | Implement compute_r2_deep delegating to h-m1 compute_single_error_axis_r2; verify gate condition (R2 < 0.80) | 10 | 2+3+3+2 |
| A-6 | Partial Correlation Analysis | Implement compute_partial_corr_deep per budget; verify gate (< 0.85) | 9 | 2+2+3+2 |
| A-7 | Baseline Comparison | Implement load_hm1_baseline, evaluate_gate with delta_R2 > 0.15 check | 9 | 2+2+3+2 |
| A-8 | Results Persistence | Implement save_results (metrics.csv, r2_analysis.csv, comparison.csv) | 6 | 1+2+1+2 |
| A-9 | Gate Visualizations | Implement plot_gate_r2_comparison (mandatory gate figure) | 8 | 2+2+2+2 |
| A-10 | Supplementary Visualizations | Implement scatter, heatmap, r2_by_method, r2_vs_budget figures | 10 | 2+2+3+3 |
| A-11 | Orchestrator | Implement run_experiment.py main() end-to-end, with gate summary print | 12 | 3+3+3+3 |
| A-12 | Integration & Validation | End-to-end smoke test, verify outputs match expected shapes, gate evaluation correctness | 13 | 3+3+3+4 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3], Medium(9-13): [A-4, A-5, A-6, A-7, A-10, A-11, A-12], Low(4-8): [A-1, A-2, A-8, A-9]

---

## Data Flow

- `HM2Config` -> `load_deep_model` -> `nn.Module`
- `HM2Config` -> `load_loo_cache` -> `loo_exact (5000, 100)`
- `HM2Config` -> `get_cifar10_loaders` (h-e1) -> `train_loader, test_loader`
- `nn.Module + loaders` -> `compute_deep_attribution_scores` -> `method_scores dict`
- `method_scores + loo_exact` -> `build_deep_metrics_df` -> `metrics_df`
- `metrics_df` -> `compute_r2_deep` -> `r2_results`
- `metrics_df` -> `compute_partial_corr_deep` -> `partial_corr_by_budget`
- `r2_results + partial_corr + hm1_baseline` -> `evaluate_gate` -> `gate_results`
- All results -> `save_results` + `visualize.*`
