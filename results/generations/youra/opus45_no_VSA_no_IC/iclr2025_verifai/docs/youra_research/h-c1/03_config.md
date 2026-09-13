# Config: H-C1 (Cross-Model SA-Correctness Generalization)

**Type**: CONDITION | Budget: 2 subtasks max

**Applied**: Standard PyTorch/dataclass defaults (Archon KB had no relevant match — best hit was PyTorch inductor config.py at similarity 0.42; not applicable to statistical-groupby experiment config).

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1)
**Status**: Config classes verified from base code — Serena tool unavailable for this path; verified via direct `Read` of `h-m1/code/config.py` instead.
**Config Files Found**: `h-m1/code/config.py` (frozen dataclass `Config`, singleton `CONFIG`)
**Pattern Used**: dataclass (frozen)

---

## C-1: Setup & Config [Complexity: 4, Budget: 4]

**Applied**: Frozen dataclass singleton, matching H-M1 pattern for consistency.

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Config:
    models: tuple[str, ...] = ("gpt4", "claude3", "codellama", "codestral")
    completions_dir: str = "data/completions"  # expects {model}.jsonl per model
    results_dir: str = "results"
    figures_dir: str = "figures"
    variance_threshold: float = 0.15   # gate: std(r) must be below this
    mean_r_threshold: float = 0.35     # gate: mean(r) must exceed this
    min_r_threshold: float = 0.20      # gate: weakest model's r must exceed this
    alpha: float = 0.05
    min_models: int = 3                # minimum models with completions to proceed
    sa_timeout_sec: int = 30           # inherited default (H-M1)
    test_timeout_sec: int = 5          # inherited default (H-M1)
    seed: int = 42

CONFIG = Config()

def completion_path(model_id: str) -> str:
    return f"{CONFIG.completions_dir}/{model_id}.jsonl"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Define Config dataclass | Fields above: models, paths, thresholds, seed |
| C-1-2 | Per-model path helper + requirements check | `completion_path()` fn; verify `requirements.txt` matches H-C1 PRD §7.1 (no new packages beyond H-M1) |

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: h-m1/code/config.py (ACTUAL CODE, verified via Read)
@dataclass(frozen=True)
class Config:
    sa_timeout_sec: int = 30
    test_timeout_sec: int = 5
    results_dir: str = "results"
    figures_dir: str = "figures"
    completions_path: str = "data/completions.jsonl"
    corr_threshold: float = 0.35
    alpha: float = 0.05
    min_samples: int = 400
    seed: int = 42

CONFIG = Config()
```

### Field Mapping Notes

- H-M1 `completions_path` (single file) → H-C1 `completions_dir` + per-model `{model}.jsonl` (H-C1 has 4 models, not 1).
- H-M1 `corr_threshold` (0.35, single-model significance gate) → H-C1 `mean_r_threshold` (0.35, cross-model mean gate) — **same value, renamed for clarity, do not confuse with new `variance_threshold`**.
- H-M1 `min_samples` (400, dataset-size check) — not reused in H-C1; replaced by `min_models` (3) since sample count is already fixed at 421/model by H-M1 dataset loader.
- `sa_timeout_sec`, `test_timeout_sec`, `alpha`, `seed` — reused unchanged, same field names.
- H-C1 does **not** subclass H-M1's `Config` (frozen dataclass, no inheritance needed) — new standalone `Config` in `h-c1/code/config.py`, values cross-checked above for consistency.

**Verified from**: `docs/youra_research/h-m1/code/config.py` (actual implementation, direct file read).
