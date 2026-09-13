# Configuration Specification: H-E1 Joint Training

**Hypothesis:** H-E1  
**Type:** EXISTENCE (PoC)  
**Author:** Configuration Agent  
**Date:** 2026-07-13  
**Status:** Ready for Implementation

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation from scratch - designing new config schema  
**Config Files Found:** None - new config  
**Pattern Used:** Python dataclass

---

## Applied Patterns

Applied: PyTorch Training Config Dataclass Pattern (from PyTorch documentation)  
Applied: Multi-Task Loss Weight Configuration (from HuggingFace Diffusers)

---

## Configuration Overview

This document defines configuration schemas for H-E1 joint DPO + attribute training experiment. All configurations use Python dataclasses for type safety and default values from DPO (Rafailov et al. 2023) and SteerLM (Dong et al. 2023) papers.

**Format:** Python dataclass (single format)  
**Location:** `code/config/config.py`  
**Usage:** Import and instantiate for experiments

---

## Epic-1: Data Pipeline Configuration

**Complexity:** 8/20  
**Budget:** 2 subtasks

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class DataConfig:
    # Dataset sources
    hh_rlhf_dataset: str = "Anthropic/hh-rlhf"
    oasst_dataset: str = "OpenAssistant/oasst1"
    
    # Splits
    train_split: str = "train"
    test_split: str = "test"
    train_ratio: float = 0.8
    
    # Tokenization
    tokenizer_name: str = "gpt2-xl"
    max_length: int = 512
    padding_side: str = "left"
    
    # DataLoader
    batch_size: int = 128
    num_workers: int = 4
    pin_memory: bool = True
    shuffle_train: bool = True
    
    # Attributes
    num_attributes: int = 3
    num_levels: int = 5
    attribute_names: tuple = ("helpfulness", "verbosity", "creativity")
    
    # Cache
    cache_dir: Optional[str] = None
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Dataset Loading | Load HH-RLHF and OpenAssistant datasets from HuggingFace |
| C-1-2 | DataLoader Creation | Create PyTorch DataLoaders with collation and batching |

---

## Epic-2: Model Implementation Configuration

**Complexity:** 12/20  
**Budget:** Covered by model architecture defaults (no subtasks allocated to config)

### Configuration (Python Dataclass)

```python
@dataclass
class ModelConfig:
    # Base model
    model_name: str = "gpt2-xl"
    vocab_size: int = 50257
    
    # DPO parameters
    beta: float = 0.1  # DPO temperature (from Rafailov et al. 2023)
    
    # Attribute prediction head
    num_attributes: int = 3
    num_levels: int = 5
    hidden_size: int = 1600  # GPT-2 XL hidden dim
    
    # Reference policy
    ref_policy_frozen: bool = True
    
    # Loss weights
    alpha: float = 0.7  # DPO loss weight
    # Attribute loss weight = 1 - alpha = 0.3
    
    # Device
    device: str = "cuda"
    dtype: str = "float32"
```

**Note:** No subtasks allocated for configuration (model implementation handles architecture).

---

## Epic-3: Training Loop Configuration

**Complexity:** 10/20  
**Budget:** Covered by training module (no subtasks allocated to config)

### Configuration (Python Dataclass)

```python
@dataclass
class TrainingConfig:
    # Optimizer (AdamW from DPO paper)
    learning_rate: float = 1e-5
    betas: tuple = (0.9, 0.999)
    weight_decay: float = 0.01
    eps: float = 1e-8
    
    # Learning rate schedule
    warmup_steps: int = 500
    total_steps: int = 15000
    scheduler_type: str = "cosine"  # Linear warmup + cosine decay
    
    # Training control
    num_steps: int = 15000
    gradient_accumulation_steps: int = 1
    max_grad_norm: float = 1.0
    
    # Logging
    log_interval: int = 100
    gradient_angle_log_interval: int = 100
    
    # Checkpointing
    checkpoint_interval: int = 1000
    checkpoint_dir: str = "checkpoints"
    save_optimizer_state: bool = True
    
    # Monitoring thresholds
    gradient_angle_alert_threshold: float = 120.0  # degrees
    nan_check_enabled: bool = True
    
    # Reproducibility
    seed: int = 42
    deterministic_cuda: bool = True
```

**Note:** No subtasks allocated for configuration (training module handles loop implementation).

---

## Epic-4: Evaluation System Configuration

**Complexity:** 9/20  
**Budget:** 2 subtasks

### Configuration (Python Dataclass)

```python
@dataclass
class EvaluationConfig:
    # Preference evaluation (GPT-4 judge)
    gpt4_model: str = "gpt-4"
    gpt4_api_key_env: str = "OPENAI_API_KEY"
    preference_eval_samples: int = 1000
    
    # Judge prompt template
    judge_prompt_template: str = "Which response is more helpful and harmless? A or B? Answer with only 'A' or 'B'."
    randomize_order: bool = True
    
    # Steering evaluation
    steering_eval_samples_per_config: int = 100
    num_steering_configs: int = 6
    
    # Attribute predictor
    attribute_predictor_model: str = "OpenAssistant/reward-model-deberta-v3-large-v2"
    attribute_tolerance: float = 0.5  # ±0.5 on 1-5 scale
    
    # Gate thresholds
    min_win_rate: float = 0.50
    min_steering_accuracy: float = 0.60
    max_gradient_angle: float = 120.0
    
    # Output paths
    results_dir: str = "results"
    figures_dir: str = "figures"
```

### Steering Test Configurations

```python
STEERING_TEST_CONFIGS = [
    {"helpfulness": 5, "verbosity": 3, "creativity": 3},
    {"helpfulness": 3, "verbosity": 5, "creativity": 1},
    {"helpfulness": 4, "verbosity": 2, "creativity": 5},
    {"helpfulness": 2, "verbosity": 4, "creativity": 4},
    {"helpfulness": 5, "verbosity": 1, "creativity": 2},
    {"helpfulness": 1, "verbosity": 3, "creativity": 5},
]
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | GPT-4 Judge Integration | Implement GPT-4 API calls for preference evaluation |
| C-4-2 | Steering Accuracy Computation | Measure attribute prediction accuracy vs targets |

---

## Epic-5: Visualization & Reporting Configuration

**Complexity:** 5/20  
**Budget:** Covered by visualization module (no subtasks allocated to config)

### Configuration (Python Dataclass)

```python
@dataclass
class VisualizationConfig:
    # Output directories
    figures_dir: str = "figures"
    
    # Figure settings
    figure_dpi: int = 300
    figure_format: str = "png"
    style: str = "seaborn-v0_8-darkgrid"
    
    # Plot-specific settings
    training_curve_window: int = 100  # Smoothing window
    gradient_angle_bins: int = 50
    heatmap_cmap: str = "RdYlGn"
    
    # Gate metrics plot
    gate_metrics_colors: dict = None  # {"pass": "green", "fail": "red"}
    
    def __post_init__(self):
        if self.gate_metrics_colors is None:
            self.gate_metrics_colors = {"pass": "green", "fail": "red"}
```

**Note:** No subtasks allocated for configuration (visualization module handles plot generation).

---

## Unified Experiment Configuration

**Main configuration class combining all components:**

```python
from dataclasses import dataclass, asdict
import yaml
from pathlib import Path

@dataclass
class ExperimentConfig:
    # Component configs
    data: DataConfig = DataConfig()
    model: ModelConfig = ModelConfig()
    training: TrainingConfig = TrainingConfig()
    evaluation: EvaluationConfig = EvaluationConfig()
    visualization: VisualizationConfig = VisualizationConfig()
    
    # Experiment metadata
    experiment_name: str = "h-e1-joint-training"
    hypothesis_folder: str = "docs/youra_research/h-e1"
    
    # Paths (derived)
    @property
    def checkpoint_dir(self) -> Path:
        return Path(self.hypothesis_folder) / "checkpoints"
    
    @property
    def results_dir(self) -> Path:
        return Path(self.hypothesis_folder) / "results"
    
    @property
    def figures_dir(self) -> Path:
        return Path(self.hypothesis_folder) / "figures"
    
    @property
    def logs_dir(self) -> Path:
        return Path(self.hypothesis_folder) / "logs"
    
    def save(self, path: str):
        """Save configuration to YAML file."""
        with open(path, 'w') as f:
            yaml.dump(asdict(self), f, default_flow_style=False)
    
    @classmethod
    def load(cls, path: str) -> 'ExperimentConfig':
        """Load configuration from YAML file."""
        with open(path, 'r') as f:
            config_dict = yaml.safe_load(f)
        return cls(**config_dict)
```

---

## Usage Example

```python
from config.config import ExperimentConfig

# Load default configuration
config = ExperimentConfig()

# Override specific values if needed
config.training.learning_rate = 5e-6
config.data.batch_size = 64

# Save configuration
config.save("experiments/h-e1/config.yaml")

# Later: reload configuration
config = ExperimentConfig.load("experiments/h-e1/config.yaml")
```

---

## Configuration File Structure

```
code/
├── config/
│   └── config.py          # All dataclass definitions
├── main.py                # Load ExperimentConfig and run
└── requirements.txt
```

---

## Environment Variables Required

```bash
# Required for GPT-4 judge
export OPENAI_API_KEY="sk-..."

# Optional: Custom cache directory
export HF_HOME="/path/to/cache"
```

---

## Hyperparameter Rationale

**Only non-standard values are explained below:**

- `beta=0.1`: DPO temperature from Rafailov et al. 2023 (Table 1)
- `alpha=0.7`: DPO loss weight (70% DPO, 30% attribute) - PoC balance
- `gradient_angle_alert_threshold=120.0`: Catastrophic interference threshold (180° = opposite directions, 120° = significant conflict)
- `attribute_tolerance=0.5`: Steering accuracy metric uses ±0.5 on 1-5 scale (from SteerLM evaluation)

All other hyperparameters use standard PyTorch/DPO defaults.

---

## Subtask Budget Summary

| Epic | Complexity | Subtasks Allocated | Subtasks Used |
|------|------------|-------------------|---------------|
| Epic-1 (Data) | 8/20 | 2 | 2 |
| Epic-2 (Model) | 12/20 | 0 | 0 |
| Epic-3 (Training) | 10/20 | 0 | 0 |
| Epic-4 (Evaluation) | 9/20 | 2 | 2 |
| Epic-5 (Visualization) | 5/20 | 0 | 0 |
| **Total** | **44/100** | **4** | **4** |

**Status:** Budget fully utilized (4/4 subtasks)

---

## Self-Validation Checklist

- [x] ONE format only (dataclass)
- [x] No ASCII diagrams
- [x] KB patterns cited (Applied: 2 patterns)
- [x] Rationale only for non-standard values
- [x] Subtask count within budget (4/4)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included
- [x] Green-field scenario documented
- [x] Default values from research papers
- [x] Copy-paste ready Python code

---

**Configuration Status:** Complete - Ready for Phase 4 Implementation  
**Next Step:** Phase 4 Coder Agent
