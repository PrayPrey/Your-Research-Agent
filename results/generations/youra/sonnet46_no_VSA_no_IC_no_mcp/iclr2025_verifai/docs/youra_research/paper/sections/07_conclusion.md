# Conclusion

We set out to test whether adding mypy to LLM repair loops improves pass@1.
It does — by nearly 9 percentage points, consistently across three seeds. We
also set out to understand why. The answer surprised us: the improvement is
not where we expected it.

The type-specificity mechanism we hypothesized — mypy identifies a type error,
tells the LLM exactly what went wrong, the LLM corrects it specifically —
turns out not to be the active channel at k=5 saturation. Both execution-only
and execution+mypy repair achieve identical 90.9% repair rates on type-error
problems. The +8.94pp overall improvement arises elsewhere, most plausibly
from general diagnostic context enrichment: mypy output adds structured text
to repair prompts that improves GPT-4o-mini's repair quality across all
problem types, regardless of whether the problem involves a type error.

## Summary

In this work, we conducted the first controlled experiment isolating the
marginal contribution of mypy static analysis feedback over execution-only
feedback in an LLM repair loop. Our contributions are:

1. **Controlled evidence for mypy's repair benefit:** On HumanEval+ (164
   problems, GPT-4o-mini, k=5, three seeds), execution+mypy repair achieves
   87.20% pass@1 versus 78.25% for execution-only — a consistent +8.94pp
   improvement across seeds 42 (+6.7pp), 123 (+11.0pp), and 456 (+9.2pp).

2. **Type-specificity refutation:** A pre-registered sub-hypothesis test
   establishes that the improvement is not concentrated on type-error problems
   (differential = 0.000, n=22 type-error problems under k=5). The intuitive
   mechanism is falsified; general context enrichment is the more parsimonious
   explanation.

3. **Benchmark-level mypy signal characterization:** HumanEval+ failing
   solutions contain mypy errors at 70%; MBPP+ failing solutions at 0%. This
   structural divergence predicts where static analysis feedback will activate
   and provides a practical guideline for feedback channel selection.

4. **Z3 spec generation pipeline:** LLM-generated Z3 specifications achieve
   91.1% validity on arithmetic HumanEval+ problems, establishing feasibility
   for automated formal specification generation, while finding that
   counterexample activation rate (16.1%) and ceiling effects currently limit
   the repair-loop benefit.

## Future Directions

**Mechanism isolation (highest priority):** The distinction between mypy
*content* (structured error information) and mypy *prompt length* (extra
tokens) as the active ingredient remains unresolved. A Condition B-Null
ablation — same prompt length as Condition B, but with generic filler text
instead of mypy output — would directly test whether the benefit is
content-specific or length-driven. This result would change the theoretical
contribution substantially.

**Early-round type-specificity:** h-m2 reported aggregate k=5 results; the
type-specificity differential at k=1..2 (before ceiling saturation) was not
extracted. Re-analysis of existing h-m2 data at earlier rounds would
determine whether type-targeted benefit exists at early rounds but washes
out — rehabilitating the original mechanism hypothesis for the early-repair
regime.

**Multi-model replication:** All experiments use GPT-4o-mini. Replication with
GPT-4o, Claude, and open-source code models (DeepSeek-Coder, CodeLlama) would
establish whether the +8.94pp improvement is robust across model capability
levels or specific to GPT-4o-mini's capacity to parse mypy output.

**Harder problems for Z3:** The 91.1% Z3 spec validity pipeline is ready for
deployment on harder benchmarks (LiveCodeBench, competitive programming) where
base pass@1 is well below the 86.6% ceiling encountered here. Harder problems
provide more headroom for counterexample-guided repair to demonstrate benefit.

## Closing

We began by asking whether adding mypy to LLM repair loops was worth the
one-subprocess-call investment. The answer is yes — substantially so. But the
research question that emerged from our controlled experiment is more
interesting: *why* does mypy help, and *where* does its benefit concentrate?
The gap between our predicted mechanism (type-targeted) and the observed
mechanism (general enrichment) opens a research agenda about feedback channel
informativeness that is richer than the original "does it help?" question.
Understanding what makes a feedback signal distinctive from execution output —
whether it is error specificity, structured format, prompt enrichment, or
something else — is the key to principled design of LLM repair loop
architectures.
