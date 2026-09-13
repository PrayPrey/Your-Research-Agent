# Configuration: H-E1 Spectral Memory Horizon Stability

**Hypothesis**: EXISTENCE PoC - CV(H_spec) < 0.3 across 1000 random sequences
**Type**: Measurement/Analysis (no training)
**Date**: 2026-03-27

Applied: Python dataclass config pattern (verified from archive h-e1 codebase)

---

## Codebase Analysis (Serena)

**Project Type**: green-field (with archive reference)
**Status**: Archive config files found - pattern verified from `_archive/20260327T191752_routing_recovery/h-e1/code/config.py`
**Config Files Found**: Archive pattern uses `@dataclass` with grouped fields (Model, Dataset, Evaluation, Output, Gate)
**Pattern Used**: dataclass

---

## A-1: Project Setup [Complexity: 5, Budget: 1 subtask]

Applied: Standard Python dataclass config pattern

### Configuration (Python Dataclass)

```python
# code/config.py
from dataclasses import dataclass


@dataclass
class ExperimentConfig:
    # Model
    model_id: str = "state-spaces/mamba-1.4b"
    model_370m_id: str = "state-spaces/mamba-370m"
    tokenizer_id: str = "EleutherAI/gpt-neox-20b"

    # Measurement
    num_samples: int = 1000
    seq_length: int = 512
    seed: int = 42

    # Gate condition
    cv_threshold: float = 0.3

    # Compute
    device: str = "cuda"
    dtype: str = "float32"  # Non-standard: float32 for stability; float64 for eigenvalue precision override

    # Output
    figures_dir: str = "figures"
    results_path: str = "results.yaml"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | ExperimentConfig | Write `code/config.py` with dataclass above; create `figures/` directory at runtime |

---

## A-5: Visualization & Results [Complexity: 9, Budget: 1 subtask]

Applied: Standard YAML results schema pattern

### Results Output Schema (results.yaml)

```yaml
# results.yaml - written by save_results()
hypothesis: "h-e1"
model_id: "state-spaces/mamba-1.4b"
num_samples: 1000
seq_length: 512
seed: 42

# Primary gate metric
cv: 0.0          # float - coefficient of variation
gate_pass: false # bool  - true if cv < cv_threshold

# Distribution statistics
mean_h_spec: 0.0   # float - mean H_spec across sequences
std_h_spec: 0.0    # float - std H_spec across sequences
min_h_spec: 0.0    # float
max_h_spec: 0.0    # float

# Per-layer summary (optional)
per_layer_lambda_max: []  # list[float] - lambda_max per layer

# Cross-validation (secondary, populated if run)
crossval:
  model_370m_id: "state-spaces/mamba-370m"
  mean_h_spec_370m: null   # float or null
  mean_h_spec_1400m: null  # float or null
  monotonic_scaling: null  # bool or null

# Figures written
figures:
  - "figures/hspec_distribution.png"
  - "figures/gate_metrics.png"
  - "figures/hspec_per_layer.png"
  - "figures/eigenvalue_distribution.png"
  - "figures/scale_comparison.png"  # only if crossval ran
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | ResultsSchema | Implement `save_results()` writing above YAML schema; figure filenames as listed |

---

## Hyperparameter Reference

| Parameter | Default | Valid Range | Notes |
|-----------|---------|-------------|-------|
| num_samples | 1000 | >= 100 | PRD requirement |
| seq_length | 512 | 64-2048 | PRD requirement |
| seed | 42 | any int | Reproducibility |
| cv_threshold | 0.3 | (0, 1) | MUST_WORK gate |
| dtype | "float32" | float32/float64 | float64 for eigenvalue precision if needed |
