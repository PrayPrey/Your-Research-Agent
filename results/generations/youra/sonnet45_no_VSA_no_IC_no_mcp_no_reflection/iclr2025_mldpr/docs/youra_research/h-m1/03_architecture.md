# Architecture Document: h-m1 Score Convergence Detection

**Hypothesis ID:** h-m1
**Type:** MECHANISM
**Date:** 2026-08-28
**Infrastructure Tier:** LIGHT

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Extends h-e1 data infrastructure
**Analyzed Path:** docs/youra_research/h-e1/src/
**Findings:** Reuses validated PWC data loading pattern, adds statistical analysis layer

---

## Applied Patterns

Applied: **Statistical Analysis Pipeline** (rolling window time-series detection)
Applied: **Data Reuse Pattern** (h-e1 validated JSONL data)

---

## System Architecture

### Module Structure

```
h-m1/
├── code/
│   ├── data_loader.py          # Reuses h-e1 JSONL schema
│   ├── convergence_detector.py # Rolling window statistics
│   ├── statistical_validator.py # Levene's test
│   ├── visualizer.py           # Timeline plots
│   └── main_experiment.py      # Pipeline orchestration
├── data/                       # Symlink to h-e1/data
├── figures/                    # Generated plots
└── results/
    └── convergence_results.json
```

---

## Module Definitions

### DataLoader (`code/data_loader.py`)

**Dependencies:** pandas, pathlib

```python
class PWCDataLoader:
    def __init__(self, data_dir: Path): ...
    def load_benchmark(self, benchmark: str) -> pd.DataFrame: ...
    def prepare_monthly_aggregation(self, df: pd.DataFrame) -> pd.DataFrame: ...
```

### ConvergenceDetector (`code/convergence_detector.py`)

**Dependencies:** pandas, numpy

```python
class ConvergenceDetector:
    def __init__(self, window_months: int = 6, threshold: float = 0.005, top_k: int = 5): ...
    def compute_rolling_std(self, df: pd.DataFrame) -> pd.Series: ...
    def detect_first_convergence(self, rolling_std: pd.Series) -> tuple[str, float]: ...
```

### StatisticalValidator (`code/statistical_validator.py`)

**Dependencies:** scipy.stats

```python
class StatisticalValidator:
    def levene_test(self, pre_scores: pd.Series, post_scores: pd.Series) -> dict: ...
    def validate_convergence(self, df: pd.DataFrame, convergence_date: str) -> dict: ...
```

### Visualizer (`code/visualizer.py`)

**Dependencies:** matplotlib

```python
class ConvergenceVisualizer:
    def __init__(self, output_dir: Path): ...
    def plot_timeline(self, benchmark: str, dates: pd.Series, std_values: pd.Series, threshold: float) -> None: ...
    def plot_gate_metrics(self, target_benchmarks: int, actual_benchmarks: int) -> None: ...
```

### MainExperiment (`code/main_experiment.py`)

**Dependencies:** All above modules

```python
def run_convergence_experiment(data_dir: Path, output_dir: Path) -> dict: ...
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| DataValidator | `from h_e1.src.data_validator import DataValidator` | `h-e1/src/data_validator.py` |
| PWC Data Schema | Direct JSONL read | `h-e1/data/pwc_leaderboards/*.jsonl` |

**Verified from:** docs/youra_research/h-e1/src/ (actual implementation)

**Data Schema (h-e1 JSONL format):**
```json
{"submission_date": "2020-01-15", "score": 78.3, "benchmark": "imagenet", "model_name": "ResNet-152"}
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M1-1 | Data Loading | Load h-e1 JSONL, monthly aggregation | 4 | 1+1+1+1 (file I/O + parsing + groupby + validation) |
| M1-2 | Rolling Window Statistics | Top-5 extraction, 6-month rolling std | 9 | 2+2+3+2 (groupby + nlargest + rolling + edge cases) |
| M1-3 | Convergence Detection | First convergence date per benchmark | 6 | 2+1+2+1 (mask logic + first index + storage + error handling) |
| M1-4 | Statistical Validation | Levene's test pre/post convergence | 7 | 2+2+2+1 (pre/post split + scipy call + p-value interpretation + reporting) |
| M1-5 | Timeline Visualization | Rolling std plots with threshold line | 8 | 2+2+2+2 (matplotlib setup + 3 benchmarks + threshold shading + save) |
| M1-6 | Gate Metrics Comparison | Target vs actual bar chart | 5 | 2+1+1+1 (data prep + bar chart + labels + save) |
| M1-7 | Pipeline Orchestration | Main experiment loop, results JSON | 7 | 2+1+2+2 (loop logic + error handling + JSON serialization + console output) |

**Total Epic Tasks:** 7
**Complexity Distribution:** 
- Low (4-8): M1-1, M1-3, M1-6
- Medium (9-13): M1-2
- High (14-17): None
- VeryHigh (18-20): None

**Avg Complexity:** 6.6

---

## Integration Points

### Data Flow
```
h-e1/data/pwc_leaderboards/*.jsonl
    ↓
data_loader.py → monthly aggregation
    ↓
convergence_detector.py → rolling std + detection
    ↓
statistical_validator.py → Levene's test
    ↓
visualizer.py → figures/
    ↓
main_experiment.py → results/convergence_results.json
```

### Success Criteria Flow
```
convergence_results.json
    ↓
Criteria: ≥2/3 benchmarks converged
    ↓
Criteria: p<0.05 for all detected
    ↓
Gate Metrics → PASS/FAIL
```

---

## Configuration

**Hardcoded Constants (LIGHT tier):**
```python
# config.py
BENCHMARKS = ["imagenet", "glue", "squad"]
WINDOW_MONTHS = 6
TOP_K = 5
CONVERGENCE_THRESHOLD = 0.005  # 0.5%
SIGNIFICANCE_LEVEL = 0.05
MIN_PERIODS = 3
```

---

## Environment

**Python Packages:**
```
pandas>=1.3.0
numpy>=1.21.0
scipy>=1.7.0
matplotlib>=3.4.0
```

**Python Version:** 3.8+

---

## Next Steps

**Phase 4 Implementation Order:**
1. M1-1: Data loading (prerequisite for all)
2. M1-2: Rolling window statistics (core mechanism)
3. M1-3: Convergence detection
4. M1-4: Statistical validation
5. M1-5, M1-6: Visualizations
6. M1-7: Pipeline orchestration

**Document Status:** READY FOR PHASE 4
