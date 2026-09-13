# Related Work

To understand the gap our work addresses, we review existing approaches to feedback-driven code generation, organizing them by feedback type.

## Static Analysis Feedback

Static analysis tools like pylint and mypy analyze code structure without execution, detecting type mismatches, undefined variables, unreachable code, and style violations. Recent work demonstrates their value for LLM code generation.

The Static Analysis as Feedback Loop approach shows that providing pylint/mypy errors as feedback during iterative refinement reduces security issues from 40% to 13% over 10 iterations. This establishes that static feedback improves code quality. However, this work does not compare against execution-based feedback, leaving open the question of whether static analysis catches different errors than tests would.

Similarly, constrained decoding approaches like Synchromesh enforce syntactic validity during generation, preventing certain structural errors. These methods operate only on structure, with no execution component.

**Limitation:** These approaches demonstrate static analysis works, but do not quantify its relationship to execution feedback.

## Execution Feedback

Execution-based feedback uses test results—pass/fail outcomes, error messages, and output comparisons—to guide refinement. This paradigm powers several successful approaches.

Self-Refine demonstrates that LLMs can iteratively improve their outputs using feedback, achieving approximately 20% improvement across diverse tasks including code generation. The framework is general but uses single-source feedback per iteration.

CodeRL and RLPF train models with execution signals as rewards, learning to generate code that passes tests. StepCoder extends this with fine-grained compiler feedback. These approaches optimize for execution success but do not incorporate static analysis.

**Limitation:** These approaches demonstrate execution feedback works, but do not quantify overlap with static analysis signals.

## Combined Approaches

Some recent work combines both feedback types. The Helping LLMs Improve Code Generation approach provides both testing results and static analysis in a unified feedback loop, achieving improvements over single-source baselines.

**Limitation:** While this work shows combining helps, it does not decompose the individual contributions. The combined improvement could stem from orthogonal signals (each catching unique errors) or from redundant signals with one dominating. Without measuring overlap, the mechanism remains unclear.

## Our Position

Prior work establishes that both static and execution feedback improve code quality. What remains unknown is whether they catch the same or different errors. Our work fills this gap by directly measuring error class overlap using Jaccard similarity. This measurement is prerequisite to understanding why combining feedback helps and how to optimally compose signals.
