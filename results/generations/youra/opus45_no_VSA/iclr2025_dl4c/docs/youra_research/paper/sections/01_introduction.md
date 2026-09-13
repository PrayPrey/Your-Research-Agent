# Introduction

RL-trained models receive execution feedback during training, but do they learn to leverage feedback more effectively at test time? Despite RL fine-tuning being standard practice for code generation---CodeRL [Le et al., 2022] pioneered execution-based rewards while PPOCoder [Shojaee et al., 2023] extended this to policy optimization---no prior work has systematically measured whether RL training transfers to improved test-time refinement. This gap matters: test-time refinement is becoming the dominant paradigm for code generation, with Self-Refine [Madaan et al., 2023] and S* [Li et al., 2025] demonstrating that iterative refinement can enable 3B models to match GPT-4o-mini. If RL training investments do not compound with refinement, practitioners may be misallocating compute.

The conventional wisdom treats training-time and test-time optimization as independent targets. RL papers report single-shot accuracy improvements, while prompting papers apply refinement to pretrained models. This separation leaves the interaction effect unmeasured. Are RL training and test-time refinement redundant (purely additive), complementary (superadditive), or even conflicting? The question has practical urgency: a superadditive interaction would justify combined investment, while a subadditive one would suggest choosing one approach over the other.

We address this gap by proposing a 2×2 factorial design that isolates the Training×Refinement interaction. Our experimental framework crosses training type (cross-entropy vs. RL with execution feedback) with inference mode (single-shot vs. K-step refinement), measuring the interaction term directly via generalized linear mixed models with problem-level random effects.

Our key insight is that RL training with diverse execution feedback may induce a feedback-conditioned edit policy---optimizing p(edit | code, feedback)---that specifically transfers to test-time refinement. We operationalize this mechanism through mutual information I(F;E) between feedback spans and edit spans, estimating it via the MINE neural estimator [Belghazi et al., 2018]. If RL training increases structural coupling between what the feedback says and where the model edits, each refinement step should be more directed, producing superadditive gains.

Building on this insight, we make the following contributions:

1. **Factorial experimental framework:** The first systematic 2×2 design for measuring Training×Refinement interaction in code generation, isolating the interaction term from main effects.

2. **I(F;E) metric operationalization:** A concrete implementation of feedback-edit mutual information as a mechanistic probe, using MINE estimation with regression control for edit length.

3. **Diversity manipulation infrastructure:** FeedbackDiversityController that achieves 1.1-bit entropy separation between high-diversity (H=2.0 bits) and low-diversity (H=0.9 bits) batches, enabling controlled ablation of diversity's role.

4. **Validated experimental infrastructure:** All code paths execute successfully at the smoke-test level, demonstrating that the methodology is ready for full-scale experiments pending GPU resources.

We organize the paper as follows: Section 2 surveys related work on RL training and test-time refinement, showing these lines have remained isolated. Section 3 presents our methodology, explaining why factorial design and I(F;E) measurement address the gap. Section 4 describes experimental setup, and Section 5 presents results validating our infrastructure. Section 6 discusses limitations and future directions.
