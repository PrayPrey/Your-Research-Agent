# Related Work

Our work sits at the intersection of automated program repair for LLM-generated code, grammar-constrained decoding, and SMT-based verification. We review each area and identify the gap that our FMD-conditioned analysis addresses.

## Iterative Feedback Repair for LLM Code Generation

A substantial body of work applies iterative feedback loops to improve LLM code generation quality. SELF-REFINE [Madaan et al., 2023] introduces a general framework where an LLM generates output, receives feedback from the same or a different model, and iteratively refines. Applied to code, feedback takes the form of execution results, compiler messages, or test outputs. Olausson et al. [2023] provide a comprehensive empirical survey of repair strategies for LLM-generated code, evaluating self-repair, external feedback, and execution-guided approaches across multiple benchmarks. Their findings show that repair effectiveness depends critically on the quality and specificity of the feedback signal.

**Limitation we address.** These methods assume that the feedback signal (type errors, syntax errors, test failures) will be informative for the model-benchmark pair under study. This assumption is implicit — never empirically verified for specific model-benchmark combinations. Our work shows that for CodeLlama-7B on HumanEval, one class of formal feedback (mypy type checking) produces zero informative output across 2,680 samples. We provide the empirical tool to measure this before applying repair.

Chen et al. [2022] introduce CodeT, which uses dual execution to filter LLM-generated solutions via test case agreement. While CodeT demonstrates ensemble effectiveness, it does not analyze the *failure mode complementarity* between different repair channels — our central question. Our C_score framework (Jaccard-based overlap of failure-to-success transition sets) extends CodeT's ensemble insight to formal mechanism analysis.

## Grammar-Constrained Decoding

Ugare et al. [2024] introduce SynCode, a grammar-constrained decoding framework that uses a pushdown automaton to mask syntactically invalid tokens during LLM generation, reducing syntax errors by construction. SynCode demonstrates effectiveness across multiple programming languages and LLM architectures. Our work builds on SynCode directly: we integrate SynCode v0.4.16 into our multi-method pipeline and measure its contribution to the FMD. We confirm SynCode's directional AST failure reduction (delta_ast=0.075) on HumanEval with CodeLlama-7B, consistent with Ugare et al.'s reported results.

**Limitation we address.** SynCode was evaluated in isolation and on its own benchmarks, without characterizing its interaction with post-hoc repair methods or measuring how it reshapes the downstream failure distribution. Our FMD pipeline measures this: SynCode reduces syntax failures, directly affecting what errors remain for Z3 and mypy to address. The 97.5% syntax dominance in the baseline we measure underscores why a syntax-first approach is critical.

## SMT-Based Verification and Repair

Z3 [De Moura and Bjørner, 2008] is a mature SMT solver with broad applicability to software verification. In the context of program repair, SMT-based approaches encode correctness constraints as logical formulae and search for constraint-satisfying code modifications. Verifying or repairing code with Z3 requires problem-specific encodings: arithmetic constraints (e.g., integer-equality test assertions) are tractable; general computation is not.

**Gap we address.** No prior work characterizes Z3 applicability to standard code generation benchmarks — specifically, what fraction of HumanEval problems are amenable to Z3 encoding. We quantify this empirically: 54/164 HumanEval problems (33%) have integer-equality test assertions suitable for Z3 constraint encoding. This scope measurement is a prerequisite for any Z3-based repair study on HumanEval.

## Code LLM Evaluation and Failure Analysis

HumanEval [Chen et al., 2021] is the standard benchmark for function-level Python code generation, comprising 164 problems with handwritten test suites. EvalPlus [Liu et al., 2023] extends HumanEval with augmented tests that reveal additional failures missed by the original test suite. Code Llama [Rozière et al., 2023] is the model family we evaluate, with 7B, 13B, and 34B parameter variants trained on code-heavy corpora. Rozière et al. report that smaller models exhibit higher syntax error rates — consistent with our finding that CodeLlama-7B's failure distribution is 97.5% syntax-dominated.

**Limitation we address.** Existing evaluations report aggregate pass@k without decomposing failures by type. Our FMD pipeline provides this decomposition: syntax (ast.parse failure), type (mypy type error), and functional/arithmetic (test failure with Z3 eligibility) strata. This decomposition is the prerequisite for failure-mode-conditioned repair — no prior work provides it for CodeLlama-7B on HumanEval.

## Formal Method Complementarity in Ensemble Systems

The concept of error complementarity — where different methods fix distinct, non-overlapping failure subsets — has been explored in the software testing literature (mutation testing, fault localization). In LLM code generation, diversity-based ensemble approaches (voting, resampling) improve pass@k by exploiting output diversity. Our work asks a different question: do formal repair methods operating on distinct signal channels (syntax, types, constraints) exhibit measurable complementarity on their *failure transition sets*? We formalize this via C_score — the Jaccard overlap between F_A→✓ and F_B→✓ compared against the independence expectation — providing a statistical test for failure set orthogonality.

## Summary and Positioning

Our contribution is orthogonal to prior repair work: we provide the empirical framework for determining which formal repair channels can activate for a given model-benchmark pair before applying them. Where prior work asks "how much does method X improve pass@k?", we ask "does method X's feedback signal exist in this setting?" The answer — empirically measured — determines which repair methods are worth applying and in what order. This positions our work as providing methodological infrastructure for the broader formal repair research program.
