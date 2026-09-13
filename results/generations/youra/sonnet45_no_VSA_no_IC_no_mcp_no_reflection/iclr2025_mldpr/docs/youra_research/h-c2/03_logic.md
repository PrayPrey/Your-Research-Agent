# Logic Design: Low-Confidence Expert Dispersion Analysis (h-c2)

**Version:** 1.0  
**Date:** 2026-08-28  
**Hypothesis ID:** h-c2  
**Budget:** 2 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** API signatures verified from base code  
**Analyzed Path:** `docs/youra_research/h-c1/code/`  
**Relevant Symbols:** SurveyDataLoader, check_sample_size, check_date_validity, plot_date_distribution

---

## Applied Patterns

Applied: Pandas groupby with std aggregation  
Applied: h-c1 module reuse via sys.path

---

## B-1: Data Pipeline [Complexity: 4, Budget: 1]

Applied: h-c1 SurveyDataLoader with inverted filter logic

### API Signatures

```python
# Reuse from h-c1 (verified from actual code)
import sys
sys.path.insert(0, '../h-c1/code')

from src.data_loader import SurveyDataLoader
from src.validators import check_sample_size, check_date_validity

def load_low_confidence_data(csv_path: str) -> pd.DataFrame:
    """
    Load and filter low-confidence responses.
    Args:
        csv_path: path to h-c1 survey CSV
    Returns:
        df with confidence < 3 (inverse of h-c1 filter)
    """
    loader = SurveyDataLoader(csv_path, confidence_threshold=3)
    df = loader.load_raw()
    return df[df['confidence'] < 3].copy()  # Invert filter
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Import h-c1 loader + invert filter | sys.path setup, confidence <3 filter, validate n>=10 |

---

## B-2: Dispersion Metrics [Complexity: 6, Budget: 1]

Applied: Standard pandas std() with decimal year conversion

### API Signatures

```python
import pandas as pd
import numpy as np
from typing import Dict, Tuple

def convert_to_decimal_year(df: pd.DataFrame) -> pd.Series:
    """year + month/12. Returns: decimal year series"""
    return df['saturation_year'] + df['saturation_month'] / 12.0

def calculate_std_dev_by_benchmark(df: pd.DataFrame, benchmark: str) -> Dict[str, float]:
    """
    Compute std dev of saturation years for one benchmark.
    Args:
        df: low-confidence responses
        benchmark: "ImageNet" | "GLUE" | "SQuAD"
    Returns:
        {
            'mean': 2021.3,
            'std_dev': 0.8,
            'std_dev_pct': 0.04,  # std_dev / mean
            'n': 15
        }
    """
    subset = df[df['benchmark'] == benchmark]
    years = convert_to_decimal_year(subset)
    
    return {
        'mean': years.mean(),
        'std_dev': years.std(),
        'std_dev_pct': (years.std() / years.mean()) if years.mean() > 0 else 0,
        'n': len(subset)
    }

def evaluate_gate(results: Dict[str, dict]) -> Tuple[bool, list]:
    """
    BEST_EFFORT gate: pass if ANY benchmark std_dev_pct > 0.30.
    Args:
        results: {benchmark: metrics_dict}
    Returns:
        (gate_satisfied, passing_benchmarks)
    """
    passing = [
        b for b, r in results.items()
        if r.get('std_dev_pct', 0) > 0.30 and r.get('n', 0) >= 10
    ]
    return len(passing) > 0, passing
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Std dev + gate logic | Decimal year conversion, per-benchmark std, 30% threshold check |

---

## Visualization (Extended from h-c1)

Applied: h-c1 plot_date_distribution + new std_dev_bars

### API Signatures

```python
from src.visualizer import plot_date_distribution  # h-c1 reuse
import matplotlib.pyplot as plt
from typing import Dict

def plot_std_dev_bars(results: Dict[str, dict], threshold: float, output_path: str) -> None:
    """
    Bar chart with 30% threshold line.
    Args:
        results: {benchmark: {'std_dev_pct': 0.35, 'n': 15}}
        threshold: gate threshold (0.30)
        output_path: save path (PNG)
    """
    benchmarks = list(results.keys())
    std_devs = [r['std_dev_pct'] * 100 for r in results.values()]  # Convert to %
    
    plt.figure(figsize=(10, 6))
    plt.bar(benchmarks, std_devs, alpha=0.7, edgecolor='black')
    plt.axhline(threshold * 100, color='red', linestyle='--', label=f'Gate Threshold ({threshold*100:.0f}%)')
    plt.xlabel('Benchmark')
    plt.ylabel('Standard Deviation (%)')
    plt.title('Low-Confidence Response Dispersion')
    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
```

---

## Main Pipeline

Applied: Argparse + Path validation (h-c1 pattern)

### API Signatures

```python
from pathlib import Path
from typing import Dict

def run_analysis(df: pd.DataFrame, output_dir: Path, benchmarks: list) -> Dict[str, dict]:
    """
    End-to-end dispersion analysis.
    Args:
        df: low-confidence responses
        output_dir: results directory
        benchmarks: ["ImageNet", "GLUE", "SQuAD"]
    Returns:
        results: {benchmark: {mean, std_dev, std_dev_pct, n}}
    
    Steps:
        1. For each benchmark:
            a. Validate n >= 10 (from h-c1 validators)
            b. Calculate std dev metrics
        2. Evaluate BEST_EFFORT gate
        3. Generate plots (std_dev_bars, date distributions)
        4. Export CSV/JSON results
    """
    ...

def export_results(results: dict, gate_status: bool, passing: list, output_dir: Path) -> None:
    """
    Write dispersion_summary.csv and dispersion_summary.json.
    Args:
        results: {benchmark: metrics_dict}
        gate_status: bool from evaluate_gate
        passing: list of benchmarks that passed
        output_dir: save directory
    """
    ...
```

---

## Configuration

Applied: Module-level constants

### API Signatures

```python
# config.py

CONFIDENCE_THRESHOLD = 3  # Low-confidence: <3/5 (inverse of h-c1 >=4)
MIN_SAMPLE_SIZE = 10  # Relaxed from h-c1's 30 (smaller expected sample)
BENCHMARKS = ["ImageNet", "GLUE", "SQuAD"]
STD_DEV_PCT_THRESHOLD = 0.30  # 30% std dev gate
VALID_YEAR_RANGE = (2017, 2024)
OUTPUT_FORMATS = ["csv", "json"]
PLOT_DPI = 150
```

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

Verified from: `docs/youra_research/h-c1/code/` (actual implementation)

```python
# From: h-c1/code/src/data_loader.py
class SurveyDataLoader:
    def __init__(self, csv_path: str, confidence_threshold: int = 4):
        """
        Args:
            csv_path: Path to survey CSV
            confidence_threshold: Min confidence (1-5)
        """
        ...
    
    def load_raw(self) -> pd.DataFrame:
        """Load CSV. Returns df with required columns."""
        ...
    
    def filter_high_confidence(self, df: pd.DataFrame) -> pd.DataFrame:
        """Keep rows where confidence >= threshold."""
        ...
    
    def get_benchmark_subset(self, df: pd.DataFrame, benchmark: str) -> pd.DataFrame:
        """Extract rows for one benchmark."""
        ...

# From: h-c1/code/src/validators.py
def check_sample_size(df: pd.DataFrame, min_size: int = 30) -> Tuple[bool, Dict[str, int]]:
    """
    Verify >=min_size responses per benchmark.
    Returns: (all_pass, counts_dict)
    """
    ...

def check_date_validity(
    df: pd.DataFrame,
    min_year: int = 2017,
    max_year: int = 2024
) -> Tuple[bool, List[int]]:
    """
    Flag dates outside valid range.
    Returns: (all_valid, invalid_row_indices)
    """
    ...

# From: h-c1/code/src/visualizer.py
def plot_date_distribution(
    df: pd.DataFrame,
    benchmark: str,
    modal_date: Tuple[int, int],
    output_path: str
) -> None:
    """
    Histogram of saturation dates with modal marker.
    Args:
        df: subset for one benchmark
        benchmark: name for title
        modal_date: (year, month) for vertical line
        output_path: save path (PNG)
    """
    ...
```

**Import Pattern:**
```python
import sys
sys.path.insert(0, '../h-c1/code')

from src.data_loader import SurveyDataLoader
from src.validators import check_sample_size, check_date_validity
from src.visualizer import plot_date_distribution
```

---

## Subtask Budget Summary

| Task | Allocated | Used | Remaining |
|------|-----------|------|-----------|
| B-1 | 1 | 1 | 0 |
| B-2 | 1 | 1 | 0 |
| **Total** | **2** | **2** | **0** |

---

**Logic Design Status:** COMPLETE  
**Phase 4 Coder Input:** Ready  
**Budget Compliance:** 2/2 subtasks used
