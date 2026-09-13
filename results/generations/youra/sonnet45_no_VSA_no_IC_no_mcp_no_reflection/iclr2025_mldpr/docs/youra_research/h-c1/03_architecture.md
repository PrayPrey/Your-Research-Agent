# Architecture: Expert Consensus Validation System (h-c1)

**Version:** 1.0  
**Date:** 2026-08-28  
**Hypothesis ID:** h-c1  
**Type:** CONDITION  
**Tier:** LIGHT (statistical analysis only)

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** Green-field implementation - no existing code to analyze  
**Analyzed Path:** N/A  
**Findings:** New implementation from scratch

---

## Applied Patterns

Applied: Statistical validation module (data loader → metrics → visualization)  
Applied: Minimal file structure (single analysis script + config)

---

## Module Structure

### 1. Data Loader (`src/data_loader.py`)

**Dependencies:** pandas, numpy

```python
import pandas as pd
from typing import Tuple
from dataclasses import dataclass

@dataclass
class SurveyResponse:
    benchmark: str
    saturation_year: int
    saturation_month: int
    confidence: int
    domain: str
    career_stage: str

class SurveyDataLoader:
    def __init__(self, csv_path: str, confidence_threshold: int = 4): ...
    def load_raw(self) -> pd.DataFrame: ...
    def filter_high_confidence(self, df: pd.DataFrame) -> pd.DataFrame: ...
    def validate_completeness(self, df: pd.DataFrame) -> Tuple[bool, str]: ...
    def get_benchmark_subset(self, df: pd.DataFrame, benchmark: str) -> pd.DataFrame: ...
```

### 2. Consensus Metrics (`src/metrics.py`)

**Dependencies:** numpy, scipy, statsmodels

```python
from typing import Tuple
import numpy as np
from scipy import stats
from statsmodels.stats.inter_rater import fleiss_kappa

def calculate_modal_date(dates: pd.Series) -> Tuple[int, int]: ...
def calculate_agreement_rate(dates: pd.Series, modal_date: Tuple[int, int], window_months: int = 12) -> float: ...
def prepare_kappa_matrix(dates: pd.Series) -> np.ndarray: ...
def calculate_fleiss_kappa(dates: pd.Series) -> float: ...
def bootstrap_confidence_interval(dates: pd.Series, window_months: int = 12, n_iterations: int = 1000) -> Tuple[float, float]: ...
def permutation_test(dates: pd.Series, observed_agreement: float, n_permutations: int = 1000) -> float: ...
```

### 3. Validation Checks (`src/validators.py`)

**Dependencies:** pandas

```python
from typing import Tuple

def check_sample_size(df: pd.DataFrame, min_size: int = 30) -> Tuple[bool, dict]: ...
def check_domain_balance(df: pd.DataFrame, min_ratio: float = 0.4, max_ratio: float = 0.6) -> Tuple[bool, dict]: ...
def check_date_validity(df: pd.DataFrame, min_year: int = 2017, max_year: int = 2024) -> Tuple[bool, list]: ...
def detect_spam_responses(df: pd.DataFrame, min_completion_time: int = 30) -> list: ...
```

### 4. Visualization (`src/visualizer.py`)

**Dependencies:** matplotlib

```python
import matplotlib.pyplot as plt
from typing import Dict

def plot_date_distribution(df: pd.DataFrame, benchmark: str, modal_date: Tuple[int, int], output_path: str): ...
def plot_agreement_bars(results: Dict[str, dict], output_path: str): ...
def plot_kappa_comparison(results: Dict[str, dict], output_path: str): ...
```

### 5. Main Analysis Script (`validate_consensus.py`)

**Dependencies:** All modules above

```python
import argparse
from pathlib import Path

def run_analysis(survey_csv: Path, output_dir: Path, config: dict) -> dict: ...
def export_results(results: dict, output_dir: Path): ...
def print_summary(results: dict): ...

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--survey_data", type=str, required=True)
    parser.add_argument("--output_dir", type=str, default="results")
    args = parser.parse_args()
    # Run analysis pipeline
```

### 6. Configuration (`config.py`)

```python
CONFIDENCE_THRESHOLD = 4
AGREEMENT_WINDOW_MONTHS = 12
MIN_SAMPLE_SIZE = 30
AGREEMENT_THRESHOLD = 0.70
KAPPA_THRESHOLD = 0.60
BOOTSTRAP_ITERATIONS = 1000
PERMUTATION_ITERATIONS = 1000
VALID_YEAR_RANGE = (2017, 2024)
BENCHMARKS = ["ImageNet", "GLUE", "SQuAD"]
```

---

## File Organization

```
h-c1/
├── code/
│   ├── src/
│   │   ├── data_loader.py
│   │   ├── metrics.py
│   │   ├── validators.py
│   │   └── visualizer.py
│   ├── validate_consensus.py
│   ├── config.py
│   └── requirements.txt
├── data/
│   ├── expert_survey_responses.csv (user-provided)
│   └── example_survey.csv (test fixture)
├── results/
│   ├── agreement_summary.csv
│   ├── agreement_summary.json
│   ├── agreement_summary.md
│   └── plots/
│       ├── imagenet_distribution.png
│       ├── glue_distribution.png
│       ├── squad_distribution.png
│       ├── agreement_bars.png
│       └── kappa_comparison.png
└── tests/
    ├── test_metrics.py
    └── test_validators.py
```

---

## Epic-Level Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Pipeline | CSV loader + high-conf filter + validation checks | 6 | 2+1+2+1 (loader=2, filter=1, validators=2, tests=1) |
| A-2 | Core Metrics | Modal date + agreement rate + Fleiss kappa | 10 | 2+3+4+1 (modal=2, agreement=3, kappa=4, tests=1) |
| A-3 | Statistical Tests | Bootstrap CI + permutation test | 8 | 3+4+1 (bootstrap=3, permutation=4, tests=1) |
| A-4 | Visualization | Date distributions + agreement bars + kappa plot | 5 | 2+2+1 (histograms=2, bars=2, export=1) |
| A-5 | Integration | Main script + config + results export | 6 | 2+1+2+1 (main=2, config=1, export=2, docs=1) |

**Distribution:**  
- VeryHigh (18-20): []  
- High (14-17): []  
- Medium (9-13): [A-2]  
- Low (4-8): [A-1, A-3, A-4, A-5]  
**Total Complexity:** 35 points (LIGHT tier confirmed)

---

## Dependencies

**External Libraries:**
- pandas (data manipulation)
- numpy (numerical operations)
- scipy (statistical tests)
- statsmodels (Fleiss kappa)
- matplotlib (visualization)

**Python Version:** ≥3.8  
**No GPU Required:** CPU-only statistical analysis  
**No Deep Learning Frameworks:** Pure statistical validation

---

## Data Flow

1. Load CSV → filter confidence ≥4 → validate completeness
2. Per benchmark: extract subset → calculate modal date
3. Per benchmark: compute agreement rate (±12 months)
4. Per benchmark: compute Fleiss kappa (year buckets)
5. Per benchmark: bootstrap CI (1000 iterations)
6. Per benchmark: permutation test (1000 iterations)
7. Aggregate results → export CSV/JSON/Markdown
8. Generate plots → save to results/plots/

---

## Key Design Decisions

**Why separate validators module?**  
Data quality checks (sample size, domain balance, date validity) are distinct from statistical metrics. Separation enables fail-fast validation before expensive bootstrap/permutation operations.

**Why statsmodels for Fleiss kappa?**  
Standard implementation. Alternative (manual calculation) requires N×K matrix construction and chance-agreement formula — error-prone for first implementation. Use stdlib when available.

**Why fixed 12-month window?**  
PRD specifies ±1 year tolerance. Hardcode for simplicity; config parameter if sensitivity analysis needed later (ponytail: fixed window, add config param if testing different thresholds).

---

## Validation Strategy

**Unit Tests:**
- `test_metrics.py`: validate modal date calculation, agreement rate edge cases (all agree, bimodal distribution)
- `test_validators.py`: sample size checks, date range validation

**Integration Test:**
- `example_survey.csv`: synthetic dataset with known modal date, expected agreement rate
- Run full pipeline → verify agreement_summary.csv matches expected values

**No test coverage target:**  
Core statistical functions only (6-8 tests total). Skip validators (trivial conditionals) unless bugs found.

---

## Performance Targets

| Operation | Target | Actual Hardware |
|-----------|--------|-----------------|
| CSV load (150 responses) | <5s | Single-core CPU |
| Agreement rate (all benchmarks) | <1s | Single-core CPU |
| Bootstrap CI (1000 iter) | <30s | Single-core CPU |
| Permutation test (1000 iter) | <30s | Single-core CPU |
| Total pipeline runtime | <5 min | Single-core CPU |

**No optimization required:**  
Survey data small (10-50 KB). Pandas vectorized operations sufficient.

---

## Gate Criteria Implementation

```python
def evaluate_gate(results: dict) -> Tuple[str, str]:
    """
    Gate logic from PRD Section 6.3.
    
    Returns: (gate_status, action)
        gate_status: "SATISFIED" | "FAILED" | "PARTIAL"
        action: next step description
    """
    passes = {}
    for benchmark in BENCHMARKS:
        r = results[benchmark]
        passes[benchmark] = (
            r["agreement_rate"] > 0.70 and
            r["n_high_conf"] >= 30 and
            r["fleiss_kappa"] > 0.60
        )
    
    if all(passes.values()):
        return "SATISFIED", "Proceed to H-M1/H-M2"
    elif all(r["agreement_rate"] < 0.50 for r in results.values()):
        return "FAILED", "PIVOT to citation-based validation"
    else:
        return "PARTIAL", "Use ImageNet consensus, citation fallback for weak benchmarks"
```

---

## Output Specification

**CSV Format (`agreement_summary.csv`):**
```
benchmark,n_total,n_high_conf,modal_date,agreement_rate,fleiss_kappa,ci_lower,ci_upper,p_value
ImageNet,50,42,2019-06,78.0,0.71,73.5,82.1,0.001
GLUE,48,38,2020-03,73.0,0.68,68.2,77.5,0.002
SQuAD,45,35,2019-10,75.0,0.69,69.8,79.8,0.001
```

**JSON Format (`agreement_summary.json`):**
```json
{
  "ImageNet": {
    "n_total": 50,
    "n_high_conf": 42,
    "modal_date": "2019-06",
    "agreement_rate": 78.0,
    "fleiss_kappa": 0.71,
    "ci_lower": 73.5,
    "ci_upper": 82.1,
    "p_value": 0.001
  }
}
```

**Markdown Summary (`agreement_summary.md`):**
```markdown
# Expert Consensus Validation Results

## Gate Status: SATISFIED

### ImageNet
- Agreement Rate: 78.0% (95% CI: 73.5%-82.1%)
- Fleiss' Kappa: 0.71 (substantial agreement)
- Modal Date: 2019-06
- Sample Size: 42 high-confidence responses

[... similar for GLUE, SQuAD ...]
```

---

## Error Handling

**Data Quality Failures:**
- Missing required fields → skip row, log warning
- Invalid date (outside 2017-2024) → skip row, log warning
- Sample size <30 → FAIL fast with error message

**Statistical Edge Cases:**
- All raters agree → κ=1.0 (handle division by zero in kappa formula)
- Bimodal distribution → select earliest mode, log warning
- Tie for modal date → select earliest date

**File I/O Errors:**
- CSV not found → clear error message with expected path
- Output directory missing → create automatically
- Permission denied → fail with actionable message

---

## Extension Points (Out of Scope)

**Not implemented (YAGNI):**
- Real-time survey monitoring dashboard
- Automated reminder emails
- Multi-language survey support
- Confidence-weighted agreement rate (alternative metric)
- Krippendorff's alpha (alternative to Fleiss kappa)
- Domain-stratified analysis (vision vs NLP separate)

**Add if needed later:**
- Domain stratification: split results by domain if imbalance detected
- Sensitivity analysis: test different window sizes (6, 12, 18 months)
- Citation-based validation fallback (separate module if gate fails)

---

**Architecture Status:** COMPLETE  
**Ready for Phase 4 (Coder):** YES  
**Total Epic Tasks:** 5  
**Estimated Implementation Effort:** ~14 hours (core code) + 2 hours (tests)
