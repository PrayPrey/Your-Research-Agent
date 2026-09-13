## Related Work

**Related Papers**
1. **Title**: Compositional generalization in multi-armed bandits
   - **Authors**: Saanum, Schulz, Speekenbrink
   - **Summary**: Demonstrates that humans transfer knowledge of simpler reward structures to make compositional generalizations about rewards in complex contexts. Serves as core inspiration for hierarchical primitive decomposition approaches.
   - **Year**: 2021

2. **Title**: Credit assignment in hierarchical option transfer
   - **Authors**: Li, Xia, Dong, Collins
   - **Summary**: Investigates precise credit assignment in hierarchical option learning, showing that humans reliably create new options without interfering with old ones. Provides mechanism for primitive reuse vs. creation decision.
   - **Year**: 2022

3. **Title**: The Risks of Invariant Risk Minimization
   - **Authors**: Rosenfeld, Ravikumar, Risteski
   - **Summary**: Demonstrates that IRM can fail catastrophically unless test data is sufficiently similar to training data. Motivates compositional approaches to provide additional robustness.
   - **Year**: 2020

4. **Title**: Does Invariant Risk Minimization Capture Invariance?
   - **Authors**: Kamath, Tangella, Sutherland, Srebro
   - **Summary**: Identifies significant gap between linear IRM variant and full formulation, showing IRM is fragile to sampling. Informs hierarchical structure design considerations.
   - **Year**: 2021

5. **Title**: DomainBed
   - **Authors**: Gulrajani, Lopez-Paz
   - **Summary**: Provides standardized evaluation framework across 9 algorithms and 7 datasets for domain generalization research. Serves as primary validation benchmark.
   - **Year**: 2020

6. **Title**: SWAD: Domain Generalization by Seeking Flat Minima
   - **Authors**: Cha et al.
   - **Summary**: Achieves state-of-the-art performance on DomainBed through flat minima optimization. Serves as primary comparison baseline.
   - **Year**: 2021

7. **Title**: The Clever Hans Mirage: A Comprehensive Survey on Spurious Correlations
   - **Authors**: Ye et al.
   - **Summary**: Comprehensive survey confirming the lack of unified framework for addressing spurious correlations as an active research gap, validating the importance of this problem area.
   - **Year**: 2024

8. **Title**: Rethinking the Evaluation Protocol of Domain Generalization (CVPR 2024)
   - **Authors**: Yu et al.
   - **Summary**: Identifies that current DomainBed protocol has test data leakage risks from ImageNet pretraining and oracle model selection procedures.
   - **Year**: 2024

9. **Title**: When Are Learning Biases Equivalent?
   - **Authors**: Mehta
   - **Summary**: Establishes information-theoretic conditions for method equivalence. Provides differentiation target as CIL offers dynamic learning architecture versus static theory.
   - **Year**: 2025

**Key Challenges**
1. **IRM Catastrophic Failure**: Invariant Risk Minimization can fail catastrophically when test data is not sufficiently similar to training data, limiting its reliability for domain generalization.

2. **Gap Between IRM Theory and Practice**: Significant discrepancy exists between linear IRM variants and the full formulation, with IRM showing fragility to sampling variations.

3. **Lack of Unified Framework**: No unified framework exists for addressing spurious correlations, representing an active research gap in the field.

4. **Evaluation Protocol Leakage**: Current DomainBed evaluation protocols suffer from test data leakage risks due to ImageNet pretraining and oracle model selection procedures.

5. **Static vs. Dynamic Learning Architectures**: Existing theoretical frameworks provide static analysis of learning biases, lacking dynamic learning architecture capabilities.
