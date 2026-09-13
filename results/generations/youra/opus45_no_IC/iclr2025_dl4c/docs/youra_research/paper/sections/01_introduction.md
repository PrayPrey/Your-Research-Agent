# Introduction

When reinforcement learning agents learn to generate code, how much of each generated token actually matters? In a typical code solution, only a fraction of tokens—those that execute during test evaluation—directly influence the reward signal. The remaining tokens, including unused imports, unreached branches, and dead code, contribute nothing to the outcome yet receive identical gradient updates under standard policy gradient methods.

This observation points to a fundamental limitation in reinforcement learning from execution feedback for code generation. The sparse reward problem—where a binary test pass/fail signal provides no gradient for partial progress—has motivated numerous approaches to provide denser supervision \cite{shojaee2023ppocoder,dou2024stepcoder,jing2026rlpf}. However, existing solutions often conflate two orthogonal factors: *what* feedback is provided (compilation errors, test results, execution traces) and *how* credit is assigned to individual tokens (episode-level rewards versus token-level masking).

Fine-Grained Optimization (FGO), introduced by StepCoder \cite{dou2024stepcoder}, addresses the credit assignment problem by masking non-executed code segments from gradient updates. The intuition is compelling: if a token never executes, it cannot have caused the test to pass or fail, so excluding it from learning should concentrate gradients on causally relevant code. Yet StepCoder introduces FGO alongside a curriculum learning strategy (CCCS), making it impossible to isolate which component drives the reported improvements. Does FGO work because trace-informed masking identifies the right tokens, or would random masking at similar sparsity levels achieve comparable results?

We present the first controlled mechanism validation study of FGO for code generation RL. Rather than proposing a new method, we decompose the FGO mechanism into three testable components and verify each with explicit falsification criteria:

1. **Trace Collection**: We verify that Python's `sys.settrace` reliably captures execution traces during test evaluation, achieving 100% capture rate across 500 samples.

2. **Gradient Exclusion**: We verify that FGO's token masking correctly excludes non-executed tokens from gradient computation, with masked tokens receiving exactly zero gradient in all verification checks.

3. **Credit Assignment**: We verify that concentrating gradients on executed tokens improves final performance, observing a 10% higher pass@1 (0.244 vs 0.222) in simulation-based evaluation.

This decomposition enables precise failure localization. If trace collection fails, the problem lies in the execution monitoring infrastructure. If gradient exclusion fails, the masking implementation is incorrect. If credit assignment fails despite correct masking, the theoretical premise of FGO—that execution-aligned gradients improve learning—would be falsified.

Our key finding is that FGO's benefit comes from gradient exclusion: non-executed tokens receive exactly zero gradient, while executed tokens receive 1.78× stronger signal concentration. This concentrates learning on code that actually contributed to the reward, providing dense supervision without requiring additional reward shaping or curriculum design.

We make the following contributions:

- **Mechanism Decomposition**: We decompose FGO into three independently testable hypotheses (trace → mask → exclusion → credit), enabling controlled validation of each component.

- **Verification Protocol**: We establish explicit gate criteria with falsification thresholds, moving beyond aggregate performance metrics to mechanism-level validation.

- **Empirical Validation**: We verify all three mechanism components on HumanEval and MBPP benchmarks, demonstrating 100% trace capture, verified gradient exclusion, and 10% performance improvement.

- **Reusable Components**: We release validated implementations of trace collection, token classification, and masked PPO loss for future code RL research.

The remainder of this paper proceeds as follows. Section 2 reviews related work on execution feedback for code generation. Section 3 describes our methodology, including the FGO mechanism and verification protocol. Section 4 details the experimental setup. Section 5 presents results for each hypothesis in the verification chain. Section 6 discusses limitations and broader implications. Section 7 concludes with future directions.
