## Related Work

**Related Papers**
1. **Title**: Derivative-Informed Fourier Neural Operator (arXiv:2512.14086)
   - **Authors**: Yao, Luo, Cao, Kovachki, O'Leary-Roseberry, Ghattas
   - **Summary**: Establishes universal approximation of Fourier Neural Operators and their Fréchet derivatives, demonstrating superior sample complexity for PDE-constrained inverse problems.
   - **Year**: 2025

2. **Title**: Convex Physics Informed Neural Networks for the Monge-Ampère Optimal Transport Problem (arXiv:2501.10162)
   - **Authors**: Caboussat, Peruso
   - **Summary**: Introduces convex neural networks that enforce convexity constraints for Monge-Ampère optimal transport, incorporating transport boundary conditions directly in the loss function.
   - **Year**: 2025

3. **Title**: Neural Estimation of Entropic Optimal Transport (arXiv:2405.06734)
   - **Authors**: Wang, Goldfeld
   - **Summary**: Achieves minimax-optimal parametric rates for entropic optimal transport using a semi-dual neural representation with non-asymptotic bounds.
   - **Year**: 2024

4. **Title**: Principled Weight Initialisation for Input-Convex Neural Networks
   - **Authors**: Hoedt, Klambauer
   - **Summary**: Develops principled initialization schemes that enable effective ICNN training without requiring skip-connections.
   - **Year**: 2023

5. **Title**: The Monge Gap: A Regularizer to Learn All Transport Maps
   - **Authors**: Uscidda, Cuturi
   - **Summary**: Proposes a regularization approach that removes the ICNN requirement for learning transport maps, though without finite-sample theory or PDE enforcement.
   - **Year**: 2023

6. **Title**: Do Neural Optimal Transport Solvers Work? A Continuous Wasserstein-2 Benchmark
   - **Authors**: Korotin et al.
   - **Summary**: Demonstrates that many neural OT solvers fail to recover true transport maps despite achieving good downstream performance, and introduces ICNN-based benchmarks for ground-truth evaluation.
   - **Year**: 2021

**Key Challenges**
1. **Lack of Finite-Sample Theory**: Existing methods like the Monge Gap approach drop convexity requirements but do not provide finite-sample theoretical guarantees for transport map estimation.
2. **Missing PDE Enforcement**: Current neural OT approaches do not explicitly enforce Monge-Ampère PDE constraints during training, limiting their theoretical grounding.
3. **Convexity-Theory Trade-off**: Standard ICNN-based OT methods guarantee convexity but lack derivative-informed training procedures and finite-sample bounds.
4. **Transport Map Recovery Failure**: Many neural OT solvers fail to accurately recover true transport maps even when achieving satisfactory performance on downstream tasks.
5. **No Unified Framework**: No existing work successfully combines finite-sample theory, Monge-Ampère constraint enforcement, and convexity guarantees in a single approach.
