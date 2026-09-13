## 6. Discussion

### 6.1 What the Results Mean

**Repair is bounded by signal extraction, not information transfer.** The cleanest account of the inverse correlation is that a model repairing its own code has to identify one edit, and the feedback's job is to make that edit obvious rather than to be complete. A traceback that says a NameError occurred at line 5 has done the job in twelve words. Pyright's diagnostic tree contains the same fact somewhere, along with forty others, and locating it is now the model's problem. Information content went up and extractable signal went down. If this is right, the productive engineering target is the feedback presentation layer rather than the verifier's rigor — and that layer is currently the least examined part of every repair loop we know of, ours included.

**The correctness-optimal and efficiency-optimal verifiers are different tools.** Execution monitoring wins on Δpass@1 by 2×; static analysis wins on correctness-per-second by 16×. Neither number is more real than the other, and the choice between them is a deployment question rather than a ranking. A batch pipeline with slack latency should use execution monitoring. An interactive assistant that must return in tens of milliseconds should use static analysis and accept the lower hit rate. The field's habit of reporting correctness without cost has made this a question nobody had the numbers to ask.

**There is a model-tier floor for SMT-integrated repair.** GPT-4o-mini's 6.3% constraint-extraction rate is not a tuning problem. Translating an informal docstring into Z3 constraints is a formal reasoning task that this tier of model does not perform reliably, and a repair pipeline that depends on it will fail on 19 of every 20 problems before the solver runs. Anyone planning such a stage should budget for a stronger extractor or a formally specified benchmark.

### 6.2 Limitations

**The overhead measurements come from a calibrated mock run.** An API key was unavailable when the efficiency experiment executed, so overhead was drawn from log-normal distributions parameterized by empirical priors measured in our specificity experiment and by published tool profiles (Pyright 100-300ms per call, subprocess execution 50-200ms). The ordering static < type < execution < SMT is robust across any realistic parameterization and agrees with the direct measurements we do have. The absolute ratios — 6.64 and 0.41 — should be read as calibrated estimates, and a live run is a straightforward replication we have not yet performed. We would not claim the specific magnitudes in a deployment recommendation; we would claim the ordering.

**Character count conflates precision with verbosity.** This is the most consequential limitation. Pyright's 24,358 characters are not 24,358 characters of insight about the failing test — they are a JSON serialization that includes unused-import notices and style warnings. Our ρ = -1.0 may therefore reflect a format effect rather than a genuine relationship between formal precision and repair utility, and we cannot separate the two with this design. The practical finding survives regardless: injecting raw Pyright JSON into a repair prompt reduces repair effectiveness in this setup, whatever the mechanism. The theoretical claim — that specificity itself is counterproductive — does not survive without the experiment in Section 7.1.

**Truncation may be doing the work.** Four thousand characters of Pyright's output reaches the model and roughly twenty thousand do not. A naive prefix cut can discard the decisive diagnostic. We cannot currently distinguish "verbose feedback is hard to use" from "we cut off the useful part," and these have different fixes.

**Z3's position is probably partly artifactual.** Z3 tops the repair ranking on a set where it produced real constraints for 8 of 126 problems and a fallback string otherwise. Those 8 may be structurally simpler, which would inflate its rate for reasons unrelated to feedback quality. We report Z3's rank because removing it does not change the inverse relationship among the remaining three, but we do not lean on it.

**One backbone.** Everything here is conditional on GPT-4o-mini's context-parsing capacity. A model that parses structured JSON well might extract Pyright's decisive diagnostic reliably and reverse the sign, which would invert our practical recommendation rather than merely weaken it. We chose this tier for cost and because it is widely deployed, not because it is representative — and we have no evidence that it is.

**The repair results are effectively HumanEval-only.** MBPP's uniform 0% floor means the ordering in Section 5.4 rests on 46 HumanEval failures. The confidence intervals overlap, and no pairwise gap is individually significant; what carries the finding is the perfect monotonicity across four categories and its persistence under stratification, not the size of any one difference.

### 6.3 Impact Statement

This work aims to make verifier selection in LLM repair pipelines an empirical decision rather than an intuitive one, and its immediate effect should be to reduce wasted computation — teams currently paying an order of magnitude in latency for verbose feedback their model cannot exploit have a reason to reconsider.

Two risks deserve naming. Our efficiency framing could encourage optimizing for correctness-per-second in settings where absolute correctness is what matters; in safety-relevant code, the 22-point improvement from execution monitoring is worth its 800 milliseconds and the ratio is the wrong metric to optimize. And our results are conditional on one model tier, so treating "avoid verbose static analysis feedback" as a general rule would overextend them — the mechanism we propose predicts the effect should weaken or reverse as models get better at parsing structured text.

More broadly, better automated repair makes it easier to produce plausible code without understanding it, which is a general property of code-generation tooling rather than a specific consequence of this work. The mitigation is unchanged: repair loops verified against real test suites, as ours are, produce code that passes tests, which is a weaker guarantee than correctness and should be described as such.

### 6.4 What We Would Deploy

Use execution monitoring when correctness per attempt is the binding constraint and latency is not. Use static analysis when throughput or interactive latency binds — accepting roughly half the correctness gain for roughly a seventeenth of the cost. Do not inject raw Pyright JSON; summarize it first, and see Section 7 for the experiment that would tell you how much that helps. Do not build an SMT stage on a GPT-4o-mini-class extractor. And if your problems look like MBPP rather than HumanEval, put the full problem specification in the repair prompt before you spend any effort choosing between verifiers — at that point the verifier is not what is limiting you.
