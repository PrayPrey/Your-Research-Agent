## Related Work

**Related Papers**
1. **Title**: Systematic softening in universal machine learning interatomic potentials (DOI: 10.1038/s41524-024-01500-6)
   - **Authors**: Deng, Choi, Zhong, Riebesell, Anand, Li, Jun, Persson, Ceder
   - **Summary**: Identifies systematic PES softening (energy/force underprediction) in M3GNet, CHGNet, MACE-MP-0 across surfaces, defects, and solid-solutions, establishing the core problem of systematic bias in universal MLIPs.
   - **Year**: 2025

2. **Title**: Performance Assessment of Universal Machine Learning Interatomic Potentials: Challenges and Directions for Materials' Surfaces (arXiv:2403.04217)
   - **Authors**: Focassio, Freitas, Schleder
   - **Summary**: Demonstrates that errors in universal MLIPs are correlated to out-of-domain distance from training data, providing empirical evidence for the representation bias hypothesis.
   - **Year**: 2024

3. **Title**: Domain-Adversarial Training of Neural Networks (JMLR 17(1):2096-2030)
   - **Authors**: Ganin, Ustinova, Ajakan, Germain, Larochelle, Laviolette, Marchand, Lempitsky
   - **Summary**: Introduces the gradient reversal layer that enables learning domain-invariant features, providing the foundational method for domain-adversarial approaches.
   - **Year**: 2016

4. **Title**: MACE-MP-0
   - **Authors**: Batatia et al.
   - **Summary**: State-of-the-art universal MLIP trained on Materials Project, serving as the primary baseline for comparison in universal interatomic potential evaluation.
   - **Year**: 2023

5. **Title**: CHGNet
   - **Authors**: Deng et al.
   - **Summary**: Universal MLIP incorporating charge information, serving as a secondary baseline to demonstrate generality of approaches across different MLIP architectures.
   - **Year**: 2023

6. **Title**: GNN + domain adaptation for mechanical fault diagnosis
   - **Authors**: Tang et al.
   - **Summary**: Demonstrates that domain adaptation techniques work effectively for graph-structured data in mechanical fault diagnosis applications, validating the approach for GNN-based models.
   - **Year**: 2024

7. **Title**: Domain-shift resistance through sparse fine-tuning
   - **Authors**: Han et al.
   - **Summary**: Proposes sparse fine-tuning methods for domain-shift resistance, inspiring shared-private architecture design approaches.
   - **Year**: 2025

8. **Title**: MLIP Arena
   - **Authors**: Chiang et al.
   - **Summary**: Introduces a new benchmark that reveals failure modes in machine learning interatomic potentials, serving as a validation target for comprehensive MLIP evaluation.
   - **Year**: 2025

**Key Challenges**
1. **Systematic PES Softening**: Universal MLIPs exhibit systematic underprediction of energies and forces across surfaces, defects, and solid-solutions, indicating a fundamental bias in current models.

2. **Out-of-Domain Generalization**: Errors in universal MLIPs correlate with distance from training data distribution, suggesting that models struggle to generalize to atomic configurations underrepresented in training sets.

3. **Representation Bias**: Current universal MLIPs develop biased internal representations that favor bulk-like configurations dominant in training data, leading to systematic errors for non-bulk structures.

4. **Domain Shift in Materials**: The significant structural differences between bulk materials and surfaces/defects create domain shift challenges that standard training approaches fail to address adequately.
