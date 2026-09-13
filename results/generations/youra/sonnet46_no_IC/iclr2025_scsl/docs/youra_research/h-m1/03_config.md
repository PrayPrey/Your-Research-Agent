# Config: H-M1
## GroupDRO Minority Group Upweighting — Mechanism Theory Confirmation

**Generated:** 2026-08-05
**Hypothesis Type:** MECHANISM (no training, no hyperparameter tuning)

Applied: flat constants-only module pattern (verified from h-p0/code/config.py)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1 builds on H-P0)
**Status**: config constants verified from actual base code
**Config Files Found**: `docs/youra_research/h-p0/code/config.py`
**Pattern Used**: constants-only module (no dataclass, no dict)

---

## Inherited Configuration (Base Hypothesis)

### Constants from h-p0/code/config.py (verified from actual code)

```python
# Verified field names from h-p0/code/config.py:
WILDS_CACHE = "/home/PrayPrey/.wilds_cache"   # dataset cache root
HF_REPO = "izmailovpavel/spurious_feature_learning"
SEEDS = [1, 2, 3]
DATA_SEED = 42
LOCAL_CHECKPOINT_ARCHIVE = ".../_archive/.../h-e1/checkpoints"
GATE_MEAN_SIM = 0.9999
GATE_VARIANCE = 1e-6
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "results")
FIGURES_DIR = os.path.join(BASE_DIR, "figures")
CHECKPOINT_DIR = os.path.join(BASE_DIR, "code", "checkpoints")
CHECKPOINT_MAP = {...}
EXPECTED_SHAPES = {...}
```

**H-M1 reuses**: `WILDS_CACHE`, `LOCAL_CHECKPOINT_ARCHIVE` (path only, copied as constants)
**H-M1 does NOT import from h-p0** — copies needed values into its own `config.py`.

---

## A-1: Project Setup [Budget: 0 subtasks — constants only]

### Configuration (h-m1/code/config.py)

```python
"""H-M1 experiment constants — no training, no hyperparameter tuning."""
import os

# ── Dataset ──────────────────────────────────────────────────────────────────
WILDS_CACHE: str = "/home/PrayPrey/.wilds_cache"
# Shared cache root from h-p0; Waterbirds dataset will be loaded/downloaded here.

WILDS_DATASET: str = "waterbirds"
# WILDS dataset name passed to wilds.get_dataset(dataset=WILDS_DATASET, ...).

# ── Gate Threshold ────────────────────────────────────────────────────────────
MINORITY_FRACTION_THRESHOLD: float = 0.10
# Gate check 1: minority groups must comprise < 10% of training data.
# Waterbirds minority fraction is ~4.6% by construction (Sagawa 2019).
# Valid range: (0.0, 0.5). Values above 0.5 would mean majority != majority.

# ── Reference WGA Values (Izmailov 2022, Table 1) ────────────────────────────
WGA_GROUPDRO: float = 0.88
# Worst-group accuracy of GroupDRO on Waterbirds (Izmailov 2022, Table 1).
# Used in gate check 4: confirms GroupDRO > ERM on worst group.

WGA_ERM: float = 0.72
# Worst-group accuracy of ERM baseline on Waterbirds (Izmailov 2022, Table 1).
# Gate passes only when WGA_GROUPDRO > WGA_ERM (0.88 > 0.72).

# ── Group Encoding (Waterbirds WILDS) ────────────────────────────────────────
MINORITY_GROUPS: list = [1, 2]
# Group indices for minority groups in Waterbirds:
#   1 = Landbird photographed on Water background (spurious mismatch)
#   2 = Waterbird photographed on Land background (spurious mismatch)
# These are small in training set, hurting ERM worst-group accuracy.

MAJORITY_GROUPS: list = [0, 3]
# Group indices for majority groups:
#   0 = Landbird+Land (aligned, common)
#   3 = Waterbird+Water (aligned, common)

GROUP_LABELS: dict = {
    0: "Landbird+Land",
    1: "Landbird+Water",
    2: "Waterbird+Land",
    3: "Waterbird+Water",
}
# Human-readable labels for figures and validation report.
# Keys are WILDS group indices (0–3); values are display strings.

# ── Output Paths (relative to h-m1/) ─────────────────────────────────────────
BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Resolves to h-m1/ regardless of working directory at run time.
# Pattern inherited from h-p0/code/config.py.

FIGURES_DIR: str = os.path.join(BASE_DIR, "figures")
# Directory for all output figures (pie chart, bar chart, schematics).
# Created at runtime if absent.

RESULTS_JSON: str = os.path.join(BASE_DIR, "results.json")
# Structured gate output: gate_result, minority_fraction, group_counts, wga values.

VALIDATION_REPORT: str = os.path.join(BASE_DIR, "04_validation.md")
# Generated markdown report: group table, mechanism pseudo-code, gate verdict.
```

---

## Notes

- No dataclass, no YAML, no argparse — this is an analysis-only script.
- All values are either dataset-construction facts (group indices, WGA from paper) or filesystem paths.
- No hyperparameter ranges; this is an EXISTENCE hypothesis (single fixed config).
