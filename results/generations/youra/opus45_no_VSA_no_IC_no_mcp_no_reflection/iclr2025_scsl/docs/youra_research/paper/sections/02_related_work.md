# Related Work

We position our investigation at the intersection of spurious correlation robustification and training dynamics analysis. Prior work establishes the phenomenon and develops mitigation strategies; we test whether gradient-based intervention is even measurable.

## Spurious Correlation and Shortcut Learning

Geirhos et al. (2020) formalized the taxonomy of shortcut learning in deep neural networks, documenting how models exploit dataset biases rather than learning intended features. Their survey established the scope of the problem but focused on detection rather than intervention.

Sagawa et al. (2020) introduced Group DRO and the Waterbirds/CelebA benchmarks, enabling standardized evaluation of worst-group accuracy. Group DRO requires group annotations during training—a resource often unavailable in practice. This limitation motivates annotation-free approaches.

**Our complement:** These works establish the phenomenon exists. We test whether gradient subspace methods can measure it during training.

## Annotation-Free Robustification

Liu et al. (2021) developed Just Train Twice (JTT), a two-stage approach that identifies spurious-reliant samples via training dynamics, then upweights them. JTT removes the need for group labels but requires two complete training runs.

Kirichenko et al. (2023) showed that last-layer retraining (Deep Feature Reweighting, DFR) suffices for robustification, suggesting pretrained representations already contain core features. DFR requires held-out data with group labels for reweighting.

Creager et al. (2021) introduced EIIL, inferring pseudo-environments from training dynamics without explicit group annotations. Like JTT, this operates at the sample level rather than gradient level.

**The gap we address:** All these methods operate on samples or final representations. None validates whether gradient directions themselves can distinguish spurious from core features—the assumption underlying gradient-based intervention.

## Simplicity Bias and Training Dynamics

Shah et al. (2020) documented simplicity bias: neural networks trained with SGD preferentially learn simpler features first. Since spurious correlations often involve simpler patterns (background texture vs. object shape), this explains early spurious feature acquisition.

Nagarajan et al. (2021) analyzed failure modes of out-of-distribution generalization, connecting training dynamics to generalization failure. Their theoretical analysis suggests early gradients favor low-complexity solutions.

**The assumption we test:** These works predict that early gradient subspaces should predominantly capture spurious directions. We attempt to measure this directly and find the measurement apparatus itself requires validation.

## Gradient-Based Representation Analysis

Gradient analysis methods have been applied to interpretability (Simonyan et al., 2014; Sundararajan et al., 2017) and adversarial robustness (Madry et al., 2018). These works analyze gradients with respect to inputs, not parameter-space subspaces.

Parameter-space gradient subspace analysis appears primarily in optimization literature (incremental PCA, streaming SVD) rather than robustification. We bridge this gap by applying subspace methods to spurious correlation measurement.

**Our contribution:** We identify minimum requirements for gradient subspace methods: sufficient accumulation density relative to parameter dimensionality. Single gradients per epoch produce subspaces too low-rank to measure anything meaningful in 25M-parameter models.

## Position Summary

Our work complements rather than supersedes existing approaches. We do not claim gradient-based robustification is impossible—we identify what valid measurement requires. Future gradient orthogonalization methods should validate their measurement apparatus using the requirements we establish before testing intervention hypotheses.
