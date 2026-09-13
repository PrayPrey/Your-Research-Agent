## Related Work

**Related Papers**
1. **Title**: AnyCBMs: How to Turn Any Black Box into a Concept Bottleneck Model (arXiv:2405.16508)
   - **Authors**: Dominici, Barbiero, Giannini, Gjoreski, Langhenirich
   - **Summary**: Proposes a residual pathway design that maintains model performance when concept coverage is incomplete, enabling conversion of black box models into concept bottleneck models.
   - **Year**: 2024

2. **Title**: Interpretability for Time Series Transformers using A Concept Bottleneck Framework (arXiv:2410.06070)
   - **Authors**: van Sprang, Acar, Zuidema
   - **Summary**: Demonstrates that concept bottleneck models can be applied to time series transformers, achieving interpretability without performance loss using CKA alignment.
   - **Year**: 2024

3. **Title**: Deep Fuzzy Cognitive Maps for Interpretable Multivariate Time Series Prediction
   - **Authors**: Wang, Peng, Wang, Li, Wu
   - **Summary**: Shows that hierarchical interpretable structures are effective for time series prediction tasks, providing inspiration for multi-scale concept hierarchy approaches.
   - **Year**: 2021

4. **Title**: HITS: Hierarchical Interpretable Time Series Classification via MIL
   - **Authors**: Han, Koay
   - **Summary**: Proposes variable-level and temporal attention mechanisms to provide post-hoc interpretability for time series classification.
   - **Year**: 2025

5. **Title**: Interpretable prognostics with concept bottleneck models
   - **Authors**: Not specified
   - **Summary**: Applies concept bottleneck models to remaining useful life (RUL) prediction using degradation concepts, demonstrating intervention capability for time series tasks.
   - **Year**: 2025

6. **Title**: Self-Interpretable Time Series with Counterfactual Explanations
   - **Authors**: Yan, Wang
   - **Summary**: Develops self-interpretable time series models using counterfactual explanations, though not based on self-supervised learning and limited to counterfactual approaches.
   - **Year**: 2023

7. **Title**: VLG-CBM: Training Concept Bottleneck Models with Vision-Language Guidance
   - **Authors**: Srivastava, Yan, Weng
   - **Summary**: Demonstrates that vision-language guidance improves concept faithfulness in concept bottleneck models, providing methodology for concept generation.
   - **Year**: 2024

**Key Challenges**
1. **Incomplete Concept Coverage**: Maintaining model performance when the defined concepts do not fully cover all relevant features in the data, requiring residual pathway designs.
2. **Interpretability-Performance Trade-off**: Achieving interpretability in time series models without sacrificing predictive performance.
3. **Self-Supervised Learning Gap**: Existing self-interpretable time series methods are not based on self-supervised learning, limiting their applicability to representation learning contexts.
4. **Limited Explanation Types**: Current interpretable time series approaches are often restricted to specific explanation methods (e.g., counterfactual only) rather than providing comprehensive concept-based interpretability.
5. **Concept Faithfulness**: Ensuring that learned concepts accurately and faithfully represent meaningful patterns in the data, particularly for time series domains.
