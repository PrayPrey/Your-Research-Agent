# Paper Summary: On the Spectral Bias of Neural Networks
**Authors:** Rahaman et al. (2019) | **arXiv:** 1806.08734 | **Citations:** ~1000

## Overview
Demonstrates that neural networks trained with gradient descent exhibit spectral bias (also called frequency principle): they learn low-frequency components of the target function first, and higher-frequency components are learned progressively later. This is the foundational theoretical result explaining why simpler (lower-frequency) features are acquired before complex (higher-frequency) ones.

## Key Contributions
- Formal analysis of frequency learning order in MLPs
- Low-frequency bias holds across architectures and optimizers
- Connection to generalization: low-frequency functions generalize better, explaining why SGD finds generalizable solutions in overparameterized settings

## Methodology
- Fourier analysis of network outputs across training epochs
- Synthetic 1D/2D function fitting tasks
- Theoretical analysis of NTK (neural tangent kernel) eigenspectrum

## Experiments & Results
- Networks fit low-frequency components within first ~10% of training epochs
- High-frequency components require 10-100x more iterations
- Effect is robust across depth, width, activation function

## Relevance to Gap 1
The spectral bias directly implies spurious features (which correlate with simpler low-frequency patterns in the input, e.g., background texture statistics) will be learned before core features (which require higher-frequency spatial reasoning, e.g., bird shape details). HOWEVER: this theory applies to function approximation of smooth functions and the connection to realistic spurious correlations in classification (where "simplicity" is defined by correlation strength, not frequency) is conceptual, not rigorously established. The gap: can spectral bias be operationalized as a measurable quantity (e.g., gradient alignment between spurious-feature-rich vs. core-feature-rich mini-batches) that predicts feature learning order on Waterbirds/CelebA?

## Limitations
Theory developed for regression on smooth functions; extension to classification with discrete spurious correlations not formalized; no per-batch gradient-level analysis on realistic benchmarks.
