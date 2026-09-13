## Related Work

**Related Papers**
1. **Title**: Regret Bounds for Adaptive Nonlinear Control (arXiv:2011.13101)
   - **Authors**: Boffi, Tu, Slotine
   - **Summary**: Establishes the first √T regret bounds for nonlinear control with matched uncertainty using contraction theory, providing theoretical foundations for adaptive control in nonlinear settings.
   - **Year**: 2020

2. **Title**: On the Sample Complexity of the Linear Quadratic Regulator (arXiv:1710.01688)
   - **Authors**: Dean, Mania, Matni, Recht, Tu
   - **Summary**: Derives sample complexity and regret bounds for LQR with unknown dynamics, establishing fundamental results for learning-based linear control.
   - **Year**: 2017

3. **Title**: Neural Contraction Metrics with Formal Guarantees
   - **Authors**: Li, Zhong, Hu, Zhang
   - **Summary**: Develops α,β-CROWN verification methods for neural contraction metrics in discrete-time systems, enabling rigorous certification of learned metrics.
   - **Year**: 2025

4. **Title**: Learning-based Adaptive Control via Contraction Theory
   - **Authors**: Tsukamoto, Chung, Slotine
   - **Summary**: Proposes contraction-based adaptive control methods that achieve asymptotic stability guarantees for learning-based control systems.
   - **Year**: 2021

5. **Title**: Lyapunov-stable Neural-network Control
   - **Authors**: Dai et al.
   - **Summary**: Presents joint synthesis of neural network controllers and Lyapunov functions via mixed-integer programming for stability-certified control.
   - **Year**: 2021

6. **Title**: Naive Exploration is Optimal for Online LQR
   - **Authors**: Simchowitz, Foster
   - **Summary**: Proves that √T regret is optimal for LQR through lower bound analysis, demonstrating that poly(log T) regret is not achievable.
   - **Year**: 2020

7. **Title**: Learning Without Mixing
   - **Authors**: Simchowitz, Mania, Tu, Jordan, Recht
   - **Summary**: Demonstrates that ordinary least squares achieves minimax optimal identification for linear systems, establishing foundational regret analysis techniques.
   - **Year**: 2018

**Key Challenges**
1. **Extension to Unknown Dynamics**: Existing contraction-based regret bounds assume matched uncertainty; extending these approaches to fully unknown dynamics remains an open problem.
2. **Regret Bounds for Contraction-Based Adaptive Control**: Current contraction-based adaptive control methods provide asymptotic stability guarantees but lack finite-time regret bounds.
3. **Verification of Learned Metrics**: Ensuring formal guarantees for neural network-based contraction metrics requires rigorous certification methods that can scale to practical systems.
4. **Fundamental Regret Limitations**: Lower bounds prove that √T regret is optimal for linear systems, constraining achievable performance improvements in the nonlinear setting.
5. **Lyapunov vs. Contraction Approaches**: Alternative stability certification methods (Lyapunov-based) exist but may offer different trade-offs compared to contraction-based frameworks for learning-based control.
