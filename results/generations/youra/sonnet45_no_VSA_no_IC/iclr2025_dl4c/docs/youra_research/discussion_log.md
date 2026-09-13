# Phase 2A: Research Discussion Log

## Metadata
- **Gap ID**: GAP-001
- **Gap Title**: Optimal Execution Feedback Granularity for Small Models
- **Start Time**: 2026-08-19T00:00:00Z
- **Architecture**: Self-Contained Tikitaka Loop
- **Execution Mode**: UNATTENDED

## Discussion Briefing

### Research Gap
Multiple papers explore execution feedback (CodeRL+, CoCoS, DebugRepair), but granularity varies: binary pass/fail (CodeRL), variable-level traces (CodeRL+), runtime evidence (DebugRepair). No systematic study on optimal granularity for <1B models.

Missing: Empirical comparison of feedback granularity (pass/fail only vs + error messages vs + stack traces vs + variable traces) specifically for lightweight models (<1B params) on HumanEval/MBPP.

Potential Impact: Could determine minimal sufficient feedback signal for small model alignment, reducing infrastructure complexity while maintaining effectiveness.

### Phase 1 Key Findings
From `01_targeted_research.md`:
- 9 recent validation papers (2025-2026) confirm execution feedback viability for small models (<1B-3B)
- Small models achieve 13-35% improvement with execution feedback (CoCoS, RLVR)
- "Feedback Over Form" study (McAndrews, 2026): execution feedback >> pipeline complexity at 1-3B scale
- Multiple fault-tolerant systems available (TorchFT, Gemini, Swift)
- Benchmarks with test suites readily available (HumanEval, MBPP, HumanEval-XL, HumanEval Pro)

### Previous Failure / Routing Context
The Phase 2A launcher checked `.serena/memories` and found no memory files.
This is the first Phase 2A attempt (not a recursive entry).

### Available Papers
(No papers prepared - Phase 1 identified no reference papers with available arXiv IDs for this gap)

### Research Repos
- https://github.com/boazlavon/eg_cfg
- https://github.com/SalesforceAIResearch/perfcodegen
- https://github.com/openai/human-eval
- https://github.com/bigcode-project/bigcode-evaluation-harness

---

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What an exciting gap we're exploring! The fact that no one has systematically studied feedback granularity specifically for small models (<1B params) is a goldmine opportunity.

Here's what strikes me: Everyone's chasing the biggest models with the fanciest feedback mechanisms — variable-level traces (CodeRL+), runtime evidence collection (DebugRepair) — but what if the **sweet spot for lightweight models is much simpler than we think**? The "Feedback Over Form" finding (McAndrews, 2026) already hints at this: execution feedback >> pipeline complexity at 1-3B scale. That's revolutionary!

I'm proposing we explore **three unconventional angles**:

**Angle 1: Minimalist Hypothesis** — What if pass/fail alone is sufficient for <1B models? The CoCoS paper achieved 35.8% MBPP improvement with 1B models using accumulated trajectory rewards. Maybe small models don't need rich granularity — they need *consistent* feedback. Think of it like teaching a child: simple "right/wrong" might be more digestible than detailed explanations when working memory is limited.

**Angle 2: Error Message Sufficiency Threshold** — Instead of adding ALL error types/stack traces, what if there's a **critical minimum set** of error signals? Python has ~60 exception types, but maybe only 5-10 drive most alignment gains (TypeError, IndexError, NameError for code structure bugs). We could create an **error taxonomy** ranked by alignment impact for small models.

**Angle 3: Cross-Benchmark Feedback Compression** — Here's a wild idea: What if the feedback granularity that works on HumanEval (algorithm-focused, 164 problems) differs from MBPP (entry-level, 974 problems)? We could test whether **benchmark characteristics** (problem complexity, test suite depth) dictate optimal feedback granularity. If HumanEval needs richer signals but MBPP works with binary, that's a design principle!

**Key Questions I'm Burning to Answer:**
- Does feedback granularity interact with model size non-linearly? (Maybe 350M needs different signals than 1B?)
- Can we identify a "diminishing returns" point where adding more feedback details stops helping?
- What if error messages matter more for CERTAIN failure types (syntax vs logic errors)?

Let's challenge the assumption that "more granular = better" — maybe for small models, **less is actually more** because it reduces noise!

**Key Points:**
- Small models may benefit from simpler feedback due to limited capacity
- Error message taxonomy could identify highest-impact signals
- Benchmark characteristics might dictate optimal granularity
- Non-linear relationship between model size and feedback needs worth exploring

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's enthusiasm is infectious, but let's ground these ideas in falsifiable predictions. I appreciate the minimalist hypothesis, but "simpler is better" needs precise operationalization.

Here's what I need to see for scientific rigor:

**On the Minimalist Hypothesis (Angle 1):**
Dr. Nova suggests pass/fail alone might suffice for <1B models. That's testable, but we need to define "suffice" precisely. I propose:
- **Testable Prediction 1**: A 600M model trained with **binary pass/fail feedback only** achieves ≥80% of the performance gain observed when training the SAME model with **pass/fail + full error messages** on HumanEval.
- **Success Criterion**: If binary achieves ≥12.4 pp improvement (80% of CoCoS's 35.8% × 0.5 for different benchmarks), minimalist hypothesis is supported.
- **Falsification**: If binary achieves <8 pp improvement (<50% of rich feedback), hypothesis is rejected.

**On Error Taxonomy (Angle 2):**
The "critical minimum set" idea is promising, but how do we identify those 5-10 exception types without circular reasoning? I propose:
- **Method**: Train separate models on disjoint error type subsets (e.g., Group A: {TypeError, NameError}, Group B: {IndexError, KeyError}, Group C: {ValueError, AttributeError}). Measure which group drives largest pass@1 gains.
- **Control**: Ensure error type frequency is balanced across groups (can't compare if Group A appears 10× more often).
- **Falsifier**: If ALL groups show similar gains, taxonomy hypothesis is weak — it's frequency, not error type semantics.

**On Cross-Benchmark Differences (Angle 3):**
This is where I see the biggest methodological risk. HumanEval (algorithm-focused) vs MBPP (entry-level) differ in MANY dimensions: problem complexity, test suite depth, domain coverage. How do we isolate feedback granularity's effect?

- **Testable Prediction 2**: Training on HumanEval with **binary feedback** transfers to MBPP with <5 pp drop, BUT training on HumanEval with **error messages** transfers with <2 pp drop. The smaller drop for richer feedback suggests granularity matters for transfer.
- **Confound Check**: We must control for model capacity saturation — if the 600M model maxes out on MBPP regardless of feedback type, we can't distinguish transfer quality.

**What Would Disprove These Ideas:**
- If binary feedback shows NO improvement over supervised fine-tuning (SFT) baseline, execution feedback's value is in the details, not the signal itself.
- If error message granularity shows gains on HumanEval but ZERO transfer to MBPP, feedback is overfitting to benchmark-specific artifacts.
- If 350M vs 1B models show IDENTICAL optimal granularity, model size doesn't interact with feedback needs (contradicts Dr. Nova's non-linearity claim).

**Edge Cases to Control:**
- **Timeout-induced pass/fail bias**: If a model generates code that times out, it's marked "fail" — but is that a learning signal or noise? We need timeout-aware metrics.
- **Test suite insufficiency**: HumanEval's tests miss edge cases (EvalPlus showed 80× more tests needed). Does richer feedback compensate for weak tests, or does it just memorize the limited test patterns?

**My Demand**: Before we celebrate "minimalism," show me the experiment that would convince us it's WRONG. That's the experiment we run first.

**Key Points:**
- Minimalist hypothesis needs ≥80% performance retention threshold
- Error taxonomy requires disjoint subset comparison with frequency control
- Cross-benchmark claims must isolate granularity from confounds
- Falsification criteria must precede confirmation bias

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Vera's rigor is essential, but let's step back and ask: **Why does this research matter beyond proving one configuration works slightly better than another?**

Here's the broader significance I see — and the questions we must answer to ensure this isn't just incremental tuning:

**Contribution 1: Democratizing Code LLM Alignment**
If the minimalist hypothesis holds (binary feedback achieves ≥80% of rich feedback's gains), that's **transformative for resource-constrained researchers**. Right now, execution feedback research is dominated by labs with massive compute — DebugRepair's runtime evidence collection requires instrumentation overhead, CodeRL+'s variable-level traces need execution engines with state tracking.

**But**: If we prove binary feedback is sufficient for <1B models, we enable:
- Academic labs with single GPUs to train aligned code models
- On-device code assistance for developers without cloud infrastructure
- Rapid iteration cycles (simpler feedback = faster training)

**The "So What" Test**: Does this finding **change who can participate** in code LLM alignment research? If yes, high impact. If it's just "use this config for 2% better pass@k," that's incremental.

**Contribution 2: Model Capacity × Feedback Granularity Principle**
Dr. Nova's non-linearity hypothesis (model size interacts with feedback needs) could establish a **design principle** for the field. Currently, researchers scale feedback complexity as models grow (7B models get richer feedback than 1B). But what if the relationship is U-shaped?

- **Hypothesis**: Ultra-small models (<350M) and large models (>7B) need rich feedback to overcome capacity limits or utilize their representational power, BUT mid-range models (600M-2B) achieve optimal learning with simpler signals because they're in the "Goldilocks zone."
- **Field Impact**: If validated, this principle guides researchers: "For your 1B model, start with binary feedback; for 7B+, invest in variable-level traces."

**Contribution 3: Benchmark-Feedback Co-Design**
The cross-benchmark angle (HumanEval vs MBPP granularity needs) opens a NEW research direction: **co-designing benchmarks and feedback mechanisms**. Right now, benchmarks define problems and tests, feedback is an afterthought. What if:

- Algorithm-heavy benchmarks (HumanEval) should be paired with coarse feedback (binary pass/fail) because the test suites are comprehensive?
- Entry-level benchmarks (MBPP) need richer feedback (error messages) because test coverage is weak?

This flips the question from "what feedback is best?" to "what feedback matches this evaluation context?" That's a **meta-principle** for the field.

**What Makes This Genuinely Novel vs Incremental:**
- **Novel**: Establishes feedback granularity as a function of model capacity and benchmark characteristics (principle)
- **Incremental**: Shows Config A beats Config B by 3% on HumanEval (empirical result)

**My Challenge**: Which of these contributions can we claim with confidence? If we're only validating "binary works for 1B models," that's useful but not paradigm-shifting. If we're establishing a **capacity-granularity-benchmark design space**, that's a foundational contribution.

**Questions This Research Must Answer for High Impact:**
1. Does the finding generalize beyond HumanEval/MBPP to other code domains (SQL generation per MATS framework, scientific workflows per MOSAIC)?
2. Can we articulate a **decision rule** practitioners use? ("For model size X on benchmark type Y, use feedback granularity Z")
3. Does this change how we evaluate code LLMs? (Should we report pass@k for MULTIPLE feedback types, not just one?)

**Key Points:**
- Democratization angle: Resource-constrained researchers gain access to alignment
- Capacity-granularity principle: Design rule for the field
- Benchmark-feedback co-design: Meta-principle for evaluation
- Must establish principles, not just empirical wins, for high impact

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Dr. Sage's vision is compelling, but let's talk about whether we can actually **build and measure** these ideas with existing resources. I see technical feasibility risks that could derail even the best-designed hypotheses.

**Feasibility Check 1: Can We Isolate Feedback Granularity Effects?**

Here's my concern with the minimalist hypothesis experiment: **feedback granularity is confounded with training signal frequency**. If binary pass/fail provides one bit per problem, but error messages provide ~log₂(60 exception types) + stack trace depth bits, we're not just comparing granularity — we're comparing information density.

**Technical Reality**: To isolate granularity, we need:
- **Controlled Information Budget**: Normalize total bits of feedback across conditions. If binary gives 1 bit/problem, error messages should give 1 bit/problem too (e.g., most-likely error type only, not full stack trace).
- **Frequency Balancing**: If error messages appear in 80% of failures but stack traces in 20%, we can't compare their effectiveness — one has 4× more training signal.

**Can We Do This?** Yes, but it requires:
1. Logging all execution outcomes with metadata (error type frequencies, stack trace depth distributions)
2. Post-processing to balance information density across feedback types
3. Retraining multiple models with controlled feedback budgets

**Resource Estimate**: 3-5 model training runs (600M params each) × 2-4 hours/run on A100 = 6-20 GPU-hours. **Feasible** with single-GPU budget.

**Feasibility Check 2: Benchmark Characteristics Measurement**

Dr. Nova's cross-benchmark angle requires us to QUANTIFY "problem complexity" and "test suite depth." How?

**Technical Approaches**:
- **Problem Complexity**: Cyclomatic complexity of reference solutions, AST depth, number of function calls, control flow graph size
- **Test Suite Depth**: Number of test cases per problem, branch coverage of tests on reference solution, assertion types (equality vs exception checks)

**Measurement Feasibility**:
- HumanEval: 164 problems, we can compute all metrics in ~1 hour (static analysis)
- MBPP: 974 problems, ~5 hours for full analysis

**Risk**: What if HumanEval and MBPP don't differ significantly on these metrics? Then we can't test the "benchmark characteristics dictate feedback" hypothesis — insufficient variance.

**Feasibility Check 3: Transfer Evaluation Without New Training**

Prof. Vera's transfer test (HumanEval → MBPP) is elegant, BUT: do we train ONE model on HumanEval and evaluate on MBPP, or do we need MULTIPLE models (one per feedback type)?

**Resource Reality**:
- Option A (One Model, Varied Feedback at Eval): Doesn't work — feedback type is baked into training, can't vary at test time.
- Option B (Multiple Models): 3 feedback types × 2 benchmarks = 6 training runs. At 4 hours/run = 24 GPU-hours. **Feasible** but not trivial.

**My Recommendation**: Start with 2 feedback types (binary vs error messages) on 2 benchmarks = 4 training runs (16 GPU-hours). Defer stack traces / variable-level traces to follow-up.

**Feasibility Check 4: Error Taxonomy Discovery**

Dr. Nova's "critical minimum set" requires empirical discovery, not assumption. Here's the technically sound approach:

1. **Frequency Analysis**: Log all error types from 1000 HumanEval + MBPP generations with a baseline model. Rank by frequency.
2. **Impact Analysis**: For each error type, measure: How often does fixing it flip a fail → pass outcome? (proxy for alignment signal strength)
3. **Subset Selection**: Pick top-5 by impact × frequency product.

**Can We Measure Impact?** Yes, with a **counterfactual experiment**:
- Generate code that fails with TypeError
- Manually fix TypeError → new code
- Re-run tests → if now passes, TypeError had high impact

**Resource**: 100 samples × 10 error types = 1000 manual fixes. **Not scalable**. Alternative: Use Self-Debug approach (model fixes own errors) and measure flip rate. **Feasible** but noisier.

**What Could Block This Research:**
- **Insufficient Model Training Budget**: If 600M models don't converge in 4 hours (require 12+ hours), 16 GPU-hours → 60+ GPU-hours. Still feasible but tight.
- **Benchmark Test Suite Instability**: HumanEval uses `assert` statements that can be flaky (environment-dependent imports, timeout sensitivity). We need **deterministic execution harness** (BigCode harness solves this).
- **Information Density Confound Ignored**: If we don't normalize bits/problem, we're not testing granularity, we're testing "more feedback = better" (obvious and uninteresting).

**My Verdict**: This research is **technically feasible** with existing HumanEval/MBPP benchmarks and single-GPU training budget, BUT only if we:
1. Control information density across feedback types
2. Limit initial scope to 2 feedback types (binary vs error messages)
3. Use BigCode harness for deterministic eval
4. Accept that error taxonomy discovery will be approximate (frequency-based, not causal impact)

**Key Points:**
- Information density must be controlled to isolate granularity
- Benchmark complexity metrics computable via static analysis
- Transfer eval requires multiple model training runs (4-6 runs feasible)
- Error taxonomy discovery needs counterfactual analysis or frequency proxy
- Technical feasibility confirmed IF we constrain scope appropriately

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Excellent progress! I'm seeing a coherent hypothesis emerging from these exchanges. Let me synthesize what we've validated so far and strengthen the areas where concerns were raised.

**Strengthened Core Hypothesis:**

**Under** the constraint of small model capacity (<1B parameters) and existing benchmark infrastructure (HumanEval, MBPP),

**If** we train models with lightweight feedback signals (binary pass/fail vs binary + error type vs binary + error + stack trace),

**Then** there exists an **optimal feedback granularity** that maximizes alignment performance while minimizing information density overhead,

**Because** small models have limited capacity to utilize rich supervision signals, and simpler feedback reduces noise-to-signal ratio in the training objective.

**Addressing Prof. Vera's Falsification Demands:**

YES to the ≥80% retention threshold for minimalist hypothesis — that's a concrete success criterion. Here's how we strengthen it:

**Primary Prediction (P1):**
A 600M parameter model trained with **binary pass/fail only** on HumanEval achieves ≥80% of the pass@1 improvement observed with **binary + full error messages**, where improvement is measured against supervised fine-tuning baseline.

- **Success Criterion**: If SFT baseline = 40% pass@1, error messages achieve 52% (+12 pp), then binary must achieve ≥49.6% (+9.6 pp).
- **Falsification**: If binary achieves <46% (+6 pp, <50% retention), hypothesis rejected.
- **Timeline**: Single-GPU training, 4 model runs × 4 hours = 16 hours total.

**Secondary Prediction (P2):**
The **error type taxonomy** derived from frequency × impact analysis predicts 60% of variance in alignment gains across disjoint error subsets.

- **Success Criterion**: Top-5 error types (by frequency × flip-rate product) account for ≥60% of total fail→pass transitions in a held-out validation set.
- **Falsification**: If top-5 account for <40% of transitions, taxonomy lacks predictive power.
- **Method**: Frequency analysis on 1000 generated samples (feasible), flip-rate proxy via Self-Debug (noisier but scalable per Prof. Pax).

**Addressing Prof. Pax's Information Density Concern:**

This is critical. We **normalize information budget** across feedback types:

1. **Binary condition**: 1 bit per problem (pass = 0, fail = 1)
2. **Error-Type condition**: 1 bit per problem (most-likely error type from top-5 taxonomy, encoded as 0-4)
3. **Stack-Trace condition**: 1 bit per problem (stack trace depth: shallow = 0, deep = 1)

**Justification**: By fixing bits/problem = 1, we isolate whether the **semantic content** of feedback (pass/fail vs error type vs trace depth) matters, not total information.

**Prof. Pax's Concern About Frequency Balancing**: We stratify sampling during training — if TypeError appears in 60% of errors but IndexError in 10%, we **oversample IndexError examples** to balance frequency. Standard stratified sampling technique.

**Addressing Dr. Sage's Impact Demand:**

We claim **Contribution 2** (Model Capacity × Feedback Granularity Principle) as our primary impact:

**Design Principle**: *For code generation models in the 600M-2B parameter range, binary execution feedback achieves near-optimal alignment on algorithm-focused benchmarks (HumanEval), while error-type feedback is necessary for entry-level benchmarks (MBPP) due to weaker test coverage.*

**Why This Matters**: Current practice scales feedback complexity with model size. Our principle suggests **benchmark characteristics** matter more than model size for feedback selection — a practitioner designing a code assistant can now match feedback to their evaluation context, not just their model budget.

**Refined Experimental Design:**

| Condition | Model | Benchmark | Feedback Type | Info Budget | Training Hours | Evaluation Metric |
|-----------|-------|-----------|---------------|-------------|----------------|-------------------|
| Baseline | 600M | HumanEval | SFT only | N/A | 4h | pass@1, pass@10 |
| Min-HE | 600M | HumanEval | Binary only | 1 bit/prob | 4h | pass@1, pass@10 |
| Err-HE | 600M | HumanEval | Error type (top-5) | 1 bit/prob | 4h | pass@1, pass@10 |
| Min-MBPP | 600M | MBPP | Binary only | 1 bit/prob | 4h | pass@1, pass@10 |
| Err-MBPP | 600M | MBPP | Error type (top-5) | 1 bit/prob | 4h | pass@1, pass@10 |
| Transfer | 600M | HumanEval → MBPP | Binary vs Error | 1 bit/prob | 4h train | pass@1 delta |

**Total**: 6 runs × 4 hours = 24 GPU-hours. **Feasible** with A100 40GB.

**Success Dashboard:**
- P1 (Minimalist): Binary achieves ≥80% of Error's gains on HumanEval → Validates lightweight approach
- P2 (Taxonomy): Top-5 errors explain ≥60% variance → Validates error selection principle
- P3 (Benchmark-Feedback Match): Error feedback shows larger gains on MBPP than HumanEval (>5 pp difference) → Validates benchmark characteristic hypothesis

**Remaining Objections Addressed:**
- **Prof. Vera's Confound Check (Model Saturation)**: We use 600M models that are NOT saturated on MBPP (current SOTA ~70%, leaving headroom).
- **Prof. Pax's Deterministic Eval**: Use BigCode harness for all evaluations (eliminates flakiness).
- **Dr. Sage's Generalization**: We test on TWO benchmarks (HumanEval + MBPP) with different characteristics — if principle holds across both, generalization is supported.

**What This Hypothesis NOW Predicts:**
1. Lightweight feedback suffices for small models on comprehensive benchmarks
2. Error taxonomy is discoverable and predictive
3. Benchmark test coverage quality interacts with optimal feedback granularity
4. Practitioners can use (model size, benchmark type) → feedback granularity decision rule

**Key Points:**
- Hypothesis now has Under-If-Then-Because structure
- Three testable predictions with success/fail thresholds
- Information density normalized, frequency balanced
- 24 GPU-hours experiment is feasible
- Design principle delivers field-level impact

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Strong synthesis by Dr. Ally, but I'm not letting this hypothesis off easy. Time to stress-test every assumption and find where it breaks down.

**Concern 1: The "Sufficient" Claim is Too Weak**

Dr. Ally proposes binary feedback achieves ≥80% of error-message gains. But 80% of what? If error messages only improve by 2 pp over SFT, then binary achieving 1.6 pp is "sufficient" by this metric — but is that scientifically interesting?

**My Demand**: Add an **absolute improvement threshold**. Binary feedback must achieve BOTH:
- ≥80% retention of error-message gains (relative)
- ≥8 pp absolute improvement over SFT baseline (absolute)

**Why 8 pp?** CoCoS paper showed 35.8% improvement on MBPP with 1B models. Scaled to HumanEval (~half the complexity), expect ~15-20 pp gains. 8 pp is ~40-50% of expected, a non-trivial floor.

**Falsification**: If binary shows <8 pp absolute gain, lightweight feedback is too weak for practical deployment, even if it's "80% of something tiny."

**Concern 2: Information Budget Normalization is Misguided**

Prof. Pax's 1 bit/problem constraint sounds rigorous, but it **cripples the rich feedback conditions**. Error messages carry ~log₂(60) ≈ 6 bits of information, stack traces add depth/line number (another 4-6 bits). By truncating to 1 bit, you're not testing "error messages," you're testing "severely degraded error signals."

**Alternative**: Use **information-theoretic fairness** instead of bit ceiling:
- Binary condition: 1 bit/problem (pass/fail)
- Error-Type condition: log₂(5) ≈ 2.3 bits/problem (top-5 error types, full vocabulary)
- Stack-Trace condition: 2.3 + log₂(10) ≈ 5.6 bits/problem (error type + trace depth bucket)

**This way**, each condition uses its natural information capacity, and we measure **efficiency**: bits-per-performance-point. If binary achieves 48% pass@1 with 1 bit and error-type achieves 52% with 2.3 bits, binary is MORE efficient (8% gain per bit vs 5.2% gain per bit).

**My Challenge**: Justify why 1 bit ceiling is scientifically valid. If you can't, switch to efficiency metric.

**Concern 3: Benchmark Characteristics Are Proxy, Not Cause**

Dr. Sage claims "algorithm-heavy benchmarks need coarse feedback, entry-level needs rich feedback" based on test coverage quality. But **test coverage is not measured**, it's assumed.

**What If**: HumanEval and MBPP have IDENTICAL test coverage quality (e.g., both ~60% branch coverage), but differ in problem domain? Then the benchmark-feedback match is spurious correlation.

**My Demand**: Measure actual test coverage before claiming causation:
1. Run reference solutions through BigCode harness with coverage tooling
2. Compute branch coverage, statement coverage for each problem
3. Correlate coverage quality with feedback-type gains

**Falsification**: If HumanEval and MBPP have <10% coverage difference but show >5 pp feedback-type difference, "test coverage" hypothesis is wrong — it's something else (problem complexity, domain, etc.).

**Concern 4: Frequency Balancing Creates Synthetic Distribution**

Dr. Ally proposes oversampling rare error types (IndexError) to balance frequency with common types (TypeError). This **distorts the natural error distribution** models will see in deployment.

**Consequence**: A model trained with balanced errors might perform well on the balanced test set, but **fail on real-world code** where TypeError is 6× more common than IndexError. We've optimized for an artificial task.

**My Alternative**: Train on NATURAL error distribution, then analyze gains **per error type separately**. If TypeError (frequent) shows 5 pp gain and IndexError (rare) shows 2 pp gain, that's valuable signal — don't throw it away with balancing.

**Justification**: Real-world deployment sees natural distributions. Training on synthetic distributions is a laboratory artifact.

**Concern 5: Transfer Evaluation Conflates Two Hypotheses**

The Transfer condition (HumanEval → MBPP) tests:
- H1: Feedback type affects cross-benchmark generalization
- H2: Feedback type affects within-benchmark performance

But the experiment ALSO trains separate models on MBPP directly (Min-MBPP, Err-MBPP). If **both** transfer and direct training show binary < error-type, we've confirmed H2 (feedback type matters) but NOT H1 (transfer differs from direct).

**What We Actually Need for H1**:
- Train on HumanEval with binary → Eval on MBPP → X% pass@1
- Train on HumanEval with error-type → Eval on MBPP → Y% pass@1
- Train directly on MBPP with binary → Eval on MBPP → Z% pass@1

**Testable Claim**: Y - X > Z - X (i.e., richer feedback helps transfer MORE than direct training). If Y - X ≈ Z - X, feedback doesn't differentially affect transfer.

**Concern 6: Model Size (600M) is Arbitrary**

Dr. Ally picks 600M as "representative small model," but CoCoS used 1B and RLVR used 0.6B-1B. Why 600M specifically? What if the capacity-feedback relationship is non-monotonic, and 600M is a local minimum?

**My Demand**: Test TWO model sizes: 350M and 1B. If both show same feedback-granularity ranking (binary < error < trace), hypothesis generalizes. If 350M shows different ranking, we've found a **phase transition** in capacity-feedback space — that's MORE interesting than single-size results.

**Resource**: 6 conditions × 2 sizes = 12 runs × 4h = 48 GPU-hours. Still feasible with A100, just needs 2 days.

**Where This Hypothesis BREAKS:**
- Binary feedback shows <8 pp absolute gain (too weak for practical use)
- HumanEval and MBPP have identical test coverage but different feedback needs (test coverage is not the cause)
- Efficiency metric (bits/performance-point) shows error-type is 2× more efficient than binary (contradicts minimalist claim)
- Transfer gains don't differ from direct training (H1 is false)
- 350M and 1B models show opposite feedback-granularity rankings (no generalizable principle)

**My Recommendation**: Add these stress tests NOW, before declaring victory. If the hypothesis survives, it's bulletproof. If it breaks, we learn where the boundary conditions are — equally valuable.

**Key Points:**
- Absolute improvement threshold (≥8 pp) prevents weak-but-technically-sufficient claims
- Information budget should measure efficiency, not impose artificial ceiling
- Test coverage must be measured, not assumed
- Natural error distributions preserve deployment realism
- Transfer hypothesis needs direct comparison of transfer vs direct training
- Multi-size validation (350M + 1B) tests generalization

---

### Exchange 7

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Rex's stress tests are exactly what we needed! I'm revising the hypothesis to address every concern while keeping it experimentally feasible.

**REVISED HYPOTHESIS (Strengthened):**

**Under** small model capacity (350M and 1B parameters tested) and existing benchmarks (HumanEval 164 problems, MBPP 974 problems with measured test coverage),

**If** we train models with execution feedback at natural error distributions (binary pass/fail, error-type vocabulary, error+trace),

**Then** lightweight feedback (binary or error-type only) achieves ≥80% relative retention of rich feedback gains AND ≥8 pp absolute improvement over SFT baseline, with feedback efficiency (pp-gain-per-bit) decreasing as granularity increases,

**Because** small models have limited capacity to utilize high-dimensional supervision signals, and natural error distributions provide sufficient signal density at lower granularity levels for algorithm-focused benchmarks.

**Strengthened Predictions:**

**P1 (Minimalist Sufficiency - DUAL THRESHOLD):**
Binary feedback on HumanEval achieves:
- ≥80% retention of error-type gains (relative), AND
- ≥8 pp absolute improvement over SFT (absolute)

**Success**: If SFT = 40%, error-type = 52% (+12 pp), then binary must achieve ≥49.6% (+9.6 pp relative) AND ≥48% (8 pp absolute). Takes stricter threshold.

**Falsification**: Binary < 48% absolute OR <80% relative → hypothesis rejected

**P2 (Efficiency Metric - Prof. Rex's Fix):**
Feedback efficiency measured as (pass@1 improvement) / (bits per problem):
- Binary (1 bit/prob): Target 8+ pp gain → 8 gain/bit
- Error-type (2.3 bits/prob): Target 12 pp gain → 5.2 gain/bit
- Error+trace (5.6 bits/prob): Target 14 pp gain → 2.5 gain/bit

**Success**: Efficiency decreases with granularity (diminishing returns confirmed)

**Falsification**: If error+trace shows HIGHER efficiency than binary → more granularity is strictly better (minimalist claim fails)

**P3 (Test Coverage Causation - Measured):**
HumanEval and MBPP test coverage differs by ≥15% (branch coverage metric), AND feedback-type gains correlate with coverage delta (r > 0.6).

**Method**:
1. Measure branch coverage for all problems using `coverage.py`
2. Compute per-problem coverage scores
3. Correlate coverage with (error-type gain - binary gain) across problems

**Success**: Coverage explains ≥60% variance in feedback-type advantage

**Falsification**: Coverage differs by <10% OR correlation <0.4 → test coverage is NOT the causal mechanism

**P4 (Transfer vs Direct - Prof. Rex's H1 Test):**
Training on HumanEval with error-type and evaluating on MBPP shows LARGER improvement over binary (compared to direct MBPP training).

**Concrete**:
- HumanEval(binary) → MBPP eval = 42% pass@1
- HumanEval(error-type) → MBPP eval = 47% pass@1 [+5 pp transfer gain]
- MBPP(binary) direct = 45% pass@1
- MBPP(error-type) direct = 48% pass@1 [+3 pp direct gain]

**Success**: Transfer gain (+5 pp) > Direct gain (+3 pp) → richer feedback helps transfer MORE

**Falsification**: Transfer gain ≤ Direct gain → feedback doesn't differentially affect generalization

**P5 (Multi-Size Validation - 350M + 1B):**
Both 350M and 1B models show same feedback-granularity efficiency ranking: Binary > Error-type > Error+trace (in gain-per-bit).

**Success**: Consistent ranking across sizes → capacity-feedback principle generalizes

**Falsification**: Rankings flip (e.g., 350M prefers error+trace, 1B prefers binary) → phase transition exists, need finer-grained size sweep

**Revised Experimental Design (Incorporating All Fixes):**

| Run ID | Model | Benchmark | Feedback | Info (bits/prob) | Train Dist | Eval | GPU-hrs |
|--------|-------|-----------|----------|------------------|------------|------|---------|
| R1 | 350M | HumanEval | SFT only | 0 | N/A | pass@1,10 | 3 |
| R2 | 350M | HumanEval | Binary | 1.0 | Natural | pass@1,10 | 3 |
| R3 | 350M | HumanEval | Error-type | 2.3 | Natural | pass@1,10 | 3 |
| R4 | 350M | HumanEval | Error+trace | 5.6 | Natural | pass@1,10 | 3 |
| R5 | 350M | MBPP | Binary | 1.0 | Natural | pass@1,10 | 3 |
| R6 | 350M | MBPP | Error-type | 2.3 | Natural | pass@1,10 | 3 |
| R7 | 1B | HumanEval | Binary | 1.0 | Natural | pass@1,10 | 5 |
| R8 | 1B | HumanEval | Error-type | 2.3 | Natural | pass@1,10 | 5 |
| R9 | 1B | MBPP | Binary | 1.0 | Natural | pass@1,10 | 5 |
| R10 | 1B | MBPP | Error-type | 2.3 | Natural | pass@1,10 | 5 |
| R11 | Coverage Analysis | HumanEval + MBPP | - | - | - | branch % | 2 |
| **Total** | | | | | | | **40** |

**Key Changes from Previous Design:**
1. ✅ **Dual threshold** (relative + absolute) per Prof. Rex concern #1
2. ✅ **Efficiency metric** (gain-per-bit) instead of artificial 1-bit ceiling per concern #2
3. ✅ **Test coverage measurement** (Run R11) to validate causation per concern #3
4. ✅ **Natural error distributions** (dropped balancing) per concern #4
5. ✅ **Transfer vs Direct comparison** built into R2/R3 + R5/R6 cross-eval per concern #5
6. ✅ **Multi-size validation** (350M + 1B) per concern #6
7. ✅ **Dropped stack-trace condition** for 350M (focus on binary vs error-type, add trace only if budget allows)

**Resource Check:**
- 40 GPU-hours fits within 2 days on single A100 40GB
- Coverage analysis (Run R11) uses static tooling, no GPU needed
- Total experiment duration: 3-4 days including eval and analysis

**Success Dashboard (All-or-Nothing):**
- [ ] P1: Binary ≥48% absolute AND ≥80% relative on HumanEval
- [ ] P2: Efficiency ranking confirmed (binary > error-type > trace in gain/bit)
- [ ] P3: Test coverage explains ≥60% variance in feedback advantage
- [ ] P4: Transfer gain > Direct gain for richer feedback
- [ ] P5: 350M and 1B show consistent efficiency ranking

**IF ALL 5 PASS**: Hypothesis survives stress test → Design principle validated
**IF ANY FAIL**: Boundary conditions identified → Refine hypothesis scope

**Remaining Risks Acknowledged:**
- **Model capacity saturation**: If 1B models hit 70%+ pass@1 on MBPP, ceiling effects may obscure feedback differences. Mitigation: Use HumanEval Pro (harder) if this occurs.
- **Test coverage proxy limits**: Branch coverage is one metric; doesn't capture semantic test quality. Mitigation: Report multiple coverage types (branch, statement, path).
- **Natural distribution skew**: If TypeError dominates 90% of errors, rare error types may be undertrained. Mitigation: Report per-error-type gains separately (stratified analysis).

**What We're NOW Ready to Test:**
1. Dual-threshold minimalist hypothesis with absolute floor
2. Information-theoretic efficiency across granularity levels
3. Causal role of test coverage in feedback-benchmark matching
4. Differential effect of feedback on transfer vs direct training
5. Generalization of efficiency ranking across model sizes

**This hypothesis is bulletproof or breaks in interpretable ways.** Either outcome advances the field.

**Key Points:**
- Dual threshold (relative + absolute) prevents weak sufficiency claims
- Efficiency metric (gain-per-bit) replaces artificial information ceiling
- Test coverage measured, not assumed (causation testable)
- Natural error distributions preserved for deployment realism
- Transfer hypothesis directly compared to direct training
- Multi-size validation (350M + 1B) tests generalization
- 40 GPU-hours feasible, 3-4 day timeline

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** **STRONG**
- **Assessment:** The multi-dimensional design space (model capacity × feedback granularity × benchmark characteristics) is novel. Current research treats feedback as a monolithic "more is better" dimension. This hypothesis establishes it as an efficiency tradeoff with diminishing returns, potentially shifting the field from maximalist to minimalist feedback design for resource-constrained settings.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** **STRONG**
- **Assessment:** Five testable predictions with clear success/failure thresholds. Dual-threshold approach (P1) prevents ambiguous "technically correct but uninteresting" outcomes. Efficiency metric (P2) and coverage causation (P3) are quantitative and falsifiable. Transfer hypothesis (P4) directly tests differential effects rather than observational correlation. Multi-size validation (P5) provides generalization check. This is a rigorous experimental design.

🎯 **Dr. Sage** (Significance):
- **Verdict:** **MODERATE-STRONG**
- **Assessment:** If all predictions pass, this establishes a **capacity-granularity-benchmark design principle** that democratizes code LLM alignment research (single-GPU budgets sufficient). However, significance depends on boundary conditions — if hypothesis only holds for 350M-1B range and algorithm-focused benchmarks, impact is narrower than claimed. The efficiency metric (gain-per-bit) is a novel evaluation lens that could influence how the field reports alignment results.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** **STRONG**
- **Assessment:** Revised design addresses all technical concerns. Natural error distributions preserve deployment realism. Efficiency metric replaces artificial information ceiling. Test coverage measurement is feasible via static analysis. 40 GPU-hours fits single-GPU budget (2 days on A100). Multi-size validation (350M + 1B) confirms generalization without excessive cost. Biggest remaining risk is model saturation on MBPP, mitigated by HumanEval Pro fallback. This experiment can be executed with existing resources.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The consensus hypothesis emerging from our discussion is:

**For small language models in the 350M-1B parameter range, execution feedback granularity exhibits diminishing returns on code generation alignment.** Specifically, lightweight feedback signals (binary pass/fail or error-type vocabulary) achieve ≥80% of the performance gains from richer feedback (error messages + stack traces) while using 2-10× fewer information bits per training example.

**Core Claim**: The optimal feedback granularity for small model alignment is determined by the **efficiency frontier** (performance gain per bit of supervision), not the absolute richness of the signal. This efficiency frontier shifts based on benchmark test coverage quality — comprehensive test suites (HumanEval) enable lightweight feedback sufficiency, while weaker test coverage (MBPP) benefits more from error-type granularity.

**Mechanism**: Small models have limited representational capacity. High-dimensional feedback (variable-level execution traces, full stack dumps) exceeds their ability to extract actionable gradients, resulting in noise-dominated learning. By contrast, low-dimensional feedback (binary outcomes, error type categories) provides concentrated supervision signals that small models can effectively utilize.

**Key Predictions**:
1. **Minimalist Sufficiency**: Binary feedback achieves ≥8 pp absolute improvement AND ≥80% relative retention of error-message gains on HumanEval
2. **Efficiency Decreases with Granularity**: Gain-per-bit ranking: Binary (8 pp/bit) > Error-type (5 pp/bit) > Error+trace (2.5 pp/bit)
3. **Test Coverage Causation**: Branch coverage differences between benchmarks explain ≥60% of variance in feedback-type advantages

**Experimental Approach**: Train 350M and 1B models on HumanEval and MBPP with three feedback conditions (binary, error-type, error+trace) under natural error distributions. Measure pass@1 improvement over SFT baseline and compute efficiency (pp-gain / bits-per-problem). Cross-validate with measured test coverage and transfer evaluation.

**Novelty**: Establishes feedback granularity as an **efficiency optimization problem** rather than a capability maximization problem. Provides practitioners with a decision rule: match feedback granularity to (model size, benchmark test coverage) instead of defaulting to "richest feedback available."

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1**: Model capacity saturation on MBPP may obscure feedback differences if 1B models hit ~70% ceiling. **Mitigation**: Use HumanEval Pro (harder benchmark) if saturation observed.
- **Concern 2**: Test coverage measurement via branch coverage is a proxy; doesn't capture semantic test quality (edge case coverage, assertion diversity). **Mitigation**: Report multiple coverage metrics (branch, statement, path) and acknowledge proxy limits in discussion.
- **Concern 3**: Natural error distributions may be heavily skewed (e.g., TypeError 90%, others 1-2% each), undertrained rare error types. **Mitigation**: Report per-error-type stratified gains to identify which errors drive overall performance.

---
