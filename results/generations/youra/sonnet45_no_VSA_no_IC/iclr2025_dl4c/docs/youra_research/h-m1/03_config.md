# Configuration Schema: h-m1 Feedback Efficiency Mechanism

**Date:** 2026-08-19  
**Hypothesis:** h-m1 (MECHANISM - Capacity limits feedback efficiency)  
**Type:** MECHANISM (PoC)  
**Gate:** MUST_WORK  
**Base:** h-e1 (extends binary/error-type config)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** config verified from h-e1 code  
**Config Files Found:** h-e1/code/config.yaml  
**Pattern Used:** YAML

---

## Configuration Overview

MECHANISM hypothesis (PoC level) uses FIXED configuration. Tests capacity limits via efficiency monotonicity, not optimal hyperparameters.

**Applied:** Standard PyTorch RL config pattern (from Archon KB: GRPO + LoRA)

**Philosophy:**
- Reuse h-e1 config for SFT/Binary/Error-Type (no re-training)
- Add ONLY error+trace section (minimal diff)
- Fixed hyperparameters (seed=42, no sweeps)

---

## Complete Configuration File

```yaml
# h-m1: Feedback Efficiency Mechanism
# Type: MECHANISM (PoC)
# Gate: MUST_WORK

experiment:
  hypothesis_id: "h-m1"
  type: "MECHANISM"
  gate: "MUST_WORK"
  description: "Capacity limits feedback efficiency - monotonic decrease in pp/bit"

dataset:
  name: "openai/openai_humaneval"
  split: "test"
  num_problems: 164
  cache_dir: "./data/humaneval"

model:
  name: "Salesforce/codegen-350M-mono"
  precision: "fp16"
  cache_dir: "./models/pretrained"

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
  # Reuse h-e1 checkpoints (no re-training)
  sft:
    enabled: false
    checkpoint_path: "../../h-e1/checkpoints/sft/final_checkpoint.pt"
  
  grpo_binary:
    enabled: false
    checkpoint_path: "../../h-e1/checkpoints/grpo_binary/final_checkpoint.pt"
  
  grpo_error_type:
    enabled: false
    checkpoint_path: "../../h-e1/checkpoints/grpo_error_type/final_checkpoint.pt"
  
  # NEW: Error+Trace GRPO
  grpo_error_trace:
    enabled: true
    optimizer: "adamw"
    learning_rate: 2.0e-7
    weight_decay: 0.01
    steps: 500
    batch_size: 4
    samples_per_problem: 4
    gradient_accumulation_steps: 1
    max_grad_norm: 1.0
    kl_coef: 0.1
    warmup_steps: 50
    lr_scheduler: "constant"
    checkpoint_dir: "../checkpoints/grpo_error_trace"
    log_interval: 50
    save_interval: 100
    early_stopping:
      enabled: true
      patience: 100
      min_reward: 0.1

execution_sandbox:
  timeout: 3.0
  binary_rewards:
    pass: 1.0
    fail: 0.0
  error_type_rewards:
    SyntaxError: 0.0
    TypeError: 0.2
    NameError: 0.4
    ValueError: 0.6
    AssertionError: 0.8
    Pass: 1.0
    Timeout: 0.0
    OtherError: 0.0
  
  # NEW: Error+Trace rewards
  error_trace:
    depth_buckets: 10
    depth_penalty_divisor: 20.0
    min_penalty: 0.5
    max_penalty: 1.0
    # Combined reward = error_type_reward × depth_penalty
    # depth_penalty = 1.0 - (depth / depth_penalty_divisor), clamped [min, max]

generation:
  training:
    max_new_tokens: 512
    temperature: 1.0
    top_p: 0.95
    do_sample: true
    num_return_sequences: 4
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

evaluation:
  checkpoint_paths:
    sft: "../../h-e1/checkpoints/sft/final_checkpoint.pt"
    binary: "../../h-e1/checkpoints/grpo_binary/final_checkpoint.pt"
    error_type: "../../h-e1/checkpoints/grpo_error_type/final_checkpoint.pt"
    error_trace: "../checkpoints/grpo_error_trace/final_checkpoint.pt"
  output_dir: "../results"
  save_completions: true

# NEW: Efficiency analysis config
efficiency:
  bits_per_condition:
    binary: 1.0
    error_type: 2.32
    error_trace: 5.64
  target_ranges:
    binary: [7.0, 100.0]
    error_type: [4.0, 6.0]
    error_trace: [2.0, 3.0]
  bootstrap_samples: 1000

# NEW: Statistical testing config
gate:
  bonferroni_alpha: 0.0167
  thresholds:
    monotonic_decrease: true
    efficiency_targets:
      binary: 7.0
      error_type: [4.0, 6.0]
      error_trace: [2.0, 3.0]

hardware:
  device: "cuda"
  fp16: true

reproducibility:
  seed: 42
  deterministic: true
  benchmark: false

logging:
  level: "INFO"
  log_file: "../logs/experiment.log"
  console_output: true
  gradient_variance:
    enabled: true
    log_interval: 10
    output_path: "../logs/gradient_variance.csv"

state_management:
  verification_state_path: "../../../../verification_state.yaml"
```

---

## Inherited Configuration (Base Hypothesis)

**Config File Verified From:** h-e1/code/config.yaml

Reused sections (no changes):
- `dataset`: HumanEval 164 problems
- `model`: CodeGen-350M-mono, fp16
- `lora`: r=16, alpha=32, target_modules=[q_proj, v_proj]
- `execution_sandbox.timeout`: 3.0s
- `execution_sandbox.binary_rewards`: {pass: 1.0, fail: 0.0}
- `execution_sandbox.error_type_rewards`: 6 categories (SyntaxError=0.0 → Pass=1.0)
- `generation`: training (temp=1.0) vs eval (temp=0.0)
- `hardware`: cuda, fp16
- `reproducibility`: seed=42, deterministic=True

---

## New Configuration Sections

### Error+Trace Reward (execution_sandbox.error_trace)

```yaml
error_trace:
  depth_buckets: 10          # Stack depth levels [0-9]
  depth_penalty_divisor: 20.0  # Penalty slope
  min_penalty: 0.5           # Floor penalty
  max_penalty: 1.0           # Ceiling penalty (no error)
```

**Calculation:**
```python
depth = min(len(traceback.extract_tb(exc_info[2])), 9)
depth_penalty = max(min_penalty, min(1.0 - (depth / depth_penalty_divisor), max_penalty))
error_trace_reward = error_type_reward * depth_penalty
```

**Examples:**
- TypeError at depth 0: 0.2 × 1.0 = 0.20
- AssertionError at depth 3: 0.8 × 0.85 = 0.68
- NameError at depth 9: 0.4 × 0.55 = 0.22

---

### Efficiency Analysis (efficiency)

```yaml
efficiency:
  bits_per_condition:
    binary: 1.0              # log₂(2)
    error_type: 2.32         # log₂(5)
    error_trace: 5.64        # log₂(50)
  target_ranges:
    binary: [7.0, 100.0]     # Lower bound only
    error_type: [4.0, 6.0]   # Range
    error_trace: [2.0, 3.0]  # Range
  bootstrap_samples: 1000    # CI computation
```

**Efficiency Formula:**
```python
efficiency = (pass_at_1 - sft_baseline) / bits_per_condition
```

---

### Gate Logic (gate)

```yaml
gate:
  bonferroni_alpha: 0.0167   # 0.05 / 3 pairwise tests
  thresholds:
    monotonic_decrease: true
    efficiency_targets:
      binary: 7.0
      error_type: [4.0, 6.0]
      error_trace: [2.0, 3.0]
```

**Gate Conditions:**
1. Binary efficiency > Error-Type efficiency (p < 0.0167)
2. Error-Type efficiency > Error+Trace efficiency (p < 0.0167)
3. Binary ≥ 7.0 pp/bit
4. Error-Type in [4.0, 6.0] pp/bit
5. Error+Trace in [2.0, 3.0] pp/bit

---

### Gradient Variance Logging (logging.gradient_variance)

```yaml
logging:
  gradient_variance:
    enabled: true
    log_interval: 10         # Every 10 steps
    output_path: "../logs/gradient_variance.csv"
```

**Purpose:** Secondary evidence for H-M2 (signal concentration hypothesis).

---

## Task Allocation (Budget: 3 Subtasks)

### M1-1: Trace Sandbox Extension (Complexity: 11, Budget: 1 subtask)

**Configuration:**
```python
# In code/sandbox_trace.py
DEPTH_CONFIG = {
    "buckets": 10,
    "max_depth": 9,
    "penalty_divisor": 20.0,
    "min_penalty": 0.5,
    "max_penalty": 1.0
}
```

**Subtask:**
| ID | Subtask | Description |
|----|---------|-------------|
| M1-1-1 | Implement trace extraction | Extract stack depth, clamp to [0-9], compute depth penalty, multiply by error_type reward |

---

### M1-2: Error+Trace Trainer (Complexity: 14, Budget: 1 subtask)

**Configuration:**
```python
# Inherit from h-e1 GRPOTrainer config
GRPO_CONFIG = {
    "learning_rate": 2.0e-7,
    "steps": 500,
    "batch_size": 4,
    "samples_per_problem": 4,
    "kl_coef": 0.1
}
```

**Subtask:**
| ID | Subtask | Description |
|----|---------|-------------|
| M1-2-1 | GRPO training loop | Load SFT ref model, run 500 GRPO steps with error+trace rewards, log gradient variance every 10 steps |

---

### M1-3: Efficiency Analysis (Complexity: 12, Budget: 1 subtask)

**Configuration:**
```python
EFFICIENCY_CONFIG = {
    "bits": {"binary": 1.0, "error_type": 2.32, "error_trace": 5.64},
    "targets": {
        "binary": (7.0, float('inf')),
        "error_type": (4.0, 6.0),
        "error_trace": (2.0, 3.0)
    },
    "bonferroni_alpha": 0.0167,
    "bootstrap_n": 1000
}
```

**Subtask:**
| ID | Subtask | Description |
|----|---------|-------------|
| M1-3-1 | Compute & test efficiency | Calculate pp/bit for 3 conditions, pairwise t-tests, bootstrap CI, plot frontier, gate verdict |

---

## Self-Validation

- [x] ONE format only (YAML, not dataclass)
- [x] No ASCII diagrams
- [x] Applied KB pattern: GRPO + LoRA (1 line)
- [x] Codebase Analysis (Serena) section included
- [x] Inherited Configuration section included
- [x] Subtask count: 3/3 (within budget)
- [x] Total length: <400 lines

---

**Configuration Version:** 1.0  
**Next Phase:** Phase 4 implementation (3 subtasks: trace sandbox → training → efficiency analysis)
