## Related Work

**Related Papers**
1. **Title**: Beyond Size and Accuracy: The Impact of Model Compression on Fairness (DOI: 10.32473/flairs.37.1.135617)
   - **Authors**: Moumita Kamal, Douglas Talbert
   - **Summary**: Empirically establishes that the type and amount of compression substantially impact both accuracy and fairness on the COMPAS dataset, demonstrating the problem of fairness degradation during model compression.
   - **Year**: 2024

2. **Title**: How Does Promoting the Minority Fraction Affect Generalization? (arXiv:2403.07310)
   - **Authors**: Hongkang Li, Shuai Zhang, et al.
   - **Summary**: Provides the first theoretical analysis of group-level generalization in ERM, finding that increasing minority fraction doesn't necessarily improve minority accuracy.
   - **Year**: 2024

3. **Title**: Comparative Assessment of Fairness Definitions and Bias Mitigation
   - **Authors**: Maria Eleftheria Vlontzou et al.
   - **Summary**: Demonstrates that 40-57% equalized odds improvement is achievable and establishes the need for composite fairness-performance measures in bias mitigation.
   - **Year**: 2025

4. **Title**: Quantizing deep convolutional networks for efficient inference
   - **Authors**: Krishnamoorthi
   - **Summary**: Introduces standard Quantization-Aware Training (QAT) methodology for efficient neural network inference through quantization.
   - **Year**: 2018

5. **Title**: Learning both Weights and Connections
   - **Authors**: Han et al.
   - **Summary**: Proposes magnitude-based pruning as a technique for neural network compression by learning both weights and network connections.
   - **Year**: 2015

6. **Title**: Mechanisms Promoting Biodiversity in Ecosystems (DOI: 10.1002/qub2.77)
   - **Authors**: Kang et al.
   - **Summary**: Demonstrates that ecosystems maintain diversity through explicit minority (endemic species) protection mechanisms, providing cross-domain inspiration for feature protection concepts.
   - **Year**: 2024

7. **Title**: AI Fairness 360 (AIF360)
   - **Authors**: Not specified
   - **Summary**: Provides an open-source toolkit for implementing and evaluating fairness metrics in machine learning systems.
   - **Year**: Not specified

**Key Challenges**
1. **Compression-Fairness Trade-off**: Model compression techniques substantially impact both accuracy and fairness, with different compression types and amounts producing varying effects on protected groups.

2. **Minority Group Generalization**: Increasing minority fraction in training data does not necessarily improve minority group accuracy, indicating that simple rebalancing approaches are insufficient.

3. **Fairness Metric Selection**: The need for composite fairness-performance measures highlights the difficulty in selecting appropriate metrics that capture both model utility and equitable treatment across groups.

4. **Lack of Minority-Aware Compression**: Standard compression techniques like QAT and magnitude-based pruning do not explicitly account for features important to minority groups, potentially exacerbating fairness issues during model compression.
