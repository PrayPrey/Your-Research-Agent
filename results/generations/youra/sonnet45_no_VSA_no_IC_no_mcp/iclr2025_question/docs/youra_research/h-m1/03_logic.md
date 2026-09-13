# Logic Design: H-M1 Correlation Analysis

**Date:** 2026-08-25
**Hypothesis:** H-M1 (MECHANISM)
**Type:** Statistical Analysis
**Budget:** 8 subtasks (medium-complexity only)

---

## Codebase Analysis (Serena)

**Project Type:** Green-field
**Status:** No existing code to analyze
**Analyzed Path:** N/A
**Relevant Symbols:** None - new implementation

---

## A-3: CorrelationAnalyzer [Complexity: 11, Budget: 2]

**Applied:** scipy.stats.pearsonr + sklearn.linear_model.LinearRegression

### API Signatures

```python
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import numpy as np

class CorrelationAnalyzer:
    """Statistical correlation analyzer."""
    
    def compute_pearson(self, x: list[float], y: list[float]) -> tuple[float, float]:
        """Compute Pearson correlation. Returns (r, p_value)."""
        return pearsonr(x, y)
    
    def fit_linear_regression(
        self, 
        x: list[float], 
        y: list[float]
    ) -> tuple[float, float, list[float]]:
        """Fit y = k*x. Returns (k, r2, residuals). x: [N], y: [N] -> residuals: [N]"""
        X = np.array(x).reshape(-1, 1)  # [N, 1]
        Y = np.array(y)  # [N]
        
        model = LinearRegression()
        model.fit(X, Y)
        
        k = model.coef_[0]  # Scaling factor
        y_pred = model.predict(X)  # [N]
        r2 = r2_score(Y, y_pred)
        residuals = (Y - y_pred).tolist()  # [N]
        
        return k, r2, residuals
    
    def compute_cv(self, values: list[float]) -> float:
        """Coefficient of variation. cv = std / mean"""
        arr = np.array(values)
        return float(np.std(arr) / np.mean(arr))
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| x, y | [N] | Input arrays (N=32 papers) |
| X | [N, 1] | Reshaped for sklearn |
| residuals | [N] | Prediction errors |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | compute_pearson | Wrap scipy.stats.pearsonr |
| L-3-2 | fit_linear_regression | LinearRegression + residuals |

---

## A-4: PerTypeAnalyzer [Complexity: 10, Budget: 2]

**Applied:** Dict grouping + per-group LinearRegression

### API Signatures

```python
from typing import Dict
import numpy as np

class PerTypeAnalyzer:
    """Per-hypothesis-type scaling analysis."""
    
    def __init__(self, analyzer: CorrelationAnalyzer):
        """Initialize with shared analyzer."""
        self.analyzer = analyzer
    
    def analyze_types(
        self, 
        grouped_corpus: dict[str, list[dict]]
    ) -> dict[str, dict]:
        """
        Analyze each hypothesis type separately.
        grouped_corpus: {type: [papers]}
        Returns: {type: {"k": float, "r2": float, "n": int}}
        """
        results = {}
        for hyp_type, papers in grouped_corpus.items():
            o10 = [p["overhead_measurements"]["micro_pilot"]["overhead_percent"] 
                   for p in papers]
            ofull = [p["overhead_measurements"]["full_scale"]["overhead_percent"] 
                     for p in papers]
            
            k, r2, _ = self.analyzer.fit_linear_regression(o10, ofull)
            results[hyp_type] = {"k": k, "r2": r2, "n": len(papers)}
        
        return results
    
    def compute_scaling_cv(self, k_by_type: dict[str, float]) -> float:
        """CV of scaling factors across types. k_by_type: {type: k}"""
        k_values = list(k_by_type.values())
        return self.analyzer.compute_cv(k_values)
```

### Pseudo-code

```
1. For each hypothesis type in grouped_corpus:
   a. Extract (O_10, O_full) arrays from papers
   b. Fit linear regression -> k, r2
   c. Store {type: {k, r2, n}}
2. Collect all k values -> compute CV
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | analyze_types | Per-type grouping + regression |
| L-4-2 | compute_scaling_cv | CV across k values |

---

## A-7: Main Pipeline [Complexity: 9, Budget: 2]

**Applied:** argparse + sequential function calls

### API Signatures

```python
import argparse
from pathlib import Path
from typing import Dict

def run_analysis(corpus_path: str, output_dir: str) -> dict:
    """
    Run full correlation analysis pipeline.
    Returns: {
        "r": float, "p": float, "k": float, "r2": float,
        "cv": float, "k_by_type": dict, "passed": bool
    }
    """
    # 1. Load data
    loader = CorpusLoader(corpus_path)
    corpus = loader.load()
    o10, ofull = loader.extract_overhead_arrays(corpus)
    grouped = loader.group_by_type(corpus)
    
    # 2. Global correlation
    analyzer = CorrelationAnalyzer()
    r, p = analyzer.compute_pearson(o10, ofull)
    k, r2, residuals = analyzer.fit_linear_regression(o10, ofull)
    
    # 3. Per-type analysis
    per_type = PerTypeAnalyzer(analyzer)
    type_results = per_type.analyze_types(grouped)
    k_by_type = {t: res["k"] for t, res in type_results.items()}
    cv = per_type.compute_scaling_cv(k_by_type)
    
    # 4. Visualizations
    types = [p["hypothesis_type"] for p in corpus]
    viz = Visualizer(output_dir)
    viz.plot_correlation_scatter(o10, ofull, types, r, p, k)
    viz.plot_scaling_factors(k_by_type)
    viz.plot_residuals(o10, residuals)
    
    # 5. Validation
    passed = r > 0.7 and p < 0.05 and cv < 0.3
    validator = ValidationWriter(f"{output_dir}/04_validation.md")
    validator.write_results(r, p, k, r2, cv, k_by_type, passed)
    
    return {
        "r": r, "p": p, "k": k, "r2": r2, "cv": cv,
        "k_by_type": k_by_type, "passed": passed
    }

def main():
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="H-M1 Correlation Analysis")
    parser.add_argument(
        "--corpus-path",
        default="experiments/h-e1_corpus_collection/data/retrospective_corpus/papers_metadata.json",
        help="Path to H-E1 corpus JSON"
    )
    parser.add_argument(
        "--output-dir",
        default="docs/youra_research/h-m1/figures",
        help="Output directory for figures and validation"
    )
    args = parser.parse_args()
    
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    results = run_analysis(args.corpus_path, args.output_dir)
    
    print(f"Results: r={results['r']:.3f}, p={results['p']:.4f}, CV={results['cv']:.2%}")
    print(f"Status: {'PASS' if results['passed'] else 'FAIL'}")
```

### Pseudo-code

```
1. Parse CLI args (corpus_path, output_dir)
2. Load corpus -> (o10, ofull, grouped)
3. Global analysis -> (r, p, k, r2)
4. Per-type analysis -> (k_by_type, cv)
5. Generate 3 visualizations
6. Write validation report
7. Return success status
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | run_analysis | Pipeline orchestration |
| L-7-2 | main | CLI + argparse |

---

## A-8: Testing/Validation [Complexity: 10, Budget: 2]

**Applied:** Threshold checks + file existence validation

### API Signatures

```python
from pathlib import Path

def validate_results(results: dict, output_dir: str) -> tuple[bool, list[str]]:
    """
    Validate analysis results against thresholds.
    Returns: (passed, [error_messages])
    """
    errors = []
    
    # Primary threshold: r > 0.7
    if results["r"] <= 0.7:
        errors.append(f"Pearson r={results['r']:.3f} <= 0.7")
    
    # Statistical significance: p < 0.05
    if results["p"] >= 0.05:
        errors.append(f"p-value={results['p']:.4f} >= 0.05 (not significant)")
    
    # Secondary threshold: CV < 30%
    if results["cv"] >= 0.3:
        errors.append(f"CV={results['cv']:.2%} >= 30% (inconsistent scaling)")
    
    # R² goodness of fit: R² > 0.5
    if results["r2"] < 0.5:
        errors.append(f"R²={results['r2']:.3f} < 0.5 (poor fit)")
    
    return len(errors) == 0, errors

def validate_outputs(output_dir: str) -> tuple[bool, list[str]]:
    """
    Check required output files exist.
    Returns: (passed, [missing_files])
    """
    required_files = [
        "correlation_scatter.png",
        "scaling_factors.png",
        "residual_plot.png",
        "04_validation.md"
    ]
    
    missing = []
    for fname in required_files:
        fpath = Path(output_dir) / fname
        if not fpath.exists():
            missing.append(str(fpath))
    
    return len(missing) == 0, missing

def run_full_validation(results: dict, output_dir: str) -> bool:
    """
    Run all validation checks.
    Returns: overall_passed
    """
    metrics_ok, metric_errors = validate_results(results, output_dir)
    files_ok, missing_files = validate_outputs(output_dir)
    
    if not metrics_ok:
        print("METRIC VALIDATION FAILED:")
        for err in metric_errors:
            print(f"  - {err}")
    
    if not files_ok:
        print("OUTPUT VALIDATION FAILED:")
        for f in missing_files:
            print(f"  - Missing: {f}")
    
    return metrics_ok and files_ok
```

### Pseudo-code

```
1. validate_results:
   a. Check r > 0.7
   b. Check p < 0.05
   c. Check CV < 30%
   d. Check R² > 0.5
   
2. validate_outputs:
   a. Check 3 figures exist
   b. Check 04_validation.md exists
   
3. run_full_validation:
   a. Run both checks
   b. Print errors if any
   c. Return overall status
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | validate_results | Threshold checks (r, p, CV, R²) |
| L-8-2 | validate_outputs | File existence checks |

---

## Summary

**Budget Usage:** 8/8 subtasks
**Patterns Applied:** 
- scipy.stats.pearsonr for correlation
- sklearn.LinearRegression for scaling factors
- argparse for CLI
- Threshold-based validation

**Key Design Decisions:**
1. `compute_pearson`: Direct scipy wrapper (no custom implementation needed)
2. `fit_linear_regression`: Returns residuals for diagnostic plots
3. `analyze_types`: Dict comprehension over grouped corpus
4. `run_analysis`: Sequential pipeline (no parallelization for n=32)
5. `validate_results`: Hard thresholds from PRD (r>0.7, p<0.05, CV<30%)

**Phase 4 Integration:**
- All signatures use stdlib types (list, dict, tuple)
- No custom data structures
- Direct imports from scipy/sklearn
- CLI defaults point to H-E1 corpus path
