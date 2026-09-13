1. **Title**: FedShield-LLM: A Secure and Scalable Federated Fine-Tuned Large Language Model (arXiv:2506.05640)
   - **Authors**: Md Jueal Mia, M. Hadi Amini
   - **Summary**: This paper introduces FedShield-LLM, a federated learning framework that fine-tunes large language models (LLMs) across decentralized organizations while preserving data privacy. It employs pruning with Fully Homomorphic Encryption (FHE) for Low-Rank Adaptation (LoRA) parameters, enabling secure computations on encrypted model updates and reducing the attack surface by deactivating less important LoRA parameters. The approach enhances scalability and efficiency, making federated learning feasible for resource-constrained clients. Experimental results demonstrate superior performance and robust privacy protection compared to existing methods.
   - **Year**: 2025

2. **Title**: Privacy Enhanced PEFT: Tensor Train Decomposition Improves Privacy Utility Tradeoffs under DP-SGD (arXiv:2601.10045)
   - **Authors**: Pradip Kunwar, Minh Vu, Maanak Gupta, Manish Bhattarai
   - **Summary**: The authors propose TTLoRA-DP, a differentially private training framework that integrates Tensor Train Low-Rank Adaptation (TTLoRA) with Differentially Private Stochastic Gradient Descent (DP-SGD). By constraining the parameter space through tensor train decomposition, TTLoRA-DP achieves improved privacy-utility tradeoffs in fine-tuning LLMs. Experiments on GPT-2 fine-tuning over the Enron and Penn Treebank datasets show that TTLoRA-DP consistently strengthens privacy protection while maintaining comparable or better downstream utility.
   - **Year**: 2026

3. **Title**: FedMentor: Domain-Aware Differential Privacy for Heterogeneous Federated LLMs in Mental Health (arXiv:2509.14275)
   - **Authors**: Nobin Sarwar, Shubhashis Roy Dipta
   - **Summary**: FedMentor is a federated fine-tuning framework that combines Low-Rank Adaptation (LoRA) with domain-aware Differential Privacy (DP) to fine-tune LLMs in sensitive domains like mental health. Each client applies a custom DP noise scale proportional to its data sensitivity, and the server adaptively reduces noise when utility falls below a threshold. Experiments on mental health datasets demonstrate improved safety and utility, maintaining performance close to non-private baselines while enhancing privacy protection.
   - **Year**: 2025

4. **Title**: Parameter-Efficient Fine-Tuning with Differential Privacy for Robust Instruction Adaptation in Large Language Models (arXiv:2512.06711)
   - **Authors**: Yulin Huang, Yaxuan Luan, Jinxu Guo, Xiangchen Song, Yuchen Liu
   - **Summary**: This study presents a parameter-efficient method that integrates differential privacy noise allocation with gradient clipping in a collaborative optimization framework for instruction fine-tuning of LLMs. By keeping the backbone model frozen and updating parameters through a low-dimensional projection subspace, the method reduces privacy budget consumption and ensures training stability. Experiments show superior accuracy, privacy budget efficiency, and parameter efficiency compared to baseline models.
   - **Year**: 2025

5. **Title**: Flocks of Stochastic Parrots: Differentially Private Prompt Learning for Large Language Models (arXiv:2305.15594)
   - **Authors**: Haonan Duan, Adam Dziedzic, Nicolas Papernot, Franziska Boenisch
   - **Summary**: The authors address privacy concerns in prompt-based learning by introducing differentially private prompt learning methods for LLMs. They demonstrate effective membership inference attacks against prompts and propose private algorithms that closely match non-private baselines, achieving high downstream accuracy with strong privacy guarantees.
   - **Year**: 2023

6. **Title**: Mimicking User Data: On Mitigating Fine-Tuning Risks in Closed Large Language Models (arXiv:2406.10288)
   - **Authors**: Francisco Eiras, Aleksandar Petrov, Philip H.S. Torr, M. Pawan Kumar, Adel Bibi
   - **Summary**: This paper explores the risks associated with fine-tuning LLMs on small, high-quality datasets, which can inadvertently undo safety alignment and increase compliance with harmful queries. The authors propose a mitigation strategy that mixes in safety data mimicking the task format and prompting style of user data, effectively re-establishing safety alignment while maintaining task performance.
   - **Year**: 2024

7. **Title**: On the Algorithmic Bias of Aligning Large Language Models with Human Preferences (arXiv:2405.16455)
   - **Authors**: [Authors not specified]
   - **Summary**: The paper investigates the algorithmic biases introduced when aligning LLMs with human preferences. It discusses the impact of preference matching regularization and the potential for preference collapse in reinforcement learning from human feedback (RLHF). The authors propose methods to mitigate these biases, enhancing the fairness and robustness of LLMs.
   - **Year**: 2024

8. **Title**: Offset Unlearning for Large Language Models (arXiv:2404.11045)
   - **Authors**: [Authors not specified]
   - **Summary**: This work introduces δ-Unlearning, a method for unlearning specific data from LLMs without requiring access to the original training data. By introducing offset models to facilitate adaptation, δ-Unlearning addresses privacy concerns and enables compliance with data protection regulations like GDPR.
   - **Year**: 2024

**Key Challenges**:

1. **Utility-Privacy Tradeoff**: Achieving a balance between maintaining model performance and ensuring strong privacy guarantees remains a significant challenge.

2. **Scalability and Efficiency**: Implementing privacy-preserving techniques in LLM fine-tuning often introduces computational overhead, making scalability and efficiency critical concerns.

3. **Adaptive Noise Calibration**: Developing effective strategies for adaptive noise injection that account for gradient sensitivity and allocate privacy budgets efficiently across model components is complex.

4. **Robustness to Attacks**: Ensuring that privacy-preserving methods are robust against various inference attacks, such as membership inference and gradient inversion, is essential for protecting sensitive data.

5. **Compliance with Regulations**: Aligning privacy-preserving fine-tuning methods with legal frameworks like GDPR requires careful consideration of data protection requirements and the ability to unlearn specific data upon request. 