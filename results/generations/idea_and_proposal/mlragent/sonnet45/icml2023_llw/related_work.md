1. **Title**: LANCE: Low Rank Activation Compression for Efficient On-Device Continual Learning (arXiv:2509.21617)
   - **Authors**: Marco Paul E. Apolinario, Kaushik Roy
   - **Summary**: This paper introduces LANCE, a framework that employs one-shot higher-order Singular Value Decomposition (SVD) to create reusable low-rank subspaces for activation projection. This approach reduces both memory and computational overhead, facilitating efficient fine-tuning and continual learning on edge devices.
   - **Year**: 2025

2. **Title**: Continual Deep Learning on the Edge via Stochastic Local Competition among Subnetworks (arXiv:2407.10758)
   - **Authors**: Theodoros Christophides, Kyriakos Tolias, Sotirios Chatzis
   - **Summary**: The authors propose a method that leverages stochastic competition principles to promote sparsity in deep networks. By organizing networks into blocks of units that compete locally, the approach results in sparse task-specific representations, reducing memory footprint and computational demand, making it suitable for edge devices.
   - **Year**: 2024

3. **Title**: LODAP: On-Device Incremental Learning Via Lightweight Operations and Data Pruning (arXiv:2504.19638)
   - **Authors**: Biqing Duan, Qing Wang, Di Liu, Wei Zhou, Zhenli He, Shengfa Miao
   - **Summary**: LODAP introduces an on-device incremental learning framework that incorporates an Efficient Incremental Module (EIM) composed of normal convolutions and lightweight operations. The framework also employs a data pruning strategy to reduce training data, thereby lowering training overhead while improving accuracy and reducing model complexity.
   - **Year**: 2025

4. **Title**: Tackling Intertwined Data and Device Heterogeneities in Federated Learning with Unlimited Staleness (arXiv:2309.13536)
   - **Authors**: Haoming Wang, Wei Gao
   - **Summary**: This paper presents a federated learning framework that addresses the challenges posed by intertwined data and device heterogeneities. By estimating the distributions of clients' local training data from their uploaded stale model updates, the approach computes non-stale client model updates, improving model accuracy and reducing training epochs.
   - **Year**: 2024

5. **Title**: Tiny Machine Learning: Progress and Futures (arXiv:2403.19076)
   - **Authors**: Ji Lin, Ligeng Zhu, Wei-Ming Chen, Wei-Chen Wang, Song Han
   - **Summary**: This review discusses the challenges and advancements in Tiny Machine Learning (TinyML), focusing on deploying and training AI models on microcontrollers and IoT devices. It emphasizes the importance of system-algorithm co-design to enable efficient on-device learning.
   - **Year**: 2024

6. **Title**: Knowledge as Priors: Cross-Modal Knowledge Generalization (arXiv:2004.00176)
   - **Authors**: [Authors not specified]
   - **Summary**: The paper addresses cross-modal knowledge generalization by interpreting knowledge as priors on network parameters. It introduces a meta-learning algorithm to generalize learned knowledge from a source dataset to a target dataset, even when direct knowledge distillation is not possible due to the absence of paired data.
   - **Year**: 2024

7. **Title**: Preprint. Under review. (arXiv:2209.14520)
   - **Authors**: [Authors not specified]
   - **Summary**: This work proposes a hierarchical federated learning framework that manages distinct regional servers. By utilizing hierarchical FL, the framework achieves computational efficiency and addresses client drift by applying localized knowledge distillation to reduce class-wise performance gaps between regions.
   - **Year**: 2024

8. **Title**: FEDROBO: Federated Learning Based Autonomous Inter Robots Communication (arXiv:2408.06382)
   - **Authors**: [Authors not specified]
   - **Summary**: The paper presents a federated learning architecture for autonomous inter-robot communication, enabling multiple robots to collaboratively train a model without sharing raw data. The approach emphasizes security and privacy mechanisms, including encryption and access control, to protect client data.
   - **Year**: 2024

9. **Title**: Published as a conference paper at ICLR 2020 (arXiv:1908.01581)
   - **Authors**: [Authors not specified]
   - **Summary**: This paper focuses on disentangling and quantifying consistent features between deep neural networks. It introduces a method to analyze feature reliability and provides insights into existing deep-learning techniques such as knowledge distillation and network compression.
   - **Year**: 2024

10. **Title**: FedKNOW: Federated Continual Learning with Signature Task Knowledge Integration at Edge (arXiv:2212.01738)
    - **Authors**: Yaxin Luopan, Rui Han, Qinglong Zhang, Chi Harold Liu, Guoren Wang
    - **Summary**: FedKNOW is a federated continual learning framework that extracts and integrates knowledge of signature tasks, which are highly influenced by the current task. It comprises a knowledge extractor, gradient restorer, and gradient integrator to prevent catastrophic forgetting and mitigate negative knowledge transfer.
    - **Year**: 2022

**Key Challenges**:

1. **Memory and Computational Constraints**: Edge devices have limited resources, making it challenging to implement complex learning algorithms without exceeding capacity.

2. **Catastrophic Forgetting**: Continual learning models often forget previously learned information when acquiring new knowledge, leading to performance degradation.

3. **Efficient Knowledge Distillation**: Transferring knowledge from complex models to simpler ones without significant loss of accuracy remains a challenge, especially in resource-constrained environments.

4. **Data and Device Heterogeneities**: Variations in data distributions and device capabilities across the network can hinder the effectiveness of federated learning approaches.

5. **Security and Privacy Concerns**: Ensuring data privacy and security during on-device learning and communication is critical, particularly when dealing with sensitive information. 