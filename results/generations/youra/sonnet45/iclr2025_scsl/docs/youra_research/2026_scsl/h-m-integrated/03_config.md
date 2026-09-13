# Configuration Specification: h-m-integrated — 3-Step Mechanism Validation

**Date:** 2026-03-20
**Author:** Phase 3 Configuration Agent
**Hypothesis:** h-m-integrated (MECHANISM)
**Applied:** PyTorch hardcoded dict config pattern

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Config classes verified from base code
**Config Files Found:** h-e1/code/run_experiment.py (argparse-based), h-e1/code/models/simclr.py, h-e1/code/training/ssl_trainer.py
**Pattern Used:** Hardcoded dict (consistent with architecture specification)

---

## Inherited Configuration (Base Hypothesis)

### Verified Parameters (From Actual Code)

The following parameters are verified from h-e1 actual implementation:

**SimCLR Model (from h-e1/code/models/simclr.py):**
```python
# SimCLR.__init__ signature:
encoder_name: str = 'resnet50'
projection_dim: int = 128
pretrained: bool = False
```

**SSL Trainer (from h-e1/code/training/ssl_trainer.py):**
```python
# SSLTrainer.__init__ signature:
lr: float = 0.3
weight_decay: float = 1e-6
temperature: float = 0.5
momentum: float = 0.9
```

**Training Parameters (from h-e1/code/run_experiment.py):**
```python
# CLI defaults from argparse:
ssl_epochs: int = 200
ssl_batch_size: int = 256
probe_epochs: int = 20
probe_batch_size: int = 256
lr_grid: List[float] = [0.01, 0.001, 0.0001]
wd_grid: List[float] = [1e-4, 1e-5, 1e-6]
seeds: List[int] = [0, 1, 2, 3, 4]
```

**Verified from:** h-e1/code/ (actual implementation)

---

## M-1: LA-SSL Sampler Implementation [Complexity: 11, Budget: 6]

**Applied:** Standard PyTorch sampler defaults

### Configuration (Hardcoded Dict)

```python
LASSL_SAMPLER_CONFIG = {
    'alpha': 0.5,           # Inverse sampling temperature
    'window_size': 10,      # Epoch window for loss delta computation
}
```

### Subtasks [3/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-1-1 | LASSLSampler class | Implement torch.utils.data.Sampler with per-sample loss tracking |
| M-1-2 | Loss history tracking | Maintain rolling window of losses, compute learning speed |
| M-1-3 | Probability computation | Inverse weighting: p_i ∝ (learning_speed_i)^(-alpha) |

---

## M-2: LA-SSL Training Infrastructure [Complexity: 9, Budget: 6]

**Applied:** Reuse h-e1 SSLTrainer parameters

### Configuration (Hardcoded Dict)

```python
LASSL_TRAINER_CONFIG = {
    # Inherited from h-e1 SSLTrainer
    'lr': 0.3,              # Scaled by batch_size/256
    'weight_decay': 1e-6,
    'temperature': 0.5,
    'momentum': 0.9,

    # LA-SSL specific
    'use_sampler': True,    # Enable LA-SSL sampler
}
```

### Subtasks [3/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-2-1 | LASSLTrainer class | Extend h-e1 SSLTrainer with sampler integration |
| M-2-2 | Loss callback | Per-batch loss tracking for sampler updates |
| M-2-3 | Checkpoint saving | Save model state every 10 epochs aligned with SimCLR |

---

## M-3: SimCLR Baseline Training [Complexity: 8, Budget: 6]

**Applied:** Direct reuse of h-e1 validated config

### Configuration (Hardcoded Dict)

```python
SIMCLR_CONFIG = {
    # Model architecture (from h-e1/code/models/simclr.py)
    'encoder_name': 'resnet50',
    'projection_dim': 128,
    'pretrained': False,

    # Training (from h-e1/code/training/ssl_trainer.py)
    'lr': 0.3,              # Scaled by batch_size/256
    'weight_decay': 1e-6,
    'temperature': 0.5,
    'momentum': 0.9,

    # Schedule (from h-e1/code/run_experiment.py)
    'epochs': 100,          # Reduced from h-e1 (200) for mechanism validation
    'batch_size': 128,      # Reduced from h-e1 (256) for GPU memory
    'checkpoint_freq': 10,  # Save every 10 epochs for AMI evolution
    'seeds': [0, 1, 2],     # MECHANISM hypothesis: 3 seeds
}
```

### Subtasks [3/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-3-1 | run_simclr.py script | Orchestrate SimCLR training with h-e1 modules |
| M-3-2 | Checkpoint loop | Save checkpoints at epochs [10, 20, ..., 100] |
| M-3-3 | Embedding extraction | Extract frozen embeddings from all checkpoints |

---

## M-4: LA-SSL Training Execution [Complexity: 8, Budget: 6]

**Applied:** Align with SimCLR baseline schedule

### Configuration (Hardcoded Dict)

```python
LASSL_CONFIG = {
    # Inherit all from SIMCLR_CONFIG
    **SIMCLR_CONFIG,

    # LA-SSL sampler
    'sampler_alpha': 0.5,
    'sampler_window': 10,
}
```

### Subtasks [3/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-4-1 | run_lassl.py script | Orchestrate LA-SSL training with sampler |
| M-4-2 | Aligned checkpoints | Save at same epochs as SimCLR for comparison |
| M-4-3 | Loss tracking | Log per-sample losses for sampler updates |

---

## M-5: Embedding Extraction & Clustering [Complexity: 10, Budget: 6]

**Applied:** Standard sklearn k-means defaults

### Configuration (Hardcoded Dict)

```python
CLUSTERING_CONFIG = {
    'n_clusters': 4,        # 4 subgroups in Waterbirds
    'random_state': 42,
    'n_init': 10,           # K-means restarts for stability
}
```

### Subtasks [4/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-5-1 | Embedding extraction | Extract 2048-dim embeddings from all checkpoints |
| M-5-2 | K-means clustering | Run k-means on test set embeddings |
| M-5-3 | AMI computation | Compute Adjusted Mutual Information vs true groups |
| M-5-4 | AMI evolution tracking | Plot AMI over training epochs for both methods |

---

## M-6: Linear Probe & Cluster Retraining [Complexity: 12, Budget: 6]

**Applied:** Reuse h-e1 linear probe grid search

### Configuration (Hardcoded Dict)

```python
LINEAR_PROBE_CONFIG = {
    # Grid search (from h-e1/code/run_experiment.py)
    'lr_grid': [0.01, 0.001, 0.0001],
    'wd_grid': [1e-4, 1e-5, 1e-6],
    'seeds': [0, 1, 2, 3, 4],

    # Training
    'epochs': 20,
    'batch_size': 32,       # Reduced from h-e1 (256) for cluster balancing
}
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-6-1 | Baseline linear probe | Train ERM classifier on frozen embeddings |
| M-6-2 | Grid search | Find optimal (lr, wd, seed) on validation WGA |
| M-6-3 | Cluster weight computation | Compute inverse cluster frequency weights |
| M-6-4 | Cluster-balanced retraining | Retrain with cluster-weighted loss |
| M-6-5 | ΔWGA computation | Calculate improvement: WGA_cluster - WGA_baseline |
| M-6-6 | Cross-checkpoint analysis | Apply to all 10 SimCLR checkpoints |

---

## M-7: Mechanism Validation Suite [Complexity: 14, Budget: 6]

**Applied:** Standard statistical test thresholds from research

### Configuration (Hardcoded Dict)

```python
VALIDATION_CONFIG = {
    # M1: InfoNCE creates clusters
    'ami_threshold': 0.4,           # High clusterability
    'silhouette_threshold': 0.3,    # Cluster quality

    # M2: Clusterability predicts efficacy
    'correlation_pvalue': 0.05,     # Statistical significance
    'delta_wga_threshold': 2.0,     # Percentage points improvement

    # M3: LA-SSL disperses clusters
    'ami_reduction_threshold': 0.3,  # 30% AMI reduction
    'auc_delta_threshold': 0.05,     # Linear separability preserved
}
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-7-1 | M1 gate check | Validate AMI ≥0.4 on SimCLR epoch-100 |
| M-7-2 | M2 correlation test | Pearson correlation(AMI, ΔWGA) with p-value |
| M-7-3 | M2 stratified analysis | Compare high-AMI (≥0.4) vs low-AMI (<0.3) |
| M-7-4 | M3 AMI reduction | Compute (SimCLR - LA-SSL) / SimCLR at epoch 100 |
| M-7-5 | M3 separability test | Logistic regression AUC for subgroup prediction |
| M-7-6 | Report generation | JSON metrics + pass/fail for M1/M2/M3 |

---

## M-8: Visualization & Reporting [Complexity: 10, Budget: 6]

**Applied:** Standard visualization defaults

### Configuration (Hardcoded Dict)

```python
VISUALIZATION_CONFIG = {
    'tsne_perplexity': 30,
    'tsne_random_state': 42,
    'figure_dpi': 300,
    'figure_format': 'png',
}
```

### Subtasks [5/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-8-1 | AMI evolution plot | Line plot: epoch vs AMI (SimCLR vs LA-SSL) |
| M-8-2 | AMI-ΔWGA correlation | Scatter plot with regression line |
| M-8-3 | t-SNE embeddings | 2D projection colored by groups and clusters |
| M-8-4 | Group accuracy bars | 4 groups × {Baseline, Cluster-balanced, LA-SSL} |
| M-8-5 | Validation report | Markdown report with gate results |

---

## Shared Configuration

### Data Pipeline

```python
DATA_CONFIG = {
    'root_dir': '../.data_cache/datasets/waterbird_complete95_forest2water2',
    'num_workers': 4,
    'image_size': 224,
}
```

### Environment

```python
ENVIRONMENT_CONFIG = {
    'device': 'cuda',
    'seed': 42,
    'output_dir': './results',
    'checkpoint_dir': './checkpoints',
    'figure_dir': './figures',
}
```

---

## Complete Configuration (For Phase 4 Copy-Paste)

```python
"""Configuration for h-m-integrated: 3-Step Mechanism Validation."""

# LA-SSL Sampler (M-1)
LASSL_SAMPLER_CONFIG = {
    'alpha': 0.5,
    'window_size': 10,
}

# SimCLR Baseline (M-3)
SIMCLR_CONFIG = {
    # Model
    'encoder_name': 'resnet50',
    'projection_dim': 128,
    'pretrained': False,

    # Training
    'lr': 0.3,
    'weight_decay': 1e-6,
    'temperature': 0.5,
    'momentum': 0.9,

    # Schedule
    'epochs': 100,
    'batch_size': 128,
    'checkpoint_freq': 10,
    'seeds': [0, 1, 2],
}

# LA-SSL Training (M-2, M-4)
LASSL_CONFIG = {
    **SIMCLR_CONFIG,
    'sampler_alpha': 0.5,
    'sampler_window': 10,
}

# Clustering (M-5)
CLUSTERING_CONFIG = {
    'n_clusters': 4,
    'random_state': 42,
    'n_init': 10,
}

# Linear Probe (M-6)
LINEAR_PROBE_CONFIG = {
    'lr_grid': [0.01, 0.001, 0.0001],
    'wd_grid': [1e-4, 1e-5, 1e-6],
    'seeds': [0, 1, 2, 3, 4],
    'epochs': 20,
    'batch_size': 32,
}

# Mechanism Validation (M-7)
VALIDATION_CONFIG = {
    # M1
    'ami_threshold': 0.4,
    'silhouette_threshold': 0.3,

    # M2
    'correlation_pvalue': 0.05,
    'delta_wga_threshold': 2.0,

    # M3
    'ami_reduction_threshold': 0.3,
    'auc_delta_threshold': 0.05,
}

# Visualization (M-8)
VISUALIZATION_CONFIG = {
    'tsne_perplexity': 30,
    'tsne_random_state': 42,
    'figure_dpi': 300,
    'figure_format': 'png',
}

# Data
DATA_CONFIG = {
    'root_dir': '../.data_cache/datasets/waterbird_complete95_forest2water2',
    'num_workers': 4,
    'image_size': 224,
}

# Environment
ENVIRONMENT_CONFIG = {
    'device': 'cuda',
    'seed': 42,
    'output_dir': './results',
    'checkpoint_dir': './checkpoints',
    'figure_dir': './figures',
}
```

---

## Validation Checklist

- [x] ONE format only (Hardcoded dict)
- [x] No ASCII diagrams
- [x] KB search applied (PyTorch dataclass config experiment)
- [x] Rationale only for non-standard values
- [x] Subtask count within budget (M-1: 3/6, M-2: 3/6, M-3: 3/6, M-4: 3/6, M-5: 4/6, M-6: 6/6, M-7: 6/6, M-8: 5/6)
- [x] Total length <400 lines
- [x] Codebase Analysis section included
- [x] Inherited Configuration section with verified field names
- [x] Base hypothesis config verified from actual code

---

**END OF CONFIGURATION SPECIFICATION**
