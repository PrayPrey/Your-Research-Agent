# Related Work

## Execution-Based Feedback for Code Generation

Execution feedback uses unit test outcomes as training signals. **CodeRL** (Le et al., 2022) pioneered actor-critic reinforcement learning for code, using test pass/fail as episode-level rewards. A critic network predicts functional correctness, enabling critical sampling for code regeneration. CodeRL achieves 2.69 pass@1 on APPS with critic sampling.

**RLTF** (Liu et al., 2023) extends execution feedback with multi-granularity signals. Beyond binary pass/fail, RLTF extracts fine-grained error locations from unit test output, providing line-level localization. Online RL with real-time data generation yields state-of-the-art results: 1.45 pass@1 on APPS without critic sampling. RLTF demonstrates that granularity matters—fine-grained feedback outperforms coarse rewards.

**PPOCoder** (Shojaee et al., 2023) combines PPO-based RL with non-differentiable execution feedback and structure alignment. The framework is task-agnostic, achieving strong results across APPS and MBPP benchmarks.

These methods share a limitation: execution feedback provides no semantic guidance about *why* code fails. A failed test says the output was wrong; it does not explain the underlying algorithmic error, naming confusion, or design flaw.

## AI-Generated Feedback for Code

AI feedback uses LLM-generated critique for code improvement. **Self-Refine** (Madaan et al., 2023) demonstrates zero-shot iterative refinement: the same LLM generates code, critiques it, and refines based on its own feedback. No training is required—refinement occurs at inference time. Self-Refine achieves +8.2% improvement on code optimization tasks.

However, AI feedback suffers from low fidelity. Madaan et al. analyze Self-Refine failures: 33% stem from identifying the wrong error location, and 61% from proposing incorrect fixes. Combined, 94% of failures trace to bad feedback rather than inherent problem difficulty.

**RefineCoder** (Zhou et al., 2025) introduces Adaptive Critique Refinement (ACR), using LLM-as-Judge and LLM-as-Critic for self-generated code refinement. Unlike Self-Refine's test-time approach, RefineCoder integrates AI feedback during training via distillation.

**OAIF** (Guo et al., 2024) uses Online AI Feedback for direct preference alignment, with an LLM serving as annotator. This approach outperforms offline DAP and RLHF but focuses on general text rather than code generation.

## Hybrid Approaches

Some work combines execution and AI elements. **CodeT** (Chen et al., 2022) uses LLM-generated test cases executed for code ranking. Dual execution agreement ranks candidates by test consistency and cross-sample agreement. This represents a hybrid where AI generates tests (not feedback) and execution verifies correctness.

## The Gap: No Controlled Comparison

Despite extensive work on both execution and AI feedback, no study directly compares them under controlled conditions. Each method uses different base models (CodeT5, GPT-3.5, various LLMs), different benchmarks (APPS, MBPP, HumanEval, proprietary), and different training protocols (RL, distillation, none). The research question "which feedback type is more effective?" cannot be answered from existing literature.

Furthermore, no prior work treats execution as a *verification mechanism* for AI feedback. Existing methods view execution and AI feedback as alternatives; we propose using execution to filter AI suggestions, potentially achieving both high fidelity and high semantic richness.
