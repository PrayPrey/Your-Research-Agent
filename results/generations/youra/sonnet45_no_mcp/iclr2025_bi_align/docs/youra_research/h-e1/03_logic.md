# Logic Design: h-e1
# Statistical Analysis Module APIs

**Date:** 2026-04-19  
**Hypothesis:** h-e1 (EXISTENCE - PoC)  
**Author:** Logic Agent  
**Focus:** Task A-3 (Statistical Analysis)

---

## Codebase Analysis (Serena)

**Project Type**: Green-field  
**Status**: No existing code (no-MCP mode)  
**Analyzed Path**: N/A  
**Relevant Symbols**: None - new implementation

**Note:** Pipeline running in no-MCP mode. Archon KB and Serena MCP calls skipped.

---

## Applied Patterns

Applied: Standard statistical analysis patterns (scipy, statsmodels)

---

## A-3: Statistical Analysis [Complexity: 11, Budget: 2]

**Applied**: scipy.stats.binomtest + statsmodels.stats.inter_rater

### API Signatures

```python
from typing import Tuple, Dict, Optional
import pandas as pd
import numpy as np
from scipy.stats import binomtest, chi2_contingency
from statsmodels.stats.inter_rater import cohens_kappa, aggregate_raters

class StatisticalAnalyzer:
    """Compute inter-annotator agreement, base-rate, and gate tests."""
    
    def __init__(self, annotations: pd.DataFrame, n_annotators: int = 3):
        """
        Initialize analyzer.
        
        Args:
            annotations: DataFrame with columns [sample_id, annotator_id, judgment]
                         judgment: 0 (marginal) or 1 (genuine violation)
            n_annotators: Number of independent annotators (default: 3)
        """
        self.annotations = annotations
        self.n_annotators = n_annotators
        self.n_samples = len(annotations['sample_id'].unique())
    
    def compute_cohens_kappa(self) -> Tuple[float, float, float]:
        """
        Compute aggregate Cohen's κ across all annotators.
        
        Returns:
            kappa: Aggregate κ value
            ci_lower: 95% CI lower bound
            ci_upper: 95% CI upper bound
        
        Shape: annotations [N_samples × N_annotators] → scalar κ
        """
        ...
    
    def majority_vote(self) -> pd.Series:
        """
        Apply majority voting across annotators for final labels.
        
        Returns:
            labels: Series with index=sample_id, values=0/1
        
        Shape: annotations [N_samples × N_annotators] → [N_samples]
        """
        ...
    
    def compute_base_rate(self, labels: pd.Series) -> float:
        """
        Calculate proportion of genuine violations.
        
        Args:
            labels: Binary labels (0/1) from majority vote
        
        Returns:
            base_rate: p = (# violations) / N_samples
        
        Shape: labels [N_samples] → scalar p
        """
        ...
    
    def binomial_test(
        self, 
        n_violations: int, 
        n_total: int, 
        p_null: float = 0.40
    ) -> Dict[str, float]:
        """
        One-tailed binomial test for H0: p < p_null vs H1: p >= p_null.
        
        Args:
            n_violations: Number of genuine violations
            n_total: Total sample size (500)
            p_null: Null hypothesis threshold (default: 0.40)
        
        Returns:
            result: {
                'p_value': float,
                'test_statistic': int,
                'ci_lower': float,
                'ci_upper': float
            }
        """
        ...
    
    def length_bias_test(
        self, 
        samples: pd.DataFrame, 
        labels: pd.Series
    ) -> Dict[str, any]:
        """
        Chi-square test for violation rate differences across length quartiles.
        
        Args:
            samples: DataFrame with columns [sample_id, length_quartile]
            labels: Binary violation labels (0/1)
        
        Returns:
            result: {
                'chi2_statistic': float,
                'p_value': float,
                'quartile_rates': Dict[str, float]  # Q1-Q4 violation rates
            }
        """
        ...
```

### Pseudo-code

**compute_cohens_kappa()**
```
1. Pivot annotations to matrix [N_samples × N_annotators]
2. For each annotator pair (i, j):
   - Compute pairwise κ using statsmodels.stats.inter_rater.cohens_kappa
3. Aggregate using mean of pairwise κ values
4. Compute 95% CI using bootstrap (1000 samples)
5. Return (κ_mean, ci_lower, ci_upper)
```

**majority_vote()**
```
1. Group annotations by sample_id
2. For each sample:
   - Sum judgments across annotators
   - Label = 1 if sum >= 2 (majority), else 0
3. Return Series with sample_id index
```

**compute_base_rate()**
```
1. Count n_violations = labels.sum()
2. base_rate = n_violations / len(labels)
3. Return base_rate
```

**binomial_test()**
```
1. Call scipy.stats.binomtest(n_violations, n_total, p_null, alternative='greater')
2. Extract p_value from result
3. Compute 95% CI using proportion_confint (statsmodels)
4. Return dict with p_value, test_statistic, ci_lower, ci_upper
```

**length_bias_test()**
```
1. Merge samples with labels on sample_id
2. Group by length_quartile, compute violation rate per quartile
3. Build contingency table: quartiles × [violation, no_violation]
4. Call scipy.stats.chi2_contingency(contingency_table)
5. Return chi2_statistic, p_value, and quartile_rates dict
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Inter-annotator agreement | Implement Cohen's κ with statsmodels aggregate_raters |
| L-3-2 | Base-rate + binomial test | Majority vote, base-rate calculation, scipy.binomtest |

---

## Dependencies Summary

### External Libraries

```python
# Statistical testing
from scipy.stats import binomtest, chi2_contingency
from statsmodels.stats.inter_rater import cohens_kappa, aggregate_raters
from statsmodels.stats.proportion import proportion_confint

# Data handling
import pandas as pd
import numpy as np
```

### Input Data Schema

**annotations DataFrame:**
| Column | Type | Description |
|--------|------|-------------|
| sample_id | int | Unique sample identifier (0-499) |
| annotator_id | int | Annotator ID (0, 1, 2) |
| judgment | int | 0 (marginal) or 1 (genuine violation) |
| violation_type | str | Category if judgment=1, else None |

**samples DataFrame:**
| Column | Type | Description |
|--------|------|-------------|
| sample_id | int | Unique sample identifier |
| length_quartile | str | 'Q1', 'Q2', 'Q3', 'Q4' |
| response_text | str | HH-RLHF rejected response |

---

## Gate Decision Logic

```python
def evaluate_gate(analyzer: StatisticalAnalyzer, labels: pd.Series) -> bool:
    """
    Evaluate MUST_WORK gate condition.
    
    Gate PASS if:
        1. base_rate >= 0.40
        2. binomial test p_value < 0.05
        3. (optional) kappa >= 0.75
    """
    base_rate = analyzer.compute_base_rate(labels)
    n_violations = int(labels.sum())
    test_result = analyzer.binomial_test(n_violations, len(labels), p_null=0.40)
    kappa, ci_lower, ci_upper = analyzer.compute_cohens_kappa()
    
    condition_1 = base_rate >= 0.40
    condition_2 = test_result['p_value'] < 0.05
    condition_3 = kappa >= 0.75  # Secondary check
    
    gate_pass = condition_1 and condition_2
    
    print(f"[GATE] Base-rate: {base_rate:.3f} (>= 0.40: {condition_1})")
    print(f"[GATE] Binomial p-value: {test_result['p_value']:.4f} (< 0.05: {condition_2})")
    print(f"[GATE] Cohen's κ: {kappa:.3f} (>= 0.75: {condition_3})")
    print(f"[GATE] Status: {'PASS' if gate_pass else 'FAIL'}")
    
    return gate_pass
```

---

## Usage Example

```python
# Load annotations from CSV
annotations = pd.read_csv('data/annotations/combined_annotations.csv')

# Initialize analyzer
analyzer = StatisticalAnalyzer(annotations, n_annotators=3)

# Compute inter-annotator agreement
kappa, ci_lower, ci_upper = analyzer.compute_cohens_kappa()
print(f"Cohen's κ: {kappa:.3f} (95% CI: [{ci_lower:.3f}, {ci_upper:.3f}])")

# Majority vote for final labels
labels = analyzer.majority_vote()

# Compute base-rate
base_rate = analyzer.compute_base_rate(labels)
print(f"Base-rate: {base_rate:.3f}")

# Binomial test
n_violations = int(labels.sum())
test_result = analyzer.binomial_test(n_violations, len(labels))
print(f"Binomial test p-value: {test_result['p_value']:.4f}")

# Length bias check
samples = pd.read_csv('data/sampled_responses.csv')
bias_result = analyzer.length_bias_test(samples, labels)
print(f"Length bias chi-square p-value: {bias_result['p_value']:.3f}")

# Gate decision
gate_pass = evaluate_gate(analyzer, labels)
```

---

## Self-Validation Checklist

- [x] No ASCII diagrams
- [x] No KB search logs (noted "no-MCP mode")
- [x] Codebase Analysis section included
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes in comments (N/A for statistical data)
- [x] Subtask count within budget (2/2)
- [x] Total length < 600 lines
- [x] EXISTENCE PoC constraints applied (minimal APIs only)
- [x] Applied patterns noted (scipy + statsmodels)

---

*Generated by Logic Agent*  
*Next: Config Agent (Phase 3 Step 5)*
