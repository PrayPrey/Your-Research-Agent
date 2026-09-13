# Logic Specifications: h-m3 Bootstrap CI Stability

**Date:** 2026-03-21
**Hypothesis ID:** h-m3 (MECHANISM - Analysis-Only)
**Version:** 1.0
**Phase:** 3 (Implementation Planning)
**Total Budget:** 8 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** API signatures verified from h-e1 implementation
**Analyzed Path:** `docs/youra_research/20260318_question/h-e1/code/`
**Relevant Symbols:** ExperimentConfig (dataclass), load_dataset, run_single_experiment, generate_variance_summary, check_gate_condition
**Key Findings:** h-e1 provides experiment_logs.csv with test accuracy data. Bootstrap analysis will reuse data loading patterns but replace model training with statistical resampling. Structure follows h-e1's modular pattern (config, data_loader, analysis, visualize, orchestrator).

---

## External Dependencies API (From h-e1 Code)

### Data Artifacts (From h-e1 Experiment Results)

Verified from actual h-e1 CSV structure:

```python
# From: h-e1/code/results/experiment_logs.csv (ACTUAL DATA)
# CSV Structure (verified):
#   Columns: dataset, architecture, seed, test_accuracy, device, error
#   Rows: 120 (4 conditions × 30 seeds)

# Data extraction:
import pandas as pd
df = pd.read_csv("../../h-e1/code/results/experiment_logs.csv")
condition_data = df[(df['dataset']=='mnist') & (df['architecture']=='1layer')]['test_accuracy'].values  # [30]
```

**Verified from**: `h-e1/code/results/experiment_logs.csv` (actual file)

---

## A-1: Configuration Setup [Complexity: 4, Budget: 1/8]

**Applied:** Python dataclass pattern

### API Signatures

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

@dataclass
class BootstrapConfig:
    """Bootstrap analysis configuration."""
    n_resamples: int = 1000
    confidence_level: float = 0.95
    ci_width_threshold_pct: float = 50.0
    random_seed: int = 42
    h_e1_results_path: str = "../../h-e1/code/results/experiment_logs.csv"
    results_dir: str = "./results"
    figures_dir: str = "./figures"
    conditions: List[str] = field(default_factory=lambda: [
        "1layer_mnist", "1layer_fashion_mnist",
        "2layer_mnist", "2layer_fashion_mnist"
    ])

    def __post_init__(self):
        """Ensure directories exist."""
        Path(self.results_dir).mkdir(parents=True, exist_ok=True)
        Path(self.figures_dir).mkdir(parents=True, exist_ok=True)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Config dataclass | Define BootstrapConfig with bootstrap parameters |

---

## A-2: Data Loading from h-e1 [Complexity: 8, Budget: 2/8]

**Applied:** pandas CSV loading

### API Signatures

```python
import pandas as pd
import numpy as np
from typing import Dict

def load_h_e1_test_accuracies(csv_path: str) -> Dict[str, np.ndarray]:
    """Load test accuracies from h-e1. Returns: {condition: [30]}"""
    ...

def validate_condition_data(data: Dict[str, np.ndarray], expected_samples: int = 30) -> None:
    """Validate shape, NaN/Inf, range [0, 100]."""
    ...

def extract_condition_data(df: pd.DataFrame, dataset: str, architecture: str) -> np.ndarray:
    """Extract 30 test accuracies. Returns: [30]"""
    ...
```

### Pseudo-code

```
1. df = pd.read_csv(csv_path)
2. For each (dataset, architecture):
   a. Filter: df[(df['dataset']==dataset) & (df['architecture']==architecture)]
   b. Extract: filtered['test_accuracy'].values
   c. Validate: shape==(30,), no NaN/Inf, range [0,100]
3. Return {condition: data}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | CSV loader | Load experiment_logs.csv with pandas |
| L-2-2 | Data validation | Check shape, NaN/Inf, range |

---

## A-3: Bootstrap Core Algorithm [Complexity: 12, Budget: 3/8]

**Applied:** Bootstrap percentile method

### API Signatures

```python
from typing import Tuple

def bootstrap_variance_ci(
    data: np.ndarray,
    n_resamples: int,
    confidence_level: float,
    random_seed: int
) -> Tuple[float, float, float, float]:
    """Bootstrap variance CI. data: [30] -> (var_point, ci_lower, ci_upper, ci_width_pct)"""
    ...

def compute_variance_point_estimate(bootstrap_samples: np.ndarray) -> float:
    """Mean of bootstrap distribution. [B] -> scalar"""
    ...

def compute_percentile_ci(bootstrap_samples: np.ndarray, confidence_level: float) -> Tuple[float, float]:
    """Percentile [2.5, 97.5]. [B] -> (lower, upper)"""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| data | (30,) | Original test accuracies |
| bootstrap_sample | (30,) | Single resample with replacement |
| variance_estimates | (1000,) | B bootstrap variances |

### Pseudo-code

```
1. np.random.seed(random_seed)
2. variance_estimates = []
3. For i in range(n_resamples):
   a. bootstrap_sample = np.random.choice(data, size=30, replace=True)
   b. variance_estimates.append(np.var(bootstrap_sample, ddof=1))
4. variance_point = np.mean(variance_estimates)
5. ci_lower = np.percentile(variance_estimates, 2.5)
6. ci_upper = np.percentile(variance_estimates, 97.5)
7. ci_width_pct = ((ci_upper - ci_lower) / variance_point) * 100
8. Return (variance_point, ci_lower, ci_upper, ci_width_pct)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Resample loop | Bootstrap resampling with replacement |
| L-3-2 | Variance computation | Compute variance with ddof=1 |
| L-3-3 | Percentile CI | Calculate [2.5, 97.5] percentile bounds |

---

## A-4: Multi-Condition Analysis [Complexity: 9, Budget: 2/8]

**Applied:** Iterative processing

### API Signatures

```python
def analyze_all_conditions(
    conditions_data: Dict[str, np.ndarray],
    config: BootstrapConfig
) -> Dict[str, Dict[str, float]]:
    """Run bootstrap for all 4 conditions. Returns: {condition: metrics}"""
    ...
```

### Pseudo-code

```
1. results = {}
2. For condition_name, data in conditions_data.items():
   a. variance_point, ci_lower, ci_upper, ci_width_pct = bootstrap_variance_ci(data, ...)
   b. results[condition_name] = {
         "variance_point": variance_point,
         "ci_lower": ci_lower,
         "ci_upper": ci_upper,
         "ci_width_pct": ci_width_pct,
         "n_samples": 30,
         "n_resamples": 1000
      }
3. Return results
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Multi-condition loop | Iterate over 4 conditions |
| L-4-2 | Progress logging | Log condition progress |

---

## A-5: Gate Validation Logic [Complexity: 7, Budget: 0/8]

**Applied:** Threshold checking pattern

### API Signatures

```python
from typing import Any

def check_ci_width_threshold(
    bootstrap_results: Dict[str, Dict[str, float]],
    threshold: float
) -> Dict[str, Any]:
    """Validate CI width ≤ threshold. Returns: gate result dict"""
    ...

def generate_gate_report(
    bootstrap_results: Dict[str, Dict[str, float]],
    gate_result: Dict[str, Any]
) -> str:
    """Generate text report."""
    ...
```

### Pseudo-code

```
1. For condition, metrics in bootstrap_results.items():
   a. passed = metrics['ci_width_pct'] <= threshold
2. all_passed = all(passed for each condition)
3. Return {
      "gate_type": "SHOULD_WORK",
      "threshold": threshold,
      "gate_result": "PASS" if all_passed else "FAIL",
      "details": {condition: {"ci_width_pct": ..., "passed": ...}}
   }
```

---

## A-6: Visualization [Complexity: 11, Budget: 0/8]

**Applied:** matplotlib subplots

### API Signatures

```python
def plot_bootstrap_distributions(conditions_data, bootstrap_results, config, save_path) -> None:
    """4 subplots: histograms with CI bounds."""
    ...

def plot_ci_width_comparison(bootstrap_results, threshold, save_path) -> None:
    """Bar chart: CI width % vs threshold."""
    ...

def plot_variance_vs_ci_width(bootstrap_results, save_path) -> None:
    """Scatter: variance vs CI width %."""
    ...
```

---

## A-7: Results Output [Complexity: 5, Budget: 0/8]

**Applied:** JSON serialization

### API Signatures

```python
def save_bootstrap_results(bootstrap_results: Dict, save_path: str) -> None:
    """Save bootstrap_results.json."""
    ...

def save_gate_result(gate_result: Dict, save_path: str) -> None:
    """Save gate_result.json."""
    ...
```

---

## A-8: Orchestration [Complexity: 6, Budget: 0/8]

**Applied:** Sequential pipeline pattern

### API Signatures

```python
def main() -> str:
    """Run full bootstrap analysis. Returns: 'PASS' or 'FAIL'"""
    ...
```

### Pseudo-code

```
1. config = BootstrapConfig()
2. conditions_data = load_h_e1_test_accuracies(config.h_e1_results_path)
3. validate_condition_data(conditions_data)
4. bootstrap_results = analyze_all_conditions(conditions_data, config)
5. gate_result = check_ci_width_threshold(bootstrap_results, config.ci_width_threshold_pct)
6. save_bootstrap_results(bootstrap_results, f"{config.results_dir}/bootstrap_results.json")
7. save_gate_result(gate_result, f"{config.results_dir}/gate_result.json")
8. plot_bootstrap_distributions(...)
9. plot_ci_width_comparison(...)
10. plot_variance_vs_ci_width(...)
11. print(generate_gate_report(bootstrap_results, gate_result))
12. Return gate_result['gate_result']
```

---

## Budget Summary

| Task | Complexity | Budget Allocated | Budget Used |
|------|------------|------------------|-------------|
| A-1: Configuration | 4 | 1 | 1 |
| A-2: Data Loading | 8 | 2 | 2 |
| A-3: Bootstrap Algorithm | 12 | 3 | 3 |
| A-4: Multi-Condition | 9 | 2 | 2 |
| A-5: Gate Validation | 7 | 0 | 0 |
| A-6: Visualization | 11 | 0 | 0 |
| A-7: Results Output | 5 | 0 | 0 |
| A-8: Orchestration | 6 | 0 | 0 |
| **Total** | **62** | **8** | **8** |

**Status:** Budget fully utilized (8/8). Tasks A-5 through A-8 have no allocated subtasks (implement with standard patterns).

---

## File Structure

```
code/
├── config.py              # BootstrapConfig dataclass
├── data_loader.py         # CSV loading and validation
├── bootstrap_analysis.py  # Core bootstrap algorithm
├── gate_validator.py      # CI width threshold checking
├── visualize.py           # 3 matplotlib figures
└── run_analysis.py        # Main orchestrator

results/
├── bootstrap_results.json
└── gate_result.json

figures/
├── bootstrap_distributions.png
├── ci_width_comparison.png
└── variance_vs_ci_width.png
```

---

## Statistical Implementation Details

### Bootstrap Percentile Method
- Resamples: B=1000
- CI Level: 95% (α=0.05)
- Percentiles: [2.5, 97.5]
- Variance Estimator: np.var(data, ddof=1)
- Point Estimate: Mean of bootstrap distribution

### CI Width Calculation
```python
ci_width_pct = ((ci_upper - ci_lower) / variance_point) * 100
```

### Reproducibility
- Fixed random seed: 42
- Deterministic resampling

---

## Validation Criteria

### Code Correctness
- Load 120 samples from h-e1 CSV (4 conditions × 30 seeds)
- Bootstrap produces 1000 variance estimates per condition
- Percentile CI at [2.5, 97.5]

### Gate Validation
- PASS: CI width ≤ 50% for ALL 4 conditions
- FAIL: Any condition > 50%

### Performance
- Runtime < 30 seconds (CPU-only)
- Memory < 100MB

### Outputs
- 2 JSON files in results/
- 3 PNG figures in figures/

---

## Expected Results (Preliminary h-e1 Data)

**Hypothesis Prediction:** CI width ≤ 50%

**Actual Expectation:**
- MNIST conditions: Mean variance ~0.01%, CI width ~80%
- Fashion-MNIST conditions: Mean variance ~0.35-0.59%, CI width ~80%

**Interpretation if FAIL:**
- N=30 provides estimates but high uncertainty
- Recommendation: Add N sensitivity analysis (N=50, 100, 200)

---

*Phase 3 Logic Design Complete*
*Next: Phase 4 (Implementation)*
