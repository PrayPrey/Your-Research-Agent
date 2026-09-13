1. **Title**: Mol-AIR: Molecular Reinforcement Learning with Adaptive Intrinsic Rewards for Goal-directed Molecular Generation (arXiv:2403.20109)
   - **Authors**: Jinyeong Park, Jaegyoon Ahn, Jonghwan Choi, Jibum Kim
   - **Summary**: Mol-AIR introduces a reinforcement learning framework that employs adaptive intrinsic rewards to enhance goal-directed molecular generation. By integrating history-based and learning-based intrinsic rewards, the method effectively explores the vast chemical space and optimizes specific chemical properties without prior knowledge.
   - **Year**: 2024

2. **Title**: 3D-Mol: A Novel Contrastive Learning Framework for Molecular Property Prediction with 3D Information (arXiv:2309.17366)
   - **Authors**: Taojie Kuang, Yiming Ren, Zhixiang Ren
   - **Summary**: 3D-Mol presents a contrastive learning framework that leverages 3D spatial information for molecular property prediction. By deconstructing molecules into hierarchical graphs and utilizing contrastive learning on a large dataset, the model achieves superior performance in capturing geometric information and predicting molecular properties.
   - **Year**: 2023

3. **Title**: Valid Property-Enhanced Contrastive Learning for Targeted Optimization & Resampling for Novel Drug Design (arXiv:2509.00684)
   - **Authors**: Amartya Banerjee, Somnath Kar, Anirban Pal, Debabrata Maiti
   - **Summary**: VECTOR+ is a framework that combines property-guided representation learning with controllable molecule generation. It applies to both regression and classification tasks, enabling data-efficient exploration of functional chemical space and generating novel, synthetically tractable drug candidates.
   - **Year**: 2025

4. **Title**: Contrastive Multi-Task Learning with Solvent-Aware Augmentation for Drug Discovery (arXiv:2508.01799)
   - **Authors**: Jing Lan, Hexiao Ding, Hongzhao Chen, Yufeng Jiang, Ng Nga Chun, Gerald W. Y. Cheng, Zongxi Li, Jing Cai, Liang-ting Lin, Jung Sun Yoo
   - **Summary**: This study introduces a pre-training method that incorporates ligand conformational ensembles generated under diverse solvent conditions as augmented input. The model integrates molecular reconstruction, interatomic distance prediction, and contrastive learning to improve binding affinity prediction and virtual screening in drug discovery.
   - **Year**: 2025

5. **Title**: BindGPT: A Language Model for 3D Molecular Data Representation and Generation (arXiv:2406.03686)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: BindGPT is a language model designed to handle spatial molecular structures in text format. It utilizes structural SMILES and spatial XYZ formats to describe molecular graphs and atom locations, enabling accurate and realistic 3D molecular structure generation without relying on external software for graph reconstruction.
   - **Year**: 2024

6. **Title**: Contextual Distillation Model for Diversified Recommendation (arXiv:2406.09021)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: The Contextual Distillation Model (CDM) is introduced to enhance diversity in recommendation systems. By leveraging contextual information from candidate items and employing a contrastive context encoder, CDM effectively models diverse contexts, leading to improved recommendation quality and diversity.
   - **Year**: 2024

7. **Title**: A Simple Framework for Contrastive Learning of Visual Representations (arXiv:2002.05709)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This paper presents a framework for contrastive learning of visual representations, emphasizing the importance of data augmentation in learning good representations. The study systematically examines the impact of individual data augmentations and their compositions on model performance.
   - **Year**: 2024

8. **Title**: Preprint. Under review. (arXiv:2406.03686)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This preprint discusses a novel framework applying language modeling to 3D molecular data represented by textual tokens. The approach leverages the GPT paradigm to foster a causal language model adept at navigating the complex space of 3D molecules, demonstrating applications in 3D molecular generation and targeted binding affinity prediction.
   - **Year**: 2024

9. **Title**: Published as a conference paper at ICLR 2024 (arXiv:2401.11237)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This conference paper explores goal-conditioned reinforcement learning in controlled Markov processes. It discusses data collection methods, including the use of context-conditioned policies, and presents theoretical analyses alongside empirical results using outcome conditional behavioral cloning.
   - **Year**: 2024

10. **Title**: Published at the ICLR 2022 workshop on Objects, Structure and Causality (arXiv:2203.05997)
    - **Authors**: [Authors not specified in the provided excerpt]
    - **Summary**: This workshop paper discusses an approach for learning image-level and object-centric representations in a self-supervised manner. It combines competition-based attention mechanisms with contrastive losses applied in global and object latent spaces, aiming to improve object representations without relying on pixel reconstruction.
    - **Year**: 2024

**Key Challenges:**

1. **High-Dimensional and Continuous Goal Spaces**: Molecular discovery involves optimizing within vast, continuous, and high-dimensional goal spaces, making it challenging for goal-conditioned reinforcement learning (GCRL) methods to effectively navigate and identify optimal solutions.

2. **Sparse and Expensive Feedback**: Evaluating molecular properties often requires costly simulations or experiments, resulting in sparse and expensive feedback signals that hinder efficient learning and optimization processes.

3. **Representation Learning of Molecular Structures**: Developing effective representations that capture the complex and diverse nature of molecular structures is crucial. Current methods may struggle to learn representations that accurately reflect chemical similarity and synthesizability.

4. **Generalization to Novel Target Properties**: Ensuring that models can generalize to novel molecular properties and targets is a significant challenge, as it requires the ability to extrapolate learned knowledge to unseen scenarios.

5. **Balancing Exploration and Exploitation**: In the context of molecular generation, maintaining a balance between exploring new chemical spaces and exploiting known favorable regions is essential for discovering novel molecules with desired properties. 