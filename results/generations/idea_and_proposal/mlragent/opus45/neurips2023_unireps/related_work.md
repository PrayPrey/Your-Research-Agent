1. **Title**: AlignMerge - Alignment-Preserving Large Language Model Merging via Fisher-Guided Geometric Constraints (arXiv:2512.16245)
   - **Authors**: Aniruddha Roy, Jyoti Patel, Aman Chadha, Vinija Jain, Amitava Das
   - **Summary**: This paper introduces AlignMerge, a framework for merging large language models while preserving alignment. It employs Fisher-guided geometric constraints to ensure that the merged model maintains safety and performance characteristics of the original models.
   - **Year**: 2025

2. **Title**: MAGIC: Achieving Superior Model Merging via Magnitude Calibration (arXiv:2512.19320)
   - **Authors**: Yayuan Li, Jian Zhang, Jintao Guo, Zihan Cheng, Lei Qi, Yinghuan Shi, Yang Gao
   - **Summary**: MAGIC proposes a magnitude calibration approach to model merging, focusing on aligning both feature direction and magnitude. This method enhances performance across various tasks without additional training.
   - **Year**: 2025

3. **Title**: When Representations Align: Universality in Representation Learning Dynamics (arXiv:2402.09142)
   - **Authors**: Loek van Rossem, Andrew M. Saxe
   - **Summary**: The authors derive an effective theory of representation learning, demonstrating that different neural network architectures develop similar representations under certain conditions, highlighting universal patterns in learning dynamics.
   - **Year**: 2024

4. **Title**: Structure-Preserving Contrastive Learning for Spatial Time Series (arXiv:2502.06380)
   - **Authors**: Yiru Jiao, Sander van Cranenburgh, Simeon Calvert, Hans van Lint
   - **Summary**: This study introduces regularizers in contrastive learning to preserve the topology and geometry of spatial time series data, enhancing the quality of learned representations for downstream tasks.
   - **Year**: 2025

5. **Title**: Examining Learning Dynamics in Deep Neural Networks
   - **Authors**: Not specified
   - **Summary**: The paper investigates how representations in deep neural networks evolve during training, focusing on the impact of label noise and the phenomenon of epoch-wise double descent.
   - **Year**: 2025

6. **Title**: Similarity Learning with Neural Networks
   - **Authors**: D. Naiff
   - **Summary**: This work introduces a neural network algorithm designed to automatically identify similarity relations from data, approximating underlying physical laws that relate dimensionless quantities.
   - **Year**: 2025

7. **Title**: Representation Similarity Reveals Implicit Layer Grouping in Neural Networks
   - **Authors**: Not specified
   - **Summary**: The study explores the use of representation similarity to identify clusters of similar layers within neural networks, revealing potential layer groupings that correspond to functional abstractions.
   - **Year**: 2025

8. **Title**: Decoupling Semantic Similarity from Spatial Alignment for Neural Networks
   - **Authors**: Not specified
   - **Summary**: This paper addresses the challenge of measuring similarity in neural network activations by proposing methods to decouple semantic similarity from spatial alignment, providing a clearer understanding of learned representations.
   - **Year**: 2024

9. **Title**: Invariant Representations Learning with Future Dynamics
   - **Authors**: Not specified
   - **Summary**: The authors present a method for learning invariant representations in reinforcement learning by incorporating future dynamics, aiming to improve sample efficiency and generalization in uncertain environments.
   - **Year**: 2024

10. **Title**: Three Mechanisms of Feature Learning in a Linear Network
    - **Authors**: Yizhou Xu, Liu Ziyin
    - **Summary**: This work provides an exact solution for the learning dynamics of a one-hidden-layer linear network, identifying three novel mechanisms specific to the feature learning regime.
    - **Year**: 2025

**Key Challenges**:

1. **Divergence in Learning Trajectories**: Merging models that have significantly diverged during training poses challenges due to differences in their learning trajectories, leading to potential incompatibilities in representations.

2. **Representation Alignment**: Ensuring that merged models maintain aligned representations is difficult, especially when models have developed distinct feature spaces.

3. **Preserving Model Performance**: Maintaining or enhancing the performance of merged models without additional training is a significant challenge, as merging can introduce performance degradation.

4. **Understanding Learning Dynamics**: Gaining insights into how representations evolve over time in different models is complex, yet crucial for effective model merging strategies.

5. **Identifying Synchronization Points**: Determining optimal points during training where models can be merged without disrupting their learning processes requires a deep understanding of representation trajectories. 