# Abstract

Execution-based feedback — using test pass/fail signals to guide model training — is the dominant paradigm for code generation alignment, exemplified by methods like CodeRL. This approach assumes that test-based feedback uniformly proxies human intent across task types. We challenge this assumption through the first systematic mapping of **feedback orthogonality**: the correlation structure between execution-based, AI reward model, and human rating feedback, segmented by task specification completeness.

Across three datasets spanning competitive programming (HumanEval), basic problems (MBPP), and realistic software tasks (SWE-bench), we find that execution-human correlation is **task-dependent**, varying 2.29× (ANOVA F=2226.34, p<0.0001): ρ=0.68 for competitive tasks drops to ρ=0.35 for realistic tasks. This variance is not noise — it reflects a validated mechanism where **specification completeness determines test-intent capture**. Realistic tasks miss 2.00× more intent dimensions than competitive tasks (66% vs 33%, chi-square p<0.0001), explaining why execution feedback degrades as a proxy for human judgment.

We demonstrate a viable alternative: **supervised AI feedback** (CodeBERT fine-tuned on human annotations) achieves ρ=0.85 AI-human correlation, a +75% improvement over zero-shot baseline (ρ=0.485). This validates a supervised learning path analogous to InstructGPT's RLHF for text generation, offering a cheaper alternative to human-in-the-loop reinforcement learning.

Our findings challenge the execution-only alignment assumption underlying CodeRL and related methods, establish specification completeness as a moderator of feedback effectiveness, and validate supervised learning for code quality assessment. We enable adaptive feedback weighting strategies that route execution feedback for well-specified tasks and AI/human feedback for underspecified tasks, with expected +10-20% performance gains on realistic benchmarks.

**Keywords**: code generation, alignment, feedback orthogonality, execution-based feedback, supervised learning, specification completeness

---

**Word count**: 250 (target: 250)
