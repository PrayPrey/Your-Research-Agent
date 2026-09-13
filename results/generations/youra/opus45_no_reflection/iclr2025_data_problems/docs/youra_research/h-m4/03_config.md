# Configuration: H-M4

**Format:** Python Dataclass (single `ExperimentConfig`)

**Applied**: Standard PyTorch/HF experiment-config dataclass convention (no specific Archon KB pattern matched — search returned unrelated diffusion-model docs).

## Codebase Analysis (Serena)

**Project Type**: green-field (h-m4/code/ not materialized; h-m3/code/ also absent — only specs exist)
**Status**: Green-field — new config design, no actual code to verify field names against
**Config Files Found**: None
**Pattern Used**: dataclass

---

## Core Config

```python
from dataclasses import dataclass, field

@dataclass
class ExperimentConfig:
    # Data
    dataset_name: str = "glue"
    dataset_config: str = "sst2"
    max_length: int = 128
    train_batch_size: int = 32

    # Training
    epochs: int = 3
    lr: float = 2e-5
    bert_model_id: str = "bert-base-uncased"
    gpt2_model_id: str = "gpt2"

    # Mislabeling
    mislabel_fraction: float = 0.05

    # Reproducibility
    seeds: list[int] = field(default_factory=lambda: [42, 123, 456])

    # Compute-budget sweep (proj_dim levels for EK-FAC/TRAK; checkpoint-count proxy for TracIn)
    compute_budgets: list[int] = field(default_factory=lambda: [64, 128, 256, 512, 1024])
    tracin_checkpoint_counts: dict = field(default_factory=lambda: {
        64: 1, 128: 1, 256: 2, 512: 2, 1024: 3,
    })  # budget level -> n_checkpoints used (max 3, matches epochs=3)

    # Methods / architectures under test
    methods: list[str] = field(default_factory=lambda: ["ekfac", "tracin", "trak"])
    architectures: list[str] = field(default_factory=lambda: ["bert", "gpt2"])

    # Statistics
    alpha: float = 0.05

    # Paths
    output_dir: str = "."
    figures_dir: str = "../figures"
    checkpoints_dir: str = "./checkpoints"

    # Device
    device: str = "cuda"
```

**Non-standard**: `tracin_checkpoint_counts` maps 5 compute-budget levels onto only 3 available epoch checkpoints (1/1/2/2/3) since fine-tuning saves 3 epochs total — repeats highest counts at top budget levels rather than requiring more checkpoints than epochs.

### YAML equivalent (for results.yaml / run manifest, not for code input)

```yaml
dataset_name: glue
dataset_config: sst2
max_length: 128
train_batch_size: 32
epochs: 3
lr: 2.0e-5
bert_model_id: bert-base-uncased
gpt2_model_id: gpt2
mislabel_fraction: 0.05
seeds: [42, 123, 456]
compute_budgets: [64, 128, 256, 512, 1024]
tracin_checkpoint_counts: {64: 1, 128: 1, 256: 2, 512: 2, 1024: 3}
methods: [ekfac, tracin, trak]
architectures: [bert, gpt2]
alpha: 0.05
```

---

## A-2: Model fine-tuning across seeds [Complexity: 9, Budget: 9]

**Applied**: Standard HF Trainer-free manual loop config (per-epoch checkpointing).

### Configuration (uses `ExperimentConfig` fields: `epochs`, `lr`, `train_batch_size`, `seeds`, `checkpoints_dir`)

Checkpoint naming: `{arch}_sst2_seed{seed}_epoch{epoch}.pt` (e.g. `bert_sst2_seed42_epoch1.pt`).

### Subtasks [3/3 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-2-1 | Model loaders | `load_bert_classifier`, `load_gpt2_classifier` return (model, tokenizer) |
| C-2-2 | Training loop | 3-epoch loop per seed, saves checkpoint after each epoch |
| C-2-3 | Checkpoint I/O | `load_checkpoint(model, path)` restores state_dict |

---

## A-8: Cross-seed statistical analysis [Complexity: 9, Budget: 9]

**Applied**: Paired t-test aggregation over fixed seed list, matching `alpha` from config.

### Configuration
```python
@dataclass
class StatsConfig:
    alpha: float = 0.05
    seeds: list[int] = field(default_factory=lambda: [42, 123, 456])
    predictions: tuple[str, ...] = ("P1_ekfac_gpt2_gt_bert", "P2_tracin_bert_gt_gpt2", "P3_trak_diff_lt_5pct")
    trak_invariance_threshold: float = 0.05  # 5% AUC diff threshold for P3
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-8-1 | Aggregation | `aggregate_seed_results`: mean/std per (method, arch, budget) |
| C-8-2 | Paired t-test | `paired_ttest_across_seeds(auc_bert, auc_gpt2)` per (method, budget) |
| C-8-3 | Prediction evaluation | `evaluate_predictions`: check P1/P2/P3 against `alpha` and `trak_invariance_threshold` |
| C-8-4 | Result assembly | Merge into `results.yaml`-ready dict |

---

## A-9: Visualization suite [Complexity: 10, Budget: 10]

**Applied**: matplotlib figure-config dict (paths + fixed styling), single hardcoded dict — no dataclass needed for plotting constants.

### Configuration
```python
PLOT_CONFIG = {
    "pareto_grid_shape": (2, 3),
    "figsize": (15, 8),
    "dpi": 150,
    "x_scale": "log",  # compute time axis
    "colors": {"bert": "#1f77b4", "gpt2": "#ff7f0e"},
    "fixed_budget_for_bar_chart": 256,  # mid-range budget for auc_bar_fixed_budget plot
}
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-9-1 | Pareto grid | `plot_pareto_frontier_grid`: 2x3, log-x compute time vs AUC |
| C-9-2 | Arch comparison | `plot_arch_comparison_per_method`: 3 overlaid BERT-vs-GPT2 plots |
| C-9-3 | Dominance + proj-dim plots | `plot_dominance_heatmap`, `plot_auc_vs_projdim` |
| C-9-4 | Fixed-budget bar chart | `plot_auc_bar_fixed_budget` at `fixed_budget_for_bar_chart=256` |
