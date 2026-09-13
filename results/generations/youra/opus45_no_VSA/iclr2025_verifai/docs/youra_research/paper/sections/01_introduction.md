# Introduction

When debugging code, do you fix typos before logic errors, or dive straight into the failing test? For humans, the answer is instinctive—clean up syntax first, then tackle semantics. Yet LLM-based code repair systems treat all feedback equally, presenting execution failures and static analysis warnings in arbitrary order. This seemingly trivial presentation choice, we show, causes a 29% performance difference in repair quality.

LLM self-repair has emerged as a promising approach to code generation, achieving 10-17% relative improvement on standard benchmarks [Olausson et al., 2023]. The dominant paradigm iteratively refines generated code using execution feedback—test results, stack traces, and assertion failures—until tests pass or a budget is exhausted. Recent work has explored augmenting execution feedback with static analysis (type checking, linting, style violations), demonstrating significant reductions in security and reliability issues [Blyth et al., 2025].

However, existing studies conflate feedback *content* with feedback *presentation*. When comparing "static analysis feedback" against "execution feedback," prior work necessarily varies the information provided—more feedback types mean more information. This leaves a fundamental question unanswered: does the **order** in which feedback is presented independently affect repair quality, holding content constant?

This gap matters because presentation order is a free variable in any feedback-based repair system. If order affects quality—and if that effect is large—then current systems leave significant performance on the table by ignoring this structural choice. Moreover, understanding *why* order matters would reveal insights into how LLMs process sequential feedback during iterative repair.

We hypothesize that static-first feedback ordering creates a coarse-to-fine repair trajectory. When static analysis errors (syntax violations, type mismatches, style warnings) appear before execution failures, the LLM resolves surface-level issues before tackling semantic errors. This clears low-level noise from the repair space, providing a cleaner foundation for logical reasoning. The key insight is not that static-first provides different information—we control for that—but that it structures the repair process differently.

Our experiments confirm this hypothesis with surprising strength. On HumanEval (164 problems) + MBPP (500 problems) with GPT-4o-mini, static→execution ordering achieves 55.57% pass@1 versus 43.07% for execution→static—a **29.02% relative improvement** (95% CI: [15.74%, 44.53%], p=6.31×10⁻⁶). Critically, both conditions receive byte-identical feedback content; only the presentation order differs.

Investigating the mechanism, we find that the effect operates through regression prevention rather than early-gain amplification. Static-first repairs exhibit 38% fewer inter-iteration regressions (p=0.0198)—previously passing tests stay passing. Early iteration gains, by contrast, are statistically indistinguishable between conditions. The scaffolding metaphor applies, but not in the way one might expect: static-first ordering doesn't help the LLM build faster, it helps it build more stably.

We make the following contributions:

1. **Matched-content experimental design:** We introduce a methodology that isolates feedback ordering from information volume by ensuring byte-identical content across conditions. This controls the primary confound in prior feedback comparison studies.

2. **Evidence of ordering effect:** We demonstrate that static→execution ordering achieves 29% relative pass@1 improvement over execution→static ordering, with strong statistical significance (p<10⁻⁵).

3. **Mechanism identification:** We show that the effect operates through regression prevention (38% reduction) rather than early-gain acceleration, refining the scaffolding hypothesis.

The remainder of this paper is organized as follows. Section 2 reviews related work on LLM code repair and feedback mechanisms. Section 3 describes our experimental methodology. Section 4 presents the experimental setup, Section 5 reports results, and Section 6 discusses implications and limitations. Section 7 concludes with future directions.
