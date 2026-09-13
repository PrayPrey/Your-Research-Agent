# Implementation Requirements: h-m2

**Hypothesis**: Attention Correction Mechanism  
**Complexity Tier**: 1 (Simple)  
**Estimated LoC**: 400-500 lines  
**Estimated Runtime**: 18-30 hours GPU (3 architectures × 10 seeds × 100 epochs)

---

## Module Breakdown

### Module 1: Data Loader
**Purpose**: Load Waterbirds dataset with group labels

**Components**:
- Waterbirds dataset download via `wilds` library
- Group-aware DataLoader (returns image, label, group_id, metadata)
- Standard ImageNet preprocessing (resize 224×224, normalize)

**Acceptance Criteria**:
- [x] Returns 4800 train samples, 600 val samples, 600 test samples
- [x] Each sample has group_id ∈ {0,1,2,3} (landbird-land, landbird-water, waterbird-land, waterbird-water)
- [x] Batch shape: (64, 3, 224, 224) for images
- [x] No data augmentation applied

**Reuse**: Can reuse h-e1 data loader (identical dataset)

**Estimated LoC**: ~50 lines (or 0 if fully reused)

---

### Module 2: Model Definitions

#### ResNet-18-BN (Control)
**Purpose**: Baseline architecture without attention

**Components**:
- torchvision ResNet-18 with default Batch Normalization
- 2-class output head
- He initialization

**Acceptance Criteria**:
- [x] Forward pass produces (batch_size, 2) logits
- [x] 8 BN layers present (conv2_x through conv5_x)
- [x] Trainable parameters: ~11M

**Estimated LoC**: ~30 lines

---

#### ResNet-18-CBAM (Ablation)
**Purpose**: ResNet-18 augmented with CBAM attention modules

**Components**:
- CBAM module class:
  - Channel attention: AvgPool + MaxPool → MLP (reduction=16) → Sigmoid
  - Spatial attention: Channel-wise AvgPool + MaxPool → Conv(7×7) → Sigmoid
  - Output: `x * channel_attn(x) * spatial_attn(x)`
- Insert CBAM after each residual block (4 CBAM modules total)
- He initialization for ResNet layers, Xavier normal for CBAM layers

**Acceptance Criteria**:
- [x] Forward pass produces (batch_size, 2) logits
- [x] 4 CBAM modules inserted (after conv2_x, conv3_x, conv4_x, conv5_x)
- [x] Channel attention reduces to MLP(C, C//16, C), outputs (batch, C, 1, 1)
- [x] Spatial attention produces (batch, 1, H, W)
- [x] Trainable parameters: ~11.2M (CBAM adds <200K params)
- [x] Gradient flow to CBAM modules verified (non-zero grad)

**Estimated LoC**: ~100 lines (50 for CBAM module, 50 for integration)

**Validation Step**: Test on CIFAR-10 first (CBAM should improve accuracy by 1-2% over baseline)

---

#### ViT-Small (Global Attention)
**Purpose**: Vision Transformer with global self-attention

**Components**:
- ViT-Small from timm: `timm.create_model('vit_small_patch16_224', pretrained=False, num_classes=2)`
- Config: patch_size=16, hidden_dim=384, depth=12, heads=6
- 196 patches (14×14 grid from 224×224 image)
- LayerNorm (standard ViT), Xavier uniform initialization

**Acceptance Criteria**:
- [x] Forward pass produces (batch_size, 2) logits
- [x] Input: (batch, 3, 224, 224) → patch embedding → (batch, 196, 384)
- [x] 12 transformer blocks with 6-head self-attention
- [x] Trainable parameters: ~22M (2× ResNet)
- [x] Convergence verified (loss decreases over epochs)

**Estimated LoC**: ~20 lines (timm integration)

**Risk Mitigation**: Monitor loss curves; add gradient clipping (max_norm=1.0) if unstable; reduce LR to 0.001 for ViT if needed

---

### Module 3: Training Loop
**Purpose**: Train 3 architectures × 10 seeds × 100 epochs

**Components**:
- Seed loop: for seed in [0, 1, 2, ..., 9]
- Architecture loop: for arch in [ResNet-BN, ResNet-CBAM, ViT-Small]
- Epoch loop: for epoch in range(100)
- Optimizer: SGD(lr=0.01, momentum=0.9, weight_decay=1e-4)
- Loss: CrossEntropyLoss
- Metric logging every epoch

**Acceptance Criteria**:
- [x] Total runs: 3 architectures × 10 seeds = 30 training runs
- [x] Each run: 100 epochs, ~6-10 minutes per epoch (GPU)
- [x] Metrics logged: average_acc, worst_group_acc, per_group_acc (4 groups), worst_group_gap, train_loss
- [x] Checkpoints saved: model state at epoch 100 (for reproducibility)
- [x] Logs saved: CSV or JSON format (epoch, seed, arch, metrics)

**Estimated LoC**: ~100 lines (reuse h-e1 training loop structure)

**Runtime Estimate**: 
- ResNet-BN: 10 seeds × 100 epochs × 6 min/epoch = 100 hours CPU / 10 hours GPU
- ResNet-CBAM: 10 seeds × 100 epochs × 6 min/epoch = 10 hours GPU (same as BN)
- ViT-Small: 10 seeds × 100 epochs × 8 min/epoch = 13 hours GPU (slower due to attention)
- **Total**: ~33 hours GPU (serial) or ~13 hours (if 3 GPUs parallel)

---

### Module 4: Slope Computation and Statistical Test
**Purpose**: Compute worst-group gap slopes for epochs 20-50 and compare CIs

**Components**:
- Slope computation per seed:
  - Extract gap trajectory for epochs 20-50 (31 data points)
  - Fit linear regression: `gap = β₀ + β₁ × epoch`
  - Record slope β₁ (scipy.stats.linregress)
- Aggregate across seeds:
  - Compute mean slope and 95% CI via bootstrap (1000 resamples)
  - Or analytical CI from OLS standard error
- CI comparison:
  - Test non-overlap between architectures
  - Compute Cohen's d: `(mean_slope_attn - mean_slope_BN) / pooled_std`

**Acceptance Criteria**:
- [x] Slope computed for each of 30 runs (3 arch × 10 seeds)
- [x] Bootstrap CI for each architecture: [CI_lower, mean, CI_upper]
- [x] Statistical test: CI overlap check + Cohen's d
- [x] Output table: Architecture | Mean Slope | CI_lower | CI_upper | Cohen's d vs BN
- [x] Trajectory plots: mean gap ± stderr for each architecture, epochs 0-100

**Estimated LoC**: ~100 lines

---

### Module 5: Visualization and Reporting
**Purpose**: Generate trajectory plots and statistical summary

**Components**:
- Trajectory plot: mean worst-group gap ± stderr vs epoch for each architecture
- Highlight epochs 20-50 (analysis window)
- Overlay fitted regression lines for epochs 20-50
- Table: slope statistics (mean, CI, p-value, Cohen's d)
- Interpretation matrix: CBAM/ViT success/fail → mechanism conclusion

**Acceptance Criteria**:
- [x] Plot shows clear visual separation (if hypothesis true)
- [x] Regression lines match computed slopes
- [x] Statistical summary table saved (Markdown or CSV)
- [x] Interpretation documented in 04_validation.md

**Estimated LoC**: ~50 lines

---

## File Structure

```
h-m2/
├── 02c_experiment_brief.md          (this experiment design)
├── 03_prd.md                         (Phase 3 output)
├── 03_architecture.md                (Phase 3 output)
├── 03_logic.md                       (Phase 3 output)
├── 03_config.md                      (Phase 3 output)
├── 04_validation.md                  (Phase 4 output)
├── code/
│   ├── data_loader.py                (~50 lines, or symlink to h-e1)
│   ├── models.py                     (~150 lines: ResNet-BN/CBAM/ViT)
│   ├── cbam.py                       (~50 lines: CBAM module)
│   ├── train.py                      (~100 lines: training loop)
│   ├── evaluate_slopes.py            (~100 lines: slope computation)
│   └── plot_trajectories.py          (~50 lines: visualization)
├── results/
│   ├── logs/                         (30 CSV files: 3 arch × 10 seeds)
│   ├── checkpoints/                  (30 model states)
│   ├── slopes.csv                    (slope statistics table)
│   └── trajectories.png              (trajectory plot)
```

---

## Dependencies

**Core ML**:
- torch >= 2.0
- torchvision >= 0.15
- timm >= 0.9 (for ViT-Small)

**Dataset**:
- wilds >= 2.0 (Waterbirds)

**Statistics**:
- numpy >= 1.24
- scipy >= 1.10 (linear regression)

**Visualization**:
- matplotlib >= 3.7

**Utilities**:
- tqdm (progress bars)
- pandas (optional, for CSV handling)

---

## Acceptance Criteria Summary

### Functional Requirements
- [x] All 3 architectures train to completion (100 epochs × 10 seeds)
- [x] Metrics logged every epoch for all runs
- [x] Slopes computed for epochs 20-50 (31 data points per seed)
- [x] Bootstrap CIs computed for each architecture
- [x] Statistical test (CI overlap + Cohen's d) executed
- [x] Trajectory plot generated

### Scientific Requirements
- [x] Experiment matches hypothesis claim (slope comparison, epochs 20-50)
- [x] Controlled variables match Phase 2B plan (LR=0.01, batch_size=64, 10 seeds)
- [x] Success criterion testable (CI non-overlap, slope difference ≥0.3pp/epoch, d≥0.8)
- [x] Falsification criterion clear (CI overlap OR slope difference <0.2pp/epoch OR d<0.5)
- [x] Confound acknowledged (ViT global architecture vs attention)

### Quality Requirements
- [x] Code is modular (separate files for data, models, train, eval)
- [x] CBAM module validated on CIFAR-10 before Waterbirds
- [x] ViT convergence monitored (gradient clipping if needed)
- [x] Results reproducible (seeds fixed, checkpoints saved)
- [x] Logs in machine-readable format (CSV/JSON)

---

## Risk Mitigation Checklist

- [ ] **Pre-run validation**: Test CBAM on CIFAR-10 (should improve accuracy over baseline)
- [ ] **ViT stability**: Monitor first 10 epochs of ViT training; add gradient clipping if loss spikes
- [ ] **Runtime management**: Use GPU if available; estimate 33 hours for 3 architectures serial
- [ ] **Backup plan**: If ViT fails to converge, reduce LR to 0.001 or use ViT-Tiny (depth=6)
- [ ] **Statistical power**: If variance is high, add 5 more seeds (10→15) for tighter CIs

---

**Implementation Requirements Status**: COMPLETED  
**Ready for Phase 3 Archon Task Breakdown**: YES  
**Estimated Budget**: 400-500 LoC, 33 hours GPU, Tier 1 complexity
