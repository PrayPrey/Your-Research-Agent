## Related Work

**Related Papers**

1. **Title**: E(n) Equivariant Graph Neural Networks (Satorras et al., 2021)
   - **Authors**: Satorras et al.
   - **Summary**: Introduces scalable E(n)-equivariant message passing for molecular tasks without expensive higher-order representations. This serves as the primary baseline architecture for static molecular property prediction.
   - **Year**: 2021

2. **Title**: Neural Ordinary Differential Equations (Chen et al., 2018)
   - **Authors**: Chen et al.
   - **Summary**: Foundational work introducing continuous-time modeling via ODE integration with adjoint method for backpropagation. Enables neural networks to model continuous dynamics.
   - **Year**: 2018

3. **Title**: Principles of Equivariant Neural Networks (Kondor, 2025)
   - **Authors**: Kondor
   - **Summary**: Provides theoretical foundations explaining why equivariant operations take specific forms, deriving general structure of E(n)-equivariant layers via Clebsch-Gordan theory. Explicitly notes absence of temporal/dynamical aspects in current equivariance theory.
   - **Year**: 2025

4. **Title**: Geometric Deep Learning and Equivariant Neural Networks (Gerken et al., 2021)
   - **Authors**: Gerken et al.
   - **Summary**: Establishes mathematical foundations including gauge equivariance and principal bundles, generalizing equivariance to manifolds via fiber bundles.
   - **Year**: 2021

5. **Title**: On Path Integration of Grid Cells (Gao et al., 2020)
   - **Authors**: Gao et al.
   - **Summary**: Demonstrates that grid cells perform continuous temporal integration via group representation and isotropic scaling while maintaining E(2) hexagonal lattice symmetry during movement. Provides biological evidence for combining equivariance with temporal dynamics.
   - **Year**: 2020

6. **Title**: Cerebellar Manifold Contractions (Zhu et al., 2025)
   - **Authors**: Zhu et al.
   - **Summary**: Shows dynamic manifold geometry during motor learning, linking manifold contractions to network integration during reinforcement learning. Demonstrates temporal evolution of geometric structure in biological systems.
   - **Year**: 2025

7. **Title**: Hippocampal Hyperbolic Geometry (Zhang et al., 2022)
   - **Authors**: Zhang et al.
   - **Summary**: Reveals that CA1 neurons use hyperbolic geometry that expands over time with experience, providing evidence for temporal evolution of non-Euclidean geometric structure in biological representations.
   - **Year**: 2022

**Key Challenges**

1. **Static Equivariance Limitation**: Current geometric deep learning focuses on static equivariance without modeling temporal dynamics. E(n)-EGNN and similar architectures treat each molecular configuration independently, failing to exploit temporal autocorrelation in sequential data.

2. **Lack of Temporal Integration in Equivariant Architectures**: No prior work combines E(n)-equivariant graph operations with continuous-time temporal dynamics (neural ODEs). The theoretical framework for equivariant neural networks explicitly omits temporal/dynamical aspects.

3. **Symmetry Preservation During Temporal Evolution**: Maintaining geometric symmetries (E(n)-equivariance) during continuous-time ODE integration is challenging due to numerical error accumulation. Existing geometric integration methods focus on analytical systems rather than learned equivariant manifolds.

4. **Sample Efficiency in Sequential Molecular Dynamics**: Static models require large training datasets because they don't leverage temporal structure. Temporal smoothness constraints could reduce hypothesis space and improve sample efficiency, but this has not been validated for equivariant architectures.

5. **Bio-Inspired Transfer to Artificial Systems**: Biological neural systems (grid cells, motor cortex) demonstrate continuous temporal integration with symmetry preservation, but transferring these substrate-agnostic principles to artificial molecular dynamics prediction remains unexplored.

6. **Smooth vs. Non-Smooth Trajectory Modeling**: Molecular force fields can produce both smooth potential energy surfaces and stiff dynamics with rapid oscillations. Whether neural ODE smoothness bias helps or hinders molecular dynamics prediction requires empirical validation.

7. **Missing Benchmark Dataset Citations**: Critical dataset sources (MD17, ISO17) and graph neural ODE literature need proper attribution for reproducibility and positioning within the broader research landscape.

8. **Alternative Temporal Mechanisms**: Distinguishing whether sample efficiency gains come from continuous-time smoothness constraints versus other factors (parameter efficiency, implicit regularization, temporal context windows) requires careful ablation studies.
