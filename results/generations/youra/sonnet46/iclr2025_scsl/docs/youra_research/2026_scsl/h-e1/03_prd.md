---
stepsCompleted:
  - executive_summary
  - problem_statement
  - functional_requirements
  - non_functional_requirements
  - success_criteria
  - data_spec
  - evaluation_spec
  - dependencies
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
phase: Phase 3
generated_at: '2026-03-16'
source: Phase 2C Experiment Brief (02c_experiment_brief.md)
---

# Product Requirements Document: H-E1
## Normalized Gradient Norm as Minority Group Proxy (Existence PoC)

**Hypothesis ID:** H-E1
**Type:** EXISTENCE (PoC)
**Gate:** MUST_WORK — ratio ≥ 3x AND AUC > 0.70 AND balance deviation ≤ 10%
**Date:** 2026-03-16
**Pipeline:** Anonymous Research Pipeline | Phase 2C → Phase 3 → Phase 4

---

## Executive Summary

H-E1 validates whether normalized per-sample last-layer gradient norms (`g_tilde_i = ||∇_W ℓ_i|| / ||h(x_i)||`) computed during early ERM training on the Waterbirds benchmark serve as a reliable proxy for minority group membership. This is a foundational existence proof: if gradient norms separate minority from majority samples without group supervision, the GNR-LLR pipeline (Phases H-M1 through H-M4) becomes viable.

**What we build:** A diagnostic experiment script that:
1. Trains ResNet-50 via standard ERM on Waterbirds for 10 epochs
2. Computes per-sample normalized gradient norms at epochs 1, 3, 5, 10 via FC-layer hooks
3. Evaluates whether g_tilde values satisfy three quantitative gate criteria

**Success Threshold:** All three gate criteria must pass at T_id=5:
- g_tilde ratio (minority/majority mean) ≥ 3x
- AUC(g_tilde → minority membership) > 0.70
- Top-25% high-norm subset within-class balance deviation ≤ 10%

---

## Problem Statement

### Research Context

Standard ERM training on spuriously correlated datasets (e.g., Waterbirds: 95% landbirds on land backgrounds) causes neural networks to rely on shortcut features (background) rather than semantic features (bird type). Minority-group samples (e.g., landbirds on water backgrounds) cannot be fit by the spurious-feature shortcut solution and therefore produce persistently elevated per-sample loss — and thus elevated gradient norms.

The **NHT (Norm-Hierarchy Theory) Prediction**: Minority samples resist the shortcut basin, producing gradient norms 6–14x higher than majority samples. If this holds after feature-magnitude normalization (accounting for BatchNorm equalization), then gradient norm provides a group-label-free proxy for minority group membership.

### What H-E1 Must Demonstrate

H-E1 is a **diagnostic experiment** (not a full pipeline experiment). It does NOT:
- Perform last-layer retraining
- Compute worst-group accuracy on test set
- Compare against JTT/DFR baselines

H-E1 ONLY validates: *Does g_tilde separate minority from majority?*

### Known Unknowns

1. **BatchNorm equalization effect**: BatchNorm is expected to equalize ||h(x_i)|| across groups within a class. If it over-equalizes, the g_tilde ratio may be lower than the 6–14x raw norm ratio. Expected normalized ratio: 3–8x.
2. **Feature norm variability**: If ||h(x_i)|| varies substantially across groups (BatchNorm failure case), g_tilde normalization may actually amplify or collapse the signal.
3. **Temporal dynamics**: Peak signal is expected at T_id=5 (peak shortcut phase). Earlier epochs may show weaker signal; later epochs may show decay.

---

## Functional Requirements

### FR-1: Dataset Loading and Preprocessing

**FR-1.1 Dataset**: Load Waterbirds standard split (train/val/test)
- Source: Sagawa et al. 2019 GroupDRO benchmark
- Root path: `.data_cache/datasets/waterbirds/`
- Metadata file: `metadata.csv` with columns: `img_filename`, `y` (class), `place` (background), `split`
- Split encoding: train=0, val=1, test=2
- Group encoding: G0=landbird/land (y=0,place=0), G1=landbird/water (y=0,place=1), G2=waterbird/land (y=1,place=0), G3=waterbird/water (y=1,place=1)

**FR-1.2 Split Usage**:
- Training split (n=4,795): ERM training + gradient norm computation
- Validation split (n=1,199): Optional per-epoch accuracy tracking only
- Test split (n=5,794): NOT used in H-E1 (used in H-M4)
- Group labels: Used ONLY post-hoc for metric evaluation, NOT during training

**FR-1.3 Preprocessing**:
- Resize: 256×256 → CenterCrop 224×224
- Normalize: mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225] (ImageNet)
- Training augmentation: RandomHorizontalFlip
- Evaluation: No augmentation (CenterCrop + Normalize only)

**FR-1.4 DataLoader**:
- Batch size: 128
- Shuffle: True for training, False for gradient norm collection pass
- num_workers: 4
- pin_memory: True (GPU training)

---

### FR-2: Model Architecture and Initialization

**FR-2.1 Architecture**: ResNet-50 (ImageNet pretrained)
- Load via: `torchvision.models.resnet50(pretrained=True)`
- Replace classifier: `model.fc = nn.Linear(2048, 2)` (2-class Waterbirds)
- All other layers: frozen during gradient norm analysis? NO — standard ERM unfrozen training
- BatchNorm: kept in train mode during ERM training

**FR-2.2 Gradient Hook Registration**:
- Register `register_forward_hook` on `model.fc` to capture FC input features h(x_i) ∈ ℝ^2048
- Hook must capture per-sample features (not aggregated)
- Hook fires on forward pass; features stored in GradientNormAnalyzer.features dict

---

### FR-3: ERM Training Protocol

**FR-3.1 Training Configuration**:
- Optimizer: SGD with lr=0.001, momentum=0.9, weight_decay=1e-4
- Loss: Cross-entropy (standard ERM, no group weights)
- Epochs: 10 total
- Batch size: 128
- Seed: 1 (fixed for reproducibility — EXISTENCE PoC single seed)
- Device: CUDA (single GPU)

**FR-3.2 Training Loop**:
- Standard forward + backward + optimizer step
- Track per-epoch: train loss, train accuracy (overall)
- Optional: val accuracy per epoch (for monitoring)
- Gradient norm collection at epochs: 1, 3, 5, 10 (see FR-4)

**FR-3.3 Checkpoint Policy**:
- Save model checkpoint at epochs 1, 3, 5, 10 (for reproducibility)
- Checkpoint path: `outputs/h-e1/checkpoints/epoch_{N}.pt`
- Minimum: save epoch 5 checkpoint (primary analysis point)

---

### FR-4: Gradient Norm Computation

**FR-4.1 Collection Schedule**:
Compute per-sample gradient norms on the FULL training set (4,795 samples) at:
- Epoch 1 (pre-shortcut baseline)
- Epoch 3 (early shortcut acquisition)
- Epoch 5 (T_id primary — peak shortcut phase)
- Epoch 10 (post-peak, for H-M1 data collection)

**FR-4.2 Gradient Norm Formula**:
```
g_raw_i  = ||∇_W ℓ_i||    (FC weight gradient L2 norm)
h_norm_i = ||h(x_i)||      (FC input feature L2 norm)
g_tilde_i = g_raw_i / (h_norm_i + ε)   where ε = 1e-8
```

**FR-4.3 Efficient Computation**:
Use the outer-product decomposition for CE loss to avoid per-sample backward passes:
```
For CE loss: ∇_W ℓ_i = (p_i - y_i_onehot) ⊗ h(x_i)
           → ||∇_W ℓ_i|| = ||p_i - y_i_onehot|| × ||h(x_i)||
           → g_raw_i = ||p_i - y_i_onehot|| × h_norm_i
           → g_tilde_i = ||p_i - y_i_onehot||  (residual norm)
```
This vectorized approach computes all per-sample norms in a single forward pass without individual backward passes.

**FR-4.4 Collection Mode**:
- Switch model to eval mode for gradient norm collection pass (no BatchNorm training updates)
- No gradient accumulation in optimizer during collection (zero_grad at each batch)
- Collect: g_raw (B,), g_tilde (B,), h_norm (B,), sample_indices (B,), group_labels (B,), class_labels (B,)
- Store per-epoch: numpy arrays saved to `outputs/h-e1/gradnorm_epoch_{N}.npz`

---

### FR-5: Evaluation Metrics

**FR-5.1 Gate Metric 1 — g_tilde Ratio**:
```python
minority_mask = (group_labels == 1) | (group_labels == 2)  # G1, G2
minority_mean = g_tilde[minority_mask].mean()
majority_mean = g_tilde[~minority_mask].mean()
ratio = minority_mean / majority_mean
# Gate: ratio ≥ 3.0
```

**FR-5.2 Gate Metric 2 — AUC**:
```python
binary_labels = minority_mask.astype(int)
auc = roc_auc_score(binary_labels, g_tilde)
# Gate: auc > 0.70
```

**FR-5.3 Gate Metric 3 — Balance Deviation**:
```python
top_k_idx = np.argsort(g_tilde)[-int(0.25 * len(g_tilde)):]  # top 25% = 1199 samples
selected_y = class_labels[top_k_idx]
selected_g = group_labels[top_k_idx]
deviations = []
for y_val in [0, 1]:
    y_mask = (selected_y == y_val)
    if y_mask.sum() > 0:
        g_in_y = selected_g[y_mask]
        place_counts = np.bincount(g_in_y % 2, minlength=2)  # place=0 vs place=1 within class
        p_place = place_counts / place_counts.sum()
        deviations.append(np.max(np.abs(p_place - 0.5)))
max_deviation = max(deviations)
# Gate: max_deviation ≤ 0.10 (10%)
```

**FR-5.4 Secondary Metrics** (for analysis, not gate):
- Per-group mean g_tilde: mean(g_tilde | G0), mean(g_tilde | G1), mean(g_tilde | G2), mean(g_tilde | G3)
- Per-group mean h_norm: mean(h_norm | G0..G3) — validates BatchNorm equalization
- Per-group mean g_raw: mean(g_raw | G0..G3) — raw norm for comparison
- Temporal trajectory: all metrics at epochs 1, 3, 5, 10

**FR-5.5 All metrics computed at epochs 1, 3, 5, 10** (not just T_id=5)

---

### FR-6: Visualization

**FR-6.1 Required Figure** (Gate-critical):
- Bar chart with 3 panels:
  - (a) g_tilde ratio at epochs 1, 3, 5, 10 (with dashed line at 3x gate threshold)
  - (b) AUC at epochs 1, 3, 5, 10 (with dashed line at 0.70 gate threshold)
  - (c) Balance deviation at k=25% across epochs (with dashed line at 10%)
- Save: `outputs/h-e1/figures/gate_metrics.png`

**FR-6.2 Additional Figures**:
- Figure 2: Per-epoch gradient norm trajectory — line plot of mean g_tilde per group (G0, G1, G2, G3) across epochs 1–10 (log scale y-axis)
  - Save: `outputs/h-e1/figures/trajectory.png`
- Figure 3: Distribution histogram at T_id=5 — overlaid KDE of g_tilde for minority (G1+G2) vs majority (G0+G3)
  - Save: `outputs/h-e1/figures/distribution_epoch5.png`
- Figure 4: Contingency heatmap — 4×2 heatmap of group composition (G0-G3 × class 0-1) in top-25% subset vs full training set
  - Save: `outputs/h-e1/figures/balance_heatmap.png`
- Figure 5: Feature norm box plots — ||h(x_i)|| per group at T_id=5 (validates BatchNorm equalization)
  - Save: `outputs/h-e1/figures/feature_norms.png`

**FR-6.3 All figures**: 300 DPI, saved as PNG, axes labeled, title includes hypothesis ID and epoch

---

### FR-7: Results Output

**FR-7.1 Results File**: Save JSON summary to `outputs/h-e1/results.json`:
```json
{
  "hypothesis_id": "H-E1",
  "gate_results": {
    "ratio_epoch5": <float>,
    "auc_epoch5": <float>,
    "balance_deviation_epoch5": <float>,
    "gate_pass": <bool>
  },
  "per_epoch_metrics": {
    "1": {"ratio": ..., "auc": ..., "balance_deviation": ...},
    "3": {...},
    "5": {...},
    "10": {...}
  },
  "secondary_metrics": {...},
  "seed": 1,
  "timestamp": "..."
}
```

**FR-7.2 Console Output**: Print per-epoch gate metrics during collection pass.

---

## Non-Functional Requirements

### NFR-1: Computational Efficiency
- Use outer-product decomposition (FR-4.3) to avoid O(N) backward passes
- Total compute budget: ≤ 2 GPU-hours on single modern GPU (RTX 3090 / A100 class)
- Gradient norm collection pass: ≤ 5 minutes per epoch on Waterbirds (4795 samples, batch=128)

### NFR-2: Reproducibility
- Fixed random seed: seed=1 for PyTorch, NumPy, Python random
- Deterministic CUDA operations where possible (`torch.backends.cudnn.deterministic = True`)
- All outputs version-controlled in `outputs/h-e1/`

### NFR-3: Code Quality (LIGHT tier)
- Infrastructure: argparse for CLI args (LIGHT tier — no YAML config required)
- Logging: print statements + CSV per-epoch log (LIGHT tier — no WandB required)
- Testing: smoke test with 10 batches to verify hook fires correctly
- No unit test framework required (EXISTENCE PoC)

### NFR-4: Data Integrity
- Group labels used ONLY for post-hoc evaluation (not loaded during training forward pass)
- Verify dataset statistics match expected (n=4795 train, 4 groups, class balance)
- Assert hook captures correct feature dimension (2048)

### NFR-5: Efficiency Note — Multi-Hypothesis Data Collection
Per Phase 2C guidance, simultaneously collect data needed for H-M1 and H-M2:
- Per-epoch, per-group g_tilde and g_raw statistics (for H-M1 temporal persistence)
- Per-group h_norm statistics (for H-M2 normalization effectiveness)
Store in the same `gradnorm_epoch_{N}.npz` files to avoid redundant GPU runs.

---

## Success Criteria

### Gate Criteria (ALL must pass at T_id=5)

| Criterion | Metric | Target | Failure Action |
|-----------|--------|--------|---------------|
| **Gradient norm separation** | g_tilde ratio (min/maj) | ≥ 3.0x | If < 1.5x: PIVOT normalization approach |
| **Proxy quality** | AUC(g_tilde → minority) | > 0.70 | If ≤ 0.60: ABORT H-GNR-LLR-v1 entirely |
| **Balance property** | Max within-class deviation | ≤ 10% | If > 15%: REVIEW selection strategy |

### Expected Performance (from Phase 2A priors)
- Raw gradient norm ratio: 6–14x (confirmed from prior runs)
- Normalized ratio (g_tilde): 3–8x (BatchNorm equalization expected)
- AUC: 0.72–0.85 (given 6–14x raw separation, minority dominates high-norm tail)

### PoC Pass Definition
Code runs without error AND all three gate criteria pass at T_id=5.

### Mechanism Activation Verification
```python
indicators = {
    "hook_fired": features_captured_count > 0,
    "ratio_above_chance": g_tilde_ratio > 1.5,
    "auc_above_random": auc > 0.55,
    "feature_norms_equalized": h_norm_std_ratio < 0.5,  # std/mean within group
}
```

---

## Data Specification

### Dataset: Waterbirds

| Property | Value |
|----------|-------|
| Source | Sagawa et al. 2019 GroupDRO |
| Type | Real images (bird + background composites) |
| Split | Standard (train/val/test) |
| Train | 4,795 samples |
| Val | 1,199 samples |
| Test | 5,794 samples |
| Classes | 2 (landbird=0, waterbird=1) |
| Groups | 4 (y × place: G0=0/land, G1=0/water, G2=1/land, G3=1/water) |
| Minority | G1 (n=184) + G2 (n=56) = 240 samples (5.0% of train) |
| Majority | G0 (n=3498) + G3 (n=1057) = 4555 samples (95.0% of train) |
| Spurious correlation | 95% landbirds on land, 95% waterbirds on water |
| Synthetic data | NO (real images — policy PASSED) |

**Download**: Manual download from GroupDRO repo or WILDS benchmark
**Cache path**: `.data_cache/datasets/waterbirds/`
**Required file**: `metadata.csv` in root directory

---

## Dependencies

### Software Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| Python | ≥3.8 | Runtime |
| PyTorch | ≥1.12 | DL framework, hooks |
| torchvision | ≥0.13 | ResNet-50 pretrained weights |
| numpy | ≥1.21 | Array ops, metric computation |
| pandas | ≥1.3 | Metadata CSV loading |
| scikit-learn | ≥1.0 | roc_auc_score |
| matplotlib | ≥3.5 | Visualization |
| seaborn | ≥0.11 | KDE plots, heatmap |
| Pillow | ≥9.0 | Image loading |
| scipy | ≥1.7 | Optional: KDE smoothing |

### Data Dependencies
| Resource | Required | Notes |
|----------|----------|-------|
| Waterbirds dataset | YES | Manual download required |
| ResNet-50 pretrained weights | YES | Auto-downloaded via torchvision |
| GPU (CUDA) | YES | Single GPU, ≥8GB VRAM |

### Upstream Phase Dependencies
| Phase | Artifact | Status |
|-------|----------|--------|
| Phase 2B | 02b_context.md — verification plan | COMPLETED |
| Phase 2C | 02c_experiment_brief.md — this PRD's source | COMPLETED |
| Phase 1/2A | Research context, NHT theory | COMPLETED |

### Downstream (H-E1 → Subsequent Hypotheses)
| Hypothesis | Dependency | What It Needs |
|------------|-----------|---------------|
| H-M1 | Requires H-E1 PASS | g_tilde epoch 10 data for temporal persistence |
| H-M2 | Requires H-M1 PASS | Per-group h_norm stats (BatchNorm equalization) |
| H-M3 | Requires H-M2 PASS | Top-k% selection mechanism |
| H-M4 | Requires H-M3 PASS | Full GNR-LLR pipeline |

**Note**: Collect H-M1 and H-M2 supporting data simultaneously (FR-5.4, NFR-5) to avoid redundant GPU computation.

---

## Scope Boundaries

### In Scope (H-E1)
- ERM training on Waterbirds train split
- Gradient norm computation via FC hooks
- g_tilde ratio, AUC, balance deviation metrics at epochs 1, 3, 5, 10
- Visualization of diagnostic metrics
- Saving intermediate data for H-M1/H-M2 reuse

### Out of Scope (H-E1)
- Last-layer retraining (H-M3, H-M4)
- Worst-group accuracy on test set (H-M4)
- CelebA dataset experiments (main hypothesis)
- JTT/DFR baseline comparison (H-M4)
- Group annotation during training

---

## Phase 2C Completeness Verification

| Phase 2C Item | Included in PRD |
|---------------|-----------------|
| Dataset: Waterbirds (standard) | ✅ FR-1 |
| Model: ResNet-50 (ImageNet pretrained) | ✅ FR-2 |
| Training: SGD lr=0.001, momentum=0.9, WD=1e-4 | ✅ FR-3 |
| Batch size: 128 | ✅ FR-1.4, FR-3.1 |
| Epochs: 10 (collection at 1,3,5,10) | ✅ FR-3.2, FR-4.1 |
| Gradient norm mechanism (FC hook + normalization) | ✅ FR-2.2, FR-4 |
| Gate metrics: ratio, AUC, balance deviation | ✅ FR-5.1–5.3 |
| Outer-product decomposition (efficiency) | ✅ FR-4.3 |
| Visualization requirements | ✅ FR-6 |
| Multi-hypothesis data collection (H-M1/H-M2) | ✅ NFR-5, FR-5.4 |
| Seed=1 (EXISTENCE PoC single seed) | ✅ FR-3.1 |
| Abort/Pivot failure conditions | ✅ Success Criteria table |

---

*Generated by Phase 3 Workflow (inline PRD generation — BMAD bmm not installed)*
*Source: Phase 2C Experiment Brief (02c_experiment_brief.md)*
*Hypothesis: H-E1 | Type: EXISTENCE | Gate: MUST_WORK*
*Next Step: Phase 3 Step 3 — Architecture Agent*
