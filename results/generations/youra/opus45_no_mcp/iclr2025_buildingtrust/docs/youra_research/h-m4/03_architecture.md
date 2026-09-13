# Architecture: H-M4 Hedging-Confidence Correlation Analysis

**Type:** MECHANISM (statistical analysis, no training)
**Applied:** statistical_analysis_pattern

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-M3)
**Status:** Patterns found from base code — reused directly (H-M4 mirrors H-M3's structure)
**Analyzed Path:** `h-m3/code/`
**Findings:** H-M3 uses flat-file modules (`config.py`, `data_loader.py`, analysis module, `gate_metrics.py`, `visualization.py`, `run_experiment.py`) with a dataclass `Config` that auto-creates `output_dir`/`figures_dir`. H-M2 cache format is a **flat JSON list** of dicts (verified via `data_loader.validate_cache_format`), NOT `{'outputs': [...]}` as the PRD pseudo-code assumed — H-M4 loader must handle the flat-list format and tolerant field names (`hedging_count`/`num_hedging_markers`, `confidence`/`confidence_score`).

---

## Module Structure

### H_M4_Config (`config.py`)

**Dependencies**: none

```python
@dataclass
class H_M4_Config:
    hypothesis_id: str = "H-M4"
    hypothesis_type: str = "MECHANISM"
    h_m2_cache_path: Path  # ../h-m2/code/results/h-m2_results.json
    output_dir: Path       # ./results
    figures_dir: Path      # ../figures
    gate_r_threshold: float = -0.2
    gate_p_threshold: float = 0.05
    min_samples: int = 500
    hedging_buckets: List[tuple] = [(0,0), (1,2), (3,5), (6,999)]
    figure_dpi: int = 150
    def __post_init__(self): ...  # mkdir output_dir, figures_dir
```

### data_loader (`data_loader.py`)

**Dependencies**: config

```python
def load_h_m2_cache(cache_path: Path) -> List[Dict[str, Any]]: ...
def validate_cache_format(data: Any) -> bool: ...
def extract_pairs(data: List[Dict]) -> Tuple[List[int], List[float]]:
    """Returns (hedging_counts, confidence_scores), skipping items with missing fields."""
```

### correlation_analyzer (`correlation_analyzer.py`)

**Dependencies**: numpy, scipy.stats

```python
def compute_spearman(hedging_counts: List[int], confidence_scores: List[float]) -> Dict[str, float]:
    """Returns {'spearman_r', 'p_value', 'n_samples'}."""

def compute_confidence_interval(r: float, n: int, alpha: float = 0.05) -> Tuple[float, float]:
    """Fisher z-transform 95% CI for Spearman r."""

def detect_outliers(hedging_counts: List[int], confidence_scores: List[float]) -> Dict[str, Any]:
    """IQR-based outlier flags on confidence_scores; returns counts + indices."""

def compute_gate_metrics(stats: Dict, ci: Tuple[float,float], n: int, config: H_M4_Config) -> Dict[str, Any]:
    """Combines r, p, n, ci into gate_1_pass/gate_2_pass/gate_3_pass/all_gates_pass."""
```

### visualization (`visualization.py`)

**Dependencies**: matplotlib, seaborn, correlation_analyzer output

```python
def plot_scatter_regression(hedging_counts, confidence_scores, r, p, output_path: Path, dpi=150) -> None: ...
def plot_box_by_bucket(hedging_counts, confidence_scores, buckets, output_path: Path, dpi=150) -> None: ...
def plot_gate_comparison(gate_metrics: Dict, output_path: Path, dpi=150) -> None:
    """Bar chart: threshold r (-0.2) vs actual r."""
def plot_hedging_histogram(hedging_counts, output_path: Path, dpi=150) -> None: ...
```

### run_experiment (`run_experiment.py`)

**Dependencies**: config, data_loader, correlation_analyzer, visualization

```python
def run_h_m4_experiment(config: H_M4_Config = None) -> dict:
    """
    1. load_h_m2_cache -> extract_pairs
    2. compute_spearman, compute_confidence_interval, detect_outliers
    3. compute_gate_metrics
    4. plot_scatter_regression, plot_box_by_bucket, plot_gate_comparison, plot_hedging_histogram
    5. Save results/h-m4_results.json, results/gate_metrics.yaml
    """
if __name__ == '__main__': ...  # sys.exit(0 if all_gates_pass else 1)
```

---

## File Organization

```
h-m4/code/
  config.py
  data_loader.py
  correlation_analyzer.py
  visualization.py
  run_experiment.py
  results/
    h-m4_results.json
    gate_metrics.yaml
h-m4/figures/
  scatter_regression.png
  box_by_bucket.png
  gate_comparison.png
  hedging_histogram.png
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| H-M2 cache (data only, not code) | `Path("../h-m2/code/results/h-m2_results.json")` | `h-m2/code/results/h-m2_results.json` |

**Verified from**: `h-m3/code/config.py` (`h_m2_cache_path` default) and `h-m3/code/data_loader.py` (flat-list format, tolerant field validation) — no H-M3 Python modules are imported directly; only the config/loader *pattern* is reused since H-M4's data schema (hedging_count, confidence) differs from H-M3's (positional markers).

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config setup | H_M4_Config dataclass, paths, thresholds | 5 | 2+1+1+1 |
| A-2 | Data loader | Load H-M2 cache, validate, extract pairs | 7 | 2+2+2+1 |
| A-3 | Correlation core | spearmanr, CI (Fisher z), outlier detection | 9 | 3+2+3+1 |
| A-4 | Gate metrics | Combine stats into gate pass/fail dict | 5 | 2+2+1+2 |
| A-5 | Visualization suite | 4 figures (scatter, box, gate bar, histogram) | 9 | 3+2+2+2 |
| A-6 | Experiment runner + export | Orchestrate pipeline, JSON/YAML export, CLI exit code | 7 | 2+3+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3, A-5], Low(4-8): [A-1, A-2, A-4, A-6]
