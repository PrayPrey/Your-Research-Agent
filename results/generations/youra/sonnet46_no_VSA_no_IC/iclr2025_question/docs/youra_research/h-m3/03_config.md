# Config: H-M3
# AUROC Bootstrap CI on Aggregation Differences

**Applied**: None — Archon KB no relevant content (diffusion model content only)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M2)
**Status**: Config verified from H-M2 03_config.md (actual implementation)
**Config Files Found**: `h-m2/03_config.md`
**Pattern Used**: flat module-level constants (matches H-M2/H-M1/H-E1 pattern)

---

## Inherited Configuration

H-M3 is a statistical re-analysis — no model inference. The following H-M2 fields are **reused directly**:

| H-M2 Field | H-M3 | Change |
|---|---|---|
| `DATASETS` | kept | same |
| `MODELS_TO_RUN` | kept | same |
| `AGGREGATION_METHODS` | kept | same |
| `SEED` | kept | 42 |
| `N_RESAMPLES_BOOTSTRAP` | kept | 1000 |
| `CONFIDENCE_LEVEL` | kept | 0.95 |
| `BOOTSTRAP_METHOD` | kept | "percentile" |
| `MAX_NEW_TOKENS` | **dropped** | no inference |
| `TORCH_DTYPE` | **dropped** | no inference |
| `DEVICE_MAP` | **dropped** | no inference |
| `N_SAMPLES` | **dropped** | loaded from npz |
| `FEW_SHOT_K` | **dropped** | no inference |
| `MIN_GENERATED_TOKENS` | **dropped** | no inference |

New H-M3 fields: `P1_THRESHOLD`, `P2_THRESHOLD`, `H_E1_RESULTS_DIR`, `H_M2_RESULTS_DIR`.

---

## C-1: Constants Module (`code/config.py`)

```python
# code/config.py  (complete file)
import os

# ── Paths ──────────────────────────────────────────────────────────────────────
_THIS_DIR   = os.path.dirname(os.path.abspath(__file__))
_H_M3_ROOT  = os.path.dirname(_THIS_DIR)
_YOURA_ROOT = os.path.dirname(_H_M3_ROOT)

H_E1_RESULTS_DIR = os.path.join(_YOURA_ROOT, "h-e1", "results")
H_M2_RESULTS_DIR = os.path.join(_YOURA_ROOT, "h-m2", "results")
RESULTS_DIR      = os.path.join(_H_M3_ROOT, "results")
FIGURES_DIR      = os.path.join(_H_M3_ROOT, "figures")

# ── Models / Datasets / Aggregations ──────────────────────────────────────────
MODELS_TO_RUN       = ["llama2", "mistral"]
DATASETS            = ["trivia_qa", "nq", "truthful_qa"]
AGGREGATION_METHODS = ["min", "mean", "raw_sum"]

# ── Bootstrap ─────────────────────────────────────────────────────────────────
SEED                   = 42
N_RESAMPLES_BOOTSTRAP  = 1000
CONFIDENCE_LEVEL       = 0.95
BOOTSTRAP_METHOD       = "percentile"   # scipy.stats.bootstrap method param

# ── Gate Thresholds ───────────────────────────────────────────────────────────
# Non-standard: 0.02 (not 0.05) — tighter threshold per H-M3 gate spec
P1_THRESHOLD = 0.02   # min CI lower > mean CI upper (P1 gate)
P2_THRESHOLD = 0.02   # min-mean diff CI excludes zero (P2 gate)
```

---

## C-2: ExperimentConfig Dataclass (`run_experiment.py`)

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class ExperimentConfig:
    # Paths (overrideable for testing)
    h_e1_results_dir: str = ""      # default: resolved from config.py at runtime
    h_m2_results_dir: str = ""
    results_dir: str = ""
    figures_dir: str = ""

    # Scope
    models: List[str] = field(default_factory=lambda: ["llama2", "mistral"])
    datasets: List[str] = field(default_factory=lambda: ["trivia_qa", "nq", "truthful_qa"])
    aggregations: List[str] = field(default_factory=lambda: ["min", "mean", "raw_sum"])

    # Bootstrap
    n_resamples: int = 1000
    seed: int = 42
    confidence_level: float = 0.95

    # Gates
    p1_threshold: float = 0.02
    p2_threshold: float = 0.02
```

---

## C-3: YAML Config (`config.yaml`)

```yaml
# config.yaml — passed to run_experiment.py --config config.yaml
# Paths left empty → resolved automatically from config.py at runtime
paths:
  h_e1_results_dir: ""
  h_m2_results_dir: ""
  results_dir: ""
  figures_dir: ""

scope:
  models: ["llama2", "mistral"]
  datasets: ["trivia_qa", "nq", "truthful_qa"]
  aggregations: ["min", "mean", "raw_sum"]

bootstrap:
  n_resamples: 1000
  seed: 42
  confidence_level: 0.95

gates:
  p1_threshold: 0.02
  p2_threshold: 0.02
```

---

## Subtasks

Budget: 0 dedicated subtasks — config integrated into epic tasks.
