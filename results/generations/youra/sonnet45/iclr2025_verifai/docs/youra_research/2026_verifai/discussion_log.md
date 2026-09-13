# Phase 2A Round Table Discussion Log
**Gap:** Orchestration Framework for Multi-Source Feedback Integration
**Gap ID:** gap-1
**Priority:** CRITICAL | **Relevance:** PRIMARY
**Date:** 2026-03-18
**Version:** 9.0.0 (Tikitaka Self-Contained Loop)

---

## Research Context

**Main Research Question:**
Can we demonstrate feasibility of integrating lightweight formal verification techniques (static analysis, constraint checking, type verification) with LLM-generated code through proof-of-concept validation on small-scale representative examples?

**Selected Research Gap:**
**Current State:** Individual feedback mechanisms well-studied (test-driven: 4 papers + 3 repos, execution feedback: 8 papers + 3 repos, static analysis: 2 repos, constraint synthesis: 5 papers + 2 repos). Each approach uses 3-5 iteration loops with single feedback type. Success rates: 60-80% improvement over single-shot.

**Missing Piece:** Orchestration logic for combining multiple feedback sources, conflict resolution when feedback types contradict, prioritization strategy, termination criteria, small-scale validation on 3-5 problem classes.

**Potential Impact:** High — Directly blocks the research question's core "integration" claim

---

## Briefing Materials

### Supporting Evidence Summary

**Academic Papers (from Phase 1):**
- LLMDebugger (Li et al., 2024): Execution feedback only, 581 citations
- PerfCodeGen (Takerngsaksiri et al., 2024): Test execution feedback, 43 citations
- CoTran (Jana et al., 2024): Compiler + symexec feedback, 34 citations
- ReTool (Feng et al., 2025): Tool-use strategy for code interpreter, 229 citations
- Tests as Prompt (Cui, 2025): TDD benchmark, uses tests as specification

**GitHub Implementations (from Phase 1):**
- FloridSleeves/LLMDebugger: Execution feedback with basic blocks
- SalesforceAIResearch/perfcodegen: Test execution feedback
- BoukeNijhuis/test-driven-generation: TDD approach (Java)
- ahmedhus22/llm4lint: Static analysis only (Qwen2.5)
- ksanu1998/static_analysis_codegen_llms: Static analysis evaluation

**Key Insight:** All 22 directly relevant sources use **single feedback type** only. No prior work demonstrates systematic integration of static analysis + execution + constraints.

### Feasibility Constraints (From Previous Failure - h-e1)

**MANDATORY CONSTRAINTS:**
- Dataset scale: <10K samples or 10% sampling (No multi-GB datasets)
- Template/schema design: 3-5 representative cases (Not 42 exhaustive classes)
- Implementation: 3-8 tasks max, <20 complexity points (Not 40+ hours)
- Training time: <30 minutes (Not multi-hour fine-tuning)
- Hypothesis type: EXISTENCE = qualitative feasibility, not production metrics

### Papers Available for Reading

No reference papers were prepared (Phase 1 was research data collection via MCP searches only).

---

## Discussion Rounds

### Instructions for Participants

You are participating in a Tikitaka discussion to develop a testable hypothesis addressing Gap 1. The orchestrator will guide you through multiple rounds until convergence is reached.

**Convergence Criteria:**
- SPECIFIC: Clear core claim stated
- MECHANISM: How it works explained
- PREDICTIONS: 2-3 testable predictions with criteria
- NOVELTY: What's new articulated
- FEASIBILITY: Implementation realistic
- OBJECTIONS: Major criticisms addressed

**Discussion will continue below as orchestrated by orchestrate_exchange.py**

---

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

The research gap we're addressing is fascinating — after reviewing the Phase 1 data, I see a clear pattern: we have successful single-source feedback mechanisms (test-driven development showing 60-80% improvement, execution feedback via LLMDebugger, static analysis tools like mypy/pylint), but NO prior work has attempted systematic orchestration of multiple feedback sources.

This presents a unique opportunity for **layered feedback orchestration** — I'm thinking of this not as a monolithic system, but as a priority-based cascade where each feedback type serves a specific role:

**Three unconventional angles to explore:**

1. **Feedback Type Prioritization via Error Category Mapping**: Rather than treating all feedback equally, map each error type to its most effective feedback source:
   - Type errors, null safety → Static analysis (mypy) catches these at parse time
   - Logic errors, edge cases → Test execution reveals these
   - Performance issues, resource leaks → Runtime profiling
   - This creates a "first responder" system where we route problems to the feedback source most likely to catch them

2. **Conflict Resolution as Feature, Not Bug**: When feedback types contradict (e.g., tests pass but static analyzer flags type issues), use this as a signal for deeper investigation. I'm imagining a "confidence weighting" system where:
   - High-certainty feedback (compiler errors, test failures) → immediate fix
   - Medium-certainty (linter warnings, coverage gaps) → suggestions
   - Low-certainty (style issues) → deferred
   - Contradictions trigger a meta-analysis step

3. **Lightweight Constraint DSL as "Feedback Translation Layer"**: Instead of raw linter output ("mypy: error: Argument 1 has incompatible type 'str'; expected 'int'"), create a minimal DSL that expresses constraints in LLM-friendly natural language:
   - Original: `mypy: error: Argument 1 has incompatible type 'str'; expected 'int' [arg-type]`
   - Translated: `Function 'calculate_age' expects an integer for parameter 'birth_year', but received a string. Suggestion: Convert input using int() or fix the function signature.`

**Key Points:**
- We're not building a production system — we're proving the **concept** of orchestration on 3-5 problem classes (buffer safety, null pointer, type correctness)
- Previous failure (h-e1) taught us to avoid exhaustive coverage — we validate the approach on representative examples only
- The novelty is in the orchestration logic itself, not the individual tools (which already exist)

**Questions for the group:**
- Which of these three angles has the strongest claim to novelty? (I'm leaning toward the conflict resolution framework)
- How do we validate orchestration effectiveness without building a full framework? (Maybe measure improvement over baseline single-source approaches?)

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

The evidence suggests you are circling a potentially novel idea, but at present it is underspecified as a scientific hypothesis. "Layered feedback orchestration" must be reduced to testable claims. For example: *Given a fixed set of programming tasks, an LLM augmented with orchestrated multi-source feedback will achieve a higher functional correctness rate than (a) no feedback and (b) any single feedback source alone.* That is falsifiable. What would disprove this? If the orchestrated system performs no better than the strongest single-source baseline under controlled conditions, the hypothesis fails.

Of your three angles, the conflict resolution mechanism is the most scientifically interesting — but only if we define measurable predictions. You propose treating contradictions (e.g., tests pass but static analysis fails) as signals for deeper analysis. Very well. Then we must quantify: How often do such contradictions occur? In how many of those cases does meta-analysis improve final correctness versus ignoring the contradiction? I would design an ablation study with four arms: (1) test-only feedback, (2) static-only, (3) naive aggregation (concatenate all feedback), (4) orchestrated with conflict-triggered meta-step. The primary metric: final pass rate on held-out tasks. Secondary metrics: number of iterations to convergence, rate of regression introduction, and overfitting to tests.

Your "error category mapping" idea is only meaningful if we predefine error classes and verify separability. For example: inject controlled fault types into benchmark tasks (type errors, boundary logic errors, resource misuse). Then measure detection latency and correction success per feedback source. The orchestration hypothesis predicts: routing based on error category yields faster convergence than uniform feedback exposure. A critical confound must be controlled: feedback verbosity. If one source simply produces more tokens, improvements may reflect information volume rather than orchestration quality. Token budget must be equalized across conditions.

Regarding the DSL translation layer: the key question is not whether it sounds clearer, but whether it changes measurable outcomes. A clean experiment would compare raw tool output versus DSL-translated output, keeping semantic content constant. If correction rates differ significantly, the DSL contributes explanatory power. If not, it is cosmetic. The achilles heel here is over-interpretation: the LLM may already internally normalize tool output, making the DSL redundant.

Finally, we must guard against benchmark leakage and circularity. If tests define correctness, an LLM can overfit to them. Therefore, use hidden oracle tests not exposed during feedback, or mutation testing to assess robustness. What would convince me this orchestration is real? A statistically significant improvement over the best single-source baseline across at least three distinct error classes, with pre-registered metrics and ablations demonstrating that conflict handling—not mere aggregation—is the causal factor. If that holds, I will say: *This meets my standards.*

**Key Points:**
- Formulate orchestration as a falsifiable hypothesis with explicit baselines and ablations.
- Quantify the causal impact of conflict resolution and routing via controlled error-class experiments.
- Control confounds (token budget, verbosity, overfitting to tests) to isolate true orchestration effects.

---

### Exchange 3

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Vera raises excellent methodological points, but let me ground this in implementation reality given our Phase 4 constraints. We learned from h-e1's failure that infrastructure complexity kills proof-of-concept validation. Let me walk through what's actually feasible within our <30min experiment, <10K samples, <8 tasks budget.

**Reality check on Prof. Vera's four-arm ablation study:**

The proposed experimental design is methodologically sound but **too expensive** for our proof-of-concept scope. Each arm requires:
- Separate orchestration logic implementation
- Independent evaluation runs on benchmark subsets
- Statistical power analysis (likely needs 50+ tasks per arm for significance)
- Multiple random seeds for robustness

That's 4 arms × 50+ tasks × 3-5 iterations per task × 3 random seeds = 600-3000 generation calls. Even at 10 seconds per call, we're talking 2-10 hours just for inference, not counting implementation time.

**Feasible alternative:**
Single hypothesis with A/B comparison — "Orchestrated 2-source feedback (static + execution) vs. best single source (execution-only baseline from prior work)." This cuts implementation to 2-3 tasks max:
1. Task A: Orchestrator logic (priority: execution errors → mypy type errors → done)
2. Task B: Baseline wrapper (execution-only feedback, matching prior work pattern)
3. Task C: Evaluation harness (run both on HumanEval subset, 20-30 problems)

**What we CAN demonstrate in <30min:**

Dr. Nova's **error category mapping** is the most implementation-ready angle. Here's the minimal viable version:
- Use 3 problem classes only: type errors (mypy detects), logic errors (tests catch), both types (orchestration advantage)
- Manually curate 5-10 tasks per class from HumanEval (total 15-30 tasks, well under 10K sample constraint)
- Simple priority cascade: Run mypy first (instant), if no errors → run tests (5-10 sec), aggregate results
- Measure: Does the 2-source orchestration improve pass@1 on "both types" tasks more than on single-type tasks?

**The conflict resolution idea is aspirational for Phase 4:**
Prof. Vera asks "How often do contradictions occur?" — that's an empirical question requiring:
- Ground truth labels for what constitutes a "real" error vs. false positive
- Meta-analysis step implementation (another LLM call for each contradiction)
- Controlled injection of contradictory scenarios

This is a **research question in itself**, not a proof-of-concept validator. I'd defer conflict resolution to "future work" and focus on simple additive orchestration first.

**On the DSL translation layer:**
I agree with Prof. Vera's critique, but here's the pragmatic version: We don't need a custom DSL. Existing tools already have structured output modes:
- mypy `--json-output` → parse error objects programmatically
- pytest `--json-report` → structured test results
- We can write a 20-line Python function that converts these to natural language without inventing a new language

**Minimal hypothesis I'd bet on for Phase 4 success:**

*"On HumanEval tasks requiring both type correctness and logic correctness (N=10), a 2-source feedback orchestrator (mypy → pytest, sequential cascade) achieves higher pass@1 than execution-feedback-only baseline (matched to PerfCodeGen methodology), with improvement margin ≥10 percentage points."*

This is:
- ✅ Falsifiable (binary: did pass@1 improve ≥10pp or not?)
- ✅ Feasible (10 tasks, 2 systems, <100 LLM calls total)
- ✅ Novel (no prior work shows static+exec orchestration)
- ✅ Constrained (no exhaustive coverage, no conflict resolution complexity)

**Key Points:**
- Four-arm ablation is too expensive — do A/B test instead (orchestrated vs. baseline)
- Error category mapping is implementation-ready; conflict resolution is not
- Don't build a DSL — use existing tool JSON outputs + simple translation function
- Aim for a 10-15 percentage point improvement margin to demonstrate orchestration value

**What needs tightening:**
How do we define "tasks requiring both type and logic correctness" without circular reasoning? We need an objective task selection criterion.

---

### Exchange 4

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good — this is getting sharper. But here's where this still breaks down: your *task selection criterion* is dangerously close to circular. "Tasks requiring both type and logic correctness" — defined how? If you label tasks post hoc based on where orchestration helps, reviewers will tear this apart. Show me a **pre-registered, operational definition** that does not depend on your system's performance.

For example, before running any LLM experiments, you could statically analyze the HumanEval corpus and classify tasks using objective signals:
- A task is "type-sensitive" if at least one incorrect but syntactically valid solution passes tests yet fails mypy under strict mode.
- A task is "logic-sensitive" if incorrect implementations pass mypy but fail hidden tests.
- A task is "dual-sensitive" if you can *construct or retrieve* at least one plausible solution exhibiting each failure mode independently.

That means you must generate or mine counterfactual incorrect solutions *before* orchestration runs. Otherwise, you are defining the category using the outcome. What would convince me? A small appendix showing that this classification was frozen prior to evaluation, with examples.

Now let's talk about your central claim of novelty. Right now, it risks sounding incremental: "static + execution > execution alone." That could be dismissed as additive signal gain. Where is the differentiation from naïve concatenation? If your orchestrator is just "run mypy, then pytest, concatenate messages," that's not orchestration — that's aggregation with ordering. The field already knows multiple signals help. Your burden is to show that **the routing policy itself contributes causal lift**.

Here's how you do that without Vera's full four-arm design: implement two conditions:
1. **Naïve aggregation**: run mypy + pytest every iteration, concatenate outputs.
2. **Priority cascade**: run mypy first; only if clean, run pytest; only pass one feedback source per iteration.

Prediction: If routing matters, cascade should reduce iteration count or regression rate on dual-sensitive tasks relative to naïve aggregation under equal token budget. If performance is identical, your "orchestration" adds nothing beyond extra information. That's the stress test.

On impact: you need to articulate why this matters beyond HumanEval. What assumption are you making? That real-world codebases exhibit heterogeneous error classes where feedback types vary in precision and latency. Then say that explicitly. Frame this as a **general control policy problem**: given heterogeneous feedback channels with different costs and reliabilities, can a routing policy improve correction efficiency? That abstraction differentiates you from tool-stacking papers. Otherwise, reviewers will say, "Yes, combining tools helps. We knew that."

Finally, your ≥10pp improvement target — why 10? Is that powered? If N=10 dual-sensitive tasks, a single additional solved task is already 10pp. That's not robust. Either increase N to ~20 for that slice or report confidence intervals and treat this as an effect-size estimation study, not hypothesis confirmation. Be honest about statistical fragility.

Tough love: you're close. But tighten task definition, isolate the causal role of routing, and elevate the framing beyond "two tools are better than one."

**Key Points:**
- Predefine and freeze an objective, non-circular task classification before evaluation.
- Compare cascade routing against naïve aggregation to isolate orchestration's causal effect.
- Reframe impact as a general feedback routing policy problem and justify statistical power for claimed improvement.

---

### Exchange 5

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Rex's critique is surgical — and it transforms this from an incremental systems paper into a research contribution with broader implications. Let me build on the "general control policy problem" framing and articulate why this matters to the VerifAI workshop and the broader LLM safety community.

**The real research question here is not "do two tools work better than one?"**

It's: **"Can we demonstrate principled feedback routing as an alternative to heavyweight formal verification for practical LLM code generation?"**

This positions our work directly at the VerifAI workshop's special theme: "lightweight formal methods integration with LLMs for code generation." Here's the narrative:

The formal methods community has powerful tools (SMT solvers, proof assistants, model checkers) but they require expertise and multi-hour proof time — our h-e1 failure demonstrated this. The LLM code generation community has execution feedback and test-driven approaches, but they suffer from two problems:
1. **Overfitting to tests**: LLMs can game the feedback loop (as Bose, 2025 showed with property-based testing revealing 18-23% additional failures)
2. **Lack of compositional verification**: Tests validate end-to-end behavior but don't provide modular safety guarantees

**Our contribution bridges these communities:**

Static analysis tools (mypy, pylint) provide *lightweight formal guarantees* — they check properties compositionally (type safety, null safety) without execution. But they need to be orchestrated with execution feedback to catch logic errors. The question is: can we design a routing policy that achieves *fast iteration* (static checks are instant) while maintaining *comprehensive coverage* (execution catches logic gaps)?

**Impact dimensions I see:**

1. **Methodological**: Prof. Rex's cascade vs. naïve aggregation comparison **directly tests whether orchestration is a valid research primitive**. If cascade shows no advantage over concatenation, we've learned that feedback routing doesn't matter — that's a negative result worth publishing at VerifAI (they explicitly welcome negative results).

2. **Practical**: If routing policy demonstrates 10-20pp improvement AND reduced iteration count, this informs real-world LLM code assistant design. GitHub Copilot, Cursor, Aider — all these tools currently use execution feedback only. Our work would provide evidence for when to trigger static vs. dynamic checks.

3. **Theoretical**: The "general control policy problem" framing opens a research direction: given N feedback sources with varying latency/precision tradeoffs, what is the optimal routing policy under iteration budget constraints? This connects to active learning and Bayesian optimization literature.

**Target audience and contribution claims:**

For **VerifAI workshop**: We demonstrate that lightweight formal methods (static analysis) can be systematically integrated with LLM code generation through routing policies, without requiring custom SMT templates or multi-hour proofs. This addresses their special theme directly.

For **broader ML community**: We provide empirical evidence on feedback orchestration effectiveness and introduce the routing policy abstraction as a design pattern for tool-augmented LLMs.

**Addressing Prof. Rex's statistical power concern:**

I agree N=10 dual-sensitive tasks is fragile. Here's a more robust design:
- Identify 20-30 dual-sensitive tasks (pre-registered, frozen classification)
- Primary outcome: Average iteration-to-solution count (continuous variable, more statistical power)
- Secondary outcomes:
  - Pass@1 success rate (binary, needs larger N)
  - Regression introduction rate (did orchestration cause new bugs?)
  - Token efficiency (solutions per feedback token, normalizes for verbosity)

With iteration count as primary outcome, we can use paired t-test (cascade vs. aggregation on same tasks), which has better power than independent proportions test.

**Key Points:**
- Reframe as "lightweight verification routing policy" — positions against heavyweight formal methods
- VerifAI contribution: evidence that static analysis + orchestration can replace SMT-heavy approaches
- Methodological contribution: cascade vs. aggregation isolates causal role of routing
- Use iteration count as primary outcome for better statistical power (N=20-30 sufficient)

**Next step:** Dr. Ally should synthesize this into a concrete hypothesis statement with measurable predictions.

---

### Exchange 6

🔬 **Prof. Vera** (Rigorous Validation Architect):

The evidence suggests we are converging on a properly falsifiable core: *routing policy as the causal variable*. I agree with Prof. Rex that without isolating routing from mere signal aggregation, this reduces to "more feedback helps." That is not a scientific contribution. Therefore, I propose the following pre-registered primary hypothesis:

> **H1 (Routing Causality):** On pre-registered dual-sensitive tasks (N ≥ 20), a priority cascade policy (static → execution, single-source feedback per iteration) will reduce mean iterations-to-correct-solution by ≥20% relative to naïve aggregation (static + execution concatenated each iteration), under equal token budget constraints.

This is precise. It has a measurable effect size. It can fail. If the 95% confidence interval of the paired mean difference includes zero, or the reduction is <20%, H1 is not supported.

Now to the critical issue of task classification. I concur with Prof. Rex: categories must be frozen prior to evaluation and independent of orchestration outcomes. I recommend the following operational definition. Before any routing experiments, generate a fixed pool of candidate incorrect solutions per HumanEval task using a baseline LLM (single-shot, temperature fixed, K=20 samples). For each task:
- If ≥1 sample fails mypy (strict mode) but passes visible tests → mark as *type-sensitive candidate*.
- If ≥1 sample passes mypy but fails hidden oracle tests → mark as *logic-sensitive candidate*.
- If both conditions are satisfied (via distinct samples), classify as *dual-sensitive*.
This classification depends only on baseline sampling, not on the routing systems being evaluated. Freeze the list. Archive it. Any post hoc reclassification invalidates the study. What would disprove the dual-sensitive framing? If fewer than 20 tasks meet criteria, statistical power collapses and the hypothesis becomes exploratory.

Regarding outcome measures: Dr. Sage is correct that iteration count offers greater statistical power than pass@1. However, iteration count must be carefully defined. I propose: one iteration equals one model generation conditioned on a single feedback source (cascade) or concatenated feedback (aggregation). Impose a hard cap (e.g., 5 iterations). Record (a) iterations to first solution passing hidden tests and mypy, (b) total tokens consumed. Token equality is a non-negotiable control; aggregation must not receive a larger informational budget. If aggregation uses more tokens per iteration, the comparison is confounded.

Finally, the achilles heel: it is entirely plausible that aggregation performs as well or better because the model internally prioritizes signals regardless of presentation order. If so, routing policy adds no independent causal value. We must state this explicitly. A null result here would suggest that LLMs already perform implicit feedback weighting, and external orchestration is redundant. That would be a meaningful negative finding for VerifAI.

If the cascade policy demonstrates statistically significant iteration reduction without increased regression rate, under strict pre-registration and controlled token budgets, then I will say: *This meets my standards.*

**Key Points:**
- Define a pre-registered, non-circular dual-sensitive task classification using baseline-generated counterexamples.
- Test a precise, falsifiable routing hypothesis with ≥20 tasks, paired analysis, ≥20% iteration reduction target, and equal token budgets.
- Explicitly acknowledge and test the null: aggregation may perform equivalently, invalidating routing as a causal factor.

---

### Exchange 7

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Excellent — we now have the core scientific scaffolding. Let me synthesize the discussion into a complete, strengthened hypothesis that's ready for Phase 2B refinement.

**CONSENSUS HYPOTHESIS:**

*"Priority-based feedback routing policies for LLM code generation provide causal iteration efficiency gains beyond naïve signal aggregation, when applied to tasks requiring compositional verification (type safety + logical correctness)."*

**Core Mechanism:**

The cascade policy operates as a **staged verification protocol** that mimics human debugging patterns:
1. **Static analysis first** (mypy strict mode): Instant compositional verification of type safety, null checks, function signatures — catches ~30-40% of bugs with zero execution cost
2. **Execution feedback second** (pytest): Only triggered if static checks pass, validates logical correctness through test cases
3. **Single-source per iteration**: LLM receives focused feedback from one source at a time, avoiding information overload and forced prioritization

This differs from naïve aggregation (which dumps both sources simultaneously) in three ways:
- **Attention economy**: Humans read one error message at a time; likewise, single-source may reduce LLM context confusion
- **Cost efficiency**: Skip expensive test execution if static analysis already identifies issues
- **Failure localization**: When cascade takes 2 iterations (static → fix → execution), we learn that both error types were present; aggregation conflates them

**Pre-Registered Predictions (Falsifiable):**

1. **Primary (H1 - Routing Causality):**
   - Metric: Mean iterations-to-correct-solution
   - Tasks: N ≥ 20 dual-sensitive tasks (pre-classified using K=20 baseline samples per task)
   - Comparison: Cascade vs. Naïve Aggregation (paired t-test)
   - Effect size: ≥20% reduction in iteration count (e.g., 3.0 iters → 2.4 iters)
   - Constraints: Equal token budget per condition (control for verbosity)
   - Failure condition: CI includes zero OR reduction <20%

2. **Secondary (H2 - Type Safety Efficiency):**
   - Metric: Fraction of type errors caught in first iteration (before any execution)
   - Prediction: Cascade ≥ 60% type errors resolved in iteration 1; Aggregation ≤ 40% (due to split attention)
   - Rationale: Cascade forces LLM to focus exclusively on mypy output; aggregation dilutes it

3. **Negative Control (H3 - Regression Rate):**
   - Metric: Rate of introducing new bugs when fixing identified issues
   - Prediction: Cascade ≤ Aggregation (not worse) — if cascade causes MORE regressions, routing policy is harmful
   - Measurement: Compare iteration N solution to N+1 solution on orthogonal tests

**Task Classification Protocol (Pre-Registration):**

Step 1: Generate K=20 candidate solutions per HumanEval task using CodeLlama-7B (temperature=0.8, single-shot, no feedback)
Step 2: For each candidate, run mypy --strict and pytest (visible tests)
Step 3: Classify tasks:
   - Dual-sensitive: ≥1 sample fails mypy but passes pytest, AND ≥1 sample passes mypy but fails pytest (distinct samples)
   - Type-sensitive only: Only mypy failures exist
   - Logic-sensitive only: Only pytest failures exist
   - Neither: All samples pass both or fail both (exclude from study)
Step 4: Freeze list, archive results, pre-register task IDs (e.g., HumanEval/42, HumanEval/57, ...)
Step 5: If <20 dual-sensitive tasks found, expand to MBPP+ corpus

**Implementation Feasibility (Prof. Pax's constraints):**

- Task count: 3-5 tasks (minimal orchestrator, baseline wrapper, evaluation harness, classification script, analysis/viz)
- Time budget: <30min per experimental run (20 tasks × 5 max iters × 2 conditions = 200 LLM calls @ ~5 sec each = 17min)
- Data scale: HumanEval (164 tasks) + MBPP+ (378 tasks) = 542 total, well under 10K limit
- No training: Pure inference-only evaluation using pretrained CodeLlama-7B
- Existing tools only: mypy (pip install), pytest (pip install), no custom DSL

**Novelty Positioning (from Dr. Sage):**

- **Against formal methods community**: "Lightweight formal verification routing" as alternative to SMT-heavy approaches (h-e1 failed with 42 CWE templates)
- **Against LLM code generation community**: First empirical evidence on feedback routing causality (prior work: LLMDebugger, PerfCodeGen use single sources only)
- **Methodological contribution**: Cascade vs. Aggregation ablation isolates routing policy as independent variable

**Remaining Risks (Prof. Rex's stress tests):**

1. **Null result is possible**: Aggregation may perform equally well → implies LLMs internally prioritize feedback, external routing is redundant → publishable negative result at VerifAI
2. **Classification may yield <20 tasks**: Power collapses → treat as exploratory, report effect sizes with wide CIs
3. **Token budget enforcement**: If aggregation systematically uses fewer tokens (e.g., duplicate info suppressed), we can't claim efficiency gains → report tokens per solution

**Key Points:**
- Hypothesis: Priority cascade provides causal iteration efficiency beyond aggregation
- Three pre-registered predictions: iteration reduction (≥20%), type error efficiency (≥60% first-iter), no increased regressions
- Pre-classified dual-sensitive tasks using baseline samples (frozen before evaluation)
- Implementation fits <30min, <10K samples, 3-5 tasks, inference-only constraints
- Positioned as lightweight verification routing (VerifAI contribution)
- Null result is meaningful: if aggregation equals cascade, routing doesn't matter

**Convergence check:** Have we met all criteria?
- ✅ SPECIFIC: "Priority cascade reduces iterations by ≥20% vs. aggregation"
- ✅ MECHANISM: Staged verification (static first, execution second, single-source per iteration)
- ✅ PREDICTIONS: 3 pre-registered metrics with falsification criteria
- ✅ NOVELTY: First routing causality test; lightweight verification positioning
- ✅ FEASIBILITY: <30min, <10K samples, 3-5 tasks, inference-only
- ✅ OBJECTIONS: Null result addressed (aggregation may equal cascade)

Ready for Final Assessments?

---

### Exchange 8

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good. This is the first version that feels like a study instead of a tool demo. But here's where I'm still uneasy.

First: your **20% iteration reduction threshold**. Why 20%? Right now it reads as aspirational, not justified. If the baseline mean is 2.5 iterations, a 20% reduction is 0.5 iterations. Is that practically meaningful? Is it detectable with N=20 under realistic variance? Show me a back-of-the-envelope power calculation. What would convince me is a simulated power analysis assuming σ ≈ 1 iteration and a paired design. If you can demonstrate ≥80% power to detect a 0.5 iteration mean difference at α=0.05 with N=20, I'll accept 20% as principled. Otherwise, you're picking a round number and hoping.

Second: your **dual-sensitive classification protocol** is better, but it hides a landmine. You're using visible tests for logic failure detection during classification. That means your logic-sensitive criterion is conditional on the test suite quality. If tests are weak, you under-classify logic sensitivity. Worse: if orchestration later overfits those same tests, your evaluation is partially aligned with your classification filter. That's a subtle coupling. What would convince me is this: classification uses visible tests only, but evaluation success requires passing an augmented hidden test set (e.g., MBPP+ style robustness tests). Otherwise, you risk selecting tasks that are "dual-sensitive under shallow tests" and then measuring improvement under the same shallow oracle.

Third: your cascade vs. aggregation comparison still has a hidden asymmetry. In aggregation, the model sees both error sources simultaneously. In cascade, it sees them sequentially. That's not just routing — that's a difference in *information timing*. If cascade wins, is it because of prioritization, or because it enforces temporal decomposition of the debugging task? To isolate routing as policy rather than serialization effect, I'd like to see a third arm:

- **Staged Aggregation**: Run both mypy and pytest each iteration, but only show one source per iteration, alternating deterministically (mypy on odd iterations, pytest on even), regardless of pass/fail.

If cascade outperforms staged aggregation, then conditional routing (i.e., "only run execution if static passes") is doing real work. If they're similar, the benefit may simply be serialized cognitive load reduction.

Fourth: your H2 prediction (≥60% type errors resolved in iteration 1 under cascade) feels brittle. That assumes type errors are fixable in one pass and that mypy messages are clean. Have you audited mypy's error verbosity under `--strict`? Some messages cascade (one root error produces five downstream errors). Aggregation might actually help here by giving execution context that disambiguates type intent. I'd soften H2 into an empirical question rather than a directional claim with numeric thresholds unless you have pilot data.

Now, where you've improved substantially: you've clearly isolated routing as the causal variable, acknowledged the null result, and imposed token parity. That's real rigor. But token parity needs operationalization. Equal *maximum* token budget is not enough. You must log actual tokens consumed per solved task and report efficiency as "tokens-to-solution." If cascade reduces iterations but increases tokens per iteration (due to verbose mypy traces), your efficiency claim collapses.

Here's what would make me say, "Now you've addressed my concerns":
- A brief power justification for the ≥20% threshold.
- Augmented hidden evaluation tests decoupled from classification tests.
- Inclusion of staged aggregation to disentangle conditional routing from mere serialization.
- Explicit token-to-solution efficiency reporting.

You're close. But reviewers don't attack what you intended — they attack what you didn't control.

**Key Points:**
- Justify the ≥20% effect size with power analysis; don't rely on a round-number target.
- Decouple task classification from evaluation by using stronger hidden tests at evaluation time.
- Add a staged aggregation control to isolate conditional routing from simple serialization effects.

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Rex, your critiques are valid but some push beyond our proof-of-concept budget. Let me separate what's feasible from what's aspirational, then propose a scaled version that addresses your core concerns without exploding implementation scope.

**On the 20% threshold and power analysis:**

You're right — it's aspirational. Here's the back-of-envelope calculation you want:
- Paired t-test, α=0.05, β=0.20 (80% power)
- Assume baseline μ=3.0 iterations, cascade μ=2.4 (20% reduction = 0.6 iterations)
- Assume within-pair σ ≈ 0.8 iterations (based on PerfCodeGen paper reporting σ ≈ 1.0 for execution feedback)
- Required N using paired t formula: N ≈ 18 tasks

So yes, N=20 is powered for a 0.6 iteration difference IF σ ≤ 0.8. But you're right that this is speculative. **Revised approach:**

Make H1 explicitly exploratory with pre-registered direction but no fixed threshold:
> *"H1 (Routing Causality - Exploratory): Cascade will reduce mean iterations relative to aggregation. We will report the paired mean difference, 95% CI, Cohen's d effect size, and interpret practical significance post-hoc. If CI excludes zero and d ≥ 0.5, we consider this meaningful."*

This is more honest — we're estimating effect size, not testing a specific threshold. VerifAI welcomes exploratory studies.

**On hidden tests vs. visible tests coupling:**

This is a REAL problem and I agree completely. **Feasible solution:**
- Classification uses HumanEval's **visible** tests (provided)
- Evaluation uses HumanEval**+** augmented tests (evalplus package provides these for free — 80+ additional tests per task)
- Report two success rates: visible-only pass rate (may show circularity) and HumanEval+ full test pass rate (true correctness)

This adds zero implementation burden (evalplus is pip install, 1 line of code) and cleanly decouples classification from evaluation. I'll commit to this.

**On staged aggregation third arm:**

This is where I push back on feasibility. Adding a third condition means:
- Implementing a new routing policy (deterministic alternation logic)
- 50% more LLM calls (N×2 becomes N×3 conditions)
- Statistical power dilution (we'd need N=30-40 for three-way comparison)

**Compromise:** Report qualitative analysis of iteration transcripts. In the paper, manually inspect 5 representative dual-sensitive tasks and show whether cascade's conditional routing (skip execution when static fails) actually triggered differently than a serialization-only strategy would. If static errors are fixed by iteration 2, and execution only runs iteration 3+, that's evidence of conditional routing value. If static errors persist through iterations while execution alternates anyway, that undermines the routing claim.

This is a **post-hoc interpretability analysis**, not a controlled experiment, but it's honest about what we can demonstrate within scope.

**On H2 brittleness (60% type errors iteration 1):**

I agree this is fragile. **Revised H2 to empirical reporting:**
> *"H2 (Error Resolution Patterns - Descriptive): We will report the distribution of error types resolved per iteration for cascade vs. aggregation. If cascade shows earlier resolution of static analysis errors (median iteration 1-2) while aggregation shows more mixed resolution patterns, this supports attentional focusing. No pre-registered threshold."*

This turns H2 into a descriptive analysis instead of a brittle prediction. More appropriate for proof-of-concept.

**On tokens-to-solution efficiency:**

100% agree. **Implementation commitment:**
- Log feedback tokens consumed per iteration (using tiktoken on feedback strings)
- Report per-task metrics: total iterations, total feedback tokens, success/failure
- Primary comparison: mean iterations to solution (our H1)
- Secondary comparison: mean tokens-to-solution (efficiency check)
- If cascade reduces iterations but increases tokens-per-iteration, we report this transparently

This is ~10 lines of logging code, completely feasible.

**Revised Implementation Scope (Still Fits <30min, 3-5 Tasks):**

1. **Task A-1:** Classification script (generate K=20 baseline samples, classify dual-sensitive using visible tests, freeze list)
2. **Task A-2:** Cascade policy orchestrator (static first, execution only if clean)
3. **Task A-3:** Aggregation baseline (concatenate both sources each iteration)
4. **Task A-4:** Evaluation harness (run both policies on N=20 dual-sensitive tasks, HumanEval+ full tests for success, log iterations + tokens)
5. **Task A-5:** Analysis + visualization (paired t-test, tokens-to-solution, qualitative routing transcript analysis)

Total: 5 tasks, ~15-20 complexity points, fits LIGHT tier. Runtime: 20 tasks × 2 conditions × 5 max iterations = 200 calls @ 10 sec each = ~30min.

**What We're NOT Doing (Deferred to Future Work):**
- Three-arm staged aggregation control → qualitative transcript analysis instead
- Pilot data for H2 threshold tuning → make H2 descriptive instead
- Power analysis based on real variance → report exploratory effect size estimation

**What We ARE Doing (Addresses Core Rex Concerns):**
- ✅ Power-justified N=20 (assuming σ ≤ 0.8, defensible from prior work)
- ✅ Hidden tests decoupling (HumanEval+ for evaluation, visible for classification)
- ✅ Tokens-to-solution efficiency reporting (catches verbosity confounds)
- ✅ Explicit acknowledgment of null result validity

**Key Points:**
- Revise H1 to exploratory effect-size estimation (more honest than fixed 20% threshold)
- Use HumanEval+ augmented tests for evaluation to decouple from classification
- Add qualitative transcript analysis instead of three-arm experiment (feasibility trade-off)
- Log and report tokens-to-solution efficiency to catch verbosity confounds
- Final scope: 5 tasks, ~20 complexity points, <30min runtime — feasible for Phase 4

If Prof. Vera and Dr. Sage can accept these feasibility trade-offs while preserving scientific integrity, I think we have a convergent hypothesis.

---

### Exchange 10

🔬 **Prof. Vera** (Rigorous Validation Architect):

The evidence suggests we are now balancing ambition with methodological discipline. I accept the shift from a fixed ≥20% threshold to an effect-size–focused H1, provided it remains quantitatively anchored. However, let us be precise: an exploratory claim must still define what constitutes *practically meaningful*. Reporting a paired mean difference with 95% CI and Cohen's d is appropriate. I recommend pre-specifying that if the CI excludes zero *and* the lower bound of d exceeds 0.3, we interpret this as at least a small-to-moderate effect. Anything weaker should be described as inconclusive. What would disprove routing causality? A CI spanning zero with |d| < 0.3. That must be stated explicitly in advance.

I strongly endorse the decoupling of classification and evaluation via HumanEval+ augmented tests. The prior coupling between visible tests (for classification) and evaluation success was a subtle but real threat to validity. Using visible tests only to *identify task sensitivity*, then requiring passage of HumanEval+ hidden tests for success, restores independence between selection and outcome measurement. This design ensures that routing is evaluated against a stricter oracle than the one used for task filtering. If cascade improves visible-test performance but fails to improve HumanEval+ pass rates, the hypothesis collapses under stronger scrutiny. That is exactly the kind of asymmetry we must be prepared to observe.

On the absence of a third "staged aggregation" arm: while I understand the feasibility constraint, we must be careful in our causal language. Without that control, we cannot definitively attribute gains to *conditional routing* rather than mere serialization. Therefore, any claim should be framed narrowly: "sequential single-source routing outperforms simultaneous aggregation under equal budgets." Not "conditional execution skipping provides benefit." The qualitative transcript analysis you propose is acceptable as exploratory evidence of mechanism, but it must not be conflated with causal proof. The paper should clearly label mechanism claims as hypothesized, not established.

Token accounting is non-negotiable. I recommend defining two secondary efficiency metrics: (1) total feedback tokens-to-solution, and (2) total wall-clock LLM calls-to-solution. If cascade reduces iterations but increases tokens-to-solution by >15%, we must report this as a trade-off rather than a pure gain. Additionally, cap maximum feedback length per iteration to avoid asymmetry from verbose mypy traces. Otherwise, routing may appear superior simply because it constrains context size. What would disprove the efficiency claim? Equal or higher tokens-to-solution under cascade despite fewer iterations.

Finally, I want one additional robustness check: randomize task order and fix model temperature and seed per task-condition pair to ensure paired comparability. Variance inflation from stochastic decoding could obscure or fabricate effects. If the paired differences remain stable under two independent random seeds, confidence increases substantially. If results flip sign across seeds, the effect is likely noise.

If these controls are implemented and reported transparently, I would consider the study scientifically defensible. Not definitive—but rigorous.

**Key Points:**
- Pre-specify quantitative interpretation of effect sizes (CI exclusion of zero and d > 0.3) to prevent post-hoc narrative inflation.
- Decouple classification (visible tests) from evaluation (HumanEval+) to eliminate selection–outcome coupling.
- Control and report tokens-to-solution, cap feedback verbosity, and stabilize randomness to preserve causal interpretability.

---

### Exchange 11

🎯 **Dr. Sage** (Research Impact Evaluator):

I believe we've reached a scientifically defensible AND practically impactful hypothesis. Let me articulate why this refined version addresses VerifAI's workshop goals and broader community needs, then propose we move to Final Assessments.

**VerifAI Workshop Positioning:**

The workshop explicitly seeks work on "lightweight formal methods integration with LLMs for code generation" and welcomes works-in-progress. Our refined hypothesis hits this target perfectly:

1. **Lightweight formal methods**: Static analysis (mypy) provides compositional formal guarantees (type safety) without heavyweight SMT solvers or multi-hour proofs
2. **Integration mechanism**: Sequential routing policies as the integration layer, not ad-hoc tool stacking
3. **Proof-of-concept scope**: N=20 tasks, exploratory effect size estimation, acknowledges limitations

The key message for VerifAI: *"We provide empirical evidence that formal guarantees from static analysis can be systematically integrated with execution feedback through routing policies, achieving practical efficiency gains without the infrastructure burden of traditional formal verification."*

**Methodological Contribution (Addresses Prof. Vera's Standards):**

- Pre-registered task classification (K=20 baseline samples, frozen before evaluation)
- Decoupled evaluation oracle (HumanEval+ hidden tests vs. classification visible tests)
- Token-to-solution efficiency metrics (catches verbosity confounds)
- Effect size estimation with d > 0.3 threshold (honest about statistical power)
- Paired design with fixed seeds (controls stochastic variance)
- Narrow causal claims ("sequential routing outperforms aggregation", not "conditional skipping proven beneficial")

This is publishable even with a null result — if aggregation equals cascade, we've shown that routing policy doesn't matter, which is useful negative evidence.

**Practical Impact (Even as Proof-of-Concept):**

If cascade demonstrates d ≥ 0.5 effect on iteration reduction with HumanEval+ success:
- **Tool developers** (Cursor, Aider, GitHub Copilot): Consider sequential feedback presentation instead of simultaneous error dumps
- **LLM researchers**: Routing policies as a design primitive for tool-augmented systems (generalizes beyond code generation)
- **Verification community**: Lightweight static analysis CAN integrate with LLMs effectively (rebuttal to "formal methods are too heavy")

**Risk Assessment:**

Prof. Rex's concerns are addressed within feasibility constraints:
- No three-arm control → honest about mechanism ambiguity (serialization vs. conditional routing)
- H2 made descriptive → no brittle 60% threshold
- 20% threshold removed → effect size estimation with d > 0.3 interpretive anchor

Remaining risks:
- <20 dual-sensitive tasks found → report as exploratory, expand to MBPP+ if needed
- Aggregation equals cascade → publishable negative result at VerifAI
- Tokens-to-solution worse under cascade → report as trade-off, not pure gain

**Implementation Feasibility Confirmed:**

Prof. Pax's 5-task breakdown:
1. Classification script (~4 complexity)
2. Cascade orchestrator (~5 complexity)
3. Aggregation baseline (~3 complexity)
4. Evaluation harness (~5 complexity)
5. Analysis + viz (~3 complexity)
Total: ~20 complexity points, 5 tasks, LIGHT tier, <30min runtime

**Convergence Assessment:**

- ✅ **SPECIFIC**: "Sequential single-source routing (cascade) reduces mean iterations-to-solution relative to simultaneous aggregation, with effect size d > 0.3 on N=20 dual-sensitive HumanEval tasks"
- ✅ **MECHANISM**: Staged verification (static → execution, single-source per iteration) vs. aggregation (both sources concatenated)
- ✅ **PREDICTIONS**:
  - H1: Paired mean iteration reduction, d > 0.3, CI excludes zero
  - H2 (descriptive): Error resolution patterns show earlier static error fixes under cascade
  - Efficiency metrics: Tokens-to-solution, LLM-calls-to-solution
- ✅ **NOVELTY**: First empirical test of feedback routing causality (vs. single-source or naive aggregation)
- ✅ **FEASIBILITY**: 5 tasks, <30min, N=20, inference-only, existing tools (mypy, pytest, evalplus)
- ✅ **OBJECTIONS**: Null result acknowledged, mechanism ambiguity addressed with narrow claims

**I recommend we proceed to Final Assessments.**

All personas have contributed substantive refinements. The hypothesis is scientifically rigorous (Prof. Vera satisfied), methodologically sound (Prof. Rex's critiques addressed within feasibility bounds), implementable within constraints (Prof. Pax confirmed), and positioned for meaningful impact (VerifAI + broader communities).

**Key Points:**
- Hypothesis targets VerifAI's "lightweight formal methods + LLM" theme directly
- Methodological rigor: pre-registration, decoupled oracles, token accounting, effect size anchoring (d > 0.3)
- Practical impact: informs tool design for code assistants, provides negative result value
- Feasibility confirmed: 5 tasks, ~20 complexity, <30min, fits LIGHT tier constraints
- All convergence criteria met → ready for Final Assessments

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Now we're talking. This version is disciplined. But I'm not here to applaud — I'm here to see if anything still cracks under pressure.

First, on H1: shifting from a fixed ≥20% reduction to effect-size estimation with a pre-specified interpretation (CI excludes zero *and* d > 0.3) is the right move. That's defensible. But here's where this can still break down: your assumed σ ≤ 0.8 for iterations. That assumption is doing a lot of work. If σ drifts to 1.2 — which is entirely plausible under stochastic decoding — your power collapses. What would convince me is this: before running the full N=20 comparison, run a 5-task pilot under aggregation only and estimate within-task iteration variance across two seeds. If empirical σ > 1.0, you explicitly downgrade claims to "underpowered exploratory." Don't discover post hoc that your detectable effect was fantasy.

Second, on mechanism claims. I accept dropping the staged aggregation arm for feasibility, but then you must amputate causal language with surgical precision. If cascade wins, the only claim you are allowed is: *"Sequential single-source presentation improves convergence relative to simultaneous multi-source presentation under fixed budgets."* Full stop. You cannot attribute benefit to conditional skipping of execution, nor to prioritizing formal guarantees, without that third arm. If you even hint at "causal evidence for routing policy," reviewers will pounce. Your qualitative transcript analysis must explicitly test one prediction:
- If cascade's benefit is due to conditional gating, then execution feedback should appear in fewer total iterations than in aggregation, and primarily *after* static convergence.
If that pattern doesn't appear, your mechanism story weakens substantially.

Third, good — you've finally taken token accounting seriously. But don't just log total feedback tokens. Break it down into:
1. Static-analysis tokens
2. Execution-feedback tokens
3. Model response tokens

If cascade reduces iterations but increases static-feedback verbosity by 2×, that tells us something about cognitive load shaping versus informational efficiency. What would convince me of true efficiency gain is: lower or equal total tokens-to-solution *and* fewer iterations. If tokens increase by >15% (as Vera suggested), you must frame the result as a trade-off, not a win.

Fourth, the classification protocol. Decoupling via HumanEval+ is excellent. But here's the unstated assumption: that dual sensitivity under visible tests correlates with meaningful robustness under HumanEval+. If many "dual-sensitive" tasks fail HumanEval+ even after passing visible tests, your classification may be selecting brittle tasks rather than genuinely dual-signal ones. I want one sanity check: report the proportion of baseline (no-orchestration) solutions that pass visible tests but fail HumanEval+. If that's high (>30%), your task pool is systematically shallow under visible tests, which complicates interpretation.

Now — where you've genuinely improved:
- Pre-specifying d > 0.3 as practically meaningful
- Decoupling selection and evaluation oracles
- Fixing seeds and randomizing task order
- Narrowing causal language

That's rigor. I'm no longer worried this is a tool demo masquerading as science. I'm now evaluating it as a constrained causal comparison with honest scope.

If you implement the variance pilot, mechanism-prediction check in transcripts, and token breakdown reporting, I'll say it plainly: *Now you've addressed my concerns.*

**Key Points:**
- Validate variance assumptions with a small pilot; don't rely on optimistic σ for power claims.
- Sever mechanism claims from routing results unless transcript evidence matches explicit gating predictions.
- Report granular token accounting and visible-vs-HumanEval+ robustness to prevent hidden confounds.

---

### Exchange 13

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Rex, I accept every one of your final refinements. These are the controls that transform this from "promising idea" into "defensible science." Let me incorporate them into the FINAL CONVERGED HYPOTHESIS.

## ✅ CONVERGED HYPOTHESIS (Ready for Phase 2B)

**Title:** Sequential Single-Source Feedback Routing for LLM Code Generation: A Lightweight Formal Verification Integration

**Core Claim:**
Sequential single-source feedback presentation (static analysis → execution, one source per iteration) improves iteration-to-solution efficiency relative to simultaneous multi-source aggregation on programming tasks requiring compositional verification guarantees.

**Mechanism (Hypothesized, Not Causally Established):**
Cascade routing enforces staged verification: mypy (instant type checking) → pytest (execution validation only if static clean). This may reduce cognitive load (single-source attention) and computational cost (skip execution if static fails), but mechanism attribution requires staged-aggregation control (deferred to future work).

**Pre-Registered Protocol:**

1. **Pilot Phase (N=5 tasks):**
   - Run aggregation-only baseline on 5 randomly selected dual-sensitive tasks, 2 seeds each
   - Estimate empirical within-task σ for iteration count
   - If σ > 1.0 → downgrade H1 to "underpowered exploratory"
   - Archive pilot data, freeze estimate before main comparison

2. **Task Classification (Pre-Registered, Frozen Before Evaluation):**
   - Generate K=20 baseline samples per HumanEval task (CodeLlama-7B, temp=0.8, single-shot, fixed seed)
   - Dual-sensitive: ≥1 sample fails mypy --strict but passes visible tests, AND ≥1 passes mypy but fails visible tests (distinct samples)
   - Freeze N=20 dual-sensitive task list (expand to MBPP+ if <20 found)
   - Report baseline visible-pass-but-HumanEval+-fail rate as classification validity check (target <30%)

3. **Experimental Conditions (Paired Design, N=20):**
   - **Cascade:** mypy → pytest (execution only if mypy clean), single-source feedback per iteration
   - **Aggregation:** mypy + pytest concatenated, both sources every iteration
   - Max 5 iterations, fixed seed per task-condition pair, randomized task order
   - Success criterion: Pass HumanEval+ full augmented test suite (not just visible tests)

4. **Pre-Registered Outcomes:**

**H1 (Primary - Effect Size Estimation):**
- Metric: Paired mean difference in iterations-to-solution (cascade - aggregation)
- Pre-specified interpretation:
  - CI excludes zero AND lower bound d > 0.3 → "meaningful efficiency gain"
  - CI excludes zero AND d ∈ [0.2, 0.3) → "small effect, interpret cautiously"
  - CI includes zero OR |d| < 0.2 → "no evidence for routing benefit"
- Failure condition: CI includes zero with |d| < 0.3

**H2 (Descriptive - Error Resolution Patterns):**
- Metric: Distribution of iteration number where (a) mypy errors resolve, (b) pytest errors resolve
- Report median + IQR for each condition
- No pre-specified threshold; descriptive comparison only

**Efficiency Metrics (Secondary):**
- Tokens-to-solution (granular breakdown):
  1. Static-analysis feedback tokens
  2. Execution-feedback tokens
  3. Model generation response tokens
- LLM-calls-to-solution (wallclock efficiency)
- If cascade increases tokens-to-solution by >15% → report as "iteration vs. token trade-off"

**Mechanism Evidence (Qualitative, Exploratory):**
- For 5 representative dual-sensitive tasks, analyze iteration transcripts:
  - Count iterations with execution feedback in cascade vs. aggregation
  - Check if execution appears primarily *after* static errors resolve under cascade
  - If pattern NOT observed → mechanism hypothesis (conditional gating) unsupported
- Claims limited to: "Sequential presentation improves convergence" (NOT "conditional gating causes benefit")

5. **Robustness Checks:**
   - Two independent random seeds per task-condition pair
   - Report if results flip sign across seeds (effect is noise)
   - Cap feedback verbosity: max 1000 tokens per source per iteration (prevents asymmetry)

**Implementation Scope (Fits <30min, 5 Tasks, LIGHT Tier):**

1. Task A-1: Pilot + classification script (~6 complexity) — generate K=20 samples, classify, run pilot N=5
2. Task A-2: Cascade orchestrator (~5 complexity) — mypy first, pytest if clean, single-source feedback
3. Task A-3: Aggregation baseline (~3 complexity) — concatenate both sources each iteration
4. Task A-4: Evaluation harness (~5 complexity) — run N=20 paired, HumanEval+ evaluation, token logging
5. Task A-5: Analysis + transcript qualitative (~4 complexity) — paired t-test, tokens breakdown, mechanism check

Total: ~23 complexity points, 5 tasks, ~25-30min runtime (pilot + main)

**Positioning for VerifAI Workshop:**

*"We provide empirical evidence that lightweight formal methods (static analysis providing compositional type safety guarantees) can be systematically integrated with execution feedback through sequential routing policies, demonstrating measurable iteration efficiency gains (d > 0.3) on dual-sensitive programming tasks. This offers a practical alternative to heavyweight SMT-based verification approaches, with transparent reporting of null-result possibility and mechanism ambiguity."*

**All Convergence Criteria Met:**

- ✅ **SPECIFIC**: Sequential single-source routing improves iterations (d > 0.3, CI excludes zero)
- ✅ **MECHANISM**: Staged verification (static → execution, single-source per iteration) — hypothesized, not causally proven
- ✅ **PREDICTIONS**:
  - H1: Iteration reduction with d > 0.3 (pilot-validated power)
  - H2: Error resolution patterns (descriptive)
  - Efficiency: Tokens-to-solution breakdown
  - Mechanism: Transcript analysis (conditional gating pattern)
- ✅ **NOVELTY**: First empirical test of feedback routing vs. aggregation (Gap 1 from Phase 1)
- ✅ **FEASIBILITY**: 5 tasks, ~23 complexity, <30min, pilot + main, inference-only, existing tools
- ✅ **OBJECTIONS**: Null result acknowledged, mechanism ambiguity transparent, power validated via pilot, token trade-offs reported

**Prof. Vera's Standards Met:** Pre-registration, decoupled oracles, token accounting, variance pilot
**Prof. Rex's Concerns Addressed:** Pilot σ validation, mechanism claims severed, granular tokens, visible-HumanEval+ check
**Prof. Pax's Feasibility Confirmed:** 5 tasks, <30min, LIGHT tier
**Dr. Sage's Impact Articulated:** VerifAI positioning, tool design implications, negative result value

---

**HYPOTHESIS IS CONVERGED. Ready for Phase 2B decomposition into verifiable sub-hypotheses.**

---

### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect):

The evidence suggests this protocol is now structurally sound, provided we treat the pilot variance check as binding rather than ceremonial. I want to sharpen one detail: the pilot must estimate *paired* within-task variance under the same stochastic controls planned for the main study. That means two seeds per task, identical temperature, identical max-iteration cap, and identical feedback caps. Compute the standard deviation of the *paired difference* in iterations across seeds, not just raw iteration variance. Power depends on the variance of differences, not marginal dispersion. If the SD of paired differences exceeds 1.0, then the detectable effect size shifts materially, and the interpretation thresholds for d must be contextualized accordingly. This must be reported transparently before examining cascade results.

On H1, your pre-specified interpretive ladder (CI excludes zero and lower bound d > 0.3) is acceptable. However, I recommend computing both a paired t-test and a nonparametric alternative (e.g., Wilcoxon signed-rank). Iteration counts are discrete and capped at 5; normality is not guaranteed. If the parametric and nonparametric conclusions diverge, that divergence itself becomes evidence of distributional instability. What would disprove robustness? A significant t-test but non-significant Wilcoxon with clustered ceiling effects at 5 iterations. In that case, claims must be downgraded to "distribution-sensitive."

Regarding mechanism probing: your transcript analysis needs one additional quantitative hook. Pre-register a measurable gating index:
\\[
G = \\frac{\\text{# iterations with execution feedback before static convergence}}{\\text{total iterations}}
\\]
Under true staged gating, we predict \\( G_{cascade} < G_{aggregation} \\), ideally approaching zero. If \\( G_{cascade} \\approx G_{aggregation} \\), then the improvement—if observed—cannot be attributed to conditional sequencing. The evidence would then suggest a presentation-format effect rather than a verification-order effect. That distinction must be made explicit.

On token accounting, I approve the granular breakdown. But I want normalization. Report tokens-to-solution *conditional on success* and separately report failure cases (censored at 5 iterations). Otherwise, cascade could appear efficient simply because it fails earlier. Additionally, compute tokens-per-successful-task across the full N=20. If cascade yields fewer iterations but lower success rate, iteration efficiency is meaningless. What would falsify the efficiency claim? Equal or higher tokens-per-successful-task combined with no improvement in success probability.

Finally, I want one pre-specified handling rule for missing or degenerate outcomes. If a task is unsolved by both methods within 5 iterations under both seeds, it should remain in the paired analysis as a tied maximum (difference = 0), not discarded. Excluding hard tasks would bias toward apparent gains. The best experiments are designed to fail; retaining difficult cases ensures we are not selectively measuring only the tractable subset.

If these clarifications are written into the protocol—not implied, not assumed—then I will say, with care: this meets my standards for a constrained but rigorous causal comparison.

**Key Points:**
- Estimate and report variance of *paired differences* in the pilot; power depends on this, not marginal σ.
- Add nonparametric robustness test and a quantitative gating index to discipline mechanism claims.
- Normalize token efficiency by success and retain unsolved tasks to prevent selective bias.

---

### Exchange 15

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Vera, all of your final refinements are implementable with minimal code additions. Let me confirm feasibility and signal **CONVERGENCE**.

**Pilot Variance Estimation (Paired Differences):**
- Implementation: Run aggregation on N=5 tasks with 2 seeds each
- Compute paired difference (seed 1 - seed 2) for each of 5 tasks
- SD of paired differences: `np.std([diff_task1, diff_task2, ..., diff_task5])`
- Report before main comparison: "Pilot SD of paired differences: X.XX, power implications: [interpretation]"
- Code cost: ~5 lines, zero runtime overhead (pilot runs before main anyway)
- ✅ FEASIBLE

**Nonparametric Test (Wilcoxon Signed-Rank):**
- Implementation: `from scipy.stats import wilcoxon; wilcoxon(cascade_iters, agg_iters)`
- Report alongside paired t-test in results
- If t-test significant but Wilcoxon not → flag as "distribution-sensitive, ceiling effects at 5 iterations"
- Code cost: 1 line
- ✅ FEASIBLE

**Gating Index (Quantitative Mechanism Check):**
- Implementation: For each task-iteration, log boolean `execution_ran_before_static_clean`
- Compute per-condition: `G = (# iters with execution before static clean) / (total iters)`
- Pre-registered prediction: `G_cascade < G_aggregation` (ideally G_cascade ≈ 0)
- If G values similar → mechanism claim weakens to "presentation format, not conditional gating"
- Code cost: ~10 lines (track static error state per iteration)
- ✅ FEASIBLE

**Token Normalization by Success:**
- Implementation:
  - Filter tasks where final solution passes HumanEval+ (success subset)
  - Compute `mean_tokens_per_successful_task = sum(tokens | success) / count(success)`
  - Report separately for success vs. failure (censored at 5 iters)
  - Compare success rates: `success_rate_cascade vs. success_rate_aggregation`
- Falsification: If cascade has lower success rate OR higher tokens-per-success → efficiency claim fails
- Code cost: ~15 lines (conditional aggregation)
- ✅ FEASIBLE

**Retain Unsolved Tasks (No Selective Exclusion):**
- Implementation: For tasks unsolved by both conditions → difference = 0 (tied at max 5 iterations)
- Include in paired analysis (prevents bias toward tractable tasks)
- Code cost: 0 lines (default pandas/numpy behavior if we don't filter)
- ✅ FEASIBLE

**Total Implementation Cost of Vera's Refinements:**
- Pilot paired variance: ~5 lines
- Wilcoxon test: 1 line
- Gating index: ~10 lines
- Token normalization: ~15 lines
- Unsolved task handling: 0 lines (default)
- **Total: ~31 additional lines across Tasks A-4 (evaluation harness) and A-5 (analysis)**

This fits comfortably within our original ~23 complexity budget (now ~25 with refinements), still LIGHT tier.

**Final Scope Summary:**

- **5 Tasks**:
  1. A-1: Pilot + classification (~6 complexity) + paired variance analysis (+1) = 7
  2. A-2: Cascade orchestrator (~5 complexity) + gating index logging (+1) = 6
  3. A-3: Aggregation baseline (~3 complexity)
  4. A-4: Evaluation harness (~5 complexity) + token normalization (+2) = 7
  5. A-5: Analysis (~4 complexity) + Wilcoxon + gating index reporting (+1) = 5

- **Total Complexity**: ~28 points (was ~23, now +5 for Vera's refinements)
- **Still LIGHT Tier** (LIGHT = ≤30 complexity, <10 tasks)
- **Runtime**: ~25-30min (unchanged — all additions are post-processing or logging)

**CONVERGENCE DECLARATION:**

All personas have contributed substantive refinements:
- ✅ Dr. Nova: Identified novelty angle (orchestration framework)
- ✅ Prof. Vera: Imposed rigorous falsifiability, pre-registration, variance pilot, nonparametric robustness
- ✅ Prof. Rex: Stress-tested task circularity, mechanism ambiguity, token confounds
- ✅ Dr. Sage: Positioned for VerifAI impact, articulated negative result value
- ✅ Prof. Pax: Confirmed feasibility within constraints at every step
- ✅ Dr. Ally: Synthesized converged hypothesis with all controls

**The hypothesis is scientifically rigorous, methodologically sound, implementably feasible, and positioned for meaningful contribution.**

**Convergence criteria:**
- ✅ SPECIFIC: Sequential routing improves iterations (d > 0.3, CI excludes zero, Wilcoxon confirms)
- ✅ MECHANISM: Staged verification (single-source, static → execution), gating index G validates
- ✅ PREDICTIONS:
  - H1: Iteration reduction (paired t-test + Wilcoxon, d > 0.3)
  - Gating index: G_cascade < G_aggregation
  - Token efficiency: Tokens-per-successful-task (normalized)
  - H2: Error resolution patterns (descriptive)
- ✅ NOVELTY: First empirical routing causality test (Gap 1)
- ✅ FEASIBILITY: 5 tasks, ~28 complexity, <30min, LIGHT tier
- ✅ OBJECTIONS: Null result transparent, mechanism ambiguity acknowledged, power validated

**DISCUSSION HAS CONVERGED. Ready to write Final Assessments and proceed to Step 2 (Result Structuring).**

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis addresses a clear research gap (Gap 1 from Phase 1): no prior work tests feedback routing causality for LLM code generation. The cascade vs. aggregation comparison isolates routing policy as an independent variable, moving beyond "more tools are better" to "how tools are composed matters." The gating index provides a novel quantitative mechanism probe.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The protocol meets rigorous falsifiability standards: pre-registered task classification, variance-validated pilot, dual statistical tests (paired t-test + Wilcoxon), explicit effect size thresholds (d > 0.3), HumanEval+ decoupled evaluation oracle, and transparent null-result handling. The hypothesis can fail through multiple paths: CI spans zero, |d| < 0.3, Wilcoxon contradicts t-test, gating index shows no conditional sequencing, or token efficiency worsens.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** The research targets VerifAI workshop's core theme (lightweight formal methods + LLM integration) and provides actionable evidence for tool developers (GitHub Copilot, Cursor, Aider). Even a null result (aggregation equals cascade) has value by demonstrating that routing policies don't matter for LLM code correction. The positioned as an alternative to heavyweight SMT-based verification approaches.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Implementation scope confirmed feasible: 5 tasks, ~28 complexity points (LIGHT tier), <30min runtime, inference-only using existing tools (mypy, pytest, evalplus). All refinements (pilot variance, Wilcoxon test, gating index, token normalization) add minimal code (31 lines total) and zero runtime overhead. No training, no large datasets, no custom infrastructure.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

**Sequential Single-Source Feedback Routing for LLM Code Generation: A Lightweight Formal Verification Integration**

We hypothesize that sequential single-source feedback presentation (cascade: static analysis → execution, one source per iteration) reduces iteration-to-solution count relative to simultaneous multi-source aggregation (both sources concatenated each iteration) on programming tasks requiring compositional verification (type safety + logical correctness). The mechanism operates through staged verification: mypy provides instant compositional type checking, followed by pytest execution validation only if static checks pass. This enforces single-source attention economy and computational efficiency (skip expensive execution if static analysis identifies issues).

**Pre-Registered Protocol:**
1. Pilot N=5 tasks to estimate paired variance (SD of differences across 2 seeds), downgrade to "underpowered exploratory" if σ > 1.0
2. Classify N=20 dual-sensitive HumanEval tasks using K=20 baseline samples (freeze list before evaluation)
3. Paired comparison: cascade vs. aggregation, max 5 iterations, fixed seeds, HumanEval+ augmented tests for success

**Falsifiable Predictions:**
- **H1 (Primary):** Paired mean iteration reduction with CI excludes zero AND lower bound d > 0.3 (plus Wilcoxon robustness check)
- **Gating Index:** G_cascade < G_aggregation (execution feedback appears primarily after static convergence under cascade)
- **Token Efficiency:** Tokens-per-successful-task ≤ aggregation (no verbosity trade-off)
- **H2 (Descriptive):** Median iteration for static error resolution lower under cascade

**Novelty:** First empirical test isolating feedback routing policy causality (vs. naive aggregation or single-source baselines). Addresses Gap 1 from Phase 1 targeted research.

**Feasibility:** 5 tasks, ~28 complexity, <30min, LIGHT tier, inference-only, existing tools.

**Impact:** Positioned for VerifAI workshop as lightweight formal verification integration. Informs tool design for code assistants. Transparent null-result handling ensures publishable outcomes regardless of direction.

**Mechanism Caveat:** Without staged-aggregation control, causality is limited to "sequential presentation" not "conditional gating." Qualitative transcript analysis provides exploratory mechanism evidence only.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** Power assumption (σ ≤ 0.8) may be optimistic. **Mitigation:** Pilot estimates empirical paired variance before main comparison, downgrade to exploratory if σ > 1.0.
- **Concern 2:** Mechanism attribution is ambiguous without third-arm staged aggregation control. **Mitigation:** Narrow causal claims to "sequential vs. simultaneous presentation," use gating index for exploratory mechanism evidence, explicitly label routing causality as hypothesized not proven.
- **Concern 3:** Classification-evaluation coupling risk if tasks are shallow under visible tests. **Mitigation:** HumanEval+ augmented tests decouple evaluation oracle, report baseline visible-pass-but-HumanEval+-fail rate as validity check.

---
