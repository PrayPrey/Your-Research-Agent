## Related Work

**Related Papers**
1. **Title**: Architecture-independent generalization bounds (Chen et al., 2025)
   - **Authors**: Chen et al.
   - **Summary**: Proves that architectural differences manifest as differences in metric geometry of learned representations, with bounds depending on regularity properties of activation and operator norms of weights.
   - **Year**: 2025

2. **Title**: Gradient flow with architectural constraints (Min et al., 2021)
   - **Authors**: Min et al.
   - **Summary**: Shows that gradient flow dx/dt = -∇L(x) evolves on manifold M_A determined by architecture, with initialization constraining dynamics to invariant sets leading to min-norm solution in architecture-specific norm.
   - **Year**: 2021

3. **Title**: Edge of Stability (Arora et al., 2022)
   - **Authors**: Arora et al.
   - **Summary**: Demonstrates that sharpness stabilizes at 2/LR early in training (typically <10% of total steps), indicating implicit bias manifests quickly during optimization.
   - **Year**: 2022

4. **Title**: Encoder-only vs decoder-only Transformers scaling (Yao et al., 2024)
   - **Authors**: Yao et al.
   - **Summary**: Shows that encoder-only Transformers exhibit different scaling behavior than decoder-only architectures for time series tasks, suggesting architecture families have distinct scaling profiles.
   - **Year**: 2024

5. **Title**: Renormalization group analysis of neural training (Roberts et al., 2022)
   - **Authors**: Roberts et al.
   - **Summary**: Successfully applied renormalization group analysis to neural network training, showing different architectures correspond to different RG fixed points leading to different universality classes.
   - **Year**: 2022

6. **Title**: Power-law emergence thresholds in GNNs (Zhu et al., 2024)
   - **Authors**: Zhu et al.
   - **Summary**: Empirically validated power-law T = T₀ · system_size^α for predicting GNN emergence thresholds in power systems (10K-19K bus systems), demonstrating predictive power-law approach.
   - **Year**: 2024

7. **Title**: Scaling Laws for Neural Language Models (Kaplan et al., 2020)
   - **Authors**: Kaplan et al.
   - **Summary**: Demonstrates power-law scaling Loss L(N) ~ N^(-α) in neural networks, establishing foundation for understanding how performance scales with model size, though architecture-agnostic in original formulation.
   - **Year**: 2020

8. **Title**: Statistical Physics Universality Theory (Wilson, Fisher)
   - **Authors**: Wilson, Fisher
   - **Summary**: Foundation of universality class theory showing systems with same symmetries and dimensionality belong to same universality class, exhibiting identical critical exponents despite microscopic differences (e.g., Ising model universality class).
   - **Year**: Not specified

9. **Title**: Neural Tangent Kernel Theory
   - **Authors**: Not specified
   - **Summary**: Shows that at initialization, architecture defines kernel structure K(x,x') which determines function space (RKHS), with different architectures producing different kernels and therefore different function spaces.
   - **Year**: Not specified

10. **Title**: Johnson-Lindenstrauss Lemma
    - **Authors**: Not specified
    - **Summary**: Proves that random projection from D dimensions to O(log n) dimensions preserves pairwise distances with high probability, enabling tractable metric geometry analysis with reduced computational complexity.
    - **Year**: Not specified

11. **Title**: Lottery Ticket Hypothesis
    - **Authors**: Not specified
    - **Summary**: Shows that winning tickets are identifiable at initialization, suggesting early network structure matters and influences final training outcomes.
    - **Year**: Not specified

12. **Title**: Implicit bias literature (min-norm solutions)
    - **Authors**: Not specified
    - **Summary**: Demonstrates that implicit bias emerges from initialization and persists throughout training, with gradient descent finding minimum-norm solutions in architecture-specific function spaces.
    - **Year**: Not specified

13. **Title**: Feature Learning Literature
    - **Authors**: Not specified
    - **Summary**: Shows that different architectural primitives learn fundamentally different functional forms: attention mechanisms learn token interaction functions, convolutions learn local pattern detectors, recurrence learns sequential state updates.
    - **Year**: Not specified

**Key Challenges**
1. **Theory-Practice Gap**: Existing scaling laws (Kaplan et al., 2020) are architecture-agnostic and cannot predict emergence thresholds for specific architectures before training, requiring expensive trial-and-error approaches.

2. **Measurability of Inductive Bias**: Inductive biases are typically characterized qualitatively (e.g., "attention mechanisms have global receptive field"), lacking tractable quantitative measures that can be computed before or early in training.

3. **Architecture Heterogeneity**: Modern neural architectures span diverse families (Transformers, CNNs, GNNs, SSMs, hybrids) with fundamentally different primitives, making it unclear if unified scaling principles exist across architecture types.

4. **Emergence Unpredictability**: Emergent capabilities (in-context learning, reasoning) appear suddenly at certain scales with no reliable a priori prediction method, leading to 10× or greater compute waste when selecting suboptimal architectures.

5. **Universality Class Identification**: While statistical physics universality theory provides conceptual framework, neural architectures have discrete structural differences rather than continuous symmetries, making direct application of phase transition theory unclear.

6. **Temporal Stability of Bias**: Unclear whether inductive biases measured at initialization or early training remain stable and predictive throughout training, or if architectures undergo qualitative phase transitions (e.g., feature learning → memorization).

7. **Discrete vs Continuous Architecture Space**: Tension between treating architectures as discrete classes (Transformers, CNNs) versus continuous spectrum (hybrid architectures with varying % attention vs convolution), affecting how universality classes should be defined.

8. **Scalability of Analysis**: High computational cost of characterizing implicit bias traditionally requires full training runs, limiting ability to explore large architecture spaces efficiently.

9. **Cross-Domain Generalization**: Unclear whether scaling principles derived from language modeling extend to other domains (vision, graph learning, reinforcement learning, scientific computing).

10. **Saturation Regimes**: Power-law scaling may break down at very large scales due to diminishing returns, but existing work lacks framework for predicting when saturation occurs or how it varies by architecture.
