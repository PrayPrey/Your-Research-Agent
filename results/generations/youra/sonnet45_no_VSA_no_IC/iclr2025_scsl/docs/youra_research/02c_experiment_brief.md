# Experiment Brief: H-E1 Gradient Abnormality Detection

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE  
**Gate:** MUST_WORK  
**Date:** 2026-08-20  
**Phase:** 2C Experiment Design  

---

## 1. Hypothesis Statement

**Claim:** Minority group samples (waterbird-land, landbird-water) exhibit significantly higher GAIA-Z gradient abnormality scores than majority group samples (waterbird-water, landbird-land) on the Waterbirds dataset.

**Rationale:** Validates that gradient abnormality (GAIA framework) extends from OOD detection to subpopulation shift detection within ID distribution. Spurious reliance creates gradient scattering when shortcuts conflict with core features in minority samples.

**Success Criteria (PoC: Direction-based):**
- Primary: Mean GAIA-Z(minority) ≥ Mean GAIA-Z(majority) + 0.2 AND p < 0.01
- Secondary: Cohen's d ≥ 0.8 (large effect size)

**Gate Behavior:**
- Type: MUST_WORK
- If Fail: ABANDON entire gradient abnormality approach

---

## 2. Dataset Specification

### 2.1 Dataset Details

| Field | Value |
|-------|-------|
| **Name** | Waterbirds |
| **Type** | standard |
| **Source** | WILDS benchmark (pip install wilds) |
| **Access Method** | `wilds.get_dataset('waterbirds', download=True)` |
| **Cache Path** | `~/.wilds/waterbirds_v1.0/` |
| **License** | Open (academic use) |
| **Citation** | Sagawa et al. 2020 (DRO), Koh et al. 2021 (WILDS) |

### 2.2 Data Characteristics

**Size:**
- Train: 4795 samples (standard split)
- Validation: 1199 samples
- Test: 5794 samples (**PRIMARY EVALUATION SET**)
- Total: 11,788 images

**Structure:**
- Classes: 2 (waterbird=0, landbird=1)
- Backgrounds: 2 (water=0, land=1)
- Groups: 4 (class × background)
  - Group 0: waterbird-water (MAJORITY, ~3498 train samples, 90%)
  - Group 1: waterbird-land (MINORITY, ~184 train samples, 10%)
  - Group 2: landbird-water (MINORITY, ~467 train samples, 10%)
  - Group 3: landbird-land (MAJORITY, ~3626 train samples, 90%)

**Spurious Correlation:**
- Training correlation: 90% (background correlates with class)
- Test correlation: ~50% (balanced across groups)
- Group annotations: Available via `dataset.metadata_array`

**Image Properties:**
- Resolution: 224×224 (after preprocessing)
- Format: RGB
- Preprocessing: ImageNet normalization (mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])

### 2.3 Verification Checklist

- [ ] Dataset downloads successfully via WILDS API
- [ ] Test set contains 5794 samples with group labels
- [ ] Group distribution matches expected (majority ~90%, minority ~10% in train)
- [ ] Images load correctly with 224×224 resolution
- [ ] Metadata array provides (class, background, group) annotations

---

## 3. Model Specification

### 3.1 Model Details

| Field | Value |
|-------|-------|
| **Architecture** | ResNet-50 |
| **Source** | torchvision.models.resnet50 |
| **Pretrained** | ImageNet (torchvision default) |
| **Output Layer** | 2-class linear classifier (binary) |
| **Cache Path** | `~/.cache/torch/hub/checkpoints/resnet50-*.pth` |

### 3.2 Training Configuration

**Hyperparameters (from GroupDRO baseline):**
- Optimizer: SGD
- Learning rate: 1e-3
- Momentum: 0.9
- Weight decay: 1e-4
- Batch size: 128
- Epochs: 300 (early stop if WGA plateau)
- Loss: Cross-entropy

**Expected Performance:**
- Average Accuracy: ~95-97%
- Worst-Group Accuracy (WGA): <80% (confirms spurious reliance)
- Minority group accuracy: ~60-70% (required for GradCAM validity, see A1)

### 3.3 Verification Checklist

- [ ] Model trains to convergence (avg acc >95%)
- [ ] WGA <80% (confirms spurious correlation learning)
- [ ] Minority group accuracy ≥60% (validates GradCAM assumption A1)
- [ ] Model checkpoint saved for gradient analysis

---

## 4. Experiment Design

### 4.1 Procedure

**Phase 1: Model Training**
1. Load Waterbirds dataset via WILDS
2. Train ResNet-50 on 90% correlation split
3. Verify WGA <80% and minority accuracy ≥60%
4. Save trained checkpoint

**Phase 2: Gradient Collection**
1. Load test set (5794 samples) with group annotations
2. For each test sample:
   - Forward pass → predicted class
   - Compute GradCAM attribution on final conv layer (layer4)
   - Extract gradient tensor: ∇_{A}y_c (gradients w.r.t. activations)
3. Store gradients with metadata: (sample_id, group_id, gradient_tensor)

**Phase 3: GAIA-Z Computation**
1. For each sample's gradient tensor:
   - Compute channel-wise statistics (mean, std)
   - Measure zero-deflation ratio: GAIA-Z = |{g_i : |g_i| < ε}| / total_elements
   - Store GAIA-Z score per sample
2. Aggregate by group: {minority_scores, majority_scores}

**Phase 4: Statistical Analysis**
1. Two-sample t-test: H0: μ(minority) = μ(majority)
2. Compute Cohen's d effect size
3. Visualize distributions (box plot, histogram)

### 4.2 Implementation Plan

**Key Components:**

1. **GradCAM Implementation**
   - Library: pytorch-grad-cam (pip install grad-cam)
   - Target layer: model.layer4 (final conv block)
   - Reference: https://github.com/jacobgil/pytorch-grad-cam

2. **GAIA-Z Metric**
   - Input: gradient tensor (C×H×W from GradCAM)
   - Zero threshold: ε = 1e-6 (near-zero cutoff)
   - Output: scalar in [0,1] (ratio of near-zero elements)

3. **Statistical Testing**
   - Library: scipy.stats.ttest_ind
   - Effect size: (μ_minority - μ_majority) / pooled_std
   - Visualization: matplotlib/seaborn

**Code Structure:**
```
experiments/
├── h_e1_detection/
│   ├── train_model.py          # Phase 1: Train ResNet-50
│   ├── collect_gradients.py    # Phase 2: GradCAM extraction
│   ├── compute_gaia_z.py       # Phase 3: GAIA-Z scoring
│   ├── statistical_test.py     # Phase 4: t-test + effect size
│   ├── utils/
│   │   ├── gradcam.py         # GradCAM wrapper
│   │   ├── gaia_metrics.py    # GAIA-Z computation
│   │   └── visualization.py   # Plotting utilities
│   └── configs/
│       └── h_e1_config.yaml   # Hyperparameters
```

### 4.3 Computational Requirements

**Resources:**
- GPU: 1× NVIDIA GPU with ≥8GB VRAM (RTX 3070 or better)
- CPU: 8+ cores (for data loading)
- RAM: 16GB minimum
- Storage: ~2GB (dataset + checkpoints)

**Runtime Estimates:**
- Model training: ~2-3 hours (300 epochs)
- Gradient collection: ~15 minutes (5794 samples, GPU inference)
- GAIA-Z computation: ~5 minutes (CPU vectorized ops)
- Total: ~3 hours

---

## 5. Evaluation Metrics

### 5.1 Primary Metrics

| Metric | Definition | Success Threshold |
|--------|------------|-------------------|
| **GAIA-Z Divergence** | μ(minority) - μ(majority) | ≥ 0.2 |
| **p-value** | Two-sample t-test | < 0.01 |
| **Cohen's d** | Effect size | ≥ 0.8 (large) |

### 5.2 Secondary Metrics

| Metric | Definition | Purpose |
|--------|------------|---------|
| **WGA** | min(acc_group0, ..., acc_group3) | Verify spurious reliance (<80%) |
| **Minority Accuracy** | avg(acc_group1, acc_group2) | Validate GradCAM assumption (≥60%) |
| **Average Accuracy** | Overall test accuracy | Sanity check (~95%) |

### 5.3 Visualization

**Required Plots:**
1. Box plot: GAIA-Z scores by group (majority vs minority)
2. Histogram: GAIA-Z distributions overlaid
3. Scatter: GAIA-Z vs group ID (4 groups)
4. Training curve: WGA over epochs

**Statistical Table:**
```
Group | N    | GAIA-Z Mean | GAIA-Z Std | Accuracy
------|------|-------------|------------|----------
Maj-0 | 3498 | X.XX        | X.XX       | XX.X%
Min-1 | 184  | X.XX        | X.XX       | XX.X%
Min-2 | 467  | X.XX        | X.XX       | XX.X%
Maj-3 | 3626 | X.XX        | X.XX       | XX.X%
------|------|-------------|------------|----------
Minority Avg  | X.XX        | X.XX       | XX.X%
Majority Avg  | X.XX        | X.XX       | XX.X%
Divergence    | X.XX (p=X.XXX, d=X.XX)
```

---

## 6. Baseline Comparison

**Status:** NOT APPLICABLE (h-e1 is existence hypothesis)

**Rationale:** This hypothesis tests whether gradient abnormality *exists* in minority groups, not whether it outperforms other methods. No baseline comparison required.

**Note:** Baselines (GroupDRO, JTT) become relevant in h-m-mitigate (mitigation hypothesis).

---

## 7. Risk Mitigation

### 7.1 Critical Risks

| Risk ID | Description | Mitigation | Fallback |
|---------|-------------|------------|----------|
| **R1** | Minority accuracy <60% → GradCAM highlights spurious (not core) features | Monitor during training; if <60%, flag as assumption violation | Fall back to global gradient regularization (no spatial masking) |
| **R3** | Complexity confound → GAIA-Z captures image complexity, not spurious conflict | Use Waterbirds only (controlled backgrounds); validate via augmentation test (swap backgrounds) | Abandon if augmentation effect <10% |

### 7.2 Validation Checks

**During Training:**
- [ ] WGA <80% at convergence (confirms spurious learning)
- [ ] Minority accuracy ≥60% (validates GradCAM assumption A1)

**During Gradient Analysis:**
- [ ] GAIA-Z scores non-uniform (not all ~0.5)
- [ ] Visual inspection: minority samples show higher GAIA-Z

**Post-hoc Validation (optional, for R3):**
- [ ] Swap backgrounds on 100 minority samples → expect GAIA-Z reduction ≥30%

---

## 8. Implementation References

### 8.1 Code Repositories

| Resource | URL | Purpose |
|----------|-----|---------|
| **WILDS Benchmark** | https://github.com/p-lambda/wilds | Dataset loading |
| **GroupDRO Baseline** | https://github.com/kohpangwei/group_DRO | Training reference |
| **PyTorch GradCAM** | https://github.com/jacobgil/pytorch-grad-cam | GradCAM implementation |

### 8.2 Key Dependencies

```
# requirements.txt
torch>=2.0.0
torchvision>=0.15.0
wilds>=2.0.0
grad-cam>=1.5.0
scipy>=1.10.0
matplotlib>=3.7.0
seaborn>=0.12.0
pyyaml>=6.0
tqdm>=4.65.0
```

### 8.3 Data Files

**Input:**
- Waterbirds dataset (auto-downloaded via WILDS)

**Output:**
- `trained_model.pth` (ResNet-50 checkpoint)
- `gradients.npz` (gradient tensors per sample)
- `gaia_z_scores.csv` (GAIA-Z per sample + metadata)
- `statistical_results.json` (t-test, Cohen's d, means)
- `plots/` (visualizations)

---

## 9. Success Criteria Summary

### 9.1 Must-Have (Gate: MUST_WORK)

✓ **Primary:**
- GAIA-Z(minority) ≥ GAIA-Z(majority) + 0.2
- p-value < 0.01 (two-sample t-test)

✓ **Secondary:**
- Cohen's d ≥ 0.8 (large effect size)

### 9.2 Quality Checks

✓ **Training:**
- WGA <80% (spurious reliance confirmed)
- Minority accuracy ≥60% (GradCAM validity, A1)

✓ **Analysis:**
- GAIA-Z scores cover meaningful range (not degenerate)
- Visual inspection confirms minority scores higher

### 9.3 Failure Response

**If Primary Criteria Fail:**
- Action: ABANDON gradient abnormality approach
- Rationale: Foundation hypothesis invalid → dependent hypotheses (h-m-integrated, h-m-mitigate) cannot proceed

**If Quality Checks Fail:**
- WGA ≥80%: Retrain with different hyperparameters
- Minority accuracy <60%: Assumption A1 violated → pivot to global regularization (no spatial masking)

---

## 10. Timeline & Milestones

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| **Phase 1: Training** | 3 hours | trained_model.pth, WGA <80% verified |
| **Phase 2: Gradients** | 15 min | gradients.npz (5794 samples) |
| **Phase 3: GAIA-Z** | 5 min | gaia_z_scores.csv |
| **Phase 4: Statistics** | 10 min | statistical_results.json, plots/ |
| **Total** | ~4 hours | Complete h-e1 validation |

**Next Steps (if h-e1 passes):**
- Proceed to h-m-integrated (mechanism validation)
- Design experiment for correlation sweep (50%-95% spurious rates)

---

## Appendices

### A. GAIA-Z Formula

**Definition:**
```
GAIA-Z(G) = |{g_i ∈ G : |g_i| < ε}| / |G|
```

Where:
- G = gradient tensor (flattened)
- ε = 1e-6 (near-zero threshold)
- Output: ratio in [0, 1]

**Interpretation:**
- High GAIA-Z → many near-zero gradients → gradient scattering/abnormality
- Low GAIA-Z → sparse near-zero gradients → normal gradient flow

### B. GradCAM Target Layer

**Layer Selection:**
- Target: `model.layer4` (final conv block before avgpool)
- Rationale: Highest semantic feature representation
- Shape: (batch, 2048, 7, 7) for ResNet-50 with 224×224 input

**Gradient Extraction:**
```python
from pytorch_grad_cam import GradCAM

cam = GradCAM(model=model, target_layers=[model.layer4])
grayscale_cam = cam(input_tensor, targets=None)  # Class-agnostic
# Extract raw gradients from cam.activations_and_grads.gradients
```

### C. Statistical Test Details

**Two-Sample t-test:**
- Type: Independent samples
- Assumption: Unequal variances (Welch's t-test)
- Library: `scipy.stats.ttest_ind(equal_var=False)`

**Cohen's d:**
```
d = (μ_minority - μ_majority) / √((σ²_minority + σ²_majority) / 2)
```

Interpretation:
- d ≥ 0.8: Large effect
- d ≥ 0.5: Medium effect
- d ≥ 0.2: Small effect

---

**Document Status:** Complete  
**Next Action:** Phase 3 Implementation Planning (PRD, Architecture, PRP)  
**Archon Task ID:** 28693385-e2a4-42df-ba9a-8f8e903c76bb  
**Phase Task ID:** e5e29855-a636-4d17-b973-516946a29a29
