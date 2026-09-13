## Related Work

**Related Papers**
1. **Title**: LeanDojo: Theorem Proving with Retrieval-Augmented Language Models (arXiv:2306.15626)
   - **Authors**: Yang, Swope, Gu, Chalamala, Song, Yu, Godil, Prenger, Anandkumar
   - **Summary**: Provides open-source Lean playground with programmatic proof state access; ReProver achieves 51.2% on MiniF2F with retrieval-augmented premise selection, serving as infrastructure foundation for theorem proving systems.
   - **Year**: 2023

2. **Title**: DeepSeek-Prover-V2: Advancing Formal Mathematical Reasoning (arXiv:2504.21801)
   - **Authors**: Ren, Shao, et al.
   - **Summary**: Demonstrates that subgoal decomposition via reinforcement learning achieves 88.9% on MiniF2F-test, establishing the value of proof decomposition strategies for formal theorem proving.
   - **Year**: 2025

3. **Title**: Goedel-Prover-V2: Scaling Formal Theorem Proving with Scaffolded Self-Correction (arXiv:2508.03613)
   - **Authors**: Goedel-LM
   - **Summary**: Shows that self-correction improves pass rate from 88.1% to 90.4% on MiniF2F, demonstrating the effectiveness of post-hoc correction approaches in theorem proving.
   - **Year**: 2025

4. **Title**: Fault self-healing: A biological immune heuristic reinforcement learning method
   - **Authors**: Tian, Yin, Jiang
   - **Summary**: Proposes TCN-VAE combined with effector T-cell immune-inspired reinforcement learning, achieving 95%+ fault self-healing rates, providing cross-domain inspiration for failure-aware architectures.
   - **Year**: 2024

5. **Title**: ReProver (LeanDojo baseline)
   - **Authors**: Not specified
   - **Summary**: Achieves 51.2% on MiniF2F benchmark, serving as a direct comparison target for theorem proving systems.
   - **Year**: Not specified

6. **Title**: A Survey on Deep Learning for Theorem Proving
   - **Authors**: Li et al.
   - **Summary**: Comprehensive survey confirming that no existing work uses explicit failure classification for recovery and identifying intermediate step errors as a key challenge in theorem proving.
   - **Year**: 2024

**Key Challenges**
1. **Lack of Explicit Failure Classification**: No existing work uses explicit failure classification mechanisms for recovery in theorem proving systems, leaving a gap in proactive error handling approaches.
2. **Intermediate Step Errors**: Errors occurring at intermediate steps during proof construction represent a key challenge that current systems struggle to address effectively.
3. **Reactive vs. Proactive Recovery**: Current approaches like self-correction operate post-hoc rather than proactively classifying and addressing failures during the proving process.
