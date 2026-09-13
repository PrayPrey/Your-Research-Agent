## Related Work

**Related Papers**
1. **Title**: Human-like systematic generalization through a meta-learning neural network (DOI: 10.1038/s41586-023-06668-3)
   - **Authors**: Lake & Baroni
   - **Summary**: Demonstrates that meta-learning enables compositional generalization, providing foundational theory for compositional approaches in learning systems.
   - **Year**: 2023

2. **Title**: In-context Reinforcement Learning with Algorithm Distillation (arXiv:2210.14215)
   - **Authors**: Laskin et al.
   - **Summary**: Shows that Transformers can learn RL algorithms in-context, establishing the in-context reinforcement learning (ICRL) paradigm.
   - **Year**: 2022

3. **Title**: Supervised Pretraining Can Learn In-Context RL (arXiv:2306.14892)
   - **Authors**: Lee et al.
   - **Summary**: Introduces DPT, demonstrating that supervised pretraining enables in-context RL with exploration capabilities.
   - **Year**: 2023

4. **Title**: Meta-World: A Benchmark for Multi-Task and Meta RL (arXiv:1910.10897)
   - **Authors**: Yu et al.
   - **Summary**: Establishes a standard benchmark for multi-task and meta-RL evaluation, revealing that meta-RL approaches struggle to scale beyond 10 tasks.
   - **Year**: 2019

5. **Title**: Mixture-of-Experts Meets In-Context Reinforcement Learning (T2MIR) (arXiv:2506.05426)
   - **Authors**: Wu et al.
   - **Summary**: Proposes an end-to-end Mixture-of-Experts approach for ICRL, serving as a direct competitor in the compositional ICRL space.
   - **Year**: 2025

6. **Title**: PEARL: Efficient Off-Policy Meta-RL
   - **Authors**: Rakelly et al.
   - **Summary**: Introduces a context-based meta-RL method that achieves 20-100x greater sample efficiency compared to prior approaches.
   - **Year**: 2019

7. **Title**: Motion Learning via Motor Primitives and Modulation
   - **Authors**: Wang et al.
   - **Summary**: Provides biological evidence supporting modular primitive and composition architectures for motion learning.
   - **Year**: 2024

8. **Title**: Mastering Massive Multi-Task RL via MoE Decision Transformer (M3DT) (arXiv:2505.24378)
   - **Authors**: Kong et al.
   - **Summary**: Demonstrates that MoE Decision Transformers can scale to 160 tasks, providing support for compositional approaches in multi-task RL.
   - **Year**: 2025

**Key Challenges**
1. **Limited Task Scalability in Meta-RL**: Current meta-RL methods struggle to generalize effectively beyond approximately 10 tasks, as evidenced by Meta-World benchmark evaluations.
2. **Compositional Generalization**: Achieving human-like systematic generalization through compositional learning remains a fundamental challenge that meta-learning approaches aim to address.
3. **Differentiation from End-to-End Approaches**: Distinguishing compositional methods from end-to-end MoE approaches for ICRL requires demonstrating clear architectural and performance advantages.
4. **Sample Efficiency**: Balancing sample efficiency with scalability remains challenging, with context-based methods like PEARL achieving efficiency gains but potentially at the cost of task diversity.
