# Logic Specification: H-M1

**Date:** 2026-08-19
**Hypothesis:** Observed coupling persists when controlling for instance difficulty (partial phi ≥ 0.25)
**Type:** MECHANISM
**Budget:** 2 subtasks allocated

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** API signatures verified from h-e1 actual code
**Analyzed Path:** docs/youra_research/h-e1_code/src/
**Relevant Symbols:** CouplingAnalyzer.compute_phi_coefficient, load_multitrust, extract_binary_labels
**Note:** h-e1 provides coupling data generation and phi computation. h-m1 adds difficulty control layer.

---

## M-1: Difficulty Generation [Complexity: 7, Budget: 1]

**Applied:** Standard numpy random generation + scipy.stats correlation

### API Signatures

```python
# src/difficulty_generator.py

def generate_difficulty_scores(n_samples: int, seed: int = 42) -> np.ndarray:
    """Generate instance difficulty scores independent of dimension labels.
    
    Returns: [n_samples] float array in [0, 1], Normal(0.5, 0.15) clipped
    """

def validate_independence(
    difficulty: np.ndarray,
    dimension_labels: dict[str, np.ndarray],
    threshold: float = 0.2
) -> bool:
    """Validate difficulty is independent of all dimension labels.
    
    Args:
        difficulty: [N] difficulty scores
        dimension_labels: {dimension: [N] binary array}
        threshold: Max allowed |correlation|
    
    Returns: True if all |corr(difficulty, dim)| < threshold
    """
```

### Pseudo-code

```
1. generate_difficulty_scores:
   - scores = np.random.normal(0.5, 0.15, n_samples)
   - return np.clip(scores, 0, 1)

2. validate_independence:
   - For each dimension in dimension_labels:
       corr = scipy.stats.pearsonr(difficulty, labels)
       if |corr| >= threshold: return False
   - return True
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M1-1 | Independence Validation | Correlation check for all 5 dimensions |

---

## M-2: Partial Correlation [Complexity: 9, Budget: 1]

**Applied:** pingouin.partial_corr for partial phi coefficient

### API Signatures

```python
# src/partial_correlation.py

def compute_partial_correlation(
    df: pd.DataFrame,
    dim1: str,
    dim2: str,
    covar: str = 'difficulty_score'
) -> tuple[float, float, tuple[float, float]]:
    """Compute partial correlation controlling for difficulty.
    
    Args:
        df: DataFrame with binary dimension columns + difficulty_score
        dim1, dim2: Dimension names
        covar: Covariate column name
    
    Returns: (partial_r, p_value, (ci_lower, ci_upper))
    """

def analyze_all_pairs(
    df: pd.DataFrame,
    dimension_pairs: list[tuple[str, str]]
) -> pd.DataFrame:
    """Compute partial correlation for all dimension pairs.
    
    Args:
        df: DataFrame with all dimensions + difficulty_score
        dimension_pairs: List of (dim1, dim2) tuples (6 pairs from h-e1)
    
    Returns: DataFrame with columns [dim1, dim2, partial_r, p_value, ci_lower, ci_upper]
    """
```

### Pseudo-code

```
1. compute_partial_correlation:
   - result = pingouin.partial_corr(data=df, x=dim1, y=dim2, covar=covar)
   - return (result['r'], result['p-val'], (result['CI95%'][0], result['CI95%'][1]))

2. analyze_all_pairs:
   - results = []
   - For (dim1, dim2) in dimension_pairs:
       partial_r, p, ci = compute_partial_correlation(df, dim1, dim2)
       results.append({dim1, dim2, partial_r, p, ci[0], ci[1]})
   - return pd.DataFrame(results)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M2-1 | Pingouin Integration | Wrapper for 6 dimension pairs |

---

## M-3: Stratified Analysis [Complexity: 10, Budget: 0]

**Applied:** pandas.qcut + scipy.stats.chi2_contingency

### API Signatures

```python
# src/stratified_analyzer.py

def bin_by_quartiles(
    df: pd.DataFrame,
    difficulty_col: str = 'difficulty_score',
    n_quartiles: int = 4
) -> pd.DataFrame:
    """Bin instances into difficulty quartiles.
    
    Returns: df with added 'quartile' column (values: 0, 1, 2, 3)
    """

def compute_quartile_phi(
    df: pd.DataFrame,
    dim1: str,
    dim2: str,
    quartile_col: str = 'quartile'
) -> pd.DataFrame:
    """Compute phi coefficient within each quartile.
    
    Returns: DataFrame with columns [quartile, phi, p_value, n_samples]
    """

def validate_persistence(
    quartile_results: pd.DataFrame,
    threshold: float = 0.25,
    min_quartiles: int = 3
) -> bool:
    """Check if coupling persists across quartiles.
    
    Returns: True if phi >= threshold in >= min_quartiles quartiles
    """
```

---

## M-4: Dual Validation [Complexity: 6, Budget: 0]

**Applied:** Simple comparison logic

### API Signatures

```python
# src/stratified_analyzer.py

def compare_validation_methods(
    partial_results: pd.DataFrame,
    quartile_results: pd.DataFrame,
    threshold: float = 0.25
) -> dict:
    """Compare partial correlation vs stratified results.
    
    Returns: {
        'agreement': list of (dim1, dim2) pairs where both methods agree,
        'partial_only': pairs passing partial threshold only,
        'quartile_only': pairs passing quartile persistence only
    }
    """
```

---

## M-5: Visualization [Complexity: 8, Budget: 0]

**Applied:** matplotlib + seaborn standard plotting

### API Signatures

```python
# src/visualization.py

def plot_partial_vs_raw_phi(
    partial_results: pd.DataFrame,
    raw_phi: dict,
    output_path: str
):
    """Scatter plot comparing raw vs partial phi coefficients."""

def plot_quartile_stratified_phi(
    quartile_results: pd.DataFrame,
    output_path: str
):
    """Line plot showing phi across quartiles for each dimension pair."""

def plot_difficulty_independence(
    df: pd.DataFrame,
    dimensions: list[str],
    output_path: str
):
    """Correlation heatmap: difficulty vs dimension labels."""

def plot_effect_size_retention(
    partial_results: pd.DataFrame,
    raw_phi: dict,
    output_path: str
):
    """Bar plot: effect size retention after difficulty control."""
```

---

## M-6: Integration [Complexity: 8, Budget: 0]

**Applied:** Standard Python script orchestration

### API Signatures

```python
# scripts/run_experiment.py

def main():
    """Execute difficulty-controlled coupling analysis.
    
    Pipeline:
        1. Load h-e1 coupling data via load_multitrust()
        2. Generate difficulty scores (independent)
        3. Validate difficulty independence
        4. Compute partial correlations (6 pairs)
        5. Run stratified quartile analysis
        6. Dual validation comparison
        7. Generate 4 visualizations
        8. Save results + gate evaluation
    """
```

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

The following APIs are called from h-e1 code. Signatures verified from actual implementation:

```python
# From: docs/youra_research/h-e1_code/src/data_loader.py
def load_multitrust(samples: int = 500, seed: int = 42) -> pd.DataFrame:
    """Generate synthetic trustworthiness failure data with known coupling.
    
    Returns: DataFrame with columns [prompt, truthfulness, robustness, 
             fairness, safety, privacy]
    """

def extract_binary_labels(
    df: pd.DataFrame,
    dimensions: list[str]
) -> dict[str, np.ndarray]:
    """Extract binary labels from synthetic data.
    
    Returns: {dimension: [N] binary array (1=fail, 0=pass)}
    """

# From: docs/youra_research/h-e1_code/src/coupling_analyzer.py
class CouplingAnalyzer:
    def __init__(self, dimensions: list[str]):
        """Initialize with dimension names."""
    
    def compute_phi_coefficient(
        self,
        labels_d1: np.ndarray,
        labels_d2: np.ndarray
    ) -> tuple[float, float]:
        """Compute phi coefficient and p-value for dimension pair.
        
        Returns: (phi_coefficient, p_value)
        """
```

**Verified from:** docs/youra_research/h-e1_code/src/ (actual implementation)

---

## Notes

- **MECHANISM:** Statistical validation, no API calls (fast runtime)
- **Budget:** 2 subtasks allocated to M-1 and M-2 (highest complexity)
- **Data Flow:** h-e1 data → add difficulty → partial corr + quartile analysis → dual validation
- **Key Library:** pingouin.partial_corr for difficulty-controlled phi

---

**Subtasks:** 2/2 used (M-1: 1, M-2: 1)
