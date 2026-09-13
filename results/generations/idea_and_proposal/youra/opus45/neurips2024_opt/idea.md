## Title
Sharpness-Triggered Optimizer Scheduling for Efficient Large-Scale Transformer Training

## Motivation
Training large language models costs millions of dollars and significant energy, yet practitioners typically use a single optimizer (Adam) throughout training despite evidence that loss landscape curvature evolves dramatically across training phases. Recent work on "edge of stability" dynamics shows that neural networks naturally progress through distinct sharpness regimes, suggesting different optimizers may be optimal at different phases. However, no principled method exists to exploit this insight for improved training efficiency at scale.

## Main Idea
We hypothesize that tracking sharpness evolution (maximum Hessian eigenvalue λ_max) and triggering optimizer transitions when sharpness stabilizes at the edge of stability (λ_max ≈ 2/η) improves training efficiency by 10-20% compared to fixed Adam. The causal mechanism: Adam's per-parameter adaptivity excels in high-curvature early training, while SGD's implicit regularization provides advantages after the edge of stability plateau, helping find flatter, better-generalizing solutions.

We will validate this using critical sharpness measurements (~10 forward passes overhead) across GPT-style models (125M-1B parameters) trained on standard corpora. Key predictions: (1) sharpness plateau provides reliable transition signals across scales, (2) scheduled training achieves target loss with ≤90% baseline compute, (3) optimal transition timing shifts earlier (relatively) at larger scales. Falsification occurs if efficiency gains fall below 5% or sharpness plateaus are undetectable. Success would enable principled optimizer scheduling, reducing training costs substantially.