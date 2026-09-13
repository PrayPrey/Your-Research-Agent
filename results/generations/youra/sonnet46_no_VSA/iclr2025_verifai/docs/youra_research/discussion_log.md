# Phase 2A Discussion Log

**Gap ID:** gap-1  
**Gap Title:** No Execution-Based Contract-Strength Measurement Across LLM Families on ContractEval  
**Initialized:** 2026-08-03T12:41:00+00:00  
**Architecture:** Self-Contained Tikitaka Loop  
**Execution Mode:** UNATTENDED  

---

### Previous Failure / Routing Context

**Source Memory:** `.serena/memories/failure_h-e1_run1.md`  
**Status:** GATE_FAIL — ROUTED_TO_PHASE_0 → Phase 1 → Phase 2A (Recursive Entry v2)

| Item | Detail |
|------|--------|
| **Previous Hypothesis** | h-e1 (Run 1) |
| **Statement** | Z3 on negated post-conditions of ContractEval contracts on HumanEval+/MBPP+ |
| **Gate Result** | FAIL: Z3 tractability 25.82% < 50% threshold |
| **Contract Strength Ratio** | 0.0742 (PASSED — concept valid) |
| **Root Cause** | 73.9% of ContractEval contracts unencodeable in Z3's linear arithmetic fragment |

**What failed:** Z3/SMT as primary verification mechanism for Python-native contracts.  
**What showed promise:** Contract strength concept valid — 27 violations confirmed (programs passing tests but failing contracts). Core direction (formal verification > testing) is sound.  
**Prohibited redesign directions:** Do NOT use Z3/SMT as primary verifier. Do NOT assume ContractEval contracts are SMT-encodeable without pre-filtering. Do NOT set tractability threshold >30% without encoder improvements.  
**Suggested new directions (from failure record):** Runtime fuzzing against contract assertions, hybrid Z3+execution, CrossHair for Python-native contracts, Hypothesis PBT.

**Impact on this discussion:** All personas must redesign away from Z3/SMT. New hypothesis must achieve 100% tractability by construction using execution-based checking. Preserve the validated insight (contract strength ratio >0) and build on it.

---

## Research Briefing

**Selected Gap:** Gap 1 — No execution-based contract-strength measurement across LLM families on ContractEval

**Core Research Question:** When LLM-generated code is evaluated against formal contracts using execution-based verification (Hypothesis PBT, runtime assertion checking, CrossHair) on ContractEval subset of HumanEval+/MBPP+, what fraction of test-passing programs fail at least one formal contract, and how does this gap vary across LLM model families?

**Available Papers (prepared):**
- `arxiv_2510_12047.md` — ContractEval (Lim et al. 2025, ACL 2026) — PRIMARY BENCHMARK
- `arxiv_2305_01210.md` — EvalPlus/HumanEval+ (Liu et al. 2023) — INFRASTRUCTURE
- `arxiv_2510_09907.md` — Agentic PBT (Maaz et al. 2025, Anthropic) — PBT VALIDATION
- (Bose 2025 "From Prompts to Properties" — 429 error, not available, but characterized in Phase 1)

**Key Evidence from Phase 1:**
- ContractEval: 364 tasks, 5 open-source LLMs, 0% contract satisfaction under standard prompting (uses SMT)
- Bose (2025): PBT finds 18-32% additional failures vs unit tests on StarCoder/CodeLlama (only 2 models)
- Code Monitor Red Teaming (OpenAI 2026): 23,081/43,677 test-passing programs fail hidden checks (52.9%)
- Tools: Hypothesis v6.156.7 (8788★), CrossHair (1296★), evalplus (1789★) — all pip-installable
- Closest unpublished: darshana-v/llmcodeprobe (CrossHair+Hypothesis on HumanEval/MBPP, not ContractEval-specific)

**Feasibility Constraints (Pipeline-Enforced):**
- NO new benchmarks or scoring frameworks
- NO synthetic/generated data
- NO human evaluation or annotation
- ONLY existing real datasets and existing benchmarks

---

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

🔭 **Dr. Nova** (Creative Novelty Explorer):

This is a genuinely exciting moment in code evaluation research. We've inherited a powerful negative result from h-e1 — Z3 can't handle ContractEval's Python-native contracts — but that failure revealed something profound: the contracts ARE stronger than tests (7.42% violation rate on the tiny tractable fraction). Now the question is: can we measure this gap cleanly at scale, using tools that speak Python natively?

Let me propose three angles that haven't been explored yet. First, the **"tractability ceiling removal"** angle: if we swap Z3 for execution-based checking, we go from 25.82% coverage to 100% by construction. That's not an incremental improvement — it's a qualitative phase transition. The ContractEval paper's 0% contract satisfaction finding is measured on a biased, tractable-only subset via neuro-symbolic synthesis. Our execution-based rate on all 364 problems could be the first true denominator.

Second, the **cross-model stratification** angle is genuinely novel. ContractEval evaluated only 5 open-source models, zero closed models. The EvalPlus leaderboard (Liu et al., 2023) compared 26 LLMs on functional correctness — but nobody has mapped that same landscape onto formal contract satisfaction. GPT-4o versus CodeLlama-7B on contract adherence is an unmeasured axis. Bose (2025) found 18-32% PBT-based failure rates for StarCoder/CodeLlama — what does GPT-4o look like?

Third — and this is the most creative angle — **contract type attribution**. ContractEval provides pre-conditions and post-conditions separately. When Hypothesis generates random inputs satisfying pre-conditions and checks post-conditions, we can decompose violations by type. Do LLMs better satisfy pre-conditions (input domain correctness) or post-conditions (functional correctness)? This breakdown has never been published.

The core novel claim I want to explore: **execution-based contract checking reveals a systematically higher and more complete contract-strength gap than any prior SMT-based measurement, and this gap varies significantly across model families in ways that cannot be predicted from pass@k alone.**

**Key Points:**
- Phase transition: 25.82% SMT coverage → 100% execution coverage (not incremental)
- Zero published cross-model (open + closed) execution-based contract evaluation exists
- Contract type breakdown (pre vs post condition violation rates) is a genuinely novel contribution

---


### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

The central claim is ambitious: that execution-based contract checking will (1) expose a larger "contract-strength gap" than SMT-based methods and (2) reveal cross-model variation not predictable from pass@k alone. The evidence from EvalPlus suggests caution. When they expanded test coverage by ~80× (from ~9.6 to ~764 tests/task), pass@1★ dropped by up to 23.1% and model rankings inverted [Liu et al., 2023]. The evidence suggests that evaluation *methodology alone* can materially reshape conclusions. Therefore, before we celebrate a "phase transition" from 25.82% SMT tractability to 100% execution coverage, we must define precisely what would falsify the claim that this shift is qualitatively different rather than merely another coverage increase.

First, the "100% coverage by construction" assertion is testable. What would disprove it? If execution-based checking with Hypothesis fails to generate inputs that trigger known contract violations in a non-trivial fraction of tasks, then coverage is illusory. I propose a calibration experiment: inject synthetic contract-violating mutants into ground-truth implementations (analogous to mutation testing in EvalPlus [Liu et al., 2023]) and measure detection rate. Predefine a success criterion: ≥95% of injected post-condition violations must be detected within a fixed budget (e.g., 1,000 generated inputs/task). If detection falls below this threshold, the "100%" claim is empirically false in practice.

Second, your cross-model stratification hypothesis requires a quantitative prediction. For example: "The rank correlation (Spearman ρ) between pass@1 on EvalPlus-style augmented tests and contract-satisfaction rate will be <0.6." That is falsifiable. If ρ ≥ 0.8 across models (as might be expected if contracts largely encode stronger functional tests), then contract evaluation adds little new signal. Additionally, predefine an effect size: at least one pair of models must invert ranking under contract satisfaction compared to pass@1, mirroring the mis-ranking effect observed in HUMANEVAL vs. HUMANEVAL+ [Liu et al., 2023]. Without such criteria, "varies significantly" is too vague to evaluate.

Third, the pre- vs. post-condition decomposition is promising—but methodologically delicate. Preconditions in EvalPlus serve as input filters, not behavioral guarantees. If Hypothesis generates only inputs satisfying preconditions, you cannot measure precondition violation unless you deliberately test boundary-breaking inputs. Therefore, design two regimes: (A) in-distribution inputs satisfying preconditions; (B) adversarial near-boundary inputs that minimally violate them. Define measurable outputs: proportion of samples that (i) fail to enforce input domain checks, (ii) produce incorrect outputs despite valid inputs. The hypothesis predicts asymmetry. What result would disprove it? If violation rates for pre- and post-conditions are statistically indistinguishable (e.g., paired t-test, p > 0.05 across tasks), then the claimed structural weakness distinction does not hold.

Finally, control the obvious confound: input generation quality. EvalPlus used LLM-seeded, type-aware mutation plus differential testing against ground truth [Liu et al., 2023]. If your contract-checking inputs are weaker than HUMANEVAL+, any observed "gap" may reflect test inadequacy rather than contract strength. I would require a matched-budget comparison: same mutation budget (one hour/task), same seed strategy, differing only in oracle (ground-truth equality vs. contract predicate). Only then can we attribute differences to contracts rather than input distribution.

If these conditions are met—clear falsifiers, predefined statistical thresholds, mutation-calibrated detection guarantees—then we will have a rigorous measurement of the contract-strength gap. Until then, the evidence suggests promise, but not yet proof.

**Key Points:**
- Define falsifiable thresholds (e.g., ≥95% mutant detection, Spearman ρ < 0.6) to make claims testable.
- Calibrate execution-based contract checking via mutation injection to validate the "100% coverage" assertion.
- Control for input-generation confounds using matched-budget, oracle-isolated comparisons inspired by EvalPlus [Liu et al., 2023].

---

### Exchange 3

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Vera raises essential rigor requirements, and I want to ground both her concerns and Dr. Nova's creative angles in what we can actually implement with pip install and publicly available code within a reasonable compute budget. Let me assess each component against reality.

On the "100% tractability by construction" claim: this is correct in the sense that Python `assert` execution never fails to terminate the way Z3 does. But Prof. Vera's concern about effective detection rate is legitimate. The critical question is: how well does Hypothesis generate inputs that satisfy ContractEval pre-conditions? For simple pre-conditions like `n > 0` or `len(lst) > 0`, icontract-hypothesis can infer strategies automatically. For complex pre-conditions like `sorted(lst) == lst and all(x >= 0 for x in lst)`, strategy inference may fail and fall back to random sampling with `assume()` — which can be extremely slow (Hypothesis discards up to 99% of generated inputs if pre-conditions are tight). This is a known limitation documented in the Hypothesis docs. The practical solution: measure Hypothesis filter rate per task and report it. For tasks where filter rate > 90% (too restrictive for effective PBT), fall back to direct contract assertion with exhaustive domain sampling.

On Prof. Vera's mutant detection calibration: this is exactly the right validation — but I propose a simpler version that doesn't require a new benchmark. ContractEval includes programs from real LLMs that the paper's neuro-symbolic pipeline confirmed fail contracts. Those ARE our ground-truth violating programs. We don't need to inject synthetic mutants — we already have them (the 94 SAT cases from h-e1 and ContractEval's own evaluation). Run our execution-based checker on those known violators and measure detection rate. If we detect ≥80% of programs that ContractEval's SMT pipeline confirmed as violators, we've validated our method against ground truth without any new data.

On cross-model scope: GPT-4o and Claude 3.5 via API add cost but evalplus already has Anthropic and OpenAI backends. The realistic model set for a publishable study: GPT-4o-mini (cost-efficient closed), Claude-3-haiku (cost-efficient closed), DeepSeek-Coder-V2-Lite (open, 16B), CodeLlama-13B (open, mid-size), CodeLlama-34B (open, large). Generate n=10 samples per model per problem on ContractEval's 364 tasks. API cost estimate: ~$50-100 total at current pricing. That's feasible.

On the pre/post-condition decomposition: Prof. Vera's concern about measuring pre-condition enforcement is valid. The practical implementation: run Hypothesis in two modes. Mode A — respect pre-conditions via `assume(pre_condition(x))`; Mode B — ignore pre-conditions and test all inputs. Mode B tests whether the implementation correctly enforces its own input domain. ContractEval contracts have both `@pre` and `@post` annotations, so this decomposition is structurally supported.

The implementation stack is concrete: `pip install hypothesis evalplus crosshair-tool icontract-hypothesis`. All components available, all open-source, no human annotation needed. Full experiment fits on a single GPU machine for local models, API calls for closed models.

**Key Points:**
- Hypothesis filter rate must be measured and reported per task — high filter rate tasks need alternate strategy
- Ground-truth validation available from ContractEval's own confirmed violators (no new benchmark needed)
- Concrete model set (5 models) and cost estimate (~$50-100 API) confirms feasibility

---


### Exchange 4

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good — this is finally getting concrete. Now let me show you where this still breaks down.

First, the "phase transition" claim. I don't buy it yet. EvalPlus already demonstrated that simply expanding test coverage by ~80× caused pass@1⋆ to drop by up to 23.1% and even inverted rankings [Liu et al., 2023]. That is a *methodological amplification effect*, not a phase change. If your execution-based contract checking is just "more tests with a different oracle," then it's squarely in the same family. What would convince me it's a true qualitative shift? You must isolate the oracle effect. Run matched input sets: generate inputs using the exact EvalPlus pipeline (LLM seeds + type-aware mutation + one-hour budget) and evaluate the same candidate programs under two oracles: (1) ground-truth equality (EvalPlus style) and (2) contract predicates only. If contract failure rates exceed differential-testing failure rates by a statistically significant margin (e.g., ≥10% absolute across tasks, paired test p < 0.01), *then* you've demonstrated contract strength beyond dense testing. Otherwise, you've just rebranded fuzzing.

Second, your "100% tractability by construction" is rhetorically dangerous. Execution never times out like Z3 — fine. But effective tractability depends on input generation efficiency. Prof. Pax is right to flag Hypothesis filter rates. Show me the distribution of valid-input yield per task. If 20–30% of tasks have <10% acceptance rate under `assume(pre)`, then your practical coverage collapses. What would convince me? A per-task effective sample size report and a mutant-detection calibration. And I want it aligned with EvalPlus's own adequacy philosophy: they preserved *mutant killings* and *LLM sample killings* during reduction [Liu et al., 2023]. You should too. Take known contract-violating LLM samples (as Pax suggests) and require ≥90% detection within a fixed budget. If you can't hit that, your oracle is underpowered.

Third, the cross-model "unpredictable from pass@k" claim is currently hand-wavy. EvalPlus already showed ranking inversions (e.g., open models surpassing ChatGPT under HUMANEVAL+) [Liu et al., 2023]. So mis-ranking alone is not novel. Your bar must be higher: demonstrate low rank correlation (predefine ρ threshold), and more importantly, demonstrate *residual variance*. Regress contract satisfaction rate on pass@1⋆ and model size. If substantial unexplained variance remains (say R² < 0.6), then contracts measure something orthogonal. If R² > 0.85, then contracts are just a noisier proxy for functional correctness. Decide now which outcome would falsify your novelty claim.

Fourth, the pre/post-condition decomposition is promising — but here's the unstated assumption: that contract authors wrote semantically rich postconditions. What if many postconditions are shallow restatements of equality with ground truth? Or weak predicates? You need a contract-strength audit. Sample 50 tasks and categorize postconditions by logical expressiveness. If most are weak, then high satisfaction rates tell us nothing. If they're strong and frequently violated while pass@1⋆ is high, *that* is your paper.

**Key Points:**
- Isolate oracle strength from input density using matched-input evaluation (contract vs. ground-truth equality).
- Validate effective coverage via mutant/known-violator detection ≥90% under fixed budget.
- Predefine quantitative novelty thresholds (rank correlation, residual variance, additional failure rate) or the claim collapses.

---

### Exchange 5

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Rex's stress-test points are productive — they're turning vague claims into precise experimental requirements. But I want to redirect us from methodology debates toward the research impact question: *who cares, and why?* Because this shapes which measurements matter most.

The research significance argument has two tiers. Tier 1 (evaluation science): we need a better oracle than unit tests for assessing LLM-generated code. EvalPlus [Liu et al., 2023] showed that 80× more tests shifted rankings and reduced pass@1 by up to 23%. But even augmented test suites test the same thing — functional equivalence to a reference implementation. Contracts test something categorically different: specification conformance, including correctness properties that no finite test set can exhaustively check. The OpenAI Code Monitor Red Teaming paper (2026) found 52.9% of test-passing programs fail hidden checks — this is a massive gap between apparent and actual correctness. Execution-based contract checking is a practical, deployable tool to close part of that gap without Z3's tractability limitations. That's Tier 1 significance: method-level contribution to code evaluation.

Tier 2 (model selection): the cross-model comparison has genuine practical stakes. Organizations choosing between GPT-4o, Claude 3.5, and DeepSeek-Coder for production code generation need to know whether model selection affects specification adherence, not just test-passing. If the contract violation rate for GPT-4o-mini is meaningfully lower than CodeLlama-7B at comparable pass@k — or if the ranking inverts — that directly informs deployment decisions. This is the same pragmatic framing that made EvalPlus's ranking inversions impactful.

Now, regarding Prof. Rex's specific challenges: the "additional failure beyond dense testing" threshold (≥10% absolute) is reasonable and I endorse it as a primary success criterion. Here's why it's achievable: Agentic PBT [Maaz et al., 2025] found that LLM-generated Hypothesis tests caught genuine bugs in NumPy, SciPy, Pandas — production code that had survived years of review. Contract-guided Hypothesis (using actual pre/post-conditions as oracles rather than LLM-generated properties) is more constrained but better targeted. The failure mode is clear when the LLM generates code that handles the provided test cases but mishandles edge cases the contract specifies. For algorithms like sorting, string processing, and mathematical operations (dominant in HumanEval+/MBPP+), postconditions typically encode the *actual intended behavior* — not just equality to a reference — making them genuinely stronger.

The contract richness concern Prof. Rex raises about shallow postconditions is worth addressing empirically. A lightweight audit: count ContractEval postconditions with universal quantification (`all()`), relational properties (`sorted()`), or multi-variable constraints vs. simple equality. Phase 1 data suggests ContractEval contracts are Python-expressive (list comprehensions, string ops) — the very richness that defeated Z3. That same richness makes them strong as behavioral specifications. A shallow postcondition like `return True` would never have defeated Z3 in the first place.

For research impact, the **core publishable contribution** should be: execution-based contract checking on ContractEval reveals X% contract-strength gap (with X > 0% confirmed by h-e1's 7.42% on the tractable fraction), this gap varies meaningfully by model family (Spearman ρ < 0.6 with pass@k), and Hypothesis PBT detects a significant fraction of violations not caught by the 764-test-per-task EvalPlus battery.

**Key Points:**
- Tier 1 impact: practical alternative to SMT for Python-native contract evaluation (direct response to h-e1 failure)
- Tier 2 impact: cross-model contract violation ranking for deployment-relevant model selection
- Contract richness is an empirical question answerable from ContractEval's own contract structure (no new data)

---


### Exchange 6

🔬 **Prof. Vera** (Rigorous Validation Architect):

The discussion is converging appropriately. I will sharpen it further. The central scientific question is not whether execution-based contract checking is *feasible*—it clearly is—but whether it provides **measurably stronger discrimination** than dense differential testing as implemented in EvalPlus [Liu et al., 2023]. The evidence from HUMANEVAL+ shows that simply increasing test density (~9.6 → ~764 tests/task) reduced pass@1⋆ by up to 23.1% and inverted rankings. Therefore, any claimed "contract-strength gap" must exceed what we would expect from oracle-equivalent dense testing.

I propose a decisive, oracle-isolation experiment. Use EvalPlus's exact input-generation pipeline—LLM-seeded inputs (≈30/task), type-aware mutation, one-hour budget, and optional reduction preserving LLM-sample killings [Liu et al., 2023]. Fix this input set. Then evaluate identical candidate programs under two oracles: (1) **Differential oracle**: f(x) = gt(x) (EvalPlus standard), (2) **Contract oracle**: execution of postconditions only (ignoring equality). Pre-register: mean contract-failure rate will exceed differential-failure rate by ≥10% absolute, paired Wilcoxon test p < 0.01.

Second, the "100% tractability by construction" assertion must be operationalized. For each task, report: (i) total generated inputs, (ii) valid inputs after precondition filtering, (iii) unique behavioral paths exercised. Define failure condition: if ≥20% of tasks have effective valid-input yield <100 samples within fixed budget, practical coverage collapses. Adopt adequacy backstop: ≥90% detection of ContractEval's known contract-violating programs within fixed budget.

Third, cross-model novelty requires orthogonality, not just mis-ranking. Regression: contract-satisfaction rate ~ pass@1⋆ + model size. Predefine R² < 0.6 as meaningful residual variance. Require Spearman ρ(pass@1⋆, contract-rate) < 0.6. If R² > 0.85 and ρ ≥ 0.8, contract evaluation is largely monotonic with dense functional correctness.

**Key Points:**
- Oracle-isolation experiment: ≥10% additional contract failures beyond matched differential testing (p < 0.01).
- Operationalize tractability with per-task yield metrics and ≥90% known-violator detection.
- Pre-register orthogonality criteria (ρ < 0.6, R² < 0.6) for cross-model novelty claim.

---

### Exchange 7

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

We now have a rich discussion — let me synthesize the convergent threads and strengthen the hypothesis into a form that survives all the challenges raised.

The core contribution is becoming clear through this discussion: **a measurement study establishing the execution-based contract-strength gap for LLM-generated code on ContractEval, with cross-model stratification and oracle-isolation controls.** This directly succeeds h-e1 by replacing Z3 with Python-native execution, achieving 100% tractability in principle (with Prof. Vera's yield-adequacy backstop as quality control).

The hypothesis I propose for consolidation: **Under ContractEval's 364 HumanEval+/MBPP+ tasks, when LLM-generated code that passes all unit tests is evaluated against Python pre/post-condition contracts via Hypothesis PBT (with icontract-hypothesis strategy inference), execution-based checking reveals a contract-strength gap (test-pass-but-contract-fail rate) that is: (a) ≥10% absolute above what matched-input differential testing detects (isolating oracle strength), (b) ≥25% on average across programs (extrapolating from h-e1's 7.42% on 25.82% tractable subset to full 100% coverage), and (c) significantly variable across LLM model families (Spearman ρ < 0.6 with pass@k).**

This addresses every challenge: Prof. Rex's oracle isolation requirement is encoded in criterion (a). Prof. Vera's statistical pre-registration is in (a) and (c). Prof. Pax's yield adequacy is operational procedure (measure and report yield, exclude tasks with <100 valid samples, but don't fail the study). Dr. Sage's impact framing is served by criteria (b) and (c) together: the gap is real and model-family-dependent.

The mechanism is clean: LLM-generated code that satisfies finite test cases may violate universal properties encoded in contracts (e.g., sorting stability, bounds preservation, type invariants). Hypothesis explores the input space beyond what unit tests cover, triggering violations that tests miss. This is why the gap is expected to be substantial — not just at the margin of dense testing.

The novelty is precisely scoped: first execution-based (not SMT) cross-model contract-strength gap measurement on ContractEval, with oracle isolation controls. No new benchmarks needed. No human annotation. All tools pip-installable. Direct successor to h-e1 with root-cause fix.

**Key Points:**
- Hypothesis: execution-based contract-strength gap ≥10% above matched differential testing, ≥25% overall, with Spearman ρ < 0.6 across model families
- Oracle isolation controls address Prof. Rex/Vera falsifiability requirements
- No new benchmarks, no human annotation — purely existing data and tools

---


### Exchange 8

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good — this is finally shaped like a testable claim. But I'm still going to press on the weak joints.

First, your ≥10% "oracle-isolated" gap only means something if the input distribution is truly controlled. EvalPlus's pipeline is not just "many tests" — it is *white-box seeded*, mutation-scaled, and contract-filtered, with a one-hour mutation budget and ~30 LLM seeds per task [Liu et al., 2023]. If you reuse that exact machinery, then you've matched density and semantic validity. But here's where this breaks down: Hypothesis-based generation is *adaptive*, whereas EvalPlus mutation is stochastic but non-adaptive. So I want two runs: (1) **Matched static inputs** from EvalPlus evaluated under both oracles (pure isolation). (2) **Adaptive PBT inputs** evaluated under contract oracle only (realistic upper bound). If the ≥10% gap only appears in (2) but not (1), then the gain is from smarter input search, not oracle strength. That distinction matters.

Second, your ≥25% overall contract-strength gap projection from h-e1's 7.42% on 25.82% tractable tasks is mathematically hand-wavy. You're extrapolating across a non-random subset. What if Z3 failed precisely on the *hardest* contracts, which are also hardest to violate via execution? What would convince me: stratification by contract syntactic richness (quantifiers, comprehensions, cross-variable relations). Report contract-failure rates per stratum. If richer contracts produce systematically higher additional failures, your mechanism story holds.

Third, on adequacy: adopt EvalPlus's leave-one-out violation preservation. For each task, identify programs passing base tests but failing contracts. Reduce PBT input set via set cover and check ≥90% of violators remain detected. Show me preservation under reduction — then I'll believe this isn't brute-force fuzzing.

Finally, run partial correlation controlling for HUMANEVAL+ pass@1⋆. If contracts explain significant variance beyond dense testing (ΔR² ≥ 0.1), that's real. If not, contract satisfaction is largely monotonic with already-augmented correctness.

**Key Points:**
- Separate oracle strength from adaptive input search (static matched vs. adaptive PBT).
- Stratify contract richness and report per-stratum failure rates.
- Demonstrate adequacy via violation-preservation under reduction and ΔR² beyond HUMANEVAL+ pass@1⋆.

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Rex's distinction between static-matched and adaptive-PBT inputs is important and implementable. Let me convert it to concrete implementation decisions.

For the static-matched oracle isolation experiment: EvalPlus publishes its test inputs for HumanEval+ (the 764-test-per-task set) as a public dataset. We use those exact inputs as our static set. Run them through two oracles: (1) ground-truth equality (already computed by EvalPlus), (2) ContractEval pre/post-condition assertions. This requires no new input generation — just re-evaluation of existing inputs against a different oracle. Implementation: load EvalPlus test cases as Python dictionaries (they're JSON-serializable), execute ContractEval's `@pre`/`@post` assertions on each, record pass/fail. Compute oracle-isolation gap = (contract failures on EvalPlus inputs) - (EvalPlus failures on same inputs). This is ~1-2 days of engineering.

For the adaptive PBT experiment: Hypothesis with icontract-hypothesis runs independently and generates its own inputs guided by pre-conditions. This is the "realistic upper bound" Prof. Rex describes. Implementation: for each ContractEval task, wrap the LLM-generated function in Hypothesis `@given` with strategy inferred from `@pre` by icontract-hypothesis, check `@post` as the test body. Run for fixed budget (e.g., 1000 examples or 60 seconds per task per model). Report filter rate (valid/total), violation rate, and detection of ContractEval's known violators.

The stratification of contract richness is feasible without human annotation: write a Python AST analyzer that categorizes each ContractEval postcondition by: (a) pure equality to ground truth, (b) structural invariant (sorted, unique, length-preserving), (c) relational property (cross-variable), (d) universal quantification (contains `all()` or `any()`). This takes ~2 hours to implement. No human raters needed — purely syntactic.

The ≥25% gap projection concern is valid. The projection from 7.42% to ≥25% assumes Z3-tractable problems were not representative. The most defensible framing: h-e1 provided a *lower bound* (7.42% on the easiest-to-check contracts). The true rate is unknown — and that's the contribution. Drop the specific ≥25% threshold from the hypothesis. Instead, the primary MUST_WORK gate should be: (a) contract-strength gap > 0 on the full 364 tasks (confirmed by h-e1 on the tractable subset, expected to hold broadly), and (b) oracle-isolation gap ≥10% on the static EvalPlus input set.

Implementation stack confirmed: `pip install hypothesis icontract-hypothesis crosshair-tool evalplus`. All public. All pip-installable. Full experiment runnable in 3-5 days on a single machine with API credits for closed models (~$50-100).

**Key Points:**
- Oracle isolation uses EvalPlus's published 764-test inputs re-evaluated against ContractEval predicates — zero new input generation
- Contract richness stratification: AST-based Python analyzer, no human annotation, ~2 hours to implement
- Drop ≥25% projection; primary gate is oracle-isolation gap ≥10% + contract-strength gap > 0 on full 364 tasks

---


### Exchange 10

🔬 **Prof. Vera** (Rigorous Validation Architect):

This is now approaching scientific shape. I will formalize the falsifiable core.

On oracle isolation: define for each program p and task t: D_pt (failure under differential oracle) and C_pt (failure under contract oracle on same input set). Primary test: paired difference Δ_pt = C_pt - D_pt. Pre-register: mean Δ > 0.10 (absolute) with Wilcoxon signed-rank p < 0.01, across programs that pass base tests. What disproves: mean Δ ≤ 0.02 or non-significant after Holm correction across models.

Separate adaptive PBT as its own mechanism — Experiment A (static EvalPlus inputs, dual oracles) vs. Experiment B (Hypothesis/icontract-hypothesis, contract oracle only, fixed budget). If gap in A ≥10%, oracle strength is causal. If A ≈ 0 but B is large, then gain is from adaptive search, not contract semantics. Both must be reported.

Adequacy via set-cover preservation: apply greedy set cover to reduce PBT inputs; measure preservation = |programs detected under reduced set| / |total violators|. Pre-register ≥90% preservation threshold.

Orthogonality must control for HUMANEVAL+ pass@1⋆ (not original pass@1). Predefine partial ΔR² ≥ 0.10 and Spearman ρ(contract-rate, pass@1⋆_+) < 0.6. If ρ ≥ 0.8, contract satisfaction is monotonic with dense correctness.

**Key Points:**
- Oracle-isolation: mean static gap ≥10% (Wilcoxon p < 0.01); ≤2% falsifies.
- Separate adaptive-search effects from oracle semantics; ≥90% violation preservation under set-cover reduction.
- Orthogonality beyond HUMANEVAL+ pass@1⋆: ΔR² ≥ 0.10, ρ < 0.6.

---

### Exchange 11

🎯 **Dr. Sage** (Research Impact Evaluator):

We've now reached the point where the hypothesis is scientifically rigorous enough to assess for publication impact. Let me evaluate what we have and where the remaining impact leverage is.

The experiment design has converged to a two-experiment structure that is genuinely publishable: Experiment A (oracle isolation using EvalPlus static inputs) and Experiment B (adaptive Hypothesis PBT with ContractEval contracts). Prof. Vera's formal pre-registration criteria (Wilcoxon p < 0.01, Δ ≥ 10%, ΔR² ≥ 0.10, ρ < 0.6) make this a proper empirical study, not a demo.

Impact assessment: if the hypothesis holds, this paper makes three contributions with different venues/communities:
1. **Evaluation science contribution**: demonstrates contracts provide oracle strength beyond dense differential testing (Δ ≥ 10% on static inputs) — this speaks to the SE/ISSTA/ASE community that cares about test oracle quality.
2. **LLM code evaluation contribution**: first cross-model contract-strength gap table (open vs. closed, small vs. large) with orthogonality to pass@1⋆ — this speaks to the NeurIPS/ICLR/ACL community that evaluates LLMs.
3. **Practical deployment contribution**: the fact that execution-based checking is 100% tractable (vs. 25.82% for Z3/h-e1) makes it a deployable tool, not just an analysis — this speaks to practitioners and MLOps communities.

The cross-model comparison specifically: if we find that GPT-4o satisfies contracts at significantly higher rates than CodeLlama-7B after controlling for pass@k, that's a deployment-relevant ranking that doesn't exist anywhere in the literature. Organizations choosing models for specification-critical code generation (embedded systems, financial APIs, safety-critical software) need exactly this table.

One impact-amplifying addition I propose: compare against darshana-v/llmcodeprobe as an unpublished baseline. That work measures "correctness_gap" with CrossHair+Hypothesis on HumanEval/MBPP (not ContractEval-specific). By showing our ContractEval-specific contract oracle produces a systematically larger gap than their generic approach, we demonstrate the value of having formal contracts vs. ad-hoc property testing. This comparison doesn't require new experiments — their methodology is public and we re-implement on ContractEval.

The research is well-positioned: ContractEval (2025/2026 ACL) is freshly published with only 1 citation. Getting in early with the first execution-based follow-up is a strong positioning move. Timeline: full experiment in 2-3 weeks if models are queried via API.

**Key Points:**
- Three distinct contribution types: evaluation science, LLM benchmarking, practical deployment tool
- Cross-model contract-violation ranking is deployment-relevant and currently unpublished
- Compare against llmcodeprobe as unpublished baseline to demonstrate ContractEval-specific contract strength

---


### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

This is much tighter. But I'm not done with you yet.

On oracle isolation using EvalPlus static inputs: those inputs were *optimized to expose differential mismatches*, not contract violations. If contract gap on static set is small (say 3–5%), that does not mean contracts are weak — it may mean EvalPlus's input distribution under-samples states where postconditions bite but outputs still match ground truth by coincidence. I want a diagnostic: classify contract violations on static inputs into (1) output-equal-to-gt but contract-failing (semantic-unique), (2) output-different-and-contract-failing (redundant). Require ≥5% absolute mass in (1) to claim semantic strength. Otherwise this is redundancy, not oracle strength.

On ranking inversion: predefine Kendall τ between model rankings under pass@1⋆_+ and contract-satisfaction rate. If τ ≥ 0.8, you haven't discovered a new axis. If τ ≤ 0.6 with statistically significant discordant pairs, now we're talking genuinely orthogonal capability.

On adequacy: require symmetric preservation in reduction — ≥90% for total violators AND ≥85% for contract-unique violators (cases detected only by contracts, not differential oracle).

On oracle soundness: run contracts against ground-truth implementations and report zero violations under adaptive PBT at high budget. EvalPlus found 11% of HUMANEVAL ground truths were defective [Liu et al., 2023]. If contracts fire on reference implementations, the oracle is unsound.

**Key Points:**
- Contract-unique failures (output-equal but contract-violating) ≥5% absolute mass to claim semantic strength.
- Kendall τ ≤ 0.6 for ranking orthogonality beyond pass@1⋆_+.
- Oracle soundness: zero violations on ground-truth implementations + symmetric preservation in reduction.

---

### Exchange 13

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Rex's contract-unique failure diagnostic is brilliant — let me incorporate it into the hypothesis structure and show why it will hold.

The contract-unique failures (output-equal but contract-violating) are precisely the most interesting case: a program that computes the right output value for the test inputs but via a mechanism that violates the universal property. Consider sorting: a LLM might return the correct sorted output on the 10 test cases but implement a sort variant that doesn't preserve stability, or doesn't handle duplicate elements correctly per the contract's `all(lst[i] <= lst[i+1] for i in range(len(lst)-1))` with additional uniqueness constraints. Those programs pass ground-truth equality on finite tests but fail the universal property when Hypothesis finds the edge input.

This is exactly the h-e1 precedent: the 27 confirmed violations found by Z3 were almost certainly of this type — programs passing all ContractEval's tests but failing when the post-condition was checked more carefully. Our execution-based approach scales this to all 364 problems instead of 25.82%.

For oracle soundness against ground-truth: ContractEval's contracts were written to match the reference implementations. If we run Hypothesis against the reference implementation at high budget (say 100,000 examples), we should see zero violations. If we find any, we flag those tasks for exclusion and report them (this is actually a secondary contribution — identifying flawed contracts). This is implementable and takes ~1 day.

The Kendall τ ≤ 0.6 threshold for ranking orthogonality is appropriate. I want to build the hypothesis around a single, strong, falsifiable core claim that synthesizes everything we've discussed:

**Consolidated Hypothesis (H-ContractStrength-v2):**

Under the ContractEval subset of HumanEval+/MBPP+ (364 tasks), for LLM-generated programs that pass all unit tests, execution-based contract checking (Hypothesis PBT with icontract-hypothesis strategy inference) reveals a contract-strength gap characterized by:
- **(P1) Oracle Strength**: Mean contract-failure rate exceeds EvalPlus differential-oracle failure rate on the same static input set by ≥10% absolute (Wilcoxon p < 0.01), with ≥5% absolute mass from contract-unique violations (output-equal but contract-failing).
- **(P2) Ranking Orthogonality**: Kendall τ between model rankings on contract-satisfaction rate and HUMANEVAL+ pass@1⋆ is ≤ 0.6, with ΔR² ≥ 0.10 in regression controlling for pass@1⋆.
- **(P3) Cross-Model Variation**: Contract-strength gap varies by ≥10% absolute between the best and worst performing model families (open vs. closed, small vs. large), not explained by pass@k differences alone.

**Key Points:**
- Contract-unique failures are theoretically expected and the most interesting result — they show LLMs satisfy finite tests but fail universal properties
- Oracle soundness check against ground-truth is implementable and a secondary contribution
- Three-prediction structure (P1: oracle strength, P2: orthogonality, P3: cross-model) is complete and falsifiable

---


### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect):

This is now scientifically structured. Final tightening before endorsement.

On oracle soundness: run Hypothesis with pre-registered budget (100k inputs or 2-hour wall-clock) against reference implementation for every ContractEval task. Success: zero contract violations. Falsifier: ≥1% of tasks with reproducible violations. Quarantine failing tasks, exclude from statistics, report counts.

On Experiment A (static inputs, oracle isolation): classify failures into (1) contract-unique: f(x)=gt(x) but contract fails — this is the semantic strength signal; (2) redundant: f(x)≠gt(x) and contract fails; (3) differential-only. Primary claim of semantic strength requires ≥5% absolute mass in (1), aggregated across programs, reported with bootstrap confidence intervals.

On Experiment B (adaptive PBT): fix budgets — 5,000 max examples/task, fixed RNG seeds. Report failure rate as function of budget (1k, 2.5k, 5k). Falsifier: marginal detection gain >2% between 2.5k and 5k on average indicates unstable estimates.

On ranking orthogonality: Kendall τ ≤ 0.6 between pass@1⋆_+ and contract-satisfaction rankings (permutation p < 0.05). ΔR² ≥ 0.10 in regression with pass@1⋆_+. If τ ≥ 0.8 and ΔR² < 0.05, contracts do not define a new capability axis — P2 falsified.

**Key Points:**
- Oracle soundness: zero reference violations; ≥1% task rate falsifies.
- Failure decomposition: ≥5% contract-unique mass (bootstrap CI) for semantic strength claim.
- Fixed budgets + saturation curve + τ ≤ 0.6 + ΔR² ≥ 0.10 for orthogonality.

---

### Exchange 15

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Vera's full experimental protocol is rigorous, and I need to assess total implementation burden to confirm this is feasible as a single study (not a multi-year research program).

**Experiment A (oracle isolation, static inputs):** Load EvalPlus's published test inputs (JSON, publicly available at evalplus/evalplus). For each ContractEval task, find matching HumanEval+/MBPP+ test inputs (ContractEval is a subset, so there's direct mapping). Execute each LLM-generated program against (1) ground-truth equality check and (2) ContractEval pre/post-condition assertions. Record per-sample outcomes. Implementation: ~3 days. Zero new data generation.

**Reference soundness check:** Run Hypothesis (5k examples, fixed seed) against ContractEval reference implementations. Flag tasks with violations. Implementation: ~1 day. Quarantine up to 5% of tasks without affecting study validity (expected rate near zero based on ContractEval authors' methodology).

**Experiment B (adaptive PBT):** For each (model, task) pair, run Hypothesis with icontract-hypothesis strategy inference for 5k examples or 60s. 5 models × 364 tasks × 10 samples/model = 18,200 contract-checking runs. Wall-clock: ~30 min for local models on GPU, ~2h for API-gated closed models (async batching). Implementation: ~4 days including API integration via evalplus backends.

**Contract richness audit (AST analysis):** Parse ContractEval contracts with Python's `ast` module. Classify by: `all()`/`any()` usage (universal), cross-variable references, structural invariants. ~2 hours to implement, zero human annotation.

**Statistics:** All analyses are standard numpy/scipy. Wilcoxon signed-rank test for paired differences. Bootstrap CI via scipy. Kendall τ via scipy.stats.kendalltau. Regression via sklearn/statsmodels. ~1 day.

**Total implementation time:** ~10-12 working days for a skilled ML engineer familiar with evalplus and hypothesis. ~$50-100 API budget for closed models. All tools pip-installable. No new benchmarks. No human annotators. No synthetic data.

This study is feasible, well-scoped, and can produce publication-ready results in 2-3 weeks. The implementation stack is mature and every component has been validated in production use (evalplus/NeurIPS, hypothesis/production ecosystems, ContractEval/ACL).

**Key Points:**
- Total implementation: ~10-12 days + $50-100 API cost
- Every component pip-installable, every dataset publicly available
- Experiment A requires zero new data generation — pure re-evaluation of existing EvalPlus inputs

---


---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The execution-based contract-strength gap is genuinely novel: no published study applies Python-native contract checking across multiple LLM families on ContractEval. The contract-unique failure category (output-equal but contract-violating) represents a qualitatively new evaluation signal — programs that satisfy finite test equivalence but violate universal behavioral properties. The cross-model contract violation table is an unmeasured axis in the LLM evaluation literature.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is now fully falsifiable with pre-registered, quantitative thresholds: Wilcoxon p < 0.01 for oracle strength, ≥5% absolute contract-unique mass, Kendall τ ≤ 0.6 for orthogonality, ΔR² ≥ 0.10 in regression, zero reference violations for soundness. Each prediction has an explicit falsifier. The two-experiment structure (oracle isolation vs. adaptive PBT) cleanly separates oracle strength from input generation strategy.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Three distinct contribution tiers: (1) evaluation science — demonstrates contracts provide oracle strength beyond dense differential testing; (2) LLM benchmarking — first cross-model contract-satisfaction ranking; (3) deployment tool — 100% tractable alternative to Z3. The study is well-positioned in a nascent area (ContractEval has only 1 citation at publication). If the hypothesis holds, it reframes code correctness evaluation for specification-critical deployments.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Full implementation in ~10-12 working days, $50-100 API cost, all tools pip-installable. Experiment A requires zero new data (re-evaluates existing EvalPlus inputs against ContractEval predicates). Experiment B has precise budgets (5k examples, fixed seeds, 60s wall-clock). No new benchmarks, no human annotation, no synthetic data. Every component validated in production.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion has converged on **H-ContractStrength-v2**: a measurement study demonstrating that execution-based contract checking (Hypothesis PBT with icontract-hypothesis strategy inference) provides a semantically stronger oracle than dense differential testing for evaluating LLM-generated code on ContractEval's 364 HumanEval+/MBPP+ tasks.

**Core claim:** For LLM-generated programs that pass all unit tests, Hypothesis-based contract checking reveals a contract-strength gap characterized by three falsifiable predictions: (P1) ≥10% additional failures over matched EvalPlus differential testing (with ≥5% from contract-unique violations — programs output-equal to ground truth but failing universal properties); (P2) ranking orthogonality with Kendall τ ≤ 0.6 and ΔR² ≥ 0.10 beyond pass@1⋆; (P3) ≥10% absolute gap between best and worst model families on contract-satisfaction rate.

**Mechanism:** LLM-generated code satisfies finite test equivalence by memorizing or correctly computing the output on training-distribution inputs. But contracts encode universal properties (relational invariants, structural guarantees, quantified conditions over all inputs) that finite tests cannot exhaust. Hypothesis explores the input space systematically beyond test coverage, finding inputs where the LLM's implementation fails the universal property despite matching ground truth on provided tests. This is the same mechanism that enabled h-e1's 7.42% violation rate — now applied to all 364 problems (100% tractable) instead of the 25.82% Z3-tractable subset.

**Experimental approach:** Two experiments. Experiment A: oracle isolation using EvalPlus's static 764-test-per-task inputs re-evaluated under contract oracle (zero new data). Experiment B: adaptive Hypothesis PBT with 5k examples per program, fixed seeds, icontract-hypothesis strategy inference. Oracle soundness validated against reference implementations first. Contract richness stratified by AST analysis. Cross-model comparison: GPT-4o-mini, Claude-3-haiku (closed), DeepSeek-Coder-V2-Lite, CodeLlama-13B, CodeLlama-34B (open).

**What this avoids from h-e1:** No SMT encoding. No Z3. No tractability ceiling. Execution-based checking is 100% tractable by construction for Python-native contracts.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** EvalPlus's static inputs were optimized for differential mismatches, not contract violations. If the oracle-isolation gap is small on static inputs but large under adaptive PBT, the gain is from smarter search, not oracle semantics. The experiment must report both separately.
- **Concern 2:** Contract richness gradient must be demonstrated — richer contracts should yield higher contract-unique failure rates. If the gradient is flat, the universal-property mechanism is weakened.
- **Mitigation Strategy:** Commit to the dual-experiment structure (A: static oracle isolation, B: adaptive PBT), report both, and include AST-based contract richness stratification in all analyses. Oracle soundness check against reference implementations quarantines defective contracts before any model evaluation.

