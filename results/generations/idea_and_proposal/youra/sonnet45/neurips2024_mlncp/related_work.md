## Related Work

**Related Papers**
1. **Title**: A Unified Model for Large-Scale Inexact Fixed-Point Iteration: A Stochastic Optimization Perspective (2025)
   - **Authors**: Abolfazl Hashemi
   - **Summary**: Proves convergence of inexact fixed-point iteration under stochastic perturbations when noise variance is below a specific threshold (δ² where δ = σ_min(J)/√n). Theorem 3.1 provides theoretical foundation that analog noise is tolerable in iterative algorithms.
   - **Year**: 2025
   - **DOI**: 10.1109/TAC.2024.3486655

2. **Title**: Deep Unfolding Approach for Signal Processing Algorithms: Convergence Acceleration and Its Theoretical Interpretation (2020)
   - **Authors**: Tadashi Wadayama, Satoshi Takabe
   - **Summary**: Demonstrates that spectral radius control via Chebyshev step enables learnable momentum parameters to accelerate convergence by 5-15×. Provides algorithmic optimization strategy for adaptive momentum mechanisms.
   - **Year**: 2020
   - **DOI**: 10.1587/essfr.14.1_60

3. **Title**: Hybrid Digital/Analog Memristor-based Computing Architecture (2024)
   - **Authors**: Zheng et al.
   - **Summary**: Achieved 8.32× speedup for sparse neural networks using hybrid digital-analog approach. Validates feasibility of hybrid architecture pattern combining digital control with analog acceleration.
   - **Year**: 2024
   - **Identifier**: Semantic Scholar ID: eaca4af080951226275b...

4. **Title**: torchdeq framework - Digital DEQ with Anderson Acceleration
   - **Authors**: Not specified
   - **Summary**: Current state-of-the-art framework for DEQ training efficiency in digital hardware. Serves as baseline for energy and convergence speed comparison.
   - **Year**: Not specified

5. **Title**: Purely Analog Inference Systems (Photonic NNs, FeFET-only)
   - **Authors**: Not specified
   - **Summary**: Alternative approach using full analog computation versus hybrid approaches. Represents comparison point for flexibility trade-offs, as hybrid maintains programmability.
   - **Year**: Not specified

6. **Title**: Apple Neural Engine Case Study
   - **Authors**: Not specified
   - **Summary**: Pattern of custom hardware for iterative transformer computation using digital control with specialized accelerator. Referenced from Archon KB knowledge base.
   - **Year**: Not specified

7. **Title**: NVIDIA cuBLAS Reproducibility Documentation
   - **Authors**: Not specified
   - **Summary**: Documents challenges with numerical precision in iterative algorithms on digital hardware. Referenced from Archon KB knowledge base.
   - **Year**: Not specified

8. **Title**: AnalogAI Framework
   - **Authors**: Not specified
   - **Summary**: Simulation platform for analog computation with noise modeling. Available on GitHub (PJLAB-CHIP/AnalogAI). Currently lacks DEQ-specific integration or convergence analysis.
   - **Year**: Not specified

9. **Title**: cross-sim simulator
   - **Authors**: Not specified
   - **Summary**: Demonstrates 100× energy efficiency for matrix operations in analog in-memory computing hardware.
   - **Year**: Not specified

10. **Title**: FeFET Device Characterization Studies
   - **Authors**: Pereira-Rial et al.
   - **Summary**: Demonstrates 5-bit precision with feedback compensation in FeFET analog devices. Reports mismatch σ ~ 0.05-0.1 for analog IMC device characteristics.
   - **Year**: 2025

11. **Title**: DEQ Theory Literature (Lin et al.)
   - **Authors**: Lin et al.
   - **Summary**: Shows contractive mappings (eigenvalues < 1) are robust to small perturbations. Demonstrates DEQ's tolerance for approximate solutions with 5% accuracy degradation acceptable.
   - **Year**: 2025

**Key Challenges**
1. **Noise Management in Analog Hardware**: Analog device mismatch (FeFET variability) introduces stochastic noise to fixed-point iteration. Challenge is ensuring noise remains bounded by theoretical thresholds (Var(noise) < δ² where δ = σ_min(J)/√n) to maintain convergence guarantees.

2. **I.I.D. Noise Assumption vs Spatial Correlation**: Hashemi's convergence theory assumes independent and identically distributed (i.i.d.) noise, but FeFET device mismatch exhibits spatial correlation within crossbars (~0.6 correlation). Strategic device placement and crossbar tiling needed to decorrelate noise sources to acceptable levels (< 0.3).

3. **Communication Overhead**: On-chip analog IMC required for full speedup gains. Off-chip implementations suffer from PCIe latency (50-100ms per iteration), which negates analog efficiency advantages. Challenge is ensuring hybrid communication latency remains below critical thresholds (< 1ns/element on-chip).

4. **Scalability and Tiling Overhead**: Tiling overhead grows quadratically with layer size (5% for 256×256, 15% for 512×512, 25% for 1024×1024). Very large DEQ layers (> 1024×1024) face overhead exceeding 20%, negating efficiency gains.

5. **Gap in DEQ-Analog Integration**: No prior work applies stochastic fixed-point iteration theory to analog neural network hardware. Existing analog NN research treats noise as error to minimize, rather than formalizing it as convergence-accelerating stochastic perturbation.

6. **Device Precision Requirements**: Extremely low-bit analog hardware (< 3-bit) insufficient for DEQ convergence precision requirements. Challenge is balancing energy efficiency with adequate numerical precision (5-bit target, potentially 8-bit for ill-conditioned models).

7. **Calibration Complexity**: Calibration complexity increases with crossbar count, requiring per-device feedback compensation. Challenge scales with hardware deployment size.

8. **Jacobian Stability Under Perturbation**: DEQ Jacobian eigenvalues must remain stable under analog perturbations (Lipschitz constant preserved below noise threshold). If eigenvalues destabilize, convergence guarantees break down.
