# Introduction

We set out to test whether adding mypy type checking to LLM repair loops
improves pass@1 on Python code generation benchmarks. The answer is yes —
by nearly 9 percentage points. But the mechanism we hypothesized turned out
to be wrong.

Large language models can repair their own code when given execution feedback:
run the generated solution, capture the output or exception, and feed it back
to the model for correction. This *repair loop* paradigm, exemplified by
Self-Debug [Chen et al., 2023] and Reflexion [Shinn et al., 2023], has become
a standard technique for improving pass@k on benchmarks like HumanEval and
MBPP. The dominant feedback signal is execution output — a binary pass/fail
plus stderr. The intuition is that more *specific* feedback should produce
better repairs: if the model knows not just *that* it failed but *why* (a
type error at line 5 with expected type `int`, received `str`), it should
correct the error more reliably. Static analysis tools like mypy generate
exactly this kind of structured, type-level diagnostic. Yet no controlled
study has measured whether adding mypy to a repair loop produces measurable
improvement over execution-only feedback.

The gap matters for a practical reason: execution feedback is cheap but
coarse. mypy feedback is almost equally cheap (a subprocess call, ~30ms) but
structured — it provides error category, file location, and error message.
If this structure translates into better repairs, the improvement is available
to any practitioner today, requiring only a one-line addition to an existing
repair loop. But without controlled evidence, we cannot answer: how much does
it help, when does it help, and — critically — *why* does it help?

We conducted a five-sub-hypothesis controlled experiment to answer these
questions. The experiment proceeds as a causal chain: we first verify that
mypy produces actionable signal on our target benchmarks (h-e1), then verify
the signal is consumed by the LLM (h-m1), then test whether the improvement is
concentrated on type-error problems (h-m2), then measure the overall pass@1
improvement (h-m3), and finally test whether a formal verification extension
(Z3 counterexample feedback) provides additional benefit (h-z1).

The results surprised us. On HumanEval+ (164 problems, GPT-4o-mini, k=5
repair rounds, 3 seeds), execution+mypy repair achieves **87.20% pass@1**
versus **78.25%** for execution-only repair — a **+8.94 percentage point**
improvement, consistent across all three seeds. mypy errors are eliminated
within a single repair round (mean errors: 1.55 → 0.00 by round 2; Spearman
ρ = −0.707). So far, the story fits the intuition.

But the mechanism does not. We pre-registered a sub-hypothesis (h-m2) that
the improvement would be concentrated on type-error problems — the problems
where mypy provides its diagnostic signal. It is not. Under k=5 repair rounds,
type-error problems achieve **90.9% repair rate under both conditions**
(differential = 0.000). The improvement exists uniformly across problem types.
The most parsimonious explanation is *general diagnostic context enrichment*:
mypy output, regardless of whether it signals a type error, augments the
repair prompt with structured text that improves GPT-4o-mini's repair quality.

A second surprise: mypy error rates differ dramatically between HumanEval+
(70% of failing solutions have mypy errors) and MBPP+ (0%). This benchmark
divergence predicts where static analysis feedback will and will not help,
providing a practical guideline for practitioners. The Z3 formal verification
extension (h-z1) shows null improvement (−0.9pp) on an arithmetic subset,
constrained by low counterexample activation (16.1%) and ceiling effects.

This paper makes the following contributions:

1. **First controlled empirical comparison** of execution+mypy repair versus
   execution-only repair on HumanEval+ (GPT-4o-mini, k=5, three seeds),
   showing a consistent +8.94pp pass@1 improvement — the first published
   evidence for the marginal contribution of static analysis feedback over
   execution feedback alone in a repair loop.

2. **Type-specificity refutation**: a pre-registered sub-hypothesis test
   establishing that the improvement is *not* concentrated on type-error
   problems (identical 90.9% repair rates under both conditions at k=5),
   motivating the general context enrichment interpretation.

3. **Benchmark-level mypy signal characterization**: HumanEval+ and MBPP+
   have fundamentally different mypy error profiles (70% vs 0%), a structural
   difference that predicts where static analysis feedback will activate.

4. **Z3 spec validation pipeline** achieving 91.1% spec validity rate on
   arithmetic HumanEval+ problems, establishing feasibility for future formal
   verification work while identifying the ceiling effects that currently
   limit its repair-loop utility.

We organize the paper as follows. Section 2 reviews related work on LLM repair
loops and static analysis feedback, positioning our controlled comparison
against prior work that bundles but does not ablate feedback channel types.
Section 3 describes our experimental methodology and the five-sub-hypothesis
causal chain. Section 4 details the experimental setup. Section 5 presents
results across all sub-hypotheses. Section 6 discusses the mechanistic
implications, limitations, and benchmark-level boundary conditions. Section 7
concludes with future work directions.
