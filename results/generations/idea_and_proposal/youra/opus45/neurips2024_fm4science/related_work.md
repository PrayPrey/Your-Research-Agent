## Related Work

**Related Papers**
1. **Title**: Constraint-Aware Neurosymbolic Uncertainty Framework (CANUF) (arXiv:2601.12442)
   - **Authors**: Shahnawaz Alam, Mohammed Mudassir Uddin, Mohammed Kaif Pasha
   - **Summary**: Proposes a neurosymbolic framework achieving 34.7% ECE reduction and 99.2% constraint satisfaction through differentiable constraint extraction with 91.4% precision. Serves as primary baseline for constraint-aware uncertainty quantification.
   - **Year**: 2026

2. **Title**: Calibrated Physics-Informed Uncertainty Quantification (arXiv:2502.04406)
   - **Authors**: Vignesh Gopakumar, Ander Gray, et al.
   - **Summary**: Demonstrates that physics residuals can serve as nonconformity scores to provide distribution-free coverage guarantees in conformal prediction settings.
   - **Year**: 2025

3. **Title**: Uncertainty-Aware Diagnostics for Physics-Informed ML (OpenReview:7PORoDlSS4)
   - **Authors**: Not specified
   - **Summary**: Introduces the PILE score and provides theoretical justification for using physics residuals and constraint violations as valid uncertainty indicators in physics-informed machine learning.
   - **Year**: 2026

4. **Title**: Standard Conformal Prediction
   - **Authors**: Vovk et al.
   - **Summary**: Establishes the foundational conformal prediction methodology without constraint augmentation, serving as a baseline comparison approach.
   - **Year**: Not specified

5. **Title**: Bayesian Neural Networks with Variational Inference
   - **Authors**: Not specified
   - **Summary**: Provides an alternative uncertainty quantification approach based on distributional assumptions through variational inference in neural networks.
   - **Year**: Not specified

6. **Title**: Foundation Models for Scientific Discovery
   - **Authors**: Not specified
   - **Summary**: Demonstrates that uncertainty quantification remains a key challenge for deploying foundation models in scientific applications.
   - **Year**: 2025

7. **Title**: TruthHypo/KnowHD
   - **Authors**: Not specified
   - **Summary**: Addresses hallucination detection in models but lacks explicit uncertainty quantification integration, representing a gap in current approaches.
   - **Year**: 2025

**Key Challenges**
1. **Uncertainty Quantification in Scientific Foundation Models**: UQ remains a critical unresolved challenge for reliable deployment of foundation models in scientific discovery applications.
2. **Distributional Assumptions in Bayesian Approaches**: Existing Bayesian methods for uncertainty quantification rely on distributional assumptions that may not hold in practice.
3. **Lack of Constraint Awareness in Standard Methods**: Traditional conformal prediction approaches do not incorporate domain constraints, limiting their applicability to physics-informed settings.
4. **Hallucination Detection Without UQ Integration**: Current hallucination detection methods operate independently from uncertainty quantification frameworks, missing opportunities for unified approaches.
5. **Distribution-Free Coverage with Physical Constraints**: Achieving valid coverage guarantees while simultaneously satisfying physical constraints remains an open methodological challenge.
