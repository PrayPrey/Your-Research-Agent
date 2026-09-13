# Phase 2A Discussion Log
## Gap: No Systematic Empirical Comparison of Formal Constraint Types on LLM Code Correctness

**Gap ID:** Gap-1
**Priority:** HIGH | PRIMARY
**Architecture:** Self-Contained Tikitaka Loop (Independent-Controller Ablation)
**Execution Mode:** UNATTENDED
**Date:** 2026-08-26

---

## Briefing Context

**Research Question:** Can integrating formal method techniques measurably improve pass@k functional correctness of LLM-generated code on existing benchmarks?

**Selected Gap:** No published study systematically compares all four constraint tightness levels (none → syntax/grammar → type/static → SMT-semantic) on the same LLM models and benchmarks under controlled compute conditions.

**Key papers available:**
- Outlines (Willard & Louf 2023): FSM-based CFG/regex constrained decoding; no pass@k code comparison
- EvalPlus (Liu et al. 2023): HumanEval+/MBPP+ with stronger tests
- HumanEval (Chen et al. 2021): defines pass@k; unconstrained sampling baseline
- Self-Debug (Chen et al. 2023): execution feedback repair baseline
- Reflexion (Shinn et al. 2023): verbal feedback repair baseline
- SWE-bench (Jimenez et al. 2023) + SWE-agent (Yang et al. 2024): agentic benchmark

**Feasibility Constraints (Pipeline-Enforced):**
- No new benchmarks or rubrics
- No synthetic/future data
- No human evaluation or annotation
- Must test on existing real datasets and benchmarks

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

The gap here is genuinely unexplored and the framing opportunity is striking. Every practitioner using Outlines or Guidance for constrained decoding assumes the constraint helps — but nobody has run the controlled ablation. What if constraint tightness has a **non-monotone relationship** with pass@k? That would be the surprising, publishable finding: medium constraint (type-checking) outperforms full SMT-semantic constraint because SMT encoding forces over-specification that excludes valid solutions.

My proposal: focus on **Gap 1 as the core contribution** — a 2×4 factorial ablation across constraint levels (none / grammar / type+static / SMT) × model scales (7B / 70B parameter class), evaluated on HumanEval+ and MBPP+. The hypothesis I'd push: **grammar-constrained decoding yields modest pass@k gains (+3-8%) for small models but near-zero or negative gains for larger models**, because larger models have already internalized grammar as soft knowledge. This would explain why the community hasn't chased this — the effect may be model-size-dependent.

I'd further propose a **mechanism story**: constraint tightness removes low-quality probability mass at each token, but the benefit only materializes when the model's own token distribution has substantial probability mass in the invalid region. For large code models, this mass is already small. For smaller or generalist models, the constraint signal is stronger.

Concrete, testable, uses existing benchmarks and tools. This is the paper.

**Key Points:**
- Non-monotone constraint-correctness relationship as the surprising finding
- 2×4 factorial: constraint level × model scale
- Mechanism: constraint benefit scales inversely with model quality
- Fully implementable with Outlines + vLLM + HumanEval harness

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's framing is evocative but the falsifiability needs sharpening before we commit. Let me work through the testability issues.

The "non-monotone" prediction is vague as stated. For it to be falsifiable, we need exact operationalizations: (1) what counts as "grammar constraint" — Python AST-valid tokens only, or full CFG? (2) what counts as "type constraint" — mypy-valid tokens at generation time (infeasible), or post-hoc mypy filter? (3) what counts as "SMT-semantic" — Z3 pre-conditions on function signature, or full Hoare-triple verification? Each operationalization choice changes the experiment entirely.

More critically: **grammar-constrained decoding at inference time** (Outlines-style logit masking) is fundamentally different from **post-hoc repair loops** (Self-Debug, Z3-guided repair). Conflating them into a single "constraint tightness ladder" mixes two different intervention architectures. We should pick ONE architecture class for the primary hypothesis:
- **Architecture A:** Decoding-time constraint (grammar/type logit masking)
- **Architecture B:** Post-hoc repair loop (execution → static → SMT feedback)

These have different compute profiles, different failure modes, and different practical use cases. A single factorial conflating them will be nearly impossible to interpret cleanly.

My recommendation: primary hypothesis on **Architecture B (repair loops)** because it's more tractable — you can compare (A) execution-only repair, (B) execution+static-analysis repair, (C) execution+static+Z3-guided repair — all as post-generation steps, same decoding, fair compute budget per repair round. Benchmark: HumanEval+ with pass@1 after k repair rounds (k=3).

**Key Points:**
- Separate decoding-time constraints from post-hoc repair loops — don't conflate
- Architecture B (repair loops) more tractable for controlled comparison
- Operationalize exactly: execution-only vs execution+static vs execution+static+SMT
- pass@1 after k=3 repair rounds as primary metric

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Both perspectives are valuable. Let me assess the significance landscape.

The VerifAI workshop audience cares about the *verification* angle — they want to know if formal methods add value over execution testing. Prof. Vera's Architecture B framing (repair loop escalation: execution → static → SMT) maps perfectly to this audience's mental model. It's also directly actionable: a practitioner can add mypy to their repair loop today if the paper shows +5% pass@1 improvement.

From a significance standpoint, the key question is: **what is the minimum effect size that would matter?** For HumanEval+ (164 problems), a +3% absolute improvement in pass@1 corresponds to ~5 additional problems solved. This is marginal but publishable at a workshop. On MBPP+ (378 problems), same +3% = ~11 problems. More convincing. For a workshop paper, I'd set the significance bar at **+5% absolute pass@1 improvement on HumanEval+ and MBPP+ combined**.

The null result case is also valuable for VerifAI's stated openness: if execution-only repair is as good as adding static analysis, that's a meaningful negative result — saves practitioners from the overhead of mypy integration.

I want to raise one scope concern: **SWE-bench is too expensive** for a workshop paper validation. 500 instances × multiple repair rounds × multiple models = thousands of API calls. Keep the primary hypothesis on HumanEval+ and MBPP+, treat SWE-bench as optional stretch goal.

**Key Points:**
- Architecture B aligns with VerifAI audience (formal verification mindset)
- Primary benchmark: HumanEval+ + MBPP+ (affordable, sufficient effect size)
- SWE-bench is stretch goal only (too expensive for workshop)
- +5% absolute pass@1 as significance threshold
- Negative result also publishable per workshop charter

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me ground this in implementation reality. The discussion is converging on Architecture B (escalating repair loops), which is the right call. Here's what the implementation actually looks like and where the risks are.

**Feasible today:**
- Execution-only repair: run code → capture pytest/exec output → feed error to LLM → regenerate. This is Self-Debug [Chen et al. 2023]. Already implemented.
- Static analysis repair: run code → run mypy/ruff → feed type errors + linter warnings → LLM regenerates. Straightforward extension of Self-Debug.
- Z3-guided repair: run code → encode function contract as Z3 assertion → get counterexample → feed to LLM → regenerate.

**The Z3 step is the hard part.** Python programs from HumanEval have natural language docstrings but no formal pre/postconditions. Automatically deriving Z3 constraints from docstrings is a research problem in itself (EvoEval, DafnyBench territory). We have two options:
1. **Manual encoding for HumanEval problems** — HumanEval has 164 problems; manually writing Z3 specs for all is ~40 person-hours. Feasible but brittle.
2. **LLM-derived Z3 constraints** — ask the LLM to also generate a Z3 spec, then use it for verification. This changes the intervention (now the LLM generates spec + code), which is a different hypothesis.

My recommendation: **use LLM-derived Z3 constraints** (Option 2) and be explicit that the Z3 constraint is LLM-generated. This is feasible and actually more novel — we're testing whether LLM-generated formal specs can guide LLM code repair better than execution alone. The hypothesis becomes: "LLM-generated Z3 specs provide richer repair signal than execution errors."

Also: cap repair rounds at k=3. Each round = 1 LLM call. For HumanEval+ (164 problems) × 3 conditions × k=3 rounds × 3 seeds = ~4,400 LLM calls. At GPT-4o-mini pricing (~$0.15/1M tokens), this costs ~$10-15 total. Fully feasible.

**Key Points:**
- Z3 step requires formal specs — use LLM-generated Z3 constraints (novel + feasible)
- Execution-only and static-analysis repair steps are straightforward
- Total compute: ~4,400 LLM calls = ~$10-15 at GPT-4o-mini pricing
- k=3 repair rounds is the right cap
- Manual Z3 spec writing is feasible but brittle — LLM-derived is better

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

The discussion has crystallized beautifully. Let me synthesize and strengthen the emerging consensus hypothesis.

**Core Claim Emerging:** Adding formal method feedback to LLM repair loops — specifically, escalating from execution-only → execution+static-analysis → execution+LLM-generated-Z3 — produces a measurable, monotonically increasing improvement in pass@1 on HumanEval+ and MBPP+.

The mechanism Dr. Nova identified (constraint removes invalid probability mass) combines with Prof. Vera's architecture distinction and Prof. Pax's feasibility framing to give us a clean experimental design. Let me sharpen the hypothesis into falsifiable form:

**H: Under Python code generation on HumanEval+ and MBPP+, if repair loops are augmented with progressively richer formal feedback (execution-only → execution+mypy → execution+mypy+LLM-Z3), then pass@1 after k=3 repair rounds increases monotonically across conditions, because richer feedback provides more targeted correction signal that narrows the LLM's next-attempt distribution toward valid solutions.**

This is testable with existing tools. The null hypothesis is that all three conditions achieve equivalent pass@1 after k=3 rounds — i.e., execution feedback alone is as informative as formal analysis.

One strengthening element: we should test on BOTH HumanEval+ AND MBPP+ to show the effect generalizes. If the improvement appears on both benchmarks, the claim is stronger. If it only appears on one, that itself is informative.

I also want to preserve Dr. Sage's insight about negative results: even if pass@1 is flat across conditions, we measure **repair efficiency** (how many rounds to reach pass) and **error category analysis** (what types of bugs each feedback level catches). These secondary metrics add depth whether the primary result is positive or negative.

**Key Points:**
- Monotone improvement hypothesis: execution < execution+static < execution+static+Z3
- Mechanism: richer feedback → narrower next-attempt distribution toward valid solutions
- Test on HumanEval+ AND MBPP+ for generalizability
- Secondary metrics: repair efficiency, error category analysis (positive and negative result coverage)
- LLM-generated Z3 constraints: both novel and feasible

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

I need to push back on several under-examined assumptions before we declare convergence.

**Concern 1: Monotonicity assumption is unwarranted.** Dr. Ally's hypothesis asserts monotone improvement, but there's a plausible mechanism for non-monotonicity: LLM-generated Z3 constraints may be *wrong* — they may encode an incorrect formalization of the problem. If the LLM misspecifies the Z3 constraint, the counterexample it generates will be a counterexample to the wrong spec, leading the repair in the wrong direction. This could make pass@1 *decrease* in the Z3 condition. The hypothesis should be **directional but not assume monotonicity** — otherwise a non-monotone result falsifies the mechanism story even if the individual conditions show improvement over baseline.

**Concern 2: Confound from LLM-generated Z3 spec quality.** Prof. Pax flagged this but softened it too quickly. If we use LLM-derived Z3 constraints, we're simultaneously testing two things: (1) does formal feedback help? and (2) can the LLM correctly formalize problem specs? These are entangled. A cleaner design: for HumanEval problems specifically, there exist manually-written test suites (EvalPlus unit tests) that can serve as the ground truth. We don't need Z3 at all if we use more comprehensive unit tests as the feedback signal. **The "formal method" novelty then comes from static type analysis (mypy), not Z3.**

**Concern 3: k=3 is arbitrary.** Why k=3? If the effect only emerges at k=5 but we stop at k=3, we miss it. If the effect is fully captured at k=1, k=3 is wasteful. The right design: run until pass or k=5, report pass@k as a function of k, and analyze the learning curve.

**Mitigation Proposals:**
- Change primary hypothesis: execution-only vs. execution+mypy (drop Z3, cleaner comparison)
- Z3 becomes a secondary condition with explicit caveat about spec quality confound
- Report pass@k for k=1..5, not just k=3
- Add a "repair success rate by error type" analysis (syntax, type, semantic) to understand *which* errors each feedback catches

**Key Points:**
- Drop monotonicity claim — predict execution+mypy > execution-only (single directional claim)
- Z3 as secondary condition with explicit spec-quality confound caveat
- Run k=1..5, report learning curve
- Error type analysis as explanatory secondary metric

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's critique is mostly right, and I accept the refinement. But let me push back on one point: dropping Z3 entirely makes the paper less interesting to the VerifAI audience. The workshop is specifically about formal verification meeting LLM code generation — a paper that only tests mypy is missing the "formal" hook.

Here's a compromise that addresses Rex's confound concern while preserving the formal-methods narrative:

**Use Z3 on a curated subset.** HumanEval has 164 problems. For problems with simple numerical/arithmetic specifications (pure functions of integers/strings), we CAN reliably encode Z3 specs — these are ~40-60 problems. For the remaining problems (complex data structures, I/O), we fall back to the execution+mypy condition. This gives us:

- Full set (164 problems): execution-only vs. execution+mypy (primary comparison)
- Curated subset (~50 problems): execution-only vs. execution+mypy vs. execution+mypy+Z3 (formal methods spotlight)

This design is:
1. Honest about Z3's scope (not overselling)
2. Preserves formal methods contribution for VerifAI
3. Avoids the confound on the primary comparison
4. Makes the negative space productive (why only 50 problems? — that IS the finding about SMT scope)

And on novelty: the primary contribution is still the **first controlled comparison of static analysis feedback in LLM repair loops**, which hasn't been published. The Z3 subset adds a formal-methods flourish that makes it right for VerifAI specifically.

**Key Points:**
- Keep Z3 but as curated-subset analysis (~50 arithmetic-heavy HumanEval problems)
- Primary comparison: execution-only vs. execution+mypy (full 164 problems)
- Z3 section: formal methods spotlight on tractable subset
- Primary claim: execution+mypy > execution-only on HumanEval+/MBPP+
- Secondary claim: Z3 adds further gains on subset where specs are reliable

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

The hybrid design Dr. Nova proposes is acceptable from a falsifiability standpoint, provided we pre-register the subset selection criteria before running experiments. The key falsifiability properties of the final hypothesis:

**Primary falsifiable claim:** On HumanEval+ and MBPP+, execution+mypy repair achieves strictly higher pass@1 (averaged over k=1..5 repair rounds) than execution-only repair, at matched compute budget (same number of LLM calls per problem).

**Falsification criteria:**
- NULL: Welch's t-test on pass@1 improvement (mypy vs. baseline) p ≥ 0.05 on both benchmarks
- WEAK: Only one benchmark shows improvement (p < 0.05)
- STRONG: Both benchmarks show improvement (p < 0.05), effect size ≥ 1% absolute pass@1

**Secondary falsifiable claim:** On the curated Z3 subset (~50 arithmetic-heavy HumanEval problems), execution+mypy+Z3 achieves strictly higher pass@1 than execution+mypy.

**The mechanism claim** (richer feedback → narrower next-attempt distribution) is not directly measurable but generates a testable intermediate prediction: mypy feedback should correlate with fewer type errors in subsequent repair attempts. This can be checked by running mypy on each repair attempt and tracking type error count across rounds.

**Controlled variables:** same LLM model (GPT-4o-mini), same temperature (0.0 for repair, 0.8 for initial generation), same token budget per repair prompt, same benchmark split.

**Key Points:**
- Pre-register Z3 subset selection criteria (pure functions with simple int/str types)
- Primary metric: pass@1 averaged over k=1..5 rounds
- Significance: Welch's t-test, p < 0.05, ≥ 1% absolute effect size
- Intermediate prediction: mypy feedback reduces type error frequency in subsequent rounds
- Fully controlled variables specified

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Good. Let me verify the final design against real-world constraints.

**Revised feasibility check:**

| Component | Status | Notes |
|-----------|--------|-------|
| HumanEval+ harness | ✅ Ready | openai/human-eval + evalplus/evalplus |
| MBPP+ harness | ✅ Ready | evalplus/evalplus |
| Execution-only repair | ✅ Ready | Standard Self-Debug implementation |
| mypy integration | ✅ Ready | `mypy --strict` on generated code |
| Z3 subset selection | ✅ Feasible | Manual review of 164 problems (~2h) |
| LLM-generated Z3 specs | ⚠️ Risk | Quality depends on model; mitigated by curated subset |
| GPT-4o-mini API access | ✅ Assumed | $10-15 budget |
| k=1..5 repair rounds | ✅ Feasible | ~7,400 calls for full study |

One implementation detail that matters: mypy error output can be verbose. We need a **mypy feedback formatter** that extracts actionable lines (error type, line number, message) and truncates to fit in context window. This is 20 lines of Python — not a blocker.

**Z3 subset pre-registration criteria (proposed):**
1. Function signature is pure (no side effects, no file I/O)
2. Input types are only int, str, float, List[int], or List[str]
3. Problem statement contains a clear mathematical or string-manipulation spec
4. No reference to external state or environment

Applying these criteria to HumanEval (164 problems), I estimate 45-60 qualify. This matches Dr. Nova's ~50 estimate.

**Timeline for a solo researcher:** 2 weeks to implement + 3 days to run + 1 week to write = 3.5 weeks total. Well within workshop timeline.

**Key Points:**
- Implementation feasible in 3.5 weeks
- mypy feedback formatter needed (20 lines, not a blocker)
- Z3 subset criteria pre-registered and clear
- ~50 HumanEval problems qualify for Z3 subset
- Full experiment: ~7,400 LLM calls at $10-15

---

### Exchange 10

🎯 **Dr. Sage** (Research Impact Evaluator):

We're at convergence. Let me do a final impact assessment and confirm the hypothesis meets the VerifAI publication bar.

**VerifAI Workshop fit:** The paper directly addresses "formal method techniques × LLM code generation" — the exact workshop theme. The dual contribution (mypy primary + Z3 curated subset) gives the formal methods community something concrete to engage with.

**Novelty assessment:** The specific comparison "execution-only vs. execution+static-analysis in LLM repair loops on HumanEval+/MBPP+" has not, to my knowledge, been published. Self-Debug and Reflexion use execution feedback only. CodeAct-style agents use execution + observation but not static analysis as a distinct signal. The mypy integration as an explicit repair-loop condition is the novel element.

**Significance:** If the primary result (execution+mypy > execution-only) is positive, the practical takeaway is immediate: add mypy to your LLM code repair loop. If negative, the takeaway is equally clear: execution feedback already captures what mypy would add. Both outcomes are informative.

**Effect size calibration:** On HumanEval+ (164 problems), pass@1 of a strong baseline (GPT-4o-mini, execution-only, k=3 repair rounds) is likely around 60-70% based on published benchmarks. A +3% absolute improvement means 5 additional problems solved. The mypy condition should provide this if type errors are a meaningful failure mode — which they are (~20-30% of HumanEval failures involve type mismatches based on EvalPlus analysis).

**Convergence Verdict:** This hypothesis is READY for Phase 2B. All convergence criteria met:
- SPECIFIC: Clear core claim ✅
- MECHANISM: Richer feedback → narrower next-attempt distribution ✅
- PREDICTIONS: P1 (mypy > baseline), P2 (Z3 > mypy on subset), P3 (type errors decrease across repair rounds) ✅
- NOVELTY: First controlled static-analysis-in-repair-loop comparison ✅
- FEASIBILITY: 3.5 weeks, $15 budget ✅
- OBJECTIONS: Z3 confound addressed via curated subset + pre-registration ✅

**Key Points:**
- All 6 convergence criteria met
- Direct fit to VerifAI workshop theme
- Actionable positive AND negative result scenarios
- Ready for Phase 2B

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The primary comparison (execution+mypy vs. execution-only in LLM repair loops) fills a genuine gap in the literature. No published work has isolated static analysis feedback as a distinct repair-loop signal on HumanEval+/MBPP+. The Z3 curated-subset angle adds a formal-methods narrative that makes this right for VerifAI. The non-monotone possibility (Z3 might not help) is itself a publishable finding.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The primary hypothesis is fully falsifiable: execution+mypy vs. execution-only on two benchmarks, Welch's t-test, p < 0.05, ≥ 1% absolute pass@1 improvement. Pre-registration of Z3 subset criteria eliminates post-hoc flexibility. Controlled variables (same model, same temperature, same token budget) are specified. The mechanism generates a testable intermediate prediction (type error reduction across rounds).

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Direct match to VerifAI workshop theme. Actionable regardless of result direction (positive → add mypy; negative → execution feedback is sufficient). Effect sizes are calibrated to published HumanEval+ baselines. The Z3 curated subset provides formal-methods depth for the workshop audience.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Fully implementable with existing open-source tools (Outlines/vLLM not needed — repair loops use standard LLM API calls). mypy integration is 20 lines of code. Z3 subset selection requires ~2h of manual review. Total: 3.5 weeks for a solo researcher, $10-15 in API costs. No blocking dependencies.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The hypothesis that emerged from this discussion is: **Augmenting LLM code repair loops with static analysis feedback (mypy type checking) produces a measurable improvement in pass@1 on HumanEval+ and MBPP+, beyond what execution-only feedback achieves.** The proposed mechanism is that mypy provides error-type-specific correction signal that narrows the LLM's next-attempt distribution toward type-correct solutions, whereas execution-only feedback provides only pass/fail binary signal.

The experimental design is a 3-condition ablation within a repair loop framework: (A) execution-only repair (Self-Debug baseline), (B) execution + mypy repair, (C) execution + mypy + LLM-generated Z3 repair [on curated ~50-problem subset]. All conditions use the same LLM (GPT-4o-mini), same initial generation, k=1..5 repair rounds, and same compute budget per round. Primary benchmarks: HumanEval+ (164 problems) and MBPP+ (378 problems).

Primary prediction P1: Condition B achieves strictly higher pass@1 than Condition A on both benchmarks (p < 0.05, ≥ 1% absolute). Secondary prediction P2: Condition C achieves higher pass@1 than Condition B on the curated Z3 subset. Secondary prediction P3: mypy type error count in repair attempts decreases monotonically from round 1 to round 5, confirming that mypy feedback is being incorporated.

The Z3 confound (LLM-generated specs may be incorrect) is addressed by restricting the Z3 analysis to problems where specs are reliably encodable (pure functions, simple types) and pre-registering selection criteria before experiments run. The hypothesis is fully testable on existing benchmarks with existing tools within a 3.5-week timeline and $15 API budget.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Z3 spec quality remains a confound even on the curated subset — a wrong Z3 spec could guide repair toward code that satisfies the spec but fails EvalPlus tests. Mitigation: validate each LLM-generated Z3 spec by checking it on the provided test cases before using it for repair.
- mypy in strict mode may produce too many false positives on HumanEval-style Python (lots of untyped code). Mitigation: use `mypy --ignore-missing-imports --no-strict-optional` (permissive mode) to focus on actionable type errors only.
- Sample size concern: HumanEval+ (164) may be underpowered to detect 1% absolute improvement at p < 0.05 (need ~300+ samples for this effect size). Run MBPP+ (378 problems) as primary benchmark, HumanEval+ as secondary.
- **Mitigation Strategy:** Pre-validate Z3 specs on test cases; use permissive mypy flags; treat MBPP+ as primary benchmark (sufficient power); report confidence intervals alongside p-values.
