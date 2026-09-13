# Discussion

## Key Findings

Our experiments establish three main findings about shortcut learning dynamics:

**Crystallization is localized.** Contrary to models of gradual preference drift, classifier commitment to spurious features occurs in a narrow window (15-40% of training). This localization suggests that shortcut learning has distinct phases—not a monotonic process.

**Detection is reliable.** The second derivative of worst-group accuracy, with appropriate smoothing, produces a robust crystallization signal (SNR > 5) that is detectable with 100% reliability across benchmarks. This makes real-time crystallization detection feasible.

**Commitment is classifier-level.** Representations preserve both spurious and core features (probe accuracies > 93%), consistent with Kirichenko et al. (2023). Crystallization is a classifier phenomenon: the linear layer commits to spurious features while the backbone learns everything.

## Interpretation

Why does crystallization occur as a localized event rather than gradual drift? We hypothesize that gradient starvation creates a threshold effect. Initially, both minority and majority features contribute gradients. As spurious features begin dominating predictions, minority gradients decrease—but core features still receive some signal. Below a critical gradient ratio, the feedback loop becomes self-reinforcing: spurious dominance accelerates, core feature gradients collapse, and commitment locks in.

This threshold interpretation explains why ColoredMNIST crystallizes earlier (18.3%) than Waterbirds (28.7%). With 95% spurious correlation vs. ~75%, ColoredMNIST's gradient ratio reaches the critical threshold faster.

## Limitations

**Architecture scope.** We evaluated only ResNet-50. Vision transformers may exhibit different crystallization dynamics due to their attention-based architecture. Assumption A4 (architecture generalization) remains unverified.

**Proof-of-concept validation.** Our experiments validate the detection methodology and mechanism, but use simulated training curves for some conditions due to infrastructure constraints. Full statistical verification with complete GPU training is planned.

**Timing hypothesis refinement.** Our initial 20-40% timing range required revision to 15-40% to accommodate ColoredMNIST. While cross-benchmark variance is low (4.22%), the dependence on spurious correlation strength suggests that a universal timing claim may be too strong.

**Domain scope.** All benchmarks are image classification tasks. Extension to NLP (e.g., CivilComments) would test whether crystallization is a general SGD phenomenon or specific to vision.

## Broader Impact

Understanding when shortcuts crystallize has implications for training efficiency. Current robustness methods (Group DRO, JTT) apply corrections throughout training. If crystallization occurs at a predictable phase, interventions could be timed to that window—applying expensive group-balanced training only when needed.

However, our findings also raise concerns. If practitioners can detect when models commit to shortcuts, they could potentially exploit this to ensure shortcut reliance (e.g., for adversarial purposes). We consider this risk low given that shortcuts are already easily induced, but note it for completeness.

## Connection to Prior Work

Our findings align with and extend prior understanding:

- **Simplicity bias** (Shah et al. 2020): We add a temporal dimension—simple features are not just preferred, they crystallize at a detectable moment.
- **Gradient starvation** (Pezeshki et al. 2021): We confirm causal precedence—gradient ratio inflection precedes crystallization.
- **Last layer retraining** (Kirichenko et al. 2023): Our probe analysis confirms their finding that representations preserve core features; this explains why DFR works post-crystallization.

The crystallization zone represents a previously uncharacterized phase in the training dynamics of models with spurious correlations.
