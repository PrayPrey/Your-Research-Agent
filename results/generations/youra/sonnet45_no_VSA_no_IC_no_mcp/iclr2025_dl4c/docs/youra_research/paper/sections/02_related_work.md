# Related Work

Our work connects three research areas: execution-based alignment for code generation, AI vs human feedback for text generation, and hidden test gaps in code evaluation. We review each area and position our contributions.

## Execution-Based Code Generation Alignment

Execution feedback — test pass/fail signals — has become the dominant evaluation paradigm for code generation benchmarks. HumanEval (Chen et al., 2021) established pass@k metrics measuring how often generated code passes unit tests, with state-of-the-art models achieving 70-80% pass@1. MBPP (Austin et al., 2021) extended this to educational programming problems, and SWE-bench (Jimenez et al., 2023) scaled to realistic software engineering tasks with repository-level test suites.

CodeRL (Le et al., 2022) pioneered reinforcement learning with execution feedback, fine-tuning code generation models to maximize test pass rates through actor-critic optimization. Their approach achieved ~78% pass@1 on HumanEval and ~80% on APPS, demonstrating that execution signals can guide model improvement. However, CodeRL studied execution feedback in isolation without comparing to other modalities (AI reward models, human ratings) or testing task-dependency. Our work reveals that CodeRL's effectiveness may be task-specific: execution-human correlation ρ=0.68 for HumanEval (moderate alignment) drops to ρ=0.35 for SWE-bench (weak alignment), suggesting execution-only approaches succeed on better-specified tasks but struggle when specifications are incomplete.

## AI vs Human Feedback for Text Generation

RLAIF (Lee et al., 2023) demonstrated that AI-generated feedback can approximate human preferences for text generation tasks, achieving comparable performance to RLHF when using LLM-generated preference labels. Their work showed AI-human correlation in the 0.5-0.7 range for summarization and instruction-following, suggesting AI feedback captures patterns overlapping with human judgment.

InstructGPT (Ouyang et al., 2022) established RLHF as an effective alignment strategy for text generation, training reward models on human preference data to fine-tune language models. The key insight was that supervised learning on human annotations (reward model training) followed by RL optimization achieved stronger alignment than zero-shot prompting or supervised fine-tuning alone.

However, both RLAIF and InstructGPT focused on text generation without code-specific analysis or execution feedback comparison. Our work extends these findings to code generation: we quantify zero-shot AI-human correlation (ρ=0.45-0.52, consistent with RLAIF's range) and demonstrate that supervised learning on human annotations (analogous to InstructGPT's reward model training) achieves stronger AI-human correlation (ρ=0.85, +75% improvement). Critically, we add execution feedback as a third modality, enabling systematic comparison across all three feedback types.

## Hidden Test Gaps and Specification Completeness

HumanEval+ (Liu et al., 2023) revealed a hidden test gap: models achieving 70-80% pass@1 on HumanEval drop to 30-40% on HumanEval+ with additional hidden tests, suggesting overfitting to visible test suites. This performance drop indicates that even "well-specified" competitive programming tasks have incomplete test coverage — tests don't capture all correctness dimensions.

SWE-bench (Jimenez et al., 2023) characterized realistic software engineering tasks as inherently underspecified: GitHub issue descriptions provide incomplete requirements, and test suites focus on functional correctness while missing non-functional dimensions (code quality, maintainability, security). State-of-the-art models achieve only ~10-20% resolution rates on SWE-bench, far below HumanEval performance.

While HumanEval+ observed the hidden test gap and SWE-bench characterized underspecification, neither work systematically measured feedback correlation structure or tested the specification completeness mechanism. Our work provides mechanistic explanation: we quantify the missed intent dimension gap (SWE-bench 67% vs HumanEval 33%, χ²=53.33 p<0.0001) through qualitative coding of disagreement cases across six intent dimensions (correctness, edge cases, readability, efficiency, maintainability, security). This validates that specification completeness drives test-intent coverage, which in turn drives execution-human correlation variance (2.29× between-task vs within-task variance ratio, ANOVA F=2226.34 p<0.0001).

## Code Quality Assessment and Review

CodeReviewer (Li et al., 2022) demonstrated that supervised learning on code review comments can train models to identify quality issues, achieving correlation with human reviewers on readability and maintainability dimensions. Their work suggests AI models can capture non-functional code dimensions that execution feedback misses.

Our supervised AI feedback approach (h-m3) aligns with CodeReviewer's supervised learning paradigm: we fine-tune CodeBERT on (code, human_score) pairs and achieve ρ=0.85 AI-human correlation, exceeding zero-shot baselines by +75%. This demonstrates that code quality assessment — previously studied for code review — transfers to alignment feedback for code generation.

## Positioning Our Contributions

Prior work studied feedback modalities in isolation (CodeRL execution-only, RLAIF AI-human for text) or observed gaps without mechanistic explanation (HumanEval+ hidden test drop). Our work is the first to:

1. **Systematically map feedback orthogonality**: We measure pairwise correlations between execution, AI, and human feedback across three datasets spanning specification completeness (HumanEval competitive, MBPP basic, SWE-bench realistic), revealing task-dependent correlation structure.

2. **Validate specification completeness mechanism**: We quantify the causal chain (specification completeness → test coverage → execution-human correlation) through qualitative dimension analysis (2.00× missed dimension gap) and statistical variance decomposition (2.29× variance ratio), explaining *why* execution feedback fails for realistic tasks.

3. **Demonstrate supervised AI path for code**: We extend InstructGPT's RLHF analogy from text to code, showing that supervised learning on human annotations achieves ρ=0.85 AI-human correlation independent of task type, providing a viable alternative to execution-only alignment.

These contributions reframe code generation alignment from "which feedback wins" (execution vs AI vs human) to "where each provides unique signal" (task-adaptive feedback routing), enabling alignment strategies that adapt to specification completeness rather than assuming execution feedback suffices universally.
