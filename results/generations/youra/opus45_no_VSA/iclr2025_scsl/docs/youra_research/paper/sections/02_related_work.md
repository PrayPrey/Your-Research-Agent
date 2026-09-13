# Related Work

## Group Robustness Methods

The worst-group accuracy problem has motivated several intervention strategies. **Group DRO** (Sagawa et al., 2019) reweights the loss to minimize worst-group error, achieving ~91% WGA on Waterbirds but requiring group labels during training. **Just Train Twice** (Liu et al., 2021) identifies hard examples in a first training pass and upweights them in a second. **Last-layer retraining** (Kirichenko et al., 2022) demonstrates that ERM learns good features—only the classifier layer needs adjustment. This finding is critical: it shows the problem is not that core features fail to be learned, but that they are suppressed in the final classifier.

Our work extends Kirichenko et al. by asking *why* this suppression occurs. We provide a mechanistic explanation rooted in loss landscape geometry: minority groups maintain higher curvature because majority-dominated gradient updates smooth only majority-relevant directions.

## Loss Landscape Analysis

Loss landscape geometry influences generalization. **Sharpness-Aware Minimization (SAM)** (Foret et al., 2021) seeks flat minima for better generalization. Prior work in our pipeline established that group-conditional Hessian eigenspaces are near-orthogonal (~88.5°), meaning majority and minority groups effectively optimize in distinct parameter subspaces.

Kalra & Barkeshli (2023) characterized early training dynamics via a phase diagram identifying four regimes: transient, saturation, progressive sharpening, and edge of stability. Our temporal precedence finding (τ_r→SR = 3.67 epochs) situates the gradient-to-curvature mechanism within these early training phases.

## Feature Learning Dynamics

**Simplicity bias** (Shah et al., 2020) explains that neural networks preferentially learn simpler features first—often the spurious ones. **Shortcut learning** (Geirhos et al., 2020) provides a unifying framework: models learn whatever features minimize training loss, which on biased data means shortcuts.

LaBonte & Muthukumar (2026) provide the first theoretical proof that SGD learns spurious features first and exponentially fast, with the spurious component inhibiting signal feature learning. Our work complements this theory with empirical characterization: we measure *when* the gradient-curvature relationship shifts during training and establish the temporal lag that their theory predicts.

## Positioning

Existing work asks: "How do we fix worst-group accuracy?" We ask: "Why does the loss landscape become asymmetric in the first place?" By establishing that curvature asymmetry emerges from training dynamics (SR₀ ≈ 1.0) and that gradient convergence precedes curvature divergence (τ > 0), we provide the mechanistic foundation for designing temporally-aware interventions.
