# Paper Summary: The Pitfalls of Simplicity Bias in Neural Networks
**Authors:** Shah et al. (2020) | **arXiv:** 2006.09081 | **Citations:** ~500

## Overview
Formally proves that ERM with gradient descent exhibits simplicity bias: networks prefer simpler (lower-complexity) predictive features even when complex features are more robustly predictive. This explains why spurious correlations (which are typically simpler statistical patterns) dominate ERM solutions.

## Key Contributions
- Formal characterization of simplicity bias as a property of gradient-based optimization on overparameterized networks
- Demonstrates simplicity bias causes catastrophic shortcut reliance even when core features are available
- Provides theoretical analysis connecting spectral properties of data to feature selection order

## Methodology
- Synthetic datasets with controlled feature complexity
- Analysis of gradient dynamics during training
- Comparison across architectures and optimizers

## Experiments & Results
- Networks consistently learn simple spurious features to near-100% accuracy while ignoring complex core features
- Bias persists across SGD, Adam, momentum variants
- Multi-class settings amplify simplicity bias via gradient competition between feature detectors

## Relevance to Gap 1
Most directly relevant: provides formal basis for why spurious (simpler) features are learned first. However, the analysis focuses on synthetic settings; the *gradient-level mechanism* on realistic datasets (Waterbirds, CelebA) with realistic spurious correlations (bird species vs. water/land background) is not characterized. The connection between feature complexity metrics and actual gradient quantities (per-sample gradient norms, Hessian eigenspectra) is not made explicit.

## Limitations
Synthetic data; does not characterize gradient trajectories on realistic benchmarks; no per-epoch measurement of feature learning order using gradient-level probes.
