## Related Work

**Related Papers**
1. **Title**: Cognitive Load-Aware Inference (CLAI) (DOI: 10.48550/arXiv.2025.CLAI)
   - **Authors**: Zhang
   - **Summary**: Demonstrates that cognitive load theory applies to LLM token efficiency, achieving 45% reduction through hidden state analysis.
   - **Year**: 2025

2. **Title**: e3: Learning to Explore Enables Extrapolation of TTC (Semantic Scholar ID: ff76e9e076f4)
   - **Authors**: Setlur et al.
   - **Summary**: Shows that in-context exploration enables limited test-time compute extrapolation.
   - **Year**: 2025

3. **Title**: A Survey of Test-Time Compute (Semantic Scholar ID: 1fd282ff3a03)
   - **Authors**: Ji et al.
   - **Summary**: Provides a System-1 to System-2 transition framework for understanding test-time compute methods.
   - **Year**: 2025

4. **Title**: Reasoning on a Budget: A Survey of Adaptive TTC (arXiv:2507.02076)
   - **Authors**: Alomrani et al.
   - **Summary**: Presents a comprehensive taxonomy of test-time compute methods, categorizing them into L1 (controllability) and L2 (adaptiveness) approaches.
   - **Year**: 2025

5. **Title**: HALT-CoT: Model-Agnostic Early Stopping (OpenReview: CX5c7C1CZa)
   - **Authors**: Laaouach
   - **Summary**: Proposes entropy-based stopping mechanisms that achieve 15-30% token reduction in chain-of-thought reasoning.
   - **Year**: 2025

6. **Title**: REFRAIN: Reflective-Redundancy for Adaptive Inference (arXiv:2510.10103)
   - **Authors**: Sun et al.
   - **Summary**: Introduces a training-free UCB bandit approach that achieves 20-55% token reduction for adaptive inference stopping.
   - **Year**: 2025

7. **Title**: EAGER: Entropy-Guided Adaptive Resource Allocation
   - **Authors**: Scalena et al.
   - **Summary**: Demonstrates that entropy-based branching improves efficiency but does not enable extrapolation capabilities.
   - **Year**: 2025

8. **Title**: Thinking Longer, Not Larger (Semantic Scholar ID: 7d03e6e12c24)
   - **Authors**: Ma et al.
   - **Summary**: Shows that a 32B parameter model can surpass a 671B model through effective test-time compute utilization, validating the value of improved TTC methods.
   - **Year**: 2025

**Key Challenges**
1. **Efficiency-Extrapolation Gap**: Current entropy-based methods achieve computational efficiency but fail to enable extrapolation beyond training distributions, as demonstrated by EAGER's limitations.
2. **Limited Extrapolation Capabilities**: Existing approaches like e3 only enable limited test-time compute extrapolation through in-context exploration, suggesting room for improvement in extrapolation mechanisms.
3. **Adaptive Stopping Trade-offs**: While methods like HALT-CoT and REFRAIN achieve significant token reductions (15-55%), they primarily focus on efficiency rather than enhancing reasoning capabilities or enabling generalization.
4. **Metacognitive Control**: The transition from System-1 to System-2 reasoning requires sophisticated metacognitive control mechanisms that current methods do not fully address.
