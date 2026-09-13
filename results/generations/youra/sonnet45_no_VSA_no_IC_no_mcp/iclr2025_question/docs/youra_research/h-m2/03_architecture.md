# Architecture: H-M2 Bayesian Gate 2 Posterior Prediction

**Date:** 2026-08-25
**Hypothesis:** H-M2 (MECHANISM)
**Type:** Statistical Validation
**Applied:** scipy.stats Bayesian inference pattern

---

## Codebase Analysis (Serena)

**Project Type:** Green-field
**Status:** New implementation from scratch
**Analyzed Path:** N/A
**Findings:** No existing code. H-M1 has no code/ directory (validation results only).

---

## Module Structure

### DataLoader (`data_loader.py`)

**Dependencies:** pandas, pathlib

```python
class Gate2CorpusLoader:
    def __init__(self, h_m1_validation_path: str): ...
    def load(self) -> pd.DataFrame: ...
    def filter_gate2_data(self, df: pd.DataFrame) -> pd.DataFrame: ...
    def validate_sample_size(self, df: pd.DataFrame, min_samples: int = 10) -> bool: ...
```

### BayesianPredictor (`predictor.py`)

**Dependencies:** numpy

```python
class Gate1Predictor:
    def __init__(self, k: float = 1.000, prior_variance: float = 0.01): ...
    def predict(self, O_10: float) -> tuple[float, float]: ...

class Gate2BayesianPredictor:
    def __init__(self, k: float = 1.000, prior_var: float = 0.01, likelihood_var: float = 0.005): ...
    def predict(self, O_10: float, O_100: float) -> tuple[float, float]: ...
    def _gate1_prior(self, O_10: float) -> tuple[float, float]: ...
    def _bayesian_update(self, prior_mean: float, prior_var: float, 
                         likelihood_mean: float, likelihood_var: float) -> tuple[float, float]: ...
```

### ErrorAnalyzer (`error_analyzer.py`)

**Dependencies:** numpy, scipy.stats

```python
class ErrorAnalyzer:
    def compute_errors(self, predictions: np.ndarray, ground_truth: np.ndarray) -> np.ndarray: ...
    def compute_reduction(self, errors_g1: np.ndarray, errors_g2: np.ndarray) -> dict: ...
    def paired_ttest(self, errors_g1: np.ndarray, errors_g2: np.ndarray) -> dict: ...
```

### SuccessEvaluator (`evaluator.py`)

**Dependencies:** None

```python
class SuccessEvaluator:
    def __init__(self, reduction_threshold: float = 40.0, p_threshold: float = 0.05): ...
    def evaluate(self, mean_reduction: float, p_value: float) -> dict: ...
    def classify_result(self, reduction: float, p_value: float) -> str: ...
```

### Visualizer (`visualizer.py`)

**Dependencies:** matplotlib.pyplot, numpy, pathlib

```python
class Gate2Visualizer:
    def __init__(self, output_dir: str): ...
    def plot_error_reduction_histogram(self, reductions: np.ndarray): ...
    def plot_gate_comparison_scatter(self, O_full: np.ndarray, 
                                      pred_g1: np.ndarray, pred_g2: np.ndarray): ...
    def plot_paired_errors(self, errors_g1: np.ndarray, errors_g2: np.ndarray): ...
    def plot_boxplot_comparison(self, errors_g1: np.ndarray, errors_g2: np.ndarray, 
                                 p_value: float): ...
    def plot_metrics_comparison(self, target_reduction: float, actual_reduction: float,
                                target_pvalue: float, actual_pvalue: float): ...
```

### ValidationWriter (`validator.py`)

**Dependencies:** pathlib

```python
class ValidationWriter:
    def __init__(self, output_path: str): ...
    def write_results(self, sample_size: int, mean_reduction: float, p_value: float,
                     t_stat: float, dof: int, result: str, 
                     mean_error_g1: float, mean_error_g2: float): ...
```

### Main (`main.py`)

**Dependencies:** All above modules, argparse

```python
def run_validation(h_m1_path: str, output_dir: str, k: float = 1.000) -> dict: ...
def main(): ...
```

---

## File Organization

```
h-m2/code/
├── data_loader.py
├── predictor.py
├── error_analyzer.py
├── evaluator.py
├── visualizer.py
├── validator.py
├── main.py
└── requirements.txt
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| B-1 | Setup | Project structure + requirements.txt | 4 | 1+1+1+1 |
| B-2 | Data Loading | Implement Gate2CorpusLoader with filtering | 8 | 2+2+2+2 |
| B-3 | Gate 1 Predictor | Implement baseline predictor from H-M1 | 7 | 2+1+2+2 |
| B-4 | Gate 2 Predictor | Implement Bayesian update mechanism | 12 | 3+2+5+2 |
| B-5 | Error Analysis | Implement error computation + paired t-test | 11 | 3+3+3+2 |
| B-6 | Success Evaluation | Implement criteria checker | 6 | 2+1+2+1 |
| B-7 | Visualization | Implement 5 figures (histogram, scatter, paired, box, metrics) | 16 | 4+2+4+6 |
| B-8 | Validation | Implement ValidationWriter (04_validation.md) | 7 | 2+1+2+2 |
| B-9 | Main Pipeline | Implement main.py orchestration + CLI | 9 | 2+3+2+2 |
| B-10 | Testing | Run full validation + verify >40% reduction, p<0.05 | 10 | 2+2+3+3 |

**Distribution:** VeryHigh(18-20): [], High(14-17): [B-7], Medium(9-13): [B-4,B-5,B-9,B-10], Low(4-8): [B-1,B-2,B-3,B-6,B-8]

---

## Data Flow

1. `Gate2CorpusLoader.load()` → H-M1 validation data
2. `Gate2CorpusLoader.filter_gate2_data()` → hypotheses with O_100
3. `Gate2CorpusLoader.validate_sample_size()` → check n≥10
4. `Gate1Predictor.predict(O_10)` → (prior_mean, prior_var)
5. `Gate2BayesianPredictor.predict(O_10, O_100)` → (posterior_mean, posterior_var)
6. `ErrorAnalyzer.compute_errors()` → errors_g1, errors_g2
7. `ErrorAnalyzer.compute_reduction()` → mean_reduction, per-hypothesis reduction
8. `ErrorAnalyzer.paired_ttest()` → t_stat, p_value
9. `SuccessEvaluator.evaluate()` → PASS/PARTIAL/FAIL
10. `Gate2Visualizer.plot_*()` → 5 figures
11. `ValidationWriter.write_results()` → 04_validation.md

---

## Success Validation

**Primary Check:** mean_reduction > 40% AND p_value < 0.05 → PASS
**Secondary Check:** 20% ≤ reduction < 40% AND p < 0.05 → PARTIAL
**Failure:** reduction < 20% OR p ≥ 0.05 → FAIL

**Output:** 04_validation.md + 5 figures in h-m2/figures/

---

## Dependencies

```txt
scipy>=1.11.0
numpy>=1.24.0
pandas>=2.0.0
matplotlib>=3.7.0
```

---

**Lines:** 165 | **Modules:** 7 | **Tasks:** 10 | **Total Complexity:** 90
