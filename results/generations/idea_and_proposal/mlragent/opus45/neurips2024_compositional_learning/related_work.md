1. **Title**: Self-Expansion of Pre-trained Models with Mixture of Adapters for Continual Learning (arXiv:2403.18886)
   - **Authors**: Huiyi Wang, Haodong Lu, Lina Yao, Dong Gong
   - **Summary**: This paper introduces SEMA, a framework that enhances continual learning by dynamically expanding pre-trained models with modular adapters. SEMA detects distribution shifts and decides whether to reuse existing adapters or add new ones, balancing stability and adaptability. It employs a modular adapter design with functional components and representation descriptors, and uses an expandable weighting router for effective adapter composition. The approach achieves state-of-the-art performance without memory rehearsal.
   - **Year**: 2024

2. **Title**: Generalized Few-Shot Continual Learning with Contrastive Mixture of Adapters (arXiv:2302.05936)
   - **Authors**: Yawen Cui, Zitong Yu, Rizhao Cai, Xun Wang, Alex C. Kot, Li Liu
   - **Summary**: This work addresses the challenges of few-shot continual learning in both class- and domain-incremental settings. The authors propose Contrastive Mixture of Adapters (CMoA), a framework that integrates a mixture of adapters into Vision Transformers. CMoA employs cosine similarity regularization and dynamic weighting to ensure each adapter learns specific knowledge, and utilizes prototype-calibrated contrastive learning to achieve domain-invariant representations. The method demonstrates improved generalization and mitigates catastrophic forgetting.
   - **Year**: 2023

3. **Title**: ATLAS: Adapter-Based Multi-Modal Continual Learning with a Two-Stage Learning Strategy (arXiv:2410.10923)
   - **Authors**: Hong Li, Zhiquan Tan, Xingyu Li, Weiran Huang
   - **Summary**: ATLAS presents a two-stage learning paradigm for multi-modal continual learning, combining experience-based learning and novel knowledge expansion. The framework utilizes adapters to capture task-specific knowledge and addresses the redundancy among adapters by merging co-activated ones. It also incorporates both multi-modal and uni-modal tasks, enhancing generalization and mitigating forgetting.
   - **Year**: 2024

4. **Title**: Learning an Evolved Mixture Model for Task-Free Continual Learning (arXiv:2207.05080)
   - **Authors**: Fei Ye, Adrian G. Bors
   - **Summary**: This paper introduces the Evolved Mixture Model (EEM) for task-free continual learning, where task identities and boundaries are unknown. EEM dynamically expands its architecture by evaluating the Hilbert Schmidt Independence Criterion between stored knowledge and new data, adding new components as needed. It also employs dropout mechanisms to manage memory and prevent overload, achieving robust performance without explicit task information.
   - **Year**: 2022

5. **Title**: Continual Variational Autoencoder Learning via Online Cooperative Memorization (arXiv:2207.10131)
   - **Authors**: Fei Ye, Adrian G. Bors
   - **Summary**: This work addresses catastrophic forgetting in Variational Autoencoders (VAEs) during continual learning. The authors propose an Online Cooperative Memorization framework that combines short-term and long-term memory buffers to store diverse samples. The framework selectively transfers samples based on information diversity and integrates a dynamic VAE expansion mechanism, enhancing the model's ability to learn new concepts without forgetting previous ones.
   - **Year**: 2022

6. **Title**: No “Zero-Shot” Without Exponential Data: Pretraining Concept Frequency Determines Multimodal Model Performance (arXiv:2404.04125)
   - **Authors**: Vishaal Udandarao, Ameya Prabhu, Adhiraj Ghosh, Yash Sharma, Philip H.S. Torr, Adel Bibi, Samuel Albanie, Matthias Bethge
   - **Summary**: This study investigates the relationship between concept frequency in pretraining datasets and the zero-shot performance of multimodal models. The authors find that models require exponentially more data to achieve linear improvements in zero-shot performance, indicating that current models may not generalize as effectively as previously thought. This has implications for the design of continual learning systems aiming for compositional generalization.
   - **Year**: 2024

7. **Title**: Grokked Transformers are Implicit Reasoners: A Study on the Systematicity of Rule Composition (arXiv:2405.15071)
   - **Authors**: [Authors not specified]
   - **Summary**: This paper examines the ability of transformer models to perform implicit reasoning through rule composition. The authors find that while transformers can learn to apply latent rules over knowledge, their generalization to out-of-distribution data is limited. This highlights challenges in achieving compositional generalization in continual learning settings.
   - **Year**: 2024

8. **Title**: ViLPAct: A Benchmark for Compositional Generalization in Action Understanding (arXiv:2210.05556)
   - **Authors**: [Authors not specified]
   - **Summary**: ViLPAct introduces a benchmark designed to evaluate compositional generalization in action understanding tasks. The benchmark assesses models' abilities to understand and generate complex actions from simpler components, providing a valuable resource for developing and testing continual learning systems that aim to achieve compositional generalization.
   - **Year**: 2022

**Key Challenges:**

1. **Catastrophic Forgetting**: Continual learning models often struggle to retain previously learned knowledge when adapting to new tasks, leading to significant performance degradation.

2. **Balancing Stability and Plasticity**: Achieving a balance between maintaining existing knowledge (stability) and incorporating new information (plasticity) is a persistent challenge in continual learning.

3. **Efficient Memory Management**: Managing memory resources effectively to store and retrieve relevant information without overwhelming the system is crucial for scalable continual learning.

4. **Compositional Generalization**: Ensuring that models can generalize to new compositions of learned components, especially in dynamic environments, remains a significant hurdle.

5. **Task-Free Learning**: Developing models that can learn continuously without explicit task boundaries or identities poses challenges in detecting and adapting to distribution shifts autonomously. 