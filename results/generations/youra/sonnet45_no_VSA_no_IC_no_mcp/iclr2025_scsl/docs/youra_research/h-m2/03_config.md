# Configuration: h-m2

**Hypothesis**: Attention Correction Mechanism  
**Gate**: SHOULD_WORK  
**Format**: Hardcoded dictionaries  
**Generated**: 2026-08-25

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New hypothesis - designing new config schema  
**Config Files Found**: None - new config  
**Pattern Used**: Hardcoded dict (minimal PoC for SHOULD_WORK hypothesis)

---

## Data Configuration

```python
DATA_CONFIG = {
    "dataset": "waterbirds",
    "root": "./data/waterbirds/",
    "batch_size": 64,
    "num_workers": 4,
    "resize": 224,
    "normalize_mean": [0.485, 0.456, 0.406],
    "normalize_std": [0.229, 0.224, 0.225],
    "augmentation": False
}
```

---

## Model Configurations

### ResNet-18-BN (Control)

```python
RESNET_BN_CONFIG = {
    "architecture": "resnet18",
    "pretrained": False,
    "num_classes": 2,
    "normalization": "batch_norm",
    "init_mode": "kaiming_normal",
    "init_nonlinearity": "relu",
    "init_fan_mode": "fan_out"
}
```

### ResNet-18-CBAM (Ablation)

```python
RESNET_CBAM_CONFIG = {
    "architecture": "resnet18",
    "pretrained": False,
    "num_classes": 2,
    "normalization": "batch_norm",
    "cbam_reduction": 16,
    "cbam_kernel_size": 7,
    "cbam_insertion": ["layer1", "layer2", "layer3", "layer4"],
    "init_mode_resnet": "kaiming_normal",
    "init_mode_cbam": "xavier_normal",
    "init_nonlinearity": "relu",
    "init_fan_mode": "fan_out"
}
```

### ViT-Small (Global Attention)

```python
VIT_CONFIG = {
    "model_name": "vit_small_patch16_224",
    "pretrained": False,
    "num_classes": 2,
    "patch_size": 16,
    "embed_dim": 384,
    "depth": 12,
    "num_heads": 6,
    "init_linear": "xavier_uniform",
    "init_pos_embed": "normal",
    "gradient_clip_max_norm": 1.0
}
```

---

## Training Configuration

```python
TRAINING_CONFIG = {
    "optimizer": "sgd",
    "lr": 0.01,
    "momentum": 0.9,
    "weight_decay": 1e-4,
    "loss_fn": "cross_entropy",
    "epochs": 100,
    "seeds": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    "lr_schedule": None,
    "device": "cuda",
    "mixed_precision": False,
    "checkpoint_resume": True
}
```

---

## Evaluation Configuration

```python
EVAL_CONFIG = {
    "metrics": [
        "avg_acc",
        "worst_group_acc",
        "group_0_acc",
        "group_1_acc",
        "group_2_acc",
        "group_3_acc",
        "worst_group_gap",
        "train_loss"
    ],
    "logging_frequency": 1,
    "checkpoint_epochs": [100],
    "slope_analysis_start": 20,
    "slope_analysis_end": 50,
    "bootstrap_resamples": 1000,
    "ci_level": 0.95,
    "ci_percentiles": [2.5, 97.5]
}
```

---

## Success Thresholds

```python
SUCCESS_CONFIG = {
    "slope_diff_threshold": 0.3,
    "cohen_d_threshold": 0.8,
    "falsification_slope_diff": 0.2,
    "falsification_cohen_d": 0.5,
    "ci_overlap_allowed": False
}
```

---

## Runtime Configuration

```python
RUNTIME_CONFIG = {
    "log_format": "csv",
    "log_dir": "./results/logs/",
    "checkpoint_dir": "./results/checkpoints/",
    "results_dir": "./results/",
    "csv_columns": [
        "epoch",
        "seed",
        "architecture",
        "avg_acc",
        "worst_group_acc",
        "worst_group_gap",
        "train_loss",
        "group_0_acc",
        "group_1_acc",
        "group_2_acc",
        "group_3_acc"
    ]
}
```

---

## Architecture-Specific Runtime Estimates

```python
RUNTIME_ESTIMATES = {
    "resnet_bn_minutes_per_epoch": 6,
    "resnet_cbam_minutes_per_epoch": 6,
    "vit_minutes_per_epoch": 8,
    "total_gpu_hours_serial": 33,
    "total_gpu_hours_parallel_3gpu": 13
}
```

---

## CBAM Module Configuration

```python
CBAM_MODULE_CONFIG = {
    "channel_attention": {
        "pooling": ["avg", "max"],
        "mlp_reduction": 16,
        "activation": "sigmoid"
    },
    "spatial_attention": {
        "pooling": ["avg", "max"],
        "conv_kernel": 7,
        "conv_padding": 3,
        "activation": "sigmoid"
    },
    "output_combination": "multiply"
}
```

---

## Usage Pattern

```python
# Combined config for training script
EXPERIMENT_CONFIG = {
    "data": DATA_CONFIG,
    "models": {
        "resnet_bn": RESNET_BN_CONFIG,
        "resnet_cbam": RESNET_CBAM_CONFIG,
        "vit": VIT_CONFIG
    },
    "training": TRAINING_CONFIG,
    "evaluation": EVAL_CONFIG,
    "success": SUCCESS_CONFIG,
    "runtime": RUNTIME_CONFIG
}

# Access example
batch_size = EXPERIMENT_CONFIG["data"]["batch_size"]
lr = EXPERIMENT_CONFIG["training"]["lr"]
seeds = EXPERIMENT_CONFIG["training"]["seeds"]
```

---

## Validation Checklist

- [x] Dataset config matches Phase 2C (Waterbirds, batch_size=64)
- [x] Model configs match PRD (3 architectures, correct hyperparameters)
- [x] Training config matches experiment brief (LR=0.01, SGD, 100 epochs, 10 seeds)
- [x] Evaluation config includes all required metrics
- [x] Success thresholds match hypothesis claim (slope diff ≥0.3, d≥0.8)
- [x] Runtime config supports CSV logging and checkpoint resume
- [x] Format is copy-paste ready (hardcoded dicts)
