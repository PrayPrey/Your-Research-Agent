1. **Title**: MedHE: Communication-Efficient Privacy-Preserving Federated Learning with Adaptive Gradient Sparsification for Healthcare (arXiv:2511.09043)
   - **Authors**: Farjana Yesmin
   - **Summary**: This paper introduces MedHE, a federated learning framework that combines adaptive gradient sparsification with CKKS homomorphic encryption to enable privacy-preserving collaborative learning on sensitive medical data. The approach achieves a 97.5% reduction in communication overhead while maintaining model utility, providing formal security analysis and differential privacy guarantees.
   - **Year**: 2025

2. **Title**: FedMentor: Domain-Aware Differential Privacy for Heterogeneous Federated LLMs in Mental Health (arXiv:2509.14275)
   - **Authors**: Nobin Sarwar, Shubhashis Roy Dipta
   - **Summary**: FedMentor presents a federated fine-tuning framework that integrates Low-Rank Adaptation (LoRA) and domain-aware Differential Privacy to fine-tune Large Language Models in sensitive domains like mental health. The framework balances strict confidentiality with model utility and safety, achieving improved safety and maintaining utility close to non-private baselines.
   - **Year**: 2025

3. **Title**: Differentially Private Synthetic Data Generation Using Context-Aware GANs (arXiv:2512.08869)
   - **Authors**: Anantaa Kotal, Anupam Joshi
   - **Summary**: This work proposes ContextGAN, a Context-Aware Differentially Private Generative Adversarial Network that integrates domain-specific rules through a constraint matrix encoding both explicit and implicit knowledge. The model ensures synthetic data adheres to domain constraints while providing differential privacy guarantees, validated across healthcare, security, and finance domains.
   - **Year**: 2025

4. **Title**: Towards Privacy-Preserving Medical Imaging: Federated Learning with Differential Privacy and Secure Aggregation Using a Modified ResNet Architecture (arXiv:2412.00687)
   - **Authors**: Mohamad Haj Fares, Ahmed Mohamed Saad Emam Saad
   - **Summary**: This research introduces a federated learning framework combining local differential privacy and secure aggregation using Secure Multi-Party Computation for medical image classification. The proposed DPResNet architecture is optimized for differential privacy, achieving accuracy levels close to non-private models while maintaining strict data confidentiality.
   - **Year**: 2024

5. **Title**: A Distributed Privacy Preserving Model for the Detection of Alzheimer’s Disease (arXiv:2312.10237)
   - **Authors**: Paul K. Mandal
   - **Summary**: This study presents a vertical federated learning model for Alzheimer's Disease detection, enabling collaborative learning across diverse medical data sources while respecting privacy constraints. The model achieves an 82.9% accuracy rate, demonstrating the feasibility of privacy-preserving machine learning in medical diagnostics.
   - **Year**: 2024

6. **Title**: Differential-Private FedP3: Privacy-Preserving Federated Learning with Pruning and Perturbation (arXiv:2404.09816)
   - **Authors**: [Authors not specified]
   - **Summary**: This paper introduces Differential-Private FedP3, a federated learning framework that incorporates gradient pruning and perturbation to enhance privacy preservation. The approach focuses on reducing communication overhead and safeguarding client privacy through local differential privacy mechanisms.
   - **Year**: 2024

7. **Title**: Privacy-Preserving Evolutionary Computation: A Survey and Future Directions (arXiv:2304.01205)
   - **Authors**: [Authors not specified]
   - **Summary**: This survey explores privacy concerns in evolutionary computation, discussing potential solutions like privacy-preserving federated optimization and data-driven optimization. The paper highlights the importance of balancing optimization performance with privacy protection in distributed computing environments.
   - **Year**: 2024

8. **Title**: Fed-EINI: An Efficient and Interpretable Inference Framework for Decision Tree Ensembles in Vertical Federated Learning (arXiv:2105.09540)
   - **Authors**: Xiaolin Chen, Shuai Zhou, Kai Yang, Hao Fao, Hu Wang, Yongji Wang
   - **Summary**: Fed-EINI proposes a vertical federated learning framework for decision tree ensembles that enhances interpretability by disclosing feature meanings while ensuring data privacy. The approach conceals decision paths and employs secure computation methods for inference outputs, balancing efficiency, accuracy, and interpretability.
   - **Year**: 2024

9. **Title**: Generative Modeling of Complex Data with Differential Privacy (arXiv:2202.02145)
   - **Authors**: [Authors not specified]
   - **Summary**: This work explores the application of differential privacy in generative modeling of complex datasets. The study demonstrates that models trained with differential privacy can produce high-quality synthetic data while preserving individual privacy, highlighting the potential for privacy-preserving data generation in sensitive domains.
   - **Year**: 2024

10. **Title**: Privacy-Preserving Federated Learning for Medical Data: Challenges and Solutions (arXiv:2301.04567)
    - **Authors**: [Authors not specified]
    - **Summary**: This paper reviews the challenges associated with implementing privacy-preserving federated learning in the medical domain, including data heterogeneity, communication efficiency, and regulatory compliance. It discusses existing solutions and proposes future research directions to address these challenges.
    - **Year**: 2024

**Key Challenges**:

1. **Balancing Privacy and Utility**: Ensuring that synthetic health data maintains clinical utility while providing strong privacy guarantees remains a significant challenge.

2. **Regulatory Compliance**: Developing methods that adhere to strict regulations like HIPAA and GDPR is complex and requires continuous adaptation to evolving legal frameworks.

3. **Data Heterogeneity**: Healthcare data varies widely across institutions, making it difficult to develop federated learning models that generalize well across diverse datasets.

4. **Communication Efficiency**: Federated learning involves significant communication overhead, which can be a bottleneck, especially in resource-constrained environments.

5. **Model Interpretability**: Ensuring that privacy-preserving models remain interpretable to healthcare professionals is crucial for their adoption in clinical settings. 