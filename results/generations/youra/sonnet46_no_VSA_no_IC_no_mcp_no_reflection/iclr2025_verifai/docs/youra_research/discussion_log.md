# Phase 2A Discussion Log
# Architecture: Self-Contained Tikitaka Loop (Independent-Controller Ablation)
# Claude plays ALL personas. No external LLM. No orchestrate_exchange.py.

**Generated:** 2026-08-31
**Gap:** Gap 2 — No Overhead-Normalized Cross-Category Comparison of Formal Feedback Methods
**Mode:** UNATTENDED

---

## Briefing Context

### Research Gap Selected
**Gap 2 (CRITICAL / PRIMARY):** No controlled experiment exists comparing formal method feedback categories (static analysis, SMT solving, execution monitoring, type checking) on the same LLM backbone, same benchmark tasks, same overhead metric.

**Primary Research Question:** Which formal method category yields the greatest correctness improvement per unit of overhead when applied as post-generation feedback in LLM code generation?

### Key Papers Available
- P1: Self-Repair (Olausson et al., 2023) — execution feedback baseline, HumanEval/MBPP
- P2: Reflexion (Shinn et al., 2023) — verbal/execution feedback loop, HumanEval
- P3: CodeT (Bei Chen et al., 2022) — execution oracle via generated tests
- P4: Grammar-Constrained Decoding (Geng et al., 2023) — type/grammar category

### Feasibility Constraints (MANDATORY)
- Only existing benchmarks: HumanEval, MBPP, SWE-bench
- No new benchmark creation, no human annotation, no synthetic data
- Must be testable immediately

### Previous Failure / Routing Context
No failure contexts — first Phase 2A attempt. No routing archive found.

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

The gap here is deceptively rich. We have four formal method categories — static analysis, SMT solving, execution monitoring, and type checking — each studied in isolation, each on different LLMs, different benchmarks, different overhead metrics. The literature reads like four parallel universes that never collide. The creative opportunity is to make them collide: run a single controlled experiment where the *only* variable is which formal verifier sits in the Generate→Verify→Repair loop.

What's novel isn't just the comparison — it's the *framing*. Prior work asks "does feedback help?" We're asking "which *kind* of feedback is most efficient?" That's a resource-allocation question, and it reframes formal methods from a binary (formal vs. informal) to a spectrum ordered by correctness-per-overhead ratio.

Two unconventional angles I want to explore: First, can we treat the formal verifier as a "difficulty filter"? Execution monitoring catches everything a test suite catches; SMT catches things tests miss (edge cases requiring counterexample construction); static analysis catches things neither catches but at lower signal quality. If task difficulty predicts which category wins, we have a routing hypothesis, not just a comparison. Second, what if overhead normalization reveals that the "expensive" SMT option is *cheaper* on hard tasks because it terminates the repair loop faster with a more informative signal?

**Key Points:**
- Single controlled experiment: same LLM × same tasks × vary only verifier type
- Reframes question as correctness-per-overhead resource allocation
- Two angles: difficulty-routing hypothesis; SMT may be cheaper on hard tasks despite higher per-call cost

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's framing is appealing, but we need to be precise about what "overhead" means before we can measure it. Three candidate definitions: (1) wall-clock time per repair attempt, (2) total wall-clock time to final solution, (3) LLM API tokens consumed per solved problem. These are *not* equivalent and can rank categories differently. Static analysis (Pyright) runs in milliseconds; SMT solving (Z3) can time out after seconds or minutes depending on constraint complexity; execution monitoring runs the generated code which may hang or be slow on complex benchmarks. We must pick one overhead metric and justify it.

On the HumanEval/MBPP side, testability is strong — both benchmarks have ground-truth test suites, pass@k is well-defined, and the openai/human-eval harness is public. But we need to be careful about one confound: test-based execution monitoring *uses the same test suite* that pass@k is measured against. That's circularity if the execution oracle and the evaluation oracle are identical. We should either use a held-out subset of tests as the repair oracle or use CodeT-style generated tests as repair signal — keeping evaluation tests blind to the repair loop.

For SMT on HumanEval: the key obstacle is property annotation. HumanEval problems don't have formal pre/post-conditions. We either (a) auto-generate them from docstrings using an LLM, or (b) hand-annotate a subset, or (c) restrict SMT to properties extractable automatically (type constraints, assertion statements). Option (c) is the only feasible one under our constraints — no human annotation allowed.

**Key Points:**
- Overhead metric must be fixed upfront: wall-clock per-problem is most interpretable
- Execution circularity: repair oracle ≠ evaluation oracle — use generated tests or disjoint subset
- SMT feasibility: auto-extract properties from assertions/type hints only (no human annotation)

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

This discussion is converging on something genuinely publishable at a workshop level. Let me assess the significance landscape. The *why it matters* argument is straightforward: practitioners choosing a formal feedback approach for LLM code generation pipelines have no principled guidance. Should they spend 200ms on Pyright or 2 seconds on Z3? This paper would give the first empirical answer.

The prior art gap is real — Self-Repair (Olausson 2023) is the nearest work but it: (a) tests only execution feedback, (b) doesn't measure overhead, (c) doesn't include static analysis or SMT. Reflexion is verbal/execution only. CodeT is selection not repair. The cross-category controlled comparison doesn't exist.

For significance, the hypothesis needs to produce a *directional claim*, not just "results vary." The most impactful finding would be a clear ranking with a mechanism explanation — e.g., "execution monitoring dominates on easy tasks (overhead advantage) while static analysis dominates on medium tasks (signal quality advantage), and SMT is cost-ineffective even on hard tasks due to annotation overhead." That's a concrete, actionable finding that practitioners can use.

One concern: SWE-bench may be too hard for this comparison. SWE-bench requires repository-level reasoning; formal method feedback at function level (HumanEval style) doesn't map cleanly. I'd recommend scoping to HumanEval + MBPP, with SWE-bench as a stretch goal if time permits.

**Key Points:**
- Clear practitioner value: first empirical guidance on formal feedback category selection
- Prior gap confirmed: no controlled cross-category comparison exists
- Scope recommendation: HumanEval + MBPP primary; SWE-bench as stretch
- Need directional claim, not just "results vary"

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Good discussion so far. Let me ground this. What can actually be built in a reasonable experiment timeline using only existing tools?

**Execution monitoring:** Trivially implementable. `subprocess.run` the generated code against HumanEval test cases, capture stdout/stderr, inject into LLM repair prompt. Already done in Self-Repair (Olausson 2023). This is our baseline category — we replicate their setup.

**Static analysis (Pyright):** `pyright --outputjson solution.py` gives structured JSON with error type, line number, message. Inject into LLM prompt as "Pyright reports: [error list]. Fix the following code:". Overhead is ~100-300ms per call. Fully feasible on HumanEval/MBPP. No annotation required.

**Type checking (mypy):** Similar to Pyright. `mypy --show-error-codes solution.py`. Slightly different error coverage. Could run both as a "type checking" category or pick one. Mypy is slower (~500ms); Pyright is faster and more accurate on modern Python. Pick Pyright.

**SMT (Z3):** This is the hard one. Prof. Vera is right — HumanEval problems lack formal annotations. Auto-extraction approach: parse the docstring with an LLM to generate Z3 constraints (pre/post-conditions). This adds an LLM call overhead. Alternatively, restrict to problems that have explicit assertions in the test suite — extract those as properties. Feasible for ~30-50% of HumanEval problems. We can annotate the *feasible subset* automatically.

**Practical constraint:** Fix 3 repair iterations max (from Self-Repair best practice). Fix GPT-4o-mini as LLM backbone (cost control). HumanEval (164 problems) + MBPP (374 problems) = 538 problems. Feasible in <24 hours of compute with API budget ~$50-100.

**Key Points:**
- All four categories implementable with existing tools
- SMT requires auto-extracted properties — feasible for ~40% of HumanEval problems
- Fix: GPT-4o-mini backbone, 3 repair iterations, wall-clock overhead metric
- Scope: HumanEval + MBPP primary (538 problems total)

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Building on what everyone has said, I want to crystallize a hypothesis that's both testable and directional. The discussion has converged on a core structure: a controlled experiment with four feedback conditions applied to the same LLM, same problems, same iteration budget, measured by pass@1 improvement per unit wall-clock overhead.

Here's the hypothesis I'm advocating: **Among formal feedback categories applied post-generation to LLM code, execution monitoring will achieve the best correctness-per-overhead ratio on standard benchmarks (HumanEval/MBPP), while static analysis will provide the most reliable signal with lower overhead than SMT, and SMT-based feedback will show correctness gains only on the property-annotatable subset but at higher overhead cost — resulting in a clear efficiency ordering: execution ≥ static analysis > type checking ≈ SMT (on feasible subset).**

The mechanism: feedback signal specificity trades off with overhead. Execution gives binary pass/fail plus error trace (low overhead, moderate specificity). Static analysis gives typed structural errors (low overhead, higher specificity than execution for type-related bugs). SMT gives exact counterexamples (high overhead, highest specificity for logic bugs). The efficiency ordering follows from this trade-off interacting with the distribution of error types in HumanEval/MBPP (mostly type errors and logical errors, not deep semantic violations requiring formal proof).

This is falsifiable: if SMT proves more efficient than execution on the annotatable subset, the ordering is violated and the signal-specificity-overhead trade-off mechanism needs revision.

**Key Points:**
- Proposed ordering: execution ≥ static analysis > type checking ≈ SMT (on feasible subset)
- Mechanism: feedback signal specificity trades off with overhead
- Falsifiable: SMT outperforming execution would disconfirm the ordering
- Actionable: practitioners get a concrete recommendation

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

I'll stress-test Dr. Ally's hypothesis rigorously.

**Concern 1 — Apples-to-oranges problem:** Execution monitoring tests the *complete* program behavior (all inputs in the test suite). Static analysis tests only a program's *static structure*. SMT tests *logical properties* of a *subset* of inputs. These are not measuring the same thing — they catch different bug types. A "correctness-per-overhead" metric that treats them as interchangeable conflates complementary tools. The hypothesis needs to acknowledge this and restrict comparison to problems where all methods apply meaningfully.

**Concern 2 — Repair loop coupling:** The quality of LLM repair depends on the feedback *format*, not just the feedback *type*. Pyright JSON error messages may be clearer for LLM injection than Z3 counterexample traces. If we observe differences, we can't attribute them purely to "formal category" — it could be "feedback format." Need to control or at least acknowledge this confound.

**Concern 3 — The 40% SMT coverage problem:** Prof. Pax noted SMT applies to only ~40% of HumanEval problems. If the hypothesis is tested on all 164 problems but SMT is evaluated on only 65, the comparison is not on identical task sets. This could inflate or deflate SMT's apparent efficiency. Solution: report all-problem results AND matched-subset results separately.

**Concern 4 — Baseline underspecification:** "Execution monitoring" in this context must be defined precisely: is it HumanEval's *actual* test suite (visible) or generated tests? Using the evaluation test suite as repair oracle is circular (Prof. Vera's point). This must be resolved in experimental design.

**Mitigation Strategy:** (1) Restrict primary comparison to tasks where all methods apply; (2) standardize feedback injection format across categories; (3) report matched-subset and full-coverage results separately; (4) use generated tests (CodeT-style) as execution oracle, keeping evaluation test suite blind.

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex has sharpened the hypothesis considerably. I want to respond to Concern 1 (apples-to-oranges) with a reframe that actually strengthens novelty.

The fact that these categories catch *different* bug types is not a weakness — it's the central finding. If we document which bug types each category catches and which it misses, we're producing a *taxonomy of formal feedback coverage* for LLM code. That's a more interesting contribution than a simple ranking.

Concretely: on HumanEval/MBPP, we can classify why each problem failed at generation (type error, logic error, runtime error, off-by-one, etc.) using static analysis of the error traces. Then we can show that static analysis feedback helps most for type errors, execution feedback helps most for runtime/assertion errors, and SMT feedback helps most for logic errors (on the annotatable subset). This gives a *diagnostic routing* contribution: "use the formal method matched to your bug type."

This reframe also addresses Prof. Rex's Concern 1: we're not claiming the methods are interchangeable — we're documenting their complementary coverage profile. The "correctness-per-overhead" metric becomes secondary to the routing insight.

**Key Points:**
- Reframe: bug-type coverage profile is the contribution, not just efficiency ranking
- Diagnostic routing: match formal method to dominant bug type in your task distribution
- Stronger novelty: taxonomy of formal feedback coverage + routing recommendation

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's reframe is genuinely stronger. Let me formalize the testable predictions that would follow.

**P1 (Primary — Efficiency Ordering):** On HumanEval + MBPP, execution monitoring (with generated-test oracle) will yield the highest pass@1 / wall-clock-overhead ratio across all 538 problems. Static analysis will rank second. SMT (on feasible subset) will rank lower due to overhead despite higher per-error specificity.

**P2 (Bug-Type Coverage):** When problems are stratified by failure type (type error / runtime error / logic error), static analysis feedback will show disproportionate improvement on type-error tasks, execution feedback on runtime-error tasks, and SMT feedback on logic-error tasks in the annotatable subset.

**P3 (Difficulty Interaction):** Harder HumanEval/MBPP problems (as measured by baseline LLM pass@1 < 30%) will show larger absolute pass@1 gains from any formal feedback than easy problems, but the efficiency ordering will hold across difficulty strata.

Each prediction is falsifiable with exact success criteria:
- P1: Execution ratio ≥ 1.5× static analysis ratio (ratio = Δpass@1 / mean wall-clock seconds per problem)
- P2: Chi-squared test significant (p < 0.05) for bug-type × feedback-category interaction on improvement rates
- P3: ANOVA significant (p < 0.05) for difficulty × feedback-category interaction; ordering preserved in all strata

**Key Points:**
- Three testable predictions with quantitative success criteria
- P1 efficiency ordering as primary; P2 bug-type routing as secondary; P3 difficulty stratification as tertiary
- All measurable on HumanEval + MBPP with existing tools

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The reframed hypothesis — bug-type coverage profile + diagnostic routing — is genuinely novel. No prior work documents which formal method category catches which bug type in LLM code generation. The routing contribution (match method to bug type) is actionable and differentiates this from prior single-category studies. The efficiency ordering as a resource-allocation frame is also new.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** All three predictions have quantitative success criteria (ratio thresholds, chi-squared test, ANOVA). Confounds (feedback format, execution circularity, SMT coverage subset) are acknowledged and mitigated in experimental design. The hypothesis is well-specified and testable on existing benchmarks without human annotation.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Clear practitioner value — first empirical guidance on formal feedback category selection for LLM code pipelines. Prior gap is confirmed (no controlled cross-category comparison exists). The bug-type routing contribution elevates the paper above a simple benchmark study. Workshop-appropriate scope with potential for journal extension.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** MODERATE
- **Assessment:** Execution monitoring and static analysis are fully implementable. SMT auto-extraction is feasible for ~40% of problems. Bug-type classification adds complexity (need to classify failure modes). Total experiment is realistic in <48 hours of compute with $50-100 API budget. The matched-subset reporting for SMT adds analysis complexity but is straightforward. Feasible with proper planning.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The Phase 2A discussion has converged on the following hypothesis: **Among post-generation formal feedback categories applied in a Generate→Verify→Repair loop for LLM code generation, feedback categories differ in their correctness-per-overhead efficiency and their bug-type coverage profile, such that execution monitoring achieves the highest efficiency ratio overall, static analysis provides the best tradeoff for type-error-dominated tasks, and SMT-based feedback provides the highest per-error specificity at greater overhead cost — enabling a diagnostic routing recommendation: practitioners should match formal feedback method to the dominant bug type in their task distribution.**

The core mechanism is feedback signal specificity versus overhead: execution feedback is cheap and broad (catches any test-failing behavior); static analysis is cheap and precise for structural type errors; SMT is expensive but provides exact counterexamples for logical violations. The distribution of bug types in HumanEval/MBPP (predominantly type errors and runtime errors, fewer deep logic violations) predicts that execution monitoring and static analysis will dominate efficiency metrics on these benchmarks.

The experiment is fully implementable: GPT-4o-mini backbone, 3 repair iterations, HumanEval (164 problems) + MBPP (374 problems), four feedback conditions (execution/static/type-check/SMT), wall-clock overhead measured per problem, bug-type classification from error traces, matched-subset SMT comparison. No new benchmarks, no human annotation, no synthetic data — all existing tools and datasets.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** SMT auto-extraction from HumanEval docstrings may be low-quality — Z3 constraints generated by LLM from natural language are prone to unsound encodings. This would underestimate SMT's actual potential.
- **Concern 2:** Bug-type classification depends on heuristic error trace parsing — misclassification could confound P2 (bug-type routing prediction).
- **Mitigation Strategy:** For Concern 1, validate Z3 encoding soundness on a 20-problem pilot before full run; report encoding quality as a limitation. For Concern 2, use agreement between automated classification and a secondary classifier (e.g., Pyright error category) as reliability check; report inter-rater agreement. Both mitigations are feasible without human annotation.
