## Related Work

**Related Papers**
1. **Title**: In Search of Dispersed Memories: Generative Diffusion Models Are Associative Memory Networks
   - **Authors**: Ambrogioni
   - **Summary**: Establishes that diffusion energy is equivalent to Hopfield energy asymptotically, providing the theoretical foundation for treating diffusion models as attractor systems.
   - **Year**: 2023

2. **Title**: Memorization to Generalization: Emergence of Diffusion Models from Associative Memory
   - **Authors**: Pham et al.
   - **Summary**: Demonstrates that phase transitions exist between memorization and generalization regimes in diffusion models, with spurious states occurring at the boundary between these phases.
   - **Year**: 2025

3. **Title**: Associative Memory and Generative Diffusion in the Zero-noise Limit
   - **Authors**: Hess & Morris
   - **Summary**: Applies bifurcation theory to characterize transitions in diffusion models and establishes Morse-Smale systems as universal approximators for these dynamics.
   - **Year**: 2025

4. **Title**: Denoising Diffusion Probabilistic Models (Standard DDPM)
   - **Authors**: Ho et al.
   - **Summary**: Introduces the foundational DDPM framework with standard noise schedules, serving as the baseline for noise scheduling without modulation parameters.
   - **Year**: 2020

5. **Title**: Classifier-Free Guidance
   - **Authors**: Not specified
   - **Summary**: Provides an alternative inference-time control mechanism for diffusion models that controls semantic alignment rather than the memory-generation trade-off.
   - **Year**: Not specified

6. **Title**: Memristor Synapse-Driven Simplified Hopfield Neural Network: Hidden Dynamics, Attractor Control
   - **Authors**: Chen, Min, Cai, Bao
   - **Summary**: Demonstrates that amplitude and offset control can shift attractor basins without retraining in Hopfield networks, providing cross-domain inspiration for using noise variance as a control variable.
   - **Year**: 2024

**Key Challenges**
1. **Lack of Inference-Time Control for Memory-Generation Trade-off**: Existing methods like classifier-free guidance control semantic alignment but do not provide mechanisms to navigate between memorization and generalization during inference.

2. **Understanding Phase Transitions**: While phase transitions between memorization and generalization have been identified, practical methods to control and exploit these transitions remain underdeveloped.

3. **Spurious States at Phase Boundaries**: The existence of spurious states at the boundary between memorization and generalization regimes presents challenges for reliable generation quality.

4. **Cross-Domain Transfer of Control Mechanisms**: Insights from hardware implementations (memristor-based Hopfield networks) showing attractor control without retraining have not been systematically applied to diffusion model frameworks.
