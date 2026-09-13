# 1. Introduction

A code generation model passes all unit tests on a competitive programming benchmark (HumanEval, 68% correlation with human judgment) but fails to meet developer expectations in production (SWE-bench, 35% correlation). Same model, different task, different feedback signal reliability. This gap reveals a fundamental assumption underlying current alignment approaches: that execution-based feedback — test pass/fail signals — uniformly proxies human intent across all code generation tasks.

Execution-only alignment methods like CodeRL (Le et al., 2022) achieve ~70-80% pass@1 on competitive programming benchmarks by training models via reinforcement learning on test outcomes. However, these methods assume that test-based feedback captures what humans value in code — correctness, readability, maintainability, efficiency — regardless of task type. No prior work has systematically measured whether this assumption holds when task specifications vary in completeness, from fully-specified competitive programming problems to underspecified real-world software tasks.

This paper challenges the execution-only assumption through the first systematic mapping of **feedback orthogonality**: the correlation structure between execution-based feedback, AI reward model feedback, and human rating feedback, segmented by task specification completeness. We ask: when do these three feedback modalities agree, and when do they diverge?

We find that **execution-human correlation is task-dependent**, varying 2.29× across task types (ANOVA F=2226.34, p<0.0001): ρ=0.68 for competitive programming (HumanEval) drops to ρ=0.35 for realistic software tasks (SWE-bench). This variance is not noise — it reflects a mechanism where **specification completeness determines test-intent capture**. When tests encode all requirements (competitive tasks), execution feedback aligns well with human judgment. When specifications are underspecified (realistic tasks), tests miss critical dimensions that only humans evaluate, resulting in a 2.00× gap in missed intent dimensions (chi-square p<0.0001).

Importantly, we demonstrate a viable alternative: **supervised AI feedback** trained on human annotations achieves ρ=0.85 AI-human correlation (+75% improvement over zero-shot baseline), validating a supervised learning path analogous to InstructGPT's RLHF for text generation (Ouyang et al., 2022). This finding suggests that when execution feedback fails — on realistic, underspecified tasks — AI models can be trained to proxy human judgment effectively.

## Contributions

This work makes three contributions to code generation alignment research:

1. **First systematic feedback orthogonality mapping**: We measure pairwise correlations (execution/AI/human) across three datasets spanning specification completeness (HumanEval, MBPP, SWE-bench), revealing task-dependent correlation structure previously assumed uniform.

2. **Mechanism validation**: We validate the causal chain from specification completeness → test coverage gap → execution-human correlation variance through qualitative disagreement analysis, showing realistic tasks miss 2.00× intent dimensions compared to competitive tasks (66% vs 33%).

3. **Supervised AI feedback path**: We demonstrate that CodeBERT fine-tuned on human annotations achieves strong AI-human alignment (ρ=0.85), establishing supervised learning as a viable alternative to execution-only alignment for code quality assessment.

## Implications

Our findings have direct implications for alignment research and practice:

- **Challenges execution-only alignment assumption**: CodeRL's effectiveness is task-dependent — strong for competitive programming, weak for realistic software tasks. Multi-modal feedback is needed.

- **Enables adaptive feedback weighting**: Task type prediction (competitive vs realistic) can route feedback signals — trust execution for well-specified tasks, trust AI/human for underspecified tasks.

- **Validates supervised learning for code quality**: InstructGPT's RLHF approach (training reward models on human feedback) generalizes to code generation, offering a cheaper alternative to human-in-the-loop reinforcement learning.

The remainder of this paper is structured as follows: Section 2 positions our work within related research on execution feedback, AI alignment, and code evaluation. Section 3 describes our methodology, including datasets, feedback modalities, and statistical methods. Section 4 details our experiments validating correlation infrastructure (h-e1), specification completeness mechanism (h-m1), task-dependent variance (h-m2), and supervised AI effectiveness (h-m3). Section 5 presents results through correlation heatmaps, intent dimension analysis, and ANOVA decomposition. Section 6 discusses the HumanEval magnitude deviation, mechanism interpretation, supervised learning path, and limitations. Section 7 concludes with implications and future work.
