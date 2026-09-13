---
hypothesis_id: h-m2
type: MECHANISM
gate: MUST_WORK
date: 2026-03-18
generated_by: Phase 3 Configuration Design
---

# Configuration Specification: Selective SSM Adapter Distillation (h-m2)

**Applied:** PyTorch dataclass patterns, MOHAWK distillation defaults

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: New implementation - no code reuse from h-m1
**Config Files Found**: None - new config design
**Pattern Used**: Python dataclass
**Note**: h-m1 used static SVD analysis, h-m2 uses dynamic distillation training (different methodologies)

---

## D-1: Environment Setup (Complexity: 6, Budget: 1)

**Applied**: Standard PyTorch environment setup

### Configuration (Python Dataclass)

```python
@dataclass
class EnvironmentConfig:
    cuda_visible_devices: str = "0"
    use_fp16: bool = True
    hf_token: Optional[str] = None
```

### Subtasks (1/1 used)

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | SetupEnvironment | Install mamba-ssm, verify CUDA, configure HF token |

---

## D-2: Data Pipeline (Complexity: 10, Budget: 1)

**Applied**: HuggingFace streaming dataset patterns

### Configuration (Python Dataclass)

```python
@dataclass
class DataConfig:
    dataset_name: str = "EleutherAI/pile"
    dataset_fallback: str = "allenai/c4"
    longbench_tasks: List[str] = field(default_factory=lambda: ["narrativeqa", "qasper", "hotpotqa", "multifieldqa_en"])
    batch_size: int = 8
    context_length: int = 4096
    streaming: bool = True
    num_eval_samples: int = 100
```

### Subtasks (1/1 used)

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | DataPipeline | Implement streaming data loaders for The Pile/C4 and LongBench |

---

## D-3: Model Loading Module (Complexity: 8, Budget: 1)

**Applied**: HuggingFace model loading patterns

### Configuration (Python Dataclass)

```python
@dataclass
class ModelConfig:
    model_name: str = "meta-llama/Llama-2-7b-hf"
    target_layer: int = 28
    device: str = "cuda"
    dtype: torch.dtype = field(default=torch.float16)
    max_position_embeddings: int = 131072
    # Non-standard: Extended context (128K) for RoPE scaling validation
```

### Subtasks (1/1 used)

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | ModelLoader | Load LLaMA-7B, extract L28, configure RoPE scaling |

---

## D-4: SSM Adapter Implementation (Complexity: 11, Budget: 0)

**Applied**: Mamba SSM default configurations

### Configuration (Python Dataclass)

```python
@dataclass
class SSMConfig:
    d_model: int = 4096
    d_state: int = 512
    # Non-standard: Using 512 as primary state size for W2 < 0.05 criterion
    d_conv: int = 4
    expand: int = 2
    state_sizes_sweep: List[int] = field(default_factory=lambda: [64, 128, 256, 512, 1024])
```

### Subtasks (0/0 used)

No additional subtasks allocated (within D-4 breakdown).

---

## D-5: Jacobian Analyzer (Complexity: 12, Budget: 0)

**Applied**: PyTorch autograd patterns, Wasserstein-2 computation

### Configuration (Python Dataclass)

```python
@dataclass
class JacobianConfig:
    use_double_precision: bool = True
    # Non-standard: FP64 for Jacobian computation to avoid numerical instability
    eigenvalue_clipping: bool = True
    clip_threshold: float = 1e-8
    w2_threshold: float = 0.05
```

### Subtasks (0/0 used)

No additional subtasks allocated (within D-5 breakdown).

---

## D-6: MOHAWK Distiller (Complexity: 15, Budget: 1)

**Applied**: MOHAWK 3-stage distillation framework

### Configuration (Python Dataclass)

```python
@dataclass
class MOHAWKConfig:
    # Stage 1: Matrix Orientation
    stage1_tokens: int = 100_000_000
    stage1_lr: float = 1e-4

    # Stage 2: Hidden-State Alignment
    stage2_tokens: int = 500_000_000
    stage2_lr: float = 5e-5
    lambda_jacobian: float = 0.1

    # Stage 3: End-to-End Distillation
    stage3_tokens: int = 2_400_000_000
    stage3_lr: float = 1e-5

    # Training dynamics
    gradient_accumulation_steps: int = 4
    optimizer: str = "adamw"
    checkpoint_dir: str = "checkpoints/"
```

### Subtasks (1/1 used)

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | MOHAWKDistiller | Implement 3-stage distillation training loop with loss functions |

---

## D-7: Evaluation Suite (Complexity: 13, Budget: 0)

**Applied**: Standard metric computation patterns

### Configuration (Python Dataclass)

```python
@dataclass
class EvaluationConfig:
    exponential_fit_r2_threshold: float = 0.95
    cross_domain_delta_threshold: float = 0.03
    selective_advantage_threshold: float = 0.5
    # Non-standard: MSE_selective / MSE_LTI < 0.5 means 2x improvement
    num_jacobian_samples: int = 100
```

### Subtasks (0/0 used)

No additional subtasks allocated (within D-7 breakdown).

---

## D-8: State Size Sweep (Complexity: 10, Budget: 0)

**Applied**: Sequential training protocol

### Configuration (Python Dataclass)

```python
@dataclass
class SweepConfig:
    state_sizes: List[int] = field(default_factory=lambda: [64, 128, 256, 512, 1024])
    parallel_training: bool = False
    save_checkpoints: bool = True
```

### Subtasks (0/0 used)

No additional subtasks allocated (within D-8 breakdown).

---

## D-9: Visualization Suite (Complexity: 9, Budget: 0)

**Applied**: Matplotlib/Seaborn plotting patterns

### Configuration (Python Dataclass)

```python
@dataclass
class VisualizationConfig:
    output_dir: str = "figures/"
    figure_format: str = "png"
    dpi: int = 300
    style: str = "seaborn-v0_8-darkgrid"
```

### Subtasks (0/0 used)

No additional subtasks allocated (within D-9 breakdown).

---

## D-10: Gate Validation (Complexity: 8, Budget: 0)

**Applied**: Boolean validation patterns

### Configuration (Python Dataclass)

```python
@dataclass
class GateConfig:
    w2_threshold: float = 0.05
    exponential_r2_threshold: float = 0.95
    cross_domain_threshold: float = 0.03
    selective_ratio_threshold: float = 0.5
    validation_report_path: str = "04_validation.md"
```

### Subtasks (0/0 used)

No additional subtasks allocated (within D-10 breakdown).

---

## Unified Configuration (Main Config Class)

```python
from dataclasses import dataclass, field
from typing import List, Optional
import torch

@dataclass
class DistillationConfig:
    """Unified configuration for h-m2 selective SSM adapter distillation experiment."""

    # Environment
    cuda_visible_devices: str = "0"
    use_fp16: bool = True
    hf_token: Optional[str] = None
    random_seed: int = 42

    # Model
    model_name: str = "meta-llama/Llama-2-7b-hf"
    target_layer: int = 28
    device: str = "cuda"
    dtype: torch.dtype = field(default=torch.float16)
    max_position_embeddings: int = 131072

    # Data
    dataset_name: str = "EleutherAI/pile"
    dataset_fallback: str = "allenai/c4"
    longbench_tasks: List[str] = field(default_factory=lambda: ["narrativeqa", "qasper", "hotpotqa", "multifieldqa_en"])
    batch_size: int = 8
    context_length: int = 4096
    streaming: bool = True
    num_eval_samples: int = 100

    # SSM Adapter
    d_model: int = 4096
    d_state: int = 512
    d_conv: int = 4
    expand: int = 2
    state_sizes_sweep: List[int] = field(default_factory=lambda: [64, 128, 256, 512, 1024])

    # MOHAWK Distillation
    stage1_tokens: int = 100_000_000
    stage1_lr: float = 1e-4
    stage2_tokens: int = 500_000_000
    stage2_lr: float = 5e-5
    lambda_jacobian: float = 0.1
    stage3_tokens: int = 2_400_000_000
    stage3_lr: float = 1e-5
    gradient_accumulation_steps: int = 4
    optimizer: str = "adamw"

    # Jacobian Analysis
    use_double_precision_jacobian: bool = True
    eigenvalue_clipping: bool = True
    clip_threshold: float = 1e-8
    num_jacobian_samples: int = 100

    # Evaluation
    exponential_fit_r2_threshold: float = 0.95
    cross_domain_delta_threshold: float = 0.03
    selective_advantage_threshold: float = 0.5

    # Gate Criteria
    w2_threshold: float = 0.05

    # Paths
    output_dir: str = "docs/youra_research/20260318_scope/h-m2"
    checkpoint_dir: str = "checkpoints/"
    figures_dir: str = "figures/"
    validation_report_path: str = "04_validation.md"

    # Visualization
    figure_format: str = "png"
    dpi: int = 300
    style: str = "seaborn-v0_8-darkgrid"


def load_config(config_path: Optional[str] = None) -> DistillationConfig:
    """Load configuration from file or environment variables."""
    import os

    config = DistillationConfig()

    # Override from environment variables
    if "HF_TOKEN" in os.environ:
        config.hf_token = os.environ["HF_TOKEN"]

    if "CUDA_VISIBLE_DEVICES" in os.environ:
        config.cuda_visible_devices = os.environ["CUDA_VISIBLE_DEVICES"]

    if "MODEL_NAME" in os.environ:
        config.model_name = os.environ["MODEL_NAME"]

    if "OUTPUT_DIR" in os.environ:
        config.output_dir = os.environ["OUTPUT_DIR"]

    return config
```

---

## Gate Validation Configuration

### MUST_WORK Gate Criteria

```python
GATE_CRITERIA = {
    "w2_jacobian": {
        "threshold": 0.05,
        "condition": "W2(eigenvals_teacher, eigenvals_student) < 0.05 at N=512",
        "gate_type": "MUST_WORK"
    },
    "exponential_decay": {
        "threshold": 0.95,
        "condition": "MSE(N) = a*exp(-b*N) with R² > 0.95",
        "gate_type": "MUST_WORK"
    },
    "cross_domain_stability": {
        "threshold": 0.03,
        "condition": "|Error(Pile) - Error(LongBench)| < 3%",
        "gate_type": "MUST_WORK"
    },
    "selective_advantage": {
        "threshold": 0.5,
        "condition": "MSE_selective / MSE_LTI < 0.5",
        "gate_type": "MUST_WORK"
    }
}
```

---

## Environment Setup Script

```bash
#!/bin/bash
# File: code/run_distillation.sh

# Check GPU availability
nvidia-smi

# Select empty GPU
echo "Available GPUs shown above. Select empty GPU ID:"
read GPU_ID
export CUDA_VISIBLE_DEVICES=$GPU_ID

# Set HuggingFace token
if [ -z "$HF_TOKEN" ]; then
    echo "Error: HF_TOKEN not set. Please set it via:"
    echo "  export HF_TOKEN=your_token_here"
    exit 1
fi

# Install dependencies
pip install mamba-ssm --no-build-isolation
pip install -r requirements.txt

# Run distillation experiment
python src/main.py
```

---

## Requirements

```txt
# File: code/requirements.txt

# Deep learning
torch>=2.1.0
transformers>=4.30.0
datasets>=2.12.0

# Mamba SSM (requires --no-build-isolation)
mamba-ssm>=2.3.1
causal-conv1d>=1.1.0

# Scientific computing
scipy>=1.10.0
numpy>=1.24.0

# Visualization
matplotlib>=3.5.0
seaborn>=0.12.0

# Utilities
pyyaml>=6.0
tqdm>=4.65.0
```

---

## Configuration Validation

```python
def validate_config(config: DistillationConfig) -> None:
    """Validate configuration before running experiment."""
    import torch
    import os

    # Validate model config
    assert config.target_layer >= 0, "target_layer must be non-negative"
    assert config.d_model > 0, "d_model must be positive"
    assert config.d_state > 0, "d_state must be positive"

    # Validate data config
    assert config.batch_size > 0, "batch_size must be positive"
    assert config.context_length > 0, "context_length must be positive"
    assert len(config.longbench_tasks) > 0, "longbench_tasks must not be empty"

    # Validate MOHAWK config
    assert config.stage1_tokens > 0, "stage1_tokens must be positive"
    assert config.stage2_tokens > 0, "stage2_tokens must be positive"
    assert config.stage3_tokens > 0, "stage3_tokens must be positive"
    assert config.gradient_accumulation_steps > 0, "gradient_accumulation_steps must be positive"

    # Validate gate thresholds
    assert 0.0 < config.w2_threshold < 1.0, "w2_threshold must be in (0, 1)"
    assert 0.0 < config.exponential_fit_r2_threshold <= 1.0, "R² threshold must be in (0, 1]"
    assert 0.0 < config.cross_domain_delta_threshold < 1.0, "cross_domain threshold must be in (0, 1)"
    assert 0.0 < config.selective_advantage_threshold < 1.0, "selective threshold must be in (0, 1)"

    # Check GPU availability
    assert torch.cuda.is_available(), "CUDA not available"

    # Check HF token
    if config.hf_token is None:
        print("Warning: HF_TOKEN not set. LLaMA model download may fail.")

    print("✓ Configuration validated")
    print(f"  Model: {config.model_name}")
    print(f"  Target layer: L{config.target_layer}")
    print(f"  SSM state size: {config.d_state}")
    print(f"  Training tokens: {config.stage1_tokens + config.stage2_tokens + config.stage3_tokens:,}")
    print(f"  GPU: {torch.cuda.get_device_name(0)}")
```

---

## Usage Example

```python
# In src/main.py
from config import load_config, validate_config
from data import DistillationDataModule
from model_loader import LLaMALayerExtractor
from adapter import SelectiveSSMAdapter, LTIControlAdapter
from distiller import MOHAWKDistiller
from jacobian import JacobianAnalyzer
from evaluate import DistillationEvaluator
from visualize import DistillationVisualizer

def main():
    # Load and validate configuration
    config = load_config()
    validate_config(config)

    # Setup components
    data_module = DistillationDataModule(config)
    model_loader = LLaMALayerExtractor(config)
    teacher_layer = model_loader.extract_layer(config.target_layer)

    # Run state size sweep
    results = {}
    for state_size in config.state_sizes_sweep:
        # Create student adapter
        student = SelectiveSSMAdapter(
            d_model=config.d_model,
            d_state=state_size,
            d_conv=config.d_conv,
            expand=config.expand
        )

        # Run MOHAWK distillation
        distiller = MOHAWKDistiller(teacher_layer, student, config)
        distiller.stage1_matrix_orientation(data_module.pile_loader, config.stage1_tokens)
        distiller.stage2_hidden_state_alignment(data_module.pile_loader, config.stage2_tokens, config.lambda_jacobian)
        distiller.stage3_end_to_end(data_module.pile_loader, config.stage3_tokens)

        # Evaluate
        jacobian_analyzer = JacobianAnalyzer(config)
        evaluator = DistillationEvaluator(teacher_layer, student, jacobian_analyzer)
        results[state_size] = evaluator.evaluate_all_metrics(data_module)

    # Validate gate criteria
    gate_pass = validate_gate_criteria(results, config)

    # Generate visualizations
    visualizer = DistillationVisualizer(config)
    visualizer.generate_all_figures(results)

    # Write validation report
    write_validation_report(results, gate_pass, config)

if __name__ == "__main__":
    main()
```

---

## Summary

**Total Subtasks Allocated**: 5/5

| Task | Complexity | Subtasks |
|------|------------|----------|
| D-1 | 6 | 1 |
| D-2 | 10 | 1 |
| D-3 | 8 | 1 |
| D-4 | 11 | 0 |
| D-5 | 12 | 0 |
| D-6 | 15 | 1 |
| D-7 | 13 | 0 |
| D-8 | 10 | 0 |
| D-9 | 9 | 0 |
| D-10 | 8 | 1 |

**Key Configuration Decisions:**

1. **State Size**: Primary N=512 for W2 < 0.05 criterion
2. **Training Tokens**: 3B total (100M + 500M + 2.4B) from MOHAWK paper
3. **Learning Rates**: Stage-specific decay (1e-4 → 5e-5 → 1e-5)
4. **Jacobian Precision**: FP64 for numerical stability
5. **Selective Advantage**: 2x improvement threshold (ratio < 0.5)

---

*Configuration designed for MECHANISM validation | MOHAWK distillation framework | Jacobian alignment testing*
