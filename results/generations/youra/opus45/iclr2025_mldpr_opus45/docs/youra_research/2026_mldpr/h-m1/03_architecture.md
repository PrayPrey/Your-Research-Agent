# Architecture: h-m1 PELT Changepoint Detection

**Hypothesis:** PELT Changepoint Detection for HuggingFace Dataset Download Trajectories
**Type:** MECHANISM (PoC)
**Gate:** MUST_WORK (detection_rate > 0.50)

Applied: minimal-poc-pattern (EXISTENCE rules - 3-5 epics, flat file structure)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code (direct file reads; Serena MCP inactive for this project)
**Analyzed Path**: `docs/youra_research/20260325_mldpr/h-e1/code/`
**Findings**: h-e1 uses flat 5-file structure (config.py, data.py, model.py, evaluate.py, main.py) with local imports (`from config import ExperimentConfig`). Cache file is `hf_dataset_cache.json` co-located with code. Preprocessing returns tslearn 3D format [N, T, 1]; h-m1 needs 2D numpy [N, T] for ruptures.

---

## File Structure

- `h-m1/code/config.py` - experiment configuration
- `h-m1/code/data.py` - data loading (reuses h-e1 cache)
- `h-m1/code/model.py` - baseline + PELT changepoint detection
- `h-m1/code/evaluate.py` - metrics, gate check, figures, report
- `h-m1/code/main.py` - experiment runner

---

## Module Definitions

### ExperimentConfig (`h-m1/code/config.py`)

**Dependencies**: none

```python
@dataclass
class ExperimentConfig:
    # Data
    min_series_length: int = 12
    target_n_series: int = 500
    random_state: int = 42

    # PELT parameters
    pelt_model: str = "l2"
    pelt_min_size: int = 3
    pelt_jump: int = 1

    # Penalty selection
    penalty_range: tuple = (1.0, 100.0)
    n_penalties: int = 20

    # Gate threshold
    detection_rate_threshold: float = 0.50

    # Output
    figures_dir: str = "h-m1/figures"
    output_path: str = "h-m1/04_validation.md"
    cache_path: str = "../h-e1/code/hf_dataset_cache.json"
```

---

### DataLoader (`h-m1/code/data.py`)

**Dependencies**: ExperimentConfig, h-e1 cache

```python
def load_series(config: ExperimentConfig) -> List[Dict]:
    """Load time series from h-e1 cache or re-collect via HuggingFace.
    Returns list of {"id": str, "series": np.ndarray}."""
    ...

def preprocess_for_pelt(raw_series: List[np.ndarray]) -> List[np.ndarray]:
    """Log-transform + z-score per series. Returns list of 1D np.ndarray.
    Note: returns List[np.ndarray] (NOT tslearn 3D format)."""
    ...

def validate_series(datasets: List[Dict]) -> Tuple[bool, Dict]: ...
```

---

### Models (`h-m1/code/model.py`)

**Dependencies**: ExperimentConfig, ruptures

```python
class BaselineDetector:
    """Three null baselines: random, no-changepoint, fixed-interval."""

    def __init__(self, config: ExperimentConfig) -> None: ...

    def detect_random(self, series: np.ndarray) -> List[int]:
        """Randomly place 0-4 changepoints uniformly.""" ...

    def detect_none(self, series: np.ndarray) -> List[int]:
        """Return empty list (null model).""" ...

    def detect_fixed_interval(self, series: np.ndarray, interval: int = 6) -> List[int]:
        """Place changepoints at fixed intervals.""" ...

    def compute_detection_rate(
        self, all_series: List[np.ndarray], method: str = "random"
    ) -> float: ...


class PELTDetector:
    """PELT changepoint detection with BIC penalty."""

    def __init__(self, config: ExperimentConfig) -> None: ...

    def detect(self, series: np.ndarray) -> Tuple[List[int], float]:
        """Run PELT with BIC penalty. Returns (changepoints, optimal_penalty).""" ...

    def detect_all(
        self, all_series: List[np.ndarray]
    ) -> Tuple[List[List[int]], float]:
        """Apply PELT to all series. Returns (all_changepoints, detection_rate).""" ...

    def penalty_sensitivity(
        self, series: np.ndarray
    ) -> List[Tuple[float, int, List[int]]]:
        """CROPS-style grid search. Returns [(penalty, n_cps, changepoints)].""" ...
```

---

### Evaluator (`h-m1/code/evaluate.py`)

**Dependencies**: ExperimentConfig, numpy, matplotlib

```python
def compute_gate_metrics(
    all_changepoints: List[List[int]],
    config: ExperimentConfig,
) -> Dict: ...
    """Returns detection_rate, mean_cps, gate_pass."""

def generate_figures(
    all_series: List[np.ndarray],
    all_changepoints: List[List[int]],
    baseline_rates: Dict[str, float],
    pelt_rate: float,
    config: ExperimentConfig,
) -> List[str]:
    """Generate and save all figures to figures_dir. Returns list of paths.""" ...

def write_validation_report(results: Dict, config: ExperimentConfig) -> str:
    """Write 04_validation.md. Returns 'PASS' or 'FAIL'.""" ...
```

---

### Main Runner (`h-m1/code/main.py`)

**Dependencies**: all modules

```python
def run_experiment(config: ExperimentConfig) -> Dict: ...

if __name__ == "__main__":
    config = ExperimentConfig(
        figures_dir="<abs_path>/h-m1/figures",
        output_path="<abs_path>/h-m1/04_validation.md",
        cache_path="<abs_path>/h-e1/code/hf_dataset_cache.json",
    )
    results = run_experiment(config)
    sys.exit(0 if results["gate_pass"] else 1)
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| Cache file | `../h-e1/code/hf_dataset_cache.json` | `h-e1/code/hf_dataset_cache.json` |
| Preprocessing logic | copied/adapted in h-m1/code/data.py | `h-e1/code/data.py` (collect_datasets, preprocess) |

**Verified from**: `docs/youra_research/20260325_mldpr/h-e1/code/` (actual implementation)

**Key difference from h-e1**: h-e1 `preprocess()` returns tslearn `[N, T, 1]` 3D format. h-m1 needs flat `List[np.ndarray]` for ruptures. Preprocessing must be reimplemented in h-m1/code/data.py.

**Cache path**: h-e1 stores cache at `hf_dataset_cache.json` co-located with code files. h-m1 should reference this as fallback before re-collecting.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Config | Project structure, config.py, requirements | 5 | 1+1+1+2 |
| A-2 | Data Loading | load_series() with h-e1 cache reuse, preprocess_for_pelt() | 9 | 2+3+2+2 |
| A-3 | Baseline Models | BaselineDetector (random, none, fixed-interval) | 7 | 2+2+2+1 |
| A-4 | PELT Detector | PELTDetector with BIC penalty + CROPS grid search | 12 | 3+3+4+2 |
| A-5 | Evaluation & Figures | Gate metrics, 4 figures, validation report | 10 | 2+2+3+3 |
| A-6 | Integration & Run | main.py, end-to-end test, gate check | 8 | 2+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-4, A-5], Low(4-8): [A-1, A-3, A-6]
