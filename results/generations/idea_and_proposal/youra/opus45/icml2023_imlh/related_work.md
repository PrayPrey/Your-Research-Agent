## Related Work

**Related Papers**
1. **Title**: Concept Bottleneck Models (arXiv:2007.04612)
   - **Authors**: Koh, Nguyen, Tang, Mussmann, Pierson, Kim, Liang
   - **Summary**: Introduces concept bottleneck models that enable concept-level intervention while achieving competitive accuracy with interpretation, serving as the foundational architecture for interpretable concept-based prediction.
   - **Year**: 2020

2. **Title**: Uncertainty Quantification for Machine Learning in Healthcare: A Survey (arXiv:2505.02874)
   - **Authors**: López et al.
   - **Summary**: Provides a comprehensive uncertainty quantification framework for healthcare ML pipelines and identifies a critical gap in concept-level uncertainty quantification methods.
   - **Year**: 2025

3. **Title**: Auto-Encoding Variational Bayes (arXiv:1312.6114)
   - **Authors**: Kingma & Welling
   - **Summary**: Introduces the reparameterization trick for variational inference, enabling gradient-based optimization of variational models and providing the theoretical foundation for variational concept layers.
   - **Year**: 2013

4. **Title**: Uncertainty-Aware Concept Bottleneck Models with Enhanced Interpretability (arXiv:2510.00773)
   - **Authors**: Zhang, Barry, Brandao
   - **Summary**: Proposes prototype-based uncertainty estimation for concept bottleneck models using distance from class prototypes as an alternative approach to uncertainty quantification in CBMs.
   - **Year**: 2025

5. **Title**: BC-LLM
   - **Authors**: Feng et al.
   - **Summary**: Addresses concept selection uncertainty by determining which concepts matter for prediction, but does not address concept value uncertainty (confidence in individual concept predictions).
   - **Year**: 2024

**Key Challenges**
1. **Lack of Concept-Level Uncertainty Quantification**: No existing work provides uncertainty quantification at the concept level within concept bottleneck models, representing a significant gap in interpretable ML for healthcare.

2. **Deterministic Concept Representations**: Vanilla CBM approaches use deterministic concept layers, resulting in lower calibration and no uncertainty estimates for concept predictions.

3. **Distinction Between Selection and Value Uncertainty**: Current methods like BC-LLM address which concepts matter (selection uncertainty) but fail to quantify how confident the model is in individual concept values (value uncertainty), leaving these as orthogonal problems requiring separate solutions.

4. **Limited Principled UQ Approaches**: Simple uncertainty quantification baselines like MC Dropout applied to CBMs are less principled than variational approaches, suggesting need for more theoretically grounded methods.
