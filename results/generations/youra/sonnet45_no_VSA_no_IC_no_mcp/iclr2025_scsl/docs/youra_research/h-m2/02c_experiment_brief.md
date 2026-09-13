# Phase 2C: Experiment Design Brief

**Generated**: 2026-08-25  
**Hypothesis ID**: h-m2  
**Hypothesis Type**: MECHANISM  
**Gate**: SHOULD_WORK (mechanism hypothesis, does NOT block Phase 5 if fails)  
**Archon Task ID**: 477802a1-5780-457f-9d7b-a6cf7081730f  
**Pipeline Project ID**: e434b9c6-e150-46c4-8cb5-1c8e857b014c

---

## Hypothesis Statement

**Title**: Attention Enables Mid-Training Correction

**Statement**: ViT or ResNet-CBAM shows steeper worst-group gap reduction slope (≥0.3pp/epoch more negative) from epoch 20-50 than ResNet-BN on Waterbirds.

**Causal Mechanism**: Attention mechanisms enable mid-training correction of spurious features via global (ViT) or channel-wise (CBAM) feature re-weighting. This manifests as steeper worst-group gap reduction during mid-training phase compared to ResNet-BN.

**Prerequisites**: h-e1 (EXISTENCE hypothesis must be validated first)

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

---

### Baseline Architectures

#### Architecture 1: ResNet-18-BN (Control)
- Base: torchvision ResNet-18 with Batch Normalization (default)
- Normalization layers: 8 BN layers (conv2_x through conv5_x, 2 per block)
- Pretrained: False (train from scratch)
- Initialization: He normal (kaiming_normal with fan_out, relu mode)
- Output: 2 classes (landbird, waterbird)
- **Role**: Control baseline (no attention)

#### Architecture 2: ResNet-18-CBAM
- Base: torchvision ResNet-18 with CBAM (Convolutional Block Attention Module) added
- CBAM insertion: After each residual block (4 CBAM modules total)
- CBAM structure: Channel attention (avg+max pool → MLP → sigmoid) + Spatial attention (channel avg+max → Conv → sigmoid)
- Normalization: Batch Normalization (same as control)
- Pretrained: False (train from scratch)
- Initialization: He normal for ResNet layers, Xavier normal for CBAM layers
- Output: 2 classes (landbird, waterbird)
- **Role**: Test channel+spatial attention with local receptive field preserved

#### Architecture 3: ViT-Small
- Base: Vision Transformer Small (patch_size=16, hidden_dim=384, depth=12, heads=6)
- Input: 224×224 images → 196 patches (14×14)
- Normalization: LayerNorm (standard ViT)
- Pretrained: False (train from scratch)
- Initialization: Xavier uniform for linear layers, normal for positional embeddings
- Output: 2 classes (landbird, waterbird)
- **Role**: Test global self-attention (confounded: global architecture + parameter count difference)

**Implementation Notes**:
- CBAM code available in standard implementations (e.g., timm library or custom module)
- ViT-Small from timm: `timm.create_model('vit_small_patch16_224', pretrained=False, num_classes=2)`
- CBAM preserves ResNet local inductive bias; ViT has global receptive field from layer 1

---

### Training Configuration

**Controlled Variables** (from Phase 2B):
- Learning rate: 0.01 (constant, no schedule)
- Batch size: 64
- Optimizer: SGD with momentum=0.9, weight_decay=1e-4
- Loss function: CrossEntropyLoss (no class reweighting)
- Epochs: 100
- Random seeds: 10 (seeds 0-9 for statistical power)
- Device: CUDA if available, else CPU

**Training Loop**:
1. For each architecture in [ResNet-BN, ResNet-CBAM, ViT-Small]:
   - For each seed in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
     - Set global seed: `torch.manual_seed(seed)`, `np.random.seed(seed)`
     - Initialize model with architecture-specific initialization
     - Train for 100 epochs
     - Log metrics every epoch

**Metrics Logged Per Epoch**:
- Average accuracy (over all test samples)
- Worst-group accuracy (min accuracy across 4 groups)
- Per-group accuracy (4 values: landbird-land, landbird-water, waterbird-land, waterbird-water)
- Worst-group gap: `average_accuracy - worst_group_accuracy`
- Training loss (average over epoch)

---

### Evaluation Protocol

**Primary Analysis: Slope Comparison (Epochs 20-50)**

1. **Per-Seed Slope Computation**:
   - For each architecture and each seed:
     - Extract worst-group gap trajectory for epochs 20-50 (31 data points)
     - Fit linear regression: `gap = β₀ + β₁ × epoch`
     - Record slope coefficient β₁ (units: percentage points per epoch)
     - Negative slope = gap closing; steeper negative = faster correction

2. **Aggregate Statistics**:
   - For each architecture:
     - Compute mean slope across 10 seeds: `mean_slope`
     - Compute 95% confidence interval via bootstrap (1000 resamples) or analytical CI from OLS
     - Record: `[mean_slope, CI_lower, CI_upper]`

3. **Comparison Test**:
   - Compare ResNet-CBAM vs ResNet-BN:
     - Success if CBAM CI does NOT overlap with BN CI AND `mean_slope_CBAM < mean_slope_BN - 0.3`
   - Compare ViT vs ResNet-BN:
     - Success if ViT CI does NOT overlap with BN CI AND `mean_slope_ViT < mean_slope_BN - 0.3`

4. **Effect Size**:
   - Cohen's d for slope difference: `(mean_slope_attention - mean_slope_BN) / pooled_std`
   - Target: d ≥ 0.8 (large effect)

**Success Criterion**:
- (ResNet-CBAM OR ViT) shows steeper negative slope than ResNet-BN by ≥0.3pp/epoch AND
- Non-overlapping 95% CIs AND
- Cohen's d ≥ 0.8

**Falsification Criterion**:
- Both CBAM and ViT CIs overlap with ResNet-BN CI OR
- Slope difference < 0.2pp/epoch OR
- Cohen's d < 0.5 (medium effect)

**Interpretation Matrix**:

| CBAM Result | ViT Result | Interpretation |
|-------------|-----------|----------------|
| Success | Success | Attention mechanism contributes to correction |
| Success | Fail | Channel attention sufficient; global architecture not required |
| Fail | Success | ViT correction due to global architecture, NOT attention alone |
| Fail | Fail | Attention does NOT enable mid-training correction; hypothesis falsified |

---

### Secondary Analysis: Trajectory Visualization

**Purpose**: Confirm slope difference is not driven by outlier epochs

**Method**:
1. Plot mean worst-group gap trajectory (± std error) for each architecture
2. Highlight epochs 20-50 (analysis window)
3. Overlay fitted regression lines for epochs 20-50
4. Visual inspection: trajectory smoothness, outlier epochs, phase transitions

**Expected Pattern if Hypothesis True**:
- ResNet-BN: slow gap reduction (shallow slope) in epochs 20-50
- ResNet-CBAM/ViT: steep gap reduction (steep negative slope) in epochs 20-50
- Trajectories diverge most clearly in mid-training window

---

## Expected Outcomes

### If Hypothesis Confirmed (SHOULD_WORK gate satisfied):
- Attention mechanism contributes to spurious correlation correction
- Inform architecture selection: prefer attention-augmented models for spurious correlation robustness
- Mechanism understanding: attention enables feature re-weighting during mid-training
- Proceed to Phase 3 implementation planning for h-m2

### If Hypothesis Partially Confirmed (ViT succeeds, CBAM fails):
- Weaken claim: "Global architecture enables correction, not attention alone"
- Confound acknowledged: ViT differs from ResNet in multiple dimensions
- Interpretation: global receptive field or patch-based processing drives correction
- Document limitation in Phase 6 paper

### If Hypothesis Falsified (SHOULD_WORK gate failed):
- Attention does NOT enable mid-training correction under these conditions
- Alternative explanations:
  - Correction occurs in different epoch range (test epochs 50-80)
  - Attention effect requires learning rate schedule (constant LR suppresses it)
  - Correction is optimization artifact, not architectural feature
- Does NOT block Phase 5 (SHOULD_WORK hypothesis)
- Document null result (publishable finding)

---

## Implementation Complexity Assessment

**Tier Estimate**: Tier 1 (Simple)

**Rationale**:
- Standard dataset (same as h-e1: Waterbirds via `wilds`)
- Standard architectures (ResNet-18, ViT-Small available in timm)
- CBAM is well-documented module (~50 lines)
- Slope computation via standard linear regression (scipy.stats.linregress)
- No novel algorithms or custom training procedures

**Estimated LoC**: ~400-500 lines
- Data loading: ~50 lines (reuse from h-e1)
- Model definitions: ~150 lines (ResNet-BN, ResNet-CBAM, ViT-Small)
- CBAM module: ~50 lines
- Training loop: ~100 lines (reuse from h-e1)
- Evaluation and slope computation: ~100 lines
- Plotting and statistical tests: ~50 lines

**Dependencies**:
- torch, torchvision (core ML)
- timm (ViT-Small, potentially CBAM)
- wilds (dataset)
- numpy, scipy (statistics, linear regression)
- matplotlib (plotting)
- tqdm (progress bars)

---

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| ViT fails to converge (instability) | Medium | High (cannot test ViT branch) | Monitor loss curves, add gradient clipping if needed, reduce LR to 0.001 for ViT if default fails |
| CBAM implementation bug | Low | Medium (wrong conclusion) | Validate CBAM output shapes, test on CIFAR-10 first, compare with reference implementation |
| Epoch 20-50 window misses correction phase | Medium | Medium (false negative) | Plot full trajectories, test alternative windows (30-60, 40-70) in secondary analysis |
| High variance across seeds (wide CIs) | Medium | Medium (overlapping CIs) | 10 seeds provides 80% power for 0.3pp/epoch effect; accept wider uncertainty if needed |
| ResNet-CBAM training instability | Low | Medium (CBAM fails) | Monitor gradient norms, add gradient clipping, reduce CBAM attention strength if needed |

---

## Validation Checklist

Before marking h-m2 experiment design as COMPLETED, verify:

- [x] Dataset is real (not synthetic) — Waterbirds is standard benchmark ✓
- [x] Sample size is statistically meaningful — 600 test samples × 100 epochs × 10 seeds ✓
- [x] Experiment measures hypothesis claim — slope comparison in epochs 20-50 ✓
- [x] Controlled variables match Phase 2B plan — LR, batch size, seeds ✓
- [x] Success criterion is falsifiable — clear CI non-overlap + effect size thresholds ✓
- [x] Tier 1 complexity is justified — standard architectures, CBAM is ~50 lines ✓
- [x] Ablation isolates attention effect — CBAM preserves local architecture ✓
- [x] Confound acknowledged — ViT success may be global architecture, not attention ✓

---

## Next Steps (Phase 3)

1. Initialize Archon project for h-m2 with this experiment brief
2. Generate PRD (Product Requirements Document):
   - User story: "As a researcher, I need to train ResNet-BN, ResNet-CBAM, and ViT-Small on Waterbirds and compare worst-group gap reduction slopes during epochs 20-50"
   - Acceptance criteria: Slope difference ≥0.3pp/epoch, non-overlapping CIs, Cohen's d≥0.8
3. Generate Architecture document:
   - Module 1: Data loader (reuse from h-e1)
   - Module 2: Model definitions (ResNet-BN, ResNet-CBAM, ViT-Small)
   - Module 3: CBAM attention module
   - Module 4: Training loop (3 architectures × 10 seeds × 100 epochs)
   - Module 5: Slope computation and statistical test
4. Break into Epic-level Archon tasks:
   - EPIC-DATA: Waterbirds loader (reuse h-e1)
   - EPIC-MODEL-CBAM: ResNet-CBAM implementation
   - EPIC-MODEL-VIT: ViT-Small integration
   - EPIC-TRAIN: Training loop for 3 architectures
   - EPIC-EVAL: Slope regression and CI comparison

---

**Experiment Brief Status**: COMPLETED  
**Ready for Phase 3**: YES (after h-e1 validation completes)  
**Blocking Issues**: NONE  
**Prerequisite Status**: h-e1 validation completed (gate PASSED)
