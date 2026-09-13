1. **Title**: Lie Detector: Unified Backdoor Detection via Cross-Examination Framework (arXiv:2503.16872)
   - **Authors**: Xuan Wang, Siyuan Liang, Dongping Liao, Han Fang, Aishan Liu, Xiaochun Cao, Yu-liang Lu, Ee-Chien Chang, Xitong Gao
   - **Summary**: This paper introduces a unified backdoor detection framework that cross-examines inconsistencies between models from two independent service providers. By integrating central kernel alignment, it measures feature similarity across different architectures and learning paradigms, facilitating precise identification of backdoor triggers. The method also employs fine-tuning sensitivity analysis to distinguish backdoor triggers from adversarial perturbations, reducing false positives.
   - **Year**: 2025

2. **Title**: QSentry: Backdoor Detection for Quantum Neural Networks via Measurement Clustering (arXiv:2511.15376)
   - **Authors**: Shuolei Wang, Zimeng Xiao, Jinjing Shi, Heyuan Shi, Shichao Zhang, Xuelong Li
   - **Summary**: The authors propose QSentry, a framework for detecting backdoors in quantum neural networks. It utilizes a quantum measurement clustering method to identify statistical anomalies in measurement outputs, effectively detecting backdoor-induced distributions. QSentry demonstrates high detection accuracy across various quantum attack scenarios.
   - **Year**: 2025

3. **Title**: ProP: Efficient Backdoor Detection via Propagation Perturbation for Overparametrized Models (arXiv:2411.07036)
   - **Authors**: Tao Ren, Qiongxiu Li
   - **Summary**: ProP introduces a backdoor detection method leveraging statistical output distributions to identify compromised models and their target classes without exhaustive optimization. It introduces the benign score metric to quantify output distributions, distinguishing between benign and backdoored models. ProP operates with minimal assumptions, requiring no prior knowledge of triggers or malicious samples, making it practical for real-world scenarios.
   - **Year**: 2024

4. **Title**: Robust Backdoor Detection for Deep Learning via Topological Evolution Dynamics (arXiv:2312.02673)
   - **Authors**: Xiaoxing Mo, Yechao Zhang, Leo Yu Zhang, Wei Luo, Nan Sun, Shengshan Hu, Shang Gao, Yang Xiang
   - **Summary**: This work presents TED (Topological Evolution Dynamics), a model-agnostic approach for robust backdoor detection. TED views a deep-learning model as a dynamical system, analyzing the evolution trajectories of inputs to outputs. Benign inputs follow natural trajectories, while malicious samples display distinct paths, enabling effective backdoor detection.
   - **Year**: 2023

5. **Title**: AEVA: Black-box Backdoor Detection Using Adversarial Extreme Value Analysis (arXiv:2110.14880)
   - **Authors**: Xijie Huang, Moustafa Alzantot, Mani Srivastava
   - **Summary**: AEVA addresses the black-box hard-label backdoor detection problem by leveraging adversarial extreme value analysis. It identifies adversarial singularities in the adversarial map of backdoor-infected examples, enabling effective detection without access to model parameters or training data.
   - **Year**: 2021

6. **Title**: A Graph Backdoor Detection Method for Data Collection Scenarios
   - **Authors**: Xiaogang Xing, Ming Xu, Bai Y., et al.
   - **Summary**: This paper proposes a backdoor detection method tailored for graph neural networks in data collection scenarios. It focuses on identifying backdoors by analyzing the structural properties and node features within the graph, providing a novel approach to securing graph-based models.
   - **Year**: 2025

7. **Title**: UMD: Unsupervised Model Detection for X2X Backdoor Attacks
   - **Authors**: Zhen Xiang, Zidi Xiong, Bo Li
   - **Summary**: UMD introduces an unsupervised method for detecting X2X backdoor attacks, where multiple source classes are mapped to multiple target classes. It defines a transferability statistic to measure and select putative backdoor class pairs, followed by an aggregation of reverse-engineered trigger sizes for detection inference.
   - **Year**: 2023

8. **Title**: NeuronInspect: Detecting Backdoors in Neural Networks via Output Explanations (arXiv:1911.07399)
   - **Authors**: Xijie Huang, Moustafa Alzantot, Mani Srivastava
   - **Summary**: NeuronInspect detects backdoors by generating explanation heatmaps of the output layer. It identifies attack targets by analyzing the characteristics of these heatmaps, extracting features that measure attributes such as sparsity, smoothness, and persistence, and uses outlier detection to identify backdoor targets.
   - **Year**: 2019

9. **Title**: BAN: Detecting Backdoors Activated by Adversarial Neuron Noise
   - **Authors**: Xiaoyun Xu, Zhuoran Liu, Stefanos Koffas, Shujian Yu, Stjepan Picek
   - **Summary**: BAN improves backdoor feature inversion for detection by incorporating neuron activation information. It adversarially increases the loss of backdoored models with respect to weights to activate the backdoor effect, facilitating differentiation between backdoored and clean models.
   - **Year**: 2024

10. **Title**: Backdoor Attack Detection via Prediction Trustworthiness Assessment
    - **Authors**: [Authors not specified]
    - **Summary**: This study proposes a defense mechanism that assesses the trustworthiness of model predictions to detect backdoor attacks. It evaluates the consistency and reliability of predictions, identifying anomalies indicative of backdoor presence.
    - **Year**: 2024

**Key Challenges**:

1. **Generalization Across Diverse Backdoor Types**: Developing detection methods that effectively identify various backdoor attacks without prior knowledge of the attack strategy remains a significant challenge.

2. **Minimal Clean Data Requirements**: Creating detection frameworks that operate effectively with limited access to clean data is crucial for practical deployment.

3. **Computational Efficiency**: Ensuring that backdoor detection methods are computationally efficient to facilitate real-time or large-scale applications is a persistent challenge.

4. **Robustness Against Adaptive Attacks**: Designing detection mechanisms that remain effective against attackers who adapt their strategies to evade existing defenses is essential.

5. **Cross-Domain Applicability**: Extending backdoor detection techniques beyond computer vision to domains like natural language processing and federated learning requires addressing domain-specific challenges. 