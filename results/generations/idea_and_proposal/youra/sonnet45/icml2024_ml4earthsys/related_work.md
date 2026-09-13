## Related Work

**Related Papers**

1. **Title**: Basic Framework and Main Methods of Uncertainty Quantification ([SS:not_provided])
   - **Authors**: Zhang et al. (2020)
   - **Summary**: Provides comprehensive taxonomy of UQ methods including uncertainty propagation, model calibration, surrogate modeling, and variance-based sensitivity analysis framework that forms the foundation for hierarchical Bayesian decomposition.
   - **Year**: 2020

2. **Title**: Uncertainty Estimates via General Bias-Variance Decomposition ([SS:not_provided])
   - **Authors**: Gruber et al. (2022)
   - **Summary**: Systematic decomposition of predictive uncertainty into bias (epistemic) and variance (aleatoric) using Bregman Information, providing theoretical foundation for separating epistemic vs aleatoric uncertainty.
   - **Year**: 2022

3. **Title**: Bayesian Modeling for Uncertainty Management in Financial Risk Forecasting
   - **Authors**: Not specified
   - **Summary**: Hierarchical Bayesian Dynamic Linear Models decompose financial risk into market/model/parameter components using multi-level priors, operational in Basel III regulatory framework for 15+ years.
   - **Year**: 2024

4. **Title**: Mutual information based weighted variance for uncertainty quantification in ESMs ([SS:42a6f83d])
   - **Authors**: Majhi et al. (2023)
   - **Summary**: Applies mutual information-based variance decomposition to traditional Earth System Models (ESMs), quantifying uncertainty across parameterizations without addressing hybrid physics-ML models.
   - **Year**: 2023

5. **Title**: Deep Ensembles for Uncertainty Quantification in Statistical Downscaling ([SS:778be93e])
   - **Authors**: González-Abad et al. (2023)
   - **Summary**: Uses deep ensembles (multiple NN architectures) to quantify ML epistemic uncertainty in climate downscaling and improves uncertainty calibration under climate change conditions.
   - **Year**: 2023

6. **Title**: Quantifying uncertainty with conformal ensembles in climate prediction ([SS:47053957])
   - **Authors**: Harris et al. (2024)
   - **Summary**: Applies conformal prediction to climate projections for distribution-free coverage guarantees without parametric assumptions, providing early-stage work on non-parametric uncertainty quantification.
   - **Year**: 2024

7. **Title**: Non-Intrusive ML Framework for Debiasing Coarse Climate Simulations ([SS:9503a311])
   - **Authors**: Sorensen et al. (2024)
   - **Summary**: Quantifies rare events with return periods 2 orders of magnitude longer than training data using ML debiasing, addressing extrapolation challenge for high impact-low likelihood events.
   - **Year**: 2024

8. **Title**: Stable climate simulations using a realistic GCM with neural network parameterizations ([SS:affcf07c])
   - **Authors**: Wang et al. (2022)
   - **Summary**: ResD NNs replace super-parameterization in CAM5, achieving 10+ year stable simulations with improved tropical precipitation extremes, providing first demonstration of multi-year hybrid physics-ML climate model stability.
   - **Year**: 2022

9. **Title**: Stress-testing hybrid physics-ML climate simulations on unseen warmer climates ([SS:ad39ea22])
   - **Authors**: Lin et al. (2024)
   - **Summary**: Evaluates out-of-distribution generalization of hybrid models under climate change conditions and finds design decisions insufficient without multi-climate training data, identifying extrapolation failure problems.
   - **Year**: 2024

10. **Title**: Stable ML parameterization from embedded convection-permitting simulations ([SS:ee94ccfa])
    - **Authors**: Hu et al. (2024)
    - **Summary**: U-Net with thermodynamic constraints achieves 5-year stable simulations for E3SM-MMF, demonstrating importance of physics constraints for ML stability in climate modeling.
    - **Year**: 2024

11. **Title**: Dynamical-generative downscaling of climate model ensembles ([SS:a9421144])
    - **Authors**: Lopez-Gomez et al. (2024)
    - **Summary**: Combines physics-based models with generative AI (cGANs) for regional downscaling, drastically reducing computational cost while retaining physics-based skill using soft physics constraints.
    - **Year**: 2024

12. **Title**: A Reliable GAN Approach for Climate Downscaling and Weather Generation ([SS:95450dc1])
    - **Authors**: Rampal et al. (2025)
    - **Summary**: cGAN with intensity constraints achieves reliable downscaling across hyperparameters and captures extreme event statistics, demonstrating robustness of generative models for climate applications.
    - **Year**: 2025

13. **Title**: Differentiable Programming for Parameter Inference in Climate Models
    - **Authors**: Qu et al. (2024)
    - **Summary**: Demonstrates differentiable programming (JAX autodiff) enables gradient-based Bayesian inference in climate models at scale, achieving KL[q||p] < 0.05 for variational approximation.
    - **Year**: 2024

14. **Title**: Hybrid ML + Physics Model for Earth's Atmosphere ([GitHub:neuralgcm/neuralgcm, 900+ stars])
    - **Authors**: NeuralGCM (Google Research)
    - **Summary**: Production-ready hybrid model combining CAM5 dynamical core with ML parameterizations (clouds, convection, radiation) trained on ClimSim multi-scale dataset, providing primary validation target for uncertainty quantification frameworks.
    - **Year**: Not specified

15. **Title**: $50k Kaggle Competition for Hybrid Physics-ML Climate Emulation ([GitHub:leap-stc/climsim-kaggle-edition])
    - **Authors**: ClimSim Dataset
    - **Summary**: Largest multi-scale dataset (5.6M samples) for training ML parameterizations in hybrid climate models, including high-resolution super-parameterization outputs and coarse-resolution inputs.
    - **Year**: Not specified

**Key Challenges**

1. **No Uncertainty Decomposition in CMIP6**: Current state-of-the-art CMIP6 multi-model ensemble conflates physics differences, internal variability, and structural model errors without distinguishing sources, preventing targeted model improvement.

2. **Hybrid Physics-ML Model Uncertainty Gap**: Traditional ESM uncertainty quantification methods do not address ML-specific uncertainty sources (architecture choices, training data limitations) in hybrid physics-ML models.

3. **Statistical Independence Assumptions**: Hierarchical Bayesian frameworks assume statistical independence of uncertainty sources, but physical reality exhibits correlations (e.g., physics parameterization errors correlate with ML training data gaps in tropical convection).

4. **Computational Cost of Ensemble Methods**: CMIP6 requires 50 models × 30 ensemble members × 150-year simulations = 225,000 simulation-years, prohibitive for high-resolution or exploratory scenarios.

5. **Rare Event Uncertainty Quantification**: Conformal prediction with N=50-100 ensemble members limits rare event resolution (1% events → 0.5-1 samples per calibration), requiring stratified calibration or extreme value theory extensions.

6. **Out-of-Distribution Extrapolation**: Hybrid models trained on historical climate data (1980-2020) may not generalize to future climate states under RCP8.5 scenarios (4°C warming), requiring time-varying uncertainty characterization.

7. **Variational Approximation Error**: ELBO-optimized variational posteriors tend toward overconfidence, potentially underestimating tail uncertainty by ~10%, requiring posterior predictive checks and MCMC validation.

8. **Attribution Validation Challenge**: Demonstrating that targeted improvements based on uncertainty attribution (e.g., enhancing ML training in high-uncertainty regions) actually reduces total uncertainty requires multi-year retraining experiments with significant computational costs.
