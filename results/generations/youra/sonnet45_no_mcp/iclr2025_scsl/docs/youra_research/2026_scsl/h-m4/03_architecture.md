# System Architecture: H-M4 Geometry-Phenotype Coupling

**Project:** H-M4 Implementation
**Date:** 2026-04-24
**Author:** Architecture Agent
**Hypothesis Type:** MECHANISM (FULL tier)
**Task Budget:** 6-12 Epic tasks, 30 total

---

## Codebase Analysis (Serena)

**Base Hypothesis Analysis (h-m3):**

Analyzed existing codebase from h-m3:
- `code/curvature/` - Hessian computation, Marchenko-Pastur outlier detection
- `code/metrics/alignment.py` - A(w) alignment metric computation
- `code/data/waterbirds.py` - Dataset loading with group labels
- `code/data/minority_gradients.py` - Per-group gradient extraction
- `code/models/resnet.py` - ResNet-50 wrapper for Waterbirds

**Key Findings:**
- Curvature computation pipeline is stable and validated across h-m1, h-m2, h-m3
- Alignment metric A(w) implementation proven in h-m2 (minority alignment 0.844)
- Waterbirds data loader handles 4-group split correctly
- All prerequisite code is production-ready for reuse

**Import Patterns (from actual code):**
```python
from curvature.marchenko_pastur import detect_outlier_eigenvalues
from metrics.alignment import compute_alignment_metric
from data.minority_gradients import extract_group_gradients
from data.waterbirds import get_waterbirds_dataloader
```

---

## Architecture Overview

### Design Philosophy

**Reuse-First Architecture:**
- Maximum code reuse from h-m1 (curvature), h-m2 (alignment), h-m3 (validated pipeline)
- New functionality: Path sampling and correlation analysis only
- Minimal novelty to reduce implementation risk

**Applied:** Layered Architecture Pattern (Archon KB)
- Separation: Data → Metrics → Analysis → Visualization
- Clear boundaries enable independent testing
- Reused components stay untouched

---

## Module Structure

### Module 1: Path Sampling (`path_sampling/`)

**Purpose:** Sample checkpoints along mode-connected paths between ERM and DRO endpoints

**Files:**
- `fge_sampler.py` - Fast Geometric Ensembling path sampling
- `linear_sampler.py` - Linear interpolation baseline
- `checkpoint_loader.py` - Load and validate endpoint checkpoints

**Applied:** Strategy Pattern (Archon KB)
- Abstract `PathSampler` interface with `sample()` method
- Concrete implementations: `FGESampler`, `LinearSampler`
- Easy to add new path types (e.g., Bezier curves)

### Module 2: Metrics (`metrics/`)

**Purpose:** Compute A(w) and WGA for each checkpoint

**Files:**
- `alignment.py` - **REUSED FROM H-M2** (A(w) computation)
- `wga_evaluator.py` - Worst-group accuracy evaluation
- `group_accuracy.py` - Per-group accuracy computation

**Applied:** Composition Pattern (Archon KB)
- `WGAEvaluator` composes `GroupAccuracy` for each group
- Reuses `compute_alignment_metric()` from h-m2 unchanged

### Module 3: Analysis (`analysis/`)

**Purpose:** Correlation analysis and statistical tests

**Files:**
- `correlation.py` - Spearman correlation with p-value
- `statistical_tests.py` - Significance testing
- `results_aggregator.py` - Combine FGE and linear results

**Applied:** Data Analysis Pipeline Pattern (Archon KB)
- Input: Arrays of A(w) and WGA values
- Processing: Correlation, p-value, confidence intervals
- Output: Statistical results dictionary

### Module 4: Visualization (`visualization/`)

**Purpose:** Generate all required figures

**Files:**
- `coupling_plot.py` - Scatter plot with regression (A(w) vs WGA)
- `trajectory_plot.py` - Path trajectory (α vs metrics dual axes)
- `comparison_plot.py` - FGE vs linear side-by-side
- `group_accuracy_plot.py` - 4-group accuracy along path

**Applied:** Template Method Pattern (Archon KB)
- Base `PlotGenerator` with `generate()` template
- Concrete plotters override `_prepare_data()` and `_create_figure()`

### Module 5: Experiments (`experiments/`)

**Purpose:** Main experiment orchestration

**Files:**
- `run_coupling_experiment.py` - Main entry point
- `config.py` - Experiment configuration (dataclass)
- `validator.py` - Input validation and sanity checks

**Applied:** Facade Pattern (Archon KB)
- `CouplingExperiment` facade coordinates all modules
- Simple interface: `experiment.run()` executes full pipeline

---

## File Structure

```
h-m4/code/
├── path_sampling/
│   ├── __init__.py
│   ├── fge_sampler.py          # FGE path sampling (NEW)
│   ├── linear_sampler.py       # Linear interpolation (NEW)
│   └── checkpoint_loader.py    # Endpoint loading (NEW)
├── metrics/
│   ├── __init__.py
│   ├── alignment.py            # REUSED from h-m2 (A(w) computation)
│   ├── wga_evaluator.py        # WGA evaluation (NEW)
│   └── group_accuracy.py       # Per-group accuracy (NEW)
├── analysis/
│   ├── __init__.py
│   ├── correlation.py          # Spearman correlation (NEW)
│   ├── statistical_tests.py   # P-value tests (NEW)
│   └── results_aggregator.py  # Results aggregation (NEW)
├── visualization/
│   ├── __init__.py
│   ├── coupling_plot.py        # Scatter plot (NEW)
│   ├── trajectory_plot.py      # Path trajectory (NEW)
│   ├── comparison_plot.py      # FGE vs linear (NEW)
│   └── group_accuracy_plot.py  # Group accuracy (NEW)
├── experiments/
│   ├── __init__.py
│   ├── run_coupling_experiment.py  # Main script (NEW)
│   ├── config.py               # Config dataclass (NEW)
│   └── validator.py            # Input validation (NEW)
├── data/
│   └── waterbirds.py           # REUSED from h-m3
├── curvature/
│   └── marchenko_pastur.py     # REUSED from h-m1
└── tests/
    ├── test_path_sampling.py
    ├── test_metrics.py
    ├── test_analysis.py
    └── test_integration.py
```

---

## External Dependencies

**From h-m1:**
```python
from curvature.marchenko_pastur import (
    detect_outlier_eigenvalues,
    compute_hessian_eigenvalues
)
```

**From h-m2:**
```python
from metrics.alignment import compute_alignment_metric
from data.minority_gradients import extract_group_gradients
```

**From h-m3:**
```python
from data.waterbirds import get_waterbirds_dataloader
from models.resnet import ResNet50Wrapper
```

**Verification:** All imports verified from actual h-m3 code/ directory structure

---

## Proposed Epic Tasks

### Epic E-1: Path Sampling Module (Complexity: 14/20 = HIGH)
**Module:** path_sampling/
**Description:** Implement FGE and linear interpolation checkpoint sampling
**Complexity Breakdown:**
- Module Size: 3/5 (3 files, ~300 LOC)
- Dependencies: 3/5 (torch checkpoints, model architecture)
- Algorithm: 4/5 (parameter interpolation, validation)
- Integration: 4/5 (load endpoints from h-e1)

**Subtasks:** 4 (see 03_logic.md)

### Epic E-2: WGA Evaluation Module (Complexity: 12/20 = MEDIUM-HIGH)
**Module:** metrics/wga_evaluator.py, metrics/group_accuracy.py
**Description:** Evaluate worst-group accuracy for each checkpoint
**Complexity Breakdown:**
- Module Size: 2/5 (2 files, ~200 LOC)
- Dependencies: 3/5 (Waterbirds loader, group labels)
- Algorithm: 3/5 (min over group accuracies)
- Integration: 4/5 (reuse h-m3 data loader)

**Subtasks:** 3 (see 03_logic.md)

### Epic E-3: A(w) Computation Integration (Complexity: 8/20 = MEDIUM-LOW)
**Module:** metrics/alignment.py (REUSED)
**Description:** Integrate h-m2 alignment metric computation
**Complexity Breakdown:**
- Module Size: 1/5 (reuse existing)
- Dependencies: 2/5 (h-m1 curvature, h-m2 alignment)
- Algorithm: 1/5 (already implemented)
- Integration: 4/5 (adapt for checkpoint iteration)

**Subtasks:** 2 (integration adapters only)

### Epic E-4: Correlation Analysis Module (Complexity: 10/20 = MEDIUM)
**Module:** analysis/
**Description:** Spearman correlation and statistical tests
**Complexity Breakdown:**
- Module Size: 3/5 (3 files, ~250 LOC)
- Dependencies: 2/5 (scipy.stats)
- Algorithm: 2/5 (correlation, p-value)
- Integration: 3/5 (aggregate FGE and linear results)

**Subtasks:** 3 (see 03_logic.md)

### Epic E-5: Visualization Module (Complexity: 16/20 = HIGH)
**Module:** visualization/
**Description:** Generate all required figures (4 plot types)
**Complexity Breakdown:**
- Module Size: 4/5 (4 files, ~400 LOC)
- Dependencies: 3/5 (matplotlib, seaborn)
- Algorithm: 4/5 (regression lines, dual axes)
- Integration: 5/5 (combine all metrics)

**Subtasks:** 4 (see 03_logic.md)

### Epic E-6: Experiment Orchestration (Complexity: 11/20 = MEDIUM)
**Module:** experiments/
**Description:** Main experiment script and configuration
**Complexity Breakdown:**
- Module Size: 3/5 (3 files, ~300 LOC)
- Dependencies: 3/5 (all modules)
- Algorithm: 2/5 (pipeline orchestration)
- Integration: 3/5 (coordinate modules)

**Subtasks:** 3 (see 03_logic.md)

### Epic E-7: Validation Reporting (Complexity: 9/20 = MEDIUM-LOW)
**Module:** experiments/validator.py + reporting
**Description:** Generate Phase 4 validation report
**Complexity Breakdown:**
- Module Size: 2/5 (2 files, ~200 LOC)
- Dependencies: 2/5 (results from analysis)
- Algorithm: 2/5 (format results, check gates)
- Integration: 3/5 (aggregate all outputs)

**Subtasks:** 2 (see 03_logic.md)

---

## Task Summary

**Epic Tasks:** 7 (within 6-12 range for FULL tier)
**Estimated Subtasks:** 21 (from complexity allocation)
**Infrastructure Tasks:** 2 (data + environment)
**Total Estimated:** 30 tasks (exact FULL tier budget)

**Complexity Distribution:**
- Very High (18-20): 0 tasks
- High (14-17): 2 tasks (E-1, E-5)
- Medium (9-13): 4 tasks (E-2, E-4, E-6, E-7)
- Low (4-8): 1 task (E-3)

---

## Integration Points

### With h-e1:
- Load ERM checkpoint: `h-e1/checkpoints/erm_final.pt`
- Load DRO checkpoint: `h-e1/checkpoints/dro_final.pt`

### With h-m1:
- Import: `curvature.marchenko_pastur.detect_outlier_eigenvalues()`
- Import: `curvature.marchenko_pastur.compute_hessian_eigenvalues()`

### With h-m2:
- Import: `metrics.alignment.compute_alignment_metric()`
- Import: `data.minority_gradients.extract_group_gradients()`

### With h-m3:
- Import: `data.waterbirds.get_waterbirds_dataloader()`
- Import: `models.resnet.ResNet50Wrapper`

---

## Testing Strategy

**Unit Tests (per module):**
- `tests/test_path_sampling.py` - Interpolation correctness
- `tests/test_metrics.py` - WGA computation
- `tests/test_analysis.py` - Correlation calculation
- `tests/test_visualization.py` - Figure generation

**Integration Tests:**
- `tests/test_integration.py` - End-to-end pipeline

**Validation Checks:**
- A(w) values in [0, 1]
- WGA values in [0, 1]
- Correlation statistical significance

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Checkpoint loading failures | Validation step before sampling |
| Memory overflow (M=20 models) | Load checkpoints sequentially, not all at once |
| Correlation computation errors | scipy.stats error handling |
| Missing h-e1 checkpoints | Fallback: Document in validation report |

---

*Architecture v1.0 | Generated for Phase 3 Implementation Planning*
*Applied patterns: Layered Architecture, Strategy, Composition, Facade, Template Method*
