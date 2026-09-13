# Configuration: h-e1 - Uncertainty Quantification for Selective Prediction

**Date:** 2026-08-20
**Hypothesis:** EXISTENCE
**Status:** PoC Configuration

Applied: Standard PyTorch DL config patterns

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field project - designing new config schema
**Config Files Found:** None - new config
**Pattern Used:** Python dataclass (single source of truth)

---

## Configuration Schema

### Python Dataclass (config.py)

```python
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class ModelConfig:
    """Model inference configuration."""
    model_id: str = "meta-llama/Llama-3.1-8B-Instruct"
    cache_dir: str = "./cache"
    batch_size: int = 8
    max_tokens: int = 100
    temperature: float = 1.0
    top_p: float = 1.0
    device_map: str = "auto"
    torch_dtype: str = "float16"


@dataclass
class DataConfig:
    """Dataset loading and splitting configuration."""
    dataset_name: str = "truthfulqa/truthful_qa"
    dataset_config: str = "generation"
    cal_ratio: float = 0.4
    seed: int = 42


@dataclass
class UQConfig:
    """Uncertainty quantification methods configuration."""
    # Temperature scaling
    temp_epochs: int = 50
    temp_lr: float = 0.01
    
    # Conformal prediction
    alpha: float = 0.1
    
    # MC dropout
    dropout_rate: float = 0.1
    mc_k_values: list[int] = field(default_factory=lambda: [1, 3, 5, 10])


@dataclass
class EvaluationConfig:
    """Evaluation and gating configuration."""
    auroc_threshold: float = 0.7
    spearman_threshold: float = 0.2
    save_results: bool = True
    results_dir: str = "./results"
    plots_dir: str = "./plots"


@dataclass
class ExperimentConfig:
    """Root configuration for h-e1 experiment."""
    model: ModelConfig = field(default_factory=ModelConfig)
    data: DataConfig = field(default_factory=DataConfig)
    uq: UQConfig = field(default_factory=UQConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
```

---

## Subtask Allocation

**Budget:** 2 subtasks
**Used:** 2/2

| ID | Subtask | Description |
|----|---------|-------------|
| C-1 | Dataclass schema | ExperimentConfig with nested configs (model, data, uq, evaluation) |
| C-2 | Default hyperparameters | seed=42, alpha=0.1, batch_size=8, auroc_threshold=0.7 |

---

## Usage Example

```python
from config import ExperimentConfig

# Default configuration
config = ExperimentConfig()

# Override specific values
config.model.batch_size = 16
config.uq.alpha = 0.05
config.data.seed = 123

# Access nested configs
print(config.model.model_id)  # meta-llama/Llama-3.1-8B-Instruct
print(config.uq.mc_k_values)  # [1, 3, 5, 10]
```

---

## Validation Notes

- [x] Single format (dataclass only)
- [x] No ASCII diagrams
- [x] Codebase Analysis section included
- [x] Subtask count within budget (2/2)
- [x] Total length < 400 lines
- [x] EXISTENCE PoC: Single fixed config (no hyperparameter grid)
