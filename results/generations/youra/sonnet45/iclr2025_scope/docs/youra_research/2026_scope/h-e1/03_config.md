---
hypothesis_id: h-e1
type: EXISTENCE
gate: MUST_WORK
date: 2026-03-18
generated_by: Phase 3 Configuration Design
---

# Configuration Specification: Low-Rank Structure Analysis (h-e1)

**Applied:** PyTorch dataclass patterns, HuggingFace model loading defaults, Standard SVD analysis settings

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: New implementation - no existing codebase analyzed
**Config Files Found**: None - new config design
**Pattern Used**: Python dataclass

---

## EXISTENCE Hypothesis - PoC Configuration

**Type:** EXISTENCE (Proof-of-Concept validation)
**Configuration Goal:** Minimal fixed settings to validate "does low-rank structure exist?"

This configuration contains ONLY:
- Single fixed values (no hyperparameter grid)
- Default values from research literature
- 1 seed for reproducibility
- Minimal sample count (sufficient to detect effect)

---

## C-1: Analysis Configuration (Complexity: 3, Budget: 3)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AnalysisConfig:
    """Configuration for low-rank structure analysis of LLaMA attention matrices."""

    # Model Configuration
    model_name: str = "meta-llama/Llama-2-7b-hf"
    model_precision: str = "fp16"  # Memory efficiency for V100/A100
    device: str = "cuda"

    # Target Layers
    target_layers_start: int = 20
    target_layers_end: int = 32

    # Data Configuration
    dataset_name: str = "EleutherAI/pile"
    dataset_split: str = "train"
    num_samples: int = 5000
    context_length: int = 2048
    batch_size: int = 4
    streaming: bool = True  # Memory-efficient dataset loading

    # SVD Analysis Parameters
    variance_threshold: float = 0.99  # 99% variance for effective rank
    # Non-standard: Using 0.99 threshold based on LoRA literature (standard: 0.95)

    # Entropy Analysis
    numerical_stability_epsilon: float = 1e-6  # For log-det computation

    # Regression Analysis
    regression_alpha: float = 0.01  # p-value threshold for statistical significance

    # Reproducibility
    random_seed: int = 42

    # Output Configuration
    output_dir: str = "./results"
    figures_dir: str = "./figures"
    figure_format: str = "png"
    figure_dpi: int = 300

    # Validation Thresholds (Gate Criteria)
    max_effective_rank: int = 256  # MUST_WORK threshold
    entropy_slope_max: float = 0.0  # β < 0 requirement

    @property
    def target_layers(self) -> range:
        """Return range object for target layers."""
        return range(self.target_layers_start, self.target_layers_end)
```

### Subtasks (3/3 used)

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | ModelConfig | Model loading and precision settings |
| C-1-2 | DataConfig | Dataset, sampling, and batching configuration |
| C-1-3 | AnalysisConfig | SVD thresholds, entropy parameters, output paths |

### Configuration Usage

```python
# In src/config.py
from dataclasses import asdict
import json


def load_config(config_path: Optional[str] = None) -> AnalysisConfig:
    """Load configuration from file or return defaults."""
    if config_path is None:
        return AnalysisConfig()

    with open(config_path, 'r') as f:
        config_dict = json.load(f)

    return AnalysisConfig(**config_dict)


def save_config(config: AnalysisConfig, output_path: str) -> None:
    """Save configuration to JSON file."""
    with open(output_path, 'w') as f:
        json.dump(asdict(config), f, indent=2)
```

---

## Configuration Rationale

### Model Settings
- **model_name**: LLaMA-2-7b-hf (standard for low-rank analysis)
- **model_precision**: fp16 (fits V100 16GB, standard practice)
- **target_layers**: 20-32 (deep layers, hypothesis focus)

### Data Settings
- **num_samples**: 5000 (sufficient for statistical significance, balances runtime)
- **context_length**: 2048 (standard LLaMA context, manageable memory)
- **batch_size**: 4 (V100/A100 memory constraint)
- **streaming**: True (The Pile is 825GB, streaming required)

### Analysis Settings
- **variance_threshold**: 0.99 (LoRA standard for attention rank estimation)
- **numerical_stability_epsilon**: 1e-6 (standard for log-det computation)

### Validation Thresholds
- **max_effective_rank**: 256 (hypothesis requirement, derived from SSM state budget)
- **entropy_slope_max**: 0.0 (monotonic decrease requirement, β < 0)

---

## Environment Configuration

### GPU Setup Script
```bash
#!/bin/bash
# File: code/run_analysis.sh

# Check GPU availability
nvidia-smi

# Select empty GPU (REQUIRED before running)
echo "Available GPUs shown above. Select empty GPU ID:"
read GPU_ID
export CUDA_VISIBLE_DEVICES=$GPU_ID

# Run analysis
python src/main.py --config config.json
```

### Requirements
```txt
# File: code/requirements.txt
torch>=2.0.0
transformers>=4.30.0
datasets>=2.12.0
scipy>=1.10.0
matplotlib>=3.5.0
seaborn>=0.12.0
```

---

## Configuration Validation

### Pre-run Checks
```python
# In src/config.py
def validate_config(config: AnalysisConfig) -> None:
    """Validate configuration before running experiment."""
    assert config.target_layers_end > config.target_layers_start, "Invalid layer range"
    assert config.num_samples > 0, "num_samples must be positive"
    assert 0.0 < config.variance_threshold < 1.0, "variance_threshold must be in (0, 1)"
    assert config.batch_size > 0, "batch_size must be positive"
    assert config.context_length > 0, "context_length must be positive"

    # Check GPU availability
    import torch
    assert torch.cuda.is_available(), "CUDA not available"

    print(f"✓ Configuration validated")
    print(f"  Model: {config.model_name}")
    print(f"  Target layers: {config.target_layers_start}-{config.target_layers_end}")
    print(f"  Samples: {config.num_samples}")
    print(f"  GPU: {torch.cuda.get_device_name(0)}")
```

---

## EXISTENCE Hypothesis Note

This is a **PoC configuration** - no hyperparameter tuning or grid search. The goal is to answer:
> "Does low-rank structure exist in deep LLaMA layers?"

Success criteria are binary (MUST_WORK gate):
1. r_eff < 256 for ALL layers 20-32
2. β < 0 with p < 0.01

If these criteria are not met with these settings, the hypothesis FAILS and the entire conversion approach is ABORTED.

---

*Configuration designed for EXISTENCE validation | Fixed settings | No hyperparameter tuning*
