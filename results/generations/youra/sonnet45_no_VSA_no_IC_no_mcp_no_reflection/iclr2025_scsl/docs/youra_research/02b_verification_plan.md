# Phase 2B: Verification Plan
**Generated**: 2026-08-28T22:14:33Z  
**Main Hypothesis**: H-TemporalGradient-v1  
**Execution Mode**: UNATTENDED

---

## Main Hypothesis

**ID**: H-TemporalGradient-v1  
**Title**: Gradient-Level Temporal Signature of Spurious Feature Learning  
**Statement**: Under gradient descent optimization on spurious correlation benchmarks (CMNIST, Waterbirds, CelebA, NICO++), if we measure per-epoch gradient norms for spurious features vs core features, then spurious features will converge significantly earlier (E_s < E_c by ≥2 epochs), because spurious features provide simpler, lower-level decision boundaries that gradient descent implicitly prefers early in training.

**Confidence Level**: 0.85  
**Source**: `03_refinement.yaml` (Phase 2A output)

---

## Sub-Hypothesis Breakdown

### 1. H-E1: Temporal Ordering Foundation (MUST_WORK)
**Type**: EXISTENCE  
**Statement**: Spurious features converge at least 2 epochs earlier than core features across all 4 datasets (CMNIST, Waterbirds, CelebA, NICO++)

**Gate**: MUST_WORK (required for all dependent hypotheses)  
**Status**: READY (no prerequisites)  
**Prerequisites**: None

**Experimental Approach**:
- Ablation training on CMNIST (spurious-only, core-only, baseline)
- Measure convergence epochs E_s and E_c (gradient norm < 10% of peak for 3 consecutive epochs)
- Statistical Test 1: Paired t-test on (E_s, E_c) across 10 random seeds
- Success Criterion: p < 0.05 AND mean(E_c - E_s) ≥ 2 epochs

**Timeline**: 2 weeks  
**Risk**: HIGH (foundation hypothesis - failure blocks H-E2, H-E3, H-M1, H-M2)

---

### 2. H-E2: Multi-Metric Signature (SHOULD_WORK)
**Type**: EXISTENCE  
**Statement**: Spurious features exhibit lower gradient variance (V_spurious < V_core, variance ratio < 0.7) and lower forgetting rate than core features

**Gate**: SHOULD_WORK (supporting evidence, not critical)  
**Status**: NOT_STARTED  
**Prerequisites**: [h-e1]

**Experimental Approach**:
- Compute rolling 3-epoch gradient variance for spurious vs core features
- Track forgetting events per Toneva et al. (2019) - examples that flip predictions
- Statistical Test 2: F-test for variance ratio (V_spurious / V_core)
- Statistical Test 3: Paired t-test on forgetting rates
- Statistical Test 4: Partial correlation test (determines if forgetting is independent or derived from E_s)

**Timeline**: 1 week  
**Risk**: MEDIUM (SHOULD_WORK gate - failure does not block Phase 5)

---

### 3. H-E3: Continuous Diagnostic (SHOULD_WORK)
**Type**: EXISTENCE  
**Statement**: GradCAM temporal ratio R_temporal(t) decreases monotonically from epoch 5 to 50 (Kendall τ < -0.7, p < 0.05)

**Gate**: SHOULD_WORK  
**Status**: NOT_STARTED  
**Prerequisites**: [h-e1]

**Experimental Approach**:
- Compute GradCAM saliency maps at each epoch on Waterbirds, CelebA, NICO++
- R_temporal(t) = A_spurious / (A_spurious + A_core) where A = pixel attribution in respective regions
- Statistical Test 5: Kendall τ correlation between R_temporal(t) and epoch t
- Statistical Test 6: Cross-method consistency (R_temporal vs E_s from ablation training)

**Timeline**: 2 weeks  
**Risk**: MEDIUM (novel diagnostic method - may require calibration)

---

### 4. H-M1: Feature Complexity Mechanism (MUST_WORK)
**Type**: MECHANISM  
**Statement**: Temporal gap is driven by feature complexity difference (simpler spurious features converge faster) - validated via layer-neuron consistency test (Test 8)

**Gate**: MUST_WORK (mechanism required for intervention H-C1)  
**Status**: NOT_STARTED  
**Prerequisites**: [h-e1]

**Experimental Approach**:
- Compute neuron-spurious correlation ρ_j from ablation data
- Test layer-wise consistency: do early layers have higher ρ_j than late layers?
- Statistical Test 8: Layer-neuron consistency test (validates that R_temporal and ρ_j align)

**Timeline**: 1 week  
**Risk**: HIGH (mechanism hypothesis - failure blocks H-C1 intervention)

---

### 5. H-M2: Architectural Modulation (SHOULD_WORK)
**Type**: MECHANISM  
**Statement**: CNNs show larger temporal gaps than Vision Transformers (Δ_ResNet > Δ_ViT by ≥2 epochs) due to architectural inductive bias differences

**Gate**: SHOULD_WORK  
**Status**: NOT_STARTED  
**Prerequisites**: [h-e1]

**Experimental Approach**:
- Run ResNet-50 and ViT-B/16 on Waterbirds and CelebA
- Measure temporal gaps Δ_ResNet and Δ_ViT
- Statistical Test 7: Independent samples t-test on architectural differences

**Timeline**: 2 weeks  
**Risk**: MEDIUM (architectural insight - not critical for main hypothesis)

---

### 6. H-C1: Gradient-Aware Intervention (SHOULD_WORK)
**Type**: CONDITION  
**Statement**: Gradient-aware training (lr_j = lr_base * (1 - ρ_j)) matches or exceeds JTT worst-group accuracy on Waterbirds (within 1%)

**Gate**: SHOULD_WORK  
**Status**: NOT_STARTED  
**Prerequisites**: [h-m1]

**Experimental Approach**:
- Implement feature-selective learning rate modulation
- Train on Waterbirds and compare worst-group accuracy against ERM, JTT, Layer-wise Regularization baselines
- Statistical Test 9: Paired t-test on worst-group accuracy (10 seeds)
- Success Criterion: mean(Gradient-Aware) ≥ mean(JTT) - 1%

**Timeline**: 3 weeks  
**Risk**: MEDIUM (intervention validation - SHOULD_WORK allows secondary benefits even if ≈ JTT)

---

## Dependency Graph (DAG)

```
h-e1 (MUST_WORK, READY)
  ├─→ h-e2 (SHOULD_WORK)
  ├─→ h-e3 (SHOULD_WORK)
  ├─→ h-m1 (MUST_WORK)
  │     └─→ h-c1 (SHOULD_WORK)
  └─→ h-m2 (SHOULD_WORK)
```

**Critical Path**: h-e1 → h-m1 → h-c1 (5 weeks + 1 week + 3 weeks = 9 weeks)  
**Parallel Tracks**: h-e2, h-e3, h-m2 can run in parallel with h-m1 after h-e1 completes

---

## Risk Analysis

### High-Risk Hypotheses (MUST_WORK gates)
1. **H-E1** (Temporal Ordering Foundation)
   - **Risk**: If E_s ≥ E_c, entire temporal hypothesis is falsified
   - **Mitigation**: Multi-dataset validation (4 benchmarks) reduces cherry-picking
   - **Fallback**: Test relaxed criterion (E_s < E_c without 2-epoch threshold)

2. **H-M1** (Feature Complexity Mechanism)
   - **Risk**: If layer-neuron consistency fails, mechanism story is weak
   - **Mitigation**: Cross-validate with R_temporal (Test 6)
   - **Fallback**: Alternative mechanism (e.g., loss landscape sharpness)

### Medium-Risk Hypotheses (SHOULD_WORK gates)
- **H-E2, H-E3, H-M2**: Supporting evidence - failures do not block Phase 5
- **H-C1**: Intervention - conservative success criterion (match JTT, not beat it)

---

## Statistical Test Summary

| Test | Hypothesis | Method | Success Criterion |
|------|-----------|--------|-------------------|
| 1 | H-E1 | Paired t-test on (E_s, E_c) | p < 0.05 AND mean gap ≥ 2 epochs |
| 2 | H-E2 | F-test for variance ratio | p < 0.05 AND ratio < 0.7 |
| 3 | H-E2 | Paired t-test on forgetting rates | p < 0.05 AND F_spurious < F_core |
| 4 | H-E2 | Partial correlation (E, F controlled) | Determines if F is independent |
| 5 | H-E3 | Kendall τ (R_temporal vs epoch) | τ < -0.7 AND p < 0.05 |
| 6 | H-E3 | Cross-method consistency (R vs E_s) | Spearman ρ > 0.7 |
| 7 | H-M2 | Independent t-test (ResNet vs ViT) | p < 0.05 AND gap ≥ 2 epochs |
| 8 | H-M1 | Layer-neuron consistency | Early layers show higher ρ_j |
| 9 | H-C1 | Paired t-test (Gradient-Aware vs JTT) | mean diff ≥ -1% AND p < 0.05 |

---

## Timeline Estimate

**Total Duration**: 11 weeks (sequential critical path)

**Week-by-Week Breakdown**:
- Weeks 1-2: H-E1 (CMNIST ablation training + Tests 1-4)
- Week 3: H-E2 (variance + forgetting analysis on CMNIST data)
- Weeks 4-5: H-E3 (GradCAM temporal ratio on Waterbirds/CelebA/NICO++)
- Week 6: H-M1 (layer-neuron consistency test)
- Weeks 7-8: H-M2 (ResNet vs ViT architectural comparison)
- Weeks 9-11: H-C1 (gradient-aware training implementation + Waterbirds eval)

**Parallel Optimization**: H-E2, H-E3, H-M2 can overlap after H-E1 → reduces wall-clock time to ~9 weeks

---

## Controlled Variables (from Phase 2A)

**Datasets**: CMNIST (color), Waterbirds (background), CelebA (gender), NICO++ (context)  
**Models**: ResNet-18 (CMNIST), ResNet-50 (others), ViT-B/16 (Waterbirds, CelebA)  
**Optimizer**: SGD with momentum 0.9  
**Learning Rate**: Dataset-specific (cosine annealing or step decay per standard)  
**Random Seeds**: 10 per experiment (statistical power)  
**Baselines**: ERM, JTT (Just Train Twice), Layer-wise Regularization

---

## Dialectical Synthesis (from Phase 2A Round Table)

**Thesis**: Temporal ordering (E_s < E_c) is a universal law of spurious learning  
**Antithesis**: May only apply to low-level visual features (color, texture), not semantic features  
**Synthesis**: Test across diverse spurious types:
- Low-level: CMNIST (color)
- Mid-level: Waterbirds (background texture)
- Attribute-based: CelebA (gender-attribute correlation)
- Semantic: NICO++ (object-context associations)

If temporal gap exists across all 4 → generalizable signature  
If gap only in CMNIST/Waterbirds → bounded to low-level spurious features

---

## Phase 5 Readiness

**DETERMINES_SUCCESS Gate** (Main Hypothesis Level):
- Phase 5 baseline comparison validates overall approach
- Success: Gradient-aware training outperforms or matches baseline method (JTT)
- Failure routing: PARTIAL → Phase 0 (new direction needed)

**Sub-Hypothesis Gate Summary**:
- 2 MUST_WORK gates (H-E1, H-M1) must pass to reach Phase 5
- 4 SHOULD_WORK gates (H-E2, H-E3, H-M2, H-C1) provide supporting evidence
- SHOULD_WORK failures do NOT block Phase 5 progression

---

## Next Steps (Phase 2C)

1. Start with **H-E1** (READY status, no prerequisites)
2. Generate experiment design document (`02c_experiment_design_h-e1.md`)
3. Proceed through Phase 3 (implementation planning) → Phase 4 (coding + validation)
4. Upon H-E1 validation: unlock H-E2, H-E3, H-M1, H-M2
5. Continue hypothesis loop until all sub-hypotheses processed
6. Advance to Phase 5 (baseline comparison) if all MUST_WORK gates pass

---

**Status**: Phase 2B Complete  
**Verification State**: Initialized with 6 sub-hypotheses  
**Archon Project**: Not created (MCP unavailable during Phase 2B execution)  
**Next Action**: Begin Phase 2C with h-e1
