## Related Work

**Related Papers**

1. **Title**: Chen et al. (2024) - Large-Scale Materials Screening
   - **Authors**: Not specified
   - **Summary**: Demonstrated 500K materials screening using ML property prediction. Identified the critical limitation that "Predicted materials often cannot be synthesized."
   - **Year**: 2024

2. **Title**: Pyzer-Knapp et al. (2025) - Foundation Models Review
   - **Authors**: Not specified
   - **Summary**: Comprehensive review of materials foundation model landscape, identifying synthesis integration as "critical future direction" and discussing models like MACE, MatterSim, and CHGNet.
   - **Year**: 2025

3. **Title**: Wang et al. (2025) - High-Pressure Materials Discovery
   - **Authors**: Not specified
   - **Summary**: ML for predicting high-pressure phase stability, showing that individual synthesis parameters (pressure) can be modeled, but limited to pressure alone without full synthesis pathway modeling.
   - **Year**: 2025

4. **Title**: Xin et al. (2025) - Synthesizability Filter
   - **Authors**: Not specified
   - **Summary**: Binary classification (synthesizable yes/no) from structure with ~70% precision in filtering. Provides post-processing filtering but is non-differentiable and cannot optimize synthesis parameters.
   - **Year**: 2025

5. **Title**: Kononova et al. (2019) - Text-Mined Synthesis Recipes
   - **Authors**: Not specified
   - **Summary**: Extracted 19K synthesis recipes from 53K papers using NLP, providing critical training data for synthesis pathway modeling.
   - **Year**: 2019

6. **Title**: Chen et al. (2018) - Neural Ordinary Differential Equations
   - **Authors**: Not specified
   - **Summary**: Introduced continuous-depth neural networks with adjoint method for backpropagation (NeurIPS 2018 Best Paper), providing foundational methodology for neural SDEs.
   - **Year**: 2018

7. **Title**: Li et al. (2020) - Neural SDEs as Infinite-Dimensional GANs
   - **Authors**: Not specified
   - **Summary**: Extended Neural ODEs to stochastic differential equations with learned drift and diffusion functions, providing technical foundation for modeling synthesis stochasticity.
   - **Year**: 2020

8. **Title**: Kidger et al. (2021) - Neural SDEs: Theory and Applications
   - **Authors**: Not specified
   - **Summary**: Comprehensive framework for neural SDEs with torchsde library implementation, demonstrating that adjoint sensitivity method works for SDEs with careful handling of noise.
   - **Year**: 2021

9. **Title**: Batzner et al. (2022) - NequIP (E(3)-Equivariant GNNs)
   - **Authors**: Not specified
   - **Summary**: Rotation/translation equivariant message passing achieving state-of-art on MD simulation and property prediction, providing architecture for equivariant SDE dynamics.
   - **Year**: 2022

10. **Title**: Batatia et al. (2022) - MACE
    - **Authors**: Not specified
    - **Summary**: Higher-order equivariant architecture, current SOTA materials foundation model for structure-property prediction with integration point for synthesis pathway modeling.
    - **Year**: 2022

11. **Title**: Schütt et al. (2021) - Equivariant Message Passing for Molecules (SchNet)
    - **Authors**: Not specified
    - **Summary**: Continuous-filter convolutions for molecules, providing alternative equivariant architecture for molecular and materials modeling.
    - **Year**: 2021

12. **Title**: Merchant et al. (2023) - Transfer Learning for Materials Property Prediction
    - **Authors**: Not specified
    - **Summary**: Demonstrates pre-training on large dataset → fine-tune on small dataset achieving 10-20% improvement with 10x less data, validating three-stage transfer learning strategy.
    - **Year**: 2023

13. **Title**: FlowMM (Facebook Research) - Riemannian Flow Matching
    - **Authors**: Not specified
    - **Summary**: Generative model for crystal structures using flow-based generation on materials manifold, but generates structures without synthesis pathway modeling.
    - **Year**: Not specified

14. **Title**: Crystal Diffusion VAE (Meta AI)
    - **Authors**: Not specified
    - **Summary**: VAE for crystal structure generation with physical constraints, but ignores synthesis and focuses on structure generation only.
    - **Year**: Not specified

**Key Challenges**

1. **Synthesis-Property Gap**: Computationally "optimal" materials (40-60% according to Xin et al. 2025) often cannot be synthesized, with predicted structures being thermodynamically stable but kinetically inaccessible.

2. **Theory-Experiment Disconnect**: Synthesis conditions strongly affect final properties (defects, grain boundaries, phase purity), but current models assume perfect structures and ignore synthesis-induced variations.

3. **Post-Processing Limitations**: Existing synthesizability filters are binary (yes/no), non-differentiable, and provide no pathway information or ability to optimize synthesis parameters.

4. **Lack of Temporal Modeling**: Prior work treats synthesis as static decisions rather than modeling time-dependent evolution of synthesis pathways.

5. **Data Insufficiency**: Text-mined synthesis data may have high noise (parsing errors, incomplete information) and many synthesis papers report final phase but not grain size or defects.

6. **Non-Differentiable Optimization**: Sequential design workflows (design structure → plan synthesis) lack feedback loops and cannot backpropagate property gradients to synthesis parameters.

7. **Domain Shift**: Published syntheses may differ from real lab practices due to publication bias toward successful, optimized syntheses.

8. **Missing Cross-Domain Transfer**: Neural ODE/SDE techniques proven in chemical engineering and machine learning have not been applied to materials synthesis pathway modeling.

9. **Coarse-Graining Challenge**: Balancing the need to capture critical atomic-scale defect information while maintaining computational tractability with coarse-grained state representations.

10. **Training Instability**: Neural SDEs can suffer from vanishing/exploding gradients and solver divergence, requiring careful architecture design and hyperparameter tuning.
