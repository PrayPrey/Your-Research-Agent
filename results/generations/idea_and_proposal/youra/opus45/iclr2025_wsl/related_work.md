## Related Work

**Related Papers**
1. **Title**: Compositional generalization through abstract representations in human and artificial neural networks
   - **Authors**: Ito, Klinger, Schultz, Murray, Cole, Rigotti
   - **Summary**: Demonstrates that primitives pretraining enables zero-shot compositional generalization, with abstract representations being key to transfer across tasks.
   - **Year**: 2022

2. **Title**: Graph Neural Networks for Learning Equivariant Representations of Neural Networks (Kofinas et al., 2024)
   - **Authors**: Kofinas et al.
   - **Summary**: Shows that neural networks can be represented as computational graphs and that GNNs can preserve permutation symmetry when processing weight spaces.
   - **Year**: 2024

3. **Title**: Universal Neural Functionals (Zhou et al., 2024)
   - **Authors**: Zhou et al.
   - **Summary**: Introduces auto-construction of equivariant models that can process weight spaces from any architecture.
   - **Year**: 2024

4. **Title**: Permutation Equivariant Neural Functionals (Zhou et al., 2023)
   - **Authors**: Zhou et al.
   - **Summary**: Proposes a framework for permutation equivariant weight processing using NF-Layers.
   - **Year**: 2023

5. **Title**: SANE (Schürholt et al., 2024)
   - **Authors**: Schürholt et al.
   - **Summary**: Introduces sequential weight processing methods focused on same-architecture neural network analysis.
   - **Year**: 2024

6. **Title**: Neural Graphs (Kofinas et al., 2024)
   - **Authors**: Kofinas et al.
   - **Summary**: Proposes node-level GNN processing for neural network weights, supporting multi-architecture settings but without motif-based approaches.
   - **Year**: 2024

7. **Title**: NFN (Zhou et al., 2023)
   - **Authors**: Zhou et al.
   - **Summary**: Develops layer-level equivariant processing methods for neural network weight spaces.
   - **Year**: 2023

8. **Title**: MultiZoo-SANE (Falk et al., 2025)
   - **Authors**: Falk et al.
   - **Summary**: Represents the first attempt at processing heterogeneous model zoos, revealing limitations of existing approaches.
   - **Year**: 2025

9. **Title**: The Impact of Model Zoo Size and Composition
   - **Authors**: Not specified
   - **Summary**: Demonstrates the need for cross-architecture methods when working with diverse model collections.
   - **Year**: Not specified

**Key Challenges**
1. **Same-Architecture Limitation**: Existing methods like SANE focus primarily on processing weights from networks with identical architectures, limiting applicability to diverse model zoos.
2. **Lack of Motif-Based Representations**: Current multi-architecture approaches like Neural Graphs operate at the node level without leveraging motif-based structural patterns that could enable better generalization.
3. **Heterogeneous Zoo Processing**: As evidenced by MultiZoo-SANE, processing model zoos with diverse architectures remains challenging, with existing methods showing significant limitations.
4. **Cross-Architecture Generalization**: There is a demonstrated need for methods that can effectively transfer knowledge and representations across different neural network architectures.
