# Product Requirements Document: H-M2

**Hypothesis ID:** H-M2
**Type:** MECHANISM (Spurious-Specificity Test)
**Date:** 2026-04-14
**Author:** Anonymous
**Phase:** 3 - Implementation Planning

---

## Executive Summary

This PRD defines the implementation requirements for validating hypothesis H-M2: that trajectory divergence reflects spurious-feature conflict specifically, demonstrated by differential AUROC attenuation under GroupDRO vs random reweighting interventions.

**Core Claim:** If trajectory divergence reflects spurious-feature conflict specifically, then AUROC will attenuate >0.10 under GroupDRO training but <0.05 under variance-matched random reweighting, because GroupDRO targets spurious reliance while random reweighting only smooths gradients generically.

**Gate:** SHOULD_WORK - If this fails, explore generic hardness explanation but continue pipeline.

**Base Hypothesis:** H-E1 (PASS, AUROC=0.9452) - Reuses trajectory extraction infrastructure

---

## Problem Statement

### Background
H-E1 demonstrated that loss trajectory features can predict minority group membership with AUROC=0.9452. However, this could reflect either:
1. **Spurious-specific conflict:** Trajectory divergence caused by spurious feature reliance
2. **Generic sample hardness:** Minority samples are simply "harder" regardless of spurious correlations

### Opportunity
By comparing AUROC attenuation under two interventions:
- **GroupDRO:** Specifically targets spurious feature reliance by upweighting worst-group loss
- **Random reweighting:** Generic gradient smoothing without targeting spurious features

If GroupDRO significantly reduces trajectory divergence (AUROC drop) while random reweighting does not, this confirms the spurious-specificity hypothesis.

### Success Criteria
- **Primary:** AUROC_ERM - AUROC_GroupDRO > 0.10 (GroupDRO attenuates divergence)
- **Secondary:** AUROC_ERM - AUROC_Random < 0.05 (Random reweighting has no effect)
- **Interpretation:** Both conditions met → divergence is spurious-specific

---

## Functional Requirements

### FR-1: Dataset Loading and Preprocessing

**FR-1.1: Waterbirds Dataset Loading**
- Reuse dataset from H-E1 cache: `/home/anonymous/YouRA_results_new_4_sonnet45/TEST_scsl_opus45_4/docs/youra_research/20260414_scsl/.data_cache/datasets/waterbirds/`
- Load Waterbirds dataset (4,795 training, 1,199 validation, 5,794 test samples)
- Preserve group labels (4 groups: bird_type × background)
- **NEW:** Group counts required for GroupDRO weight initialization

**FR-1.2: Data Preprocessing**
- Training transforms: RandomResizedCrop(224, scale=0.7-1.0), RandomHorizontalFlip(), Normalize(ImageNet)
- Evaluation transforms: Resize(256), CenterCrop(224), Normalize(ImageNet)
- ImageNet normalization: mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]

**FR-1.3: Group Information**
- Extract group counts for GroupDRO initialization
- Compute minority mask for evaluation
- Groups: G0 (landbird/land), G1 (landbird/water=minority), G2 (waterbird/land=minority), G3 (waterbird/water)

### FR-2: Model Architecture

**FR-2.1: ResNet-50 (Shared Across Regimes)**
- Load torchvision ResNet-50 with ImageNet pretrained weights
- Replace final FC layer: Linear(2048, 2) for binary classification
- Same architecture for ERM, GroupDRO, and Random Reweighting

**FR-2.2: Model Initialization**
- Use `torchvision.models.ResNet50_Weights.IMAGENET1K_V1`
- **CRITICAL:** Fresh initialization for each training regime
- Set random seed per regime for reproducibility

### FR-3: Three Training Regimes

**FR-3.1: ERM Training (Baseline)**
- Optimizer: SGD with momentum=0.9, weight_decay=0.0001
- Learning rate: 0.001
- Batch size: 128
- Epochs: 20
- Loss: Standard CrossEntropyLoss (equal weight per sample)
- **Baseline AUROC reference from H-E1:** 0.9452

**FR-3.2: GroupDRO Training**
- Optimizer: SGD with momentum=0.9, weight_decay=1.0 (strong regularization per official repo)
- Learning rate: 0.001
- Batch size: 128
- Epochs: 20
- **GroupDRO Parameters:**
  - gamma (step size): 0.1
  - Initial group weights: uniform (1/4 each)
  - Weight update: exponentiated gradient ascent on group losses
- Loss computation:
  ```python
  per_sample_loss = F.cross_entropy(logits, labels, reduction='none')
  group_losses = [per_sample_loss[group_mask].mean() for group in groups]
  group_weights = group_weights * torch.exp(gamma * group_losses)
  group_weights = group_weights / group_weights.sum()
  loss = (group_losses * group_weights).sum()
  ```

**FR-3.3: Random Reweighting Training (Control)**
- Optimizer: SGD with momentum=0.9, weight_decay=0.0001
- Learning rate: 0.001
- Batch size: 128
- Epochs: 20
- **Variance-matched random weights:**
  - Sample weights from same distribution as GroupDRO weight variance
  - Verify: Var(gradient_random) ≈ Var(gradient_groupdro)
- Loss computation:
  ```python
  per_sample_loss = F.cross_entropy(logits, labels, reduction='none')
  weights = random_weights[sample_idx]  # Pre-computed variance-matched
  loss = (per_sample_loss * weights).sum() / weights.sum()
  ```

### FR-4: Trajectory Feature Extraction (Reuse from H-E1)

**FR-4.1: Per-Sample Loss Logging**
- After each training epoch (1-5), run deterministic evaluation pass
- Log per-sample losses indexed by sample ID
- **Apply to all 3 training regimes**

**FR-4.2: Feature Computation (From H-E1)**
- **F1 (Initial Loss):** L₁ = loss at epoch 1
- **F2 (Slope):** (L₅ - L₁) / 4
- **F3 (Variance):** var(L_normalized) where L_normalized = L / L₁
- **F4 (Convergence Time):** First epoch where loss reaches 95% of minimum

**FR-4.3: Feature Output**
- Generate feature matrix for each regime: shape (num_samples, 4)
- Store separately for ERM, GroupDRO, and Random Reweighting

### FR-5: Evaluation

**FR-5.1: AUROC Computation (Per Regime)**
- Use sklearn LogisticRegression as classifier
- Apply 5-fold stratified cross-validation
- Compute mean and std AUROC for each training regime:
  - AUROC_ERM
  - AUROC_GroupDRO
  - AUROC_Random

**FR-5.2: Delta AUROC Computation**
- ΔAUROC_GroupDRO = AUROC_ERM - AUROC_GroupDRO
- ΔAUROC_Random = AUROC_ERM - AUROC_Random

**FR-5.3: Gate Evaluation**
- **Pass Condition 1:** ΔAUROC_GroupDRO > 0.10
- **Pass Condition 2:** ΔAUROC_Random < 0.05
- **Gate Result:** PASS if BOTH conditions met

**FR-5.4: Mechanism Verification**
- Verify GroupDRO weights diverge from uniform (mechanism active)
- Verify gradient variance matching for random reweighting
- Log activation indicators per epoch

### FR-6: Visualization

**FR-6.1: Required Figures**
- **Gate Metrics Comparison:** Bar chart showing ΔAUROC_GroupDRO vs ΔAUROC_Random with threshold lines at 0.10 and 0.05
- **AUROC Comparison:** Bar chart of AUROC_ERM, AUROC_GroupDRO, AUROC_Random with error bars

**FR-6.2: Additional Figures**
- **Training Loss Trajectories:** Per-group loss curves under each training regime (3 panels)
- **Group Weight Evolution:** GroupDRO group weights across epochs
- **Gradient Variance Verification:** Histogram comparing gradient variance of GroupDRO vs Random Reweighting

**FR-6.3: Output**
- Save all figures to `{hypothesis_folder}/figures/`
- Support PNG format at 300 DPI

### FR-7: Results Logging

**FR-7.1: Metrics Output**
- AUROC for each regime with 95% CI
- Delta AUROC values
- GroupDRO final group weights
- Gradient variance comparison

**FR-7.2: Gate Evaluation**
- Compare against thresholds (0.10 and 0.05)
- Output PASS/FAIL determination
- Log to verification_state.yaml

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seeds per regime (seed=42+regime_idx)
- Deterministic CUDA operations where possible
- 3 seeds per regime for statistical reliability

### NFR-2: Performance
- Single GPU execution (select lowest memory usage GPU)
- Total training time: ~90 minutes (3 regimes × 20 epochs × ~1.5 min/regime)
- Memory usage < 16GB GPU RAM

### NFR-3: Code Quality
- Type hints for all function signatures
- Docstrings with tensor shape documentation
- Modular design reusing H-E1 trajectory infrastructure
- Clear separation between training regimes

### NFR-4: Logging
- Console progress for epoch completion per regime
- GroupDRO weight updates logged per epoch
- Gradient variance logged for verification

---

## Technical Dependencies

### Python Packages
- PyTorch >= 2.0
- torchvision >= 0.15
- scikit-learn >= 1.0
- numpy >= 1.20
- matplotlib >= 3.5
- WILDS >= 2.0 (or manual download)
- tqdm (progress bars)
- PyYAML (config files)

### Hardware
- Single NVIDIA GPU (8GB+ VRAM recommended)
- 32GB+ system RAM
- 10GB+ disk space for dataset

### External Resources
- Waterbirds dataset (reuse from H-E1 cache)
- ImageNet pretrained weights (auto-download)

### Reference Implementations
- kohpangwei/group_DRO (official GroupDRO)
- coastalcph/fairlex (modular GroupDRO)
- danieltan07/learning-to-reweight-examples (sample reweighting)

---

## Data Flow

```
[Waterbirds Dataset + Group Labels]
        ↓
[DataLoader with index + group tracking]
        ↓
┌───────────────────────────────────────────────────────┐
│           3 INDEPENDENT TRAINING PIPELINES            │
├───────────────┬───────────────┬───────────────────────┤
│  ERM Training │ GroupDRO      │ Random Reweighting    │
│  (baseline)   │ (spurious-    │ (control)             │
│               │  targeted)    │                       │
├───────────────┼───────────────┼───────────────────────┤
│  Loss Traj.   │  Loss Traj.   │  Loss Traj.           │
│  Features     │  Features     │  Features             │
└───────┬───────┴───────┬───────┴───────────┬───────────┘
        ↓               ↓                   ↓
   AUROC_ERM      AUROC_GroupDRO       AUROC_Random
        ↓               ↓                   ↓
        └───────────────┴───────────────────┘
                        ↓
              [Delta AUROC Comparison]
                        ↓
              [Gate: ΔGDRO>0.10 AND ΔRand<0.05]
```

---

## Success Metrics

| Metric | Target | Baseline | Gate |
|--------|--------|----------|------|
| ΔAUROC_GroupDRO | > 0.10 | 0.00 | SHOULD_WORK |
| ΔAUROC_Random | < 0.05 | 0.00 | SHOULD_WORK |
| GroupDRO Mechanism | Weights diverge | Uniform | Verification |
| Variance Matching | Within 20% | N/A | Verification |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| GroupDRO doesn't attenuate AUROC | Medium | Medium (explore generic hardness) | Multiple seed averaging |
| Random reweighting also attenuates | Low | High (confounds mechanism) | Verify variance matching |
| Training instability | Low | Medium | Use official hyperparameters |
| Memory overflow | Low | Low | Reduce batch size |

---

## Implementation Priority

1. **P0 (Critical Path):**
   - GroupDRO training loop with loss logging
   - Random reweighting with variance matching
   - AUROC computation per regime
   - Delta AUROC evaluation

2. **P1 (Required):**
   - Gate metrics visualization
   - GroupDRO weight evolution tracking
   - Mechanism verification checks

3. **P2 (Nice to have):**
   - Gradient variance histograms
   - Per-group loss trajectory plots

---

## Appendix: Traceability to Phase 2C

| PRD Section | Phase 2C Source |
|-------------|-----------------|
| Dataset specs | Experiment Specification > Dataset |
| Three training regimes | Experiment Specification > Training Protocol |
| GroupDRO parameters | Exa GitHub: kohpangwei/group_DRO |
| Random reweighting | Exa GitHub: danieltan07/learning-to-reweight-examples |
| Evaluation metrics | Experiment Specification > Evaluation |
| Gate conditions | Gate Condition (ΔAUROC thresholds) |
| Base hypothesis | H-E1 validated infrastructure |

---

## Appendix: Reuse from H-E1

| Component | H-E1 Source | Reuse Strategy |
|-----------|-------------|----------------|
| Dataset loading | h-e1/code/data_loader.py | Import directly |
| Trajectory logging | h-e1/code/trainer.py | Extend for 3 regimes |
| Feature extraction | h-e1/code/features.py | Import directly |
| AUROC evaluation | h-e1/code/evaluate.py | Apply per regime |
| Visualization | h-e1/code/visualize.py | Extend with new figures |

---

*Generated by Phase 3 Implementation Planning*
*Source: h-m2/02c_experiment_brief.md*
*Base Hypothesis: H-E1 (PASS, AUROC=0.9452)*
*Next: Architecture Design*
