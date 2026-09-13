1. **Title**: Dual-Stream Cross-Modal Representation Learning via Residual Semantic Decorrelation (arXiv:2512.07568)
   - **Authors**: Xuecheng Li, Weikuan Jia, Alisher Kurbonaliev, Qurbonaliev Alisher, Khudzhamkulov Rustam, Ismoilov Shuhratjon, Eshmatov Javhariddin, Yuanjie Zheng
   - **Summary**: This paper introduces DSRSD-Net, a framework designed to disentangle modality-specific and modality-shared information through residual decomposition and semantic decorrelation constraints. It addresses issues like modality dominance and redundant information coupling by separating intra-modal (private) and inter-modal (shared) latent factors, aligning shared factors into a common space, and enforcing orthogonality between shared and private streams.
   - **Year**: 2025

2. **Title**: Asymmetric Reinforcing against Multi-modal Representation Bias (arXiv:2501.01240)
   - **Authors**: Xiyuan Gao, Bing Cao, Pengfei Zhu, Nannan Wang, Qinghua Hu
   - **Summary**: The authors propose ARM, a method that dynamically reinforces weaker modalities while preserving the representation capabilities of dominant modalities using conditional mutual information. This approach aims to balance modality contributions and mitigate imbalanced multimodal learning by narrowing the contribution gaps between modalities.
   - **Year**: 2025

3. **Title**: Self-MI: Efficient Multimodal Fusion via Self-Supervised Multi-Task Learning with Auxiliary Mutual Information Maximization (arXiv:2311.03785)
   - **Authors**: Cam-Van Thi Nguyen, Ngoc-Hoa Thi Nguyen, Duc-Trong Le, Quang-Thuy Ha
   - **Summary**: Self-MI introduces a self-supervised learning framework that leverages Contrastive Predictive Coding to maximize mutual information between unimodal inputs and their fusion. It includes a label generation module to create informative labels for each modality, enhancing multimodal fusion by aligning the multimodal fusion with individual modalities.
   - **Year**: 2023

4. **Title**: Multimodal Information Bottleneck: Learning Minimal Sufficient Unimodal and Multimodal Representations (arXiv:2210.17444)
   - **Authors**: Sijie Mai, Ying Zeng, Haifeng Hu
   - **Summary**: This work introduces the Multimodal Information Bottleneck (MIB) framework, aiming to learn minimal sufficient representations by maximizing mutual information between representations and targets while constraining mutual information with input data. MIB regularizes both multimodal and unimodal representations to filter out noisy information and prevent redundancy.
   - **Year**: 2022

5. **Title**: CrossFuse: A Novel Cross Attention Mechanism based Infrared and Visible Image Fusion (arXiv:2406.10581)
   - **Authors**: Hui Li, Xiao-Jun Wu
   - **Summary**: CrossFuse presents a cross attention mechanism designed to enhance complementary information in multimodal image fusion, particularly for infrared and visible images. The method involves a two-stage training strategy with auto-encoder networks and a cross attention module to integrate features from different modalities effectively.
   - **Year**: 2024

6. **Title**: Manifold Integrated Gradients: Riemannian Geometry for Feature Attribution (arXiv:2405.09800)
   - **Authors**: [Authors not specified]
   - **Summary**: This paper introduces Manifold Integrated Gradients (MIG), an approach that applies Riemannian geometry to feature attribution in neural networks. MIG aims to enhance interpretability by considering the data manifold's geometry, providing more reliable and effective gradient-based explanations.
   - **Year**: 2024

7. **Title**: MDPO: Conditional Preference Optimization for Multimodal Large Language Models (arXiv:2406.11839)
   - **Authors**: Fei Wang, Wenxuan Zhou, James Y. Huang, Nan Xu, Sheng Zhang, Hoifung Poon, Muhao Chen
   - **Summary**: MDPO addresses the unconditional preference problem in multimodal preference optimization by introducing a multimodal DPO objective that optimizes image preferences alongside language preferences. It incorporates a reward anchor to ensure positive rewards for chosen responses, improving model performance and reducing hallucinations.
   - **Year**: 2024

8. **Title**: The (Un)Reliability of Saliency Methods (arXiv:1711.00867)
   - **Authors**: [Authors not specified]
   - **Summary**: This study evaluates the reliability of various saliency methods used for interpreting neural network predictions. It highlights the sensitivity of these methods to input transformations and the importance of choosing appropriate reference points for accurate attribution.
   - **Year**: 2024

9. **Title**: Did the Model Understand the Question? (arXiv:1805.05492)
   - **Authors**: [Authors not specified]
   - **Summary**: The paper investigates the effectiveness of question-answering systems by analyzing their reliance on specific question terms. It employs Integrated Gradients to identify influential question words and discusses the implications for model interpretability and robustness.
   - **Year**: 2024

10. **Title**: Multimodal Information Bottleneck: Learning Minimal Sufficient Unimodal and Multimodal Representations (arXiv:2210.17444)
    - **Authors**: Sijie Mai, Ying Zeng, Haifeng Hu
    - **Summary**: This work introduces the Multimodal Information Bottleneck (MIB) framework, aiming to learn minimal sufficient representations by maximizing mutual information between representations and targets while constraining mutual information with input data. MIB regularizes both multimodal and unimodal representations to filter out noisy information and prevent redundancy.
    - **Year**: 2022

**Key Challenges**:

1. **Modality Dominance**: Ensuring balanced contributions from all modalities during training to prevent one modality from overshadowing others.

2. **Redundant Information Coupling**: Effectively disentangling modality-specific and shared information to avoid redundancy and enhance representation quality.

3. **Dynamic Modality Contributions**: Developing methods to adaptively adjust modality weights based on their evolving contributions throughout the training process.

4. **Interpretability of Multimodal Representations**: Creating tools and metrics to visualize and understand the interactions and contributions of different modalities over time.

5. **Robustness to Modality Imbalance**: Designing models that maintain performance and robustness even when certain modalities are noisy, missing, or less informative. 