# H-E1: Gradient Abnormality Detection on Minority Groups

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE  
**Gate:** MUST_WORK  
**Status:** Experiment Design Complete (Phase 2C)  
**Date:** 2026-08-20  

---

## Quick Summary

**Research Question:**  
Do minority group samples exhibit higher gradient abnormality than majority group samples on spuriously-correlated datasets?

**Hypothesis Statement:**  
Minority group samples (waterbird-land, landbird-water) exhibit GAIA-Z gradient abnormality scores ≥0.2 higher than majority group samples (waterbird-water, landbird-land) on Waterbirds dataset.

**Approach:**  
Train ResNet-50 on Waterbirds → Extract GradCAM gradients → Compute GAIA-Z scores → Statistical test (t-test, Cohen's d)

**Success Criteria:**
- GAIA-Z(minority) ≥ GAIA-Z(majority) + 0.2
- p < 0.01 (statistical significance)
- Cohen's d ≥ 0.8 (large effect size)

**Timeline:** ~4 hours (3hr training + 1hr analysis)

---

## Contents

This directory contains complete Phase 2C experiment design for hypothesis h-e1:

```
h-e1/
├── README.md                   # This file (overview)
├── experiment_design.md        # Full experiment specification
├── dataset_spec.yaml           # Waterbirds dataset details
├── model_spec.yaml             # ResNet-50 training configuration
├── metrics_spec.yaml           # GAIA-Z computation + statistical tests
└── implementation_refs.md      # Code repos, dependencies, troubleshooting
```

---

## Key Files

### 1. experiment_design.md
**Purpose:** Complete experiment protocol  
**Contents:**
- Hypothesis statement
- Dataset/model specifications
- 4-phase procedure (train → gradients → GAIA-Z → stats)
- Success criteria + gate behavior
- Timeline + directory structure

**Read this first** for end-to-end understanding.

### 2. dataset_spec.yaml
**Purpose:** Waterbirds dataset configuration  
**Key Details:**
- Source: WILDS benchmark (`wilds.get_dataset('waterbirds')`)
- Test size: 5794 samples (PRIMARY EVALUATION)
- 4 groups: 2 majority (90% train) + 2 minority (10% train)
- Spurious: background (water/land) correlates with class (waterbird/landbird)

### 3. model_spec.yaml
**Purpose:** ResNet-50 training setup  
**Key Details:**
- Architecture: ResNet-50 (ImageNet pretrained)
- Training: SGD (lr=1e-3, momentum=0.9, weight_decay=1e-4), 300 epochs
- Target: WGA <80%, minority_acc ≥60%
- GradCAM target: layer4 (final conv block)

### 4. metrics_spec.yaml
**Purpose:** GAIA-Z computation + statistical tests  
**Key Details:**
- GAIA-Z: zero-deflation ratio (ε=1e-6)
- Statistical test: two-sample t-test (Welch's)
- Effect size: Cohen's d
- Visualizations: box plots, histograms

### 5. implementation_refs.md
**Purpose:** Code repositories + dependencies  
**Key Details:**
- WILDS: https://github.com/p-lambda/wilds
- GradCAM: https://github.com/jacobgil/pytorch-grad-cam (pip: grad-cam)
- GroupDRO: https://github.com/kohpangwei/group_DRO (hyperparameter reference)
- Full dependency list + installation commands

---

## Experiment Workflow

### Phase 1: Model Training (~3 hours)
```bash
# Train ResNet-50 on Waterbirds
python train_model.py --config configs/config.yaml

# Verify:
# - WGA <80% (spurious learning confirmed)
# - Minority accuracy ≥60% (GradCAM validity)
# - Average accuracy >95% (sanity check)
```

### Phase 2: Gradient Collection (~15 min)
```bash
# Extract GradCAM gradients from test set
python collect_gradients.py \
    --checkpoint checkpoints/trained_model.pth \
    --output outputs/gradients.npz
```

### Phase 3: GAIA-Z Computation (~5 min)
```bash
# Compute GAIA-Z scores per sample
python compute_gaia_z.py \
    --gradients outputs/gradients.npz \
    --output outputs/gaia_z_scores.csv
```

### Phase 4: Statistical Analysis (<1 min)
```bash
# Perform t-test + effect size
python statistical_test.py \
    --scores outputs/gaia_z_scores.csv \
    --output outputs/statistical_results.json

# Generates:
# - statistical_results.json (PASS/FAIL decision)
# - plots/gaia_z_boxplot_by_type.png
# - plots/gaia_z_histogram.png
```

---

## Success Criteria

### Primary (MUST_WORK Gate)

✓ **Divergence:** GAIA-Z(minority) - GAIA-Z(majority) ≥ 0.2  
✓ **Significance:** p-value < 0.01 (two-sample t-test)

### Secondary

✓ **Effect Size:** Cohen's d ≥ 0.8 (large effect)

### Quality Gates

✓ **Training:** WGA <80%, minority_acc ≥60%, avg_acc >95%  
✓ **Data:** 5794 test samples with valid GAIA-Z scores  
✓ **Reproducibility:** Seed=42, deterministic results

---

## Gate Behavior

```
IF h-e1 PASSES:
    → Proceed to h-m-integrated (mechanism validation)
    → Unblock h-m-mitigate (mitigation hypothesis)

IF h-e1 FAILS:
    → ABANDON gradient abnormality approach
    → Block h-m-integrated, h-m-mitigate
    → Investigate failure mode (divergence vs significance vs effect size)
```

**Rationale:** h-e1 is the foundation hypothesis. If gradient abnormality doesn't exist in minority groups, the entire approach (mechanism + mitigation) is invalid.

---

## Dependencies

### Quick Install
```bash
pip install torch torchvision wilds grad-cam scipy matplotlib seaborn pandas pyyaml tqdm
```

### Full Environment
See `implementation_refs.md` Section 2 for detailed installation instructions.

---

## Computational Requirements

**Hardware:**
- GPU: 1× NVIDIA (≥8GB VRAM, RTX 3070+)
- CPU: 8+ cores
- RAM: 16GB minimum
- Storage: ~5GB

**Runtime:**
- Training: ~3 hours (300 epochs, batch_size=128)
- Gradient collection: ~15 minutes (5794 samples)
- GAIA-Z + stats: ~5 minutes
- **Total:** ~3.5 hours

---

## Outputs

### Required Files
```
outputs/
├── gaia_z_scores.csv           # Per-sample GAIA-Z scores + metadata
├── statistical_results.json    # t-test, Cohen's d, PASS/FAIL decision
└── training_log.csv            # Training metrics per epoch

plots/
├── gaia_z_boxplot_by_type.png  # Minority vs majority
├── gaia_z_boxplot_by_group.png # 4 groups
└── gaia_z_histogram.png        # Distributions overlaid

checkpoints/
└── trained_model.pth           # Trained ResNet-50
```

### Optional Files (Debugging)
```
outputs/
└── gradients.npz               # Raw gradient tensors (~500MB)
```

---

## Risk Mitigation

### Critical Risks

**R1: Minority accuracy <60%**
- Detection: Monitor during training
- Impact: GradCAM may highlight spurious (not core) features (Assumption A1 violation)
- Response: Flag in results, pivot to global regularization (not spatial)

**R3: Complexity confound**
- Detection: Visual inspection, augmentation test (swap backgrounds)
- Impact: GAIA-Z captures image complexity, not spurious conflict
- Response: If augmentation effect <10%, ABANDON

---

## Next Steps

### After h-e1 Design Complete (Current)
1. **Phase 3:** Implementation planning (PRD, architecture, PRP)
2. Generate Archon tasks for code implementation

### After h-e1 Passes
1. Archive outputs for reproducibility
2. Design h-m-integrated experiment (correlation sweep)
3. Reuse trained model for mechanism validation

### After h-e1 Fails
1. Analyze failure mode in detail
2. Generate diagnostic plots
3. Decision: ABANDON or reformulate hypothesis

---

## Contact & References

**Archon Task ID:** 28693385-e2a4-42df-ba9a-8f8e903c76bb  
**Phase Task ID:** e5e29855-a636-4d17-b973-516946a29a29  
**Verification Plan:** `../02b_verification_plan.md`  
**Experiment Brief:** `../02c_experiment_brief.md`  

**Key Papers:**
- Sagawa et al. 2020: Distributionally Robust Neural Networks (Waterbirds)
- Koh et al. 2021: WILDS Benchmark
- Chen et al. 2023: GAIA (Gradient Abnormality for OOD Detection)

---

**Document Status:** Complete  
**Last Updated:** 2026-08-20  
**Next Phase:** Phase 3 (Implementation Planning)
