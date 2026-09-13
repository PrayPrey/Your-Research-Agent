# Config: h-m1 (MECHANISM)

**Applied**: No direct KB match for this domain (diffusion/inductor/jax docs only); using standard Python dict-config extension pattern (base dict spread + override keys), consistent with h-e1.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1, VALIDATED)
**Status**: Config classes verified from base code — `h-e1/code/config.py` exports a single dict constant `CONFIG` (not a dataclass, not flat module vars).
**Config Files Found**: `docs/youra_research/h-e1/code/config.py`
**Pattern Used**: Hardcoded dict (plain Python dict, no dataclass)

h-m1 follows the same pattern for consistency: single dict constant, extended via `**BASE_CONFIG` spread.

---

## Inherited Configuration (Base Hypothesis)

### Base Config (Actual Code, from `h-e1/code/config.py`)

```python
# From: docs/youra_research/h-e1/code/config.py (ACTUAL CODE)
CONFIG = {
    "seed": 42,
    "model_id": "meta-llama/Llama-2-7b-hf",
    "device": "cuda",
    "dtype": "float16",
    "target_layers": (24, 31),   # inclusive, LLaMA-2-7B has layers 0-31
    "n_folds": 5,
    "auroc_threshold": 0.55,     # h-e1 EXISTENCE gate, not used by h-m1
    "min_fold_threshold": 0.52,  # h-e1 EXISTENCE gate, not used by h-m1
    "min_pass_rate": 0.8,        # h-e1 EXISTENCE gate, not used by h-m1
    "dataset": "truthful_qa",
    "dataset_config": "multiple_choice",
    "figures_dir": os.path.join(os.path.dirname(__file__), "figures"),
    "outputs_dir": os.path.join(os.path.dirname(__file__), "outputs"),
    "batch_size": 4,
}
```

**Verified from**: `docs/youra_research/h-e1/code/config.py` (actual implementation, field names confirmed — matches h-e1's own spec, no drift).

---

## B-1: Config Setup [Complexity: 4, Budget: 0 subtasks]

**Applied**: Dict-spread extension pattern (`{**BASE, override_keys}`), avoids duplicating base fields.

### Configuration (Hardcoded Dict)

```python
# h-m1/code/config.py
from h_e1.code.config import CONFIG as BASE_CONFIG

CONFIG = {
    **BASE_CONFIG,
    "lrt_df": 2,                     # degrees of freedom: NTI + CMI params added
    "auroc_gain_threshold": 0.03,    # success criterion (FR-6)
    "lrt_pvalue_threshold": 0.05,    # success criterion (FR-6)
    "falsify_gain": 0.02,            # falsification bound (FR-6)
    "falsify_pvalue": 0.10,          # falsification bound (FR-6)
    "logreg_C": 1.0,                 # sklearn LogisticRegression default
    "logreg_max_iter": 1000,         # sklearn default is 100; raised for convergence
    "figures_dir": "figures/",       # overrides base absolute path with relative (h-m1 own dir)
}
```

`figures_dir` intentionally overrides the base absolute path since h-m1 has its own `code/` directory; `outputs_dir` inherited unchanged is not used (no separate outputs needed beyond figures + printed summary).

No dataclass — h-m1 uses the same plain-dict pattern as h-e1 for consistency; `CONFIG` is the single source of truth imported by `cmi.py`, `evaluate.py`, `visualize.py`, `run.py`.

---

## Notes

- All hyperparameters are fixed defaults (sklearn/scipy standard values + PRD-specified thresholds) — no tuning grid, consistent with reused single-run CV design.
- Seed inherited from h-e1 (`42`), used for both `stratified_folds` (data) and `run_cv_lrt` (fold reproducibility) — no separate seed field needed.
- No new dependencies: numpy, sklearn, scipy.stats, matplotlib only (all present in h-e1 environment).
