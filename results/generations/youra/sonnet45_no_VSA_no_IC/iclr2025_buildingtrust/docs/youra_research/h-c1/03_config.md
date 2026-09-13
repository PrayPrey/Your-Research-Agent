# Configuration: H-C1

**Date:** 2026-08-19
**Hypothesis:** Coupling matrices differ across models (Mantel test r < 0.7 for ≥1 model pair)
**Type:** COMPARISON

Applied: Statistical comparison config pattern (hardcoded dict)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - new config design
**Config Files Found:** None - new config
**Pattern Used:** Hardcoded dict

---

## Configuration Schema

### config.py

```python
CONFIG = {
    "models": ["GPT-4", "Claude-3", "Llama-3"],
    "dimensions": ["truthfulness", "robustness", "fairness", "safety", "privacy"],
    "dataset": {
        "name": "TrustLLM",
        "samples_per_dim": 100,
        "seed": 42
    },
    "statistical": {
        "phi_threshold": 0.3,
        "p_threshold": 0.01,
        "mantel_perms": 10000,
        "bonferroni_alpha": 0.0167
    },
    "paths": {
        "data": "data/",
        "results": "results/",
        "figures": "figures/"
    }
}
```

---

## Task Configurations

### C-1: Data Pipeline [Complexity: 9, Budget: 5]

```python
DATA_CONFIG = {
    "source": "TrustLLM",
    "models": ["GPT-4", "Claude-3", "Llama-3"],
    "dimensions": ["truthfulness", "robustness", "fairness", "safety", "privacy"],
    "samples_per_dim": 100,
    "seed": 42,
    "binarize_threshold": 0.5
}
```

**Subtasks [5/5 used]:**
| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | TrustLLM loader | HuggingFace dataset loading for 3 models |
| C-1-2 | Stratified sampling | 100 samples per dimension (5 dims × 3 models) |
| C-1-3 | Label binarization | Convert scores to binary (pass/fail) |
| C-1-4 | Data validation | Check sample counts, class balance |
| C-1-5 | Data persistence | Save processed labels to disk |

---

### C-2: Coupling Matrix [Complexity: 10, Budget: 5]

```python
COUPLING_CONFIG = {
    "phi_threshold": 0.3,
    "p_threshold": 0.01,
    "dimension_pairs": 10,
    "matrix_size": 5
}
```

**Subtasks [5/5 used]:**
| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Contingency tables | Build 2×2 tables for 10 dimension pairs |
| C-2-2 | Phi coefficient | matthews_corrcoef for each pair |
| C-2-3 | Chi-square test | Significance testing via chi2_contingency |
| C-2-4 | Matrix construction | Build 5×5 symmetric matrix |
| C-2-5 | Matrix validation | Check symmetry, diagonal = 1.0 |

---

### C-3: Mantel Test [Complexity: 12, Budget: 5]

```python
MANTEL_CONFIG = {
    "perms": 10000,
    "method": "pearson",
    "tail": "two-tail",
    "bonferroni_alpha": 0.0167,
    "comparisons": [
        ("GPT-4", "Claude-3"),
        ("GPT-4", "Llama-3"),
        ("Claude-3", "Llama-3")
    ]
}
```

**Subtasks [5/5 used]:**
| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Mantel test wrapper | Call mantel.test with 10k permutations |
| C-3-2 | Pairwise comparison | Run 3 model pair comparisons |
| C-3-3 | Bonferroni correction | Apply corrected alpha = 0.0167 |
| C-3-4 | Results aggregation | Collect (r, p, z) for all pairs |
| C-3-5 | Significance flagging | Mark pairs with p < 0.0167 |

---

### C-4: Visualization [Complexity: 8, Budget: 5]

```python
VIZ_CONFIG = {
    "heatmap": {
        "cmap": "RdBu_r",
        "center": 0,
        "vmin": -1,
        "vmax": 1,
        "annot": True
    },
    "scatter": {
        "figsize": (8, 6),
        "alpha": 0.7,
        "add_regression": True
    },
    "output_formats": ["png", "pdf"]
}
```

**Subtasks [5/5 used]:**
| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Coupling heatmaps | 3 side-by-side matrices (one per model) |
| C-4-2 | Scatter plots | Pairwise phi value comparisons |
| C-4-3 | Mantel results plot | Bar chart of r values with significance markers |
| C-4-4 | Figure export | Save PNG/PDF to figures/ |
| C-4-5 | Figure validation | Check file existence, size |

---

### C-5: Integration [Complexity: 9, Budget: 5]

```python
EXPERIMENT_CONFIG = {
    "models": ["GPT-4", "Claude-3", "Llama-3"],
    "total_instances": 1500,
    "output_files": {
        "matrices": "results/coupling_matrices.npy",
        "mantel_results": "results/mantel_results.csv",
        "phi_stats": "results/phi_statistics.json",
        "validation": "04_validation.md"
    }
}
```

**Subtasks [5/5 used]:**
| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Pipeline orchestration | Load data → compute matrices → run Mantel |
| C-5-2 | Results collection | Aggregate all metrics into report |
| C-5-3 | Gate decision logic | PASS/PARTIAL/FAIL based on Mantel r |
| C-5-4 | Validation report | Generate 04_validation.md |
| C-5-5 | Artifact export | Save matrices, CSV, JSON |

---

### C-6: Gate Decision [Complexity: 6, Budget: 5]

```python
GATE_CONFIG = {
    "thresholds": {
        "pass": 0.7,
        "partial": 0.9
    },
    "p_threshold": 0.0167,
    "decision_logic": {
        "PASS": "r < 0.7 for ≥1 pair with p < 0.0167",
        "PARTIAL": "0.7 ≤ r < 0.9 for ≥1 pair",
        "FAIL": "r ≥ 0.9 for all pairs"
    }
}
```

**Subtasks [4/5 used]:**
| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Result parsing | Extract r, p values from mantel_results.csv |
| C-6-2 | Threshold comparison | Check r < 0.7 and p < 0.0167 conditions |
| C-6-3 | Gate assignment | Map to PASS/PARTIAL/FAIL |
| C-6-4 | Report formatting | Write decision to 04_validation.md |

---

## Hyperparameter Rationale

**Non-standard values only:**

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| mantel_perms | 10000 | PRD requirement for p-value precision |
| bonferroni_alpha | 0.0167 | Corrected α = 0.05/3 for 3 comparisons |
| samples_per_dim | 100 | PRD requirement for chi-square validity |

---

## Dependencies

```
# requirements.txt
numpy>=1.20
scipy>=1.7
scikit-learn>=1.0
mantel>=2.0
pandas>=1.3
matplotlib>=3.5
seaborn>=0.11
datasets>=2.0
```

---

## Notes

COMPARISON hypothesis - no baseline model, compares 3 models. All config values from PRD/architecture. Uses hardcoded dict (no dataclass needed for statistical analysis). Total subtask allocation: 29/30 used (1 under budget).
