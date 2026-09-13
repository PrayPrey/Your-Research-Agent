# 2. Related Work

Our work sits at the intersection of three research threads: predicting neural network
properties from weights, symmetry-aware architectures for weight-space learning, and
model zoo benchmarking. We review each in turn, highlighting the specific gaps our
controlled benchmark fills.

## 2.1 Weight-Space Property Prediction

The idea of predicting neural network properties directly from weight tensors was
established by Unterthiner et al. [2020], who trained flat MLP encoders — concatenating
all weight tensors into a single vector — to predict test accuracy on a proprietary model
zoo. They demonstrate that Spearman rank correlation ($\rho$) is a natural evaluation
metric for rank-ordering models by accuracy, and achieve $\rho \approx 0.5$–$0.7$ on
their benchmark. This flat MLP approach has since become the standard baseline for
weight-space property prediction.

Eilertsen et al. [2020] extend property prediction to training objective classification
from CNN weights, further demonstrating that weight tensors carry predictive information
beyond a single property. Both works, however, use flat concatenation — treating weight
tensors as unstructured vectors — without exploiting the permutation symmetry structure
inherent to feedforward networks.

The limitation of flat approaches is precisely what our work quantifies: at a fixed
parameter budget, flat MLPs waste substantial capacity distinguishing permutation-equivalent
weight configurations that should map to identical predictions.

## 2.2 Symmetry-Aware Weight-Space Encoders

**Neural Functional Networks (NFNs).** Navon et al. [2023] introduce equivariant weight-space
networks that respect the neuron-permutation symmetry of feedforward networks. Their
architecture defines equivariant linear maps between spaces of weight tensors, ensuring that
permuting neurons in the target network produces a corresponding permutation in the encoder's
internal representations. Applied to the Schurholt MNIST-CNN zoo, they report accuracy
prediction $\rho$ values substantially higher than flat MLP baselines.

Zhou et al. [2023] independently develop Neural Functional Transformers (NFTs), extending
equivariance to transformer-based weight encoders. Kofinas et al. [2023] propose AETHER,
a further refinement with improved equivariant message passing. All three works demonstrate
that exploiting permutation symmetry improves weight-space learning.

However, a critical limitation shared across these works is that comparisons against flat
MLP baselines are **not controlled for encoder capacity**. The NFN architectures naturally
use different numbers of parameters than flat MLPs evaluated in the same papers, making
it impossible to isolate the inductive bias contribution from capacity effects. Our
matched-capacity benchmark directly addresses this confound.

**Deep Sets and permutation-invariant encoders.** Zaheer et al. [2017] prove that any
permutation-invariant function on sets can be decomposed as $\rho(\sum_i \phi(x_i))$ for
appropriate $\phi$ and $\rho$. This Deep Sets architecture provides *permutation invariance*
— a weaker property than the *permutation equivariance* of NFNs — and has been applied to
various set-structured data. However, Deep Sets has not been benchmarked as an intermediate
baseline on model zoo accuracy prediction, leaving the invariance-vs-equivariance gap
unmeasured. We fill this gap by including a matched-capacity Deep Sets baseline in our
symmetry spectrum benchmark.

## 2.3 Model Zoo Benchmarking

Schurholt et al. [2022] release the first large-scale model zoo benchmarks for weight-space
learning: the MNIST-CNN zoo (~4,000 checkpoints) and CIFAR-10 zoo (~1,500 checkpoints),
each with ground-truth test accuracies and standardized train/test splits. These benchmarks
have become the standard evaluation platform for weight-space property prediction methods.

Schurholt et al. [2023] subsequently compare multiple encoder architectures on their own
zoo, providing a broad survey of approaches. However, their comparison does not match
encoder capacities across architectures, does not include bootstrap confidence intervals
on $\Delta\rho$, and does not include a Deep Sets intermediate baseline. Our work
retrofits these missing methodological components onto the same Schurholt benchmark.

## 2.4 Permutation Symmetry in Neural Networks

The mathematical structure of permutation symmetry in feedforward networks is well-established.
For a network with $L$ hidden layers of widths $n_1, \ldots, n_L$, any permutation of
neurons within layer $\ell$ produces a functionally-equivalent weight configuration — yielding
$|S_{n_1}| \times \cdots \times |S_{n_L}|$ symmetry-equivalent weight vectors per function
[Navon et al., 2023; Zhou et al., 2023]. The practical consequence for encoder design has been
discussed theoretically but never empirically quantified via permutation sensitivity scores
before our work.

Related work on loss landscape symmetry [Entezari et al., 2022] and linear mode connectivity
[Ainsworth et al., 2023] studies permutation symmetry from a different angle — seeking to
align networks before interpolation rather than to encode them. Our work focuses specifically
on the encoder design implication: structural equivariance eliminates the need to learn
permutation invariance from data.

## 2.5 Positioning Our Contribution

Our controlled $\Delta\rho$ benchmark differs from all prior work in three ways:
(1) we match encoder capacity ($\pm5\%$ parameter count) across all three symmetry levels
via per-architecture width grid search; (2) we report bootstrap 95% CIs on $\Delta\rho$,
enabling statistical comparison; (3) we directly measure the capacity-wasting mechanism
via permutation sensitivity scores rather than inferring it from downstream performance.
Together, these contributions establish a reproducible benchmark methodology that the
community can apply to future encoder comparisons.
