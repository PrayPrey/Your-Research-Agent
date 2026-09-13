1. **Title**: OmniRL: In-Context Reinforcement Learning by Large-Scale Meta-Training in Randomized Worlds (arXiv:2502.02869)
   - **Authors**: Fan Wang, Pengtao Shao, Yiming Zhang, Bo Yu, Shaoshan Liu, Ning Ding, Yang Cao, Yu Kang, Haifeng Wang
   - **Summary**: This paper introduces OmniRL, a model trained on a vast array of procedurally generated tasks to achieve generalizable in-context reinforcement learning. The authors propose an efficient data synthesis pipeline and a novel framework integrating imitation and reinforcement learning, demonstrating that in-context learning can effectively address unseen tasks without gradient-based fine-tuning.
   - **Year**: 2025

2. **Title**: Meta-in-context learning in large language models (arXiv:2305.12907)
   - **Authors**: Julian Coda-Forno, Marcel Binz, Zeynep Akata, Matthew Botvinick, Jane X. Wang, Eric Schulz
   - **Summary**: The authors explore the concept of meta-in-context learning, where large language models improve their in-context learning abilities through exposure to sequential tasks. They demonstrate that this approach allows models to adaptively reshape their priors and learning strategies, enhancing performance on real-world regression problems.
   - **Year**: 2023

3. **Title**: RL + Transformer = A General-Purpose Problem Solver (arXiv:2501.14176)
   - **Authors**: Micah Rentschler, Jesse Roberts
   - **Summary**: This study shows that fine-tuning a pre-trained transformer with reinforcement learning across multiple episodes enables the model to develop in-context reinforcement learning capabilities. The resulting meta-learner excels in solving unseen tasks with remarkable sample efficiency and adaptability to non-stationary environments.
   - **Year**: 2025

4. **Title**: AMAGO: Scalable In-Context Reinforcement Learning for Adaptive Agents (arXiv:2310.09971)
   - **Authors**: Jake Grigsby, Linxi Fan, Yuke Zhu
   - **Summary**: AMAGO is introduced as an in-context reinforcement learning agent utilizing sequence models to address challenges in generalization, long-term memory, and meta-learning. The approach involves training long-sequence transformers over entire rollouts in parallel with end-to-end reinforcement learning, demonstrating strong performance in meta-RL and long-term memory domains.
   - **Year**: 2023

5. **Title**: Meta-Reinforcement Learning Robust to Distributional Shift Via Performing Lifelong In-Context Learning
   - **Authors**: Tengye Xu, Zihao Li, Qinyuan Ren
   - **Summary**: The authors propose Posterior Sampling Bayesian Lifelong In-Context Reinforcement Learning (PSBL), a method robust to task distribution shifts. PSBL meta-trains a transformer variant to perform amortized inference about the predictive posterior distribution of the optimal policy, enabling online adaptation without parameter updates.
   - **Year**: 2024

6. **Title**: Towards Large-Scale In-Context Reinforcement Learning by Meta-Training in Randomized Worlds
   - **Authors**: Fan Wang, Pengtao Shao, Yiming Zhang, Bo Yu, Shaoshan Liu, Ning Ding, Yang Cao, Yu Kang, Haifeng Wang
   - **Summary**: This work presents a procedurally generated task set named AnyMDP to facilitate scalable in-context reinforcement learning. The authors introduce decoupled policy distillation and prior information induction, demonstrating that large-scale meta-training enables generalization to unseen tasks through versatile in-context learning paradigms.
   - **Year**: 2025

7. **Title**: Meta-Learning Transformers to Improve In-Context Generalization
   - **Authors**: Lorenzo Braccaioli, Anna Vettoruzzo, Prabhant Singh, Joaquin Vanschoren, Mohamed-Rafik Bouguelia, Nicola Conci
   - **Summary**: The paper proposes a training strategy leveraging multiple small-scale, domain-specific datasets to enhance in-context learning in transformers. This approach addresses challenges associated with large, unstructured datasets, improving generalization to new tasks based solely on input prompts.
   - **Year**: 2025

8. **Title**: Rapid Word Learning Through Meta In-Context Learning
   - **Authors**: Wentao Wang, Guangyuan Jiang, Tal Linzen, Brenden Lake
   - **Summary**: The authors introduce Minnow, a method that trains language models to generate new examples of a word's usage given a few in-context examples. This meta-in-context learning approach enables models to quickly learn and use new words in novel contexts, demonstrating competitive performance to traditional learning algorithms.
   - **Year**: 2025

9. **Title**: A Survey of In-Context Reinforcement Learning
   - **Authors**: Amir Moeini, Jiuqi Wang, Jacob Beck, Ethan Blaser, Shimon Whiteson, Rohan Chandra, Shangtong Zhang
   - **Summary**: This survey examines the behavior of agents that solve new tasks without parameter updates by conditioning on additional context, known as in-context reinforcement learning. The paper reviews existing work, highlighting the potential and challenges of this approach.
   - **Year**: 2025

10. **Title**: How Should We Meta-Learn Reinforcement Learning Algorithms?
    - **Authors**: Alexander David Goldie, Zilin Wang, Jakob Nicolaus Foerster, Shimon Whiteson
    - **Summary**: The authors conduct an empirical comparison of different approaches to meta-learning reinforcement learning algorithms. They investigate factors such as interpretability, sample cost, and training time, proposing guidelines to ensure future learned algorithms are as performant as possible.
    - **Year**: 2025

**Key Challenges:**

1. **Sensitivity to Demonstration Selection and Ordering**: In-context learning performance is highly dependent on the choice and sequence of demonstration examples, leading to variability and potential suboptimal outcomes.

2. **Generalization Across Tasks**: Current methods often struggle to generalize effectively across diverse tasks, particularly when faced with out-of-distribution queries or domain shifts.

3. **Data Efficiency**: Achieving robust in-context learning capabilities typically requires large-scale, diverse datasets, posing challenges in terms of data collection, storage, and processing.

4. **Interpretability of Generated Demonstrations**: Understanding what constitutes an effective in-context example remains poorly understood, limiting the ability to design and generate optimal demonstrations systematically.

5. **Balancing Exploration and Exploitation**: Incorporating reinforcement learning into in-context learning frameworks necessitates careful management of exploration-exploitation trade-offs to optimize downstream task performance. 