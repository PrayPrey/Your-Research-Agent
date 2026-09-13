# Configuration Specification: h-m4

**Document Version:** 1.0  
**Date:** 2026-05-11  
**Hypothesis:** H-M4 (MECHANISM)  
**Type:** Cross-Architecture Directional Replication Analysis

**Applied Patterns:** PyTorch dataclass pattern, Multi-model config, Statistical analysis configuration

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Config classes verified from h-m3 actual code  
**Config Files Found**: `h-m3/code/src/config_h_m3.py` (H_M3_Config)  
**Pattern Used**: Python dataclass (copy-paste ready)

**Critical Verification**: Field names verified from h-m3 actual implementation. H-M4 extends with multi-model family support (5 architectures), increased seeds (3→5), and directional replication analysis parameters.

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

The following configs are inherited from base hypothesis h-m3:

```python
# From: h-m3/code/src/config_h_m3.py (ACTUAL CODE)
@dataclass
class H_M3_Config:
    """Complete configuration for H-M3 MECHANISM hypothesis"""
    
    # Project
    project_name: str = "h-m3-cross-dimensional-correlation"
    output_dir: str = "./outputs"
    figures_dir: str = "./figures"
    activation_cache_dir: str = "./outputs/activations"
    
    # Model
    model_id: str = "gpt2"
    device: str = "cuda"
    
    # LoRA (verified from h-m2/h-m3)
    lora_rank: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.1
    target_modules: List[str] = field(default_factory=lambda: ["c_attn"])
    lora_bias: str = "none"
    task_type: str = "CAUSAL_LM"
    
    # Training
    learning_rate: float = 5e-5
    num_epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 2
    warmup_ratio: float = 0.1
    max_grad_norm: float = 1.0
    training_samples: int = 500
    
    # Data
    max_length: int = 512
    cache_dir: Optional[str] = None
    
    # Experiment
    num_replicates: int = 3
    random_seeds: List[int] = field(default_factory=lambda: [42, 43, 44])
    
    # Evaluation
    eval_batch_size: int = 8
    
    # Multi-Dimensional Evaluation
    dimensions: List[str] = field(default_factory=lambda: ["truthfulness", "fairness", "robustness"])
    eval_limit: Dict[str, Optional[int]] = field(default_factory=lambda: {
        "truthfulness": None,
        "fairness": None,
        "robustness": None
    })
    
    # Dataset Sources
    truthfulqa_dataset: str = "truthfulqa/truthful_qa"
    truthfulqa_split: str = "validation"
    truthfulqa_task: str = "generation"
    bbq_dataset: str = "lighteval/bbq_helm"
    bbq_split: str = "test"
    bbq_subset: str = "all"
    advglue_path: Optional[str] = None
    
    # Cross-Dimensional Correlation
    correlation_method: str = "pearson"
    significance_threshold: float = 0.05
    permutation_iterations: int = 1000
    
    # Visualization
    figure_format: str = "png"
    dpi: int = 300
    style: str = "seaborn-v0_8"
```

**Verified from**: `h-m3/code/src/config_h_m3.py` (actual implementation)

---

## Extended Configuration (H-M4)

### Complete H-M4 Configuration Class

```python
"""Configuration for H-M4 Experiment - Cross-Architecture Directional Replication"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict

@dataclass
class H_M4_Config:
    """
    Complete configuration for H-M4 MECHANISM hypothesis.
    Extends h-m3 with multi-model family support and directional replication analysis.
    """
    
    # Project
    project_name: str = "h-m4-cross-architecture-replication"
    output_dir: str = "./outputs"
    figures_dir: str = "./figures"
    
    # Multi-Model Family Configuration (NEW for h-m4)
    model_families: List[str] = field(default_factory=lambda: [
        "llama", "mistral", "qwen", "mamba", "falcon"
    ])
    model_ids: Dict[str, str] = field(default_factory=lambda: {
        "llama": "meta-llama/Llama-3.2-1B",
        "mistral": "mistralai/Mistral-7B-v0.1",
        "qwen": "Qwen/Qwen-1.8B",
        "mamba": "state-spaces/mamba-1.4b",
        "falcon": "tiiuae/falcon-7b"
    })
    device: str = "cuda"
    
    # LoRA Configuration (inherited from h-m3)
    lora_rank: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    lora_bias: str = "none"
    task_type: str = "CAUSAL_LM"
    
    # Family-Specific Target Modules (NEW for h-m4)
    target_modules_map: Dict[str, List[str]] = field(default_factory=lambda: {
        "llama": ["q_proj", "k_proj", "v_proj", "o_proj"],
        "mistral": ["q_proj", "k_proj", "v_proj", "o_proj"],
        "qwen": ["c_attn"],
        "mamba": ["in_proj", "out_proj"],
        "falcon": ["query_key_value", "dense"]
    })
    
    # Training (inherited from h-m3)
    learning_rate: float = 2e-4
    num_epochs: int = 3
    batch_size: int = 8
    gradient_accumulation_steps: int = 2
    warmup_ratio: float = 0.1
    max_grad_norm: float = 1.0
    training_samples: int = 500
    
    # Data (inherited from h-m3)
    max_length: int = 512
    cache_dir: Optional[str] = None
    
    # Experiment (INCREASED seeds from 3 to 5)
    n_seeds: int = 5
    seeds: List[int] = field(default_factory=lambda: [42, 43, 44, 45, 46])
    
    # Evaluation (inherited from h-m3)
    eval_batch_size: int = 8
    
    # Multi-Dimensional Evaluation (inherited from h-m3)
    dimensions: List[str] = field(default_factory=lambda: ["truthfulness", "fairness", "robustness"])
    
    # Dataset Sources (inherited from h-m3, replaced AdvGLUE with ANLI)
    truthfulqa_dataset: str = "truthfulqa/truthful_qa"
    truthfulqa_split: str = "validation"
    bbq_dataset: str = "lighteval/bbq_helm"
    bbq_split: str = "test"
    anli_dataset: str = "facebook/anli"
    anli_split: str = "test_r3"
    
    # Directional Replication Analysis (NEW for h-m4)
    correlation_threshold: float = 0.3
    replication_threshold: float = 0.6
    correlation_method: str = "pearson"
    significance_threshold: float = 0.05
    
    # Visualization (inherited from h-m3)
    figure_format: str = "png"
    dpi: int = 300
    style: str = "seaborn-v0_8"

def get_default_config() -> H_M4_Config:
    """Get default h-m4 configuration"""
    return H_M4_Config()

def get_model_families() -> List[str]:
    """Get default model families for cross-architecture analysis"""
    return ["llama", "mistral", "qwen", "mamba", "falcon"]

def get_target_modules(model_family: str) -> List[str]:
    """Get LoRA target modules for specific model family"""
    target_modules_map = {
        "llama": ["q_proj", "k_proj", "v_proj", "o_proj"],
        "mistral": ["q_proj", "k_proj", "v_proj", "o_proj"],
        "qwen": ["c_attn"],
        "mamba": ["in_proj", "out_proj"],
        "falcon": ["query_key_value", "dense"]
    }
    return target_modules_map.get(model_family, ["q_proj", "v_proj"])
```

---

## Key Configuration Changes from H-M3

| Parameter | H-M3 Value | H-M4 Value | Rationale |
|-----------|------------|------------|-----------|
| `model_id` | "gpt2" | Dict of 5 families | Multi-architecture support |
| `model_families` | N/A | ["llama", "mistral", "qwen", "mamba", "falcon"] | 5-model cross-architecture |
| `target_modules` | ["c_attn"] | Dict per family | Architecture-specific LoRA |
| `n_seeds` | 3 | 5 | Statistical power |
| `seeds` | [42, 43, 44] | [42, 43, 44, 45, 46] | 5 replicates |
| `lora_dropout` | 0.1 | 0.05 | Standard LoRA value |
| `learning_rate` | 5e-5 | 2e-4 | Standard LoRA fine-tuning |
| `batch_size` | 4 | 8 | Larger models support |
| `correlation_threshold` | N/A | 0.3 | Direction classification |
| `replication_threshold` | N/A | 0.6 | Gate criterion (≥3/5) |
| `anli_dataset` | advglue_path | "facebook/anli" | Better HuggingFace support |

**Unchanged (Controlled Comparison):**
- LoRA architecture: r=8, α=16
- Training protocol: 3 epochs, gradient_accumulation_steps=2
- Dimensions: ["truthfulness", "fairness", "robustness"]
- Evaluation: Full benchmark datasets
- Statistical method: Pearson correlation

---

## YAML Configuration Template

```yaml
# H-M4 Experiment Configuration
project_name: h-m4-cross-architecture-replication
output_dir: ./outputs
figures_dir: ./figures

# Multi-Model Family Configuration
model_families:
  - llama
  - mistral
  - qwen
  - mamba
  - falcon

model_ids:
  llama: meta-llama/Llama-3.2-1B
  mistral: mistralai/Mistral-7B-v0.1
  qwen: Qwen/Qwen-1.8B
  mamba: state-spaces/mamba-1.4b
  falcon: tiiuae/falcon-7b

device: cuda

# LoRA Configuration
lora_rank: 8
lora_alpha: 16
lora_dropout: 0.05

# Family-Specific Target Modules
target_modules_map:
  llama: [q_proj, k_proj, v_proj, o_proj]
  mistral: [q_proj, k_proj, v_proj, o_proj]
  qwen: [c_attn]
  mamba: [in_proj, out_proj]
  falcon: [query_key_value, dense]

# Training
learning_rate: 2.0e-4
num_epochs: 3
batch_size: 8
gradient_accumulation_steps: 2
training_samples: 500

# Data
max_length: 512

# Experiment (5 seeds for statistical power)
n_seeds: 5
seeds: [42, 43, 44, 45, 46]

# Multi-Dimensional Evaluation
dimensions:
  - truthfulness
  - fairness
  - robustness

# Dataset Sources
truthfulqa_dataset: truthfulqa/truthful_qa
truthfulqa_split: validation
bbq_dataset: lighteval/bbq_helm
bbq_split: test
anli_dataset: facebook/anli
anli_split: test_r3

# Directional Replication Analysis
correlation_threshold: 0.3
replication_threshold: 0.6
correlation_method: pearson
significance_threshold: 0.05

# Visualization
figure_format: png
dpi: 300
```

---

## Configuration Loading Utilities

```python
from pathlib import Path
import yaml

def load_config(config_path: Optional[str] = None) -> H_M4_Config:
    """Load configuration from YAML file or use defaults."""
    if config_path is None:
        return H_M4_Config()
    
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)
    
    return H_M4_Config(**config_dict)

def save_config(config: H_M4_Config, path: str):
    """Save configuration to YAML file."""
    from dataclasses import asdict
    
    with open(path, 'w') as f:
        yaml.dump(asdict(config), f, default_flow_style=False)

def validate_config(config: H_M4_Config) -> bool:
    """Validate configuration parameters."""
    assert len(config.model_families) == 5, "Must have exactly 5 model families"
    assert len(config.seeds) == config.n_seeds, "Seeds must match n_seeds"
    assert config.n_seeds == 5, "Must have 5 seeds for statistical power"
    assert config.training_samples > 0, "Training samples must be positive"
    assert config.replication_threshold == 0.6, "Replication threshold must be 0.6 (3/5)"
    assert len(config.dimensions) == 3, "Must have exactly 3 dimensions"
    return True
```

---

## Validation Checklist

- [x] Single format only (dataclass)
- [x] No ASCII diagrams
- [x] Applied patterns noted (1 line)
- [x] Field names verified from h-m3 actual code
- [x] Subtask count within budget (2 subtasks allocated, 0 used - Epic tasks predefined)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included
- [x] Inherited Configuration section with verified field names
- [x] Copy-paste ready Python code

---

*Generated by Phase 3 Configuration Agent*  
*Patterns Applied: PyTorch dataclass pattern, Multi-model config, Statistical analysis configuration*  
*MECHANISM hypothesis - extends h-m3 to validate cross-architecture directional replication*
