# Research Context: h-m2

**Hypothesis ID**: h-m2  
**Main Hypothesis**: H-TemporalArchSig-v1  
**Phase**: 2C (Experiment Design) COMPLETED  
**Generated**: 2026-08-25

---

## Hypothesis Lineage

### Main Hypothesis (Phase 2A)
**Title**: Architectural Components as Temporal Filters in Spurious Correlation Learning

**Core Claim**: Neural network architectures with different normalization (BN vs LN) and attention mechanisms (ResNet-CBAM, ViT) produce DISTINCT worst-group accuracy gap trajectories when plotted against training progress (average accuracy on x-axis) under stochastic spurious correlations.

**Causal Mechanism**:
1. BN amplifies early spurious learning via batch-level statistics
2. LN reduces early spurious amplification via instance-level normalization
3. Attention mechanisms enable mid-training correction via global feature aggregation

---

### Sub-Hypothesis Breakdown (Phase 2B)

**h-e1** (EXISTENCE, MUST_WORK):
- Tests whether BN-LN gap difference exists (≥5pp at 90% accuracy)
- Foundation hypothesis — blocks Phase 5 if fails
- **Status**: VALIDATED (gap difference 9.41pp, p=5.43e-05, Cohen's d=3.94)

**h-m2** (MECHANISM, SHOULD_WORK) — THIS HYPOTHESIS:
- Tests whether attention enables mid-training correction (slope difference ≥0.3pp/epoch)
- Mechanism hypothesis — does NOT block Phase 5 if fails
- **Status**: Experiment design COMPLETED, ready for Phase 3
- **Prerequisite**: h-e1 validated ✓

**h-m1** (MECHANISM, SHOULD_WORK):
- Tests BN amplification mechanism via gradient flow analysis
- Depends on h-e1 (sibling to h-m2)

**h-c1** (CONDITION, SHOULD_WORK):
- Tests signature generalization across datasets (Waterbirds → CelebA)
- Depends on h-e1 (sibling to h-m2)

---

## Research Trajectory

### Phase 0 (Brainstorming)
Main hypothesis conceived: architectural components create temporal signatures in spurious correlation learning.

### Phase 1 (Targeted Research)
Literature review confirmed:
- BN-LN normalization effects documented
- Attention mechanisms improve robustness
- Gap: no temporal trajectory analysis with accuracy-matched comparison

### Phase 2A (Hypothesis Dialogue)
Refined hypothesis via dialectical process:
- Controlled for learning rate schedule confound (use constant LR)
- Identified statistical power requirements (10 seeds for 2pp detection)
- Defined accuracy-matched comparison to eliminate training speed artifact

### Phase 2B (Verification Planning)
Decomposed main hypothesis into 4 sub-hypotheses:
- h-e1 as foundation (MUST_WORK)
- h-m1, h-m2, h-c1 as mechanisms/conditions (SHOULD_WORK)
- Created dependency DAG: h-e1 → {h-m1, h-m2, h-c1}

### Phase 2C (Experiment Design) — CURRENT
**h-e1**: Designed and validated (9.41pp gap difference confirmed)  
**h-m2**: Designed (this document) — slope-based trajectory analysis for attention correction

---

## Controlled Variables (All Experiments)

From Phase 2B, these variables are controlled across ALL sub-hypotheses:

- **Learning Rate**: Constant LR=0.01 (no schedule)
- **Batch Size**: Fixed at 64
- **Initialization**: He initialization for conv layers, architecture-specific for others
- **Random Seeds**: 10 seeds (0-9) for statistical power
- **Dataset**: Waterbirds (primary for all hypotheses)
- **Training Duration**: 100 epochs per experiment
- **Loss Function**: CrossEntropyLoss (no class reweighting)
- **Optimizer**: SGD with momentum=0.9, weight_decay=1e-4
- **Data Augmentation**: None (isolate architectural effects)

---

## Design Decisions for h-m2

### Why Slope Comparison (epochs 20-50)?
- **Early phase (1-20)**: Dominated by initialization effects, all architectures memorize spurious features
- **Mid-training (20-50)**: Correction phase where attention may re-weight features
- **Late phase (70-100)**: Convergence plateau, small gradient signal
- **Statistical power**: 31-epoch window provides sufficient data points for robust linear regression

### Why ResNet-CBAM as Ablation?
- Isolates attention effect by preserving ResNet's local receptive field
- CBAM adds channel + spatial attention without changing architecture globally
- If CBAM succeeds but ViT fails → attention alone insufficient
- If ViT succeeds but CBAM fails → global architecture drives correction, not attention

### Why ViT-Small (not ViT-Base)?
- Parameter count closer to ResNet-18 (reduces parameter confound)
- Faster training (3× fewer parameters than ViT-Base)
- Sufficient depth (12 layers) for attention correction hypothesis test

### Why Bootstrap CI (not analytical CI)?
- Robust to non-normal slope distributions
- No assumptions about residual variance homogeneity
- 1000 resamples provides stable CI estimate

---

## h-m2 Specific Risks and Contingencies

### Risk 1: ViT Training Instability
**Symptom**: ViT loss diverges or fails to converge  
**Contingency**:
1. Add gradient clipping (max_norm=1.0)
2. Reduce LR to 0.001 for ViT (keep ResNet at 0.01)
3. If still unstable: use ViT with LayerScale or reduce depth to 6 layers

### Risk 2: CBAM Implementation Bug
**Symptom**: ResNet-CBAM accuracy significantly worse than ResNet-BN  
**Contingency**:
1. Validate CBAM module on CIFAR-10 (should improve accuracy over baseline)
2. Compare with reference implementation (timm or official CBAM repo)
3. Test CBAM output shapes and gradient flow

### Risk 3: Epoch 20-50 Misses Correction Phase
**Symptom**: Slopes show no difference, but trajectories diverge in other epochs  
**Contingency**:
1. Plot full 100-epoch trajectories (visual inspection)
2. Test alternative windows: epochs 30-60, 40-70, 50-80
3. Compute piecewise slopes: epochs 1-25, 25-50, 50-75, 75-100
4. Document if correction occurs outside pre-specified window

### Risk 4: High Variance Across Seeds
**Symptom**: Wide CIs, overlapping between architectures  
**Contingency**:
1. 10 seeds provides 80% power for 0.3pp/epoch effect (pre-computed)
2. Accept wider uncertainty if variance is intrinsic
3. Add 5 more seeds (seeds 10-14) if variance is unexpectedly high
4. Report effect size (Cohen's d) even if CIs overlap

---

## Connection to Phase 5 (Baseline Comparison)

**If h-m2 succeeds (SHOULD_WORK gate satisfied)**:
- Attention-augmented architectures (CBAM/ViT) prioritized for Phase 5
- Baseline comparison: Our temporal signature method vs Group DRO (Sagawa et al. 2020)
- Success: Architecture selection via signatures outperforms baseline worst-group accuracy by ≥5pp

**If h-m2 fails (SHOULD_WORK gate NOT satisfied)**:
- Does NOT block Phase 5 (SHOULD_WORK hypothesis)
- Null result documented: "Attention does not enable mid-training correction under constant LR"
- Alternative mechanisms explored (e.g., h-m1 BN amplification may still hold)
- Phase 5 proceeds with h-e1 findings (BN-LN difference confirmed)

---

## Next Steps

**Immediate**: Begin Phase 3 (Implementation Planning) for h-m2  
**After Phase 3**: Execute Phase 4 (PoC Validation) — implement and run experiment  
**After Phase 4**: Integrate h-m2 results with h-e1, h-m1, h-c1 for Phase 5 synthesis

**Parallel Work**: h-m1 and h-c1 can execute Phase 2C→3→4 concurrently with h-m2

---

**Document Status**: COMPLETED  
**Last Updated**: 2026-08-25  
**Ready for Phase 3**: YES
