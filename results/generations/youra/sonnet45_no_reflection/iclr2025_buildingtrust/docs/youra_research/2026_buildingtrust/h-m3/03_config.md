# Configuration Specification: h-m3

**Document Version:** 1.0  
**Date:** 2026-05-11  
**Hypothesis:** H-M3 (MECHANISM)  
**Type:** Cross-Dimensional Correlation Analysis

**Applied Patterns:** Multi-task evaluation config, PyTorch dataclass pattern, Statistical analysis configuration

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Config classes verified from h-m2 actual code  
**Config Files Found**: `h-m2/code/src/config.py` (H_M2_Config)  
**Pattern Used**: Python dataclass (copy-paste ready)

**Critical Verification**: Field names verified from h-m2 actual implementation. H-M3 extends with multi-dimensional evaluation parameters (dimensions list, eval limits, permutation test settings).

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

The following configs are inherited from base hypothesis h-m2:

```python
# From: h-m2/code/src/config.py (ACTUAL CODE)
@dataclass
class H_M2_Config:
    """Complete configuration for H-M2 MECHANISM hypothesis"""
    
    # Project
    project_name: str = "h-m2-representation-change"
    output_dir: str = "./outputs"
    figures_dir: str = "./figures"
    activation_cache_dir: str = "./outputs/activations"
    
    # Model (inherited from h-m1)
    model_id: str = "gpt2"
    device: str = "cuda"
    
    # LoRA (inherited from h-m1, verified values)
    lora_rank: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.1
    target_modules: List[str] = field(default_factory=lambda: ["c_attn"])
    lora_bias: str = "none"
    task_type: str = "CAUSAL_LM"
    
    # Training (inherited from h-m1)
    learning_rate: float = 1e-4
    num_epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 2
    warmup_ratio: float = 0.1
    max_grad_norm: float = 1.0
    
    # Data (TruthfulQA only)
    max_length: int = 512
    truthfulqa_task: str = "truthfulqa_mc2"
    training_samples: int = 100
    cache_dir: Optional[str] = None
    
    # Experiment
    num_replicates: int = 3
    random_seeds: List[int] = field(default_factory=lambda: [42, 43, 44])
    
    # Evaluation
    eval_batch_size: int = 8
    
    # Representation Extraction
    n_layers: int = 12
    layers_to_analyze: List[str] = field(default_factory=list)
    save_activations: bool = True
    activation_format: str = "pt"
    
    # CKA Analysis
    use_pytorch_cka: bool = True
    kernel_type: str = "linear"
    center_kernel: bool = True
    save_cka_scores: bool = True
    
    # Statistical Analysis
    correlation_method: str = "pearson"
    significance_threshold: float = 0.05
    h_m1_performance_delta: float = 0.0232
    min_layers_with_change: int = 12
    
    # Visualization
    figure_format: str = "png"
    dpi: int = 300
    style: str = "seaborn-v0_8"
```

**Verified from**: `h-m2/code/src/config.py` (actual implementation)

---

## Extended Configuration (H-M3)

### Complete H-M3 Configuration Class

```python
"""Configuration for H-M3 Experiment"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict

@dataclass
class H_M3_Config:
    """
    Complete configuration for H-M3 MECHANISM hypothesis.
    Extends h-m2 with multi-dimensional evaluation and cross-dimensional correlation.
    """
    
    # Project
    project_name: str = "h-m3-cross-dimensional-correlation"
    output_dir: str = "./outputs"
    figures_dir: str = "./figures"
    activation_cache_dir: str = "./outputs/activations"
    
    # Model (inherited from h-m2)
    model_id: str = "gpt2"
    device: str = "cuda"
    
    # LoRA (inherited from h-m2 - proven values)
    lora_rank: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.1
    target_modules: List[str] = field(default_factory=lambda: ["c_attn"])
    lora_bias: str = "none"
    task_type: str = "CAUSAL_LM"
    
    # Training (inherited from h-m2, increased sample size)
    learning_rate: float = 5e-5
    num_epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 2
    warmup_ratio: float = 0.1
    max_grad_norm: float = 1.0
    training_samples: int = 500  # Increased from h-m2's 100
    
    # Data (tokenization settings inherited from h-m2)
    max_length: int = 512
    cache_dir: Optional[str] = None
    
    # Experiment (inherited from h-m2)
    num_replicates: int = 3
    random_seeds: List[int] = field(default_factory=lambda: [42, 43, 44])
    
    # Evaluation (inherited from h-m2)
    eval_batch_size: int = 8
    
    # Representation Extraction (inherited from h-m2)
    n_layers: int = 12
    layers_to_analyze: List[str] = field(default_factory=list)
    save_activations: bool = True
    activation_format: str = "pt"
    
    # CKA Analysis (inherited from h-m2)
    use_pytorch_cka: bool = True
    kernel_type: str = "linear"
    center_kernel: bool = True
    save_cka_scores: bool = True
    
    # Multi-Dimensional Evaluation (NEW for h-m3)
    dimensions: List[str] = field(default_factory=lambda: ["truthfulness", "fairness", "robustness"])
    eval_limit: Dict[str, Optional[int]] = field(default_factory=lambda: {
        "truthfulness": None,  # Full TruthfulQA validation set (817)
        "fairness": None,      # Full BBQ test split (500+)
        "robustness": None     # Full AdvGLUE standard splits
    })
    
    # Dataset Sources (NEW for h-m3)
    truthfulqa_dataset: str = "truthfulqa/truthful_qa"
    truthfulqa_split: str = "validation"
    truthfulqa_task: str = "generation"
    bbq_dataset: str = "lighteval/bbq_helm"
    bbq_split: str = "test"
    bbq_subset: str = "all"
    advglue_path: Optional[str] = None  # Path to downloaded AdvGLUE benchmark
    
    # Cross-Dimensional Correlation (NEW for h-m3)
    correlation_method: str = "pearson"
    significance_threshold: float = 0.05
    permutation_iterations: int = 1000
    
    # Statistical Analysis (inherited from h-m2)
    min_layers_with_change: int = 12
    
    # Visualization (inherited from h-m2)
    figure_format: str = "png"
    dpi: int = 300
    style: str = "seaborn-v0_8"
    
    def __post_init__(self):
        """Generate layer names for GPT-2 (12 layers) if not provided."""
        if not self.layers_to_analyze:
            self.layers_to_analyze = []
            # Attention patterns: blocks.{i}.attn.hook_pattern
            for i in range(12):
                self.layers_to_analyze.append(f"blocks.{i}.attn.hook_pattern")
            # Hidden states: blocks.{i}.hook_resid_post
            for i in range(12):
                self.layers_to_analyze.append(f"blocks.{i}.hook_resid_post")

def get_default_config() -> H_M3_Config:
    """Get default h-m3 configuration"""
    return H_M3_Config()

def get_default_dimensions() -> List[str]:
    """Get default trustworthiness dimensions"""
    return ["truthfulness", "fairness", "robustness"]
```

---

## Per-Task Configuration

### A-1: Project Setup [Complexity: 7, Budget: 0]

**Applied**: h-m2 project structure with multi-dimensional extensions

```python
@dataclass
class ProjectConfig:
    project_name: str = "h-m3-cross-dimensional-correlation"
    base_dir: str = "./h-m3"
    code_dir: str = "./h-m3/code"
    output_dir: str = "./h-m3/outputs"
    figures_dir: str = "./h-m3/figures"
    activation_cache_dir: str = "./h-m3/outputs/activations"
```

---

### A-2: Multi-Dimensional Data Pipeline [Complexity: 10, Budget: 0]

**Applied**: HuggingFace datasets pattern for multi-benchmark loading

```python
@dataclass
class MultiDimensionalDataConfig:
    # TruthfulQA (Target Dimension - inherited from h-m2)
    truthfulqa_dataset: str = "truthfulqa/truthful_qa"
    truthfulqa_split: str = "validation"
    truthfulqa_task: str = "generation"
    truthfulqa_training_samples: int = 500
    
    # BBQ (Fairness/Bias Dimension)
    bbq_dataset: str = "lighteval/bbq_helm"
    bbq_split: str = "test"
    bbq_subset: str = "all"
    
    # AdvGLUE (Robustness Dimension)
    advglue_path: Optional[str] = None  # Downloaded benchmark path
    advglue_tasks: List[str] = field(default_factory=lambda: ["sst2", "mnli", "qnli", "qqp", "rte"])
    
    # Tokenization (inherited from h-m2)
    max_length: int = 512
    cache_dir: Optional[str] = None
```

---

### A-3: BBQ Evaluator [Complexity: 9, Budget: 0]

**Applied**: HuggingFace lm-eval pattern for bias evaluation

```python
@dataclass
class BBQEvaluatorConfig:
    dataset: str = "lighteval/bbq_helm"
    split: str = "test"
    subset: str = "all"
    batch_size: int = 8
    # BBQ uses accuracy on bias detection
    metric: str = "accuracy"
```

---

### A-4: AdvGLUE Evaluator [Complexity: 10, Budget: 0]

**Applied**: Custom benchmark wrapper pattern

```python
@dataclass
class AdvGLUEEvaluatorConfig:
    benchmark_path: Optional[str] = None
    tasks: List[str] = field(default_factory=lambda: ["sst2", "mnli", "qnli", "qqp", "rte"])
    batch_size: int = 8
    # AdvGLUE uses robustness score (accuracy on adversarial examples)
    metric: str = "robustness_accuracy"
```

---

### A-5: Multi-Dimensional Orchestrator [Complexity: 8, Budget: 0]

**Applied**: Multi-task evaluation orchestration pattern

```python
@dataclass
class MultiDimensionalOrchestratorConfig:
    dimensions: List[str] = field(default_factory=lambda: ["truthfulness", "fairness", "robustness"])
    eval_limit: Dict[str, Optional[int]] = field(default_factory=lambda: {
        "truthfulness": None,  # Full validation set
        "fairness": None,
        "robustness": None
    })
    parallel_evaluation: bool = False  # Sequential to avoid memory issues
    batch_size: int = 8
```

---

### A-6: Cross-Dimensional Correlation Analyzer [Complexity: 9, Budget: 0]

**Applied**: scipy statistical analysis pattern

```python
@dataclass
class CorrelationAnalyzerConfig:
    correlation_method: str = "pearson"  # scipy.stats.pearsonr
    significance_threshold: float = 0.05
    alternative: str = "two-sided"
    # Dimension pairs to analyze
    dimension_pairs: List[tuple[str, str]] = field(default_factory=lambda: [
        ("truthfulness", "fairness"),
        ("truthfulness", "robustness"),
        ("fairness", "robustness")
    ])
```

---

### A-7: Permutation Test [Complexity: 10, Budget: 0]

**Applied**: Bootstrap permutation testing pattern

```python
@dataclass
class PermutationTestConfig:
    n_permutations: int = 1000
    random_seed: int = 42
    # Compare observed correlation to null distribution
    alternative: str = "two-sided"
    confidence_level: float = 0.95
```

---

### A-8: Layer-Wise Correlation [Complexity: 11, Budget: 0]

**Applied**: Layer-specific representation analysis pattern

```python
@dataclass
class LayerWiseCorrelationConfig:
    layers_to_analyze: List[str] = field(default_factory=list)  # 24 layers from __post_init__
    dimensions: List[str] = field(default_factory=lambda: ["truthfulness", "fairness", "robustness"])
    correlation_method: str = "pearson"
    significance_threshold: float = 0.05
    # Output: 24 layers × 3 dimensions correlation matrix
```

---

### A-9: Training Pipeline Extension [Complexity: 7, Budget: 0]

**Applied**: h-m2 LoRA training with increased sample size

```python
@dataclass
class TrainingConfig:
    # LoRA (inherited from h-m2 - proven values)
    lora_rank: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.1
    target_modules: List[str] = field(default_factory=lambda: ["c_attn"])
    
    # Training (inherited from h-m2)
    learning_rate: float = 5e-5
    num_epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 2
    warmup_ratio: float = 0.1
    max_grad_norm: float = 1.0
    
    # Training samples - INCREASED from h-m2's 100 for better coverage
    training_samples: int = 500
    
    # Seeds (inherited from h-m2)
    random_seeds: List[int] = field(default_factory=lambda: [42, 43, 44])
```

---

### A-10: Visualization Suite [Complexity: 9, Budget: 0]

**Applied**: matplotlib/seaborn multi-panel figure pattern

```python
@dataclass
class VisualizationConfig:
    # Figure settings (inherited from h-m2)
    figure_format: str = "png"
    dpi: int = 300
    style: str = "seaborn-v0_8"
    
    # Plot dimensions
    figsize_correlation_scatter: tuple[int, int] = (15, 5)  # 3 panels
    figsize_correlation_matrix: tuple[int, int] = (8, 6)
    figsize_layer_heatmap: tuple[int, int] = (12, 8)
    figsize_performance_bars: tuple[int, int] = (10, 6)
    figsize_permutation: tuple[int, int] = (8, 6)
    
    # Output directory
    figures_dir: str = "./h-m3/figures"
```

---

### A-11: Experiment Orchestration [Complexity: 10, Budget: 0]

**Applied**: Multi-stage experiment workflow pattern

```python
@dataclass
class ExperimentConfig:
    experiment_name: str = "h-m3-cross-dimensional-correlation"
    num_replicates: int = 3
    random_seeds: List[int] = field(default_factory=lambda: [42, 43, 44])
    
    # Workflow stages
    stages: List[str] = field(default_factory=lambda: [
        "load_datasets",
        "pre_intervention_eval",
        "extract_pre_activations",
        "train_lora",
        "post_intervention_eval",
        "extract_post_activations",
        "compute_cka",
        "correlation_analysis",
        "permutation_tests",
        "layer_wise_correlation",
        "generate_visualizations"
    ])
    
    # Output settings
    output_dir: str = "./h-m3/outputs"
    save_intermediate: bool = True
```

---

## YAML Configuration Template

```yaml
# H-M3 Experiment Configuration
project_name: h-m3-cross-dimensional-correlation
output_dir: ./h-m3/outputs
figures_dir: ./h-m3/figures
activation_cache_dir: ./h-m3/outputs/activations

# Model (inherited from h-m2)
model_id: gpt2
device: cuda

# LoRA (inherited from h-m2 - proven values)
lora_rank: 8
lora_alpha: 16
lora_dropout: 0.1
target_modules:
  - c_attn

# Training (inherited from h-m2, increased samples)
learning_rate: 5.0e-5
num_epochs: 3
batch_size: 4
gradient_accumulation_steps: 2
training_samples: 500  # Increased from h-m2's 100

# Data
max_length: 512

# Multi-Dimensional Evaluation (NEW for h-m3)
dimensions:
  - truthfulness
  - fairness
  - robustness

# Dataset Sources
truthfulqa_dataset: truthfulqa/truthful_qa
truthfulqa_split: validation
truthfulqa_task: generation
bbq_dataset: lighteval/bbq_helm
bbq_split: test
bbq_subset: all
advglue_path: null  # Set to downloaded benchmark path

# Experiment
num_replicates: 3
random_seeds:
  - 42
  - 43
  - 44

# Representation Extraction (inherited from h-m2)
n_layers: 12
save_activations: true
activation_format: pt

# CKA Analysis (inherited from h-m2)
use_pytorch_cka: true
kernel_type: linear
save_cka_scores: true

# Cross-Dimensional Correlation (NEW for h-m3)
correlation_method: pearson
significance_threshold: 0.05
permutation_iterations: 1000

# Visualization
figure_format: png
dpi: 300
```

---

## Configuration Loading Utilities

```python
from pathlib import Path
import yaml

def load_config(config_path: Optional[str] = None) -> H_M3_Config:
    """Load configuration from YAML file or use defaults."""
    if config_path is None:
        return H_M3_Config()
    
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)
    
    return H_M3_Config(**config_dict)

def save_config(config: H_M3_Config, path: str):
    """Save configuration to YAML file."""
    from dataclasses import asdict
    
    with open(path, 'w') as f:
        yaml.dump(asdict(config), f, default_flow_style=False)

def validate_config(config: H_M3_Config) -> bool:
    """Validate configuration parameters."""
    assert len(config.dimensions) == 3, "Must have exactly 3 dimensions"
    assert len(config.random_seeds) == config.num_replicates, "Seeds must match replicates"
    assert config.training_samples > 0, "Training samples must be positive"
    assert config.permutation_iterations >= 1000, "Permutation iterations should be >= 1000"
    assert len(config.layers_to_analyze) == 24, "Must analyze 24 layers (12 attn + 12 hidden)"
    return True
```

---

## Key Configuration Changes from H-M2

| Parameter | H-M2 Value | H-M3 Value | Rationale |
|-----------|------------|------------|-----------|
| `training_samples` | 100 | 500 | Better representation coverage |
| `learning_rate` | 1e-4 | 5e-5 | Standard LoRA fine-tuning rate |
| `dimensions` | N/A | ["truthfulness", "fairness", "robustness"] | Multi-dimensional evaluation |
| `permutation_iterations` | N/A | 1000 | Statistical robustness for null distribution |
| `eval_limit` | N/A | None (full datasets) | Use full benchmark splits |

**Unchanged (Controlled Comparison):**
- LoRA parameters: r=8, α=16, dropout=0.1
- Training protocol: 3 epochs, batch_size=4
- Seeds: [42, 43, 44]
- Model: GPT-2 (124M)
- Representation analysis: 24 layers, CKA similarity

---

## Validation Checklist

- [x] Single format only (dataclass)
- [x] No ASCII diagrams
- [x] Applied patterns noted (1 line each)
- [x] Field names verified from h-m2 actual code
- [x] Subtask count within budget (0 subtasks - Epic tasks predefined)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included
- [x] Inherited Configuration section with verified field names
- [x] Copy-paste ready Python code

---

*Generated by Phase 3 Configuration Agent*  
*Patterns Applied: Multi-task evaluation config, PyTorch dataclass pattern, Statistical analysis configuration*  
*MECHANISM hypothesis - extends h-m2 to validate cross-dimensional correlation propagation*
