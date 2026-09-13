# Phase 2A Discussion Log

## Metadata
- **Workflow:** phase2a-dialogue
- **Architecture:** Self-Play Loop (Claude-only, IC-ablation)
- **Gap ID:** gap3
- **Gap Title:** Systematic Ranking of Formal Feedback Signal Types on Standard Code Benchmarks
- **Execution Mode:** UNATTENDED
- **Date:** 2026-08-05
- **MIN_EXCHANGES:** 15 | **MAX_EXCHANGES:** 20

---

## Briefing: Selected Research Gap

**Gap 3 — Systematic Ranking of Formal Feedback Signal Types on Standard Code Benchmarks**

**Priority:** HIGH + PRIMARY | **Connection:** Directly addresses Q1 of detailed questions (which feedback type gives largest marginal improvement in pass@1 and pass@k on HumanEval/MBPP)

**Current State:** Three feedback signal categories exist in isolation:
1. Execution feedback (CodeRL, RLEF, Self-Debugging, Reflexion, FeedbackEval) — dominant in literature; best result: 91% HumanEval (Reflexion)
2. Static analysis feedback (pylint, bandit, mypy) — Blyth et al. 2025 tested on PythonSecurityEval ONLY; NOT on HumanEval/MBPP functional correctness
3. Type/grammar constraints (Mündler et al. 2025, CRANE, SynCode) — tested on HumanEval/MBPP but in constrained decoding mode, not iterative repair; no comparison to execution feedback

**Missing Piece:** Head-to-head comparison of (a) execution test feedback, (b) pylint/mypy static analysis, (c) type-constrained decoding — all on same LLMs, same benchmarks (HumanEval, MBPP), measuring pass@1 delta vs. no-feedback baseline at equal inference compute.

**Supporting Papers:**
- P1: FeedbackEval (Dai et al., 2025) — 2504.06939 — closest existing comparison but missing pylint/mypy and type-constrained decoding
- P2: Type-Constrained Code Generation (Mündler et al., 2025) — 2504.09246 — type constraint condition; no comparison to other feedback types
- P3: Static Analysis as Feedback Loop (Blyth et al., 2025) — 2508.14419 — pylint/bandit condition; PythonSecurityEval only
- P4: Self-Debug (Chen et al., 2023) — 2304.05128 — execution trace; +12% MBPP; key execution baseline
- P5: Reflexion (Shinn et al., 2023) — 2303.11366 — execution+verbal; 91% HumanEval upper bound

**Implementation Resources:**
- SYSUSELab/FeedbackEval (multi-feedback type framework; extendable)
- eth-sri/type-constrained-code-generation (type constraint implementation)
- cyb3rlab/CodeEnhancer (SAST + LLM pipeline)
- structuredllm/syncode (grammar-constrained decoding)

**Feasibility Constraints (Mandatory):**
- REJECT: new benchmarks, rubrics, or scoring frameworks
- REJECT: synthetic/generated data; human evaluation or annotation
- ACCEPT: hypotheses testable immediately on HumanEval, MBPP using existing infrastructure

---

## Previous Failure / Routing Context

*First Phase 2A execution — no failure history. No Serena memory files found.*

---


## Discussion Transcript

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What a delicious gap! The literature has been treating feedback types as if they live in separate universes — execution feedback folk over here, static analysis folk over there, type-constraint people doing their own thing. But nobody has put them in the same ring and said: *fight*. At equal inference compute, at the same benchmarks, on the same models, which signal actually wins?

Here's what I find genuinely exciting: FeedbackEval [Dai et al., 2025] came close — they systematically compared compiler feedback, test feedback, and minimal feedback on HumanEval. But they stopped short. They used "compiler" feedback (syntax errors only) rather than *semantic* static analysis from pylint/mypy, and they didn't include type-constrained decoding at all. Mündler et al. [2025] show type-constrained decoding cuts compilation errors by >50% on HumanEval/MBPP — but their only comparison is unconstrained generation. Blyth et al. [2025] run pylint/bandit for 10 iterations on security code and get security vulnerabilities from 40% down to 13% — but never touch HumanEval/MBPP functional correctness.

What if the different signals are actually complementary rather than competing? Imagine this: type constraints prevent the generation of syntactically/type-invalid code upfront (zero execution cost!), pylint catches style and common semantic errors without running code, and execution test feedback catches the remaining logic errors. The question isn't just *which wins* — it's whether they compose additively or exhibit diminishing returns when stacked.

I want to propose we explore a hypothesis around **signal hierarchy**: execution feedback is the ceiling signal (requires running code), static analysis is the mid-tier (requires parsing only), and type constraints are the floor (imposed at decoding time). Testing whether these three form a cost-benefit hierarchy — more informative = more expensive — could be the unifying insight.

**Key Points:**
- The literature has all three feedback types but no iso-compute head-to-head
- FeedbackEval is the nearest comparison but missing pylint/mypy semantic analysis and type-constrained decoding
- Opportunity: test a cost-informativeness hierarchy (type constraints < static analysis < execution)
- Composition question: do signals stack additively, or does execution dominate completely?

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises the right question but I need to push back on the framing before we commit to it. The "signal hierarchy" idea is elegant, but it risks being unfalsifiable as stated. "More informative = more expensive" is a claim that needs operationalization. What is "informativeness" here — mutual information with pass@1? Bits of error signal per token? If we can't measure it independently, we can't test whether hierarchy explains the ranking.

Let me be precise about what *can* be cleanly tested, drawing on [Dai et al., 2025]. FeedbackEval's Repair@k metric is the right measurement unit. The cleaner experiment is **an ablation table**: each signal alone (against no-feedback baseline) on HumanEval and MBPP at fixed total token budget.

The key falsifiable prediction from an additive composition hypothesis would be: the combined signal condition achieves statistically significantly higher pass@1 than any individual signal. If execution feedback alone already saturates the improvement (approaches Reflexion's 91% on HumanEval), combination doesn't add value, and the hypothesis is refuted. That's a testable null.

I'm also worried about Dr. Nova's framing of "type constraints at decoding time vs. repair mode." Type-constrained decoding (Mündler et al.) is fundamentally different from iterative repair: it prevents errors during generation, while repair corrects errors after. Comparing these at "equal compute" is non-trivial — you need to define the compute budget in tokens, not in repair rounds.

**Key Points:**
- "Signal hierarchy" needs operationalization to be falsifiable
- Cleanest design: ablation table at fixed token budget per condition
- Prediction for composition test: combined > individual signals (falsifiable)
- Type-constrained decoding vs. iterative repair need careful compute-budget equalization

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Both perspectives have merit, but let me ask the field-impact question: *who cares, and why now?*

The significance of this gap is not merely taxonomic. In 2025-2026, production coding assistants must make real-time decisions about which feedback signals to invoke. Running a test suite takes 0.5-5 seconds per attempt; calling pylint takes milliseconds. If the paper establishes that static analysis feedback achieves 70% of execution feedback's improvement at 10% of the compute cost, that's an immediately deployable finding.

The reason *now* matters: Self-Debug [Chen et al., 2023] showed +12% MBPP, Reflexion [Shinn et al., 2023] achieved 91% HumanEval — those were 2023 results on GPT-3.5/GPT-4. The Iterative Self-Repair paper (2026) shows modern 8B models can do repair successfully. But we still have no study using 2025-era open-source models (Llama 3, Qwen 2.5) to compare all three signal types on the same benchmark.

The significance claim: if execution feedback is the default recommendation and we never tested alternatives, we may be spending 100x the compute for a marginal gain over well-deployed static analysis. This paper's value is in *preventing wasted inference compute at scale*.

**Key Points:**
- Practical significance: production systems must choose feedback signals under compute constraints
- Modern 2025-era open-source models not yet tested in tri-way feedback comparison
- The finding "static analysis achieves X% of execution feedback's improvement at Y% compute cost" is immediately deployable
- Most impactful result: the cross-over point where static analysis saturates

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me ground this in what's technically possible before we get carried away.

The conceptual cleanness of the ablation table runs into a genuine technical challenge: type-constrained decoding (Mündler et al., 2025) and iterative repair feedback loops are *mechanistically incompatible* as direct comparison conditions. Type-constrained decoding modifies the decoding algorithm itself — it requires access to logits and vocabulary filtering at generation time. Iterative repair is a black-box outer loop over any generation API. You cannot run them at equal token budget in the same framework without significant engineering.

One approach: define compute budget as total output tokens per problem (summed across all repair rounds). For type-constrained decoding, this is one pass. For iterative repair, this is up to N passes. This is measurable and gives a fair comparison.

Feasibility assessment:
- Pylint/mypy static analysis feedback: HIGH feasibility (no sandbox needed)
- Execution feedback: HIGH feasibility via Johin2/iterative-code-repair (sandboxed execution, already supports HumanEval/MBPP)
- Type-constrained decoding: MEDIUM feasibility — requires local GPU, open-source models only (eth-sri/type-constrained-code-generation)

**Key Points:**
- Type-constrained decoding requires local HuggingFace inference
- Compute normalization: total output tokens per problem is the right unit
- All three signal types are implementable with existing repos

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Excellent — we now have four perspectives converging. Let me synthesize and propose a concrete hypothesis:

> *Under the HumanEval and MBPP benchmarks, for open-source instruction-tuned LLMs (7B+), if formal feedback type is varied across (a) no feedback [baseline], (b) pylint/mypy static analysis feedback, (c) execution test feedback, and (d) type-constrained decoding, at iso-compute (fixed total output token budget per problem), then the ranking of pass@1 improvement delta will be: execution > static analysis > type-constrained > no-feedback, because each signal type captures a different subset of code errors with decreasing coverage completeness but increasing computational efficiency.*

This is testable: the ranking is the prediction. If static analysis improves pass@1 no more than type-constrained decoding, the intermediate tier collapses. If execution shows no significant advantage over static analysis, the dominant assumption is refuted.

Feasibility path: Johin2/iterative-code-repair for execution; cyb3rlab/CodeEnhancer for pylint; eth-sri for type-constrained decoding. HumanEval and MBPP are existing benchmarks. No new benchmarks, no human annotation.

**Key Points:**
- Core hypothesis: ranked delta comparison (execution > static analysis > type-constrained) at iso-compute
- Both primary ranking and null result are publishable
- Feasibility satisfied: HumanEval + MBPP + existing repos

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good synthesis from Dr. Ally, but I'm going to break this hypothesis before it leaves the room.

**Break point 1: The ranking prediction is directionally arbitrary.** "Execution > static analysis > type-constrained" is assumed based on intuitive error coverage, but there's no evidence that pylint/mypy semantic warnings actually improve *functional* pass@k on HumanEval/MBPP. HumanEval problems are algorithmic — they rarely fail because of PEP 8 violations or unused imports. Blyth et al. showed pylint reduces *security* issues, not functional correctness. On HumanEval, pylint feedback may have NEAR-ZERO effect on pass@1.

**Break point 2: Type-constrained decoding is a different mode, not just a weaker signal.** It doesn't *repair* — it *prevents*. Without knowing the error type distribution on HumanEval/MBPP, the ranking is underdetermined.

**Break point 3: "Iso-compute" is ill-defined for different architectural modes.** The comparison requires a specific operationalization that must be stated upfront.

Show me the evidence that pylint feedback improves functional correctness on HumanEval before committing to a ranking that includes it as a meaningful tier.

**Key Points:**
- Pylint/mypy feedback may have near-zero effect on HumanEval/MBPP functional correctness
- Type-constrained decoding is prevention-mode, not repair-mode — incomparable without error distribution data
- "Iso-compute" needs precise operationalization
- The ranking prediction could be empirically wrong

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex just sharpened the hypothesis significantly. His critique reveals something more interesting: we don't need the ranking to go the way we expect. The scientific value is in *knowing* the answer.

On **break point 1** (pylint near-zero effect on HumanEval): This is actually the most interesting empirical unknown! If pylint doesn't help functional correctness, that's a *publishable finding* — it tells the field that static analysis feedback's domain is code quality not functional correctness. We should formulate the hypothesis to *allow* for this: the null result for pylint is as valuable as the positive result.

On **break point 2** (error type distribution): Mündler et al. already tell us type-constrained decoding reduces compilation errors >50% on HumanEval, suggesting type constraints have limited benefit on logic-error problems. We can stratify results by failure type via automated tool analysis.

On **break point 3** (iso-compute ill-defined): Agreed — operationalize as total generation tokens: budget_k tokens per problem instance, any method uses them however it wants.

New stronger framing: the primary finding is the **error-type decomposition** — which feedback type reduces which *error category* most efficiently?

**Key Points:**
- A null result for pylint on HumanEval is publishable — defines the domain of static analysis feedback
- Error-type stratification can explain the ranking without pre-assuming it
- Compute operationalization: total generation tokens per problem instance (budget_k)
- Strongest framing: error-type decomposition as primary finding

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's pivot to error-type decomposition is scientifically sound. Let me separate what's testable.

**The core testable experiment** (no additional annotation):
1. Generate code for HumanEval (164 problems) and MBPP (374 problems) under each condition at fixed token budget B
2. Compute pass@1 delta vs. baseline for each condition
3. Test statistical significance (McNemar's test over 164/374 problems per model)

**The error-type decomposition** (automated analysis, no human annotation):
- For no-feedback baseline failures: run pylint, run mypy, run execution — classify each failure as syntax/type/logic/runtime by which tool detects an error. Automated via tool output.
- Then measure: does each feedback type preferentially fix the error category it was designed to catch?

Precise falsifiable predictions:
- **P1 (Primary):** At budget B=2000 output tokens per problem, execution feedback achieves statistically significantly higher pass@1 delta than pylint feedback (p<0.05, McNemar's test) on HumanEval with a 7B model
- **P2:** Pylint feedback achieves a statistically significant pass@1 delta over no-feedback baseline on HumanEval (or p>0.05 = pylint does NOT help functional correctness)
- **P3:** Error-type analysis shows type-constrained decoding reduces syntax/type error failures proportionally more than execution feedback

**Key Points:**
- Two-part experiment: pass@1 delta comparison + automated error-type decomposition
- Error classification automated via tool output — no human annotation required
- Three independently falsifiable predictions (P1, P2, P3)
- McNemar's test or bootstrap CI for statistical significance

---

### Exchange 9

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Vera has given us the experimental architecture. Let me assess significance for VerifAI reviewers.

The gap this paper closes has been open for 2+ years: every feedback type paper compares only against unconstrained generation, never against competing feedback types. FeedbackEval (2025) came closest but explicitly excluded semantic static analysis and type-constrained decoding.

*For workshop (VerifAI):* The contribution is the experimental finding + the iso-compute comparison methodology. Exactly VerifAI scope: LLMs for code verification.

*For future main venue:* Extend to larger models (70B), more benchmarks (SWE-bench), compute-efficiency Pareto curves.

Most impactful abstract claim: "We show that execution feedback achieves [X]pp improvement on HumanEval at fixed token budget, while pylint/mypy feedback achieves [Y]pp improvement — establishing the first cost-informativeness tradeoff curve for formal feedback signals in LLM code generation." Either result (Y≈X or Y<<X) is significant.

Recommendation: frame type-constrained decoding as "prevention baseline" separately from "repair feedback types" — don't force it into the same ranking as repair conditions. Keeps the main message clean.

**Key Points:**
- Contribution closes a 2-year gap — either outcome is publishable
- VerifAI scope: perfect fit
- Recommendation: type-constrained decoding as separate prevention baseline, not in main ranking

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Dr. Sage's prevention vs. repair distinction is technically critical. Let me amplify this.

**Bifurcated design:**
- **Primary comparison:** execution feedback vs. pylint/mypy static analysis feedback, in iterative repair mode, at fixed total output token budget. Both are repair modes. Apples-to-apples.
- **Secondary study:** type-constrained decoding as "prevention baseline" — one-pass generation with type constraints vs. one-pass unconstrained generation. Separate comparison, separate section.

This eliminates the architectural incompatibility problem. The primary comparison is mechanistically clean.

Feasibility of the bifurcated design:
- Johin2/iterative-code-repair: execution feedback condition — directly implemented for HumanEval/MBPP. HIGH feasibility.
- cyb3rlab/CodeEnhancer: SAST + LLM iterative loop — needs adaptation from security benchmark to HumanEval/MBPP functional correctness. MEDIUM feasibility. (The adaptation is a data loading and metric change, not an algorithm change.)
- eth-sri/type-constrained-code-generation: type-constrained prevention study. MEDIUM feasibility — requires local GPU inference.

**Key Points:**
- Bifurcate: (A) execution vs. pylint in repair mode (primary); (B) type-constrained vs. unconstrained one-pass (secondary)
- Primary comparison is apples-to-apples mechanistically
- Execution feedback: HIGH feasibility; pylint adaptation: MEDIUM; type-constrained: MEDIUM (local GPU)

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Pax's bifurcation and Dr. Sage's framing together make this publishable. Let me write the refined hypothesis:

**Refined Core Hypothesis:**

> *Under HumanEval and MBPP benchmarks, for open-source instruction-tuned LLMs of at least 7B parameters, if formal feedback type is varied between (A) pylint/mypy static analysis feedback and (B) execution test feedback — both in iterative repair mode at fixed token budget B — then execution test feedback achieves a statistically significantly larger pass@1 improvement delta over no-feedback baseline than pylint/mypy feedback, because execution feedback provides complete program semantics (observed actual output vs. expected output), whereas static analysis provides signals that may have lower correlation with logical correctness failures on HumanEval/MBPP problem types.*

**Novelty:** First iso-compute head-to-head of execution vs. static analysis feedback in iterative repair mode on standard functional correctness benchmarks. FeedbackEval [Dai et al., 2025] compared feedback types but used compiler errors (not semantic pylint/mypy) and did not normalize token budget.

**Null hypothesis:** H0: Δ_pylint = Δ_execution (directly testable; rejecting either direction is publishable).

**Secondary study:** type-constrained decoding vs. unconstrained one-pass generation (prevention baseline, separate from repair comparison).

**Key Points:**
- Refined hypothesis: execution > pylint in pass@1 delta at iso-compute on HumanEval/MBPP
- Mechanism: execution covers full error distribution; pylint covers subset (to be measured, not assumed)
- Null hypothesis is testable — rejecting either direction is publishable
- Primary (repair comparison) + secondary (prevention baseline) structure

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally's refinement is significantly stronger. Two remaining attacks:

**Attack 1: The mechanism claim is still empirically unjustified.** "Static analysis provides signals that may have lower correlation with logical correctness failures" — this is stated as the explanation, but it's stated as prior knowledge. Pylint reports undefined variables (NameError before execution), attribute access on wrong types, incorrect function signatures — these ARE logical errors. The mechanism claim needs to become a testable prediction, not an assumed explanation.

**Attack 2: The model selection is underspecified.** "At least 7B parameters" is vague. A 7B and a 70B model will respond very differently. Name specific models or explicitly scope to one.

**What would convince me:**
1. Restate the mechanism as H-M testable prediction: "pylint/mypy feedback will improve pass@1 by less than [threshold] pp, consistent with the hypothesis that style/syntax signals have low correlation with HumanEval logical failures" — with the measurement as automated pylint coverage of baseline failures
2. Specify at least two models explicitly (e.g., Llama 3.1 8B + one other)

**Key Points:**
- Mechanism must be testable prediction, not assumed explanation
- Pylint catches some logical errors — not purely style feedback
- Name specific models
- Both concerns are fixable without rejecting the hypothesis

---

### Exchange 13

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's attacks are exactly right. Final sharpening:

**On mechanism claim:** Make it a testable prediction: "the fraction of HumanEval/MBPP failures that pylint catches pre-execution is significantly lower than the fraction that execution test feedback catches." This is **measurable**: run pylint on baseline failures, count how many pylint would have flagged, compare to execution catch rate. Automated, no human annotation. The mechanism becomes the second major finding of the paper.

**On model selection:** Use **Llama 3.1 8B** (smallest practical 2024-era model; more room to improve from feedback, so effects are easier to detect) as primary, with spot-check replication on **Qwen2.5-Coder-7B** (strong code-specialized model, different training regime). Two data points at 7B scale from different families — sufficient for a workshop paper, honest about generalizability scope.

The paper now has two main contributions: (1) the pass@1 delta ranking at iso-compute; (2) the automated pylint coverage analysis explaining the ranking mechanism. Both are derived from existing benchmarks, existing tools, no human annotation.

**Key Points:**
- Mechanism: testable prediction via automated pylint coverage analysis on baseline failures
- Model selection: Llama 3.1 8B (primary) + Qwen2.5-Coder-7B (replication)
- Two main contributions: pass@1 ranking + pylint coverage analysis
- Both require only existing benchmarks and tools

---

### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect):

Converging well. Final rigor pass:

**Experimental spec (complete):**
- Benchmarks: HumanEval (164 problems), MBPP (374 problems)
- Models: Llama 3.1 8B (primary), Qwen2.5-Coder-7B (replication)
- Conditions: (1) no-feedback baseline; (2) pylint/mypy repair; (3) execution test repair; (4) type-constrained one-pass [secondary]
- Token budget: B=1000 total output tokens per problem instance (allows ~3 repair rounds of ~300 tokens each OR one type-constrained pass)
- Metric: pass@1 delta vs. baseline; statistical test: McNemar's test (paired binary outcomes)
- Error coverage analysis: automated (run pylint on baseline failure set; count flagged vs. unflagged; compare to execution catch rate)

**Three falsifiable predictions:**
- **P1:** Execution feedback achieves statistically significantly larger pass@1 delta than pylint/mypy feedback on HumanEval at B=1000 tokens, Llama 3.1 8B (McNemar's test, α=0.05)
- **P2:** The fraction of HumanEval baseline failures that pylint detects pre-execution is significantly less than the fraction that execution feedback catches
- **P3:** Type-constrained decoding achieves positive pass@1 delta over unconstrained one-pass generation on HumanEval (secondary study)

**Key Points:**
- Token budget B=1000 output tokens per problem instance operationalizes iso-compute
- Four conditions: no-feedback, pylint/mypy repair, execution repair, type-constrained prevention
- McNemar's test for P1; automated coverage analysis for P2
- 164 HumanEval problems give adequate statistical power for 10pp difference detection

---

### Exchange 15

🎯 **Dr. Sage** (Research Impact Evaluator):

We've reached a solid scientific core. Final significance assessment:

**Three reasons this earns its place:**

1. **The iso-compute framework is the methodological contribution.** No existing paper compares feedback types while holding total output tokens constant. This framework is reusable — other researchers can use it to compare new feedback signals fairly. The framework itself is citable beyond the specific ranking finding.

2. **The finding is significant regardless of outcome direction.** If execution >> pylint: confirms the dominant assumption with rigor, gives practitioners a quantified cost-benefit ratio. If pylint ≈ execution: overturns the dominant assumption, has immediate deployment implications. Either finding appears in an AI coding systems paper within one year.

3. **The automated error coverage analysis is the mechanistic bridge.** The paper doesn't just report a ranking — it explains *why* the ranking is what it is, using automated tool analysis. This makes the finding predictive: for benchmarks with higher proportions of type errors, we'd predict type constraints and pylint to gain relative to execution.

**Verdict: STRONG significance.** Scope (7B models, HumanEval/MBPP) is appropriate for a VerifAI workshop paper.

**Framing note:** Frame around the *framework* (iso-compute feedback type comparison), not just the *finding* (ranking). Frameworks are cited more than rankings.

**Key Points:**
- Iso-compute comparison framework is a standalone methodological contribution (reusable)
- Significance is outcome-independent
- Automated error coverage analysis provides mechanistic explanation
- Frame around the framework, not just the finding

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The iso-compute feedback type comparison is genuinely novel — not because no one thought to compare signal types, but because the comparison infrastructure (token-budget-controlled, repair-mode-vs-prevention bifurcation, automated error coverage analysis) didn't exist before. The automated coverage analysis (measuring what fraction of HumanEval failures pylint catches pre-execution) is a novel secondary contribution that opens a new characterization problem: what is each formal feedback signal's "coverage radius" on a given benchmark?

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Three independently falsifiable predictions (P1: McNemar's test on pass@1 delta; P2: automated pylint coverage analysis; P3: type-constrained decoding prevention baseline) with pre-specified statistical tests and sample sizes. The null hypothesis H0: Δ_pylint = Δ_execution is directly testable. The mechanism prediction is operationalized as an automated measurement, not a post-hoc narrative.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Closes a 2-year empirical gap. Significance is outcome-independent: both "execution >> pylint" and "pylint ≈ execution" are deployable findings for production coding systems choosing feedback signals. The reusable iso-compute framework has citation value beyond the specific finding. Perfect scope for VerifAI workshop.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** MODERATE-STRONG
- **Assessment:** Primary comparison (execution vs. pylint in repair mode) is HIGH feasibility — Johin2/iterative-code-repair covers execution; pylint wrapper is straightforward. Secondary study (type-constrained decoding) is MEDIUM feasibility — requires local HuggingFace inference. Main risk: cyb3rlab/CodeEnhancer adaptation for HumanEval/MBPP functional correctness testing (currently security-focused). This is a medium implementation task, not a theoretical barrier.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The hypothesis that emerged from this discussion: Under HumanEval and MBPP, for open-source instruction-tuned LLMs at 7B scale (Llama 3.1 8B primary, Qwen2.5-Coder-7B replication), varying formal feedback type between (A) pylint/mypy static analysis feedback and (B) execution test feedback — both in iterative repair mode at fixed token budget B=1000 output tokens per problem — execution test feedback achieves a statistically significantly larger pass@1 improvement delta over no-feedback baseline than pylint/mypy feedback (McNemar's test, α=0.05), because execution feedback covers the full distribution of code errors while static analysis covers a subset with lower correlation to the specific logical failures that dominate HumanEval/MBPP problem types. The mechanism is a testable prediction operationalized as automated pylint coverage analysis on baseline failures — not an assumed explanation.

Type-constrained decoding is studied separately as a prevention baseline (one-pass comparison against unconstrained generation), establishing whether generation-time constraints improve pass@1 on the same benchmarks. The full experimental design: four conditions (no-feedback baseline, pylint/mypy repair, execution repair, type-constrained one-pass), on HumanEval + MBPP, two models, fixed token budget B=1000. No new benchmarks. No human annotation. All inference on existing open-source repos.

Two main contributions: (1) the first iso-compute comparison of execution vs. static analysis feedback in repair mode on functional correctness benchmarks; (2) automated error coverage analysis characterizing what fraction of HumanEval failures pylint can detect pre-execution (explaining the mechanism).

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Pylint's functional coverage on HumanEval is empirically unknown — the experiment may find pylint has zero effect on pass@1, which would BE the finding, not a failure
- cyb3rlab/CodeEnhancer adaptation for HumanEval/MBPP functional correctness testing requires 2-4 days engineering work (currently security-focused benchmark setup)
- 7B-only models limit generalizability claims — conclusions must be explicitly scoped to 7B instruction-tuned models in the abstract
- **Mitigation Strategy:** Treat the pylint null result as a primary finding framing (paper answers the question regardless of direction). Budget CodeEnhancer adaptation as a known implementation task in Phase 2B plan. Explicitly scope all conclusions to 7B instruction-tuned open-source models.

