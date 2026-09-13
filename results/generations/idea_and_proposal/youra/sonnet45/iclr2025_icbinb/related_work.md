## Related Work

**Related Papers**

1. **Title**: Empirically Validating Conformal Prediction on Modern Vision Architectures Under Distribution Shift (Semantic Scholar ID: eaed28f3100af8761acea42ce398dc8b746d210e)
   - **Authors**: Kasa et al.
   - **Summary**: Provides conformal prediction methodology for uncertainty quantification, demonstrating that calibration degrades under distribution shift and establishes the need for multi-dimensional assessment approaches.
   - **Year**: 2023

2. **Title**: Predicting Out-of-Distribution Performance with Model Conformance (Semantic Scholar ID: f794d88d2ef76098bc82d14160a918fccab08ce5)
   - **Authors**: Kaur et al.
   - **Summary**: Demonstrates feasibility of pre-deployment performance prediction, showing that model conformance correlates with out-of-distribution performance.
   - **Year**: 2023

3. **Title**: Probabilistic Runtime Verification, Evaluation and Risk Assessment of Visual Deep Learning Systems (Semantic Scholar ID: 2868580769382cdd23e7a03534fab8ec4372e396)
   - **Authors**: Torpmann-Hagen et al.
   - **Summary**: Introduces probabilistic risk assessment with 0.01-0.1 accuracy estimation error, demonstrating that explicit distribution shift modeling improves risk quantification.
   - **Year**: 2025

4. **Title**: BBVA mercury-robust Framework (https://github.com/BBVA/mercury-robust)
   - **Authors**: Not specified
   - **Summary**: Provides drift detection methodology with data drift tests, label leaking detection, and schema validation for production ML systems.
   - **Year**: Not specified

5. **Title**: TabularBench: Benchmarking Adversarial Robustness for Tabular Deep Learning in Real-world Use-cases (Semantic Scholar ID: c7140c1d5d83ab68c563435f9de8506b4ec258f5)
   - **Authors**: Simonetto et al.
   - **Summary**: Establishes benchmark for tabular ML robustness evaluation across 200 models in finance, healthcare, and security domains under adversarial attacks.
   - **Year**: 2024

6. **Title**: IBM ARES (AI Robustness Evaluation System) (https://github.com/IBM/ares)
   - **Authors**: Not specified
   - **Summary**: Provides robustness testing tools for measuring adversarial attack success rates against ML models.
   - **Year**: Not specified

7. **Title**: Trustworthy Multi-Modal AI in Healthcare: A Comprehensive Framework for Bias Detection, Explanation, and Mitigation (Semantic Scholar ID: 15474e1ae5c3facbbabae573e9f21603de5e4f41)
   - **Authors**: Anderson
   - **Summary**: Identifies healthcare AI deployment failures due to algorithmic bias and fragile generalization, establishing the need for predictive fairness assessment.
   - **Year**: 2025

8. **Title**: Fairness and Bias Mitigation in Computer Vision: A Survey (Semantic Scholar ID: a3dfc24885132fd0df2b1e04fabd5799771a4e55)
   - **Authors**: Dehdashtian et al.
   - **Summary**: Comprehensive survey on bias discovery and mitigation methods in computer vision systems, providing background for fairness as risk dimension.
   - **Year**: 2024

9. **Title**: Risk-Aware Financial Forecasting Enhanced by Machine Learning and Intuitionistic Fuzzy Multi-Criteria Decision-Making (ArXiv 2512.17936)
   - **Authors**: Turgay et al.
   - **Summary**: Develops IF-MCDA methodology with entropy weighting achieving 3.03% MAPE in financial forecasting, demonstrating ML + IF-MCDA integration with 95% confidence intervals outperforms single models.
   - **Year**: 2025

10. **Title**: Landslide risk assessment using an integrated framework of machine learning algorithms and multi-criteria decision analysis (Semantic Scholar ID: [from Phase 1])
    - **Authors**: Ha et al.
    - **Summary**: Demonstrates that ML + MCDA integrated frameworks outperform single-method approaches in geospatial risk assessment.
    - **Year**: 2025

11. **Title**: Evidently AI Framework (https://github.com/evidentlyai/evidently)
    - **Authors**: Not specified
    - **Summary**: Post-deployment monitoring framework with 100+ metrics for evaluation, testing, and monitoring of ML systems, representing closest existing approach to integrated assessment.
    - **Year**: Not specified

12. **Title**: ENGINEERING ROBUST AI PRODUCTS THROUGH CONTINUOUS QUALITY ASSURANCE (Semantic Scholar ID: ce3ebfb03cb9485ee1a7ef1907267e449953f31e)
    - **Authors**: Grover et al.
    - **Summary**: Proposes continuous ML system quality assurance framework with real-time verification for adaptive ML systems.
    - **Year**: 2025

13. **Title**: CORTEX: Composite Overlay for Risk Tiering and Exposure in Operational AI Systems (Semantic Scholar ID: d9ebb689042b60e00f4a1d09785a93a8608e4755)
    - **Authors**: Muhammad et al.
    - **Summary**: Develops multi-layered risk scoring methodology analyzing 1,200+ documented AI incidents, identifying 29 technical vulnerability groups.
    - **Year**: 2025

14. **Title**: kennethleungty/Failed-ML Repository (https://github.com/kennethleungty/Failed-ML)
    - **Authors**: Kenneth Leung
    - **Summary**: Compilation of high-profile ML deployment failures providing real-world failure case documentation for systematic analysis.
    - **Year**: Not specified

**Key Challenges**

1. **Fragmented Single-Dimension Tools**: Current pre-deployment assessment relies on isolated tools (drift detection OR fairness auditing OR robustness testing) that capture only one failure mode, missing critical interactions between risk dimensions.

2. **Lack of Uncertainty Quantification**: Existing approaches provide binary pass/fail decisions without confidence intervals, preventing risk-informed deployment decisions under uncertainty.

3. **Manual Threshold Tuning**: Current tools (Evidently, mercury-robust) require expert-driven configuration and threshold tuning for each model and domain, limiting scalability.

4. **Reactive vs Predictive Assessment**: Mature post-deployment monitoring tools exist (Evidently, Phoenix), but pre-deployment failure prediction frameworks are absent from the literature.

5. **No Integrated Evaluation Protocol**: Tool-specific benchmarks exist without unified baseline comparison frameworks for assessing integrated multi-dimensional approaches.

6. **Cross-Domain Transfer Gap**: Multi-criteria decision analysis methodologies validated in financial forecasting and geospatial risk assessment have not been applied to deep learning deployment risk prediction.

7. **Operational Definition Gap**: Absence of standardized "deployment failure" definitions across domains, hindering systematic empirical validation of risk assessment approaches.

8. **Integration Engineering Complexity**: Assembling heterogeneous risk signals (statistical uncertainty, distributional shift, adversarial fragility, fairness violations) into unified probabilistic scores without formal mathematical framework.
