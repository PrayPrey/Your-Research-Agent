# Configuration: h-m2

**Applied**: No relevant KB config pattern (best match similarity 0.34, unrelated diffusion/inductor repos) — used standard dataclass-extension pattern instead.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m1)
**Status**: Serena unavailable for this workspace (no active project registered); verified actual config via direct file read of `h-m1/code/config.py` per fallback rule.
**Config Files Found**: `h-m1/code/config.py` (`ExperimentConfig` dataclass, `set_all_seeds`, `setup_dirs`)
**Pattern Used**: Dataclass (extended via subclassing)

---

## Inherited Configuration (Base Hypothesis h-m1)

Verified from actual code — field names differ from what specs might imply (e.g. `probes_per_mode` not `n_probes`, `tracin_num_checkpoints` not `n_checkpoints`):

```python
# From: h-m1/code/config.py (ACTUAL CODE)
@dataclass
class ExperimentConfig:
    seed: int = 42
    epochs: int = 5              # h-m1 PoC value; h-m2 overrides to 200 per PRD FR-1
    batch_size: int = 128
    lr: float = 0.1
    momentum: float = 0.9
    weight_decay: float = 5e-4
    checkpoint_every: int = 5

    data_root: str = "..."       # unchanged, reused
    ckpt_dir: str = "./h-m1/checkpoints"
    fig_dir: str = "./h-m1/figures"

    probes_per_mode: int = 100   # h-m1 PoC value; h-m2 overrides to 1000 per PRD FR-2
    modes: tuple = ("mem", "transfer", "spurious")

    trak_proj_dim: int = 2048
    trak_use_half_precision: bool = True
    tracin_num_checkpoints: int = 1
    kronfluence_use_amp: bool = True
```

`set_all_seeds(seed)` and `setup_dirs(cfg)` are reused unmodified (imported or vendored per architecture B-2).

---

## B-1: Config extension [Complexity: 3, Budget: 3]

**Applied**: Standard dataclass-inheritance override pattern.

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass
from h_m1_code.config import ExperimentConfig  # or vendored copy

@dataclass
class MultiSeedConfig(ExperimentConfig):
    seeds: tuple = (42, 123, 456, 789, 1000, 1111, 2222, 3333, 4444, 5555)
    epochs: int = 200            # PRD FR-1 (overrides h-m1's PoC epochs=5)
    probes_per_mode: int = 1000  # PRD FR-2 (overrides h-m1's PoC value=100)

    ckpt_dir: str = "./h-m2/checkpoints"
    fig_dir: str = "./h-m2/figures"
    results_dir: str = "./h-m2/results"

    # Gate thresholds (PRD Success Criteria)
    f_ratio_threshold: float = 4.0
    cohens_d_threshold: float = 0.5
    p_value_threshold: float = 0.05

    # ANOVA degrees of freedom (3 methods, 10 seeds -> 30 samples)
    df_between: int = 2   # n_methods - 1
    df_within: int = 27   # n_samples - n_methods
```

`setup_dirs` must additionally create `results_dir` (extend h-m1's function or add one line in orchestrator).

### Subtasks [3/3 used — matches architecture breakdown]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Define MultiSeedConfig | Subclass ExperimentConfig, add seeds/epochs/probes overrides |
| C-1-2 | Add dirs + gate thresholds | ckpt/fig/results dirs, F-ratio/Cohen's d/p thresholds, df constants |
| C-1-3 | Wire setup_dirs | Ensure results_dir created; single seed sanity default (seed=42) for smoke test |

---

## B-2: Vendor/import h-m1 modules [Complexity: 5, Budget: N/A — no config, sys.path wiring only]

No new config needed. Phase 4 Coder adds `sys.path.insert(0, str(Path(__file__).parent.parent.parent / "h-m1" / "code"))` before importing `config`, `data`, `model`, `train`, `attribution_trak`, `attribution_tracin`, `attribution_kronfluence` (mirrors h-m1's `run_experiment.py` pattern).
