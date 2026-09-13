1. **Title**: Prompt-Based Continual Compositional Zero-Shot Learning (arXiv:2512.09172)
   - **Authors**: Sauda Maryam, Sara Nadeem, Faisal Qureshi, Mohsen Ali
   - **Summary**: This paper introduces PromptCCZSL, a framework that enables vision-language models to adapt continually to new attributes, objects, and their compositions without forgetting prior knowledge. It employs session-aware compositional prompts and a recency-weighted multi-teacher distillation method to maintain semantic consistency and prevent catastrophic forgetting.
   - **Year**: 2025

2. **Title**: Composition-Incremental Learning for Compositional Generalization (arXiv:2511.09082)
   - **Authors**: Zhen Li, Yuwei Wu, Chenchen Jing, Che Sun, Chuanhao Li, Yunde Jia
   - **Summary**: The authors propose a pseudo-replay framework that utilizes a visual synthesizer to generate representations of learned compositions and a linguistic primitive distillation mechanism to maintain aligned primitive representations. This approach aims to improve compositional generalization in continual learning settings.
   - **Year**: 2025

3. **Title**: Rehearsal-Free Modular and Compositional Continual Learning for Language Models (arXiv:2404.00790)
   - **Authors**: Mingyang Wang, Heike Adel, Lukas Lange, Jannik Strötgen, Hinrich Schütze
   - **Summary**: MoCL is a framework that incrementally adds new modules to language models and composes them with existing ones, facilitating knowledge transfer without the need for data replay. This method addresses catastrophic forgetting while promoting compositional generalization.
   - **Year**: 2024

4. **Title**: HAM: Hierarchical Adapter Merging for Scalable Continual Learning (arXiv:2509.13211)
   - **Authors**: Eric Nuertey Coleman, Luigi Quarantiello, Samrat Mukherjee, Julio Hurtado, Vincenzo Lomonaco
   - **Summary**: HAM introduces a framework that dynamically combines adapters from different tasks during training, enabling scalable continual learning. It maintains a fixed set of groups that hierarchically consolidate new adapters, facilitating transfer learning between related tasks.
   - **Year**: 2025

5. **Title**: Adaptive Compositional Continual Meta-Learning
   - **Authors**: Bin Wu, Jinyuan Fang, Xiangxiang Zeng, Shangsong Liang, Qiang Zhang
   - **Summary**: ACML employs a compositional premise to associate tasks with subsets of mixture components, allowing meta-knowledge sharing among heterogeneous tasks. It also introduces a component sparsification method to filter out redundant components, enhancing parameter efficiency.
   - **Year**: 2023

6. **Title**: Does Continual Learning Meet Compositionality? New Benchmarks and An Evaluation Framework
   - **Authors**: Weiduo Liao, Ying Wei, Mingchen Jiang, Qingfu Zhang, Hisao Ishibuchi
   - **Summary**: This work introduces two vision benchmarks, CGQA and COBJ, along with an evaluation framework called Compositional Few-Shot Testing (CFST). These tools assess the compositional generalization capabilities of continual learning models, highlighting areas for improvement.
   - **Year**: 2023

7. **Title**: On the Compositional Generalization in Versatile Open-domain Dialogue
   - **Authors**: Tingchen Fu, Xueliang Zhao, Lemao Liu, Rui Yan
   - **Summary**: The authors develop a sparsely activated modular network that formulates dialogue generation as the execution of a generated program, recursively composing and assembling modules. This approach aims to enhance compositional generalization in open-domain dialogue systems.
   - **Year**: 2023

8. **Title**: Compositional Interfaces for Compositional Generalization
   - **Authors**: Jelena Luketina, Jack Lanchantin, Sainbayar Sukhbaatar, Arthur Szlam
   - **Summary**: This paper demonstrates how compositional generalization can be achieved through end-to-end modular architectures, where encoding of observations and prediction of actions are handled by differentiable modules specialized to specific spaces, with a shared controller between them.
   - **Year**: 2025

9. **Title**: Exploring Continual Learning of Compositional Generalization in NLI
   - **Authors**: Xiyan Fu, Anette Frank
   - **Summary**: The authors introduce the C2Gen NLI challenge, where a model continuously acquires knowledge of primitive inference tasks as a basis for compositional inferences. They explore how continual learning affects compositional generalization in natural language inference.
   - **Year**: 2024

10. **Title**: Consistency Regularization Training for Compositional Generalization
    - **Authors**: Yongjing Yin, Jiali Zeng, Yafu Li, Fandong Meng, Jie Zhou, Yue Zhang
    - **Summary**: This work improves the compositional generalization capability of Transformer models through consistency regularization training, promoting representation and prediction consistency across samples without modifying model architectures.
    - **Year**: 2023

**Key Challenges:**

1. **Catastrophic Forgetting**: Continual learning models often forget previously learned information when adapting to new tasks, hindering long-term knowledge retention.

2. **Compositional Generalization**: Achieving the ability to generalize to unseen combinations of known components remains a significant challenge, especially in dynamic environments.

3. **Parameter Efficiency**: Balancing the addition of new modules with the efficient use of parameters is crucial to prevent model bloat and maintain scalability.

4. **Knowledge Transfer**: Facilitating effective transfer of knowledge between tasks without interference is essential for improving learning efficiency and performance.

5. **Evaluation Benchmarks**: The lack of standardized benchmarks for assessing compositional generalization in continual learning settings makes it difficult to compare and validate different approaches. 