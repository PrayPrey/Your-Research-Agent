# Phase 2A Discussion Log

## Research Gap Briefing

**Gap ID:** gap_1
**Gap Title:** No Controlled Comparison of Feedback Types on Standard Benchmarks
**Priority:** HIGH | **Relevance:** PRIMARY

**Description:** Individual papers demonstrate either execution feedback (CodeRL, Self-Debug) OR AI feedback (Self-Refine, Constitutional AI) approaches, but controlled head-to-head comparisons on same benchmarks with same base models are rare.

**Missing Piece:** A systematic ablation study comparing execution feedback vs AI feedback vs hybrid approaches on HumanEval, MBPP, and SWE-bench using identical experimental conditions.

### Reference Papers (Inferred)
- Self-Debug (Chen et al., 2023): LLM debugs own code using execution feedback
- CodeRL (Le et al., 2022): RL with unit test execution rewards
- Self-Refine (Madaan et al., 2023): LLM self-critique without execution
- Reflexion (Shinn et al., 2023): Verbal self-reflection from execution outcomes

### Feasibility Constraints
- Must use existing benchmarks (HumanEval, MBPP, SWE-bench)
- No new benchmark creation
- No human evaluation required
- Must be testable with existing datasets

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we flip the entire framing here? Everyone's been asking "execution vs AI feedback" as if these are competing paradigms. But what if the real question is about *information density*? 

Execution feedback gives you ground truth but only at the final output — it's a binary signal (works or doesn't) with optional error traces. AI feedback gives you intermediate critique — it can comment on code style, potential bugs, inefficiency — but it might hallucinate. 

Here's my wild idea: what if execution feedback and AI feedback aren't alternatives at all, but operate at *different granularities of the generation process*? Execution feedback tells you WHAT failed. AI feedback hypothesizes WHY it might fail before you even run it.

The unexplored angle: **temporal placement of feedback**. CodeRL applies execution feedback post-generation. Self-Refine applies AI feedback mid-refinement. What if we systematically varied WHEN feedback is applied, not just WHAT type?

This connects to the curriculum learning literature — coarse signals early, fine signals late. Nobody's tested whether execution feedback works better as a "final exam" while AI feedback serves as "tutoring along the way."

**Key Points:**
- Reframe as information density/timing question, not type comparison
- Execution = ground truth at output; AI = hypothetical critique at any stage
- Novel angle: systematic study of feedback timing placement
- Cross-domain connection to curriculum learning

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises an interesting reframe, but let's be precise about what we can actually test. The "temporal placement" angle is appealing but risks confounding too many variables.

Let me propose a cleaner experimental design: **hold everything constant except the feedback source**. Same base model (CodeLlama-7B or StarCoder-7B), same dataset (HumanEval-164 problems), same number of refinement iterations (k=3), same compute budget. The ONLY variable: what generates the feedback signal.

Condition A: Execution feedback (compile + run tests, return error traces)
Condition B: AI feedback (separate critic model, same parameter count, return natural language critique)
Condition C: Random baseline (shuffled feedback from other samples)

The dependent variable is pass@1 after refinement. But here's the critical falsification criterion: **if AI feedback matches or exceeds execution feedback on pass@1, the hypothesis "execution provides unique signal" is falsified.**

What would convince me execution feedback is superior? A statistically significant gap (p<0.05, effect size d>0.3) on at least 2 of 3 benchmarks (HumanEval, MBPP, one subset of SWE-bench).

Dr. Nova's timing question is secondary — first establish WHETHER the feedback types differ, THEN explore when to apply them.

**Key Points:**
- Clean ablation: hold model/dataset/iterations constant, vary only feedback source
- Three conditions: execution, AI critic, random baseline
- Falsification criterion: AI matching execution would disprove execution's unique value
- Effect size threshold: d>0.3 for meaningful difference

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Vera's experimental design is clean, but I must ask: why does this matter for the field?

The significance question isn't "which feedback is better" — that's an engineering optimization. The deeper contribution would be understanding WHY one feedback type might dominate, which would transfer to other alignment domains.

Consider: execution feedback is a special case of *verifiable reward* — the environment provides ground truth. AI feedback is a case of *proxy reward* — a learned model approximates quality. This distinction is foundational to the entire RLHF vs RLAIF debate.

If we find execution feedback significantly outperforms AI feedback for code, the implication is: **verifiable rewards should be preferred wherever available**. This changes how we think about domains with partial verifiability — math proofs, SQL queries, hardware descriptions.

Conversely, if AI feedback matches execution feedback, the implication is: **proxy rewards can substitute for ground truth even when ground truth is available**. This would justify AI feedback in domains where execution is expensive (long-running simulations, hardware-in-the-loop tests).

The research contribution isn't the benchmark number — it's the principle about when verifiable rewards matter.

**Key Points:**
- Frame as verifiable reward (execution) vs proxy reward (AI feedback) study
- Generalizes beyond code to any domain with partial verifiability
- Finding matters for RLHF vs RLAIF debate
- Contribution is the principle, not the benchmark delta

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Hold on — before we commit to this experimental design, I need to flag some feasibility concerns. NOT about cost (that's implementation), but about whether the comparison is even *scientifically valid*.

**Concern 1: Information asymmetry.** Execution feedback includes the actual error message and stack trace. AI feedback... what exactly? If we give the AI critic access to the same code, it's arguably using *less* information than execution feedback. This isn't a fair comparison — it's comparing a signal-rich channel to a signal-poor one.

**Concern 2: Critic model quality.** Prof. Vera says "same parameter count" for the critic. But a 7B code critic trained on what data? If it's trained on code correctness labels, it's indirectly learning from execution. If it's trained on human preferences, it's a different signal entirely. The AI feedback condition isn't one thing — it's a family of methods.

**Proposed fix:** Define AI feedback more precisely. I suggest: "AI feedback = natural language critique from a model that has NEVER seen execution results during training." This makes the comparison clean: learned heuristics vs ground truth.

**Feasibility verdict:** The mechanism is sound IF we operationalize AI feedback carefully. The study can work in principle.

**Key Points:**
- Concern: information asymmetry between feedback types must be controlled
- Concern: AI critic training data determines what signal it provides
- Fix: AI feedback must come from model never trained on execution labels
- Feasibility: Sound if operationalized carefully

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Pax raises valid concerns, and I think we can address them to strengthen the hypothesis.

**Addressing information asymmetry:** Let's equalize information access. Both feedback types receive: (1) the problem description, (2) the generated code, (3) the expected output format. Execution feedback additionally receives runtime signal. AI feedback receives nothing extra — but this IS the point. We're testing whether AI can INFER what execution reveals.

**Addressing critic training:** We can use an off-the-shelf instruction-tuned model (GPT-4, Claude) as the AI critic — models trained on diverse data without explicit execution feedback fine-tuning. This is actually the common deployment scenario: practitioners use general-purpose LLMs as critics.

Here's the refined hypothesis statement:

**Under** code generation with iterative refinement, **if** feedback is provided by execution (compiler + tests) versus AI critique (instruction-tuned LLM), **then** execution feedback will yield higher pass@1 rates, **because** execution provides ground-truth error localization that AI critique must approximate.

**Null hypothesis (H0):** There is no significant difference in pass@1 between execution feedback and AI feedback conditions.

This is testable, falsifiable, and addresses Prof. Pax's concerns.

**Key Points:**
- Information asymmetry is the experimental design, not a confound
- Use off-the-shelf LLMs as AI critics (realistic deployment scenario)
- Refined Under-If-Then-Because statement
- Clear null hypothesis for statistical testing

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally's refinement is good, but I see two remaining weaknesses:

**Weakness 1: Confounded with error parsing.** If execution feedback includes raw error messages, the model must parse compiler output. If AI feedback is natural language, it's already parsed. We might be measuring "error message parsing ability" not "feedback type effectiveness." 

**Fix:** Normalize both to natural language. Execution feedback → have a simple template convert errors to NL ("Line 5: TypeError — expected int, got str"). AI feedback is already NL. Now we compare signal content, not format.

**Weakness 2: Single-model dependency.** Testing on CodeLlama-7B tells us about CodeLlama-7B. For generalization, we need at least 2 base models from different families (e.g., CodeLlama + StarCoder, or open vs proprietary).

**What would convince me:** (1) Effect holds across 2+ model families, (2) Effect holds on 2+ benchmarks, (3) Ablation on feedback granularity (binary vs detailed) to isolate the mechanism.

The hypothesis is almost ready. Add the granularity ablation — comparing "pass/fail only" vs "detailed error trace" execution feedback — and we have a complete study.

**Key Points:**
- Normalize feedback format to natural language (remove parsing confound)
- Test on 2+ model families for generalization
- Add granularity ablation: binary vs detailed execution feedback
- Three conditions become four: Exec-binary, Exec-detailed, AI-critic, Random

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

I love where this has converged! Prof. Rex's granularity ablation actually brings back my original timing intuition, but in a cleaner form.

Here's the final synthesis I see emerging:

**Core claim:** Execution feedback outperforms AI feedback for code generation post-training, primarily because of ground-truth error localization. The advantage scales with feedback granularity (detailed > binary).

**Mechanism:** Execution feedback provides *counterfactual information* — "if you had written X differently, Y would not have failed." AI feedback provides *predictive critique* — "this pattern might cause problems." The counterfactual is more actionable because it's tied to actual failure.

**Testable predictions:**
1. **P1 (Primary):** Exec-detailed > AI-critic > Exec-binary on pass@1 (ordering effect)
2. **P2:** Effect size larger on complex tasks (SWE-bench) vs simple (HumanEval) — complexity amplifies execution advantage
3. **P3:** AI-critic approaches Exec-detailed when critic is same model (self-critique matches self-execution) — tests whether the gap is about model capacity

**What's novel:** First controlled comparison with granularity ablation. Prior work compared methods (CodeRL vs Self-Refine) but not feedback types in isolation.

The hypothesis is ready for Phase 2B verification design.

**Key Points:**
- Core claim: execution > AI, scaling with granularity
- Mechanism: counterfactual (execution) vs predictive (AI) information
- Three predictions with ordering, complexity moderation, self-critique test
- Novelty: first controlled feedback-type comparison with granularity ablation

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** This is the first controlled comparison of feedback types with granularity ablation. The reframe from "method comparison" to "signal comparison" is novel and generalizes to other verifiable-reward domains.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Clear falsification criteria: AI matching execution disproves unique value of ground truth. Statistical thresholds defined (p<0.05, d>0.3). Three predictions all testable with existing benchmarks.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Contribution extends beyond code to the RLHF/RLAIF debate. Findings inform when verifiable rewards matter, applicable to math, SQL, formal methods. High field impact.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All components exist: HumanEval/MBPP benchmarks, open-source base models, execution sandboxes, off-the-shelf LLM critics. No new infrastructure required. Mechanism is scientifically sound.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on a hypothesis comparing execution feedback versus AI feedback for code generation post-training alignment. The core claim is that execution feedback (compiler errors, test failures, runtime exceptions) will outperform AI feedback (LLM-generated critique) on standard benchmarks, with the advantage scaling with feedback granularity. The proposed mechanism is that execution provides counterfactual error localization (ground truth about what failed and why) while AI feedback provides predictive critique that must approximate this signal. 

The experimental design involves four conditions: execution-binary, execution-detailed, AI-critic (off-the-shelf LLM), and random baseline. Testing will use HumanEval and MBPP on two model families (CodeLlama, StarCoder). Three predictions are proposed: (P1) ordering effect where detailed execution outperforms AI which outperforms binary execution; (P2) complexity moderation where the execution advantage is larger on harder tasks; (P3) self-critique matching where AI feedback from the same model approaches execution-detailed performance.

The novelty is being the first controlled feedback-type ablation rather than method comparison. Significance extends to the broader RLHF vs RLAIF debate about when verifiable rewards are essential.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- AI critic quality varies by model — results may not generalize across critic architectures
- Execution sandbox differences (timeout handling, partial credit) could affect reproducibility
- **Mitigation Strategy:** Report critic model identity; use standardized sandbox (E2B or equivalent); publish all execution parameters

---

