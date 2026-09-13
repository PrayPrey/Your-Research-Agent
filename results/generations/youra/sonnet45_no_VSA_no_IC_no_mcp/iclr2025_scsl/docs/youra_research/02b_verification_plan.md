# Phase 2B: Verification Planning

**Generated**: 2026-08-24T22:45:00Z  
**Main Hypothesis ID**: H-TemporalArchSig-v1  
**Pipeline Project ID**: e434b9c6-e150-46c4-8cb5-1c8e857b014c  
**Execution Mode**: UNATTENDED

---

## Main Hypothesis

**Title**: Architectural Components as Temporal Filters in Spurious Correlation Learning

**Statement**: Under stochastic spurious correlations (Waterbirds 85% co-occurrence, CelebA 95% co-occurrence), if we compare neural network architectures with different normalization (Batch Normalization vs Layer Normalization) and attention mechanisms (ResNet-CBAM, Vision Transformer) during training, then we will observe DISTINCT worst-group accuracy gap trajectories when measured against training progress (average accuracy on x-axis), because normalization and attention mechanisms differ in how they resolve gradient ambiguity from stochastic spurious correlations.

**Causal Mechanism**:
1. BN amplifies early spurious learning via batch-level statistics
2. LN reduces early spurious amplification via instance-level normalization
3. Attention mechanisms enable mid-training correction via global feature aggregation

---

## Sub-Hypotheses Breakdown

### H-E1: Existence Hypothesis (MUST_WORK, Foundation)
**Type**: EXISTENCE  
**Statement**: BN-LN worst-group gap difference exists: ResNet-BN shows ≥5 percentage point higher worst-group accuracy gap than ResNet-LN when both reach 90% average accuracy on Waterbirds dataset.

**Gate**: MUST_WORK (foundation hypothesis, blocks Phase 5 if fails)  
**Prerequisites**: None (READY for immediate execution)  
**Archon Task ID**: c4f70e7d-cb8d-476c-9f74-91c168c072b0

**Test Method**:
- Train ResNet-BN and ResNet-LN on Waterbirds for 100 epochs
- Log worst-group gap and average accuracy every epoch
- For each of 10 seeds, identify epoch where each architecture reaches 90% average accuracy
- Record worst-group gap at that epoch
- Compute mean gap difference across 10 seeds
- Perform paired t-test (α=0.05, two-tailed)

**Success Criterion**:
- Mean gap difference (BN - LN) ≥ 5 percentage points AND
- p < 0.05 AND
- Effect size (Cohen's d) ≥ 0.8 (large effect)

**Falsification**:
- If p > 0.05 OR mean gap difference < 3pp OR effect size < 0.5 → BN amplification hypothesis rejected

---

### H-M1: BN Amplification Mechanism (SHOULD_WORK)
**Type**: MECHANISM  
**Statement**: BN amplifies early spurious learning: ResNet-BN's batch-level statistics make stochastic batch spurious correlations easier to learn than instance-level core features, causing higher early worst-group gap.

**Gate**: SHOULD_WORK (mechanism hypothesis, does NOT block Phase 5 if fails)  
**Prerequisites**: H-E1 (depends on existence being confirmed)  
**Archon Task ID**: 14806d36-2041-4164-96d5-cd778cbf5dbf

**Test Method**:
- Analyze gradient flow to spurious vs core features in ResNet-BN during early training (epochs 1-20)
- Compare with ResNet-LN gradient flow patterns
- Measure batch-level spurious correlation strength vs instance-level

**Success Criterion**:
- ResNet-BN shows measurably higher gradient magnitude to batch-level spurious features than ResNet-LN in epochs 1-20
- Quantitative difference ≥20% in gradient ratio (spurious/core)

**Falsification**:
- If gradient flow patterns are statistically indistinguishable (p>0.05) between BN and LN → mechanism hypothesis unsupported

---

### H-M2: Attention Correction Mechanism (SHOULD_WORK)
**Type**: MECHANISM  
**Statement**: Attention enables mid-training correction: ViT or ResNet-CBAM shows steeper worst-group gap reduction slope (≥0.3pp/epoch more negative) from epoch 20-50 than ResNet-BN on Waterbirds.

**Gate**: SHOULD_WORK (mechanism hypothesis, does NOT block Phase 5 if fails)  
**Prerequisites**: H-E1 (depends on existence being confirmed)  
**Archon Task ID**: 477802a1-5780-457f-9d7b-a6cf7081730f

**Test Method**:
- For each architecture and seed, compute linear regression slope of worst-group gap vs epoch for epochs 20-50
- Compute mean slope and 95% confidence interval across 10 seeds
- Compare ViT slope CI and ResNet-CBAM slope CI against ResNet-BN slope CI

**Success Criterion**:
- ViT or ResNet-CBAM slope CI does NOT overlap with ResNet-BN slope CI AND
- ViT/CBAM slope is more negative than ResNet-BN slope by ≥ 0.3 percentage points per epoch

**Falsification**:
- If slope CIs overlap OR difference < 0.2pp/epoch → attention correction hypothesis rejected
- Weaken claim to "ViT architecture corrects" if ViT succeeds but CBAM fails (global structure, not attention)

---

### H-C1: Signature Consistency Condition (SHOULD_WORK)
**Type**: CONDITION  
**Statement**: Signatures generalize across datasets: Architecture ranking by worst-group gap at 90% average accuracy is consistent from Waterbirds to CelebA, with Spearman rank correlation ρ > 0.8.

**Gate**: SHOULD_WORK (condition hypothesis, does NOT block Phase 5 if fails)  
**Prerequisites**: H-E1 (depends on existence being confirmed)  
**Archon Task ID**: 45641465-d6cc-4287-8c8f-5f45b1d55e63

**Test Method**:
- For each architecture, compute mean worst-group gap at 90% average accuracy across 10 seeds on Waterbirds
- Rank architectures 1-4 (lowest gap = rank 1 = best)
- Repeat on CelebA
- Compute Spearman rank correlation between Waterbirds ranking and CelebA ranking

**Success Criterion**:
- Spearman ρ > 0.8 (strong positive correlation)

**Falsification**:
- If ρ < 0.6 OR ranking reversal occurs → signature consistency rejected
- Interpretation: temporal signatures are dataset-specific, not purely architectural

---

## Dependency Graph (DAG)

```
H-E1 (EXISTENCE, MUST_WORK)
├─→ H-M1 (MECHANISM, SHOULD_WORK)
├─→ H-M2 (MECHANISM, SHOULD_WORK)
└─→ H-C1 (CONDITION, SHOULD_WORK)
```

**Execution Order**:
1. **Phase 2C→3→4**: H-E1 (foundation, READY immediately)
2. **Phase 2C→3→4**: H-M1, H-M2, H-C1 in parallel (after H-E1 completes)

---

## Risk Assessment

| Hypothesis | Risk Level | Primary Risk | Mitigation |
|------------|-----------|--------------|------------|
| H-E1 | Medium | Statistical power, training-speed confound | 10 seeds (2pp detectable effect), accuracy-matched comparison |
| H-M1 | Low | Gradient measurement noise | 5-epoch smoothing, validation set measurement |
| H-M2 | Medium | Attention effect confounded (ViT multi-difference) | ResNet-CBAM ablation, weakened claim if CBAM fails |
| H-C1 | Medium | Dataset-specific signatures (ρ<0.6) | Test on third dataset (CMNIST), accept scope limitation if fails |

---

## Timeline Estimate

### Sequential Phase (H-E1 foundation):
- Phase 2C (Experiment Design): 2-3 days
- Phase 3 (Implementation Planning): 3-4 days
- Phase 4 (PoC Validation): 5-7 days
- **Subtotal**: ~2 weeks

### Parallel Phase (H-M1, H-M2, H-C1):
- Phase 2C (Experiment Design): 2-3 days
- Phase 3 (Implementation Planning): 3-4 days
- Phase 4 (PoC Validation): 5-7 days
- **Subtotal**: ~2 weeks (parallel execution)

**Total Phase 2B→4 Duration**: ~4 weeks

**Phase 5 (Baseline Comparison)**: 1 week (after all sub-hypotheses complete)

---

## Controlled Variables (All Experiments)

From Phase 2A refinement, these variables are controlled across all sub-hypotheses:

- **Learning Rate**: Constant LR=0.01 (no schedule) to isolate architectural effects
- **Batch Size**: Fixed at 64
- **Initialization**: He initialization for all architectures
- **Random Seeds**: 10 seeds (0-9) for statistical power
- **Datasets**: Waterbirds (primary), CelebA (generalization), CMNIST (boundary test)
- **Architectures**: ResNet-18 (BN/LN/CBAM variants), ViT-Small/DeiT
- **Training Duration**: 100 epochs per experiment

---

## Dialectical Analysis

**Thesis**: Architectural components (normalization type, attention mechanisms) create distinct temporal worst-group gap signatures.

**Antithesis**: Optimization hyperparameters (learning rate, batch size, optimizer choice) dominate temporal learning dynamics, not architectural components.

**Synthesis**: Test via accuracy-matched comparison (eliminates LR schedule confound) with 10-seed statistical power (detects 2pp effects). Null result → optimization-dominance finding (publishable).

**Core Tension**: Attention effect partially confounded (ViT differs from ResNet in receptive field, parameter count, optimization dynamics, not just attention).

**Resolution**: ResNet-CBAM ablation isolates channel attention while preserving local receptive field. If CBAM shows correction → attention contributes. If not → ViT correction due to global architecture, weaken claim accordingly.

---

## Phase 5 Readiness

**DETERMINES_SUCCESS Gate**: After all sub-hypotheses complete Phase 4 PoC validation:
- If ≥1 MUST_WORK hypothesis fails → ROUTE to Phase 0 (fundamental flaw)
- If all MUST_WORK hypotheses pass → Proceed to Phase 5 baseline comparison
- SHOULD_WORK hypotheses inform mechanistic understanding but do NOT block Phase 5

**Baseline Comparison Strategy**:
- Our method: Accuracy-matched temporal gap measurement with architectural ablation
- Baseline: Standard worst-group accuracy at convergence (Sagawa et al. 2020 Group DRO)
- Success: Our temporal signatures enable architecture selection that outperforms baseline worst-group accuracy by ≥5pp

---

## Open Questions for Phase 2C→4

1. Will CMNIST (deterministic spurious correlation) show architectural signatures or confirm stochastic-only scope?
2. Will ResNet-CBAM isolate attention effect or confirm ViT correction is due to global architecture?
3. Will signature ranking transfer from Waterbirds to CelebA (Spearman ρ>0.8) or reveal dataset-dependence?

---

## Next Steps

**Immediate**: Begin Phase 2C experiment design for H-E1 (foundation hypothesis, READY status).

**After H-E1 validation**: Launch Phase 2C for H-M1, H-M2, H-C1 in parallel.

**Workflow**: Phase 2C → Phase 3 → Phase 4 for each hypothesis, then Phase 5 for main hypothesis.
