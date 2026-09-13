# Related Work

Our work bridges LLM code repair and feedback mechanism design. We review each area, highlighting the gap our matched-content design addresses.

## LLM Self-Repair

Iterative self-repair has become the dominant paradigm for improving LLM code generation beyond single-shot accuracy. Olausson et al. [2023] demonstrated that feeding execution feedback (test results, stack traces) back to the model enables 12-17% relative improvement on HumanEval. Arimbur [2026] showed that most gains concentrate in the first 2-3 repair iterations, with diminishing returns thereafter.

Several frameworks operationalize self-repair. CodeRL [Le et al., 2022] integrates reinforcement learning with execution feedback. ThinkRepair [ISSTA 2024] uses self-directed debugging on Defects4J. More recent work explores multi-agent architectures: CodeCoR [2025] achieves 77.13% pass@1 on HumanEval/MBPP through agent collaboration.

These approaches share a common assumption: feedback content determines repair quality. The question of feedback *ordering*—given the same content—remains unexplored.

## Static Analysis Feedback

Static analysis provides complementary signals to execution feedback. Jain et al. [2024] showed that LLM-assisted code cleaning improves code quality without runtime signals. Blyth et al. [2025] demonstrated that Pylint feedback reduces security issues from >40% to 13% and reliability warnings from >50% to 11%.

AutoSafeCoder [Nunez et al., 2024] combines static analysis with fuzz testing in a multi-agent framework, achieving 13% vulnerability reduction. Dolcetti et al. [2024] integrated testing and static analysis feedback for safety improvements.

However, studies comparing static and execution feedback face a fundamental confound: they necessarily vary information volume alongside feedback type. Cascaded approaches (static + execution) provide more information than single-type approaches. Our prior work (h-c1) achieved 16.18% improvement with cascaded feedback, but whether this stems from *more* information or *ordered* information was unclear.

## Feedback Presentation Effects

Research on prompt engineering and positional effects suggests LLMs are sensitive to presentation order. Recency effects in transformer attention mean later tokens receive disproportionate weight. This raises an alternative hypothesis: static-first might help not because it structures the repair process, but simply because execution feedback appears last (terminal position bias).

FeedbackEval [Dai et al., 2025] benchmarked feedback-driven code repair across feedback types, finding mixed feedback yields 63.6% repair success. However, ordering effects were not systematically tested.

## Our Contribution

Unlike prior work, we control for information volume by ensuring byte-identical feedback across conditions. This matched-content design isolates the ordering effect from the content effect. We test both the existence of an ordering effect and its mechanism—distinguishing scaffolding (coarse-to-fine repair) from recency bias (terminal position advantage).
