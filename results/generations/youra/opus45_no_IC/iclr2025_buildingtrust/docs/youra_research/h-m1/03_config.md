# Configuration: H-M1 (MECHANISM)

**Applied**: No KB match (diffusion-model results only) — standard module-level constants, matching h-e1's existing `config.py` pattern.

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1)
**Status**: Config classes verified from actual h-e1 code
**Config Files Found**: `docs/youra_research/h-e1/code/config.py` — exposes `SEED`, `MODEL_ID`, `CATEGORY_TO_CLUSTER`, `CLUSTER_NAMES`
**Pattern Used**: Plain module-level constants (dict-style), not dataclass

---

## Inherited Configuration (Base Hypothesis)

```python
# From: docs/youra_research/h-e1/code/config.py (ACTUAL CODE, imported via `from h_e1.code.config import *`)
SEED = 42
MODEL_ID = "meta-llama/Llama-2-7b-hf"
CATEGORY_TO_CLUSTER = { ... }   # 38 categories -> 7 clusters
CLUSTER_NAMES = { ... }         # cluster_id -> name
```

## M-1..M-9: Config (all tasks share one config file) [Complexity: 5-10, combined]

**Applied**: Reuse-and-extend pattern — no new hyperparameter search, MECHANISM test with fixed constants only.

### Configuration (h-m1/code/config.py)

```python
from h_e1.code.config import *  # SEED, MODEL_ID, CATEGORY_TO_CLUSTER, CLUSTER_NAMES

# KS test parameters
ALPHA: float = 0.05             # significance threshold
N_CLUSTERS: int = 7
MIN_CLUSTER_SIZE: int = 100     # gate: FR-1 validation
MAJORITY_PAIRS_REQUIRED: int = 11  # of 21 total pairs (C(7,2))

# Inference
BATCH_SIZE: int = 8
PRECISION: str = "float16"

# Output paths
RESULTS_JSON: str = "results.json"
VALIDATION_MD: str = "../04_validation.md"
FIGURES_DIR: str = "figures/"
```

**Non-standard**: `MAJORITY_PAIRS_REQUIRED = 11` derived from gate spec (>=11/21), not a tunable default.

### Subtasks [0/0 — no additional decomposition; config is a single shared file across M-1..M-9]

---

## Self-Validation
- ONE format only: plain constants (dict/module-level), no dataclass mixed in.
- No ASCII diagrams, no KB search logs beyond 1-line note.
- Rationale given only for non-standard value (MAJORITY_PAIRS_REQUIRED).
- Codebase Analysis (Serena) section included, base hypothesis fields verified from actual h-e1 code.
