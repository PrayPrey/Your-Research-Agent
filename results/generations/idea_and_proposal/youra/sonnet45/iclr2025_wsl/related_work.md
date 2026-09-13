## Related Work

**Related Papers**
1. **Title**: Permutation Equivariant Neural Functionals (Zhou et al., NeurIPS 2023)
   - **Authors**: Zhou et al.
   - **Summary**: Introduced NF-Layers for processing weights of other networks with permutation equivariance, demonstrating 17% improvement in INR classification and enabling weight space learning for neural networks.
   - **Year**: 2023

2. **Title**: Equivariant Architectures for Learning in Deep Weight Spaces (Navon et al., ICML 2023)
   - **Authors**: Navon et al.
   - **Summary**: Provided full characterization of affine equivariant/invariant layers for MLP weight permutations, introducing DWS-layers (pooling, broadcasting, FC) for weight space processing.
   - **Year**: 2023

3. **Title**: Graph Metanetworks for Processing Diverse Neural Architectures (Lim et al., ICLR 2024)
   - **Authors**: Lim et al.
   - **Summary**: Developed graph-based approach for diverse feed-forward architectures, demonstrating INR editing with 95% reconstruction fidelity and computational graph representation for neural networks.
   - **Year**: 2024

4. **Title**: The Impact of Model Zoo Size and Composition on Weight Space Learning (Falk et al., 2025)
   - **Authors**: Falk et al.
   - **Summary**: Addressed extension of weight space learning to heterogeneous populations, identifying dataset diversity impact and zero-shot transfer capabilities across architectures.
   - **Year**: 2025

5. **Title**: Equivariant Neural Functional Networks for Transformers (Tran-Viet et al., 2024)
   - **Authors**: Tran-Viet et al.
   - **Summary**: Developed architecture-specific NFN for transformers with maximal symmetric group for attention heads, creating 125K transformer checkpoint dataset for validation.
   - **Year**: 2024

6. **Title**: Applied Category Theory in the Wolfram Language using Categorica I (Gorard, 2024)
   - **Authors**: Gorard
   - **Summary**: Provides mathematical foundation for functors as structure-preserving mappings, introducing universal constructions, limits and colimits, and natural transformations applicable to neural weight spaces.
   - **Year**: 2024

7. **Title**: Lax structures in 2-category theory (Štěpán, 2025)
   - **Authors**: Štěpán
   - **Summary**: Theoretical framework for lax functors enabling approximate structure preservation through weak structures turned strict universally with lax-idempotent relaxation.
   - **Year**: 2025

8. **Title**: LieOTAlign: Differentiable Protein Structure Alignment (Hu et al., 2025)
   - **Authors**: Hu et al.
   - **Summary**: Developed heterogeneous structure alignment using Lie groups for continuous symmetries and optimal transport for distance metrics, successfully unifying heterogeneous protein folds.
   - **Year**: 2025

9. **Title**: SIFT-based protein structure alignment (Guo et al., 2023)
   - **Authors**: Guo et al.
   - **Summary**: Introduced scale-invariant features and distance matrix representation for flexible protein structure alignment, providing methodological inspiration for heterogeneous structure processing.
   - **Year**: 2023

10. **Title**: Task Arithmetic Through The Lens Of One-Shot Federated Learning (Tao et al., TMLR 2024)
    - **Authors**: Tao et al.
    - **Summary**: Provided theoretical framework for task arithmetic showing FedAvg equivalence and mathematical analysis of data/training heterogeneity in weight space operations.
    - **Year**: 2024

11. **Title**: Revisiting Weight Averaging for Model Merging (Choi et al., 2024)
    - **Authors**: Choi et al.
    - **Summary**: Analyzed state-of-the-art model merging with centered task vectors, low-rank approximation, and singular value concentration for improved interpolation-based merging.
    - **Year**: 2024

12. **Title**: On the Expressive Power of Permutation-Equivariant Weight-Space Networks (Dayan et al., 2026)
    - **Authors**: Dayan et al.
    - **Summary**: Proved equivalent expressive power of weight space learning architectures and established universality conditions in weight- and function-space settings.
    - **Year**: 2026

13. **Title**: Geometry of Linear Neural Networks: Equivariance and Invariance (Kohn et al., 2023)
    - **Authors**: Kohn et al.
    - **Summary**: Characterized weight space as determinantal variety and provided geometric interpretation of equivariant/invariant functions under permutation groups.
    - **Year**: 2023

14. **Title**: A Model Zoo on Phase Transitions in Neural Networks (Schürholt et al., 2025)
    - **Authors**: Schürholt et al.
    - **Summary**: Created 12 large-scale model zoos covering phase transitions in neural networks, demonstrating that phase transitions affect weight averaging and contrastive learning design.
    - **Year**: 2025

15. **Title**: mergekit (arcee-ai)
    - **Authors**: Not specified
    - **Summary**: Industry-standard model merging tool implementing SLERP, Task Arithmetic, TIES, DARE methods requiring architecture matching, with 6.7k GitHub stars demonstrating production-scale adoption.
    - **Year**: Not specified

16. **Title**: AllanYangZhou/universal_neural_functional
    - **Authors**: Not specified
    - **Summary**: Implementation of Universal Neural Functional (UNF) algorithm with automatic symmetry construction and equivariant layer implementations for weight space processing.
    - **Year**: Not specified

17. **Title**: mkofinas/neural-graphs (ICLR 2024 Oral)
    - **Authors**: Not specified
    - **Summary**: GNN-based weight processing with computational graph construction from weight tensors, presented as oral at ICLR 2024.
    - **Year**: 2024

**Key Challenges**
1. **Architecture Heterogeneity Gap**: Existing neural functionals work only for single architecture families (CNNs or Transformers separately) and cannot unify heterogeneous architectures with incompatible symmetry groups (translation, permutation, temporal).

2. **Scalability Limitations**: Flat weight encoding approaches scale as O(n²) and cannot handle billion-parameter models; hierarchical coarsening needed to achieve O(n log n) complexity.

3. **Lack of Theoretical Foundation**: Model merging methods (mergekit) are heuristic and lack mathematical framework for principled cross-architecture operations despite production-scale success.

4. **Approximate Symmetry Handling**: Neural networks exhibit approximate (not exact) symmetries requiring lax functorial constraints, but optimal relaxation parameter α and its impact on downstream tasks remain empirically underdetermined.

5. **Universal Space Existence**: Unknown whether a universal latent space U exists with sufficient capacity to accommodate embeddings from all architecture types while maintaining semantic relationships across heterogeneous populations.

6. **Feed-Forward Limitation**: Graph Metanetworks limited to feed-forward variants and cannot handle recurrent architectures or long-range temporal dependencies in RNNs.

7. **Zero-Shot Generalization**: Unknown how well weight space learning generalizes to novel architectures discovered through Neural Architecture Search without manual symmetry group specification.

8. **Semantic Validity of Cross-Architecture Operations**: Unclear whether interpolation between heterogeneous architectures (e.g., 0.5·CNN + 0.5·Transformer) produces semantically valid and functional models.

9. **Multi-Task Alignment**: Models trained on different tasks (classification vs detection) require task-agnostic behavioral loss definitions for meaningful weight space alignment.

10. **Training Data Requirements**: Requires diverse model zoos (100+ models per architecture type) for learning universal encoders, creating data collection challenges.
