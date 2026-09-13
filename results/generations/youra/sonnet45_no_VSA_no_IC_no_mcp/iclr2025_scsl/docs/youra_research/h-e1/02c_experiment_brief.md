# Phase 2C: Experiment Design Brief

**Generated**: 2026-08-24  
**Hypothesis ID**: h-e1  
**Hypothesis Type**: EXISTENCE  
**Gate**: MUST_WORK (foundation hypothesis, blocks Phase 5 if fails)  
**Archon Task ID**: c4f70e7d-cb8d-476c-9f74-91c168c072b0  
**Pipeline Project ID**: e434b9c6-e150-46c4-8cb5-1c8e857b014c

---

## Hypothesis Statement

**Title**: BN-LN Worst-Group Gap Difference Exists

**Statement**: ResNet-BN shows ≥5 percentage point higher worst-group accuracy gap than ResNet-LN when both reach 90% average accuracy on Waterbirds dataset.

**Causal Mechanism**: BN amplifies early spurious learning via batch-level statistics, while LN reduces spurious amplification via instance-level normalization. This manifests as measurably higher worst-group gap at matched average accuracy.

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

#### Architecture 1: ResNet-18-BN
- Base: torchvision ResNet-18 with Batch Normalization (default)
- Normalization layers: 8 BN layers (conv2_x through conv5_x, 2 per block)
- Pretrained: False (train from scratch)
- Initialization: He normal (kaiming_normal with fan_out, relu mode)
- Output: 2 classes (landbird, waterbird)

#### Architecture 2: ResNet-18-LN
- Base: torchvision ResNet-18 with Batch Normalization layers replaced by Layer Normalization
- Normalization layers: 8 LN layers (normalized_shape=[C, H, W] per feature map)
- Pretrained: False (train from scratch)
- Initialization: He normal (kaiming_normal with fan_out, relu mode)
- Output: 2 classes (landbird, waterbird)

**Implementation Note**: Replace `nn.BatchNorm2d(C)` with `nn.LayerNorm([C, H, W])` where H, W are feature map dimensions. Use `elementwise_affine=True` to match BN learnable parameters.

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
1. For each seed in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
   - Set global seed: `torch.manual_seed(seed)`, `np.random.seed(seed)`
   - Initialize model with He initialization
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

**Primary Comparison**:
1. For each architecture and each seed:
   - Identify epoch where average accuracy first reaches ≥90%
   - Record worst-group gap at that epoch
   - If 90% never reached, record gap at epoch 100 (and flag as incomplete)

2. Compute statistics across 10 seeds:
   - Mean worst-group gap for ResNet-BN at 90% avg accuracy
   - Mean worst-group gap for ResNet-LN at 90% avg accuracy
   - Gap difference: `mean_gap_BN - mean_gap_LN`
   - Standard error of gap difference

3. Statistical test:
   - Paired t-test (10 pairs: BN gap vs LN gap per seed)
   - Significance level: α = 0.05 (two-tailed)
   - Effect size: Cohen's d (mean difference / pooled std)

**Success Criterion**:
- Gap difference ≥ 5 percentage points AND
- p < 0.05 AND
- Cohen's d ≥ 0.8 (large effect size)

**Falsification Criterion**:
- p > 0.05 OR
- Gap difference < 3 percentage points OR
- Cohen's d < 0.5 (medium effect)

---

## Expected Outcomes

### If Hypothesis Confirmed (MUST_WORK gate satisfied):
- BN amplification mechanism supported
- Foundation for mechanism hypotheses (h-m1, h-m2) established
- Proceed to Phase 3 implementation planning for h-e1
- Unblock h-m1, h-m2, h-c1 for parallel execution

### If Hypothesis Falsified (MUST_WORK gate failed):
- Route to Phase 0 (fundamental flaw in main hypothesis)
- Re-examine: Is BN-LN difference real or optimization artifact?
- Alternative paths:
  - Test on CelebA (higher spurious correlation 95% vs Waterbirds 85%)
  - Test with LR schedule (does constant LR suppress BN effect?)
  - Measure earlier in training (epoch 20-40 instead of 90% accuracy)

---

## Implementation Complexity Assessment

**Tier Estimate**: Tier 1 (Simple)

**Rationale**:
- Standard dataset (available via `wilds` library)
- Standard architecture (torchvision ResNet-18)
- One architectural change: BN → LN layer replacement
- No novel algorithms or custom training procedures
- Metrics are standard accuracy measurements with group splits

**Estimated LoC**: ~300-400 lines
- Data loading: ~50 lines
- Model definition: ~100 lines (BN and LN variants)
- Training loop: ~100 lines
- Evaluation and logging: ~100 lines
- Plotting and statistical test: ~50 lines

**Dependencies**:
- torch, torchvision (core ML)
- wilds (dataset)
- numpy, scipy (statistics)
- matplotlib (plotting)
- tqdm (progress bars)

---

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| 90% avg accuracy never reached | Medium | High (cannot measure gap at target) | Fallback: measure gap at epoch 80 or best avg accuracy |
| Training speed confound (BN trains faster) | Medium | High (confounds mechanism) | Accuracy-matched comparison eliminates confound |
| Statistical power insufficient (high variance) | Low | Medium (false negative) | 10 seeds provides 80% power for 2pp effect |
| LN convergence instability | Low | Medium (LN fails to train) | Monitor loss curves, add gradient clipping if needed |
| Dataset download failure | Low | Low (blocking) | Cache dataset locally, verify MD5 checksum |

---

## Validation Checklist

Before marking h-e1 experiment design as COMPLETED, verify:

- [ ] Dataset is real (not synthetic) — Waterbirds is standard benchmark ✓
- [ ] Sample size is statistically meaningful — 600 test samples per architecture ✓
- [ ] Experiment measures hypothesis claim — worst-group gap at matched accuracy ✓
- [ ] Controlled variables match Phase 2B plan — LR, batch size, seeds ✓
- [ ] Success criterion is falsifiable — clear p-value and effect size thresholds ✓
- [ ] Tier 1 complexity is justified — standard components, one BN→LN change ✓

---

## Next Steps (Phase 3)

1. Initialize Archon project for h-e1 with this experiment brief
2. Generate PRD (Product Requirements Document):
   - User story: "As a researcher, I need to train ResNet-BN and ResNet-LN on Waterbirds and compare worst-group gaps at 90% average accuracy"
   - Acceptance criteria: Gap difference ≥5pp, p<0.05, Cohen's d≥0.8
3. Generate Architecture document:
   - Module 1: Data loader (Waterbirds with group labels)
   - Module 2: Model definitions (ResNet-BN, ResNet-LN)
   - Module 3: Training loop (10 seeds, 100 epochs)
   - Module 4: Evaluation and statistical test
4. Break into Epic-level Archon tasks:
   - EPIC-DATA: Waterbirds download and preprocessing
   - EPIC-MODEL: ResNet-BN and ResNet-LN implementations
   - EPIC-TRAIN: Training loop with metric logging
   - EPIC-EVAL: Gap comparison and t-test

---

**Experiment Brief Status**: COMPLETED  
**Ready for Phase 3**: YES  
**Blocking Issues**: NONE
