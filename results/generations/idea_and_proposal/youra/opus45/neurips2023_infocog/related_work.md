## Related Work

**Related Papers**
1. **Title**: Mutual Information Neural Estimation (MINE) (arXiv:1801.04062)
   - **Authors**: Belghazi et al.
   - **Summary**: Demonstrates that neural networks can estimate mutual information with linear scalability in dimensionality, establishing the neural MI estimation paradigm.
   - **Year**: 2018

2. **Title**: InfoBridge: Mutual Information estimation via Bridge Matching (arXiv:2502.01383)
   - **Authors**: Kholkin et al.
   - **Summary**: Introduces bridge matching as a technique for unbiased MI estimation through domain transfer, providing foundation for bridge-based approaches.
   - **Year**: 2025

3. **Title**: Mutual Information Estimation via Normalizing Flows (arXiv:2403.02187)
   - **Authors**: Butakov et al.
   - **Summary**: Proposes transformation to tractable distributions as a method for efficient MI estimation, demonstrating the effectiveness of flow-based approaches.
   - **Year**: 2024

4. **Title**: CLUB: Contrastive Log-ratio Upper Bound of MI
   - **Authors**: Cheng et al.
   - **Summary**: Presents an upper bound approach to MI estimation using contrastive log-ratio methods, offering a different estimation philosophy from lower bound approaches.
   - **Year**: 2020

5. **Title**: MIGE: Mutual Information Gradient Estimation
   - **Authors**: Wen et al.
   - **Summary**: Develops a gradient-based approach to mutual information estimation for optimization applications.
   - **Year**: 2020

6. **Title**: Latent MI: Approximating MI of high-dimensional variables
   - **Authors**: Gowri et al.
   - **Summary**: Demonstrates that MI approximation is achievable through learned low-dimensional representations, validating dimension reduction approaches for MI estimation.
   - **Year**: 2024

7. **Title**: Accurate Estimation of MI in High Dimensional Data
   - **Authors**: Abdelaleem et al.
   - **Summary**: Provides systematic evaluation revealing gaps and limitations in existing MI estimators for high-dimensional settings.
   - **Year**: 2025

8. **Title**: Transfer Entropy as a Measure of Brain Connectivity
   - **Authors**: Ursino et al.
   - **Summary**: Analyzes temporal information flow in neural data, supporting the design of temporal encoders for brain connectivity analysis.
   - **Year**: 2020

**Key Challenges**
1. **High-Dimensional Scalability**: Existing MI estimators face significant limitations when applied to high-dimensional data, with systematic evaluations revealing gaps in current methods.
2. **Bias in Estimation**: Traditional neural MI estimation approaches may suffer from bias, motivating the development of unbiased estimation techniques such as bridge matching.
3. **Representation Learning for MI**: Effective MI estimation in complex domains requires learning appropriate low-dimensional representations that preserve information-theoretic properties.
4. **Temporal Information Flow**: Capturing temporal dependencies in sequential data (such as neural recordings) requires specialized encoder designs beyond standard MI estimation frameworks.
