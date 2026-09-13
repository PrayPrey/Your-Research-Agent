# Config: h-m2

**Applied**: No relevant KB pattern found — standard dataclass extension of h-e1 base config (verified from actual code).

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from base code (Serena unavailable for this path; read `h-e1/code/config.py` directly, consistent with architecture's own finding).
**Config Files Found**: `docs/youra_research/h-e1/code/config.py`
**Pattern Used**: dataclass

All budget items (B-1..B-9) are Low/Medium complexity — architecture already fully decomposed them; no further subtask breakdown needed (budget: 0 subtasks).

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code — `h-e1/code/config.py`)

```python
MODELS: dict[str, float] = {
    "pythia-1b": 1.0e9,
    "pythia-2.8b": 2.8e9,
    "pythia-6.9b": 6.9e9,
    "pythia-12b": 1.2e10,
}

MODEL_HF_IDS: dict[str, str] = {
    "pythia-1b": "EleutherAI/pythia-1b",
    "pythia-2.8b": "EleutherAI/pythia-2.8b",
    "pythia-6.9b": "EleutherAI/pythia-6.9b",
    "pythia-12b": "EleutherAI/pythia-12b",
}

RANKS: list[int] = [4, 8, 16, 32, 64, 128]
SEEDS: list[int] = [42, 1337, 2024]
TARGET_MODULES: list[str] = ["query_key_value"]

@dataclass
class TrainConfig:
    epochs: int = 3
    lr: float = 1e-4
    batch_size: int = 8
    grad_accum: int = 4
    warmup_steps: int = 100
    max_length: int = 384
    lr_scheduler: str = "linear"
    grad_clip: float = 1.0
    gradient_checkpointing: bool = True

@dataclass
class LoRAConfig:
    rank: int = 16
    alpha_multiplier: int = 2
    dropout: float = 0.05
    target_modules: list[str] = field(default_factory=lambda: TARGET_MODULES)
```

**Verified from**: `docs/youra_research/h-e1/code/config.py` (actual implementation, read directly).
**Integration**: Per architecture, `model.py`, `data.py`, `train.py`, and these constants/classes are copied verbatim into `h-m2/code/config.py`; h-m2 only adds `DATASETS`, `Paths` (new fields), and `StatsConfig` below.

---

## B-1..B-9: Shared Config [Complexity: all ≤ 9, Budget: 0 subtasks each]

**Applied**: Standard dataclass extension — new `Paths`/`StatsConfig` added alongside inherited base config, no new format introduced.

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field

# MODELS, MODEL_HF_IDS, RANKS, SEEDS, TARGET_MODULES, TrainConfig, LoRAConfig
# copied unchanged from h-e1/code/config.py (see Inherited Configuration above)

DATASETS: list[str] = ["squad_v2", "hotpotqa"]

@dataclass
class Paths:
    results_dir: str = "results"
    figures_dir: str = "figures"
    checkpoint_dir: str = "checkpoints"
    rank_sweep_squad_csv: str = "../h-e1/code/results/h-e1_rank_sweep.csv"  # reused, not regenerated
    rank_sweep_hotpotqa_csv: str = "results/h-m2_rank_sweep_hotpotqa.csv"
    sensitivities_csv: str = "results/h-m2_sensitivities.csv"
    phase_transition_json: str = "results/h-m2_phase_transition.json"
    sensitivity_plot_png: str = "figures/h-m2_sensitivity_vs_scale.png"
    rank_curves_png: str = "figures/h-m2_rank_curves.png"

@dataclass
class StatsConfig:
    alpha: float = 0.05
    n_bootstrap: int = 1000
    ratio_threshold: float = 2.0       # H0: S(12B) <= 2*S(1B)
    ci_lower_threshold: float = 1.5    # success criterion: 95% CI lower bound > 1.5
```

### HotpotQA-specific defaults (B-2, B-3)

```python
HOTPOTQA_HF_ID: str = "hotpot_qa"
HOTPOTQA_CONFIG: str = "distractor"
HOTPOTQA_SPLIT: str = "validation"
# max_length=384 (from TrainConfig, unchanged) — context = concatenated
# supporting + distractor paragraphs, truncated same as SQuAD tokenization
```

No new fields needed for B-4 (sweep driver reuses `TrainConfig`/`LoRAConfig`/`MODELS`/`RANKS`/`SEEDS`), B-5 (merge uses `Paths`), B-6 (sensitivity uses `RANKS`), B-7/B-8 (use `StatsConfig`), B-9 (uses `Paths`).

All 9 tasks share this single config module — no per-task subtask breakdown (budget: 0).
