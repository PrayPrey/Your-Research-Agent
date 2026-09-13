## Related Work

**Related Papers**

1. **Title**: Invariant Risk Minimization (Arjovsky et al., 2019)
   - **Authors**: Arjovsky, M., Bottou, L., Gulrajani, I., & Lopez-Paz, D.
   - **Summary**: Introduced IRM principle for learning invariant predictors across environments using gradient penalty for structural invariance via optimization constraint. Achieved 70% test accuracy on ColoredMNIST (vs. 10% ERM on shifted test).
   - **Year**: 2019

2. **Title**: Counterfactual Invariance to Spurious Correlations: Why and How to Pass Stress Tests (Veitch et al., 2021)
   - **Authors**: Veitch, V., D'Amour, A., Yadlowsky, S., & Eisenstein, J.
   - **Summary**: Formalizes counterfactual invariance and stress testing framework, demonstrating that causal structure determines which regularization schemes succeed. Validates that invariance leads to stable features.
   - **Year**: 2021

3. **Title**: Causality: Models, Reasoning, and Inference (2nd ed.)
   - **Authors**: Pearl, J.
   - **Summary**: Foundational work establishing do-calculus and causal graph theory, providing mathematical foundation for causal inference and intervention-based reasoning.
   - **Year**: 2009

4. **Title**: The Clever Hans Mirage: A Comprehensive Survey on Spurious Correlations in Machine Learning (Ye et al., 2024)
   - **Authors**: Ye, W., Zheng, G., Cao, X., et al.
   - **Summary**: Most comprehensive taxonomy of spurious correlation methods across communities (causal ML, fairness, OOD), identifying that these communities address spurious correlations independently and highlighting the gap for unified frameworks.
   - **Year**: 2024

5. **Title**: Towards Out-Of-Distribution Generalization: A Survey (Shen et al., 2021)
   - **Authors**: Shen, Z., Liu, J., He, Y., et al.
   - **Summary**: First comprehensive OOD generalization framework categorizing methods into unsupervised representation learning, supervised model learning, and optimization approaches. Establishes spurious correlation as primary OOD failure mode.
   - **Year**: 2021

6. **Title**: Causal Feature Selection for Responsible Machine Learning (Moraffah et al., 2024)
   - **Authors**: Moraffah, R., Sheth, P., Vishnubhatla, S., & Liu, H.
   - **Summary**: Addresses four pillars (interpretability, fairness, robustness, generalization) via causal lens, emphasizing that distinguishing causality from correlation is key to responsible ML but treating pillars separately.
   - **Year**: 2024

7. **Title**: Distributionally Robust Neural Networks for Group Shifts (Sagawa et al., 2020)
   - **Authors**: Sagawa, S., Koh, P. W., Hashimoto, T. B., & Liang, P.
   - **Summary**: Introduced Group DRO for distributional robustness by minimizing worst-group loss, achieving 91.4% worst-group accuracy on Waterbirds but requiring group annotations and lacking causal/OOD integration.
   - **Year**: 2020

8. **Title**: Fairness and Bias Mitigation in Computer Vision: A Survey (Dehdashtian et al., 2024)
   - **Authors**: Dehdashtian, S., He, R., Li, Y., et al.
   - **Summary**: CV-specific fairness methods covering bias discovery, analysis, and mitigation, providing fairness community perspective but lacking cross-community integration with causal/OOD methods.
   - **Year**: 2024

9. **Title**: Emerging algorithmic bias: fairness drift as the next dimension of model maintenance and sustainability (Davis et al., 2025)
   - **Authors**: Davis, S. E., Dorn, C., Park, D. J., & Matheny, M. E.
   - **Summary**: 11-year clinical study demonstrating temporal fairness drift where spurious correlations emerge over time, showing that model updating can both help and harm fairness and suggesting need for multi-constraint frameworks.
   - **Year**: 2025

10. **Title**: Domain-Adversarial Training of Neural Networks (Ganin et al., 2016)
    - **Authors**: Ganin, Y., Ustinova, E., Ajakan, H., et al.
    - **Summary**: Introduced DANN using adversarial training to learn domain-invariant features for environmental invariance, achieving 85.5% average domain accuracy on PACS dataset but lacking explicit causal or fairness constraints.
    - **Year**: 2016

11. **Title**: Evaluation of domain generalization and adaptation on improving model robustness to temporal dataset shift in clinical medicine (Guo et al., 2021)
    - **Authors**: Guo, L., Pfohl, S., Fries, J., et al.
    - **Summary**: Large clinical study finding that domain generalization/unsupervised domain adaptation methods sometimes failed vs. ERM under temporal shift, demonstrating that domain generalization alone doesn't guarantee robustness and 2.8% worst-group accuracy improvement with PDE methods.
    - **Year**: 2021

12. **Title**: ShortcutProbe: Probing Prediction Shortcuts for Learning Robust Models (Zheng et al., 2025)
    - **Authors**: Zheng, G., Ye, W., & Zhang, A.
    - **Summary**: Post-hoc framework identifying shortcuts in latent space without group labels, showing shortcuts violate invariance and providing complementary discovery method for spurious correlations.
    - **Year**: 2025

13. **Title**: Improving Group Robustness on Spurious Correlation via Evidential Alignment (Ye et al., 2025)
    - **Authors**: Ye, W., Zheng, G., & Zhang, A.
    - **Summary**: Uses uncertainty quantification (evidential deep learning) for detecting spurious correlations without annotations, providing signals for which invariance types are most critical for a given dataset.
    - **Year**: 2025

14. **Title**: Robust Learning with PDE (Deng et al., 2023)
    - **Authors**: Not specified
    - **Summary**: Demonstrated 2.8% worst-group accuracy improvement using partial differential equation-based robust learning methods for handling spurious correlations.
    - **Year**: 2023

**Key Challenges**

1. **Community Fragmentation**: Methods from causal ML, algorithmic fairness, and OOD generalization address spurious correlations independently without unified framework or cross-community method translation, leading to fragmented solutions and limited effectiveness on multi-dimensional distribution shifts.

2. **Single-Dimension Limitations**: Existing SOTA methods (IRM for causal, GroupDRO for fairness, DANN for OOD) enforce only one type of invariance constraint, missing spurious correlations that are stable in one dimension but unstable in others, as demonstrated by clinical studies showing domain generalization alone failing.

3. **Annotation Requirements**: Most distributional robustness methods require explicit group annotations, limiting applicability to annotation-scarce domains and preventing automated discovery of spurious correlations across dimensions.

4. **Temporal Dynamics Gap**: While temporal fairness drift has been documented (11-year study showing spurious correlations emerge over time), existing frameworks don't integrate temporal invariance with causal, distributional, and environmental invariances for deployed model maintenance.

5. **Translation Protocol Absence**: No systematic methodology exists for adapting methods across communities (e.g., causal methods to fairness problems), preventing practitioners from leveraging specialized techniques from adjacent research areas.

6. **Invariance Compatibility Unknown**: Unclear whether structural, distributional, and environmental invariances can be jointly satisfied without contradiction or producing degenerate solutions, with potential for optimization conflicts when satisfying one invariance makes others harder to satisfy.

7. **Computational Scalability**: Multi-constraint optimization approaches may incur significant training overhead (potentially 10× baseline), limiting practical adoption for large-scale applications (ImageNet, GPT-scale models) in industry settings.

8. **Semantic Preservation Risk**: When translating methods across communities via unified frameworks, community-specific semantics and optimizations (e.g., fairness constraint relaxations) may not preserve the original method's effectiveness or theoretical guarantees.

9. **Evaluation Fragmentation**: No unified benchmark evaluates structural (intervention robustness), distributional (worst-group accuracy), and environmental (cross-domain performance) dimensions jointly, preventing direct comparison of methods across communities on shared evaluation criteria.

10. **Weight Learning Ambiguity**: For application-specific multi-constraint balancing, no established methodology exists for learning optimal invariance weights from limited validation data, with unclear choice between multi-objective optimization, constraint satisfaction, or meta-learning approaches.
