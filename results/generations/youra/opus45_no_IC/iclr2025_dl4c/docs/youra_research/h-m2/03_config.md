# Configuration: H-M2 (Token Masking / FGO)

**Type:** MECHANISM | **Budget:** FULL tier (max 30 tasks)

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** No `code/` folder found at H-M1 (`h-m1/code/`) or in repo — green-field, new config design.
**Config Files Found:** None
**Pattern Used:** Python dataclass

**Applied:** Standard PPO hyperparameter defaults (TRL/OpenRLHF conventions)

---

## A-1: Training Configuration [Complexity: 3, Budget: 8]

**Applied:** Standard PPO config pattern (TRL PPOTrainer conventions)

### Configuration (Python Dataclass)
```python
from dataclasses import dataclass, field
from typing import Literal

@dataclass
class TrainingConfig:
    algorithm: str = "ppo"
    optimizer: str = "adamw"
    learning_rate: float = 1e-5
    lr_schedule: str = "cosine"
    batch_size: int = 16
    ppo_epochs: int = 4
    clip_epsilon: float = 0.2
    gae_lambda: float = 0.95
    gamma: float = 1.0
    training_steps: int = 1000
    max_grad_norm: float = 1.0
    weight_decay: float = 0.01
    seeds: list = field(default_factory=lambda: [42, 123, 456])

@dataclass
class ModelConfig:
    model_name: str = "meta-llama/CodeLlama-7b-Instruct-hf"
    context_length: int = 4096
    dtype: str = "float16"
    device_map: str = "auto"
```

### Subtasks [3/8 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | PPO trainer setup | Init TRL PPOTrainer with TrainingConfig |
| C-1-2 | Optimizer/scheduler | AdamW + cosine schedule wiring |
| C-1-3 | Model loading | Load CodeLlama-7B-Instruct per ModelConfig |

---

## A-2: FGO Masking Configuration [Complexity: 4, Budget: 10]

**Applied:** StepCoder Algorithm 1 (FGO masked PPO loss)

### Configuration (Python Dataclass)
```python
@dataclass
class MaskingConfig:
    masking_mode: Literal["none", "random", "trace"] = "trace"
    zero_grad_eps: float = 1e-8  # denominator epsilon for masked-token avg
    random_mask_seed: int = 42
    # random masking must match trace-based sparsity per-sample
    match_sparsity_to_trace: bool = True
```

### Subtasks [4/10 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | compute_fgo_masked_loss | Implement masked PPO loss (per brief pseudocode) |
| C-2-2 | Trace-to-mask mapping | Reuse H-M1 token classifier to build execution_mask |
| C-2-3 | Random mask generator | Sample random mask matching trace sparsity per example |
| C-2-4 | Gradient verification hook | Log per-position grad norms, assert masked==0 |

---

## A-3: Ablation Conditions Configuration [Complexity: 2, Budget: 4]

**Applied:** Standard ablation-condition dict pattern

### Configuration (Python Dataclass)
```python
@dataclass
class AblationCondition:
    name: str
    masking_mode: str

ABLATION_CONDITIONS: list = [
    AblationCondition(name="no_masking", masking_mode="none"),
    AblationCondition(name="random_masking", masking_mode="random"),
    AblationCondition(name="trace_masking", masking_mode="trace"),
]
```

### Subtasks [1/4 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Condition runner | Loop conditions × seeds, dispatch training runs |

---

## A-4: Dataset & Evaluation Configuration [Complexity: 3, Budget: 6]

**Applied:** Standard HF datasets + pass@k eval pattern

### Configuration (Python Dataclass)
```python
@dataclass
class DataConfig:
    humaneval_id: str = "openai_humaneval"
    mbpp_id: str = "mbpp"
    humaneval_split: str = "test"
    mbpp_split: str = "test"

@dataclass
class EvalConfig:
    k: int = 1
    num_samples: int = 1
    significance_test: str = "paired_ttest"
    alpha: float = 0.05
```

### Subtasks [2/6 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Dataset loader | Load & merge HumanEval + MBPP test splits |
| C-4-2 | pass@1 + stats | Compute pass@1 per condition, paired t-test across seeds |

---

## A-5: Experiment Orchestration [Complexity: 2, Budget: 2]

**Applied:** Standard experiment-runner dict/dataclass composition

### Configuration (Python Dataclass)
```python
@dataclass
class ExperimentConfig:
    training: TrainingConfig = field(default_factory=TrainingConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    masking: MaskingConfig = field(default_factory=MaskingConfig)
    data: DataConfig = field(default_factory=DataConfig)
    eval: EvalConfig = field(default_factory=EvalConfig)
    output_dir: str = "./results/h-m2"
```

### Subtasks [1/2 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Result/figure output | Save JSON results + gate metrics bar chart |

---

**Total subtasks allocated:** 11/30 (within FULL tier budget)
