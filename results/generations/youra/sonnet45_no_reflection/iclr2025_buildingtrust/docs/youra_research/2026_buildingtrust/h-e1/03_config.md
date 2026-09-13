# Configuration Specification: h-e1

**Document Version:** 1.0  
**Date:** 2026-05-11  
**Hypothesis:** H-E1 (EXISTENCE)  
**Type:** Proof-of-Concept  

**Applied Patterns:** Standard PyTorch dataclass config, HuggingFace transformers defaults

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation from scratch  
**Config Files Found**: None - new config design  
**Pattern Used**: Python dataclass (copy-paste ready)

---

## Configuration Format

Single dataclass format for experiment configuration. All parameters have defaults from research.

---

## A-1: Project Setup [Complexity: 5, Budget: 5]

**Applied**: Standard Python package structure

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ProjectConfig:
    project_name: str = "h-e1-trustworthiness"
    base_dir: Path = Path("./h-e1")
    code_dir: Path = Path("./h-e1/code")
    results_dir: Path = Path("./h-e1/results")
    figures_dir: Path = Path("./h-e1/figures")
    cache_dir: Path = Path("./h-e1/cache")
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Create directory structure | Initialize all project directories |
| C-1-2 | Setup requirements.txt | Define Python dependencies |
| C-1-3 | Initialize __init__.py files | Create package structure |
| C-1-4 | Create config.yaml template | YAML config file for experiments |
| C-1-5 | Setup README.md | Basic setup and usage instructions |

---

## A-2: Data Loading [Complexity: 8, Budget: 8]

**Applied**: HuggingFace datasets standard loading pattern

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class DataConfig:
    # TruthfulQA (Truthfulness dimension)
    truthfulqa_variant: str = "multiple_choice"
    truthfulqa_split: str = "validation"
    
    # BBQ (Fairness dimension)
    bbq_dataset: str = "heegyu/bbq"
    bbq_categories: list[str] = field(default_factory=lambda: [
        "Age", "Disability_status", "Gender_identity", "Nationality",
        "Physical_appearance", "Race_ethnicity", "Religion", "SES", "Sexual_orientation"
    ])
    bbq_split: str = "test"
    
    # AdvGLUE (Robustness dimension)
    advglue_tasks: list[str] = field(default_factory=lambda: ["adv_sst2", "adv_mnli", "adv_qnli"])
    advglue_split: str = "validation"
    
    # Common settings
    max_seq_length: int = 512
    cache_dir: Optional[str] = None
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Implement TruthfulQA loader | Load MC1/MC2/Gen variants |
| C-2-2 | Implement BBQ loader | Load 9 demographic categories |
| C-2-3 | Implement AdvGLUE loader | Load 5 adversarial tasks |
| C-2-4 | Create TrustworthinessDataset class | Unified dataset interface |
| C-2-5 | Implement DataCollator | Tokenization and batching |
| C-2-6 | Add dataset validation | Check data integrity |
| C-2-7 | Implement dataset caching | Cache processed datasets |
| C-2-8 | Create dataset statistics | Log dataset sizes and splits |

---

## A-3: Model Implementation [Complexity: 10, Budget: 10]

**Applied**: HuggingFace transformers + PEFT LoRA pattern

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class ModelConfig:
    # Base model
    model_id: str = "meta-llama/Meta-Llama-3-8B"
    torch_dtype: str = "bfloat16"
    device_map: str = "auto"
    
    # LoRA configuration (from HuggingFace PEFT docs)
    lora_r: int = 16
    lora_alpha: int = 16
    lora_target_modules: list[str] = field(default_factory=lambda: ["q_proj", "v_proj"])
    lora_dropout: float = 0.05
    lora_bias: str = "none"
    task_type: str = "CAUSAL_LM"
    
    # Memory optimization
    gradient_checkpointing: bool = True
    use_cache: bool = False
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Implement BaselineModel class | Load Llama-3-8B and tokenizer |
| C-3-2 | Implement model loading | AutoModelForCausalLM.from_pretrained |
| C-3-3 | Implement tokenizer loading | AutoTokenizer.from_pretrained |
| C-3-4 | Create LoRAInterventionModel class | LoRA adapter configuration |
| C-3-5 | Implement LoRA application | get_peft_model integration |
| C-3-6 | Add trainable parameters extraction | Filter requires_grad parameters |
| C-3-7 | Implement model inference | Generation methods for benchmarks |
| C-3-8 | Add gradient checkpointing | Memory optimization |
| C-3-9 | Implement parameter counting | Track trainable vs total params |
| C-3-10 | Create model state saving | Checkpoint management |

---

## A-4: Training Pipeline [Complexity: 9, Budget: 9]

**Applied**: Standard PyTorch training loop + HuggingFace transformers

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class TrainingConfig:
    # Optimizer (from research - standard AdamW for LLMs)
    optimizer: str = "adamw"
    betas: tuple[float, float] = (0.9, 0.999)
    weight_decay: float = 0.01
    
    # Learning rate (varied across replicates)
    learning_rate: float = 5e-5
    lr_scheduler: str = "cosine"
    warmup_steps: int = 100
    
    # Training settings
    epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 4
    max_grad_norm: float = 1.0
    
    # Logging
    logging_steps: int = 10
    eval_steps: int = 50
    save_steps: int = 100
    
    # Reproducibility
    seed: int = 42
```

### Subtasks [9/9 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Implement InterventionTrainer class | Main training orchestrator |
| C-4-2 | Setup optimizer | AdamW with specified hyperparameters |
| C-4-3 | Setup learning rate scheduler | Cosine with warmup |
| C-4-4 | Implement training epoch loop | Single epoch training logic |
| C-4-5 | Add gradient accumulation | Effective batch size handling |
| C-4-6 | Implement loss computation | Cross-entropy causal LM loss |
| C-4-7 | Add gradient clipping | Prevent exploding gradients |
| C-4-8 | Implement checkpoint saving | Save model states during training |
| C-4-9 | Create train_single_replicate function | Full intervention training workflow |

---

## A-5: Evaluation System [Complexity: 11, Budget: 11]

**Applied**: Official benchmark evaluation protocols

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class EvaluationConfig:
    # TruthfulQA metrics
    truthfulqa_metrics: list[str] = field(default_factory=lambda: ["mc1", "mc2"])
    
    # BBQ metrics
    bbq_metrics: list[str] = field(default_factory=lambda: ["bias_score", "disambiguation_accuracy"])
    
    # AdvGLUE metrics
    advglue_metrics: list[str] = field(default_factory=lambda: ["adversarial_accuracy"])
    
    # Correlation analysis
    correlation_method: str = "pearson"
    significance_threshold: float = 0.01
    
    # Evaluation settings
    eval_batch_size: int = 8
    num_samples: int = None  # None = use full dataset
```

### Subtasks [11/11 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Implement TruthfulQAEvaluator class | MC1 and MC2 metrics |
| C-5-2 | Implement compute_mc1 | Best answer log-probability |
| C-5-3 | Implement compute_mc2 | Normalized probability for true answers |
| C-5-4 | Implement BBQEvaluator class | Bias and disambiguation metrics |
| C-5-5 | Implement compute_bias_score | Stereotype-aligned vs conflicting |
| C-5-6 | Implement compute_disambiguation_accuracy | Performance on informative contexts |
| C-5-7 | Implement AdvGLUEEvaluator class | Adversarial accuracy metrics |
| C-5-8 | Implement compute_adversarial_accuracy | Per-task accuracy computation |
| C-5-9 | Implement CorrelationAnalyzer class | Cross-dimensional correlation |
| C-5-10 | Implement extract_delta_scores | Compute post-intervention deltas |
| C-5-11 | Implement compute_pearson_correlation | Pearson rho and p-values |

---

## A-6: Experiment Orchestration [Complexity: 7, Budget: 7]

**Applied**: Standard experiment workflow pattern

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field

@dataclass
class ExperimentConfig:
    # Experiment settings
    experiment_name: str = "h-e1-poc"
    target_dimension: str = "truthfulness"
    n_replicates: int = 3
    
    # Hyperparameter perturbations (varied across replicates)
    lora_ranks: list[int] = field(default_factory=lambda: [8, 16, 32])
    learning_rates: list[float] = field(default_factory=lambda: [1e-5, 5e-5, 1e-4])
    epochs_list: list[int] = field(default_factory=lambda: [1, 3, 5])
    
    # Output settings
    output_dir: str = "./results"
    save_baseline: bool = True
    save_interventions: bool = True
    save_correlations: bool = True
```

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Implement main workflow orchestrator | Entry point logic |
| C-6-2 | Implement baseline measurement phase | Evaluate base model on all benchmarks |
| C-6-3 | Implement intervention loop | Run N replicates with perturbations |
| C-6-4 | Add hyperparameter sampling | Generate perturbation configurations |
| C-6-5 | Implement results aggregation | Collect all replicate scores |
| C-6-6 | Add correlation computation | Compute cross-dimensional correlations |
| C-6-7 | Implement results saving | Save JSON outputs |

---

## A-7: Visualization [Complexity: 6, Budget: 6]

**Applied**: Standard matplotlib/seaborn visualization patterns

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class VisualizationConfig:
    # Figure settings
    figure_format: str = "png"
    dpi: int = 300
    style: str = "seaborn-v0_8"
    
    # Plot settings
    colormap: str = "coolwarm"
    figsize_heatmap: tuple[int, int] = (10, 8)
    figsize_scatter: tuple[int, int] = (15, 5)
    figsize_histogram: tuple[int, int] = (12, 4)
    
    # Output
    save_figures: bool = True
    figures_dir: str = "./figures"
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Implement FigureGenerator class | Visualization orchestrator |
| C-7-2 | Implement plot_correlation_heatmap | 3x3 correlation matrix |
| C-7-3 | Implement plot_scatter_grid | Dimension pair scatter plots |
| C-7-4 | Implement plot_delta_distributions | Delta score histograms |
| C-7-5 | Implement plot_intervention_effects | Mean delta bar chart |
| C-7-6 | Implement plot_significance_map | p<0.01 binary heatmap |

---

## Complete Configuration

For reference, here is the consolidated experiment configuration:

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

@dataclass
class H_E1_Config:
    """
    Complete configuration for H-E1 EXISTENCE hypothesis.
    Minimal PoC configuration with fixed defaults from research.
    """
    
    # Project
    project_name: str = "h-e1-trustworthiness"
    base_dir: Path = Path("./h-e1")
    output_dir: str = "./h-e1/results"
    figures_dir: str = "./h-e1/figures"
    cache_dir: Optional[str] = "./h-e1/cache"
    
    # Model
    model_id: str = "meta-llama/Meta-Llama-3-8B"
    torch_dtype: str = "bfloat16"
    device_map: str = "auto"
    gradient_checkpointing: bool = True
    
    # LoRA
    lora_r: int = 16
    lora_alpha: int = 16
    lora_target_modules: list[str] = field(default_factory=lambda: ["q_proj", "v_proj"])
    lora_dropout: float = 0.05
    
    # Training
    learning_rate: float = 5e-5
    epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 4
    warmup_steps: int = 100
    weight_decay: float = 0.01
    max_grad_norm: float = 1.0
    
    # Data
    max_seq_length: int = 512
    truthfulqa_variant: str = "multiple_choice"
    bbq_dataset: str = "heegyu/bbq"
    advglue_tasks: list[str] = field(default_factory=lambda: ["adv_sst2", "adv_mnli", "adv_qnli"])
    
    # Experiment
    target_dimension: str = "truthfulness"
    n_replicates: int = 3
    lora_ranks: list[int] = field(default_factory=lambda: [8, 16, 32])
    learning_rates: list[float] = field(default_factory=lambda: [1e-5, 5e-5, 1e-4])
    epochs_list: list[int] = field(default_factory=lambda: [1, 3, 5])
    seed: int = 42
    
    # Evaluation
    eval_batch_size: int = 8
    correlation_method: str = "pearson"
    significance_threshold: float = 0.01
    
    # Visualization
    figure_format: str = "png"
    dpi: int = 300
    colormap: str = "coolwarm"
```

---

## Configuration Loading

```python
def load_config(config_path: Optional[str] = None) -> H_E1_Config:
    """Load configuration from YAML file or use defaults."""
    if config_path is None:
        return H_E1_Config()
    
    import yaml
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)
    
    return H_E1_Config(**config_dict)

def save_config(config: H_E1_Config, path: str):
    """Save configuration to YAML file."""
    import yaml
    from dataclasses import asdict
    
    with open(path, 'w') as f:
        yaml.dump(asdict(config), f, default_flow_style=False)
```

---

## Validation Checklist

- [x] Single format only (dataclass)
- [x] No ASCII diagrams
- [x] Applied patterns noted (1 line each)
- [x] Defaults from research (HuggingFace docs, TrustLLM paper)
- [x] Subtask count within budget (all tasks exactly at budget)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included
- [x] Green-field project noted
- [x] Copy-paste ready Python code

---

*Generated by Phase 3 Configuration Agent*  
*Patterns Applied: Standard PyTorch dataclass config, HuggingFace transformers defaults*  
*EXISTENCE hypothesis - minimal configuration for proof-of-concept validation*
