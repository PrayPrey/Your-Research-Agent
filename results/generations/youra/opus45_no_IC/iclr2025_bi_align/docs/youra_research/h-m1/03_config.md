# Config: H-M1 (User Adaptation to AI Patterns)

**Type:** MECHANISM | **Tier:** STANDARD

Applied: No KB match (searched "DL config patterns experiment hyperparameters" — results were unrelated GPU/diffusion configs). Design follows PRD/architecture spec directly (statistical pipeline, not DL training).

## Codebase Analysis (Serena)

**Project Type:** green-field (extends H-E1 spec, but no `code/` exists for either hypothesis on disk)
**Status:** Green-field — designing new config schema. `h-e1/code/` does not exist yet; `config.py` skeleton in `03_architecture.md` is the only reference and is treated as authoritative since it's the intended file for this hypothesis itself.
**Config Files Found:** None
**Pattern Used:** Dataclass (single module-level `Config` object, matches architecture.md's flat `config.py` style)

---

## Configuration (Python Dataclass)

Single source of truth, `h-m1/code/config.py`. Not a training experiment — no hyperparameter grid, one fixed run.

```python
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ExperimentConfig:
    seed: int = 42
    n_workers: int = 8  # multiprocessing pool size (NFR-1: <60min for 26,395 convos)

    # Paths
    bcs_checkpoint_path: str = "h-e1/results/bcs_checkpoint.pkl"
    dataset_fallback: str = "Anthropic/hh-rlhf"
    results_dir: str = "h-m1/results"
    figures_dir: str = "h-m1/figures"
    results_path: str = "h-m1/results/lag_analysis.pkl"


@dataclass
class LagAnalysisConfig:
    max_lag: int = 3          # FR-2.3: support lag range [-3, +3]
    min_turns: int = 4        # FR-1.3 / NFR-4: min aligned turn pairs per convo
    min_valid_len: int = 3    # NFR-4: filter convos with <3 aligned pairs after lag shift
    primary_lag: int = 1      # FR-2.3: primary focus AI[t] -> User[t+1]
    significance_threshold: float = 0.05  # FR-3.1 gate criterion


@dataclass
class BaselineConfig:
    n_permutations: int = 1000  # FR-4.3
    random_seed: int = 42       # NFR-2 reproducibility
    null_p_threshold: float = 0.10  # FR-4.2: expected baseline p > 0.10


@dataclass
class LengthStratConfig:
    # FR-6.1 bins: short 4-6, medium 7-10, long 11+
    bins: dict = field(default_factory=lambda: {
        "short": (4, 6),
        "medium": (7, 10),
        "long": (11, None),
    })


@dataclass
class OutputConfig:
    checkpoint_path: str = "h-m1/results/lag_analysis.pkl"
    figure_dpi: int = 150
    figure_format: str = "png"
    figures: tuple = (
        "lag_profile.png",       # required: correlation vs lag
        "gate_pvalue.png",       # required: p-value vs 0.05 target
        "lag1_histogram.png",
        "length_scatter.png",
        "shuffled_vs_real.png",
        "length_heatmap.png",
    )
```

### Subtasks [0/9 used]

No subtasks allocated to Config Agent — task decomposition owned by Architecture (M-1..M-9 in `03_architecture.md`). Config values above map directly to those tasks' `config.py` dependency.

---

## YAML Equivalent (reference only, not used at runtime)

```yaml
experiment:
  seed: 42
  n_workers: 8
  bcs_checkpoint_path: h-e1/results/bcs_checkpoint.pkl
  dataset_fallback: Anthropic/hh-rlhf
  results_path: h-m1/results/lag_analysis.pkl

lag_analysis:
  max_lag: 3
  min_turns: 4
  min_valid_len: 3
  primary_lag: 1
  significance_threshold: 0.05

baseline:
  n_permutations: 1000
  random_seed: 42
  null_p_threshold: 0.10

length_strat:
  bins:
    short: [4, 6]
    medium: [7, 10]
    long: [11, null]

output:
  figure_dpi: 150
  figure_format: png
```

**Note**: Python dataclasses in `config.py` are the ready-to-import format Phase 4 Coder will use directly (`from config import ExperimentConfig, LagAnalysisConfig, BaselineConfig, LengthStratConfig, OutputConfig`). YAML block is documentation only — no YAML loader needed for this statistical pipeline (all-static config, no per-run overrides required).
