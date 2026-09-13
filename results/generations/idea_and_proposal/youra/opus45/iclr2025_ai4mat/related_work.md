## Related Work

**Related Papers**
1. **Title**: Performance Assessment of Universal Machine Learning Interatomic Potentials: Challenges and Directions for Materials' Surfaces (arXiv:2403.04217)
   - **Authors**: Focassio, Freitas, Schleder
   - **Summary**: Demonstrates that universal MLIPs (MACE, CHGNet, M3GNet) exhibit significant out-of-domain failure on surface energies, with prediction errors correlated to distance from the training distribution.
   - **Year**: 2024

2. **Title**: Equivariant message passing for the prediction of tensorial properties and molecular spectra (PaiNN) (arXiv:2102.03150)
   - **Authors**: Schütt, Unke, Gastegger
   - **Summary**: Shows that rotationally equivariant representations improve prediction accuracy while reducing model size, providing architectural foundations for equivariant local features.
   - **Year**: 2021

3. **Title**: Atomistic Line Graph Neural Network for improved materials property predictions (ALIGNN) (DOI: 10.1038/s41524-021-00650-1)
   - **Authors**: Choudhary, DeCost
   - **Summary**: Demonstrates that explicit bond angle encoding via line graph representations improves property predictions by up to 85%, validating hierarchical decomposition approaches.
   - **Year**: 2021

4. **Title**: MatGL Library
   - **Authors**: Ko et al.
   - **Summary**: Provides a unified library with implementations of M3GNet, CHGNet, and MEGNet models for materials property prediction.
   - **Year**: 2025

5. **Title**: Multi-fidelity Physics-informed Learning (arXiv:2202.06139)
   - **Authors**: Ramezankhani et al.
   - **Summary**: Shows that transfer learning from low-fidelity to high-fidelity data with adaptive weighting improves model convergence in physics-informed settings.
   - **Year**: 2022

6. **Title**: Multi-Source Domain Generalization for ECG-Based Cognitive Load Estimation (DOI: 10.1109/ICASSP48485.2024.10447676)
   - **Authors**: Wang et al.
   - **Summary**: Demonstrates that adversarial learning can extract domain-invariant features across heterogeneous domains, providing precedent for cross-domain alignment techniques.
   - **Year**: 2024

7. **Title**: Structure-based out-of-distribution (OOD) materials property prediction: a benchmark study (DOI: 10.1038/s41524-024-01316-4)
   - **Authors**: Omee, Fu, Dong, Hu
   - **Summary**: Confirms that current GNN architectures significantly underperform on out-of-distribution property prediction tasks in materials science.
   - **Year**: 2024

**Key Challenges**
1. **Out-of-Domain Failure in Universal MLIPs**: Universal machine learning interatomic potentials show significant performance degradation when applied to surface energies and other properties outside their training distribution, with errors correlating to distance from training data.

2. **Generalization Gap in Materials Property Prediction**: Current graph neural network architectures exhibit substantial underperformance on out-of-distribution property prediction tasks, limiting their applicability to novel materials systems.

3. **Domain Heterogeneity**: Materials data spans heterogeneous domains with varying characteristics, requiring methods that can extract domain-invariant features for robust cross-domain generalization.

4. **Multi-Fidelity Data Integration**: Effectively leveraging data of varying fidelity levels (e.g., different computational methods or experimental sources) requires adaptive strategies for transfer learning and weighting.
