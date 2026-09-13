## Related Work

**Related Papers**
1. **Title**: Hardware-aware training for large-scale and diverse DL inference using IMC accelerators
   - **Authors**: Rasch et al.
   - **Summary**: Demonstrates that CNNs, RNNs, and Transformers can achieve iso-accuracy on analog hardware through systematic retraining approaches, establishing methodological foundations for hardware-aware neural network training.
   - **Year**: 2023

2. **Title**: Towards Chip-in-the-loop SNN Training via Metropolis-Hastings Sampling (arXiv:2402.06284)
   - **Authors**: Safa et al.
   - **Summary**: Shows that hardware noise can enable MCMC sampling, achieving 27% accuracy improvement over backpropagation, validating the concept of treating noise as a computational resource.
   - **Year**: 2024

3. **Title**: Variance-Aware Noisy Training (arXiv:2503.16183)
   - **Authors**: Wang et al.
   - **Summary**: Proposes dynamic noise handling techniques that improve robustness from 79.3% to 97.6%, addressing temporal stability assumptions in noisy hardware training.
   - **Year**: 2025

4. **Title**: Photonic probabilistic machine learning using quantum vacuum noise
   - **Authors**: Choi et al.
   - **Summary**: Demonstrates that quantum vacuum noise can enable probabilistic photonic computing, validating the optical paradigm for noise-based computation.
   - **Year**: 2024

5. **Title**: Photonic Bayesian Neural Networks
   - **Authors**: Zhuge et al.
   - **Summary**: Achieves 98% accuracy on photonic Bayesian neural networks through paradigm-specific optimization approaches.
   - **Year**: 2025

6. **Title**: MemTorch Framework
   - **Authors**: Not specified
   - **Summary**: Provides a mature simulation framework for memristive deep learning with comprehensive noise models for analog hardware validation.
   - **Year**: Not specified

7. **Title**: Random noise promotes slow heterogeneous synaptic dynamics
   - **Authors**: Rungratsameetaweemana et al.
   - **Summary**: Demonstrates that biological neural networks utilize synaptic noise as a computational resource, providing cross-domain biological precedent for noise exploitation.
   - **Year**: 2025

8. **Title**: Thermodynamic computing via autonomous quantum thermal machines
   - **Authors**: Lipka-Bartosik et al.
   - **Summary**: Shows that thermal fluctuations can implement neural network computations, establishing physics-based precedent for thermal noise as a computational primitive.
   - **Year**: 2023

**Key Challenges**
1. **Cross-paradigm generalization**: Existing hardware-aware training methods are typically designed for specific hardware paradigms (analog, photonic, etc.) rather than providing unified approaches that work across diverse neuromorphic computing platforms.

2. **Noise treatment as obstacle vs. resource**: Traditional approaches treat hardware noise as a problem to be mitigated rather than exploited, missing opportunities to leverage noise as a computational resource.

3. **Temporal noise stability**: Current methods often assume static noise characteristics, failing to address the dynamic and time-varying nature of hardware noise in real neuromorphic systems.

4. **Paradigm-specific optimization trade-offs**: Existing solutions achieve high accuracy through paradigm-specific optimizations, sacrificing flexibility and portability across different hardware implementations.
