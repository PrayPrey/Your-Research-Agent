# Related Work

Our work sits at the intersection of three research areas: execution feedback systems for LLM code generation, static analysis integration for safety and correctness, and multi-source verification orchestration. While individual feedback mechanisms have been extensively studied, systematic orchestration of multiple sources remains unexplored.

## Execution Feedback Systems

Execution-based feedback has emerged as the dominant paradigm for iterative LLM code generation. PerfCodeGen (Peng et al., 2024) represents the state-of-the-art in this space, using a training-free framework with execution feedback for performance optimization on HumanEval, MBPP, and APPS benchmarks. Their approach achieves significant improvements over single-shot generation by iteratively refining code based on test execution results. Similarly, LiveCodeBench provides a contamination-free benchmark for evaluating code generation with execution feedback, establishing standard protocols for pass@k metrics.

LLMDebugger (Li et al., 2024) extends execution feedback with basic block instrumentation, providing fine-grained runtime information to guide LLM debugging. Their rubber duck debugging approach demonstrates that detailed execution traces can help LLMs identify logic errors more effectively. LLMLOOP (Ravi et al., 2025) introduces multiple feedback loops incorporating compilation, static analysis, testing, and mutation testing, but critically, uses all sources simultaneously in an aggregation pattern rather than testing routing policies.

While these systems demonstrate the value of execution feedback, they share a common limitation: they operate with a single primary feedback source (execution) and do not systematically explore how multiple verification mechanisms should be orchestrated. Our work differs by explicitly testing routing policy as an independent variable—cascade versus aggregation—on tasks where both static and dynamic verification provide complementary signals.

## Static Analysis for Code Generation

Static analysis integration represents a complementary approach to code generation verification. Blyth et al. (2025) demonstrate that static analysis tools (Bandit for security, Pylint for readability) can reduce security issues from 40% to 13% and readability issues from 80% to 11% within 10 iterations of LLM refinement. Their work validates that static analysis provides actionable, structured feedback that LLMs can effectively process for iterative improvement.

AutoSafeCoder (Nunez et al., 2024) combines static analysis with fuzzing in a multi-agent framework for security-focused code generation. While they demonstrate benefits from multiple verification sources, their system does not isolate routing versus aggregation effects—all feedback sources operate simultaneously without explicit orchestration policy testing.

PropertyGPT and related work on constraint-guided generation explore using formal specifications (pre/post-conditions, type annotations) to steer LLM code generation. These approaches demonstrate that compositional guarantees from static analysis can complement execution-based validation, but they typically integrate specifications at generation time rather than as iterative feedback signals.

The gap in existing work is clear: static analysis has been validated as effective for iterative refinement, but its integration with execution feedback remains ad-hoc. Systems either use static analysis alone, or combine it with execution without testing whether presentation order (cascade vs. aggregation) affects efficiency. Our cascade routing explicitly tests whether static analysis should function as a pre-filter before expensive execution.

## Test-Driven and Multi-Source Verification

Test-driven LLM code generation explores using tests as specifications. TiCoder (Fakhoury et al., 2024) achieves 45.97% pass@1 improvement within 5 interactions using guided intent clarification through tests on MBPP and HumanEval. Their focus is on using tests to clarify requirements during generation, not on orchestrating verification feedback during refinement.

CoTran, ReTool, and "Tests as Prompt" approaches similarly explore test integration, but primarily at specification time rather than as iterative feedback orchestration. These works establish that tests provide valuable signal for LLM code generation, complementing our finding that test execution should be conditionally gated after static analysis rather than run unconditionally.

SAGA and PythonSaga explore property-based testing and compositional verification for LLM-generated code, demonstrating the value of structured test generation. However, these systems do not address the feedback routing question: when both static and dynamic verification are available, in what order should they be presented?

## Positioning Our Contribution

Our work makes three key departures from prior research:

**First**, we explicitly test feedback routing policy causality through paired-comparison experimental design. While systems like LLMLOOP use multiple feedback sources, they aggregate them simultaneously without ablation studies comparing orchestration strategies. Our cascade-versus-aggregation comparison isolates routing as the independent variable.

**Second**, we introduce dual-sensitive task classification to enable within-task paired design, controlling for task difficulty. This methodological contribution allows us to attribute efficiency differences to routing policy rather than task selection bias. Prior work uses between-task comparisons that confound routing effects with inherent task characteristics.

**Third**, we validate computational efficiency (layered verification with early filtering) as cascade routing's primary mechanism, distinct from cognitive efficiency (attention economy). Our 99.6% mypy detection rate demonstrates that static analysis can function as a nearly universal pre-filter for dual-sensitive tasks, enabling one-third of iterations to skip expensive execution. This finding shifts the framing from "more feedback is better" to "architectural layering matters"—fast checks before expensive checks, computational optimization over cognitive heuristics.

Where prior work optimizes individual feedback mechanisms (deeper execution traces in LLMDebugger, stronger static analysis in AutoSafeCoder), we optimize their integration. Our results suggest that production LLM coding assistants should implement cascade routing not for LLM attention management, but for resource efficiency: static analysis (<0.1 seconds) before test execution (5-10 seconds), with conditional gating to skip unnecessary computation.
