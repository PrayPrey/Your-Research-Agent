# Logic Design & Implementation Details
# Hypothesis: H-E1 - Base-Rate Validation Study

**Version:** 1.0  
**Date:** 2026-04-19  
**Hypothesis ID:** h-e1  
**Focus:** API Signatures, Algorithms, Tensor Shapes (N/A for annotation study)

---

## Codebase Analysis (Serena)

**Analysis Status:** Green-field implementation (no existing codebase)

**Context:** Novel annotation study with no code dependencies. All APIs designed from scratch following standard Python data science patterns.

**Applied:** Standard data processing API patterns (KB-002-DataPipeline)

---

## 1. Module: Data Sampling (`src/data/`)

### 1.1 API: `sampler.py`

#### Function: `stratified_sample`

```python
def stratified_sample(
    dataset: Dataset,
    sample_size: int = 500,
    strata_column: str = "length_quartile",
    seed: int = 42
) -> pd.DataFrame:
    """
    Perform stratified random sampling from HH-RLHF dataset.
    
    Args:
        dataset: HuggingFace Dataset object (rejected responses only)
        sample_size: Total number of samples to draw (default 500)
        strata_column: Column name for stratification (default "length_quartile")
        seed: Random seed for reproducibility (default 42)
    
    Returns:
        pd.DataFrame with columns: [id, prompt, rejected_response, length, length_quartile]
        Shape: (500, 5)
    
    Algorithm:
        1. Convert HF Dataset to pandas DataFrame
        2. Calculate response lengths
        3. Assign length quartiles (Q1, Q2, Q3, Q4)
        4. Sample equally from each quartile (125 samples per quartile)
        5. Return combined DataFrame
    """
```

**Algorithm Pseudo-code:**
```python
# Step 1: Compute lengths
df["length"] = df["rejected"].apply(len)

# Step 2: Assign quartiles
df["length_quartile"] = pd.qcut(df["length"], q=4, labels=["Q1", "Q2", "Q3", "Q4"])

# Step 3: Stratified sampling
samples_per_quartile = sample_size // 4  # 125
sampled = df.groupby("length_quartile", group_keys=False).apply(
    lambda x: x.sample(n=samples_per_quartile, random_state=seed)
)

return sampled
```

---

#### Function: `load_hh_rlhf_dataset`

```python
def load_hh_rlhf_dataset(
    dataset_name: str = "Anthropic/hh-rlhf",
    subset: str = "harmless-base",
    split: str = "train"
) -> Dataset:
    """
    Load HH-RLHF dataset from HuggingFace.
    
    Args:
        dataset_name: HuggingFace dataset identifier
        subset: Dataset subset (harmless-base or helpful-base)
        split: Data split (train, test)
    
    Returns:
        HuggingFace Dataset object with rejected responses
        Fields: prompt, chosen, rejected
    
    Algorithm:
        1. Load dataset via HuggingFace API
        2. Filter to rejected responses only
        3. Return Dataset object
    """
```

---

## 2. Module: Annotation Interface (`src/annotation/`)

### 2.1 API: `interface.py`

#### Function: `present_sample_for_annotation`

```python
def present_sample_for_annotation(
    sample: Dict[str, str],
    violation_criteria: List[str],
    annotator_id: int
) -> bool:
    """
    Present a single sample to annotator and collect judgment.
    
    Args:
        sample: Dict with keys {id, prompt, rejected_response}
        violation_criteria: List of 6 violation types (checklist)
        annotator_id: Annotator identifier (1, 2, or 3)
    
    Returns:
        bool: True = genuine violation, False = marginal preference
    
    Algorithm:
        1. Display prompt and rejected response (blinded to original label)
        2. Show violation criteria checklist
        3. Ask: "Is this a genuine safety violation?" (Y/N)
        4. Return boolean judgment
    """
```

**Violation Criteria (Display):**
```
1. Direct harm/violence encouragement
2. Toxic/offensive language
3. Privacy violations or personal information disclosure
4. Dangerous/illegal advice
5. Deception or misinformation
6. Other safety policy violations
```

---

#### Function: `collect_annotations_batch`

```python
def collect_annotations_batch(
    samples: pd.DataFrame,
    annotator_id: int,
    output_file: str = "data/annotations.csv"
) -> pd.DataFrame:
    """
    Collect annotations for all samples from one annotator.
    
    Args:
        samples: DataFrame with 500 samples (from stratified_sample)
        annotator_id: Annotator identifier (1, 2, or 3)
        output_file: Path to save annotations
    
    Returns:
        pd.DataFrame with columns: [sample_id, annotator_id, judgment]
        Shape: (500, 3)
    
    Algorithm:
        1. Iterate through all samples
        2. For each sample, call present_sample_for_annotation()
        3. Store judgment in DataFrame
        4. Save to CSV after each batch (checkpoint)
        5. Return full annotation DataFrame
    """
```

---

## 3. Module: Statistical Analysis (`src/analysis/`)

### 3.1 API: `agreement.py`

#### Function: `compute_cohens_kappa`

```python
def compute_cohens_kappa(
    annotations: pd.DataFrame,
    n_annotators: int = 3
) -> Tuple[float, pd.DataFrame]:
    """
    Calculate Cohen's kappa for multi-rater agreement.
    
    Args:
        annotations: DataFrame with columns [sample_id, annotator_id, judgment]
        n_annotators: Number of annotators (default 3)
    
    Returns:
        Tuple[float, pd.DataFrame]:
            - Overall multi-rater kappa (float)
            - Pairwise kappa matrix (3×3 DataFrame)
        
    Shape:
        - Input: (1500, 3)  [500 samples × 3 annotators]
        - Output: scalar + (3, 3) matrix
    
    Algorithm:
        1. Pivot annotations to rating matrix (500 × 3)
        2. Compute pairwise kappa for all annotator pairs
        3. Compute overall kappa using Fleiss' extension
        4. Return both overall and pairwise kappas
    """
```

**Algorithm Pseudo-code:**
```python
# Step 1: Pivot to rating matrix
rating_matrix = annotations.pivot(
    index="sample_id", 
    columns="annotator_id", 
    values="judgment"
)  # Shape: (500, 3)

# Step 2: Pairwise kappa
from statsmodels.stats.inter_rater import cohens_kappa
pairwise_kappas = pd.DataFrame(index=[1,2,3], columns=[1,2,3])
for i in [1, 2, 3]:
    for j in [1, 2, 3]:
        if i != j:
            kappa = cohens_kappa(rating_matrix[[i, j]].values)
            pairwise_kappas.loc[i, j] = kappa

# Step 3: Overall kappa (average of pairwise)
overall_kappa = pairwise_kappas.values[~np.isnan(pairwise_kappas.values)].mean()

return overall_kappa, pairwise_kappas
```

---

### 3.2 API: `metrics.py`

#### Function: `calculate_base_rate`

```python
def calculate_base_rate(
    final_labels: np.ndarray,
    confidence_level: float = 0.95
) -> Tuple[float, Tuple[float, float]]:
    """
    Calculate base-rate of genuine violations with confidence interval.
    
    Args:
        final_labels: Binary array (1=violation, 0=marginal) from majority vote
        confidence_level: CI confidence level (default 0.95)
    
    Returns:
        Tuple[float, Tuple[float, float]]:
            - Base-rate p (proportion of violations)
            - 95% confidence interval (lower, upper)
        
    Shape:
        - Input: (500,) binary array
        - Output: scalar + (lower, upper) tuple
    
    Algorithm:
        1. Count genuine violations (sum of 1s)
        2. Calculate proportion p = violations / total
        3. Compute 95% CI using Wilson score interval
        4. Return (p, CI)
    """
```

**Algorithm Pseudo-code:**
```python
n = len(final_labels)
k = np.sum(final_labels)  # Count violations
p = k / n  # Base-rate

# Wilson score interval for binomial proportion
from statsmodels.stats.proportion import proportion_confint
ci_lower, ci_upper = proportion_confint(
    count=k, 
    nobs=n, 
    alpha=1-confidence_level, 
    method='wilson'
)

return p, (ci_lower, ci_upper)
```

---

#### Function: `majority_vote`

```python
def majority_vote(
    annotations: pd.DataFrame,
    n_annotators: int = 3
) -> np.ndarray:
    """
    Determine final labels using majority vote from 3 annotators.
    
    Args:
        annotations: DataFrame with columns [sample_id, annotator_id, judgment]
        n_annotators: Number of annotators (default 3)
    
    Returns:
        np.ndarray: Binary array (1=violation, 0=marginal)
        Shape: (500,)
    
    Algorithm:
        1. Pivot to rating matrix (500 × 3)
        2. Sum votes across annotators
        3. Apply majority rule: ≥2 votes → 1, else → 0
        4. Return binary array
    """
```

**Algorithm Pseudo-code:**
```python
rating_matrix = annotations.pivot(
    index="sample_id", 
    columns="annotator_id", 
    values="judgment"
)

# Sum votes per sample (0-3 range)
vote_sums = rating_matrix.sum(axis=1)

# Majority rule: ≥2 votes for violation → 1
final_labels = (vote_sums >= 2).astype(int).values

return final_labels  # Shape: (500,)
```

---

### 3.3 API: `hypothesis_test.py`

#### Function: `binomial_test`

```python
def binomial_test(
    n_successes: int,
    n_trials: int,
    p_null: float = 0.40,
    alpha: float = 0.05,
    alternative: str = "greater"
) -> Tuple[float, bool]:
    """
    Perform one-tailed binomial test for H0: p < 0.40 vs H1: p ≥ 0.40.
    
    Args:
        n_successes: Number of genuine violations observed
        n_trials: Total sample size (500)
        p_null: Null hypothesis threshold (default 0.40)
        alpha: Significance level (default 0.05)
        alternative: Test direction ('greater' for one-tailed)
    
    Returns:
        Tuple[float, bool]:
            - p-value (float)
            - PASS/FAIL decision (True=PASS, False=FAIL)
        
    Algorithm:
        1. Use scipy.stats.binomtest
        2. One-tailed test with alternative='greater'
        3. Compare p-value to alpha
        4. Return (p_value, decision)
    """
```

**Algorithm Pseudo-code:**
```python
from scipy.stats import binomtest

result = binomtest(
    k=n_successes,
    n=n_trials,
    p=p_null,
    alternative=alternative
)

p_value = result.pvalue
decision = (p_value < alpha)  # True=PASS gate, False=FAIL gate

return p_value, decision
```

---

## 4. Module: Visualization (`src/visualization/`)

### 4.1 API: `plots.py`

#### Function: `plot_base_rate_comparison`

```python
def plot_base_rate_comparison(
    base_rate: float,
    threshold: float = 0.40,
    p_value: float = None,
    output_path: str = "outputs/figures/base_rate.png"
) -> None:
    """
    Generate bar chart comparing base-rate to threshold.
    
    Args:
        base_rate: Observed base-rate p
        threshold: Null hypothesis threshold (0.40)
        p_value: Binomial test p-value (for annotation)
        output_path: Save path for figure
    
    Returns:
        None (saves figure to file)
    
    Visualization:
        - Bar chart with 2 bars: [Threshold=0.40, Observed=p]
        - Horizontal line at 0.40
        - Annotation: p-value and PASS/FAIL decision
    """
```

---

#### Function: `plot_agreement_heatmap`

```python
def plot_agreement_heatmap(
    pairwise_kappas: pd.DataFrame,
    output_path: str = "outputs/figures/agreement_heatmap.png"
) -> None:
    """
    Generate heatmap of inter-annotator agreement (Cohen's kappa).
    
    Args:
        pairwise_kappas: 3×3 DataFrame of pairwise kappa values
        output_path: Save path for figure
    
    Returns:
        None (saves figure to file)
    
    Visualization:
        - Heatmap with annotated kappa values
        - Color scale: red (low) → green (high)
        - Diagonal = 1.0 (self-agreement)
    """
```

---

#### Function: `plot_violation_distribution`

```python
def plot_violation_distribution(
    annotations: pd.DataFrame,
    output_path: str = "outputs/figures/violation_types.png"
) -> None:
    """
    Generate bar chart of violation type frequency.
    
    Args:
        annotations: DataFrame with violation type labels
        output_path: Save path for figure
    
    Returns:
        None (saves figure to file)
    
    Visualization:
        - Bar chart with 6 bars (one per violation criterion)
        - Y-axis: count of samples marked for each criterion
    """
```

---

#### Function: `plot_length_bias`

```python
def plot_length_bias(
    samples: pd.DataFrame,
    final_labels: np.ndarray,
    output_path: str = "outputs/figures/length_bias.png"
) -> None:
    """
    Generate scatter plot of violation rate vs response length quartile.
    
    Args:
        samples: DataFrame with length_quartile column
        final_labels: Binary array (1=violation, 0=marginal)
        output_path: Save path for figure
    
    Returns:
        None (saves figure to file)
    
    Visualization:
        - Scatter plot: X=length_quartile (Q1-Q4), Y=violation_rate
        - Shows if violations cluster in certain length ranges
    """
```

---

## 5. Module: Experiment Runner (`src/main.py`)

### 5.1 API: `main.py`

#### Function: `run_experiment`

```python
def run_experiment(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Orchestrate full annotation study pipeline.
    
    Args:
        config_path: Path to configuration YAML
    
    Returns:
        Dict with results:
            {
                "base_rate": float,
                "confidence_interval": (float, float),
                "kappa": float,
                "p_value": float,
                "decision": bool
            }
    
    Pipeline Steps:
        1. Load HH-RLHF dataset
        2. Stratified sampling (500 samples)
        3. Collect annotations (3 annotators)
        4. Compute inter-annotator agreement
        5. Majority vote for final labels
        6. Calculate base-rate
        7. Binomial hypothesis test
        8. Generate visualizations
        9. Write report
    """
```

**Algorithm Pseudo-code:**
```python
# Step 1: Load config
config = yaml.safe_load(open(config_path))

# Step 2: Data sampling
dataset = load_hh_rlhf_dataset()
samples = stratified_sample(dataset, sample_size=500)
samples.to_csv("data/hh_rlhf_samples.csv")

# Step 3: Annotation collection (manual or interface)
print("Run annotation interface for 3 annotators...")
# annotations.csv created manually or via interface

# Step 4: Load annotations
annotations = pd.read_csv("data/annotations.csv")

# Step 5: Inter-annotator agreement
kappa, pairwise_kappas = compute_cohens_kappa(annotations)
print(f"Cohen's kappa: {kappa:.3f}")

# Step 6: Majority vote
final_labels = majority_vote(annotations)

# Step 7: Base-rate calculation
base_rate, ci = calculate_base_rate(final_labels)
print(f"Base-rate: {base_rate:.3f} (95% CI: {ci})")

# Step 8: Binomial test
n_violations = np.sum(final_labels)
p_value, decision = binomial_test(n_violations, n_trials=500)
print(f"Binomial test p-value: {p_value:.4f}")
print(f"Gate decision: {'PASS' if decision else 'FAIL'}")

# Step 9: Visualizations
plot_base_rate_comparison(base_rate, p_value=p_value)
plot_agreement_heatmap(pairwise_kappas)
plot_violation_distribution(annotations)
plot_length_bias(samples, final_labels)

# Step 10: Write report
results = {
    "base_rate": base_rate,
    "confidence_interval": ci,
    "kappa": kappa,
    "p_value": p_value,
    "decision": decision
}

with open("outputs/results.json", "w") as f:
    json.dump(results, f, indent=2)

write_report(results)

return results
```

---

## 6. Data Structures & Shapes

### 6.1 Key Data Shapes

| Data Structure | Shape | Description |
|----------------|-------|-------------|
| `samples` | (500, 5) | Sampled responses with metadata |
| `annotations` | (1500, 3) | 500 samples × 3 annotators |
| `rating_matrix` | (500, 3) | Pivoted annotation matrix |
| `final_labels` | (500,) | Binary violation labels |
| `pairwise_kappas` | (3, 3) | Inter-annotator agreement matrix |

### 6.2 DataFrame Schemas

**samples.csv:**
```
Columns: [id, prompt, rejected_response, length, length_quartile]
Types: [int, str, str, int, str]
Shape: (500, 5)
```

**annotations.csv:**
```
Columns: [sample_id, annotator_id, judgment]
Types: [int, int, bool]
Shape: (1500, 3)  # 500 × 3
```

---

## 7. Error Handling & Edge Cases

### 7.1 Edge Cases

1. **Tie in Majority Vote:** If annotators split 1-2 or 0-3, use sum ≥ 2 rule
2. **Missing Annotations:** Validate all 1500 annotations present before analysis
3. **Low Inter-Annotator Agreement:** If κ < 0.60, warn and flag for investigation

### 7.2 Validation Checks

```python
# Pre-analysis validation
assert len(samples) == 500, "Sample size must be 500"
assert len(annotations) == 1500, "Must have 3 annotations per sample"
assert annotations["annotator_id"].nunique() == 3, "Must have 3 unique annotators"
```

---

## 8. Performance Considerations

**Computational Complexity:**
- Sampling: O(n log n) for sorting by length
- Cohen's κ: O(n × k²) where k=3 annotators, n=500 samples
- Binomial test: O(1) (closed-form calculation)
- Visualizations: O(n) for plotting

**Memory:** < 10 MB for all data structures (500 samples × 3 annotators)

**Runtime:** < 5 minutes for full pipeline (excluding manual annotation time)

---

## 9. Dependencies Summary

### 9.1 External Libraries

```python
from datasets import load_dataset              # HuggingFace datasets
import pandas as pd                            # Data manipulation
import numpy as np                             # Numerical operations
from statsmodels.stats.inter_rater import cohens_kappa  # Agreement
from statsmodels.stats.proportion import proportion_confint  # CI
from scipy.stats import binomtest              # Hypothesis test
import matplotlib.pyplot as plt                # Plotting
import seaborn as sns                          # Heatmaps
import yaml                                    # Config loading
import json                                    # Results serialization
```

---

## 10. Testing Guidance

### 10.1 Unit Tests

**test_sampler.py:**
```python
def test_stratified_sample_balance():
    # Test: Each quartile has 125 samples
    assert len(samples[samples["length_quartile"] == "Q1"]) == 125
    
def test_stratified_sample_reproducibility():
    # Test: Same seed produces same samples
    samples1 = stratified_sample(dataset, seed=42)
    samples2 = stratified_sample(dataset, seed=42)
    assert samples1.equals(samples2)
```

**test_agreement.py:**
```python
def test_cohens_kappa_perfect_agreement():
    # Test: κ=1.0 for identical annotators
    annotations = create_perfect_agreement_data()
    kappa, _ = compute_cohens_kappa(annotations)
    assert np.isclose(kappa, 1.0)
```

**test_hypothesis_test.py:**
```python
def test_binomial_test_pass():
    # Test: p=0.45 should PASS gate
    p_value, decision = binomial_test(n_successes=225, n_trials=500)
    assert decision == True  # PASS
```

---

**Document Status:** COMPLETE  
**Next Phase:** Configuration Design (03_config.md)  
**Applied Patterns:** KB-002-DataPipeline, Standard statistical testing APIs
