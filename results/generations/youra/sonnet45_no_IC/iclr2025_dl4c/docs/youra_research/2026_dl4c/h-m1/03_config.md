# Configuration Specification: h-m1
# Phase 1 Execution-Heavy Weight Validation

**Hypothesis ID**: h-m1  
**Type**: MECHANISM  
**Gate**: MUST_WORK  
**Date**: 2026-07-12  
**Budget**: 1 subtask (A-6: 1)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: config classes verified from base code  
**Config Files Found**: `h-e1/code/config/experiment_config.py`  
**Pattern Used**: dataclass (consistent with h-e1)

---

## Applied Patterns

**Applied**: PyTorch Training Checkpoint Pattern (from Archon KB)  
**Applied**: Dataclass Type Safety Pattern (h-e1 validated approach)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

The following configs are inherited from h-e1:

```python
# From: h-e1/code/config/experiment_config.py (ACTUAL CODE)

@dataclass
class DataConfig:
    """Dataset configuration"""
    dataset_name: str = "humaneval_mbpp_combined"
    humaneval_split: str = "test"
    mbpp_train_split: str = "train"
    mbpp_test_split: str = "test"
    train_ratio: float = 0.8
    val_ratio: float = 0.1
    test_ratio: float = 0.1
    max_length: int = 512
    batch_size: int = 32
    num_workers: int = 4
    cache_dir: str = "../data/datasets"


@dataclass
class ModelConfig:
    """Model architecture configuration"""
    model_name: str = "Salesforce/codegen-350M-mono"
    max_length: int = 512
    temperature: float = 0.8
    top_p: float = 0.95
    num_return_sequences: int = 1


@dataclass
class TriModalAggregatorConfig:
    """Tri-modal reward aggregator configuration"""
    num_phases: int = 3
    initial_weights: List[float] = field(default_factory=lambda: [0.8, 0.1, 0.1])
    peak_timesteps: List[float] = field(default_factory=lambda: [0.15, 0.5, 0.85])
    decay_rates: List[float] = field(default_factory=lambda: [0.5, 0.3, 0.2])
    percentile_window: int = 100


@dataclass
class FeedbackConfig:
    """Feedback collection configuration"""
    execution_timeout: float = 5.0
    sandbox_enabled: bool = True
    reward_model_path: Optional[str] = None
    reward_model_name: str = "microsoft/codebert-base"
    annotation_cache_path: str = "./data/annotations/cache.json"
    fallback_score: float = 0.5


@dataclass
class PPOConfig:
    """PPO training configuration"""
    learning_rate: float = 5e-5
    batch_size: int = 32
    mini_batch_size: int = 8
    ppo_epochs: int = 4
    max_grad_norm: float = 1.0
    clip_range: float = 0.2
    clip_range_vf: float = 0.2
    vf_coef: float = 0.5
    ent_coef: float = 0.01
    gamma: float = 0.99
    gae_lambda: float = 0.95
    target_kl: float = 0.01
    total_steps: int = 10000
    gradient_accumulation_steps: int = 1
    warmup_steps: int = 500
    logging_steps: int = 10
    save_steps: int = 1000
    eval_steps: int = 500
```

**Verified from**: `h-e1/code/config/experiment_config.py` (actual implementation)

---

## A-6: Phase 1 Configuration Setup [Complexity: 5, Budget: 1]

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path


@dataclass
class Phase1Config:
    """Phase 1 specific configuration for weight monitoring."""
    
    # Checkpoints for Phase 1 analysis
    checkpoints: List[float] = field(default_factory=lambda: [0.0, 0.1, 0.2, 0.3, 0.7, 1.0])
    
    # Training episodes
    total_episodes: int = 10000
    
    # Evaluation samples (validation set size from h-e1)
    eval_samples: int = 113
    
    # Gate validation thresholds
    weight_dominance_threshold: float = 0.0  # execution_weight - max(ai, human) > 0
    improvement_rate_threshold: float = 1.0  # Phase 1 rate / Later rate > 1.0
    correlation_threshold: float = -0.6  # Pearson rho < -0.6
    
    def __post_init__(self):
        # Validate checkpoints within [0, 1]
        assert all(0.0 <= cp <= 1.0 for cp in self.checkpoints), \
            "All checkpoints must be in [0, 1] range"
        
        # Ensure Phase 1 checkpoints present
        phase1_required = {0.0, 0.1, 0.2, 0.3}
        assert phase1_required.issubset(set(self.checkpoints)), \
            "Must include Phase 1 checkpoints: 0.0, 0.1, 0.2, 0.3"


@dataclass
class CheckpointConfig:
    """Checkpoint management configuration."""
    
    # Directory paths
    checkpoint_dir: str = "./checkpoints"
    log_dir: str = "./logs"
    figure_dir: str = "./figures"
    
    # Checkpoint file format
    checkpoint_format: str = "progress_{:.1f}.json"
    weights_csv: str = "weights_phase1.csv"
    pass_at_1_csv: str = "pass_at_1_trajectory.csv"
    
    # Checkpoint data to save
    save_model_state: bool = True
    save_optimizer_state: bool = True
    save_weights: bool = True
    save_metrics: bool = True
    
    def __post_init__(self):
        # Create directories if they don't exist
        Path(self.checkpoint_dir).mkdir(parents=True, exist_ok=True)
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)
        Path(self.figure_dir).mkdir(parents=True, exist_ok=True)


@dataclass
class Phase1ExperimentConfig:
    """Extended experiment configuration for h-m1."""
    
    # Inherited configs from h-e1
    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    aggregator: TriModalAggregatorConfig = field(default_factory=TriModalAggregatorConfig)
    feedback: FeedbackConfig = field(default_factory=FeedbackConfig)
    ppo: PPOConfig = field(default_factory=PPOConfig)
    
    # h-m1 specific configs
    phase1: Phase1Config = field(default_factory=Phase1Config)
    checkpoint: CheckpointConfig = field(default_factory=CheckpointConfig)
    
    # Experiment metadata
    experiment_name: str = "h-m1-phase1-validation"
    hypothesis_id: str = "h-m1"
    seed: int = 42
    device: str = "cuda"
    output_dir: str = "./h-m1"
    
    # Gate criteria (MUST_WORK)
    must_work_criteria: dict = field(default_factory=lambda: {
        "execution_dominance_phase1": True,  # Primary
        "improvement_rate_phase1_higher": True,  # Primary
        "weight_correlation_negative": True,  # Secondary
        "all_checkpoints_logged": True
    })


def load_phase1_config(config_path: Optional[str] = None) -> Phase1ExperimentConfig:
    """Load Phase 1 experiment configuration."""
    if config_path is None:
        return Phase1ExperimentConfig()
    
    import json
    with open(config_path, 'r') as f:
        config_dict = json.load(f)
    
    return Phase1ExperimentConfig(**config_dict)


def save_phase1_config(config: Phase1ExperimentConfig, output_path: str):
    """Save Phase 1 configuration to JSON."""
    from dataclasses import asdict
    import json
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(asdict(config), f, indent=2)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Phase1Config Implementation | Implement Phase1Config, CheckpointConfig, and Phase1ExperimentConfig dataclasses with validation |

---

## Configuration File Management

### Usage Example

```python
from h_m1.code.config.experiment_config import Phase1ExperimentConfig

# Create configuration with defaults
config = Phase1ExperimentConfig(
    experiment_name="h-m1_run1",
    output_dir="./h-m1/run1"
)

# Override specific values
config.phase1.total_episodes = 15000  # Extend training
config.checkpoint.checkpoint_dir = "./custom_checkpoints"

# Save to file
from h_m1.code.config.experiment_config import save_phase1_config
save_phase1_config(config, "./h-m1/config.json")

# Load from file
from h_m1.code.config.experiment_config import load_phase1_config
config = load_phase1_config("./h-m1/config.json")
```

### Validation Example

```python
def validate_phase1_config(config: Phase1ExperimentConfig) -> bool:
    """Validate Phase 1 configuration."""
    checks = []
    
    # Phase 1 checkpoints present
    phase1_checkpoints = [cp for cp in config.phase1.checkpoints if cp <= 0.3]
    checks.append(len(phase1_checkpoints) >= 4)
    
    # Total episodes sufficient
    checks.append(config.phase1.total_episodes >= 1000)
    
    # Evaluation samples match h-e1 validation split
    checks.append(config.phase1.eval_samples == 113)
    
    # Inherited configs match h-e1
    checks.append(config.model.model_name == "Salesforce/codegen-350M-mono")
    checks.append(config.ppo.learning_rate == 5e-5)
    
    return all(checks)
```

---

## Configuration Differences from h-e1

### New Parameters (h-m1 Specific)

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `phase1.checkpoints` | [0.0, 0.1, 0.2, 0.3, 0.7, 1.0] | Phase 1 monitoring points |
| `phase1.total_episodes` | 10000 | Training episodes |
| `phase1.weight_dominance_threshold` | 0.0 | Gate criterion |
| `phase1.improvement_rate_threshold` | 1.0 | Gate criterion |
| `phase1.correlation_threshold` | -0.6 | Gate criterion |
| `checkpoint.weights_csv` | "weights_phase1.csv" | Weight trajectory log |
| `checkpoint.pass_at_1_csv` | "pass_at_1_trajectory.csv" | Pass@1 trajectory log |

### Inherited Parameters (Unchanged from h-e1)

All parameters from `DataConfig`, `ModelConfig`, `TriModalAggregatorConfig`, `FeedbackConfig`, and `PPOConfig` are inherited without modification to ensure consistency with validated h-e1 baseline.

---

## Summary

### Configuration Coverage

| Component | Config Class | Purpose |
|-----------|--------------|---------|
| Phase 1 Analysis | `Phase1Config` | Checkpoints and gate thresholds (allocated task) |
| Checkpoint Management | `CheckpointConfig` | File paths and logging settings |
| Experiment | `Phase1ExperimentConfig` | Master config extending h-e1 |
| Data | `DataConfig` | Inherited from h-e1 |
| Model | `ModelConfig` | Inherited from h-e1 |
| Aggregator | `TriModalAggregatorConfig` | Inherited from h-e1 |
| Feedback | `FeedbackConfig` | Inherited from h-e1 |
| PPO | `PPOConfig` | Inherited from h-e1 |

### Key Design Choices

**Format**: Python dataclass (consistent with h-e1)  
**Validation**: Automatic via `__post_init__` for critical constraints  
**Inheritance**: Full reuse of h-e1 configs for consistency  
**Extensions**: Only Phase 1 specific monitoring added

---

**Document Status**: COMPLETED  
**Next Phase**: Phase 4 - Implementation  
**Output Path**: `/workspace/TEST_dl4c/docs/youra_research/h-m1/03_config.md`
