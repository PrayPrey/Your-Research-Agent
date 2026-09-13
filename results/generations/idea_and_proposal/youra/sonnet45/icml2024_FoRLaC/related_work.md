## Related Work

**Related Papers**
1. **Title**: Lyapunov-stable neural-network control (2021)
   - **Authors**: Hongkai Dai, Benoit Landry, Lujie Yang, M. Pavone, Russ Tedrake
   - **Summary**: Introduces MIP-based verification approach that synthesizes provably stable neural controllers for low-dimensional systems (inverted pendulum, quadrotor); establishes baseline that is extended to high dimensions through hierarchical decomposition.
   - **Year**: 2021

2. **Title**: Stochastic Policy Gradient Methods: Improved Sample Complexity for Fisher-non-degenerate Policies (2023)
   - **Authors**: Ilyas Fatkhullin, Anas Barakat, Anastasia Kireeva, Niao He
   - **Summary**: Demonstrates improved sample complexity O(ε^-2) for continuous state-action reinforcement learning; shows theoretical progress in scalability but lacks stability guarantees.
   - **Year**: 2023

3. **Title**: Data-Driven Control of Markov Jump Systems: Sample Complexity and Regret Bounds (2022)
   - **Authors**: Zhe Du, Yahya Sattar, Davoud Ataee Tarzanagh, Laura Balzano, Necmiye Ozay, Samet Oymak
   - **Summary**: Achieves O(√T) regret bounds for Markov jump linear systems; presents learning-theoretic approach to control but linear dynamics assumption limits extension to nonlinear high-dimensional systems.
   - **Year**: 2022

4. **Title**: A Fast and High Quality Multilevel Scheme for Partitioning Irregular Graphs (METIS Graph Partitioning) (1998)
   - **Authors**: Karypis & Kumar
   - **Summary**: Demonstrates efficient balanced graph partitioning with minimized edge cuts for sparse graphs; provides algorithmic foundation for subsystem decomposition.
   - **Year**: 1998

5. **Title**: Input-to-state stability for discrete-time nonlinear systems (Small-Gain Theorem) (2001)
   - **Authors**: Jiang & Wang
   - **Summary**: Establishes compositional stability from local certificates under coupling conditions; provides theoretical foundation for global certificate from subsystem Lyapunov functions.
   - **Year**: 2001

6. **Title**: Diffuser (2022)
   - **Authors**: Not specified
   - **Summary**: Diffusion-based planning with hierarchical structure for reinforcement learning; empirically effective but lacks formal stability certificates or provable guarantees.
   - **Year**: 2022

**Key Challenges**
1. **Computational Intractability of Monolithic Verification**: MIP-based Lyapunov verification approaches (Dai et al. 2021) fail beyond 10-15 state dimensions due to exponential complexity O(n^k), making verification intractable for industrial-scale systems (100+ states).

2. **Scalability-Guarantee Tradeoff**: Existing approaches either achieve scalability without formal guarantees (hierarchical RL methods like Diffuser) or provide provable stability for only low-dimensional systems (MIP verification), but not both simultaneously.

3. **Extension from Linear to Nonlinear High-Dimensional Systems**: Learning-theoretic control methods (Du et al. 2022) demonstrate regret bounds for Markov jump systems but assume linear dynamics, limiting applicability to nonlinear high-dimensional control problems.

4. **Lack of Systematic Decomposition Methods**: No existing framework automatically decomposes high-dimensional neural control systems to exploit structural sparsity for tractable verification while maintaining global stability guarantees.

5. **Compositional Verification Conservatism**: Small-gain theorem provides sufficient but not necessary conditions for global stability; may reject stable systems with moderate coupling strength, limiting applicability.

6. **Subsystem Coupling Characterization**: Unclear how to systematically identify weakly-coupled subsystem structures in realistic high-dimensional systems (power grids, traffic networks) to enable compositional verification approaches.
