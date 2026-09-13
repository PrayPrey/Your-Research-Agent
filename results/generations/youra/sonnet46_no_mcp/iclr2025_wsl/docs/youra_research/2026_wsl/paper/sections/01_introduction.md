# 1. Introduction

When a flat MLP encoder is trained to predict neural network accuracy from weights,
it faces a problem that grows factorially with network depth: every permutation of neurons
within a hidden layer produces a weight vector that is functionally identical yet appears
as a completely distinct input. A network with two hidden layers of width 32 already has
over $10^{83}$ permutation-equivalent weight configurations — more than atoms in the
observable universe. At 500K encoder parameters, we show empirically that flat MLPs
cannot learn their way out of this problem: they assign distinguishably different embeddings
to functionally-equivalent weight pairs (permutation sensitivity score = 0.649), and their
prediction quality collapses accordingly (Spearman $\rho = 0.17$). A permutation-equivariant
Neural Functional Network (NFN) encoder at the same capacity maps all equivalent configurations
to the same embedding — with a sensitivity score 885,000$\times$ lower — and achieves
$\rho = 0.68$, a gap of $\Delta\rho = 0.51$.

This gap matters because **model zoo analysis** — predicting properties of trained neural networks
from their weights — is increasingly central to neural architecture search, model selection,
and transfer learning [Schurholt et al., 2022; Unterthiner et al., 2020]. Accurate accuracy
prediction from weights enables zero-shot model selection from large model repositories without
expensive retraining. The dominant approach trains an encoder on weight tensors and optimizes
for Spearman rank correlation ($\rho$) with ground-truth test accuracy [Unterthiner et al., 2020].

Prior work has established that permutation-equivariant encoders (NFNs) outperform flat MLP
encoders on this task [Navon et al., 2023; Zhou et al., 2023; Kofinas et al., 2023]. However,
all published comparisons suffer from a common confound: the two encoder types use different
numbers of parameters. Navon et al. (2023) report NFN $\rho \approx 0.73$ vs. flat MLP
$\rho \approx 0.60$, but these numbers cannot be compared directly — the flat MLP and NFN use
different capacities, so the observed $\Delta\rho$ reflects both the inductive bias advantage
and any capacity differences. Without controlling for capacity, we cannot answer the question
that practitioners actually face: *given a fixed parameter budget, should I use an equivariant
encoder?*

**The gap we address.** No published study provides a standardized $\Delta\rho$ benchmark
comparing matched-capacity NFN and flat MLP encoders on the Schurholt model zoo benchmarks
with bootstrap 95% confidence intervals. Three specific gaps exist: (1) no matched-capacity
($\pm5\%$) Δρ measurement with bootstrap CI; (2) no intermediate baseline (e.g., Deep Sets,
which provides permutation *invariance* rather than *equivariance*) to map the full symmetry
spectrum; (3) no direct empirical measurement of the capacity-wasting mechanism via permutation
sensitivity scores.

**Our insight.** Equivariant encoders eliminate the permutation orbit navigation problem by
construction: NFN encoders map all permutation-equivalent weight configurations to the same
embedding before prediction, operating effectively on the permutation-quotient space. At matched
capacity, every parameter is available for accuracy-predictive signal rather than orbit
disambiguation. We test whether this structural guarantee provides a decisive advantage over
encoders that must learn approximate invariance from data — and find that it does.

**Contributions.** Building on this insight, we make four contributions:

1. **First matched-capacity controlled $\Delta\rho$ benchmark.** We train flat MLP, Deep Sets
(permutation-invariant), and NFN (permutation-equivariant) encoders at matched $\sim$500K
parameters ($\pm5\%$) on the Schurholt MNIST-CNN model zoo and report $\Delta\rho$ with
bootstrap 95% confidence intervals. We find $\Delta\rho(\text{NFN} - \text{flat MLP}) = 0.512$
[95% CI: 0.381, 0.638] — exceeding the minimum meaningful threshold by a factor of 10.

2. **Symmetry spectrum benchmark.** We confirm a monotone symmetry hierarchy:
$\rho(\text{flat MLP}) = 0.169 < \rho(\text{Deep Sets}) = 0.447 < \rho(\text{NFN}) = 0.681$,
establishing that the degree of symmetry exploitation monotonically predicts accuracy prediction
quality at matched capacity.

3. **Empirical mechanism quantification.** Using permutation sensitivity scores, we directly
measure the capacity-wasting mechanism: flat MLP sensitivity = 0.649 (embeddings distinguish
permutation-equivalent weights) vs. NFN sensitivity = $7.34 \times 10^{-7}$ (885,000$\times$
reduction), confirming that equivariance eliminates the orbit navigation problem in practice.

4. **Discovery of accuracy-tier dependence.** NFN advantage is accuracy-regime-specific:
$\rho(\text{NFN}) = 0.856$ for low-accuracy models and $-0.314$ for high-accuracy models,
refuting our pre-registered prediction (P3) of mid-tier dominance and revealing that equivariant
benefit depends on weight-space diversity relative to accuracy diversity.

We organize the paper as follows. Section 2 reviews weight-space property prediction,
symmetry-aware encoders, and model zoo benchmarking. Section 3 describes our controlled
benchmark design. Section 4 presents the experimental setup. Section 5 reports results.
Section 6 discusses implications and limitations. Section 7 concludes.
