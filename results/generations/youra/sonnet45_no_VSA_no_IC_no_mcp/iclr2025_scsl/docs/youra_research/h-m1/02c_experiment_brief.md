# Phase 2C: Experiment Design Brief

**Generated**: 2026-08-24  
**Hypothesis ID**: h-m1  
**Hypothesis Type**: MECHANISM  
**Gate**: SHOULD_WORK (does NOT block Phase 5 if fails)  
**Prerequisite**: h-e1 (VALIDATED)  
**Archon Task ID**: 14806d36-2041-4164-96d5-cd778cbf5dbf  
**Pipeline Project ID**: e434b9c6-e150-46c4-8cb5-1c8e857b014c

---

## Hypothesis Statement

**Title**: BN Amplifies Early Spurious Learning via Batch-Level Statistics

**Statement**: ResNet-BN's batch-level statistics make stochastic batch spurious correlations easier to learn than instance-level core features, causing higher early worst-group gap.

**Causal Mechanism**: BN processes features with batch statistics (mean/variance over batch dimension), which amplifies spurious correlations that are stochastically present at batch level. LN processes features with instance statistics (mean/variance over channel/spatial dimensions), which does not amplify batch-level spurious patterns.

**Prerequisite Validation**: h-e1 confirmed BN exhibits 9.41pp higher worst-group gap than LN at 90% average accuracy (p < 0.001, Cohen's d = 3.94).

---

## Experiment Design

### Dataset

**Name**: Waterbirds  
**Type**: standard  
**Source**: Spurious correlation benchmark from Sagawa et al. 2020  
**Description**: Binary classification (landbird vs waterbird) with spurious background correlation (land vs water).

**Statistics**:
- Total images: ~6000
- Train: ~4800
- Val: ~600
- Test: ~600
- Groups: 4 (landbird-land, landbird-water, waterbird-land, waterbird-water)
- Spurious correlation: 95% in train (waterbirds on water, landbirds on land)
- Minority groups: landbird-water, waterbird-land (5% each)

**Preprocessing**:
- Resize to 224×224
- Standard ImageNet normalization (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
- No data augmentation (isolate architectural effects)

**Access**:
- Download via `wilds` library: `wilds.get_dataset(dataset='waterbirds', download=True)`
- Cache path: `./data/waterbirds/`
- **Reuse**: Same dataset instance as h-e1 (already cached)

---

### Baseline Architectures

#### Architecture 1: ResNet-18-BN
- Base: torchvision ResNet-18 with Batch Normalization (default)
- Normalization layers: 17 BN layers (1 conv1 + 16 residual blocks)
- Pretrained: False (train from scratch)
- Initialization: He normal (kaiming_normal with fan_out, relu mode)
- Output: 2 classes (landbird, waterbird)
- **Reuse**: Same model as h-e1

#### Architecture 2: ResNet-18-LN
- Base: torchvision ResNet-18 with Batch Normalization layers replaced by Layer Normalization
- Normalization layers: 17 LN layers (normalized_shape=[C, H, W] per feature map)
- Pretrained: False (train from scratch)
- Initialization: He normal (kaiming_normal with fan_out, relu mode)
- Output: 2 classes (landbird, waterbird)
- **Reuse**: Same model as h-e1

---

### Gradient Flow Measurement

**Objective**: Measure gradient magnitude to spurious vs core features during early training (epochs 1-20).

**Feature Definition**:
- **Spurious features**: Background-related features (water/land texture, color)
- **Core features**: Bird-related features (shape, pose, wing pattern)

**Proxy Measurement** (implementation-feasible approach):
1. **Layer-wise gradient magnitude**:
   - For each normalization layer (BN or LN), measure mean gradient magnitude during backward pass
   - Log per epoch: `grad_norm = torch.norm(layer.weight.grad)`
   - Compare early-layer gradients (spurious-sensitive) vs late-layer gradients (core-sensitive)

2. **Group-stratified gradient analysis**:
   - Split validation set by spurious alignment:
     - **Majority group** (spurious-aligned): waterbird-water, landbird-land (95% of train)
     - **Minority group** (spurious-misaligned): waterbird-land, landbird-water (5% of train)
   - Compute loss gradient w.r.t. first conv layer features:
     - `grad_majority = torch.autograd.grad(loss_majority, first_conv_features)`
     - `grad_minority = torch.autograd.grad(loss_minority, first_conv_features)`
   - Measure gradient ratio: `spurious_amplification = ||grad_majority|| / ||grad_minority||`
   - **Hypothesis**: BN shows higher spurious amplification ratio than LN in epochs 1-20

3. **Per-batch spurious correlation strength**:
   - For each training batch, measure spurious correlation: `corr(y, background)`
   - Track per-batch loss and gradient magnitude
   - **Hypothesis**: BN loss decreases faster on high-spurious batches than low-spurious batches

**Primary Metric**: Gradient ratio (spurious/core) in early training (epochs 1-20)
- **Spurious gradient**: Mean gradient norm on majority group samples
- **Core gradient**: Mean gradient norm on minority group samples
- Compute per epoch for both architectures
- **Success criterion**: BN gradient ratio ≥ 20% higher than LN gradient ratio

---

### Training Configuration

**Controlled Variables** (same as h-e1):
- Learning rate: 0.01 (constant, no schedule)
- Batch size: 64
- Optimizer: SGD with momentum=0.9, weight_decay=1e-4
- Loss function: CrossEntropyLoss (no class reweighting)
- Epochs: 100 (measure gradients in epochs 1-20, full training for context)
- Random seeds: 10 (seeds 0-9 for statistical power)
- Device: CUDA if available, else CPU

**Training Loop with Gradient Logging**:
1. For each seed in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
   - Set global seed: `torch.manual_seed(seed)`, `np.random.seed(seed)`
   - Initialize model with He initialization
   - Train for 100 epochs
   - **On epochs 1-20**: Register backward hooks to measure gradient norms
   - Log metrics every epoch

**Metrics Logged Per Epoch**:
- Average accuracy (over all test samples)
- Worst-group accuracy (min accuracy across 4 groups)
- Per-group accuracy (4 values)
- Worst-group gap: `average_accuracy - worst_group_accuracy`
- Training loss (average over epoch)
- **Gradient metrics (epochs 1-20 only)**:
  - Mean gradient norm on majority group samples
  - Mean gradient norm on minority group samples
  - Gradient ratio: `grad_majority / grad_minority`
  - Per-layer gradient norms (first conv, first BN/LN, last BN/LN)

---

### Evaluation Protocol

**Primary Comparison**: Gradient ratio in early training (epochs 1-20)

1. For each architecture and each seed:
   - Compute mean gradient ratio across epochs 1-20: `mean_ratio = mean(grad_majority / grad_minority)`
   - Record per-epoch gradient ratios for visualization

2. Compute statistics across 10 seeds:
   - Mean gradient ratio for ResNet-BN (epochs 1-20)
   - Mean gradient ratio for ResNet-LN (epochs 1-20)
   - Ratio difference: `mean_ratio_BN - mean_ratio_LN`
   - Standard error of ratio difference

3. Statistical test:
   - Independent t-test (10 BN samples vs 10 LN samples)
   - Significance level: α = 0.05 (two-tailed)
   - Effect size: Cohen's d (mean difference / pooled std)

**Success Criterion**:
- BN gradient ratio ≥ 20% higher than LN gradient ratio AND
- p < 0.05 AND
- Cohen's d ≥ 0.5 (medium effect size)

**Falsification Criterion**:
- p > 0.05 OR
- BN gradient ratio < 10% higher than LN gradient ratio OR
- Cohen's d < 0.3 (small effect)

**Secondary Analysis**: Per-batch spurious correlation effect
- Correlate batch spurious correlation strength with batch loss
- Compare BN vs LN correlation coefficients
- **Expected**: BN shows stronger positive correlation (high spurious batches → lower loss)

---

## Expected Outcomes

### If Hypothesis Confirmed (SHOULD_WORK gate satisfied):
- BN amplification mechanism validated
- Mechanistic understanding of h-e1 result strengthened
- Evidence for batch-level spurious feature amplification
- Proceed to Phase 3 implementation planning for h-m1

### If Hypothesis Falsified (SHOULD_WORK gate failed):
- BN-LN gap difference (h-e1) exists but mechanism unsupported
- Alternative mechanisms:
  - Optimization dynamics (BN second-order effects on gradient descent)
  - Feature scale differences (BN normalizes differently than LN)
  - Batch composition effects (unrelated to spurious correlations)
- **Does NOT block Phase 5** (h-e1 foundation still valid)
- Weaken mechanistic claim in paper: "BN amplifies worst-group gaps (mechanism unclear)"

---

## Implementation Complexity Assessment

**Tier Estimate**: Tier 1.5 (Simple-to-Moderate)

**Rationale**:
- Standard dataset (reuse h-e1 Waterbirds loader)
- Standard architectures (reuse h-e1 ResNet-BN and ResNet-LN)
- Additional complexity: Gradient measurement via backward hooks
- No novel algorithms, but gradient logging adds ~100 LoC

**Estimated LoC**: ~450-550 lines
- Data loading: ~50 lines (reuse h-e1)
- Model definition: ~100 lines (reuse h-e1)
- Training loop with gradient hooks: ~150 lines (+50 from h-e1)
- Gradient analysis and logging: ~100 lines (new)
- Evaluation and statistical test: ~100 lines
- Plotting: ~50 lines

**Dependencies** (same as h-e1):
- torch, torchvision (core ML)
- wilds (dataset)
- numpy, scipy (statistics)
- matplotlib (plotting)
- tqdm (progress bars)

**Implementation Budget**:
- Low: 350 tokens (assumes maximum code reuse from h-e1)
- High: 550 tokens (includes gradient logging infrastructure)

---

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Gradient measurement noise (high variance) | Medium | Medium (weak signal) | Average over 10 seeds, smooth across 5-epoch windows |
| Spurious/core feature proxy invalid | Medium | High (measures wrong thing) | Validate: majority/minority group gradient should differ |
| Gradient vanishing in early layers | Low | Medium (cannot measure spurious features) | Use gradient norm (not raw gradients), log scale if needed |
| Computational overhead (gradient hooks) | Low | Low (training 2× slower) | Acceptable; measure gradients on validation set only (not train) |
| h-e1 code unavailable for reuse | Low | Low (re-implementation) | h-e1 codebase already validated in Phase 4 |

---

## Validation Checklist

Before marking h-m1 experiment design as COMPLETED, verify:

- [x] Dataset is real (not synthetic) — Waterbirds is standard benchmark
- [x] Sample size is statistically meaningful — 600 test samples, 10 seeds
- [x] Experiment measures hypothesis claim — gradient ratio (spurious/core)
- [x] Controlled variables match Phase 2B plan — LR, batch size, seeds
- [x] Success criterion is falsifiable — clear p-value and effect size thresholds
- [x] Tier 1.5 complexity is justified — gradient hooks add moderate complexity
- [x] Reuses h-e1 components — dataset, models, training loop (efficiency gain)

---

## Phase 3 Preview

**Archon Tasks** (Epic-level breakdown):
1. **EPIC-GRAD-HOOKS**: Implement backward hooks for gradient norm measurement
2. **EPIC-GROUP-SPLIT**: Split validation set by majority/minority groups
3. **EPIC-GRAD-LOG**: Log per-epoch gradient ratios (epochs 1-20)
4. **EPIC-GRAD-EVAL**: Compute gradient ratio statistics and t-test
5. **EPIC-VIZ**: Plot gradient ratio trajectories (BN vs LN, epochs 1-20)

**Reuse from h-e1**:
- Data loader (Waterbirds with group labels)
- Model definitions (ResNet-BN, ResNet-LN)
- Training loop scaffold (10 seeds, 100 epochs)
- Evaluation framework (per-group accuracy tracking)

**New Components**:
- Gradient measurement infrastructure (backward hooks)
- Group-stratified gradient analysis
- Spurious/core gradient ratio computation

---

## Research Context

**Related Work**:
- Sagawa et al. 2020 (Group DRO): Showed worst-group accuracy gap exists but did not analyze BN role
- Shen et al. 2021 (BN hurts worst-group accuracy): Observed BN-LN gap but no mechanistic explanation
- Ioffe & Szegedy 2015 (Batch Normalization): Batch-level statistics improve convergence but no analysis of spurious correlations

**Novel Contribution**:
- First gradient-level analysis of BN's role in spurious correlation learning
- Mechanistic explanation for h-e1 existence result
- Directly tests batch-level vs instance-level statistics hypothesis

**Open Question**: If BN amplifies batch-level spurious correlations, can we design a normalization layer that suppresses them (hybrid BN-LN, batch-conditional normalization)?

---

**Experiment Brief Status**: COMPLETED  
**Ready for Phase 3**: YES  
**Blocking Issues**: NONE  
**Prerequisite Status**: h-e1 VALIDATED (9.41pp gap difference, p < 0.001)
