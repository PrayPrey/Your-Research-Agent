## Related Work

**Related Papers**
1. **Title**: Deep Equilibrium Models (Bai et al., NeurIPS 2019)
   - **Authors**: Bai et al.
   - **Summary**: Introduced DEQs - infinite-depth networks via fixed-point solving with constant memory. Foundational architecture for implicit models.
   - **Year**: 2019

2. **Title**: Reversible Deep Equilibrium Models (McCallum et al.)
   - **Authors**: McCallum et al.
   - **Summary**: Exact gradients without implicit function theorem, fewer evaluations. Improves gradient computation efficiency for DEQs.
   - **Year**: 2025

3. **Title**: Lyapunov-Stable Deep Equilibrium Models (Chu et al.)
   - **Authors**: Chu et al.
   - **Summary**: Provable stability via Lyapunov theory with adversarial robustness guarantees for DEQs under perturbations.
   - **Year**: 2023

4. **Title**: SpiNNaker2: A Large-Scale Neuromorphic System (Gonzalez et al.)
   - **Authors**: Gonzalez et al.
   - **Summary**: Scalable digital neuromorphic platform with event-driven ML support for spiking neural networks.
   - **Year**: 2024

5. **Title**: Energy-Efficient Deployment of ML on Neuromorphic Hardware (Chandarana et al.)
   - **Authors**: Chandarana et al.
   - **Summary**: DNN-to-SNN conversion for Intel Loihi demonstrating 27× power reduction and 5× energy reduction for image classification.
   - **Year**: 2022

6. **Title**: BitsAndBytes: 8-bit Optimizers & Quantization (Dettmers et al.)
   - **Authors**: Dettmers et al.
   - **Summary**: 4-bit/8-bit quantization with minimal accuracy loss using NormalFloat (NF4) data type for efficient model compression.
   - **Year**: Not specified

7. **Title**: Surrogate Gradient Learning in Spiking Neural Networks (Neftci et al.)
   - **Authors**: Neftci et al.
   - **Summary**: Smooth approximations to spike discontinuities enable gradient-based SNN training through backpropagation.
   - **Year**: 2019

8. **Title**: TransPIM: Memory-based Acceleration via SW-HW Co-Design (Zhou et al.)
   - **Authors**: Zhou et al.
   - **Summary**: Co-optimized dataflow and hardware for Transformers achieving 22× speedup compared to GPUs through processing-in-memory.
   - **Year**: 2022

9. **Title**: Self-Supervised DEQ for MRI Reconstruction (Gan et al.)
   - **Authors**: Gan et al.
   - **Summary**: DEQ for MRI reconstruction without ground truth achieving state-of-the-art results on medical imaging benchmarks.
   - **Year**: 2023

10. **Title**: Dynamic Precision Analog Computing for Neural Networks (Garg et al.)
    - **Authors**: Garg et al.
    - **Summary**: 89% energy reduction via dynamic precision in analog processors with less than 2% accuracy degradation.
    - **Year**: 2021

11. **Title**: Pruning and Model Compression (Han et al.)
    - **Authors**: Han et al.
    - **Summary**: Model compression techniques for reducing network size and computational requirements for edge deployment.
    - **Year**: 2015

12. **Title**: Distillation (Hinton et al.)
    - **Authors**: Hinton et al.
    - **Summary**: Knowledge distillation methods for transferring knowledge from large models to smaller, more efficient models.
    - **Year**: 2015

13. **Title**: Photonic Bayesian Neural Networks (Zhuge et al.)
    - **Authors**: Zhuge et al.
    - **Summary**: Photonic implementation of Bayesian neural networks achieving 98% accuracy matching full-precision models.
    - **Year**: 2025

14. **Title**: Energy efficiency measurements for analog VLSI SNNs (Moriya et al.)
    - **Authors**: Moriya et al.
    - **Summary**: Reports 14.4 fJ/SOP efficiency for analog VLSI spiking neural networks demonstrating neuromorphic energy advantages.
    - **Year**: 2025

**Key Challenges**
1. **Hardware Deployment Gap**: No prior work exists on deploying implicit models (DEQs, Neural ODEs) on neuromorphic hardware - all existing DEQ research assumes GPU/TPU execution with full-precision arithmetic.

2. **Quantization for Implicit Differentiation**: Quantization-aware training and surrogate gradients have not been applied to implicit differentiation - QAT literature covers only explicit networks, and surrogate gradients are limited to explicit backpropagation through time.

3. **Edge Deployment Power Constraints**: No ultra-low-power (sub-10mW) edge deployment solution exists for iterative implicit models - current MRI reconstruction and mobile vision systems rely on high-power GPUs or explicit networks.

4. **Neuromorphic Noise Impact**: Spike noise in neuromorphic hardware may increase iteration counts in fixed-point solving, potentially negating energy efficiency gains from sparse computation.

5. **Convergence Tolerance Trade-offs**: Relaxing DEQ convergence criteria for neuromorphic compatibility (ε=1e-2 vs 1e-3) requires validation that accuracy degradation remains under 2% for practical applications.

6. **Training-Deployment Gap**: Hybrid-precision training requires GPU/TPU infrastructure while deployment targets neuromorphic edge devices, creating toolchain complexity.

7. **Limited Hardware Support**: Neuromorphic platforms have capacity constraints (e.g., Loihi 2: ~131k neurons) that may limit deployment of large-scale DEQ models without model partitioning.

8. **Lack of Standardized Tooling**: No plug-and-play DEQ-to-SNN compiler exists, requiring custom engineering for neuromorphic deployment unlike mature frameworks for conventional hardware.
