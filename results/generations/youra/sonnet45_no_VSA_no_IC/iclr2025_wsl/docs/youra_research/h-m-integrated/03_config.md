# Configuration Specification: h-m-integrated
## Hierarchical VAE for Cross-Architecture Model Zoo Analysis

**Hypothesis ID:** h-m-integrated  
**Type:** MECHANISM  
**Date:** 2026-08-20

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase (h-e1 as reference)  
**Status:** New config design with h-e1 dataclass pattern  
**Config Files Found:** `experiments/h-e1/src/config.py`  
**Pattern Used:** dataclass

---

## Configuration Structure

Applied: Standard PyTorch dataclass pattern from h-e1

```python
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import yaml

@dataclass
class DataConfig:
    cache_dir: str = "datasets/"
    zenodo_dois: List[str] = field(default_factory=lambda: [
        "10.5281/zenodo.6620868"
    ])
    sane_zoos: List[str] = field(default_factory=lambda: [
        "tune_zoo_cifar10_resnet18_kaiming_uniform",
        "tune_zoo_cifar100_resnet18_kaiming_uniform"
    ])
    train_split: float = 0.70
    val_split: float = 0.15
    test_split: float = 0.15
    phase1_pairs: int = 200
    normalization: str = "per_architecture_zscore"

@dataclass
class ModelConfig:
    latent_dim: int = 512
    hidden_dim: int = 512
    transformer_layers: int = 6
    transformer_heads: int = 8
    transformer_feedforward: int = 2048
    nfn_hidden_dim: int = 256
    dropout: float = 0.1

@dataclass
class TrainingConfig:
    epochs: int = 200
    batch_size: int = 32
    learning_rate: float = 1e-4
    weight_decay: float = 0.01
    gradient_clip: float = 1.0
    checkpoint_every: int = 10
    max_checkpoints: int = 5
    optimizer: str = "adamw"

@dataclass
class LossConfig:
    beta_kl_start: float = 1.0
    beta_kl_end: float = 0.1
    lambda_contrast: float = 0.5
    gamma_task: float = 0.1
    contrastive_margin: float = 0.3

@dataclass
class EvaluationConfig:
    cka_same_task_threshold: float = 0.6
    cka_diff_task_threshold: float = 0.4
    wcss_p_value_threshold: float = 0.01
    wcss_effect_size_threshold: float = 0.5
    reconstruction_accuracy_threshold: float = 0.70
    ablation_degradation_threshold: float = 0.15
    bootstrap_resamples: int = 100

@dataclass
class HardwareConfig:
    gpus: List[int] = field(default_factory=lambda: [0, 1])
    vram_per_gpu: int = 16
    storage_gb: int = 70
    mixed_precision: bool = True
    num_workers: int = 4

@dataclass
class ExperimentConfig:
    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    loss: LossConfig = field(default_factory=LossConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    hardware: HardwareConfig = field(default_factory=HardwareConfig)
    output_dir: str = "outputs/h-m-integrated"
    seed: int = 42

def load_config(path: str = "config.yaml") -> ExperimentConfig:
    with open(path) as f:
        data = yaml.safe_load(f)
    return ExperimentConfig(**data) if data else ExperimentConfig()
```

---

## Configuration Rationale

### Model Architecture
- **latent_dim=512**: From NVAE hierarchical VAE best practices
- **transformer_layers=6, heads=8**: Standard BERT-base configuration, sufficient for relational modeling
- **transformer_feedforward=2048**: 4x latent_dim per Vaswani et al. (Attention Is All You Need)

### Training
- **lr=1e-4**: AdamW default for VAE training
- **batch_size=32**: Fits 2x V100 16GB with gradient accumulation disabled
- **epochs=200**: NVAE convergence timeline, validated in experiment brief Section 4.2

### Loss Weighting
- **beta_kl anneal 1.0→0.1**: Prevents posterior collapse, linear schedule over epochs
- **lambda_contrast=0.5**: From HIT paper contrastive VAE experiments
- **gamma_task=0.1**: Weak supervision, task acts as auxiliary signal

### Evaluation Thresholds
All values from PRD Section 1.2 MUST_WORK gate criteria.

---

## YAML Configuration Template

```yaml
# config.yaml for h-m-integrated

data:
  cache_dir: "datasets/"
  train_split: 0.70
  val_split: 0.15
  test_split: 0.15
  phase1_pairs: 200

model:
  latent_dim: 512
  transformer_layers: 6
  transformer_heads: 8

training:
  epochs: 200
  batch_size: 32
  learning_rate: 0.0001
  gradient_clip: 1.0
  checkpoint_every: 10

loss:
  beta_kl_start: 1.0
  beta_kl_end: 0.1
  lambda_contrast: 0.5
  gamma_task: 0.1
  contrastive_margin: 0.3

evaluation:
  cka_same_task_threshold: 0.6
  cka_diff_task_threshold: 0.4
  wcss_p_value_threshold: 0.01
  wcss_effect_size_threshold: 0.5

hardware:
  gpus: [0, 1]
  vram_per_gpu: 16
  storage_gb: 70

output_dir: "outputs/h-m-integrated"
seed: 42
```

---

## Usage

```python
from config import load_config

# Load from YAML
config = load_config("config.yaml")

# Access nested configs
print(config.model.latent_dim)  # 512
print(config.training.learning_rate)  # 1e-4

# Compute beta_kl schedule
def get_beta_kl(epoch: int) -> float:
    progress = epoch / config.training.epochs
    return config.loss.beta_kl_start - (config.loss.beta_kl_start - config.loss.beta_kl_end) * progress
```

---

**Document Version:** 1.0  
**Last Updated:** 2026-08-20  
**Status:** APPROVED - Ready for Phase 4 Implementation
