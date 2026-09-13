# Configuration: H-M2 DPO Boundary Preservation

**Applied**: Standard TRL DPOTrainer + LoRA defaults (from experiment brief, no tuning)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design (h-m2/code/ does not exist yet; h-m1/code/config.py exists but H-M2 only consumes H-M1's *numeric baseline results*, not its config classes)
**Config Files Found**: None
**Pattern Used**: Python dataclass

---

## 1. Python Dataclasses

```python
from dataclasses import dataclass, field
from typing import List


@dataclass
class ModelConfig:
    base_model: str = "meta-llama/Llama-2-7b-hf"
    ref_model: str = "meta-llama/Llama-2-7b-hf"  # frozen reference
    torch_dtype: str = "bfloat16"


@dataclass
class LoraConfig:
    r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    target_modules: List[str] = field(
        default_factory=lambda: ["q_proj", "v_proj", "k_proj", "o_proj"]
    )
    task_type: str = "CAUSAL_LM"


@dataclass
class DPOTrainConfig:
    output_dir: str = "./dpo_model_h-m2"
    beta: float = 0.1  # preference sharpness temperature
    per_device_train_batch_size: int = 2
    gradient_accumulation_steps: int = 8
    num_train_epochs: int = 1
    learning_rate: float = 5e-7
    max_length: int = 512
    max_prompt_length: int = 256
    bf16: bool = True
    gradient_checkpointing: bool = True
    logging_steps: int = 50
    eval_strategy: str = "steps"
    eval_steps: int = 500
    save_strategy: str = "steps"
    save_steps: int = 1000
    seed: int = 42
    max_grad_norm: float = 1.0  # gradient clipping (training stability, risk mitigation)


@dataclass
class DataConfig:
    dataset_name: str = "Anthropic/hh-rlhf"
    fallback_dataset: str = "Trelis/hh-rlhf-dpo"  # pre-formatted alternative
    subsets: List[str] = field(
        default_factory=lambda: ["helpful-base", "helpful-online", "harmless-base"]
    )
    train_size: int = 160_000
    val_fraction: float = 0.10
    test_size: int = 5_000
    boundary_case_source: str = "h-m1"  # RLHF margin < 0.1 pairs
    boundary_margin_threshold: float = 0.1
    boundary_case_count: int = 500


@dataclass
class BaselineConfig:
    """H-M1 RLHF reference values for comparison (not trained; loaded as constants)."""
    rlhf_margin_mean: float = 0.023
    rlhf_accuracy: float = 0.535
    rlhf_reward_range: float = 0.83


@dataclass
class EvalConfig:
    kl_divergence_max: float = 1.0  # secondary success threshold
    sharpness_ratio_threshold: float = 1.0  # primary success threshold
    boundary_accuracy_threshold: float = 0.55
    confident_ratio_threshold: float = 0.3
    confidence_margin_threshold: float = 0.1  # |margin| > 0.1 = "confident"
    win_rate_threshold: float = 0.55
    generation_max_new_tokens: int = 256


@dataclass
class PathConfig:
    output_dir: str = "./dpo_model_h-m2"
    metrics_path: str = "./boundary_sharpness_metrics.json"
    plot_path: str = "./margin_comparison.png"
    boundary_cases_path: str = "./h-m1_boundary_cases.jsonl"


@dataclass
class ExperimentConfig:
    model: ModelConfig = field(default_factory=ModelConfig)
    lora: LoraConfig = field(default_factory=LoraConfig)
    train: DPOTrainConfig = field(default_factory=DPOTrainConfig)
    data: DataConfig = field(default_factory=DataConfig)
    baseline: BaselineConfig = field(default_factory=BaselineConfig)
    eval: EvalConfig = field(default_factory=EvalConfig)
    paths: PathConfig = field(default_factory=PathConfig)
```

Non-standard: `max_grad_norm=1.0` added beyond brief's explicit dict — required by brief's risk mitigation table ("gradient clipping") but omitted from the `DPOConfig` code sample.

---

## 2. YAML Configuration Schema

```yaml
model:
  base_model: meta-llama/Llama-2-7b-hf
  ref_model: meta-llama/Llama-2-7b-hf
  torch_dtype: bfloat16

lora:
  r: 16
  lora_alpha: 32
  lora_dropout: 0.05
  target_modules: [q_proj, v_proj, k_proj, o_proj]
  task_type: CAUSAL_LM

train:
  output_dir: ./dpo_model_h-m2
  beta: 0.1
  per_device_train_batch_size: 2
  gradient_accumulation_steps: 8
  num_train_epochs: 1
  learning_rate: 5.0e-7
  max_length: 512
  max_prompt_length: 256
  bf16: true
  gradient_checkpointing: true
  logging_steps: 50
  eval_strategy: steps
  eval_steps: 500
  save_strategy: steps
  save_steps: 1000
  seed: 42
  max_grad_norm: 1.0

data:
  dataset_name: Anthropic/hh-rlhf
  fallback_dataset: Trelis/hh-rlhf-dpo
  subsets: [helpful-base, helpful-online, harmless-base]
  train_size: 160000
  val_fraction: 0.10
  test_size: 5000
  boundary_case_source: h-m1
  boundary_margin_threshold: 0.1
  boundary_case_count: 500

baseline:
  rlhf_margin_mean: 0.023
  rlhf_accuracy: 0.535
  rlhf_reward_range: 0.83

eval:
  kl_divergence_max: 1.0
  sharpness_ratio_threshold: 1.0
  boundary_accuracy_threshold: 0.55
  confident_ratio_threshold: 0.3
  confidence_margin_threshold: 0.1
  win_rate_threshold: 0.55
  generation_max_new_tokens: 256

paths:
  output_dir: ./dpo_model_h-m2
  metrics_path: ./boundary_sharpness_metrics.json
  plot_path: ./margin_comparison.png
  boundary_cases_path: ./h-m1_boundary_cases.jsonl
```

---

## 3. Environment Variables (Compute Settings)

```bash
CUDA_VISIBLE_DEVICES=0          # 1x A100 80GB
HF_TOKEN=<huggingface_token>    # gated Llama-2 access
TRANSFORMERS_CACHE=./hf_cache
WANDB_DISABLED=true             # optional; enable for run tracking
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True  # mitigates OOM with 2 models loaded
```

---

## 4. Hyperparameter Ranges for Ablation

Per brief Secondary Criteria ("β parameter produces measurable sharpness effect") and risk mitigation ("use smaller β if needed"):

| Parameter | Default | Ablation Range | Notes |
|-----------|---------|-----------------|-------|
| `beta` | 0.1 | `[0.01, 0.05, 0.1, 0.5]` | Core sharpness control; brief flags reducing if KL explodes |
| `learning_rate` | 5e-7 | `[1e-7, 5e-7, 1e-6]` | Brief specifies low LR for stability |
| `lora.r` | 16 | `[8, 16, 32]` | Standard LoRA rank sweep |
| `num_train_epochs` | 1 | `[1, 2]` | Brief fixes to 1; extend only if underfit |

Ablations are optional extensions beyond the PRD's fixed config — primary run uses defaults only.

---

## 5. Subtasks

| ID | Subtask | Description |
|----|---------|--------------|
| C-M2-1 | Dataclass module | Implement dataclasses above in `code/config.py` |
| C-M2-2 | YAML loader | Load/merge YAML into `ExperimentConfig` (e.g., via `omegaconf` or manual `**dict` unpack) |
| C-M2-3 | Env var wiring | Read `CUDA_VISIBLE_DEVICES`, `HF_TOKEN` at startup |
