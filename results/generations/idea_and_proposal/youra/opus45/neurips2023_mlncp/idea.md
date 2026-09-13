## Title
Noise as a Resource: Cross-Paradigm Bayesian Neural Networks via Unified Hardware Noise Abstraction

## Motivation
Emerging analog and optical hardware offer energy-efficient alternatives to digital computing, but inherent device noise is typically treated as an obstacle requiring mitigation. Meanwhile, Bayesian neural networks (BNNs) require stochastic sampling, traditionally implemented via costly digital random number generation. This creates a fundamental mismatch: hardware has unwanted noise while algorithms need randomness. Current approaches develop paradigm-specific solutions, preventing model portability across hardware types. We address this gap by reconceptualizing hardware noise as a computational resource for probabilistic inference.

## Main Idea
We propose a Noise Abstraction Layer that characterizes device-specific noise (thermal in analog, shot noise in optical) using Neural-SDEs, then maps these to a unified Gaussian probabilistic interface. This enables BNNs trained once in simulation to deploy across both analog and optical hardware without retraining. The key insight is that statistical properties of hardware noise—mean, variance, temporal correlation—can directly serve BNN weight sampling, replacing digital random number generation.

**Methodology:** Characterize noise via Neural-SDE profiling, map to unified abstraction, deploy noise-consuming BNN layers on MemTorch (analog) and pytorch-onn (optical) simulators.

**Expected outcomes:** <5% accuracy degradation across paradigms, well-calibrated uncertainty (ECE<5%), and >2× energy efficiency versus digital MC Dropout baselines on MNIST/CIFAR-10.