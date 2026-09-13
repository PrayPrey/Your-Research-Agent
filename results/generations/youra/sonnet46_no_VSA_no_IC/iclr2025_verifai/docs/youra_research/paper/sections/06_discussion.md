# 6. Discussion

## 6.1 Key Findings

**The EvalPlus failure set is a reproducible foundation for repair research.** The
h-e1-v2 PASS result establishes something that prior repair work has not explicitly
verified: the failure set from a LLM evaluation run is fully recoverable from archive,
with stored incorrect outputs, API accessibility, and deterministic test selection all
confirmed. This is not a trivial infrastructure finding. Many repair papers report
results on corpora that are not reproducible — bug datasets that have evolved, model
outputs that were not archived, or evaluation environments that changed. Our 4-condition
verification protocol provides a reusable template for establishing reproducibility
before executing expensive repair experiments.

**Static analysis is the wrong oracle for EvalPlus semantic failures.** The 16-32%
SA fire rate across benchmark types is a decisive empirical result. It means that
two-thirds to five-sixths of EvalPlus failures are opaque to the standard repair
pipeline: no lint warning, no type error, no actionable static feedback. Any repair
system that routes these failures to a SA-based oracle is operating blind on the
majority of its input. Specification-aligned repair — providing the model with intent,
behavioral gap, and deviation — is not an optional enhancement; it is the minimum
viable oracle for this failure population.

**The h-e1 → h-e1-v2 trajectory illustrates hypothesis refinement in practice.** The
h-e1 gate failed because it targeted `plus_fail_tests` completeness, which has a
4.5% gap. h-e1-v2 redesigned the verification to target `solutions_cache.jsonl`
coverage, which is 134/134 complete. This is not a goal-post move: `solutions_cache.jsonl`
is the correct data source for Condition B/C prompt construction (the stored incorrect
outputs are the actual model outputs needed for deviation detection). The trajectory
demonstrates that existence verification failures should prompt verification target
redesign, not hypothesis abandonment.

## 6.2 Limitations

**Mechanism experiments not yet executed.** The primary scientific contribution —
demonstrating that specification-aligned repair outperforms blind reprompting — is a
pre-registered prediction, not a measured result. P1, P2, and P3 are all
INCONCLUSIVE. We establish the data infrastructure and pre-register the design in
this paper; the comparative results are the subject of the companion mechanism
experiments (h-m1, h-m2, h-c1). We make no empirical claim about the effectiveness
of the specification triple beyond its design motivation from prior literature.

**6-task exclusion (n=128, not n=134).** The 128-task working set excludes 6 tasks
with empty `plus_fail_tests` in the archive. This 4.5% exclusion does not materially
affect statistical power (McNemar power remains ≥ 80% at expected fix rate range).
The exclusion is principled — these tasks cannot have Condition C prompts constructed
from archived data — and documented in full (specific task IDs listed).

**Single model, single temperature.** All experiments use GPT-4o-mini at temperature
=0.2, seed=42. Assumption A1 (GPT-4o-mini can leverage structured specification
context) is unverified until h-m1 executes. If A1 is violated (C ≈ B), the correct
response is to test stronger models (GPT-4o, Claude 3.5 Sonnet) before concluding
that specification-aligned repair is ineffective — not to conclude that the approach
fails generally. Generalization across models and temperatures is a direction for
future work.

**Component ablation deferred.** The specification triple is evaluated as an
integrated oracle. The relative contribution of each component — docstring,
I/O pair, actual output — cannot be determined from the 3-condition design.
Full component ablation requires 7 additional conditions (all combinations of
the three components). We defer this to future work; the primary claim concerns
the integrated triple.

## 6.3 Broader Impact

This work advances the empirical methodology for LLM code repair evaluation in two
ways. First, the 4-condition existence verification protocol demonstrates how to
establish reproducibility of a LLM failure set before executing expensive repair
experiments. This reduces the risk of running comparisons on non-reproducible data.
Second, the pre-registration of P1/P2/P3 before mechanism experiment execution
prevents hypothesis drift — the predictions are on record before data collection.

The approach carries no apparent negative societal impact. Improved LLM code repair
reduces programming errors, which is broadly beneficial. The method's reliance on
structured specification context encourages better problem documentation practices
(clear docstrings, comprehensive tests) as a byproduct of repair oracle construction.
