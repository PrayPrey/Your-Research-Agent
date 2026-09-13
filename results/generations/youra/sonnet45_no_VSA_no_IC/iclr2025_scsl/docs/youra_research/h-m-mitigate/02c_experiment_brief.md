# Experiment Brief: Spatial Gradient Regularization for Spurious Mitigation

**Hypothesis ID:** h-m-mitigate  
**Type:** Mechanism (Mitigation)  
**Gate:** SHOULD_WORK  
**Prerequisites:** h-m-integrated (COMPLETED)  
**Generated:** 2026-08-20  

---

## 1. Research Context

### 1.1 Hypothesis Statement

Under training with spatial gradient regularization (penalizing gradient divergence in GradCAM-identified spurious regions), if we apply adaptive penalty scaling, then worst-group accuracy improves by ≥5% over GroupDRO because regularization forces model reliance on core features.

### 1.2 Background & Motivation

**Prior Work:**
- GroupDRO (Sagawa et al. 2019): Minimizes worst-group training loss via reweighting, achieves 85-88% WGA on Waterbirds but requires group annotations at train time
- JTT (Liu et al. 2021): Two-stage training identifies then upweights error-prone examples, achieves ~88% WGA
- SCER (2025): Embedding-space regularization, ~90% WGA (code unavailable)
- h-m-integrated: Validated that gradient abnormality (GAIA-Z) detects minority groups with |ρ|>0.7 correlation to WGA

**Research Gap:**
- Existing methods operate on loss reweighting (GroupDRO/JTT) or embedding space (SCER)
- No prior work uses gradient-space regularization to mitigate spurious correlations
- h-m-integrated demonstrated diagnostic capability; this hypothesis tests intervention capability

**Novelty:**
- First gradient-based spatial regularization for spurious mitigation
- Automatic spurious region localization via GradCAM difference maps (no feature engineering)
- Unified framework: same abnormality mechanism for detection (h-m-integrated) and mitigation

### 1.3 Success Criteria (PoC Direction-Based)

**Primary (MNIST+Color toy validation):**
- WGA improvement ≥10% over baseline when spurious region masked
- Color-only accuracy ≥ baseline+10% (validates mechanism)
- Digit-only accuracy ≤ baseline-5% (confirms spatial targeting)

**Primary (Waterbirds real-world validation):**
- WGA ≥ GroupDRO+5% (absolute percentage points)
- Average accuracy drop ≤2% (no catastrophic overfitting to minority)

**Secondary:**
- GradCAM heatmap shift: spurious region attention decreases ≥20% (validates mechanism)
- Statistical significance: p<0.05 via bootstrap test (n=1000 resamples)

**Gate Logic:**
- SHOULD_WORK: If MNIST passes but Waterbirds fails → reframe as detection-only (Tier 3)
- If MNIST fails → mechanism fundamentally broken, abandon mitigation claim

---

## 2. Experimental Design

### 2.1 Dataset Specifications

#### 2.1.1 MNIST+Color (Toy Validation)

**Purpose:** Controlled validation of spatial regularization mechanism

**Construction:**
- Base: MNIST digits (60k train, 10k test) via torchvision.datasets.MNIST
- Spurious feature: Color channel correlation (90% correlation with digit class)
- Groups: 4 groups (digit-color majority/minority)

**Preprocessing:**
1. Convert grayscale to RGB
2. Assign colors: Even digits (0,2,4,6,8) → Red (90% of samples), Odd digits → Green (90% of samples)
3. Minority groups: Even-Green (10%), Odd-Red (10%)

**Splits:**
- Train: 54k (random 90% of original train)
- Val: 6k (random 10% of original train)
- Test: 10k (original test split, balanced groups)

**Type:** programmatic-api (real data with synthetic coloring)

**Storage:**
- Cache: `~/.cache/mnist_color_90pct/`
- Metadata: CSV with (image_id, digit, color, group, split)

#### 2.1.2 Waterbirds (Real-World Validation)

**Purpose:** Real-world spurious correlation benchmark

**Source:** 
- CUB-200-2011 birds + Places365 backgrounds
- Download: https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz
- Alternative: `wilds.get_dataset('waterbirds')` (auto-download)

**Statistics:**
- Train: 4795 images (90% correlation: waterbird-water, landbird-land)
- Val: 1199 images (balanced groups)
- Test: 5794 images (balanced groups)
- Groups: 4 (waterbird-water, waterbird-land, landbird-water, landbird-land)

**Preprocessing:**
- Resize: 224×224
- Normalization: ImageNet stats (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
- Augmentation (train only): RandomHorizontalFlip(p=0.5)

**Type:** standard (established benchmark)

**Storage:**
- Path: `./datasets/waterbirds/waterbird_complete95_forest2water2/`
- Metadata: `metadata.csv` (columns: img_id, img_filename, y, split, place, place_filename)

**Validation:**
- Verify 4 groups present in metadata
- Check train correlation: ≥90% majority groups
- Confirm test balance: each group ≥20% of test set

### 2.2 Model Architecture

#### 2.2.1 MNIST+Color

**Backbone:** ResNet-18 (torchvision.models.resnet18)
- Input: 3×28×28 RGB
- Output: 10 classes (digits)
- Pretrained: False (train from scratch)

**Rationale:** Simple enough for toy validation, matches architecture family of Waterbirds model

#### 2.2.2 Waterbirds

**Backbone:** ResNet-50 (torchvision.models.resnet50)
- Input: 3×224×224 RGB
- Output: 2 classes (waterbird vs landbird)
- Pretrained: True (ImageNet weights)

**Rationale:** 
- Standard for Waterbirds benchmark (all baselines use ResNet-50)
- Enables direct comparison to GroupDRO (Sagawa et al. 2019)

**GradCAM Target Layer:**
- ResNet-50: `model.layer4[-1]` (last conv block before pooling)
- Justification: Highest spatial resolution with semantic features

### 2.3 Training Configuration

#### 2.3.1 Baseline (ERM)

**MNIST+Color:**
- Optimizer: SGD (lr=0.01, momentum=0.9, weight_decay=1e-4)
- Batch size: 128
- Epochs: 50
- Scheduler: ReduceLROnPlateau (patience=5, factor=0.1)
- Loss: CrossEntropyLoss

**Waterbirds:**
- Optimizer: SGD (lr=0.001, momentum=0.9, weight_decay=1e-4)
- Batch size: 128
- Epochs: 300
- Scheduler: None (fixed LR per GroupDRO baseline)
- Loss: CrossEntropyLoss

#### 2.3.2 Spatial Gradient Regularization

**Core Innovation:** Penalize gradient divergence in spurious regions identified by GradCAM difference maps

**Algorithm:**
1. **Spurious Region Identification (per batch):**
   - Compute GradCAM for majority group samples (waterbird-water, landbird-land)
   - Compute GradCAM for minority group samples (waterbird-land, landbird-water)
   - Difference map: `D = |GradCAM_majority - GradCAM_minority|`
   - Spurious mask: `M_spurious = (D > percentile(D, 75))`  # Top 25% divergent regions

2. **Spatial Regularization Loss:**
   ```
   L_total = L_CE + λ * L_spatial
   
   where:
   L_spatial = mean(gradient_variance[M_spurious])
   gradient_variance = var(gradients, dim=channel)  # Channel-wise variance
   ```

3. **Adaptive Penalty Scaling:**
   - λ initialized to 0.01
   - Update every epoch: `λ_new = λ_old * exp(0.1 * (WGA_gap))`
   - WGA_gap = (majority_accuracy - minority_accuracy) on validation set
   - Clamp: λ ∈ [0.001, 1.0]

**Hyperparameters (tuned on validation set):**
- λ_init: {0.001, 0.01, 0.1}
- Percentile threshold: {75, 85, 95} (for spurious mask)
- GradCAM update frequency: {every batch, every 10 batches}

**Efficiency:**
- GradCAM computed on subset of batch (32 samples max) to reduce overhead
- Gradient computation: backward hook on target layer (no additional forward pass)

#### 2.3.3 Baseline Methods (Waterbirds Only)

**GroupDRO (Sagawa et al. 2019):**
- Implementation: https://github.com/kohpangwei/group_DRO
- Config: `--reweight_groups --robust --gamma 0.1 --generalization_adjustment 0`
- Hyperparameters: lr=0.001, batch_size=128, weight_decay=1e-4, epochs=300
- Expected WGA: 85-88% (from paper)

**ERM (Empirical Risk Minimization):**
- Standard cross-entropy loss without reweighting
- Same hyperparameters as GroupDRO (for fair comparison)
- Expected WGA: 60-75% (high average, poor worst-group)

### 2.4 Evaluation Protocol

#### 2.4.1 Metrics

**Primary:**
- Worst-Group Accuracy (WGA): `min(acc_group0, acc_group1, acc_group2, acc_group3)`
- Average Accuracy: `mean(acc_all_samples)`
- WGA Gap: `(majority_acc - minority_acc)`

**Secondary (Mechanism Validation):**
- GradCAM heatmap shift: Compare spurious region attention before/after regularization
  - Metric: `mean(GradCAM[M_spurious])` for minority samples
  - Expected: ≥20% decrease (attention shifts from spurious to core features)
- Feature attribution: Ablation study (mask spurious regions, measure accuracy drop)

**Statistical Testing:**
- Bootstrap test (n=1000 resamples) for WGA comparison
- Null hypothesis: WGA_spatial ≤ WGA_GroupDRO
- Report: mean ± std, p-value

#### 2.4.2 Experiment Sequence

**Phase 1: MNIST+Color Toy Validation (Budget: 2 GPU-hours)**

1. **Baseline ERM:** Train 5 random seeds, measure WGA
2. **Global Regularization:** Penalize all gradients (no spatial masking)
   - Validates that spatial targeting matters
3. **Spatial Spurious-Region Regularization:** Penalize gradients in M_spurious
   - Expected: WGA ≥ baseline+10%
4. **Spatial Core-Region Regularization:** Penalize gradients in M_core (inverse mask)
   - Expected: WGA ≤ baseline-5% (validates direction)
5. **Ablation:** Color-only test set (mask digit), Digit-only test set (mask color)
   - Validates mechanism: spurious regularization should increase digit-only accuracy

**Success Gate:** If spatial spurious-region WGA < baseline+10% → mechanism fails → PIVOT to detection-only

**Phase 2: Waterbirds Real-World Validation (Budget: 10 GPU-hours)**

1. **Baseline ERM:** Train 5 random seeds, measure WGA (expected: 60-75%)
2. **GroupDRO Baseline:** Train with official implementation (expected: 85-88%)
3. **Spatial Gradient Regularization:** Train 5 random seeds
   - Hyperparameter search: 3 λ_init × 3 percentile thresholds = 9 configs
   - Select best config on validation WGA
4. **Statistical Test:** Bootstrap comparison vs GroupDRO
5. **Mechanism Validation:** GradCAM heatmap analysis (10 samples per group)

**Success Gate:** If WGA < GroupDRO+5% → PIVOT to detection-only (Tier 3 positioning)

---

## 3. Implementation Plan

### 3.1 Code Structure

```
experiments/h_m_mitigate/
├── data/
│   ├── mnist_color.py          # MNIST+Color dataset loader
│   ├── waterbirds.py           # Waterbirds dataset loader
│   └── transforms.py           # Augmentation pipelines
├── models/
│   ├── resnet.py               # ResNet-18/50 wrappers
│   └── gradcam.py              # GradCAM implementation (from pytorch-grad-cam)
├── trainers/
│   ├── erm_trainer.py          # Baseline ERM
│   ├── groupdro_trainer.py     # GroupDRO baseline (wrapper)
│   └── spatial_reg_trainer.py  # Spatial gradient regularization
├── utils/
│   ├── metrics.py              # WGA, average accuracy, bootstrap test
│   ├── visualization.py        # GradCAM heatmap plotting
│   └── logging.py              # Weights & Biases integration
├── configs/
│   ├── mnist_color.yaml        # MNIST+Color hyperparameters
│   └── waterbirds.yaml         # Waterbirds hyperparameters
├── scripts/
│   ├── train_mnist.sh          # Phase 1 experiments
│   └── train_waterbirds.sh     # Phase 2 experiments
└── run_experiment.py           # Main entry point
```

### 3.2 Key Dependencies

**Core:**
- PyTorch 2.0+
- torchvision 0.15+
- pytorch-grad-cam (https://github.com/jacobgil/pytorch-grad-cam)

**Data:**
- wilds (for Waterbirds dataset)
- pandas (metadata handling)

**Evaluation:**
- scikit-learn (bootstrap resampling)
- scipy (statistical tests)

**Logging:**
- wandb (experiment tracking)
- matplotlib/seaborn (visualization)

### 3.3 Computational Requirements

**MNIST+Color (Phase 1):**
- GPU: 1× NVIDIA GPU (≥8GB VRAM)
- Time: ~2 hours (5 seeds × 50 epochs × 4 conditions)
- Storage: ~500MB (cached datasets + checkpoints)

**Waterbirds (Phase 2):**
- GPU: 1× NVIDIA GPU (≥16GB VRAM preferred for batch_size=128)
- Time: ~10 hours (5 seeds × 300 epochs × 3 methods)
- Storage: ~5GB (dataset + checkpoints)

**Total Budget:** 12 GPU-hours

---

## 4. Expected Results & Validation

### 4.1 MNIST+Color (Toy Validation)

**Baseline ERM:**
- Average Accuracy: ~98%
- WGA: ~60% (minority groups fail due to spurious color correlation)

**Spatial Spurious-Region Regularization:**
- Average Accuracy: ~96% (slight drop acceptable)
- WGA: ~70% (≥10% improvement over baseline)
- Color-only accuracy: ~50% (random guess, validates spurious suppression)
- Digit-only accuracy: ~95% (validates core feature learning)

**Control (Spatial Core-Region Regularization):**
- WGA: ~50% (worse than baseline, validates direction)

### 4.2 Waterbirds (Real-World Validation)

**Baseline ERM:**
- Average Accuracy: 95-97%
- WGA: 60-75%

**GroupDRO:**
- Average Accuracy: 90-92%
- WGA: 85-88%

**Spatial Gradient Regularization (Target):**
- Average Accuracy: 88-92% (≤2% drop from GroupDRO)
- WGA: 90-93% (≥5% improvement over GroupDRO)
- Bootstrap p-value: <0.05

**Mechanism Validation:**
- GradCAM attention shift: ≥20% reduction in spurious regions (background)
- Minority group samples: Attention shifts from background to bird features

### 4.3 Failure Modes & Fallback

**Failure Mode 1: MNIST WGA < baseline+10%**
- Diagnosis: Spatial regularization mechanism fundamentally broken
- Action: ABANDON mitigation claim, reframe h-m-mitigate as negative result
- Impact: Thesis positioning becomes detection-only (Tier 3)

**Failure Mode 2: MNIST passes, Waterbirds WGA < GroupDRO+5%**
- Diagnosis: Mechanism works in toy setting but not real-world complexity
- Action: PIVOT to detection-only contribution, position regularization as future work
- Impact: Tier 3 positioning, acknowledge limitation in paper

**Failure Mode 3: Average accuracy drop >5%**
- Diagnosis: Overfitting to minority groups (opposite of ERM problem)
- Action: Adjust λ_init tuning range, add average accuracy constraint to adaptive scaling
- Impact: Re-run Phase 2 with revised hyperparameters

---

## 5. Baseline Comparison

### 5.1 GroupDRO (Sagawa et al. 2019)

**Approach:** Minimize worst-group training loss via group reweighting

**Strengths:**
- Proven effective: 85-88% WGA on Waterbirds
- Simple objective: max-min optimization over groups
- Open-source implementation: https://github.com/kohpangwei/group_DRO

**Limitations:**
- Requires group annotations at train time (not always available)
- Two hyperparameters: γ (adjustment), step_size (reweighting rate)
- No diagnostic capability (cannot detect spurious features without annotations)

**Comparison to h-m-mitigate:**
- GroupDRO = loss reweighting, h-m-mitigate = gradient regularization
- GroupDRO needs annotations, h-m-mitigate discovers spurious regions via GradCAM
- h-m-mitigate provides both detection (h-m-integrated) and mitigation in unified framework

### 5.2 JTT (Liu et al. 2021)

**Approach:** Two-stage training: (1) identify error-prone examples, (2) upweight them

**Performance:** ~88% WGA on Waterbirds

**Limitations:**
- Two-stage training (inefficient)
- Requires validation set to identify error-prone examples
- No interpretability (does not explain why samples are error-prone)

**Comparison to h-m-mitigate:**
- JTT = sample reweighting, h-m-mitigate = gradient regularization
- JTT black-box, h-m-mitigate interpretable (GradCAM shows spurious regions)

### 5.3 SCER (2025)

**Approach:** Embedding-space regularization for spurious mitigation

**Performance:** ~90% WGA (estimated, code unavailable)

**Limitations:**
- Code not released (cannot reproduce)
- Operates on embedding space (different intervention point)

**Comparison to h-m-mitigate:**
- SCER = embedding regularization, h-m-mitigate = gradient regularization
- Complementary intervention points (could be combined)
- h-m-mitigate reproducible, SCER is not

---

## 6. Risk Mitigation

### 6.1 Key Assumptions

**A1: Minority groups ≥60% correctly classified**
- Risk: If <60%, GradCAM highlights spurious (not core) features
- Detection: Monitor minority classification accuracy during training
- Mitigation: Fall back to global gradient regularization (no spatial masking)

**A2: Percentile normalization (75th) avoids majority bias**
- Risk: Penalty too weak on minority groups if threshold too high
- Detection: Compare penalty magnitudes across groups (should be similar)
- Mitigation: Hyperparameter search over {75, 85, 95} percentile thresholds

**A3: Regularization reduces spurious reliance, not just smooths gradients**
- Risk: WGA improves but mechanism is gradient smoothing (not feature shift)
- Detection: GradCAM heatmap analysis + ablation study (color-only/digit-only)
- Mitigation: If mechanism fails, MNIST toy experiment detects early (Phase 1 gate)

### 6.2 Computational Constraints

**Risk: GradCAM overhead slows training by >2×**
- Mitigation: Compute GradCAM on subset of batch (32 samples max)
- Fallback: Update GradCAM every N batches instead of every batch

**Risk: Hyperparameter search exceeds 10 GPU-hour budget**
- Mitigation: Phase 1 (MNIST) selects λ_init range, Phase 2 searches only 3 values
- Fallback: Use validation WGA for early stopping (halt poor configs at epoch 100)

---

## 7. Deliverables

### 7.1 Code Artifacts

- [ ] MNIST+Color dataset loader with 90% correlation
- [ ] Waterbirds dataset loader (wilds integration)
- [ ] Spatial gradient regularization trainer (with adaptive λ)
- [ ] GradCAM implementation (pytorch-grad-cam wrapper)
- [ ] GroupDRO baseline wrapper (official repo integration)
- [ ] Evaluation scripts (WGA, bootstrap test, heatmap visualization)
- [ ] Experiment configs (YAML files for reproducibility)

### 7.2 Experimental Outputs

- [ ] MNIST+Color results: 4 conditions × 5 seeds = 20 models
- [ ] Waterbirds results: 3 methods × 5 seeds = 15 models
- [ ] Statistical analysis: bootstrap p-values, mean±std tables
- [ ] Visualizations: GradCAM heatmaps (before/after regularization)
- [ ] Ablation study: color-only/digit-only accuracy tables

### 7.3 Documentation

- [ ] Training logs (wandb dashboards)
- [ ] Hyperparameter search results
- [ ] Failure mode analysis (if applicable)
- [ ] Reproducibility guide (README with exact commands)

---

## 8. Timeline

**Phase 1: MNIST+Color Toy Validation (Days 1-2)**
- Day 1: Implement dataset loader, spatial regularization trainer
- Day 2: Run 4 conditions × 5 seeds, analyze results, gate decision

**Phase 2: Waterbirds Real-World Validation (Days 3-7)** (assuming Phase 1 passes)
- Day 3: Setup Waterbirds dataset, integrate GroupDRO baseline
- Day 4-5: Hyperparameter search (9 configs)
- Day 6: Train best config × 5 seeds, run GroupDRO baseline
- Day 7: Statistical analysis, GradCAM visualization, finalize report

**Total Duration:** 7 days (assumes serial execution, no parallelization)

---

## 9. Success Metrics Summary

| Metric | Threshold | Priority |
|--------|-----------|----------|
| MNIST WGA improvement | ≥10% over baseline | MUST_WORK (Phase 1 gate) |
| MNIST color-only accuracy | ≥baseline+10% | SHOULD_WORK (mechanism validation) |
| Waterbirds WGA | ≥GroupDRO+5% | SHOULD_WORK (h-m-mitigate gate) |
| Average accuracy drop | ≤2% | SHOULD_WORK (no catastrophic overfitting) |
| GradCAM attention shift | ≥20% reduction in spurious regions | NICE_TO_HAVE (interpretability) |
| Statistical significance | p<0.05 | SHOULD_WORK (rigor) |

**Gate Decision Tree:**
```
MNIST WGA < baseline+10% → ABANDON mitigation, reframe as negative result
├─ MNIST passes, Waterbirds WGA < GroupDRO+5% → PIVOT to detection-only (Tier 3)
└─ Both pass → SUCCESS, proceed to Phase 4 implementation
```

---

## 10. References

**Baselines:**
- Sagawa et al. (2019): Distributionally Robust Neural Networks (GroupDRO)
- Liu et al. (2021): Just Train Twice (JTT)
- SCER (2025): Embedding-space regularization (code unavailable)

**Datasets:**
- Waterbirds: https://github.com/kohpangwei/group_DRO
- MNIST: torchvision.datasets.MNIST

**Implementation:**
- GradCAM: https://github.com/jacobgil/pytorch-grad-cam
- GroupDRO: https://github.com/kohpangwei/group_DRO

**Prior Hypotheses:**
- h-m-integrated: Validated gradient abnormality detection (|ρ|>0.7 correlation)

---

**Document Status:** Complete  
**Next Action:** Phase 3 Implementation Planning (PRD, Architecture, Task List)
