1. **Title**: ALaRM: Align Language Models via Hierarchical Rewards Modeling (arXiv:2403.06754)
   - **Authors**: Yuhang Lai, Siyuan Wang, Shujun Liu, Xuanjing Huang, Zhongyu Wei
   - **Summary**: This paper introduces ALaRM, a framework that models hierarchical rewards in reinforcement learning from human feedback (RLHF) to enhance the alignment of large language models (LLMs) with human preferences. By integrating holistic rewards with aspect-specific rewards, ALaRM addresses inconsistencies and sparsity in human supervision signals, providing more precise guidance for language models, especially in complex text generation tasks.
   - **Year**: 2024

2. **Title**: Energy-Based Reward Models for Robust Language Model Alignment (arXiv:2504.13134)
   - **Authors**: Anamika Lochab, Ruqi Zhang
   - **Summary**: The authors propose Energy-Based Reward Models (EBRM), a post-hoc refinement framework that enhances the robustness and generalization of reward models used in aligning LLMs with human preferences. EBRM explicitly models the reward distribution, capturing uncertainties in human preferences and mitigating the impact of noisy annotations through conflict-aware data filtering and label-noise-aware contrastive training.
   - **Year**: 2025

3. **Title**: Active Preference Optimization for Sample Efficient RLHF (arXiv:2402.10500)
   - **Authors**: Nirjhar Das, Souradip Chakraborty, Aldo Pacchiano, Sayak Ray Chowdhury
   - **Summary**: This work presents Active Preference Optimization (APO), an active-learning algorithm designed to enhance model alignment by querying preference data from the most informative samples. By reformulating RLHF within a contextual preference bandit framework, APO achieves superior performance with a smaller sample budget, addressing the costliness of collecting high-quality human preference data.
   - **Year**: 2024

4. **Title**: Efficient Reinforcement Learning from Human Feedback via Bayesian Preference Inference (arXiv:2511.04286)
   - **Authors**: Matteo Cercola, Valeria Capretti, Simone Formentin
   - **Summary**: The authors propose a hybrid framework that unifies the scalability of RLHF with the query efficiency of Preference-Based Optimization (PBO). By integrating an acquisition-driven module into the RLHF pipeline, the framework enables active and sample-efficient preference gathering, demonstrating consistent improvements in both sample efficiency and overall performance across high-dimensional preference optimization and LLM fine-tuning tasks.
   - **Year**: 2025

5. **Title**: RLAIF: Scaling Reinforcement Learning from Human Feedback
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This paper investigates the effectiveness of combining human feedback and AI feedback in the task of summarization. The approach, referred to as RLHF + RLAIF, is compared against RLHF alone. The study explores various setups, including using RLAIF as a "warm-up" policy refined with RLHF and collecting more AI feedback than human feedback to reduce costs.
   - **Year**: 2024

6. **Title**: Training Language Models to Follow Instructions
   - **Authors**: Long Ouyang, Jeff Wu, Xu Jiang, Diogo Almeida, Carroll L. Wainwright, et al.
   - **Summary**: This work demonstrates that fine-tuning language models with human feedback can align them more closely with user intent. By collecting a dataset of labeler demonstrations and rankings of model outputs, the authors fine-tune GPT-3 using supervised learning and reinforcement learning from human feedback, resulting in InstructGPT models that show improvements in truthfulness and reductions in toxic output generation.
   - **Year**: 2022

7. **Title**: On the Algorithmic Bias of Aligning Large Language Models with RLHF: Preference Collapse and Matching Regularization
   - **Authors**: Jiancong Xiao, Ziniu Li, Xingyu Xie, Emily Getzen, Cong Fang, Qi Long, Weijie J. Su
   - **Summary**: The authors argue that RLHF suffers from inherent algorithmic bias due to its Kullback–Leibler-based regularization, which can lead to preference collapse where minority preferences are disregarded. They introduce preference matching RLHF, a novel approach that aligns LLMs with the preference distribution of the reward model, balancing response diversification and reward maximization.
   - **Year**: 2024

**Key Challenges:**

1. **Variability in Human Feedback Quality**: Human feedback is influenced by factors such as cognitive load, task complexity, and fatigue, leading to noisy and inconsistent data that can mislead alignment algorithms.

2. **Modeling Cognitive Effort**: Accurately estimating the cognitive effort invested by humans in providing feedback is complex, yet crucial for weighting feedback reliability appropriately.

3. **Sample Efficiency**: Collecting high-quality human preference data is costly and time-consuming, necessitating the development of sample-efficient learning paradigms that can achieve robust alignment with limited data.

4. **Algorithmic Bias and Preference Collapse**: Existing alignment methods may introduce biases that lead to the disregard of minority preferences, resulting in a lack of diversity in model outputs.

5. **Scalability of Alignment Methods**: Ensuring that alignment techniques can scale effectively to high-dimensional tasks, such as fine-tuning large language models, without compromising performance or efficiency remains a significant challenge. 