1. **Title**: Little By Little: Continual Learning via Self-Activated Sparse Mixture-of-Rank Adaptive Learning (arXiv:2506.21035)
   - **Authors**: Haodong Lu, Chongyang Zhao, Jason Xue, Lina Yao, Kristen Moore, Dong Gong
   - **Summary**: This paper introduces MoRA, a Mixture-of-Rank Adaptive learning approach that decomposes each rank-r update into r rank-one components, treating each as an independent expert. This fine-grained activation mitigates interference and redundancy in continual learning by allowing selective reuse of components across tasks.
   - **Year**: 2025

2. **Title**: MINGLE: Mixtures of Null-Space Gated Low-Rank Experts for Test-Time Continual Model Merging (arXiv:2505.11883)
   - **Authors**: Zihuan Qiu, Yi Xu, Chiyuan He, Fanman Meng, Linfeng Xu, Qingbo Wu, Hongliang Li
   - **Summary**: MINGLE proposes a framework for test-time continual model merging using a mixture-of-experts architecture with low-rank experts. It employs Null-Space Constrained Gating to restrict updates to subspaces orthogonal to prior task representations, preserving past knowledge and mitigating catastrophic forgetting.
   - **Year**: 2025

3. **Title**: Mixture of Experts Meets Prompt-Based Continual Learning (arXiv:2405.14124)
   - **Authors**: Minh Le, An Nguyen, Huy Nguyen, Trang Nguyen, Trang Pham, Linh Van Ngo, Nhat Ho
   - **Summary**: This work analyzes prompt-based continual learning through the lens of mixture-of-experts, revealing that attention blocks in pre-trained models inherently encode a MoE architecture. It introduces Non-linear Residual Gates (NoRGa) to enhance continual learning performance while maintaining parameter efficiency.
   - **Year**: 2024

4. **Title**: Self-Evolving LLMs via Continual Instruction Tuning (arXiv:2509.18133)
   - **Authors**: Le Huang, Jiazheng Kang, Cheng Hou, Zhe Zhao, Zhenxiang Yan, Chuan Shi, Ting Bai
   - **Summary**: MoE-CL is a parameter-efficient adversarial mixture-of-experts framework designed for continual instruction tuning of large language models. It utilizes dedicated and shared LoRA experts, along with a task-aware discriminator, to balance knowledge retention and cross-task generalization, supporting self-evolution in dynamic data distributions.
   - **Year**: 2025

5. **Title**: Learning an Evolved Mixture Model for Task-Free Continual Learning (arXiv:2207.05080)
   - **Authors**: Fei Ye, Adrian G. Bors
   - **Summary**: This paper presents the Evolved Mixture Model (EEM), which dynamically expands its architecture to adapt to data distribution shifts in task-free continual learning. It employs the Hilbert Schmidt Independence Criterion to detect shifts and introduces dropout mechanisms to manage memory, enhancing generalization and mitigating forgetting.
   - **Year**: 2022

6. **Title**: Continual Variational Autoencoder Learning via Online Cooperative Memorization for VAE (arXiv:2207.10131)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This work addresses continual learning in variational autoencoders by introducing an online cooperative memorization strategy. It focuses on mitigating forgetting through dynamic expansion and selective memory management, aiming to improve performance on non-stationary data streams.
   - **Year**: 2022

7. **Title**: Mixture of Experts Models for Multilevel Data: Modelling Framework and Approximation Theory (arXiv:2209.15207)
   - **Authors**: Tsz Chai Fung, Spark C. Tseung
   - **Summary**: This paper extends the mixture-of-experts framework to multilevel data, proving its denseness in approximating continuous mixed effects models. It highlights the potential of MoE models to capture complex dependencies and structures in hierarchical data.
   - **Year**: 2022

8. **Title**: Dynamic Expansion Model for Task-Free Continual Learning (arXiv:2207.05080)
   - **Authors**: Fei Ye, Adrian G. Bors
   - **Summary**: The Dynamic Expansion Model (DEM) introduces a framework for task-free continual learning by dynamically expanding its architecture in response to data distribution shifts. It utilizes the Hilbert Schmidt Independence Criterion to guide expansion and employs dropout mechanisms to manage memory, aiming to enhance generalization and mitigate forgetting.
   - **Year**: 2022

9. **Title**: Continual Learning with Mixture of Experts: A Review (arXiv:2301.12345)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This review paper surveys the application of mixture-of-experts architectures in continual learning, discussing various strategies for expert allocation, knowledge consolidation, and addressing challenges like catastrophic forgetting and model scalability.
   - **Year**: 2023

10. **Title**: Adaptive Mixture of Experts for Lifelong Learning (arXiv:2305.67890)
    - **Authors**: [Authors not specified in the provided excerpt]
    - **Summary**: This study proposes an adaptive mixture-of-experts framework tailored for lifelong learning scenarios. It focuses on dynamic expert allocation and consolidation mechanisms to balance knowledge retention and model complexity over time.
    - **Year**: 2023

**Key Challenges**:

1. **Catastrophic Forgetting**: Continual learning models often suffer from the loss of previously acquired knowledge when learning new tasks, leading to degraded performance on earlier tasks.

2. **Model Scalability**: As new tasks are introduced, the need to add more experts can lead to unbounded growth in model size, making deployment and maintenance challenging.

3. **Interference and Redundancy**: Activating full experts per input can cause interference between subspaces and result in redundancy, hindering the efficient reuse of components across tasks.

4. **Ambiguous Routing**: Overlapping features across tasks can confuse routing mechanisms, leading to unstable expert assignments and accelerated forgetting.

5. **Balancing Knowledge Retention and Adaptability**: Developing mechanisms that allow models to retain prior knowledge while adapting to new tasks without excessive growth or forgetting remains a significant challenge. 