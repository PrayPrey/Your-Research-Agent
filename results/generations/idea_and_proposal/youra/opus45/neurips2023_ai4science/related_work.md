## Related Work

**Related Papers**
1. **Title**: E(3)-equivariant graph neural networks for data-efficient and accurate interatomic potentials (NequIP)
   - **Authors**: Batzner et al.
   - **Summary**: Demonstrates that E(3)-equivariant convolutions achieve 1000x data efficiency in molecular dynamics simulations, validating that symmetry encoding dramatically improves data efficiency.
   - **Year**: 2022

2. **Title**: Universal Physics Transformers
   - **Authors**: Alkin, Furst, Schmid, et al.
   - **Summary**: Proposes a unified architecture for mesh-based, steady-state, and Lagrangian simulations without explicit equivariance, establishing that transfer learning is possible across physics domains without built-in symmetry constraints.
   - **Year**: 2024

3. **Title**: FMint: Bridging Human Designed and Data Pretrained Models for Differential Equation Foundation Model
   - **Authors**: Song, Yuan, Yang
   - **Summary**: Presents a foundation model for dynamical systems that achieves 1-2 orders of magnitude accuracy improvement via error correction, validating the multi-physics pretraining approach for foundation models.
   - **Year**: 2024

4. **Title**: Equivariant Adaptation of Large Pretrained Models
   - **Authors**: Not specified
   - **Summary**: Demonstrates that LoRA-style adapters can preserve equivariance while enabling efficient fine-tuning, providing an adapter mechanism for efficient domain adaptation.
   - **Year**: 2023

5. **Title**: Towards Scientific Discovery with Generative AI
   - **Authors**: Not specified
   - **Summary**: Identifies the need for unified AI4Science frameworks, highlighting gaps in current approaches to scientific machine learning.
   - **Year**: 2024

**Key Challenges**
1. **Cross-domain transfer in physics ML**: Current methods remain domain-siloed, with cross-domain transfer in physics machine learning remaining an unsolved problem.
2. **Lack of unified AI4Science frameworks**: Existing approaches lack unified frameworks that can generalize across different scientific domains and physics problems.
3. **Trade-off between equivariance and transfer learning**: While non-equivariant architectures enable transfer across domains, incorporating equivariance may improve transfer efficiency, but this hypothesis remains to be validated.
