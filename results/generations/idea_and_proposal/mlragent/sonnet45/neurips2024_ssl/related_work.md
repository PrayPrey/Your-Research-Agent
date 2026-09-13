1. **Title**: Self-MI: Efficient Multimodal Fusion via Self-Supervised Multi-Task Learning with Auxiliary Mutual Information Maximization (arXiv:2311.03785)
   - **Authors**: Cam-Van Thi Nguyen, Ngoc-Hoa Thi Nguyen, Duc-Trong Le, Quang-Thuy Ha
   - **Summary**: This paper introduces Self-MI, a self-supervised learning framework that employs Contrastive Predictive Coding (CPC) to maximize mutual information between unimodal inputs and their multimodal fusion. The approach includes a label generation module, ULG_MI, to create informative labels in a self-supervised manner, enhancing multimodal fusion performance.
   - **Year**: 2023

2. **Title**: Selecting Task with Optimal Transport Self-Supervised Learning for Few-Shot Classification (arXiv:2204.00289)
   - **Authors**: Renjie Xu, Xinghao Yang, Baodi Liu, Kai Zhang, Weifeng Liu
   - **Summary**: The authors propose Optimal Transport Task Selecting (OTTS), an algorithm that selects auxiliary tasks for few-shot learning by measuring task similarity through optimal transport distance. OTTS aims to reduce the distribution gap between auxiliary and target tasks, leading to more stable and effective few-shot learning.
   - **Year**: 2022

3. **Title**: Self-Supervised Auxiliary Learning for Graph Neural Networks via Meta-Learning (arXiv:2103.00771)
   - **Authors**: Dasol Hwang, Jinyoung Park, Sunyoung Kwon, Kyung-Min Kim, Jung-Woo Ha, Hyunwoo J. Kim
   - **Summary**: This study presents a self-supervised auxiliary learning framework for graph neural networks, utilizing meta-learning to identify effective combinations of auxiliary tasks. The approach aims to improve generalization performance in node classification and link prediction tasks.
   - **Year**: 2021

4. **Title**: Predictive and Contrastive: Dual-Auxiliary Learning for Recommendation (arXiv:2203.03982)
   - **Authors**: Yinghui Tao, Min Gao, Junliang Yu, Zongwei Wang, Qingyu Xiong, Xu Wang
   - **Summary**: The paper introduces DUAL, a framework that integrates predictive and contrastive auxiliary tasks to enhance recommendation systems. By leveraging self-supervised signals from positive correlations in heterogeneous interaction data, DUAL improves recommendation performance.
   - **Year**: 2022

5. **Title**: Meta-SGD: Learning to Learn Quickly (arXiv:1707.09835)
   - **Authors**: Zhenguo Li, Fengwei Zhou, Fei Chen, Hang Li
   - **Summary**: Meta-SGD is a meta-learning algorithm that learns to initialize and adapt any differentiable learner efficiently. It extends the capabilities of MAML by learning not only the initialization but also the update direction and learning rate, facilitating rapid adaptation in few-shot learning scenarios.
   - **Year**: 2017

6. **Title**: Partly Supervised Multitask Learning (arXiv:2005.02523)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This work addresses the challenge of learning multiple tasks with varying levels of supervision. It introduces a framework that combines supervised and self-supervised learning to improve performance across tasks, particularly when labeled data is scarce.
   - **Year**: 2020

7. **Title**: Continual Variational Autoencoder Learning via Online Cooperative Memorization (arXiv:2207.10131)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: The authors propose an online cooperative memorization approach for continual learning with variational autoencoders. The method aims to mitigate catastrophic forgetting by maintaining a diverse memory without requiring task labels, facilitating unsupervised learning in dynamic environments.
   - **Year**: 2022

8. **Title**: Delving into Identify-Emphasize Paradigm for Debiasing in Self-Supervised Learning (arXiv:2302.11414)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This paper investigates the use of self-supervised learning techniques, such as dense contrastive learning and rotation prediction tasks, to debias models. By incorporating these pretext tasks, the approach aims to learn richer representations and alleviate biases in the learned models.
   - **Year**: 2023

9. **Title**: Task-Free Continual Learning via Online Discrepancy Distance Learning (arXiv:2210.06579)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: The study introduces Online Discrepancy Distance Learning (ODDL), a method for task-free continual learning that detects data distribution shifts and dynamically expands the model. ODDL aims to balance model generalization and complexity without requiring task labels.
   - **Year**: 2022

10. **Title**: Accepted by IEEE Transactions on Pattern Analysis and Machine Intelligence (arXiv:2201.08071)
    - **Authors**: [Authors not specified in the provided excerpt]
    - **Summary**: This paper addresses weakly-supervised temporal sentence grounding in videos. It explores methods that do not require precise temporal annotations, focusing on multi-instance learning and reconstruction-based models to improve video-query alignment.
    - **Year**: 2022

**Key Challenges:**

1. **Task Selection Criteria**: Determining principled methods for selecting auxiliary tasks that effectively enhance downstream performance remains an open challenge.

2. **Mutual Information Estimation**: Accurately estimating mutual information between representations and task-relevant features is complex, especially in high-dimensional spaces.

3. **Sample Complexity**: Establishing theoretical bounds that connect auxiliary task choices to sample efficiency and downstream performance is still underdeveloped.

4. **Computational Efficiency**: Developing practical algorithms for auxiliary task selection that reduce computational costs without extensive trial-and-error is challenging.

5. **Generalization Across Domains**: Ensuring that the theoretical frameworks and practical methods for auxiliary task selection generalize well across different domains and data modalities is a significant hurdle. 