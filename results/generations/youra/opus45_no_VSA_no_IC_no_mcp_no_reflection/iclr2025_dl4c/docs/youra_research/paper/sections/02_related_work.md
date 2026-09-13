# Related Work

We review three lines of work: execution-based reward design for code LLMs, multi-granularity feedback approaches, and process supervision methods. Each provides building blocks for our study, but none addresses the question of minimum experimental scale for reward ablation.

## Execution Feedback for Code LLMs

CodeRL (Le et al., 2022) established the RLEF paradigm using binary execution rewards: the model receives reward 1 if all test cases pass, 0 otherwise. This simple signal achieved strong results on HumanEval, demonstrating that execution feedback can guide policy improvement. However, binary rewards are informationally sparse—a model receives the same 0 reward whether its output has a syntax error or fails one assertion on an edge case.

PPOCoder (Shojaee et al., 2023) adapted Proximal Policy Optimization for code generation, validating PPO's stability in this domain. Their focus was algorithmic (PPO vs. REINFORCE) rather than reward design, and they used binary execution feedback.

Both works report final accuracy but not samples-to-threshold or learning curves. This makes it impossible to assess how much training was required for policy improvement to emerge—a gap our work aimed to address.

## Multi-Granularity Feedback

RLTF (Liu et al., 2023) introduced fine-grained feedback incorporating test pass rates and error type information. Their results suggested that richer feedback improves performance, but the comparison lacked controlled ablation: different conditions used different training infrastructure, making it unclear whether improvements stemmed from feedback granularity or implementation details.

Self-repair approaches (Chen et al., 2023) use error traces for iterative debugging, demonstrating that error information has value for code improvement. However, this is a prompting technique rather than a reward signal for RL training.

Our work builds on RLTF's multi-granularity concept but provides controlled comparison: same model, same optimizer, same hyperparameters, same evaluation—varying only the reward function.

## Process Supervision

Process reward models (Lightman et al., 2023) demonstrated that step-by-step supervision outperforms outcome-only supervision for mathematical reasoning. This "Let's Verify Step by Step" approach provides dense intermediate feedback rather than sparse final rewards.

For code generation, however, process supervision requires explicit step annotations that are expensive to obtain. Execution feedback provides free intermediate signals (error types, partial test results) without human labeling. Our information bandwidth framework connects these approaches: process supervision increases feedback density, and so does our categorical error scoring—but ours requires no annotation.

## The Missing Piece: Scale Requirements

Across all these works, a consistent pattern emerges: papers report what works but not how much training was required. Sample complexity for code LLM RL remains uncharacterized. Our contribution—a negative result establishing minimum scale requirements—fills this gap. When all conditions produce zero learning at 1-epoch scale, we learn something valuable: PoC pilots may be systematically uninformative for reward design research.

This absence of scale guidance in the literature motivated our study. Unfortunately, our own scale proved insufficient, but we report this explicitly rather than abandoning the study without publication.
