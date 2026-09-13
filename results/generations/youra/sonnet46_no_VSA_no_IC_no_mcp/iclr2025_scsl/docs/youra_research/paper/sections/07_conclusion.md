# 7. Conclusion

We began with a widely held assumption: that contrastive self-supervised learning amplifies spurious correlations because its augmentation-invariance objective makes background texture strongly instance-discriminative. Our experiments on Waterbirds and CelebA demonstrate the opposite.

Supervised ERM encodes spurious background features significantly more strongly than contrastive MoCo-v3 on Waterbirds (ratio diff = 0.025, Cohen's d = 5.68, p < 0.0001), while ERM ≈ DINO (p = 1.0). The pretraining paradigm effect is highly significant across both datasets (Waterbirds ANOVA F = 35.99, p = 2.42 × 10⁻⁷; CelebA F = 5.51, p = 0.009). The paradigm ranking reverses across datasets, establishing that spurious attribute type interacts with pretraining objective in ways not captured by existing theory.

**Summary of contributions:**

1. **First controlled 4-paradigm comparison** of spurious attribute probe accuracy on frozen ResNet-50 features across two group-annotated benchmarks, demonstrating a highly significant paradigm effect.

2. **Directional finding:** Supervised ERM encodes spurious Waterbirds background features more strongly than contrastive MoCo-v3 (d = 5.68) — refuting the augmentation-invariance amplification hypothesis and implicating supervised label correlation as the primary driver.

3. **Dataset interaction:** MoCo-v3 and DINO exchange rankings between Waterbirds and CelebA, establishing that spurious attribute type × pretraining objective interaction is a necessary design consideration — not captured by any single-dataset paradigm comparison.

4. **Mechanistic lever:** Background-replacement augmentation in contrastive SSL is verified as a functional causal intervention for spurious encoding modulation (mechanism active at 19× detection threshold).

**Future directions.** Our results open three grounded future investigations. First, testing a masked autoencoder (MAE) — label-free and non-contrastive — would directly distinguish whether label-agnostic training or augmentation-based suppression drives the MoCo-v3 vs ERM difference. Second, measuring downstream worst-group accuracy via DFR-style last-layer retraining on MoCo-v3 vs ERM features would test whether lower spurious encoding translates to practical robustness gains. Third, extending the comparison to ViT backbones and additional spurious attribute types (spatial, color, object-level) would map the paradigm × attribute-type interaction matrix needed for principled backbone selection.

The pretraining objective is a design choice that practitioners make before any robustness intervention. Our findings suggest this choice already determines the spurious content of the resulting representations — and that label-agnostic pretraining provides partial spurious feature suppression as a free byproduct of not seeing class labels.
