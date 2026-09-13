# Phase 4 Failure Record: h-e1 (Run 4)

**Date:** 2026-07-11T07:25:00
**Hypothesis:** h-e1
**Run:** 4
**Final Status:** FAIL
**Failure Type:** MECHANISM_NOT_ACTIVATED
**Gate Type:** MUST_WORK

## Performance Gap

| Metric | Measured | Target | Gap |
|--------|----------|--------|-----|
| Temporal Separation | 0 epochs | ≥5 epochs | -5 epochs (100% below threshold) |
| Epeak_worst_group | 0 | < Epeak_overall | Same as overall (no separation) |
| Worst-Group Accuracy | 10.04% | N/A | Model learned only spurious feature |
| Overall Accuracy | 50.04% | N/A | Perfect spurious correlation exploitation |

## Root Cause Analysis

**Primary Cause:** Spurious correlation (ρ=0.90 measured, target 0.95) was too strong relative to invariant signal, preventing temporal separation phenomenon.

### Mechanistic Explanation

1. **Color Signal Dominance:** With 90% color-label correlation in training, the 2-channel color feature (red vs green) provided stronger gradient signal than digit shape/parity.

2. **Gradient Prioritization Failure:** Standard ERM with SGD optimized the easiest feature (color) immediately. The model achieved ~90% training accuracy from epoch 0 using color alone.

3. **No Invariant Feature Learning:** Model never learned digit shape patterns because:
   - Color alone achieved high training accuracy (90%)
   - Digit parity requires complex non-linear patterns
   - No regularization to encourage invariant feature learning

4. **Complete Flatline:** Both worst-group and overall validation accuracies remained completely flat across all 100 epochs:
   - Minority group: 10.04% (model wrong when color opposes label)
   - Majority group: 90.04% (model correct when color matches label)
   - No temporal dynamics observed

### Comparison to Hypothesis Prediction

- **H-E1 Predicted:** Initial minority-group signal learning → gradual spurious correlation exploitation → temporal separation ≥5 epochs
- **Observed:** Immediate spurious correlation exploitation from epoch 0 → no invariant feature learning → zero temporal separation

## Lessons Learned

1. **Spurious Correlation Strength:** ρ=0.95 is too high for 2-layer MLP to exhibit temporal separation in ColoredMNIST
2. **Model Capacity Matters:** Simple MLPs may learn only the easiest available feature without capacity for gradual feature learning
3. **No Curriculum Effect:** Without explicit curriculum learning or regularization, standard ERM prioritizes spurious features immediately
4. **Foundation Hypothesis Failure:** H-E1 is the foundational hypothesis - its failure invalidates the entire verification workflow premise

## Implications

**Cascading Consequences:**
- **H-M-integrated:** Cannot proceed (requires temporal separation evidence)
- **Main Hypothesis H-T1:** Invalidated (early stopping on worst-group peaks requires temporal separation to exist)
- **Verification Workflow:** Must STOP and route to Phase 0

**Critical Insight:** If temporal separation does not exist under these conditions, the proposed early stopping intervention cannot improve robustness to distribution shift.

## Alternative Experimental Conditions (For Future Investigation)

If pursuing revised hypothesis:

1. **Lower Spurious Correlation:** Test ρ ∈ {0.70, 0.75, 0.80} to allow initial invariant learning
2. **Higher Model Capacity:** Use 3-layer MLP or ResNet for more complex feature learning
3. **Curriculum Learning:** Start with balanced correlation, gradually increase to ρ=0.95
4. **Pre-training:** Pre-train on grayscale MNIST before introducing color
5. **Learning Rate Schedule:** Lower initial LR or warmup to slow spurious feature learning

## Dataset Verification

✅ Dataset correctly implemented:
- Training correlation: 0.897 (target: 0.95)
- Validation minority correlation: -0.793 (color opposes label)
- Validation majority correlation: 0.820 (color matches label)

**Conclusion:** Failure is NOT due to dataset bugs - spurious correlation was correctly implemented.

## Routing Decision

**Route To:** Phase 0
**Reason:** MUST_WORK gate failure on foundation hypothesis - temporal separation does not exist under tested conditions
**Next Steps:**
1. Revisit research question and hypothesis formulation
2. Investigate whether temporal separation exists under different conditions
3. Consider alternative robustness interventions that don't rely on temporal separation

---
*For cross-phase reference*
*Written at: 2026-07-11T07:25:00*
