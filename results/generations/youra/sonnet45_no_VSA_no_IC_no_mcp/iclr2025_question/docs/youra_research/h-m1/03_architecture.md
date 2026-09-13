# Architecture: H-M1 Correlation Analysis

**Date:** 2026-08-25
**Hypothesis:** H-M1 (MECHANISM)
**Type:** Statistical Analysis
**Applied:** Standard scipy/sklearn pattern

---

## Codebase Analysis (Serena)

**Project Type:** Green-field
**Status:** No existing code to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch

---

## Module Structure

### DataLoader (`data_loader.py`)

**Dependencies:** json, pathlib

```python
class CorpusLoader:
    def __init__(self, corpus_path: str): ...
    def load(self) -> list[dict]: ...
    def extract_overhead_arrays(self, corpus: list[dict]) -> tuple[list[float], list[float]]: ...
    def group_by_type(self, corpus: list[dict]) -> dict[str, list[dict]]: ...
```

### CorrelationAnalyzer (`analyzer.py`)

**Dependencies:** scipy.stats, sklearn.linear_model, numpy

```python
class CorrelationAnalyzer:
    def __init__(self): ...
    def compute_pearson(self, x: list[float], y: list[float]) -> tuple[float, float]: ...
    def fit_linear_regression(self, x: list[float], y: list[float]) -> tuple[float, float, float]: ...
    def compute_cv(self, values: list[float]) -> float: ...
```

### PerTypeAnalyzer (`per_type_analyzer.py`)

**Dependencies:** CorrelationAnalyzer, numpy

```python
class PerTypeAnalyzer:
    def __init__(self, analyzer: CorrelationAnalyzer): ...
    def analyze_types(self, grouped_corpus: dict[str, list[dict]]) -> dict[str, dict]: ...
    def compute_scaling_cv(self, k_values: dict[str, float]) -> float: ...
```

### Visualizer (`visualizer.py`)

**Dependencies:** matplotlib.pyplot, pathlib

```python
class Visualizer:
    def __init__(self, output_dir: str): ...
    def plot_correlation_scatter(self, o10: list[float], ofull: list[float], 
                                   types: list[str], r: float, p: float, k: float): ...
    def plot_scaling_factors(self, k_by_type: dict[str, float]): ...
    def plot_residuals(self, o10: list[float], residuals: list[float]): ...
```

### ValidationWriter (`validator.py`)

**Dependencies:** pathlib

```python
class ValidationWriter:
    def __init__(self, output_path: str): ...
    def write_results(self, r: float, p: float, k: float, r2: float, cv: float,
                     k_by_type: dict[str, float], passed: bool): ...
```

### Main (`main.py`)

**Dependencies:** All above modules, argparse

```python
def run_analysis(corpus_path: str, output_dir: str) -> dict: ...
def main(): ...
```

---

## File Organization

```
h-m1/code/
├── data_loader.py
├── analyzer.py
├── per_type_analyzer.py
├── visualizer.py
├── validator.py
├── main.py
└── requirements.txt
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup | Project structure + requirements.txt | 4 | 1+1+1+1 (size+deps+algo+integ) |
| A-2 | Data Loading | Implement CorpusLoader with JSON parsing | 8 | 2+2+2+2 |
| A-3 | Correlation Analysis | Implement CorrelationAnalyzer (pearsonr + LinearRegression) | 11 | 3+2+4+2 |
| A-4 | Per-Type Analysis | Implement PerTypeAnalyzer with grouping logic | 10 | 2+3+3+2 |
| A-5 | Visualization | Implement Visualizer (3 figures: scatter, bars, residuals) | 14 | 4+2+3+5 |
| A-6 | Validation | Implement ValidationWriter (04_validation.md generation) | 7 | 2+1+2+2 |
| A-7 | Main Pipeline | Implement main.py orchestration + CLI | 9 | 2+3+2+2 |
| A-8 | Testing | Run full pipeline + verify r>0.7, p<0.05, CV<30% | 10 | 2+2+3+3 |

**Distribution:** VeryHigh(18-20): [], High(14-17): [A-5], Medium(9-13): [A-3,A-4,A-7,A-8], Low(4-8): [A-1,A-2,A-6]

---

## Data Flow

1. `DataLoader.load()` → corpus (32 papers)
2. `DataLoader.extract_overhead_arrays()` → (O_10, O_full)
3. `CorrelationAnalyzer.compute_pearson()` → (r, p)
4. `CorrelationAnalyzer.fit_linear_regression()` → (k, r2, residuals)
5. `DataLoader.group_by_type()` → grouped_corpus
6. `PerTypeAnalyzer.analyze_types()` → k_by_type
7. `PerTypeAnalyzer.compute_scaling_cv()` → cv
8. `Visualizer.plot_*()` → 3 figures
9. `ValidationWriter.write_results()` → 04_validation.md

---

## Success Validation

**Primary Check:** r > 0.7 AND p < 0.05
**Secondary Check:** cv < 30%
**Output:** 04_validation.md + 3 figures in h-m1/figures/

---

## Dependencies

```txt
scipy>=1.11.0
scikit-learn>=1.3.0
numpy>=1.24.0
matplotlib>=3.7.0
```

---

**Lines:** 147 | **Modules:** 6 | **Tasks:** 8 | **Total Complexity:** 73
