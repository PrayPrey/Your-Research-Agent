## Related Work

**Related Papers**
1. **Title**: Matformer: Periodic Graph Transformers for Crystal Material Property Prediction (Yan et al., 2022)
   - **Authors**: Yan, K., Liu, Y., Lin, Y.C., & Ji, S.
   - **Summary**: Foundation for periodic invariance via learned lattice encodings and repeating pattern transformer for crystal materials. Achieves MAE = 0.022 eV/atom on MatBench benchmark using Materials Project ~100k structures.
   - **Year**: 2022

2. **Title**: Equivariant Networks for Crystal Structures (Kaba & Ravanbakhsh, 2022)
   - **Authors**: Kaba, S., & Ravanbakhsh, S.
   - **Summary**: Provides theoretical foundation for equivariance across crystallographic groups, with generalized message passing maintaining symmetry under space group operations.
   - **Year**: 2022

3. **Title**: E3NN: Euclidean Neural Networks (Geiger & Smidt, 2022)
   - **Authors**: Geiger, M., & Smidt, T.
   - **Summary**: Software library providing E(3)-equivariant tensor operations with spherical harmonics, enabling equivariant message passing layers and periodic boundary condition handling.
   - **Year**: 2022

4. **Title**: Learning Transferable Visual Models From Natural Language Supervision (CLIP) (Radford et al., 2021)
   - **Authors**: Radford, A., et al.
   - **Summary**: Introduces cross-domain contrastive alignment by aligning image and text encoders in shared latent space via contrastive learning. Serves as inspiration for multi-encoder shared space paradigm.
   - **Year**: 2021

5. **Title**: BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding (Devlin et al., 2019)
   - **Authors**: Devlin, J., et al.
   - **Summary**: Introduces subword tokenization and pre-training paradigm where models pre-train on large corpus then fine-tune on downstream tasks. Demonstrates 70-80% of monolingual performance with 10% of data in transfer learning.
   - **Year**: 2019

6. **Title**: Smooth Overlap of Atomic Positions (SOAP) (Bartók et al., 2013)
   - **Authors**: Bartók, A. P., et al.
   - **Summary**: Develops rotation-invariant descriptor of local atomic environment via spherical harmonics expansion. Used in ML potentials to predict energies with ~meV/atom accuracy.
   - **Year**: 2013

7. **Title**: Structure-based Out-of-Distribution Materials Property Prediction (Omee et al., 2024)
   - **Authors**: Omee, S. S., et al.
   - **Summary**: Identifies five OOD categories for materials (structure, chemistry, property, etc.) and reveals generalization gap. Shows structure-based features enable generalization across composition space within crystals.
   - **Year**: 2024

8. **Title**: CHGNet: Pretrained Universal Neural Network Potential for Charge-Informed Atomistic Modeling (Deng et al., 2023)
   - **Authors**: Deng, B., et al.
   - **Summary**: Develops single universal potential trained on Materials Project (100k+ crystals) with charge prediction. Demonstrates charge-informed potentials (electronics) improve accuracy through hierarchical information.
   - **Year**: 2023

9. **Title**: DiffCSP: Crystal Structure Prediction with Diffusion (Jiao et al., 2023)
   - **Authors**: Jiao, R., et al.
   - **Summary**: Proposes joint diffusion over lattice vectors and atomic positions with equivariance for generative modeling of crystals. Provides lattice parametrization approach used in adaptive graph construction.
   - **Year**: 2023

10. **Title**: PyTorch Geometric (Fey & Lenssen, 2019)
    - **Authors**: Fey, M., & Lenssen, J. E.
    - **Summary**: Software library providing efficient message passing on irregular graph structures with core GNN layers, data structures, and training utilities for materials modeling.
    - **Year**: 2019

11. **Title**: Matbench: Benchmark Suite for Materials Property Prediction (Dunn et al., 2020)
    - **Authors**: Dunn, A., et al.
    - **Summary**: Establishes 13 standardized evaluation tasks on Materials Project data with leaderboard for crystal property prediction benchmarking.
    - **Year**: 2020

**Key Challenges**
1. **Data Silos Across Material Classes**: Materials Project (crystals), PoLyInfo (polymers), and Catalysis-Hub (surfaces) are separate databases with different formats, creating barriers to unified modeling approaches.

2. **Fundamental Physics Differences**: Periodic vs. non-periodic vs. semi-periodic boundary conditions appear fundamentally incompatible, leading to assumption that separate models are necessary for each material class.

3. **Limited Cross-Class Transfer Learning**: No existing work addresses multi-class unification for materials. Closest approaches include multi-task learning on multiple properties within single class (e.g., CHGNet predicts energy, forces, stresses for crystals only) or transfer learning within single class composition shifts.

4. **Community Fragmentation**: Crystal ML researchers (materials science) and polymer ML researchers (chemistry/chemical engineering) operate in separate venues, limiting cross-pollination of methods.

5. **Quantum Mechanical Coupling Challenge**: The assumption that "grammar" (physics) can be separated from "vocabulary" (atoms) faces theoretical tension, as quantum mechanics is non-separable—local atomic environment properties emerge from global electronic structure (band structure in crystals vs. localized orbitals in molecules).

6. **Dataset Sufficiency for Transfer Validation**: Compositional overlap across material classes may be limited, restricting transfer evaluation to narrow chemical space. Requires validation that carbon-based materials and oxides provide sufficient overlap.

7. **Out-of-Distribution Generalization Gap**: As identified by Omee et al. (2024), materials models struggle with structure-based, chemistry-based, and property-based OOD categories within single material class, and extending to cross-class OOD presents additional challenges.

8. **Computational Scaling Limitations**: Memory scaling may limit batch size for structures >200 atoms with multi-encoder architectures, potentially slowing convergence and limiting practical applicability.

9. **Measurement Heterogeneity**: Properties like glass transition temperature depend on measurement method (DSC, DMA, simulation) with experimental variability ~5-10K, making it difficult to establish ground truth for transfer learning validation.

10. **Equivariance Compatibility Across Classes**: Different equivariance groups per class (E(3) for crystals, SE(3) for polymers, E(2)×T for surfaces) require careful architecture design to handle without conflicts while maintaining physical validity.
