# Related Work

## Spurious Correlations and Group Robustness

Spurious correlations cause models to rely on dataset biases rather than causal features. Sagawa et al. (2020) introduced Group DRO, which minimizes worst-case loss over predefined groups, achieving strong results on Waterbirds and CelebA. However, Group DRO requires group annotations during training — expensive and often unavailable.

Methods without group annotations have emerged. **Just Train Twice (JTT)** (Liu et al., 2021) trains an initial ERM model, identifies misclassified examples (which correlate with minority groups), and upweights them in a second training run. **Learning from Failure (LfF)** (Nam et al., 2020) explicitly trains a biased network and uses its failures to guide debiasing. Both methods exploit the insight that spurious features are learned early, but require two-stage training.

**Deep Feature Reweighting (DFR)** (Kirichenko et al., 2022) demonstrates that pretrained ERM features are sufficient for state-of-the-art worst-group accuracy when the last layer is retrained on group-balanced data. This finding directly informs our negative result: if CLIP features already separate spurious and core concepts, there are no emergence dynamics left to observe.

## Simplicity Bias and Learning Dynamics

Shah et al. (2020) established that SGD exhibits **simplicity bias**: networks learn the simplest predictive features first and may never learn more complex features even when they have higher predictive power. This explains why spurious (often simpler) correlations dominate.

**Gradient Starvation** (Pezeshki et al., 2021) provides a dynamical systems perspective: cross-entropy minimization on features with different frequencies causes some features to receive diminishing gradient signal. Once simple features achieve low loss, complex features are "starved" of learning signal.

Our work extends this literature by testing whether emergence *uniformity* (variance across sample subsets) differs between spurious and core features. The negative result suggests that while emergence *timing* may differ during training, this signal is lost in pretrained representations.

## Linear Probing for Representation Analysis

Linear probes are standard tools for analyzing pretrained representations (Alain & Bengio, 2017). The CLIP evaluation protocol (Radford et al., 2021) uses logistic regression with regularization-strength sweeps (C-sweep) to assess representation quality.

We adapted this protocol for emergence dynamics: treating C as an epoch proxy and computing CV across sample subsets. Our failure reveals a category error: C-sweep produces representation quality scores, not learning trajectory data. Convex optimization converges in a single pass regardless of C; there is no "emergence" to measure.

## Positioning Our Work

| Method | Stage | Annotations | Detects During Training |
|--------|-------|-------------|-------------------------|
| Group DRO | 1 | Yes | N/A |
| JTT | 2 | No | Yes (early errors) |
| LfF | 2 | No | Yes (biased network) |
| DFR | 1 | Yes (balanced retrain) | No |
| **EUR (proposed)** | 1 | No | **Intended: Yes** |

Our contribution is a negative result: the CV-based detection that EUR depends on does not work on frozen pretrained features. This finding clarifies the necessary conditions for emergence-based spurious detection and guides future work toward training-time measurement.
