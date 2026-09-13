# Discussion

## What the Results Mean

We establish that **behavioral fingerprints exist** in CNN model zoos: 67.6% of class-wise accuracy variance is unexplained by overall accuracy alone. This quantifies an intuition that model behavior is richer than a single accuracy number. Models with 85% accuracy can fail on entirely different classes—and this variation is substantial.

However, **extracting this signal from weights is non-trivial**. Simple per-layer statistics (mean, std, min, max, norm) do not capture behavioral variance better than a stratified baseline. The behavioral information may be encoded in higher-order weight interactions, cross-layer dependencies, or distributional properties that scalar statistics miss.

## Why the Mechanism Failed

Several factors likely contribute to H-M1's failure:

**Sample Size.** Our 193-model subset is 150× smaller than the full zoo (~30,000 models). With 25 features and 154 training examples, Ridge regression has limited statistical power. The Class 4 anomaly (R² = -2.74) may reflect overfitting to spurious patterns.

**Feature Expressivity.** Five scalar statistics per layer may be too coarse. Behavioral information could reside in:
- Weight distributions (histograms, higher moments)
- Singular value spectra
- Cross-layer correlations
- Non-linear feature combinations

**Undertrained Models.** Mean overall accuracy in our subset is 18.7%—near random for 10-class classification. Many models may not have converged, adding noise to behavioral patterns. The existence signal (H-E1) survives this noise; the extraction signal (H-M1) may not.

## Implications for Weight-Space Learning

Our results suggest a **gap between existence and extraction** of behavioral information:

1. **Behavioral structure is real.** Model zoos contain meaningful per-class variation beyond accuracy. This motivates behavioral prediction as a target for weight-space methods.

2. **Simple statistics are insufficient.** Prior success (R² > 0.9) on scalar accuracy does not extend to structured behavioral prediction with simple features.

3. **Learned representations warranted.** NF-Layers, SANE embeddings, or behavioral autoencoders may capture the cross-layer and distributional information that scalar statistics miss.

## Limitations

**Sample Size.** 193 models provide pilot-study evidence. Full validation requires the complete zoo (~30,000 models).

**Feature Choice.** We tested one feature set (25 statistics). More expressive alternatives (histograms, spectra, learned embeddings) remain untested.

**Architecture Scope.** Results apply to the Small CNN Zoo's 3-conv+2-FC architecture. Generalization to ResNets, Transformers, or larger models is not established.

**Training Convergence.** Low mean accuracy (18.7%) suggests undertrained models. Results may differ on converged-only subsets.

## Future Directions

1. **Scale to full zoo.** Test H-M1 with n ≈ 30,000 to isolate sample-size effects.

2. **Expressive features.** Weight histograms, singular values, or gradient statistics may capture behavioral structure.

3. **Learned representations.** Train NF-Layer or SANE encoders on class-wise accuracy targets to test whether learned embeddings succeed where statistics fail.

4. **Non-linear probes.** Gradient boosting or neural networks may capture feature interactions Ridge regression misses.

5. **Cross-metric transfer.** Test whether behavioral embeddings trained on class-wise accuracy transfer to confusion matrix similarity or sample-level agreement.
