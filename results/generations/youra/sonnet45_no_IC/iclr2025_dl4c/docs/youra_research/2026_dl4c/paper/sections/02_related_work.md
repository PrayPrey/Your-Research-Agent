# Related Work

Our work builds on three research threads—execution-based reinforcement learning for code generation, human feedback alignment, and multi-criteria reward modeling—while introducing a novel fourth dimension: dynamic curriculum over feedback modality. We position our contribution against prior work chronologically, showing the field's natural convergence toward multi-modal integration, and explain why dynamic scheduling addresses limitations that static approaches cannot resolve.

## Execution Feedback Reinforcement Learning

PPOCoder (Shojaee et al., 2023) pioneered execution-based RL for code generation, training policy models with rewards derived solely from automated test case pass/fail signals. Their work demonstrated substantial correctness improvements—approximately 30 percentage points on MBPP benchmarks—validating that non-differentiable execution feedback can be integrated into policy gradient optimization through Proximal Policy Optimization. More recent work extends this foundation: Process-Supervised RL (Ye et al., 2025) introduces line-by-line verification with compiler feedback, enabling finer-grained correctness signals during generation. These methods excel at producing functional code but optimize a single objective—test passage—ignoring code quality, readability, and maintainability. Generated solutions may be correct yet unmaintainable in production environments.

Our Phase 1 mechanism builds directly on PPOCoder's execution feedback paradigm, using execution weight dominance (0.800) during early training to establish correctness foundations. However, we extend beyond single-objective optimization by treating execution feedback as the *first stage* of a multi-phase curriculum, not the sole training signal throughout.

## Human Feedback Alignment for Code

The RLHF paradigm, established for general language model alignment (Ouyang et al., 2022) and adapted for code generation, trains models to optimize human preference scores collected through pairwise comparisons or Likert-scale quality ratings. This approach captures subjective quality dimensions—code elegance, naming conventions, documentation—that automated metrics cannot evaluate. However, human annotation is expensive (approximately $10–20 per code sample with multiple annotators), limiting scalability, and human-only training may sacrifice functional correctness for stylistic preferences.

ProSec (Xu et al., 2024) applies human feedback specifically to security alignment, synthesizing vulnerability scenarios from Common Weakness Enumeration entries and training reward models on security-focused preferences. SEAlign (Zhang et al., 2025) extends human feedback to multi-step software engineering tasks, using Monte Carlo Tree Search to align agent decision processes with human software engineering practices. While these methods demonstrate the value of human oversight, they apply human feedback uniformly across training—a static integration strategy that ignores the potential for phase-specific emphasis.

Our approach uses human feedback strategically in Phase 3 (70–100% training progress) with increasing weight (0.400→0.636), reserving expensive human oversight for edge case refinement after correctness and quality foundations are established. This reduces annotation requirements while targeting human judgment where it provides maximum value: resolving conflicts between execution-only collapse and quality optimization.

## Multi-Criteria Reward Modeling

Themis (Paul et al., 2026) represents the state-of-the-art in multi-criteria code reward modeling, training reward models on 350,000+ preference pairs across multiple quality dimensions (functional correctness, API validity, syntactic well-formedness, semantic coherence). Unlike PPOCoder's binary execution signal or RLHF's holistic quality score, Themis learns to predict multi-dimensional assessments, enabling models to balance correctness, style, and efficiency simultaneously. However, Themis operates as an offline ranking system: the reward model scores candidates during inference but does not dynamically adjust which criteria dominate during training.

Curriculum-RLAIF (Li et al., 2025) introduces curriculum learning to alignment, but schedules task difficulty (progressing from simple to complex code generation problems) rather than feedback modality. Their AI feedback weight remains constant throughout training, missing the opportunity to match feedback emphasis to capability-building stages.

Our tri-modal framework extends multi-criteria approaches in two ways. First, we integrate three distinct feedback sources—execution, AI, human—*online during RL training*, not as an offline ranking tool. Second, we apply dynamic weight scheduling: execution weight decays (0.800→0.182), AI weight peaks mid-training (max 0.545 at 50% progress), and human weight increases late (0.100→0.636). This curriculum over feedback type distinguishes our work from both static multi-criteria models and task-difficulty curricula.

## Behavioral Specification and Process Supervision

BeSpec (Xu et al., 2026) introduces behavioral specification alignment, building explicit behavioral models to verify generated code against intent specifications rather than relying solely on test case execution. This aligns with our observation that execution feedback alone is insufficient—BeSpec addresses intent alignment, while we address quality and edge case handling. Process-supervised methods like those in Ye et al. (2025) provide finer-grained execution signals but remain single-modality: they improve *how* execution feedback is collected (line-by-line vs. whole-program), not *when* to emphasize execution vs. other signals.

These works are complementary to ours. BeSpec could serve as a fourth feedback modality in future extensions; process supervision could refine our Phase 1 execution feedback granularity. Our contribution lies in demonstrating that *scheduling which feedback type dominates* is a viable training strategy, orthogonal to improving individual feedback signals.

## Positioning Our Contribution

The field has naturally progressed from single-feedback methods (PPOCoder execution-only, RLHF human-only) toward multi-criteria integration (Themis) and curriculum learning (Curriculum-RLAIF over task difficulty). Yet no prior work explores curriculum over feedback *modality*—dynamically adjusting which signal type receives emphasis across training phases. Our mechanism validation demonstrates that execution→AI→human scheduling is implementable, produces predicted weight patterns, and achieves phase-specific objectives (correctness foundation, quality refinement, edge case handling). This opens a new dimension in multi-objective RL: not just *which* feedback to combine, but *when* to emphasize each signal.

We do not claim prior work is wrong—PPOCoder's execution feedback is essential for correctness, RLHF's human signal is critical for quality, and Themis's multi-criteria modeling is foundational for our AI feedback component. Rather, we argue that static integration forces compromise, while dynamic scheduling enables phase-appropriate optimization. The mechanism-level validation (all four sub-hypotheses pass gates) provides initial evidence; performance validation remains for future work.
