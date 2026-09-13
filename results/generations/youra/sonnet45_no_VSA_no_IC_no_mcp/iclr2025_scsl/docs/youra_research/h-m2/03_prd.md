# Product Requirements Document (PRD): h-m2

**Hypothesis**: Attention Correction Mechanism  
**Hypothesis ID**: h-m2  
**Type**: MECHANISM  
**Gate**: SHOULD_WORK  
**Pipeline Project ID**: e434b9c6-e150-46c4-8cb5-1c8e857b014c  
**Archon Task ID**: 477802a1-5780-457f-9d7b-a6cf7081730f  
**Generated**: 2026-08-25  
**Phase**: 3 (Implementation Planning)

---

## Executive Summary

Build experiment to test whether attention mechanisms enable mid-training correction of spurious correlations. Compare ResNet-18-BN (control), ResNet-18-CBAM (channel+spatial attention), and ViT-Small (global self-attention) on Waterbirds dataset. Measure worst-group gap reduction slope during epochs 20-50. Success: slope difference ≥0.3pp/epoch, non-overlapping 95% CIs, Cohen's d≥0.8.

---

## User Story

**As a researcher**, I need to train three architectures (ResNet-BN, ResNet-CBAM, ViT-Small) on Waterbirds dataset for 100 epochs × 10 seeds, log worst-group metrics every epoch, compute gap reduction slopes for epochs 20-50, and test whether attention mechanisms show steeper correction slopes than baseline.

**So that** I can validate whether attention enables mid-training spurious correlation correction and distinguish between channel attention (CBAM) vs global architecture (ViT) effects.

---

## Success Criteria

### Primary (Hypothesis Validation)
1. **Slope computation**: Linear regression fit for epochs 20-50 produces slope β₁ (pp/epoch) for each architecture×seed combination (30 slopes total)
2. **Statistical test**: Bootstrap 95% CI computed for each architecture's mean slope
3. **Hypothesis test**: 
   - (ResNet-CBAM OR ViT) shows mean slope < ResNet-BN mean slope - 0.3pp/epoch AND
   - CIs do not overlap AND
   - Cohen's d ≥ 0.8
4. **Falsification**: Both CBAM and ViT CIs overlap with BN OR slope difference <0.2pp/epoch OR d<0.5

### Functional
1. All 30 training runs complete (3 architectures × 10 seeds × 100 epochs)
2. Metrics logged every epoch: avg_acc, worst_group_acc, per_group_acc (4 groups), gap, train_loss
3. Checkpoints saved at epoch 100 for reproducibility
4. Logs in machine-readable format (CSV)
5. Trajectory plot generated (gap vs epoch for all 3 architectures, with regression lines)

### Quality
1. CBAM module validated on CIFAR-10 before Waterbirds (accuracy improvement ≥1%)
2. ViT training monitored for stability (gradient norms logged, clipping if needed)
3. Code is modular (separate files: data, models, train, eval, viz)
4. Results reproducible (seeds fixed, environment documented)
5. Statistical summary table saved (slopes, CIs, Cohen's d)

---

## Scope

### In Scope
- **Data**: Waterbirds dataset via wilds library (reuse h-e1 loader)
- **Architectures**:
  - ResNet-18-BN (torchvision, default BN)
  - ResNet-18-CBAM (custom CBAM module + ResNet-18)
  - ViT-Small (timm, patch16_224)
- **Training**: 10 seeds, 100 epochs, SGD(lr=0.01, momentum=0.9, wd=1e-4), batch_size=64
- **Evaluation**: Slope regression (epochs 20-50), bootstrap CI, Cohen's d
- **Visualization**: Trajectory plot, regression lines, statistical table

### Out of Scope
- Learning rate schedules (constant LR only)
- Data augmentation (isolate architectural effects)
- Pretrained models (train from scratch)
- Alternative attention mechanisms (e.g., SE-Net, non-local blocks)
- Alternative epoch windows (20-50 is fixed; secondary analysis may test others)
- Class reweighting or group balancing (vanilla ERM training)

---

## Detailed Requirements

### R1: Data Loader
**Requirement**: Load Waterbirds dataset with group labels  
**Input**: None (download via wilds)  
**Output**: DataLoader yielding (image, label, group_id, metadata)  
**Acceptance Criteria**:
- 4800 train samples, 600 val, 600 test
- Group IDs ∈ {0,1,2,3} (landbird-land, landbird-water, waterbird-land, waterbird-water)
- Images preprocessed: resize 224×224, normalize (ImageNet stats)
- Batch size: 64
- No data augmentation

**Reuse**: Can reuse h-e1 data loader (identical dataset)

---

### R2: Model Definitions

#### R2.1: ResNet-18-BN (Control)
**Requirement**: Standard ResNet-18 with Batch Normalization  
**Input**: (batch, 3, 224, 224) images  
**Output**: (batch, 2) logits  
**Acceptance Criteria**:
- torchvision ResNet-18, num_classes=2
- 8 BN layers (conv2_x through conv5_x)
- He initialization
- Trainable params: ~11M

#### R2.2: ResNet-18-CBAM (Ablation)
**Requirement**: ResNet-18 with CBAM attention modules  
**Input**: (batch, 3, 224, 224) images  
**Output**: (batch, 2) logits  
**Acceptance Criteria**:
- CBAM module:
  - Channel attention: AvgPool+MaxPool → MLP(C→C//16→C) → Sigmoid → (batch,C,1,1)
  - Spatial attention: Channel AvgPool+MaxPool → Conv(7×7) → Sigmoid → (batch,1,H,W)
  - Output: x * channel_attn(x) * spatial_attn(x)
- 4 CBAM modules inserted after each residual block
- He init for ResNet, Xavier normal for CBAM
- Trainable params: ~11.2M (CBAM adds <200K)
- Gradient flow verified (CBAM grads non-zero)

**Validation**: Test on CIFAR-10 first (CBAM should improve accuracy ≥1% over baseline)

#### R2.3: ViT-Small (Global Attention)
**Requirement**: Vision Transformer Small  
**Input**: (batch, 3, 224, 224) images  
**Output**: (batch, 2) logits  
**Acceptance Criteria**:
- timm.create_model('vit_small_patch16_224', pretrained=False, num_classes=2)
- Config: patch_size=16, hidden_dim=384, depth=12, heads=6
- 196 patches (14×14 grid)
- LayerNorm, Xavier uniform init
- Trainable params: ~22M
- Convergence verified (loss decreases)

**Risk Mitigation**: Monitor loss; add gradient clipping (max_norm=1.0) if unstable; reduce LR to 0.001 if needed

---

### R3: Training Loop
**Requirement**: Train 3 architectures × 10 seeds × 100 epochs  
**Input**: DataLoader, model, optimizer, seed  
**Output**: Training logs (CSV), checkpoints  
**Acceptance Criteria**:
- Total runs: 30 (3 arch × 10 seeds)
- Per run: 100 epochs, ~6-10 min/epoch (GPU)
- Optimizer: SGD(lr=0.01, momentum=0.9, weight_decay=1e-4)
- Loss: CrossEntropyLoss
- Metrics logged every epoch:
  - average_accuracy (all test samples)
  - worst_group_accuracy (min over 4 groups)
  - per_group_accuracy (4 values)
  - worst_group_gap (avg - worst)
  - train_loss
- Checkpoints saved at epoch 100
- Logs: CSV format (epoch, seed, arch, metrics)

**Runtime Estimate**: 33 hours GPU serial (10h ResNet-BN + 10h CBAM + 13h ViT)

---

### R4: Slope Computation
**Requirement**: Compute worst-group gap slopes for epochs 20-50  
**Input**: Training logs (gap trajectories)  
**Output**: Slope statistics table (slopes.csv)  
**Acceptance Criteria**:
- Per seed: extract epochs 20-50 (31 points), fit `gap = β₀ + β₁×epoch` via scipy.stats.linregress
- Per architecture: compute mean slope, 95% CI via bootstrap (1000 resamples)
- Output table columns: arch, mean_slope, CI_lower, CI_upper, Cohen_d_vs_BN
- Statistical tests:
  - CI overlap check (CBAM vs BN, ViT vs BN)
  - Cohen's d: (mean_slope_attn - mean_slope_BN) / pooled_std
- Success: CI non-overlap AND slope diff ≥0.3pp/epoch AND d≥0.8
- Falsification: CI overlap OR slope diff <0.2pp/epoch OR d<0.5

---

### R5: Visualization
**Requirement**: Generate trajectory plot and statistical summary  
**Input**: Training logs, slope statistics  
**Output**: trajectories.png, statistical_summary.md  
**Acceptance Criteria**:
- Plot: mean gap ± stderr vs epoch for each architecture
- Highlight epochs 20-50 (analysis window, shaded region)
- Overlay regression lines for epochs 20-50
- Legend: ResNet-BN (control), ResNet-CBAM, ViT-Small
- Table: slopes, CIs, p-values, Cohen's d
- Interpretation matrix: CBAM success/fail × ViT success/fail → mechanism conclusion

---

## Non-Functional Requirements

### Performance
- Training runtime: ≤40 hours GPU (33h estimate + 20% buffer)
- Memory: ≤16GB GPU RAM per run (ResNet ~4GB, ViT ~8GB)
- Disk: ≤50GB (logs ~100MB, checkpoints ~2GB, dataset ~5GB)

### Reliability
- Reproducibility: seeds fixed (0-9), environment documented
- Error handling: checkpoint resume if training interrupted
- Validation: CBAM tested on CIFAR-10 before Waterbirds

### Maintainability
- Modular code: separate files for data, models, train, eval, viz
- Clear separation: CBAM module in cbam.py, models in models.py
- Logging: structured CSV (no manual parsing)
- Documentation: README with run instructions

---

## Dependencies

**Python Packages**:
- torch >= 2.0
- torchvision >= 0.15
- timm >= 0.9 (ViT)
- wilds >= 2.0 (Waterbirds)
- numpy >= 1.24
- scipy >= 1.10 (stats)
- matplotlib >= 3.7
- tqdm (progress bars)
- pandas (optional, CSV handling)

**Hardware**:
- GPU recommended (CUDA-capable, ≥16GB VRAM)
- CPU fallback supported (runtime ~10× slower)

**Data**:
- Waterbirds dataset downloaded via wilds.get_dataset('waterbirds', download=True)
- Cache path: ./data/waterbirds/

---

## File Structure

```
h-m2/
├── 02c_experiment_brief.md
├── 03_prd.md                  (this document)
├── 03_architecture.md          (Phase 3 output)
├── 03_logic.md                 (Phase 3 output)
├── 03_config.md                (Phase 3 output)
├── 04_validation.md            (Phase 4 output)
├── code/
│   ├── data_loader.py          (~50 lines or symlink to h-e1)
│   ├── models.py               (~150 lines: ResNet-BN/CBAM/ViT)
│   ├── cbam.py                 (~50 lines: CBAM module)
│   ├── train.py                (~100 lines: training loop)
│   ├── evaluate_slopes.py      (~100 lines: slope computation)
│   └── plot_trajectories.py    (~50 lines: visualization)
├── results/
│   ├── logs/                   (30 CSV files)
│   ├── checkpoints/            (30 model states)
│   ├── slopes.csv              (slope statistics)
│   ├── trajectories.png        (plot)
│   └── statistical_summary.md  (interpretation)
```

---

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| ViT training instability | Medium | High (cannot test ViT) | Monitor loss, gradient clipping, LR=0.001 fallback |
| CBAM implementation bug | Low | Medium (wrong conclusion) | Validate on CIFAR-10 first |
| Epoch 20-50 misses correction | Medium | Medium (false negative) | Plot full trajectories, test alternative windows in secondary analysis |
| High variance (wide CIs) | Medium | Medium (overlapping CIs) | 10 seeds provides 80% power; add 5 more if needed |
| Runtime exceeds budget | Low | Low (delay only) | Parallelize across 3 GPUs or accept 33h serial |

---

## Constraints

- **No learning rate schedule**: Constant LR=0.01 (isolate architectural effects)
- **No pretrained weights**: Train from scratch (fair comparison)
- **No data augmentation**: Isolate architectural differences
- **Fixed epoch window**: 20-50 (design decision from Phase 2B)
- **SHOULD_WORK gate**: Does NOT block Phase 5 if hypothesis fails

---

## Success Metrics Summary

**Hypothesis Validated** if:
- (CBAM OR ViT) mean slope < BN mean slope - 0.3pp/epoch AND
- CIs do not overlap AND
- Cohen's d ≥ 0.8

**Hypothesis Falsified** if:
- Both CBAM and ViT CIs overlap with BN OR
- Slope difference < 0.2pp/epoch OR
- Cohen's d < 0.5

**Partial Success** (ViT succeeds, CBAM fails):
- Interpretation: global architecture drives correction, not attention alone
- Document confound in Phase 6 paper

---

## Acceptance Sign-off

**Functional**: All 30 runs complete, metrics logged, slopes computed, plot generated  
**Scientific**: Hypothesis test executed, falsification criterion clear, confound acknowledged  
**Quality**: CBAM validated, ViT stability monitored, code modular, results reproducible

---

**PRD Status**: COMPLETED  
**Ready for Architecture Design**: YES  
**Estimated Complexity**: Tier 1 (400-500 LoC, 33h GPU, standard architectures)
