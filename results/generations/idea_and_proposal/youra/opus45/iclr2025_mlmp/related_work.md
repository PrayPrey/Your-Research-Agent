## Related Work

**Related Papers**
1. **Title**: Machine learning renormalization group for statistical physics (DOI: 10.1088/2632-2153/ad0101)
   - **Authors**: Hou, You
   - **Summary**: MLRG automatically learns optimal RG transformations without supervision and demonstrates unsupervised phase classification in statistical physics systems.
   - **Year**: 2023

2. **Title**: Operator Learning Renormalization Group (arXiv:2403.03199)
   - **Authors**: Luo, Luo, Melko
   - **Summary**: OLRG unifies Wilson's NRG and White's DMRG through operator learning and provides scaling consistency bounds for renormalization group methods.
   - **Year**: 2024

3. **Title**: Transfer Learning in Physics-Informed Neural Networks (Semantic Scholar ID: c558528d781b11d55752d8e34fc6d5e5b8ada7cb)
   - **Authors**: Wang et al.
   - **Summary**: Demonstrates that LoRA significantly improves convergence in PINNs and shows that transfer learning works effectively across boundary conditions, materials, and geometries.
   - **Year**: 2025

4. **Title**: PhysiX: A Foundation Model for Physics Simulations
   - **Authors**: Not specified
   - **Summary**: A 4.5B parameter autoregressive model achieving state-of-the-art performance on The Well benchmark (18/21 evaluation points) using a data-driven approach without explicit RG structure.
   - **Year**: 2025

5. **Title**: GPhyT: General Physics Transformer
   - **Authors**: Not specified
   - **Summary**: Trained on 1.8TB of data with zero-shot generalization capabilities, achieving 5-29x improvement over FNO through an in-context learning approach.
   - **Year**: 2025

6. **Title**: Dreaming up scale invariance via inverse renormalization group
   - **Authors**: Rançon et al.
   - **Summary**: Demonstrates that minimal neural networks can invert RG coarse-graining and that simple local rules encode universality in physical systems.
   - **Year**: 2025

7. **Title**: A Renormalization Group Framework for Scale-Invariant Feature Learning
   - **Authors**: Liaw
   - **Summary**: Shows that layer-wise DNN transformations are analogous to RG transformations and introduces scale-aware activations for feature learning.
   - **Year**: 2025

8. **Title**: Coarse-Graining with Equivariant Neural Networks
   - **Authors**: Loose, Voth
   - **Summary**: Achieves data-efficient coarse-graining with symmetry preservation, enabling functional model learning from single frames.
   - **Year**: 2023

**Key Challenges**
1. **Lack of Explicit RG Structure in Foundation Models**: Current large-scale physics foundation models like PhysiX achieve strong performance through data-driven approaches but do not incorporate explicit renormalization group structure, potentially limiting their physical interpretability and generalization.

2. **Scale Invariance Learning**: Existing methods struggle to systematically learn and exploit scale invariance properties, with recent work only beginning to explore how neural networks can encode universality through inverse RG approaches.

3. **Unification of RG Methods with Modern Architectures**: While theoretical connections between RG transformations and neural network layers have been identified, practical integration of these principles into scalable foundation models remains an open problem.

4. **Transfer Learning Across Physical Domains**: Although transfer learning has shown promise in PINNs for adapting across boundary conditions and geometries, extending these capabilities to broader multi-physics scenarios with RG-based approaches is not yet established.

5. **Data Efficiency with Symmetry Preservation**: Achieving data-efficient learning while preserving physical symmetries through coarse-graining remains challenging, with current equivariant approaches limited in scope.
