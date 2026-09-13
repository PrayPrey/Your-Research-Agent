## Related Work

**Related Papers**
1. **Title**: Self-Consistency Improves Chain of Thought Reasoning in Language Models (arXiv/Semantic Scholar)
   - **Authors**: Xuezhi Wang, Jason Wei, Dale Schuurmans, et al.
   - **Summary**: Demonstrates that self-consistency through sampling diverse reasoning paths improves accuracy, achieving +17.9% improvement on GSM8K benchmark.
   - **Year**: 2022

2. **Title**: Towards Reasoning Era: A Survey of Long Chain-of-Thought for Reasoning LLMs (arXiv/Semantic Scholar)
   - **Authors**: Qiguang Chen, Libo Qin, et al.
   - **Summary**: Surveys inference-time scaling approaches and identifies "overthinking" as a key challenge in Long Chain-of-Thought reasoning, providing a taxonomy of reasoning paradigms.
   - **Year**: 2025

3. **Title**: DiffAdapt: Difficulty-Adaptive Reasoning for Token-Efficient LLM Inference (arXiv:2510.19669)
   - **Authors**: Xiang Liu, Xuming Hu, et al.
   - **Summary**: Identifies U-shaped entropy patterns across difficulty levels and achieves 22.4% token reduction through difficulty classification approaches.
   - **Year**: 2025

4. **Title**: Think Just Enough: Sequence-Level Entropy as a Confidence Signal for LLM Reasoning (arXiv:2510.08146)
   - **Authors**: Sharma & Chopra
   - **Summary**: Demonstrates 25-50% compute savings using Shannon entropy for early stopping, identifying this as an emergent property in reasoning models.
   - **Year**: 2025

5. **Title**: Chain-of-Thought Prompting Elicits Reasoning in Large Language Models
   - **Authors**: Jason Wei, et al.
   - **Summary**: Establishes the foundational Chain-of-Thought approach which serves as a baseline with no early stopping, representing the upper bound on accuracy and lower bound on efficiency.
   - **Year**: 2022

6. **Title**: Token-Budget-Aware LLM Reasoning (TALE) (ACL 2025)
   - **Authors**: Not specified
   - **Summary**: Achieves 67% token reduction via budget prompting with less than 3% accuracy decrease, representing an alternative approach using explicit budget constraints.
   - **Year**: 2025

7. **Title**: Optimal Stopping Theory (Foundational - Information Theory)
   - **Authors**: Not specified
   - **Summary**: Provides theoretical foundation for determining when to stop a sequential decision process to maximize expected utility, applicable to entropy stabilization as an optimal stopping criterion.
   - **Year**: Not specified

**Key Challenges**
1. **Overthinking in Long Chain-of-Thought**: Extended reasoning chains lead to unnecessary computation where models continue reasoning beyond the point of useful contribution, wasting computational resources.

2. **Difficulty-Adaptive Token Efficiency**: Existing approaches rely on difficulty classification to reduce tokens, but this requires explicit categorization rather than dynamic adaptation during inference.

3. **Absolute vs. Rate-Based Entropy Signals**: Prior work uses absolute Shannon entropy values for early stopping decisions, which may not capture the stabilization dynamics as effectively as rate-of-change (delta-entropy) approaches.

4. **Balancing Accuracy and Efficiency**: Achieving significant token reduction while maintaining accuracy remains challenging, with existing methods showing trade-offs between computational savings and performance degradation.

5. **Verification Mechanisms for Early Stopping**: Determining when reasoning has reached sufficient quality requires robust verification approaches to ensure premature termination does not compromise answer correctness.
