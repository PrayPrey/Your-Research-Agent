---
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
date: 2026-05-12
author: architecture-agent
status: Phase 3 - Architecture Design
derived_from: 03_prd.md, 02c_experiment_brief.md
---

# System Architecture: h-e1 LoRA-MoE Coordination

**Applied Pattern**: Modular DL experiment (data/model/train/eval separation)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: New implementation from scratch
**Analyzed Path**: N/A
**Findings**: No existing code - clean slate implementation

---

## File Structure

```
h-e1/code/
├── config.py              # Configuration management
├── data.py                # Dataset loading and preprocessing
├── models/
│   ├── baseline.py        # Frozen Mixtral-8x7B
│   ├── proposed.py        # LoRA-MoE coordination
│   └── components.py      # Reusable components (router, LoRA expert)
├── train.py               # Training pipeline
├── evaluate.py            # Evaluation and metrics
├── visualize.py           # Figure generation
└── main.py                # Entry point
```

---

## Module Specifications

### Config (`config.py`)

**Dependencies**: None

```python
from dataclasses import dataclass
from typing import List

@dataclass
class DataConfig:
    glue_tasks: List[str]
    superglue_tasks: List[str]
    max_length: int
    batch_size: int
    num_workers: int

@dataclass
class ModelConfig:
    model_name: str
    lora_rank: int
    lora_alpha: int
    lora_dropout: float
    num_lora_experts: int
    top_k: int
    target_modules: List[str]

@dataclass
class TrainingConfig:
    learning_rate: float
    weight_decay: float
    num_epochs: int
    gradient_accumulation_steps: int
    warmup_steps: int
    alignment_loss_weight: float
    aux_loss_weight: float
    seed: int
    mixed_precision: str

@dataclass
class ExperimentConfig:
    data: DataConfig
    model: ModelConfig
    training: TrainingConfig
    output_dir: str
    checkpoint_dir: str
    figures_dir: str
    
    @classmethod
    def from_yaml(cls, path: str) -> "ExperimentConfig": ...
    
    def to_yaml(self, path: str) -> None: ...
```

---

### Data (`data.py`)

**Dependencies**: Config

```python
from torch.utils.data import Dataset, DataLoader
from typing import Dict, Tuple

class MultiTaskDataset(Dataset):
    def __init__(self, config: DataConfig, split: str): ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]: ...

def load_glue_task(task_name: str, split: str) -> Dataset: ...
def load_superglue_task(task_name: str, split: str) -> Dataset: ...

def create_dataloaders(config: DataConfig) -> Tuple[DataLoader, DataLoader]: ...
```

---

### Model Components (`models/components.py`)

**Dependencies**: Config

```python
import torch
import torch.nn as nn

class LoRAExpert(nn.Module):
    def __init__(self, hidden_dim: int, rank: int, alpha: int): ...
    def forward(self, x: torch.Tensor) -> torch.Tensor: ...

class LoRARouter(nn.Module):
    def __init__(self, hidden_dim: int, num_experts: int, top_k: int): ...
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]: ...

class CoordinationModule(nn.Module):
    def __init__(self, config: ModelConfig): ...
    def forward(
        self, 
        hidden_states: torch.Tensor,
        moe_expert_probs: torch.Tensor,
        task_weights: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]: ...
    def compute_alignment_loss(
        self,
        lora_probs: torch.Tensor,
        moe_probs: torch.Tensor,
        task_weights: torch.Tensor
    ) -> torch.Tensor: ...
```

---

### Baseline Model (`models/baseline.py`)

**Dependencies**: Config, Components

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

class BaselineModel(nn.Module):
    def __init__(self, config: ModelConfig): ...
    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        labels: torch.Tensor = None
    ) -> Dict[str, torch.Tensor]: ...
    def load_pretrained(self) -> None: ...
```

---

### Proposed Model (`models/proposed.py`)

**Dependencies**: Config, Components, Baseline

```python
class ProposedModel(nn.Module):
    def __init__(self, config: ModelConfig): ...
    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        labels: torch.Tensor = None,
        task_weights: torch.Tensor = None
    ) -> Dict[str, torch.Tensor]: ...
    def extract_moe_probs(self) -> torch.Tensor: ...
    def inject_coordination_modules(self) -> None: ...
```

---

### Training (`train.py`)

**Dependencies**: Config, Data, Models, Evaluate

```python
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR

class Trainer:
    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        config: TrainingConfig
    ): ...
    
    def train_epoch(self, epoch: int) -> Dict[str, float]: ...
    def validate(self) -> Dict[str, float]: ...
    def compute_task_weights(self, val_metrics: Dict[str, float]) -> torch.Tensor: ...
    def save_checkpoint(self, epoch: int, metrics: Dict[str, float]) -> None: ...
    def load_checkpoint(self, path: str) -> None: ...

def setup_optimizer(model: nn.Module, config: TrainingConfig) -> AdamW: ...
def setup_scheduler(optimizer: AdamW, config: TrainingConfig) -> CosineAnnealingLR: ...
```

---

### Evaluation (`evaluate.py`)

**Dependencies**: Config, Data

```python
from typing import Dict, List

class Evaluator:
    def __init__(self, model: nn.Module, config: DataConfig): ...
    def evaluate_task(self, task_name: str, dataloader: DataLoader) -> Dict[str, float]: ...
    def evaluate_all_tasks(self) -> Dict[str, Dict[str, float]]: ...
    def compute_aggregate_metrics(self, task_results: Dict) -> Dict[str, float]: ...
    def compute_super_additive_gain(
        self,
        baseline: float,
        lora_only: float,
        moe_only: float,
        proposed: float
    ) -> float: ...

def compute_expert_utilization_entropy(expert_probs: torch.Tensor) -> float: ...
def compute_routing_alignment(lora_probs: torch.Tensor, moe_probs: torch.Tensor) -> float: ...
```

---

### Visualization (`visualize.py`)

**Dependencies**: Evaluate

```python
import matplotlib.pyplot as plt
import seaborn as sns

def plot_gate_metrics(
    baseline: float,
    proposed: float,
    target: float,
    save_path: str
) -> None: ...

def plot_training_curves(
    metrics_history: Dict[str, List[float]],
    save_path: str
) -> None: ...

def plot_expert_utilization(
    expert_probs: torch.Tensor,
    task_names: List[str],
    save_path: str
) -> None: ...

def plot_per_task_comparison(
    task_results: Dict[str, Dict[str, float]],
    save_path: str
) -> None: ...

def generate_all_figures(
    results: Dict,
    metrics_history: Dict,
    save_dir: str
) -> None: ...
```

---

### Main Entry Point (`main.py`)

**Dependencies**: All modules

```python
def run_baseline_experiment(config: ExperimentConfig) -> Dict[str, float]: ...
def run_proposed_experiment(config: ExperimentConfig) -> Dict[str, float]: ...
def run_comparison(config: ExperimentConfig) -> Dict[str, Any]: ...
def generate_validation_report(results: Dict, output_path: str) -> None: ...

def main():
    config = ExperimentConfig.from_yaml("config.yaml")
    results = run_comparison(config)
    generate_validation_report(results, "04_validation.md")
    generate_all_figures(results, config.figures_dir)

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Configuration Setup | Create config.py with all hyperparameters from PRD | 5 | 1+1+2+1 (dataclass+yaml+validation+docs) |
| A-2 | Data Pipeline | Implement data.py: load GLUE+SuperGLUE, preprocessing, dataloaders | 12 | 3+3+3+3 (glue+superglue+tokenization+batching) |
| A-3 | Model Components | Build components.py: LoRAExpert, LoRARouter, CoordinationModule | 14 | 4+4+4+2 (expert+router+coordination+alignment_loss) |
| A-4 | Baseline Model | Implement baseline.py: load Mixtral-8x7B, freeze weights, forward pass | 10 | 3+2+3+2 (load+freeze+forward+device_map) |
| A-5 | Proposed Model | Build proposed.py: inject coordination modules, extract MoE probs | 16 | 4+5+4+3 (injection+moe_extract+forward+integration) |
| A-6 | Training Loop | Implement train.py: optimizer, scheduler, epoch loop, checkpointing | 13 | 3+3+4+3 (optimizer+epoch+loss+checkpoint) |
| A-7 | Evaluation System | Build evaluate.py: per-task metrics, aggregate, super-additive gain | 11 | 3+3+3+2 (task_eval+aggregate+gain+entropy) |
| A-8 | Visualization & Report | Create visualize.py + main.py: figures, validation report | 9 | 3+2+2+2 (gate_fig+curves+utils+report) |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-5], Medium(9-13): [A-2, A-3, A-4, A-6, A-7, A-8], Low(4-8): [A-1]

**Total Task Count**: 8 Epic tasks (within EXISTENCE 4-8 range)

---

## Design Rationale

**EXISTENCE Scope**: Minimal architecture for PoC validation.

**Key Simplifications**:
- Single seed (42) - no statistical testing
- Fixed hyperparameters - no tuning
- Baseline + Proposed only - no ablation modules
- Single experiment run - no multi-seed aggregation

**Complexity Drivers**:
- A-5 (16): Complex MoE integration, routing extraction, coordination injection
- A-3 (14): Novel coordination mechanism, alignment loss, routing logic
- A-6 (13): Multi-task training loop, gradient accumulation, loss composition
- A-2 (12): 17 tasks × 2 benchmarks, task-specific preprocessing

**Integration Points**:
- Data → Train: MultiTaskDataset provides task-level batching
- Components → Proposed: CoordinationModule injected into Mixtral layers
- Proposed → Train: Forward pass returns task_loss + alignment_loss
- Evaluate → Visualize: Metrics dict consumed by plotting functions
- All → Main: Orchestrates full experiment workflow

---

## Validation Checklist

- [x] No ASCII diagrams
- [x] Module sections = interface code only
- [x] 8 Epic tasks (within 4-8 EXISTENCE range)
- [x] Complexity scores with breakdown
- [x] Total length < 500 lines
- [x] Codebase Analysis section included
- [x] Applied pattern documented

---

*Generated by Phase 3 Architecture Agent*
*Hypothesis Type: EXISTENCE (PoC)*
*Target: Minimal viable architecture for super-additive coordination validation*
