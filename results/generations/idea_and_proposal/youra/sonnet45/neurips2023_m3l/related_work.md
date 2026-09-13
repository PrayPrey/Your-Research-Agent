## Related Work

**Related Papers**
1. **Title**: Adaptive Gradient Methods at the Edge of Stability (arXiv:2207.14484)
   - **Authors**: Cohen, J., Kaur, S., Li, Y., Kolter, J. Z., & Talwalkar, A.
   - **Summary**: Empirical study documenting Edge of Stability phenomenon where adaptive gradient methods (Adam, AdaGrad) operate near instability boundary with learning rate η ≈ 2/λ_max. Key observations include training entering regime with loss oscillations but overall descent, and sharpness self-stabilization near 2/η boundary.
   - **Year**: 2022

2. **Title**: Implicit Bias of Gradient Descent for Wide Two-layer Neural Networks
   - **Authors**: Chizat, L., & Bach, F.
   - **Summary**: Rigorous theoretical analysis of gradient descent convergence and implicit bias for two-layer neural networks in the infinite-width limit using mean-field approximation. Demonstrates that gradient flow converges to global minimum under suitable initialization and provides mathematically rigorous analysis via optimal transport theory.
   - **Year**: 2020

3. **Title**: Scaling Laws for Linear Complexity Language Models (arXiv:2406.16690)
   - **Authors**: Shen, Y., Song, Z., Mei, S., & Santurkar, S.
   - **Summary**: Empirical study of scaling laws for linear-complexity language model architectures (Mamba, RWKV). Key findings include that power-law relationships L ~ N^{-α} persist for linear-complexity architectures, with scaling exponents α differing across architectures (α_Mamba ≈ 0.21, α_RWKV ≈ 0.24).
   - **Year**: 2024

4. **Title**: Scaling Laws for Neural Language Models (arXiv:2001.08361)
   - **Authors**: Kaplan, J., McCandlish, S., Henighan, T., Brown, T. B., et al.
   - **Summary**: Foundational empirical work establishing power-law scaling relationships for Transformer language models with respect to parameter count N, dataset size D, and compute C. Key relationships include L ~ N^{-0.076}, L ~ D^{-0.095}, L ~ C^{-0.050}, with performance predictable over 7+ orders of magnitude.
   - **Year**: 2020

5. **Title**: Deep networks on toroids: Removing symmetries reveals the structure of flat regions in the landscape of neural networks
   - **Authors**: Pittorino, F., Ferraro, A., & Seoane, L. F.
   - **Summary**: Demonstrates that discrete architectural symmetries (weight permutations, sign flips) create flat regions in loss landscape via toroidal quotient space analysis. Shows that removing symmetries (factoring by symmetry group G) reveals intrinsic landscape with unique minima replacing degenerate flat manifolds.
   - **Year**: 2022

6. **Title**: Visualizing the Loss Landscape of Neural Nets
   - **Authors**: Goldstein, T., et al.
   - **Summary**: Practical implementation for loss landscape visualization using low-dimensional projections. Techniques include random directions, PCA on parameters, and filter-normalized directions to enable 1D/2D landscape plots revealing basin structure, sharpness, and convergence path geometry.
   - **Year**: Not specified

7. **Title**: Generalization bounds for deep learning (arXiv:2012.04115)
   - **Authors**: Valle Pérez, G., & Louis, A. A.
   - **Summary**: PAC-Bayesian generalization bounds for deep networks incorporating sharpness and flatness measures. Shows that flatter minima (measured by Hessian spectrum) correlate with better generalization, with sharpness-aware bounds tighter than naive parameter counting.
   - **Year**: 2020

8. **Title**: Renormalization group and critical phenomena
   - **Authors**: Wilson, K. G.
   - **Summary**: Foundational work establishing Renormalization Group (RG) theory for understanding phase transitions and critical phenomena in statistical physics. Key ideas include systems exhibiting qualitatively different behavior at different scales, RG flow toward fixed points describing scale-invariant critical behavior, and critical exponents deriving from symmetry groups and fixed point analysis.
   - **Year**: 1971

9. **Title**: Neural Tangent Kernel (mentioned in context)
   - **Authors**: Jacot et al.
   - **Summary**: Framework that assumes linearization regime with small learning rates and infinite width for analyzing neural network training dynamics.
   - **Year**: 2018

**Key Challenges**
1. **Lack of Theoretical Understanding for Empirical Phenomena**: Edge of Stability has been empirically observed but lacks theoretical explanation for why stability regime transitions occur at learning rate threshold η ≈ 2/λ_max.

2. **No Mechanistic Explanation for Scaling Laws**: Empirically fitted power-laws L ~ N^{-α} exist without mechanistic explanation for where exponents originate or why they differ across architectures. Scaling exponents α are treated as free empirical parameters.

3. **Disconnection Between Static Geometry and Training Dynamics**: While symmetry-landscape connection has been demonstrated statically, there is no established connection to training dynamics, convergence behavior, or scaling laws.

4. **Computational Intractability for Billion-Scale Networks**: Theoretical analysis of billion-parameter networks faces prohibitive computational barriers including O(N²) memory for Hessian computation, O(NT) storage for full trajectory analysis, and potentially exponential complexity for symmetry enumeration.

5. **Expensive Empirical Validation of New Architectures**: Current practice requires training at multiple scales (e.g., 10M, 100M, 1B, 10B parameters) to fit scaling laws empirically, costing $50K-$100K per architecture for 5-10 full training runs.

6. **Scale Limitations of Rigorous Theory**: Mean-field theory and other rigorous approaches are limited to small networks (two-layer, infinite-width limits) and don't explain phenomena like Edge of Stability that are not present in infinite-width limits.

7. **No Predictive Framework for Architecture Design**: Cannot predict scaling behavior α for new architectures without expensive multi-scale training trials, providing no actionable insights for architecture design decisions.

8. **Transformer Symmetry Complexity**: Attention mechanisms create complex non-local symmetries with all-to-all interactions, making symmetry orbit enumeration potentially exponentially hard or requiring approximations that lose theoretical elegance.

9. **Theory-Practice Gap**: Small-network rigorous theory doesn't apply to practical billion-scale training, while large-scale empirical observations lack theoretical foundation, leaving a gap between mathematically rigorous analysis and practical applicability.

10. **No Connection Between Architecture Properties and Training Outcomes**: Existing work doesn't explain which architectural choices lead to flat vs. sharp minima, or how architectural properties affect convergence rates and scaling behavior.
