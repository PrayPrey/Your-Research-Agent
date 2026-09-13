## Related Work

**Related Papers**
1. **Title**: Diagnosing failures of fairness transfer across distribution shift in real-world medical settings
   - **Authors**: Schrouff, Harris et al.
   - **Summary**: Provides a causal framing for diagnosing distribution shift effects, establishing theoretical foundations for drift detection design in medical settings.
   - **Year**: 2022

2. **Title**: Towards Foundation Models for Critical Care Time Series
   - **Authors**: Burger, Sergeev et al.
   - **Summary**: Introduces a harmonized dataset for transfer learning and is the first work to address distribution shift arising from varying treatment policies in critical care settings.
   - **Year**: 2024

3. **Title**: Automatic correction of performance drift under acquisition shift in medical image classification
   - **Authors**: Roschewitz, Khara, Yearsley et al.
   - **Summary**: Proposes Unsupervised Prediction Alignment that preserves sensitivity/specificity without requiring labels, validating automatic recalibration approaches for medical imaging.
   - **Year**: 2023

4. **Title**: Self-Supervised Transformer for Sparse and Irregularly Sampled Multivariate Clinical Time-Series
   - **Authors**: Tipirneni, Reddy
   - **Summary**: Introduces STraTS observation triplet representation, providing a foundational architecture for handling sparse and irregular healthcare time series data.
   - **Year**: 2021

5. **Title**: Empirical data drift detection experiments on real-world medical imaging data
   - **Authors**: Kore, Bavil et al.
   - **Summary**: Demonstrates that drift detection is feasible in medical imaging but identifies that current methods lack systematic deployment integration.
   - **Year**: 2024

**Key Challenges**
1. **Lack of Systematic Deployment Integration**: Current drift detection methods have been shown to work empirically but lack frameworks for systematic integration into clinical deployment pipelines.

2. **Distribution Shift from Varying Treatment Policies**: Critical care settings experience distribution shifts due to changing treatment protocols, which existing models do not adequately address.

3. **Label-Free Adaptation Requirements**: Medical settings often lack timely ground truth labels, necessitating unsupervised approaches for model recalibration and performance maintenance.

4. **Foundation Model Deployment Gap**: Existing foundation models for critical care focus primarily on accuracy improvements but lack comprehensive deployment frameworks for real-world clinical use.

5. **Handling Sparse and Irregular Clinical Data**: Healthcare time series data is inherently sparse and irregularly sampled, requiring specialized architectural approaches for effective modeling.
