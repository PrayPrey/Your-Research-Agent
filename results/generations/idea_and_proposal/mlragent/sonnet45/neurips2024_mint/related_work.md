1. **Title**: IMPACT: Importance-Aware Activation Space Reconstruction (arXiv:2507.03828)
   - **Authors**: Md Mokarram Chowdhury, Daniel Agyei Asante, Ernie Chang, Yang Li
   - **Summary**: This paper introduces IMPACT, a framework that focuses on the low-rank structure of activations in large language models (LLMs). By considering both activation structure and gradient sensitivity, IMPACT formulates an optimization problem to derive optimal reconstruction bases, leading to significant model size reduction while preserving accuracy.
   - **Year**: 2025

2. **Title**: FedMS: Federated Learning with Mixture of Sparsely Activated Foundation Models (arXiv:2312.15926)
   - **Authors**: Panlong Wu, Kangshuo Li, Ting Wang, Fangxin Wang
   - **Summary**: FedMS proposes a two-stage federated learning algorithm that constructs a mixture of foundation models with global and local experts. It introduces a Sparsely Activated LoRA (SAL) algorithm, which progressively activates low-rank adaptation matrices during training, enhancing personalization and efficiency in resource-constrained settings.
   - **Year**: 2023

3. **Title**: Probe-Free Low-Rank Activation Intervention (arXiv:2502.04043)
   - **Authors**: Chonghe Jiang, Bao Nguyen, Anthony Man-Cho So, Viet Anh Nguyen
   - **Summary**: This work presents FLORAIN, a probe-free intervention method that applies nonlinear low-rank mappings to all attention heads in a specific activation layer. By minimizing the distance between modified activations and their projection onto the manifold of desirable content, FLORAIN enhances model truthfulness and quality without the need for trained classifiers.
   - **Year**: 2025

4. **Title**: LoRKD: Low-Rank Knowledge Decomposition for Medical Foundation Models (arXiv:2409.19540)
   - **Authors**: Haolin Li, Yuhang Zhou, Ziheng Zhao, Siyuan Du, Jiangchao Yao, Weidi Xie, Ya Zhang, Yanfeng Wang
   - **Summary**: LoRKD introduces a framework that decomposes medical foundation models into multiple lightweight expert models dedicated to specific anatomical regions. By incorporating low-rank expert modules and efficient knowledge separation convolution, LoRKD enhances specialization and reduces resource consumption, achieving state-of-the-art performance in medical tasks.
   - **Year**: 2024

5. **Title**: pyvene: A Library for Understanding and Improving PyTorch Models via Interventions (arXiv:2403.07809)
   - **Authors**: Zhengxuan Wu, Atticus Geiger, Aryaman Arora, Jing Huang, Zheng Wang, Noah D. Goodman, Christopher D. Manning, Christopher Potts
   - **Summary**: pyvene is an open-source Python library that supports customizable interventions on PyTorch models. It facilitates complex intervention schemes with an intuitive configuration format, enabling both static and trainable parameter interventions, thereby aiding in model interpretability and improvement.
   - **Year**: 2024

6. **Title**: AtP∗: An Efficient and Scalable Method for Localizing LLM Behaviour to Components (arXiv:2403.00745)
   - **Authors**: János Kramár, Tom Lieberum, Rohin Shah, Neel Nanda
   - **Summary**: AtP∗ proposes an efficient method for causal attribution in large language models by accelerating the process of activation patching. It addresses failure modes in existing methods and provides a scalable approach to identify and verify the impact of specific model components on behavior.
   - **Year**: 2024

7. **Title**: Interpretability, Then What? Editing Machine Learning Models to Reflect Human Knowledge and Values (arXiv:2206.15465)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This paper discusses GAM Changer, an interactive visualization tool that empowers domain experts and data scientists to interpret and edit machine learning models. It emphasizes aligning model behaviors with human knowledge and values, highlighting the critical role of human agency in responsible AI.
   - **Year**: 2022

8. **Title**: Counteracting Duration Bias in Video Recommendation via Counterfactual Watch Time (arXiv:2406.07932)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This study addresses duration bias in video recommendation systems by introducing counterfactual watch time. It proposes methods to mitigate biases arising from video length, enhancing the fairness and effectiveness of recommendation algorithms.
   - **Year**: 2024

**Key Challenges:**

1. **Contextual Sensitivity of Interventions**: Developing intervention methods that dynamically adapt to varying input contexts remains challenging. Fixed modifications can lead to over-correction or under-correction, affecting model performance and fairness.

2. **Balancing Bias Mitigation and Task Performance**: Ensuring that interventions effectively reduce biases without degrading the model's general capabilities is a delicate balance that requires careful optimization.

3. **Scalability of Intervention Methods**: As models grow in size and complexity, scalable intervention techniques that do not compromise efficiency or effectiveness are essential but difficult to design.

4. **Interpretability of Intervention Decisions**: Providing clear and interpretable insights into why certain interventions are applied in specific contexts is crucial for trust and transparency but remains an open challenge.

5. **Resource Constraints in Deployment**: Implementing adaptive intervention methods in resource-constrained environments, such as edge devices, poses significant challenges in terms of computational and memory efficiency. 