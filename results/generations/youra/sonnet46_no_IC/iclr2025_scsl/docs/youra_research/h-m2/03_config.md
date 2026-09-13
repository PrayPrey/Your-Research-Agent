# Config: H-M2
## Group-Balanced Gradient Propagates Through All Backbone Layers — Proxy Verification

**Generated:** 2026-08-05
**Hypothesis Type:** MECHANISM (Proxy Verification — no new training)

Applied: flat constants-only module pattern (from h-m1/code/config.py)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: config constants verified from actual h-m1 code
**Config Files Found**: `docs/youra_research/h-m1/code/config.py`
**Pattern Used**: constants-only module (no dataclass, no dict)

---

## Inherited Configuration (Base Hypothesis)

From `h-m1/code/config.py` (actual code, verified):

```python
# Inherited field names (exact):
WILDS_CACHE = "/home/PrayPrey/.wilds_cache"
WILDS_DATASET = "waterbirds"
CHECKPOINT_ARCHIVE = ".../_archive/.../h-e1/checkpoints"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGURES_DIR = os.path.join(BASE_DIR, "figures")
RESULTS_JSON = os.path.join(BASE_DIR, "results.json")
VALIDATION_REPORT = os.path.join(BASE_DIR, "04_validation.md")
```

H-M2 copies these values into its own `config.py` — no cross-hypothesis imports.

---

## A-10: Orchestration Config [Complexity: 1, Budget: 1 subtask]

### Configuration (`h-m2/code/config.py`)

```python
"""H-M2 experiment constants — proxy verification, no new training."""
import os

# ── Paths ─────────────────────────────────────────────────────────────────────
WILDS_CACHE: str = "/home/PrayPrey/.wilds_cache"
WILDS_DATASET: str = "waterbirds"
CHECKPOINT_ARCHIVE: str = (
    "/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scsl/docs/youra_research"
    "/_archive/20260805T130336_routing_recovery/h-e1/checkpoints"
)
BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGURES_DIR: str = os.path.join(BASE_DIR, "figures")
RESULTS_JSON: str = os.path.join(BASE_DIR, "results.json")
VALIDATION_REPORT: str = os.path.join(BASE_DIR, "04_validation.md")

# ── Experiment scope ──────────────────────────────────────────────────────────
METHODS: list = ["erm", "groupdro", "sam", "dfr"]
SEEDS: list = [1, 2, 3]

# ── Gradient norm analysis (FR-2) ─────────────────────────────────────────────
N_GRAD_BATCHES: int = 50        # 50×32 = 1600 samples ≈ 1/3 of train set
GRAD_BATCH_SIZE: int = 32
GRAD_LOSS_TYPES: list = ["erm", "groupdro"]
N_GROUPS: int = 4

# ── Linear probe (FR-3) — consistent with H-P0 proven protocol ───────────────
PROBE_C: float = 1e9            # Near-zero regularization: unbiased feature probe
PROBE_SOLVER: str = "lbfgs"
PROBE_MAX_ITER: int = 1000
PROBE_RANDOM_STATE: int = 42
PROBE_N_TEST_SAMPLES: int = 5794  # Full test set — no subsampling

# ── Weight difference analysis (FR-1) ────────────────────────────────────────
LAYER4_BLOCKS: list = [0, 1, 2]
WEIGHT_DIFF_EPSILON: float = 1e-6   # Threshold for "gradient reached" detection
PAIRED_METHODS: list = [
    ("erm", "groupdro"),
    ("erm", "sam"),
    ("erm", "dfr"),
]

# ── ImageNet normalization (shared with h-m1) ─────────────────────────────────
IMAGENET_MEAN: list = [0.485, 0.456, 0.406]
IMAGENET_STD: list = [0.229, 0.224, 0.225]
```

### Orchestration Flow (OOM-safe sequential)

```python
# In run_experiment.py — pattern for each checkpoint pair:
for seed in SEEDS:
    for method_a, method_b in PAIRED_METHODS:
        ckpt_a = load_checkpoint(method_a, seed)   # load to CPU
        ckpt_b = load_checkpoint(method_b, seed)
        result = analyze_pair(ckpt_a, ckpt_b)
        del ckpt_a, ckpt_b
        gc.collect()
        results.append(result)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-10-1 | Write config.py | Constants-only module with all values above |
