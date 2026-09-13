## Related Work

**Related Papers**
1. **Title**: Exposing the Limitations of Molecular Machine Learning with Activity Cliffs
   - **Authors**: van Tilborg, Alenicheva, Grisoni
   - **Summary**: Demonstrates that all 24 evaluated ML methods struggle with activity cliffs and provides the MoleculeACE benchmark as an evaluation framework for this problem.
   - **Year**: 2022

2. **Title**: Chemprop: A Machine Learning Package for Chemical Property Prediction
   - **Authors**: Heid et al.
   - **Summary**: Introduces D-MPNN with uncertainty quantification support, achieving state-of-the-art performance in molecular property prediction.
   - **Year**: 2023

3. **Title**: Conformal Prediction for Uncertainty Quantification in Drug-Target Interaction Prediction (arXiv:2505.18890)
   - **Authors**: Rakhshaninejad et al.
   - **Summary**: Proposes cluster-conditioned conformal prediction that achieves tighter prediction intervals and reliable subgroup coverage for drug-target interaction tasks.
   - **Year**: 2025

4. **Title**: Conformal prediction for uncertainty quantification in dynamic biological systems
   - **Authors**: Portela, Banga, Matabuena
   - **Summary**: Establishes that conformal prediction provides non-asymptotic guarantees even under model misspecification in biological systems.
   - **Year**: 2025

5. **Title**: CoDrug: Conformal Drug Property Prediction with Density Estimation under Covariate Shift (NeurIPS 2023)
   - **Authors**: Laghuvarapu, Lin, Sun
   - **Summary**: Combines energy-based density estimation with KDE to reduce coverage gap by 35% in drug property prediction under covariate shift.
   - **Year**: 2023

6. **Title**: Standard Split Conformal Prediction
   - **Authors**: Not specified
   - **Summary**: Provides marginal coverage guarantees without conditional guarantees, serving as a baseline conformal prediction method.
   - **Year**: Not specified

7. **Title**: Conformal Prediction for Molecular Properties under Label Shift
   - **Authors**: Lee et al.
   - **Summary**: Identifies label shift as an ongoing challenge in drug discovery AI, highlighting the need for robust uncertainty quantification methods.
   - **Year**: 2025

8. **Title**: FDA AI Guidance
   - **Authors**: Not specified
   - **Summary**: Establishes regulatory requirements for uncertainty estimates in AI systems used for drug development.
   - **Year**: 2025

**Key Challenges**
1. **Activity Cliff Prediction Failure**: All existing ML methods (24 evaluated) struggle to accurately predict molecular properties for activity cliffs, where structurally similar molecules exhibit dramatically different activities.

2. **Lack of Conditional Coverage Guarantees**: Standard conformal prediction methods only provide marginal coverage guarantees without ensuring reliable coverage for specific subgroups or challenging molecular regions.

3. **Label Shift in Drug Discovery**: Distribution shifts between training and deployment data remain a persistent challenge for uncertainty quantification in drug discovery applications.

4. **Regulatory Requirements for Uncertainty**: FDA guidance mandates reliable uncertainty estimates in drug development AI, creating practical need for methods with formal guarantees.

5. **Covariate Shift Handling**: Existing methods require specialized density estimation techniques to address coverage gaps caused by covariate shift in molecular property prediction.
