## Title
Saliency-Guided Adaptive Neural Operators for Efficient PDE Solving with Localized Complexity

## Motivation
Neural operators like FNO achieve remarkable efficiency for PDEs but use fixed spectral mode allocation regardless of local solution complexity. This wastes computation in smooth regions while under-resolving sharp gradients, boundary layers, and shocks—precisely where accuracy matters most. Recent benchmarks reveal significant limitations of current architectures for high-frequency components critical to turbulent flows and discontinuities. Inspired by visual cortex saliency processing, we propose adaptive computational resource allocation that concentrates spectral modes where solution complexity demands it.

## Main Idea
We introduce AGANO (Adaptive Gumbel-softmax Allocation Neural Operator), which dynamically allocates Fourier spectral modes based on learned solution complexity. A lightweight complexity detector (MobileNet-style CNN, ~2% FLOPs overhead) identifies high-gradient regions from coarse solution estimates. Gumbel-softmax transformation converts these complexity scores into differentiable mode allocation weights, enabling end-to-end training while converging to near-discrete selection via temperature annealing (τ=5→0.1). High-complexity regions receive up to 32 modes; smooth regions use as few as 4.

**Key predictions:** ≥30% L2 error reduction at equal FLOPs (or equal accuracy with 50% fewer FLOPs) on PDEs with localized sharp gradients (Navier-Stokes, Burgers, Darcy). Validation includes complexity detector localization accuracy (>90% IoU) and mode allocation entropy convergence. This approach enables higher-resolution scientific simulations within fixed computational budgets.