## Related Work

**Related Papers**
1. **Title**: Two Roads to Koopman Operator Theory for Control (2025)
   - **Authors**: Haseli, Mezić, Cortés
   - **Summary**: Extends controlled Koopman theory to input-dependent systems, providing theoretical foundations that address selectivity mechanisms in architectures like Mamba.
   - **Year**: 2025

2. **Title**: Representing Neural Network Layers as Linear Operations via Koopman (2024)
   - **Authors**: Aswani, Jabari, Shafique
   - **Summary**: Demonstrates that neural network layers can be replaced with finite-dimensional Koopman operators while maintaining 97% accuracy, establishing practical viability of Koopman-based neural representations.
   - **Year**: 2024

3. **Title**: Mamba: Linear-Time Sequence Modeling with Selective State Spaces (2023)
   - **Authors**: Gu, Dao
   - **Summary**: Introduces selective state space models that achieve state-of-the-art performance with 5x faster inference, demonstrating the importance of spectral structure in sequence modeling.
   - **Year**: 2023

4. **Title**: S4: Efficiently Modeling Long Sequences with Structured State Spaces (2022)
   - **Authors**: Gu, Goel, Re
   - **Summary**: Proposes the HiPPO matrix as a principled spectral initialization approach for capturing long-range dependencies in sequence modeling.
   - **Year**: 2022

5. **Title**: SPectral ARchiteCture Search (SPARCS) (arXiv:2504.00885)
   - **Authors**: Peri, Chicchi, Fanelli, Giambagli
   - **Summary**: Demonstrates that spectral attributes can enable gradient-based neural architecture search.
   - **Year**: 2025

6. **Title**: Benchmarking Spectral Graph Neural Networks (arXiv:2406.09675)
   - **Authors**: Liao et al.
   - **Summary**: Characterizes over 30 spectral GNN filters and provides a unified benchmark framework for evaluating spectral graph neural networks.
   - **Year**: 2024

7. **Title**: HuggingFace Diffusers Library
   - **Authors**: Not specified
   - **Summary**: Implementation library containing multiple diffusion schedulers (DDPM, DDIM, DPM) that coexist without unified theoretical grounding, illustrating the need for principled selection frameworks.
   - **Year**: Not specified

8. **Title**: Flow Matching for Generative Modeling (2022)
   - **Authors**: Lipman et al.
   - **Summary**: Demonstrates that ODE-based unification of generative modeling approaches is viable, achieving partial unification of diffusion-based methods.
   - **Year**: 2022

**Key Challenges**
1. **Lack of Unified Theory for Diffusion Schedulers**: Multiple diffusion schedulers (DDPM, DDIM, DPM) exist in practice without a unified theoretical framework to guide principled selection among them.
2. **Input-Dependent System Modeling**: Extending Koopman operator theory to handle input-dependent and selective mechanisms in modern architectures like Mamba requires additional theoretical development.
3. **Partial Unification in Generative Modeling**: While ODE-based approaches show promise for unifying generative models, current methods achieve only partial unification, leaving gaps in theoretical completeness.
4. **Bridging Spectral Theory and Neural Architectures**: Despite evidence that spectral attributes enable architecture search and neural layers can be represented as Koopman operators, a comprehensive framework connecting these insights remains underdeveloped.
