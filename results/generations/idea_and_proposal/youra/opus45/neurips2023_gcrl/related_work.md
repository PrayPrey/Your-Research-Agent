## Related Work

**Related Papers**
1. **Title**: Contrastive Learning as Goal-Conditioned Reinforcement Learning (arXiv:2206.07568)
   - **Authors**: Eysenbach, Zhang, Salakhutdinov, Levine
   - **Summary**: Proves the equivalence φ(s)ᵀψ(g) = V(s,g), demonstrating that contrastive representations encode goal-conditioned value functions.
   - **Year**: 2022

2. **Title**: Hindsight Experience Replay (arXiv:1707.01495)
   - **Authors**: Andrychowicz et al. (OpenAI)
   - **Summary**: Introduces a method for sample-efficient learning from sparse binary rewards through goal relabeling, enabling agents to learn from failed trajectories.
   - **Year**: 2017

3. **Title**: UniCorn: A Unified Contrastive Learning Approach for Multi-view Molecular Representation Learning (arXiv:2405.10343)
   - **Authors**: Feng et al.
   - **Summary**: Proposes a multi-view contrastive learning framework that achieves state-of-the-art performance on molecular property prediction tasks.
   - **Year**: 2024

4. **Title**: Goal-Conditioned Reinforcement Learning: Problems and Solutions
   - **Authors**: Liu, Zhu, Zhang
   - **Summary**: Provides a comprehensive survey of GCRL methods and confirms that molecular design remains an unexplored application domain for goal-conditioned approaches.
   - **Year**: 2022

5. **Title**: Mol-AIR: Molecular Reinforcement Learning with Adaptive Intrinsic Rewards
   - **Authors**: Park, Ahn, Choi, Kim
   - **Summary**: Presents a goal-directed molecular generation approach using adaptive intrinsic rewards to guide exploration in chemical space.
   - **Year**: 2024

6. **Title**: Goal-conditioned GFlowNets for Controllable Multi-Objective Molecular Design
   - **Authors**: Roy, Bacon, Pal, Bengio
   - **Summary**: Introduces a multi-objective molecular design framework using GFlowNets with Pareto exploration for controllable generation.
   - **Year**: 2023

7. **Title**: OGBench: Benchmarking Offline Goal-Conditioned RL
   - **Authors**: Park, Frans, Eysenbach, Levine
   - **Summary**: Establishes a comprehensive benchmark with 85 datasets across 8 environments, all focused on robotics domains, highlighting the absence of molecular benchmarks.
   - **Year**: 2024

8. **Title**: Sample Efficiency Matters: A Benchmark for Practical Molecular Optimization
   - **Authors**: Gao, Fu, Sun, Coley
   - **Summary**: Introduces the PMO benchmark with a 10K query budget constraint, establishing the importance of sample efficiency in practical molecular optimization.
   - **Year**: 2022

9. **Title**: Metric Residual Networks for Sample Efficient Goal-Conditioned RL
   - **Authors**: Liu, Feng, Liu, Stone
   - **Summary**: Proposes neural architecture designs that improve sample efficiency in goal-conditioned reinforcement learning through metric residual networks.
   - **Year**: 2022

**Key Challenges**
1. **Molecular Domain Gap in GCRL**: Existing GCRL benchmarks and methods focus exclusively on robotics domains, with molecular design remaining unexplored despite being a natural fit for goal-conditioned formulations.
2. **Sample Efficiency in Molecular Optimization**: Practical molecular optimization requires methods that can achieve strong performance within limited query budgets (e.g., 10K evaluations), making sample efficiency a critical concern.
3. **Sparse Reward Learning**: Learning from sparse binary rewards in goal-conditioned settings remains challenging, requiring techniques like hindsight relabeling to extract learning signal from unsuccessful trajectories.
4. **Multi-Objective Molecular Design**: Molecular design often involves optimizing multiple competing objectives simultaneously, requiring methods capable of Pareto exploration and controllable generation.
5. **Representation Learning for Goal-Conditioned Value Functions**: Effectively encoding goal-conditioned value functions through learned representations remains an open challenge, with contrastive methods showing promise but requiring adaptation to molecular domains.
