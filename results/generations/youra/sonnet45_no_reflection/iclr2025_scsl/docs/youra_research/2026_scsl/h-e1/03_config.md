# Configuration Schema: h-e1
# Jacobian Stable Rank Regularization - EXISTENCE PoC

**Date:** 2026-05-12  
**Hypothesis Type:** EXISTENCE (PoC)  
**Config Pattern:** Applied: Standard PyTorch training config with dataclass

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation from scratch - no existing config files  
**Config Files Found**: None - new config design  
**Pattern Used**: dataclass

---

## A-1: Data Pipeline [Complexity: 8, Budget: 1 subtask]

Applied: Standard HuggingFace Datasets pattern

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class DataConfig:
    dataset_name: str = "allenai/c4"
    subset: str = "en"
    tokenizer_name: str = "gpt2"
    seq_length: int = 512
    batch_size: int = 32
    num_workers: int = 4
    streaming: bool = True
    total_tokens: int = 10_000_000_000  # 10B tokens
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Implement C4DataModule | Streaming dataset loader with tokenization |

---

## A-2: Baseline Model [Complexity: 10, Budget: 1 subtask]

Applied: Standard GPT-2 small configuration from HuggingFace

### Configuration (Python Dataclass)

```python
@dataclass
class ModelConfig:
    vocab_size: int = 50257
    n_positions: int = 1024
    n_embd: int = 768
    n_layer: int = 12
    n_head: int = 12
    n_inner: int = 3072  # 4 * n_embd
    activation_function: str = "gelu_new"
    resid_pdrop: float = 0.1
    embd_pdrop: float = 0.1
    attn_pdrop: float = 0.1
    layer_norm_epsilon: float = 1e-5
    initializer_range: float = 0.02
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Implement BaselineGPT2 | Standard GPT-2 with causal LM loss |

---

## A-3: Stable Rank Regularization [Complexity: 16, Budget: 1 subtask]

Applied: Power iteration + Hutchinson trace estimation pattern

### Configuration (Python Dataclass)

```python
@dataclass
class RegularizationConfig:
    n_power_iterations: int = 5
    n_hutchinson_probes: int = 10
    epsilon: float = 1e-12  # Numerical stability for division
    lambda_init: float = 0.01
    lambda_min: float = 1e-4
    lambda_max: float = 1.0
    lambda_decay: float = 0.95
    lambda_growth: float = 1.05
    adaptive_tuning: bool = True
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Implement StableRankRegularizer | Hutchinson trace + power iteration + residual correction |

---

## A-4: Proposed Model Training [Complexity: 14, Budget: 1 subtask]

Applied: Standard AdamW optimizer with cosine schedule

### Configuration (Python Dataclass)

```python
@dataclass
class TrainingConfig:
    learning_rate: float = 3e-4
    weight_decay: float = 0.1
    betas: tuple[float, float] = (0.9, 0.95)
    warmup_steps: int = 2000
    gradient_accumulation_steps: int = 4  # Effective batch 128
    max_grad_norm: float = 1.0
    seed: int = 42
    eval_interval: int = 500
    checkpoint_interval: int = 10000
    stable_rank_eval_interval: int = 1000
    use_mixed_precision: bool = True
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Implement GPT2Trainer | Training loop with adaptive lambda and checkpointing |

---

## A-5: Evaluation & Metrics [Complexity: 12, Budget: 1 subtask]

Applied: Standard perplexity computation + custom stable rank metrics

### Configuration (Python Dataclass)

```python
@dataclass
class EvaluationConfig:
    eval_batch_size: int = 32
    eval_samples: int = 1000
    perplexity_stride: int = 256
    stable_rank_samples: int = 100
    # Gate targets
    target_sr_reduction: float = 0.20  # 20% reduction
    target_ppl_deviation: float = 0.01  # 1% max deviation
    target_layer_variance_ratio: float = 2.0  # <2x mean
    target_measurement_cv: float = 0.15  # <15%
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Implement MetricsEvaluator | Perplexity, stable rank per layer, variance, CV |

---

## A-6: Visualization [Complexity: 7, Budget: 1 subtask]

Applied: Standard matplotlib plotting configuration

### Configuration (Python Dataclass)

```python
@dataclass
class VisualizationConfig:
    output_dir: str = "figures"
    dpi: int = 300
    figsize: tuple[int, int] = (10, 6)
    style: str = "seaborn-v0_8-darkgrid"
    save_formats: list[str] = None  # Default: ["png", "pdf"]
    
    def __post_init__(self):
        if self.save_formats is None:
            self.save_formats = ["png", "pdf"]
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Implement ExperimentVisualizer | Generate 5 required figures |

---

## A-7: Gate Validation [Complexity: 6, Budget: 1 subtask]

Applied: Simple validation logic with pass/fail criteria

### Configuration (Python Dataclass)

```python
@dataclass
class ValidationConfig:
    baseline_checkpoint: str = "checkpoints/baseline/final.pt"
    proposed_checkpoint: str = "checkpoints/proposed/final.pt"
    implicit_checkpoint: str = "checkpoints/implicit_control/final.pt"
    report_path: str = "results/gate_validation.json"
    gate_type: str = "MUST_WORK"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Implement gate validation | Compare metrics to targets, generate report |

---

## Complete Experiment Configuration

### Master Config (All Variants)

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ExperimentConfig:
    """Complete configuration for SCSL experiment variants."""
    
    # Component configs
    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    regularization: RegularizationConfig = field(default_factory=RegularizationConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    
    # Variant-specific
    variant: str = "baseline"  # "baseline", "proposed", "implicit_control"
    output_dir: str = "outputs"
    device: str = "cuda"
    
    def __post_init__(self):
        # Compute total steps from tokens
        tokens_per_step = self.data.batch_size * self.training.gradient_accumulation_steps * self.data.seq_length
        self.total_steps = self.data.total_tokens // tokens_per_step


def get_baseline_config() -> ExperimentConfig:
    """Standard GPT-2 without regularization."""
    config = ExperimentConfig(variant="baseline")
    config.regularization.lambda_init = 0.0  # Disable regularization
    config.regularization.adaptive_tuning = False
    config.output_dir = "outputs/baseline"
    return config


def get_proposed_config() -> ExperimentConfig:
    """GPT-2 with stable rank regularization."""
    config = ExperimentConfig(variant="proposed")
    config.regularization.adaptive_tuning = True
    config.output_dir = "outputs/proposed"
    return config


def get_implicit_control_config() -> ExperimentConfig:
    """GPT-2 with adaptive LR (no explicit regularization)."""
    config = ExperimentConfig(variant="implicit_control")
    config.regularization.lambda_init = 0.0
    config.regularization.adaptive_tuning = False
    config.training.learning_rate = 3e-4  # Will be adapted during training
    config.output_dir = "outputs/implicit_control"
    return config
```

---

## Configuration Usage Pattern

```python
# In main.py
from config import get_baseline_config, get_proposed_config, get_implicit_control_config

# Run baseline
baseline_config = get_baseline_config()
baseline_results = run_experiment(baseline_config)

# Run proposed
proposed_config = get_proposed_config()
proposed_results = run_experiment(proposed_config)

# Run implicit control
implicit_config = get_implicit_control_config()
implicit_results = run_experiment(implicit_config)

# Validate gate
validate_gate_criteria(baseline_results, proposed_results, implicit_results)
```

---

## Environment Configuration

```bash
# GPU selection (before running experiments)
export CUDA_VISIBLE_DEVICES=0  # Use empty GPU from nvidia-smi

# Optional: Enable TF32 for faster computation on Ampere GPUs
export TORCH_ALLOW_TF32_ON_MATMUL=1
export TORCH_ALLOW_TF32_ON_CUDNN=1
```

---

## Subtask Budget Summary

| Task ID | Task Name | Complexity | Budget | Used |
|---------|-----------|------------|--------|------|
| A-1 | Data Pipeline | 8 | 1 | 1 |
| A-2 | Baseline Model | 10 | 1 | 1 |
| A-3 | Stable Rank Regularization | 16 | 1 | 1 |
| A-4 | Proposed Model Training | 14 | 1 | 1 |
| A-5 | Evaluation & Metrics | 12 | 1 | 1 |
| A-6 | Visualization | 7 | 1 | 1 |
| A-7 | Gate Validation | 6 | 1 | 1 |

**Total:** 7/7 subtasks allocated

---

## Critical Configuration Notes

### Adaptive Lambda Strategy

The regularization strength is tuned during training to maintain iso-perplexity:

```python
# In trainer (pseudocode)
if current_ppl > baseline_ppl * (1 + target_ppl_deviation):
    lambda_reg *= lambda_decay  # Reduce regularization
elif current_ppl < baseline_ppl * (1 - target_ppl_deviation):
    lambda_reg *= lambda_growth  # Increase regularization
lambda_reg = clip(lambda_reg, lambda_min, lambda_max)
```

### Numerical Stability

- `epsilon = 1e-12`: Prevents division by zero in spectral norm computation
- `max_grad_norm = 1.0`: Gradient clipping prevents instability from regularization term
- `use_mixed_precision = True`: FP16 for memory efficiency, automatic loss scaling

### Memory Optimization

- `gradient_accumulation_steps = 4`: Effective batch 128 with batch 32
- `streaming = True`: Load C4 dataset without downloading entire corpus
- Checkpoint gradients recommended for long sequences (not in config, implementation detail)

---

## Validation Criteria

Gate passes if ALL conditions met:

1. Mean stable rank reduction: `(baseline_sr - proposed_sr) / baseline_sr >= 0.20`
2. Perplexity deviation: `|proposed_ppl - baseline_ppl| / baseline_ppl <= 0.01`
3. Layer variance: `std(stable_ranks) / mean(stable_ranks) < 2.0`
4. Measurement CV: `cv(spectral_norm_estimates) < 0.15`

---

**Status:** Configuration schema complete  
**Next Phase:** Phase 4 - Code Implementation  
**Subtask Allocation:** 7/7 subtasks within budget
