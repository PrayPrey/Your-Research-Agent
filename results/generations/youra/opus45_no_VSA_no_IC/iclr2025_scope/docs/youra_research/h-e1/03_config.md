# Config: h-e1

**Type**: EXISTENCE (PoC) | **Gate**: MUST_WORK

Applied: HF Trainer + PEFT LoRA config sweep pattern (from architecture); no closer match in KB (results were unrelated: latent-diffusion, torch inductor, jax releases)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass (single format, no YAML/dict duplication)

---

## A-1: Config & data pipeline [Complexity: 6, Budget: 1 subtask]

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field

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
    grad_accum: int = 4              # effective batch = 32
    warmup_steps: int = 100
    max_length: int = 384
    lr_scheduler: str = "linear"
    grad_clip: float = 1.0           # NFR risk mitigation: training instability
    gradient_checkpointing: bool = True  # required for pythia-12b OOM mitigation

@dataclass
class LoRAConfig:
    rank: int = 16                   # overridden per sweep point
    alpha_multiplier: int = 2        # alpha = rank * alpha_multiplier (rsLoRA)
    dropout: float = 0.05
    target_modules: list[str] = field(default_factory=lambda: TARGET_MODULES)

@dataclass
class Paths:
    results_dir: str = "results"
    figures_dir: str = "figures"
    checkpoint_dir: str = "checkpoints"
    rank_sweep_csv: str = "results/h-e1_rank_sweep.csv"
    optimal_ranks_csv: str = "results/h-e1_optimal_ranks.csv"
    scaling_fit_json: str = "results/h-e1_scaling_fit.json"
    scaling_plot_png: str = "figures/h-e1_scaling_plot.png"

@dataclass
class AnalysisConfig:
    n_bootstrap: int = 1000
    alpha_ci: float = 0.95
```

No hyperparameter tuning — values fixed from PRD FR-3/FR-4. Sweep dimensions (MODELS × RANKS × SEEDS = 4×6×3 = 72 runs) are the experiment grid, not hyperparameter search.

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Config module | Define MODELS, RANKS, SEEDS, TrainConfig, LoRAConfig, Paths, AnalysisConfig dataclasses in `config.py` |

---

## Experiment Tracking Schema (rank_sweep.csv)

```
model,rank,seed,f1_score
pythia-1b,4,42,<float>
...
```

72 rows total (4 models × 6 ranks × 3 seeds). Written incrementally by `main.py` sweep driver for checkpoint/resume (A-4, separate task — not in this budget).

## Skipped

- No YAML file — dataclasses with Python defaults are sufficient for a green-field PoC; add YAML if Phase 4 needs CLI overrides.
- No per-model batch-size/lr overrides — PRD specifies uniform hyperparameters across all model sizes.
