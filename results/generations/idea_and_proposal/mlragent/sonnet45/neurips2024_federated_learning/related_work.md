1. **Title**: Efficient Federated Prompt Tuning for Black-box Large Pre-trained Models (arXiv:2310.03123)
   - **Authors**: Zihao Lin, Yan Sun, Yifan Shi, Xueqian Wang, Lifu Huang, Li Shen, Dacheng Tao
   - **Summary**: This paper introduces Federated Black-Box Prompt Tuning (Fed-BBPT), a method that enables efficient prompt tuning of large pre-trained models in federated settings without accessing model parameters or private datasets. By leveraging API-driven learning and zero-order optimization, Fed-BBPT addresses memory constraints and privacy concerns associated with traditional fine-tuning approaches.
   - **Year**: 2023

2. **Title**: Multi-Modal Style Transfer-based Prompt Tuning for Efficient Federated Domain Generalization (arXiv:2601.05955)
   - **Authors**: Yuliang Chen, Xi Lin, Jun Wu, Xiangrui Cai, Qiaolun Zhang, Xichun Fan, Jiapeng Xu, Xiu Su
   - **Summary**: The authors propose FaST-PT, a framework that employs multi-modal style transfer and dual-prompt modules to enhance federated domain generalization. By augmenting local features and adaptively generating prompts, FaST-PT effectively mitigates domain shifts and reduces communication overhead in federated learning environments.
   - **Year**: 2026

3. **Title**: FedDEAP: Adaptive Dual-Prompt Tuning for Multi-Domain Federated Learning (arXiv:2510.18837)
   - **Authors**: Yubin Zheng, Pak-Hei Yeung, Jing Xia, Tianjie Ju, Peng Tang, Weidong Qiu, Jagath C. Rajapakse
   - **Summary**: FedDEAP introduces an adaptive federated prompt tuning framework that enhances the generalization of vision-language models like CLIP across multiple domains. The method utilizes dual prompts to capture both global semantic and local domain-specific knowledge, addressing challenges posed by domain shifts and label heterogeneity in federated learning.
   - **Year**: 2025

4. **Title**: DiPrompT: Disentangled Prompt Tuning for Multiple Latent Domain Generalization in Federated Learning (arXiv:2403.08506)
   - **Authors**: Sikai Bai, Jie Zhang, Shuaicheng Li, Song Guo, Jingcai Guo, Jun Hou, Tao Han, Xiaocheng Lu
   - **Summary**: DiPrompT presents a method for learning adaptive prompts in federated learning without explicit domain labels. By designing global and domain-specific prompts and introducing a dynamic query metric, the approach effectively handles domain generalization challenges in decentralized settings.
   - **Year**: 2024

5. **Title**: Distributed Pruning Towards Tiny Neural Networks in Federated Learning (arXiv:2212.01977)
   - **Authors**: Hong Huang, Lan Zhang, Chaoyue Sun, Ruogu Fang, Xiaoyong Yuan, Dapeng Wu
   - **Summary**: This paper introduces FedTiny, a distributed pruning framework that generates specialized tiny models for resource-constrained devices in federated learning. By incorporating adaptive batch normalization and progressive pruning modules, FedTiny addresses challenges related to memory and computation constraints while maintaining model performance.
   - **Year**: 2023

6. **Title**: Federated Personalized and Privacy-friendly Network Pruning (arXiv:2404.09816)
   - **Authors**: [Authors not specified]
   - **Summary**: The paper proposes FedP3, a framework that integrates personalized and privacy-friendly network pruning in federated learning. By assigning predefined pruning mechanisms to clients and employing dynamic network pruning, FedP3 enhances computational efficiency and privacy preservation in federated settings.
   - **Year**: 2024

7. **Title**: Flocks of Stochastic Parrots: Differentially Private Prompt Learning for Large Language Models (arXiv:2305.15594)
   - **Authors**: [Authors not specified]
   - **Summary**: This work introduces methods for differentially private prompt learning, including PromptDPSGD and PromptPATE, to adapt large language models while preserving data privacy. The approaches leverage differential privacy mechanisms to ensure that prompt tuning does not compromise sensitive information.
   - **Year**: 2023

8. **Title**: Towards Scalable and Non-IID Robust Hierarchical Federated Learning via Label-Driven Knowledge Aggregator (arXiv:2209.14520)
   - **Authors**: Minh-Duong Nguyen, Q.-Viet Pham, Dinh Thai Hoang, Long Tran-Thanh, Diep N. Nguyen, Won-Joo Hwang
   - **Summary**: The authors propose Full-stack FL (F2L), a hierarchical federated learning framework that enhances scalability and robustness to non-IID data. By utilizing a label-driven knowledge distillation technique, F2L effectively aggregates knowledge across clients, addressing challenges related to data heterogeneity and scalability.
   - **Year**: 2023

9. **Title**: TrojFSP: Trojan Insertion in Few-shot Prompt Tuning (arXiv:2312.10467)
   - **Authors**: Mengxin Zheng, Jiaqi Xue, Xun Chen, YanShan Wang, Qian Lou, Lei Jiang
   - **Summary**: TrojFSP investigates the security vulnerabilities in few-shot prompt tuning by introducing a method for Trojan insertion. The paper highlights challenges such as poisoned imbalance and overfitting, proposing techniques like Target-Class Shrink and Selective Token Poisoning to enhance attack success rates while maintaining clean data accuracy.
   - **Year**: 2023

10. **Title**: PEVL: Position-enhanced Pre-training and Prompt Tuning for Vision-language Models (arXiv:2205.11169)
    - **Authors**: Yuan Yao, Qianyu Chen, Ao Zhang, Wei Ji, Zhiyuan Liu, Tat-Seng Chua, Maosong Sun
    - **Summary**: PEVL introduces a method that enhances vision-language pre-training and prompt tuning by incorporating explicit object position modeling. The approach reformulates object positions and language in a unified framework, improving performance on position-sensitive tasks such as referring expression comprehension and phrase grounding.
    - **Year**: 2023

**Key Challenges:**

1. **Data Heterogeneity**: Variations in data distributions across clients can lead to challenges in model generalization and performance consistency in federated learning environments.

2. **Privacy Preservation**: Ensuring data privacy while enabling collaborative learning requires mechanisms that prevent sensitive information leakage during prompt optimization and model training.

3. **Communication Efficiency**: Reducing communication overhead is crucial, especially when dealing with large models and limited bandwidth, to maintain the feasibility of federated learning.

4. **Model Adaptation**: Effectively adapting foundation models to diverse domain-specific tasks without extensive computational resources or access to raw data remains a significant challenge.

5. **Security Vulnerabilities**: Protecting federated learning systems from adversarial attacks, such as Trojan insertions during prompt tuning, is essential to maintain model integrity and reliability. 