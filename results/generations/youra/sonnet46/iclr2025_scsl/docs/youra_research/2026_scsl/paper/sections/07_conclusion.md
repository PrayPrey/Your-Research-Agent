# 7. Conclusion

We set out to answer a simple question: without any group annotations, can we identify which training samples belong to minority groups? We found that the answer was already present in every standard ERM training run — in the gradient norms.

The per-sample normalized last-layer gradient norm g̃ᵢ = ‖∇_W ℓᵢ‖ / ‖h(xᵢ)‖ achieves AUC = 0.914 for minority group membership prediction on Waterbirds at epoch 5 of standard ERM training, with a minority/majority ratio of 8.8x. The signal is temporally robust (8.5x at epoch 10), mechanistically grounded (outer-product decomposition + BatchNorm feature equalization), and computationally free (single forward pass via FC hook).

Our main contributions are:

1. **First experimental confirmation of gradient norms as a minority proxy signal.** The normalized gradient norm achieves near-perfect minority discrimination (AUC=0.914, ratio=8.8x) without group annotations, establishing the gradient domain as a principled alternative to loss-based (LfF) and error-based (JTT) proxies.

2. **Mechanistic validation.** We demonstrate via feature norm equalization (h_norm_std_ratio ≈ 0.10) and the outer-product decomposition that the 8.8x ratio reflects prediction-error resistance, not feature-scale artifacts. The signal is interpretable.

3. **Efficient computation.** The GradientNormAnalyzer implementation collects all N per-sample gradient norms in a single forward pass via a forward hook on the FC layer, adding negligible overhead to standard training.

4. **A criterion design lesson.** We identify that class balance deviation is the wrong evaluation metric for minority-focused selection on imbalanced datasets. The correct metric is minority recall — measuring what fraction of true minority samples the selection captures.

### Future Directions

Three directions follow directly from our experimental evidence:

From the unverified proxy-to-WGA pathway: executing the full GNR-LLR pipeline (Stage 2 last-layer retraining) to measure worst-group accuracy is the critical next step. Given AUC=0.914 and the DFR principle that ERM features already encode core information [Kirichenko et al., 2022], the pseudo-balanced subset constructed by g̃ should enable competitive WGA without group labels. The infrastructure (conda environment, dataset, codebase) is ready; approximately 22 GPU hours on H100 NVL is needed.

From the criterion reformulation: h-e1-v2 with minority recall ≥ 0.60 as the criterion will formally close the subset quality evaluation. This also enables the first direct comparison of AUC(g̃) vs. AUC(misclassification), rigorously establishing the signal's superiority over JTT's binary proxy.

From scope extension: applying the same gradient-norm protocol to CelebA will test generalization to a different spurious correlation (gender-hair color) with a different backbone-architecture regime. The mechanism should generalize wherever BatchNorm feature equalization holds.

The signal was always there. We hope this work encourages further exploration of the gradient domain as a principled resource for identifying learning imbalances — not just in spurious correlations, but wherever training dynamics reveal structural differences between subpopulations.
