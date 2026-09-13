## Related Work

**Related Papers**
1. **Title**: Getting aligned on representational alignment ([Sucholutsky et al. 2023](identifier if available))
   - **Authors**: Sucholutsky et al.
   - **Summary**: Identified the causal mechanism linking representational similarity to behavioral and value alignment as an open problem, providing the foundational motivation for causal analysis in representational alignment research.
   - **Year**: 2023

2. **Title**: Macaque IT alignment → robustness ([Dapello et al. 2022](identifier if available))
   - **Authors**: Dapello et al.
   - **Summary**: Provided empirical evidence for the T→M→Y pathway showing correlation between neural representation alignment and robust behavior outcomes in macaque models.
   - **Year**: 2022

3. **Title**: Functional correspondence evaluation ([Bo & Khosla 2024](identifier if available))
   - **Authors**: Bo & Khosla
   - **Summary**: Demonstrated that geometric metrics for measuring representational similarity correlate with behavioral outcomes, establishing geometric approaches as viable measurement frameworks.
   - **Year**: 2024

4. **Title**: Multilevel mediation framework (VanderWeele & Tchetgen 2021)
   - **Authors**: VanderWeele & Tchetgen
   - **Summary**: Developed the theoretical foundation for Natural Indirect Effect (NIE) and Natural Direct Effect (NDE) decomposition in causal mediation analysis.
   - **Year**: 2021

5. **Title**: Sensitivity analysis for omitted variables (Cinelli & Hazlett 2020)
   - **Authors**: Cinelli & Hazlett
   - **Summary**: Established methodology for bounding unmeasured confounding effects using R² sensitivity thresholds, enabling transparent reporting of causal inference robustness.
   - **Year**: 2020

6. **Title**: High-dimensional mediation (Huang et al. 2021)
   - **Authors**: Huang et al.
   - **Summary**: Developed LASSO-based mediator selection methods for high-dimensional causal mediation analysis, enabling principled dimensionality reduction in neural activation spaces.
   - **Year**: 2021

7. **Title**: Continuous treatment mediation (Wang et al. 2017)
   - **Authors**: Wang et al.
   - **Summary**: Extended mediation analysis framework to continuous treatment variables using generalized propensity scores, enabling application to gradient-based alignment interventions.
   - **Year**: 2017

8. **Title**: Geometry-aware distillation (Bhattarai et al. 2025)
   - **Authors**: Bhattarai et al.
   - **Summary**: Introduced the only prior alignment-targeted intervention method using geometric representational features, though without causal validation framework.
   - **Year**: 2025

9. **Title**: Representation Engineering (Zou et al. 2023)
   - **Authors**: Zou et al.
   - **Summary**: Developed activation steering methods for targeted behavioral modification, providing validation protocols for testing mediator sufficiency in representational interventions.
   - **Year**: 2023

10. **Title**: TruthfulQA (Lin et al. 2022)
    - **Authors**: Lin et al.
    - **Summary**: Established standardized benchmark for measuring truthfulness in language model outputs, providing validated outcome measurement for alignment research.
    - **Year**: 2022

**Key Challenges**
1. **Causal Mechanism Uncertainty**: The causal mechanism linking representational similarity to behavioral and value alignment remains unclear, with existing work limited to correlational analysis (Gap 3 from Sucholutsky et al. 2023).

2. **Correlation vs. Causation**: Current state-of-the-art approaches demonstrate correlation coefficients (r ∈ [0.55, 0.75]) between representational metrics and behavioral outcomes, but lack causal decomposition frameworks to quantify mediation effects.

3. **Unmeasured Confounding**: Alignment research faces challenges in controlling for confounding variables such as training data biases, base model architectures, and hyperparameter configurations that may create spurious correlations.

4. **Mediator Measurement Error**: Existing representational metrics (e.g., CKA, attention patterns) may miss local features or capture incomplete views of the true mediating representations.

5. **Scale Generalization**: Lack of evidence for whether causal pathways identified in smaller models (7B parameters) generalize to larger models (70B+ parameters) or across different model families.

6. **Intervention Efficiency**: Generic fine-tuning approaches lack theoretical frameworks for targeting specific representational pathways, limiting the efficiency of alignment interventions.

7. **Cross-Domain Transferability**: Existing alignment methods developed for text-only language models lack validated frameworks for adaptation to vision, multimodal, or other non-textual domains.

8. **Temporal Ordering Validation**: Limited methodological approaches for rigorously validating that representational changes precede behavioral changes during training dynamics.

9. **Non-Linear Mediation**: Assumption of linear mediation relationships may not hold at extreme intervention intensities or in complex multi-pathway scenarios.

10. **Transparent Robustness Reporting**: Lack of standardized methods for reporting sensitivity to assumption violations in deep learning alignment contexts, limiting reproducibility and trust in causal claims.
