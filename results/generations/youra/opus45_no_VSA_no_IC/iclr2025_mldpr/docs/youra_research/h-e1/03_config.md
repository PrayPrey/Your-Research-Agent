# Config: H-E1 Benchmark Fingerprint Detection

**Type:** EXISTENCE (PoC) — single fixed config, no hyperparameter search.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass

**Applied**: KB search ("DL config patterns") returned no directly relevant results (diffusion/inductor/JAX config, not applicable) — used standard PyTorch+sklearn PoC defaults instead.

---

## A-1..A-7: Shared Config [Complexity: n/a, Budget: 3 subtasks]

Single `Config` dataclass used by all modules (per architecture 03_architecture.md).

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field

@dataclass
class Config:
    # data
    benchmarks: list = field(default_factory=lambda: ["cub", "dogs", "flowers", "cars", "aircraft"])
    probe_dataset: str = "nabirds"
    data_root: str = "./data"
    num_workers: int = 4

    # reproducibility
    seeds: list = field(default_factory=lambda: [0, 1, 2])

    # finetuning (FR1.3)
    epochs: int = 30
    lr: float = 0.01
    batch_size: int = 32
    weight_decay: float = 1e-4
    momentum: float = 0.9
    # cosine annealing: T_max = epochs

    # model
    feature_dim: int = 2048
    pretrained: bool = True

    # linear probe (FR3)
    probe_C: float = 1.0                 # L2 reg strength
    probe_max_iter: int = 1000
    train_split: float = 0.70
    val_split: float = 0.15
    test_split: float = 0.15

    # stats (FR5)
    cv_folds: int = 3
    bootstrap_resamples: int = 1000
    chance_accuracy: float = 0.20        # 1/5 benchmarks

    # paths
    ckpt_dir: str = "./models/finetuned"
    feature_dir: str = "./features"
    results_path: str = "./results/h_e1_results.json"
    figure_path: str = "./figures/confusion_matrix.png"
```

No hyperparameter grid, no ablation variants — PoC uses fixed values from PRD directly (FR1.3, FR3.3, FR5.1/FR5.2).

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1 | Config dataclass | Implement `Config` in `src/config.py` exactly as above |
| C-2 | Path setup | Ensure `ckpt_dir`, `feature_dir`, results/figure parent dirs are created on load |
| C-3 | Seed utility | `set_seed(seed: int)` helper (torch/numpy/random) called per-model in A-3 |
