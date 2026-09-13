## Related Work

**Related Papers**
1. **Title**: Similarity of Neural Network Representations Revisited (arXiv:1905.00414)
   - **Authors**: Kornblith, Norouzi, Lee, Hinton
   - **Summary**: Demonstrates that CKA (Centered Kernel Alignment) reliably identifies correspondences between neural representations and is invariant to orthogonal transformations.
   - **Year**: 2019

2. **Title**: Human-AI coevolution (doi:10.1016/j.artint.2024.104244)
   - **Authors**: Pedreschi, Pappalardo, Ferrara, et al.
   - **Summary**: Establishes that human-AI feedback loops create complex systemic outcomes that require new measurement frameworks to properly assess.
   - **Year**: 2024

3. **Title**: Training a Helpful and Harmless Assistant with RLHF
   - **Authors**: Bai et al. (Anthropic)
   - **Summary**: Establishes the RLHF paradigm demonstrating how AI model updates can be driven by human feedback.
   - **Year**: 2022

4. **Title**: Position: Towards Bidirectional Human-AI Alignment
   - **Authors**: Shen et al.
   - **Summary**: Proposes a theoretical framework for bidirectional human-AI alignment but lacks computational metrics for implementation.
   - **Year**: 2024

5. **Title**: The Human-AI Handshake Framework
   - **Authors**: Pyae
   - **Summary**: Proposes 5 bidirectional attributes for human-AI collaboration but provides no formal operationalization of these concepts.
   - **Year**: 2025

**Key Challenges**
1. **Unidirectional Measurement Limitations**: Existing RLHF metrics (reward model accuracy, preference prediction) only capture one-way information flow and fail to measure bidirectional adaptation dynamics.

2. **Static Assessment Inadequacy**: Current user satisfaction scores provide only static post-interaction ratings without capturing richer temporal information about the evolution of human-AI interactions.

3. **Lack of Computational Metrics for Bidirectional Alignment**: While theoretical frameworks for bidirectional human-AI alignment exist, there are no computational metrics to operationalize these concepts.

4. **Missing Formal Operationalization**: Proposed bidirectional attributes for human-AI collaboration lack formal operationalization, preventing practical implementation and measurement.

5. **Absence of Contrastive Learning Approaches**: No existing work combines contrastive learning methods for developing bidirectional human-AI collaboration metrics.
