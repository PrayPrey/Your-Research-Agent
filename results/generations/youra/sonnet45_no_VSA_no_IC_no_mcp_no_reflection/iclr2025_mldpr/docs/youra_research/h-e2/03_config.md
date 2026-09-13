# Configuration: h-e2

**Date:** 2026-08-28
**Hypothesis:** Velocity Decay Detection via Linear Regression
**Type:** EXISTENCE (Proof-of-Concept)
**Budget:** 4 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** New implementation from scratch
**Config Files Found:** None - new config
**Pattern Used:** Hardcoded dict (EXISTENCE minimal config)

---

## Applied Patterns

Applied: Standard scipy/pandas statistical analysis defaults

---

## A-1: Data Loading [Complexity: 8, Budget: 1]

### Configuration (Hardcoded Dict)

```python
DATA_CONFIG = {
    "benchmarks": ["imagenet", "glue", "squad-v1", "squad-v2"],
    "date_start": "2018-01-01",
    "date_end": "2024-12-31",
    "min_submissions": 100,
    "required_fields": ["date", "score", "model", "paper"]
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | PWC API Client | Fetch benchmark results, parse dates/scores |

---

## A-2: Core Detector [Complexity: 12, Budget: 1]

### Configuration (Hardcoded Dict)

```python
DETECTOR_CONFIG = {
    "window_days": 180,
    "velocity_threshold": 0.1,
    "min_points_per_window": 10,
    "pvalue_threshold": 0.05,
    "slope_to_monthly": 30
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | VelocityDecayDetector | Rolling window linregress with threshold detection |

---

## A-3: Baseline [Complexity: 5, Budget: 1]

### Configuration (Hardcoded Dict)

```python
BASELINE_CONFIG = {
    "window_days": 180,
    "improvement_threshold": 0.01
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Manual Inspection | Naive 6mo <1% improvement heuristic |

---

## A-4: Metrics [Complexity: 6, Budget: 1]

### Configuration (Hardcoded Dict)

```python
METRICS_CONFIG = {
    "pvalue_significance": 0.05,
    "cv_stability_threshold": 0.5,
    "significance_ratio_threshold": 0.5
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Gate Metrics | Detection success, CV, significance ratio |

---

## A-5: Visualization [Complexity: 9, Budget: 0]

Budget exhausted. No subtasks allocated.

**Implementation:** Direct matplotlib plotting in main.py (no module decomposition).

---

## A-6: Pipeline [Complexity: 7, Budget: 0]

Budget exhausted. No subtasks allocated.

**Implementation:** Orchestrate in main.py without decomposition.

---

## Experiment Settings

### Default Run Configuration

```python
EXPERIMENT_CONFIG = {
    "output_dir": "docs/youra_research/h-e2",
    "figures_dir": "docs/youra_research/h-e2/figures",
    "validation_report": "docs/youra_research/h-e2/04_validation.md",
    "plot_formats": ["png"]
}
```

### Gate Criteria

```python
GATE_CONFIG = {
    "detection_success": True,
    "cv_max": 0.5,
    "significance_ratio_min": 0.5
}
```

---

## Self-Validation

- [x] ONE format only (hardcoded dict)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Rationale only for non-standard values (all standard)
- [x] Subtask count within budget (4/4 used)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included

**EXISTENCE PoC Mode:** Single fixed config, no hyperparameter variations, minimal epochs/windows.
