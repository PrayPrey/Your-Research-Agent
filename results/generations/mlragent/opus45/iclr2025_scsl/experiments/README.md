# Shortcut Learning in Self-Supervised Contrastive Learning

This repository contains the experimental code for analyzing shortcut learning dynamics in self-supervised contrastive learning (SSCL) through loss landscape analysis.

## Overview

The experiment investigates:
1. **How spurious correlations shape the loss landscape** in contrastive learning
2. **Temporal dynamics of feature learning** - when shortcuts are learned vs semantic features
3. **CR-InfoNCE**: A curvature-aware contrastive loss to mitigate shortcut learning

## Methods Compared

1. **SimCLR** (Baseline): Standard contrastive learning with InfoNCE loss
2. **CR-InfoNCE** (Proposed): Curvature-Regularized InfoNCE that penalizes sharp minima
3. **SimCLR+WD**: SimCLR with strong weight decay regularization
4. **LateTVG**: Pruning later layers to remove spurious information

## Dataset

We use CIFAR-10 with synthetic spurious correlations:
- Each class is associated with a colored border with probability `p_spurious`
- Default `p_spurious=0.9` creates strong spurious correlations
- Test sets include both aligned (spurious matches label) and conflicting (spurious differs from label) data

## Requirements

```
torch>=2.0.0
torchvision>=0.15.0
numpy
matplotlib
pandas
scikit-learn
tqdm
```

## Running the Experiment

### Basic Usage

```bash
python run_experiment.py
```

### With Custom Parameters

```bash
python run_experiment.py \
    --epochs 30 \
    --batch_size 128 \
    --p_spurious 0.9 \
    --lambda_curv 0.01 \
    --output_dir ./claude_code
```

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--train_size` | 5000 | Number of training samples |
| `--val_size` | 1000 | Number of validation samples |
| `--test_size` | 1000 | Number of test samples |
| `--p_spurious` | 0.9 | Spurious correlation strength |
| `--epochs` | 30 | Number of training epochs |
| `--batch_size` | 128 | Batch size |
| `--lr` | 1e-3 | Learning rate |
| `--temperature` | 0.5 | InfoNCE temperature |
| `--lambda_curv` | 0.01 | Curvature regularization weight |
| `--eval_freq` | 5 | Feature probing frequency |
| `--seed` | 42 | Random seed |

## Output Files

The experiment generates:

- `log.txt`: Complete experiment log
- `results.json`: All metrics in JSON format
- `summary.csv`: Summary table of final metrics
- `training_curves.png`: Training/validation loss curves
- `encoding_rates.png`: Spurious vs core feature encoding over time
- `robustness_comparison.png`: Performance on aligned vs conflicting test sets
- `learning_dynamics.png`: Relative learning speed comparison
- `final_comparison.png`: Comprehensive comparison of all methods

## Key Metrics

1. **Spurious Encoding Rate (SER)**: How well representations predict spurious attributes
2. **Core Encoding Rate (CER)**: How well representations predict semantic labels
3. **Robustness Gap**: Difference in accuracy between aligned and conflicting test sets
4. **Relative Learning Speed**: Ratio of time to learn core vs spurious features

## Expected Results

- SimCLR tends to learn spurious features faster than core features (ρ < 1)
- CR-InfoNCE should reduce the robustness gap by penalizing sharp spurious-aligned minima
- The proposed method should improve worst-group (conflicting) accuracy

## Citation

Based on the research proposal: "Understanding and Mitigating Shortcut Learning Dynamics in Self-Supervised Contrastive Learning through Loss Landscape Analysis"
