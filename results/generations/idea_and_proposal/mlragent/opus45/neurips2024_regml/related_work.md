1. **Title**: zkUnlearner: A Zero-Knowledge Framework for Verifiable Unlearning with Multi-Granularity and Forgery-Resistance (arXiv:2509.07290)
   - **Authors**: Nan Wang, Nan Wu, Xiangyu Hui, Jiafan Wang, Xin Yuan
   - **Summary**: This paper introduces zkUnlearner, a zero-knowledge framework designed for verifiable machine unlearning. It supports multi-granularity unlearning (sample-level, feature-level, and class-level) and incorporates forgery-resistant mechanisms. The framework employs a bit-masking technique to enable selective zero-knowledge proofs for gradient descent algorithms, ensuring compatibility with various proof systems.
   - **Year**: 2025

2. **Title**: ZK-APEX: Zero-Knowledge Approximate Personalized Unlearning with Executable Proofs (arXiv:2512.09953)
   - **Authors**: Mohammad M Maheri, Sunil Cotterill, Alex Davidson, Hamed Haddadi
   - **Summary**: ZK-APEX presents a zero-shot personalized unlearning method that operates directly on personalized models without retraining. It combines sparse masking with a compensation step using a blockwise empirical Fisher matrix to create a curvature-aware update. Paired with Halo2 zero-knowledge proofs, it enables providers to verify the correct application of unlearning transformations without revealing private data or personalized parameters.
   - **Year**: 2025

3. **Title**: TruVRF: Towards Triple-Granularity Verification on Machine Unlearning (arXiv:2408.06063)
   - **Authors**: Chunyi Zhou, Anmin Fu, Zhiyang Dai
   - **Summary**: TruVRF introduces a non-invasive unlearning verification framework operating at class-, volume-, and sample-level granularities. It includes three Unlearning-Metrics designed to detect dishonest servers: Unlearning-Metric-I checks class alignment, Unlearning-Metric-II verifies sample count, and Unlearning-Metric-III confirms specific sample deletion. The framework demonstrates robust performance across various datasets and unlearning frameworks.
   - **Year**: 2024

4. **Title**: Offset Unlearning for Large Language Models (arXiv:2404.11045)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This work addresses the challenge of unlearning specific information from large language models (LLMs). It introduces a method that focuses on offsetting the learned representations associated with the data to be unlearned, aiming to mitigate the entanglement of knowledge within the model. The approach is evaluated on the TOFU benchmark, demonstrating its effectiveness in removing target information while preserving the model's utility on other data.
   - **Year**: 2024

5. **Title**: Towards Probabilistic Verification of Machine Unlearning (arXiv:2003.04247)
   - **Authors**: David Marco Sommer, Liwei Song, Sameer Wagh, Prateek Mittal
   - **Summary**: This paper proposes a formal framework for verifying machine unlearning in the context of machine learning as a service (MLaaS). It introduces a backdoor-based verification mechanism that allows users to probabilistically verify data deletion requests with high confidence. The approach is evaluated across various network architectures and datasets, demonstrating minimal impact on model accuracy while providing effective verification of unlearning.
   - **Year**: 2020

6. **Title**: Personhood Credentials (arXiv:2408.07892)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This paper outlines the design requirements for a personhood credentialing system, balancing user privacy with the need to prevent deceptive activities at scale. It discusses enrollment and usage processes, emphasizing privacy-preserving mechanisms such as zero-knowledge proofs to ensure that service providers learn nothing beyond the validity of the credential.
   - **Year**: 2024

7. **Title**: Perfect Zero Knowledge for Quantum Multiprover Interactive Proofs (arXiv:1905.11280)
   - **Authors**: Alex B. Grilo, William Slofstra, Henry Yuen
   - **Summary**: This work explores the relationship between multiprover interactive proofs, quantum entanglement, and zero-knowledge proofs. It demonstrates that every MIP* protocol can be transformed into an equivalent zero-knowledge MIP* protocol, preserving the completeness-soundness gap. This result provides a quantum analogue to classical zero-knowledge proofs in multiprover interactive protocols.
   - **Year**: 2019

**Key Challenges:**

1. **Computational Efficiency**: Developing unlearning methods that are computationally efficient and scalable, especially for large-scale models, remains a significant challenge.

2. **Formal Guarantees**: Ensuring that unlearning methods provide formal guarantees of data removal without compromising model performance is complex.

3. **Verification Mechanisms**: Creating robust and tamper-proof verification mechanisms that can be independently audited to demonstrate compliance with regulations like the GDPR is essential.

4. **Privacy Preservation**: Balancing the need for verifiable unlearning with the requirement to preserve user privacy, especially when using cryptographic methods like zero-knowledge proofs, is challenging.

5. **Knowledge Entanglement**: Addressing the issue of knowledge entanglement, where unlearning specific data may inadvertently affect related information within the model, requires careful consideration. 