# System Architecture: h-e2

**Date:** 2026-08-28
**Hypothesis:** Velocity Decay Detection via Linear Regression
**Type:** EXISTENCE (Proof-of-Concept)
**Specification Level:** 1.5 (Concrete + Pseudo-code)

---

## Knowledge Base Patterns

Applied: Statistical analysis pipeline pattern (scipy/pandas time series)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** New implementation from scratch
**Analyzed Path:** N/A
**Findings:** No existing h-e2 code. Referenced h-e1 pattern (PWC API → validation → report).

---

## Module Structure

### VelocityDecayDetector (`src/detector.py`)

**Dependencies:** scipy.stats, pandas, numpy

```python
class VelocityDecayDetector:
    def __init__(self, window_days: int = 180, threshold: float = 0.1): ...
    def detect(self, df: pd.DataFrame) -> Tuple[Optional[pd.Timestamp], List]: ...
    def _compute_velocity(self, window: pd.DataFrame) -> Tuple[float, float]: ...
```

### DataLoader (`src/data_loader.py`)

**Dependencies:** pandas, paperswithcode (optional)

```python
def load_pwc_benchmark(benchmark_id: str) -> pd.DataFrame: ...
def preprocess_leaderboard(df: pd.DataFrame) -> pd.DataFrame: ...
```

### Baseline (`src/baseline.py`)

**Dependencies:** pandas

```python
def manual_inspection_baseline(df: pd.DataFrame) -> Optional[pd.Timestamp]: ...
```

### Metrics (`src/metrics.py`)

**Dependencies:** numpy

```python
def compute_detection_success(first_decay_date: Optional[pd.Timestamp]) -> bool: ...
def compute_stability_cv(velocities: List[float]) -> float: ...
def compute_significance_ratio(p_values: List[float], threshold: float = 0.05) -> float: ...
```

### Visualizer (`src/visualizer.py`)

**Dependencies:** matplotlib, pandas

```python
def plot_score_timeline(df: pd.DataFrame, decay_date: Optional[pd.Timestamp], output_path: Path): ...
def plot_velocity_timeline(velocities: List, threshold: float, output_path: Path): ...
def plot_pvalue_distribution(p_values: List, output_path: Path): ...
def plot_gate_metrics(metrics: dict, output_path: Path): ...
```

### Main Pipeline (`src/main.py`)

**Dependencies:** All above modules

```python
def run_experiment(benchmark_id: str, output_dir: Path) -> dict: ...
def main(): ...
```

---

## File Organization

```
docs/youra_research/h-e2/
├── src/
│   ├── detector.py          # VelocityDecayDetector
│   ├── data_loader.py       # PWC API + preprocessing
│   ├── baseline.py          # Manual inspection
│   ├── metrics.py           # Detection success, CV, significance
│   ├── visualizer.py        # 4 required plots
│   └── main.py              # Pipeline orchestration
├── data/                    # Leaderboard snapshots (runtime)
├── figures/                 # Output plots (runtime)
└── 04_validation.md         # Results report (runtime)
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Loading | Fetch PWC benchmarks, preprocess timestamps/scores | 8 | Module(2) + Deps(2) + Algo(2) + Integration(2) |
| A-2 | Core Detector | VelocityDecayDetector with rolling windows + linregress | 12 | Module(3) + Deps(2) + Algo(4) + Integration(3) |
| A-3 | Baseline | Manual inspection heuristic (6mo <1% improvement) | 5 | Module(1) + Deps(1) + Algo(2) + Integration(1) |
| A-4 | Metrics | Compute detection success, CV, significance ratio | 6 | Module(2) + Deps(1) + Algo(2) + Integration(1) |
| A-5 | Visualization | 4 plots (score timeline, velocity, p-value, gate metrics) | 9 | Module(2) + Deps(2) + Algo(2) + Integration(3) |
| A-6 | Pipeline | Orchestrate experiment, generate validation report | 7 | Module(2) + Deps(1) + Algo(1) + Integration(3) |

**Distribution:** High(12): [A-2], Medium(9-11): [A-5], Low(5-8): [A-1, A-3, A-4, A-6]

**Total Complexity:** 47

---

## Interface Contracts

### Detector → Metrics
```python
first_decay_date, velocities = detector.detect(df)
# velocities format: List[(pd.Timestamp, float, float)]  # (date, velocity, p_value)
```

### Data Loader → Detector
```python
df = load_pwc_benchmark("imagenet")
df = preprocess_leaderboard(df)
# df schema: ['date': datetime, 'score': float]
```

### All Modules → Main
```python
results = {
    'detection_success': bool,
    'first_decay_date': Optional[pd.Timestamp],
    'stability_cv': float,
    'significance_ratio': float,
    'baseline_date': Optional[pd.Timestamp]
}
```

---

## Dependencies

**External Libraries:**
- scipy (linregress)
- numpy (statistics)
- pandas (data manipulation)
- matplotlib (plotting)
- paperswithcode (optional, API client)

**Installation:**
```bash
pip install scipy numpy pandas matplotlib paperswithcode
```

---

## Self-Validation

- [x] No ASCII diagrams
- [x] KB pattern noted (1 line)
- [x] Codebase Analysis section included
- [x] Module sections = interface signatures only
- [x] 6 Epic tasks with complexity (EXISTENCE: relaxed to 6)
- [x] Total length < 500 lines
- [x] Serena validation: green-field project confirmed
- [x] Import paths verified (new codebase, no external deps)
