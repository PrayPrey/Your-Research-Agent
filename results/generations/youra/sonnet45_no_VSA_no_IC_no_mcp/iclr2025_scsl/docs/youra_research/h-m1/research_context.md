# Research Context: h-m1

**Generated**: 2026-08-24  
**Hypothesis ID**: h-m1  
**Phase**: 2C (Experiment Design)

---

## Main Hypothesis Connection

**Main Hypothesis**: Architectural Components as Temporal Filters in Spurious Correlation Learning

**Sub-hypothesis Role**: h-m1 explains the MECHANISM behind h-e1's existence finding (BN-LN worst-group gap difference).

**Position in DAG**:
```
H-E1 (EXISTENCE, MUST_WORK) [VALIDATED]
└─→ H-M1 (MECHANISM, SHOULD_WORK) [IN_PROGRESS]
```

---

## Related Work

### Batch Normalization Literature

**Ioffe & Szegedy 2015** - Batch Normalization: Accelerating Deep Network Training by Reducing Internal Covariate Shift
- Introduced BN as convergence accelerator
- Batch-level statistics (mean/variance over batch dimension)
- No analysis of spurious correlation effects

**Santurkar et al. 2018** - How Does Batch Normalization Help Optimization?
- BN smooths loss landscape (not just covariate shift)
- Makes gradients more predictable
- Did not analyze group-level disparities

**Shen et al. 2021** - Connect the Dots: Detecting Adversarial Perturbations Using Context Inconsistency
- Observed BN hurts worst-group accuracy vs LN
- No mechanistic explanation (empirical observation only)

### Spurious Correlation Literature

**Sagawa et al. 2020** - Distributionally Robust Neural Networks (Group DRO)
- Defined worst-group accuracy gap metric
- Showed ERM fails on minority groups
- Did not analyze architectural components (BN/LN/attention)

**Nagarajan et al. 2021** - Understanding the Failure Modes of Out-of-Distribution Generalization
- Spurious features learned earlier than core features (simplicity bias)
- Did not analyze normalization layer role

**Kirichenko et al. 2022** - Last Layer Retraining for Robustness
- Fine-tuning last layer improves worst-group accuracy
- Suggests early layers learn spurious features (consistent with h-m1)

---

## Novel Contribution

**h-m1 advances beyond prior work**:
1. First gradient-level analysis of BN's role in spurious correlation learning
2. Mechanistic explanation for observed BN-LN gap (h-e1)
3. Tests batch-level vs instance-level statistics hypothesis directly
4. Measures spurious vs core gradient flow in early training

**Hypothesis**: BN amplifies batch-level spurious correlations → higher early worst-group gap

**Prior work gap**: Previous studies observed BN-LN difference empirically but did not explain WHY.

---

## Open Questions

1. **Gradient measurement validity**: Does majority/minority group gradient ratio actually proxy spurious/core features?
   - Assumption: Majority group gradients driven by spurious correlations
   - Assumption: Minority group gradients driven by core features
   - Validation: Check if gradient ratio correlates with worst-group gap

2. **Batch composition effects**: Does BN amplification depend on per-batch spurious correlation strength?
   - Test: Correlate batch spurious correlation with batch loss
   - Prediction: BN shows stronger correlation than LN

3. **Normalization design space**: Can we design a normalization layer that suppresses batch-level spurious correlations?
   - Candidates: Hybrid BN-LN, batch-conditional normalization, group normalization
   - Future work: Design and test spurious-robust normalization

---

## Phase 2A Refinement Notes

From Phase 2A dialogue, key refinements for h-m1:
- Use accuracy-matched comparison (measure gradients at matched training progress, not matched epochs)
- Control for learning rate (constant LR=0.01, no schedule)
- 10 seeds for statistical power (detect 20% gradient ratio difference)
- Early training focus (epochs 1-20, when spurious learning dominates)

---

## Connection to Future Hypotheses

**h-m2** (Attention correction mechanism):
- If h-m1 confirms BN amplifies early spurious learning, does attention enable mid-training correction?
- Complementary mechanisms: BN amplifies early, attention corrects later

**h-c1** (Signature consistency):
- If h-m1 mechanism is batch-level statistics (not dataset-specific), gradient ratio should generalize across datasets
- Test: Measure BN-LN gradient ratio on CelebA, compare with Waterbirds

---

## Experimental Design Lineage

**h-e1 (prerequisite)**:
- Established BN-LN gap exists (9.41pp, p < 0.001)
- Used Waterbirds dataset, ResNet-18-BN vs ResNet-18-LN
- Measured worst-group gap at 90% average accuracy

**h-m1 (this experiment)**:
- Reuses h-e1 dataset, models, training configuration
- Adds gradient measurement via backward hooks
- Measures gradient ratio (spurious/core) in epochs 1-20
- Tests mechanism hypothesis: BN amplifies batch-level spurious correlations

**Efficiency gain**: Code reuse from h-e1 (dataset, models, training loop) reduces implementation time by ~50%.
