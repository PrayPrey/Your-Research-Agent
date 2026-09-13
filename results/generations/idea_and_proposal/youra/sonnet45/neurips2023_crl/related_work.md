## Related Work

**Related Papers**

1. **Title**: Towards Interpretable Deep Generative Models via Causal Representation Learning (arXiv preprint)
   - **Authors**: Moran, G. E., & Aragam, B.
   - **Summary**: Introduces CRL from statistical perspective (factor analysis, graphical models, nonparametric statistics), reviews identifiability results (sufficient conditions for latent variable recovery), and discusses implementation strategies for practical CRL deployment. Provides the statistical framework used for automated identifiability verification.
   - **Year**: 2025

2. **Title**: Toward Causal Representation Learning (Proceedings of the IEEE)
   - **Authors**: Schölkopf, B., Locatello, F., Bauer, S., Ke, N. R., Kalchbrenner, N., Goyal, A., & Bengio, Y.
   - **Summary**: Foundational survey that establishes the CRL field, reviews fundamental concepts of causal inference (interventions, counterfactuals, identifiability), relates causality to crucial ML problems (transfer learning, domain generalization), and identifies CRL (discovery of high-level causal variables from low-level observations) as central AI problem.
   - **Year**: 2021

3. **Title**: Causality-Medical-Image-Domain-Generalization (GitHub: cheng-01037, IEEE Transactions on Medical Imaging)
   - **Authors**: Not specified
   - **Summary**: Provides single-source domain generalization for medical image segmentation using encoder-decoder with causal latent variables, multi-site generalization objective handling clinical confounding, and data processing pipeline for medical imaging. Serves as template architecture blueprint for medical imaging CRL.
   - **Year**: 2022

4. **Title**: Simplified Artificial Neural Network Configuration in R Programming for Predictive Modelling (Journal of Intelligent & Fuzzy Systems)
   - **Authors**: Razak, T. R., Jarimi, H., & Ahmad, E. Z.
   - **Summary**: Addresses difficulty of ANN configuration by providing straightforward methodology, systematic and comprehensive framework ensuring accessibility for practitioners without advanced ML knowledge. Implements two-tier abstraction (novice auto-config, expert manual tuning) with empirical results showing success rate increased from 45% to 82% for non-ML-experts.
   - **Year**: 2023

5. **Title**: AI-Driven Quality Assurance Framework for Inclusive Government and E-Commerce Web Services (International Journal of Web Services Research)
   - **Authors**: Kaur, P., & Gupta, V.
   - **Summary**: Integrated AI-driven QA framework bridging usability, accessibility, and emerging technologies. Aligns with WCAG 2.1 and ISO/IEC 25010 standards, emphasizes inclusive design for users of diverse abilities, provides accessibility validation tools with user-centric approach.
   - **Year**: 2025

6. **Title**: A Physics-Informed Machine Learning Framework for Safe and Optimal Control of Autonomous Systems (arXiv preprint)
   - **Authors**: Tayal, M., Singh, A., Kolathaya, S. N. Y., & Bansal, S.
   - **Summary**: Bridges safety and performance in autonomous systems via physics-informed ML, formulates co-optimization as state-constrained optimal control, uses physics-informed ML to approximate HJB equations efficiently, employs conformal prediction for safety guarantees and uncertainty quantification, demonstrates scalable learning for complex, high-dimensional systems.
   - **Year**: 2025

7. **Title**: BISCUIT: Causal Representation Learning from Binary Interactions (UAI Conference)
   - **Authors**: Not specified
   - **Summary**: CRL from binary interaction data (robot-object interactions) with application to pose estimation and manipulation planning. Provides interventional CRL for physical systems and validates future template expansion to robotics domain.
   - **Year**: 2023

8. **Title**: scMultiomeGRN: Single-Cell Multi-Omic Gene Regulatory Network Inference
   - **Authors**: Zhang, Y., et al.
   - **Summary**: Cell-specific gene regulatory network (GRN) inference using single-cell multi-omic data (RNA-seq + ATAC-seq), demonstrates causal structure learning in high-dimensional biological systems. Validates future template expansion to biology domain.
   - **Year**: 2025

9. **Title**: Marrying Causal Representation Learning with Dynamical Systems (arXiv preprint)
   - **Authors**: Lachapelle, S., et al.
   - **Summary**: CRL for dynamical systems (wind simulator, climate data) with temporal causal discovery in continuous-time systems. Shows CRL versatility beyond static imaging and demonstrates template generalizability across domains.
   - **Year**: 2024

10. **Title**: CausalVerse: Benchmark Platform for Causal Representation Learning
    - **Authors**: Not specified
    - **Summary**: Standardized benchmarks for CRL evaluation with unified evaluation protocols (identifiability metrics, downstream task performance) and leaderboard for CRL methods. Focuses on evaluation methodology for measuring CRL quality.
    - **Year**: 2025

11. **Title**: py-why/causal-learn: Python Library for Causal Discovery (GitHub)
    - **Authors**: Not specified (py-why organization: Microsoft Research + community)
    - **Summary**: Comprehensive causal discovery algorithms (PC, FCI, GES, LINGAM), independence tests and score functions for causal structure learning. Well-maintained, production-ready general-purpose causal discovery library.
    - **Year**: Not specified

**Key Challenges**

1. **Theory-Practice Gap in CRL Applications**: CRL requires PhD-level understanding of causal inference theory (DAGs, interventions, identifiability conditions) for correct deployment, creating significant expertise barriers that limit real-world adoption in practical domains like medical imaging.

2. **Accessibility-Theoretical Rigor Trade-off**: Simplifying interfaces to reduce expertise requirements risks hiding critical causal assumptions, leading to theoretically unsound models, while requiring full expertise limits adoption to small research communities.

3. **Template Generalization Across Domains**: Medical imaging CRL patterns need to generalize across diverse tasks (classification, segmentation, diagnosis) and imaging modalities (skin lesions, chest X-rays, brain MRI) while maintaining causal correctness.

4. **Identifiability Verification Computational Cost**: Statistical identifiability tests must be computed efficiently (1-5 minutes) for practical deployment without frustrating users with long wait times, especially for large-scale models with many latent variables.

5. **Verification False Positive/Negative Balance**: Automated identifiability checkers must balance precision and recall to avoid both overly conservative rejections (frustrating users) and missed violations (deploying theoretically unsound models).

6. **Domain Expert Causal Reasoning Translation**: Medical causal reasoning (clinical, observational) differs from statistical causality (interventional, mechanistic), requiring careful translation in human-readable explanations and interface design.

7. **Small Template Library Coverage**: Initial implementations rely on limited validated templates (e.g., single cheng-01037 pattern), which may be insufficient for diverse medical imaging tasks requiring custom architectures.

8. **User Study Recruitment Logistics**: Recruiting sufficient numbers (5-10) of qualified medical imaging domain experts willing to participate in 4-8 hour studies is time-intensive and requires institutional partnerships.
