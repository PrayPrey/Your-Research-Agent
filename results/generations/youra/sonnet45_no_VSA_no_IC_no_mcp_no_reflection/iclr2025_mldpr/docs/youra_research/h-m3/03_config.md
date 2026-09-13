# Configuration Design Document: h-m3 Citation Velocity Correlation Detector

**Hypothesis ID:** h-m3
**Type:** MECHANISM
**Date:** 2026-08-28
**Subtask Budget:** 0 tasks (LIGHT tier)
**Infrastructure Tier:** LIGHT (hardcoded config)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Extends h-m1 (saturation) + h-m2 (citations) with velocity correlation
**Config Files Found:** h-m2/code/config.py (hardcoded constants)
**Pattern Used:** Hardcoded dict (LIGHT tier standard)

---

## Applied Patterns

Applied: **Hardcoded Config Pattern** (LIGHT tier uses constants)

---

## Configuration Schema

### config.py (Hardcoded Constants)

```python
"""
Configuration for h-m3 citation velocity correlation detection.
LIGHT tier: Hardcoded constants for velocity spike analysis.
"""
from pathlib import Path

# Data Sources
BASE_DIR = Path(__file__).parent.parent
H1_RESULTS_PATH = BASE_DIR.parent / "h-m1" / "results" / "convergence_results.json"
H2_CITATION_CACHE = BASE_DIR.parent / "h-m2" / "data" / "citations"
GROUND_TRUTH_PATH = BASE_DIR / "data" / "paradigm_shifts.json"

# Output Directories
OUTPUT_DIR = BASE_DIR / "results"
FIGURES_DIR = BASE_DIR / "figures"
DATA_DIR = BASE_DIR / "data"

# Benchmarks (15 minimum for sample size)
BENCHMARKS = [
    "imagenet", "glue", "squad", "coco", "wmt14", "librispeech",
    "superglue", "mnli", "hellaswag", "boolq", "arc", "winogrande",
    "mmlu", "truthfulqa", "gsm8k"
]

# Velocity Detection Parameters
VELOCITY_WINDOW = 3  # months (rolling window for velocity computation)
SPIKE_THRESHOLD = 2.0  # σ above mean (2σ = 95% confidence)

# Correlation Parameters
CORRELATION_LEAD_TIME = 6  # months (saturation to paradigm shift)
SEARCH_WINDOW_PRE = 3  # months before saturation
SEARCH_WINDOW_POST = 6  # months after saturation

# Gate Success Criteria
TARGET_PRECISION = 0.8
TARGET_RECALL = 0.7
MIN_SAMPLE_SIZE = 15

# Visualization
DPI = 300
FIGSIZE = (10, 6)
```

---

## Inherited Configuration (Base Hypothesis)

### h-m1 Convergence Detection (Verified from Actual Code)

```python
# From: docs/youra_research/h-m1/code/convergence_detector.py
class ConvergenceDetector:
    def __init__(self, window_months: int = 6, threshold: float = 0.005, top_k: int = 5):
        self.window_months = window_months
        self.threshold = threshold
        self.top_k = top_k
```

**Reused in h-m3:** Import as baseline saturation detector (M3-4)

### h-m2 Citation Infrastructure (Verified from Actual Code)

```python
# From: docs/youra_research/h-m2/code/config.py
CACHE_DIR = DATA_DIR / "citations"
RATE_LIMIT = (100, 300)  # 100 requests per 300 seconds
ADOPTION_THRESHOLD = 50  # citations/month
ADOPTION_WINDOW = 3  # months sustained
RANDOM_SEED = 42
```

**Reused in h-m3:** Citation cache directory pattern, rate limiting

---

## Task Configurations

### M3-1: Data Integration

```python
CONFIG = {
    "h1_results": H1_RESULTS_PATH,
    "h2_cache": H2_CITATION_CACHE,
    "ground_truth": GROUND_TRUTH_PATH,
    "benchmarks": BENCHMARKS
}
```

### M3-2: Velocity Computation

```python
CONFIG = {
    "window": VELOCITY_WINDOW,
    "method": "rolling_diff",  # (citations[t] - citations[t-window]) / window
    "fill_na": "forward"
}
```

### M3-3: Spike Detection

```python
CONFIG = {
    "threshold": SPIKE_THRESHOLD,
    "search_window_pre": SEARCH_WINDOW_PRE,
    "search_window_post": SEARCH_WINDOW_POST,
    "method": "zscore"  # (velocity - mean) / std
}
```

### M3-4: Baseline Model

```python
CONFIG = {
    "detector": "h-m1.ConvergenceDetector",
    "params": {
        "window_months": 6,
        "threshold": 0.005,
        "top_k": 5
    }
}
```

### M3-5: Proposed Model

```python
CONFIG = {
    "saturation_detector": "h-m1.ConvergenceDetector",
    "velocity_detector": "VelocityDetector",
    "temporal_alignment": CORRELATION_LEAD_TIME,
    "logic": "AND"  # Both saturation AND velocity spike
}
```

### M3-6: Ground Truth Labels

```python
CONFIG = {
    "label_threshold": CORRELATION_LEAD_TIME,  # 6 months
    "label_logic": "shift within threshold of saturation",
    "format": "binary"  # 1 = shift, 0 = no shift
}
```

### M3-7: Metrics Computation

```python
CONFIG = {
    "metrics": ["precision", "recall", "f1"],
    "zero_division": 0,  # sklearn parameter
    "output_path": OUTPUT_DIR / "metrics.json"
}
```

### M3-8: Gate Metrics Plot

```python
CONFIG = {
    "output_path": FIGURES_DIR / "gate_metrics.png",
    "target_precision": TARGET_PRECISION,
    "target_recall": TARGET_RECALL,
    "models": ["Target", "Baseline", "Proposed"],
    "figsize": (8, 5),
    "dpi": DPI
}
```

### M3-9: Velocity Timeline Plot

```python
CONFIG = {
    "output_path": FIGURES_DIR / "citation_velocity_timeline.png",
    "markers": ["saturation_date", "shift_date"],
    "figsize": FIGSIZE,
    "dpi": DPI
}
```

### M3-10: Confusion Matrix Heatmap

```python
CONFIG = {
    "output_path": FIGURES_DIR / "confusion_matrix.png",
    "annot": True,
    "cmap": "RdBu_r",
    "figsize": (6, 5),
    "dpi": DPI
}
```

### M3-11: Pipeline Orchestration

```python
CONFIG = {
    "output_predictions": OUTPUT_DIR / "predictions.csv",
    "output_metrics": OUTPUT_DIR / "metrics.json",
    "benchmarks": BENCHMARKS,
    "verbose": True,
    "gate_evaluation": True
}
```

---

## Ground Truth File Format

### paradigm_shifts.json

```json
{
  "imagenet": "2015-12",
  "glue": "2018-10",
  "squad": "2019-02",
  "coco": "2021-05",
  "wmt14": "2020-06",
  "librispeech": "2020-09",
  "superglue": "2019-04",
  "mnli": "2018-11",
  "hellaswag": "2019-05",
  "boolq": "2019-08",
  "arc": "2019-07",
  "winogrande": "2019-12",
  "mmlu": "2020-09",
  "truthfulqa": "2021-09",
  "gsm8k": "2021-11"
}
```

**Note:** Dates represent documented paradigm shift events (GPT-3, ViT, LLaMA releases aligned to benchmarks).

---

## Directory Setup

```python
# setup.py (create folders on first run)
from pathlib import Path

def create_directory_structure():
    """Create output directories if they don't exist."""
    directories = [
        Path(__file__).parent.parent / "results",
        Path(__file__).parent.parent / "figures",
        Path(__file__).parent.parent / "data"
    ]
    for dir_path in directories:
        dir_path.mkdir(exist_ok=True, parents=True)
    print("Directory structure created")

if __name__ == "__main__":
    create_directory_structure()
```

---

## Configuration Summary

| Category | Method | Rationale |
|----------|--------|-----------|
| Format | Hardcoded dict | LIGHT tier standard |
| Data Source | h-m1 + h-m2 outputs | Reuses validated data |
| Parameters | Fixed values | EXISTENCE hypothesis - no tuning |
| Logging | print() | No framework overhead |
| Subtasks | 0/0 used | LIGHT tier - no decomposition |

---

**Document Status:** READY FOR PHASE 4
