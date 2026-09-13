1. **Title**: Joint Parameter and Parameterization Inference with Uncertainty Quantification through Differentiable Programming (arXiv:2403.02215)
   - **Authors**: Yongquan Qu, Mohamed Aziz Bhouri, Pierre Gentine
   - **Summary**: This paper introduces a framework for jointly estimating physical parameters and machine learning parameterizations with uncertainty quantification. By integrating differentiable programming, the approach enables efficient Bayesian inference within high-dimensional parameter spaces, enhancing hybrid physics-ML modeling capabilities.
   - **Year**: 2024

2. **Title**: Am I Confused or Is This Confusing?: Deep Ensembles for ENSO Uncertainty Quantification (arXiv:2512.17153)
   - **Authors**: Devin M. McAfee, Elizabeth A. Barnes
   - **Summary**: The authors deploy deep ensembles to analyze the predictability of the El-Niño Southern Oscillation (ENSO) within the Community Earth System Model 2 Large Ensemble. They demonstrate that epistemic uncertainty, modeled by ensemble disagreement, effectively signals predictive error growth associated with distributional shifts under climate change scenarios.
   - **Year**: 2025

3. **Title**: AutoDEUQ: Automated Deep Ensemble with Uncertainty Quantification (arXiv:2110.13511)
   - **Authors**: Romain Egele, Romit Maulik, Krishnan Raghavan, Bethany Lusch, Isabelle Guyon, Prasanna Balaprakash
   - **Summary**: AutoDEUQ presents an automated approach for generating deep neural network ensembles, leveraging joint neural architecture and hyperparameter search. The method decomposes predictive variance into aleatoric and epistemic uncertainties, outperforming several existing uncertainty quantification methods on regression benchmarks.
   - **Year**: 2021

4. **Title**: Adversarial Uncertainty Quantification in Physics-Informed Neural Networks (arXiv:1811.04026)
   - **Authors**: Yibo Yang, Paris Perdikaris
   - **Summary**: This work introduces a deep learning framework for quantifying and propagating uncertainty in systems governed by non-linear differential equations using physics-informed neural networks. The approach employs latent variable models and adversarial inference to constrain predictions to satisfy physical laws, effectively characterizing uncertainty in physical systems.
   - **Year**: 2018

5. **Title**: Efficient Error Certification for Physics-Informed Neural Networks (arXiv:2305.10157)
   - **Authors**: [Authors not specified]
   - **Summary**: The paper addresses the challenge of error certification in physics-informed neural networks (PINNs). It proposes an efficient method for certifying errors in PINNs, enhancing their reliability for modeling physical systems.
   - **Year**: 2023

**Key Challenges:**

1. **Reliable Uncertainty Quantification**: Developing methods that accurately capture both epistemic and aleatoric uncertainties in hybrid physics-ML climate models remains a significant challenge.

2. **Integration of Physics Constraints**: Ensuring that machine learning models adhere to fundamental physical laws, such as conservation principles, requires sophisticated techniques to incorporate these constraints effectively.

3. **Handling Distributional Shifts**: Climate models must account for distributional shifts due to climate change, which can affect the reliability of predictions and uncertainty estimates.

4. **Computational Efficiency**: Balancing the complexity of models with the need for computational efficiency is crucial, especially when dealing with high-dimensional parameter spaces and large datasets.

5. **Data Scarcity and Quality**: Limited availability of high-quality observational data poses challenges for training and validating hybrid models, impacting their accuracy and generalizability. 