# Configuration: h-m2 Training Dynamics Measurement

**Hypothesis ID:** h-m2  
**Type:** MECHANISM  
**Gate:** MUST_WORK  
**Date:** 2026-08-19  

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends h-e1)  
**Status**: Config schema reuses h-e1 YAML structure  
**Config Files Found**: h-e1/code/config.yaml, h-e1/code/config.py  
**Pattern Used**: YAML (training configs), Python dict (runtime constants)

---

## Configuration Strategy

**Format:** YAML (6 files, one per model × feedback combination)

**Inheritance:** Reuse h-e1 hyperparameters for reproducibility (SFT baseline identical, GRPO parameters from PRD Section 2.4).

**Key Changes from h-e1:**
- GRPO learning rate: 5e-6 (h-e1 used 2e-7)
- GRPO batch size: 8 (h-e1 used 4)
- GRPO group size: 8 (h-e1 used 4 samples_per_problem)
- Added dynamics logging configuration
- Added error+trace reward schema (new feedback type)

---

## Base Configuration Schema

```yaml
# Common structure for all 6 configs
experiment:
  hypothesis_id: "h-m2"
  type: "MECHANISM"
  gate: "MUST_WORK"
  experiment_id: "{feedback_type}_{model_size}"  # e.g., "binary_350m"

dataset:
  name: "openai/openai_humaneval"
  split: "test"
  num_problems: 164
  cache_dir: "/home/PrayPrey/.cache/huggingface/datasets/openai_humaneval"

model:
  name: "{model_path}"  # Model-specific
  precision: "fp16"
  cache_dir: "/home/PrayPrey/.cache/huggingface/hub"

lora:
  enabled: true
  r: 16
  alpha: 32
  dropout: 0.05
  target_modules:
    - "q_proj"
    - "v_proj"
  bias: "none"
  task_type: "CAUSAL_LM"

training:
  sft:
    enabled: true
    optimizer: "adamw"
    learning_rate: 2.0e-5
    weight_decay: 0.01
    epochs: 3
    batch_size: 8
    gradient_accumulation_steps: 1
    max_grad_norm: 1.0
    warmup_steps: 100
    lr_scheduler: "linear"
    checkpoint_dir: "../checkpoints/{experiment_id}/sft"
    log_interval: 10
    save_interval: 100

  grpo:
    enabled: true
    optimizer: "adamw"
    learning_rate: 5.0e-6
    weight_decay: 0.01
    epochs: 5
    batch_size: 8
    group_size: 8
    gradient_accumulation_steps: 2
    max_grad_norm: 1.0
    kl_penalty: 0.04
    clip_eps: 0.2
    warmup_steps: 50
    lr_scheduler: "constant"
    checkpoint_dir: "../checkpoints/{experiment_id}/grpo"
    log_interval: 10
    save_every_epoch: true
    feedback_type: "{feedback_type}"  # binary | error_type | error_trace

execution_sandbox:
  timeout: 3.0
  binary_rewards:
    pass: 1.0
    fail: 0.0
  error_type_rewards:
    SyntaxError: 0.2
    TypeError: 0.35
    NameError: 0.5
    IndexError: 0.65
    ValueError: 0.8
    Pass: 1.0
    Timeout: 0.0
    OtherError: 0.0
  error_trace_rewards:
    error_types:
      - "SyntaxError"
      - "TypeError"
      - "NameError"
      - "IndexError"
      - "ValueError"
    error_type_weight: 0.15  # Per error type increment
    depth_buckets: [0, 1, 2, 3, 5, 10, 20, 50, 100, 200]
    depth_weight: 0.05  # Per bucket increment
    pass: 1.0

generation:
  training:
    max_new_tokens: 512
    temperature: 1.0
    top_p: 0.95
    do_sample: true
    num_return_sequences: 8
    stop_tokens:
      - "\n\n"
      - "def "
      - "class "

  evaluation:
    max_new_tokens: 512
    temperature: 0.0
    top_p: 1.0
    do_sample: false
    num_return_sequences: 1
    stop_tokens:
      - "\n\n"
      - "def "
      - "class "

logging:
  dynamics_log: "../logs/{experiment_id}_dynamics.json"
  log_level: "INFO"
  log_file: "../logs/{experiment_id}.log"
  console_output: true
  dynamics_enabled: true  # Enable per-batch gradient variance logging

evaluation:
  checkpoint_paths:
    sft: "../checkpoints/{experiment_id}/sft/final_checkpoint.pt"
    grpo: "../checkpoints/{experiment_id}/grpo/epoch_{1-5}.pt"
  output_dir: "../results/{experiment_id}"
  save_completions: true

gate:
  thresholds:
    convergence_speedup: 0.20  # Binary/error-type must converge ≥20% faster than error+trace
    variance_reduction: 0.30   # Binary/error-type must show ≥30% lower gradient variance

hardware:
  device: "cuda"
  fp16: true

reproducibility:
  seed: 42
  deterministic: true
  benchmark: false

state_management:
  verification_state_path: "../../../../verification_state.yaml"
```

---

## Concrete Configurations

### 1. binary_350m.yaml

```yaml
experiment:
  hypothesis_id: "h-m2"
  type: "MECHANISM"
  gate: "MUST_WORK"
  experiment_id: "binary_350m"

dataset:
  name: "openai/openai_humaneval"
  split: "test"
  num_problems: 164
  cache_dir: "/home/PrayPrey/.cache/huggingface/datasets/openai_humaneval"

model:
  name: "Salesforce/codegen-350M-mono"
  precision: "fp16"
  cache_dir: "/home/PrayPrey/.cache/huggingface/hub"

lora:
  enabled: true
  r: 16
  alpha: 32
  dropout: 0.05
  target_modules: ["q_proj", "v_proj"]
  bias: "none"
  task_type: "CAUSAL_LM"

training:
  sft:
    enabled: true
    optimizer: "adamw"
    learning_rate: 2.0e-5
    weight_decay: 0.01
    epochs: 3
    batch_size: 8
    gradient_accumulation_steps: 1
    max_grad_norm: 1.0
    warmup_steps: 100
    lr_scheduler: "linear"
    checkpoint_dir: "../checkpoints/binary_350m/sft"
    log_interval: 10
    save_interval: 100

  grpo:
    enabled: true
    optimizer: "adamw"
    learning_rate: 5.0e-6
    weight_decay: 0.01
    epochs: 5
    batch_size: 8
    group_size: 8
    gradient_accumulation_steps: 2
    max_grad_norm: 1.0
    kl_penalty: 0.04
    clip_eps: 0.2
    warmup_steps: 50
    lr_scheduler: "constant"
    checkpoint_dir: "../checkpoints/binary_350m/grpo"
    log_interval: 10
    save_every_epoch: true
    feedback_type: "binary"

execution_sandbox:
  timeout: 3.0
  binary_rewards:
    pass: 1.0
    fail: 0.0

generation:
  training:
    max_new_tokens: 512
    temperature: 1.0
    top_p: 0.95
    do_sample: true
    num_return_sequences: 8
    stop_tokens: ["\n\n", "def ", "class "]
  evaluation:
    max_new_tokens: 512
    temperature: 0.0
    top_p: 1.0
    do_sample: false
    num_return_sequences: 1
    stop_tokens: ["\n\n", "def ", "class "]

logging:
  dynamics_log: "../logs/binary_350m_dynamics.json"
  log_level: "INFO"
  log_file: "../logs/binary_350m.log"
  console_output: true
  dynamics_enabled: true

evaluation:
  checkpoint_paths:
    sft: "../checkpoints/binary_350m/sft/final_checkpoint.pt"
  output_dir: "../results/binary_350m"
  save_completions: true

gate:
  thresholds:
    convergence_speedup: 0.20
    variance_reduction: 0.30

hardware:
  device: "cuda"
  fp16: true

reproducibility:
  seed: 42
  deterministic: true
  benchmark: false

state_management:
  verification_state_path: "../../../../verification_state.yaml"
```

### 2. error_type_350m.yaml

```yaml
experiment:
  experiment_id: "error_type_350m"
  hypothesis_id: "h-m2"
  type: "MECHANISM"
  gate: "MUST_WORK"

dataset:
  name: "openai/openai_humaneval"
  split: "test"
  num_problems: 164
  cache_dir: "/home/PrayPrey/.cache/huggingface/datasets/openai_humaneval"

model:
  name: "Salesforce/codegen-350M-mono"
  precision: "fp16"
  cache_dir: "/home/PrayPrey/.cache/huggingface/hub"

lora:
  enabled: true
  r: 16
  alpha: 32
  dropout: 0.05
  target_modules: ["q_proj", "v_proj"]
  bias: "none"
  task_type: "CAUSAL_LM"

training:
  sft:
    enabled: true
    optimizer: "adamw"
    learning_rate: 2.0e-5
    weight_decay: 0.01
    epochs: 3
    batch_size: 8
    gradient_accumulation_steps: 1
    max_grad_norm: 1.0
    warmup_steps: 100
    lr_scheduler: "linear"
    checkpoint_dir: "../checkpoints/error_type_350m/sft"
    log_interval: 10
    save_interval: 100

  grpo:
    enabled: true
    optimizer: "adamw"
    learning_rate: 5.0e-6
    weight_decay: 0.01
    epochs: 5
    batch_size: 8
    group_size: 8
    gradient_accumulation_steps: 2
    max_grad_norm: 1.0
    kl_penalty: 0.04
    clip_eps: 0.2
    warmup_steps: 50
    lr_scheduler: "constant"
    checkpoint_dir: "../checkpoints/error_type_350m/grpo"
    log_interval: 10
    save_every_epoch: true
    feedback_type: "error_type"

execution_sandbox:
  timeout: 3.0
  error_type_rewards:
    SyntaxError: 0.2
    TypeError: 0.35
    NameError: 0.5
    IndexError: 0.65
    ValueError: 0.8
    Pass: 1.0
    Timeout: 0.0
    OtherError: 0.0

generation:
  training:
    max_new_tokens: 512
    temperature: 1.0
    top_p: 0.95
    do_sample: true
    num_return_sequences: 8
    stop_tokens: ["\n\n", "def ", "class "]
  evaluation:
    max_new_tokens: 512
    temperature: 0.0
    top_p: 1.0
    do_sample: false
    num_return_sequences: 1
    stop_tokens: ["\n\n", "def ", "class "]

logging:
  dynamics_log: "../logs/error_type_350m_dynamics.json"
  log_level: "INFO"
  log_file: "../logs/error_type_350m.log"
  console_output: true
  dynamics_enabled: true

evaluation:
  checkpoint_paths:
    sft: "../checkpoints/error_type_350m/sft/final_checkpoint.pt"
  output_dir: "../results/error_type_350m"
  save_completions: true

gate:
  thresholds:
    convergence_speedup: 0.20
    variance_reduction: 0.30

hardware:
  device: "cuda"
  fp16: true

reproducibility:
  seed: 42
  deterministic: true
  benchmark: false

state_management:
  verification_state_path: "../../../../verification_state.yaml"
```

### 3. error_trace_350m.yaml

```yaml
experiment:
  experiment_id: "error_trace_350m"
  hypothesis_id: "h-m2"
  type: "MECHANISM"
  gate: "MUST_WORK"

dataset:
  name: "openai/openai_humaneval"
  split: "test"
  num_problems: 164
  cache_dir: "/home/PrayPrey/.cache/huggingface/datasets/openai_humaneval"

model:
  name: "Salesforce/codegen-350M-mono"
  precision: "fp16"
  cache_dir: "/home/PrayPrey/.cache/huggingface/hub"

lora:
  enabled: true
  r: 16
  alpha: 32
  dropout: 0.05
  target_modules: ["q_proj", "v_proj"]
  bias: "none"
  task_type: "CAUSAL_LM"

training:
  sft:
    enabled: true
    optimizer: "adamw"
    learning_rate: 2.0e-5
    weight_decay: 0.01
    epochs: 3
    batch_size: 8
    gradient_accumulation_steps: 1
    max_grad_norm: 1.0
    warmup_steps: 100
    lr_scheduler: "linear"
    checkpoint_dir: "../checkpoints/error_trace_350m/sft"
    log_interval: 10
    save_interval: 100

  grpo:
    enabled: true
    optimizer: "adamw"
    learning_rate: 5.0e-6
    weight_decay: 0.01
    epochs: 5
    batch_size: 8
    group_size: 8
    gradient_accumulation_steps: 2
    max_grad_norm: 1.0
    kl_penalty: 0.04
    clip_eps: 0.2
    warmup_steps: 50
    lr_scheduler: "constant"
    checkpoint_dir: "../checkpoints/error_trace_350m/grpo"
    log_interval: 10
    save_every_epoch: true
    feedback_type: "error_trace"

execution_sandbox:
  timeout: 3.0
  error_trace_rewards:
    error_types: ["SyntaxError", "TypeError", "NameError", "IndexError", "ValueError"]
    error_type_weight: 0.15
    depth_buckets: [0, 1, 2, 3, 5, 10, 20, 50, 100, 200]
    depth_weight: 0.05
    pass: 1.0

generation:
  training:
    max_new_tokens: 512
    temperature: 1.0
    top_p: 0.95
    do_sample: true
    num_return_sequences: 8
    stop_tokens: ["\n\n", "def ", "class "]
  evaluation:
    max_new_tokens: 512
    temperature: 0.0
    top_p: 1.0
    do_sample: false
    num_return_sequences: 1
    stop_tokens: ["\n\n", "def ", "class "]

logging:
  dynamics_log: "../logs/error_trace_350m_dynamics.json"
  log_level: "INFO"
  log_file: "../logs/error_trace_350m.log"
  console_output: true
  dynamics_enabled: true

evaluation:
  checkpoint_paths:
    sft: "../checkpoints/error_trace_350m/sft/final_checkpoint.pt"
  output_dir: "../results/error_trace_350m"
  save_completions: true

gate:
  thresholds:
    convergence_speedup: 0.20
    variance_reduction: 0.30

hardware:
  device: "cuda"
  fp16: true

reproducibility:
  seed: 42
  deterministic: true
  benchmark: false

state_management:
  verification_state_path: "../../../../verification_state.yaml"
```

### 4. binary_1b.yaml

```yaml
experiment:
  experiment_id: "binary_1b"
  hypothesis_id: "h-m2"
  type: "MECHANISM"
  gate: "MUST_WORK"

dataset:
  name: "openai/openai_humaneval"
  split: "test"
  num_problems: 164
  cache_dir: "/home/PrayPrey/.cache/huggingface/datasets/openai_humaneval"

model:
  name: "bigcode/starcoder"
  precision: "fp16"
  cache_dir: "/home/PrayPrey/.cache/huggingface/hub"

lora:
  enabled: true
  r: 16
  alpha: 32
  dropout: 0.05
  target_modules: ["q_proj", "v_proj"]
  bias: "none"
  task_type: "CAUSAL_LM"

training:
  sft:
    enabled: true
    optimizer: "adamw"
    learning_rate: 2.0e-5
    weight_decay: 0.01
    epochs: 3
    batch_size: 8
    gradient_accumulation_steps: 1
    max_grad_norm: 1.0
    warmup_steps: 100
    lr_scheduler: "linear"
    checkpoint_dir: "../checkpoints/binary_1b/sft"
    log_interval: 10
    save_interval: 100

  grpo:
    enabled: true
    optimizer: "adamw"
    learning_rate: 5.0e-6
    weight_decay: 0.01
    epochs: 5
    batch_size: 8
    group_size: 8
    gradient_accumulation_steps: 2
    max_grad_norm: 1.0
    kl_penalty: 0.04
    clip_eps: 0.2
    warmup_steps: 50
    lr_scheduler: "constant"
    checkpoint_dir: "../checkpoints/binary_1b/grpo"
    log_interval: 10
    save_every_epoch: true
    feedback_type: "binary"

execution_sandbox:
  timeout: 3.0
  binary_rewards:
    pass: 1.0
    fail: 0.0

generation:
  training:
    max_new_tokens: 512
    temperature: 1.0
    top_p: 0.95
    do_sample: true
    num_return_sequences: 8
    stop_tokens: ["\n\n", "def ", "class "]
  evaluation:
    max_new_tokens: 512
    temperature: 0.0
    top_p: 1.0
    do_sample: false
    num_return_sequences: 1
    stop_tokens: ["\n\n", "def ", "class "]

logging:
  dynamics_log: "../logs/binary_1b_dynamics.json"
  log_level: "INFO"
  log_file: "../logs/binary_1b.log"
  console_output: true
  dynamics_enabled: true

evaluation:
  checkpoint_paths:
    sft: "../checkpoints/binary_1b/sft/final_checkpoint.pt"
  output_dir: "../results/binary_1b"
  save_completions: true

gate:
  thresholds:
    convergence_speedup: 0.20
    variance_reduction: 0.30

hardware:
  device: "cuda"
  fp16: true

reproducibility:
  seed: 42
  deterministic: true
  benchmark: false

state_management:
  verification_state_path: "../../../../verification_state.yaml"
```

### 5. error_type_1b.yaml

```yaml
experiment:
  experiment_id: "error_type_1b"
  hypothesis_id: "h-m2"
  type: "MECHANISM"
  gate: "MUST_WORK"

dataset:
  name: "openai/openai_humaneval"
  split: "test"
  num_problems: 164
  cache_dir: "/home/PrayPrey/.cache/huggingface/datasets/openai_humaneval"

model:
  name: "bigcode/starcoder"
  precision: "fp16"
  cache_dir: "/home/PrayPrey/.cache/huggingface/hub"

lora:
  enabled: true
  r: 16
  alpha: 32
  dropout: 0.05
  target_modules: ["q_proj", "v_proj"]
  bias: "none"
  task_type: "CAUSAL_LM"

training:
  sft:
    enabled: true
    optimizer: "adamw"
    learning_rate: 2.0e-5
    weight_decay: 0.01
    epochs: 3
    batch_size: 8
    gradient_accumulation_steps: 1
    max_grad_norm: 1.0
    warmup_steps: 100
    lr_scheduler: "linear"
    checkpoint_dir: "../checkpoints/error_type_1b/sft"
    log_interval: 10
    save_interval: 100

  grpo:
    enabled: true
    optimizer: "adamw"
    learning_rate: 5.0e-6
    weight_decay: 0.01
    epochs: 5
    batch_size: 8
    group_size: 8
    gradient_accumulation_steps: 2
    max_grad_norm: 1.0
    kl_penalty: 0.04
    clip_eps: 0.2
    warmup_steps: 50
    lr_scheduler: "constant"
    checkpoint_dir: "../checkpoints/error_type_1b/grpo"
    log_interval: 10
    save_every_epoch: true
    feedback_type: "error_type"

execution_sandbox:
  timeout: 3.0
  error_type_rewards:
    SyntaxError: 0.2
    TypeError: 0.35
    NameError: 0.5
    IndexError: 0.65
    ValueError: 0.8
    Pass: 1.0
    Timeout: 0.0
    OtherError: 0.0

generation:
  training:
    max_new_tokens: 512
    temperature: 1.0
    top_p: 0.95
    do_sample: true
    num_return_sequences: 8
    stop_tokens: ["\n\n", "def ", "class "]
  evaluation:
    max_new_tokens: 512
    temperature: 0.0
    top_p: 1.0
    do_sample: false
    num_return_sequences: 1
    stop_tokens: ["\n\n", "def ", "class "]

logging:
  dynamics_log: "../logs/error_type_1b_dynamics.json"
  log_level: "INFO"
  log_file: "../logs/error_type_1b.log"
  console_output: true
  dynamics_enabled: true

evaluation:
  checkpoint_paths:
    sft: "../checkpoints/error_type_1b/sft/final_checkpoint.pt"
  output_dir: "../results/error_type_1b"
  save_completions: true

gate:
  thresholds:
    convergence_speedup: 0.20
    variance_reduction: 0.30

hardware:
  device: "cuda"
  fp16: true

reproducibility:
  seed: 42
  deterministic: true
  benchmark: false

state_management:
  verification_state_path: "../../../../verification_state.yaml"
```

### 6. error_trace_1b.yaml

```yaml
experiment:
  experiment_id: "error_trace_1b"
  hypothesis_id: "h-m2"
  type: "MECHANISM"
  gate: "MUST_WORK"

dataset:
  name: "openai/openai_humaneval"
  split: "test"
  num_problems: 164
  cache_dir: "/home/PrayPrey/.cache/huggingface/datasets/openai_humaneval"

model:
  name: "bigcode/starcoder"
  precision: "fp16"
  cache_dir: "/home/PrayPrey/.cache/huggingface/hub"

lora:
  enabled: true
  r: 16
  alpha: 32
  dropout: 0.05
  target_modules: ["q_proj", "v_proj"]
  bias: "none"
  task_type: "CAUSAL_LM"

training:
  sft:
    enabled: true
    optimizer: "adamw"
    learning_rate: 2.0e-5
    weight_decay: 0.01
    epochs: 3
    batch_size: 8
    gradient_accumulation_steps: 1
    max_grad_norm: 1.0
    warmup_steps: 100
    lr_scheduler: "linear"
    checkpoint_dir: "../checkpoints/error_trace_1b/sft"
    log_interval: 10
    save_interval: 100

  grpo:
    enabled: true
    optimizer: "adamw"
    learning_rate: 5.0e-6
    weight_decay: 0.01
    epochs: 5
    batch_size: 8
    group_size: 8
    gradient_accumulation_steps: 2
    max_grad_norm: 1.0
    kl_penalty: 0.04
    clip_eps: 0.2
    warmup_steps: 50
    lr_scheduler: "constant"
    checkpoint_dir: "../checkpoints/error_trace_1b/grpo"
    log_interval: 10
    save_every_epoch: true
    feedback_type: "error_trace"

execution_sandbox:
  timeout: 3.0
  error_trace_rewards:
    error_types: ["SyntaxError", "TypeError", "NameError", "IndexError", "ValueError"]
    error_type_weight: 0.15
    depth_buckets: [0, 1, 2, 3, 5, 10, 20, 50, 100, 200]
    depth_weight: 0.05
    pass: 1.0

generation:
  training:
    max_new_tokens: 512
    temperature: 1.0
    top_p: 0.95
    do_sample: true
    num_return_sequences: 8
    stop_tokens: ["\n\n", "def ", "class "]
  evaluation:
    max_new_tokens: 512
    temperature: 0.0
    top_p: 1.0
    do_sample: false
    num_return_sequences: 1
    stop_tokens: ["\n\n", "def ", "class "]

logging:
  dynamics_log: "../logs/error_trace_1b_dynamics.json"
  log_level: "INFO"
  log_file: "../logs/error_trace_1b.log"
  console_output: true
  dynamics_enabled: true

evaluation:
  checkpoint_paths:
    sft: "../checkpoints/error_trace_1b/sft/final_checkpoint.pt"
  output_dir: "../results/error_trace_1b"
  save_completions: true

gate:
  thresholds:
    convergence_speedup: 0.20
    variance_reduction: 0.30

hardware:
  device: "cuda"
  fp16: true

reproducibility:
  seed: 42
  deterministic: true
  benchmark: false

state_management:
  verification_state_path: "../../../../verification_state.yaml"
```

---

## Validation Rules

**Config Schema Validation:**
```python
def validate_config(config: dict) -> bool:
    # Required fields
    assert config['experiment']['hypothesis_id'] == 'h-m2'
    assert config['training']['grpo']['feedback_type'] in ['binary', 'error_type', 'error_trace']
    
    # Hyperparameter constraints
    assert 1 <= config['training']['grpo']['epochs'] <= 10
    assert config['training']['grpo']['batch_size'] * config['training']['grpo']['group_size'] <= 128
    assert config['training']['grpo']['kl_penalty'] > 0
    assert 0 < config['training']['grpo']['clip_eps'] < 1
    
    # Feedback-specific validation
    feedback = config['training']['grpo']['feedback_type']
    if feedback == 'binary':
        assert 'binary_rewards' in config['execution_sandbox']
    elif feedback == 'error_type':
        assert 'error_type_rewards' in config['execution_sandbox']
        assert len(config['execution_sandbox']['error_type_rewards']) >= 5
    elif feedback == 'error_trace':
        assert 'error_trace_rewards' in config['execution_sandbox']
        assert len(config['execution_sandbox']['error_trace_rewards']['error_types']) == 5
        assert len(config['execution_sandbox']['error_trace_rewards']['depth_buckets']) == 10
    
    # Logging validation
    assert config['logging']['dynamics_enabled'] is True
    assert config['logging']['dynamics_log'].endswith('_dynamics.json')
    
    return True
```

**Runtime Constants (Python):**

```python
# dynamics_constants.py
ERROR_TYPES = ["SyntaxError", "TypeError", "NameError", "IndexError", "ValueError"]
STACK_DEPTH_BUCKETS = [0, 1, 2, 3, 5, 10, 20, 50, 100, 200, float('inf')]

DYNAMICS_SCHEMA = {
    "experiment_id": str,
    "feedback_type": str,
    "model_size": str,
    "epochs": list,
    "convergence_epochs": float,
    "mean_grad_variance": float
}

BATCH_METRICS = ["step", "grad_variance", "grad_norm", "reward_variance", "kl_divergence"]
EPOCH_METRICS = ["epoch", "eval_loss", "eval_reward_mean", "eval_pass@1"]
```

---

## Environment Variables

```bash
# Required environment setup
export HF_HOME=/home/PrayPrey/.cache/huggingface
export CUDA_VISIBLE_DEVICES=0
export TOKENIZERS_PARALLELISM=false
export TRANSFORMERS_CACHE=/home/PrayPrey/.cache/huggingface/hub
export HF_DATASETS_CACHE=/home/PrayPrey/.cache/huggingface/datasets

# Optional: Performance tuning
export OMP_NUM_THREADS=8
export MKL_NUM_THREADS=8
```

---

## Configuration Differences Summary

| Config | Model | Feedback | Error Reward Schema | Dynamics Log |
|--------|-------|----------|---------------------|--------------|
| binary_350m | codegen-350M-mono | binary | pass=1.0, fail=0.0 | ../logs/binary_350m_dynamics.json |
| error_type_350m | codegen-350M-mono | error_type | 5 error types, 0.2-0.8 | ../logs/error_type_350m_dynamics.json |
| error_trace_350m | codegen-350M-mono | error_trace | 5 types × 10 depths | ../logs/error_trace_350m_dynamics.json |
| binary_1b | bigcode/starcoder | binary | pass=1.0, fail=0.0 | ../logs/binary_1b_dynamics.json |
| error_type_1b | bigcode/starcoder | error_type | 5 error types, 0.2-0.8 | ../logs/error_type_1b_dynamics.json |
| error_trace_1b | bigcode/starcoder | error_trace | 5 types × 10 depths | ../logs/error_trace_1b_dynamics.json |

**Key Invariants (All Configs):**
- GRPO lr: 5e-6 (from PRD 2.4)
- GRPO epochs: 5
- GRPO batch_size: 8
- GRPO group_size: 8
- KL penalty: 0.04
- Clip epsilon: 0.2
- Gradient accumulation: 2 steps
- Max generation length: 512 tokens
- Seed: 42
- LoRA r=16, alpha=32

---

## Notes

**Reproducibility:** All configs use seed=42 and deterministic=true to ensure reproducibility across runs.

**Compute Budget:** Each training run (5 epochs × ~500 steps) takes ~3 hours on H100 NVL. Total: 6 runs × 3 hours = 18 GPU-hours.

**Storage:** Dynamics JSON files estimated at 50MB each (5 epochs × 500 batches × 200 bytes/batch). Total: 6 × 50MB = 300MB.
