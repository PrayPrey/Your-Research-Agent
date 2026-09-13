# Title: Calibration-Free Diffusion Priors for Inverse Problems with Unknown Forward Models

## Motivation
Current diffusion-based inverse problem solvers assume precise knowledge of the forward model, which is unrealistic in many practical scenarios. In medical imaging, the actual system response often deviates from idealized models due to hardware imperfections, patient-specific variations, and environmental factors. Similarly, in seismic imaging or microscopy, calibration drift and unmodeled physics create significant model-reality gaps. This mismatch leads to reconstruction artifacts and unreliable uncertainty estimates, limiting the deployment of powerful diffusion priors in real-world applications.

## Main Idea
I propose a joint inference framework that simultaneously estimates the unknown forward model parameters and reconstructs the signal using diffusion priors. The key innovation is a hierarchical posterior sampling scheme where: (1) the outer loop samples forward model parameters from a learned prior over plausible degradation operators, and (2) the inner loop performs conditional diffusion sampling given the current forward model estimate. 

The methodology involves training a compact neural network to parameterize a family of forward models, regularized by physics-informed constraints. During inference, we alternate between updating forward model parameters via gradient-based optimization and sampling reconstructions using score-based guidance.

Expected outcomes include robust reconstructions under model uncertainty and automatic forward model calibration. This approach could significantly impact domains like portable medical imaging devices and field-deployed sensing systems where precise calibration is impractical.