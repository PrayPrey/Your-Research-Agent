# Configuration Schema: h-e1 Binary Feedback Sufficiency

**Date:** 2026-08-19  
**Hypothesis:** h-e1 (EXISTENCE - Binary feedback dual-threshold sufficiency)  
**Source Documents:** 03_prd.md, 03_architecture.md, 03_logic.md  

---

## Configuration Overview

EXISTENCE hypothesis uses FIXED configuration (no hyperparameter sweeps). Single-point validation of binary feedback sufficiency.

**Configuration Philosophy:**
- Minimal PoC: Fixed hyperparameters from successful prior work (RLVR small models paper)
- Single seed: Deterministic results (seed=42)
- No variations: EXISTENCE gate tests "does it work?", not "what's optimal?"

---

## Complete Configuration File

```yaml
# h-e1: Binary Feedback Sufficiency Experiment
# Type: EXISTENCE (PoC)
# Gate: MUST_WORK

experiment:
  hypothesis_id: "h-e1"
  type: "EXISTENCE"
  gate: "MUST_WORK"
  description: "Binary feedback achieves dual-threshold sufficiency (≥8pp absolute, ≥80% retention)"

dataset:
  name: "openai/openai_humaneval"
  split: "test"
  num_problems: 164
  cache_dir: "./data/humaneval"

model:
  # Primary option (faster training)
  name: "Salesforce/codegen-350M-mono"
  # Fallback option (if baseline too weak)
  # name: "bigcode/starcoderbase-1b"
  
  precision: "fp16"  # Mixed precision for memory efficiency
  cache_dir: "./models/pretrained"
  
  architecture:
    context_window: 2048  # CodeGen-350M
    vocab_size: 51200
    hidden_size: 1024
    num_layers: 20
    num_heads: 16

lora:
  enabled: true
  r: 16  # Rank
  alpha: 32  # Scaling factor (alpha/r = 2.0)
  dropout: 0.05
  target_modules:
    - "q_proj"
    - "v_proj"
  bias: "none"
  task_type: "CAUSAL_LM"

training:
  # Stage 1: Supervised Fine-Tuning (SFT)
  sft:
    enabled: true
    optimizer: "adamw"
    learning_rate: 2.0e-5
    weight_decay: 0.01
    epochs: 5
    batch_size: 8
    gradient_accumulation_steps: 1
    max_grad_norm: 1.0
    warmup_steps: 100
    lr_scheduler: "linear"
    checkpoint_dir: "./checkpoints/sft"
    log_interval: 10  # Log every 10 steps
    save_interval: 100  # Save checkpoint every 100 steps
  
  # Stage 2: GRPO Binary Feedback
  grpo_binary:
    enabled: true
    optimizer: "adamw"
    learning_rate: 2.0e-7  # 100x lower than SFT
    weight_decay: 0.01
    steps: 500  # Extend to 1000 if reward still improving
    batch_size: 4  # 4 problems per batch
    samples_per_problem: 4  # 4 completions per problem
    gradient_accumulation_steps: 1
    max_grad_norm: 1.0
    kl_coef: 0.1  # KL divergence penalty
    warmup_steps: 50
    lr_scheduler: "constant"
    checkpoint_dir: "./checkpoints/grpo_binary"
    log_interval: 50
    save_interval: 100
    early_stopping:
      enabled: true
      patience: 100  # Stop if mean_reward < 0.1 for 100 steps
      min_reward: 0.1
  
  # Stage 3: GRPO Error-Type Feedback (upper bound)
  grpo_error_type:
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
    checkpoint_dir: "./checkpoints/grpo_error_type"
    log_interval: 50
    save_interval: 100
    early_stopping:
      enabled: true
      patience: 100
      min_reward: 0.1

execution_sandbox:
  timeout: 3.0  # Seconds
  max_memory: null  # No memory limit (rely on timeout)
  enable_network: false
  enable_file_io: false
  
  # Binary reward mapping
  binary_rewards:
    pass: 1.0
    fail: 0.0
  
  # Error-type reward mapping (5 categories)
  error_type_rewards:
    SyntaxError: 0.0
    TypeError: 0.2
    NameError: 0.4
    ValueError: 0.6
    AssertionError: 0.8
    Pass: 1.0
    Timeout: 0.0
    OtherError: 0.0  # Catch-all

generation:
  # Training generation (GRPO sampling)
  training:
    max_new_tokens: 512
    temperature: 1.0  # Sampling for exploration
    top_p: 0.95
    do_sample: true
    num_return_sequences: 4  # samples_per_problem
    stop_tokens:
      - "\n\n"
      - "def "
      - "class "
  
  # Evaluation generation (greedy decoding)
  evaluation:
    max_new_tokens: 512
    temperature: 0.0  # Greedy (deterministic)
    top_p: 1.0
    do_sample: false
    num_return_sequences: 1
    stop_tokens:
      - "\n\n"
      - "def "
      - "class "

evaluation:
  checkpoint_paths:
    sft: "./checkpoints/sft/final_checkpoint.pt"
    binary: "./checkpoints/grpo_binary/final_checkpoint.pt"
    error_type: "./checkpoints/grpo_error_type/final_checkpoint.pt"
  
  output_dir: "./results"
  save_completions: true  # Save generated code for inspection
  
  metrics:
    - "pass@1"  # Primary metric
    # pass@k not needed for EXISTENCE gate

gate:
  thresholds:
    absolute_improvement: 8.0  # Percentage points
    retention_ratio: 0.80  # 80% of error-type gains
  
  visualization:
    mandatory:
      - name: "gate_metrics"
        type: "bar_chart"
        output_path: "./figures/gate_metrics.png"
        dpi: 300
        size: [8, 6]  # inches
    
    optional:
      - name: "training_curves"
        type: "line_plot"
        output_path: "./figures/training_curves.png"
        dpi: 300
        size: [10, 6]
      
      - name: "reward_distribution"
        type: "histogram"
        output_path: "./figures/reward_distribution.png"
        dpi: 300
        size: [8, 6]
      
      - name: "error_breakdown"
        type: "bar_chart"
        output_path: "./figures/error_breakdown.png"
        dpi: 300
        size: [8, 6]

hardware:
  device: "cuda"  # Require GPU
  cuda_visible_devices: "0"  # Single GPU
  fp16: true
  bf16: false  # Use fp16 instead
  
  memory:
    max_vram_gb: 16
    gradient_checkpointing: false  # Enable if OOM
    cpu_offload: false  # Keep all on GPU

reproducibility:
  seed: 42
  deterministic: true
  benchmark: false  # Disable cuDNN benchmarking for reproducibility
  
  # Pin library versions
  requirements:
    transformers: "4.45.0"
    trl: "0.24.0"
    datasets: "3.0.0"
    torch: "2.4.0"
    accelerate: "1.0.0"
    peft: "0.8.0"
    human-eval: "git+https://github.com/openai/human-eval"
    matplotlib: "3.8.0"
    numpy: "1.26.0"
    pyyaml: "6.0"

logging:
  level: "INFO"
  log_file: "./logs/experiment.log"
  console_output: true
  
  wandb:
    enabled: false  # No external logging for PoC
    project: null
    entity: null

state_management:
  verification_state_path: "../../verification_state.yaml"
  checkpoint_state_path: "./04_checkpoint.yaml"
  
  update_fields:
    - "sub_hypotheses.h-e1.gate.satisfied"
    - "sub_hypotheses.h-e1.gate.result"
    - "sub_hypotheses.h-e1.validation.result"
    - "sub_hypotheses.h-e1.validation.key_findings"
```

---

## Hyperparameter Rationale

### Model Selection: CodeGen-350M

**Why CodeGen-350M over StarCoderBase-1B:**
- Faster training (350M params vs 1B)
- Lower memory footprint
- Sufficient for EXISTENCE validation
- Fallback to StarCoder if baseline pass@1 <5%

**Alternatives Considered:**
- StarCoderBase-1B: Higher capacity, longer context (8192), but slower
- CodeGen-2B: Too large for single GPU with LoRA

**Source:** RLVR small models paper used Qwen3-0.6B, Llama3.2-1B (similar scale)

---

### LoRA Configuration: r=16, alpha=32

**Why r=16:**
- Balances expressiveness vs memory efficiency
- r=8 too restrictive for policy learning
- r=32 marginal gains, doubles memory

**Why alpha=32 (scaling factor 2.0):**
- Standard ratio: alpha/r = 2.0
- Higher scaling → stronger LoRA contribution
- Empirically effective for code generation tasks

**Target Modules: q_proj, v_proj:**
- Query and value projections in multi-head attention
- Cover both key pathway (q) and content pathway (v)
- Exclude k_proj, o_proj to minimize trainable params

**Source:** PEFT library recommendations, validated on code tasks

---

### SFT Learning Rate: 2e-5

**Why 2e-5:**
- Standard for fine-tuning pretrained LLMs
- 10x lower than pretraining LR (typical: 2e-4)
- Prevents catastrophic forgetting of pretrained knowledge

**Epochs: 5:**
- HumanEval has 164 canonical solutions (small dataset)
- 5 epochs ≈ 820 gradient steps (with batch_size=8)
- Sufficient for convergence on small supervised dataset

**Source:** Standard LLM fine-tuning practice (GPT-3 paper, T5 paper)

---

### GRPO Learning Rate: 2e-7

**Why 100x lower than SFT:**
- RL policies more sensitive to learning rate than supervised
- Policy gradient variance requires conservative updates
- GRPO uses advantages → larger gradient magnitudes than SFT

**Steps: 500 (extendable to 1000):**
- Prior work: Qwen3-0.6B achieved +13pp on MBPP with ~1000 steps
- Start with 500 for faster PoC validation
- Extend if reward still improving (not plateaued)

**Source:** RLVR small models paper (arxiv.org/html/2605.30478)

---

### KL Coefficient: 0.1

**Why 0.1:**
- Prevents policy from diverging >10% from reference (SFT baseline)
- Too low (0.01) → Reward hacking, degenerate solutions
- Too high (0.5) → Policy too conservative, slow learning

**Monitoring:**
- KL divergence logged every 50 steps
- Warning if KL > 1.0 (excessive divergence)
- Increase to 0.2 if degeneration detected

**Source:** PPO paper (Schulman et al.), TRL library defaults

---

### Samples Per Problem: 4

**Why 4:**
- GRPO requires multiple samples per problem for group advantages
- Too few (1-2) → High variance in advantage estimates
- Too many (8+) → Slow training, memory constraints

**Effective Batch Size:**
- 4 problems × 4 samples = 16 rollouts per batch
- Sufficient for stable advantage normalization

**Source:** GRPO paper (arxiv.org/abs/2402.03300)

---

### Execution Timeout: 3 seconds

**Why 3 seconds:**
- HumanEval functions typically run <100ms
- 3s allows 30x margin for inefficient solutions
- Prevents infinite loops from hanging training
- Shorter (1s) → False negatives on valid slow solutions
- Longer (10s) → Training too slow

**Source:** Human-eval evaluation harness default

---

### Error-Type Rewards: 5 Categories

**Category Ordering Rationale:**

| Error Type | Reward | Reasoning |
|------------|--------|-----------|
| SyntaxError | 0.0 | Code unparseable, furthest from correct |
| TypeError | 0.2 | Code parses, but type system violated |
| NameError | 0.4 | Types correct, but undefined variables |
| ValueError | 0.6 | Variables defined, but invalid values |
| AssertionError | 0.8 | Logic runs, produces wrong answer (closest to correct) |
| Pass | 1.0 | All tests passed |

**Linear Spacing (0.2 increments):**
- Provides smooth gradient for policy learning
- Not based on empirical error frequency (uniform spacing)
- Alternative: Learned reward model (too complex for PoC)

**Source:** LETI paper (doi.org/10.18653/v1/2024.findings-naacl.16) used textual feedback with similar error categorization

---

### Generation Config: Training vs Evaluation

**Training (Sampling):**
- Temperature: 1.0 (exploration)
- Top-p: 0.95 (nucleus sampling)
- Enables diversity for reward-based learning

**Evaluation (Greedy):**
- Temperature: 0.0 (deterministic)
- Top-p: 1.0 (no filtering)
- Reproducible results, no variance across runs

**Why Different:**
- RL training requires exploration (sampling)
- Final evaluation requires best solution (greedy)

**Source:** Standard RL practice (PPO/GRPO papers)

---

## Configuration Variations (NOT Used for EXISTENCE)

EXISTENCE hypothesis uses FIXED config. Future MECHANISTIC hypotheses (h-m1, h-m2, h-m3) may sweep:

**Potential Sweeps (if h-e1 passes):**
- Model size: 350M vs 1B vs 3B
- Learning rate: [1e-7, 2e-7, 5e-7]
- KL coefficient: [0.05, 0.1, 0.2]
- Samples per problem: [2, 4, 8]
- Error-type granularity: 3 categories vs 5 vs 10

**Not Applicable for h-e1:** Single configuration point validates existence, not optimization.

---

## Hardware Constraints

### Memory Budget (16GB VRAM)

**Breakdown:**
| Component | Memory | Notes |
|-----------|--------|-------|
| Model (fp16) | ~2GB | 350M params × 2 bytes |
| LoRA adapters | ~200MB | r=16 → 1% of full params |
| Reference model | 0GB | Shared weights with policy |
| Training batch (8 samples, SFT) | ~8GB | Activations + gradients |
| Training batch (16 rollouts, GRPO) | ~10GB | 4 problems × 4 samples |
| Optimizer states (AdamW) | ~4GB | 2× model params (momentum + variance) |
| **Total (SFT)** | **~14GB** | Fits comfortably |
| **Total (GRPO)** | **~16GB** | Tight fit, no headroom |

**Fallback if OOM:**
1. Enable gradient checkpointing (trades compute for memory)
2. Reduce batch size: 8→4 (SFT), 4→2 problems (GRPO)
3. Use bf16 instead of fp16 (same memory, different precision)

---

### Time Budget (12 hours total)

**Stage Breakdown:**
| Stage | Time | Notes |
|-------|------|-------|
| Dataset download | 5 min | Cached after first run |
| Model download | 10 min | Cached after first run |
| SFT training (5 epochs) | 2 hours | ~820 steps at 8 samples/sec |
| GRPO Binary (500 steps) | 4 hours | Slower due to execution sandbox |
| GRPO Error-Type (500 steps) | 4 hours | Same as Binary |
| Evaluation (3 models × 164 problems) | 1 hour | Greedy generation + execution |
| Validation + Visualization | 10 min | Post-processing |
| **Total** | **~11.5 hours** | Within 12-hour budget |

**Critical Path:** GRPO training stages (8 hours of 11.5)

---

## Reproducibility Guarantees

### Fixed Random Seed: 42

**Seeded Components:**
```python
import random
import numpy as np
import torch

random.seed(42)
np.random.seed(42)
torch.manual_seed(42)
torch.cuda.manual_seed_all(42)
```

**Why 42:** Convention (Hitchhiker's Guide reference), arbitrary but consistent

### Deterministic Operations

**PyTorch Settings:**
```python
torch.backends.cudnn.deterministic = True  # Disable non-deterministic ops
torch.backends.cudnn.benchmark = False  # Disable auto-tuner (non-deterministic)
```

**Trade-off:** ~10% slower training, but fully reproducible

### Library Version Pinning

**Why Pin Versions:**
- transformers API changes frequently (breaking changes)
- torch/CUDA version compatibility critical
- Ensures exact reproduction 6 months later

**Pinned in requirements.txt:**
```
transformers==4.45.0
trl==0.24.0
torch==2.4.0
...
```

---

## Configuration File Location

**Path:** `h-e1/code/config.yaml`

**Loading:**
```python
import yaml

with open("config.yaml") as f:
    config = yaml.safe_load(f)

# Access nested config
lr = config['training']['sft']['learning_rate']  # 2e-5
```

**Override via CLI:**
```bash
python run_experiment.py --config config.yaml --override training.sft.epochs=10
```

---

## Validation Checklist

Before running experiment, verify config:

- [ ] Model fits in 16GB VRAM (check memory breakdown)
- [ ] Total time <12 hours (check stage breakdown)
- [ ] Seed set to 42 (reproducibility)
- [ ] LoRA enabled (memory efficiency)
- [ ] Sandbox timeout = 3s (safety)
- [ ] Binary rewards = {0.0, 1.0} (no intermediate values)
- [ ] Error-type rewards = {0.0, 0.2, 0.4, 0.6, 0.8, 1.0} (5 categories + pass)
- [ ] Evaluation temperature = 0.0 (greedy)
- [ ] Training temperature = 1.0 (sampling)
- [ ] Gate thresholds = {absolute: 8.0, retention: 0.80}

**All checkboxes must be ✓ before Phase 4 execution.**

---

**Configuration Version:** 1.0  
**Next Steps:** Task breakdown (03_tasks.yaml), Implementation (Phase 4)
