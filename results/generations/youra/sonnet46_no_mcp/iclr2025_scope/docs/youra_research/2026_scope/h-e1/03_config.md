# Config: H-E1 — Eviction-Aware LoRA Weight Divergence (EXISTENCE PoC)

**Applied**: HuggingFace Trainer LoRA config pattern (PEFT standard defaults + LongLoRA training reference)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field - no existing codebase to analyze
**Config Files Found**: None - new config design
**Pattern Used**: dataclass

---

## A-5: Training Loop [Complexity: 9, Budget: 1 subtask]

**Applied**: HuggingFace Trainer LoRA config pattern

### Full Dataclass Definitions (`code/h-e1/config.py`)

```python
from dataclasses import dataclass, field
from typing import List, Optional
import os

@dataclass
class LoRAConfig:
    rank: int = 16
    alpha: int = 32
    dropout: float = 0.05
    target_modules: List[str] = field(default_factory=lambda: ["q_proj", "v_proj"])

@dataclass
class TrainingConfig:
    model_name: str = ""
    condition: str = ""                        # "baseline" or "eviction-aware"
    output_dir: str = ""
    max_seq_length: int = 32768
    per_device_train_batch_size: int = 1
    gradient_accumulation_steps: int = 16      # effective batch = 16
    num_train_epochs: int = 1
    learning_rate: float = 2e-4
    warmup_ratio: float = 0.03
    lr_scheduler_type: str = "cosine"
    seed: int = 42
    kv_budget_ratio: float = 0.5
    fp16: bool = True
    bf16: bool = False                         # set True if GPU supports bfloat16
    dataloader_num_workers: int = 4
    save_strategy: str = "no"                  # final adapter only, no intermediate checkpoints
    logging_steps: int = 10
    report_to: str = "none"                    # "wandb" or "none" (CSV fallback)
    run_name: Optional[str] = None
    lora: LoRAConfig = field(default_factory=LoRAConfig)
```

### 4 Experiment Configurations

```python
def get_all_configs() -> List[TrainingConfig]:
    BASE_OUTPUT = "outputs/h-e1"
    return [
        # FR-1: LLaMA-2-7B Baseline
        TrainingConfig(
            model_name="meta-llama/Llama-2-7b-hf",
            condition="baseline",
            output_dir=f"{BASE_OUTPUT}/llama2-7b-baseline",
            run_name="h-e1-llama2-baseline",
        ),
        # FR-2: LLaMA-2-7B Eviction-Aware
        TrainingConfig(
            model_name="meta-llama/Llama-2-7b-hf",
            condition="eviction-aware",
            output_dir=f"{BASE_OUTPUT}/llama2-7b-eviction-aware",
            run_name="h-e1-llama2-eviction",
        ),
        # FR-3: Mistral-7B Baseline
        TrainingConfig(
            model_name="mistralai/Mistral-7B-v0.1",
            condition="baseline",
            output_dir=f"{BASE_OUTPUT}/mistral-7b-baseline",
            run_name="h-e1-mistral-baseline",
        ),
        # FR-4: Mistral-7B Eviction-Aware
        TrainingConfig(
            model_name="mistralai/Mistral-7B-v0.1",
            condition="eviction-aware",
            output_dir=f"{BASE_OUTPUT}/mistral-7b-eviction-aware",
            run_name="h-e1-mistral-eviction",
        ),
    ]
```

### HuggingFace TrainingArguments Mapping (`code/h-e1/train.py`)

```python
from transformers import TrainingArguments

def get_training_args(cfg: TrainingConfig) -> TrainingArguments:
    return TrainingArguments(
        output_dir=cfg.output_dir,
        num_train_epochs=cfg.num_train_epochs,
        per_device_train_batch_size=cfg.per_device_train_batch_size,
        gradient_accumulation_steps=cfg.gradient_accumulation_steps,
        learning_rate=cfg.learning_rate,
        warmup_ratio=cfg.warmup_ratio,
        lr_scheduler_type=cfg.lr_scheduler_type,
        fp16=cfg.fp16,
        bf16=cfg.bf16,
        seed=cfg.seed,
        dataloader_num_workers=cfg.dataloader_num_workers,
        save_strategy=cfg.save_strategy,
        logging_steps=cfg.logging_steps,
        report_to=cfg.report_to,
        run_name=cfg.run_name,
        remove_unused_columns=False,
        gradient_checkpointing=True,           # required for 32k seq len on single GPU
        optim="adamw_torch",
        ddp_find_unused_parameters=False,
    )
```

### Environment Variable Handling

```python
import os

# Set before any CUDA/torch imports - use single GPU with lowest memory usage
# Check: nvidia-smi | grep -E "MiB" to find empty GPU
os.environ["CUDA_VISIBLE_DEVICES"] = os.getenv("CUDA_VISIBLE_DEVICES", "0")

# Optional WandB config
os.environ["WANDB_PROJECT"] = os.getenv("WANDB_PROJECT", "youra-h-e1")
os.environ["WANDB_DISABLED"] = os.getenv("WANDB_DISABLED", "true")   # default off
```

### Logging Config

```python
# In TrainingConfig: report_to = "none" (default, CSV logs only)
# To enable WandB: set cfg.report_to = "wandb" and WANDB_DISABLED=false
# CSV logs auto-saved by Trainer to output_dir/trainer_log.jsonl

# Minimal logging setup in run_experiment.py:
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("outputs/h-e1/experiment.log"),
    ]
)
```

### Config Validation Rules

```python
def validate_config(cfg: TrainingConfig) -> None:
    assert cfg.condition in ("baseline", "eviction-aware"), \
        f"condition must be 'baseline' or 'eviction-aware', got: {cfg.condition}"
    assert cfg.model_name != "", "model_name must be set"
    assert cfg.output_dir != "", "output_dir must be set"
    assert 0.0 < cfg.kv_budget_ratio < 1.0, \
        f"kv_budget_ratio must be in (0, 1), got: {cfg.kv_budget_ratio}"
    assert cfg.lora.rank > 0 and (cfg.lora.rank & (cfg.lora.rank - 1)) == 0, \
        f"LoRA rank should be power of 2, got: {cfg.lora.rank}"
    assert not (cfg.fp16 and cfg.bf16), "fp16 and bf16 cannot both be True"
    os.makedirs(cfg.output_dir, exist_ok=True)
```

### YAML Schema (Reference Only)

```yaml
# experiment_config.yaml - matches TrainingConfig fields
model_name: "meta-llama/Llama-2-7b-hf"
condition: "baseline"           # "baseline" | "eviction-aware"
output_dir: "outputs/h-e1/llama2-7b-baseline"
max_seq_length: 32768
per_device_train_batch_size: 1
gradient_accumulation_steps: 16
num_train_epochs: 1
learning_rate: 0.0002
warmup_ratio: 0.03
lr_scheduler_type: "cosine"
seed: 42
kv_budget_ratio: 0.5
fp16: true
bf16: false
dataloader_num_workers: 4
save_strategy: "no"
logging_steps: 10
report_to: "none"               # "wandb" | "none"
run_name: null
lora:
  rank: 16
  alpha: 32
  dropout: 0.05
  target_modules: ["q_proj", "v_proj"]
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | TrainingArguments builder | `get_training_args(cfg: TrainingConfig) -> TrainingArguments` — maps all TrainingConfig fields to HuggingFace TrainingArguments; includes gradient_checkpointing=True for 32k seq len, adamw_torch optimizer, no intermediate checkpoints |
