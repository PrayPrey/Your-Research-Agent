# Configuration: h-m1

**Hypothesis:** h-m1  
**Type:** MECHANISM (EXISTENCE)  
**Gate:** MUST_WORK (accuracy ≥ 70%)  
**Date:** 2026-08-24  

Applied: Hardcoded dict pattern, sklearn defaults

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Verified h-e1 actual config implementation  
**Config Files Found**: `docs/youra_research/h-e1/code/config.py`  
**Pattern Used**: Hardcoded dict (CONFIG global)

---

## Inherited Configuration (Base Hypothesis)

### Config Pattern (From h-e1 Actual Code)

```python
# From: docs/youra_research/h-e1/code/config.py (ACTUAL CODE)
CONFIG = {
    "data": {...},
    "output": {...},
    "seed": 42
}
```

**Verified from**: h-e1 actual implementation (hardcoded dict, no dataclass)

---

## M1-1: Data Loading [Complexity: 6, Budget: 2]

Applied: Standard NumPy data loading

### Configuration (Python Dict)

```python
CONFIG = {
    "data": {
        "h_e1_results_path": "/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_buildingtrust/docs/youra_research/h-e1/code/results/entropy_results.json",
        "entity_label": 0,
        "non_entity_label": 1
    }
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M1-1-1 | Load JSON | Read h-e1 entropy_results.json |
| M1-1-2 | Extract arrays | Convert to NumPy arrays (X, y) |

---

## M1-2: Train/Test Split [Complexity: 4, Budget: 2]

Applied: sklearn.train_test_split defaults

### Configuration (Python Dict)

```python
CONFIG = {
    "split": {
        "train_ratio": 0.8,
        "test_size": 0.2,
        "stratify": True,
        "random_state": 42
    }
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M1-2-1 | Import sklearn | Use train_test_split |
| M1-2-2 | Apply split | 80/20 stratified split |

---

## M1-3: Threshold Classifier [Complexity: 9, Budget: 2]

Applied: Grid search pattern (NumPy linspace)

### Configuration (Python Dict)

```python
CONFIG = {
    "classifier": {
        "threshold_min": 0.0,
        "threshold_max": 1.0,
        "threshold_steps": 101
    }
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M1-3-1 | Grid search | Loop 101 thresholds on train set |
| M1-3-2 | Select best | Return threshold with max accuracy |

---

## M1-4: Test Evaluation [Complexity: 7, Budget: 2]

Applied: sklearn.metrics defaults

### Configuration (Python Dict)

```python
CONFIG = {
    "evaluation": {
        "metrics": ["accuracy", "precision", "recall", "f1"]
    }
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M1-4-1 | Apply threshold | Predict on test set |
| M1-4-2 | Compute metrics | sklearn.metrics functions |

---

## M1-5: Gate Check [Complexity: 4, Budget: 2]

Applied: Boolean comparison

### Configuration (Python Dict)

```python
CONFIG = {
    "gate": {
        "threshold": 0.70
    }
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M1-5-1 | Compare accuracy | test_acc >= 0.70 |
| M1-5-2 | Return bool | PASS/FAIL status |

---

## M1-6: Baseline Comparison [Complexity: 5, Budget: 2]

Applied: NumPy random.choice

### Configuration (Python Dict)

```python
CONFIG = {
    "baseline": {
        "random_state": 42
    }
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M1-6-1 | Random classifier | np.random.choice([0, 1]) |
| M1-6-2 | Compute accuracy | Compare baseline vs proposed |

---

## M1-7: Visualizations [Complexity: 10, Budget: 2]

Applied: matplotlib defaults

### Configuration (Python Dict)

```python
CONFIG = {
    "visualization": {
        "figures_dir": "./figures/",
        "figure_dpi": 300,
        "figure_format": "png"
    }
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M1-7-1 | Plot functions | 3 plots (threshold curve, confusion matrix, distributions) |
| M1-7-2 | Save files | Write PNG to figures/ |

---

## M1-8: Results Reporting [Complexity: 5, Budget: 2]

Applied: JSON stdlib

### Configuration (Python Dict)

```python
CONFIG = {
    "output": {
        "results_file": "./results/classification_results.json",
        "figures_dir": "./figures/"
    }
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M1-8-1 | Collect results | Dict with metrics + gate status |
| M1-8-2 | Save JSON | json.dump to results file |

---

## Complete Configuration (Copy-Paste Ready)

```python
"""Configuration for h-m1 threshold classifier experiment."""

CONFIG = {
    # Data Configuration
    "data": {
        "h_e1_results_path": "/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_buildingtrust/docs/youra_research/h-e1/code/results/entropy_results.json",
        "entity_label": 0,
        "non_entity_label": 1
    },

    # Train/Test Split
    "split": {
        "train_ratio": 0.8,
        "test_size": 0.2,
        "stratify": True,
        "random_state": 42
    },

    # Threshold Classifier
    "classifier": {
        "threshold_min": 0.0,
        "threshold_max": 1.0,
        "threshold_steps": 101
    },

    # Evaluation Metrics
    "evaluation": {
        "metrics": ["accuracy", "precision", "recall", "f1"]
    },

    # Gate Check
    "gate": {
        "threshold": 0.70
    },

    # Baseline Comparison
    "baseline": {
        "random_state": 42
    },

    # Visualization
    "visualization": {
        "figures_dir": "./figures/",
        "figure_dpi": 300,
        "figure_format": "png"
    },

    # Output
    "output": {
        "results_file": "./results/classification_results.json",
        "figures_dir": "./figures/"
    },

    # Reproducibility
    "seed": 42
}
```

---

## Configuration Notes

1. **h_e1_results_path**: Absolute path verified from h-e1 actual code structure
2. **Labels**: 0=entity-error, 1=non-entity-error (PRD spec)
3. **threshold_steps**: 101 points for [0.00, 0.01, ..., 1.00] grid
4. **seed=42**: Consistent with h-e1 base hypothesis

---

**Config Version:** 1.0  
**Status:** Ready for Phase 4 Implementation
