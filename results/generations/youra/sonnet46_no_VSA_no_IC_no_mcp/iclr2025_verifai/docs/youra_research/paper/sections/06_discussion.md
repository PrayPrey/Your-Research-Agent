# Discussion

## Key Findings and Implications

### mypy Augmentation Provides Substantial but Mechanism-Agnostic Benefit

Our primary finding is a +8.94pp pass@1 improvement from adding mypy to
execution-based repair loops on HumanEval+ (GPT-4o-mini, k=5, three seeds
consistent). This is substantial for a one-subprocess-call intervention —
practitioners can deploy it today by adding a single mypy invocation to an
existing repair loop.

But the mechanism is not what we expected. The type-specificity hypothesis —
that mypy helps specifically for type-error problems by providing type-targeted
correction signal — is not supported. Both conditions achieve identical 90.9%
repair rates on type-error problems (h-m2, n=22, differential=0.000). The
improvement must come from a different channel. The most parsimonious
interpretation is *general diagnostic context enrichment*: mypy output, even
when it signals no errors, adds structured text to the repair prompt that
activates GPT-4o-mini's latent knowledge about Python error patterns,
improving repair quality across problem types. This is consistent with
the general prompt-enrichment hypothesis from h-m2's EXPLORE route analysis.

The implication for practitioners is that mypy's value in repair loops is
not primarily as a type-checker — it is as a structured diagnostic narrator.
This suggests that other structured diagnostic channels (linters like flake8,
import checkers, semantic analyzers) might provide similar general enrichment
benefits, independent of whether they target the specific failure mode.

### Benchmark-Level Signal Divergence Changes the Applicability Picture

The 70% vs 0% mypy error rate between HumanEval+ and MBPP+ is a new empirical
finding about these benchmarks' failure mode structures. HumanEval+ failures
are dominated by undefined-name errors — GPT-4o-mini hallucinating function
or variable references — while MBPP+ failures appear to be pure algorithmic
correctness errors (off-by-one, wrong formula) invisible to mypy.

This divergence has a practical prediction: mypy-augmented repair will
provide substantial benefit on HumanEval+-style problems (complex function
signatures, library references) but not on MBPP+-style problems (simple
algorithmic manipulation). A practitioner selecting a repair feedback strategy
for a new benchmark should first profile the mypy error rate in failing
solutions — if it is low (<10%), mypy feedback will not activate frequently
enough to drive improvement.

### Z3 Counterexample Feedback: Sound Architecture, Insufficient Activation

The Z3 sub-hypothesis (h-z1) produced a null result (−0.9pp), but its failure
mode is informative. The spec generation pipeline achieves 91.1% validity —
LLM-generated Z3 specifications are mostly correct on arithmetic HumanEval+
problems. The bottleneck is counterexample activation: only 16.1% of problems
receive a counterexample. For the remaining 83.9%, Condition C and Condition B
are identical. Given an already-high base pass@1 of 86.6%, the arithmetic
implies a theoretical maximum gain of ~2.2pp even under ideal Z3 guidance,
making the null result expected rather than surprising.

The implication is not that Z3 feedback cannot help LLM repair — it is that
the current setup applies Z3 to the wrong problems. Z3 counterexamples would
be most valuable on problems where (a) the base pass@1 is well below the
ceiling (<60%), leaving genuine headroom, and (b) the problem structure
produces specific, actionable counterexamples. LiveCodeBench or competitive
programming problems may be better candidates.

## Limitations

**L1: MBPP+ pass@1 comparison not completed.** All quantitative pass@1 claims
(+8.94pp) are HumanEval+-specific. The h-m3 MBPP+ experiment was started
(122/378 tasks of seed=42 Condition A) but not completed due to compute
constraints. Given the 0% mypy error rate on MBPP+ (h-e1, h-m1), Condition B
is unlikely to show improvement on MBPP+ — but this remains unconfirmed.
We restrict all pass@1 claims to HumanEval+ and note that the mypy signal
mechanism does not activate on MBPP+ under current conditions.

**L2: Type-specificity mechanism alternative unverified.** We propose general
context enrichment as the mechanism driving the +8.94pp improvement, but the
ablation study needed to confirm it (Condition B-Null: same prompt length as B
but with generic filler text instead of mypy output) was not executed. Without
this ablation, we cannot distinguish between mypy *content* (structured error
information) and mypy *length* (extra tokens) as the active ingredient.
Confirming this distinction is the highest-priority future experiment, as it
changes the theoretical contribution: if content-specific, mypy provides
diagnostic signal; if length-driven, any structured context would suffice.

**L3: Single model, single framework.** All experiments use GPT-4o-mini.
The repair benefit may be model-capability-dependent: weaker models may
fail to parse mypy output; stronger models (GPT-4o, Claude) may already
achieve near-ceiling on execution-only repair, leaving less headroom for
mypy to help. Replication with at least one open-source code model
(e.g., DeepSeek-Coder) is straightforward future work.

**L4: Z3 feedback at high base pass@1.** The arithmetic subset experiment
was conducted at base pass@1\_B = 86.6%, leaving 13.4% headroom. The null
result may not generalize to settings with lower base pass@1 where Z3
counterexamples have more room to guide repair.

## Broader Impact

This work establishes that adding mypy to LLM repair loops provides
substantial, reproducible improvement in Python code generation quality.
Practical deployment is low-cost (one subprocess call per repair round,
~30ms latency). The finding that the improvement is not type-specific
suggests that other structured feedback channels (linters, semantic analyzers)
deserve controlled experimental evaluation rather than being bundled with
execution feedback and assumed beneficial.

The Z3 pipeline contribution — 91.1% valid Z3 specs for arithmetic Python
problems using LLM generation — establishes feasibility for automated formal
specification generation, a building block for future work on formal
verification of LLM-generated code.

We do not foresee significant negative impacts: the work improves software
quality through better automated repair. Automated code generation systems
that this work could improve carry their own ethical considerations (job
displacement, generated code quality, security), but these are not amplified
by mypy augmentation specifically.
