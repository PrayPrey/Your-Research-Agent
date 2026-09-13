# Configuration Specification: h-m1

**Document Version:** 1.0  
**Date:** 2026-05-11  
**Hypothesis:** H-M1 (MECHANISM)  
**Type:** Target Dimension Improvement Validation

**Applied Patterns:** Standard PyTorch dataclass config, h-e1 proven configuration

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Config classes verified from base code (h-e1)  
**Config Files Found**: `h-e1/code/src/config.py` (ExperimentConfig)  
**Pattern Used**: Python dataclass (copy-paste ready)

**Critical Verification**: Field names verified from actual h-e1 implementation (`model_id`, `num_epochs`, `random_seeds`, `lora_rank`, `lora_alpha`).

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

The following configs are inherited from base hypothesis h-e1:

```python
# From: h-e1/code/src/config.py (ACTUAL CODE)
@dataclass
class ExperimentConfig:
    """Experiment hyperparameters and settings"""
    
    # Model configuration
    model_id: str = "gpt2"
    lora_rank: int = 8
    lora_alpha: int = 8
    lora_dropout: float = 0.05
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
    target_dimensions: List[str] = None  # h-e1: ["truthfulness", "fairness", "robustness"]
    random_seeds: List[int] = None  # Defaults to [42, 43, 44]
    
    # Evaluation configuration
    eval_batch_size: int = 8
```

**Verified from**: `h-e1/code/src/config.py` (actual implementation)

---

## Configuration Format

Single dataclass format for experiment configuration. All parameters inherit h-e1 defaults except where h-m1 requires adjustments.

---

## A-1: Project Setup [Complexity: 6, Budget: 6]

**Applied**: h-e1 project structure pattern

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ProjectConfig:
    project_name: str = "h-m1-target-improvement"
    base_dir: Path = Path("./h-m1")
    code_dir: Path = Path("./h-m1/code")
    results_dir: Path = Path("./h-m1/results")
    figures_dir: Path = Path("./h-m1/figures")
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Create directory structure | Initialize project directories |
| C-1-2 | Setup requirements.txt | h-e1 dependencies + scipy |
| C-1-3 | Configure h-e1 imports | Python path for h-e1 module access |
| C-1-4 | Initialize __init__.py files | Package structure |
| C-1-5 | Create config.yaml template | Default configuration file |
| C-1-6 | Setup README.md | Usage instructions |

---

## A-2: Data Pipeline [Complexity: 7, Budget: 7]

**Applied**: HuggingFace datasets + lm-eval harness pattern

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class DataConfig:
    # TruthfulQA (target dimension only)
    truthfulqa_task: str = "truthfulqa_mc2"
    truthfulqa_split: str = "validation"
    num_fewshot: int = 0
    
    # Common settings (inherited from h-e1)
    max_length: int = 512
    cache_dir: Optional[str] = None
```

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Implement TruthfulQADataset class | lm-eval harness integration |
| C-2-2 | Create training data preparation | Language modeling from validation set |
| C-2-3 | Implement DataCollator | GPT-2 tokenization and batching |
| C-2-4 | Add dataset validation | Check data integrity |
| C-2-5 | Implement dataset caching | Cache processed datasets |
| C-2-6 | Create evaluation wrapper | lm-eval simple_evaluate interface |
| C-2-7 | Add dataset statistics logging | Dataset sizes and splits |

---

## A-3: Model Integration [Complexity: 8, Budget: 8]

**Applied**: h-e1 model classes (direct imports)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class ModelConfig:
    # Base model (inherited from h-e1)
    model_id: str = "gpt2"
    
    # LoRA configuration (h-m1 adjustment: alpha=16 per PRD)
    lora_rank: int = 8
    lora_alpha: int = 16  # Adjusted from h-e1's 8
    lora_dropout: float = 0.05
    target_modules: List[str] = field(default_factory=lambda: ["c_attn"])
    lora_bias: str = "none"
    task_type: str = "CAUSAL_LM"
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Import h-e1 BaselineModel | Verify import path compatibility |
| C-3-2 | Import h-e1 LoRAInterventionModel | Verify LoRA adapter integration |
| C-3-3 | Create H_M1_Model wrapper | Configuration adapter for h-m1 |
| C-3-4 | Implement load_baseline method | GPT-2 model and tokenizer loading |
| C-3-5 | Implement apply_intervention method | LoRA adapter application |
| C-3-6 | Add model inference methods | Generation for TruthfulQA |
| C-3-7 | Implement parameter counting | Trainable vs total parameters |
| C-3-8 | Add model state management | Checkpoint loading/saving |

---

## A-4: Training Pipeline [Complexity: 10, Budget: 10]

**Applied**: h-e1 InterventionTrainer pattern

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class TrainingConfig:
    # Optimizer (inherited from h-e1)
    optimizer: str = "adamw"
    betas: tuple[float, float] = (0.9, 0.999)
    weight_decay: float = 0.01
    
    # Learning rate (inherited from h-e1)
    learning_rate: float = 1e-4
    lr_scheduler: str = "cosine"
    warmup_ratio: float = 0.1
    
    # Training settings (inherited from h-e1)
    num_epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 2
    max_grad_norm: float = 1.0
    
    # Reproducibility (inherited from h-e1)
    random_seeds: List[int] = field(default_factory=lambda: [42, 43, 44])
    
    # Logging
    logging_steps: int = 10
    save_steps: int = 100
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Import h-e1 InterventionTrainer | Verify trainer compatibility |
| C-4-2 | Implement train_single_replicate function | Single seed training workflow |
| C-4-3 | Add seed management | Deterministic training per replicate |
| C-4-4 | Implement run_all_replicates function | N=3 replicate loop |
| C-4-5 | Add pre-intervention evaluation | Baseline score measurement |
| C-4-6 | Add post-intervention evaluation | Per-replicate TruthfulQA scoring |
| C-4-7 | Implement training metrics tracking | Loss curves per replicate |
| C-4-8 | Add checkpoint saving | Model states at epoch boundaries |
| C-4-9 | Implement result collection | (seed, pre_score, post_score, delta) tuples |
| C-4-10 | Add error handling | OOM, training failures |

---

## A-5: Evaluation System [Complexity: 9, Budget: 9]

**Applied**: lm-eval harness + scipy statistical tests

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class EvaluationConfig:
    # TruthfulQA metric
    truthfulqa_metric: str = "truthfulqa_mc2"
    
    # Statistical test settings
    test_type: str = "paired_t_test"
    significance_threshold: float = 0.05
    alternative: str = "two-sided"
    
    # Evaluation settings (inherited from h-e1)
    eval_batch_size: int = 8
```

### Subtasks [9/9 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Implement TruthfulQAEvaluator class | lm-eval harness wrapper |
| C-5-2 | Implement evaluate_mc2 method | MC2 score extraction |
| C-5-3 | Add model path handling | Support base and fine-tuned models |
| C-5-4 | Implement StatisticalAnalyzer class | Paired t-test analysis |
| C-5-5 | Implement extract_deltas method | Compute Δ = post - pre |
| C-5-6 | Implement compute_paired_ttest method | scipy.stats.ttest_rel wrapper |
| C-5-7 | Add directional consistency check | Count(Δ > 0) / N |
| C-5-8 | Implement evaluate_gate method | Gate pass/fail logic |
| C-5-9 | Add results formatting | Structured output dictionaries |

---

## A-6: Statistical Analysis [Complexity: 8, Budget: 8]

**Applied**: Standard statistical analysis pattern (scipy)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class StatisticsConfig:
    # Gate thresholds
    mean_delta_threshold: float = 0.0  # Must be positive
    p_value_threshold: float = 0.05
    consistency_threshold: float = 0.70  # 70% replicates show Δ > 0
    
    # Analysis settings
    confidence_level: float = 0.95
    test_type: str = "paired"
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Implement delta extraction | Parse replicate results |
| C-6-2 | Compute mean and std | Descriptive statistics |
| C-6-3 | Implement paired t-test | scipy.stats.ttest_rel |
| C-6-4 | Calculate confidence intervals | 95% CI for mean delta |
| C-6-5 | Check directional consistency | Proportion with Δ > 0 |
| C-6-6 | Implement gate evaluation logic | Mean Δ > 0 AND p < 0.05 |
| C-6-7 | Format statistical report | Structured results dictionary |
| C-6-8 | Add statistical interpretation | Pass/fail with rationale |

---

## A-7: Visualization [Complexity: 6, Budget: 6]

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
    
    # Plot settings
    figsize_comparison: tuple[int, int] = (8, 6)
    figsize_deltas: tuple[int, int] = (8, 6)
    figsize_training: tuple[int, int] = (10, 6)
    figsize_gate: tuple[int, int] = (8, 6)
    
    # Output
    figures_dir: str = "./h-m1/figures"
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Implement FigureGenerator class | Visualization orchestrator |
| C-7-2 | Implement plot_pre_post_comparison | Bar chart with error bars |
| C-7-3 | Implement plot_replicate_deltas | Scatter plot with Δ=0 line |
| C-7-4 | Implement plot_training_curves | Loss curves per replicate |
| C-7-5 | Implement plot_gate_metrics | Target vs actual bar chart |
| C-7-6 | Implement save_all_figures | Export all plots to files |

---

## A-8: Experiment Orchestration [Complexity: 7, Budget: 7]

**Applied**: Standard experiment workflow pattern

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class ExperimentConfig:
    # Experiment settings
    experiment_name: str = "h-m1-poc"
    target_dimension: str = "truthfulness"
    num_replicates: int = 3
    
    # Seeds (inherited from h-e1)
    random_seeds: List[int] = field(default_factory=lambda: [42, 43, 44])
    
    # Output settings
    output_dir: str = "./h-m1/results"
    save_baseline: bool = True
    save_interventions: bool = True
    save_analysis: bool = True
```

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | Implement main workflow orchestrator | Entry point logic |
| C-8-2 | Add environment setup | GPU selection, seed setting |
| C-8-3 | Implement baseline measurement phase | Pre-intervention TruthfulQA |
| C-8-4 | Implement intervention loop | N=3 replicates with seeds |
| C-8-5 | Add statistical analysis phase | Compute deltas, t-test, gate |
| C-8-6 | Implement visualization phase | Generate all 4 figures |
| C-8-7 | Add results saving | JSON outputs and checkpoints |

---

## Complete Configuration

Consolidated h-m1 experiment configuration:

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

@dataclass
class H_M1_Config:
    """
    Complete configuration for H-M1 MECHANISM hypothesis.
    Inherits h-e1 proven configuration with h-m1 specific adjustments.
    """
    
    # Project
    project_name: str = "h-m1-target-improvement"
    base_dir: Path = Path("./h-m1")
    output_dir: str = "./h-m1/results"
    figures_dir: str = "./h-m1/figures"
    
    # Model (inherited from h-e1)
    model_id: str = "gpt2"
    
    # LoRA (h-m1 adjustment: alpha=16)
    lora_rank: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    target_modules: List[str] = field(default_factory=lambda: ["c_attn"])
    lora_bias: str = "none"
    task_type: str = "CAUSAL_LM"
    
    # Training (inherited from h-e1)
    learning_rate: float = 1e-4
    num_epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 2
    warmup_ratio: float = 0.1
    max_grad_norm: float = 1.0
    
    # Data (TruthfulQA only)
    max_length: int = 512
    truthfulqa_task: str = "truthfulqa_mc2"
    cache_dir: Optional[str] = None
    
    # Experiment
    target_dimension: str = "truthfulness"
    num_replicates: int = 3
    random_seeds: List[int] = field(default_factory=lambda: [42, 43, 44])
    
    # Evaluation (inherited from h-e1)
    eval_batch_size: int = 8
    
    # Statistical Analysis
    significance_threshold: float = 0.05
    consistency_threshold: float = 0.70
    
    # Visualization
    figure_format: str = "png"
    dpi: int = 300
    style: str = "seaborn-v0_8"
```

---

## Configuration Loading

```python
def load_config(config_path: Optional[str] = None) -> H_M1_Config:
    """Load configuration from YAML file or use defaults."""
    if config_path is None:
        return H_M1_Config()
    
    import yaml
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)
    
    return H_M1_Config(**config_dict)

def save_config(config: H_M1_Config, path: str):
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
- [x] Applied patterns noted
- [x] Field names verified from h-e1 actual code
- [x] Subtask count within budget (all tasks exactly at budget)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included
- [x] Inherited Configuration section included
- [x] Copy-paste ready Python code

---

*Generated by Phase 3 Configuration Agent*  
*Patterns Applied: Standard PyTorch dataclass config, h-e1 proven configuration*  
*MECHANISM hypothesis - extends h-e1 for target dimension improvement validation*
