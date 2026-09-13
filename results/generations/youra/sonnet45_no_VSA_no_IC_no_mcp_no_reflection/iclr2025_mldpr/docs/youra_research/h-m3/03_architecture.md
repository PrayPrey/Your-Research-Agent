# Architecture Document: h-m3 Citation Velocity Correlation Detector

**Hypothesis ID:** h-m3
**Type:** MECHANISM
**Date:** 2026-08-28
**Infrastructure Tier:** LIGHT

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Extends h-m1 (saturation) + h-m2 (citations) with velocity correlation
**Analyzed Path:** docs/youra_research/h-m1/code/, docs/youra_research/h-m2/code/
**Findings:** Reuses h-m1 ConvergenceDetector, h-m2 CitationFetcher/LeadTimeAnalyzer. Adds velocity spike detection layer.

---

## Applied Patterns

Applied: **Time Series Velocity Analysis** (rolling differentiation + anomaly detection)
Applied: **Binary Classification Validation** (precision/recall with sklearn.metrics)

---

## System Architecture

### Module Structure

```
h-m3/
├── code/
│   ├── config.py                      # Constants (thresholds, window sizes)
│   ├── velocity_detector.py           # Citation velocity spike detection
│   ├── correlation_detector.py        # Combined saturation + velocity
│   ├── ground_truth_loader.py         # Paradigm shift labels
│   ├── precision_recall_evaluator.py  # sklearn metrics wrapper
│   ├── visualizer.py                  # Gate metrics + timeline plots
│   └── main_experiment.py             # Pipeline orchestration
├── data/
│   ├── citations/                     # Symlink to h-m2/data/citations/
│   └── paradigm_shifts.json           # Manual ground truth labels
├── figures/                           # Generated plots
└── results/
    ├── predictions.csv                # Per-benchmark predictions
    └── metrics.json                   # Precision/recall/F1
```

---

## Module Definitions

### VelocityDetector (`code/velocity_detector.py`)

**Dependencies:** pandas, numpy

```python
class VelocityDetector:
    def __init__(self, velocity_window: int = 3, spike_threshold: float = 2.0): ...
    def compute_velocity(self, citation_df: pd.DataFrame) -> pd.Series: ...
    def detect_spike(self, velocity_series: pd.Series, window_start: str, window_end: str) -> bool: ...
```

### CorrelationDetector (`code/correlation_detector.py`)

**Dependencies:** VelocityDetector, h-m1.ConvergenceDetector, h-m2.CitationFetcher

```python
class CorrelationDetector:
    def __init__(self, saturation_dates: dict, velocity_detector: VelocityDetector): ...
    def detect_shift(self, benchmark: str, citation_df: pd.DataFrame) -> int: ...
    def detect_all(self, benchmarks: list, citation_data: dict) -> dict: ...
```

### GroundTruthLoader (`code/ground_truth_loader.py`)

**Dependencies:** json, pandas

```python
class GroundTruthLoader:
    def load_paradigm_shifts(self, path: Path) -> dict: ...
    def create_labels(self, saturation_dates: dict, shift_dates: dict, threshold_months: int = 6) -> dict: ...
```

### PrecisionRecallEvaluator (`code/precision_recall_evaluator.py`)

**Dependencies:** sklearn.metrics

```python
class PrecisionRecallEvaluator:
    def compute_metrics(self, y_true: list, y_pred: list) -> dict: ...
    def generate_classification_report(self, y_true: list, y_pred: list) -> str: ...
```

### Visualizer (`code/visualizer.py`)

**Dependencies:** matplotlib, seaborn

```python
class MetricsVisualizer:
    def __init__(self, output_dir: Path): ...
    def plot_gate_metrics(self, precision: float, recall: float, target_precision: float = 0.8, target_recall: float = 0.7) -> None: ...
    def plot_citation_velocity_timeline(self, benchmark: str, citations_df: pd.DataFrame, saturation_date: str, shift_date: str) -> None: ...
    def plot_confusion_matrix(self, y_true: list, y_pred: list) -> None: ...
```

### MainExperiment (`code/main_experiment.py`)

**Dependencies:** All above modules

```python
def run_correlation_experiment(
    h1_results_path: Path,
    h2_citation_cache: Path,
    ground_truth_path: Path,
    output_dir: Path
) -> dict: ...
```

---

## External Dependencies (Base Hypotheses)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| ConvergenceDetector | `from h_m1.code.convergence_detector import ConvergenceDetector` | `h-m1/code/convergence_detector.py` |
| CitationFetcher | `from h_m2.code.citation_fetcher import CitationFetcher` | `h-m2/code/citation_fetcher.py` |
| LeadTimeAnalyzer | `from h_m2.code.lead_time_analyzer import LeadTimeAnalyzer` | `h-m2/code/lead_time_analyzer.py` |
| h-m1 Results | Direct JSON read | `h-m1/results/convergence_results.json` |
| h-m2 Citations | Direct JSON read | `h-m2/data/citations/*.json` |

**Verified from:** docs/youra_research/h-m1/code/, docs/youra_research/h-m2/code/ (actual implementations)

**h-m1 Convergence Results Schema:**
```json
{
  "results": {
    "imagenet": {"convergence_date": "2015-08", "final_std": 0.00341}
  }
}
```

**h-m2 Citation Cache Schema:**
```json
[
  {"date": "2020-01", "citations": 15},
  {"date": "2020-02", "citations": 23}
]
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M3-1 | Data Integration | Load h-m1 saturation dates, h-m2 citation cache, ground truth labels | 5 | 1+2+1+1 (h-m1 JSON + h-m2 cache read + ground truth JSON + validation) |
| M3-2 | Velocity Computation | Monthly citation velocity with 3-month rolling window | 7 | 2+2+2+1 (pandas rolling + differentiation + smoothing + edge cases) |
| M3-3 | Spike Detection | 2σ threshold anomaly detection in saturation window | 6 | 2+2+1+1 (window extraction + z-score threshold + binary flag + storage) |
| M3-4 | Baseline Model | Saturation-only detector (reuse h-m1) | 4 | 1+1+1+1 (import h-m1 + binary prediction + loop + results) |
| M3-5 | Proposed Model | Combined saturation + velocity correlation | 8 | 2+2+2+2 (saturation call + velocity call + temporal alignment + AND logic) |
| M3-6 | Ground Truth Labels | Binary labels (shift within 6mo of saturation) | 5 | 2+1+1+1 (date parsing + temporal offset + label logic + dict storage) |
| M3-7 | Metrics Computation | Precision/recall/F1 with sklearn | 6 | 2+2+1+1 (sklearn import + metrics call + confusion matrix + JSON save) |
| M3-8 | Gate Metrics Plot | Bar chart (target vs baseline vs proposed) | 6 | 2+2+1+1 (data prep + bar chart + threshold lines + save) |
| M3-9 | Velocity Timeline Plot | Citation velocity over time with event markers | 7 | 2+2+2+1 (velocity plot + saturation marker + shift marker + save) |
| M3-10 | Confusion Matrix Heatmap | 2×2 heatmap with percentages | 5 | 2+1+1+1 (seaborn heatmap + annotations + color scale + save) |
| M3-11 | Pipeline Orchestration | Main loop, gate evaluation, results serialization | 9 | 2+2+3+2 (benchmark loop + detector calls + gate logic + error handling) |

**Total Epic Tasks:** 11
**Complexity Distribution:** 
- Low (4-8): M3-1, M3-2, M3-3, M3-4, M3-5, M3-6, M3-7, M3-8, M3-9, M3-10
- Medium (9-13): M3-11
- High (14-17): None
- VeryHigh (18-20): None

**Avg Complexity:** 6.2

---

## Integration Points

### Data Flow
```
h-m1/results/convergence_results.json → saturation_dates
h-m2/data/citations/*.json → citation_timeseries
data/paradigm_shifts.json → ground_truth_labels
    ↓
velocity_detector.py → velocity_series + spike detection
    ↓
correlation_detector.py → combined predictions (saturation AND velocity)
    ↓
precision_recall_evaluator.py → metrics.json
    ↓
visualizer.py → figures/ (gate_metrics.png, timeline.png, confusion.png)
    ↓
main_experiment.py → gate evaluation (PASS if precision>0.8 AND recall>0.7)
```

### Success Criteria Flow
```
predictions.csv (per-benchmark)
    ↓
metrics.json
    ↓
Criteria: Precision >80%
Criteria: Recall >70%
Criteria: Sample size 15-20
    ↓
Gate Metrics → PASS/FAIL
```

---

## Configuration

**Hardcoded Constants (LIGHT tier):**
```python
# config.py
BENCHMARKS = [
    "imagenet", "glue", "squad", "coco", "wmt14", "librispeech",
    "superglue", "mnli", "hellaswag", "boolq", "arc", "winogrande",
    "mmlu", "truthfulqa", "gsm8k"
]  # 15 benchmarks minimum

H1_RESULTS_PATH = Path("../h-m1/results/convergence_results.json")
H2_CITATION_CACHE = Path("../h-m2/data/citations/")
GROUND_TRUTH_PATH = Path("data/paradigm_shifts.json")

VELOCITY_WINDOW = 3  # months
SPIKE_THRESHOLD = 2.0  # σ above mean
CORRELATION_LEAD_TIME = 6  # months (saturation to shift)
SEARCH_WINDOW_PRE = 3  # months before saturation
SEARCH_WINDOW_POST = 6  # months after saturation

TARGET_PRECISION = 0.8
TARGET_RECALL = 0.7
MIN_SAMPLE_SIZE = 15
```

**Ground Truth File Format (data/paradigm_shifts.json):**
```json
{
  "imagenet": "2015-12",
  "glue": "2018-10",
  "squad": "2019-02",
  "coco": "2021-05",
  "wmt14": "2020-06"
}
```

---

## Environment

**Python Packages:**
```
pandas>=1.3.0
numpy>=1.21.0
scikit-learn>=0.24.0
matplotlib>=3.4.0
seaborn>=0.11.0
```

**Python Version:** 3.8+

**Data Dependencies:**
- h-m1 convergence results (validated)
- h-m2 citation cache (validated)
- Manual paradigm shift annotation (provided)

---

## Next Steps

**Phase 4 Implementation Order:**
1. M3-1: Data integration (prerequisite for all)
2. M3-2: Velocity computation (core mechanism)
3. M3-3: Spike detection (velocity feature)
4. M3-6: Ground truth labels (evaluation prerequisite)
5. M3-4: Baseline model (comparison baseline)
6. M3-5: Proposed model (hypothesis test)
7. M3-7: Metrics computation (gate evaluation)
8. M3-8, M3-9, M3-10: Visualizations (validation plots)
9. M3-11: Pipeline orchestration (full experiment)

**Document Status:** READY FOR PHASE 4
