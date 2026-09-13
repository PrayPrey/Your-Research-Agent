# H-M3 Configuration

Applied: flat-constants pattern (verified from h-m2/code/config.py)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: config verified from actual h-m2/code/config.py
**Config Files Found**: `docs/youra_research/h-m2/code/config.py`
**Pattern Used**: flat Python constants (no dataclass, no YAML)

---

## Inherited Configuration (Base Hypothesis)

Fields carried over unchanged from `h-m2/code/config.py`:

| Field | H-M2 Value | H-M3 Value | Status |
|---|---|---|---|
| `WILDS_CACHE` | `"/home/PrayPrey/.wilds_cache"` | same | inherited |
| `WILDS_DATASET` | `"waterbirds"` | same | inherited |
| `CHECKPOINT_ARCHIVE` | same path | same | inherited |
| `BASE_DIR` | `dirname(dirname(__file__))` | same | inherited |
| `FIGURES_DIR` | `BASE_DIR/figures` | same | inherited |
| `RESULTS_JSON` | `BASE_DIR/results.json` | same | inherited |
| `VALIDATION_REPORT` | `BASE_DIR/04_validation.md` | same | inherited |
| `SEEDS` | `[1, 2, 3]` | same | inherited |
| `PROBE_C` | `1e9` | same | inherited |
| `PROBE_SOLVER` | `"lbfgs"` | same | inherited |
| `PROBE_MAX_ITER` | `1000` | same | inherited |
| `PROBE_RANDOM_STATE` | `42` | same | inherited |
| `PROBE_N_TEST_SAMPLES` | `5794` | same | inherited |
| `IMAGENET_MEAN` | `[0.485, 0.456, 0.406]` | same | inherited |
| `IMAGENET_STD` | `[0.229, 0.224, 0.225]` | same | inherited |

### Delta from H-M2

| Field | Change |
|---|---|
| `METHODS` | `["erm","groupdro","sam","dfr"]` → `["erm","groupdro","sam"]` (drop dfr) |
| `PRIMARY_METHODS` | NEW — `["erm", "groupdro"]` for paired t-test gate |
| `BATCH_SIZE` | NEW — `100` (feature extraction batch size) |
| `N_GRAD_BATCHES` | REMOVED (FR-2 dropped) |
| `GRAD_BATCH_SIZE` | REMOVED (FR-2 dropped) |
| `GRAD_LOSS_TYPES` | REMOVED (FR-2 dropped) |
| `N_GROUPS` | REMOVED (FR-2 dropped) |
| `LAYER4_BLOCKS` | REMOVED (FR-1 dropped) |
| `WEIGHT_DIFF_EPSILON` | REMOVED (FR-1 dropped) |
| `PAIRED_METHODS` | REMOVED (FR-1 dropped) |
| Transform | H-M2: `Resize((224,224))` → H-M3: `Resize(256)+CenterCrop(224)` |

---

## config.py (Full Content)

```python
"""H-M3 experiment constants — background linear decodability test."""
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
METHODS: list = ["erm", "groupdro", "sam"]  # no dfr — H-M3 scope
SEEDS: list = [1, 2, 3]
PRIMARY_METHODS: list = ["erm", "groupdro"]  # paired t-test gate only

# ── Data loading ──────────────────────────────────────────────────────────────
BATCH_SIZE: int = 100

# ── ImageNet normalization ────────────────────────────────────────────────────
IMAGENET_MEAN: list = [0.485, 0.456, 0.406]
IMAGENET_STD: list = [0.229, 0.224, 0.225]
# Transform: Resize(256) + CenterCrop(224) — defined in run_experiment.py

# ── Linear probe — consistent with H-P0 proven protocol ──────────────────────
PROBE_C: float = 1e9          # no regularization (pre-registered)
PROBE_SOLVER: str = "lbfgs"
PROBE_MAX_ITER: int = 1000
PROBE_RANDOM_STATE: int = 42
PROBE_N_TEST_SAMPLES: int = 5794

# ── Tiered verdict thresholds ─────────────────────────────────────────────────
# CONFIRMED:   p < 0.05 and cohens_d > 0
# SUGGESTIVE:  p < 0.10 and cohens_d > 0.5
# REJECTED:    else
VERDICT_CONFIRMED_P: float = 0.05
VERDICT_CONFIRMED_D: float = 0.0
VERDICT_SUGGESTIVE_P: float = 0.10
VERDICT_SUGGESTIVE_D: float = 0.5
```

---

## Verdict Threshold Logic (for run_experiment.py)

```python
def gate_verdict(p_value: float, cohens_d: float) -> str:
    if p_value < VERDICT_CONFIRMED_P and cohens_d > VERDICT_CONFIRMED_D:
        return "CONFIRMED"
    if p_value < VERDICT_SUGGESTIVE_P and cohens_d > VERDICT_SUGGESTIVE_D:
        return "SUGGESTIVE"
    return "REJECTED"
```
