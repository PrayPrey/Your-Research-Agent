# Configuration: H-M2
# Causal Propagation — CISE OrbitVar → LightGBM Prediction Variance

**Hypothesis ID:** H-M2
**Type:** MECHANISM (Causal Step 2)
**Date:** 2026-08-03

Applied: standard-sklearn-kfold-cv pattern (no relevant LightGBM KB pattern found, max sim ~0.49)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from h-m1 actual code (`run_experiment.py`, top-level constants)
**Config Files Found**: `h-m1/code/run_experiment.py` (constants), `h-m1/03_config.md` (reference)
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

Field names verified from `h-m1/code/run_experiment.py` actual constants:

```python
# Verified from h-m1/code/run_experiment.py:
# BUILD_ON_VALUE = 0.010333   → orbit_var_expected: float = 0.010333
# K = 50 (from h-e1 argparse) → K: int = 50
# seed = 1 (from h-e1 argparse) → seed: int = 1
# n_models = 100 (from h-e1 argparse) → N_MODELS: int = 100
# EMBED_DIM not explicit in h-m1 — inferred from encoder_c1 output (64)
```

---

## C-1: LightGBM + CV + Orbit Config (Epics A-3, A-4) [Complexity: 2, Budget: 1]

**Applied**: standard-sklearn-kfold-cv pattern

```python
from dataclasses import dataclass

@dataclass
class LGBMConfig:
    n_estimators: int = 500
    learning_rate: float = 0.05
    num_leaves: int = 31
    reg_alpha: float = 0.0
    reg_lambda: float = 0.1
    random_state: int = 42
    boosting_type: str = 'gbdt'

@dataclass
class CVConfig:
    n_splits: int = 5
    shuffle: bool = True
    random_state: int = 42

@dataclass
class OrbitConfig:
    K: int = 50    # verified from h-m1 (h-e1 argparse default)
    seed: int = 1  # verified from h-m1 (h-e1 argparse default)

@dataclass
class GateConfig:
    ratio_threshold: float = 0.10         # PRIMARY gate: MSE_perm / MSE_total >= 0.10
    orbit_var_expected: float = 0.010333  # verified from h-m1 BUILD_ON_VALUE
    orbit_var_tol: float = 0.20           # 20% tolerance on OrbitVar prerequisite check
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | LightGBM + CV + Orbit + Gate configs | Dataclasses for lgbm_trainer.py, embeddings.py, evaluate.py |

---

## C-2: Experiment Paths + Reference Constants (Epic A-8) [Complexity: 1, Budget: 1]

**Applied**: flat-path-config pattern

```python
from dataclasses import dataclass

@dataclass
class PathConfig:
    data_path: str = "../../data/dataset_cifar_small_hyp_rand.pt"
    h1_code_dir: str = "../../h-m1/code"
    h1_results_path: str = "../../h-m1/results/orbit_var_ratios.json"
    results_dir: str = "results"
    figures_dir: str = "figures"

# Reference constants (not tunable — verified from H-M1/H-E1 actual code)
C0_R2: float = 0.984      # C0 baseline R² (secondary gate: R²(C1) must be below this)
C0_TAU: float = 0.915     # C0 baseline Kendall's τ
N_MODELS: int = 100       # dataset size (fixed by H-E1 dataset)
GATE_RATIO: float = 0.10  # MSE_perm / MSE_total threshold (mirrors GateConfig.ratio_threshold)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | PathConfig + reference constants | Paths and fixed reference values for run_experiment.py |

---

## Complete YAML Config Schema (config.yaml)

Load in `run_experiment.py` via `yaml.safe_load(open("config.yaml"))`.

```yaml
# H-M2 experiment config
paths:
  data_path: "../../data/dataset_cifar_small_hyp_rand.pt"
  h1_code_dir: "../../h-m1/code"
  h1_results_path: "../../h-m1/results/orbit_var_ratios.json"
  results_dir: "results"
  figures_dir: "figures"

lgbm:
  n_estimators: 500
  learning_rate: 0.05
  num_leaves: 31
  reg_alpha: 0.0
  reg_lambda: 0.1
  random_state: 42
  boosting_type: gbdt

cv:
  n_splits: 5
  shuffle: true
  random_state: 42

orbit:
  K: 50
  seed: 1

gate:
  ratio_threshold: 0.10
  orbit_var_expected: 0.010333
  orbit_var_tol: 0.20

# Read-only reference constants (do not tune)
reference:
  C0_R2: 0.984
  C0_TAU: 0.915
  N_MODELS: 100
  GATE_RATIO: 0.10
```

### Loader snippet for run_experiment.py

```python
import yaml

def load_config(path: str = "config.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)
```

---

## Self-Validation

- [x] ONE format only (dataclass)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X" line)
- [x] Rationale only for non-standard values
- [x] 2 subtasks within budget (2/2)
- [x] Total length < 400 lines
- [x] Codebase Analysis (Serena) section included
- [x] Inherited Configuration section with verified field names from h-m1 actual code
- [x] YAML schema included
