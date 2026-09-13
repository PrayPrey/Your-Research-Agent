# Configuration Design: H-E1
**Hypothesis:** Structural Signal Existence in LLM Code Coverage Prediction
**Type:** EXISTENCE (PoC)
**Date:** 2026-03-18

Applied: Minimal PoC experiment pattern, scikit-learn standard pipeline

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: New implementation from scratch
**Config Files Found**: None - new config design
**Pattern Used**: Hardcoded dict (simplest for PoC)

---

## EXISTENCE PoC Configuration

This is an EXISTENCE hypothesis requiring minimal configuration for proof-of-concept validation. The config uses single fixed values with no hyperparameter variations or subtask decomposition.

### Configuration (Hardcoded Dict)

```python
# code/config.py

CONFIG = {
    # Dataset
    "dataset_path": "coverage-eval",
    "num_tasks": 164,

    # Features
    "num_features": 12,
    "scaler_type": "StandardScaler",

    # Model
    "ridge_alpha": 1.0,
    "random_seed": 42,

    # Thresholds
    "median_ratio_threshold": 0.5,
    "task_coverage_threshold": 0.7,
    "delta_r2_threshold": 0.1,
    "vif_threshold": 5.0,

    # Output
    "output_dir": "docs/youra_research/h-e1",
    "figures_dir": "docs/youra_research/h-e1/figures",
}
```

---

## Task-Specific Configurations

### A-1: Setup & Data [Complexity: 8, Budget: 3]

**Applied**: Standard Python data loading patterns

```python
DATA_CONFIG = {
    "dataset_repo": "https://github.com/microsoft/coverage-eval.git",
    "clone_path": "coverage-eval",
    "data_format": "json",
    "coverage_key": "coverage",
    "statement_coverage_key": "statement_coverage",
    "branch_coverage_key": "branch_coverage",
}
```

**Subtasks [3/3 used]**:
| ID | Subtask | Description |
|----|---------|-------------|
| C-A-1-1 | Environment setup | Install radon, tree-sitter, sklearn, clone CoverageEval |
| C-A-1-2 | DataLoader class | Implement CoverageEvalLoader with problem parsing |
| C-A-1-3 | Data validation | Verify coverage data ranges, detect anomalies |

---

### A-2: Feature Extraction [Complexity: 12, Budget: 3]

**Applied**: Standard radon + tree-sitter patterns

```python
FEATURE_CONFIG = {
    "radon_metrics": ["complexity", "sloc", "lloc", "comments"],
    "ast_metrics": ["nesting_depth", "branch_density", "ast_entropy",
                    "function_count", "early_returns", "exception_handlers",
                    "defensive_branches", "code_complexity_ratio"],
    "tree_sitter_language": "python",
    "normalization": "StandardScaler",
    "missing_value_strategy": "task_median",
    "outlier_winsorize": [1, 99],  # percentiles
}
```

**Subtasks [3/3 used]**:
| ID | Subtask | Description |
|----|---------|-------------|
| C-A-2-1 | Radon integration | Extract cyclomatic complexity, SLOC, LLOC, comment ratio |
| C-A-2-2 | Tree-sitter parser | Extract AST-based 8 metrics |
| C-A-2-3 | Feature preprocessing | StandardScaler, median imputation, winsorization |

---

### A-3: Baseline Model [Complexity: 5, Budget: 3]

**Applied**: Standard sklearn baseline patterns

```python
BASELINE_CONFIG = {
    "model_type": "TaskLevelMean",
    "group_by": "task_id",
    "metric": "r2_score",
}
```

**Subtasks [3/3 used]**:
| ID | Subtask | Description |
|----|---------|-------------|
| C-A-3-1 | TaskLevelBaseline class | Group by task_id, compute mean coverage |
| C-A-3-2 | Fit method | Store task-level means |
| C-A-3-3 | Evaluation | R² score on held-out tasks |

---

### A-4: Proposed Model [Complexity: 9, Budget: 3]

**Applied**: sklearn Ridge regression defaults

```python
PROPOSED_MODEL_CONFIG = {
    "model_type": "Ridge",
    "alpha": 1.0,
    "solver": "auto",
    "random_state": 42,
    "fit_intercept": True,
    "normalize": False,  # Use StandardScaler instead
}
```

**Subtasks [3/3 used]**:
| ID | Subtask | Description |
|----|---------|-------------|
| C-A-4-1 | StructuralCoveragePredictor class | Ridge regression wrapper |
| C-A-4-2 | Feature engineering | Combine 12 structural features + task difficulty |
| C-A-4-3 | Training pipeline | Fit Ridge with StandardScaler preprocessing |

---

### A-5: Variance Analysis [Complexity: 14, Budget: 3]

**Applied**: Standard hierarchical regression analysis

```python
ANALYSIS_CONFIG = {
    "hierarchical_models": [
        {"name": "Model1", "formula": "Coverage ~ TaskDifficulty"},
        {"name": "Model2", "formula": "Coverage ~ TaskDifficulty + StructuralFeatures"},
        {"name": "Model3", "formula": "Coverage ~ TaskDifficulty + StructuralFeatures + SemanticCluster"},
    ],
    "cross_validation": "LeaveOneGroupOut",
    "cv_groups": "task_id",
    "bootstrap_iterations": 1000,
    "confidence_level": 0.95,
}
```

**Subtasks [3/3 used]**:
| ID | Subtask | Description |
|----|---------|-------------|
| C-A-5-1 | Hierarchical R² decomposition | Fit 3 models, compute R²_marginal / R²_conditional |
| C-A-5-2 | VIF computation | Variance Inflation Factor for multicollinearity check |
| C-A-5-3 | Bootstrap CI | 95% confidence interval for median ratio |

---

### A-6: Visualization [Complexity: 10, Budget: 3]

**Applied**: matplotlib/seaborn standard patterns

```python
VIS_CONFIG = {
    "figure_dpi": 300,
    "figure_format": "png",
    "style": "seaborn-v0_8-darkgrid",
    "color_palette": "Set2",
    "figures": [
        {"name": "gate_metrics", "type": "bar", "threshold_line": 0.5},
        {"name": "ratio_distribution", "type": "histogram", "bins": 30},
        {"name": "feature_importance", "type": "bar", "top_k": 12},
        {"name": "complexity_vs_coverage", "type": "scatter", "alpha": 0.6},
        {"name": "hierarchical_r2", "type": "stacked_bar"},
    ],
}
```

**Subtasks [3/3 used]**:
| ID | Subtask | Description |
|----|---------|-------------|
| C-A-6-1 | Gate metrics figure | Bar chart with 0.5 threshold and 95% CI error bars |
| C-A-6-2 | Diagnostic figures | Ratio distribution, feature importance, complexity scatter |
| C-A-6-3 | Hierarchical R² plot | Stacked bar chart showing variance decomposition |

---

### A-7: Integration [Complexity: 11, Budget: 3]

**Applied**: Standard Python experiment pipeline

```python
PIPELINE_CONFIG = {
    "execution_order": [
        "load_data",
        "extract_features",
        "train_baseline",
        "train_proposed",
        "evaluate",
        "visualize",
        "generate_report",
    ],
    "logging_level": "INFO",
    "checkpoint_steps": True,
    "save_intermediate": True,
}
```

**Subtasks [3/3 used]**:
| ID | Subtask | Description |
|----|---------|-------------|
| C-A-7-1 | Main experiment script | run_experiment.py with all modules integrated |
| C-A-7-2 | Validation report generator | Create 04_validation.md with gate status |
| C-A-7-3 | Error handling | Logging, exception handling, data integrity checks |

---

## Rationale for Non-Standard Values

All configuration values use standard defaults from scikit-learn, radon, and tree-sitter libraries. No non-standard values require justification for this EXISTENCE PoC.

---

## Self-Validation

### Quick Checks
- [x] ONE format only (Hardcoded dict)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Rationale only for non-standard values (none required)
- [x] Subtask count within budget (3 per task)
- [x] Total length < 400 lines
- [x] "Codebase Analysis (Serena)" section included

### Serena MCP Validation
- [x] Green-field project → Serena skip acceptable (noted in Codebase Analysis)

### EXISTENCE PoC Checks
- [x] Single fixed config (no variations)
- [x] Default values from libraries
- [x] 1 seed (42)
- [x] No hyperparameter grid
- [x] No ablation configs

---

*Configuration designed for Phase 4 implementation | EXISTENCE PoC for H-E1*
