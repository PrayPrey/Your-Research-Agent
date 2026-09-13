```
# Literature Review: Cross-Domain Backdoor Defense via Universal Trigger Pattern Detection Using Self-Supervised Representation Learning

## 1. Related Papers

1. **Title**: TextGuard: Provable Defense against Backdoor Attacks on Text Classification (arXiv:2311.11225)
   - **Authors**: Hengzhi Pei, Jinyuan Jia, Wenbo Guo, Bo Li, Dawn Song
   - **Summary**: This paper introduces TextGuard, the first provable defense against backdoor attacks in text classification. By partitioning training data into sub-training sets and employing ensemble learning, TextGuard ensures predictions remain unaffected by backdoor triggers within certain thresholds.
   - **Year**: 2023

2. **Title**: MARS: A Malignity-Aware Backdoor Defense in Federated Learning (arXiv:2509.20383)
   - **Authors**: Wei Wan, Yuxuan Ning, Zhicong Huang, Cheng Hong, Shengshan Hu, Ziqi Zhou, Yechao Zhang, Tianqing Zhu, Wanlei Zhou, Leo Yu Zhang
   - **Summary**: MARS introduces a defense mechanism in federated learning by leveraging backdoor energy to assess the malicious extent of each neuron. It employs a novel clustering method to effectively identify and mitigate backdoor models.
   - **Year**: 2025

3. **Title**: Backdooring Self-Supervised Contrastive Learning by Noisy Alignment (arXiv:2508.14015)
   - **Authors**: Tuo Chen, Jie Gui, Minjing Dong, Ju Jia, Lanting Fang, Jian Liu
   - **Summary**: This study presents a data poisoning backdoor attack on self-supervised contrastive learning models. By manipulating the random cropping mechanism, the proposed method achieves state-of-the-art performance in backdoor attacks while maintaining clean-data accuracy.
   - **Year**: 2025

4. **Title**: NT-ML: Backdoor Defense via Non-target Label Training and Mutual Learning (arXiv:2508.05404)
   - **Authors**: Wenjie Huo, Katinka Wolter
   - **Summary**: NT-ML proposes a defense mechanism combining non-target label training and mutual learning to restore poisoned models under advanced backdoor attacks. The approach effectively defends against multiple backdoor attacks with minimal clean samples.
   - **Year**: 2025

5. **Title**: A Zero‑Sum Game‑Theoretic Analysis for Cost‑Aware Backdoor Attacks and Defenses in Deep Learning
   - **Authors**: Kassem Kallas, Carine Tannous, Hichem Faraoun
   - **Summary**: This paper introduces BG_{Cost}, a game-theoretic framework that models the strategic interplay between attackers and defenders in backdoor scenarios, considering resource constraints and cost-aware utility functions.
   - **Year**: 2025

6. **Title**: Invisible Backdoor Attack against Self-supervised Learning (arXiv:2405.14672v2)
   - **Authors**: Hanrong Zhang, Zhenting Wang, Boheng Li, Fulin Lin, Tingxu Han, Mingyu Jin, Chenlu Zhan, Mengnan Du, Hongwei Wang, Shiqing Ma
   - **Summary**: The authors propose an imperceptible backdoor attack against self-supervised learning models, highlighting the vulnerability of such models to subtle, undetectable triggers.
   - **Year**: 2025

7. **Title**: A Survey on Backdoor Threats in Large Language Models (LLMs): Attacks, Defenses, and Evaluation Methods
   - **Authors**: Yihe Zhou, Tao Ni, Wei-Bin Lee, Qingchuan Zhao
   - **Summary**: This survey provides a comprehensive overview of backdoor attacks and defenses in large language models, discussing various attack methods, defense strategies, and evaluation techniques.
   - **Year**: 2025

8. **Title**: Investigating Self-Supervised Methods for Label-Efficient Learning
   - **Authors**: [Authors not specified]
   - **Summary**: This study examines different self-supervised pretext tasks, such as contrastive learning and clustering, to assess their effectiveness in low-shot learning scenarios across various downstream tasks.
   - **Year**: 2025

9. **Title**: DLP: Towards Active Defense against Backdoor Attacks with Decoupled Learning Process
   - **Authors**: Bin Wu
   - **Summary**: DLP introduces a training pipeline that actively defends against backdoor attacks by decoupling the learning process into supervised learning, active unlearning, and active semi-supervised fine-tuning stages.
   - **Year**: 2023

10. **Title**: A Decoupled Contrastive Learning Framework for Backdoor Defense in Federated Learning
    - **Authors**: [Authors not specified]
    - **Summary**: This paper presents a defense strategy named Decoupled Contrastive Learning (DCL) designed to counter backdoor threats in federated learning systems by encouraging the separation of malicious and benign representations.
    - **Year**: 2025

## 2. Key Challenges

1. **Domain-Specific Limitations**: Existing backdoor defenses are often tailored to specific domains (e.g., CV or NLP), making them less effective when applied across different modalities.

2. **Generalization Across Attack Types**: Many defense mechanisms struggle to generalize across various backdoor attack strategies, limiting their applicability in diverse scenarios.

3. **Detection of Novel Triggers**: Identifying unseen or novel backdoor triggers remains a significant challenge, as current methods may not effectively detect triggers that deviate from known patterns.

4. **Reliance on Domain-Specific Heuristics**: Many defenses depend on heuristics specific to a particular domain, which may not translate well to other domains, reducing their overall effectiveness.

5. **Scalability in Multi-Modal Systems**: Implementing a unified defense framework that operates effectively across multiple modalities (e.g., vision, language, multimodal) poses scalability challenges due to the diverse nature of data representations.
``` 