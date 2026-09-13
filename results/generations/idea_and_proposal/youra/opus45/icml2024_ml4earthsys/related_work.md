## Related Work

**Related Papers**
1. **Title**: Physics-Constrained Flow Matching: Sampling Generative Models with Hard Constraints (arXiv:2506.04171)
   - **Authors**: Utkarsh et al. (MIT)
   - **Summary**: Proposes a zero-shot inference framework that enforces arbitrary nonlinear constraints in pretrained flow-based models through continuous physics-based corrections.
   - **Year**: 2025

2. **Title**: Physics-aware generative models for turbulent fluid flows through energy-consistent stochastic interpolants (arXiv:2504.05852)
   - **Authors**: Mücke & Sanderse
   - **Summary**: Introduces learnable interpolant parameters to achieve energy stability and divergence-freeness in turbulent flow generation, achieving 10x longer stable rollouts compared to baselines.
   - **Year**: 2025

3. **Title**: Combining deep generative models with extreme value theory for synthetic hazard simulation
   - **Authors**: Peard & Hall
   - **Summary**: Combines GANs with extreme value theory (EVT) to produce spatially coherent compound hazard simulations for climate applications.
   - **Year**: 2023

4. **Title**: Fast, scale-adaptive and uncertainty-aware downscaling of Earth system model fields
   - **Authors**: Hess et al.
   - **Summary**: Demonstrates that consistency models enable zero-shot downscaling of Earth system model outputs with built-in uncertainty quantification capabilities.
   - **Year**: 2024

5. **Title**: ClimateDiffuse
   - **Authors**: Watt & Mansfield
   - **Summary**: Provides unconstrained climate diffusion modeling with probabilistic outputs but without physics constraints.
   - **Year**: 2024

6. **Title**: Conditional Diffusion with Soft Physics
   - **Authors**: Aich et al.
   - **Summary**: Implements soft physics penalties via loss functions in conditional diffusion models, but provides no hard guarantees on physical constraint satisfaction.
   - **Year**: 2024

7. **Title**: Stress-testing hybrid physics-ML climate simulations on unseen warmer climate
   - **Authors**: Lin et al.
   - **Summary**: Demonstrates the out-of-distribution challenge in climate modeling, showing that climate-invariant features help but do not fully solve extreme event generation under novel conditions.
   - **Year**: 2024

**Key Challenges**
1. **Lack of Hard Physics Constraints**: Existing diffusion and flow-based generative models for climate applications either lack physics constraints entirely or implement only soft penalties via loss functions, providing no guarantees on physical consistency.

2. **Out-of-Distribution Generalization**: Hybrid physics-ML climate simulations struggle with unseen warmer climate conditions, and while climate-invariant features provide some improvement, they do not fully address extreme event generation under distribution shift.

3. **Conservation Guarantee Absence**: Current EVT-based approaches for hazard simulation lack conservation guarantees, limiting their physical plausibility for Earth system applications.

4. **Missing Integration Patterns**: Established architectural patterns (e.g., UNet2DConditionModel, diffuser patterns) lack integration mechanisms for hard constraint enforcement in diffusion and flow models.
