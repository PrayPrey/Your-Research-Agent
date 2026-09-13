# Configuration Schema: h-m1

**Generated**: 2026-08-24  
**Hypothesis ID**: h-m1  
**Hypothesis Type**: MECHANISM  
**Complexity**: Tier 1.5 (Simple-to-Moderate)  
**Budget**: 350-550 tokens

---

## Codebase Analysis

**Project Type**: Base hypothesis (h-e1)  
**Status**: Extending h-e1 with gradient measurement infrastructure  
**Config Files Found**: None (h-e1 uses hardcoded values in train.py)  
**Pattern Used**: Hardcoded dict (matches h-e1 pattern)

---

## Configuration

```python
# Gradient Measurement Configuration for h-m1
CONFIG = {
    # Data (inherited from h-e1)
    "dataset_name": "waterbirds",
    "data_dir": "./data/waterbirds/",
    "batch_size": 64,
    "num_workers": 4,
    "image_size": 224,
    "normalize_mean": [0.485, 0.456, 0.406],
    "normalize_std": [0.229, 0.224, 0.225],
    
    # Model (inherited from h-e1)
    "architectures": ["ResNet-18-BN", "ResNet-18-LN"],
    "num_classes": 2,
    "pretrained": False,
    "init_mode": "kaiming_normal",
    
    # Training (inherited from h-e1)
    "optimizer": "SGD",
    "learning_rate": 0.01,
    "momentum": 0.9,
    "weight_decay": 1e-4,
    "epochs": 100,
    "seeds": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    "device": "cuda",
    
    # Gradient measurement (new for h-m1)
    "gradient_measurement": {
        "enabled_epochs": [1, 20],  # Measure gradients in epochs 1-20
        "hook_targets": ["conv1", "first_norm", "last_norm"],
        "group_split": {
            "majority_groups": [0, 3],  # Spurious-aligned
            "minority_groups": [1, 2]   # Spurious-misaligned
        },
        "measurement_split": "val",  # Measure on validation set
        "log_per_layer": True
    },
    
    # Statistical test (new for h-m1)
    "evaluation": {
        "significance_level": 0.05,
        "min_effect_size": 0.5,  # Cohen's d
        "min_ratio_difference": 0.20,  # 20% higher BN gradient ratio
        "aggregation_window": [1, 20]  # Average gradient ratio over epochs 1-20
    },
    
    # Output
    "output": {
        "results_dir": "results/h-m1/",
        "metrics_file": "training_metrics.csv",
        "stats_file": "gradient_analysis.txt",
        "plots": {
            "gradient_ratio_over_time": "gradient_ratio_over_time.png",
            "gradient_ratio_boxplot": "gradient_ratio_boxplot.png",
            "layer_gradient_heatmap": "layer_gradient_heatmap.png"
        }
    }
}
```

---

## Inherited Configuration (h-e1)

```python
# From: h-e1/train.py (actual implementation)
# Lines 71, 132-136

# Training hyperparameters (verified from h-e1 code)
lr = 0.01
momentum = 0.9
weight_decay = 1e-4
batch_size = 64
epochs = 100  # h-e1 ran 20 for testing, 100 specified in config
seeds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
device = 'cpu'  # h-e1 used CPU for stability, h-m1 supports CUDA
```

**Verified from**: `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_scsl/h-e1/train.py`

---

## New Parameters (h-m1)

### Gradient Measurement

```python
gradient_measurement = {
    "enabled_epochs": [1, 20],  # Only epochs 1-20 to reduce overhead
    "hook_targets": ["conv1", "first_norm", "last_norm"],
    "group_split": {
        "majority_groups": [0, 3],  # Waterbird-water, landbird-land
        "minority_groups": [1, 2]   # Waterbird-land, landbird-water
    },
    "measurement_split": "val",
    "log_per_layer": True
}
```

**Rationale**:
- `enabled_epochs=[1, 20]`: Early training window where spurious learning is strongest (per PRD FR3.5)
- `majority_groups=[0,3]`: Spurious-aligned groups from Waterbirds dataset definition
- `measurement_split="val"`: Avoid training loop interference, measure on clean validation split

### Statistical Test

```python
evaluation = {
    "significance_level": 0.05,
    "min_effect_size": 0.5,
    "min_ratio_difference": 0.20,
    "aggregation_window": [1, 20]
}
```

**Rationale**:
- `min_effect_size=0.5`: Medium effect per Cohen's d (weaker than h-e1's 0.8 for exploratory mechanism test)
- `min_ratio_difference=0.20`: 20% threshold from PRD success criterion FR6.4

---

## Usage

```python
# Direct copy-paste into train_with_gradients.py

from config import CONFIG

# Access gradient measurement settings
start_epoch, end_epoch = CONFIG["gradient_measurement"]["enabled_epochs"]
majority_groups = CONFIG["gradient_measurement"]["group_split"]["majority_groups"]
minority_groups = CONFIG["gradient_measurement"]["group_split"]["minority_groups"]

# Training loop
for epoch in range(CONFIG["epochs"]):
    if start_epoch <= epoch <= end_epoch:
        # Register gradient hooks
        pass
```

---

## Validation

- Single format (hardcoded dict): Matches h-e1 pattern
- MECHANISM hypothesis: Fixed config, no hyperparameter grid
- Inherited h-e1 hyperparameters: Learning rate, batch size, seeds verified from actual code
- Gradient measurement: Epochs 1-20 per PRD (computational efficiency)
- Statistical power: 10 seeds from h-e1 (no changes)
