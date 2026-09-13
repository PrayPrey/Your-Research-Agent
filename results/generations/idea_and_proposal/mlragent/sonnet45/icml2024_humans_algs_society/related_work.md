1. **Title**: Dual-Weighted Reinforcement Learning for Generative Preference Modeling (arXiv:2510.15242)
   - **Authors**: Shengyu Feng, Yun He, Shuang Ma, Beibin Li, Yuanhao Xiong, Vincent Li, Karishma Mandyam, Julian Katz-Samuels, Shengjie Bi, Licheng Yu, Hejia Zhang, Karthik Abinav Sankararaman, Han Fang, Riham Mansour, Yiming Yang, Manaal Faruqui
   - **Summary**: This paper introduces Dual-Weighted Reinforcement Learning (DWRL), a framework that integrates chain-of-thought reasoning with the Bradley-Terry model through a dual-weighted RL objective. DWRL emphasizes under-trained pairs misaligned with human preferences and promotes promising thoughts, enhancing preference modeling beyond verifiable tasks.
   - **Year**: 2025

2. **Title**: Learning Pareto-Optimal Rewards from Noisy Preferences: A Framework for Multi-Objective Inverse Reinforcement Learning (arXiv:2505.11864)
   - **Authors**: Kalyan Cherukuri, Aarav Lala
   - **Summary**: This work presents a theoretical framework for preference-based Multi-Objective Inverse Reinforcement Learning (MO-IRL), modeling human preferences as latent vector-valued reward functions. It establishes conditions for identifying multi-objective structures and introduces a provably convergent algorithm for policy optimization using preference-inferred reward cones.
   - **Year**: 2025

3. **Title**: Inverse-Q*: Token Level Reinforcement Learning for Aligning Large Language Models Without Preference Data (arXiv:2408.14874)
   - **Authors**: Han Xia, Songyang Gao, Qiming Ge, Zhiheng Xi, Qi Zhang, Xuanjing Huang
   - **Summary**: Inverse-Q* is a framework that optimizes token-level reinforcement learning without additional reward or value models. It estimates the conditionally optimal policy directly from model responses, reducing reliance on human annotation and external supervision, making it suitable for low-resource settings.
   - **Year**: 2024

4. **Title**: Inverse Preference Learning: Preference-based RL without a Reward Function (arXiv:2305.15363)
   - **Authors**: Joey Hejna, Dorsa Sadigh
   - **Summary**: This paper introduces Inverse Preference Learning (IPL), an algorithm designed for learning from offline preference data without a learned reward function. IPL leverages the insight that for a fixed policy, the Q-function encodes all information about the reward function, simplifying the learning process.
   - **Year**: 2023

5. **Title**: RRHF: Rank Responses to Align Language Models with Human Feedback without tears (arXiv:2304.05302)
   - **Authors**: Zheng Yuan, Hongyi Yuan, Chuanqi Tan, Wei Wang, Songfang Huang, Fei Huang
   - **Summary**: RRHF proposes a learning paradigm that scores sampled responses via logarithm of conditional probabilities and aligns these probabilities with human preferences through ranking loss. It efficiently aligns language models with human preferences without complex hyperparameter tuning.
   - **Year**: 2023

6. **Title**: A General Theoretical Paradigm to Understand Learning from Human Preferences (arXiv:2310.12036)
   - **Authors**: Mohammad Gheshlaghi Azar, Mark Rowland, Bilal Piot, Daniel Guo, Daniele Calandriello, Michal Valko, Rémi Munos
   - **Summary**: This paper derives a new general objective called ΨPO for learning from human preferences, expressed in terms of pairwise preferences. It provides an in-depth analysis of RLHF and DPO, identifying potential pitfalls and proposing an efficient optimization procedure with performance guarantees.
   - **Year**: 2023

7. **Title**: From Demonstrations to Rewards: Alignment Without Explicit Human Preferences (arXiv:2503.13538)
   - **Authors**: Siliang Zeng, Yao Liu, Huzefa Rangwala, George Karypis, Mingyi Hong, Rasool Fakoor
   - **Summary**: This work proposes a perspective on learning alignment based on inverse reinforcement learning principles, directly learning the reward model from demonstration data without relying on large preference datasets.
   - **Year**: 2025

8. **Title**: Strategic manipulation of preferences in the rank minimization mechanism
   - **Authors**: [Not specified]
   - **Summary**: This study examines one-sided matching problems where agents are allocated items based on stated preferences. It explores how agents can strategically manipulate their preferences to achieve desired outcomes under the rank minimization mechanism.
   - **Year**: 2024

9. **Title**: Offline reward shaping with scaling human preference feedback for deep reinforcement learning
   - **Authors**: [Not specified]
   - **Summary**: This paper addresses the challenge of designing reward functions that align with human intent by proposing a framework that scales human preference feedback for deep reinforcement learning, enhancing the alignment of learned policies with human preferences.
   - **Year**: 2025

10. **Title**: Strategic Behavior in Two-sided Matching Markets with Prediction-enhanced Preference-formation
    - **Authors**: Stefania Ionescu, Yuhao Du, Kenneth Joseph, Ancsa Hannak
    - **Summary**: This work introduces the concept of adversarial interaction attacks in two-sided matching markets, where agents can manipulate future predictions by interacting non-optimally in the short term, highlighting the need to consider strategic behavior in preference formation.
    - **Year**: 2023

**Key Challenges**:

1. **Modeling Strategic Behavior**: Accurately capturing and predicting strategic user behavior in preference elicitation remains complex, as users may misreport preferences to influence outcomes.

2. **Disentangling True Preferences from Strategic Distortions**: Separating genuine user preferences from strategic manipulations is challenging, requiring sophisticated models and algorithms.

3. **Convergence to Truthful Preference Revelation**: Ensuring that algorithms converge to truthful preference revelation despite strategic behavior involves intricate mechanism design and theoretical guarantees.

4. **Scalability and Efficiency**: Developing scalable and efficient algorithms that can handle large-scale data while accounting for strategic behavior is a significant challenge.

5. **Empirical Validation**: Demonstrating the effectiveness of proposed frameworks in real-world applications, such as recommendation systems, requires extensive empirical validation and user studies. 