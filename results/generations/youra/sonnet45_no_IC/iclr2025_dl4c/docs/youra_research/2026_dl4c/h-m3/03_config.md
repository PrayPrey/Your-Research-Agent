# Configuration Specification: h-m3
# Phase 3 Human Feedback Peak Validation

**Hypothesis ID**: h-m3  
**Type**: MECHANISM  
**Gate**: SHOULD_WORK  
**Date**: 2026-07-12  
**Budget**: 2 subtasks (Phase3 Aggregator Config, Conflict Case Evaluation Config)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: config classes verified from base code  
**Config Files Found**: `h-m2/code/config/experiment_config.py`, `h-m2/code/config/phase1_config.py`  
**Pattern Used**: dataclass (consistent with h-m1, h-m2)

---

## Applied Patterns

**Applied**: Gaussian Weight Scheduling Pattern (from h-m2)  
**Applied**: Incremental Extension Pattern (h-m2 validated framework)  
**Applied**: Dataclass Type Safety Pattern (h-m1/h-m2 validated approach)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

The following configs are inherited from h-m2 (which extends h-m1):

```python
# From: h-m2/code/config/experiment_config.py (ACTUAL CODE)

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

**Verified from**: `h-m2/code/config/experiment_config.py` (actual implementation)

---

## Phase 3 Aggregator Configuration [Complexity: 10, Budget: 1]

**Applied**: Gaussian Weight Scheduling Pattern (extended from h-m2)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List


@dataclass
class Phase3AggregatorConfig:
    """Phase 3 tri-modal aggregator configuration with human peak scheduling."""
    
    # Phase 3 boundaries
    phase3_start: float = 0.70
    phase3_end: float = 1.00
    
    # Human peak configuration (increases throughout Phase 3)
    human_peak_progress: float = 1.00
    human_weight_start: float = 0.40
    human_weight_end: float = 0.70
    
    # Execution weight schedule (decay from 0.40 to 0.20)
    exec_weight_start: float = 0.40
    exec_weight_end: float = 0.20
    
    # AI weight schedule (maintain mid-level ~0.20-0.30)
    ai_weight_floor: float = 0.20
    ai_weight_ceiling: float = 0.30
    
    # Phase 3 checkpoints
    checkpoints: List[float] = field(default_factory=lambda: [0.70, 0.80, 0.90, 1.00])
    
    # Weight normalization tolerance
    normalization_tolerance: float = 1e-6
    
    def __post_init__(self):
        # Validate Phase 3 boundaries
        assert 0.0 <= self.phase3_start < self.phase3_end <= 1.0, \
            "Phase 3 boundaries must satisfy 0 <= start < end <= 1"
        
        # Validate human weight increase
        assert self.human_weight_start < self.human_weight_end, \
            "Human weight must increase from start to end"
        
        # Validate checkpoints
        assert all(self.phase3_start <= cp <= self.phase3_end for cp in self.checkpoints), \
            "All checkpoints must be within Phase 3 boundaries"
        
        # Validate human peak at end
        assert self.human_peak_progress == self.phase3_end, \
            "Human peak should be at Phase 3 end (100%)"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Phase3AggregatorConfig Implementation | Implement Phase3AggregatorConfig dataclass with human peak scheduling and validation |

---

## Conflict Case Evaluation Configuration [Complexity: 9, Budget: 1]

**Applied**: Edge Case Evaluation Pattern (from RLHF research)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field


@dataclass
class ConflictCaseConfig:
    """Conflict case dataset and evaluation configuration."""
    
    # Conflict case filtering criteria
    target_count: int = 50
    pass_at_1_threshold: float = 1.0
    preference_threshold: float = 0.3
    
    # h-m1 baseline reference
    h_m1_baseline_results_path: str = "../h-m1/logs/execution_only_baseline_results.json"
    
    # Conflict case dataset paths
    conflict_cases_path: str = "./data/conflict_cases.json"
    
    # Evaluation settings
    eval_batch_size: int = 8
    eval_num_workers: int = 2
    
    # Expected preference score range (non-collapse)
    expected_median_min: float = 0.1
    expected_median_max: float = 0.4
    collapse_threshold: float = 0.1
    
    def __post_init__(self):
        # Validate filtering criteria
        assert 0.0 <= self.pass_at_1_threshold <= 1.0, \
            "pass@1 threshold must be in [0, 1]"
        assert 0.0 <= self.preference_threshold <= 1.0, \
            "Preference threshold must be in [0, 1]"
        
        # Validate expected range
        assert self.expected_median_min < self.expected_median_max, \
            "Median min must be less than median max"
        assert self.collapse_threshold <= self.expected_median_min, \
            "Collapse threshold should be below expected range"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | ConflictCaseConfig Implementation | Implement ConflictCaseConfig dataclass with filtering criteria and evaluation settings |

---

## Phase 3 PPO Configuration

**Applied**: Checkpoint Loading Pattern (extended from h-m2)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass


@dataclass
class Phase3PPOConfig:
    """Phase 3 PPO training configuration."""
    
    # h-m2 checkpoint configuration
    h_m2_checkpoint_path: str = "../h-m2/checkpoints/checkpoint_progress_0.70.pt"
    verify_checkpoint_metadata: bool = True
    expected_progress: float = 0.70
    expected_phase: str = "Phase 2"
    
    # Phase 3 training configuration
    learning_rate: float = 1e-5
    batch_size: int = 64
    total_episodes: int = 3000
    
    # Training progress mapping (70% -> 100%)
    progress_offset: int = 7000
    total_steps: int = 10000
    
    # Checkpoint and evaluation frequency
    checkpoint_frequency: int = 1000
    eval_frequency: int = 500
    conflict_eval_start_progress: float = 0.80
    
    # Inherited PPO hyperparameters from h-m2
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
        """Compute training progress for Phase 3 (70% -> 100%)."""
        return (current_episode + self.progress_offset) / self.total_steps
    
    def __post_init__(self):
        # Validate progress mapping
        start_progress = self.compute_training_progress(0)
        end_progress = self.compute_training_progress(self.total_episodes)
        
        assert 0.69 <= start_progress <= 0.71, \
            f"Start progress should be ~0.70, got {start_progress}"
        assert 0.99 <= end_progress <= 1.01, \
            f"End progress should be ~1.00, got {end_progress}"
```

---

## Phase 3 Metrics Configuration

**Applied**: Quality Metrics Pattern (extended from h-m2)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass


@dataclass
class Phase3MetricsConfig:
    """Phase 3 metrics and analysis configuration."""
    
    # Phase 3 analysis range
    phase3_start: float = 0.70
    phase3_end: float = 1.00
    
    # Human weight trajectory analysis
    weight_correlation_method: str = "pearson"
    min_positive_correlation: float = 0.0
    
    # Conflict case preference evaluation
    conflict_eval_samples: int = 50
    median_preference_min: float = 0.1
    median_preference_max: float = 0.4
    
    # Correctness maintenance evaluation
    execution_timeout: float = 5.0
    pass_at_1_eval_samples: int = 104
    correctness_maintenance_ratio: float = 0.95
    
    # Checkpoint data paths
    checkpoint_dir: str = "./checkpoints"
    log_dir: str = "./logs"
    
    # Human weight increase detection
    human_weight_increase_method: str = "endpoint_comparison"
    smooth_trajectory: bool = False
    
    def __post_init__(self):
        # Validate ratio thresholds
        assert 0.0 <= self.correctness_maintenance_ratio <= 1.0, \
            "Correctness maintenance ratio must be in [0, 1]"
        
        # Validate preference range
        assert self.median_preference_min < self.median_preference_max, \
            "Median preference min must be less than max"
```

---

## Phase 3 Gate Configuration

**Applied**: Gate Validation Pattern (extended from h-m2)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Phase3GateConfig:
    """Phase 3 gate validation configuration."""
    
    # Gate 1: Human weight increase
    gate1_name: str = "Human Weight Increase"
    gate1_description: str = "Human weight at 100% > human weight at 70%"
    gate1_enabled: bool = True
    
    # Gate 2: Conflict case non-collapse
    gate2_name: str = "Conflict Case Non-Collapse"
    gate2_description: str = "Median conflict preference in [0.1, 0.4]"
    gate2_threshold_min: float = 0.1
    gate2_threshold_max: float = 0.4
    gate2_enabled: bool = True
    
    # Gate 3: Correctness maintenance
    gate3_name: str = "Correctness Maintained"
    gate3_description: str = "Pass@1 at 100% >= 0.95 * Pass@1 at 70%"
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
            "gate1_human_increase": self.gate1_enabled,
            "gate2_conflict_non_collapse": self.gate2_enabled,
            "gate3_correctness_maintained": self.gate3_enabled
        }
    
    def __post_init__(self):
        # Validate thresholds
        assert 0.0 <= self.gate3_threshold <= 1.0, \
            "Correctness maintenance threshold must be in [0, 1]"
        assert self.gate2_threshold_min < self.gate2_threshold_max, \
            "Gate 2 min threshold must be less than max"
```

---

## Master Configuration

### Extended Configuration (h-m3)

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from .experiment_config import DataConfig, ModelConfig, FeedbackConfig


@dataclass
class Phase3ExperimentConfig:
    """Master configuration for h-m3 Phase 3 experiment."""
    
    # Inherited configs from h-m2/h-m1
    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    feedback: FeedbackConfig = field(default_factory=FeedbackConfig)
    
    # h-m3 specific configs
    aggregator: Phase3AggregatorConfig = field(default_factory=Phase3AggregatorConfig)
    ppo: Phase3PPOConfig = field(default_factory=Phase3PPOConfig)
    conflict: ConflictCaseConfig = field(default_factory=ConflictCaseConfig)
    metrics: Phase3MetricsConfig = field(default_factory=Phase3MetricsConfig)
    gate: Phase3GateConfig = field(default_factory=Phase3GateConfig)
    
    # Experiment metadata
    experiment_name: str = "h-m3-phase3-validation"
    hypothesis_id: str = "h-m3"
    seed: int = 42
    device: str = "cuda"
    output_dir: str = "./h-m3"
    
    # Gate criteria (SHOULD_WORK)
    should_work_criteria: dict = field(default_factory=lambda: {
        "human_weight_increase": True,
        "conflict_non_collapse": True,
        "correctness_maintained": True
    })
    
    def __post_init__(self):
        # Create output directories
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        Path(f"{self.output_dir}/checkpoints").mkdir(parents=True, exist_ok=True)
        Path(f"{self.output_dir}/logs").mkdir(parents=True, exist_ok=True)
        Path(f"{self.output_dir}/figures").mkdir(parents=True, exist_ok=True)
        Path(f"{self.output_dir}/data").mkdir(parents=True, exist_ok=True)
        
        # Validate h-m2 checkpoint path exists
        checkpoint_path = Path(self.ppo.h_m2_checkpoint_path)
        if not checkpoint_path.parent.exists():
            print(f"Warning: h-m2 checkpoint directory not found: {checkpoint_path.parent}")
        
        # Validate h-m1 baseline results path exists
        baseline_path = Path(self.conflict.h_m1_baseline_results_path)
        if not baseline_path.parent.exists():
            print(f"Warning: h-m1 baseline directory not found: {baseline_path.parent}")
```

---

## Configuration File Management

### Usage Example

```python
from h_m3.code.config.phase3_config import Phase3ExperimentConfig

# Create configuration with defaults
config = Phase3ExperimentConfig(
    experiment_name="h-m3_run1",
    output_dir="./h-m3/run1"
)

# Override specific values
config.ppo.h_m2_checkpoint_path = "/custom/path/checkpoint_progress_0.70.pt"
config.conflict.target_count = 50
config.aggregator.human_weight_end = 0.75

# Access nested configs
print(f"Learning rate: {config.ppo.learning_rate}")
print(f"Human peak: {config.aggregator.human_peak_progress}")
print(f"Conflict threshold: {config.gate.gate2_threshold_min}")
```

### Validation Example

```python
def validate_phase3_config(config: Phase3ExperimentConfig) -> bool:
    """Validate Phase 3 configuration."""
    checks = []
    
    # Phase 3 checkpoints present
    phase3_checkpoints = config.aggregator.checkpoints
    checks.append(len(phase3_checkpoints) == 4)
    checks.append(min(phase3_checkpoints) >= 0.70)
    checks.append(max(phase3_checkpoints) <= 1.00)
    
    # h-m2 checkpoint path configured
    checks.append(config.ppo.h_m2_checkpoint_path != "")
    
    # Learning rate consistent with h-m2
    checks.append(config.ppo.learning_rate == 1e-5)
    
    # Human weight increase configured
    checks.append(config.aggregator.human_weight_start < config.aggregator.human_weight_end)
    
    # Conflict case count configured
    checks.append(config.conflict.target_count == 50)
    
    # Gate criteria enabled
    checks.append(config.gate.gate1_enabled)
    checks.append(config.gate.gate2_enabled)
    checks.append(config.gate.gate3_enabled)
    
    return all(checks)
```

---

## Configuration Differences from h-m2

### New Parameters (h-m3 Specific)

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `aggregator.phase3_start` | 0.70 | Phase 3 start boundary |
| `aggregator.phase3_end` | 1.00 | Phase 3 end boundary |
| `aggregator.human_peak_progress` | 1.00 | Human weight peak location |
| `aggregator.human_weight_start` | 0.40 | Human weight at 70% |
| `aggregator.human_weight_end` | 0.70 | Human weight at 100% |
| `aggregator.exec_weight_end` | 0.20 | Execution weight at 100% |
| `aggregator.checkpoints` | [0.70, 0.80, 0.90, 1.00] | Phase 3 monitoring points |
| `ppo.h_m2_checkpoint_path` | "../h-m2/checkpoints/checkpoint_progress_0.70.pt" | Starting checkpoint |
| `ppo.total_episodes` | 3000 | Phase 3 training episodes (reduced from 4000) |
| `ppo.progress_offset` | 7000 | Maps episodes to 70%-100% |
| `conflict.target_count` | 50 | Number of conflict cases |
| `conflict.pass_at_1_threshold` | 1.0 | Filter: execution passes |
| `conflict.preference_threshold` | 0.3 | Filter: low preference |
| `conflict.expected_median_min` | 0.1 | Gate 2 lower bound |
| `conflict.expected_median_max` | 0.4 | Gate 2 upper bound |
| `metrics.median_preference_min` | 0.1 | Non-collapse threshold |
| `metrics.median_preference_max` | 0.4 | Non-collapse threshold |
| `gate.gate2_threshold_min` | 0.1 | Conflict case median min |
| `gate.gate2_threshold_max` | 0.4 | Conflict case median max |

### Modified Parameters (Changed from h-m2)

| Parameter | h-m2 Value | h-m3 Value | Reason |
|-----------|-----------|-----------|--------|
| `ppo.total_episodes` | 10000 (for 30-70%) | 3000 (for 70-100%) | Shorter Phase 3 range |
| `ppo.progress_offset` | 3000 | 7000 | Start from 70% instead of 30% |

### Inherited Parameters (Reused from h-m2/h-m1)

All parameters from `DataConfig`, `ModelConfig`, `FeedbackConfig`, and core `PPOConfig` hyperparameters (clip_range, vf_coef, learning_rate, etc.) are inherited without modification to ensure consistency with validated h-m2 checkpoint.

---

## Summary

### Configuration Coverage

| Component | Config Class | Purpose |
|-----------|--------------|---------|
| Phase 3 Aggregator | `Phase3AggregatorConfig` | Human peak scheduling (Task C-2) |
| Conflict Cases | `ConflictCaseConfig` | Edge case dataset (Task C-1) |
| Phase 3 PPO | `Phase3PPOConfig` | Checkpoint loading and training (Task C-4) |
| Phase 3 Metrics | `Phase3MetricsConfig` | Human weight, conflict, correctness tracking (Task C-6) |
| Gate Validator | `Phase3GateConfig` | SHOULD_WORK validation (Task C-7) |
| Experiment | `Phase3ExperimentConfig` | Master config extending h-m2 |
| Data | `DataConfig` | Inherited from h-m2/h-m1 |
| Model | `ModelConfig` | Inherited from h-m2/h-m1 |
| Feedback | `FeedbackConfig` | Inherited from h-m2/h-m1 |

### Key Design Choices

**Format**: Python dataclass (consistent with h-m1, h-m2)  
**Validation**: Automatic via `__post_init__` for critical constraints  
**Inheritance**: Full reuse of h-m2/h-m1 configs for consistency  
**Extensions**: Phase 3 human peak scheduling, conflict case evaluation, gate validation

---

**Document Status**: COMPLETED  
**Next Phase**: Phase 4 - Implementation  
**Output Path**: `/workspace/TEST_dl4c/docs/youra_research/h-m3/03_config.md`
