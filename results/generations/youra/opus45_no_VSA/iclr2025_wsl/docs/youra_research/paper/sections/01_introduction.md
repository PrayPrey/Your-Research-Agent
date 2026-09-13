# Introduction

We set out to prove that stable spectral properties indicate model quality — and proved the exact opposite. The coefficient of variation of participation ratio (CV\_PR), a measure of randomized SVD estimator variance, was hypothesized to correlate negatively with ImageNet accuracy: models with flat spectra should produce consistent singular value estimates across random projections, and this stability should signal better generalization. Instead, experiments on 94 pretrained models from the timm library revealed a strong *positive* correlation (r = +0.61, p < 10^{-10}). Higher variance accompanied better models, not worse.

This finding matters because spectral analysis of neural network weights has become a cornerstone of model quality assessment. Martin and Mahoney [Martin & Mahoney, 2019] established that heavy-tailed eigenvalue distributions reflect training quality; Unterthiner et al. [Unterthiner et al., 2020] showed weight statistics predict accuracy with R² > 0.98. Yet the directional relationship between spectral *variance* and generalization remained untested. Practitioners selecting from model zoos—timm alone hosts over 1,000 architectures—rely on implicit assumptions about what spectral properties mean. If those assumptions are inverted, model selection criteria may systematically favor inferior models.

The deeper problem is conceptual. Prior work computed spectral features directly (effective rank, participation ratio, power-law exponents) but did not examine the variance of these estimates under randomized computation. Randomized SVD introduces stochasticity: projecting a weight matrix onto random subspaces yields different singular value approximations across seeds. We reasoned that this variance reflects spectral shape—flat spectra should produce stable estimates, peaked spectra should not. The gap in existing work is simple: no one had systematically tested whether this computational variance predicts model quality, or in which direction.

Our key insight, validated through falsification, is that CV\_PR positively correlates with accuracy. The intuition that "stability signals quality" is wrong, at least for this metric. We offer two competing explanations: (1) model size confounds both accuracy and spectral diversity—larger models have more parameters, higher accuracy, and potentially more varied spectral structure; (2) higher CV reflects richer, more diverse feature representations, not instability. Distinguishing these requires partial correlation analysis controlling for parameter count, which we leave for future work.

Building on this falsification, we make three contributions:

1. **Methodology validation**: We demonstrate that CV\_PR can be reliably extracted from 100+ pretrained models using randomized SVD with 20 seeds (100% completion rate, finite values in [0.001, 0.033]).

2. **Hypothesis falsification**: We show that CV\_PR correlates positively with ImageNet accuracy (r = +0.61, 95% CI [0.506, 0.703]), directly contradicting the negative correlation hypothesis.

3. **Interpretive framework**: We provide alternative explanations (confounding, inverted mechanism) that guide future hypothesis reformulation.

The remainder of this paper is organized as follows. Section 2 reviews related work on spectral analysis and model quality prediction. Section 3 describes our methodology for CV\_PR extraction. Section 4 presents experimental setup. Section 5 reports results, and Section 6 discusses implications, limitations, and future directions.
