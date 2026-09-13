# Configuration Design: h-m2

**Date:** 2026-08-25
**Hypothesis:** h-m2 (MECHANISM)
**Type:** Statistical analysis - ANOVA variance validation
**Architecture:** 03_architecture.md
**PRD:** 03_prd.md

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Config verified from h-e1 implementation
**Config Pattern Found:** Hardcoded values in run_experiment.py (no dataclass config)
**Pattern Used:** Hardcoded dict (matching h-e1 pattern)

---

## Applied Patterns (Archon KB)

Applied: Statistical analysis config pattern (bootstrap params, significance thresholds, reproducibility seed)

---

## Inherited Configuration (Base Hypothesis)

### h-e1 Settings (From Actual Code)

The following values are verified from h-e1/code/run_experiment.py:

```python
# From: h-e1/code/run_experiment.py (lines 44, 58)
n_samples = 50          # PoC reduced sample count
batch_size = 4          # Code generation batch size
max_tokens = 256        # Code generation token limit
seed = 42               # Human feedback simulation seed
```

**Note:** h-e1 used hardcoded values in run_experiment.py, no separate config.py file.

---

## M1: Feedback Loading Configuration

**Applied:** Standard file I/O defaults

```python
CONFIG_M1 = {
    # Path settings
    "h_e1_cache_dir": "/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_dl4c/docs/youra_research/.data_cache/feedback/h-e1",
    "datasets": ["humaneval", "mbpp", "swebench"],
    
    # Expected sample counts (from h-e1 collection)
    "expected_counts": {
        "humaneval": 50,
        "mbpp": 50,
        "swebench": 50
    },
    
    # Validation thresholds
    "allow_missing_values": False,
    "human_rating_range": (1.0, 5.0),
    "exec_score_range": (0.0, 1.0)
}
```

**Subtasks [2/2 used]:**

| ID | Subtask | Description |
|----|---------|-------------|
| M1-1 | Load h-e1 cache | Read exec/ai/human .npy files per dataset |
| M1-2 | Validate integrity | Check shapes, ranges, no NaN/Inf |

---

## M2: ANOVA Testing Configuration

**Applied:** Bootstrap resampling standard (1000 iterations per distribution)

```python
CONFIG_M2 = {
    # Bootstrap parameters
    "n_bootstrap": 1000,        # Iterations per dataset correlation distribution
    "seed": 42,                  # Reproducibility (inherited from h-e1)
    
    # Statistical test thresholds
    "alpha": 0.05,               # ANOVA significance threshold
    
    # Performance
    "parallel": False            # CPU-only, no parallelization needed for 3000 total iterations
}
```

**Subtasks [2/2 used]:**

| ID | Subtask | Description |
|----|---------|-------------|
| M2-1 | Bootstrap distributions | Resample correlation per dataset (1000×3) |
| M2-2 | One-way ANOVA | scipy.stats.f_oneway on 3 distributions |

---

## M3: Variance Analysis Configuration

**Applied:** Variance decomposition standard (between/within ratio)

```python
CONFIG_M3 = {
    # Variance ratio threshold (secondary criterion)
    "variance_ratio_threshold": 2.0,    # Between-task ≥ 2× within-task
}
```

**Subtasks [2/2 used]:**

| ID | Subtask | Description |
|----|---------|-------------|
| M3-1 | Between-task variance | np.var on 3 correlation values |
| M3-2 | Within-task variance | Mean of 3 bootstrap distribution variances |

---

## M4: Effect Size Configuration

**Applied:** Correlation difference (standard effect size for correlations)

```python
CONFIG_M4 = {
    # Effect size threshold (primary criterion)
    "min_effect_size": 0.3,     # Medium to large effect (Cohen's guidelines)
    
    # Comparison endpoints
    "comparison_datasets": ("humaneval", "swebench")  # Competitive vs realistic
}
```

**Subtasks [2/2 used]:**

| ID | Subtask | Description |
|----|---------|-------------|
| M4-1 | Compute difference | abs(r_humaneval - r_swebench) |
| M4-2 | Threshold check | effect_size > 0.3 |

---

## M5: Task-Type Visualization Configuration

**Applied:** matplotlib/seaborn publication defaults

```python
CONFIG_M5 = {
    # Figure settings
    "figure_size": (10, 6),
    "dpi": 300,
    "font_size": 12,
    
    # Color scheme
    "palette": "Set2",           # seaborn colorblind-safe palette
    
    # Output paths
    "figures_dir": "figures",
    "figure_names": {
        "correlation_by_task": "correlation_by_task.png",
        "correlation_heatmap": "correlation_heatmap.png",
        "variance_decomposition": "variance_decomposition.png"
    },
    
    # Heatmap settings
    "heatmap_cmap": "RdYlGn",    # Red-Yellow-Green for correlation values
    "heatmap_vmin": -1.0,
    "heatmap_vmax": 1.0,
    "annotate_cells": True
}
```

**Subtasks [2/2 used]:**

| ID | Subtask | Description |
|----|---------|-------------|
| M5-1 | Bar/scatter plots | Correlation by task with CI error bars |
| M5-2 | Heatmap | 3×3 grid: datasets × correlation pairs |

---

## M6: Validation Report Configuration

**Applied:** Standard markdown report template

```python
CONFIG_M6 = {
    # Report path
    "report_path": "04_validation.md",
    
    # Pass/fail criteria
    "primary_criteria": {
        "anova_p_threshold": 0.05,
        "min_effect_size": 0.3
    },
    
    "secondary_criteria": {
        "variance_ratio_threshold": 2.0,
        "predicted_pattern": {
            "humaneval": {"min_r": 0.8},
            "mbpp": {"min_r": 0.6, "max_r": 0.8},
            "swebench": {"max_r": 0.5}
        }
    },
    
    # Report sections
    "include_sections": [
        "summary_table",
        "statistical_tests",
        "pass_fail_status",
        "figure_references"
    ]
}
```

**Subtasks [2/2 used]:**

| ID | Subtask | Description |
|----|---------|-------------|
| M6-1 | Generate report | 04_validation.md with all sections |
| M6-2 | Pass/fail logic | Check primary criteria (ANOVA + effect size) |

---

## Master Configuration (run_analysis.py)

**Consolidated config for main runner:**

```python
CONFIG = {
    # Paths
    "base_dir": "/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_dl4c/docs/youra_research/h-m2",
    "h_e1_cache_dir": "/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_dl4c/docs/youra_research/.data_cache/feedback/h-e1",
    
    # Datasets
    "datasets": ["humaneval", "mbpp", "swebench"],
    
    # Statistical parameters
    "n_bootstrap": 1000,
    "seed": 42,
    "alpha": 0.05,
    
    # Thresholds
    "min_effect_size": 0.3,
    "variance_ratio_threshold": 2.0,
    
    # Visualization
    "figure_size": (10, 6),
    "dpi": 300,
    "palette": "Set2",
    
    # Output
    "figures_dir": "figures",
    "report_path": "04_validation.md"
}
```

---

## Self-Validation

**Quick Checks:**
- [x] ONE format only (hardcoded dict, matching h-e1 pattern)
- [x] No ASCII diagrams
- [x] KB pattern applied: Bootstrap resampling standard
- [x] Rationale only for non-standard values (none - all standard)
- [x] All subtask counts = 2 (within budget)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included
- [x] Inherited Configuration section with verified h-e1 values

**Base Hypothesis Checks:**
- [x] Read actual h-e1 code (run_experiment.py)
- [x] Field names verified from implementation (n_samples, batch_size, max_tokens, seed)
- [x] h-e1 pattern identified (hardcoded values, no dataclass)
- [x] Inherited Configuration section included

---

**Next Phase:** Phase 4 - Task breakdown and implementation
