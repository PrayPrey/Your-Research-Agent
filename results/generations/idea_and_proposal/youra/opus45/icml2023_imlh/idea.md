## Title
Variational Concept Bottleneck Models for Calibrated Medical Image Interpretation

## Motivation
Medical AI systems increasingly support clinical decisions, yet their black-box nature undermines trust. Concept Bottleneck Models (CBMs) improve interpretability by predicting human-understandable concepts before final diagnoses, but their deterministic concept predictions lack uncertainty quantification—critical for high-stakes medical settings. Clinicians need to know not just *what* the model predicts, but *how confident* it is about each clinical finding. Current CBMs provide point estimates without calibrated confidence, limiting their clinical utility and preventing effective human-AI collaboration through targeted interventions.

## Main Idea
We propose Variational Concept Bottleneck Models (V-CBM), replacing deterministic concept layers with variational layers that output Gaussian parameters (μ, σ²) for each clinical concept. The core mechanism: variational inference naturally captures predictive uncertainty through learned distributions, enabling per-concept confidence estimates that align with actual accuracy (improved calibration).

**Methodology:** Using CheXpert/MIMIC-CXR datasets with DenseNet-121 encoders, we train dual-head concept predictors with reparameterization trick and ELBO loss. We measure concept-level Expected Calibration Error (ECE) across 5-fold cross-validation.

**Expected Outcomes:** >30% ECE improvement over vanilla CBMs; high-uncertainty concepts correlate with prediction errors, enabling targeted clinician intervention. This advances interpretable medical AI by providing calibrated, actionable uncertainty at the reasoning level clinicians understand.