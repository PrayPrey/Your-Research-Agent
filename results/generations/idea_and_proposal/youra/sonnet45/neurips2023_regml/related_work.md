## Related Work

**Related Papers**
1. **Title**: Data Privacy and Trustworthy ML (Strobel & Shokri, 2022)
   - **Authors**: Strobel, Shokri
   - **Summary**: Identifies privacy risks in query-based explainability methods, demonstrating that LIME/SHAP queries can enable membership inference and model extraction attacks without proposing solutions.
   - **Year**: 2022

2. **Title**: Bridging the Gap in XAI (Seth & Sankarapu, 2025)
   - **Authors**: Seth, Sankarapu
   - **Summary**: Proposes "Governance by Metrics" paradigm establishing the regulatory need for privacy-preserving explanations but provides only a conceptual framework without technical implementation.
   - **Year**: 2025

3. **Title**: POTA: Pipelined Oblivious Transfer Acceleration (Zhang et al., 2025)
   - **Authors**: Zhang et al.
   - **Summary**: Achieves 192-597× FPGA hardware speedup for Secure Multi-Party Computation on CNNs, enabling practical encrypted inference but not yet applied to explainability workloads.
   - **Year**: 2025

4. **Title**: Scalable Cryptography for Trustworthy ML in LLM Era (Tan, 2025)
   - **Authors**: Tan
   - **Summary**: Develops MPC techniques for billion-parameter language models focusing on secure training and inference, validating that SMPC scales to modern architectures.
   - **Year**: 2025

5. **Title**: Practical Secure Aggregation for Federated Learning (Bonawitz et al., 2017)
   - **Authors**: Bonawitz et al.
   - **Summary**: Presents secure aggregation protocol for federated learning that prevents servers from learning individual model updates, addressing cross-silo privacy rather than single-model query privacy.
   - **Year**: 2017

6. **Title**: An Information Geometric Approach to Local Privacy (Zamani et al., 2025)
   - **Authors**: Zamani et al.
   - **Summary**: Introduces mutual information minimization framework for optimal local differential privacy budget allocation in distributed data collection settings.
   - **Year**: 2025

7. **Title**: The Algorithmic Foundations of Differential Privacy (Dwork & Roth, 2014)
   - **Authors**: Dwork, Roth
   - **Summary**: Establishes fundamental differential privacy theory including composition theorems, post-processing immunity, and DP mechanism design that forms the privacy accounting framework.
   - **Year**: 2014

8. **Title**: Federated SHAP (Dhiya et al., 2025)
   - **Authors**: Dhiya et al.
   - **Summary**: Computes SHAP values across multiple data silos in federated learning using secure aggregation of per-silo Shapley contributions, addressing cross-silo data privacy.
   - **Year**: 2025

9. **Title**: EU AI Act, Stakeholder Needs, and XAI (Hummel et al., 2025)
   - **Authors**: Hummel et al.
   - **Summary**: Maps EU AI Act requirements to explainability techniques, providing conceptual framework without addressing privacy considerations.
   - **Year**: 2025

10. **Title**: Combined Rule-Based and ML Approach for Automated GDPR Compliance Checking (El Hamdani et al., 2021)
    - **Authors**: El Hamdani et al.
    - **Summary**: Develops automated GDPR compliance verification framework for data processing activities but does not extend to ML model explainability.
    - **Year**: 2021

11. **Title**: Tradeoffs between Privacy, Fairness and Utility in Federated Learning (Sun et al., 2023)
    - **Authors**: Sun et al.
    - **Summary**: Formalizes privacy-utility-fairness Pareto frontier in federated learning with differential privacy and fairness constraints.
    - **Year**: 2023

12. **Title**: Secure Multi-Party Computation (Goldreich, 1998)
   - **Authors**: Goldreich
   - **Summary**: Provides foundational security proofs for multi-party computation under honest-but-curious adversary model establishing cryptographic privacy guarantees.
   - **Year**: 1998

13. **Title**: Secret Sharing Schemes (Shamir, 1979)
   - **Authors**: Shamir
   - **Summary**: Introduces fundamental secret sharing technique enabling encrypted computational environments without revealing inputs, foundational for SMPC protocols.
   - **Year**: 1979

14. **Title**: PATE Framework (Papernot et al., 2017)
   - **Authors**: Papernot et al.
   - **Summary**: Proposes Private Aggregation of Teacher Ensembles for training differentially private surrogate models that can be explained, achieving ~0.6 fidelity.
   - **Year**: 2017

15. **Title**: LIME: Local Interpretable Model-Agnostic Explanations (Ribeiro et al., 2016)
   - **Authors**: Ribeiro et al.
   - **Summary**: Introduces model-agnostic post-hoc explainability method through local perturbations, serving as baseline non-private explanation approach.
   - **Year**: 2016

16. **Title**: Membership Inference Attacks (Shokri et al., 2017)
   - **Authors**: Shokri et al.
   - **Summary**: Demonstrates membership inference attacks using shadow models to predict whether data points were in training sets, establishing baseline privacy auditing methodology.
   - **Year**: 2017

**Key Challenges**
1. **Privacy-Utility Tradeoff in Query-Based Explanations**: Traditional per-query differential privacy adds noise to each model prediction independently, resulting in O(N) privacy cost that forces a severe tradeoff between privacy guarantees and explanation fidelity, achieving only ρ < 0.3 at regulatory privacy levels (ε=1.0) for N=5000 queries.

2. **Computational Overhead of SMPC**: Secure Multi-Party Computation protocols for encrypted inference typically impose 100x computational overhead on CPU implementations, making real-time privacy-preserving explanations impractical without hardware acceleration.

3. **Cross-Silo vs. Single-Model Privacy**: Existing federated explainability methods (Federated SHAP) address cross-silo data privacy in multi-organization settings but do not solve the single-model query privacy problem where repeated queries to a single model enable membership inference and model extraction attacks.

4. **Trusted Aggregator Requirement**: SMPC protocols under honest-but-curious adversary model require at least one trusted party to perform secure aggregation, creating a single point of trust that may be unacceptable in adversarial multi-stakeholder deployments.

5. **Scalability to Large Models**: Secure Multi-Party Computation complexity grows with model size, making feasibility unclear for very large models (>1B parameters like GPT-4) without approximation techniques that may compromise security guarantees.

6. **Regulatory Compliance Gap**: GDPR requires both explainability (Article 22: Right to Explanation) and privacy (Article 5: Privacy by Design), but existing solutions force practitioners to choose between high-fidelity explanations or strong privacy guarantees, with no clear technical path to satisfy both simultaneously.

7. **Adaptive Adversary Threats**: Query correlation in explainability methods (LIME perturbations are sampled near the original input) may leak information to adaptive adversaries who observe query patterns, potentially requiring stronger privacy guarantees than standard differential privacy analysis suggests.

8. **Hardware Acceleration Availability**: Near-real-time privacy-preserving explanations require specialized FPGA accelerators (e.g., POTA) that may not be available in many deployment environments, limiting practical applicability to organizations with advanced hardware infrastructure.
