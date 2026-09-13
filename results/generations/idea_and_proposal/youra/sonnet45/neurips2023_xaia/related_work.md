## Related Work

**Related Papers**

1. **Title**: A Critical Survey on Fairness Benefits of Explainable AI
   - **Authors**: Luca Deck, Jakob Schoeffer, Maria De-Arteaga, Niklas Kühl
   - **Summary**: Critical analysis reveals XAI-fairness validation claims often vague/simplistic, lacking normative grounding. Demonstrates that existing universal XAI metrics lack domain validity.
   - **Year**: 2023

2. **Title**: Explainable AI for government: Does the type of explanation matter?
   - **Authors**: Naomi Aoki, et al.
   - **Summary**: Empirical evidence that explanation type affects perceived accuracy/fairness differently for affected individuals, validating stakeholder-type differentiation needs.
   - **Year**: 2024

3. **Title**: Explainability for Natural Language Processing
   - **Authors**: Marina Danilevsky, et al.
   - **Summary**: Qualitative study reveals NLP validation is ad-hoc and project-specific, exemplifying domain-specific validation challenges.
   - **Year**: 2021

4. **Title**: Explainable AI (XAI) in Healthcare: Building Trust in Medical Diagnosis Systems
   - **Authors**: Ms. Prajakta Sudhir Khade
   - **Summary**: Healthcare validation requires clinical expert assessment, which is fundamentally different from statistical metrics, demonstrating domain-specificity needs.
   - **Year**: 2025

5. **Title**: A Survey on Explainable Artificial Intelligence (XAI): Toward Medical XAI
   - **Authors**: Erico Tjoa, Cuntai Guan
   - **Summary**: Different stakeholders (clinicians vs patients vs regulators) require different interpretability levels, establishing multi-stakeholder taxonomy foundation.
   - **Year**: 2019

6. **Title**: Model-Agnostic Meta-Learning for Fast Adaptation of Deep Networks (MAML)
   - **Authors**: Chelsea Finn, Pieter Abbeel, Sergey Levine
   - **Summary**: Foundational meta-learning approach enabling rapid adaptation to new tasks through "learn-to-learn" paradigm.
   - **Year**: 2017

7. **Title**: Prototypical Networks for Few-Shot Learning
   - **Authors**: Jake Snell, Kevin Swersky, Richard Zemel
   - **Summary**: Meta-learning via prototype representations in embedding space, offering alternative approach for metric calibration.
   - **Year**: 2017

8. **Title**: From Predictions to Explanations: Explainable AI for Autism Diagnosis
   - **Authors**: Kush Gupta, et al.
   - **Summary**: Demonstrates cross-domain transfer learning (general imaging → autism) with XAI (saliency, Grad-CAM, SHAP) is successful, providing empirical evidence for cross-domain XAI feasibility.
   - **Year**: 2025

9. **Title**: Transfer learning with XAI for robust malware and IoT network security
   - **Authors**: Ahmad S. Almadhor, et al.
   - **Summary**: Cross-domain transfer (malware → IoT) maintains 96% accuracy with XAI explainability, providing additional evidence for cross-domain XAI transfer feasibility.
   - **Year**: 2025

10. **Title**: Test Equating, Scaling, and Linking (3rd ed)
    - **Authors**: Michael J. Kolen, Robert L. Brennan
    - **Summary**: Educational assessment uses equating methods to calibrate scores across heterogeneous tests, providing analogous framework for validation metric calibration.
    - **Year**: 2014

**Key Challenges**

1. **Cross-Domain Validation Standardization**: Each domain uses incompatible metrics, preventing objective comparison of XAI effectiveness across domains (Deck 2023, Danilevsky 2021).

2. **Stakeholder Adaptation Operationalization**: While stakeholder differences have been observed (Aoki 2024, Tjoa 2019), no framework exists to operationalize automated stakeholder classification and adaptive metric selection.

3. **Validation Without Ground Truth**: Circular reasoning problem - how to validate validation frameworks when no absolute ground truth exists for XAI effectiveness.

4. **Limited Cross-Domain Empirical Evidence**: Only 2 out of 40 papers in Phase 1 review tested cross-domain transfer (Gupta 2025, Almadhor 2025), leaving transferability claims largely unvalidated.

5. **Meta-Learning for Validation Metrics**: No prior application of meta-learning techniques to validation metric calibration; existing meta-learning work focuses on model parameters, not evaluation protocols.

6. **Commensurability vs. Domain-Specificity Trade-off**: Tension between maintaining domain-specific validation rigor (clinical accuracy for healthcare, procedural justice for fairness) while enabling cross-domain comparison through unified constructs.

7. **Universal XAI Metrics Lack Normative Grounding**: Single universal metrics (e.g., fidelity, consistency) criticized for ignoring domain context and stakeholder requirements (Deck et al. 2023).

8. **Ad-Hoc Validation Practices**: Current practice involves project-specific, non-standardized validation approaches, preventing systematic knowledge accumulation across domains (Danilevsky et al. 2021).
