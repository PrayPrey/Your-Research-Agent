# Config: H-P2
## Spurious Probe Accuracy vs WGA Correlation

**Generated:** 2026-08-05
**Type:** MECHANISM (Exploratory Correlation) — Incremental extension of H-M3

Applied: flat-constants pattern (matches h-m3/code/config.py style; no dataclass overhead for read-only config)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (h-m3)
**Status:** Config classes verified from actual h-m3/code/config.py
**Config Files Found:** `docs/youra_research/h-m3/code/config.py`
**Pattern Used:** flat module-level constants (no dataclass)

Key finding: `h-m3/code/config.py` uses flat constants, not dataclasses. H-P2 follows the same pattern for consistency. Critical discrepancy confirmed: `WGA_BY_METHOD_SEED` in h-m3 has `sam_seed*: 0.78` — H-P2 corrects this to `0.74` per Izmailov 2022 Table 1.

---

## Inherited Configuration (Base Hypothesis)

### Constants Inherited from h-m3/code/config.py (Verified)

```python
# Verified field names and defaults from actual h-m3/code/config.py:
WILDS_CACHE: str = "/home/PrayPrey/.wilds_cache"
WILDS_DATASET: str = "waterbirds"
CHECKPOINT_ARCHIVE: str = (
    "/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scsl/docs/youra_research"
    "/_archive/20260805T130336_routing_recovery/h-e1/checkpoints"
)
METHODS: list = ["erm", "groupdro", "sam"]
SEEDS: list = [1, 2, 3]
BATCH_SIZE: int = 100
IMAGENET_MEAN: list = [0.485, 0.456, 0.406]
IMAGENET_STD: list = [0.229, 0.224, 0.225]
# Linear probe (inherited unchanged):
PROBE_C: float = 1e9
PROBE_SOLVER: str = "lbfgs"
PROBE_MAX_ITER: int = 1000
PROBE_RANDOM_STATE: int = 42
PROBE_N_TEST_SAMPLES: int = 5794
```

**WGA discrepancy (CRITICAL):**
- h-m3: `sam_seed*: 0.78` (incorrect)
- H-P2: `sam_seed*: 0.74` (Izmailov 2022 Table 1, Waterbirds — corrected)

---

## A-3: 9-Point Dataset Assembly [Complexity: 7, Budget: 2 subtasks]

**Applied:** flat-constants pattern

### Configuration (code/config.py — excerpt)

```python
# ── Checkpoint paths ──────────────────────────────────────────────────────────
import os

BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H_M3_DIR: str = os.path.join(
    os.path.dirname(BASE_DIR), "h-m3"
)
H_M3_RESULTS_JSON: str = os.path.join(H_M3_DIR, "results.json")
H_M3_CODE_DIR: str = os.path.join(H_M3_DIR, "code")
CHECKPOINT_ARCHIVE: str = (
    "/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scsl/docs/youra_research"
    "/_archive/20260805T130336_routing_recovery/h-e1/checkpoints"
)
WILDS_CACHE: str = "/home/PrayPrey/.wilds_cache"
WILDS_DATASET: str = "waterbirds"

METHODS: list = ["erm", "sam", "groupdro"]
SEEDS: list = [1, 2, 3]

# ── WGA ground truth (Izmailov 2022 Table 1, Waterbirds) ─────────────────────
# Non-standard: SAM=0.74 (corrects h-m3 value of 0.78 which was wrong)
WGA_VALUES: dict = {
    "erm_seed1": 0.72, "erm_seed2": 0.72, "erm_seed3": 0.72,
    "sam_seed1": 0.74, "sam_seed2": 0.74, "sam_seed3": 0.74,
    "groupdro_seed1": 0.88, "groupdro_seed2": 0.88, "groupdro_seed3": 0.88,
}
WGA_SOURCE: str = "Izmailov 2022 Table 1"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Checkpoint path config | CHECKPOINT_ARCHIVE, H_M3_RESULTS_JSON, H_M3_CODE_DIR paths |
| C-3-2 | WGA ground truth constants | WGA_VALUES dict with corrected SAM=0.74, WGA_SOURCE annotation |

---

## A-6: Ablation Config [Complexity: 7, Budget: 2 subtasks]

**Applied:** flat-constants pattern (dict, no YAML file — avoids extra dependency)

### Configuration (code/config.py — excerpt)

```python
# ── Ablation variants ─────────────────────────────────────────────────────────
ABLATION_VARIANTS: dict = {
    "full_n9": {
        "description": "Full 9 checkpoints (ERM×3 + SAM×3 + GroupDRO×3)",
        "include_methods": ["erm", "sam", "groupdro"],
        "collapse_seeds": False,
        "n": 9,
    },
    "erm_groupdro_n6": {
        "description": "ERM + GroupDRO only (exclude SAM)",
        "include_methods": ["erm", "groupdro"],
        "collapse_seeds": False,
        "n": 6,
    },
    "method_means_n3": {
        "description": "Per-method means (3 data points)",
        "include_methods": ["erm", "sam", "groupdro"],
        "collapse_seeds": True,
        "n": 3,
    },
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Ablation variant definitions | ABLATION_VARIANTS dict with 3 variants |
| C-6-2 | Method color palette | METHOD_COLORS for consistent figure styling across ablations |

---

## A-4: Correlation Config [Complexity: 6, Budget: 2 subtasks]

**Applied:** flat-constants pattern

### Configuration (code/config.py — excerpt)

```python
# ── Correlation / bootstrap ───────────────────────────────────────────────────
BOOTSTRAP_N: int = 1000
BOOTSTRAP_RNG: int = 42
CI_LEVEL: float = 0.95
CI_ALTERNATIVE: str = "less"          # one-sided H1: r < 0
PRIMARY_CI_METHOD: str = "BCa"
FALLBACK_CI_METHOD: str = "percentile"

# ── Verdict thresholds (pre-registered) ───────────────────────────────────────
CONFIRMED_R: float = -0.5
CONFIRMED_CI_HIGH: float = 0.0        # CI upper bound must be < 0
SUGGESTIVE_R: float = -0.3
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Bootstrap params | BOOTSTRAP_N, BOOTSTRAP_RNG, CI_LEVEL, CI_ALTERNATIVE, CI method names |
| C-4-2 | Verdict thresholds | CONFIRMED_R, CONFIRMED_CI_HIGH, SUGGESTIVE_R (pre-registered cutoffs) |

---

## A-10: Results / Output Config [Complexity: 6, Budget: 2 subtasks]

**Applied:** flat-constants pattern

### Configuration (code/config.py — excerpt)

```python
# ── Output paths ──────────────────────────────────────────────────────────────
FIGURES_DIR: str = os.path.join(BASE_DIR, "figures")
RESULTS_JSON: str = os.path.join(BASE_DIR, "results.json")
VERIFICATION_STATE: str = os.path.join(
    os.path.dirname(os.path.dirname(BASE_DIR)),
    "verification_state.yaml"
)
HYPOTHESIS_ID: str = "h-p2"

# ── Figure filenames ──────────────────────────────────────────────────────────
SCATTER_FIG: str = "scatter_probe_vs_wga.png"
BOOTSTRAP_FIG: str = "bootstrap_distribution.png"
METHOD_COMPARISON_FIG: str = "method_comparison_bar.png"
ABLATION_FIG: str = "ablation_sensitivity.png"

# ── Figure style ──────────────────────────────────────────────────────────────
METHOD_COLORS: dict = {"erm": "steelblue", "sam": "darkorange", "groupdro": "forestgreen"}
FIGURE_DPI: int = 150
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-10-1 | Output path constants | FIGURES_DIR, RESULTS_JSON, VERIFICATION_STATE, HYPOTHESIS_ID |
| C-10-2 | Figure filename + style constants | SCATTER_FIG, BOOTSTRAP_FIG, METHOD_COMPARISON_FIG, ABLATION_FIG, METHOD_COLORS, FIGURE_DPI |

---

## Complete config.py (Copy-Paste Ready)

```python
"""H-P2 experiment constants — probe accuracy vs WGA correlation analysis."""
import os

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H_M3_DIR: str = os.path.join(os.path.dirname(BASE_DIR), "h-m3")
H_M3_RESULTS_JSON: str = os.path.join(H_M3_DIR, "results.json")
H_M3_CODE_DIR: str = os.path.join(H_M3_DIR, "code")
CHECKPOINT_ARCHIVE: str = (
    "/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scsl/docs/youra_research"
    "/_archive/20260805T130336_routing_recovery/h-e1/checkpoints"
)
WILDS_CACHE: str = "/home/PrayPrey/.wilds_cache"
WILDS_DATASET: str = "waterbirds"

FIGURES_DIR: str = os.path.join(BASE_DIR, "figures")
RESULTS_JSON: str = os.path.join(BASE_DIR, "results.json")
VERIFICATION_STATE: str = os.path.join(
    os.path.dirname(os.path.dirname(BASE_DIR)), "verification_state.yaml"
)
HYPOTHESIS_ID: str = "h-p2"

# ── Experiment scope ──────────────────────────────────────────────────────────
METHODS: list = ["erm", "sam", "groupdro"]
SEEDS: list = [1, 2, 3]

# ── WGA ground truth (Izmailov 2022 Table 1, Waterbirds) ─────────────────────
# Non-standard: SAM=0.74 (corrects h-m3/config.py value of 0.78 — Izmailov 2022 Table 1)
WGA_VALUES: dict = {
    "erm_seed1": 0.72, "erm_seed2": 0.72, "erm_seed3": 0.72,
    "sam_seed1": 0.74, "sam_seed2": 0.74, "sam_seed3": 0.74,
    "groupdro_seed1": 0.88, "groupdro_seed2": 0.88, "groupdro_seed3": 0.88,
}
WGA_SOURCE: str = "Izmailov 2022 Table 1"

# ── Correlation / bootstrap ───────────────────────────────────────────────────
BOOTSTRAP_N: int = 1000
BOOTSTRAP_RNG: int = 42
CI_LEVEL: float = 0.95
CI_ALTERNATIVE: str = "less"
PRIMARY_CI_METHOD: str = "BCa"
FALLBACK_CI_METHOD: str = "percentile"

# ── Verdict thresholds (pre-registered) ───────────────────────────────────────
CONFIRMED_R: float = -0.5
CONFIRMED_CI_HIGH: float = 0.0
SUGGESTIVE_R: float = -0.3

# ── Ablation variants ─────────────────────────────────────────────────────────
ABLATION_VARIANTS: dict = {
    "full_n9": {
        "description": "Full 9 checkpoints (ERM×3 + SAM×3 + GroupDRO×3)",
        "include_methods": ["erm", "sam", "groupdro"],
        "collapse_seeds": False,
        "n": 9,
    },
    "erm_groupdro_n6": {
        "description": "ERM + GroupDRO only (exclude SAM)",
        "include_methods": ["erm", "groupdro"],
        "collapse_seeds": False,
        "n": 6,
    },
    "method_means_n3": {
        "description": "Per-method means (3 data points)",
        "include_methods": ["erm", "sam", "groupdro"],
        "collapse_seeds": True,
        "n": 3,
    },
}

# ── Probe params (inherited from h-m3; used only in fallback re-extraction) ───
PROBE_C: float = 1e9
PROBE_SOLVER: str = "lbfgs"
PROBE_MAX_ITER: int = 1000
PROBE_RANDOM_STATE: int = 42
BATCH_SIZE: int = 100
IMAGENET_MEAN: list = [0.485, 0.456, 0.406]
IMAGENET_STD: list = [0.229, 0.224, 0.225]

# ── Figure output ─────────────────────────────────────────────────────────────
SCATTER_FIG: str = "scatter_probe_vs_wga.png"
BOOTSTRAP_FIG: str = "bootstrap_distribution.png"
METHOD_COMPARISON_FIG: str = "method_comparison_bar.png"
ABLATION_FIG: str = "ablation_sensitivity.png"
METHOD_COLORS: dict = {"erm": "steelblue", "sam": "darkorange", "groupdro": "forestgreen"}
FIGURE_DPI: int = 150
```

---

## Subtask Budget Summary

| Task | Budget | Used | Subtasks |
|------|--------|------|----------|
| A-3 | 2 | 2 | C-3-1, C-3-2 |
| A-6 | 2 | 2 | C-6-1, C-6-2 |
| A-4 | 2 | 2 | C-4-1, C-4-2 |
| A-10 | 2 | 2 | C-10-1, C-10-2 |
| **Total** | **8** | **8** | |
