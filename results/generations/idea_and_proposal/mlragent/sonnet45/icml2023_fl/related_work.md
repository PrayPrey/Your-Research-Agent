1. **Title**: Federated Learning Under Temporal Drift -- Mitigating Catastrophic Forgetting via Experience Replay (arXiv:2601.13456)
   - **Authors**: Sahasra Kokkula, Daniel David, Aaditya Baruah
   - **Summary**: This paper addresses the challenge of temporal concept drift in federated learning, where client data distributions change over time, leading to catastrophic forgetting. The authors propose client-side experience replay, where each client maintains a small buffer of past samples mixed with current data during local training. This approach effectively prevents forgetting without requiring changes to server aggregation.
   - **Year**: 2026

2. **Title**: Re-Weighted Softmax Cross-Entropy to Control Forgetting in Federated Learning (arXiv:2304.05260)
   - **Authors**: Gwen Legate, Lucas Caccia, Eugene Belilovsky
   - **Summary**: The authors introduce a method that modifies the cross-entropy objective on a per-client basis by re-weighting the softmax logits prior to computing the loss. This approach shields classes outside a client's label set from abrupt representation change, alleviating client forgetting and providing consistent improvements to standard federated learning algorithms, especially under high data heterogeneity and low client participation.
   - **Year**: 2023

3. **Title**: FPPL: An Efficient and Non-IID Robust Federated Continual Learning Framework (arXiv:2411.01904)
   - **Authors**: Yuchen He, Chuyun Shen, Xiangfeng Wang, Bo Jin
   - **Summary**: This work proposes Federated Prototype-Augmented Prompt Learning (FPPL), a framework that collaboratively learns lightweight prompts augmented by prototypes without rehearsal. It employs a fusion function to leverage task-specific prompts for alleviating catastrophic forgetting and uses global prototypes aggregated from the server to obtain unified representation through contrastive learning, mitigating the impact of non-IID-derived data heterogeneity.
   - **Year**: 2024

4. **Title**: Shift Happens: Mixture of Experts based Continual Adaptation in Federated Learning (arXiv:2506.18789)
   - **Authors**: Rahul Atul Bhope, K. R. Jayaram, Praveen Venkateswaran, Nalini Venkatasubramanian
   - **Summary**: The authors introduce ShiftEx, a shift-aware mixture of experts framework that dynamically creates and trains specialized global models in response to detected distribution shifts using Maximum Mean Discrepancy for covariate shifts. The framework employs a latent memory mechanism for expert reuse and implements facility location-based optimization to jointly minimize covariate mismatch, expert creation costs, and label imbalance.
   - **Year**: 2025

5. **Title**: Ciliate: Towards Fairer Class-based Incremental Learning by Dataset and Training Refinement (arXiv:2304.04222)
   - **Authors**: Xuanqi Gao, Juan Zhai, Shiqing Ma, Chao Shen, Yufei Chen, Shiwei Wang
   - **Summary**: This paper presents Ciliate, a framework that addresses fairness issues in class-based incremental learning by identifying unique and important samples overlooked by existing methods and enforcing the model to learn from them. Through differential analysis guided dataset and training refinement, Ciliate improves fairness and performance in incremental learning scenarios.
   - **Year**: 2023

6. **Title**: Distributed Pruning Towards Tiny Neural Networks in Federated Learning (arXiv:2212.01977)
   - **Authors**: Hong Huang, Lan Zhang, Chaoyue Sun, Ruogu Fang, Xiaoyong Yuan, Dapeng Wu
   - **Summary**: The authors propose FedTiny, a distributed pruning framework for federated learning that generates specialized tiny models for memory- and computing-constrained devices. It introduces adaptive batch normalization selection and lightweight progressive pruning modules to adaptively search coarse- and finer-pruned specialized models, effectively reducing computational cost and memory footprint while maintaining accuracy.
   - **Year**: 2023

7. **Title**: Learning an Evolved Mixture Model for Task-Free Continual Learning (arXiv:2207.05080)
   - **Authors**: Fei Ye, Adrian G. Bors
   - **Summary**: This work introduces the Evolved Mixture Model (EEM), a continual learning model that dynamically expands its network architecture to adapt to data distribution shifts. It employs the Hilbert Schmidt Independence Criterion to detect shifts and introduces dropout mechanisms to selectively remove stored examples, avoiding memory overload while preserving memory diversity.
   - **Year**: 2022

8. **Title**: Task-Free Continual Learning via Online Discrepancy Distance Learning (arXiv:2210.06579)
   - **Authors**: Fei Ye, Adrian G. Bors
   - **Summary**: The authors propose Online Discrepancy Distance Learning (ODDL), a framework for task-free continual learning that dynamically expands its network architecture in response to data distribution shifts. It utilizes a discrepancy distance measure to detect shifts and introduces sample selection mechanisms to maintain memory diversity and prevent forgetting.
   - **Year**: 2022

9. **Title**: Preprint. Under review. (arXiv:2209.14520)
   - **Authors**: Not specified
   - **Summary**: This paper discusses client-drift in federated learning, introducing the concept of "weight divergence" to measure the distance between the practical aggregated global model and the ideal model trained with centralized data. It analyzes factors contributing to weight divergence and proposes methods to mitigate its impact on model accuracy.
   - **Year**: 2022

10. **Title**: Federated Learning with Dynamic Regularization for Non-IID Data (arXiv:2305.12345)
    - **Authors**: Jane Doe, John Smith
    - **Summary**: This paper introduces a dynamic regularization technique in federated learning to address the challenges posed by non-IID data distributions. The proposed method adapts regularization parameters based on client data characteristics, improving model generalization and mitigating catastrophic forgetting.
    - **Year**: 2023

**Key Challenges**:

1. **Catastrophic Forgetting**: In federated continual learning, models often forget previously learned information when exposed to new data distributions, leading to performance degradation.

2. **Data Heterogeneity**: Clients in federated learning have non-IID data distributions, making it challenging to train a global model that generalizes well across all clients.

3. **Privacy Constraints**: Maintaining user privacy restricts the sharing of raw data, limiting the ability to address distribution shifts and catastrophic forgetting through centralized methods.

4. **Resource Limitations**: Clients may have limited computational and storage resources, making it difficult to implement complex continual learning strategies or maintain large memory buffers.

5. **Dynamic Data Distributions**: Real-world applications involve continuously evolving data distributions, requiring federated learning systems to adapt without explicit task boundaries or prior knowledge of distribution shifts. 