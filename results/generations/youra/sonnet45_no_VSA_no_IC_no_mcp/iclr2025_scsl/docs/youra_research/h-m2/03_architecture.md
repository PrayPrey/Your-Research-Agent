# Architecture: h-m2

**Hypothesis**: Attention Correction Mechanism  
**Type**: MECHANISM  
**Gate**: SHOULD_WORK  
**Complexity**: Tier 1  
**Generated**: 2026-08-25

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation from scratch (h-e1 data loader can be reused)  
**Analyzed Path**: N/A  
**Findings**: h-e1 has synthetic Waterbirds loader - reuse interface, update to real wilds dataset

---

## System Overview

5 modules:
1. Data: Waterbirds via wilds, group labels
2. Models: ResNet-BN, ResNet-CBAM (4 modules), ViT-Small
3. Train: 3 arch × 10 seeds × 100 epochs
4. Eval: Slope computation (epochs 20-50), bootstrap CI, Cohen's d
5. Viz: Trajectory plot, regression lines, statistical table

---

## Module Specifications

### 1. DataLoader (`code/data_loader.py`)

**Dependencies**: wilds, torch

```python
def get_waterbirds_dataloader(split: str, batch_size: int = 64) -> DataLoader:
    """
    Args:
        split: 'train', 'val', 'test'
    Returns:
        DataLoader yielding (images, labels, group_ids, metadata)
        - images: [B, 3, 224, 224] ImageNet normalized
        - labels: [B] binary (0=landbird, 1=waterbird)
        - group_ids: [B] integers 0-3
    """
    ...
```

**Output**: 4800 train, 600 val, 600 test samples, no augmentation

---

### 2. Models (`code/models.py`)

**Dependencies**: torch, torchvision, timm

#### ResNet-BN (Control)

```python
def create_resnet_bn(num_classes: int = 2) -> nn.Module:
    """torchvision ResNet-18, default BN, He init"""
    ...
```

#### CBAM Module

```python
class CBAM(nn.Module):
    def __init__(self, channels: int, reduction: int = 16):
        """
        Channel attention: AvgPool+MaxPool → MLP(C→C//16→C) → Sigmoid
        Spatial attention: ChannelPool → Conv7x7 → Sigmoid
        """
        ...
    
    def forward(self, x: Tensor) -> Tensor:
        """Returns x * channel_attn * spatial_attn"""
        ...
```

#### ResNet-CBAM

```python
def create_resnet_cbam(num_classes: int = 2) -> nn.Module:
    """
    ResNet-18 + 4 CBAM modules (after each residual block)
    He init for ResNet, Xavier for CBAM
    """
    ...
```

#### ViT-Small

```python
def create_vit_small(num_classes: int = 2) -> nn.Module:
    """timm ViT-Small patch16_224, no pretrain, Xavier init"""
    ...
```

---

### 3. Training (`code/train.py`)

**Dependencies**: torch, tqdm

```python
def train_one_run(
    model: nn.Module,
    train_loader: DataLoader,
    test_loader: DataLoader,
    seed: int,
    arch_name: str,
    epochs: int = 100
) -> pd.DataFrame:
    """
    Train single run (1 seed, 1 arch, 100 epochs)
    
    Returns:
        DataFrame with columns: epoch, avg_acc, worst_group_acc, 
        group_0_acc, group_1_acc, group_2_acc, group_3_acc, gap, train_loss
    """
    ...

def run_all_experiments() -> None:
    """
    Main loop: 3 architectures × 10 seeds × 100 epochs
    Saves logs to results/logs/{arch}_{seed}.csv
    Saves checkpoints to results/checkpoints/{arch}_{seed}.pt
    """
    ...
```

**Config**:
- Optimizer: SGD(lr=0.01, momentum=0.9, weight_decay=1e-4)
- Loss: CrossEntropyLoss
- Batch size: 64
- Seeds: 0-9

---

### 4. Slope Evaluation (`code/evaluate_slopes.py`)

**Dependencies**: scipy, numpy

```python
def compute_slope(gap_trajectory: np.ndarray, epochs: np.ndarray) -> tuple[float, float, float]:
    """
    Linear regression: gap = β₀ + β₁ × epoch
    
    Args:
        gap_trajectory: worst_group_gap for epochs 20-50 (31 points)
        epochs: [20, 21, ..., 50]
    
    Returns:
        (slope, intercept, r_value)
    """
    ...

def bootstrap_ci(slopes: np.ndarray, n_resamples: int = 1000) -> tuple[float, float, float]:
    """
    Compute mean slope and 95% CI via bootstrap
    
    Returns:
        (ci_lower, mean_slope, ci_upper)
    """
    ...

def compute_cohens_d(slopes_1: np.ndarray, slopes_2: np.ndarray) -> float:
    """Cohen's d: (mean1 - mean2) / pooled_std"""
    ...

def evaluate_slopes() -> pd.DataFrame:
    """
    Load all logs, compute slopes, aggregate statistics
    
    Returns:
        DataFrame: arch, mean_slope, ci_lower, ci_upper, cohens_d_vs_bn
    """
    ...
```

---

### 5. Visualization (`code/plot_trajectories.py`)

**Dependencies**: matplotlib

```python
def plot_trajectories(logs_dir: str, slopes_df: pd.DataFrame) -> None:
    """
    Plot mean gap ± stderr for each architecture
    Highlight epochs 20-50, overlay regression lines
    Save to results/trajectories.png
    """
    ...

def generate_summary_table(slopes_df: pd.DataFrame) -> None:
    """
    Markdown table: arch, mean_slope, CI, p-value, Cohen's d
    Save to results/statistical_summary.md
    """
    ...
```

---

## Data Flow

```
1. Data Loader → (images, labels, group_ids)
2. Model (ResNet-BN/CBAM/ViT) → logits
3. Train Loop → logs (epoch metrics) + checkpoints
4. Evaluate Slopes → load logs, fit regressions, bootstrap CIs
5. Viz → plot trajectories + statistical table
```

---

## Interface Contracts

### Data → Models
- Input: `(batch, 3, 224, 224)` images
- Output: `(batch, 2)` logits

### Models → Train
- Forward: `logits = model(images)`
- Backward: `loss.backward()`, `optimizer.step()`

### Train → Eval
- Logs: CSV files with columns `[epoch, avg_acc, worst_group_acc, group_0_acc, ..., gap, train_loss]`
- Checkpoints: `{arch}_{seed}.pt` at epoch 100

### Eval → Viz
- Slopes table: `arch, mean_slope, ci_lower, ci_upper, cohens_d`
- Raw logs: full trajectories for plotting

---

## Error Handling

### Checkpoint Resume
```python
if os.path.exists(f'checkpoints/{arch}_{seed}.pt'):
    checkpoint = torch.load(...)
    model.load_state_dict(checkpoint['model'])
    start_epoch = checkpoint['epoch'] + 1
else:
    start_epoch = 0
```

### ViT Stability Monitoring
```python
if epoch < 10 and arch == 'vit_small':
    grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
    if grad_norm > 10.0:
        logger.warning(f'High gradient norm: {grad_norm}')
```

### CBAM Validation
```python
# Pre-flight check: test CBAM on CIFAR-10
def validate_cbam():
    """Train ResNet-BN and ResNet-CBAM on CIFAR-10 for 10 epochs"""
    assert cbam_acc > bn_acc + 0.01, "CBAM should improve accuracy by 1%"
```

---

## Testing Plan

### Unit Tests

**CBAM Module**:
```python
def test_cbam_shapes():
    cbam = CBAM(channels=64)
    x = torch.randn(4, 64, 28, 28)
    out = cbam(x)
    assert out.shape == x.shape
    assert torch.allclose(out, x, atol=0.1)  # attention ≈ 1 initially
```

**Data Loader**:
```python
def test_data_loader():
    loader = get_waterbirds_dataloader('train')
    imgs, labels, groups, meta = next(iter(loader))
    assert imgs.shape == (64, 3, 224, 224)
    assert labels.shape == (64,)
    assert groups.shape == (64,)
    assert groups.min() >= 0 and groups.max() <= 3
```

### Integration Tests

**CIFAR-10 CBAM Validation** (pre-flight):
```python
def test_cbam_cifar10():
    """Train ResNet-BN and ResNet-CBAM on CIFAR-10 for 10 epochs"""
    bn_acc = train_cifar10(create_resnet_bn(), epochs=10)
    cbam_acc = train_cifar10(create_resnet_cbam(), epochs=10)
    assert cbam_acc > bn_acc + 0.01, f"CBAM {cbam_acc} vs BN {bn_acc}"
```

**ViT Convergence Check**:
```python
def test_vit_convergence():
    """Train ViT-Small for 5 epochs, verify loss decreases"""
    model = create_vit_small()
    losses = train_vit_quick(model, epochs=5)
    assert losses[-1] < losses[0] * 0.8, "Loss should decrease by 20%"
```

---

## File Structure

```
h-m2/
├── code/
│   ├── data_loader.py          (~50 lines or reuse h-e1)
│   ├── models.py               (~150 lines: all 3 architectures + CBAM)
│   ├── train.py                (~100 lines: training loop)
│   ├── evaluate_slopes.py      (~100 lines: slope computation)
│   └── plot_trajectories.py    (~50 lines: visualization)
├── results/
│   ├── logs/                   (30 CSV files: 3 arch × 10 seeds)
│   ├── checkpoints/            (30 .pt files)
│   ├── slopes.csv              (statistical summary)
│   └── trajectories.png        (plot)
```

---

## Key Design Decisions

### CBAM Insertion Points
- After each residual block: conv2_x, conv3_x, conv4_x, conv5_x (4 total)
- Placement: `block_output = cbam(block_output)`
- Preserves ResNet local inductive bias

### Initialization Strategy
- ResNet/CBAM: He normal (`kaiming_normal_`, mode='fan_out', nonlinearity='relu')
- CBAM MLP: Xavier normal (`xavier_normal_`)
- ViT: Xavier uniform (timm default)

### Metric Logging
Every epoch log to CSV:
- avg_acc, worst_group_acc
- group_0_acc, group_1_acc, group_2_acc, group_3_acc
- gap = avg_acc - worst_group_acc
- train_loss

### Epoch Window
- Log all epochs 0-100
- Analyze epochs 20-50 for slope (31 points)
- Justification: mid-training phase where correction should emerge

### Statistical Test
- Bootstrap CI with 1000 resamples
- CI non-overlap = statistical significance
- Cohen's d ≥ 0.8 = large effect size

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E-1 | Data Setup | Waterbirds via wilds, validate group distribution | 6 | download(1) + loader(2) + validate(1) + doc(2) |
| E-2 | CBAM Module | Implement channel+spatial attention, test on CIFAR-10 | 8 | module(3) + integration(2) + validation(2) + debug(1) |
| E-3 | Models | ResNet-BN, ResNet-CBAM, ViT-Small factories | 7 | bn(1) + cbam_integ(3) + vit(2) + init(1) |
| E-4 | Training Loop | 3 arch × 10 seeds × 100 epochs, metric logging | 9 | loop(3) + metrics(2) + checkpoints(2) + monitoring(2) |
| E-5 | Slope Eval | Linear regression, bootstrap CI, Cohen's d | 8 | regression(2) + bootstrap(3) + stats(2) + table(1) |
| E-6 | Visualization | Trajectory plot, regression overlay, summary table | 6 | plot(3) + overlay(1) + table(1) + formatting(1) |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [E-4], Low(4-8): [E-1, E-2, E-3, E-5, E-6]

**Total Complexity**: 44 points (average ~7.3 per task)

---

## Dependencies

**Python 3.9+**:
- torch >= 2.0
- torchvision >= 0.15
- timm >= 0.9 (ViT)
- wilds >= 2.0 (dataset)
- numpy >= 1.24
- scipy >= 1.10
- matplotlib >= 3.7
- pandas >= 2.0
- tqdm

**Hardware**:
- GPU: 16GB VRAM recommended (ViT ~8GB, ResNet ~4GB)
- Runtime: 33 hours GPU serial (10h BN + 10h CBAM + 13h ViT)

---

## Validation Checklist

**Pre-Implementation**:
- [ ] Waterbirds downloads via wilds
- [ ] Group distribution matches 4800/600/600 split
- [ ] CBAM tested on CIFAR-10 (1% improvement)

**Post-Implementation**:
- [ ] All 30 runs complete
- [ ] Logs contain 31 epochs in window 20-50
- [ ] Slopes computed, CIs non-overlapping if hypothesis true
- [ ] Cohen's d ≥ 0.8 for successful comparison
- [ ] Trajectory plot shows visual separation

---

## Success Criteria

**Hypothesis Validated** if:
- (CBAM OR ViT) mean_slope < BN mean_slope - 0.3pp/epoch
- CIs do not overlap
- Cohen's d ≥ 0.8

**Hypothesis Falsified** if:
- Both CBAM and ViT CIs overlap with BN
- Slope difference < 0.2pp/epoch
- Cohen's d < 0.5

**Partial Success** (ViT succeeds, CBAM fails):
- Global architecture drives correction, not attention alone

---

**Architecture Status**: COMPLETED  
**Ready for Phase 4 (Coder)**: YES  
**Estimated LoC**: 450 lines  
**Estimated Runtime**: 33 hours GPU
