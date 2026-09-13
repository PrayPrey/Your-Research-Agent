## Related Work

**Related Papers**

1. **Title**: Algorithmic Learning in a Random World (Vovk et al. 2005)
   - **Authors**: Vovk et al.
   - **Summary**: Established the foundational conformal prediction framework, proving that coverage ≥1-α can be maintained under exchangeability assumptions.
   - **Year**: 2005

2. **Title**: Uncertainty Quantification over Graph with Conformalized GNN (CF-GNN) (Huang et al. 2023)
   - **Authors**: Huang et al.
   - **Summary**: Achieved conformal prediction on graphs with 74% smaller prediction sets while maintaining valid coverage through permutation invariance conditions. Current SOTA for structured data but assumes static i.i.d. graphs.
   - **Year**: 2023

3. **Title**: Adaptive Conformal Inference Under Distribution Shift (Gibbs & Candès 2021)
   - **Authors**: Gibbs & Candès
   - **Summary**: Demonstrated that simple sliding window approaches can maintain approximate coverage under gradual distribution shift in adaptive conformal prediction settings.
   - **Year**: 2021

4. **Title**: Efficiently Modeling Long Sequences with Structured State Spaces (S4) (Gu et al. 2022)
   - **Authors**: Gu et al.
   - **Summary**: Introduced S4 parameterization achieving O(d·log(T)) complexity via FFT for sequence modeling, proven to be a universal approximator for temporal sequences.
   - **Year**: 2022

5. **Title**: Diffusion-based Time Series Imputation and Forecasting with SSMs (SSSD) (Lopez Alcaraz & Strodthoff 2022)
   - **Authors**: Lopez Alcaraz & Strodthoff
   - **Summary**: Demonstrated that state-space models (SSMs) effectively capture long-term temporal dependencies in time series data, validating SSM effectiveness for temporal structure exploitation.
   - **Year**: 2022

6. **Title**: A New Approach to Linear Filtering and Prediction Problems (Kalman 1960)
   - **Authors**: Kalman
   - **Summary**: Developed optimal online state estimation via recursive Bayesian updates, establishing foundational principles for adaptive filtering and control theory.
   - **Year**: 1960

7. **Title**: Adaptive Filtering (Widrow & Stearns 1985)
   - **Authors**: Widrow & Stearns
   - **Summary**: Established exponentially weighted moving average (EWMA) methods for non-stationary signal tracking in adaptive filtering applications.
   - **Year**: 1985

8. **Title**: Simple and Scalable Predictive Uncertainty Estimation using Deep Ensembles (Lakshminarayanan et al. 2017)
   - **Authors**: Lakshminarayanan et al.
   - **Summary**: Proposed Bayesian approximation via ensemble of networks for uncertainty quantification, though without formal coverage guarantees and with 5-10× computational overhead.
   - **Year**: 2017

9. **Title**: Linear Opinion Pooling for UQ on Graphs (Damke & Hüllermeier 2024)
   - **Authors**: Damke & Hüllermeier
   - **Summary**: Developed uncertainty quantification methods using mixtures of Dirichlet distributions and opinion pooling for combining multiple calibration sources on graph data.
   - **Year**: 2024

10. **Title**: eXponential FAmily Dynamical Systems (XFADS) (Dowling et al. 2024)
    - **Authors**: Dowling et al.
    - **Summary**: Achieved linear time scaling for state-space models through low-rank VAE parameterization, demonstrating parallel innovations in structured parameterization for computational efficiency.
    - **Year**: 2024

**Key Challenges**

1. **Distribution Shift in Non-Stationary Sequences**: Existing conformal prediction methods (e.g., CF-GNN) assume static i.i.d. data and fail to maintain coverage guarantees under distribution shift, with coverage degrading to 82-85% during gradual drift.

2. **Lack of Temporal Structure Exploitation**: Current adaptive conformal prediction methods (Gibbs & Candès 2021) use simple sliding windows without modeling temporal autocorrelation, missing opportunities for tighter prediction bounds.

3. **Computational Inefficiency of Full Recalibration**: Full model retraining or recalibration approaches require O(n²) computational cost per timestep, making them infeasible for real-time applications and edge devices.

4. **No Formal Guarantees in Bayesian Methods**: Deep ensemble approaches provide uncertainty estimates but lack distribution-free coverage guarantees and incur 5-10× computational overhead.

5. **Gap Between SSM Prediction and UQ**: State-space models (S4, SSSD) have been successfully applied to prediction tasks but not to uncertainty quantification, leaving temporal structure unexploited in UQ settings.

6. **Reactive vs. Proactive Shift Handling**: Existing methods react to coverage violations after they occur rather than proactively detecting shifts early through model likelihood monitoring.

7. **Limited Applicability to Safety-Critical Domains**: Lack of reliable uncertainty quantification under distribution shift blocks deployment of ML systems in safety-critical applications (autonomous driving, medical monitoring, climate forecasting) that require formal guarantees.

8. **Trade-off Between Adaptation Speed and Stability**: Higher decay rates enable faster adaptation to shifts but increase variance in quantile estimates, creating instability in coverage guarantees.