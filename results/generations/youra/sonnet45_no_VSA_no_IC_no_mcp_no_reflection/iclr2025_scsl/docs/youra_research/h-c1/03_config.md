# Configuration Design: h-c1 Gradient-Aware Training

**Date:** 2026-08-29  
**Hypothesis:** h-c1 (CONDITION)  
**Author:** Configuration Agent  
**Budget:** 7 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Config verified from h-m1 code  
**Pattern Used:** YAML dict (not dataclass)

h-m1 uses flat YAML config loaded as dict. h-c1 adopts same pattern.

---

## Applied: YAML Dict Configuration Pattern

**Source:** h-m1 verified actual code (analyze_layers.py, data_loader.py)  
**Pattern:** Flat YAML config loaded with `yaml.safe_load()`, passed as dict  

---

## Configuration Schema

### config.yaml

```yaml
# h-c1 Gradient-Aware Training Configuration

experiment:
  name: "h-c1-gradient-aware-training"
  hypothesis_id: "h-c1"
  hypothesis_type: "CONDITION"
  prerequisite: "h-m1"

data:
  dataset_name: "Waterbirds"
  data_root: "./data/waterbirds"
  download: true
  batch_size: 128
  num_workers: 4
  image_size: 224
  # Augmentation
  horizontal_flip: true  # Train only

model:
  architecture: "resnet50"
  num_classes: 2
  pretrained: true  # ImageNet pretrained
  
optimizer:
  type: "sgd"
  lr: 0.001
  momentum: 0.9
  weight_decay: 0.0001
  
scheduler:
  type: "cosine"
  epochs: 300

training:
  epochs: 300
  log_interval: 10
  checkpoint_best: true  # Save best worst-group accuracy
  gradient_clip_norm: 1.0  # Stability
  lr_floor: 0.00001  # Minimum LR after modulation

gradient_aware:
  rho_j_source: "../h-m1/results/layer_rho_j.npy"  # h-m1 output
  update_interval: 10  # Re-compute ρ_j every N epochs
  modulation_formula: "lr * (1 - rho_j)"

jtt:
  stage1_epochs: 100
  stage2_epochs: 200
  upweight_factor: 10  # Upweight misclassified examples

evaluation:
  metrics:
    - "worst_group_accuracy"
    - "average_accuracy"
    - "per_group_accuracy"
  num_groups: 4

statistical_test:
  num_seeds: 10
  alpha: 0.05
  test_type: "paired_ttest"
  target_threshold: 0.86  # JTT baseline - 1%

output:
  output_folder: "./docs/youra_research/h-c1"
  checkpoint_folder: "./docs/youra_research/h-c1/checkpoints"
  figures_folder: "./docs/youra_research/h-c1/figures"
  validation_report: "04_validation.md"
  
  # Figure filenames
  gate_metrics_bar: "gate_metrics.png"
  lr_modulation_heatmap: "lr_modulation.png"
  training_curves: "training_curves.png"
  per_group_accuracy: "per_group_accuracy.png"

reproducibility:
  seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
  device: "cuda"
  cudnn_deterministic: true
```

---

## Inherited Configuration (Base Hypothesis)

### Verified from h-m1 Actual Code

**Data Loading Pattern** (from `data_loader.py`):
```python
# h-m1 uses dict config keys:
data_config['batch_size']
data_config['num_workers']
data_config['data_path']
data_config['download']
data_config['spurious_train_correlation']
data_config['spurious_test_correlation']
```

**Config Loading Pattern** (from `analyze_layers.py`):
```python
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Accessed as nested dict:
config['data']['batch_size']
config['model']['layer_names']
config['analysis']['alpha']
config['reproducibility']['seed']
```

**Training Config** (from `analyze_layers.py` training function):
```python
config['training']['lr']
config['training']['momentum']
config['training']['weight_decay']
config['training']['epochs']
```

**h-c1 Reuses:**
- `batch_size`: 128 (modified from h-m1's 256 for ResNet-50 memory)
- `num_workers`: 4
- `download`: true
- `device`: "cuda"
- `seed` pattern: Single seed for h-m1, multi-seed for h-c1

---

## Per-Task Configurations

### Epic 1: Waterbirds Dataset Setup (Complexity: 7)

**Config Section:** `data`

```yaml
data:
  dataset_name: "Waterbirds"
  data_root: "./data/waterbirds"
  download: true
  batch_size: 128
  num_workers: 4
  image_size: 224
  horizontal_flip: true
```

**Subtasks [2/7]:**
- C-1-1: Dataset download and group labels extraction
- C-1-2: Dataloader with transforms (Resize→CenterCrop→Normalize)

---

### Epic 2: ResNet-50 Baseline Model (Complexity: 5)

**Config Section:** `model`

```yaml
model:
  architecture: "resnet50"
  num_classes: 2
  pretrained: true
```

**Subtasks [1/7]:**
- C-2-1: Load torchvision ResNet-50, modify final layer

---

### Epic 3: ρ_j Loading from h-m1 (Complexity: 9)

**Config Section:** `gradient_aware`

```yaml
gradient_aware:
  rho_j_source: "../h-m1/results/layer_rho_j.npy"
  update_interval: 10
  modulation_formula: "lr * (1 - rho_j)"
```

**Subtasks [2/7]:**
- C-3-1: Load .npy file with h-m1 ρ_j values
- C-3-2: Map CMNIST layer names to ResNet-50 parameter names

**Risk:** ρ_j transfer from CMNIST to Waterbirds may fail. Fallback: Set uniform ρ_j=0.5.

---

### Epic 4: GradientAwareOptimizer (Complexity: 11)

**Config Section:** `optimizer`, `gradient_aware`

```yaml
optimizer:
  type: "sgd"
  lr: 0.001
  momentum: 0.9
  weight_decay: 0.0001

training:
  lr_floor: 0.00001
  gradient_clip_norm: 1.0
```

**Subtasks [2/7]:**
- C-4-1: Optimizer wrapper applying `lr_j = base_lr * (1 - ρ_j)`
- C-4-2: Unit test verifying per-parameter-group LR modulation

---

### Epic 5: JTT Baseline Implementation (Complexity: 12)

**Config Section:** `jtt`

```yaml
jtt:
  stage1_epochs: 100
  stage2_epochs: 200
  upweight_factor: 10
```

**Subtasks [0/7]:**
(No config-specific subtasks, uses `training` section)

---

### Epic 6: Training Pipeline (Complexity: 10)

**Config Section:** `training`, `evaluation`

```yaml
training:
  epochs: 300
  log_interval: 10
  checkpoint_best: true
  gradient_clip_norm: 1.0

evaluation:
  metrics:
    - "worst_group_accuracy"
    - "average_accuracy"
    - "per_group_accuracy"
  num_groups: 4
```

**Subtasks [0/7]:**
(Training loop uses configs from all sections)

---

### Epic 7: Statistical Validation (Complexity: 8)

**Config Section:** `statistical_test`

```yaml
statistical_test:
  num_seeds: 10
  alpha: 0.05
  test_type: "paired_ttest"
  target_threshold: 0.86
```

**Subtasks [0/7]:**
(Statistical test uses collected results from all seeds)

---

### Epic 8: Visualization and Reporting (Complexity: 9)

**Config Section:** `output`

```yaml
output:
  output_folder: "./docs/youra_research/h-c1"
  checkpoint_folder: "./docs/youra_research/h-c1/checkpoints"
  figures_folder: "./docs/youra_research/h-c1/figures"
  validation_report: "04_validation.md"
  
  gate_metrics_bar: "gate_metrics.png"
  lr_modulation_heatmap: "lr_modulation.png"
  training_curves: "training_curves.png"
  per_group_accuracy: "per_group_accuracy.png"
```

**Subtasks [0/7]:**
(Visualization uses collected results from training)

---

## Total Subtasks: 7/7 Allocated

| Epic | Subtasks |
|------|----------|
| Epic 1 | 2 |
| Epic 2 | 1 |
| Epic 3 | 2 |
| Epic 4 | 2 |
| Epic 5 | 0 |
| Epic 6 | 0 |
| Epic 7 | 0 |
| Epic 8 | 0 |
| **Total** | **7** |

---

## Configuration Loading Utility

```python
# config_loader.py
import yaml
from pathlib import Path

def load_config(config_path: str = "config.yaml") -> dict:
    """Load h-c1 configuration from YAML file."""
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config

def validate_config(config: dict) -> None:
    """Validate h-c1 configuration."""
    # Check h-m1 ρ_j file exists
    rho_j_path = Path(config['gradient_aware']['rho_j_source'])
    if not rho_j_path.exists():
        raise FileNotFoundError(f"h-m1 ρ_j file not found: {rho_j_path}")
    
    # Check seeds
    if len(config['reproducibility']['seeds']) != config['statistical_test']['num_seeds']:
        raise ValueError("Seed count mismatch")
    
    print("✓ Config validated")
```

---

## Environment Dependencies

```txt
torch>=2.0.0
torchvision>=0.15.0
numpy>=1.21.0
scipy>=1.7.0
matplotlib>=3.3.0
seaborn>=0.11.0
pandas>=1.3.0
pyyaml>=5.4
```

---

**Version:** 1.0  
**Status:** Ready for Complexity Assessment
