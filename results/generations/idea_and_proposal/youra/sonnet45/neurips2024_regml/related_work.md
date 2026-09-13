## Related Work

**Related Papers**

1. **Title**: Privacy and Fairness in Federated Learning: On the Perspective of Tradeoff
   - **Authors**: Chen et al.
   - **Summary**: First systematic documentation that differential privacy (DP) exacerbates unfairness in federated learning; demonstrated that DP noise disproportionately affects minority groups and fairness interventions leak privacy. Showed demographic disparity increased 15-30% when ε decreased from 10 to 1 on Adult Income dataset.
   - **Year**: 2023

2. **Title**: A Comprehensive Survey of Privacy-preserving Federated Learning
   - **Authors**: Yin et al.
   - **Summary**: Comprehensive survey providing 5W-scenario-based taxonomy of privacy-preserving federated learning (PPFL), reviewing differential privacy, secure multi-party computation, and homomorphic encryption in FL contexts. Analyzes FL architectural patterns (FedAvg, FedProx, FedOpt) and privacy-utility tradeoffs.
   - **Year**: 2021

3. **Title**: Privacy-Preserving Aggregation in Federated Learning: A Survey
   - **Authors**: Liu et al.
   - **Summary**: Survey of privacy-preserving aggregation protocols in federated learning, covering secure aggregation, differential privacy aggregation, and functional encryption. Identifies aggregation as the critical privacy bottleneck in FL.
   - **Year**: 2022

4. **Title**: Federated Machine Learning, Privacy-Enhancing Technologies, and Data Protection Laws
   - **Authors**: Brauneck et al.
   - **Summary**: Legal and technical analysis proving that federated learning combined with secure multi-party computation and differential privacy satisfies GDPR Articles 5 (data minimization), 25 (privacy by design), and 32 (security). Establishes ε-DP with ε ≤ 2.0 as "adequate protection" under GDPR.
   - **Year**: 2023

5. **Title**: Algorithmic Fairness and the EU AI Act
   - **Authors**: Deck et al.
   - **Summary**: Legal analysis bridging AI Act transparency and fairness requirements with algorithmic fairness research. Provides interpretation showing AI Act Article 10 (data governance) implies fairness requirements for high-risk systems.
   - **Year**: 2024

6. **Title**: XAI and AI Act Transparency Gap
   - **Authors**: Gyevnar et al.
   - **Summary**: Analysis identifying the gap between explainable AI (XAI) research capabilities and AI Act legal transparency requirements, highlighting challenges in legal-to-technical translation for regulatory ML compliance.
   - **Year**: 2023

7. **Title**: NSGA-Net: Neural Architecture Search using Multi-Objective Genetic Algorithm
   - **Authors**: Not specified
   - **Summary**: Demonstrates application of multi-objective optimization to neural architecture search, computing Pareto frontier of model accuracy versus computational cost (FLOPs, latency), providing precedent for Pareto methods in machine learning contexts.
   - **Year**: 2019

8. **Title**: Fairness-Aware Agnostic Federated Learning
   - **Authors**: Not specified
   - **Summary**: Proposes fairness-aware client selection methods for federated learning to achieve fairness objectives without privacy mechanisms.
   - **Year**: Not specified

9. **Title**: Ditto: Fair and Robust Federated Learning Through Personalization
   - **Authors**: Not specified
   - **Summary**: Addresses per-client fairness in federated learning through personalization techniques, achieving fairness-aware aggregation but lacking privacy mechanisms.
   - **Year**: Not specified

10. **Title**: Pareto Efficiency in Resource Allocation (Foundational Economics Theory)
   - **Authors**: Pareto (1906), formalized in microeconomic theory
   - **Summary**: Core principle establishing that Pareto frontier characterizes optimal resource allocations where improving one objective requires worsening another. Provides mathematical formalism including Pareto dominance, Pareto frontier, and scalarization methods.
   - **Year**: 1906

11. **Title**: Multicriteria Optimization (Operations Research Methods)
   - **Authors**: Ehrgott
   - **Summary**: Comprehensive treatment of multi-objective optimization techniques including ε-constraint method (fix one objective as constraint, optimize the other), weighted sum method, and reference point methods for generating Pareto solutions.
   - **Year**: 2005

**Key Challenges**

1. **Fairness-Privacy Tradeoff in Federated Learning**: Differential privacy mechanisms exacerbate unfairness because noise disproportionately affects minority groups with smaller sample sizes, while fairness interventions can leak privacy through gradient magnitude information.

2. **Lack of Pareto Optimization Framework**: Existing work documents the fairness-privacy tension empirically (Chen et al. 2023) but provides no optimization framework for systematically navigating the tradeoff or characterizing achievable solutions.

3. **Single-Objective Optimization Limitation**: Privacy-preserving federated learning (PPFL) optimizes only privacy while degrading fairness, and fair federated learning optimizes only fairness while neglecting privacy, leaving no integrated solution for dual-objective optimization.

4. **Regulatory Context Translation Gap**: No systematic method exists for translating qualitative legal requirements (GDPR, AI Act, HIPAA, fair lending laws) into quantitative optimization parameters for machine learning systems.

5. **Fragmented Tooling Landscape**: Organizations deploying federated learning in regulated sectors face fragmented tools—privacy libraries handle only privacy, fairness libraries target centralized ML, and no production-ready solution exists for simultaneous fairness-privacy compliance.

6. **Legal-Technical Alignment Validation**: Legal compliance work provides interpretations of regulations but lacks technical implementation, while technical work lacks validation that implementations actually satisfy legal requirements.

7. **Multi-Jurisdictional Compliance Complexity**: Organizations operating across multiple regulatory contexts (e.g., EU GDPR and US fair lending laws) face conflicting privacy-priority versus fairness-priority requirements with no principled framework for resolution.

8. **Computational Overhead of Multi-Objective Optimization**: Computing Pareto frontiers through extensive hyperparameter sweeps adds significant computational cost compared to single-objective optimization, potentially limiting scalability to large-scale production systems.

9. **Fairness Metric Adequacy for Legal Requirements**: Standard algorithmic fairness metrics (demographic parity, equalized odds) may not fully capture domain-specific legal fairness notions in healthcare, finance, or criminal justice contexts.

10. **Dynamic System Stability**: Federated learning systems face data distribution shifts over time (concept drift, new clients joining), but frontier recomputation overhead may be prohibitive if data shifts frequently in production environments.
