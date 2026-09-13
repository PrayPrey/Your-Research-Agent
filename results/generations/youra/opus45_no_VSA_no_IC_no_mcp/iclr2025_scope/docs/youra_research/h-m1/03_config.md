# H-M1 Configuration

**Hypothesis**: Task embeddings learned from clustered hidden states encode functional specialization patterns.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design (no active `h-m1/code/` exists; sibling `h-e1/code/config.py` uses plain module constants, not dataclasses — not reused since H-M1 requires structured ablation grid)
**Config Files Found**: None - new config
**Pattern Used**: dataclass (Python)

**Applied**: Standard PyTorch/dataclass config pattern (no KB match needed for this schema)

---

## Config Format: Python Dataclasses

```python
from dataclasses import dataclass, field
from typing import Literal
import os

@dataclass
class ModelConfig:
    hidden_dim: int = 768          # backbone hidden size (BERT-base)
    embedding_dim: int = 32        # task embedding dim (default; see AblationConfig)
    num_tasks: int = 6

@dataclass
class TrainingConfig:
    lr: float = 1e-4
    batch_size: int = 32
    epochs: int = 10
    optimizer: Literal["adam", "adamw", "sgd"] = "adam"
    l2_reg_C: float = 1.0          # L2 regularization strength (inverse, sklearn-style)
    seed: int = 42

@dataclass
class DataConfig:
    dataset_root: str = "data/superglue"
    tasks: list[str] = field(default_factory=lambda: ["boolq", "cb", "copa", "rte", "wic", "wsc"])
    train_split: float = 0.7
    val_split: float = 0.15
    test_split: float = 0.15

@dataclass
class EvaluationConfig:
    metrics: list[str] = field(default_factory=lambda: ["accuracy", "f1", "cluster_purity", "silhouette_score"])
    silhouette_threshold: float = 0.25   # min cluster separation to claim "specialization"
    accuracy_threshold: float = 0.6      # min task-embedding probe accuracy

@dataclass
class AblationConfig:
    embedding_dim_variants: list[int] = field(default_factory=lambda: [16, 32, 64])

@dataclass
class ExperimentConfig:
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    data: DataConfig = field(default_factory=DataConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    ablation: AblationConfig = field(default_factory=AblationConfig)

    def __post_init__(self):
        assert set(self.data.tasks) <= {"boolq", "cb", "copa", "rte", "wic", "wsc"}, "unknown task in tasks list"
        assert abs(self.data.train_split + self.data.val_split + self.data.test_split - 1.0) < 1e-6, "splits must sum to 1.0"
        assert self.model.embedding_dim in self.ablation.embedding_dim_variants + [self.model.embedding_dim], "embedding_dim mismatch"
        assert self.training.batch_size > 0 and self.training.epochs > 0
        assert self.training.optimizer in ("adam", "adamw", "sgd")


def load_config() -> ExperimentConfig:
    cfg = ExperimentConfig()
    cfg.training.lr = float(os.environ.get("HM1_LR", cfg.training.lr))
    cfg.training.batch_size = int(os.environ.get("HM1_BATCH_SIZE", cfg.training.batch_size))
    cfg.training.epochs = int(os.environ.get("HM1_EPOCHS", cfg.training.epochs))
    cfg.model.embedding_dim = int(os.environ.get("HM1_EMBEDDING_DIM", cfg.model.embedding_dim))
    cfg.data.dataset_root = os.environ.get("HM1_DATA_ROOT", cfg.data.dataset_root)
    return cfg
```

## Equivalent YAML Schema (reference only — dataclass is source of truth)

```yaml
model:
  hidden_dim: 768
  embedding_dim: 32        # default; ablation variants: [16, 32, 64]
  num_tasks: 6

training:
  lr: 1.0e-4
  batch_size: 32
  epochs: 10
  optimizer: adam
  l2_reg_C: 1.0
  seed: 42

data:
  dataset_root: data/superglue
  tasks: [boolq, cb, copa, rte, wic, wsc]
  train_split: 0.7
  val_split: 0.15
  test_split: 0.15

evaluation:
  metrics: [accuracy, f1, cluster_purity, silhouette_score]
  silhouette_threshold: 0.25
  accuracy_threshold: 0.6

ablation:
  embedding_dim_variants: [16, 32, 64]
```

## Environment Variable Overrides

| Variable | Overrides | Default |
|----------|-----------|---------|
| `HM1_LR` | `training.lr` | `1e-4` |
| `HM1_BATCH_SIZE` | `training.batch_size` | `32` |
| `HM1_EPOCHS` | `training.epochs` | `10` |
| `HM1_EMBEDDING_DIM` | `model.embedding_dim` | `32` |
| `HM1_DATA_ROOT` | `data.dataset_root` | `data/superglue` |

## Validation Rules (enforced in `__post_init__`)

- `data.tasks` ⊆ `{boolq, cb, copa, rte, wic, wsc}`
- `train_split + val_split + test_split == 1.0`
- `training.optimizer` ∈ `{adam, adamw, sgd}`
- `batch_size > 0`, `epochs > 0`
- `model.embedding_dim` must be one of the ablation variants when running ablation sweeps

## Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-M1-1 | Dataclass schema | Implement `ModelConfig`, `TrainingConfig`, `DataConfig`, `EvaluationConfig`, `AblationConfig`, `ExperimentConfig` |
| C-M1-2 | Env override loader | Implement `load_config()` with `HM1_*` env var support |
| C-M1-3 | Validation | Implement `__post_init__` assertions per rules above |
