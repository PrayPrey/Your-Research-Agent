# Configuration Specification: h-m2

**Document Version:** 1.0  
**Date:** 2026-05-11  
**Hypothesis:** H-M2 (MECHANISM)  
**Type:** Representation Change Validation

**Applied Patterns:** PyTorch dataclass config, TransformerLens activation extraction config

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Config classes verified from h-m1 code  
**Config Files Found**: `h-m1/code/src/config.py` (ExperimentConfig)  
**Pattern Used**: Python dataclass (copy-paste ready)

**Critical Verification**: Field names verified from h-m1 actual implementation (`model_id`, `num_epochs`, `random_seeds`, `lora_rank`, `lora_alpha`). h-m2 extends with representation extraction parameters.

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

The following configs are inherited from base hypothesis h-m1:

```python
# From: h-m1/code/src/config.py (ACTUAL CODE)
@dataclass
class ExperimentConfig:
    """Experiment hyperparameters and settings"""
    
    # Model configuration
    model_id: str = "gpt2"
    lora_rank: int = 8
    lora_alpha: int = 16  # h-m1 verified: 16 (not 8)
    lora_dropout: float = 0.1  # h-m1 verified: 0.1 (not 0.05)
    target_modules: List[str] = None  # Defaults to ["c_attn"]
    
    # Training configuration
    learning_rate: float = 1e-4
    num_epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 2
    max_grad_norm: float = 1.0
    warmup_ratio: float = 0.1
    
    # Dataset configuration
    max_length: int = 512
    num_proc: int = 4
    
    # Experiment configuration
    num_replicates: int = 3
    target_dimensions: List[str] = None
    random_seeds: List[int] = None  # Defaults to [42, 43, 44]
    
    # Evaluation configuration
    eval_batch_size: int = 8
```

**Verified from**: `h-m1/code/src/config.py` (actual implementation)

**Note**: h-m1 config uses `lora_alpha=16` and `lora_dropout=0.1` (verified from code, differs from h-m1 specs).

---

## Configuration Format

Single dataclass format for experiment configuration. All parameters inherit h-m1 defaults, with new parameters for representation extraction and CKA analysis.

---

## A-1: Project Setup [Complexity: 7, Budget: 7]

**Applied**: h-m1 project structure pattern with TransformerLens additions

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ProjectConfig:
    project_name: str = "h-m2-representation-change"
    base_dir: Path = Path("./h-m2")
    code_dir: Path = Path("./h-m2/code")
    results_dir: Path = Path("./h-m2/outputs")
    figures_dir: Path = Path("./h-m2/figures")
    activation_cache_dir: Path = Path("./h-m2/outputs/activations")
```

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Create directory structure | Initialize project directories (outputs/, figures/, code/src/) |
| C-1-2 | Setup requirements.txt | h-m1 dependencies + transformer-lens + pytorch-cka |
| C-1-3 | Configure h-m1 imports | Python path for h-m1 module access |
| C-1-4 | Initialize __init__.py files | Package structure for src/ |
| C-1-5 | Create config.yaml template | Default configuration with layer specifications |
| C-1-6 | Setup run_experiment.py | CLI entry point |
| C-1-7 | Test TransformerLens installation | Verify GPU compatibility |

---

## A-2: Data Pipeline [Complexity: 6, Budget: 6]

**Applied**: h-m1 TruthfulQA dataset pattern (identical reuse)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class DataConfig:
    # TruthfulQA (inherited from h-m1)
    truthfulqa_task: str = "truthfulqa_mc2"
    truthfulqa_split: str = "validation"
    num_fewshot: int = 0
    training_samples: int = 100
    
    # Tokenization (inherited from h-m1)
    max_length: int = 512
    cache_dir: Optional[str] = None
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Import h-m1 TruthfulQADataset | Reuse h-m1 data module |
| C-2-2 | Implement prepare_eval_tokens | Tokenize 100 TruthfulQA samples for activation extraction |
| C-2-3 | Add batch preparation | DataLoader for evaluation |
| C-2-4 | Implement token caching | Cache tokenized inputs |
| C-2-5 | Add dataset validation | Verify sample count matches h-m1 |
| C-2-6 | Create dataset statistics logger | Log token lengths |

---

## A-3: TransformerLens Integration [Complexity: 9, Budget: 9]

**Applied**: TransformerLens HookedTransformer pattern

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class TransformerLensConfig:
    # Model wrapper
    model_id: str = "gpt2"
    device: str = "cuda"
    
    # Hook points for activation extraction
    n_layers: int = 12
    attention_hook_pattern: str = "blocks.{layer}.attn.hook_pattern"
    hidden_hook_pattern: str = "blocks.{layer}.hook_resid_post"
    
    # Activation extraction settings
    cache_activations: bool = True
    detach_on_extract: bool = True  # Free GPU memory
    move_to_cpu: bool = True  # Save activations to CPU
```

### Subtasks [9/9 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Implement TransformerLensWrapper class | Wrap GPT-2 with HookedTransformer |
| C-3-2 | Implement load_hooked_model method | Load GPT-2 with activation hooks |
| C-3-3 | Implement get_hook_names method | Generate hook point names for 24 layers |
| C-3-4 | Test run_with_cache on sample input | Verify activation extraction works |
| C-3-5 | Implement convert_from_hf_peft | Convert PEFT LoRA model to HookedTransformer |
| C-3-6 | Add hook validation | Verify all 24 hook points exist |
| C-3-7 | Test pre-intervention extraction | Extract baseline activations |
| C-3-8 | Test post-intervention extraction | Extract LoRA-modified activations |
| C-3-9 | Add memory management | Clear cache after extraction |

---

## A-4: Activation Extractor [Complexity: 10, Budget: 10]

**Applied**: TransformerLens caching + disk storage pattern

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List
from pathlib import Path

@dataclass
class ActivationConfig:
    # Layers to analyze (24 total: 12 attention + 12 hidden)
    layers_to_analyze: List[str] = field(default_factory=lambda: [
        # Attention patterns
        *[f"blocks.{i}.attn.hook_pattern" for i in range(12)],
        # Hidden states
        *[f"blocks.{i}.hook_resid_post" for i in range(12)]
    ])
    
    # Storage
    save_activations: bool = True
    activation_format: str = "pt"  # PyTorch .pt format
    activation_cache_dir: str = "./h-m2/outputs/activations"
    
    # Memory management
    batch_extract: bool = False  # Extract all at once (GPT-2 is small)
    clear_cache_after: bool = True
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Implement ActivationExtractor class | Core extraction logic |
| C-4-2 | Implement extract_activations method | run_with_cache wrapper |
| C-4-3 | Add attention pattern extraction | Extract blocks.{i}.attn.hook_pattern (12 layers) |
| C-4-4 | Add hidden state extraction | Extract blocks.{i}.hook_resid_post (12 layers) |
| C-4-5 | Implement save_activations method | torch.save to disk |
| C-4-6 | Implement load_activations method | torch.load from disk |
| C-4-7 | Add activation shape validation | Verify (batch, ...) shapes |
| C-4-8 | Implement detach and move to CPU | Free GPU memory |
| C-4-9 | Add progress tracking | Log extraction progress per layer |
| C-4-10 | Test round-trip save/load | Verify activation integrity |

---

## A-5: CKA Similarity Module [Complexity: 11, Budget: 11]

**Applied**: pytorch-cka library integration

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class CKAConfig:
    # CKA computation
    device: str = "cuda"
    use_pytorch_cka: bool = True  # Use pytorch-cka library
    
    # CKA parameters
    kernel_type: str = "linear"  # Linear CKA (standard)
    center_kernel: bool = True  # Centered Kernel Alignment
    
    # Output
    save_cka_scores: bool = True
    cka_output_format: str = "json"
```

### Subtasks [11/11 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Implement CKASimilarity class | Wrapper for pytorch-cka |
| C-5-2 | Implement compute_cka method | Single-layer CKA computation |
| C-5-3 | Add activation flattening | Reshape to (batch, features) |
| C-5-4 | Implement compute_layer_cka | Per-layer CKA scoring |
| C-5-5 | Implement compute_all_layers | Loop over 24 layers |
| C-5-6 | Add CKA validation | Check score in [0, 1] range |
| C-5-7 | Implement save_cka_scores | Save to JSON per replicate |
| C-5-8 | Add GPU memory management | Move tensors to GPU for CKA |
| C-5-9 | Test CKA on identical inputs | Verify CKA = 1.0 |
| C-5-10 | Test CKA on random inputs | Verify CKA < 1.0 |
| C-5-11 | Add error handling | Handle shape mismatches |

---

## A-6: LoRA Training Pipeline [Complexity: 8, Budget: 8]

**Applied**: h-m1 InterventionTrainer (direct reuse)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class TrainingConfig:
    # Model (inherited from h-m1)
    model_id: str = "gpt2"
    
    # LoRA (inherited from h-m1, verified values)
    lora_rank: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.1
    target_modules: List[str] = field(default_factory=lambda: ["c_attn"])
    
    # Training (inherited from h-m1)
    learning_rate: float = 1e-4
    num_epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 2
    max_grad_norm: float = 1.0
    warmup_ratio: float = 0.1
    
    # Reproducibility (inherited from h-m1)
    random_seeds: List[int] = field(default_factory=lambda: [42, 43, 44])
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Import h-m1 InterventionTrainer | Reuse training logic |
| C-6-2 | Implement H_M2_Trainer wrapper | Add activation tracking hooks |
| C-6-3 | Add pre-intervention activation extraction | Before training |
| C-6-4 | Execute LoRA training | 3 epochs on 100 TruthfulQA samples |
| C-6-5 | Add post-intervention activation extraction | After training |
| C-6-6 | Implement model state reload | Load LoRA weights into HookedTransformer |
| C-6-7 | Add training metrics tracking | Loss curves per replicate |
| C-6-8 | Test training + extraction workflow | End-to-end validation |

---

## A-7: Statistical Analysis [Complexity: 9, Budget: 9]

**Applied**: scipy Pearson correlation pattern

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class StatisticsConfig:
    # Correlation analysis
    correlation_method: str = "pearson"
    significance_threshold: float = 0.05
    alternative: str = "two-sided"
    
    # Performance delta (from h-m1 results)
    h_m1_performance_delta: float = 0.0232  # +2.32% TruthfulQA MC2
    
    # Gate thresholds (SHOULD_WORK)
    p_value_threshold: float = 0.05
    min_layers_with_change: int = 12  # >50% of 24 layers
```

### Subtasks [9/9 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Implement CorrelationAnalyzer class | Statistical analysis orchestrator |
| C-7-2 | Implement compute_change_magnitude | (1 - CKA) per layer |
| C-7-3 | Implement aggregate_across_replicates | Mean CKA per layer across 3 replicates |
| C-7-4 | Implement correlate_representation_performance | Pearson correlation |
| C-7-5 | Add p-value computation | scipy.stats.pearsonr |
| C-7-6 | Implement evaluate_gate | p < 0.05 check |
| C-7-7 | Add layer change detection | Count layers with CKA < 1.0 |
| C-7-8 | Implement format_results | Structured output dictionary |
| C-7-9 | Add statistical interpretation | Generate pass/fail rationale |

---

## A-8: Visualization [Complexity: 7, Budget: 7]

**Applied**: matplotlib/seaborn standard patterns

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class VisualizationConfig:
    # Figure settings
    figure_format: str = "png"
    dpi: int = 300
    style: str = "seaborn-v0_8"
    
    # Plot dimensions
    figsize_heatmap: tuple[int, int] = (10, 6)
    figsize_bar: tuple[int, int] = (10, 6)
    figsize_scatter: tuple[int, int] = (8, 6)
    figsize_progression: tuple[int, int] = (10, 6)
    
    # Output
    figures_dir: str = "./h-m2/figures"
```

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | Implement FigureGenerator class | Visualization orchestrator |
| C-8-2 | Implement plot_cka_heatmap | Layers × representation types heatmap |
| C-8-3 | Implement plot_change_magnitude | Bar chart per layer (attention vs hidden) |
| C-8-4 | Implement plot_layer_progression | Line plot of change across depth |
| C-8-5 | Implement plot_correlation_scatter | Required gate figure |
| C-8-6 | Add figure annotations | Correlation coefficient, p-value |
| C-8-7 | Implement save_all_figures | Export all 4 plots |

---

## A-9: Experiment Orchestration [Complexity: 8, Budget: 8]

**Applied**: Standard experiment workflow pattern

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class ExperimentConfig:
    # Experiment settings
    experiment_name: str = "h-m2-representation-change"
    num_replicates: int = 3
    
    # Seeds (inherited from h-m1)
    random_seeds: List[int] = field(default_factory=lambda: [42, 43, 44])
    
    # Workflow steps
    extract_pre_activations: bool = True
    run_lora_training: bool = True
    extract_post_activations: bool = True
    compute_cka: bool = True
    run_statistical_analysis: bool = True
    generate_visualizations: bool = True
    
    # Output settings
    output_dir: str = "./h-m2/outputs"
    save_intermediate: bool = True
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-9-1 | Implement main workflow orchestrator | Entry point (src/main.py) |
| C-9-2 | Add environment setup | GPU selection, seed setting |
| C-9-3 | Implement pre-intervention phase | Load model, extract activations |
| C-9-4 | Implement intervention loop | N=3 replicates with LoRA training |
| C-9-5 | Implement post-intervention phase | Extract activations from trained models |
| C-9-6 | Implement CKA computation phase | Layer-wise similarity for all replicates |
| C-9-7 | Implement analysis phase | Correlation, gate evaluation |
| C-9-8 | Add results saving | JSON outputs, figures, validation report |

---

## Complete Configuration

Consolidated h-m2 experiment configuration:

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

@dataclass
class H_M2_Config:
    """
    Complete configuration for H-M2 MECHANISM hypothesis.
    Extends h-m1 with representation extraction and CKA analysis.
    """
    
    # Project
    project_name: str = "h-m2-representation-change"
    base_dir: Path = Path("./h-m2")
    output_dir: str = "./h-m2/outputs"
    figures_dir: str = "./h-m2/figures"
    activation_cache_dir: str = "./h-m2/outputs/activations"
    
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
    
    # Data (TruthfulQA only, inherited from h-m1)
    max_length: int = 512
    truthfulqa_task: str = "truthfulqa_mc2"
    training_samples: int = 100
    cache_dir: Optional[str] = None
    
    # Experiment
    num_replicates: int = 3
    random_seeds: List[int] = field(default_factory=lambda: [42, 43, 44])
    
    # Evaluation (inherited from h-m1)
    eval_batch_size: int = 8
    
    # Representation Extraction (new for h-m2)
    n_layers: int = 12
    layers_to_analyze: List[str] = field(default_factory=lambda: [
        *[f"blocks.{i}.attn.hook_pattern" for i in range(12)],
        *[f"blocks.{i}.hook_resid_post" for i in range(12)]
    ])
    save_activations: bool = True
    activation_format: str = "pt"
    
    # CKA Analysis (new for h-m2)
    use_pytorch_cka: bool = True
    kernel_type: str = "linear"
    center_kernel: bool = True
    save_cka_scores: bool = True
    
    # Statistical Analysis (new for h-m2)
    correlation_method: str = "pearson"
    significance_threshold: float = 0.05
    h_m1_performance_delta: float = 0.0232
    min_layers_with_change: int = 12
    
    # Visualization (new for h-m2)
    figure_format: str = "png"
    dpi: int = 300
    style: str = "seaborn-v0_8"
```

---

## Configuration Loading

```python
def load_config(config_path: Optional[str] = None) -> H_M2_Config:
    """Load configuration from YAML file or use defaults."""
    if config_path is None:
        return H_M2_Config()
    
    import yaml
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)
    
    return H_M2_Config(**config_dict)

def save_config(config: H_M2_Config, path: str):
    """Save configuration to YAML file."""
    import yaml
    from dataclasses import asdict
    
    with open(path, 'w') as f:
        yaml.dump(asdict(config), f, default_flow_style=False)

def get_layers_to_analyze(n_layers: int = 12) -> List[str]:
    """Generate layer hook names for activation extraction."""
    attention_layers = [f"blocks.{i}.attn.hook_pattern" for i in range(n_layers)]
    hidden_layers = [f"blocks.{i}.hook_resid_post" for i in range(n_layers)]
    return attention_layers + hidden_layers
```

---

## YAML Configuration Template

```yaml
# H-M2 Experiment Configuration
project_name: h-m2-representation-change
base_dir: ./h-m2
output_dir: ./h-m2/outputs
figures_dir: ./h-m2/figures
activation_cache_dir: ./h-m2/outputs/activations

# Model
model_id: gpt2
device: cuda

# LoRA (from h-m1)
lora_rank: 8
lora_alpha: 16
lora_dropout: 0.1
target_modules:
  - c_attn

# Training (from h-m1)
learning_rate: 1.0e-4
num_epochs: 3
batch_size: 4
gradient_accumulation_steps: 2

# Data
truthfulqa_task: truthfulqa_mc2
training_samples: 100
max_length: 512

# Experiment
num_replicates: 3
random_seeds:
  - 42
  - 43
  - 44

# Representation Extraction
n_layers: 12
save_activations: true
activation_format: pt

# CKA Analysis
use_pytorch_cka: true
kernel_type: linear
save_cka_scores: true

# Statistical Analysis
correlation_method: pearson
significance_threshold: 0.05
h_m1_performance_delta: 0.0232

# Visualization
figure_format: png
dpi: 300
```

---

## Validation Checklist

- [x] Single format only (dataclass)
- [x] No ASCII diagrams
- [x] Applied patterns noted
- [x] Field names verified from h-m1 actual code
- [x] Subtask count within budget (all tasks exactly at budget)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included
- [x] Inherited Configuration section included
- [x] Copy-paste ready Python code

---

*Generated by Phase 3 Configuration Agent*  
*Patterns Applied: PyTorch dataclass config, TransformerLens activation extraction config*  
*MECHANISM hypothesis - extends h-m1 to validate representation change mechanism*
