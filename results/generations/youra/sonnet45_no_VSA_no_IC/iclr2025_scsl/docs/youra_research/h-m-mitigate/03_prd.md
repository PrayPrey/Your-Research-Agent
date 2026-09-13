# Product Requirements Document: Spatial Gradient Regularization

**Hypothesis:** h-m-mitigate  
**Type:** MECHANISM (Mitigation)  
**Generated:** 2026-08-20  

---

## Executive Summary

Implement spatial gradient regularization to mitigate spurious correlations by penalizing gradient divergence in GradCAM-identified spurious regions. Target: WGA ≥ GroupDRO+5% on Waterbirds benchmark with ≤2% average accuracy drop.

**Success Gate:** SHOULD_WORK (MNIST toy validation gates real-world experiments)

---

## Problem Statement

Existing spurious mitigation methods (GroupDRO, JTT) rely on loss reweighting. No prior work uses gradient-space regularization. h-m-integrated validated gradient abnormality detection; this extends to intervention.

**Gap:** Spatial regularization targeting GradCAM-identified spurious regions has not been explored for fairness/robustness.

---

## Functional Requirements

### FR-1: Dataset Preparation

**MNIST+Color (Toy Validation)**
- Base: MNIST 60k train, 10k test
- Spurious correlation: 90% digit-color correlation (Even→Red, Odd→Green)
- Groups: 4 (majority/minority × digit/color)
- Splits: 54k train, 6k val, 10k test
- Storage: `~/.cache/mnist_color_90pct/`
- Metadata: CSV with (image_id, digit, color, group, split)

**Waterbirds (Real-World Validation)**
- Source: CUB-200-2011 + Places365 backgrounds
- Download: https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz
- Splits: 4795 train, 1199 val, 5794 test
- Groups: 4 (waterbird-water, waterbird-land, landbird-water, landbird-land)
- Preprocessing: Resize 224×224, ImageNet normalization
- Storage: `./datasets/waterbirds/`

### FR-2: Model Architecture

**MNIST+Color Model**
- Backbone: ResNet-18 (torchvision, train from scratch)
- Input: 3×28×28 RGB
- Output: 10 classes (digits)
- GradCAM target: `model.layer4[-1]`

**Waterbirds Model**
- Backbone: ResNet-50 (ImageNet pretrained)
- Input: 3×224×224 RGB
- Output: 2 classes (waterbird/landbird)
- GradCAM target: `model.layer4[-1]`

### FR-3: Baseline Training (ERM)

**MNIST+Color ERM**
- Optimizer: SGD (lr=0.01, momentum=0.9, weight_decay=1e-4)
- Batch size: 128
- Epochs: 50
- Scheduler: ReduceLROnPlateau (patience=5, factor=0.1)
- Loss: CrossEntropyLoss

**Waterbirds ERM**
- Optimizer: SGD (lr=0.001, momentum=0.9, weight_decay=1e-4)
- Batch size: 128
- Epochs: 300
- Scheduler: None (fixed LR)
- Loss: CrossEntropyLoss

### FR-4: GroupDRO Baseline (Waterbirds Only)

- Implementation: https://github.com/kohpangwei/group_DRO
- Config: `--reweight_groups --robust --gamma 0.1 --generalization_adjustment 0`
- Hyperparameters: Same as ERM for fair comparison
- Expected WGA: 85-88%

### FR-5: Spatial Gradient Regularization Trainer

**Algorithm:**
1. Spurious region identification (per batch):
   - Compute GradCAM for majority/minority group samples
   - Difference map: `D = |GradCAM_majority - GradCAM_minority|`
   - Spurious mask: `M_spurious = (D > percentile(D, threshold))`
2. Regularization loss:
   - `L_total = L_CE + λ * mean(gradient_variance[M_spurious])`
   - `gradient_variance = var(gradients, dim=channel)`
3. Adaptive penalty scaling:
   - `λ_new = λ_old * exp(0.1 * WGA_gap)`
   - WGA_gap = (majority_acc - minority_acc) on validation set
   - Clamp: λ ∈ [0.001, 1.0]

**Hyperparameters:**
- λ_init: {0.001, 0.01, 0.1}
- Percentile threshold: {75, 85, 95}
- GradCAM update frequency: {every batch, every 10 batches}

**Efficiency:**
- GradCAM computed on subset of batch (32 samples max)
- Backward hook on target layer (no extra forward pass)

### FR-6: Ablation Studies

**MNIST+Color Ablations (Phase 1)**
1. Global Regularization: Penalize all gradients (no spatial masking)
2. Spatial Spurious-Region Regularization: Penalize `M_spurious`
3. Spatial Core-Region Regularization: Penalize `M_core` (inverse mask)
4. Color-only test set: Mask digit features
5. Digit-only test set: Mask color features

**Expected Results:**
- Spatial spurious-region: WGA ≥ baseline+10%
- Spatial core-region: WGA ≤ baseline-5% (validates direction)
- Color-only accuracy: ≤ baseline (suppresses spurious)
- Digit-only accuracy: ≥ baseline+5% (enhances core)

### FR-7: Evaluation Metrics

**Primary Metrics:**
- Worst-Group Accuracy (WGA): `min(acc_group0, ..., acc_group3)`
- Average Accuracy: `mean(acc_all_samples)`
- WGA Gap: `(majority_acc - minority_acc)`

**Secondary Metrics (Mechanism Validation):**
- GradCAM attention shift: `mean(GradCAM[M_spurious])` reduction
- Target: ≥20% decrease for minority samples
- Feature attribution: Accuracy drop when spurious regions masked

**Statistical Testing:**
- Bootstrap test (n=1000 resamples)
- Null hypothesis: WGA_spatial ≤ WGA_GroupDRO
- Report: mean ± std, p-value <0.05

### FR-8: Visualization & Logging

**GradCAM Heatmaps:**
- Before/after regularization comparison
- 10 samples per group (majority/minority)
- Highlight spurious region attention shift

**Weights & Biases Integration:**
- Log: WGA, average acc, λ, WGA_gap per epoch
- Track: GradCAM attention scores, gradient variance
- Artifacts: Model checkpoints, heatmap images

---

## Non-Functional Requirements

### NFR-1: Computational Efficiency

- **MNIST+Color:** ≤2 GPU-hours (5 seeds × 4 conditions)
- **Waterbirds:** ≤10 GPU-hours (5 seeds × 3 methods)
- **Total Budget:** 12 GPU-hours
- **Hardware:** 1× NVIDIA GPU (≥8GB VRAM for MNIST, ≥16GB for Waterbirds)

### NFR-2: Reproducibility

- Fixed random seeds: 0, 1, 2, 3, 4
- Exact hyperparameter configs in YAML
- Dataset download scripts
- Environment: PyTorch 2.0+, Python 3.9+

### NFR-3: Code Quality

- Modular trainers: `erm_trainer.py`, `spatial_reg_trainer.py`, `groupdro_trainer.py`
- Shared utilities: `metrics.py`, `visualization.py`, `logging.py`
- Config-driven: YAML files for hyperparameters
- Entry point: `run_experiment.py --config configs/mnist_color.yaml`

---

## Dependencies

**Core Libraries:**
- PyTorch 2.0+
- torchvision 0.15+
- pytorch-grad-cam (https://github.com/jacobgil/pytorch-grad-cam)

**Data Handling:**
- wilds (Waterbirds dataset)
- pandas (metadata)

**Evaluation:**
- scikit-learn (bootstrap)
- scipy (statistical tests)

**Logging:**
- wandb
- matplotlib, seaborn

**External Code:**
- GroupDRO baseline: https://github.com/kohpangwei/group_DRO (wrapper only, not full integration)

---

## Success Criteria

### Phase 1: MNIST+Color (MUST_WORK Gate)

| Metric | Threshold | Priority |
|--------|-----------|----------|
| WGA improvement | ≥10% over baseline | MUST_WORK |
| Color-only accuracy | ≥baseline+10% | SHOULD_WORK |
| Digit-only accuracy | ≤baseline-5% | SHOULD_WORK |

**Gate Logic:** If MNIST fails → ABANDON mitigation claim

### Phase 2: Waterbirds (SHOULD_WORK Gate)

| Metric | Threshold | Priority |
|--------|-----------|----------|
| WGA | ≥GroupDRO+5% | SHOULD_WORK |
| Average accuracy drop | ≤2% | SHOULD_WORK |
| GradCAM shift | ≥20% reduction | NICE_TO_HAVE |
| Statistical significance | p<0.05 | SHOULD_WORK |

**Gate Logic:** If Waterbirds fails → PIVOT to detection-only (Tier 3)

---

## Experiment Phases

**Phase 1: MNIST+Color (Days 1-2, Budget: 2 GPU-hours)**
1. Baseline ERM (5 seeds)
2. Global Regularization (5 seeds)
3. Spatial Spurious-Region Regularization (5 seeds)
4. Spatial Core-Region Regularization (5 seeds)
5. Ablation: Color-only/Digit-only test sets

**Phase 2: Waterbirds (Days 3-7, Budget: 10 GPU-hours)**
1. Baseline ERM (5 seeds)
2. GroupDRO Baseline (5 seeds, official implementation)
3. Spatial Gradient Regularization:
   - Hyperparameter search: 3 λ_init × 3 percentile = 9 configs
   - Best config: 5 seeds
4. Statistical test: Bootstrap comparison vs GroupDRO
5. Mechanism validation: GradCAM heatmap analysis

---

## Risk Mitigation

### Assumption A1: Minority groups ≥60% correctly classified
- **Risk:** If <60%, GradCAM highlights spurious features
- **Detection:** Monitor minority accuracy during training
- **Mitigation:** Fall back to global regularization (no spatial masking)

### Assumption A2: Percentile normalization avoids majority bias
- **Risk:** Penalty too weak if threshold too high
- **Detection:** Compare penalty magnitudes across groups
- **Mitigation:** Hyperparameter search over {75, 85, 95}

### Assumption A3: Regularization reduces spurious reliance (not just smoothing)
- **Risk:** WGA improves but mechanism is gradient smoothing
- **Detection:** GradCAM heatmap analysis + ablation study
- **Mitigation:** MNIST toy experiment detects early (Phase 1 gate)

### Computational Risk: GradCAM overhead >2×
- **Mitigation:** Compute GradCAM on subset of batch (32 samples max)
- **Fallback:** Update GradCAM every N batches instead of every batch

---

## Deliverables

### Code Artifacts
- [x] MNIST+Color dataset loader
- [x] Waterbirds dataset loader (wilds integration)
- [x] Spatial gradient regularization trainer
- [x] GradCAM implementation (pytorch-grad-cam wrapper)
- [x] GroupDRO baseline wrapper
- [x] Evaluation scripts (WGA, bootstrap, heatmaps)
- [x] Experiment configs (YAML)

### Experimental Outputs
- [x] MNIST results: 4 conditions × 5 seeds = 20 models
- [x] Waterbirds results: 3 methods × 5 seeds = 15 models
- [x] Statistical analysis: bootstrap p-values, mean±std tables
- [x] Visualizations: GradCAM heatmaps (before/after)
- [x] Ablation study: color-only/digit-only accuracy tables

### Documentation
- [x] Training logs (wandb dashboards)
- [x] Hyperparameter search results
- [x] Failure mode analysis (if applicable)
- [x] Reproducibility guide (README)

---

## File Structure

```
experiments/h_m_mitigate/
├── data/
│   ├── mnist_color.py          # MNIST+Color loader
│   ├── waterbirds.py           # Waterbirds loader
│   └── transforms.py           # Augmentation
├── models/
│   ├── resnet.py               # ResNet-18/50 wrappers
│   └── gradcam.py              # GradCAM (pytorch-grad-cam)
├── trainers/
│   ├── erm_trainer.py          # Baseline ERM
│   ├── groupdro_trainer.py     # GroupDRO wrapper
│   └── spatial_reg_trainer.py  # Spatial regularization
├── utils/
│   ├── metrics.py              # WGA, bootstrap
│   ├── visualization.py        # GradCAM plots
│   └── logging.py              # Weights & Biases
├── configs/
│   ├── mnist_color.yaml        # MNIST hyperparameters
│   └── waterbirds.yaml         # Waterbirds hyperparameters
├── scripts/
│   ├── train_mnist.sh          # Phase 1 experiments
│   └── train_waterbirds.sh     # Phase 2 experiments
└── run_experiment.py           # Main entry point
```

---

## References

**Baselines:**
- Sagawa et al. (2019): Distributionally Robust Neural Networks
- Liu et al. (2021): Just Train Twice
- SCER (2025): Embedding-space regularization (code unavailable)

**Datasets:**
- Waterbirds: https://github.com/kohpangwei/group_DRO
- MNIST: torchvision.datasets.MNIST

**Implementation:**
- GradCAM: https://github.com/jacobgil/pytorch-grad-cam
- GroupDRO: https://github.com/kohpangwei/group_DRO

**Prior Hypotheses:**
- h-m-integrated: Validated gradient abnormality detection (|ρ|>0.7)

---

**Document Status:** Complete  
**Next Phase:** Architecture Design (Step 3)
