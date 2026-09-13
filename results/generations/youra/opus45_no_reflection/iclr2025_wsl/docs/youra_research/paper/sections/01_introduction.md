# Introduction

Model accuracy is not the whole story. When analyzing the Small CNN Zoo—a collection of 193 convolutional neural networks trained on CIFAR-10 with varying hyperparameters and random seeds—we find that 67.6% of class-wise accuracy variance remains unexplained by overall model accuracy. This finding exceeds our detection threshold by a factor of 13.5, establishing that trained models develop distinct *behavioral fingerprints*: class-specific performance patterns that cannot be reduced to a single accuracy number.

This observation has practical implications. Model selection typically relies on aggregate metrics, yet two models with identical 85% accuracy may fail on entirely different classes. Understanding these behavioral differences from weights alone—without requiring inference—could enable efficient model auditing, ensemble construction, and failure mode prediction. The question is whether this behavioral structure can be extracted from the weight matrices themselves.

## The Gap in Weight-Space Learning

Recent advances in weight-space learning have achieved remarkable success at scalar property prediction. SANE achieves R² > 0.9 for predicting overall accuracy from weight representations on small CNNs. Unterthiner et al. demonstrate that simple weight statistics (means, standard deviations, spectral norms) can predict accuracy with R² approaching 0.97. Neural Functionals provide permutation-equivariant architectures for processing weights while respecting hidden neuron symmetries.

However, these methods predict *scalar* properties. The structured prediction problem—forecasting a 10-dimensional class-wise accuracy vector rather than a single number—remains unexplored. More fundamentally, the question of whether behavioral information (beyond accuracy) is encoded in weights at all has not been systematically tested.

## Our Contribution

We address two foundational questions:

1. **Existence:** Does meaningful behavioral variance exist in model zoos beyond what overall accuracy explains?
2. **Mechanism:** Can simple weight-space features extract this behavioral signal?

For existence (H-E1), we decompose class-wise accuracy variance into components explained by overall accuracy, per-class baseline difficulty, and residual behavioral variance. We find a residual ratio of 0.68—67.6% of variance is *not* explained by the stratified baseline—establishing that behavioral fingerprints exist in model zoos.

For mechanism (H-M1), we test whether per-layer weight statistics (mean, standard deviation, minimum, maximum, L2 norm across 5 convolutional and fully-connected layers = 25 features) can predict class-wise accuracy profiles. Using Ridge regression with 80/20 train/test splits, we find that weight features achieve R² = -0.08 compared to the stratified baseline's R² = 0.12. The mechanism test *fails*: simple weight statistics do not capture behavioral variance better than knowing overall accuracy alone.

This negative result is informative. It establishes that while behavioral fingerprints exist, extracting them from weights is non-trivial. The failure motivates future work on learned representations (NF-Layers, SANE embeddings) and larger sample sizes—our 193-model subset is 150× smaller than the full zoo's ~30,000 models.

## Paper Organization

Section 2 reviews related work on weight-space learning and property prediction. Section 3 describes our methodology: variance decomposition for existence testing and weight probes for mechanism testing. Section 4 details experimental setup including the Small CNN Zoo dataset and evaluation protocol. Section 5 presents results demonstrating existence validation and mechanism failure. Section 6 discusses implications, limitations, and the path forward for behavioral fingerprinting from weights.
