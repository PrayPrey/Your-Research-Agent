# Title
**Adaptive Diffusion Priors for Inverse Problems with Uncertain Forward Models**

## Motivation
Current diffusion-based inverse problem solvers assume perfect knowledge of the forward model (e.g., measurement operator, noise characteristics). However, real-world applications often involve model uncertainties—miscalibrated sensors, unknown blur kernels, or complex noise distributions. This mismatch between assumed and true forward models severely degrades reconstruction quality and reliability. Bridging this gap is crucial for deploying diffusion models in safety-critical domains like medical imaging and scientific instrumentation.

## Main Idea
I propose a **joint learning framework** that simultaneously estimates forward model parameters and performs posterior sampling using diffusion models. The approach consists of:

1. **Amortized model estimation**: Train a neural network to predict forward model parameters (e.g., noise levels, blur kernels) from measurements by maximizing a variational lower bound on measurement likelihood.

2. **Uncertainty-aware guidance**: Modify diffusion sampling to incorporate epistemic uncertainty in the forward model through ensemble-based or Bayesian parameter averaging, producing robust reconstructions.

3. **Self-supervised refinement**: Leverage consistency between multiple diffusion trajectories and measurement fitting to iteratively refine both model estimates and reconstructions without ground truth.

**Expected outcomes**: Improved reconstruction quality under model mismatch, quantified uncertainty estimates, and demonstrated effectiveness on medical imaging tasks with calibration errors. This enables trustworthy deployment of diffusion models when forward models are partially known or time-varying.