---
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
date: 2026-05-12
author: configuration-agent
status: Phase 3 - Configuration Design
derived_from: 03_architecture.md, 03_prd.md
---

# Configuration Specification: h-e1 LoRA-MoE Coordination

**Applied**: PEFT LoRA defaults, HuggingFace training patterns, PyTorch standard config

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project - designing new config schema
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## A-1: Configuration Setup [Complexity: 5, Budget: 5]

**Applied**: Standard dataclass pattern from architecture spec

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List
import yaml

@dataclass
class DataConfig:
    """Dataset configuration for GLUE + SuperGLUE tasks"""
    glue_tasks: List[str] = field(default_factory=lambda: [
        "cola", "sst2", "mrpc", "qqp", "mnli", "qnli", "rte", "wnli", "stsb"
    ])
    superglue_tasks: List[str] = field(default_factory=lambda: [
        "boolq", "cb", "copa", "multirc", "record", "rte", "wic", "wsc"
    ])
    max_length: int = 512
    batch_size: int = 32
    num_workers: int = 4
    
    def get_all_tasks(self) -> List[str]:
        """Returns combined list of all tasks"""
        return self.glue_tasks + self.superglue_tasks


@dataclass
class ModelConfig:
    """Model architecture configuration"""
    model_name: str = "mistralai/Mixtral-8x7B-v0.1"
    
    # LoRA parameters
    lora_rank: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    num_lora_experts: int = 8
    top_k: int = 2
    target_modules: List[str] = field(default_factory=lambda: [
        "q_proj", "k_proj", "v_proj", "o_proj"
    ])
    
    # MoE parameters
    num_moe_experts: int = 8
    moe_top_k: int = 2


@dataclass
class TrainingConfig:
    """Training hyperparameters"""
    learning_rate: float = 3e-4
    weight_decay: float = 0.01
    num_epochs: int = 5
    gradient_accumulation_steps: int = 4
    warmup_steps: int = 500
    
    # Loss weights
    alignment_loss_weight: float = 0.01
    aux_loss_weight: float = 0.01
    
    # Optimization
    adam_beta1: float = 0.9
    adam_beta2: float = 0.999
    adam_epsilon: float = 1e-8
    max_grad_norm: float = 1.0
    
    # Reproducibility
    seed: int = 42
    
    # Precision
    mixed_precision: str = "bf16"


@dataclass
class ExperimentConfig:
    """Complete experiment configuration"""
    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    
    # Output paths
    output_dir: str = "./outputs"
    checkpoint_dir: str = "./checkpoints"
    figures_dir: str = "./figures"
    
    # Experiment metadata
    experiment_name: str = "h-e1-lora-moe-coordination"
    
    @classmethod
    def from_yaml(cls, path: str) -> "ExperimentConfig":
        """Load config from YAML file"""
        with open(path, 'r') as f:
            config_dict = yaml.safe_load(f)
        
        data_cfg = DataConfig(**config_dict.get('data', {}))
        model_cfg = ModelConfig(**config_dict.get('model', {}))
        training_cfg = TrainingConfig(**config_dict.get('training', {}))
        
        return cls(
            data=data_cfg,
            model=model_cfg,
            training=training_cfg,
            output_dir=config_dict.get('output_dir', './outputs'),
            checkpoint_dir=config_dict.get('checkpoint_dir', './checkpoints'),
            figures_dir=config_dict.get('figures_dir', './figures'),
            experiment_name=config_dict.get('experiment_name', 'h-e1-lora-moe-coordination')
        )
    
    def to_yaml(self, path: str) -> None:
        """Save config to YAML file"""
        config_dict = {
            'data': self.data.__dict__,
            'model': self.model.__dict__,
            'training': self.training.__dict__,
            'output_dir': self.output_dir,
            'checkpoint_dir': self.checkpoint_dir,
            'figures_dir': self.figures_dir,
            'experiment_name': self.experiment_name
        }
        with open(path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False)
```

### Default YAML Configuration

```yaml
# config.yaml - Default experiment configuration for h-e1

data:
  glue_tasks:
    - cola
    - sst2
    - mrpc
    - qqp
    - mnli
    - qnli
    - rte
    - wnli
    - stsb
  superglue_tasks:
    - boolq
    - cb
    - copa
    - multirc
    - record
    - rte
    - wic
    - wsc
  max_length: 512
  batch_size: 32
  num_workers: 4

model:
  model_name: "mistralai/Mixtral-8x7B-v0.1"
  lora_rank: 8
  lora_alpha: 16
  lora_dropout: 0.05
  num_lora_experts: 8
  top_k: 2
  target_modules:
    - q_proj
    - k_proj
    - v_proj
    - o_proj
  num_moe_experts: 8
  moe_top_k: 2

training:
  learning_rate: 0.0003
  weight_decay: 0.01
  num_epochs: 5
  gradient_accumulation_steps: 4
  warmup_steps: 500
  alignment_loss_weight: 0.01
  aux_loss_weight: 0.01
  adam_beta1: 0.9
  adam_beta2: 0.999
  adam_epsilon: 1.0e-08
  max_grad_norm: 1.0
  seed: 42
  mixed_precision: "bf16"

output_dir: "./outputs"
checkpoint_dir: "./checkpoints"
figures_dir: "./figures"
experiment_name: "h-e1-lora-moe-coordination"
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | DataConfig class | Define dataclass with GLUE/SuperGLUE task lists |
| C-1-2 | ModelConfig class | Define LoRA and MoE hyperparameters |
| C-1-3 | TrainingConfig class | Define optimizer, scheduler, loss weights |
| C-1-4 | ExperimentConfig class | Combine all configs with YAML I/O methods |
| C-1-5 | Default YAML file | Create config.yaml with all default values |

---

## Configuration Rationale

### LoRA Parameters

**lora_rank=8, lora_alpha=16**: Standard PEFT defaults for parameter efficiency. Alpha=2×rank provides balanced adaptation strength.

**lora_dropout=0.05**: Conservative dropout to prevent overfitting in multi-task scenario.

**num_lora_experts=8**: Matches Mixtral's 8 MoE experts for 1-to-1 coordination alignment.

**target_modules**: Attention projections only (q/k/v/o) - balances efficiency with expressiveness.

### Training Parameters

**learning_rate=3e-4**: Standard AdamW LR for LoRA fine-tuning (from PRD).

**gradient_accumulation_steps=4**: Effective batch size = 32×4 = 128 for stable training.

**alignment_loss_weight=0.01, aux_loss_weight=0.01**: Small weights to guide coordination without overwhelming task loss.

**num_epochs=5**: EXISTENCE PoC - minimal epochs to detect coordination signal.

**seed=42**: Single seed for EXISTENCE hypothesis (no statistical testing).

### Data Parameters

**max_length=512**: Standard for GLUE/SuperGLUE tasks - covers 95%+ of sequences.

**batch_size=32**: Balances memory usage with training speed on single GPU.

**num_workers=4**: Parallel data loading without CPU bottleneck.

---

## Validation Checklist

- [x] Single format (dataclass with YAML I/O)
- [x] No ASCII diagrams
- [x] Rationale only for non-standard values
- [x] Subtask count = 5 (within budget)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included
- [x] Applied pattern documented

---

*Generated by Phase 3 Configuration Agent*
*Hypothesis Type: EXISTENCE (PoC)*
*Pattern: Dataclass + YAML for copy-paste ready configuration*
