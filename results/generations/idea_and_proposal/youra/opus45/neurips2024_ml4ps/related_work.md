## Related Work

**Related Papers**
1. **Title**: A Conformal Prediction Framework for Uncertainty Quantification in Physics-Informed Neural Networks (arXiv:2509.13717)
   - **Authors**: Yu, Ho, Wang
   - **Summary**: Introduces conformal prediction for PINNs with local conformal quantile estimation, treating physics as a soft constraint in the nonconformity score.
   - **Year**: 2025

2. **Title**: Conformalized Physics-Informed Neural Networks
   - **Authors**: Podina, Torabi Rad, Kohandel
   - **Summary**: C-PINNs provide distribution-free confidence intervals for forward and inverse PDE problems, establishing methodological foundations for physics-informed conformal prediction.
   - **Year**: 2024

3. **Title**: Conditional Coverage Diagnostics for Conformal Prediction
   - **Authors**: Braun, Holzmüller, Jordan, Bach
   - **Summary**: Develops methods for evaluating conditional coverage using classification-based metrics, providing evaluation methodology for verifying conditional coverage properties.
   - **Year**: 2025

4. **Title**: Scientific Machine Learning Through Physics-Informed Neural Networks: Where we are and What's Next
   - **Authors**: Cuomo et al.
   - **Summary**: Comprehensive review of PINNs identifying uncertainty quantification as a key remaining gap in the field.
   - **Year**: 2022

5. **Title**: Bayesian PINNs
   - **Authors**: Xu, Wang
   - **Summary**: Alternative uncertainty quantification approach for PINNs that requires expensive sampling procedures.
   - **Year**: 2025

6. **Title**: Uncertainty Quantification for PINNs with Extended Fiducial Inference
   - **Authors**: Shih, Jiang, Liang
   - **Summary**: Demonstrates that existing UQ methods (Bayesian, dropout) require prior specification or arbitrary hyperparameters, highlighting limitations of current approaches.
   - **Year**: 2025

**Key Challenges**
1. **Soft Physics Constraints**: Existing conformal prediction methods for PINNs treat physics as soft constraints in nonconformity scores rather than enforcing hard constraint satisfaction, potentially allowing physics-violating predictions.

2. **Expensive Sampling Requirements**: Bayesian approaches to PINN uncertainty quantification require computationally expensive sampling procedures, limiting practical applicability.

3. **Prior Specification and Hyperparameter Sensitivity**: Current UQ methods for PINNs require prior specification or arbitrary hyperparameter choices, introducing subjectivity and potential unreliability.

4. **Rigorous UQ with Physics Validity**: The combination of rigorous uncertainty quantification and guaranteed physics validity remains systematically unaddressed in the literature.

5. **Conditional Coverage Verification**: Evaluating whether uncertainty estimates provide valid conditional coverage across different input regions remains a methodological challenge.
