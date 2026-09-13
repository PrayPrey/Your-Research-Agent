## Related Work

**Related Papers**

1. **Title**: Geometric Deep Learning: Grids, Groups, Graphs, Geodesics, and Gauges (arXiv:2104.13478)
   - **Authors**: Bronstein, M. M., Bruna, J., Cohen, T., & Veličković, P.
   - **Summary**: Establishes group-theoretic framework for equivariant neural networks, providing strong inductive bias for geometric data through symmetry (group equivariance). Does not address global topological structure (only local geometric symmetries).
   - **Year**: 2021

2. **Title**: Categorical Equivariant Deep Learning: Category-Equivariant Neural Networks (Semantic Scholar ID: 9e0276e4f37505d782de1fba4db23c54df796d68)
   - **Authors**: Maruyama, Y.
   - **Summary**: Provides category theory framework unifying different equivariance types. Shows that groups, groupoids, posets, lattices all fit in categorical framework with universal approximation.
   - **Year**: 2025

3. **Title**: Symmetry Group Equivariant Convolutions for Representation Learning: A Survey (Semantic Scholar ID: 469d0e514a87b3c24c8ad4211f8396c8be707ab8)
   - **Authors**: Basheer, S., & Mishra, A. K.
   - **Summary**: Survey of equivariant convolutions (regular, steerable, PDE-based) identifying gap in equivariant networks—no topological constraints integrated with geometric symmetries.
   - **Year**: 2025

4. **Title**: e3nn: Euclidean Neural Networks (arXiv:2207.09453)
   - **Authors**: Geiger, M., & Smidt, T. E.
   - **Summary**: E(3)-equivariant neural network implementation using spherical harmonics and tensor products for efficient equivariant layers. Provides baseline architecture for geometric feature extraction.
   - **Year**: 2020

5. **Title**: SchNet: A continuous-filter convolutional neural network for modeling quantum interactions
   - **Authors**: Schütt, K. T., Kindermans, P.-J., Sauceda, H. E., Chmiela, S., Tkatchenko, A., & Müller, K.-R.
   - **Summary**: Continuous filter convolutions on molecular graphs with distance-based features for molecular property prediction. Lacks topological awareness (cannot distinguish cyclic vs. acyclic with same local geometry).
   - **Year**: 2018

6. **Title**: PersLay: A Simple and Versatile Neural Network Layer for Persistence Diagrams
   - **Authors**: Carrière, M., Chazal, F., Ike, Y., Lacombe, T., Royer, M., & Umeda, Y.
   - **Summary**: Vectorizes persistence diagrams using learnable weight functions for integration with neural networks. Topological features are precomputed inputs rather than learned end-to-end as layers.
   - **Year**: 2020

7. **Title**: TopoReg: Topological Regularization for Neural Networks
   - **Authors**: Hu et al. (inferred)
   - **Summary**: Uses topology as regularization by adding topological loss (e.g., enforce correct Betti numbers) to regularize training. Topology acts as constraint rather than learned representation.
   - **Year**: 2021

8. **Title**: Computational Topology: An Introduction
   - **Authors**: Edelsbrunner, H., & Harer, J.
   - **Summary**: Foundational text establishing persistence stability theorem: persistent homology is stable such that small perturbations cause bounded changes to persistence diagrams (bottleneck distance bound).
   - **Year**: 2010

9. **Title**: Computing Equivariant Matrices on Homogeneous Spaces (Semantic Scholar ID: 39911b1e)
   - **Authors**: Knibbeler, V.
   - **Summary**: Mathematical framework for equivariance on topological spaces. Shows equivariant maps on homogeneous spaces (quotient topologies) can be computed via coordinate-free methods.
   - **Year**: 2023

10. **Title**: Ring attractor dynamics in the Drosophila head direction circuit
    - **Authors**: Kim, S. S., Rouault, H., Druckmann, S., & Jayaraman, V.
    - **Summary**: Demonstrates biological evidence for topological structure in neural circuits. Fly head direction circuit has ring topology (S¹ manifold) enabling robust angular encoding.
    - **Year**: 2017

11. **Title**: Grid cell activities in entorhinal cortex
    - **Authors**: Gardner, R. J., et al.
    - **Summary**: Shows biological evidence for geometric structure (hexagonal symmetry) in spatial representations. Grid cells exhibit hexagonal firing patterns with group-theoretic symmetry, demonstrating biological neural systems leverage both geometry and topology simultaneously.
    - **Year**: 2022

12. **Title**: GemNet: Universal Directional Graph Neural Networks for Molecules
    - **Authors**: Gasteiger, J., Becker, F., & Günnemann, S.
    - **Summary**: Current SOTA for molecular property prediction using directional message passing with equivariant geometric features. Achieves MAE 0.012 eV on QM9 but lacks explicit topological awareness for cyclic vs. acyclic molecules.
    - **Year**: 2021

13. **Title**: PointNeXt: Revisiting PointNet++ with Improved Training and Scaling
    - **Authors**: Qian, G., Li, Y., Peng, H., Mai, J., Hammoud, H., Elhoseiny, M., & Ghanem, B.
    - **Summary**: Current SOTA for 3D shape classification (92.9% accuracy on ModelNet40) using improved PointNet++ with better training strategies and scaling. Uses local geometric features only without global topology.
    - **Year**: 2022

14. **Title**: Graph Neural Networks with Ricci Curvature
    - **Authors**: Not specified
    - **Summary**: Alternative geometric-topological hybrid approach using discrete Ricci curvature as edge features in GNNs. Provides single scalar per edge whereas persistent homology captures multi-scale global topology.
    - **Year**: Not specified

**Key Challenges**

1. **Lack of Unified Topological-Geometric Framework**: No existing framework combines topological data analysis (persistent homology) with geometric deep learning (equivariant neural networks) in an end-to-end differentiable manner.

2. **Topological Features as Preprocessing Only**: Prior work (PersLay) treats topological features as precomputed inputs rather than learned representations, preventing end-to-end topological learning.

3. **No Global Topological Awareness in Geometric Networks**: Equivariant neural networks (E3nn, SchNet, GemNet) capture local geometric symmetries but cannot distinguish topologically different structures with similar local geometry (e.g., cyclic vs. acyclic molecules).

4. **Computational Scalability of Topological Computation**: Global persistent homology has O(n³) complexity, making it impractical for large point clouds without local sampling strategies.

5. **Missing Theoretical Foundation**: Absence of mathematical framework proving that topological and geometric constraints can be enforced simultaneously without conflict.

6. **Limited Differentiability of Topological Layers**: Topological regularization approaches (TopoReg) use topology as loss function only, not as differentiable feature extraction layers within the network.

7. **Domain-Specific Performance Gaps**: Existing methods struggle on tasks where topological structure is predictive (molecular ring detection, 3D genus classification, neural circuit connectivity) due to lack of topological inductive bias.

8. **Redundancy vs. Complementarity Unclear**: Unknown whether topological and geometric features provide complementary information or are redundant for structured representation learning tasks.
