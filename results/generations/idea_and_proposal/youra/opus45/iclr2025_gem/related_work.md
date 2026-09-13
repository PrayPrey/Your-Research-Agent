## Related Work

**Related Papers**
1. **Title**: Integrating experimental feedback improves generative models for biological sequences (DOI/SS ID: a92bd0c7295febb07c2e8739b665eb7e27e2914f)
   - **Authors**: Calvanese et al.
   - **Summary**: Demonstrates that feedback integration significantly improves generative model success rates from 6.7% to 63.7% on ribozymes through direct probability modification approaches.
   - **Year**: 2025

2. **Title**: ProSpero: Active Learning for Robust Protein Design Beyond Wild-Type Neighborhoods (DOI/SS ID: fd72215ef6fc89ad126aea53931947bfcb7e3336)
   - **Authors**: Kmicikiewicz et al.
   - **Summary**: Proposes a frozen generative model combined with a learnable surrogate that achieves high fitness and novelty in protein design, validating the frozen+learnable paradigm.
   - **Year**: 2025

3. **Title**: De novo design of protein structure and function with RFdiffusion (DOI: 10.1038/s41586-023-06415-8)
   - **Authors**: Watson et al.
   - **Summary**: Introduces diffusion models for generating diverse, functional protein structures, serving as a foundational architecture for protein design.
   - **Year**: 2023

4. **Title**: Equivariant Graph Neural Networks (EGNN)
   - **Authors**: Satorras et al.
   - **Summary**: Establishes SE(3)-equivariant message passing with scalar-vector decomposition, providing the mathematical foundation for equivariant neural network architectures.
   - **Year**: 2021

5. **Title**: Augmented Memory
   - **Authors**: Guo & Schwaller
   - **Summary**: Achieves state-of-the-art sample efficiency for molecular generation via reinforcement learning approaches.
   - **Year**: 2024

**Key Challenges**
1. **Lack of Equivariant Conditioning Mechanisms**: Existing active learning approaches demonstrate the value of feedback integration but lack mechanisms for conditioning that preserve equivariance in protein models.
2. **Inapplicability of Molecular RL Methods to Proteins**: State-of-the-art sample-efficient methods like Augmented Memory are designed for molecules and cannot be directly applied to equivariant protein generative models.
3. **Limitations of Likelihood-Based Feedback Integration**: Current approaches like direct probability modification for feedback integration may not optimally leverage experimental data compared to conditioning-based approaches.
4. **Trade-offs in Model Adaptation**: Full fine-tuning approaches risk catastrophic forgetting and require substantial experimental data, while unconditional generation fails to incorporate valuable experimental feedback.
