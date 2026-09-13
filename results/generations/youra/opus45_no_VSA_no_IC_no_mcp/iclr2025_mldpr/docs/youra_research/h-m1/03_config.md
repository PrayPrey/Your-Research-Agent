# Config: h-m1 (MECHANISM)

**Applied**: statistical-correlation-pipeline-pattern (fixed-constants dict, no hyperparameter search — small-n correlation analysis)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1)
**Status**: Config classes verified from base code (`h-e1/code/config.py`, actual, not `h-e1/03_config.md` spec)
**Config Files Found**: `h-e1/code/config.py` (`CONFIG` dict, `TARGET_BENCHMARKS` dict — no dataclasses)
**Pattern Used**: dict (hardcoded constants) — consistent with h-e1

---

## M-1: Config setup [Complexity: 4, Budget: 0 subtasks]

**Applied**: Fixed-constants config pattern — n=4 correlation pilot uses single fixed config, no tuning/grid.

### Configuration (Hardcoded Dict)

```python
# code/config.py

CONFIG = {
    "n_bootstrap": 10000,
    "seed": 42,
    "success_r_threshold": -0.4,
    "fail_r_threshold": -0.2,
    "ci_level": 0.95,
    "figures_dir": "figures",
    "results_dir": "results",
}

# Non-standard: hardcoded from peer-reviewed papers (Recht 2019, Barbu 2019,
# McCoy 2019), not measured in this pipeline — see PRD FR-2.
GAP_DATA = {
    "ImageNet": 0.125,
    "CIFAR-10": 0.040,
    "ObjectNet": 0.425,
    "HANS": 0.400,
}
```

No subtasks (budget 0) — single dict definition, matches architecture spec verbatim.

---

## Inherited Configuration (Base Hypothesis h-e1)

### Config Classes (From Actual Code)

```python
# From: h-e1/code/config.py (ACTUAL CODE, verified — no dataclasses used)
CONFIG = {
    "seed": 1,
    "window_months": 6,
    "min_sota_entries": 15,   # note: 15 in actual code, not 50 as in h-e1/03_config.md spec
    "min_history_years": 3,
    "dnsi_valid_range": (0.0, 2.0),
    "success_rate_threshold": 0.5,
    "data_dir": "data/pwc",
    "figures_dir": "figures",
    "pwc_repo_url": "https://github.com/paperswithcode/paperswithcode-data",
}

TARGET_BENCHMARKS = {
    "ImageNet": 1000,
    "CIFAR-10": 10,
    "CIFAR-100": 100,
    "MNIST": 10,
    "GLUE": None,
    "SQuAD": None,
    "WMT En-De": None,
    "COCO Detection": 80,
}
```

**Deviation note**: h-e1's `03_config.md` spec says `min_sota_entries: 50`; actual code has `15` (reduced for PoC with synthetic data). h-m1 does not modify this — DNSI values are consumed via `run_pipeline()` import, not recomputed.

### Usage in h-m1 (No New Dataclass — Import Only)

h-m1 does not extend or subclass h-e1's `CONFIG`. It imports h-e1's `run_pipeline`, `CONFIG`, `TARGET_BENCHMARKS` directly (see `h-m1/03_architecture.md` External Dependencies) to map DNSI benchmark keys before merging with `GAP_DATA`. No field renaming/inheritance needed — separate flat dict, joined only via benchmark name string keys at runtime in `data.py`.

**Verified from**: `h-e1/code/config.py` (actual implementation).
