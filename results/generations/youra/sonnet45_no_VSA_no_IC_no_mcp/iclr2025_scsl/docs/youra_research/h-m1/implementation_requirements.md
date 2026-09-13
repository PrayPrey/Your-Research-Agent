# Implementation Requirements: h-m1

**Generated**: 2026-08-24  
**Hypothesis ID**: h-m1  
**Tier**: 1.5 (Simple-to-Moderate)  
**Budget**: 350-550 tokens

---

## Code Reuse from h-e1

### Reusable Components (MUST reuse to save implementation time)

1. **Data Loader** (`h-e1/data_loader.py`)
   - Waterbirds dataset download and preprocessing
   - Group label extraction (4 groups: landbird-land, landbird-water, waterbird-land, waterbird-water)
   - Train/val/test splits
   - ImageNet normalization

2. **Model Definitions** (`h-e1/models.py`)
   - ResNet-18-BN (torchvision ResNet-18 with BatchNorm2d)
   - ResNet-18-LN (ResNet-18 with LayerNorm replacement)
   - He normal initialization
   - Binary classification output (2 classes)

3. **Training Loop Scaffold** (`h-e1/train.py`)
   - 10-seed iteration (seeds 0-9)
   - 100-epoch training loop
   - SGD optimizer (lr=0.01, momentum=0.9, weight_decay=1e-4)
   - CrossEntropyLoss
   - Per-epoch metric logging (average accuracy, worst-group accuracy, per-group accuracy)

4. **Evaluation Framework** (`h-e1/evaluate.py`)
   - Per-group accuracy computation
   - Worst-group gap calculation
   - Statistical test infrastructure (t-test, Cohen's d)

---

## New Components (h-m1 specific)

### 1. Gradient Measurement Infrastructure

**File**: `gradient_hooks.py`

**Requirements**:
- Register backward hooks on normalization layers (BN and LN)
- Capture gradient norms during backward pass
- Log per-layer gradient magnitudes (first conv, first BN/LN, last BN/LN)
- Compute mean gradient norm over batch

**Implementation**:
```python
def register_gradient_hooks(model, gradient_dict):
    """
    Register backward hooks to measure gradient norms.
    
    Args:
        model: ResNet-18-BN or ResNet-18-LN
        gradient_dict: dict to store {layer_name: [grad_norms]}
    
    Returns:
        List of hook handles (for cleanup)
    """
    hooks = []
    for name, param in model.named_parameters():
        if 'bn' in name or 'ln' in name or 'conv1.weight' in name:
            hook = param.register_hook(
                lambda grad, name=name: gradient_dict[name].append(grad.norm().item())
            )
            hooks.append(hook)
    return hooks
```

### 2. Group-Stratified Gradient Analysis

**File**: `group_gradients.py`

**Requirements**:
- Split validation set into majority group (spurious-aligned) and minority group (spurious-misaligned)
- Compute loss separately on majority and minority samples
- Measure gradient magnitude for each group
- Calculate gradient ratio: `grad_majority / grad_minority`

**Majority Group** (spurious-aligned):
- waterbird-water (label=1, background=1)
- landbird-land (label=0, background=0)

**Minority Group** (spurious-misaligned):
- waterbird-land (label=1, background=0)
- landbird-water (label=0, background=1)

**Implementation**:
```python
def compute_group_gradients(model, val_loader, device):
    """
    Compute gradient norms on majority vs minority groups.
    
    Returns:
        grad_majority: mean gradient norm on majority group
        grad_minority: mean gradient norm on minority group
        grad_ratio: grad_majority / grad_minority
    """
    # Split samples by group
    majority_samples = [(x, y) for x, y, g in val_loader if g in [0, 3]]  # landbird-land, waterbird-water
    minority_samples = [(x, y) for x, y, g in val_loader if g in [1, 2]]  # landbird-water, waterbird-land
    
    # Compute gradients on each group
    grad_majority = compute_gradient_norm(model, majority_samples, device)
    grad_minority = compute_gradient_norm(model, minority_samples, device)
    
    return grad_majority, grad_minority, grad_majority / grad_minority
```

### 3. Enhanced Training Loop

**File**: `train_with_gradients.py` (extends `h-e1/train.py`)

**Modifications**:
- Add gradient measurement on epochs 1-20
- Register backward hooks before training
- Compute group-stratified gradients on validation set each epoch
- Log gradient metrics: `grad_majority`, `grad_minority`, `grad_ratio`
- Remove hooks after epoch 20 (reduce overhead for epochs 21-100)

**New Logged Metrics** (epochs 1-20 only):
- `grad_majority_norm`: mean gradient norm on majority group
- `grad_minority_norm`: mean gradient norm on minority group
- `grad_ratio`: grad_majority / grad_minority
- `conv1_grad_norm`: first conv layer gradient norm
- `first_norm_grad_norm`: first normalization layer (BN/LN) gradient norm
- `last_norm_grad_norm`: last normalization layer gradient norm

### 4. Gradient Ratio Analysis

**File**: `analyze_gradients.py`

**Requirements**:
- Load training metrics for all seeds (focus on epochs 1-20)
- Compute mean gradient ratio per architecture across 10 seeds
- Perform independent t-test (BN gradient ratios vs LN gradient ratios)
- Compute effect size (Cohen's d)
- Evaluate success criterion: BN ratio ≥ 20% higher than LN ratio

**Output**:
- Statistical test results (t-statistic, p-value, Cohen's d)
- Mean gradient ratio: ResNet-BN vs ResNet-LN
- Per-seed gradient ratio table
- Visualization: gradient ratio trajectories (epochs 1-20)

### 5. Visualization

**File**: `plot_gradients.py`

**Plots**:
1. **Gradient ratio over time** (epochs 1-20):
   - X-axis: epoch
   - Y-axis: gradient ratio (spurious/core)
   - Two lines: ResNet-BN (blue), ResNet-LN (orange)
   - Shaded region: ±1 std across 10 seeds

2. **Gradient ratio comparison** (box plot):
   - X-axis: architecture (ResNet-BN, ResNet-LN)
   - Y-axis: mean gradient ratio (epochs 1-20)
   - 10 points per architecture (one per seed)

3. **Per-layer gradient norms** (heatmap):
   - X-axis: epoch (1-20)
   - Y-axis: layer (conv1, first_norm, last_norm)
   - Color: gradient norm (log scale)
   - Separate heatmaps for BN and LN

---

## File Structure

```
h-m1/
├── gradient_hooks.py          # Backward hook registration (NEW)
├── group_gradients.py          # Majority/minority gradient computation (NEW)
├── train_with_gradients.py    # Training loop with gradient logging (MODIFIED from h-e1)
├── analyze_gradients.py        # Statistical test on gradient ratios (NEW)
├── plot_gradients.py           # Visualization (NEW)
├── data_loader.py              # REUSE from h-e1 (symlink or copy)
├── models.py                   # REUSE from h-e1 (symlink or copy)
└── results/
    └── h-m1/
        ├── training_metrics.csv         # Extended with gradient metrics
        ├── gradient_analysis.txt        # Statistical test results
        ├── gradient_ratio_over_time.png
        ├── gradient_ratio_boxplot.png
        └── layer_gradient_heatmap.png
```

---

## Dependencies

Same as h-e1 (no new dependencies):
- torch >= 1.10
- torchvision >= 0.11
- wilds >= 2.0 (Waterbirds dataset)
- numpy >= 1.20
- scipy >= 1.7 (t-test, Cohen's d)
- matplotlib >= 3.4 (plotting)
- tqdm >= 4.60 (progress bars)

---

## Computational Requirements

**Training Time** (per seed):
- 100 epochs × ~5 min/epoch (CPU) = ~8 hours/seed
- Gradient measurement overhead: +20% (backward hooks)
- Total: ~10 hours/seed × 2 architectures × 10 seeds = ~200 hours (8-9 days on CPU)

**GPU Acceleration** (if available):
- ~30 min/seed × 2 architectures × 10 seeds = ~10 hours total

**Storage**:
- Dataset: ~500 MB (Waterbirds images)
- Training metrics: ~50 KB/seed × 20 runs = ~1 MB
- Model checkpoints (optional): ~45 MB/checkpoint × 20 runs = ~900 MB

---

## Quality Assurance

### Static Analysis
- [ ] All modules compile without syntax errors
- [ ] All imports resolve correctly
- [ ] Type consistency (tensor shapes match specifications)

### Functional Validation
- [ ] Backward hooks capture gradients correctly (non-zero norms)
- [ ] Majority/minority group split is correct (group indices 0,3 vs 1,2)
- [ ] Gradient ratio is computed correctly (no division by zero)
- [ ] Training metrics include gradient columns for epochs 1-20
- [ ] Hooks are removed after epoch 20 (no memory leak)

### Reproducibility
- [ ] All RNG seeds set before model/data creation
- [ ] cudnn.deterministic enabled
- [ ] Gradient measurement does not alter training dynamics (hooks are read-only)

---

## Success Metrics

### Code Quality
- [ ] Reuses ≥80% of h-e1 codebase (data loader, models, training scaffold)
- [ ] New components (gradient hooks, group analysis) are <200 LoC each
- [ ] No code duplication (use functions/modules)

### Experiment Quality
- [ ] Gradient ratio shows non-zero variance (not flat line)
- [ ] Gradient ratio differs between BN and LN (visual inspection before statistical test)
- [ ] All 10 seeds complete without NaN gradients or CUDA errors

### Documentation
- [ ] All functions have docstrings (Args, Returns, Description)
- [ ] README explains how to run experiment (python train_with_gradients.py)
- [ ] Comments explain non-obvious gradient measurement logic

---

## Phase 3 Deliverables

From this requirements document, Phase 3 will generate:

1. **PRD** (Product Requirements Document):
   - User story: "As a researcher, I need to measure gradient flow to spurious vs core features during early training of ResNet-BN and ResNet-LN on Waterbirds"
   - Acceptance criteria: Gradient ratio measured, statistical test performed, BN vs LN comparison validated

2. **Architecture Document**:
   - Module 1: Gradient measurement infrastructure (backward hooks)
   - Module 2: Group-stratified gradient analysis (majority/minority split)
   - Module 3: Training loop with gradient logging (extends h-e1)
   - Module 4: Statistical test and visualization

3. **Epic-level Archon Tasks**:
   - EPIC-GRAD-HOOKS: Implement backward hooks for gradient norm measurement
   - EPIC-GROUP-SPLIT: Split validation set by majority/minority groups
   - EPIC-GRAD-LOG: Log per-epoch gradient ratios (epochs 1-20)
   - EPIC-GRAD-EVAL: Compute gradient ratio statistics and t-test
   - EPIC-VIZ: Plot gradient ratio trajectories and layer-wise heatmaps

---

**Requirements Document Status**: COMPLETED  
**Ready for Phase 3**: YES  
**Code Reuse Estimate**: 80% (h-e1 components) + 20% (new gradient measurement)
