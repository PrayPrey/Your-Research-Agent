# H-C1 Logic Specification
# Tactic Budget Feasibility Analysis

**Version**: 1.0  
**Date**: 2026-08-20  
**Complexity**: LOW (statistical analysis, no ML)

---

## Codebase Analysis (Serena)

**Project Type**: existing_codebase (H-E1 baseline data)  
**Status**: No base hypothesis - green-field statistical analysis  
**Analyzed Path**: H-E1 data consumer only  
**Relevant Symbols**: None - new standalone script

---

## Applied Patterns

**Applied**: Standard scipy/numpy statistical pipeline, matplotlib subplot layouts

---

## Core Functions

### F-1: Data Loading

```python
def load_data(csv_path: str) -> pd.DataFrame:
    """Load and filter H-E1 results to solved problems with tactic counts.
    
    Args:
        csv_path: Path to results.csv
    
    Returns:
        DataFrame with columns [problem_id, outcome, tactic_count]
        Filtered to: outcome == 'SOLVED' AND tactic_count.notna()
    
    Raises:
        FileNotFoundError: If csv_path does not exist
        ValueError: If N < 20 (insufficient sample)
    """
    df = pd.read_csv(csv_path, dtype={'tactic_count': 'Int64'})
    solved = df[(df['outcome'] == 'SOLVED') & df['tactic_count'].notna()].copy()
    
    if len(solved) < 20:
        raise ValueError(f"Insufficient sample: N={len(solved)} < 20")
    
    return solved[['problem_id', 'outcome', 'tactic_count']]
```

**Tensor Shapes**: N/A (tabular data)

**Pseudo-code**:
```
1. Load CSV with nullable int dtype for tactic_count
2. Filter: outcome == 'SOLVED' AND tactic_count not NaN
3. Validate: N >= 20
4. Return: [problem_id, outcome, tactic_count] columns
```

---

### F-2: Descriptive Statistics

```python
def compute_stats(tactic_counts: np.ndarray) -> dict:
    """Compute summary statistics for tactic count distribution.
    
    Args:
        tactic_counts: Array of tactic counts, shape [N]
    
    Returns:
        dict with keys: n, mean, std, median, cv, iqr, q1, q3, min, max
    """
    n = len(tactic_counts)
    mean = np.mean(tactic_counts)
    std = np.std(tactic_counts, ddof=1)  # Sample std
    median = np.median(tactic_counts)
    cv = std / mean  # Coefficient of variation
    q1, q3 = np.percentile(tactic_counts, [25, 75])
    iqr = q3 - q1
    
    return {
        'n': int(n),
        'mean': float(mean),
        'std': float(std),
        'median': float(median),
        'cv': float(cv),
        'iqr': float(iqr),
        'q1': float(q1),
        'q3': float(q3),
        'min': int(np.min(tactic_counts)),
        'max': int(np.max(tactic_counts))
    }
```

**Statistical Formulas**:
- **Mean**: μ = (1/N) Σ x_i
- **Std**: σ = sqrt((1/(N-1)) Σ (x_i - μ)²)
- **CV**: σ / μ
- **IQR**: Q3 - Q1

---

### F-3: Budget Recommendation

```python
def recommend_budget(stats: dict) -> tuple[int, str, float]:
    """Apply CV-based decision tree to recommend tactic budget.
    
    Args:
        stats: dict from compute_stats()
    
    Returns:
        (budget: int, estimator: str, coverage: float)
        - budget: ceil(mean + k*std) where k depends on CV
        - estimator: "mean+1σ" or "mean+1.4σ" or "unreliable"
        - coverage: P(X ≤ budget) computed via ECDF
    """
    cv = stats['cv']
    mean = stats['mean']
    std = stats['std']
    
    if cv <= 0.5:
        k = 1.0
        estimator = "mean+1σ"
    elif cv <= 1.0:
        k = 1.4
        estimator = "mean+1.4σ"
    else:
        return None, "unreliable", 0.0
    
    budget = int(np.ceil(mean + k * std))
    return budget, estimator, budget
```

**Decision Tree**:
```
if CV ≤ 0.5:
    budget = ⌈μ + σ⌉
    estimator = "mean+1σ"
elif CV ≤ 1.0:
    budget = ⌈μ + 1.4σ⌉
    estimator = "mean+1.4σ"
else:
    budget = None (FAIL)
    estimator = "unreliable"
```

---

### F-4: Coverage Calculation

```python
def compute_coverage(tactic_counts: np.ndarray, budget: int) -> float:
    """Compute empirical coverage P(X ≤ budget) via ECDF.
    
    Args:
        tactic_counts: Array of tactic counts, shape [N]
        budget: Recommended budget threshold
    
    Returns:
        coverage: float in [0, 1], percentage of samples ≤ budget
    """
    from scipy.stats import ecdf
    
    ecdf_result = ecdf(tactic_counts)
    coverage = ecdf_result.cdf.evaluate(budget)
    return float(coverage)
```

**Algorithm (ECDF)**:
```
1. Sort tactic_counts: x_1 ≤ x_2 ≤ ... ≤ x_N
2. ECDF(t) = (1/N) × #{x_i ≤ t}
3. coverage = ECDF(budget)
```

**Example**: budget=15, tactic_counts=[5,7,8,9,11,14,16,18,20]
- N=9, #{x_i ≤ 15} = 6
- coverage = 6/9 = 0.667 (66.7%)

---

### F-5: Gate Evaluation

```python
def evaluate_gate(cv: float) -> tuple[str, str]:
    """Evaluate H-C1 MUST_WORK gate criterion.
    
    Args:
        cv: Coefficient of variation
    
    Returns:
        (gate_result: str, verdict: str)
        - gate_result: "PASS" | "FAIL"
        - verdict: Human-readable explanation
    """
    if cv <= 1.0:
        gate_result = "PASS"
        verdict = f"CV={cv:.2f} ≤ 1.0, tactic budget feasible"
    else:
        gate_result = "FAIL"
        verdict = f"CV={cv:.2f} > 1.0, variance too high for budget control"
    
    return gate_result, verdict
```

**Gate Logic**:
```
CV ≤ 1.0 → PASS (budget feasible)
CV > 1.0 → FAIL (high variance, unreliable budget)
```

---

### F-6: Visualization

```python
def plot_distribution(
    tactic_counts: np.ndarray,
    budget: int,
    stats: dict,
    output_path: str
) -> None:
    """Generate 3-panel visualization (histogram, boxplot, ECDF).
    
    Args:
        tactic_counts: Array of tactic counts, shape [N]
        budget: Recommended budget
        stats: dict from compute_stats()
        output_path: Save path for PNG
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    # Panel 1: Histogram
    axes[0].hist(tactic_counts, bins=15, edgecolor='black', alpha=0.7)
    axes[0].axvline(budget, color='red', linestyle='--', label=f'Budget={budget}')
    axes[0].axvline(stats['mean'], color='blue', linestyle='-', label=f"Mean={stats['mean']:.1f}")
    axes[0].set_xlabel('Tactic Count')
    axes[0].set_ylabel('Frequency')
    axes[0].legend()
    axes[0].set_title('Distribution of Tactic Counts')
    
    # Panel 2: Box Plot
    axes[1].boxplot(tactic_counts, vert=True)
    axes[1].axhline(budget, color='red', linestyle='--', label=f'Budget={budget}')
    axes[1].set_ylabel('Tactic Count')
    axes[1].legend()
    axes[1].set_title('Outlier Detection (IQR)')
    
    # Panel 3: ECDF
    from scipy.stats import ecdf
    ecdf_result = ecdf(tactic_counts)
    axes[2].plot(ecdf_result.cdf.quantiles, ecdf_result.cdf.probabilities, 
                 marker='o', markersize=4, linestyle='-')
    axes[2].axvline(budget, color='red', linestyle='--', label=f'Budget={budget}')
    coverage = ecdf_result.cdf.evaluate(budget)
    axes[2].annotate(f'Coverage={coverage:.1%}', 
                     xy=(budget, coverage), 
                     xytext=(budget+2, coverage-0.1),
                     arrowprops=dict(arrowstyle='->'))
    axes[2].set_xlabel('Tactic Count')
    axes[2].set_ylabel('Cumulative Probability')
    axes[2].legend()
    axes[2].set_title('Empirical CDF')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
```

**Layout Algorithm**:
```
1. Create 1×3 subplot grid (figsize 15×4)
2. Panel 1 (histogram):
   - bins=15 (adaptive)
   - Overlay: budget (red dashed), mean (blue solid)
3. Panel 2 (boxplot):
   - Outliers: Q1 - 1.5×IQR, Q3 + 1.5×IQR
   - Budget line (red dashed)
4. Panel 3 (ECDF):
   - X = sorted tactic counts
   - Y = i/N for i-th sorted value
   - Budget line with coverage annotation
5. Save: 150 dpi, tight layout
```

---

### F-7: Report Generation

```python
def write_report(
    stats: dict,
    budget: int,
    estimator: str,
    coverage: float,
    gate_result: str,
    verdict: str,
    output_path: str
) -> None:
    """Generate markdown validation report."""
    report = f"""# H-C1 Validation Report

## Summary Statistics
- **Sample Size**: {stats['n']}
- **Mean**: {stats['mean']:.1f}
- **Std Dev**: {stats['std']:.1f}
- **CV**: {stats['cv']:.2f} ({stats['cv']*100:.0f}%)
- **Median**: {stats['median']:.1f}
- **IQR**: {stats['iqr']:.1f}

## Budget Recommendation
- **Budget**: {budget} tactic evaluations
- **Estimator**: {estimator}
- **Coverage**: {coverage:.1%} of baseline solves

## Gate Decision
- **Criterion**: CV ≤ 1.0
- **Observed CV**: {stats['cv']:.2f}
- **Result**: {gate_result}

## Interpretation
{verdict}

## Downstream Implications
- Apply budget={budget} to H-M1/M2/M3 LeanCopilot runs
- Report both raw and budget-constrained success rates in Phase 5
"""
    
    with open(output_path, 'w') as f:
        f.write(report)
```

---

## Main Pipeline

```python
def main():
    """Execute H-C1 analysis pipeline."""
    # FR-1: Load data
    df = load_data("h-e1/code/data/results/results.csv")
    tactic_counts = df['tactic_count'].values
    
    # FR-2: Compute statistics
    stats = compute_stats(tactic_counts)
    
    # FR-3: Recommend budget
    budget, estimator, _ = recommend_budget(stats)
    
    # FR-4: Compute coverage
    coverage = compute_coverage(tactic_counts, budget)
    
    # FR-5: Evaluate gate
    gate_result, verdict = evaluate_gate(stats['cv'])
    
    # FR-6: Plot visualization
    plot_distribution(tactic_counts, budget, stats, "tactic_budget_analysis.png")
    
    # FR-7: Write report
    write_report(stats, budget, estimator, coverage, gate_result, verdict, "04_validation.md")
    
    # Save summary.json
    summary = {
        'statistics': stats,
        'budget': {'value': budget, 'estimator': estimator, 'coverage': coverage},
        'gate': {'cv': stats['cv'], 'result': gate_result}
    }
    with open('summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Gate Decision: {gate_result}")
    print(f"Budget: {budget} ({estimator}), Coverage: {coverage:.1%}")
```

---

## Edge Cases

### E-1: Insufficient Sample (N < 20)
```python
# In load_data():
if len(solved) < 20:
    raise ValueError(f"Insufficient sample: N={len(solved)} < 20")
```

### E-2: High Variance (CV > 1.0)
```python
# In recommend_budget():
if cv > 1.0:
    return None, "unreliable", 0.0
```

### E-3: Missing CSV File
```python
# In load_data():
if not Path(csv_path).exists():
    raise FileNotFoundError(f"Results file not found: {csv_path}")
```

### E-4: Non-numeric Tactic Counts
```python
# In load_data():
df = pd.read_csv(csv_path, dtype={'tactic_count': 'Int64'})  # Nullable int
# NaN values automatically excluded by .notna() filter
```

---

## Dependencies

**External Libraries**:
- `pandas>=2.0.3` - DataFrame operations
- `numpy>=1.24.4` - Statistical computations
- `scipy>=1.11.2` - ECDF calculation
- `matplotlib>=3.7.2` - Plotting

**Standard Library**:
- `json` - Summary output
- `pathlib` - File path handling
- `math` - ceil() for budget rounding

---

## Validation Checks

**Self-Test Cases**:

```python
# Test CV=0.45 → budget=15
tactic_counts = np.array([5, 7, 8, 9, 11, 14, 16, 18, 20])
stats = compute_stats(tactic_counts)
assert abs(stats['cv'] - 0.45) < 0.1, "CV mismatch"

budget, estimator, _ = recommend_budget(stats)
assert budget == 15, f"Expected budget=15, got {budget}"
assert estimator == "mean+1.4σ", f"Expected mean+1.4σ, got {estimator}"

# Test gate logic
gate_result, _ = evaluate_gate(0.45)
assert gate_result == "PASS", "Gate should pass for CV=0.45"

gate_result, _ = evaluate_gate(1.2)
assert gate_result == "FAIL", "Gate should fail for CV=1.2"
```

---

## Output Files

1. **summary.json**: Machine-readable statistics
   ```json
   {
     "statistics": {...},
     "budget": {"value": 15, "estimator": "mean+1.4σ", "coverage": 0.81},
     "gate": {"cv": 0.45, "result": "PASS"}
   }
   ```

2. **tactic_budget_analysis.png**: 3-panel visualization (1500×400 px)

3. **04_validation.md**: Human-readable gate decision report

---

## Complexity Budget

**Total Functions**: 7  
**External Dependencies**: 4 libraries (pandas, numpy, scipy, matplotlib)  
**Lines of Code**: ~200 (excluding docstrings)  
**Execution Time**: <30 seconds

---

## Notes

- No machine learning, no neural networks - pure statistical analysis
- One-off script, no need for classes or abstractions
- Manual validation sufficient (no automated tests required)
- Bootstrap CI omitted (t-distribution faster for N=32)
- Outliers reported but not removed (real search complexity)
