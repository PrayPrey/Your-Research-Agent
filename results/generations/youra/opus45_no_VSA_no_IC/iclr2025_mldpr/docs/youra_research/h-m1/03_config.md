# H-M1 Configuration: BFS-Gap Correlation Analysis

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: config classes verified from base code (`docs/youra_research/h-e1/code/config.py`)
**Config Files Found**: `h-e1/code/config.py` (dataclass `Config`)
**Pattern Used**: dataclass

**⚠️ Mismatch note**: H-E1's actual `Config.benchmarks` = `["cub", "dogs", "flowers", "cars", "aircraft"]` with `probe_dataset = "nabirds"` — NOT "Flowers102/CIFAR-100" as stated in `02c_experiment_brief.md`. This config uses the **actual H-E1 code values** (flowers + one other in-domain benchmark used for the 6 checkpoints). Phase 4 Coder: verify which 2 of the 5 benchmarks were actually fine-tuned (check `h-e1/code/models/finetuned/` filenames) and set `benchmarks` accordingly.

This is a **correlation analysis (evaluation-only)**, existence-style PoC: no training, no hyperparameter sweep, single fixed config.

## H-M1: BFS-Gap Correlation Analysis [Complexity: Low, Budget: PoC]

**Applied**: Standard scipy/sklearn evaluation config (no KB pattern needed - straightforward correlation analysis)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class HM1Config:
    # inherited from H-E1 (verified from h-e1/code/config.py)
    seeds: list = field(default_factory=lambda: [0, 1, 2])
    benchmarks: list = field(default_factory=lambda: ["flowers", "cub"])  # 2 in-domain benchmarks used for 6 checkpoints; VERIFY against actual finetuned/ dir
    feature_dim: int = 2048

    # H-E1 artifact paths (reuse, do not retrain)
    e1_ckpt_dir: str = "../h-e1/code/models/finetuned"
    e1_classifier_path: str = "../h-e1/code/models/fingerprint_classifier.pkl"
    e1_results_path: str = "../h-e1/code/results/h_e1_results.json"

    # datasets
    data_root: str = "./data"
    in_domain_split: str = "test"          # in-domain test split per benchmark (matches H-E1 test_split=0.15)
    cross_dataset: str = "nabirds"          # full NABirds test set
    num_workers: int = 4

    # evaluation
    eval_batch_size: int = 64
    device: str = "cuda"

    # correlation analysis
    correlation_method: str = "pearson"
    r_threshold: float = 0.3
    p_threshold: float = 0.05
    seed: int = 0  # single seed for analysis (no stochastic step involved)

    # outputs
    results_path: str = "./results/h_m1_results.json"
    figure_dir: str = "./figures"
    scatter_plot_path: str = "./figures/bfs_vs_gap_scatter.png"

    def __post_init__(self):
        for d in [self.data_root, Path(self.results_path).parent, self.figure_dir]:
            Path(d).mkdir(parents=True, exist_ok=True)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-M1-1 | Load H-E1 artifacts | Load 6 fine-tuned checkpoints + fingerprint classifier from `e1_ckpt_dir`/`e1_classifier_path` |
| C-M1-2 | Evaluate BFS + Gap | Compute BFS (classifier confidence) and Gap (in-domain acc - NABirds acc) per model |
| C-M1-3 | Correlation + plot | `scipy.stats.pearsonr(bfs, gaps)`, save scatter plot to `scatter_plot_path` |

## Inherited Configuration (Base Hypothesis)

```python
# From: h-e1/code/config.py (ACTUAL CODE)
@dataclass
class Config:
    benchmarks: list = field(default_factory=lambda: ["cub", "dogs", "flowers", "cars", "aircraft"])
    probe_dataset: str = "nabirds"
    feature_dim: int = 2048
    ckpt_dir: str = "./models/finetuned"
    train_split: float = 0.70
    val_split: float = 0.15
    test_split: float = 0.15
```

**Verified from**: `docs/youra_research/h-e1/code/config.py` (actual implementation). `HM1Config` above reuses `feature_dim`, checkpoint dir layout, and split convention; does not subclass since H-M1 needs no finetuning fields.
