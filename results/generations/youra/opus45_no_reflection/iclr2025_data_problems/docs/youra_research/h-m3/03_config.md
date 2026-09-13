# Config: H-M3

**Applied**: dataclass ExperimentConfig pattern (from H-M2 base code)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M2)
**Status**: config classes verified from base code (direct file read of `h-m2/code/config.py`; no Serena project registered, functionally equivalent fallback per architecture doc)
**Config Files Found**: `h-m2/code/config.py`
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: h-m2/code/config.py (ACTUAL CODE)
@dataclass
class ExperimentConfig:
    dataset_name: str = "glue"
    dataset_config: str = "sst2"
    max_length: int = 128
    train_batch_size: int = 32
    epochs: int = 3
    lr: float = 2e-5
    bert_model_id: str = "bert-base-uncased"
    gpt2_model_id: str = "gpt2"
    gate_threshold: float = 0.10
    device: str = "cuda"
    output_dir: str = "."
    figures_dir: str = "../figures"
    checkpoints_dir: str = "./checkpoints"
    results_path: str = "results.yaml"
```

**Note**: H-M2 also defines `hessian_batch_size`, `lanczos_k`, `lanczos_steps`, `trace_matvecs`, `eigenvalues_path`, `seeds`, `ablation_batch_sizes` — not applicable to H-M3 (different mechanism), omitted from extended config.

**Verified from**: `docs/youra_research/h-m2/code/config.py`

---

## A-1..A-12: Full Pipeline Config [Complexity: total 105, Budget: all tasks]

**Applied**: single unified ExperimentConfig for entire attribution comparison pipeline (per architecture doc)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field

@dataclass
class ExperimentConfig:
    # Inherited from H-M2
    dataset_name: str = "glue"
    dataset_config: str = "sst2"
    max_length: int = 128
    train_batch_size: int = 32
    epochs: int = 3
    lr: float = 2e-5
    bert_model_id: str = "bert-base-uncased"
    gpt2_model_id: str = "gpt2"
    gate_threshold: float = 0.10
    device: str = "cuda"
    output_dir: str = "."
    figures_dir: str = "../figures"
    checkpoints_dir: str = "./checkpoints"
    results_path: str = "results.yaml"

    # H-M3 new fields
    mislabel_fraction: float = 0.05
    seed: int = 42
    ekfac_strategies: list[str] = field(default_factory=lambda: ["identity", "diagonal", "kfac", "ekfac"])
    trak_proj_dims: list[int] = field(default_factory=lambda: [1024, 2048, 4096])
    trak_default_proj_dim: int = 2048
    trak_seeds: list[int] = field(default_factory=lambda: [0, 1, 2, 3, 4])
    tracin_checkpoint_epochs: list[int] = field(default_factory=lambda: [1, 2, 3])
    mislabeled_indices_path: str = "mislabeled_indices.json"

GATE_CONFIG = {"min_relative_diff": 0.10}

FIGURE_FILES = {
    "gate_comparison": "gate_comparison.png",
    "quality_heatmap": "quality_heatmap.png",
    "score_distributions": "score_distributions.png",
    "rank_correlation": "rank_correlation.png",
}
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1 | ExperimentConfig dataclass | Define full config with inherited + H-M3 fields |
| C-2 | GATE_CONFIG dict | Threshold constant for gate verification |
| C-3 | FIGURE_FILES dict | Output figure filename mapping |
| C-4 | Checkpoint path templates | `bert_sst2_epoch{n}.pt`, `gpt2_sst2_epoch{n}.pt` naming |
| C-5 | Validate inherited defaults | Confirm lr/epochs/max_length match H-M2 actual code |
