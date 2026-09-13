## Related Work

**Related Papers**

1. **Title**: A comprehensive review of advances in physics-informed neural networks and their applications in complex fluid dynamics (DOI: 10.1063/5.0226562)
   - **Authors**: Chi Zhao, Feifei Zhang, Wenqiang Lou, Xi Wang, Jianyong Yang
   - **Summary**: Reviews PINN advances and identifies manual specification of physics constraints as a key limitation. Demonstrates that incorporating conservation laws improves physics fidelity but requires domain expertise, motivating the need for automatic discovery methods.
   - **Year**: 2024

2. **Title**: Gauge equivariant neural networks for quantum lattice gauge theories (DOI: 10.1103/PhysRevLett.127.276402)
   - **Authors**: Di Luo, Giuseppe Carleo, B. Clark, J. Stokes
   - **Summary**: Demonstrates that gauge-equivariant architectures achieve exact symmetry preservation when symmetries are known, validating the structural enforcement mechanism for neural networks.
   - **Year**: 2020

3. **Title**: Enhancing lattice kinetic schemes for fluid dynamics with Lattice-Equivariant Neural Networks (arXiv:2405.13850)
   - **Authors**: Giulio Ortali, Alessandro Gabbana, Imre Atmodimedjo, Alessandro Corbetta
   - **Summary**: Shows that equivariant architectures respecting predefined lattice symmetries improve accuracy and stability in fluid dynamics, providing domain-specific validation of symmetry enforcement.
   - **Year**: 2024

4. **Title**: Discrete Mechanics and Variational Integrators
   - **Authors**: Jerrold E. Marsden, Matthew West
   - **Summary**: Establishes discrete variational mechanics framework with discrete Noether's theorem and error bounds (ΔC = O(Δt²)), providing theoretical foundation for discrete conservation laws in computational systems.
   - **Year**: 2001

5. **Title**: Applications of Lie Groups to Differential Equations
   - **Authors**: Peter J. Olver
   - **Summary**: Comprehensive treatment of infinitesimal generator recovery via perturbation analysis, providing theoretical foundation for symmetry discovery in dynamical systems.
   - **Year**: 1986

6. **Title**: Group Equivariant Convolutional Networks (Cohen & Welling reference)
   - **Authors**: Cohen & Welling
   - **Summary**: Literature on equivariant networks demonstrates 10-40% out-of-distribution improvement when symmetries are known, establishing performance benchmarks for symmetry-aware architectures.
   - **Year**: 2016

7. **Title**: Geometric Deep Learning (Bronstein et al. reference)
   - **Authors**: Bronstein et al.
   - **Summary**: Establishes that symmetries provide inductive biases for generalization in deep learning, supporting the theoretical foundation that respecting symmetries improves model performance.
   - **Year**: Not specified

**Key Frameworks and Methods**

8. **Title**: e2cnn - E(2)-Equivariant CNNs
   - **Authors**: QUVA-Lab
   - **Summary**: Framework for E(2)-equivariant convolutional neural networks requiring manual specification of symmetries for 2D problems. Used as baseline for comparison (669 GitHub stars).
   - **Year**: Not specified

9. **Title**: egnn-pytorch - E(n)-Equivariant Graph Neural Networks
   - **Authors**: lucidrains
   - **Summary**: Implementation of E(n)-equivariant graph neural networks requiring manual specification of symmetries for 3D problems. Used as baseline for comparison (519 GitHub stars).
   - **Year**: Not specified

10. **Title**: Physics-Informed Neural Networks (PINNs)
   - **Authors**: Not specified
   - **Summary**: Standard approach using conservation laws as soft constraint loss terms without structural enforcement, achieving conservation violations around 10⁻³. Used as primary baseline for comparison.
   - **Year**: Not specified

**Key Challenges**

1. **Manual Symmetry Specification**: Existing equivariant networks (e2cnn, egnn-pytorch) require known symmetries as input and cannot discover them automatically, limiting applicability to problems where symmetries are not known a priori.

2. **Conservation Law Violation in PINNs**: Standard physics-informed neural networks use soft constraints that achieve conservation violations around 10⁻³, far from the machine precision (~10⁻⁵ to 10⁻⁶) that structural enforcement could achieve.

3. **Manual Conservation Law Encoding**: PINNs require manual specification of conservation laws and physics constraints, requiring domain expertise and limiting automation potential.

4. **Gap Between Discovery and Enforcement**: Zhao et al. (2024) identifies manual specification as limiting, while Luo et al. (2020) and Ortali et al. (2024) demonstrate equivariant networks require known symmetries, creating a contradiction between the need for automatic discovery and existing enforcement mechanisms.

5. **Discrete Formulation Approximations**: Discrete Noether's theorem introduces approximation errors (ΔC = O(Δt²)), requiring careful formulation to ensure conservation holds with bounded error in practice.

6. **Spurious Symmetry Detection**: Risk of false positives in automatic symmetry discovery from finite operator samples, requiring validation protocols with ground truth on synthetic benchmarks.

7. **Global Symmetry Assumptions**: Standard equivariant architectures assume global symmetries, but many multi-scale physics problems require scale-dependent or local symmetries, necessitating hierarchical extensions.

8. **Computational Overhead**: Perturbation analysis requires O(kN) forward passes (k generators, N samples) and equivariant training has 1.2-1.5× overhead compared to standard architectures.
