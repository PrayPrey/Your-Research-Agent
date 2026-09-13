# Configuration Specification: h-m2
# Phase 2 AI Feedback Peak Validation

**Hypothesis ID**: h-m2  
**Type**: MECHANISM  
**Gate**: SHOULD_WORK  
**Date**: 2026-07-12  
**Budget**: 4 subtasks (B-1: Phase2 Aggregator Config, B-3: Phase2 PPO Config, B-5: Phase2 Metrics Config, B-6: Gate Validator Config)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: config classes verified from base code  
**Config Files Found**: `h-m1/code/config/experiment_config.py`, `h-m1/code/config/phase1_config.py`  
**Pattern Used**: dataclass (consistent with h-m1)

---

## Applied Patterns

**Applied**: PyTorch Checkpoint Loading Pattern (from Archon KB)  
**Applied**: Dataclass Type Safety Pattern (h-m1 validated approach)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

The following configs are inherited from h-m1 (which extends h-e1):

```python
# From: h-m1/code/config/experiment_config.py (ACTUAL CODE)

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

**Verified from**: `h-m1/code/config/experiment_config.py` (actual implementation)

---

## B-1: Phase2 Aggregator Configuration [Complexity: 10, Budget: 1]

**Applied**: Gaussian Weight Scheduling Pattern (from h-m1)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List


@dataclass
class Phase2AggregatorConfig:
    """Phase 2 tri-modal aggregator configuration with AI peak scheduling."""
    
    # Phase 2 boundaries
    phase2_start: float = 0.30
    phase2_end: float = 0.70
    
    # AI peak configuration
    ai_peak_progress: float = 0.50
    ai_peak_variance: float = 0.05
    ai_weight_floor: float = 0.30
    
    # Execution weight schedule (decay from 0.50 to 0.20)
    exec_weight_start: float = 0.50
    exec_weight_end: float = 0.20
    
    # Human weight schedule (increase from 0.10 to 0.20)
    human_weight_start: float = 0.10
    human_weight_end: float = 0.20
    
    # Phase 2 checkpoints
    checkpoints: List[float] = field(default_factory=lambda: [0.30, 0.40, 0.50, 0.60, 0.70])
    
    # Weight normalization tolerance
    normalization_tolerance: float = 1e-6
    
    def __post_init__(self):
        # Validate Phase 2 boundaries
        assert 0.0 <= self.phase2_start < self.phase2_end <= 1.0, \
            "Phase 2 boundaries must satisfy 0 <= start < end <= 1"
        
        # Validate AI peak within Phase 2
        assert self.phase2_start <= self.ai_peak_progress <= self.phase2_end, \
            "AI peak must be within Phase 2 boundaries"
        
        # Validate checkpoints
        assert all(self.phase2_start <= cp <= self.phase2_end for cp in self.checkpoints), \
            "All checkpoints must be within Phase 2 boundaries"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Phase2AggregatorConfig Implementation | Implement Phase2AggregatorConfig dataclass with Gaussian AI peak scheduling and validation |

---

## B-3: Phase2 PPO Configuration [Complexity: 9, Budget: 1]

**Applied**: Checkpoint Loading Pattern (from Archon KB)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Phase2PPOConfig:
    """Phase 2 PPO training configuration."""
    
    # h-m1 checkpoint configuration
    h_m1_checkpoint_path: str = "../h-m1/checkpoints/checkpoint_progress_0.30.pt"
    verify_checkpoint_metadata: bool = True
    expected_progress: float = 0.30
    expected_phase: str = "Phase 1"
    
    # Phase 2 training configuration
    learning_rate: float = 1e-5
    batch_size: int = 64
    total_episodes: int = 10000
    
    # Training progress mapping (30% -> 70%)
    progress_offset: int = 3000
    total_steps: int = 10000
    
    # Checkpoint and evaluation frequency
    checkpoint_frequency: int = 1000
    eval_frequency: int = 500
    
    # Inherited PPO hyperparameters from h-m1
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
    gradient_accumulation_steps: int = 4
    
    # Learning rate schedule
    use_linear_decay: bool = True
    warmup_steps: int = 0
    
    def compute_training_progress(self, current_episode: int) -> float:
        """Compute training progress for Phase 2 (30% -> 70%)."""
        return (current_episode + self.progress_offset) / self.total_steps
    
    def __post_init__(self):
        # Validate progress mapping
        start_progress = self.compute_training_progress(0)
        end_progress = self.compute_training_progress(self.total_episodes)
        
        assert 0.29 <= start_progress <= 0.31, \
            f"Start progress should be ~0.30, got {start_progress}"
        assert 0.69 <= end_progress <= 0.71, \
            f"End progress should be ~0.70, got {end_progress}"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Phase2PPOConfig Implementation | Implement Phase2PPOConfig dataclass with checkpoint loading and progress mapping logic |

---

## B-5: Phase2 Metrics Configuration [Complexity: 11, Budget: 1]

**Applied**: Quality Metrics Pattern (from Archon KB)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Phase2MetricsConfig:
    """Phase 2 metrics and analysis configuration."""
    
    # Phase 2 analysis range
    phase2_start: float = 0.30
    phase2_end: float = 0.70
    
    # Quality evaluation configuration
    quality_annotation_cache: str = "./data/annotations/cache.json"
    quality_eval_samples: int = 104
    fallback_to_ai_feedback: bool = True
    
    # Correctness evaluation configuration
    execution_timeout: float = 5.0
    pass_at_1_eval_samples: int = 104
    
    # Checkpoint data paths
    checkpoint_dir: str = "./checkpoints"
    log_dir: str = "./logs"
    
    # Metric computation settings
    quality_improvement_rate_baseline: float = 0.0
    correctness_maintenance_ratio: float = 0.95
    
    # AI peak detection settings
    ai_peak_detection_method: str = "argmax"
    smooth_trajectory: bool = False
    
    def __post_init__(self):
        # Validate ratio thresholds
        assert 0.0 <= self.correctness_maintenance_ratio <= 1.0, \
            "Correctness maintenance ratio must be in [0, 1]"
        
        # Validate quality improvement baseline
        assert self.quality_improvement_rate_baseline >= 0.0, \
            "Quality improvement baseline must be non-negative"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Phase2MetricsConfig Implementation | Implement Phase2MetricsConfig dataclass with quality, correctness, and AI peak detection settings |

---

## B-6: Gate Validator Configuration [Complexity: 8, Budget: 1]

**Applied**: Gate Validation Pattern (from h-m1)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Phase2GateConfig:
    """Phase 2 gate validation configuration."""
    
    # Gate 1: AI weight peak detection
    gate1_name: str = "AI Peak Detected"
    gate1_description: str = "AI weight is highest among three signals at peak"
    gate1_enabled: bool = True
    
    # Gate 2: Quality improvement
    gate2_name: str = "Quality Improved"
    gate2_description: str = "Quality improvement rate > 0 from 30% to 70%"
    gate2_threshold: float = 0.0
    gate2_enabled: bool = True
    
    # Gate 3: Correctness maintenance
    gate3_name: str = "Correctness Maintained"
    gate3_description: str = "Pass@1 at 70% >= 0.95 * Pass@1 at 30%"
    gate3_threshold: float = 0.95
    gate3_enabled: bool = True
    
    # Output paths
    gate_report_path: str = "./gate_validation.json"
    gate_figure_path: str = "./figures/gate_metrics.png"
    
    # Visualization settings
    figure_dpi: int = 300
    bar_colors: Dict[str, str] = field(default_factory=lambda: {
        "pass": "green",
        "fail": "red"
    })
    
    def get_gate_criteria(self) -> Dict[str, bool]:
        """Return enabled gate criteria."""
        return {
            "gate1_ai_peak": self.gate1_enabled,
            "gate2_quality_improved": self.gate2_enabled,
            "gate3_correctness_maintained": self.gate3_enabled
        }
    
    def __post_init__(self):
        # Validate thresholds
        assert 0.0 <= self.gate3_threshold <= 1.0, \
            "Correctness maintenance threshold must be in [0, 1]"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Phase2GateConfig Implementation | Implement Phase2GateConfig dataclass with three gate criteria and visualization settings |

---

## Master Configuration

### Extended Configuration (h-m2)

```python
from dataclasses import dataclass, field
from pathlib import Path
from .experiment_config import ExperimentConfig, PPOConfig


@dataclass
class Phase2ExperimentConfig:
    """Master configuration for h-m2 Phase 2 experiment."""
    
    # Inherited configs from h-m1
    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    feedback: FeedbackConfig = field(default_factory=FeedbackConfig)
    
    # h-m2 specific configs
    aggregator: Phase2AggregatorConfig = field(default_factory=Phase2AggregatorConfig)
    ppo: Phase2PPOConfig = field(default_factory=Phase2PPOConfig)
    metrics: Phase2MetricsConfig = field(default_factory=Phase2MetricsConfig)
    gate: Phase2GateConfig = field(default_factory=Phase2GateConfig)
    
    # Experiment metadata
    experiment_name: str = "h-m2-phase2-validation"
    hypothesis_id: str = "h-m2"
    seed: int = 42
    device: str = "cuda"
    output_dir: str = "./h-m2"
    
    # Gate criteria (SHOULD_WORK)
    should_work_criteria: dict = field(default_factory=lambda: {
        "ai_peak_detected": True,
        "quality_improved": True,
        "correctness_maintained": True
    })
    
    def __post_init__(self):
        # Create output directories
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        Path(f"{self.output_dir}/checkpoints").mkdir(parents=True, exist_ok=True)
        Path(f"{self.output_dir}/logs").mkdir(parents=True, exist_ok=True)
        Path(f"{self.output_dir}/figures").mkdir(parents=True, exist_ok=True)
        
        # Validate h-m1 checkpoint path exists
        checkpoint_path = Path(self.ppo.h_m1_checkpoint_path)
        if not checkpoint_path.parent.exists():
            print(f"Warning: h-m1 checkpoint directory not found: {checkpoint_path.parent}")
```

---

## Configuration File Management

### Usage Example

```python
from h_m2.code.config.phase2_config import Phase2ExperimentConfig

# Create configuration with defaults
config = Phase2ExperimentConfig(
    experiment_name="h-m2_run1",
    output_dir="./h-m2/run1"
)

# Override specific values
config.ppo.h_m1_checkpoint_path = "/custom/path/checkpoint_progress_0.30.pt"
config.aggregator.ai_peak_progress = 0.55

# Access nested configs
print(f"Learning rate: {config.ppo.learning_rate}")
print(f"AI peak: {config.aggregator.ai_peak_progress}")
print(f"Quality threshold: {config.gate.gate2_threshold}")
```

### Validation Example

```python
def validate_phase2_config(config: Phase2ExperimentConfig) -> bool:
    """Validate Phase 2 configuration."""
    checks = []
    
    # Phase 2 checkpoints present
    phase2_checkpoints = config.aggregator.checkpoints
    checks.append(len(phase2_checkpoints) >= 5)
    checks.append(min(phase2_checkpoints) >= 0.30)
    checks.append(max(phase2_checkpoints) <= 0.70)
    
    # h-m1 checkpoint path configured
    checks.append(config.ppo.h_m1_checkpoint_path != "")
    
    # Learning rate reduced from Phase 1
    checks.append(config.ppo.learning_rate == 1e-5)
    
    # Gate criteria enabled
    checks.append(config.gate.gate1_enabled)
    checks.append(config.gate.gate2_enabled)
    checks.append(config.gate.gate3_enabled)
    
    return all(checks)
```

---

## Configuration Differences from h-m1

### New Parameters (h-m2 Specific)

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `aggregator.phase2_start` | 0.30 | Phase 2 start boundary |
| `aggregator.phase2_end` | 0.70 | Phase 2 end boundary |
| `aggregator.ai_peak_progress` | 0.50 | AI weight peak location |
| `aggregator.ai_peak_variance` | 0.05 | Gaussian peak width |
| `aggregator.checkpoints` | [0.30, 0.40, 0.50, 0.60, 0.70] | Phase 2 monitoring points |
| `ppo.h_m1_checkpoint_path` | "../h-m1/checkpoints/checkpoint_progress_0.30.pt" | Starting checkpoint |
| `ppo.learning_rate` | 1e-5 | Reduced from Phase 1 (5e-5) |
| `ppo.total_episodes` | 10000 | Phase 2 training episodes |
| `ppo.progress_offset` | 3000 | Maps episodes to 30%-70% |
| `metrics.quality_improvement_rate_baseline` | 0.0 | Gate 2 threshold |
| `metrics.correctness_maintenance_ratio` | 0.95 | Gate 3 threshold |
| `gate.gate2_threshold` | 0.0 | Quality improvement must be positive |
| `gate.gate3_threshold` | 0.95 | Max 5% correctness regression |

### Inherited Parameters (Reused from h-m1)

All parameters from `DataConfig`, `ModelConfig`, `FeedbackConfig`, and core `PPOConfig` hyperparameters (clip_range, vf_coef, etc.) are inherited without modification to ensure consistency with validated h-m1 baseline.

---

## Summary

### Configuration Coverage

| Component | Config Class | Purpose |
|-----------|--------------|---------|
| Phase 2 Aggregator | `Phase2AggregatorConfig` | AI peak scheduling (Task B-1) |
| Phase 2 PPO | `Phase2PPOConfig` | Checkpoint loading and training (Task B-3) |
| Phase 2 Metrics | `Phase2MetricsConfig` | Quality and correctness tracking (Task B-5) |
| Gate Validator | `Phase2GateConfig` | SHOULD_WORK validation (Task B-6) |
| Experiment | `Phase2ExperimentConfig` | Master config extending h-m1 |
| Data | `DataConfig` | Inherited from h-m1 |
| Model | `ModelConfig` | Inherited from h-m1 |
| Feedback | `FeedbackConfig` | Inherited from h-m1 |

### Key Design Choices

**Format**: Python dataclass (consistent with h-m1)  
**Validation**: Automatic via `__post_init__` for critical constraints  
**Inheritance**: Full reuse of h-m1/h-e1 configs for consistency  
**Extensions**: Phase 2 specific scheduling, checkpoint loading, and gate validation

---

**Document Status**: COMPLETED  
**Next Phase**: Phase 4 - Implementation  
**Output Path**: `/workspace/TEST_dl4c/docs/youra_research/h-m2/03_config.md`
