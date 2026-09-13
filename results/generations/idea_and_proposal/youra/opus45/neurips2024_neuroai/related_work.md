## Related Work

**Related Papers**
1. **Title**: Uncertainty-modulated prediction errors in cortical microcircuits (2024)
   - **Authors**: Wilmes, Petrovici, Sachidhanandam, Senn
   - **Summary**: Demonstrates that Layer 2/3 neurons compute uncertainty-weighted prediction errors (UPE) via subtractive and divisive inhibition by different inhibitory cell types, providing the core biological mechanism for uncertainty-modulated predictive coding.
   - **Year**: 2024

2. **Title**: Hebbian Learning based Orthogonal Projection for Continual Learning of SNNs (2024)
   - **Authors**: Xiao, Meng, Zhang, He, Lin
   - **Summary**: Shows that Hebbian/anti-Hebbian learning on lateral connections enables near-zero catastrophic forgetting, demonstrating compatibility between Hebbian plasticity and SNN continual learning.
   - **Year**: 2024

3. **Title**: Synchrony-Gated Plasticity with Dopamine Modulation for SNNs (2025)
   - **Authors**: Tian, Tensingh, Eshraghian, Truong, Kavehei
   - **Summary**: Introduces loss-sensitive gating that adjusts local update magnitude, demonstrating that neuromodulator broadcast mechanisms are feasible for SNN training.
   - **Year**: 2025

4. **Title**: Advancing Neuromorphic Computing With Loihi: A Survey (2021)
   - **Authors**: Davies et al.
   - **Summary**: Documents orders-of-magnitude efficiency gains for SNNs on neuromorphic hardware, establishing efficiency baselines and deployment targets for neuromorphic systems.
   - **Year**: 2021

5. **Title**: Surrogate Gradient SNN Training
   - **Authors**: Neftci et al.
   - **Summary**: Provides foundational methods for training SNNs using surrogate gradients, serving as a primary comparison baseline for accuracy, compute operations, and training stability.
   - **Year**: 2019

6. **Title**: STEP Benchmark Platform (2025)
   - **Authors**: Not specified
   - **Summary**: A NeurIPS 2025 accepted unified evaluation platform for Spiking Transformers, providing standardized comparison methodology for SNN research.
   - **Year**: 2025

7. **Title**: Brain and Cognitive Science Inspired Deep Learning: A Comprehensive Survey (2025)
   - **Authors**: Zhang, Ding, Liang, Zhou, Qin, Liu
   - **Summary**: Reviews over 300 papers on brain-inspired deep learning approaches but identifies the absence of unified integration frameworks combining SNNs, predictive coding, and Hebbian plasticity.
   - **Year**: 2025

**Key Challenges**
1. **Lack of Unified Integration Frameworks**: Despite extensive research (300+ papers reviewed), there remains no unified framework that successfully integrates SNNs, predictive coding, and Hebbian plasticity into a cohesive learning system.

2. **Biological Plausibility vs. Performance Trade-off**: Existing SNN training methods like surrogate gradients achieve good accuracy but lack biological plausibility, while biologically-inspired approaches struggle to match performance benchmarks.

3. **Scalable Neuromodulation for Learning**: Implementing effective neuromodulator broadcast mechanisms that can scale to complex SNN architectures while maintaining local learning rules remains an open challenge.

4. **Continual Learning in SNNs**: Preventing catastrophic forgetting while enabling continuous adaptation in spiking neural networks requires novel plasticity mechanisms that preserve previously learned representations.
