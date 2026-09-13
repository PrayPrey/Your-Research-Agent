# Configuration Specification
# H-C1: Tactic Budget Equalization Feasibility Analysis

**Version**: 1.0  
**Date**: 2026-08-20  
**Status**: Draft

---

## Configuration Format

**Pattern**: Hardcoded dictionary constants (no dataclass needed for single-script analysis)

**Rationale**: One-off statistical analysis with no hyperparameter tuning, no subtask decomposition required.

---

## Path Configuration

```python
# File paths (relative to project root)
PATHS = {
    "input_csv": "docs/youra_research/h-e1/code/data/results/results.csv",
    "output_dir": "docs/youra_research/h-c1/code/data/results",
    "summary_json": "docs/youra_research/h-c1/code/data/results/summary.json",
    "figure_png": "docs/youra_research/h-c1/code/data/results/tactic_budget_analysis.png",
    "validation_report": "docs/youra_research/h-c1/04_validation.md",
}
```

---

## Statistical Configuration

```python
# Decision tree thresholds for budget recommendation
BUDGET_CONFIG = {
    "cv_thresholds": [0.5, 1.0],  # CV cutoffs: [mean+1σ, mean+1.4σ]
    "multipliers": [1.0, 1.4],    # Std dev multipliers per threshold
    "confidence_level": 0.95,      # For CI estimation (t-distribution)
    "min_sample_size": 20,         # Warning threshold (N < 20)
}

# Gate criterion (from PRD FR-4)
GATE_CONFIG = {
    "cv_threshold": 1.0,           # CV ≤ 1.0 → PASS
    "coverage_target": 0.70,       # Secondary: ≥70% baseline coverage
}

# Outlier detection (IQR rule)
OUTLIER_CONFIG = {
    "iqr_multiplier": 1.5,         # Q3 + 1.5×IQR (box plot standard)
}
```

---

## Visualization Configuration

```python
# Matplotlib settings for 3-panel figure
VIZ_CONFIG = {
    "figure_size": (15, 4),        # Width=15in, Height=4in
    "dpi": 150,                    # High-res for publication
    "histogram": {
        "bins": 15,                # Adaptive bins (sturges rule)
        "alpha": 0.7,              # Bar transparency
        "edgecolor": "black",
    },
    "budget_line": {
        "color": "red",
        "linestyle": "--",
        "linewidth": 2,
        "label": "Budget",
    },
    "mean_line": {
        "color": "blue",
        "linestyle": "-",
        "linewidth": 2,
        "label": "Mean",
    },
    "ecdf": {
        "marker": "o",
        "markersize": 4,
        "linestyle": "-",
    },
}
```

---

## Data Validation Configuration

```python
# Input filtering (from PRD FR-1)
FILTER_CONFIG = {
    "outcome": "SOLVED",           # Only solved problems
    "require_tactic_count": True,  # tactic_count.notna()
    "expected_n": 32,              # H-E1 baseline sample size
}

# Data provenance
PROVENANCE_CONFIG = {
    "hash_algorithm": "sha256",    # CSV integrity check
    "timestamp_format": "iso8601", # RFC 3339
}
```

---

## Reproducibility Configuration

```python
# No random seed needed (deterministic analysis)
# Bootstrap CI uses scipy.stats.t for closed-form solution
REPRODUCIBILITY = {
    "scipy_seed": None,            # Not applicable (no resampling)
    "numpy_seed": None,            # Not applicable (descriptive stats only)
}
```

---

## Usage Example

```python
# In analyze_tactic_budget.py

from pathlib import Path

# Path constants
INPUT_CSV = Path("docs/youra_research/h-e1/code/data/results/results.csv")
OUTPUT_DIR = Path("docs/youra_research/h-c1/code/data/results")
SUMMARY_JSON = OUTPUT_DIR / "summary.json"
FIGURE_PNG = OUTPUT_DIR / "tactic_budget_analysis.png"

# Statistical thresholds
CV_THRESHOLD = 1.0
CONFIDENCE_LEVEL = 0.95
IQR_MULTIPLIER = 1.5

# Visualization
FIGURE_SIZE = (15, 4)
DPI = 150
BINS = 15

# Budget decision tree
def recommend_budget(mean: float, std: float, cv: float) -> tuple[int, str]:
    if cv <= 0.5:
        budget = math.ceil(mean + std)
        estimator = "mean+1σ"
    elif cv <= 1.0:
        budget = math.ceil(mean + 1.4 * std)
        estimator = "mean+1.4σ"
    else:
        budget = None
        estimator = "unreliable"
    return budget, estimator
```

---

## Validation

**Constraints**:
- Input CSV must contain columns: `problem_id`, `outcome`, `tactic_count`
- Sample size N ≥ 20 (warn if below, fail if N < 15)
- Budget recommendation only defined for CV ≤ 1.0
- Figure generation requires matplotlib 3.7+

**Expected Values (from H-E1)**:
- N = 32
- Mean ≈ 9.2
- Std ≈ 4.1
- CV ≈ 0.45
- Budget = 15 (mean + 1.4σ)
- Gate: PASS

---

## Dependencies

```txt
pandas==2.0.3
numpy==1.24.4
scipy==1.11.2
matplotlib==3.7.2
```

No heavy dependencies (no torch, no transformers, no Lean runtime).

---

## Notes

**EXISTENCE Hypothesis**: Single fixed configuration (no hyperparameter grid, no subtasks).

**No Training**: Purely descriptive statistics (no model parameters, no checkpoints).

**Deterministic**: Output is fully reproducible (no randomness except optional bootstrap CI, which uses t-distribution instead).

**Copy-Paste Ready**: All constants are standalone Python dicts/values.

---

## Self-Validation Checklist

- [x] ONE format only (hardcoded dict)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Rationale only for non-standard values
- [x] Total length < 400 lines
- [x] Codebase Analysis section included
- [x] Green-field project (no base hypothesis)
- [x] EXISTENCE rules: single config, no variations, no subtasks
