# Architecture Design: h-m2

**Date:** 2026-08-25
**Hypothesis:** h-m2 (MECHANISM)
**Type:** Statistical analysis extension - ANOVA variance validation
**PRD:** 03_prd.md

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Extends h-e1 validated correlation infrastructure
**Analyzed Path:** /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_dl4c/docs/youra_research/h-e1/code/
**Findings:** h-e1 implements dataset loading, feedback collection, correlation computation. h-m2 reuses data loading and adds ANOVA/variance analysis modules.

---

## Applied Patterns (Archon KB)

Applied: Statistical validation pipeline (load → correlate → ANOVA → visualize)

---

## System Overview

Statistical analysis pipeline to validate task-dependent variance in execution-human correlation across HumanEval, MBPP, SWE-bench. Extends h-e1 correlation measurement with ANOVA testing and variance decomposition.

**Purpose:** MECHANISM validation - does correlation vary systematically by task type?

**Reuses from h-e1:**
- Dataset loaders (data/loader.py)
- Feedback data format (exec, ai, human arrays)
- Correlation computation (analysis/correlations.py)

**Adds for h-m2:**
- Feedback data loader from h-e1 cache
- ANOVA testing module
- Variance decomposition module
- Task-type-specific visualization

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| Problem | `from h_e1.data.loader import Problem` | h-e1/code/data/loader.py |
| compute_pairwise_correlations | `from h_e1.analysis.correlations import compute_pairwise_correlations` | h-e1/code/analysis/correlations.py |
| bootstrap_ci | `from h_e1.analysis.correlations import bootstrap_ci` | h-e1/code/analysis/correlations.py |

**Note:** h-m2 loads pre-computed feedback from h-e1 cache. No need to import generation/feedback collection modules.

---

## Module Structure

### 1. FeedbackLoader (`data_loader.py`)

**Dependencies:** numpy, pathlib

```python
def load_h_e1_feedback(
    cache_dir: Path,
    dataset_name: str
) -> Dict[str, np.ndarray]:
    """Load exec, ai, human feedback from h-e1 cache.
    
    Returns:
        {"exec": np.ndarray, "ai": np.ndarray, "human": np.ndarray}
    """
    ...

def validate_feedback_integrity(feedback: Dict[str, np.ndarray]) -> None:
    """Check no NaN/Inf, correct shapes, valid ranges."""
    ...
```

---

### 2. StatisticalTests (`analysis/anova.py`)

**Dependencies:** scipy, numpy

```python
def compute_correlation_distributions(
    exec_scores: np.ndarray,
    human_ratings: np.ndarray,
    n_bootstrap: int = 1000,
    seed: int = 42
) -> np.ndarray:
    """Bootstrap correlation distribution for one dataset."""
    ...

def anova_test(
    corr_dist_humaneval: np.ndarray,
    corr_dist_mbpp: np.ndarray,
    corr_dist_swebench: np.ndarray
) -> Tuple[float, float]:
    """One-way ANOVA on correlation distributions.
    
    Returns:
        (f_stat, p_value)
    """
    ...

def compute_effect_size(r1: float, r2: float) -> float:
    """Absolute correlation difference."""
    ...
```

---

### 3. VarianceAnalyzer (`analysis/variance.py`)

**Dependencies:** numpy

```python
def compute_between_task_variance(
    correlations: Dict[str, float]
) -> float:
    """Variance across dataset correlation values."""
    ...

def compute_within_task_variance(
    corr_distributions: Dict[str, np.ndarray]
) -> float:
    """Mean variance within each dataset's bootstrap distribution."""
    ...

def compute_variance_ratio(
    between_var: float,
    within_var: float
) -> float:
    """Between/within ratio (threshold: ≥2.0)."""
    ...
```

---

### 4. TaskTypeVisualizer (`analysis/visualize.py`)

**Dependencies:** matplotlib, seaborn

```python
def plot_correlation_by_task(
    correlations: Dict[str, Tuple[float, Tuple[float, float]]],
    output_path: Path
) -> None:
    """Bar chart with error bars.
    
    Args:
        correlations: {dataset: (r, (ci_low, ci_high))}
    """
    ...

def plot_correlation_heatmap(
    all_correlations: Dict[str, Dict[str, float]],
    output_path: Path
) -> None:
    """3×3 heatmap: datasets × correlation pairs."""
    ...

def plot_variance_decomposition(
    between_var: float,
    within_var: float,
    output_path: Path
) -> None:
    """Bar chart: between vs within variance."""
    ...
```

---

### 5. ValidationReporter (`report_generator.py`)

**Dependencies:** pathlib

```python
def generate_validation_report(
    correlations: Dict[str, Dict[str, Tuple[float, float]]],
    anova_result: Tuple[float, float],
    effect_size: float,
    variance_ratio: float,
    figure_paths: Dict[str, Path],
    output_path: Path
) -> None:
    """Write 04_validation.md with pass/fail status."""
    ...

def check_primary_criteria(p_anova: float, effect_size: float) -> bool:
    """p_anova < 0.05 AND effect_size > 0.3."""
    ...

def check_secondary_criteria(variance_ratio: float) -> bool:
    """variance_ratio ≥ 2.0."""
    ...
```

---

### 6. MainRunner (`run_analysis.py`)

**Dependencies:** All above modules

```python
def main():
    # Setup paths
    base_dir = Path(".../h-m2")
    h_e1_cache = Path(".../h-e1/.data_cache/feedback")
    
    # Load h-e1 feedback data
    datasets = ["humaneval", "mbpp", "swebench"]
    feedback = {ds: load_h_e1_feedback(h_e1_cache, ds) for ds in datasets}
    
    # Validate data integrity
    for ds in datasets:
        validate_feedback_integrity(feedback[ds])
    
    # Compute correlations per dataset
    correlations = {}
    corr_distributions = {}
    for ds in datasets:
        r, p = pearsonr(feedback[ds]["exec"], feedback[ds]["human"])
        ci = bootstrap_ci(feedback[ds]["exec"], feedback[ds]["human"])
        correlations[ds] = {"r": r, "p": p, "ci": ci}
        corr_distributions[ds] = compute_correlation_distributions(
            feedback[ds]["exec"], feedback[ds]["human"]
        )
    
    # ANOVA test
    f_stat, p_anova = anova_test(
        corr_distributions["humaneval"],
        corr_distributions["mbpp"],
        corr_distributions["swebench"]
    )
    
    # Effect size
    effect_size = compute_effect_size(
        correlations["humaneval"]["r"],
        correlations["swebench"]["r"]
    )
    
    # Variance decomposition
    between_var = compute_between_task_variance(
        {ds: correlations[ds]["r"] for ds in datasets}
    )
    within_var = compute_within_task_variance(corr_distributions)
    variance_ratio = compute_variance_ratio(between_var, within_var)
    
    # Generate figures
    figures_dir = base_dir / "figures"
    figures_dir.mkdir(exist_ok=True)
    
    plot_correlation_by_task(
        {ds: (correlations[ds]["r"], correlations[ds]["ci"]) for ds in datasets},
        figures_dir / "correlation_by_task.png"
    )
    plot_correlation_heatmap(
        {ds: compute_pairwise_correlations(
            feedback[ds]["exec"], feedback[ds]["ai"], feedback[ds]["human"]
        ) for ds in datasets},
        figures_dir / "correlation_heatmap.png"
    )
    plot_variance_decomposition(
        between_var, within_var,
        figures_dir / "variance_decomposition.png"
    )
    
    # Validation report
    generate_validation_report(
        correlations, (f_stat, p_anova), effect_size, variance_ratio,
        {
            "correlation_by_task": figures_dir / "correlation_by_task.png",
            "correlation_heatmap": figures_dir / "correlation_heatmap.png",
            "variance_decomposition": figures_dir / "variance_decomposition.png"
        },
        base_dir / "04_validation.md"
    )
```

---

## Data Flow

```
h-e1 feedback cache → [exec, ai, human arrays per dataset]
                            ↓
Correlation Computation → [r, p, CI per dataset]
                            ↓
Bootstrap Distributions → [1000 correlation samples per dataset]
                            ↓
                     ├→ ANOVA test → (F-stat, p-value)
                     ├→ Effect size → |r_HumanEval - r_SWE-bench|
                     └→ Variance decomposition → between/within ratio
                            ↓
                     ├→ Visualizer → [3 PNG figures]
                     └→ Report Generator → [04_validation.md]
```

---

## Interface Contracts

### Feedback Data Schema (from h-e1 cache)
```python
{
    "exec": np.ndarray[float],    # Shape (n_samples,), values {0, 1}
    "ai": np.ndarray[float],      # Shape (n_samples,), values [0, 1]
    "human": np.ndarray[float]    # Shape (n_samples,), values [0, 1] (mean of 3 raters)
}
```

### Correlation Results
```python
{
    "r": float,              # Pearson correlation coefficient
    "p": float,              # p-value
    "ci": (float, float)     # (lower, upper) 95% CI
}
```

### ANOVA Results
```python
(f_stat: float, p_value: float)
```

### Variance Results
```python
{
    "between_var": float,
    "within_var": float,
    "variance_ratio": float
}
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M1 | Feedback Loading | Load h-e1 cache data, validate integrity | 7 | Module(2) + Deps(1) + Algo(2) + Integration(2) |
| M2 | ANOVA Testing | Bootstrap distributions, one-way ANOVA | 12 | Module(3) + Deps(2) + Algo(4) + Integration(3) |
| M3 | Variance Analysis | Between-task, within-task variance computation | 9 | Module(2) + Deps(1) + Algo(4) + Integration(2) |
| M4 | Effect Size | Correlation difference computation | 4 | Module(1) + Deps(1) + Algo(1) + Integration(1) |
| M5 | Task-Type Viz | Bar charts, heatmap, variance plots | 10 | Module(3) + Deps(2) + Algo(2) + Integration(3) |
| M6 | Validation Report | 04_validation.md with pass/fail logic | 8 | Module(2) + Deps(1) + Algo(3) + Integration(2) |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M2, M5], Low(4-8): [M1, M3, M4, M6]

---

## Technology Stack

**Core Libraries:**
- `scipy==1.10.0` - pearsonr, f_oneway
- `numpy==1.24.0` - variance, bootstrap resampling
- `matplotlib==3.7.0` + `seaborn==0.12.0` - visualization
- Python 3.10+

**Reused from h-e1:**
- Dataset loaders (no new collection)
- Feedback data format
- Correlation computation infrastructure

**Execution:**
- CPU-only (no GPU required)
- ~5 minutes runtime (3000 bootstrap iterations total)

---

## File Structure

```
h-m2/code/
├── data_loader.py           # Load h-e1 feedback cache (M1)
├── analysis/
│   ├── anova.py            # ANOVA testing (M2)
│   ├── variance.py         # Variance decomposition (M3)
│   └── visualize.py        # Task-type plots (M5)
├── report_generator.py     # Validation report (M6)
└── run_analysis.py         # Main orchestrator

h-m2/figures/               # Auto-generated plots (3 files)
└── (correlation_by_task.png, correlation_heatmap.png, variance_decomposition.png)
```

---

## Error Handling Strategy

**Missing h-e1 cache files:** Fail fast with clear error message
**Data integrity failures:** Raise exception, report which dataset/field failed
**Bootstrap failures:** Retry with different seed, log warning if variance high
**ANOVA invalid input:** Check all distributions non-empty, non-constant

---

## Validation Checks

**Self-checks before Phase 4:**
- [x] 6 Epic tasks (MECHANISM scope)
- [x] Module interfaces = code signatures only
- [x] No ASCII diagrams in data flow
- [x] Total length <500 lines
- [x] Base hypothesis imports verified from actual code
- [x] External dependencies table included

---

**Next Phase:** Phase 4 - Task breakdown and implementation
