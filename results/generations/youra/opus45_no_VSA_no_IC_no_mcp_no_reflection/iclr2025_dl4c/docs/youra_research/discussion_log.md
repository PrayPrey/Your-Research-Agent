# Phase 2A Discussion Log

**Gap ID:** gap-1
**Gap Title:** No Controlled Comparison of Feedback Granularities
**Research Question:** What is the relative effectiveness of different execution feedback granularities (binary pass/fail vs. detailed error traces vs. test coverage signals) for improving code LLM performance through RLEF?

---

## Briefing Context

### Selected Research Gap

**Gap 1: No Controlled Comparison of Feedback Granularities**

- **Relevance:** PRIMARY - Directly blocks answering research question
- **Current State:** CodeRL uses binary, RLTF uses multi-granularity, Self-Repair uses error traces. No head-to-head comparison under controlled conditions.
- **Missing Piece:** Controlled ablation study comparing {binary, error_trace, coverage} on same infrastructure.
- **Impact:** High

### Reference Papers

| Paper | Year | arXiv | Key Insight |
|-------|------|-------|-------------|
| CodeRL | 2022 | 2207.01780 | Foundational RLEF with binary reward |
| RLTF | 2023 | 2307.04349 | Multi-granularity feedback comparison |
| PPOCoder | 2023 | 2306.05826 | PPO-based execution feedback |
| Self-Repair | 2023 | 2306.09896 | Error trace for iterative debugging |
| Let's Verify Step by Step | 2023 | 2305.20050 | Process reward models |

### Preliminary Hypothesis Directions (from Phase 1)

- H1: Fine-grained > binary under matched compute
- H2: Coverage augmentation improves efficiency
- H3: Process supervision transfers to code

### Feasibility Constraints (Pipeline-Enforced)

- MUST use existing real datasets and existing benchmarks
- NO new benchmarks, rubrics, or scoring frameworks
- NO synthetic/generated data that does not yet exist
- NO human evaluation or annotation

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we're thinking about feedback granularity all wrong? The field has been treating this as a simple spectrum—binary at one end, detailed traces at the other—but I see an unexplored dimension here that could reshape the entire research direction.

Looking at CodeRL's binary approach and RLTF's multi-granularity feedback, everyone's focused on *what information* to provide. But what about *when* to provide it? The process reward model work from "Let's Verify Step by Step" hints at something profound: intermediate signals might matter more than final verdicts. What if the real innovation isn't choosing between binary and detailed feedback, but rather designing a *temporal curriculum* of feedback granularity?

Here's my wild idea: what if coarse binary feedback is optimal during early training when the model is learning basic structure, but fine-grained error traces become essential only after the model achieves baseline competence? This would explain why both CodeRL and RLTF work—they might be optimal for different learning phases!

Another angle: the Self-Repair work shows error traces help debugging, but requires the model to already generate near-correct code. This suggests feedback granularity interacts with model capability level. A coverage-based signal could serve as a *bridge*—providing more signal than binary but without requiring the parsing complexity of full error traces.

**Key Points:**
- Temporal curriculum of feedback granularity unexplored
- Feedback effectiveness may depend on model capability phase
- Coverage signals as a middle ground between binary and traces

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises interesting speculation, but let me ground this in testable science. The fundamental methodological gap in existing work is clear: no controlled ablation exists where feedback granularity is the *only* independent variable.

CodeRL, RLTF, and PPOCoder each use different base models, training procedures, and reward architectures. Attributing their performance differences to feedback granularity alone commits a classic confounding error. For any hypothesis about feedback effects to be scientifically valid, we need:

1. **Fixed infrastructure:** Same base model, same RL algorithm, same dataset, same compute budget
2. **Isolated intervention:** Only the reward signal structure changes
3. **Clear success criteria:** Not just pass@k, but learning efficiency curves and error type distribution

The testable prediction I'd propose: Under matched conditions, feedback type F produces statistically significant improvement in pass@k compared to feedback type B, with effect size > 0.2 and p < 0.05. This is falsifiable—if we see no significant difference, we've learned something important about whether granularity matters at all.

For Dr. Nova's temporal curriculum idea to be testable, we'd need to measure not just final performance but *learning trajectory*. That means evaluating checkpoints throughout training, which adds complexity but remains feasible with standard benchmarks like HumanEval and MBPP.

**Key Points:**
- Current evidence is confounded—no controlled comparison exists
- Falsifiable prediction: Effect size > 0.2, p < 0.05 under matched conditions
- Temporal hypotheses require checkpoint evaluation throughout training

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: why does this matter beyond academic interest? Let me position this research gap within the broader trajectory of code LLM development.

The field is approaching a critical junction. OpenAI's Codex, GitHub Copilot, and various code LLMs have demonstrated that scaling helps, but the next performance frontier requires better training signals. If we establish that fine-grained feedback significantly outperforms binary—or, equally important, if we establish that it doesn't—this shapes billions of dollars in training infrastructure decisions.

The genuine contribution here isn't just running an ablation study. It's establishing *when and why* different feedback types matter. Consider:

- If binary suffices, the field can focus compute on scale rather than feedback infrastructure
- If error traces help, we need investment in robust execution environments
- If coverage matters, we open a new research direction connecting fuzzing and LLM training

What excites me most is the potential for this to open new research questions. The process supervision literature from math reasoning hasn't been connected to code execution feedback. Establishing this bridge could spawn an entire research program on dense reward signals for code.

For impact, we need more than pass@k numbers. We need analysis of *which error types* each feedback granularity helps with. That's the insight practitioners will use to make deployment decisions.

**Key Points:**
- Research gap has major practical implications for training infrastructure
- Contribution must include *when and why*, not just *whether*
- Error type analysis needed for practitioner relevance

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic about what's technically achievable here. The good news: this hypothesis is fundamentally sound and can work in principle.

Existing infrastructure makes this feasible. EvalPlus provides robust execution harnesses. HumanEval and MBPP are standard benchmarks with existing test suites. TRL library supports PPO training. The key technical challenge isn't infrastructure—it's *defining* the reward signals precisely.

Here's what's technically valid:
- **Binary:** Pass = 1, Fail = 0. Clear and unambiguous.
- **Error trace:** Parse execution output for error type, line number, message. But parsing is noisy—different Python versions format differently.
- **Coverage:** Use coverage.py to measure branch/line coverage. Technically sound, but coverage percentage isn't obviously a good reward signal. A program that covers 80% of tests but fails all of them shouldn't get positive reward.

The fundamental barrier I see: how do we make coverage a *reward* rather than just a metric? One approach: reward = pass_rate + α × coverage_delta, where coverage_delta measures how many new branches the generated code covers compared to a baseline. This is scientifically sound but adds a hyperparameter.

For error traces, the question is: can we reliably extract signal? I propose using a simple taxonomy: syntax_error, runtime_error, assertion_error, timeout. This is parsable, stable across environments, and provides 4-level granularity without requiring complex NLP on error messages.

**Key Points:**
- Infrastructure exists: EvalPlus, TRL, standard benchmarks
- Coverage as reward needs careful design (coverage_delta approach)
- Error traces feasible with simple 4-level taxonomy

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Let me synthesize what's emerging and strengthen our hypothesis. We have strong agreement on the gap and infrastructure, with productive tension on reward design. Here's how I'd crystallize this:

**Core Hypothesis:** Under controlled conditions (same base model, RL algorithm, and compute budget), fine-grained execution feedback produces measurably better code generation performance than binary feedback, because it provides denser learning signal that guides credit assignment to specific error-inducing patterns.

The evidence supporting this causal mechanism:
1. CodeRL's binary reward struggles with partial correctness—a program failing 1 test gets the same signal as one failing all tests
2. RLTF showed promise with multi-granularity but lacked controlled comparison
3. Process reward models in math show dense signals help—and code execution is inherently process-observable

To address Prof. Vera's rigor concerns, I propose three concrete feedback conditions:

1. **BINARY:** reward = 1 if all tests pass, 0 otherwise
2. **ERROR-TYPE:** reward = 0.25 × syntax_score + 0.25 × runtime_score + 0.5 × test_pass_rate (weighted by how close to correct)
3. **COVERAGE:** reward = test_pass_rate + 0.2 × branch_coverage_fraction

This makes the intervention clean and measurable. We use the same PPO algorithm, same CodeLlama-7B base, same HumanEval + MBPP datasets. The only variable is the reward function.

For Prof. Pax's coverage concern: we tie coverage to passing tests, so high coverage on failing tests doesn't help. This is scientifically sound.

**Key Points:**
- Core hypothesis: Fine-grained > binary due to denser credit assignment
- Three concrete feedback conditions with specific formulas
- Controlled setup: same model, algorithm, datasets

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down. Dr. Ally's formulation is cleaner than before, but I see three fundamental issues:

**1. Conflating granularity with reward magnitude.** The ERROR-TYPE formulation gives intermediate rewards (0-1 range with partial credit), while BINARY gives only 0 or 1. You're not just testing feedback *type*—you're testing reward *density*. A fair comparison needs BINARY to also get partial signals, e.g., via test pass rate.

**2. Coverage reward assumes coverage correlates with correctness.** But coverage.py measures which lines *execute*, not which tests *pass*. A program could have 100% coverage and fail all assertions. The 0.2 weight seems arbitrary. Why not 0.1 or 0.5? This adds a confound.

**3. Effect size assumptions.** Prof. Vera proposed effect size > 0.2, but is this realistic? RLTF showed ~2-3% improvement on pass@k. That's practically meaningful but statistically small. We need power analysis: how many training runs are required to detect this effect reliably?

What would convince me:

- Separate "partial credit" from "feedback type." Test binary-sparse vs binary-dense vs typed-dense.
- Justify coverage weight empirically or remove coverage condition until we understand error-type effects.
- Commit to N training runs with stated statistical power.

The hypothesis is salvageable but needs tightening. Show me the study design survives these challenges.

**Key Points:**
- Current design conflates granularity with reward density
- Coverage weight (0.2) is arbitrary—needs justification or removal
- Statistical power analysis needed for effect size detection

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's challenges actually point toward something more interesting! What if the conflation of granularity and density is the insight, not a confound?

Here's my reframe: the real question isn't "binary vs. fine-grained" but "how much information per gradient update?" This reconceptualizes feedback granularity as *information bandwidth* in the reward channel. Binary gives 1 bit per episode. Error-type gives ~2 bits (4 categories). Coverage gives continuous signal.

This opens a cleaner experimental design:

**Condition 1 - LOW BANDWIDTH:** binary pass/fail (1 bit)
**Condition 2 - MEDIUM BANDWIDTH:** test_pass_rate (continuous, but single scalar)
**Condition 3 - HIGH BANDWIDTH:** error_type + test_pass_rate (categorical + continuous)

Now we're testing information theory principles applied to RL for code. The prediction: medium and high bandwidth should converge faster (fewer gradient updates to reach threshold pass@k), but final performance may plateau similarly. This is testable via learning curves.

The coverage condition can be a separate ablation: does adding structural information (what code executed) help beyond execution outcome information (what tests passed)? This cleanly separates the research questions.

**Key Points:**
- Reconceptualize as information bandwidth, not just granularity
- Three conditions: low (binary), medium (pass_rate), high (error_type + pass_rate)
- Coverage as separate ablation on structural vs outcome information

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's information bandwidth framing resolves Prof. Rex's density confound elegantly. Let me formalize the experimental design with proper controls:

**Independent Variable:** Reward information bandwidth
- LOW: reward ∈ {0, 1} (binary)
- MEDIUM: reward = test_pass_rate ∈ [0, 1]
- HIGH: reward = f(error_type, test_pass_rate) ∈ [0, 1]

**Dependent Variables:**
- Primary: pass@1, pass@10 on HumanEval (standard metric)
- Secondary: samples_to_threshold (learning efficiency)
- Tertiary: error_type_distribution (diagnostic)

**Controls:**
- Base model: CodeLlama-7B-Instruct (open, reproducible)
- RL algorithm: PPO (TRL implementation)
- Training data: MBPP training set
- Evaluation: HumanEval (held out)
- Compute: 3 epochs, same batch size, same learning rate

**Statistical Design:**
- N = 5 seeds per condition (15 total runs)
- Primary test: one-way ANOVA on pass@1
- Post-hoc: Tukey HSD for pairwise comparisons
- Power: With σ ≈ 0.03 (estimated from prior work), N=5 achieves 80% power for effect size d = 0.8

**Falsification:**
- If LOW ≈ MEDIUM ≈ HIGH: bandwidth doesn't matter
- If only HIGH > LOW but MEDIUM ≈ LOW: categorical signal matters, not continuity
- If MEDIUM ≈ HIGH > LOW: continuous reward suffices, error parsing unnecessary

This design yields interpretable results regardless of outcome.

**Key Points:**
- Three conditions with clear operationalization
- N = 5 seeds per condition, ANOVA + Tukey HSD
- Multiple falsification paths depending on results

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

The experimental design is now technically sound. Let me verify implementation feasibility:

**Infrastructure check:**
- CodeLlama-7B fits on single A100 (40GB) ✓
- TRL PPO with batch size 8 is stable ✓
- HumanEval has 164 problems, MBPP has 500+ for training ✓
- coverage.py integration straightforward ✓

**Reward function implementation:**
- LOW: `reward = 1.0 if all_tests_pass else 0.0`
- MEDIUM: `reward = num_passed / num_total`
- HIGH: `reward = 0.5 * pass_rate + 0.5 * error_score` where error_score = {syntax: 0.0, runtime: 0.25, assertion: 0.75, clean: 1.0}

Wait—the HIGH condition's error_score weighting needs justification. Why 0.25/0.75? Here's a principled approach: order by "distance to correct."
- Syntax error: code doesn't run → 0.0
- Runtime error: runs but crashes → 0.33
- Assertion error: runs, outputs wrong answer → 0.67
- All pass: correct → 1.0

This creates equal intervals on a 0-1 scale based on execution progress. Scientifically motivated, not arbitrary.

**Computational estimate:**
- 3 epochs × 500 MBPP problems × 5 seeds × 3 conditions = 45 training runs
- Each run: ~4 hours on A100
- Total: ~180 GPU-hours (feasible for single-lab study)

**Key Points:**
- Infrastructure verified: single A100 sufficient
- Error_score justified by distance-to-correct principle
- ~180 GPU-hours total, feasible for single lab

---

### Exchange 10

🎯 **Dr. Sage** (Research Impact Evaluator):

NOW we're onto something with genuine contribution potential. Let me articulate why this matters beyond the immediate results.

**Contribution 1: First Controlled Bandwidth Study**
The field lacks any controlled comparison. Even null results (bandwidth doesn't matter) would be highly citable—it would tell practitioners to invest in scale over feedback infrastructure.

**Contribution 2: Actionable Design Principle**
The "distance-to-correct" scoring principle Prof. Pax articulated is itself a contribution. It provides a systematic framework for designing reward signals beyond code—applicable to any domain with staged error types.

**Contribution 3: Bridge to Process Supervision**
By framing this as information bandwidth, we connect to the "Let's Verify Step by Step" literature on process rewards. Code execution provides *free* process supervision (each test is a step). This opens research on whether explicit process rewards (like in math) are necessary, or whether execution naturally provides them.

**New Research Questions Opened:**
1. Does error_type information help more for certain problem categories (algorithms vs. string manipulation)?
2. Can we design curriculum learning from LOW → HIGH bandwidth during training?
3. Does bandwidth interact with model scale?

For maximum impact, the paper should include not just aggregate pass@k but breakdown by problem category and learning efficiency curves. Practitioners need to know: "Fine-grained feedback helps most for X-type problems."

**Key Points:**
- First controlled study is contribution regardless of results
- Distance-to-correct principle is generalizable
- Must include problem category breakdown for practitioner impact

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

We've reached a refined hypothesis that addresses all major concerns. Let me synthesize the final formulation:

**Core Hypothesis (Refined):**
Under controlled RL training conditions, higher reward information bandwidth produces faster convergence to target code generation performance (measured by samples-to-threshold), because denser signals enable more precise credit assignment to error-causing patterns.

**Under-If-Then-Because Structure:**
- **Under:** PPO training of CodeLlama-7B on MBPP with fixed compute budget
- **If:** Reward function provides higher information bandwidth (continuous + categorical vs. binary)
- **Then:** Model reaches pass@1 > 0.3 in fewer training samples
- **Because:** Denser feedback enables gradient updates to more precisely target error-inducing code patterns

**Variables:**
- IV: Reward bandwidth (LOW/MEDIUM/HIGH as operationalized)
- DV (Primary): samples_to_threshold (pass@1 > 0.3 on HumanEval)
- DV (Secondary): final pass@1, pass@10
- Controlled: base model, algorithm, compute, dataset, hyperparameters

**Predictions:**
1. P1 (Primary): HIGH condition reaches threshold in fewer samples than LOW (stat sig at p < 0.05)
2. P2: MEDIUM > LOW in convergence speed (tests whether continuity alone helps)
3. P3: Error-type distribution differs between conditions (HIGH shows fewer syntax errors by epoch 3)

**Null Hypothesis:**
There is no significant difference in samples-to-threshold between reward bandwidth conditions.

**Key Points:**
- Refined hypothesis with Under-If-Then-Because structure
- Primary DV shifted to samples-to-threshold (learning efficiency)
- Three falsifiable predictions

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

This formulation is substantially stronger. My remaining concerns are addressable:

**Concern 1: Threshold selection.** Pass@1 > 0.3 is reasonable (CodeLlama-7B baseline is ~0.25 on HumanEval), but we should also report pass@1 > 0.35 as sensitivity check.

**Concern 2: Epoch vs. samples.** "Samples-to-threshold" is cleaner than epochs since batch sizes might vary. We should measure in actual forward passes.

**Concern 3: Error score weighting.** The 0.5/0.5 split between pass_rate and error_score in HIGH condition is still a design choice. Should be ablated or justified. Alternative: weighted average learned during training.

**Mitigation proposals:**
- Report both 0.3 and 0.35 thresholds
- Measure samples as number of generated solutions
- Keep 0.5/0.5 split, note as limitation, suggest future work on learned weighting

**What would fully convince me:**
Pre-registration of the study design (even informally in appendix) showing these decisions were made before seeing results. This prevents p-hacking concerns.

With these mitigations documented, I'm satisfied this is a rigorous, falsifiable study. The hypothesis will produce interpretable results regardless of outcome.

**Key Points:**
- Report multiple thresholds as sensitivity check
- Measure samples as generated solutions, not epochs
- Document 0.5/0.5 as pre-registered, acknowledge as limitation

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The information bandwidth framing transforms a straightforward ablation into a conceptually novel contribution. Connecting to process supervision literature creates genuine theoretical innovation beyond empirical comparison.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is fully operationalized with clear IV/DV, statistical design (N=5 × 3 conditions, ANOVA), and multiple falsification paths. The design yields interpretable results regardless of outcome.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** First controlled study in this space guarantees citable contribution. The distance-to-correct principle and bandwidth framing have broad applicability beyond code generation.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All components are technically sound. ~180 GPU-hours is feasible for single-lab study. Infrastructure exists and is validated.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The consensus hypothesis is: Higher reward information bandwidth accelerates code LLM learning under RLEF because denser feedback enables more precise credit assignment to error-causing code patterns.

We operationalize this through three conditions—LOW (binary), MEDIUM (continuous pass rate), HIGH (error-type + pass rate)—tested on CodeLlama-7B trained with PPO on MBPP and evaluated on HumanEval. The primary metric is samples-to-threshold (pass@1 > 0.3), with final pass@k as secondary metrics.

Key predictions: (1) HIGH converges faster than LOW, (2) MEDIUM converges faster than LOW, (3) HIGH shows different error-type distribution than LOW. The distance-to-correct principle provides principled error scoring: syntax=0.0, runtime=0.33, assertion=0.67, pass=1.0.

Feasibility is established: single A100, ~180 GPU-hours, existing infrastructure (TRL, EvalPlus). The study design is pre-specified and yields interpretable results regardless of direction.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- The 0.5/0.5 weighting in HIGH condition is a design choice—should be documented as limitation
- Threshold sensitivity (0.3 vs 0.35) should be reported
- Pre-registration of design choices strengthens credibility

**Mitigation Strategy:** Document all design choices in methods section before running experiments. Report multiple thresholds. Acknowledge weighting as limitation and suggest learned weighting as future work.

---

## Emerged Hypothesis Summary

### Core Statement
Under PPO training of CodeLlama-7B on MBPP with fixed compute budget, if reward function provides higher information bandwidth (continuous + categorical vs. binary), then model reaches pass@1 > 0.3 in fewer training samples, because denser feedback enables gradient updates to more precisely target error-inducing code patterns.

### Causal Mechanism
1. Higher bandwidth rewards provide more bits of information per gradient update
2. This enables the model to distinguish between error types (syntax vs. runtime vs. assertion)
3. Credit assignment becomes more precise—the model learns which code patterns cause which errors
4. Faster convergence results from more informative gradient directions

### Variables
- **IV:** Reward bandwidth (LOW/MEDIUM/HIGH)
- **DV Primary:** samples-to-threshold (pass@1 > 0.3)
- **DV Secondary:** final pass@1, pass@10
- **Controlled:** base model, algorithm, compute, dataset, hyperparameters

### Key Assumptions
- A1: Error types form a meaningful ordering (syntax → runtime → assertion → pass)
- A2: CodeLlama-7B has sufficient capacity to learn from fine-grained signals
- A3: PPO training is stable enough to attribute effects to reward function
- A4: HumanEval is representative of code generation quality
- A5: 5 seeds per condition provides sufficient statistical power

### Null Hypothesis
There is no significant difference in samples-to-threshold between reward bandwidth conditions (H0: μ_LOW = μ_MEDIUM = μ_HIGH).

### Predictions
- **P1 (Primary):** HIGH condition reaches threshold in fewer samples than LOW (p < 0.05)
- **P2:** MEDIUM > LOW in convergence speed
- **P3:** Error-type distribution differs between conditions (HIGH shows fewer syntax errors by epoch 3)

### Novelty
The information bandwidth framing is novel—no prior work conceptualizes feedback granularity as bits per gradient update. The distance-to-correct scoring principle is a generalizable contribution.

### Scope & Boundaries
- **Applies to:** RLEF training of code LLMs on execution-based feedback
- **Does not apply to:** Non-execution feedback (LLM-as-judge), very large models (unclear if scaling changes dynamics)
- **Known limitations:** 0.5/0.5 weighting is heuristic, single model size tested

### Experimental Setup
- **Dataset:** MBPP (training), HumanEval (evaluation)
- **Model:** CodeLlama-7B-Instruct
- **Baselines:** LOW (binary) is the baseline condition
- **Compute:** ~180 GPU-hours total (A100)

### Related Work & Baselines
- CodeRL (2022): binary reward baseline
- RLTF (2023): multi-granularity but uncontrolled
- PPOCoder (2023): PPO-based alternative
- Let's Verify Step by Step (2023): process rewards in math

### Phase 2B Readiness Seeds
- **SH1 (Existence):** Dense feedback provides more information → verify via mutual information analysis
- **SH2 (Mechanism):** Error-type scoring enables credit assignment → verify via gradient analysis
- **SH3 (Comparison):** Deferred to Phase 5 baseline comparison

### Established Facts
- Binary rewards work but provide sparse signal (CodeRL)
- Multi-granularity shows promise but lacks controlled comparison (RLTF)
- Process rewards help in math reasoning (Let's Verify Step by Step)
- PPO training is stable for code LLMs (PPOCoder)
