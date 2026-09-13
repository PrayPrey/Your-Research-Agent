# Logic Design: H-M2 Bayesian Gate 2 Prediction

**Date:** 2026-08-25
**Hypothesis:** H-M2 (MECHANISM)
**Type:** Statistical Validation
**Budget:** 7 subtasks (medium-complexity statistical analysis)

---

## Codebase Analysis (Serena)

**Project Type:** Green-field
**Status:** New implementation from scratch
**Analyzed Path:** N/A
**Relevant Symbols:** None - h-m1 has no code/ directory (validation results only)

---

## B-2: Data Loading [Complexity: 8, Budget: 2]

**Applied:** pandas.read_csv + dataframe filtering

### API Signatures

```python
from pathlib import Path
import pandas as pd

class Gate2CorpusLoader:
    """Load and filter Gate 2 corpus from H-M1 validation."""
    
    def __init__(self, h_m1_validation_path: str):
        """Initialize with path to H-M1 validation data."""
        self.path = Path(h_m1_validation_path)
    
    def load(self) -> pd.DataFrame:
        """Load H-M1 corpus. Returns df with columns: [hypothesis_id, type, O_10, O_100, O_full]"""
        return pd.read_csv(self.path)
    
    def filter_gate2_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter rows with non-null O_100. df: [N, 5] -> [M, 5] where M<=N"""
        return df[df["O_100"].notna()]
    
    def validate_sample_size(self, df: pd.DataFrame, min_samples: int = 10) -> bool:
        """Check if sample size >= min_samples."""
        return len(df) >= min_samples
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | load | Read CSV from h-m1 |
| L-2-2 | filter_gate2_data | Drop rows with null O_100 |

---

## B-3: Gate 1 Predictor [Complexity: 7, Budget: 1]

**Applied:** Linear scaling (y = k*x)

### API Signatures

```python
class Gate1Predictor:
    """Baseline predictor from H-M1 (linear extrapolation)."""
    
    def __init__(self, k: float = 1.000, prior_variance: float = 0.01):
        """Initialize with scaling factor k and prior uncertainty."""
        self.k = k
        self.prior_var = prior_variance
    
    def predict(self, O_10: float) -> tuple[float, float]:
        """Linear extrapolation. Returns (prior_mean, prior_variance)."""
        prior_mean = self.k * O_10
        return prior_mean, self.prior_var
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | predict | Linear scaling y = k*x |

---

## B-4: Gate 2 Predictor [Complexity: 12, Budget: 2]

**Applied:** scipy.stats Gaussian Bayesian update

### API Signatures

```python
import numpy as np

class Gate2BayesianPredictor:
    """Bayesian posterior predictor combining Gate 1 prior + Gate 2 likelihood."""
    
    def __init__(self, k: float = 1.000, prior_var: float = 0.01, likelihood_var: float = 0.005):
        """Initialize with scaling and variance parameters."""
        self.k = k
        self.prior_var = prior_var
        self.likelihood_var = likelihood_var
    
    def predict(self, O_10: float, O_100: float) -> tuple[float, float]:
        """
        Bayesian update combining prior and likelihood.
        Returns (posterior_mean, posterior_variance).
        """
        prior_mean, prior_var = self._gate1_prior(O_10)
        likelihood_mean = O_100 / self.k  # Inverse scaling
        
        posterior_mean, posterior_var = self._bayesian_update(
            prior_mean, prior_var,
            likelihood_mean, self.likelihood_var
        )
        return posterior_mean, posterior_var
    
    def _gate1_prior(self, O_10: float) -> tuple[float, float]:
        """Compute Gate 1 prior. Returns (prior_mean, prior_variance)."""
        return self.k * O_10, self.prior_var
    
    def _bayesian_update(
        self,
        prior_mean: float,
        prior_var: float,
        likelihood_mean: float,
        likelihood_var: float
    ) -> tuple[float, float]:
        """
        Gaussian-Gaussian conjugate update.
        posterior_var = 1 / (1/prior_var + 1/likelihood_var)
        posterior_mean = posterior_var * (prior_mean/prior_var + likelihood_mean/likelihood_var)
        """
        posterior_var = 1.0 / (1.0 / prior_var + 1.0 / likelihood_var)
        posterior_mean = posterior_var * (prior_mean / prior_var + likelihood_mean / likelihood_var)
        return posterior_mean, posterior_var
```

### Pseudo-code

```
1. Get Gate 1 prior: prior_mean = k * O_10, prior_var = 0.01
2. Get Gate 2 likelihood: likelihood_mean = O_100 / k, likelihood_var = 0.005
3. Bayesian update:
   a. posterior_var = 1 / (1/prior_var + 1/likelihood_var)
   b. posterior_mean = posterior_var * (prior_mean/prior_var + likelihood_mean/likelihood_var)
4. Return (posterior_mean, posterior_var)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | _gate1_prior | Compute prior distribution |
| L-4-2 | _bayesian_update | Gaussian conjugate update formula |

---

## B-5: Error Analysis [Complexity: 11, Budget: 2]

**Applied:** numpy array operations + scipy.stats.ttest_rel

### API Signatures

```python
import numpy as np
from scipy.stats import ttest_rel

class ErrorAnalyzer:
    """Compute prediction errors and statistical tests."""
    
    def compute_errors(
        self,
        predictions: np.ndarray,
        ground_truth: np.ndarray
    ) -> np.ndarray:
        """
        Relative error: |pred - truth| / truth.
        predictions: [N], ground_truth: [N] -> errors: [N]
        """
        return np.abs(predictions - ground_truth) / ground_truth
    
    def compute_reduction(
        self,
        errors_g1: np.ndarray,
        errors_g2: np.ndarray
    ) -> dict:
        """
        Error reduction percentage: (E_g1 - E_g2) / E_g1 * 100.
        Returns: {
            "mean_reduction": float,
            "per_hypothesis_reduction": np.ndarray [N]
        }
        """
        reduction_pct = (errors_g1 - errors_g2) / errors_g1 * 100
        return {
            "mean_reduction": float(np.mean(reduction_pct)),
            "per_hypothesis_reduction": reduction_pct
        }
    
    def paired_ttest(
        self,
        errors_g1: np.ndarray,
        errors_g2: np.ndarray
    ) -> dict:
        """
        Paired t-test comparing Gate 1 vs Gate 2 errors.
        Returns: {
            "t_statistic": float,
            "p_value": float,
            "dof": int
        }
        """
        t_stat, p_value = ttest_rel(errors_g1, errors_g2)
        return {
            "t_statistic": float(t_stat),
            "p_value": float(p_value),
            "dof": len(errors_g1) - 1
        }
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | compute_errors | Relative error formula |
| L-5-2 | paired_ttest | scipy.stats.ttest_rel wrapper |

---

## B-6: Success Evaluation [Complexity: 6, Budget: 0]

**Applied:** Threshold checks (no subtasks allocated - trivial)

### API Signatures

```python
class SuccessEvaluator:
    """Evaluate results against H-M2 success criteria."""
    
    def __init__(self, reduction_threshold: float = 40.0, p_threshold: float = 0.05):
        """Initialize with success thresholds."""
        self.reduction_threshold = reduction_threshold
        self.p_threshold = p_threshold
    
    def evaluate(self, mean_reduction: float, p_value: float) -> dict:
        """
        Classify result as PASS/PARTIAL/FAIL.
        Returns: {
            "result": str ("PASS" | "PARTIAL" | "FAIL"),
            "reduction_ok": bool,
            "significance_ok": bool
        }
        """
        reduction_ok = mean_reduction > self.reduction_threshold
        significance_ok = p_value < self.p_threshold
        
        if reduction_ok and significance_ok:
            result = "PASS"
        elif 20.0 <= mean_reduction < self.reduction_threshold and significance_ok:
            result = "PARTIAL"
        else:
            result = "FAIL"
        
        return {
            "result": result,
            "reduction_ok": reduction_ok,
            "significance_ok": significance_ok
        }
    
    def classify_result(self, reduction: float, p_value: float) -> str:
        """One-line classification helper."""
        return self.evaluate(reduction, p_value)["result"]
```

---

## Summary

**Budget Usage:** 7/7 subtasks
**Patterns Applied:**
- pandas for data loading/filtering
- scipy.stats Gaussian Bayesian inference
- scipy.stats.ttest_rel for paired t-test
- numpy array operations

**Key Design Decisions:**
1. `filter_gate2_data`: Drop null O_100 rows (pandas built-in)
2. `_bayesian_update`: Closed-form Gaussian-Gaussian conjugate (no MCMC needed)
3. `compute_errors`: Relative error (absolute error / ground truth)
4. `paired_ttest`: Direct scipy wrapper (paired samples from same hypotheses)
5. `evaluate`: Hard thresholds from PRD (>40%, p<0.05)

**Phase 4 Integration:**
- All signatures use stdlib types (float, dict, tuple)
- numpy arrays for vectorized operations
- No custom data structures
- Direct imports from scipy/pandas
