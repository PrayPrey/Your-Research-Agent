## Related Work

**Related Papers**
1. **Title**: Score-based Generative Modeling of Graphs via the System of Stochastic Differential Equations (2022)
   - **Authors**: Jo, Lee, Hwang
   - **Summary**: Proposes a joint node-edge SDE system for molecular graph generation, establishing the base architecture that PWGD extends upon.
   - **Year**: 2022

2. **Title**: A Survey of Uncertainty in Deep Neural Networks (2021)
   - **Authors**: Gawlikowski et al.
   - **Summary**: Provides a comprehensive taxonomy of uncertainty quantification methods in deep learning, including heteroscedastic regression as an uncertainty estimation approach.
   - **Year**: 2021

3. **Title**: Bayesian Predictive Coding (2025)
   - **Authors**: Tschantz et al.
   - **Summary**: Introduces local Bayesian updates in deep networks with precision-weighted inference, serving as cross-domain inspiration for uncertainty-aware generative modeling.
   - **Year**: 2025

4. **Title**: Generative Uncertainty in Diffusion Models (arXiv:2502.20946)
   - **Authors**: Jazbec et al.
   - **Summary**: Develops post-hoc Laplace approximation methods for uncertainty quantification in diffusion models, serving as a primary baseline for comparison.
   - **Year**: 2025

5. **Title**: Smooth ECE: Principled Reliability Diagrams via Kernel Smoothing (arXiv:2309.12236)
   - **Authors**: Błasiok, Nakkiran
   - **Summary**: Proposes the SmoothECE metric for measuring model calibration, providing evaluation methodology for uncertainty quantification.
   - **Year**: 2023

6. **Title**: Uncertainty Quantification Using Neural Networks for Molecular Property Prediction (2020)
   - **Authors**: Hirschfeld et al.
   - **Summary**: Demonstrates uncertainty quantification methods for molecular property prediction tasks, highlighting that such methods exist for prediction but not for molecular generation.
   - **Year**: 2020

7. **Title**: Unified Uncertainty Calibration (arXiv:2310.01202)
   - **Authors**: Chaudhuri, Lopez-Paz
   - **Summary**: Presents a theoretical framework for combining aleatoric and epistemic uncertainty, providing foundational theory for unified uncertainty treatment.
   - **Year**: 2023

**Key Challenges**
1. **Lack of UQ in Molecular Generation**: While uncertainty quantification methods exist for molecular property prediction, there is a notable gap in applying such methods to molecular generation tasks.
2. **Post-hoc vs. Integrated Uncertainty**: Current approaches to diffusion model uncertainty rely on post-hoc methods like Laplace approximation rather than integrating uncertainty estimation directly into the generative process.
3. **Unified Uncertainty Treatment**: Combining aleatoric and epistemic uncertainty in a principled manner within generative models remains an open challenge requiring theoretical frameworks.
4. **Calibration Measurement**: Evaluating the quality of uncertainty estimates in generative models requires specialized metrics and methodology for reliability assessment.
