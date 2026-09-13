## Related Work

**Related Papers**

1. **Title**: Algorithmic Learning in a Random World (Vovk et al., 2005)
   - **Authors**: V. Vovk et al.
   - **Summary**: Established conformal prediction framework with finite-sample coverage guarantees under exchangeability assumption, providing theoretical foundation for distribution-free prediction.
   - **Year**: 2005

2. **Title**: Distribution-Free Prediction Bands for Non-parametric Regression (Lei & Wasserman, 2014)
   - **Authors**: Jing Lei, Larry Wasserman
   - **Summary**: Introduced split conformal prediction for regression with computational efficiency, enabling scalable conformal inference.
   - **Year**: 2014

3. **Title**: Conformalized Quantile Regression (Romano et al., 2019)
   - **Authors**: Y. Romano et al.
   - **Summary**: Combined conformal prediction with quantile regression for conditional coverage, achieving adaptive prediction intervals through model-based quantile estimation.
   - **Year**: 2019

4. **Title**: Conformal Prediction Under Covariate Shift (Tibshirani et al., 2019)
   - **Authors**: Ryan J. Tibshirani et al.
   - **Summary**: Proposed weighted conformal prediction with importance weights w = p_test(x) / p_train(x) for covariate shift adaptation, requiring density ratio estimation.
   - **Year**: 2019

5. **Title**: Adaptive Conformal Inference Under Distribution Shift (Gibbs & Candès, 2021)
   - **Authors**: Isaac Gibbs, Emmanuel Candès
   - **Summary**: Developed adaptive conformal inference with test-time score adjustment for concept drift, focusing on temporal distribution shifts.
   - **Year**: 2021

6. **Title**: Conformal Prediction with Conditional Guarantees via Structural Causal Models (Xu et al., 2024)
   - **Authors**: Xu et al.
   - **Summary**: Used causal graphs to identify confounders and apply interventional conformal prediction for conditional coverage, requiring explicit causal graph specification.
   - **Year**: 2024

7. **Title**: Physics-informed neural networks: A deep learning framework for solving forward and inverse problems involving nonlinear partial differential equations (Raissi et al., 2019)
   - **Authors**: M. Raissi, P. Perdikaris, G.E. Karniadakis
   - **Summary**: Established PINN methodology for incorporating PDE constraints into neural network training via soft penalties, enabling physics-constrained learning.
   - **Year**: 2019

8. **Title**: Understanding and Mitigating Gradient Flow Pathologies in Physics-Informed Neural Networks (Wang et al., 2021)
   - **Authors**: S. Wang et al.
   - **Summary**: Identified that PINNs fail in under-sampled regions with high residuals due to gradient pathologies, establishing correlation between residuals and prediction errors.
   - **Year**: 2021

9. **Title**: Characterizing possible failure modes in physics-informed neural networks (Krishnapriyan et al., 2021)
   - **Authors**: A. Krishnapriyan et al.
   - **Summary**: Provided comprehensive analysis of PINN failure modes, showing residuals spike in out-of-distribution regions and can serve as OOD detectors.
   - **Year**: 2021

10. **Title**: Flow reconstruction with uncertainty quantification from noisy measurements based on Bayesian physics-informed neural networks (Liu et al., 2024)
    - **Authors**: Liu et al.
    - **Summary**: Developed Bayesian PINNs with posterior sampling for uncertainty quantification, requiring priors and MCMC/variational inference but providing full posterior distributions.
    - **Year**: 2024

11. **Title**: Uncertainty Quantification for Physics-Informed Neural Networks with Extended Fiducial Inference (Shih et al., 2025)
    - **Authors**: Shih et al.
    - **Summary**: Introduced Extended Fiducial Inference (EFI) framework for rigorous UQ in PINNs without priors using hyper-networks, focusing on epistemic uncertainty estimation.
    - **Year**: 2025

12. **Title**: Conformal Prediction for Physics-Informed Neural Networks (Yu et al., 2025)
    - **Authors**: Yu et al.
    - **Summary**: First application of split conformal prediction to PINNs, demonstrating finite-sample coverage guarantees without adaptive weighting (main SOTA baseline).
    - **Year**: 2025

13. **Title**: Covariate Shift Adaptation by Importance Weighted Cross Validation (Sugiyama et al., 2007)
    - **Authors**: M. Sugiyama et al.
    - **Summary**: Developed Kernel Mean Matching (KMM) for importance weight estimation under covariate shift, providing theoretical foundation for kernel-based reweighting.
    - **Year**: 2007

14. **Title**: Dataset Shift in Machine Learning (Quionero-Candela et al., 2009)
    - **Authors**: J. Quionero-Candela et al.
    - **Summary**: Provided comprehensive taxonomy of distribution shift types and established covariate shift as solvable via reweighting approaches.
    - **Year**: 2009

15. **Title**: GradOrth: A Simple Yet Efficient Out-of-Distribution Detection with Orthogonal Projection of Gradients (Ainsworth et al., 2022)
    - **Authors**: Ainsworth et al.
    - **Summary**: Proposed using gradient orthogonality for OOD detection, offering an alternative signal to physics residuals for identifying distribution shift.
    - **Year**: 2022

16. **Title**: Residual-based error bounds for physics-informed neural networks (Lütjens et al., 2023)
    - **Authors**: Lütjens et al.
    - **Summary**: Derived rigorous error bounds using PDE residuals as error indicators, providing theoretical justification for residual-error correlation assumption.
    - **Year**: 2023

**Key Challenges**

1. **High-dimensional density estimation failure**: Traditional weighted conformal prediction (Tibshirani et al., 2019) requires density ratio estimation p_test(x)/p_train(x), which fails in high-dimensional input spaces typical of PINNs (spatiotemporal coordinates).

2. **Causal modeling overhead**: Causal conformal prediction methods (Xu et al., 2024) achieve adaptive interval tightening but require explicit causal graph construction, demanding weeks of domain expert effort for implementation.

3. **Bayesian computational cost**: Bayesian PINN approaches (Liu et al., 2024) provide uncertainty quantification but require prior specification and expensive posterior sampling via MCMC or variational inference (10-100× slower than point estimates).

4. **Conservative worst-case intervals**: Standard conformal prediction for PINNs (Yu et al., 2025) guarantees coverage but uses worst-case quantiles across entire calibration set, resulting in overly wide prediction intervals under distribution shift.

5. **Lack of physics-informed adaptation**: Prior adaptive conformal methods use input features or model outputs for similarity metrics but do not leverage physics residuals, missing domain-specific structure available in scientific ML applications.

6. **MC Dropout miscalibration**: Dropout-based uncertainty estimation provides fast approximate inference but often produces miscalibrated intervals (over-confident under distribution shift) without formal coverage guarantees.

7. **Gradient pathologies in OOD regions**: PINNs exhibit high residuals and large prediction errors in under-sampled regions (Wang et al., 2021; Krishnapriyan et al., 2021), but existing UQ methods do not explicitly use residuals as adaptation signals.

8. **Coverage-efficiency trade-off**: Existing methods either guarantee valid coverage with wide intervals (standard CP) or produce tighter intervals without formal guarantees (Bayesian, ensemble methods), lacking a principled solution that achieves both.
