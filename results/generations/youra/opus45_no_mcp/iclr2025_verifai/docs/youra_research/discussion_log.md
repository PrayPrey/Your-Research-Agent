# Phase 2A Research Discussion Log

## Briefing

**Gap ID:** gap1-static-vs-execution
**Gap Title:** No Controlled Comparison of Static-Only vs Execution-Only Feedback
**Priority:** HIGH | **Relevance:** PRIMARY

### Research Question
Does integrating lightweight static analysis feedback during LLM code generation improve functional correctness on existing code benchmarks?

### Gap Description
Papers use execution feedback (CodeRL, RLPF) OR combine static + execution (Helping LLMs 2024). No isolated static-only study exists. Missing: controlled experiment comparing (A) baseline, (B) static-only, (C) execution-only, (D) combined on same benchmark/model.

### Key Evidence from Phase 1
- "Static Analysis as Feedback Loop" (2508.14419, 2025): 40%→13% security issues in 10 iterations
- "Helping LLMs Improve Code Generation" (2412.14841, 2024): Combines testing + static feedback but doesn't isolate effects
- "Self-Refine" (2303.17651, 2023): Iterative refinement paradigm shows ~20% improvement

### Implementation Resources
- **madaan/self-refine**: Official implementation with pluggable feedback loop
- **evalplus**: HumanEval+ (80x tests), MBPP+ (35x tests) for rigorous evaluation

### Feasibility Constraints (Pipeline-Enforced)
- MUST use existing real datasets (HumanEval+, MBPP+)
- MUST use existing benchmarks (pass@k metrics)
- NO new rubrics, synthetic data, or human evaluation
- Hypothesis must be testable immediately

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we've been looking at this backwards? Everyone assumes static analysis is just a cheaper substitute for execution feedback, but I see something more interesting here. Static analysis captures *structural* properties of code that execution tests miss entirely - type flows, unused variables, unreachable branches, stylistic patterns.

Imagine this: what if static and execution feedback are actually *orthogonal* signals? The "Helping LLMs Improve Code Generation" paper combines them but treats them as additive. What if they're actually complementary in a stronger sense - static catches *different classes* of bugs than execution?

Here's my wild idea: we don't just measure pass@k improvement. We categorize the errors that each feedback type fixes. Static analysis might excel at "preventable" errors (type mismatches, undefined variables) while execution feedback catches "behavioral" errors (wrong algorithm logic). If we can show orthogonality, that's far more valuable than showing "static is 80% as good as execution for 10% of the cost."

The Self-Refine framework is perfect for this because it's pluggable - we can literally swap feedback sources and measure not just final pass@k but *what changed at each iteration*.

**Key Points:**
- Hypothesis: Static and execution feedback fix orthogonal error classes, not redundant ones
- Novel angle: Categorize errors fixed by each feedback type, not just final pass@k
- Testable via Self-Refine's pluggable architecture on HumanEval+/MBPP+

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises an intriguing angle, but I need to stress-test this "orthogonality" claim before we build a hypothesis around it. The evidence must lead; enthusiasm cannot.

First, let me be precise about what "orthogonal" means operationally. If static analysis fixes bug class A and execution feedback fixes bug class B, with minimal overlap, that's orthogonality. But how do we *measure* this without creating a new taxonomy (which violates our no-new-rubrics constraint)?

Here's my proposal: we use *existing* error categorizations. HumanEval+ and MBPP+ have ground-truth test suites. When code fails, we can categorize by: (1) syntax errors, (2) type errors, (3) runtime exceptions, (4) wrong output. Static analyzers like pylint/mypy already categorize their findings. We're not creating new rubrics - we're mapping existing tool outputs to existing failure modes.

For testability, I propose a 2x2 factorial design:
- Factor A: Static feedback (on/off)
- Factor B: Execution feedback (on/off)
- Conditions: baseline (0,0), static-only (1,0), exec-only (0,1), combined (1,1)

The specific prediction: if static and execution are orthogonal, then combined > max(static-only, exec-only). If they're redundant, combined ≈ max(static-only, exec-only).

What would disprove this? If combined = static-only = exec-only, they're all doing the same thing. If combined < max, there's interference.

**Key Points:**
- Operationalize "orthogonal" using existing error categories from pylint/mypy and test failures
- 2x2 factorial design: baseline, static-only, exec-only, combined
- Falsifiable prediction: combined > max(static-only, exec-only) if orthogonal

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Let me step back and ask: why should the research community care about this specific comparison?

The field has moved toward execution-based feedback (CodeRL, RLPF, StepCoder) because execution is the "gold standard" - it tells you whether code actually works. Static analysis is seen as an approximation. If we just show "static is good enough," that's incremental. If we show "static catches different things," that opens new research directions.

The significance lies in the *practical* implications. If static and execution are orthogonal:
1. **Cost implications**: Static is ~100x cheaper (no sandbox, no execution). Combined could give best results while keeping execution minimal.
2. **Safety implications**: Static analysis doesn't require executing potentially malicious LLM-generated code.
3. **Latency implications**: Static feedback can happen per-token during generation; execution requires complete code.

But here's the question we must answer: what makes this study *methodologically* novel, not just the finding? The "Static Analysis as Feedback Loop" paper (2508.14419) already showed static analysis helps. We need to demonstrate why our controlled comparison reveals something new.

I propose the novelty is: **first systematic decomposition of feedback signal contributions on standard benchmarks**. No one has run the 2x2 factorial on HumanEval+/MBPP+ with pass@k as the primary metric. That's a gap we can fill with existing tools.

**Key Points:**
- Significance: If orthogonal, unlocks cost/safety/latency benefits not available with execution-only
- Methodological novelty: First systematic 2x2 factorial decomposition on HumanEval+/MBPP+
- Impact: Opens new research directions in hybrid feedback systems

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's ground this in what we can actually build and test. I need to assess whether the proposed mechanism is technically sound.

**Mechanism check:** Using Self-Refine as the base framework makes sense. It's designed exactly for this - generate, get feedback, refine. The feedback function is pluggable. We can implement:
- Static feedback: pylint + mypy output parsed into natural language
- Execution feedback: test results from HumanEval+/MBPP+ test suites

**Validity check:** The 2x2 design is clean but requires careful controls:
1. Same base LLM for all conditions (fixed model, fixed temperature)
2. Same number of refinement iterations per condition (or measure pass@k at each iteration)
3. Same prompt format across conditions (only feedback content differs)

**Potential barrier:** One concern - the "combined" condition needs careful design. Do we concatenate static+execution feedback? Interleave them? The Self-Refine paper uses single-source feedback. We'd need to design the combined prompt carefully to avoid confounding.

**Proposed solution:** Run combined as two variants: (1) concatenated feedback, (2) sequential (static first, then execution if static didn't fix it). Report both.

The measurement approach (pass@k) is theoretically valid and well-established. The intervention (different feedback sources) can work in principle. No fundamental barriers here - this is engineering, not physics.

**Key Points:**
- Mechanism sound: Self-Refine is designed for pluggable feedback
- Control requirements: fixed model, fixed iterations, fixed prompts except feedback content
- Combined condition needs two variants: concatenated vs sequential feedback

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Excellent foundation from all perspectives. Let me synthesize and strengthen what's emerging.

The core hypothesis crystallizing is: **Static analysis feedback and execution feedback improve LLM code generation through orthogonal mechanisms, fixing different error classes.**

Building on Prof. Vera's falsification criteria and Prof. Pax's feasibility analysis, I can strengthen this into a testable form:

**Refined Hypothesis (Under-If-Then-Because format):**
Under the condition of iterative code refinement using Self-Refine on HumanEval+/MBPP+, if we provide static-only vs execution-only vs combined feedback, then combined feedback will achieve higher pass@k than either single-source condition, because static analysis catches structural errors (type mismatches, undefined references) while execution catches behavioral errors (wrong logic, edge cases).

**Key Variables:**
- **IV:** Feedback type (none, static-only, exec-only, combined)
- **DV:** pass@k on HumanEval+/MBPP+ (primary), error category distribution (secondary)
- **Controlled:** Base LLM, temperature, iteration count, prompt format

**Predictions:**
- P1: combined pass@k > max(static-only, exec-only) pass@k
- P2: Static-only fixes more syntax/type errors than exec-only
- P3: Exec-only fixes more logic/output errors than static-only

This addresses Dr. Sage's significance concern - we're not just showing "static works" but *why* combining them matters.

**Key Points:**
- Hypothesis: Static and execution are orthogonal, combined > max(individual)
- Clear IV/DV structure with existing benchmarks
- Three testable predictions that decompose the effect

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally's synthesis is solid but I see several gaps we must address before this hypothesis is bulletproof.

**Challenge 1: The "orthogonality" claim is too strong.**
What if static and execution have 30% overlap, 70% unique? Is that "orthogonal enough"? We need a quantitative threshold. Proposal: Orthogonality index = 1 - (overlap_fixes / total_fixes). Specify minimum threshold (e.g., > 0.5).

**Challenge 2: Error categorization without new rubrics.**
Dr. Nova and Prof. Vera mention using pylint/mypy categories + test failure types. But how do we map these to "structural" vs "behavioral" without a new taxonomy? We must operationalize this precisely:
- Structural errors: pylint/mypy warnings (well-defined categories already exist)
- Behavioral errors: test failures after code is syntactically/type-correct

**Challenge 3: What if combined < max due to interference?**
Dr. Sage assumed combined > max means orthogonal. But what if combining feedback confuses the LLM? We need to predict and handle this: if combined < max, that's evidence of *interference*, which is also a finding (just not the one we hypothesized).

**Challenge 4: Base model selection matters.**
Different LLMs may respond differently to feedback types. We should specify the model (e.g., GPT-4, Claude, Code Llama) and acknowledge this as a scope limitation.

**What would convince me:** A clear decision tree:
- combined > max → orthogonal contribution (hypothesis confirmed)
- combined ≈ max → redundant (one subsumes the other)
- combined < max → interference (unexpected, needs explanation)

**Key Points:**
- Need orthogonality threshold (quantitative, not just qualitative)
- Operationalize structural vs behavioral using existing tool outputs
- Plan for all outcomes: orthogonal, redundant, or interference

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's challenges sharpen the hypothesis beautifully. Let me build on the orthogonality quantification idea with a twist.

What if we don't just measure overlap, but measure *information gain*? Here's the insight: each feedback type provides information to the LLM. If static and execution are orthogonal, the combined condition's improvement should be *predictable* from the individual improvements - like adding two independent probability distributions.

Specifically: let's define improvement as Δpass@k relative to baseline. If orthogonal:
- Δ_combined ≈ Δ_static + Δ_exec (additive)

If redundant:
- Δ_combined ≈ max(Δ_static, Δ_exec) (one subsumes the other)

If interference:
- Δ_combined < min(Δ_static, Δ_exec) (they conflict)

This gives us a continuous measure of "orthogonality degree" without needing arbitrary thresholds. And it's testable with existing pass@k metrics.

For the error categorization challenge: Prof. Rex is right that we need to be precise. I propose we use the existing pylint error codes (E=error, W=warning, C=convention, R=refactor) and mypy error codes directly. For behavioral errors, we use test result: PASS, FAIL (wrong output), ERROR (runtime exception). No new taxonomy needed - we're literally reading tool outputs.

**Key Points:**
- Orthogonality test: Δ_combined ≈ Δ_static + Δ_exec (additive model)
- Redundancy test: Δ_combined ≈ max(Δ_static, Δ_exec)
- Use existing pylint/mypy error codes and test result categories directly

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's additive model is elegant but needs careful operationalization. Let me formalize the experimental design.

**Primary Metric:** pass@1 on HumanEval+ and MBPP+ (separate results reported)
**Secondary Metrics:**
- Error reduction rate by category (pylint codes, test outcomes)
- Refinement efficiency (iterations to fix)

**Statistical Test for Orthogonality:**
H0: Δ_combined = max(Δ_static, Δ_exec) (redundant)
H1: Δ_combined > max(Δ_static, Δ_exec) (orthogonal contribution)

One-tailed t-test or bootstrap confidence interval. Effect size (Cohen's d) for practical significance.

**Sample Size Consideration:**
HumanEval+ has 164 problems, MBPP+ has 399. With 4 conditions, we have 164×4 = 656 data points for HumanEval+. This should provide adequate power for detecting meaningful differences (d > 0.3).

**Control Variables (fixed across conditions):**
1. Base LLM: Specify one model (suggest GPT-4 for reproducibility, or open-source like CodeLlama-70B)
2. Temperature: 0.0 for determinism, or fixed seed if sampling
3. Max iterations: 5 (typical in Self-Refine literature)
4. Prompt template: Identical except feedback content

**Key Points:**
- Primary DV: pass@1 on HumanEval+/MBPP+
- Statistical test: H0 (redundant) vs H1 (orthogonal) with one-tailed test
- Fixed controls: model, temperature, iterations, prompt template

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

The experimental design is crystallizing well. Let me verify final technical feasibility.

**Static Analysis Implementation:**
- pylint: Easy to run, structured JSON output, well-documented error codes
- mypy: Type checker, JSON output, catches different errors than pylint
- Integration: Parse JSON output → format as natural language feedback → inject into Self-Refine prompt

**Execution Feedback Implementation:**
- evalplus provides test harness for HumanEval+/MBPP+
- Output: pass/fail per test case, error messages for failures
- Integration: Parse test results → format as feedback → inject into prompt

**Combined Condition Implementation:**
As discussed, two variants:
1. **Concatenated:** "Static analysis found: [pylint/mypy output]. Test results: [pass/fail + errors]"
2. **Sequential:** Run static feedback iterations first, then execution feedback if needed

Both are implementable. I recommend starting with concatenated (simpler) and adding sequential as ablation.

**Compute Estimate:**
- HumanEval+: 164 problems × 4 conditions × 5 iterations = 3,280 LLM calls
- MBPP+: 399 problems × 4 conditions × 5 iterations = 7,980 LLM calls
- Total: ~11,260 LLM calls
- At ~1000 tokens/call, ~11M tokens. Feasible with API access.

**No fundamental barriers.** This is engineering work with known tools.

**Key Points:**
- Static: pylint + mypy with JSON parsing
- Execution: evalplus test harness
- Combined: concatenated (primary) + sequential (ablation)
- ~11K LLM calls total, feasible

---

### Exchange 10

🎯 **Dr. Sage** (Research Impact Evaluator):

Let me assess the significance of what we've designed.

**Contribution to the field:**
1. **First controlled 2×2 study** of feedback types on standard code generation benchmarks. Prior work either used one feedback type or combined without isolating.
2. **Quantitative orthogonality test** - the additive vs max model provides a principled way to measure feedback contribution that others can reuse.
3. **Practical guidance** - results directly inform practitioners: should you run static analysis, execution tests, or both during LLM code generation?

**Positioning relative to prior work:**
- vs "Static Analysis as Feedback Loop" (2508.14419): They show static works; we show *how* it works relative to execution
- vs "Helping LLMs Improve Code Generation" (2412.14841): They combine; we decompose
- vs Self-Refine (2303.17651): We use their framework but with novel factorial design

**Potential impact:**
If orthogonal: Opens hybrid feedback research direction, cost optimization strategies
If redundant: Clarifies that static is sufficient (cost savings)
If interference: Warns against naive combination (important negative result)

All outcomes are publishable. This is a well-designed study regardless of result.

**Key Points:**
- First controlled 2×2 decomposition on HumanEval+/MBPP+
- Reusable orthogonality test framework
- All outcomes (orthogonal/redundant/interference) are publishable findings

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

We're converging on a strong hypothesis. Let me consolidate the refined version.

**FINAL HYPOTHESIS STATEMENT:**

**Title:** Orthogonality of Static Analysis and Execution Feedback in LLM Code Generation

**Core Claim (Under-If-Then-Because):**
Under iterative code refinement using Self-Refine on HumanEval+/MBPP+, if we provide combined static+execution feedback versus single-source feedback, then the combined condition achieves pass@k improvement that exceeds the maximum of individual improvements (Δ_combined > max(Δ_static, Δ_exec)), because static analysis captures structural errors (pylint/mypy detectable) while execution captures behavioral errors (test failures) - orthogonal signal classes.

**Null Hypothesis (H0):**
Δ_combined = max(Δ_static, Δ_exec) (feedback sources are redundant; one subsumes the other)

**Variables:**
- **IV:** Feedback type (4 levels: none, static-only, exec-only, combined)
- **DV_primary:** pass@1 on HumanEval+ and MBPP+ (reported separately)
- **DV_secondary:** Error reduction by category (pylint codes, test outcome types)
- **Controlled:** Base LLM (GPT-4 or CodeLlama-70B), temperature (0.0), max iterations (5), prompt template (fixed)

**Predictions:**
- P1: Δ_combined > max(Δ_static, Δ_exec) with p < 0.05
- P2: Static-only reduces pylint E/W codes more than exec-only
- P3: Exec-only reduces test failures (FAIL/ERROR) more than static-only

**Key Points:**
- Clear Under-If-Then-Because structure
- Quantitative orthogonality test with statistical threshold
- Three falsifiable predictions using existing metrics

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

The hypothesis is nearly bulletproof. A few final stress-tests:

**Remaining concern 1: Model specificity**
We specify GPT-4 or CodeLlama-70B. Results may not generalize. **Mitigation:** Acknowledge as scope limitation. Suggest replication with other models as future work.

**Remaining concern 2: Feedback prompt sensitivity**
How we format static analysis output affects LLM response. **Mitigation:** Use standardized format from Self-Refine paper where possible. Report exact prompts in appendix.

**Remaining concern 3: What counts as "fix"?**
If code changes but still fails the same test, did feedback "work"? **Mitigation:** Define "fix" as: (a) passes at least one additional test, or (b) eliminates at least one pylint error. Track both partial and complete fixes.

**Remaining concern 4: HumanEval+ vs MBPP+ differences**
Results might differ between benchmarks. **Mitigation:** Report separately and analyze if patterns diverge.

I'm satisfied these are addressable scope limitations, not fundamental flaws. The hypothesis is ready for Phase 2B.

**Verdict: STRONG hypothesis with clear predictions, existing metrics, and no new rubrics required.**

**Key Points:**
- Model specificity acknowledged as scope limitation
- Feedback format standardized per Self-Refine
- "Fix" operationalized as incremental improvement
- Benchmark differences reported separately

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The orthogonality framing is novel - no prior work has systematically decomposed static vs execution feedback contributions. The additive improvement model (Δ_combined ≈ Δ_static + Δ_exec) provides a quantitative test that's both novel and reusable for future feedback research.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Clear statistical test (one-tailed t-test for Δ_combined > max) with p < 0.05 threshold. Three distinct predictions (P1-P3) each independently falsifiable. Uses existing metrics (pass@k, pylint codes, test outcomes) with no new rubrics required.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** First controlled 2×2 factorial on HumanEval+/MBPP+ for feedback type comparison. All outcomes (orthogonal, redundant, interference) are publishable findings with practical implications for LLM code generation systems.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Implementation path clear: Self-Refine framework + pylint/mypy + evalplus. ~11K LLM calls feasible. No fundamental barriers - all tools exist and integrate cleanly. Combined condition variants (concatenated + sequential) provide robustness.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on testing whether static analysis and execution feedback provide orthogonal signals for improving LLM code generation. The hypothesis posits that combined feedback will achieve pass@k improvements exceeding the maximum of individual feedback types because static analysis catches structural errors (type mismatches, undefined references) while execution catches behavioral errors (wrong logic, edge cases).

The experimental design uses a 2×2 factorial (static on/off × execution on/off) applied to Self-Refine iterations on HumanEval+ and MBPP+. The primary metric is pass@1, with secondary analysis of error category reduction. Controls include fixed base LLM, temperature, iteration count, and prompt template.

Three predictions: (1) combined improvement exceeds maximum individual improvement, (2) static-only reduces more pylint errors than exec-only, (3) exec-only reduces more test failures than static-only. The additive model (Δ_combined ≈ Δ_static + Δ_exec) quantifies orthogonality degree.

Implementation uses existing tools: pylint and mypy for static analysis, evalplus test harness for execution feedback, Self-Refine framework for the iteration loop. Approximately 11,000 LLM calls required across both benchmarks and all conditions.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Model specificity: Results may not generalize beyond the tested LLM
- Feedback prompt sensitivity: Formatting of static analysis output may affect results
- Benchmark differences: HumanEval+ and MBPP+ patterns may diverge
- **Mitigation Strategy:** Acknowledge model specificity as scope limitation; use standardized Self-Refine prompt formats; report benchmark results separately with divergence analysis; include prompts in appendix for reproducibility

---

