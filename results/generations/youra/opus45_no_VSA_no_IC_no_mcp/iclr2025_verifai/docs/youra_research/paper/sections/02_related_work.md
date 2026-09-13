# Related Work

Our work builds on three areas of research: LLM self-repair for code generation, compiler feedback integration, and type-aware neural code synthesis. We position our approach as the first systematic study of error message *format* as an independent variable, addressing a gap in existing work that focuses on feedback presence rather than presentation.

## Self-Repair and Iterative Refinement

The self-repair paradigm enables LLMs to iteratively refine their code outputs based on execution feedback. Chen et al. [2024] conducted a comprehensive study across model scales, demonstrating that self-repair yields minimum +4.9% improvement on HumanEval and MBPP benchmarks. Their work established that modern 8B+ parameter models can benefit from prompt-based self-repair without fine-tuning. However, their experiments used raw compiler output directly, without investigating whether alternative formatting might improve repair success.

The Self-Refine framework [Madaan et al., 2023] introduced a general paradigm for iterative LLM self-critique and revision. While influential, this framework focuses on the *iterative structure* of refinement rather than the *format* of feedback signals. Our work complements these approaches by optimizing the feedback representation itself.

InspectCoder [2025] compared static and dynamic analysis feedback for self-repair, finding that debugger-based dynamic feedback can complement static analysis. While their work varies the *type* of analysis, they do not systematically vary how static analysis errors are formatted—a dimension our work directly addresses.

## Compiler Feedback Integration

A parallel line of research integrates compiler signals into LLM training and inference. CompCoder [2024] demonstrated dramatic improvements in compilation success (44% → 89%) by using compiler feedback as a training signal. This work validates that compiler information is valuable but treats the feedback format as fixed during inference.

CodeRL [Shojaee et al., 2023] applied actor-critic reinforcement learning with unit test signals, optimizing for test-passing behavior. While effective, this approach requires fine-tuning and does not address the question of how to present feedback during inference.

The survey by [Zhang et al., 2025] on LLM-compiler integration catalogues various approaches to combining these technologies. Notably, all surveyed methods treat compiler output format as given rather than as a design variable. Our work addresses this gap by treating format as an independent variable that can be optimized.

## Type-Aware Code Generation

TyFlow [2025] introduced type-guided program synthesis, demonstrating that type checker integration during generation improves correctness. While related in spirit—both works leverage static analysis for improved code quality—TyFlow addresses generation rather than repair, and focuses on type constraints during decoding rather than error message formatting.

ReCode [2025] combines retrieval-augmented generation with static analysis for code repair. Their fine-grained retrieval approach implicitly reformats error information by retrieving relevant examples. However, they do not isolate the effect of format from the effect of additional retrieved context.

## Our Position

The works above demonstrate the value of compiler feedback (iteration improves repair), type constraints (static analysis information helps), and retrieval augmentation (additional context aids repair). However, none systematically study error message *format* as an independent variable while controlling for information content.

Our approach differs in three key ways:

1. **Format as independent variable**: We vary error format while holding information content constant, using a scrambled control condition that contains identical content with randomized section order.

2. **Causal identification**: Our paired experimental design enables causal claims about whether structure itself drives improvement, rather than merely information availability.

3. **Fix specificity dimension**: We introduce and test a scaffolding-theory-motivated framework for hint specificity, investigating not just format but also the *level* of guidance provided.

This positioning reveals that while prior work has extensively optimized *what* feedback to provide, the question of *how* to present that feedback remains largely unexplored—a gap our work directly addresses.
