1. **Title**: Towards Instance-wise Personalized Federated Learning via Semi-Implicit Bayesian Prompt Tuning (arXiv:2508.19621)
   - **Authors**: Tiandi Ye, Wenyan Liu, Kai Yao, Lichun Li, Shangchao Su, Cen Chen, Xiang Li, Shan Yin, Ming Gao
   - **Summary**: This paper introduces pFedBayesPT, a framework for personalized federated learning that addresses intra-client data heterogeneity by generating instance-wise prompts using a semi-implicit Bayesian approach. The method captures diverse visual semantics and demonstrates superior performance under both feature and label heterogeneity settings.
   - **Year**: 2025

2. **Title**: Closer to Reality: Practical Semi-Supervised Federated Learning for Foundation Model Adaptation (arXiv:2508.16568)
   - **Authors**: Guangyu Sun, Jingtao Li, Weiming Zhuang, Chen Chen, Chen Chen, Lingjuan Lyu
   - **Summary**: The authors propose FedMox, a framework that adapts foundation models in federated settings with limited labeled data and computational resources. It employs a sparse Mixture-of-Experts architecture and a spatial router to align features across resolutions, effectively adapting foundation models under practical constraints.
   - **Year**: 2025

3. **Title**: FedML-HE: An Efficient Homomorphic-Encryption-Based Privacy-Preserving Federated Learning System (arXiv:2303.10837)
   - **Authors**: Weizhao Jin, Yuhang Yao, Shanshan Han, Jiajun Gu, Carlee Joe-Wong, Srivatsan Ravi, Salman Avestimehr, Chaoyang He
   - **Summary**: This work presents FedML-HE, a federated learning system that utilizes homomorphic encryption to secure model aggregation. By selectively encrypting sensitive parameters, it significantly reduces computation and communication overheads, making privacy-preserving federated learning more practical for large foundation models.
   - **Year**: 2023

4. **Title**: Flocks of Stochastic Parrots: Differentially Private Prompt Learning for Large Language Models (arXiv:2305.15594)
   - **Authors**: Haonan Duan, Adam Dziedzic, Nicolas Papernot, Franziska Boenisch
   - **Summary**: The paper addresses privacy concerns in prompt-based learning by introducing a differentially private method for learning prompts. It demonstrates that soft prompts can be obtained privately through gradient descent, while discrete prompts require a noisy voting mechanism among an ensemble of language models to ensure privacy.
   - **Year**: 2023

5. **Title**: Distributed Pruning Towards Tiny Neural Networks in Federated Learning (arXiv:2212.01977)
   - **Authors**: Hong Huang, Lan Zhang, Chaoyue Sun, Ruogu Fang, Xiaoyong Yuan, Dapeng Wu
   - **Summary**: This study introduces FedTiny, a distributed pruning framework for federated learning that generates specialized tiny models for resource-constrained devices. It features adaptive batch normalization and progressive pruning modules to address biases and computational limitations, achieving significant reductions in computational cost and memory footprint.
   - **Year**: 2023

6. **Title**: A Distributed Privacy Preserving Model for the Detection of Alzheimer’s Disease (arXiv:2312.10237)
   - **Authors**: Paul K. Mandal
   - **Summary**: The author proposes a vertical federated learning model for Alzheimer's disease detection that respects privacy constraints by enabling collaborative learning across diverse medical data sources without data consolidation. The model achieves an accuracy rate consistent with previous studies, demonstrating its effectiveness in a privacy-preserving context.
   - **Year**: 2024

7. **Title**: FEDP3: Federated Personalized and Privacy-Friendly Network Pruning Under Model Heterogeneity (arXiv:2404.09816)
   - **Authors**: Kai Yi, Nidham Gazagnadou, Peter Richtárik, Lingjuan Lyu
   - **Summary**: FEDP3 is a federated learning framework designed to handle model heterogeneity by personalizing and pruning networks in a privacy-friendly manner. It adapts to clients with varying computational resources and data distributions, providing theoretical validation of its efficiency.
   - **Year**: 2024

8. **Title**: PPFL: Privacy-preserving Federated Learning with Trusted Execution Environments (arXiv:2104.14380)
   - **Authors**: Fan Mo, Hamed Haddadi, Kleomenis Katevas, Eduard Marin, Diego Perino, Nicolas Kourtellis
   - **Summary**: This paper presents PPFL, a federated learning framework that leverages Trusted Execution Environments (TEEs) to enhance privacy. By performing local training and secure aggregation within TEEs, it defends against data reconstruction and inference attacks while maintaining comparable model utility.
   - **Year**: 2021

**Key Challenges**:

1. **Model Heterogeneity**: Clients often possess different versions of foundation models, leading to challenges in aggregating and optimizing prompts that are compatible across diverse model architectures.

2. **Data Privacy**: Ensuring privacy while sharing prompts or model updates is critical, as sensitive information can be inferred from these exchanges, necessitating robust privacy-preserving mechanisms.

3. **Computational Constraints**: Resource-limited devices may struggle with the computational demands of prompt optimization and model adaptation, requiring efficient algorithms that minimize overhead.

4. **Data Heterogeneity**: Variations in local data distributions across clients can lead to biased or suboptimal prompt tuning, making it essential to develop methods that account for such heterogeneity.

5. **Communication Overhead**: Frequent communication between clients and the server can incur significant costs, especially when transferring large prompt embeddings or model updates, highlighting the need for communication-efficient strategies. 