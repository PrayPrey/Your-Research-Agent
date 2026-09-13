## Related Work

**Related Papers**
1. **Title**: Fourier Neural Operator for Parametric PDEs (arXiv:2010.08895)
   - **Authors**: Li, Kovachki, Azizzadenesheli, Liu, Bhattacharya, Stuart, Anandkumar
   - **Summary**: FNO parameterizes the integral kernel in Fourier space, achieving 1000x speedup over traditional methods with a fixed 12-mode truncation approach.
   - **Year**: 2020

2. **Title**: Fourier Neural Operator with Learned Deformations for PDEs on General Geometries (arXiv:2207.05209)
   - **Authors**: Li, Huang, Liu, Anandkumar
   - **Summary**: Geo-FNO extends FNO to general geometries through learned deformations, achieving 10⁵x speedup over numerical solvers and 2x improved accuracy compared to standard FNO.
   - **Year**: 2022

3. **Title**: Categorical Reparameterization with Gumbel-Softmax (arXiv:1611.01144)
   - **Authors**: Jang, Gu, Poole
   - **Summary**: Introduces Gumbel-softmax technique enabling differentiable sampling from categorical distributions, which serves as a core technique for soft mode allocation in neural architectures.
   - **Year**: 2017

4. **Title**: U-FNO for Multiphase Flow
   - **Authors**: Wen, Li, Azizzadenesheli, Anandkumar, Benson
   - **Summary**: Proposes a U-Net and FNO hybrid architecture designed to capture multi-scale features for multiphase flow problems.
   - **Year**: 2021

5. **Title**: Domain Agnostic Fourier Neural Operators
   - **Authors**: Liu, Jafarzadeh, Yu
   - **Summary**: DAFNO handles irregular geometries through a smoothed characteristic function approach, improving generalization across different domain shapes.
   - **Year**: 2023

6. **Title**: Benchmarking Long Roll-outs of Auto-regressive Neural Operators
   - **Authors**: Current, Kumar, Gaitonde, Parthasarathy
   - **Summary**: Identifies significant limitations of present neural operator architectures for capturing high-frequency components in turbulent flows during long temporal roll-outs.
   - **Year**: 2026

7. **Title**: M2NO: Multiwavelet-based Multigrid Neural Operator
   - **Authors**: Li, Lai, Zhang, Wang
   - **Summary**: Introduces a multigrid structure using multiwavelets that enhances both accuracy and computational efficiency for neural operators.
   - **Year**: 2024

**Key Challenges**
1. **Fixed Mode Truncation**: Standard FNO uses a fixed 12-mode truncation in Fourier space, which may not optimally allocate spectral resources across different frequency components or varying solution complexities.

2. **High-Frequency Component Capture**: Present neural operator architectures exhibit significant limitations in capturing high-frequency components, particularly in turbulent flow simulations during long temporal roll-outs.

3. **Multi-Scale Feature Representation**: Effectively capturing features across multiple spatial scales remains challenging, requiring hybrid architectures or specialized multi-resolution approaches.

4. **Geometry Generalization**: Standard FNO struggles with irregular and general geometries, necessitating extensions like learned deformations or domain-agnostic formulations.
