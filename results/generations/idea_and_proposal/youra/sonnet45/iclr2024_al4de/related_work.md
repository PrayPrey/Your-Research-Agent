## Related Work

**Related Papers**

1. **Title**: TT-decomposition (SIAM J. Sci. Comput. 33(5), 2295-2317)
   - **Authors**: I.V. Oseledets
   - **Summary**: Mathematical foundation for Tensor-Train decomposition showing parameter reduction from O(n^D) to O(D·r²·n) with bounded approximation error. Provides rigorous mathematical proof for TT-factorization parameter reduction.
   - **Year**: 2011

2. **Title**: Tensorizing Neural Networks
   - **Authors**: A. Novikov, D. Podoprikhin, A. Osokin, D. Vetrov
   - **Summary**: Demonstrated 100,000x compression on fully-connected layers using TT-format while preserving accuracy; validated stable gradient flow through TT-cores with standard backpropagation.
   - **Year**: 2015

3. **Title**: Fourier Neural Operator for Parametric Partial Differential Equations
   - **Authors**: Z. Li, N. Kovachki, K. Azizzadenesheli, B. Liu, K. Bhattacharya, A. Stuart, A. Anandkumar
   - **Summary**: FNO architecture with spectral convolutions achieves resolution-invariant operator learning; memory bottleneck is spectral kernel storage (modes³×channels²). Establishes baseline FNO architecture.
   - **Year**: 2021

4. **Title**: Factorized Fourier Neural Operators
   - **Authors**: A. Tran, A. Mathews, L. Xie, C.S. Ong
   - **Summary**: Tucker/CP decomposition on FNO spectral kernels achieves 10-100x parameter reduction with <5% accuracy degradation; identifies R³ core tensor as bottleneck for Tucker decomposition.
   - **Year**: 2023

5. **Title**: Neural Operator: Learning Maps Between Function Spaces
   - **Authors**: N. Kovachki, Z. Li, B. Liu, K. Azizzadenesheli, K. Bhattacharya, A. Stuart, A. Anandkumar
   - **Summary**: Theoretical framework proving universal approximation properties of neural operators with convergence rates. Ensures TT-decomposition preserves operator approximation properties.
   - **Year**: 2023

6. **Title**: U-FNO: Enhanced Fourier neural operator for multiphase flow
   - **Authors**: S.M. Rahman et al.
   - **Summary**: Multi-scale architecture helps but still capped at 128³ resolution due to memory constraints. Demonstrates that architectural solutions don't address fundamental parameter scaling issue without compression.
   - **Year**: 2023

7. **Title**: Spectral Methods Theory
   - **Authors**: Boyd
   - **Summary**: PDE solutions have exponential decay in high-frequency Fourier modes, providing theoretical foundation for low-rank structure assumption in spectral domain.
   - **Year**: 1999

8. **Title**: Quantum Tensor Network Methods (Tensor Train Decomposition for Quantum Systems)
   - **Authors**: Schollwöck
   - **Summary**: Routinely use TT-rank ~50 for million-dimensional quantum systems with negligible error. Demonstrates that quantum wavefunctions with similar smoothness properties have low TT-rank.
   - **Year**: 2011

9. **Title**: Attention Is All You Need (Transformer Training with Gradient Clipping)
   - **Authors**: Vaswani et al.
   - **Summary**: Proved effectiveness of gradient clipping for stabilizing training in Transformer models, providing precedent for training stability mechanisms.
   - **Year**: 2017

10. **Title**: neuraloperator/neuraloperator library (Official FNO Implementation)
    - **Authors**: Not specified
    - **Summary**: Production-ready FNO implementation with Tucker FNO (TFNO) containing documented memory limits (~256³ max on 16GB GPU). Serves as comparison baseline and implementation reference.
    - **Year**: Not specified

**Key Challenges**

1. **Memory Bottleneck in High-Resolution 3D PDEs**: Current FNO implementations are limited to ~256³ resolution on 16GB GPUs due to O(modes³×channels²) spectral kernel memory requirements (~32GB projected for 512³), making large-scale neural PDE solving inaccessible without multi-GPU clusters.

2. **Tucker/CP Decomposition Core Tensor Bottleneck**: Existing compression methods (Tucker, CP) suffer from O(R³) core tensor bottleneck that limits compression ratios and makes them less effective for high-dimensional 3D problems compared to theoretical potential.

3. **Resolution Invariance Under Compression**: Architectural modifications for memory reduction (U-Net hierarchies) fail to preserve FNO's key property of resolution-invariant operator learning, requiring separate models for different resolutions.

4. **Low-Rank Structure Validation**: Uncertainty about whether FNO spectral convolution kernels possess exploitable low-rank structure similar to quantum wavefunctions, as prior work on tensor decomposition (Novikov 2015) focused on fully-connected layers rather than spectral operators.

5. **Gradient Flow in Factorized Spectral Convolutions**: Unknown whether TT-format interacts favorably with FFT operations in spectral convolutions or if frequency-domain processing breaks the gradient flow assumptions validated for simpler linear transformations.

6. **Cross-Domain Transfer Gap**: Memory optimization research focuses primarily on CNNs/Transformers for standard ML tasks, with TT-decomposition under-explored for scientific computing applications that have unique requirements (resolution invariance, spectral parameterization).

7. **Training Stability with Compressed Operators**: Risk of gradient vanishing/explosion through long TT-core chains requiring specialized initialization or training procedures, contradicting the desired "drop-in replacement" simplicity.

8. **Data Availability for 3D High-Resolution**: PDEBench provides extensive 2D datasets, but high-quality 3D datasets (512³ ground truth) may not be available for all target PDE types, requiring synthetic data generation via traditional solvers.
