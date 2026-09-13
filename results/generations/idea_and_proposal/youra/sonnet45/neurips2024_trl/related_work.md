## Related Work

**Related Papers**

1. **Title**: TableRAG: A Retrieval Augmented Generation Framework for Heterogeneous Document Reasoning
   - **Authors**: Xiaohan Yu, Pu Jian, Chong Chen
   - **Summary**: Provides SQL-based retrieval architecture for heterogeneous table+text+image document QA, achieving state-of-the-art performance on FinQA (0.78 F1), HybridQA (0.71 F1), and WikiTQ (0.64 F1). Limitation: requires centralized server processing raw sensitive tables (HIPAA/GDPR violation).
   - **Year**: 2025

2. **Title**: VDocRAG: Retrieval-Augmented Generation over Visually-Rich Documents
   - **Authors**: Ryota Tanaka, Taichi Iki, Taku Hasegawa, et al.
   - **Summary**: Provides unified image-format multimodal RAG framework for tables+charts+text that prevents OCR information loss. Superior to text-based RAG on visually-rich documents but has centralized architecture with no privacy preservation.
   - **Year**: 2025

3. **Title**: SecurityBERT: Revolutionizing Cyber Threat Detection With Large Language Models
   - **Authors**: Mohamed Ferrag, Mthandazo Ndhlovu, Norbert Tihanyi, et al.
   - **Summary**: Provides Privacy-Preserving Fixed-Length Encoding (PPFLE) technique achieving 98.2% accuracy with 16.7MB model for network traffic classification. Single-table classification only, extended to multi-table retrieval in the current work.
   - **Year**: 2023

4. **Title**: Federated Learning for Secure and Privacy-Preserving Medical Image Analysis in Decentralized Healthcare Systems
   - **Authors**: M. Muthalakshmi, Karthik Jeyapal, et al.
   - **Summary**: Achieved 98.6% accuracy (vs centralized) using federated split-learning + differential privacy + homomorphic encryption for medical images. Single-modality (images only) with no reasoning capability.
   - **Year**: 2024

5. **Title**: Post-Quantum Privacy-Preserving Federated Learning via Anti-Gradients Leakage Based on Secure Multi-party Computation Techniques
   - **Authors**: Hang-chao Ding, Huayun Tang, Chen Jia, Yanzhao Wang
   - **Summary**: Provides LWE-based Kyber protocol + Shamir secret sharing to prevent gradient leakage in federated learning. Generic federated learning approach (no tables/multimodal support).
   - **Year**: 2024

6. **Title**: Privacy-Preserving Cryptography for Credit Card Reward Systems: A Secure Multi-Party Computation Approach
   - **Authors**: Hirenkumar Patel
   - **Summary**: SMPC enables multi-entity calculations without data exposure in production-deployed fintech systems. Demonstrates practical feasibility of secret sharing + homomorphic encryption for distributed computation.
   - **Year**: 2025

7. **Title**: Federated Learning and NFT-Based Privacy-Preserving Medical-Data-Sharing Scheme for Intelligent Diagnosis in Smart Healthcare
   - **Authors**: Siva Sai, Vikas Hassija, V. Chamola, M. Guizani
   - **Summary**: NFT-based ownership + access control + federated learning for medical diagnosis with blockchain incentive mechanism for data contribution quality.
   - **Year**: 2024

8. **Title**: CARTE: Pretraining and Transfer for Tabular Learning
   - **Authors**: Myung Jun Kim, Léo Grinsztajn, Gaël Varoquaux
   - **Summary**: Graph-based architecture handles unmatched columns without schema matching, addressing cross-table schema heterogeneity. Empirically showed 70% column overlap in real-world cross-organization tables. Requires centralized access to all tables.
   - **Year**: 2024

9. **Title**: TabPFN: Accurate Predictions on Small Data with a Tabular Foundation Model
   - **Authors**: Noah Hollmann, Samuel G. Müller, Lennart Purucker, et al.
   - **Summary**: First successful tabular foundation model that outperforms gradient boosting on small datasets (<10K samples). Centralized classification approach without federated deployment or privacy preservation.
   - **Year**: 2025

10. **Title**: CryptDB: Protecting Confidentiality with Encrypted Query Processing
   - **Authors**: Raluca Ada Popa et al.
   - **Summary**: Order-preserving encryption enables SQL WHERE/JOIN/GROUP BY on encrypted databases. Proves strict homomorphic encryption cannot do SQL (requires OPE which leaks order information).
   - **Year**: 2011

11. **Title**: Deep Learning with Differential Privacy
   - **Authors**: Abadi et al.
   - **Summary**: Establishes ε-differential privacy for federated embeddings with gradient clipping to prevent gradient-based inference attacks.
   - **Year**: 2016

12. **Title**: The Algorithmic Foundations of Differential Privacy
   - **Authors**: Dwork & Roth
   - **Summary**: Provides theoretical foundation for differential privacy bounds and O(ε⁻¹) accuracy degradation analysis.
   - **Year**: 2014

13. **Title**: Intel SGX Explained
   - **Authors**: Costan & Devadas
   - **Summary**: Describes Intel SGX architecture and security model for trusted execution environments.
   - **Year**: 2016

14. **Title**: Foreshadow: Extracting the Keys to the Intel SGX Kingdom with Transient Out-of-Order Execution
   - **Authors**: Van Bulck et al.
   - **Summary**: Analyzes Intel SGX side-channel vulnerabilities including Spectre and Meltdown variants.
   - **Year**: 2018

**Key Challenges**

1. **Privacy-Accuracy Trade-off**: Existing centralized table RAG systems (TableRAG, VDocRAG) achieve high accuracy but violate HIPAA/GDPR regulations by requiring raw sensitive data centralization. Privacy-preserving techniques often degrade accuracy below acceptable thresholds.

2. **SQL on Encrypted Data Limitation**: Strict homomorphic encryption cannot execute SQL queries (only supports arithmetic operations). Order-preserving encryption enables SQL but leaks order information (weaker privacy). Secure enclaves (Intel SGX) enable SQL but introduce hardware trust assumptions and known vulnerabilities.

3. **Multimodal Privacy Preservation**: While federated learning for single-modality tasks (images OR tables) has been demonstrated, extending to multimodal understanding (tables AND charts AND text) with unified privacy preservation remains unexplored.

4. **Federated Schema Heterogeneity**: Cross-organizational tables have varying schemas with only 50-80% column overlap. Privacy-preserving schema matching protocols for federated environments are not well-established in literature.

5. **Real-time vs Privacy Constraint**: Federated aggregation architecture requires coordination time (periodic synchronization), making it incompatible with real-time streaming applications (<1s latency requirements).

6. **Scalability vs Convergence Trade-off**: As number of federated institutions increases (>50), schema heterogeneity and coordination complexity grow, potentially preventing convergence of privacy-preserving protocols.

7. **Regulatory Compliance Verification**: Achieving theoretical privacy guarantees (ε-differential privacy, homomorphic encryption) doesn't automatically ensure regulatory compliance (HIPAA technical safeguards, GDPR Article 32). Gap between cryptographic privacy and legal compliance requirements.

8. **Gradient Leakage in Federated Fine-tuning**: Even without raw data access, gradient-based attacks can expose table statistics during federated LLM fine-tuning. Requires differential privacy noise injection and synthetic data quality validation.

9. **Trusted Execution Environment Vulnerabilities**: Intel SGX has known side-channel attacks (Spectre, Meltdown) requiring fallback protocols when enclave is compromised. Current systems lack explicit failover mechanisms.

10. **Performance Overhead Acceptability**: Homomorphic encryption adds 10-30x latency overhead compared to plaintext operations. Determining acceptable latency thresholds for clinical decision support and other sensitive applications remains domain-specific challenge.
