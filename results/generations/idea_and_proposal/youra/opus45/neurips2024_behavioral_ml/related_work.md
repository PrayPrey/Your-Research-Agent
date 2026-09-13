## Related Work

**Related Papers**
1. **Title**: ACT-R: A Theory of Higher Level Cognition
   - **Authors**: Anderson et al.
   - **Summary**: Defines the foundational ACT-R equations that form the theoretical basis for cognitive architecture implementations.
   - **Year**: 1998

2. **Title**: Neural Turing Machines
   - **Authors**: Graves et al.
   - **Summary**: Introduces differentiable external memory mechanisms for neural networks, providing generic memory capabilities without psychological grounding.
   - **Year**: 2014

3. **Title**: Differentiable Neural Computers
   - **Authors**: Graves et al.
   - **Summary**: Presents scalable differentiable memory systems that extend neural network capabilities, though lacking cognitive constraints.
   - **Year**: 2016

4. **Title**: Hybrid Personalization Using ACT-R
   - **Authors**: Innerebner et al.
   - **Summary**: Integrates ACT-R with machine learning approaches for personalization in recommender systems.
   - **Year**: 2025

5. **Title**: Adaptive Chunking in PFC/BG Circuit
   - **Authors**: Soni & Frank
   - **Summary**: Investigates the neural basis for working memory capacity through prefrontal cortex and basal ganglia circuit modeling, providing computational inspiration for cognitive architectures.
   - **Year**: 2024

6. **Title**: EVC in ACT-R
   - **Authors**: Yang & Stocco
   - **Summary**: Models motivation within the ACT-R framework, informing production selection utility mechanisms.
   - **Year**: 2023

7. **Title**: pyactr
   - **Authors**: Not specified
   - **Summary**: A symbolic (non-differentiable) implementation that uses ACT-R equations with cognitive constraints.
   - **Year**: Not specified

8. **Title**: DNC (Differentiable Neural Computer)
   - **Authors**: Not specified
   - **Summary**: A differentiable system with generic memory mechanisms but without ACT-R equations or cognitive constraints.
   - **Year**: Not specified

9. **Title**: Transformer
   - **Authors**: Not specified
   - **Summary**: A differentiable architecture that lacks both ACT-R-specific equations and cognitive constraints.
   - **Year**: Not specified

**Key Challenges**
1. **Lack of Differentiability in Cognitive Architectures**: Existing symbolic implementations like pyactr implement ACT-R equations but are not differentiable, limiting their integration with modern deep learning approaches.

2. **Absence of Psychological Grounding in Neural Memory Systems**: Differentiable memory systems such as Neural Turing Machines and Differentiable Neural Computers provide generic memory capabilities but lack grounding in established cognitive theories.

3. **Missing Cognitive Constraints in Differentiable Systems**: Current differentiable architectures (DNC, Transformer) do not incorporate cognitive constraints that would make them more aligned with human cognitive processes.

4. **Domain-Specific ACT-R Integration**: Prior work integrating ACT-R with ML (e.g., Innerebner et al.) targets specific applications like recommender systems rather than general-purpose working memory modeling.

5. **Gap in Combined Approach**: No existing system combines differentiability, ACT-R-specific equations, and cognitive constraints simultaneously, creating a need for soft approximations of ACT-R equations as differentiable modules.
