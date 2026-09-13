# System Architecture: h-m3 Bootstrap CI Stability

**Date:** 2026-03-21
**Hypothesis ID:** h-m3 (MECHANISM - Analysis-Only)
**Version:** 1.0
**Phase:** 3 (Implementation Planning)

Applied: Statistical analysis modular pattern, Bootstrap resampling standard

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Patterns found from h-e1 implementation
**Analyzed Path:** `docs/youra_research/20260318_question/h-e1/code/`
**Findings:** h-e1 provides experiment_logs.csv with test accuracy data. Bootstrap analysis will reuse data loading patterns but replace model training with statistical resampling. Structure follows h-e1's modular pattern (config, data_loader, analysis, visualize, orchestrator).

---

## Project Context

**Hypothesis Type:** MECHANISM (Analysis-Only)
**Goal:** Validate N=30 sample size provides stable variance estimation via bootstrap CI width ≤ 50%
**Total Analysis:** 4 conditions × 1000 bootstrap resamples = 4000 variance estimates
**Gate:** SHOULD_WORK (failure → add N sensitivity analysis to exploration phase)
**Prerequisites:** h-e1 (PASSED), h-m1 (PASSED), h-m2 (PASSED)

---

## Architecture Overview

### Design Philosophy
- Pure statistical analysis (no model training)
- Reuse h-e1 test accuracy artifacts
- Bootstrap percentile method for CI estimation
- CPU-only execution (<30 seconds runtime)

### Module Structure
```
code/
├── config.py              # Analysis parameters (B=1000, CI=95%)
├── data_loader.py         # Load h-e1 test accuracies
├── bootstrap_analysis.py  # Core bootstrap variance CI estimation
├── gate_validator.py      # CI width threshold validation
├── visualize.py           # Bootstrap distributions + CI width plots
└── run_analysis.py        # Orchestrator

results/
├── bootstrap_results.json
└── gate_result.json

figures/
├── bootstrap_distributions.png  (4 subplots with CI bounds)
├── ci_width_comparison.png      (bar chart vs 50% threshold)
└── variance_vs_ci_width.png     (scatter plot)
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From h-e1 Artifacts)

| Artifact | File Location | Expected Format |
|----------|---------------|-----------------|
| Test Accuracies | `h-e1/code/results/experiment_logs.csv` | CSV with columns: dataset, architecture, seed, test_accuracy |
| Variance Summary | `h-e1/code/results/variance_summary.json` | Reference for original variance estimates |

**Verified from:** h-e1 experiment logs (120 runs completed)

**Data Extraction:**
```python
# Load from h-e1 CSV logs
import pandas as pd
df = pd.read_csv("../../h-e1/code/results/experiment_logs.csv")

# Extract 4 condition arrays (30 samples each)
conditions = {
    "1layer_mnist": df[(df['dataset']=='mnist') & (df['architecture']=='1layer')]['test_accuracy'].values,
    "1layer_fashion_mnist": df[(df['dataset']=='fashion_mnist') & (df['architecture']=='1layer')]['test_accuracy'].values,
    "2layer_mnist": df[(df['dataset']=='mnist') & (df['architecture']=='2layer')]['test_accuracy'].values,
    "2layer_fashion_mnist": df[(df['dataset']=='fashion_mnist') & (df['architecture']=='2layer')]['test_accuracy'].values
}
```

---

## Module Specifications

### ConfigModule (`code/config.py`)

**Dependencies:** None

```python
@dataclass
class BootstrapConfig:
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
```

### DataLoaderModule (`code/data_loader.py`)

**Dependencies:** ConfigModule

```python
def load_h_e1_test_accuracies(csv_path: str) -> Dict[str, np.ndarray]:
    """Load test accuracy data from h-e1 experiment logs."""
    ...

def validate_data(data: Dict[str, np.ndarray], expected_samples: int = 30) -> None:
    """Validate data shape, check for NaN/Inf, verify range [0, 100]."""
    ...

def extract_condition_data(df: pd.DataFrame, dataset: str, architecture: str) -> np.ndarray:
    """Extract 30 test accuracies for one condition."""
    ...
```

### BootstrapAnalysisModule (`code/bootstrap_analysis.py`)

**Dependencies:** None

```python
def bootstrap_variance_ci(
    data: np.ndarray,
    n_resamples: int,
    confidence_level: float,
    random_seed: int
) -> Tuple[float, float, float, float]:
    """
    Bootstrap variance estimation with percentile CI.

    Returns:
        (variance_point, ci_lower, ci_upper, ci_width_pct)
    """
    ...

def compute_variance_point_estimate(bootstrap_samples: np.ndarray) -> float:
    """Mean of bootstrap variance distribution."""
    ...

def compute_percentile_ci(
    bootstrap_samples: np.ndarray,
    confidence_level: float
) -> Tuple[float, float]:
    """95% CI using [2.5, 97.5] percentiles."""
    ...

def analyze_all_conditions(
    conditions_data: Dict[str, np.ndarray],
    config: BootstrapConfig
) -> Dict[str, Dict[str, float]]:
    """Run bootstrap analysis for all 4 conditions."""
    ...
```

### GateValidatorModule (`code/gate_validator.py`)

**Dependencies:** BootstrapAnalysisModule

```python
def check_ci_width_threshold(
    bootstrap_results: Dict[str, Dict[str, float]],
    threshold: float
) -> Dict[str, Any]:
    """Validate CI width ≤ 50% for all conditions."""
    ...

def generate_gate_report(
    bootstrap_results: Dict[str, Dict[str, float]],
    gate_result: Dict[str, Any]
) -> str:
    """Generate text report for gate validation."""
    ...
```

### VisualizeModule (`code/visualize.py`)

**Dependencies:** BootstrapAnalysisModule, GateValidatorModule

```python
def plot_bootstrap_distributions(
    conditions_data: Dict[str, np.ndarray],
    bootstrap_results: Dict[str, Dict[str, float]],
    save_path: str
) -> None:
    """4 subplots: histograms with CI bounds and threshold marker."""
    ...

def plot_ci_width_comparison(
    bootstrap_results: Dict[str, Dict[str, float]],
    threshold: float,
    save_path: str
) -> None:
    """Bar chart: CI width % vs 50% threshold (color-coded pass/fail)."""
    ...

def plot_variance_vs_ci_width(
    bootstrap_results: Dict[str, Dict[str, float]],
    save_path: str
) -> None:
    """Scatter: variance point estimate vs CI width %."""
    ...
```

### OrchestratorModule (`code/run_analysis.py`)

**Dependencies:** All modules

```python
def main() -> None:
    """
    1. Load config
    2. Load h-e1 test accuracy data
    3. Run bootstrap analysis (4 conditions)
    4. Validate gate condition
    5. Generate visualizations
    6. Save results
    """
    ...

def save_results(
    bootstrap_results: Dict,
    gate_result: Dict,
    config: BootstrapConfig
) -> None:
    """Save bootstrap_results.json and gate_result.json."""
    ...
```

---

## Data Flow

```
1. Config Loading → BootstrapConfig
2. Data Loading → Load h-e1 CSV → Extract 4 conditions (30 samples each)
3. For each condition:
   a. Initialize random seed
   b. Run 1000 bootstrap resamples
   c. Compute variance on each resample
   d. Calculate percentile CI [2.5, 97.5]
   e. Compute CI width percentage
4. Gate Validation → Check CI width ≤ 50% for all 4
5. Visualization → 3 figures
6. Save Results → JSON files
```

---

## Implementation Details

### Bootstrap Algorithm (Percentile Method)

```python
def bootstrap_variance_ci(data, n_resamples, confidence_level, random_seed):
    np.random.seed(random_seed)
    n = len(data)
    variance_estimates = []

    # Resample with replacement
    for _ in range(n_resamples):
        bootstrap_sample = np.random.choice(data, size=n, replace=True)
        variance_estimates.append(np.var(bootstrap_sample, ddof=1))

    variance_estimates = np.array(variance_estimates)

    # Point estimate: mean of bootstrap distribution
    variance_point = np.mean(variance_estimates)

    # Percentile CI
    alpha = 1 - confidence_level
    ci_lower = np.percentile(variance_estimates, (alpha/2) * 100)
    ci_upper = np.percentile(variance_estimates, (confidence_level + alpha/2) * 100)

    # CI width as % of point estimate
    ci_width_pct = ((ci_upper - ci_lower) / variance_point) * 100

    return variance_point, ci_lower, ci_upper, ci_width_pct
```

### Gate Validation Logic

```python
def check_ci_width_threshold(bootstrap_results, threshold):
    conditions_passed = []

    for condition, metrics in bootstrap_results.items():
        passed = metrics['ci_width_pct'] <= threshold
        conditions_passed.append((condition, passed))

    all_passed = all([p for _, p in conditions_passed])

    return {
        "gate_type": "SHOULD_WORK",
        "threshold": threshold,
        "all_conditions_passed": all_passed,
        "gate_result": "PASS" if all_passed else "FAIL",
        "details": {c: {"ci_width_pct": bootstrap_results[c]['ci_width_pct'],
                        "passed": p}
                   for c, p in conditions_passed}
    }
```

### Statistical Parameters

**Bootstrap Resamples:** B=1000 (standard from literature)
**Confidence Level:** 95% (α=0.05)
**CI Method:** Percentile [2.5, 97.5]
**Variance Estimator:** Sample variance (ddof=1, Bessel's correction)
**Random Seed:** 42 (for reproducibility)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Configuration Setup | Config dataclass for bootstrap parameters and paths | 4 | Module(1)+Dep(1)+Algo(1)+Int(1) |
| A-2 | Data Loading from h-e1 | CSV parser, extract 4 conditions, validate 30 samples | 8 | Module(2)+Dep(2)+Algo(2)+Int(2) |
| A-3 | Bootstrap Core Algorithm | Resample loop, variance computation, percentile CI | 12 | Module(3)+Dep(2)+Algo(4)+Int(3) |
| A-4 | Multi-Condition Analysis | Orchestrate bootstrap for 4 conditions with progress logging | 9 | Module(2)+Dep(3)+Algo(2)+Int(2) |
| A-5 | Gate Validation Logic | CI width threshold check, generate gate report | 7 | Module(2)+Dep(2)+Algo(2)+Int(1) |
| A-6 | Visualization | 3 figures: distributions, CI width bar chart, scatter plot | 11 | Module(3)+Dep(3)+Algo(2)+Int(3) |
| A-7 | Results Output | Save bootstrap_results.json and gate_result.json | 5 | Module(2)+Dep(1)+Algo(1)+Int(1) |
| A-8 | Orchestration | Main script to execute full analysis pipeline | 6 | Module(2)+Dep(2)+Algo(1)+Int(1) |

**Distribution:**
- VeryHigh(18-20): []
- High(14-17): []
- Medium(9-13): [A-3, A-4, A-6]
- Low(4-8): [A-1, A-2, A-5, A-7, A-8]

**Total Complexity:** 62 points across 8 tasks

---

## File Specifications

### results/bootstrap_results.json
```json
{
  "1layer_mnist": {
    "variance_point": 0.00995,
    "ci_lower": 0.00620,
    "ci_upper": 0.01410,
    "ci_width_pct": 79.40,
    "n_samples": 30,
    "n_resamples": 1000
  },
  "1layer_fashion_mnist": {
    "variance_point": 0.3468,
    "ci_lower": 0.2180,
    "ci_upper": 0.5023,
    "ci_width_pct": 81.97,
    "n_samples": 30,
    "n_resamples": 1000
  },
  "2layer_mnist": {
    "variance_point": 0.00940,
    "ci_lower": 0.00589,
    "ci_upper": 0.01335,
    "ci_width_pct": 79.36,
    "n_samples": 30,
    "n_resamples": 1000
  },
  "2layer_fashion_mnist": {
    "variance_point": 0.5918,
    "ci_lower": 0.3735,
    "ci_upper": 0.8578,
    "ci_width_pct": 81.81,
    "n_samples": 30,
    "n_resamples": 1000
  }
}
```

### results/gate_result.json
```json
{
  "gate_type": "SHOULD_WORK",
  "threshold": 50.0,
  "all_conditions_passed": false,
  "gate_result": "FAIL",
  "details": {
    "1layer_mnist": {
      "ci_width_pct": 79.40,
      "passed": false
    },
    "1layer_fashion_mnist": {
      "ci_width_pct": 81.97,
      "passed": false
    },
    "2layer_mnist": {
      "ci_width_pct": 79.36,
      "passed": false
    },
    "2layer_fashion_mnist": {
      "ci_width_pct": 81.81,
      "passed": false
    }
  },
  "recommendation": "N=30 insufficient for stable variance estimation. Add N sensitivity analysis (N=50, 100, 200) to exploration phase."
}
```

---

## Validation Criteria

**Code Correctness:**
- Load all 120 samples from h-e1 CSV (4 conditions × 30 samples)
- Bootstrap resampling produces 1000 variance estimates per condition
- Percentile CI computed correctly ([2.5, 97.5] percentiles)

**Gate Validation:**
- CI width ≤ 50% for ALL 4 conditions → PASS
- Any condition CI width > 50% → FAIL (add N sensitivity to exploration)

**Performance:**
- Total analysis completes in <30 seconds (CPU-only)
- Memory usage <100MB

**Outputs:**
- 2 JSON files in results/
- 3 PNG figures in figures/
- All metrics present in bootstrap_results.json

---

## Risk Mitigation

**R-1: Gate Failure Risk (High Probability)**
- Expectation: N=30 may be insufficient (CI width ~80% based on preliminary h-e1 data)
- Mitigation: Gate is SHOULD_WORK (not MUST_WORK), failure triggers N sensitivity exploration
- Action on Failure: Add hypothesis h-m3b for N=50, 100, 200 sensitivity analysis

**R-2: Data Availability**
- Dependency: h-e1 must be COMPLETED with all 120 runs
- Mitigation: Verify experiment_logs.csv exists before starting analysis
- Validation: Check CSV has exactly 120 rows

**R-3: Bootstrap Reproducibility**
- Risk: Non-deterministic resampling across runs
- Mitigation: Fixed random seed (42) for numpy.random
- Validation: Re-run analysis, verify identical CI bounds

---

## Dependencies

**Python Libraries:**
- numpy >= 1.20.0 (bootstrap resampling)
- scipy >= 1.7.0 (optional: scipy.stats.bootstrap as alternative)
- matplotlib >= 3.4.0 (visualization)
- pandas >= 1.3.0 (CSV loading)

**System:**
- Python >= 3.8
- CPU-only (no GPU needed)

**Data Dependencies:**
- h-e1 experiment_logs.csv (120 rows, 6 columns)
- Expected columns: dataset, architecture, seed, test_accuracy, device, error

**Environment:**
- No CUDA requirements
- No special environment variables

---

## Expected Results (Based on Preliminary h-e1 Data)

**Hypothesis Prediction:** CI width ≤ 50% for all conditions
**Actual Expectation (from h-e1 variance values):**
- MNIST conditions (low variance ~0.01%): CI width ~80%
- Fashion-MNIST conditions (high variance ~0.35-0.59%): CI width ~80%

**Interpretation:**
- N=30 provides variance estimates, but CI width ~80% indicates high uncertainty
- Rajput 2023 criterion (N≥30 for power 0.85) may not apply to neural network training variance
- Failure expected → triggers N sensitivity analysis (h-m3b)

---

**Architecture Complexity:** LOW (Analysis-Only, No Training)
**Total Epic Tasks:** 8
**Expected Implementation Time:** Phase 4 (0.5 days for analysis code + <1 minute runtime)
**Next Phase:** Phase 4 (Coding and Analysis Execution)
