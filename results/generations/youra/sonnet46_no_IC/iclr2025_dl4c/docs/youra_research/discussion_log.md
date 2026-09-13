# Phase 2A Discussion Log
## Gap 1: No Controlled Comparison of Execution-Filtered SFT Data at Equal Token Budget

**Date:** 2026-08-04
**Architecture:** Self-Play Loop (Claude-only, IC-ablation — no external orchestrator)
**Execution Mode:** UNATTENDED
**Pipeline Project ID:** df86f02e-1a93-4ce4-97db-2c4ecfdc3b3c
**Recursive Entry:** v7 (ROUTED_TO_PHASE_2A from Phase 4 H-E1 failure)

---

### Previous Failure / Routing Context

**Source:** `.serena/memories/failure_h-e1.md` (2026-08-04)
**Routing Type:** ROUTED_TO_PHASE_2A
**Failed Hypothesis:** H-E1 (EXISTENCE gate — MUST_WORK)

**Failure Summary:**
Signal density feasibility scan for APPS interview problems failed to find matched subset where both `compile_rate` AND `test_pass_rate` fall in [0.15, 0.45] with Qwen2.5-Coder-7B (G=8).
- Matched problems (both signals in window): 0 / 200
- Compile rate mean: 11.6% — only 11/200 in window
- Test-pass rate: 0.0% — APPS `testing_util.reliability_guard()` blocks subprocess in nested agent context
- Joint window constraint [15%, 45%] simultaneously: 0/200 achievable

**Root Causes:**
1. APPS harness subprocess isolation failure (environment issue)
2. Compile rate too low for interview-level APPS problems
3. Joint window constraint too strict given model capability on APPS difficulty

**Prohibited Redesign Directions (must avoid):**
- APPS interview-level problems as training corpus
- RL post-training via execution feedback loop
- Joint compile+test signal window as feasibility gate
- Nested subprocess execution environments

**New Direction (Phase 1 validated):**
Switch to SFT data filtering on The Stack Python corpus. Evaluate on HumanEval + MBPP. Use `compile()` AST-check for compile gate (no subprocess), `exec()` + test runner for functional gate. No RL, no APPS, no signal window feasibility scan.

---

## Research Briefing

**Research Question:** Does execution-based filtering (compile-only or compile+test-pass) of The Stack Python corpus improve SFT performance on HumanEval and MBPP compared to unfiltered SFT at equal token budget?

**Gap Being Addressed (Gap 1):** No controlled comparison exists of unfiltered / compile-only / compile+test SFT filtering on The Stack Python at equal token budget on HumanEval + MBPP.

**Key Supporting Evidence:**
- EffiCoder [Zeng et al., 2024]: Execution-selected SFT → Qwen2.5-Coder-7B 44.8% → 57.7% HumanEval (+13pp) — strongest direct evidence
- phi-1 [Gunasekar et al., 2023]: Quality > quantity at equal token budget; GPT-4 curation method (not execution-based)
- StarCoder [Li et al., 2023]: Heuristic-only filtering on The Stack; no execution gate; 40% HumanEval baseline
- OpenCodeInstruct [2025]: Execution feedback + quality filtering → HumanEval/MBPP improvement across 1B/3B/7B
- Arctic-SnowCoder [2024]: Three-phase quality filtering; quality-task alignment is critical

**Implementation Stack:**
- Corpus: The Stack Python (BigCode)
- Filtering: `compile()` AST check + `exec()` + unittest runner (opc_data_filtering framework)
- Model: Qwen2.5-Coder-1.5B or Qwen2.5-Coder-7B (same family)
- Eval: HumanEval pass@1 + MBPP pass@1 via lm-evaluation-harness

**Feasibility Constraints:**
- Must use existing real datasets (The Stack Python) ✓
- Must use existing benchmarks (HumanEval, MBPP) ✓
- No new benchmarks, rubrics, or scoring frameworks
- No synthetic data
- No human annotation

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we stopped thinking about this as merely a data-cleaning problem and reframed it as *information density amplification*? The Stack Python contains billions of tokens, but the signal quality varies enormously. When we apply execution-based filtering, we're not just removing bad code — we're selecting for a latent property the model can actually learn from: syntactic and semantic correctness co-occurring with a solution pattern.

Here's what excites me about Gap 1: the comparison design itself is the novelty. The field has phi-1 showing quality matters [Gunasekar et al., 2023], but that used GPT-4 as a quality oracle — a circular argument (one LLM curates data for another). Execution filtering is *model-agnostic*: compile() and unit tests are objective oracles. And crucially, EffiCoder [Zeng et al., 2024] demonstrated +13pp pass@1 on HumanEval by selecting for execution correctness at *inference* time — but nobody has applied that same correctness signal to *training data selection* at scale.

What if the mechanism is this: execution-filtered training data trains the model to occupy a region of weight space where syntactically and semantically correct code is the *attractor*? The model doesn't just learn more correct patterns — it learns to treat correctness as a distributional expectation. This predicts that compile-only filtering should give partial gains (syntactic attractor), while compile+test filtering should give larger gains (semantic attractor).

NOW we're onto something! The three-condition ablation — unfiltered, compile-only, compile+test — with equal token budget is genuinely novel because no existing work controls for token count while varying execution filter strictness. The cristinaimprota ICPC 2025 pipeline gives us The Stack Python SFT infrastructure. The opc_data_filtering framework gives us the compile gate. This is executable right now.

**Key Points:**
- Reframe: execution filtering as information density amplification, not data cleaning
- Mechanism hypothesis: execution-filtered data creates a *correctness attractor* in weight space
- Equal-token-budget design isolates quality signal from quantity reduction (controls the confound phi-1 didn't)
- Gap is real and immediately executable with existing tools

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's enthusiasm is infectious, but I need to stress-test that "correctness attractor" mechanism claim before we build a hypothesis on it. The evidence suggests execution filtering improves outcomes — EffiCoder's +13pp is striking — but the proposed *mechanism* is not yet established.

Here's my concern: EffiCoder [Zeng et al., 2024] selects at *inference time*, not training time. That's a fundamentally different intervention. At inference time, you're doing repeated sampling and selecting the best completion — you're exploiting the model's existing distribution. At training time, you're shaping that distribution. The fact that correctness selection works at inference time doesn't directly imply that training on pre-filtered correct data produces the same effect. The causal chain needs to be specified.

What would actually disprove the "correctness attractor" hypothesis? If compile-only filtering yields zero improvement while compile+test filtering yields large improvement, that suggests it's functional correctness (semantics) not syntactic correctness creating the signal — which contradicts the attractor framing. If *random* subsampling of equal token budget performs as well as execution-filtered data, that means the quality signal is irrelevant and it's just a data quantity effect.

The testable form must be: (1) execution-filtered SFT outperforms unfiltered SFT at equal token count on HumanEval pass@1 and MBPP pass@1; (2) compile+test outperforms compile-only by a measurable margin; (3) execution-filtered outperforms length-matched random subsampling. Each condition must have a pre-specified threshold — say, ≥2pp absolute improvement on HumanEval pass@1 — to be declared a success.

The measurement approach is theoretically sound: HumanEval and MBPP have automated test execution, so pass@1 is objective. But we need to specify the exact filtering pipeline: what's the Python compile gate? `compile(code, '<string>', 'exec')` catches syntax errors only. The functional gate needs unit tests — but The Stack Python corpus doesn't come with unit tests! This is the critical implementation question.

**Key Points:**
- The "correctness attractor" mechanism needs precise causal specification — inference-time vs. training-time filtering are different
- Falsification conditions must be pre-specified: random subsampling baseline, per-condition success thresholds
- Critical gap: The Stack Python lacks unit tests — how does the compile+test condition get its test suite?

---

### Exchange 3

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Vera raises the pivotal technical question: The Stack Python doesn't ship with unit tests. This is the key feasibility challenge, and I want to be precise about what it implies for the experimental design.

The compile-only condition is technically clean: `compile(code, '<string>', 'exec')` is a well-validated AST check, no subprocess needed, scales to millions of files. The opc_data_filtering framework has exactly this gate. Feasibility: CONFIRMED for compile-only.

The compile+test condition requires a test source. Three options exist: (1) The cristinaimprota pipeline uses function-level pairs from The Stack where docstrings serve as specification — we could extract test cases from docstrings using a deterministic parser (no LLM), but coverage would be sparse. (2) OpenCodeInstruct's adorkin/filtered dataset already has `tests_execution_status` and `average_test_score` fields — this is pre-filtered instruction data, not raw Stack Python, but it's a valid execution-filtered SFT corpus. (3) Apply execution-filtering to a corpus that *does* have tests: CodeContests, MBPP training split, HumanEval training examples (though HumanEval has no training split).

I think option (2) is the most feasible: use OpenCodeInstruct (instruction-tuning format) for the compile+test condition, The Stack Python (opc_data_filtering compile gate) for the compile-only condition, and random subsampling from The Stack for the unfiltered baseline. The token-budget matching is straightforward: train on N tokens of each.

The mechanism question Prof. Vera raises — whether training on pre-filtered correct data shapes the distribution — is well-founded in curriculum learning literature [Bengio et al., 2009]. Training exclusively on syntactically/semantically valid examples removes negative interference from malformed patterns. This is mechanistically sound.

**Key Points:**
- Compile-only gate: technically confirmed, no subprocess needed
- Compile+test gate: The Stack lacks tests, but OpenCodeInstruct already provides execution-filtered instruction data with test status fields
- Feasibility: CONFIRMED for a hybrid design using available filtered datasets
- Mechanism (curriculum learning / negative interference removal) is theoretically grounded

---

### Exchange 4

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what does this study actually contribute to the field, and would ICML/ICLR reviewers care?

The significance case is genuinely strong, and I want to map it out carefully. The field currently has two data quality paradigms: (1) GPT-4-curated data (phi-1, WizardCoder) — expensive, opaque, not reproducible without API access; (2) Heuristic filtering (StarCoder, DeepSeek-Coder) — scalable but quality signal is indirect. Execution-based filtering is a *third paradigm*: objective, model-agnostic, grounded in the task's success criterion. If we can show it works for SFT data selection, it becomes a principled tool for any lab — including those without GPT-4 API budgets.

The equal-token-budget design is the methodological contribution. Prior work conflates quality improvement with quantity reduction. phi-1 used 1B high-quality tokens vs. more random tokens — but more tokens would also change the distribution. The cristinaimprota ICPC 2025 study used function pairs from The Stack without matching token counts across conditions. Our ablation controls this explicitly.

However, Prof. Pax's hybrid design concern (OpenCodeInstruct for compile+test condition vs. The Stack for compile-only) introduces a confound: the two conditions differ in corpus domain (instruction-tuning format vs. raw function code) in addition to filtering level. This matters because instruction-formatted data is known to be more SFT-friendly. If compile+test outperforms compile-only in that design, we can't attribute the gain to execution filtering.

The question we must ask: can we achieve all three conditions from a *single* corpus with consistent format? The answer matters for scientific cleanliness. Dr. Nova's original framing — three conditions from The Stack Python — is methodologically cleaner if we can solve the test availability problem.

**Key Points:**
- Execution filtering as third paradigm (beyond GPT-4 curation and heuristics): genuine field contribution
- Equal-token-budget design controls the quantity-quality confound: methodological contribution
- Prof. Pax's hybrid design introduces a corpus-format confound — single-corpus design preferred for clean comparison
- Significance: HIGH if we can demonstrate the effect cleanly on HumanEval + MBPP

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, and I think we can thread the needle between Prof. Pax's feasibility concern and Dr. Sage's methodological purity requirement. Let me synthesize what's emerged.

The corpus confound is solvable. Here's the key insight: we don't need *function-level unit tests* from The Stack to define a compile+test condition. We can use a looser but valid functional correctness signal: **execution without error**. Specifically: `compile()` catches syntax errors; `exec()` with a timeout catches runtime errors (NameError, TypeError, IndexError, etc.); and a script-level execution check (does the file run without crashing?) filters out broken dependencies. This is a three-tier execution filter, all from within The Stack Python corpus:

- **Tier 0 (Unfiltered):** Random subsample to N tokens
- **Tier 1 (Compile-only):** `compile(code, '<string>', 'exec')` succeeds → retain → subsample to N tokens
- **Tier 2 (Exec-clean):** `compile()` + `exec()` without runtime error → retain → subsample to N tokens

This gives three conditions from a *single corpus* in *consistent format* (raw Python functions from The Stack). The exec-clean gate is a valid proxy for functional correctness — it's weaker than unit tests but stronger than syntax-only. And critically: it avoids the subprocess isolation problem that killed H-E1, because `exec()` within the main process is not blocked by `reliability_guard()`.

NOW THAT'S stronger! The hypothesis becomes: under equal token budget from The Stack Python, SFT with exec-clean-filtered data outperforms compile-only-filtered, which outperforms unfiltered, on HumanEval pass@1 and MBPP pass@1 with Qwen2.5-Coder-1.5B/7B.

**Key Points:**
- Three-tier exec filter (compile, exec-without-error, exec-clean) from single corpus solves corpus confound
- `exec()` in-process (not subprocess) avoids H-E1's `reliability_guard()` failure
- Single corpus + single format = clean three-condition comparison
- Hypothesis now has clear causal ladder: syntax correctness → runtime correctness → benchmark performance

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down. I want to attack two claims specifically.

**Attack 1: The exec() gate is not what you think it is.** Dr. Ally proposes `exec()` in-process to catch "runtime errors." But The Stack Python contains functions, not scripts. Running `exec()` on an isolated function definition does *not* execute the function body — it defines the function in the namespace and returns. To actually test runtime correctness, you'd need to *call* the function with valid arguments. Without a test harness or argument generation, `exec()` on a function definition catches almost nothing beyond syntax (which `compile()` already catches). The "exec-clean" condition may be functionally identical to the "compile-only" condition.

**Attack 2: The equal-token-budget design has a survivorship bias problem.** Execution filtering retains, say, 30% of The Stack Python. You then subsample 30% of unfiltered data for the baseline. But those are different *distributions*: the filtered 30% are the "correct" programs; the random 30% include all difficulty levels and failure modes. Training on 30% correct programs is very different from training on 100% programs — but also very different from training on 30% random programs. The relevant comparison isn't "equal tokens from filtered vs. equal tokens from random" — it's "what is the marginal value of the filtering step?" This requires a 4-way design: (a) full unfiltered corpus, (b) full compile-only corpus, (c) full exec-clean corpus, (d) token-matched subsamples. Without this, you conflate filtering effect with subsample-size effect.

What would convince me: run a pilot on 1,000 Stack Python files, try `exec()` on function definitions, count what fraction are caught that `compile()` misses. If the answer is <5%, the two tiers are redundant.

**Key Points:**
- `exec()` on function definitions (not calls) catches negligible additional errors beyond `compile()` — exec-clean ≈ compile-only
- Equal-token-budget design conflates filtering quality signal with subsample distribution shift
- Mitigation needed: (1) function invocation or doctest extraction for runtime testing; (2) 4-way design or explicit confound analysis

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's attack on the exec() gate is valid and I have to concede it — but this is where creative thinking rescues us! What if we *exploit* The Stack's existing structure rather than trying to execute arbitrary functions?

Here's the insight: The Stack Python includes *doctest* strings in many functions. Doctests are executable test cases embedded in the docstring — `>>> function(args)` / `expected_output`. Python's `doctest` module can run these without any test generation. Extracting and running doctests gives us genuine functional correctness testing on a subset of The Stack Python that has doctests. This is a legitimate, in-process execution filter that avoids subprocess isolation.

Additionally, The Stack Python's raw files include many *scripts* (not just function definitions) — `if __name__ == "__main__":` blocks are runnable. `exec()` on whole files with `__main__` guard actually does execute. These two categories — doctest-bearing functions and executable scripts — form a valid compile+test subset.

The hypothesis refinement: our three conditions come from different data strata of The Stack Python: (0) unfiltered sample, (1) compile-only stratum, (2) doctest-passing stratum (functional correctness via embedded tests). We accept that the compile+test condition requires doctest presence — this is a sample bias, but it's *defined* and *measurable*.

NOW we're onto something! The doctest approach also addresses Prof. Rex's 4-way design concern: we can compare compile-only-doctest-subset (same files as compile+test, but without the functional test gate) vs. compile+test-doctest-subset to isolate the functional filtering effect within the same population.

**Key Points:**
- Doctest extraction: legitimate functional execution testing from within The Stack, no subprocess, no test generation
- Script-level exec for `__main__` files: valid runtime execution gate for a defined stratum
- Within-stratum comparison (compile-only-doctest-subset vs. compile+test-doctest-subset) controls for population overlap
- Prof. Rex's exec() concern fully addressed

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

The doctest approach addresses Prof. Rex's exec() concern, but I need to make the predictions precise so we can actually run this study.

The evidence suggests the doctest-bearing stratum of The Stack Python is a minority — estimates range from 5-15% of functions in open-source Python repositories have doctests. This has two implications: (1) the compile+test condition will have substantially fewer candidate files than the compile-only condition, making equal-token-budget sampling from a different-sized pool; (2) doctest-bearing functions may be systematically different from the average Stack Python function (libraries with better documentation practices, teaching repositories, standard library contributions) — this is the survivorship bias Prof. Rex mentioned.

To make this falsifiable, I propose these specific predictions with measurable criteria:

**P1 (Primary — must hold):** After SFT on Qwen2.5-Coder-1.5B, compile+test-filtered data (doctest-passing stratum) outperforms token-matched unfiltered data on HumanEval pass@1 by ≥2pp absolute. Falsification: ΔHumanEval < 2pp absolute, or improvement is within noise (paired bootstrap p > 0.05).

**P2 (Secondary — ordering):** compile+test-filtered ≥ compile-only-filtered ≥ unfiltered on HumanEval pass@1. Falsification: ordering violated (compile-only ≥ compile+test, or unfiltered ≥ either).

**P3 (Confound control):** compile-only-doctest-subset outperforms compile-only-full-stack by ≤1pp — i.e., the doctest stratum's edge comes from functional filtering, not doctest-stratum selection bias. Falsification: ΔP3 > 1pp, indicating stratum selection dominates.

These three predictions together can distinguish the mechanism (execution filtering as quality signal) from the confound (doctest stratum = better documentation culture).

**Key Points:**
- P1: ≥2pp HumanEval improvement (compile+test vs. unfiltered, equal token budget)
- P2: Ordering: compile+test ≥ compile-only ≥ unfiltered
- P3: Stratum confound check: compile-only-doctest-subset ≈ compile-only-full-stack (within 1pp)
- Doctest stratum is 5-15% of The Stack Python — feasibility depends on available doctest-bearing files

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Vera's prediction structure is clean and I want to validate the technical feasibility of each condition's implementation.

**Compile-only condition:** `compile(code, '<string>', 'exec')` — runs in-process, scales to millions of files, well-validated. Feasibility: CONFIRMED. opc_data_filtering implements this exactly.

**Doctest-passing condition:** Python's `doctest.testmod()` or `doctest.run_docstring_examples()` — in-process, deterministic, no subprocess. The challenge is extraction: we need to parse function docstrings, identify `>>>` patterns, run them. The `doctest` standard library handles this without external tools. Key technical concern: some doctests depend on state from previous tests or module-level imports — `doctest` handles this within its execution context. Feasibility: CONFIRMED in-process.

**The quantification question:** How many files in The Stack Python have valid doctests? This is empirically answerable. A 10,000-file sample of The Stack Python (publicly available on HuggingFace as `bigcode/the-stack-dedup`) can be scanned in minutes. If <2% have doctests, the compile+test condition generates fewer than 200M tokens from the full corpus — potentially insufficient for meaningful SFT comparison. But based on Python ecosystem patterns (NumPy, SciPy, standard library), 5-10% is a reasonable estimate, which would yield ~1-2B token pool even from a 20B token corpus subset. At 500M tokens per training run, this is feasible.

**Stratum confound check (P3):** Prof. Vera's P3 requires training on compile-only-doctest-subset — same files as the compile+test condition but without the doctest gate. This is trivially achievable: scan for doctest presence, then train on (a) all doctest files (no test execution) vs. (b) doctest files that pass tests. Feasibility: CONFIRMED.

**Key Points:**
- All three conditions achievable in-process using standard library (`compile`, `doctest`)
- Doctest prevalence in The Stack: ~5-10% estimated; needs empirical verification on 10k-file sample
- P3 stratum check design is straightforward and adds critical confound control
- Full feasibility: CONFIRMED pending doctest prevalence pilot

---

### Exchange 10

🎯 **Dr. Sage** (Research Impact Evaluator):

This matters because — and I want to be direct about this — we're not just answering whether data filtering works (the field already suspects it does). We're answering *which filtering criterion is sufficient* and *why*.

The three-prediction structure Prof. Vera built, combined with Prof. Pax's feasibility confirmation, gives us a study that addresses a real methodological gap. Let me situate its contribution:

The best baseline to beat is EffiCoder [Zeng et al., 2024] — +13pp HumanEval on Qwen2.5-Coder-7B. But EffiCoder filtered instruction-tuning samples, not raw pretraining/SFT corpus data, and didn't control token budget. Our contribution: same *principle* (execution filtering) applied to raw corpus SFT at equal token budget, with a clean three-condition ablation. This is additive to EffiCoder, not competitive.

The broader significance: if P1 holds (≥2pp from compile+test filtering), it validates execution-based corpus filtering as a principled alternative to GPT-4-based curation for labs without API budgets. If P3 holds (doctest stratum ≈ random Stack Python sample minus stratum bias), it tells us the quality signal is in the *testing*, not the *documentation culture*. That's a generalizable insight.

If P2 is violated (compile-only ≥ compile+test), the finding is equally important: syntax correctness alone captures most of the quality signal, and functional testing adds noise rather than signal. That would redirect the field toward compile-only filtering (cheaper, more scalable, no doctest dependency).

What opens up: a systematized corpus-filtering toolkit for code SFT — compile, exec-script, doctest, unit-test-inferred — with empirical grounding for when each tier pays off.

**Key Points:**
- Contribution is additive to EffiCoder: same principle at corpus scale with token budget control
- P1+P2+P3 together distinguish "execution filtering works" from "documentation culture confound"
- Both P2-violating and P2-confirming outcomes are publishable — negative result has clear interpretation
- Opens systematic corpus-filtering toolkit research direction

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Let me synthesize the discussion so far into the hypothesis that has emerged. What if we addressed the remaining concerns by explicitly embracing the doctest stratum as a defined scope boundary?

The strongest version of our hypothesis is:

*Under equal token budget from The Stack Python, SFT on execution-filtered data (compile-only or doctest-passing) outperforms SFT on unfiltered data of equal token count on HumanEval pass@1 and MBPP pass@1, because execution filtering selects training examples where code is syntactically and functionally consistent, reducing noise in the model's learning signal.*

The scope is explicitly: The Stack Python corpus, Python language, Qwen2.5-Coder-1.5B (primary) and 7B (secondary), SFT stage (not pretraining), HumanEval and MBPP benchmarks.

What's strengthened by the discussion:
1. **Mechanism is clear:** execution filtering as noise reduction in the training signal — programs that don't compile teach the model wrong syntactic patterns; programs that fail tests teach the model wrong logical patterns.
2. **Confound control is explicit:** P3 (stratum check) separates execution quality signal from documentation culture selection bias.
3. **Falsification is pre-specified:** Prof. Vera's P1-P3 with measurable thresholds.
4. **Implementation is confirmed feasible:** Prof. Pax verified all conditions are in-process with standard library.

The remaining open question is doctest prevalence — but Prof. Pax noted this is measurable in a pilot scan. If prevalence is too low (<2%), we fall back to compile-only as the primary comparison (Gap 1 RQ1, RQ2), which is still novel and answerable.

**Key Points:**
- Hypothesis: exec-filtered SFT > unfiltered SFT at equal token budget; mechanism = noise reduction in training signal
- Scope defined: The Stack Python, Python, Qwen2.5-Coder-1.5B/7B, SFT, HumanEval+MBPP
- Confound control explicit via P3 stratum check
- Fallback design (compile-only primary) if doctest prevalence insufficient

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally's synthesis is fair, but I have one remaining attack I want to raise before declaring convergence.

**The "noise reduction" mechanism claim is untestable as stated.** Saying execution filtering "reduces noise in the learning signal" is a post-hoc causal story, not a prediction. What would demonstrate noise reduction vs. alternative mechanisms? Two alternatives: (A) distribution shift — filtered data shifts the training distribution toward benchmark-style code, independently of correctness per se (survivorship bias of easily-solved problems); (B) coverage effect — filtered data concentrates token budget on a smaller vocabulary of correct patterns, improving fluency on a narrower distribution.

These alternatives predict: if A, then compile-only and compile+test should perform similarly to training on Python tutorial code (syntactically clean, easy programs). If B, then performance should plateau quickly as token count increases (already covers the relevant patterns). The present design doesn't distinguish these mechanisms from the "noise reduction" story.

However — and this is important — I accept that mechanism disambiguation is *Phase 2B/2C work*, not Phase 2A. The Phase 2A hypothesis only needs to establish *that* the effect exists (P1) and *which filtering tier is sufficient* (P2). The mechanism story can be refined. My remaining concern is that the Phase 2A hypothesis should not *commit* to a mechanism it can't test — instead, it should state "the mechanism is one of: noise reduction, distribution shift, coverage concentration" and leave it open for Phase 2B.

With that modification — agnostic mechanism statement — I'm satisfied. This is a testable, novel, feasible hypothesis that avoids all H-E1 failure modes.

**Key Points:**
- "Noise reduction" mechanism claim needs hedging — multiple mechanisms could produce the same effect
- Alternative mechanisms (distribution shift, coverage concentration) predict similar outcomes under P1/P2 design
- Mechanism disambiguation is Phase 2B work — Phase 2A should state effect without mechanism commitment
- With mechanism-agnostic framing: hypothesis is ACCEPTED by Prof. Rex

---

### Exchange 13

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's mechanism-agnostic refinement is exactly right, and it actually *strengthens* the hypothesis by making it more robust. Here's why: a mechanism-agnostic hypothesis that makes precise predictions (P1: ≥2pp, P2: ordering, P3: stratum check) is more falsifiable than a mechanistic hypothesis, because we're not giving ourselves an escape hatch ("oh, the mechanism is just distribution shift, not noise reduction, so the effect is still real even if…").

Let me also address one creative angle we haven't fully explored: what does it look like if the *compile-only* condition actually outperforms *compile+test* in some regime? Prof. Vera mentioned this as a falsification of P2, but it's actually a fascinating finding if true. It would mean: the doctest-passing stratum is *too* narrowly distributed (library utility functions, standard algorithms) and trains the model to be fluent on those patterns at the expense of broader code generation. Compile-only would capture a more diverse syntactic distribution.

This is a concrete prediction worth making explicit: if the doctest stratum prevalence is <5%, expect compile+test to underperform compile-only on MBPP (which has more diverse problem types than HumanEval). That's a testable, novel sub-prediction.

We now have a clean hypothesis: **Exec-FilteredSFT** — execution-filtered SFT from The Stack Python outperforms unfiltered SFT at equal token budget on HumanEval + MBPP, with filtering strictness (compile-only vs. doctest-passing) determining the magnitude and distribution of gains. This is novel, immediately executable, avoids all H-E1 failure modes, and has pre-specified falsification criteria.

**Key Points:**
- Mechanism-agnostic framing increases robustness, not weakness
- Compile-only ≥ compile+test on MBPP if doctest stratum is too narrow: concrete testable sub-prediction
- Final hypothesis name: **Exec-FilteredSFT**
- All three conditions feasible, all failure modes from H-E1 avoided

---

### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect):

The evidence suggests we're close to convergence. Let me formally check the six criteria before continuing.

SPECIFIC: ✅ — Core claim: exec-filtered SFT from The Stack Python outperforms unfiltered SFT at equal token budget on HumanEval + MBPP (with Qwen2.5-Coder-1.5B primary, 7B secondary). Clear.

MECHANISM: ✅ — Mechanism stated as mechanism-agnostic (one of noise reduction, distribution shift, coverage concentration) — testable via P3 stratum check. Clear causal chain: execution filtering → retention of syntactically/functionally consistent examples → reduced training noise / improved distributional alignment → higher pass@1.

PREDICTIONS: ✅ — P1 (≥2pp HumanEval, paired bootstrap p < 0.05), P2 (ordering: compile+test ≥ compile-only ≥ unfiltered), P3 (stratum confound check within 1pp). All three have explicit falsification conditions.

NOVELTY: ✅ — No prior work: (a) applies execution filtering to raw SFT corpus (vs. instruction data), (b) controls equal token budget, (c) compares compile-only vs. compile+test within single corpus, (d) includes stratum confound check. Gap confirmed by Phase 1 research.

FEASIBILITY: ✅ — All conditions in-process (compile(), doctest standard library), single corpus (The Stack Python), standard eval (HumanEval + MBPP via lm-evaluation-harness), existing models (Qwen2.5-Coder). Prof. Pax confirmed.

OBJECTIONS: ✅ — Prof. Rex's exec() concern addressed via doctest; mechanism commitment concern addressed via mechanism-agnostic framing; corpus confound addressed via P3 stratum check; survivorship bias addressed as explicitly bounded scope.

All 6 criteria PASS. All 6 personas have spoken (Dr. Nova: exchanges 1, 7, 13; Prof. Vera: 2, 8, 14; Prof. Pax: 3, 9; Dr. Sage: 4, 10; Dr. Ally: 5, 11; Prof. Rex: 6, 12). Minimum 15 exchanges not yet reached — continuing.

**Key Points:**
- All 6 convergence criteria met at Exchange 14
- All 6 personas have spoken
- Exchange count (14) below min_exchanges (15) — must continue

---

### Exchange 15

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Since we're continuing past the preliminary convergence check, let me use this exchange to address a practical implementation detail that could make or break the experiment: **token budget matching at the filtering-ratio level**.

Here's what worries me: if The Stack Python compile-only pass rate is, say, 70%, and doctest-pass rate is 8%, then to get equal token budget N across all three conditions, we need to subsample from very different pool sizes. Specifically:
- Unfiltered pool: 100% of corpus → random subsample to N tokens
- Compile-only pool: 70% of corpus → random subsample from that 70% to N tokens
- Doctest-passing pool: 8% of corpus → if 8% corpus < N tokens, we have a budget ceiling

The feasibility question is: is 8% of the available Stack Python large enough to give N tokens of training? The Stack Python (deduplicated) contains ~70B tokens. 8% = ~5.6B tokens. At 500M token training budget (reasonable for a research SFT study), we have 11× headroom. At 1B tokens, still 5.6× headroom. Feasibility: CONFIRMED even at doctest prevalence of 5%.

One additional mechanism point: the proposed causal chain has four steps: (1) execution filtering selects correct programs; (2) SFT on correct programs reduces exposure to syntactically/functionally invalid patterns; (3) reduced invalid pattern exposure improves model's distributional alignment with benchmark-style correct code; (4) HumanEval/MBPP pass@1 improves. Each step is falsifiable via the P1-P3 predictions or intermediate measurement (e.g., measuring n-gram overlap between filtered training data and HumanEval test cases for step 3 validation).

**Key Points:**
- Token budget feasibility at 5% doctest prevalence: ~5.6B tokens available → confirmed at 500M-1B SFT budget
- Four-step causal chain fully specified (filtration → noise reduction → distributional alignment → benchmark improvement)
- Each causal step measurable — intermediate metrics available for mechanism analysis in Phase 2B
- Implementation fully confirmed: no subprocess, no external LLM, no new infrastructure

---

## Convergence Check @ Exchange 15

**All 6 convergence criteria: PASS**
**All 6 personas have spoken: YES**
**Exchange count: 15 ≥ min_exchanges (15): YES**

- SPECIFIC: PASS — "exec-filtered SFT from The Stack Python outperforms unfiltered SFT at equal token budget on HumanEval + MBPP with Qwen2.5-Coder-1.5B/7B" [Exchange 11, 14]
- MECHANISM: PASS — Four-step causal chain (filtration → noise reduction → distributional alignment → benchmark) stated mechanism-agnostically; P3 stratum check tests mechanism vs. confound [Exchanges 11, 12, 15]
- PREDICTIONS: PASS — P1 (≥2pp HumanEval, p<0.05), P2 (ordering), P3 (stratum check within 1pp), with explicit falsification for each [Exchanges 8, 14]
- NOVELTY: PASS — No prior work applies exec filtering to raw corpus SFT at equal token budget with compile vs. doctest comparison [Exchanges 4, 10, 14]
- FEASIBILITY: PASS — All conditions in-process (compile(), doctest), token budget feasibility at 5% prevalence confirmed, standard eval stack [Exchanges 3, 9, 15]
- OBJECTIONS: PASS — exec() concern (doctest solution), mechanism commitment (agnostic framing), corpus confound (P3), survivorship bias (scoped) [Exchanges 6, 12, 14]

**Verdict: CONVERGED at Exchange 15**

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Creative Novelty Explorer):
- **Verdict:** STRONG
- **Assessment:** The Exec-FilteredSFT hypothesis is genuinely novel: no prior work applies execution-based filtering to raw SFT corpus data at equal token budget with a clean three-condition ablation. The doctest-based compile+test condition is creative and practically executable. The mechanism-agnostic framing is scientifically honest while still making precise predictions. This opens a new line of work on principled corpus filtering without GPT-4 dependence.

🔬 **Prof. Vera** (Rigorous Validation Architect):
- **Verdict:** STRONG
- **Assessment:** P1-P3 predictions have explicit numerical thresholds and pre-specified falsification conditions. The P3 stratum confound check is methodologically rigorous — it distinguishes the filtering quality signal from documentation culture selection bias. The measurement approach (HumanEval/MBPP pass@1 via lm-evaluation-harness with paired bootstrap) meets my standards for scientific rigor.

🎯 **Dr. Sage** (Research Impact Evaluator):
- **Verdict:** STRONG
- **Assessment:** Execution-based corpus filtering as a third paradigm (beyond GPT-4 curation and heuristics) has high field impact if validated. Both confirming and disconfirming outcomes for P2 are publishable with clear interpretation. The study positions execution filtering as a scalable, model-agnostic alternative for labs without API budgets.

⚙️ **Prof. Pax** (Feasibility & Reality Checker):
- **Verdict:** STRONG
- **Assessment:** All conditions technically confirmed: compile() for syntax, doctest module for functional testing, both in-process without subprocess. Token budget feasibility confirmed at 5% doctest prevalence. The four-step causal chain is mechanistically sound. No fundamental technical barriers identified.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The Exec-FilteredSFT hypothesis emerged from this discussion: under equal token budget from The Stack Python corpus, supervised fine-tuning (SFT) on execution-filtered data — specifically, data passing either a compile-only gate (`compile()` AST check) or a doctest-passing gate (compile + `doctest` module execution) — outperforms SFT on unfiltered data of equal token count on HumanEval pass@1 and MBPP pass@1, using Qwen2.5-Coder-1.5B as the primary model and 7B as a secondary generalization check.

The mechanism is stated mechanism-agnostically: execution filtering retains syntactically and functionally consistent training examples, reducing exposure to malformed patterns. The specific mechanism pathway (noise reduction, distribution shift, or coverage concentration) is left for Phase 2B to disambiguate via intermediate metrics.

Three predictions with pre-specified thresholds: P1 (≥2pp HumanEval absolute improvement, compile+test vs. unfiltered), P2 (ordering: compile+test ≥ compile-only ≥ unfiltered on HumanEval), P3 (stratum confound control: compile-only-doctest-subset ≈ compile-only-full within 1pp). All H-E1 failure modes are avoided: no APPS, no RL, no subprocess isolation, no joint signal window constraint.

### Remaining Concerns

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):
- **Concern 1:** Doctest prevalence in The Stack Python is estimated but not empirically verified — if <3%, the compile+test condition may be too narrow for meaningful SFT comparison
- **Concern 2:** The mechanism story (noise reduction vs. distribution shift vs. coverage concentration) remains unresolved — Phase 2B should design intermediate measurements to distinguish these
- **Mitigation Strategy:** Run a doctest prevalence pilot on 10k Stack Python files before committing to the full experiment. If doctest prevalence < 3%, fall back to compile-only as primary condition (Gap 1 RQ1/RQ2 still answerable without the doctest tier). Design intermediate metrics for mechanism analysis: n-gram overlap between filtered training data and HumanEval/MBPP test cases (distribution shift hypothesis); learning curve analysis (coverage concentration hypothesis).
