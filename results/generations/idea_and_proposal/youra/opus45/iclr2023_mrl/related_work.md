## Related Work

**Related Papers**
1. **Title**: Investigating Modality Contribution in Audio LLMs for Music (arXiv:2509.20641)
   - **Authors**: Morais, G., Fuentes, M.
   - **Summary**: Proposes the MM-SHAP framework to quantify modality contribution in Audio LLMs using Shapley values, validating ablation-based approaches for understanding multimodal systems.
   - **Year**: 2025

2. **Title**: Feature Importance: A Closer Look at Shapley Values and LOCO (arXiv:2303.05981)
   - **Authors**: Verdinelli, I., Wasserman, L.
   - **Summary**: Provides a critical analysis of Shapley axioms and identifies correlation as a key limitation, motivating the need for PID extension in methods like E-ITSD.
   - **Year**: 2023

3. **Title**: MultiSHAP: A Shapley-Based Framework for Explaining Cross-Modal Interactions (arXiv:2508.00576)
   - **Authors**: Wang, Z., Wang, K.
   - **Summary**: Employs Shapley Interaction Index for cross-modal explanation, demonstrating both instance-level and dataset-level explanations for multimodal models.
   - **Year**: 2025

4. **Title**: SHAPE: An Unified Approach to Evaluate Contribution and Cooperation of Individual Modalities
   - **Authors**: Hu, P., Li, X., Zhou, Y.
   - **Summary**: Introduces Shapley value-based perceptual scores to measure both modality contribution and cooperation, serving as a direct methodological precedent for multimodal analysis.
   - **Year**: 2022

5. **Title**: MultiBench: Multiscale Benchmarks for Multimodal Representation Learning
   - **Authors**: Liang, P., et al.
   - **Summary**: Provides a standardized evaluation framework for multimodal learning across 15 datasets and 10 modalities, enabling systematic comparison of methods.
   - **Year**: 2021

6. **Title**: Recursive Joint Cross-Modal Attention for Multimodal Fusion
   - **Authors**: Praveen, R.G., et al.
   - **Summary**: Achieves state-of-the-art performance in cross-attention fusion, representing a target architecture for E-ITSD analysis.
   - **Year**: 2024

7. **Title**: Multimodal Representation Learning by Alternating Unimodal Adaptation
   - **Authors**: Zhang, X., et al.
   - **Summary**: Documents the modality dominance problem in multimodal learning, highlighting the need for diagnostic capabilities that E-ITSD aims to provide.
   - **Year**: 2023

**Key Challenges**
1. **Correlation Limitations in Shapley Values**: Standard Shapley value approaches face limitations when dealing with correlated features across modalities, requiring extensions such as PID to properly account for shared information.

2. **Modality Dominance Problem**: Multimodal models often exhibit dominance by one modality over others, creating imbalanced learning dynamics that require diagnostic tools to identify and address.

3. **Quantifying Cross-Modal Interactions**: Existing methods struggle to adequately explain and quantify the interactions between different modalities, necessitating frameworks that can capture both individual contributions and cooperative effects.

4. **Lack of Unified Evaluation**: The field lacks standardized approaches for evaluating both the contribution and cooperation of individual modalities within multimodal systems.
