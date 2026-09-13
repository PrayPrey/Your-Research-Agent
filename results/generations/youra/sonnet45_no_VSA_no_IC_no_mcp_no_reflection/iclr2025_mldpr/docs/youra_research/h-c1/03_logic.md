# Logic Design: Expert Consensus Validation System (h-c1)

**Version:** 1.0  
**Date:** 2026-08-28  
**Hypothesis ID:** h-c1  
**Budget:** 3 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** Green-field implementation - no existing code to analyze  
**Analyzed Path:** N/A  
**Relevant Symbols:** None - new implementation

---

## Applied Patterns

Applied: Pandas vectorized operations for date filtering  
Applied: Statsmodels Fleiss kappa standard implementation  
Applied: Scipy permutation tests

---

## A-1: Data Pipeline [Complexity: 6, Budget: 1]

Applied: Standard pandas CSV loader with validation

### API Signatures

```python
from dataclasses import dataclass
from typing import Tuple, List
import pandas as pd

@dataclass
class SurveyResponse:
    """Single expert response."""
    benchmark: str
    saturation_year: int
    saturation_month: int
    confidence: int
    domain: str
    career_stage: str

class SurveyDataLoader:
    def __init__(self, csv_path: str, confidence_threshold: int = 4):
        """
        Args:
            csv_path: Path to survey CSV
            confidence_threshold: Min confidence (1-5)
        """
        self.csv_path = csv_path
        self.confidence_threshold = confidence_threshold
    
    def load_raw(self) -> pd.DataFrame:
        """Load CSV. Returns: df with columns [response_id, benchmark, saturation_year, saturation_month, confidence, domain, career_stage]"""
        ...
    
    def filter_high_confidence(self, df: pd.DataFrame) -> pd.DataFrame:
        """Keep rows where confidence >= threshold. Returns: filtered df"""
        ...
    
    def validate_completeness(self, df: pd.DataFrame) -> Tuple[bool, str]:
        """Check required fields exist. Returns: (is_valid, error_message)"""
        ...
    
    def get_benchmark_subset(self, df: pd.DataFrame, benchmark: str) -> pd.DataFrame:
        """Extract rows for one benchmark. Returns: subset df"""
        ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | CSV loader + high-conf filter | Load CSV, filter confidence ≥4, validate fields |

---

## A-2: Core Metrics [Complexity: 10, Budget: 1]

Applied: Statsmodels fleiss_kappa

### API Signatures

```python
from typing import Tuple
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.inter_rater import fleiss_kappa

def calculate_modal_date(dates: pd.DataFrame) -> Tuple[int, int]:
    """
    Compute mode of (year, month) pairs. If tie, select earliest.
    Args:
        dates: df with columns [saturation_year, saturation_month]
    Returns:
        (modal_year, modal_month)
    """
    ...

def calculate_agreement_rate(
    dates: pd.DataFrame, 
    modal_date: Tuple[int, int], 
    window_months: int = 12
) -> float:
    """
    % of dates within ±window_months of modal_date.
    Args:
        dates: df with [saturation_year, saturation_month]
        modal_date: (year, month)
        window_months: tolerance (default 12)
    Returns:
        agreement_rate (0-100%)
    
    Algorithm:
        1. Convert dates to months since epoch: m = year*12 + month
        2. modal_m = modal_year*12 + modal_month
        3. count dates where |m - modal_m| <= window_months
        4. agreement = count / total * 100
    """
    ...

def prepare_kappa_matrix(dates: pd.DataFrame, n_categories: int = 8) -> np.ndarray:
    """
    Convert dates to N×K matrix for Fleiss kappa.
    Args:
        dates: df with [saturation_year, saturation_month]
        n_categories: year buckets (2017-2024 = 8)
    Returns:
        matrix [n_items, n_categories] where matrix[i,j] = count of raters selecting category j for item i
    
    Note: For single-item rating (one benchmark), create synthetic items by grouping raters.
    Matrix shape: [1, 8] with counts per year bucket.
    """
    ...

def calculate_fleiss_kappa(dates: pd.DataFrame) -> float:
    """
    Chance-adjusted agreement. Uses statsmodels implementation.
    Args:
        dates: df with [saturation_year, saturation_month]
    Returns:
        kappa (0-1, can be negative if worse than chance)
    
    Edge cases:
        - All agree: κ=1.0
        - Perfect disagreement: κ≈0
        - Division by zero: return 1.0 if all raters agree
    """
    ...
```

### Mathematical Definitions

**Agreement Rate:**
```
agreement_rate = (# responses within ±12 months of mode) / (total responses) × 100
```

**Fleiss' Kappa:**
```
κ = (P̄ - P̄e) / (1 - P̄e)
where:
  P̄ = mean pairwise agreement across all items
  P̄e = expected agreement by chance
  
For year buckets (2017-2024):
  - Convert dates to years (ignore months for kappa)
  - Categories: [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
  - Use statsmodels.stats.inter_rater.fleiss_kappa(matrix, method='fleiss')
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Modal date + agreement + kappa | Compute mode, agreement %, fleiss kappa |

---

## A-3: Statistical Tests [Complexity: 8, Budget: 1]

Applied: Scipy bootstrap + permutation tests

### API Signatures

```python
from typing import Tuple
import numpy as np
import pandas as pd

def bootstrap_confidence_interval(
    dates: pd.DataFrame,
    modal_date: Tuple[int, int],
    window_months: int = 12,
    n_iterations: int = 1000,
    random_seed: int = 42
) -> Tuple[float, float]:
    """
    95% CI for agreement rate via bootstrap.
    Args:
        dates: df with [saturation_year, saturation_month]
        modal_date: (year, month)
        window_months: tolerance
        n_iterations: bootstrap samples
        random_seed: for reproducibility
    Returns:
        (ci_lower, ci_upper) as percentages
    
    Algorithm:
        1. Set random seed
        2. For i in 1..n_iterations:
            a. Resample dates with replacement (same size as original)
            b. Compute agreement_rate for resampled data
            c. Store rate
        3. ci_lower = 2.5th percentile of rates
        4. ci_upper = 97.5th percentile of rates
    """
    ...

def permutation_test(
    dates: pd.DataFrame,
    observed_agreement: float,
    window_months: int = 12,
    n_permutations: int = 1000,
    random_seed: int = 42
) -> float:
    """
    Test if agreement > random chance (null hypothesis).
    Args:
        dates: df with [saturation_year, saturation_month]
        observed_agreement: actual agreement %
        window_months: tolerance
        n_permutations: shuffle iterations
        random_seed: for reproducibility
    Returns:
        p_value: proportion of permutations with agreement >= observed
    
    Algorithm:
        1. Set random seed
        2. For i in 1..n_permutations:
            a. Shuffle dates randomly
            b. Compute modal_date from shuffled data
            c. Compute agreement_rate for shuffled data
            d. Store rate
        3. p_value = (# permuted rates >= observed_agreement) / n_permutations
        
    Expected null agreement: <30% (random chance)
    Threshold: p<0.05 for significance
    """
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Bootstrap CI + permutation test | 1000 iterations each, 95% CI, p-value |

---

## Validation Functions

Applied: Pandas groupby for stratification checks

### API Signatures

```python
from typing import Tuple, Dict, List
import pandas as pd

def check_sample_size(df: pd.DataFrame, min_size: int = 30) -> Tuple[bool, Dict[str, int]]:
    """
    Verify ≥min_size responses per benchmark.
    Args:
        df: filtered high-confidence df
        min_size: threshold (default 30)
    Returns:
        (all_pass, counts_dict)
    
    Example:
        all_pass=True, {"ImageNet": 42, "GLUE": 38, "SQuAD": 35}
    """
    ...

def check_domain_balance(
    df: pd.DataFrame, 
    min_ratio: float = 0.4, 
    max_ratio: float = 0.6
) -> Tuple[bool, Dict[str, float]]:
    """
    Check vision:NLP split in acceptable range.
    Args:
        df: full df (all benchmarks)
        min_ratio: min acceptable proportion (0.4 = 40%)
        max_ratio: max acceptable proportion (0.6 = 60%)
    Returns:
        (is_balanced, ratios_dict)
    
    Example:
        is_balanced=True, {"vision": 0.52, "nlp": 0.45, "other": 0.03}
    """
    ...

def check_date_validity(
    df: pd.DataFrame, 
    min_year: int = 2017, 
    max_year: int = 2024
) -> Tuple[bool, List[int]]:
    """
    Flag dates outside valid range.
    Args:
        df: df with saturation_year column
        min_year: earliest valid year
        max_year: latest valid year
    Returns:
        (all_valid, invalid_row_indices)
    """
    ...
```

---

## Visualization

Applied: Matplotlib histograms + error bars

### API Signatures

```python
import matplotlib.pyplot as plt
from typing import Dict, Tuple
import pandas as pd

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
    
    Plot:
        - X-axis: year.month (e.g., 2019.5 for June 2019)
        - Y-axis: count of responses
        - Vertical red line at modal_date
        - Title: "{benchmark} Saturation Date Distribution"
    """
    ...

def plot_agreement_bars(results: Dict[str, dict], output_path: str) -> None:
    """
    Bar chart: agreement rate per benchmark with 95% CI error bars.
    Args:
        results: {benchmark: {"agreement_rate": 78.0, "ci_lower": 73.5, "ci_upper": 82.1}}
        output_path: save path (PNG)
    
    Plot:
        - X-axis: benchmark names
        - Y-axis: agreement rate (%)
        - Error bars: ci_lower to ci_upper
        - Horizontal line at 70% threshold
    """
    ...

def plot_kappa_comparison(results: Dict[str, dict], output_path: str) -> None:
    """
    Bar chart: Fleiss kappa per benchmark.
    Args:
        results: {benchmark: {"fleiss_kappa": 0.71}}
        output_path: save path (PNG)
    
    Plot:
        - X-axis: benchmark names
        - Y-axis: kappa (0-1)
        - Horizontal lines at 0.6 (substantial), 0.8 (almost perfect)
    """
    ...
```

---

## Main Pipeline

Applied: Argparse CLI + Path validation

### API Signatures

```python
import argparse
from pathlib import Path
from typing import Dict

def run_analysis(survey_csv: Path, output_dir: Path, config: dict) -> Dict[str, dict]:
    """
    End-to-end pipeline.
    Args:
        survey_csv: path to survey CSV
        output_dir: results directory
        config: dict with thresholds (confidence, window_months, min_sample_size)
    Returns:
        results: {benchmark: {agreement_rate, fleiss_kappa, ci_lower, ci_upper, p_value, n_high_conf}}
    
    Steps:
        1. Load CSV, filter high-confidence
        2. Validate sample size, domain balance, date validity
        3. For each benchmark:
            a. Calculate modal date
            b. Calculate agreement rate
            c. Calculate Fleiss kappa
            d. Bootstrap 95% CI
            e. Permutation test p-value
        4. Generate plots (distributions, bars, kappa)
        5. Export results (CSV, JSON, Markdown)
        6. Return results dict
    """
    ...

def export_results(results: Dict[str, dict], output_dir: Path) -> None:
    """
    Write CSV + JSON + Markdown summaries.
    Args:
        results: {benchmark: metrics_dict}
        output_dir: save directory
    
    Outputs:
        - {output_dir}/agreement_summary.csv
        - {output_dir}/agreement_summary.json
        - {output_dir}/agreement_summary.md
    """
    ...

def evaluate_gate(results: Dict[str, dict]) -> Tuple[str, str]:
    """
    Gate decision logic from PRD.
    Args:
        results: {benchmark: {agreement_rate, n_high_conf, fleiss_kappa}}
    Returns:
        (gate_status, action)
    
    Logic:
        IF all benchmarks pass (agreement>70%, n>=30, kappa>0.6):
            return ("SATISFIED", "Proceed to H-M1/H-M2")
        ELIF all benchmarks have agreement<50%:
            return ("FAILED", "PIVOT to citation-based validation")
        ELSE:
            return ("PARTIAL", "Use ImageNet consensus, citation fallback for weak benchmarks")
    """
    ...

def print_summary(results: Dict[str, dict]) -> None:
    """Print human-readable summary to stdout."""
    ...
```

---

## Configuration

Applied: Module-level constants

### API Signatures

```python
# config.py

CONFIDENCE_THRESHOLD = 4  # Min confidence rating (1-5 scale)
AGREEMENT_WINDOW_MONTHS = 12  # ±1 year tolerance
MIN_SAMPLE_SIZE = 30  # Statistical power threshold
AGREEMENT_THRESHOLD = 0.70  # Gate pass threshold (70%)
KAPPA_THRESHOLD = 0.60  # Substantial agreement threshold
BOOTSTRAP_ITERATIONS = 1000  # 95% CI iterations
PERMUTATION_ITERATIONS = 1000  # Null hypothesis test iterations
VALID_YEAR_RANGE = (2017, 2024)  # Benchmark saturation window
BENCHMARKS = ["ImageNet", "GLUE", "SQuAD"]  # Target benchmarks
RANDOM_SEED = 42  # Reproducibility
```

---

## Error Handling

**Data Quality Failures:**
- Missing required fields → skip row, log warning, continue
- Invalid date (outside 2017-2024) → skip row, log warning
- Sample size <30 → raise ValueError with benchmark name

**Statistical Edge Cases:**
- All raters agree → κ=1.0 (handle manually if statsmodels errors)
- Bimodal distribution → select earliest mode
- Tie for modal date → select earliest date (lexicographic)

**File I/O Errors:**
- CSV not found → raise FileNotFoundError with expected path
- Output directory missing → create automatically with Path.mkdir(parents=True)
- Permission denied → raise PermissionError with actionable message

---

## Testing Strategy

Applied: Pytest with synthetic fixtures

### Test Cases

```python
# tests/test_metrics.py

def test_modal_date_simple():
    """All agree → mode = unanimous date"""
    dates = pd.DataFrame({"saturation_year": [2019]*5, "saturation_month": [6]*5})
    assert calculate_modal_date(dates) == (2019, 6)

def test_modal_date_tie():
    """Tie → select earliest"""
    dates = pd.DataFrame({
        "saturation_year": [2019, 2019, 2020, 2020],
        "saturation_month": [6, 6, 3, 3]
    })
    assert calculate_modal_date(dates) == (2019, 6)

def test_agreement_rate_perfect():
    """All within window → 100%"""
    dates = pd.DataFrame({"saturation_year": [2019]*5, "saturation_month": [6]*5})
    modal = (2019, 6)
    assert calculate_agreement_rate(dates, modal, window_months=12) == 100.0

def test_agreement_rate_partial():
    """3/5 within window → 60%"""
    dates = pd.DataFrame({
        "saturation_year": [2019, 2019, 2019, 2021, 2021],
        "saturation_month": [6, 7, 8, 1, 2]
    })
    modal = (2019, 6)
    assert calculate_agreement_rate(dates, modal, window_months=12) == 60.0

def test_fleiss_kappa_perfect():
    """All agree → κ=1.0"""
    dates = pd.DataFrame({"saturation_year": [2019]*10, "saturation_month": [6]*10})
    kappa = calculate_fleiss_kappa(dates)
    assert abs(kappa - 1.0) < 0.01

def test_bootstrap_ci_width():
    """CI width <20% for stable estimate"""
    dates = pd.DataFrame({
        "saturation_year": [2019]*30,
        "saturation_month": [6]*30
    })
    modal = (2019, 6)
    ci_lower, ci_upper = bootstrap_confidence_interval(dates, modal, n_iterations=100)
    assert (ci_upper - ci_lower) < 20.0

def test_permutation_test_significance():
    """Strong agreement → p<0.05"""
    dates = pd.DataFrame({
        "saturation_year": [2019]*40,
        "saturation_month": [6]*35 + [12]*5
    })
    observed = 87.5  # 35/40 within ±12 months of mode
    p_value = permutation_test(dates, observed, n_permutations=100)
    assert p_value < 0.05
```

---

## Subtask Budget Summary

| Task | Allocated | Used | Remaining |
|------|-----------|------|-----------|
| A-1 | 1 | 1 | 0 |
| A-2 | 1 | 1 | 0 |
| A-3 | 1 | 1 | 0 |
| **Total** | **3** | **3** | **0** |

---

## Implementation Notes

**Pandas vectorization:** Use `df.groupby()` for per-benchmark aggregation, avoid Python loops.

**Statsmodels caveat:** fleiss_kappa expects N×K matrix where N=items, K=categories. For single-benchmark rating (one item, multiple raters), treat each response as separate "item" with one category selected. Alternative: group raters into pseudo-items.

**Random seed:** Set `np.random.seed(RANDOM_SEED)` at start of bootstrap/permutation functions for reproducibility.

**Month arithmetic:** Convert (year, month) to months-since-epoch: `m = year*12 + month`. Compare with `abs(m1 - m2) <= window_months`.

**Mode ties:** Use `pd.Series.mode()` which returns earliest if tie. If multiple modes, take `mode()[0]`.

---

**Logic Design Status:** COMPLETE  
**Phase 4 Coder Input:** Ready  
**Budget Compliance:** 3/3 subtasks used
