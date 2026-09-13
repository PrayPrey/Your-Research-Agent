# Title
**Hierarchical Uncertainty Quantification for Physics-ML Hybrid Climate Models via Deep Ensembles with Physics Constraints**

## Motivation
Hybrid physics-ML climate models promise computational efficiency by replacing expensive subgrid parameterizations with learned emulators. However, their adoption is hindered by lack of reliable uncertainty estimates—critical for climate projections that inform billion-dollar policy decisions. Current ML emulators often produce overconfident predictions that fail to capture epistemic uncertainty from limited training data and aleatoric uncertainty from chaotic dynamics. Domain scientists require calibrated confidence intervals to distinguish between model uncertainty and genuine climate variability, especially for High Impact-Low Likelihood events.

## Main Idea
Develop a hierarchical Bayesian framework combining deep ensembles with physics-informed constraints for uncertainty quantification in ML-based parameterizations. The approach:
1. **Physics-constrained ensembles**: Train diverse neural networks that respect conservation laws (energy, mass, momentum) through soft constraints and architectural inductive biases
2. **Multi-fidelity calibration**: Leverage both high-resolution simulations and observational data to calibrate uncertainty estimates across scales
3. **Out-of-distribution detection**: Implement physics-based anomaly scores to identify when the emulator encounters unprecedented climate states
4. **Propagation analysis**: Quantify how parameterization uncertainty cascades through coupled climate system components

Expected outcomes include calibrated prediction intervals for temperature/precipitation extremes and improved risk assessment for climate tipping points, enabling more trustworthy hybrid models for operational climate projection.