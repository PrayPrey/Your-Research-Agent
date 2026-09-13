## Related Work

**Related Papers**
1. **Title**: Seed-Prover: Deep and Broad Reasoning for Automated Theorem Proving (arXiv:2507.23726)
   - **Authors**: Chen et al.
   - **Summary**: Demonstrates that iterative refinement with Lean feedback achieves 78.1% on IMO benchmarks, showing that LLMs can effectively learn from formal feedback mechanisms.
   - **Year**: 2025

2. **Title**: CRANE: Reasoning with Constrained LLM Generation (Semantic Scholar ID: 26356aff11581eba9f1eb9443c8519f9991c7269)
   - **Authors**: Banerjee et al.
   - **Summary**: Investigates how grammar constraints can negatively impact reasoning performance and proposes a reasoning-augmented approach that achieves 10% improvement.
   - **Year**: 2025

3. **Title**: Flexible and Efficient Grammar-Constrained Decoding (Semantic Scholar ID: 56781bbbdd457e7666fc4b3e7cf7c7583fa6ee6e)
   - **Authors**: Park et al.
   - **Summary**: Demonstrates efficient real-time verification feasibility with approximately 50μs per token mask computation for grammar-constrained decoding.
   - **Year**: 2025

4. **Title**: HyperTree Proof Search for Neural Theorem Proving (Semantic Scholar ID: 65b4b25272c50dc376f5c018338931bfd349e532)
   - **Authors**: Lample et al.
   - **Summary**: Establishes foundational neural proof guidance methodology, achieving 82.6% accuracy on Metamath benchmark.
   - **Year**: 2022

5. **Title**: VERGE: Formal Refinement and Guidance Engine (arXiv:2601.20055v1)
   - **Authors**: Not specified
   - **Summary**: Introduces claim-level neurosymbolic refinement achieving +18.7% improvement, serving as a baseline for granularity comparison in verification approaches.
   - **Year**: 2026

6. **Title**: Logically Constrained Decoding (Semantic Scholar ID: afcac8c7a800b3a74c9c98ad790370ecbf3fdddf)
   - **Authors**: Ma et al.
   - **Summary**: Extends constrained decoding techniques beyond grammar constraints to incorporate logical constraints during generation.
   - **Year**: 2025

7. **Title**: CLEVER: A Curated Benchmark for Formally Verified Code Generation (arXiv:2505.13938)
   - **Authors**: Not specified
   - **Summary**: Presents a 161-problem benchmark demonstrating that current LLMs struggle with full verification tasks, validating the existing gap in formally verified code generation.
   - **Year**: 2025

8. **Title**: Dual Process Theory in LLM Reasoning
   - **Authors**: Not specified
   - **Summary**: Cross-domain work on System 1/System 2 cognitive mapping to neural-symbolic integration, providing theoretical validation for bidirectional feedback architecture design.
   - **Year**: 2022, 2024

**Key Challenges**
1. **Grammar Constraints Degrading Reasoning**: Imposing grammar constraints during generation can negatively impact the reasoning capabilities of LLMs, requiring careful balance between structural validity and reasoning quality.

2. **Full Verification Difficulty**: Current LLMs struggle significantly with complete formal verification tasks, as evidenced by benchmark evaluations showing substantial gaps in verified code generation capabilities.

3. **Granularity of Feedback Integration**: Existing approaches vary in the level at which formal feedback is integrated (e.g., claim-level vs. token-level), with implications for both effectiveness and computational efficiency.

4. **Real-time Verification Overhead**: Achieving efficient real-time verification during generation requires careful optimization, with computational costs per token being a critical consideration for practical deployment.

5. **Neural-Symbolic Integration**: Effectively combining neural generation with symbolic verification systems remains challenging, requiring principled approaches to bidirectional feedback between the two paradigms.
