# Phase 2A Research Discussion Log

## Briefing

**Gap ID:** gap-1-static-analysis-pass-k
**Gap Title:** Static Analysis Impact on Functional Correctness Unquantified

**Research Question:** Does integrating static analyzer feedback into LLM code generation iterative repair loops improve functional correctness on existing code benchmarks compared to execution-only feedback?

**Context:** Blyth et al. (arXiv:2508.14419) demonstrated quality improvements (security 40%→13%, readability 80%→11%) but measured NO functional correctness metrics. No study measures static analysis impact on HumanEval/MBPP pass@k.

**Key Papers:**
- Static Analysis as a Feedback Loop (arXiv:2508.14419) — Quality only, no pass@k
- Self-Debug — Execution-only baseline
- Self-Refine — Iterative refinement framework

**Implementation Resources:**
- madaan/self-refine (https://github.com/madaan/self-refine)
- FloridSleeves/LLMDebugger
- pylint-dev/pylint

**Benchmarks Available:** HumanEval, MBPP (existing, standard)

**Feasibility Constraints:**
- MUST use existing datasets (HumanEval, MBPP)
- MUST use existing benchmarks (pass@k)
- NO new benchmarks, rubrics, or scoring frameworks
- NO synthetic/generated data
- NO human evaluation

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we're approaching this from the wrong direction entirely? Everyone's been asking "does static analysis help?" — but the real question might be "WHEN does static analysis help?"

Looking at arXiv:2508.14419, they showed dramatic quality improvements but never measured pass@k. That's not an oversight — it might be a signal. What if static analysis and execution feedback are complementary in ways we haven't mapped?

Here's an unconventional angle: what if static analysis catches DIFFERENT failure modes than execution? Execution tells you "this crashes" or "wrong output." Static analysis tells you "this WILL crash under certain inputs" or "this has a type mismatch that happens to work in your test but won't generalize."

Imagine this: a Self-Refine loop where the FIRST iteration uses static analysis (cheap, fast, catches structural issues), and only SUBSEQUENT iterations use execution (expensive, definitive). We'd be filtering out easy-to-catch errors before burning compute on test execution.

Or even wilder — what if static analysis provides signal on problems where execution feedback is MISLEADING? The Patchwork Problem paper (arXiv:2607.08981) showed structural failures evade verification. Static analysis might catch exactly those cases.

**Key Points:**
- Static and execution feedback may catch non-overlapping error classes
- Ordering matters: static-first could be a cheap filter before expensive execution
- Static analysis might specifically help where execution feedback misleads (patchwork failures)

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises an interesting hypothesis, but let's make it testable. The claim "static analysis catches different failure modes" is vague. What would disprove it?

I propose a concrete experimental design:

**Hypothesis (testable form):** Static analysis feedback, when added to an execution-only repair loop, will increase pass@k on HumanEval/MBPP by identifying errors that execution feedback alone misses.

**Falsification criteria:** If pass@k(static+execution) ≤ pass@k(execution-only) across all k values and both benchmarks, the hypothesis is false.

**Confounds to control:**
1. Model variation — use same base LLM across conditions
2. Iteration budget — fix total repair iterations (e.g., 5 rounds)
3. Prompt format — control for how feedback is presented
4. Static analyzer choice — standardize on pylint/mypy

**What I need to see:**
- Pre-registered success criterion (e.g., +2% pass@1 improvement)
- Error categorization: which errors does static analysis catch that execution misses?
- Ablation: static-only vs execution-only vs combined

The Self-Debug paper provides our execution-only baseline. We need to replicate their setup exactly, then add static analysis as our intervention.

**Key Points:**
- Falsifiable hypothesis: static+execution > execution-only on pass@k
- Controlled variables: model, iterations, prompt format, analyzer
- Ablation design: isolate contribution of each signal type

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Let me assess whether this contribution advances the field or is merely incremental.

**The question we must ask:** Why hasn't anyone measured this already? The gap between Blyth et al.'s quality metrics and functional correctness is conspicuous. Either (a) researchers assumed the relationship was obvious, or (b) there's a reason to believe they're orthogonal.

**Why this matters (if validated):**
1. **Practical impact:** Every production code-gen system uses iterative repair. If static analysis is a free/cheap addition that improves pass rates, industry will adopt immediately.
2. **Scientific contribution:** Establishing the causal mechanism — WHICH error types benefit from static vs execution feedback — would open new research directions in feedback signal design.
3. **Theoretical novelty:** Currently, self-debugging treats execution feedback as ground truth. Demonstrating that static analysis provides non-redundant signal challenges this assumption.

**What would make this NOT significant:**
- If the improvement is <1% — too small for practical impact
- If the improvement is limited to a narrow error class with no generalizable insight
- If the added complexity (running static analyzers) outweighs the pass@k gain

**My assessment:** This fills a genuine gap. Blyth et al. opened a door; measuring pass@k walks through it. The contribution is significant IF we get a positive signal AND can explain WHY (mechanism).

**Key Points:**
- Gap is genuine — no one has measured static analysis → pass@k relationship
- Impact is practical (industry adoption) + scientific (feedback signal theory)
- Significance depends on effect size AND mechanistic explanation

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's ground this in reality. I see potential fundamental barriers that need addressing.

**Technical feasibility assessment:**

1. **Static analyzer signal quality:** Pylint/mypy produce warnings, not fixes. The question is whether LLMs can interpret these warnings and translate them into correct repairs. This is MEASURABLE — we can study warning→fix fidelity.

2. **False positive problem:** Static analyzers are noisy. Pylint generates many warnings that don't affect correctness. Feeding ALL warnings to the LLM might dilute the signal. This is a REAL barrier but not fundamental — we can filter by warning severity or category.

3. **Complementarity assumption:** Dr. Nova assumes static and execution catch different errors. This is empirically testable: categorize HumanEval failures by whether they're detectable by static analysis vs only by execution.

**What worries me:**
- If most HumanEval failures are LOGIC errors (wrong algorithm, off-by-one), static analysis won't help — these pass type checks and lint.
- If most failures are TYPE/SYNTAX errors, execution already catches them — static adds redundancy, not value.

**What would convince me:**
- Evidence that a meaningful fraction of HumanEval failures involve issues static analyzers can detect (undefined variables, type mismatches, unused code paths)
- A pilot study: run pylint on 100 failing HumanEval solutions, count how many have actionable warnings

**Key Points:**
- LLM's ability to interpret static warnings into fixes is testable
- False positives need filtering — warning severity/category selection
- Core assumption needs validation: do HumanEval failures have static-detectable issues?

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Let me synthesize the concerns and strengthen the hypothesis.

**Addressing Prof. Pax's concern about error types:** This is actually a FEATURE of our design, not a bug. By categorizing HumanEval failures into static-detectable vs execution-only, we get:
1. A testable sub-hypothesis
2. A clear scope boundary for our main claim
3. Insight into WHEN to deploy static analysis

**Refined hypothesis:** "In LLM iterative code repair, adding static analyzer feedback improves pass@k SPECIFICALLY for error types where static analyzers produce actionable warnings — including undefined variables, type mismatches, and unreachable code. For pure logic errors, static analysis provides no benefit."

**Addressing the false positive problem:** We can use a severity filter. Pylint has error/warning/convention categories. Use ONLY errors and warnings, skip conventions. Or use pyright/mypy for type errors only — these are high-precision signals.

**Building on Prof. Vera's design:** The ablation structure is strong. Let me add a prediction:

**Prediction 1 (primary):** Static+execution > execution-only by ≥2% on pass@1 for HumanEval
**Prediction 2:** The improvement will be concentrated in problems where initial solution has static analyzer errors (not just warnings)
**Prediction 3:** For problems with only logic errors (no static warnings), conditions will perform identically

This makes our hypothesis falsifiable AND provides mechanistic insight.

**Key Points:**
- Error categorization is a strength — it scopes our claim precisely
- Severity filtering addresses false positive concern
- Three testable predictions with different granularities

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down. Let me stress-test these claims.

**Challenge 1: The 2% threshold is arbitrary.** Why 2%? HumanEval baseline pass@1 varies wildly by model (GPT-4 is ~67%, CodeLlama is ~30%). A 2% absolute improvement means different things. Use RELATIVE improvement or justify the threshold.

**Challenge 2: Execution feedback already catches most static issues.** If a variable is undefined, execution will crash. If there's a type mismatch, the test might fail. Static analysis might only catch issues BEFORE execution does — a speed advantage, not an accuracy advantage. Is your hypothesis about CORRECTNESS or EFFICIENCY?

**Challenge 3: The Self-Debug baseline may already implicitly use static-like reasoning.** When execution fails and the LLM sees the traceback, it's essentially getting a form of "static analysis" — the traceback points to the problematic line. You need to show static analysis provides ADDITIONAL signal beyond what tracebacks contain.

**What would convince me:**
- A clear case study: a HumanEval problem where execution feedback MISLEADS (test passes but code is wrong for edge cases) and static analysis catches it
- Quantification of non-overlap: what % of static warnings point to issues NOT evident in execution tracebacks?
- Evidence that the LLM can USE static warnings — maybe they just add noise

**Key Points:**
- Threshold justification needed — use relative improvement
- Clarify: is the gain in accuracy or efficiency (or both)?
- Demonstrate non-redundancy with execution tracebacks

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's challenge about redundancy is sharp. Let me think about this differently.

What if the VALUE of static analysis isn't in catching errors execution misses — but in catching them EARLIER and MORE SPECIFICALLY?

Consider: when execution fails, the traceback says "IndexError at line 15." The LLM must INFER why. Static analysis might say "array index could be negative at line 15" — same error, but with the MECHANISM explained.

This suggests a refined hypothesis: **Static analysis improves repair EFFICIENCY by providing MECHANISTIC feedback, not just failure location.**

But there's an even more interesting angle from the Patchwork Problem paper: some solutions PASS tests but are structurally wrong. They work on the test cases but fail on edge cases. Execution feedback says "great, all tests pass!" Static analysis might still flag: "unused branch," "unreachable code," "variable shadowing."

**The real novelty:** Static analysis provides signal ON PASSING SOLUTIONS. Execution feedback stops contributing once tests pass. Static analysis can still improve code that technically works.

**Key Points:**
- Static analysis provides mechanistic feedback, not just failure location
- Critical insight: static analysis contributes EVEN WHEN TESTS PASS
- Patchwork problem shows passing tests don't guarantee correctness

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's insight about passing solutions is testable. Let me formalize it.

**New prediction (P4):** Among solutions that pass ALL test cases, those with static analysis warnings will have LOWER generalization accuracy on held-out tests than those without warnings.

**Experimental design modification:**
1. For each HumanEval problem, generate N solutions per condition
2. Filter to solutions that pass all provided tests
3. Run static analysis on passing solutions
4. If possible, evaluate on extended test cases (some HumanEval problems have EvalPlus extensions)

This tests whether static analysis identifies "brittle" passing solutions — exactly the patchwork problem.

**Clarifying the main hypothesis:** We now have two claims:
- **H1 (primary):** Static+execution feedback improves pass@k vs execution-only
- **H2 (secondary):** Static analysis identifies structurally unsound solutions that pass tests

H1 is measurable on standard HumanEval. H2 requires EvalPlus or similar extended test suites.

For this study, I recommend focusing on H1 with pass@k, noting H2 as future work unless we have easy access to EvalPlus.

**Key Points:**
- P4: Static warnings on passing solutions predict lower generalization
- Two-hypothesis structure: H1 (pass@k) primary, H2 (generalization) secondary
- H1 is immediately testable on existing benchmarks

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

This is sharpening up. Let me assess feasibility of the refined design.

**H1 feasibility (pass@k improvement):**
- ✅ HumanEval, MBPP: publicly available, standard
- ✅ Self-Debug/Self-Refine: replicable baselines
- ✅ Pylint/mypy: off-the-shelf static analyzers
- ✅ LLM: can use any code-capable model (GPT-4, CodeLlama, etc.)
- ✅ Compute: iterative repair is expensive but bounded (5 iterations × N problems × M samples)

**Potential barriers resolved:**
- False positives: filter by severity (errors only, or errors+warnings)
- Prompt format: standardize as "[static warnings]\n[code]\n[execution result]"
- Iteration budget: 5 rounds matches Self-Debug

**Remaining concern:** We need to verify that static analyzers produce meaningful output on LLM-generated code. A quick sanity check:
- Generate 50 HumanEval solutions with a baseline LLM
- Run pylint on each
- Count: how many have warnings/errors? What categories?

If most solutions have zero warnings, the intervention has no signal. If most have many warnings, we have work to do on filtering.

**My verdict:** Technically feasible. Recommend a pilot study before full experiment.

**Key Points:**
- All components available: benchmarks, baselines, analyzers, LLMs
- Pilot study recommended: check static analyzer output on LLM code
- Filtering strategy: errors only, then errors+warnings if needed

---

### Exchange 10

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Let me consolidate our refined hypothesis.

**Final Hypothesis Statement:**
Under the condition of iterative LLM code repair on HumanEval/MBPP, if static analyzer feedback (pylint/mypy) is integrated alongside execution feedback, then pass@k will improve compared to execution-only feedback, because static analysis provides mechanistic error explanations and catches issues before execution, reducing repair iterations needed.

**Null Hypothesis (H0):**
There is no significant difference in pass@k between static+execution feedback and execution-only feedback conditions.

**Variables:**
- **IV:** Feedback type (execution-only vs static+execution)
- **DV:** pass@k (primary: pass@1, secondary: pass@5, pass@10)
- **Controlled:** Model, iteration budget (5), prompt format, static analyzer (pylint)

**Testable Predictions:**
- **P1 (primary):** pass@1(static+exec) > pass@1(exec-only) by ≥2% absolute
- **P2:** Improvement concentrated in problems with static-detectable errors
- **P3:** For pure logic errors, no difference between conditions

**Experimental Setup:**
- Dataset: HumanEval (164 problems), MBPP (974 problems)
- Baseline: Self-Debug style execution-only loop
- Intervention: Add pylint warnings to repair prompt
- Model: GPT-4 or CodeLlama-34B

**Key Points:**
- Under-If-Then-Because structure complete
- Three testable predictions at different granularities
- Clear experimental setup using existing resources

---

### Exchange 11

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Before we converge, one final stress test.

**Remaining concern:** The 2% absolute threshold. Let me sharpen this.

HumanEval pass@1 with GPT-4 is roughly 67%. A 2% absolute improvement (to 69%) is a 3% relative improvement. For weaker models, 2% absolute on a 30% baseline is a 7% relative improvement. 

**Recommendation:** Use BOTH absolute and relative thresholds:
- Absolute: ≥2% improvement
- Relative: ≥5% improvement

If EITHER is met, we have practical significance.

**One more falsifier:** If static analysis DECREASES pass@k (due to noise/distraction), that's strong negative evidence. Include a check that static+exec ≥ exec-only (non-inferiority).

**Final concern addressed:** Prof. Pax's pilot study handles my worry about signal quality. If the pilot shows most LLM solutions have no static warnings, we pivot to a different hypothesis.

I'm satisfied with the hypothesis structure. The predictions are falsifiable, the experiment is feasible, and the contribution is clear.

**Key Points:**
- Dual threshold: ≥2% absolute OR ≥5% relative
- Non-inferiority check: ensure static doesn't hurt
- Pilot study addresses signal quality concern

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis addresses a genuine gap — no one has measured static analysis → pass@k. The insight about static analysis providing value even on passing solutions (patchwork problem) is novel. The mechanism distinction (static provides "why" not just "where") adds theoretical depth.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Three testable predictions with clear success/failure criteria. Dual thresholds (absolute + relative) provide robustness. The ablation design (static-only vs exec-only vs combined) isolates contributions. Falsification criteria are explicit.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Fills a conspicuous gap in the literature. Practical impact is immediate — every code-gen system could adopt if positive. Scientific contribution lies in mechanistic understanding of feedback signals. The effect size threshold (2% absolute) is reasonable for practical significance.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All components exist and are accessible. HumanEval/MBPP are standard benchmarks. Self-Debug provides replicable baseline. Static analyzers (pylint, mypy) are off-the-shelf. Pilot study addresses signal quality concern. No fundamental barriers.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion has converged on a clear, testable hypothesis. We propose that integrating static analyzer feedback (pylint/mypy) into LLM iterative code repair loops will improve functional correctness (pass@k) on HumanEval and MBPP benchmarks compared to execution-only feedback loops.

The core mechanism is that static analysis provides MECHANISTIC error explanations (e.g., "variable may be undefined") rather than just failure locations (e.g., "NameError at line 5"), enabling more targeted repairs. Additionally, static analysis catches issues BEFORE execution, potentially reducing repair iterations.

We predict: (P1) pass@1 improvement of ≥2% absolute or ≥5% relative; (P2) improvement concentrated in problems with static-detectable errors; (P3) no improvement for pure logic errors without static warnings.

The experiment uses Self-Debug as baseline, adds pylint warnings to the repair prompt, and measures pass@1/5/10 on HumanEval (164 problems) with a recommended pilot study on 50 problems first.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Signal quality unknown until pilot — must verify static analyzers produce actionable output on LLM code
- Dual threshold prevents arbitrary effect size claims
- **Mitigation Strategy:** Run pilot study (50 HumanEval problems) before full experiment. If <20% of solutions have static warnings, pivot to alternative hypothesis.
