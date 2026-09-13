## Related Work

**Related Papers**

1. **Title**: Mission Critical (Rolf+ 2024)
   - **Authors**: Rolf et al.
   - **Summary**: Demonstrates satellite data as a distinct modality with specific failure modes when treated with standard computer vision methods. Validates domain-specific failure modes in agricultural ML systems.
   - **Year**: 2024
   - **Additional Info**: 75 citations, Semantic Scholar ID: 0385c1fa107ce68db9f988547bf2d7b708a0c748

2. **Title**: WILDS Benchmark (Koh+ Stanford 2021)
   - **Authors**: Koh et al.
   - **Summary**: Provides real-world distribution shift degradation documentation including geographic transfer failures in FMoW and hospital transfer failures in Camelyon. Provides failure case dataset for taxonomy construction.
   - **Year**: 2021

3. **Title**: Suitability Filter (Pouget+ 2025)
   - **Authors**: Pouget et al.
   - **Summary**: Empirically validates that covariate shift detection during validation predicts deployment performance degradation. Critical for validating validation-to-deployment correlation.
   - **Year**: 2025

4. **Title**: ML4CFD (Yagoubi+ 2024)
   - **Authors**: Yagoubi et al.
   - **Summary**: Shows community demand for out-of-distribution evaluation in computational fluid dynamics applications of machine learning.
   - **Year**: 2024
   - **Additional Info**: Semantic Scholar ID: f5ef710b90030de4a5a26f69d965e156c7e9ce2a

5. **Title**: Minimax Regret Optimization (Agarwal & Zhang 2022)
   - **Authors**: Agarwal and Zhang
   - **Summary**: Provides theoretical explanation for why reactive approaches to ML robustness are insufficient, supporting the need for proactive risk assessment.
   - **Year**: 2022
   - **Additional Info**: 36 citations, Semantic Scholar ID: 4fe3f3e113334998114211f2bb9ff1659100fc14

6. **Title**: FMEA (Failure Mode and Effects Analysis)
   - **Authors**: Not specified
   - **Summary**: Foundational reliability engineering framework providing systematic failure enumeration and Risk Priority Number (RPN) framework for risk assessment across various domains.
   - **Year**: Not specified (60+ years of development in reliability engineering)

7. **Title**: Software/Cybersecurity FMEA
   - **Authors**: Not specified
   - **Summary**: Provides precedent for applying FMEA methodology to probabilistic domains beyond traditional mechanical/hardware systems.
   - **Year**: Not specified

8. **Title**: OODRobustBench
   - **Authors**: Not specified
   - **Summary**: Provides evaluation protocol for out-of-distribution robustness assessment, relevant for the Detection dimension of ML-RPN scoring.
   - **Year**: Not specified
   - **Additional Info**: github.com/oodrobustbench/oodrobustbench

9. **Title**: RobustMLDS'24 Workshop
   - **Authors**: Not specified (workshop proceedings)
   - **Summary**: Validates the existence of Gap 1 (negative results documentation needed) in the ML robustness community.
   - **Year**: 2024

**Key Challenges**

1. **Reactive vs. Proactive Risk Assessment**: Current ML robustness tools (WILDS, OODRobustBench) document failures post-hoc after deployment, lacking systematic pre-deployment risk assessment frameworks.

2. **Lack of Systematic Failure Mode Documentation**: Agricultural ML systems lack structured taxonomies for classifying failure patterns by mechanism (temporal drift, spatial transfer) rather than just symptoms (accuracy drop).

3. **Domain-Specific Failure Modes**: Standard computer vision methods fail when applied to distinct modalities like satellite data in agricultural contexts, requiring domain-specific approaches.

4. **Validation-Deployment Gap**: Limited empirical validation that validation-stage indicators (OOD performance, calibration error) correlate with real-world deployment failures.

5. **Probabilistic vs. Deterministic FMEA Application**: Traditional FMEA assumes deterministic cause-effect relationships, but ML failures are probabilistic and context-dependent, requiring adaptation of FMEA methodology.

6. **Literature Bias in Failure Documentation**: Published academic failures may not represent the full spectrum of industry deployment failures due to publication bias toward positive results.

7. **Context-Dependent Generalization**: ML failures exhibit high context-dependency where the same algorithm architecture may succeed in one geographic region/crop type but fail in another, requiring context-conditioned risk assessment.

8. **Expert Subjectivity in Risk Scoring**: ML-RPN Severity scoring requires expert judgment for agriculture impact assessment despite structured rubrics, introducing potential subjectivity.

9. **Negative Results Documentation Gap**: Workshop call-for-papers (RobustMLDS'24) explicitly identifies need for infrastructure to document and share negative results in ML robustness research.

10. **Cross-Domain Generalization Unknown**: Failure patterns identified in agricultural ML may not generalize to other sustainability domains (climate forecasting, biodiversity monitoring, energy systems) without empirical validation.
