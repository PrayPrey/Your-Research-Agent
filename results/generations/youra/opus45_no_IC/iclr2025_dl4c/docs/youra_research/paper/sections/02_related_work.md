# Related Work

## Execution Feedback for Code Generation

Reinforcement learning from execution feedback has emerged as a dominant paradigm for aligning code generation models. PPOCoder \cite{shojaee2023ppocoder} applies Proximal Policy Optimization with binary test pass/fail rewards, demonstrating that execution feedback can improve code generation without human annotation. CodeRL \cite{le2022coderl} extends this with actor-critic methods and self-repair mechanisms. InterCode \cite{yang2023intercode} formalizes interactive coding as an RL environment where code serves as actions and execution feedback as observations.

Recent work has explored richer reward signals. RLPF \cite{jing2026rlpf} introduces staged rewards that order failed programs by execution progress and rank correct programs by efficiency improvement. ReTool \cite{feng2025retool} integrates real-time code execution within reasoning, using outcome feedback to guide tool use. These approaches provide denser supervision than binary pass/fail but operate at the episode level, applying uniform credit to all tokens.

Our work is orthogonal to reward design: we focus on *how* credit is assigned to individual tokens given any reward signal, rather than *what* reward signal is used.

## Fine-Grained Credit Assignment

The sparse reward problem in code RL has motivated token-level credit assignment. StepCoder \cite{dou2024stepcoder} introduces Fine-Grained Optimization (FGO), which masks non-executed code segments from gradient updates. The intuition is that tokens which never execute cannot have caused the test outcome, so excluding them concentrates learning on causally relevant code. StepCoder reports significant improvements over PPOCoder on APPS and MBPP benchmarks.

However, StepCoder introduces FGO alongside Curriculum of Code Completion Subtasks (CCCS), making it impossible to isolate which component drives improvement. The evaluation compares StepCoder (FGO + CCCS + compile feedback) against baselines with different feedback types, confounding mechanism effects with content effects.

Fine-Grained RLHF \cite{wu2023finegrained} demonstrates that per-segment rewards outperform holistic rewards in general language tasks, supporting the value of dense credit assignment. ORPS \cite{zhuohaoyu2025orps} unifies process and outcome rewards for code generation, showing that hybrid signals can improve sample efficiency.

Our work provides the first controlled validation of FGO's mechanism. We isolate FGO from curriculum effects and compare trace-based masking against random masking at matched sparsity, establishing whether execution information—not just sparsity—drives improvement.

## Inference-Time Execution Guidance

An alternative to training-time feedback is inference-time execution guidance. EG-CFG \cite{lavon2025egcfg} achieves state-of-the-art results (99.4% on HumanEval) by injecting runtime feedback directly into the decoding process. This approach uses execution outcomes to reweight token probabilities during generation, requiring no additional training.

While inference-time methods achieve impressive results, they incur computational overhead at every generation and do not improve the underlying model's capabilities. Training-time approaches like FGO provide complementary benefits: the learned policy internalizes execution-aligned behavior, enabling efficient inference without runtime feedback.

Our focus is training-time mechanism validation. The techniques we validate could potentially be combined with inference-time guidance, though we leave this exploration to future work.

## Mechanism Validation in Machine Learning

Our verification protocol draws inspiration from causal mechanism validation in machine learning \cite{pearl2009causality}. Rather than reporting aggregate performance improvements, we decompose the proposed mechanism into independently testable components with explicit falsification criteria. This approach enables precise failure localization and builds confidence that observed improvements stem from the hypothesized mechanism rather than confounding factors.

Similar decomposition approaches have proven valuable in interpretability research, where circuit analysis identifies specific components responsible for model behaviors \cite{elhage2021mathematical}. We apply this principle to RL mechanism validation, establishing a template for rigorous evaluation of credit assignment methods.
