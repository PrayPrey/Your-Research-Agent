## Related Work

**Related Papers**
1. **Title**: Dirichlet-based Uncertainty Calibration for Active Domain Adaptation (Xie et al. 2023)
   - **Authors**: Xie et al.
   - **Summary**: DUC (Dirichlet-based Uncertainty Calibration) learns adaptive uncertainty estimates under domain shift, achieving ECE < 0.05 under domain shift.
   - **Year**: 2023

2. **Title**: On Handling Concept Drift, Calibration and Explainability (Kebir & Tabia 2024)
   - **Authors**: Kebir & Tabia
   - **Summary**: Empirically demonstrated that calibration degrades under concept drift in resource-limited IoT/edge contexts.
   - **Year**: 2024

3. **Title**: Spectral Graph Clustering under Differential Privacy (Seif et al. 2025)
   - **Authors**: Seif et al.
   - **Summary**: Noisy power iteration balances DP privacy with computational complexity; demonstrated that DP noise adds variance and degrades downstream task performance.
   - **Year**: 2025

4. **Title**: Differential Privacy Framework with Adjustable Efficiency–Utility Trade-Offs (Kim & Cho 2025)
   - **Authors**: Kim & Cho
   - **Summary**: DPFCM framework allows control over efficiency-utility-privacy trade-offs in fuzzy clustering.
   - **Year**: 2025

5. **Title**: Event-Triggered Model Predictive Control (Gräfe et al. 2025)
   - **Authors**: Gräfe et al.
   - **Summary**: Trigger control updates only when error exceeds adaptive threshold, reducing computation by 40-80%; primary inspiration for applying event-triggering to ML calibration.
   - **Year**: 2025

6. **Title**: Bottlenecks CLUB: Unifying Information-Theoretic Trade-Offs (Razeghi et al. 2022)
   - **Authors**: Razeghi et al.
   - **Summary**: Unified information-theoretic framework for complexity-leakage-utility bottleneck (CLUB) model for privacy models.
   - **Year**: 2022

7. **Title**: Enhancing Trade-Offs via MUST (Zhao et al. 2023)
   - **Authors**: Zhao et al.
   - **Summary**: Multistage sampling (MUST) for privacy amplification improves efficiency-privacy trade-off.
   - **Year**: 2023

8. **Title**: Meta PyTorch Opacus
   - **Authors**: Not specified
   - **Summary**: Production DP-SGD framework with privacy accounting and gradient clipping capabilities (1600+ GitHub stars).
   - **Year**: Not specified

9. **Title**: Microsoft RobustLearn
   - **Authors**: Not specified
   - **Summary**: Example of trustworthy ML toolkit with robustness focus (300+ GitHub stars).
   - **Year**: Not specified

10. **Title**: Quantifying Trade-Offs Between Dimensions of Trustworthy AI (Kemmerzell & Schreiner 2024)
    - **Authors**: Kemmerzell & Schreiner
    - **Summary**: Empirical demonstration that fairness-explainability-privacy-robustness trade-offs exist and are quantifiable.
    - **Year**: 2024

11. **Title**: Efficient Acceleration of DL on Resource-Constrained Edge Devices: Review (Shuvo et al. 2023)
    - **Authors**: Shuvo et al.
    - **Summary**: Comprehensive survey of model compression, optimization, and hardware-software codesign for edge devices (253 citations).
    - **Year**: 2023

12. **Title**: Differential Privacy (Dwork & Roth 2014)
    - **Authors**: Dwork & Roth
    - **Summary**: Foundational textbook establishing DP composition theorems and formal privacy analysis.
    - **Year**: 2014

13. **Title**: On Calibration of Modern Neural Networks (Guo et al. 2017)
    - **Authors**: Guo et al.
    - **Summary**: Established ECE (Expected Calibration Error) as standard calibration metric (2000+ citations).
    - **Year**: 2017

**Key Challenges**
1. **Calibration-Privacy Trade-Off Under Computational Constraints**: Understanding how DP noise impacts calibration quality when computational budget limits recalibration iterations in resource-constrained deployments.

2. **No Principled Triggering Mechanisms**: Existing calibration methods lack principled event-triggering mechanisms to avoid wasting computation and privacy budget during stable periods.

3. **Privacy Budget Scarcity in Adaptive Systems**: Total privacy budget ε is fixed, and frequent recalibrations risk budget exhaustion, leaving no budget for severe distribution shifts.

4. **Cross-Domain Transfer Validation**: No prior work combines event-triggering from control theory with differential privacy in ML calibration contexts.

5. **Three-Way Trade-off Characterization**: Prior work addresses only two of three dimensions (privacy-utility, calibration-computation) but not all three simultaneously (privacy-calibration-computation).

6. **Resource-Constrained Edge Deployment**: Calibration methods typically assume datacenter resources and do not address edge device constraints (limited computation, memory, energy).

7. **Lack of Adaptive Budget Allocation**: Existing periodic recalibration methods allocate privacy budget uniformly without adaptation to shift severity or budget depletion state.

8. **Privacy Preservation in Calibration**: No existing work provides formal differential privacy guarantees for calibration under distribution shift with event-triggered adaptation.
