# Architecture: Low-Confidence Expert Dispersion Analysis (h-c2)

**Version:** 1.0  
**Date:** 2026-08-28  
**Hypothesis ID:** h-c2  
**Type:** CONDITION  
**Tier:** LIGHT (statistical analysis only)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Patterns found from base code  
**Analyzed Path:** `docs/youra_research/h-c1/code/`  
**Findings:** Reuses h-c1 data loader, extends with low-confidence filtering

---

## Applied Patterns

Applied: Statistical analysis pipeline (data loader → dispersion metrics → visualization)  
Applied: h-c1 module reuse (data loader, validators, visualizer)

---

## Module Structure

### 1. Data Loader (REUSED from h-c1)

**Import Path:** `sys.path.insert(0, '../h-c1/code'); from src.data_loader import SurveyDataLoader`

**Usage:**
```python
from src.data_loader import SurveyDataLoader

loader = SurveyDataLoader(
    csv_path='../h-c1/code/expert_survey_responses.csv',
    confidence_threshold=3  # INVERSE: <3 instead of >=4
)
df = loader.load_raw()
low_conf = df[df['confidence'] < 3]  # Filter low-confidence subset
```

**Note:** Inverts h-c1 filter logic (< threshold vs >= threshold)

---

### 2. Dispersion Metrics (`src/dispersion_metrics.py`)

**Dependencies:** pandas, numpy

```python
import pandas as pd
import numpy as np
from typing import Dict, Tuple

def convert_to_decimal_year(df: pd.DataFrame) -> pd.Series: ...
def calculate_std_dev_by_benchmark(df: pd.DataFrame, benchmark: str) -> Dict[str, float]: ...
def calculate_std_dev_pct(std_dev: float, mean_year: float) -> float: ...
def validate_sample_size(df: pd.DataFrame, benchmark: str, min_n: int = 10) -> Tuple[bool, int]: ...
def evaluate_gate(results: Dict[str, dict]) -> Tuple[bool, list]: ...
```

**Core Logic:**
```python
def calculate_std_dev_by_benchmark(df: pd.DataFrame, benchmark: str) -> Dict[str, float]:
    subset = df[df['benchmark'] == benchmark]
    
    # Convert YYYY-MM to decimal years
    years = subset['saturation_year'] + subset['saturation_month'] / 12.0
    
    return {
        'mean': years.mean(),
        'std_dev': years.std(),
        'std_dev_pct': (years.std() / years.mean()) if years.mean() > 0 else 0,
        'n': len(subset)
    }
```

---

### 3. Validators (REUSED from h-c1)

**Import Path:** `from src.validators import check_sample_size, check_date_validity`

**Usage:**
```python
from src.validators import check_sample_size

# Validate n >= 10 before computing std dev
valid, info = check_sample_size(low_conf_subset, min_size=10)
if not valid:
    results[benchmark] = {'status': 'insufficient_samples', 'n': info['n']}
```

---

### 4. Visualization (REUSED + EXTENDED)

**Import Path:** `from src.visualizer import plot_date_distribution`

**New Functions:**
```python
def plot_std_dev_bars(results: Dict[str, dict], threshold: float, output_path: str): ...
def plot_confidence_stratification(df: pd.DataFrame, output_path: str): ...
def plot_sample_sizes(results: Dict[str, dict], min_n: int, output_path: str): ...
```

**Extension:**
```python
def plot_std_dev_bars(results: Dict[str, dict], threshold: float, output_path: str):
    """Bar chart with 30% threshold line overlay."""
    benchmarks = list(results.keys())
    std_devs = [r['std_dev_pct'] for r in results.values()]
    
    plt.bar(benchmarks, std_devs)
    plt.axhline(y=threshold, color='r', linestyle='--', label='Gate Threshold (30%)')
    plt.ylabel('Standard Deviation (%)')
    plt.savefig(output_path)
```

---

### 5. Main Analysis Script (`analyze_dispersion.py`)

**Dependencies:** dispersion_metrics, h-c1 modules (via import)

```python
import sys
sys.path.insert(0, '../h-c1/code')  # Access h-c1 modules

from src.data_loader import SurveyDataLoader
from src.validators import check_sample_size
import src.dispersion_metrics as metrics

def run_analysis(survey_csv: str, output_dir: str) -> dict: ...
def export_results(results: dict, output_dir: str): ...
def print_summary(results: dict, gate_status: bool): ...

if __name__ == "__main__":
    # Load h-c1 data with inverted filter
    loader = SurveyDataLoader('../h-c1/code/expert_survey_responses.csv', confidence_threshold=3)
    df = loader.load_raw()
    low_conf = df[df['confidence'] < 3]  # Invert filter
    
    # Run dispersion analysis
    results = run_analysis(low_conf, 'results')
```

---

### 6. Configuration (`config.py`)

```python
# Inverse of h-c1 threshold
CONFIDENCE_THRESHOLD = 3  # Low-confidence: <3/5 (vs h-c1 >=4/5)
MIN_SAMPLE_SIZE = 10  # Relaxed from h-c1's 30 (smaller expected sample)
BENCHMARKS = ["ImageNet", "GLUE", "SQuAD"]

# Dispersion thresholds
STD_DEV_PCT_THRESHOLD = 0.30  # 30% std dev gate
VALID_YEAR_RANGE = (2017, 2024)

# Visualization
OUTPUT_FORMATS = ["csv", "json"]
PLOT_DPI = 150
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| SurveyDataLoader | `sys.path.insert(0, '../h-c1/code'); from src.data_loader import SurveyDataLoader` | `h-c1/code/src/data_loader.py` |
| Validators | `from src.validators import check_sample_size, check_date_validity` | `h-c1/code/src/validators.py` |
| Visualizer (base) | `from src.visualizer import plot_date_distribution` | `h-c1/code/src/visualizer.py` |

**Verified from:** `docs/youra_research/h-c1/code/` (actual implementation)

**Data Dependency:**
- CSV: `docs/youra_research/h-c1/code/expert_survey_responses.csv` (symlink or direct path)

---

## File Organization

```
h-c2/
├── code/
│   ├── src/
│   │   ├── dispersion_metrics.py (NEW)
│   │   └── visualizer_ext.py (NEW - extends h-c1 visualizer)
│   ├── analyze_dispersion.py (NEW - main script)
│   ├── config.py (NEW - h-c2 specific config)
│   └── requirements.txt (symlink to h-c1/code/requirements.txt)
├── results/
│   ├── dispersion_summary.csv
│   ├── dispersion_summary.json
│   └── plots/
│       ├── std_dev_bars.png
│       ├── confidence_stratification.png
│       └── sample_sizes.png
└── tests/
    └── test_dispersion_metrics.py
```

**Note:** h-c1 modules accessed via `sys.path` manipulation (no code duplication)

---

## Epic-Level Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| B-1 | Data Pipeline | Reuse h-c1 loader + invert filter + validate n>=10 | 4 | 1+1+1+1 (path setup=1, filter=1, validate=1, test=1) |
| B-2 | Dispersion Metrics | Decimal year conversion + std dev + pct calculation | 6 | 2+2+1+1 (conversion=2, std_dev=2, pct=1, test=1) |
| B-3 | Gate Logic | Per-benchmark validation + BEST_EFFORT evaluation | 5 | 2+2+1 (validation=2, gate=2, test=1) |
| B-4 | Visualization | Std dev bars + stratification plot + sample sizes | 6 | 2+2+2 (bars=2, stratification=2, sample_sizes=2) |
| B-5 | Integration | Main script + config + results export | 5 | 2+1+1+1 (main=2, config=1, export=1, docs=1) |

**Distribution:**  
- VeryHigh (18-20): []  
- High (14-17): []  
- Medium (9-13): []  
- Low (4-8): [B-2, B-4]  
- VeryLow (1-3): [B-1, B-3, B-5]  
**Total Complexity:** 26 points (LIGHT tier confirmed)

---

## Data Flow

1. Import h-c1 SurveyDataLoader via `sys.path`
2. Load CSV → filter confidence <3 (inverse of h-c1)
3. Per benchmark: validate n ≥ 10
4. Per benchmark: convert dates to decimal years
5. Per benchmark: calculate std dev, mean, std_dev_pct
6. Evaluate BEST_EFFORT gate (any benchmark std_dev_pct > 0.30)
7. Export results → CSV/JSON
8. Generate plots → std dev bars, confidence stratification, sample sizes

---

## Gate Criteria Implementation

```python
def evaluate_gate(results: Dict[str, dict]) -> Tuple[bool, list]:
    """
    BEST_EFFORT gate: Pass if ANY benchmark shows std_dev_pct > 0.30.
    
    Returns: (gate_satisfied, passing_benchmarks)
    """
    passing = [
        benchmark for benchmark, r in results.items()
        if r.get('std_dev_pct', 0) > 0.30 and r.get('n', 0) >= 10
    ]
    return len(passing) > 0, passing
```

---

## Output Specification

**CSV Format (`dispersion_summary.csv`):**
```
benchmark,n,mean_year,std_dev,std_dev_pct,gate_pass
ImageNet,15,2021.3,0.8,0.04,False
GLUE,12,2022.1,1.5,0.07,False
SQuAD,18,2020.5,7.2,0.35,True
```

**JSON Format (`dispersion_summary.json`):**
```json
{
  "ImageNet": {
    "n": 15,
    "mean_year": 2021.3,
    "std_dev": 0.8,
    "std_dev_pct": 0.04,
    "gate_pass": false
  },
  "gate_satisfied": true,
  "passing_benchmarks": ["SQuAD"]
}
```

---

## Comparison to h-c1

| Aspect | h-c1 (High-Confidence) | h-c2 (Low-Confidence) |
|--------|------------------------|------------------------|
| **Filter** | `confidence >= 4` | `confidence < 3` |
| **Sample Size** | n >= 30 | n >= 10 (relaxed) |
| **Primary Metric** | Agreement rate (%) | Standard deviation (%) |
| **Expected Result** | 76-93% agreement | >30% std dev |
| **Gate Type** | ALL benchmarks >70% | BEST_EFFORT (any >30%) |

**Inverse Validation:** High confidence → low dispersion; Low confidence → high dispersion

---

## Performance Targets

| Operation | Target | Hardware |
|-----------|--------|----------|
| CSV load (150 responses) | <1s | Single-core CPU |
| Std dev (all benchmarks) | <1s | Single-core CPU |
| Visualization (3 plots) | <5s | Single-core CPU |
| Total runtime | <30s | Single-core CPU |

---

**Architecture Status:** COMPLETE  
**Ready for Phase 4 (Coder):** YES  
**Total Epic Tasks:** 5  
**Estimated Implementation Effort:** ~8 hours (core code) + 1 hour (tests)
