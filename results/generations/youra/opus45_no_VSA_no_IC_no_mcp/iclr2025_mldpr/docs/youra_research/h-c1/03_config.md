# Config: h-c1 (CONDITION)

**Applied**: statistical-correlation-pipeline-pattern (fixed-constants dict, no hyperparameter search — small-n domain-stratified correlation)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m1)
**Status**: Config verified from actual code (`h-m1/code/config.py`), not `h-m1/03_config.md` spec — no discrepancies found for reused fields.
**Config Files Found**: `h-m1/code/config.py` (`CONFIG` dict, `GAP_DATA` dict — no dataclasses)
**Pattern Used**: dict (hardcoded constants) — consistent with h-m1/h-e1 lineage

---

## C-1: Config setup [Complexity: 4, Budget: 4 subtasks]

**Applied**: Fixed-constants config pattern — n=3-per-domain pilot uses single fixed config, no tuning/grid.

### Configuration (Hardcoded Dict)

```python
# code/config.py

CONFIG = {
    "n_bootstrap": 10000,
    "seed": 42,
    "success_r_abs_threshold": 0.3,  # Non-standard: PRD requires |R|>0.3 (looser than h-m1's -0.4)
    "ci_level": 0.95,
    "figures_dir": "figures",
    "results_dir": "results",
}

# DNSI: 4 values copied verbatim from h-m1's SYNTHETIC_DNSI fallback
# (h-e1 pipeline produces no real values for these benchmarks — see architecture.md
# Codebase Analysis). 2 new (PAWS, ANLI) via same PWC-history synthetic methodology.
DNSI_DATA = {
    "ImageNet": 0.72, "CIFAR-10": 0.85, "ObjectNet": 0.55,
    "HANS": 0.45, "PAWS": 0.60, "ANLI": 0.35,
}

# GAP_DATA: 4 values copied verbatim from h-m1/code/config.py.
# PAWS/ANLI added from published sources (Zhang 2019, Nie 2020) per PRD Dependencies.
GAP_DATA = {
    "ImageNet": 0.125, "CIFAR-10": 0.040, "ObjectNet": 0.425,
    "HANS": 0.400, "PAWS": 0.150, "ANLI": 0.300,
}

DOMAIN_MAP = {
    "ImageNet": "vision", "CIFAR-10": "vision", "ObjectNet": "vision",
    "HANS": "nlp", "PAWS": "nlp", "ANLI": "nlp",
}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | CONFIG dict | n_bootstrap, seed, threshold, ci_level, dirs |
| C-1-2 | DNSI_DATA | 4 copied + 2 new synthetic values |
| C-1-3 | GAP_DATA | 4 copied + 2 new published values |
| C-1-4 | DOMAIN_MAP | benchmark → vision/nlp mapping |

---

## Inherited Configuration (Base Hypothesis h-m1)

### Config Classes (From Actual Code)

```python
# From: h-m1/code/config.py (ACTUAL CODE, verified — no dataclasses used)
CONFIG = {
    "n_bootstrap": 10000,
    "seed": 42,
    "success_r_threshold": -0.4,   # h-c1 replaces with success_r_abs_threshold=0.3
    "fail_r_threshold": -0.2,      # not reused — h-c1 uses per-domain pass/fail via evaluate.py
    "ci_level": 0.95,
    "figures_dir": "figures",
    "results_dir": "results",
}

GAP_DATA = {
    "ImageNet": 0.125,
    "CIFAR-10": 0.040,
    "ObjectNet": 0.425,
    "HANS": 0.400,
}
```

**Deviation note**: h-m1's `success_r_threshold=-0.4` is NOT reused — h-c1 PRD mandates a looser `|R|>0.3` threshold, so a new `success_r_abs_threshold` field replaces it (see architecture.md Codebase Analysis, line 16). `fail_r_threshold` is dropped entirely; h-c1's `evaluate.py::check_domain_pass` implements pass/fail via direct sign+magnitude check instead.

### Usage in h-c1 (No New Dataclass — Flat Dict Extension)

h-c1 does not subclass or import h-m1's `CONFIG`/`GAP_DATA` at runtime (h-m1/code is not a package). Instead it copies the 4 known GAP_DATA/DNSI values verbatim into its own `config.py` and extends with 2 new NLP benchmarks (PAWS, ANLI), matching the copy-not-import pattern h-m1 itself used relative to h-e1.

**Verified from**: `h-m1/code/config.py` (actual implementation).
