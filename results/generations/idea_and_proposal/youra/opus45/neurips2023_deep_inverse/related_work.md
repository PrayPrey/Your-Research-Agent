## Related Work

**Related Papers**
1. **Title**: A Survey on Diffusion Models for Inverse Problems (arXiv:2024)
   - **Authors**: Daras, Dimakis, et al.
   - **Summary**: Provides a comprehensive taxonomy of diffusion models for inverse problems, identifying that cross-modality generalization remains underexplored in the field.
   - **Year**: 2024

2. **Title**: Improving Diffusion Models for Inverse Problems using Manifold Constraints (NeurIPS 2022)
   - **Authors**: Chung et al.
   - **Summary**: Introduces manifold constraint guidance (MCG) for diffusion-based inverse problem solvers, establishing a foundational methodology for constrained diffusion sampling.
   - **Year**: 2022

3. **Title**: MARBLE: Interpretable representations using geometric deep learning (Nature Methods)
   - **Authors**: Gosztolai et al.
   - **Summary**: Demonstrates that geometric manifold learning can transfer effectively across dynamical systems, providing inspiration for geometric latent space concepts in cross-domain applications.
   - **Year**: 2025

4. **Title**: LoRA: Low-Rank Adaptation of Large Language Models
   - **Authors**: Hu et al.
   - **Summary**: Shows that less than 1% of parameters are sufficient for effective fine-tuning of large models, establishing the adapter architecture methodology for parameter-efficient transfer.
   - **Year**: 2022

5. **Title**: HFS-SDE: High-Frequency Space Diffusion for MRI Reconstruction (TMI)
   - **Authors**: Not specified
   - **Summary**: Proposes a modality-specific diffusion approach operating in high-frequency space for MRI reconstruction tasks.
   - **Year**: 2024

6. **Title**: MCG_diffusion: Manifold Constraint Guided Diffusion (NeurIPS)
   - **Authors**: Not specified
   - **Summary**: Presents a general inverse problem solver using manifold constraints but without modular architecture design.
   - **Year**: 2022

7. **Title**: SMRD: SURE-based Robust MRI Reconstruction (NVIDIA)
   - **Authors**: Not specified
   - **Summary**: Focuses on robustness in MRI reconstruction using SURE-based approaches for improved reliability.
   - **Year**: 2023

8. **Title**: IP-Adapter: Image Prompting Adapter
   - **Authors**: Not specified
   - **Summary**: Demonstrates that adapters can efficiently preserve structural information while enabling style specialization in image generation tasks.
   - **Year**: 2023

9. **Title**: PaDIS: Patch-based Diffusion Priors for Data Efficiency
   - **Authors**: Not specified
   - **Summary**: Proposes a patch-based approach to diffusion priors for improved data efficiency, though not focused on cross-modality transfer.
   - **Year**: 2024

**Key Challenges**
1. **Cross-Modality Generalization Gap**: Current diffusion models for inverse problems lack exploration of cross-modality generalization capabilities, with most approaches being modality-specific.
2. **Modular Architecture Absence**: Existing general inverse problem solvers like MCG lack modular architectures that would enable efficient adaptation across different imaging modalities.
3. **Parameter Efficiency in Transfer**: Achieving effective transfer learning for inverse problems while maintaining parameter efficiency remains challenging, requiring adaptation strategies that modify minimal parameters.
4. **Data Efficiency Limitations**: Current approaches for data-efficient diffusion priors do not adequately address cross-modality transfer scenarios.
