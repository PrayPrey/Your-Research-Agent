# Logic Design: H-M3 Dose-Response Threshold Analysis

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - designing new APIs (analysis-only module, no prior code dependency)
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Dose-Response Analysis Module [Complexity: 3, Budget: 4]

**Applied**: statsmodels OLS for AIC/BIC model selection; numpy.polyder/roots for peak finding (per 02c experiment brief)

### API Signatures

```python
import numpy as np
import statsmodels.api as sm
from dataclasses import dataclass
from typing import Tuple, Dict

@dataclass
class DoseResponseResult:
    optimal_threshold: float          # percentile, e.g. 45.0
    optimal_score: float
    confidence_interval: Tuple[float, float]  # 95% CI, percentile units
    best_model: str                   # 'linear' | 'quadratic' | 'cubic'
    aic_values: Dict[str, float]
    bic_values: Dict[str, float]
    is_peak_internal: bool

def fit_polynomial_models(
    thresholds: np.ndarray,   # [10] float, e.g. [0,10,...,90]
    scores: np.ndarray,       # [10] mean ensemble score per threshold
) -> Dict[str, dict]:
    """Fit linear/quadratic/cubic OLS models. Returns {name: {coefficients, aic, bic, rsquared}}."""
    ...

def find_optimal_threshold(
    thresholds: np.ndarray,   # [10]
    scores: np.ndarray,       # [10]
    model_coeffs: np.ndarray, # [degree+1], highest power first (np.poly1d convention)
    degree: int,              # 1, 2, or 3
) -> Tuple[float, float, bool]:
    """Derivative-based peak search on normalized x=threshold/100. Returns (optimal_threshold, optimal_score, is_internal)."""
    ...

def compute_confidence_interval(
    thresholds: np.ndarray,      # [10]
    scores_matrix: np.ndarray,   # [10, 3] thresholds x seeds
    n_bootstrap: int = 1000,
) -> Tuple[float, float]:
    """Bootstrap seed resampling -> 95% CI of argmax threshold."""
    ...

def analyze_dose_response(
    sweep_results: Dict[float, dict],  # {threshold: {'scores': [s1,s2,s3]}}
) -> DoseResponseResult:
    """Full pipeline: fit -> select best (BIC) -> find peak -> bootstrap CI."""
    ...

def verify_optimal_balance_point(result: DoseResponseResult) -> bool:
    """Success = is_peak_internal AND best_model != 'linear' AND CI width <= 30."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| thresholds | (10,) | [0,10,...,90], normalized to x=thresholds/100 for fitting |
| scores_matrix | (10, 3) | 10 thresholds x 3 seeds, raw ensemble scores |
| mean_scores / std_scores | (10,) | `scores_matrix.mean(axis=1)` / `.std(axis=1)` |
| coefficients (degree d) | (d+1,) | `np.poly1d` convention, highest power first |
| X (design matrix, degree d) | (10, d+1) | `np.vander(x, d+1)` |

### Pseudo-code

```
fit_polynomial_models(thresholds, scores):
    x = thresholds / 100.0
    for degree, name in [(1,'linear'), (2,'quadratic'), (3,'cubic')]:
        X = np.vander(x, degree+1)
        model = sm.OLS(scores, X).fit()
        results[name] = {coefficients: model.params, aic: model.aic,
                          bic: model.bic, rsquared: model.rsquared}
    return results

find_optimal_threshold(thresholds, scores, coeffs, degree):
    x = thresholds / 100.0
    if degree == 1:
        idx = argmax(scores); return thresholds[idx], scores[idx], False
    poly = np.poly1d(coeffs)
    deriv = np.polyder(poly)
    critical = real_roots(deriv) filtered to [0, 1]
    if critical empty:
        idx = argmax(scores); return thresholds[idx], scores[idx], False
    candidates = [0] + critical + [1]
    values = poly(candidates)
    best = argmax(values)
    optimal_x = candidates[best]
    is_internal = 0.05 < optimal_x < 0.95
    return optimal_x*100, values[best], is_internal

compute_confidence_interval(thresholds, scores_matrix, n_bootstrap=1000):
    for _ in range(n_bootstrap):
        seed_idx = random_choice(n_seeds, n_seeds, replace=True)
        resampled_mean = scores_matrix[:, seed_idx].mean(axis=1)
        optimal_thresholds.append(thresholds[argmax(resampled_mean)])
    return percentile(optimal_thresholds, 2.5), percentile(optimal_thresholds, 97.5)

analyze_dose_response(sweep_results):
    thresholds = sorted(sweep_results.keys())
    scores_matrix = stack([sweep_results[t]['scores'] for t in thresholds])  # [10,3]
    mean_scores = scores_matrix.mean(axis=1)
    models = fit_polynomial_models(thresholds, mean_scores)
    best_name = argmin_bic(models)
    optimal_t, optimal_s, internal = find_optimal_threshold(
        thresholds, mean_scores, models[best_name].coefficients, degree_of(best_name))
    ci = compute_confidence_interval(thresholds, scores_matrix)
    return DoseResponseResult(optimal_t, optimal_s, ci, best_name,
                               aic={k: v.aic for k,v}, bic={k: v.bic for k,v}, internal)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | fit_polynomial_models | OLS fit degree 1-3, AIC/BIC/R2 via statsmodels |
| L-1-2 | find_optimal_threshold | np.polyder/roots peak search, boundary fallback |
| L-1-3 | compute_confidence_interval | Bootstrap over seed axis, 95% percentile CI |
| L-1-4 | analyze_dose_response + verify_optimal_balance_point | Pipeline glue + PRD success-criteria check |

---

## A-2: Data Loading & Visualization [Complexity: 2, Budget: 2]

**Applied**: Standard PyTorch/numpy IO, matplotlib for CI-band plot

### API Signatures

```python
def load_sweep_results(source_path: str) -> Dict[float, dict]:
    """Load H-E1/H-M2 sweep JSON, or synthesize mock data if unavailable.
    Returns {threshold: {'scores': [s1,s2,s3]}}."""
    ...

def plot_dose_response_curve(
    thresholds: np.ndarray,        # (10,)
    scores_matrix: np.ndarray,     # (10, 3)
    result: DoseResponseResult,
    save_path: str = "figures/dose_response_curve.png",
) -> None:
    """Scatter mean+-std, fitted polynomial curve, optimal point marker, CI shaded band."""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | load_sweep_results | Load existing JSON or generate synthetic fallback per PRD risk mitigation |
| L-2-2 | plot_dose_response_curve | Primary required figure with CI band and optimal marker |
