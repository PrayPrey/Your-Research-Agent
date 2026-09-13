# 7. Conclusion

We opened by observing that static analysis tools catch fewer than one in three of the
code generation failures that stump GPT-4o-mini on EvalPlus. We close by having done
two things about it: diagnosed why the standard repair pipeline fails on these
semantically opaque errors, and built the reproducible data infrastructure needed to
test the alternative.

The alternative is specification-aligned repair — providing the model with a structured
triple of (docstring formal intent, failing test I/O pair, actual model output) as a
repair oracle. In this work, we established and verified the data infrastructure for
testing this approach: 134 EvalPlus failure IDs confirmed, 134/134 stored GPT-4o-mini
incorrect solutions verified in `solutions_cache.jsonl`, the EvalPlus API accessible
for all 134 task IDs, and deterministic test selection confirmed via `plus_input[0]`.
Six tasks with empty `plus_fail_tests` fields define a 128-task working set adequate
for mechanism experiments. All four existence conditions pass; 5/5 pytest tests pass
in 2.32 seconds.

We pre-register three comparative predictions for the mechanism experiments:
(P1) specification-aligned repair significantly outperforms blind reprompting
(McNemar p < 0.05); (P2) it significantly outperforms the round-0 baseline with fix
rate ≥ 15%; (P3) HumanEval+ fix rate exceeds MBPP+ fix rate (directional, exploratory).
These predictions are on record before data collection.

## 7.1 Future Directions

**From untested alternative explanations.** If P1 holds, the next question is which
component of the triple is doing the work. Docstring re-anchoring, I/O counterexample,
and actual output deviation detection are three distinct mechanisms — each can be
ablated by removing the corresponding component from Condition C. This 7-condition
ablation experiment is the natural follow-up for understanding the repair mechanism
rather than just the repair result.

**From unverified assumptions.** Assumption A1 (GPT-4o-mini can leverage structured
specification context) is the core empirical question. If h-m1 shows C ≈ B, the
correct response is not to abandon specification-aligned repair but to test it with
models capable of stronger counterexample reasoning: GPT-4o, Claude 3.5 Sonnet,
or open-source instruction-tuned models. The infrastructure established here is
model-agnostic.

**From scope extension.** Three extensions are immediately tractable: recovering the
6 excluded tasks via fresh EvalPlus API evaluation (~1 hour of engineering effort,
confirmed feasible by h-e1-v2 C3 PASS), extending to multi-round repair with updated
specification context per round (each repair attempt yields a new actual output for
the next iteration), and testing on LiveCodeBench to evaluate contamination effects
on the fix rate.

The path from a failing SA oracle to a working specification-aligned repair system
is now fully mapped. What remains is execution.
