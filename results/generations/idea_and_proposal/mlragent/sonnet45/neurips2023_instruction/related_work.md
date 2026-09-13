1. **Title**: HierRouter: Coordinated Routing of Specialized Large Language Models via Reinforcement Learning (arXiv:2511.09873)
   - **Authors**: Nikunj Gupta, Bill Guo, Rajgopal Kannan, Viktor K. Prasanna
   - **Summary**: This paper introduces HierRouter, a hierarchical routing approach that dynamically assembles inference pipelines from a pool of specialized, lightweight language models. By formulating the problem as a finite-horizon Markov Decision Process and employing Proximal Policy Optimization-based reinforcement learning, HierRouter selects models iteratively to optimize performance across tasks like QA, code generation, and mathematical reasoning.
   - **Year**: 2025

2. **Title**: Reasoning Up the Instruction Ladder for Controllable Language Models (arXiv:2511.04694)
   - **Authors**: Zishuo Zheng, Vidhisha Balachandran, Chan Young Park, Faeze Brahman, Sachin Kumar
   - **Summary**: The authors address the challenge of reconciling competing instructions from multiple sources in LLMs by introducing a framework that treats instruction hierarchy resolution as a reasoning task. They construct VerIH, a dataset of constraint-following tasks with verifiable answers, and demonstrate that lightweight reinforcement learning with VerIH enhances instruction prioritization and robustness against adversarial inputs.
   - **Year**: 2025

3. **Title**: Retrieval-Augmented Hierarchical in-Context Reinforcement Learning and Hindsight Modular Reflections for Task Planning with LLMs (arXiv:2408.06520)
   - **Authors**: Chuanneng Sun, Songjun Huang, Dario Pompili
   - **Summary**: This work proposes RAHL, a framework that decomposes complex tasks into sub-tasks using an LLM-based high-level policy, inspired by Hierarchical Reinforcement Learning. The framework introduces Hindsight Modular Reflection to improve reflection efficiency and demonstrates improved performance in benchmark environments like ALFWorld, Webshop, and HotpotQA.
   - **Year**: 2024

4. **Title**: ALaRM: Align Language Models via Hierarchical Rewards Modeling (arXiv:2403.06754)
   - **Authors**: Yuhang Lai, Siyuan Wang, Shujun Liu, Xuanjing Huang, Zhongyu Wei
   - **Summary**: ALaRM introduces a framework for modeling hierarchical rewards in reinforcement learning from human feedback to enhance the alignment of LLMs with human preferences. By integrating holistic and aspect-specific rewards, the framework provides precise guidance for language models, improving performance in tasks like long-form question answering and machine translation.
   - **Year**: 2024

5. **Title**: Training Language Models to Follow Instructions (arXiv:2203.02155)
   - **Authors**: Not specified in the provided excerpt.
   - **Summary**: This paper discusses the methodology and limitations of training language models to follow instructions using reinforcement learning from human feedback. It highlights challenges such as the influence of annotators' backgrounds on labeling tasks and the models' tendencies to generate harmful outputs despite training.
   - **Year**: 2024

6. **Title**: RLAIF: Scaling Reinforcement Learning from Human Feedback (arXiv:2309.00267)
   - **Authors**: Not specified in the provided excerpt.
   - **Summary**: The authors present RLAIF, a framework for scaling reinforcement learning from human feedback to improve language model alignment. The paper discusses methodologies for efficient reinforcement learning in extractive document summarization and addresses challenges in aligning models with human preferences.
   - **Year**: 2024

7. **Title**: The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions (arXiv:2404.13208)
   - **Authors**: Not specified in the provided excerpt.
   - **Summary**: This work proposes instilling an instruction hierarchy into LLMs, where system messages take precedence over user messages, and user messages over third-party content. The approach aims to improve robustness against adversarial inputs by training models to prioritize privileged instructions.
   - **Year**: 2024

8. **Title**: Self-Refine: Iterative Refinement with Self-Feedback (arXiv:2303.17651)
   - **Authors**: Aman Madaan, Niket Tandon, Prakhar Gupta, Skyler Hallinan, Luyu Gao, Sarah Wiegreffe, Uri Alon, Nouha Dziri, Shrimai Prabhumoye, Yiming Yang, et al.
   - **Summary**: The authors introduce Self-Refine, a framework where language models iteratively refine their outputs using self-feedback. This approach enhances the models' ability to handle complex instructions by allowing them to self-correct and improve their responses over multiple iterations.
   - **Year**: 2023

9. **Title**: Large Language Models Can Self-Improve (arXiv:2210.11610)
   - **Authors**: Jiaxin Huang, Shixiang Shane Gu, Le Hou, Yuexin Wu, Xuezhi Wang, Hongkun Yu, and Jiawei Han
   - **Summary**: This paper explores the capability of large language models to self-improve by generating and utilizing their own feedback. The study demonstrates that models can enhance their performance on complex tasks through iterative self-improvement processes.
   - **Year**: 2023

10. **Title**: ChatGPT Outperforms Crowd-Workers for Text-Annotation Tasks (arXiv:2303.15056)
    - **Authors**: Fabrizio Gilardi, Meysam Alizadeh, and Maël Kubli
    - **Summary**: The authors compare the performance of ChatGPT with human crowd-workers on text-annotation tasks. The study finds that ChatGPT not only matches but often surpasses human performance, highlighting the potential of LLMs in handling complex instruction-based tasks.
    - **Year**: 2023

**Key Challenges:**

1. **Instruction Decomposition Complexity**: Effectively breaking down complex, multi-step instructions into manageable sub-tasks remains a significant challenge. Ensuring that models can autonomously and accurately perform this decomposition is crucial for systematic problem-solving.

2. **Maintaining Contextual Coherence**: As models execute decomposed sub-tasks, preserving the overall context and ensuring coherence across outputs is difficult. Loss of context can lead to incomplete or disjointed results.

3. **Reinforcement Learning Stability**: Training LLMs using hierarchical reinforcement learning frameworks introduces challenges in stability and convergence. Balancing exploration and exploitation while managing hierarchical policies adds complexity to the training process.

4. **Data Annotation and Quality**: Creating high-quality, annotated datasets with ground-truth decompositions for complex instructions is labor-intensive. Variability in human annotations can introduce inconsistencies, affecting model performance.

5. **Robustness to Adversarial Inputs**: Ensuring that models can handle adversarial or conflicting instructions without compromising performance or safety is a persistent challenge. Developing mechanisms to prioritize and adhere to privileged instructions is essential for reliable deployment. 