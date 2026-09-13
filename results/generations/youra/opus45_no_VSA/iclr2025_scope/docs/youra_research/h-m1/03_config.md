# Configuration: H-M1 (IPCR Routing)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None
**Pattern Used**: dataclass

**Applied**: Standard PyTorch/PEFT defaults (Archon KB search returned no directly applicable config patterns; using FR-2/FR-3 spec values from PRD)

---

## A-1: LoRA Adapter Config [Complexity: 2, Budget: 2]

### Configuration (Python Dataclass)
```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class LoRAConfig:
    rank: int = 16
    alpha: int = 32
    dropout: float = 0.05
    target_modules: List[str] = field(default_factory=lambda: ["q_proj", "v_proj"])
    bias: str = "none"
    task_type: str = "CAUSAL_LM"
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | LoRAConfig class | Define dataclass, convert to `peft.LoraConfig` |
| C-1-2 | Adapter bank builder | Instantiate k=8 named adapters from config |

---

## A-2: Router Config [Complexity: 1, Budget: 1]

### Configuration (Python Dataclass)
```python
@dataclass
class RouterConfig:
    encoder_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 384
    probe_checkpoint: str = "checkpoints/h-e1/linear_probe.pt"
    num_adapters: int = 8
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-2-1 | IPCRRouter loader | Load frozen MiniLM + H-E1 probe checkpoint |

---

## A-3: Training Config (LoRA pretraining) [Complexity: 2, Budget: 2]

### Configuration (Python Dataclass)
```python
@dataclass
class TrainingConfig:
    lr: float = 2e-4
    batch_size: int = 8
    epochs: int = 3
    optimizer: str = "adamw"
    weight_decay: float = 0.01
    seed: int = 42
    base_model: str = "meta-llama/Llama-2-7b-chat-hf"
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-3-1 | Per-family LoRA training loop | Train k=8 task-specific adapters |
| C-3-2 | Checkpoint saving | Save each adapter to `checkpoints/h-m1/{family}/` |

---

## A-4: Evaluation Config [Complexity: 1, Budget: 1]

### Configuration (Python Dataclass)
```python
@dataclass
class EvaluationConfig:
    held_out_families: int = 8
    min_samples: int = 500
    seed: int = 42
    metrics: List[str] = field(default_factory=lambda: ["accuracy", "rouge", "exact_match"])
    significance_alpha: float = 0.05
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-4-1 | Held-out eval + paired t-test | IPCR vs Oracle/Uniform/Random, gate check |

---

## ExperimentConfig (Combined)

```python
@dataclass
class ExperimentConfig:
    lora: LoRAConfig = field(default_factory=LoRAConfig)
    router: RouterConfig = field(default_factory=RouterConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    dataset_name: str = "Open-Orca/FLAN"
    output_dir: str = "results/h-m1"
```

**Total subtasks: 6/6 used** (budget met exactly)
