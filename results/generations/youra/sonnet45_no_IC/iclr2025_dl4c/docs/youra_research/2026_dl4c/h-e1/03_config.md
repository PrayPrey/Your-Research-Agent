# Configuration Specification: h-e1
# Tri-Modal RL Framework for Code Generation

**Hypothesis ID**: h-e1  
**Type**: EXISTENCE (PoC)  
**Gate**: MUST_WORK  
**Date**: 2026-07-12  
**Budget**: 2 subtasks (A-3: 1, A-4: 1)

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: green-field - new config design  
**Config Files Found**: None - new config  
**Pattern Used**: dataclass

---

## Applied Patterns

**Applied**: PyTorch RL Config Pattern (from Archon KB torch/_inductor/config.py)  
**Applied**: Dataclass Type Safety Pattern (standard Python pattern)

---

## A-3: Tri-Modal Aggregator Configuration [Complexity: 10, Budget: 1]

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass
import torch.nn as nn

@dataclass
class TriModalAggregatorConfig:
    """Dynamic reward aggregation with phase-based weighting."""
    
    # Phase boundaries (training progress percentiles)
    phase_1_end: float = 0.3      # Execution-dominant phase ends at 30%
    phase_2_end: float = 0.7      # AI-dominant phase ends at 70%
    
    # Peak timesteps for Gaussian-like weight curves (centered)
    exec_peak_timestep: float = 0.1    # Execution peaks early (10%)
    ai_peak_timestep: float = 0.5      # AI peaks mid-training (50%)
    human_peak_timestep: float = 0.9   # Human peaks late (90%)
    
    # Decay rates for weight curve sharpness
    exec_decay_rate: float = 0.5
    ai_decay_rate: float = 0.3
    human_decay_rate: float = 0.2
    
    # Initial weight values (must sum to 1.0)
    exec_initial_weight: float = 0.8
    ai_initial_weight: float = 0.1
    human_initial_weight: float = 0.1
    
    # Normalization method for reward alignment
    normalization: str = "percentile"   # Options: "percentile", "z-score", "min-max"
    percentile_low: float = 0.1
    percentile_high: float = 0.9
    
    def __post_init__(self):
        # Validation: weights must sum to 1.0
        total_weight = self.exec_initial_weight + self.ai_initial_weight + self.human_initial_weight
        assert abs(total_weight - 1.0) < 1e-6, f"Initial weights sum to {total_weight}, not 1.0"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Weight Schedule Implementation | Implement learnable Gaussian weight curves with phase boundaries and percentile normalization |

---

## A-4: Feedback Configuration [Complexity: 11, Budget: 1]

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass
class FeedbackConfig:
    """Execution, AI, and Human feedback collection settings."""
    
    # Execution Feedback
    exec_timeout: int = 5                    # Seconds per test case execution
    exec_max_retries: int = 2                # Retry on timeout/error
    exec_sandbox: bool = True                # Run in isolated subprocess
    
    # AI Feedback (Reward Model)
    reward_model_path: str = "models/reward_model.pt"
    reward_model_base: str = "Salesforce/codegen-350M-mono"
    reward_model_batch_size: int = 16
    reward_model_max_length: int = 512
    
    # Human Feedback (Annotation)
    annotation_cache_path: str = "data/annotations/annotations.json"
    annotation_scale_min: int = 0
    annotation_scale_max: int = 5
    annotators_per_sample: int = 3          # Majority vote from 3 annotators
    annotation_samples: int = 500           # Total training samples to annotate
    
    # Test case format
    test_case_format: str = "json"          # Options: "json", "pytest"
    test_case_keys: list = None
    
    def __post_init__(self):
        if self.test_case_keys is None:
            self.test_case_keys = ["input", "output"]
        
        # Ensure paths exist
        Path(self.reward_model_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.annotation_cache_path).parent.mkdir(parents=True, exist_ok=True)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Feedback Collectors Implementation | Implement ExecutionFeedback, AIFeedback, HumanFeedback classes with timeout handling and caching |

---

## Supporting Configurations

### Model Configuration

```python
@dataclass
class ModelConfig:
    """Base language model configuration."""
    model_name: str = "Salesforce/codegen-1.5B-mono"
    vocab_size: int = 50257
    hidden_size: int = 2048
    num_layers: int = 24
    num_heads: int = 16
    max_position_embeddings: int = 2048
    use_cache: bool = True
    gradient_checkpointing: bool = True      # Required for 1.5B on 40GB GPU
```

### PPO Configuration

```python
@dataclass
class PPOConfig:
    """Proximal Policy Optimization hyperparameters."""
    learning_rate: float = 5e-5
    clip_ratio: float = 0.2
    value_loss_coef: float = 0.5
    entropy_coef: float = 0.01
    gae_lambda: float = 0.95
    discount_gamma: float = 0.99
    max_grad_norm: float = 1.0
    batch_size: int = 32
    minibatch_size: int = 8
    ppo_epochs: int = 4
```

### Data Configuration

```python
@dataclass
class DataConfig:
    """Dataset loading and preprocessing configuration."""
    # Dataset sources
    humaneval_dataset: str = "openai/humaneval"
    mbpp_dataset: str = "google-research/mbpp"
    
    # Splits
    train_split: float = 0.8
    val_split: float = 0.1
    test_split: float = 0.1
    
    # Preprocessing
    max_length: int = 512
    batch_size: int = 32
    num_workers: int = 4
    shuffle: bool = True
    seed: int = 42
```

### Training Configuration

```python
@dataclass
class TrainingConfig:
    """Training loop configuration."""
    total_steps: int = 10000
    save_interval: int = 1000
    log_interval: int = 10
    eval_interval: int = 500
    
    # Hardware
    device: str = "cuda"
    mixed_precision: bool = True             # fp16 for memory efficiency
    
    # Reproducibility
    seed: int = 42
    
    # Checkpointing
    checkpoint_dir: str = "models"
    resume_from_checkpoint: str = None
```

### Evaluation Configuration

```python
@dataclass
class EvaluationConfig:
    """Evaluation protocol configuration."""
    test_samples: int = 67                   # 10% of 664 total problems
    annotation_samples: int = 500            # For human preference evaluation
    
    # Metrics
    metrics: list = None
    
    # Blind evaluation
    blind_evaluation: bool = True            # Annotators don't see model identity
    
    def __post_init__(self):
        if self.metrics is None:
            self.metrics = ["pass_at_1", "human_preference", "harmonic_mean"]
```

### Experiment Configuration (Master Config)

```python
@dataclass
class ExperimentConfig:
    """Master configuration combining all sub-configs."""
    model: ModelConfig = None
    ppo: PPOConfig = None
    tri_modal: TriModalAggregatorConfig = None
    feedback: FeedbackConfig = None
    data: DataConfig = None
    training: TrainingConfig = None
    evaluation: EvaluationConfig = None
    
    # Experiment metadata
    hypothesis_id: str = "h-e1"
    experiment_name: str = "tri_modal_rl_poc"
    output_dir: str = "h-e1"
    
    def __post_init__(self):
        # Initialize with defaults if not provided
        if self.model is None:
            self.model = ModelConfig()
        if self.ppo is None:
            self.ppo = PPOConfig()
        if self.tri_modal is None:
            self.tri_modal = TriModalAggregatorConfig()
        if self.feedback is None:
            self.feedback = FeedbackConfig()
        if self.data is None:
            self.data = DataConfig()
        if self.training is None:
            self.training = TrainingConfig()
        if self.evaluation is None:
            self.evaluation = EvaluationConfig()
```

---

## Usage Example

```python
from dataclasses import asdict
import yaml

# Create experiment config
config = ExperimentConfig(
    experiment_name="h-e1_tri_modal_poc_run1",
    output_dir="h-e1/run1"
)

# Save to YAML
with open("config.yaml", "w") as f:
    yaml.dump(asdict(config), f)

# Load from YAML
with open("config.yaml", "r") as f:
    config_dict = yaml.safe_load(f)
    config = ExperimentConfig(**config_dict)
```

---

## Configuration File Management

```python
# src/config.py

from dataclasses import dataclass, asdict
from pathlib import Path
import yaml
from typing import Optional

def load_config(config_path: str) -> ExperimentConfig:
    """Load configuration from YAML file."""
    with open(config_path, "r") as f:
        config_dict = yaml.safe_load(f)
    return ExperimentConfig(**config_dict)

def save_config(config: ExperimentConfig, output_path: str):
    """Save configuration to YAML file."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        yaml.dump(asdict(config), f, default_flow_style=False, sort_keys=False)

def override_config(config: ExperimentConfig, **kwargs) -> ExperimentConfig:
    """Override specific config values."""
    config_dict = asdict(config)
    for key, value in kwargs.items():
        if "." in key:
            # Support nested override: "ppo.learning_rate=1e-4"
            parts = key.split(".")
            d = config_dict
            for part in parts[:-1]:
                d = d[part]
            d[parts[-1]] = value
        else:
            config_dict[key] = value
    return ExperimentConfig(**config_dict)
```

---

## Validation & Constraints

### Automatic Validation

All dataclasses include `__post_init__` validation:
- Weight sums must equal 1.0 (tri-modal aggregator)
- Directory paths are created automatically
- Phase boundaries are within [0, 1]

### Manual Validation Checklist

```python
def validate_config(config: ExperimentConfig) -> bool:
    """Validate experiment configuration."""
    checks = []
    
    # Phase boundaries
    checks.append(0 < config.tri_modal.phase_1_end < config.tri_modal.phase_2_end < 1)
    
    # Peak timesteps within phases
    checks.append(config.tri_modal.exec_peak_timestep < config.tri_modal.phase_1_end)
    checks.append(config.tri_modal.phase_1_end < config.tri_modal.ai_peak_timestep < config.tri_modal.phase_2_end)
    checks.append(config.tri_modal.human_peak_timestep > config.tri_modal.phase_2_end)
    
    # Split ratios sum to 1.0
    total_split = config.data.train_split + config.data.val_split + config.data.test_split
    checks.append(abs(total_split - 1.0) < 1e-6)
    
    # Batch sizes
    checks.append(config.data.batch_size % config.ppo.minibatch_size == 0)
    
    return all(checks)
```

---

## Environment Variables (Optional)

```bash
# .env file for sensitive paths
REWARD_MODEL_PATH=models/reward_model.pt
ANNOTATION_CACHE_PATH=data/annotations/annotations.json
HUMANEVAL_CACHE_DIR=data/humaneval
MBPP_CACHE_DIR=data/mbpp
WANDB_API_KEY=<your_key>
HF_TOKEN=<your_token>
```

---

## Summary

### Configuration Coverage

| Component | Config Class | Purpose |
|-----------|--------------|---------|
| A-3 Tri-Modal Aggregator | `TriModalAggregatorConfig` | Weight schedule parameters (allocated task) |
| A-4 Feedback Collectors | `FeedbackConfig` | Execution, AI, human feedback settings (allocated task) |
| Model | `ModelConfig` | Base LLM architecture |
| PPO | `PPOConfig` | RL training hyperparameters |
| Data | `DataConfig` | Dataset loading and splits |
| Training | `TrainingConfig` | Training loop settings |
| Evaluation | `EvaluationConfig` | Evaluation protocol |
| Experiment | `ExperimentConfig` | Master config combining all |

### Key Design Choices

**Single Format**: Python dataclass (type-safe, validation, serialization via asdict)  
**Validation**: Automatic via `__post_init__` + manual `validate_config()`  
**Flexibility**: YAML serialization for runtime config, Python for development  
**Defaults**: All PoC values from PRD and architecture specs

---

**Document Status**: COMPLETED  
**Next Phase**: Phase 4 - Implementation  
**Output Path**: `/workspace/TEST_dl4c/docs/youra_research/h-e1/03_config.md`
