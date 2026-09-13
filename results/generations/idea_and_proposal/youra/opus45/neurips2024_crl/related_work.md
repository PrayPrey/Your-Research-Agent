## Related Work

**Related Papers**
1. **Title**: CausalVAE: Disentangled Representation Learning via Neural Structural Causal Models (arXiv:2004.08697)
   - **Authors**: Yang et al.
   - **Summary**: Introduces a VAE architecture with a causal layer that enables counterfactual generation, providing a foundational approach for integrating structural causal models with variational autoencoders.
   - **Year**: 2020

2. **Title**: Multi-View Causal Representation Learning with Partial Observability
   - **Authors**: Yao et al.
   - **Summary**: Establishes multi-view identifiability through contrastive learning, proving that shared latent representations can be recovered up to bijection under partial observability conditions.
   - **Year**: 2023 (ICLR 2024)

3. **Title**: Multi-View Causal Discovery without Non-Gaussianity (arXiv:2502.20115)
   - **Authors**: Heurtebise et al.
   - **Summary**: Demonstrates that multi-view correlation enables causal discovery without requiring distributional assumptions such as non-Gaussianity, providing theoretical grounding for temporal multi-view approaches.
   - **Year**: 2025

4. **Title**: General Identifiability and Achievability for Causal Representation Learning
   - **Authors**: Varici et al.
   - **Summary**: Proves that identifiability in causal representation learning requires "two hard uncoupled interventions per node," establishing theoretical intervention requirements for the field.
   - **Year**: 2023

5. **Title**: iVAE (Identifiable VAE)
   - **Authors**: Khemakhem et al.
   - **Summary**: Proposes an identifiable variational autoencoder framework that leverages auxiliary variables to achieve identifiability of latent representations.
   - **Year**: 2020

6. **Title**: Towards Unsupervised Causal Representation Learning via Latent Additive Noise Model
   - **Authors**: Ong et al.
   - **Summary**: Proposes using additive noise model bias for unsupervised causal representation learning, though acknowledges the approach does not guarantee unique identifiability.
   - **Year**: 2025

7. **Title**: Developmental Psychology: Infant Causal Learning
   - **Authors**: Basch & Wang
   - **Summary**: Provides evidence from developmental psychology that infants learn causality through observation by detecting temporal contingencies, suggesting temporal observation may substitute for active intervention.
   - **Year**: 2024

**Key Challenges**
1. **Intervention Requirements for Identifiability**: Current theoretical results establish that causal representation learning requires multiple hard interventions per latent node, creating practical barriers for real-world applications where interventions are costly or infeasible.

2. **Lack of Unique Identifiability in Unsupervised Settings**: Existing unsupervised approaches to causal representation learning do not guarantee unique identifiability of latent causal variables, leaving the unsupervised CRL problem fundamentally open.

3. **Distributional Assumptions**: Many causal discovery methods rely on strong distributional assumptions (e.g., non-Gaussianity), limiting their applicability to real-world data that may not satisfy these constraints.

4. **Contrastive vs. Generative Approaches**: Current multi-view methods primarily rely on contrastive learning rather than generative frameworks like VAEs, leaving open questions about alternative architectural approaches for multi-view causal representation learning.
