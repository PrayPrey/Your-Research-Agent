```
1. **Title**: A PDE-Informed Latent Diffusion Model for 2-m Temperature Downscaling (arXiv:2510.23866)
   - **Authors**: Paul Rosu, Muchang Bahng, Erick Jiang, Rico Zhu, Vahid Tarokh
   - **Summary**: This paper introduces a physics-conditioned latent diffusion model designed for dynamical downscaling of atmospheric data, specifically focusing on reconstructing high-resolution 2-meter temperature fields. The model integrates a partial differential equation (PDE) loss term into the training objective to enforce physical consistency through a finite-difference approximation of an effective advection-diffusion balance. Empirical results indicate that this approach enhances the physical plausibility of generated fields.
   - **Year**: 2025

2. **Title**: Km-scale dynamical downscaling through conformalized latent diffusion models (arXiv:2510.13301)
   - **Authors**: Alessandro Brusaferri, Andrea Ballarino
   - **Summary**: This work addresses the issue of miscalibrated grid-point-level uncertainty estimates in generative diffusion models used for dynamical downscaling. By augmenting the downscaling pipeline with a conformal prediction framework, the authors derive conditional quantile estimates incorporated into a conformalized quantile regression procedure. This method targets locally adaptive prediction intervals with finite-sample marginal validity, resulting in improved coverage and stable probabilistic scores.
   - **Year**: 2025

3. **Title**: Fast, Scale-Adaptive, and Uncertainty-Aware Downscaling of Earth System Model Fields with Generative Machine Learning (arXiv:2403.02774)
   - **Authors**: Philipp Hess, Michael Aich, Baoxiang Pan, Niklas Boers
   - **Summary**: The authors present a consistency model that efficiently and accurately downscales arbitrary Earth System Model (ESM) simulations without retraining. This approach yields probabilistic downscaled fields at resolutions limited only by the observational reference data. The model outperforms state-of-the-art diffusion models at a fraction of the computational cost while maintaining high controllability on the downscaling task and generalizing to unseen climate states without explicitly formulated physical constraints.
   - **Year**: 2024

4. **Title**: Debias Coarsely, Sample Conditionally: Statistical Downscaling through Optimal Transport and Probabilistic Diffusion Models (arXiv:2305.15618)
   - **Authors**: Zhong Yi Wan, Ricardo Baptista, Yi-fan Chen, John Anderson, Anudhyan Boral, Fei Sha, Leonardo Zepeda-Núñez
   - **Summary**: This paper introduces a two-stage probabilistic framework for statistical downscaling using unpaired data. The approach involves a debiasing step via an optimal transport map and an upsampling step achieved by a probabilistic diffusion model with posteriori conditional sampling. The method characterizes a conditional distribution without needing paired data and faithfully recovers relevant physical statistics from biased samples, demonstrating utility on fluid flow problems representative of challenges in numerical simulations of weather and climate.
   - **Year**: 2023

5. **Title**: Efficient Error Certification for Physics-Informed Neural Networks (arXiv:2305.10157)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This work focuses on providing efficient error certification methods for physics-informed neural networks (PINNs). By developing techniques to obtain error bounds and assess the reliability of PINN solutions, the authors aim to enhance the trustworthiness of these models in solving partial differential equations relevant to physical systems.
   - **Year**: 2023

6. **Title**: Efficient Posterior Sampling For Diverse Super-Resolution (arXiv:2205.10347)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: The authors propose a method for efficient posterior sampling in the context of diverse super-resolution tasks. By leveraging hierarchical variational autoencoders (HVAEs), the approach aims to improve the expressiveness and generalization capabilities of generative models, potentially benefiting applications in climate downscaling where diverse high-resolution outputs are desired.
   - **Year**: 2023

7. **Title**: GenesisTex: Adapting Image Denoising Diffusion to Texture Space (arXiv:2403.17782)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This paper presents GenesisTex, a method that adapts image denoising diffusion models to texture space. By introducing a sampling algorithm in texture space and employing multi-view consistency strategies, the approach aims to generate high-quality texture maps, which could be relevant for enhancing the realism of downscaled climate data visualizations.
   - **Year**: 2024

8. **Title**: A Bayesian Drift-Diffusion Model of Schachter-Singer’s Two Factor Theory of Emotion (arXiv:2406.11086)
   - **Authors**: Lance Ying, Audrey Michal, Jun Zhang
   - **Summary**: The authors develop a Bayesian drift-diffusion model to computationally implement Schachter-Singer's Two-Factor theory of emotion. While not directly related to climate downscaling, the Bayesian modeling approach and handling of uncertainty may offer insights applicable to probabilistic climate modeling.
   - **Year**: 2024

9. **Title**: Technical report. In progress (arXiv:2310.15111)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This technical report discusses generative modeling with inverse heat dissipation, presenting methods that could be relevant for modeling diffusion processes in climate systems. The work is in progress and may provide foundational insights for future research in physics-constrained generative models.
   - **Year**: 2023

10. **Title**: Published as a conference paper at ICLR 2024 (arXiv:2405.14616)
    - **Authors**: [Authors not specified in the provided excerpt]
    - **Summary**: This conference paper presents a study on unified hyperparameter results for long-term forecasting tasks, comparing various competitive models under different prediction lengths. The findings may offer valuable benchmarks and methodologies applicable to climate downscaling models.
    - **Year**: 2024
```

**Key Challenges:**

1. **Physical Consistency**: Ensuring that downscaled outputs adhere to fundamental physical laws, such as conservation of mass and energy, remains a significant challenge. Integrating hard physical constraints into generative models without compromising their flexibility is complex.

2. **Uncertainty Quantification**: Accurately capturing and representing both aleatoric (inherent randomness) and epistemic (model-related) uncertainties in downscaled climate projections is essential for reliable decision-making but remains difficult.

3. **Generalization to Unseen Climate States**: Developing models that can generalize effectively to climate conditions not present in the training data is challenging, particularly given the non-stationary nature of climate systems and the occurrence of extreme events.

4. **Computational Efficiency**: Balancing the need for high-resolution, physically consistent downscaling with computational efficiency is a persistent challenge, especially when aiming for methods that are significantly faster than traditional dynamical downscaling approaches.

5. **Data Availability and Quality**: The scarcity of high-quality, high-resolution climate datasets for training and validation poses a challenge. Ensuring that models are trained on representative and comprehensive datasets is crucial for their performance and reliability.
``` 