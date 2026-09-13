## Title
Homeostatic α-Control (HαC): Adaptive Learning Rate Regulation via Online Gradient Tail Index Monitoring

## Motivation
Heavy-tailed gradient noise naturally emerges during neural network training and correlates with generalization—moderate tail indices (α ∈ [1.5, 1.9]) help SGD escape narrow minima and find flatter, more generalizable solutions. However, existing approaches either ignore this phenomenon or inject artificial noise (e.g., AHTSGD). No method currently monitors and adaptively controls the *emergent* tail behavior. This gap leaves a powerful training signal unexploited.

## Main Idea
We propose HαC, an optimizer wrapper that monitors gradient noise tail index (α) using online Hill estimation and dynamically adjusts learning rate through homeostatic feedback to maintain α within the beneficial range [1.5, 1.9]. The causal mechanism: higher learning rates increase exploration, producing heavier tails (lower α); lower rates yield lighter tails. When measured α falls below 1.5 (too heavy), HαC increases learning rate; when above 1.9 (too light), it decreases learning rate.

Key methodology: (1) maintain rolling buffer of ~1000 gradient samples, (2) compute confidence-weighted Hill estimates, (3) apply bounded adjustments (≤5% per step) with EMA smoothing. We predict HαC-wrapped SGD achieves ≥1% test accuracy improvement over baselines on CIFAR-10/100 with <10% computational overhead. Unlike noise-injection methods, HαC leverages naturally emerging heavy-tailed dynamics, offering a principled "observe-and-adapt" approach to generalization-aware optimization.