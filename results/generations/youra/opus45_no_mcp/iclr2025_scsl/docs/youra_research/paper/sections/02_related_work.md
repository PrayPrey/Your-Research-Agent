# Related Work

## Shortcut Learning in Deep Neural Networks

Geirhos et al. (2020) provide a comprehensive taxonomy of shortcut learning across vision, language, and medical imaging domains. They characterize shortcuts as decision rules that perform well on standard benchmarks but fail under distribution shift. While their survey establishes the ubiquity of the problem, it does not address temporal dynamics—when during training shortcuts become dominant.

## Simplicity Bias and Feature Learning

Shah et al. (2020) formalized simplicity bias: neural networks trained with gradient descent preferentially learn features that are linearly separable in the input space. Their theoretical and empirical analysis shows that when multiple features predict the label, the simpler one is learned first. This provides the "what"—spurious features, often simpler than core features, gain early advantage. However, simplicity bias is characterized as a static property of SGD optimization, not as a temporal phase.

Hermann and Lampinen (2020) extended this analysis to show that even when models eventually learn complex features, they do so more slowly and less reliably than simple ones. This suggests a window where intervention could redirect learning, but they do not identify when this window closes.

## Gradient Starvation

Pezeshki et al. (2021) identified gradient starvation as the mechanism by which dominant features suppress learning of minority features. When one feature explains most of the variance in the loss, gradients flowing to alternative feature pathways diminish. This creates a feedback loop: dominant features receive stronger gradients, further increasing their dominance.

Gradient starvation explains *why* shortcuts persist once established, but not *when* the feedback loop becomes self-reinforcing. Our work identifies this transition point—the crystallization zone—where gradient starvation accelerates and commitment becomes irreversible.

## Group Robustness Methods

Sagawa et al. (2020) introduced distributionally robust optimization (Group DRO) and the Waterbirds benchmark, establishing worst-group accuracy as the primary metric for spurious correlation robustness. Group DRO requires group labels throughout training, applying upweighting uniformly across epochs.

Liu et al. (2021) proposed Just Train Twice (JTT), which trains an initial ERM model, identifies misclassified examples, and upweights them in a second training phase. This two-stage approach implicitly acknowledges that early training produces shortcuts, but does not characterize when the critical transition occurs.

Kirichenko et al. (2023) showed that last layer retraining (DFR) is surprisingly effective: retraining only the final linear layer on a balanced validation set recovers most of the worst-group accuracy lost to shortcuts. Crucially, they demonstrated that representations learned by ERM contain both spurious and core features—the problem is classifier-level weighting, not representation-level suppression. Our findings align with this: crystallization is a classifier phenomenon, and representations preserve both feature types even post-crystallization.

## Loss Landscape and Training Dynamics

Cohen et al. (2021) characterized the edge of stability phenomenon: gradient descent with large learning rates operates at the edge of instability, with progressive sharpening throughout training. While this describes general optimization dynamics, the connection to spurious feature learning remains unexplored.

Foret et al. (2021) introduced Sharpness-Aware Minimization (SAM), showing that flat minima correlate with better generalization. Whether SAM affects crystallization timing or prevents it entirely is an open question for future work.

## Positioning Our Work

Prior work describes *what* features are learned (simplicity bias), *why* shortcuts persist (gradient starvation), and *how* to correct them (Group DRO, JTT, DFR). We contribute the temporal dimension: *when* classifier commitment accelerates and becomes irreversible. This crystallization zone—occurring at 15-40% of training—represents a previously uncharacterized phase transition in shortcut learning dynamics.

Our detection method using d²WGA/dt² provides a practical tool for identifying this transition. Combined with existing robustness methods, this enables timing-aware interventions that could improve efficiency while maintaining effectiveness.
