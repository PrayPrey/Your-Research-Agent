## Related Work

**Related Papers**
1. **Title**: Scaling Test-Time Compute Optimally can be More Effective than Scaling Model Parameters (Snell et al. 2024)
   - **Authors**: Snell, C., Lee, J., Xu, K., & Kumar, A.
   - **Summary**: Demonstrated that process verifiers combined with test-time scaling can outperform pre-training scale, achieving 15% absolute accuracy improvement on MATH (40%→55%) and GSM8K (70%→85%) datasets using separate process verifier training with beam search at test-time.
   - **Year**: 2024

2. **Title**: AReaL - Lightning-Fast RL for LLM Reasoning
   - **Authors**: inclusionAI
   - **Summary**: Efficient PPO implementation for reasoning tasks with outcome rewards, achieving ~35%→48% accuracy improvement (+13% absolute) on mathematical reasoning tasks through RL training with outcome rewards on solution correctness.
   - **Year**: Not specified

3. **Title**: Can 1B Surpass 405B (Liu et al. 2025)
   - **Authors**: Liu et al.
   - **Summary**: Demonstrated that a 1B model with compute-optimal test-time scaling can achieve 72% accuracy matching a 405B model at 68% through dynamic test-time scaling with fixed compute budget, showing unified optimization enables efficiency.
   - **Year**: 2025

4. **Title**: Unveiling Causal Reasoning in LLMs (G²-Reasoner 2025)
   - **Authors**: Various
   - **Summary**: Introduced counterfactual generation methodology for Level-1 vs Level-2 causal reasoning tasks in LLMs, demonstrating the effectiveness of counterfactual reasoning for causal discovery in language models.
   - **Year**: 2025

5. **Title**: Self-rewarding Reasoning LLM
   - **Authors**: RLHFlow
   - **Summary**: Developed a method where policy generates own rewards through self-evaluation using outcome-level rewards only, without step-by-step supervision.
   - **Year**: Not specified

6. **Title**: Thinking-Optimal Scaling
   - **Authors**: Not specified
   - **Summary**: Optimized Chain-of-Thought length per domain through domain-level optimization, not per-instance adaptation.
   - **Year**: Not specified

7. **Title**: Thought Anchors
   - **Authors**: Not specified
   - **Summary**: Demonstrated critical sentence identification in reasoning tasks using attention mechanisms and sentence importance scoring.
   - **Year**: Not specified

8. **Title**: PlanBench
   - **Authors**: Not specified
   - **Summary**: Benchmark for logical planning tasks used for evaluating cross-domain transfer of reasoning systems.
   - **Year**: Not specified

9. **Title**: Interplay Study (Training Stages)
   - **Authors**: Not specified
   - **Summary**: Showed that training stages have causal contributions in LLM development, demonstrating that different training phases contribute causally to model capabilities.
   - **Year**: Not specified

10. **Title**: Thinking, Fast and Slow (Dual-Process Theory)
    - **Authors**: Kahneman, D.
    - **Summary**: Cognitive psychology framework proposing human reasoning combines fast intuitive judgments (System 1) with slow deliberate verification (System 2), inspiring computational dual-process models.
    - **Year**: 2011

**Key Challenges**
1. **Systematic Integration Gap**: Prior work optimizes RL training OR test-time scaling separately without a unified framework that integrates both components systematically.

2. **Training-Testing Consistency**: Process verifiers trained on different data than policy (e.g., Snell's approach) create distribution mismatch between training and test-time evaluation criteria.

3. **Efficiency-Accuracy Trade-off**: Exhaustive verification approaches (like Snell's beam search) are computationally expensive (1.5-2.0x overhead), while greedy decoding misses errors - need for selective verification approach.

4. **Joint Optimization Challenge**: Separate training of policy and process rewards loses potential synergy from feedback loops between the two components.

5. **Domain Transfer Limitations**: Process reward models may not transfer zero-shot across qualitatively different domains (mathematical reasoning to social reasoning, creative tasks).

6. **Step-Level Supervision Requirements**: Most datasets lack intermediate step annotations, constraining domain applicability to math/logic domains with available supervision.

7. **Real-Time Deployment Overhead**: Test-time verification overhead (20-40% computational increase) is problematic for latency-critical applications like chatbots and interactive systems.

8. **Critical Step Identification Accuracy**: Attention weights may not align with actual reasoning importance, potentially missing subtle errors or over-focusing on salient but correct steps.

9. **Optimization Interference Risk**: Joint training may cause policy to exploit process reward model artifacts (Goodhart's Law), requiring careful mitigation strategies like gradient scaling and consistency regularization.

10. **Cross-Domain Generalization**: Limited evidence on whether process reward models trained on one domain (e.g., mathematics) can effectively transfer to qualitatively different domains without significant fine-tuning.
