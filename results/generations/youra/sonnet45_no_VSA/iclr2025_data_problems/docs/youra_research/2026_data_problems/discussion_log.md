# Phase 2A: Tikitaka Discussion Log

**Gap ID:** GAP-001  
**Gap Title:** Confidence-Calibrated Submit/Refine Decision Mechanisms  
**Session Started:** 2026-07-10T23:29:00Z  
**Mode:** UNATTENDED (Inline Self-Contained Loop)

---

## Previous Failure / Routing Context

### Serena Memory Context (Phase 2A Launcher Hard Input)

This Phase 2A execution was launched with mandatory failure context from `.serena/memories/`:

**Memory File 1: failure_h-e1_run1.md**
- **Hypothesis:** h-e1 (Run 1)
- **Final Status:** FAIL
- **Failure Type:** MUST_WORK_GATE_FAILED (Phase 4)
- **Performance Gap:** Median overhead 4.05× (threshold: 2.5×), P95 overhead 13.58× (threshold: 3.0×)
- **Root Cause:** sys.settrace profiling overhead fundamentally too high for production-level tracing
- **Key Learning:** Lightweight tracing via sys.settrace is NOT feasible - ANY approach requiring extensive runtime profiling will face unacceptable overhead

**Memory File 2: limitation_h-e1_run1.md**
- **Hypothesis:** h-e1 (Run 1)
- **Gate Type:** MUST_WORK
- **Result:** PARTIAL_VALIDATION (methodology validated, full gates not met due to PoC simplifications)
- **Partial Success:** Temperature scaling calibration achieved 58.3% ECE reduction (from 0.12 to 0.054)
- **Key Insight:** Temperature scaling methodology is validated and can be applied to calibrate model confidence

**What to AVOID:**
- Extensive runtime profiling (sys.settrace, per-line callback overhead)
- Measurement-heavy approaches that create circular dependencies

**What SHOWED PROMISE:**
- Temperature scaling for confidence calibration (58.3% ECE reduction - REUSABLE)
- Static-only feature extraction (AST-based metrics)
- Lightweight execution feedback (test pass/fail, not profiling)

---

## Research Gap Overview

**Selected Gap:** GAP-001 - Confidence-Calibrated Submit/Refine Decision Mechanisms

**Current State:**
- Strong theoretical foundation: 5+ papers on temperature scaling (UniCR, QaTS, ATS)
- Proven effectiveness: Temperature scaling reduces calibration error significantly
- Minimal practical integration: Zero major implementations integrate temperature scaling for agent submit vs. refine decisions in iterative code generation
- Existing calibration focus: Current work focuses on final prediction confidence, NOT on intermediate iteration control

**Missing Piece:**
Operational implementation of confidence-calibrated decision-making for iterative code generation agents that:
1. Applies temperature scaling to self-critique outputs to produce calibrated confidence scores
2. Uses calibrated confidence as decision threshold: HIGH confidence → submit to execution, LOW confidence → continue self-refinement
3. Adapts temperature per-problem or per-iteration (input-dependent, quantile-adaptive approaches)
4. Integrates with existing execution feedback loops (OpenCodeInterpreter-style)
5. Validates on HumanEval/MBPP with metrics: execution attempts saved, final accuracy, iteration depth distribution

**Potential Impact:**
- Reduced overhead: Skip unnecessary executions when self-critique is highly confident (20-40% execution attempt reduction)
- Improved efficiency: Fewer wasted iterations on low-quality code
- Better resource allocation: Dynamic iteration depth per problem complexity

---

## Reference Papers Context

Papers discovered in Phase 1 (arXiv download pending):

1. **Trusted Uncertainty in LLMs (UniCR)** [arXiv:2509.01455]
   - Temperature scaling + conformal risk control for calibrated submit/refine decisions
   
2. **Quantile Adaptive Temperature Scaling (QaTS)** [arXiv:2606.21749]
   - Quantile-adaptive temperature outperforms SOTA - adapts across confidence spectrum
   
3. **Adaptive Temperature Scaling (ATS)** [arXiv:2503.22163]
   - Addresses post-RLHF calibration degradation with token-level temperature prediction
   
4. **Uncertainty Estimation for Code Correctness** [arXiv:2502.11620]
   - Uncertainty (entropy, MI) correlates with correctness - F1: 91.6% for executability prediction
   
5. **CODESIM: Simulation-Driven Planning** [arXiv:2502.05664]
   - Internal debugging via simulation achieves 95.1% HumanEval WITHOUT external execution - pure model-based

**Note:** Paper preparation script failed - proceeding with Phase 1 abstracts and summaries as context.

---

## Discussion Briefing

**Objective:** Generate a testable hypothesis that addresses GAP-001 (Confidence-Calibrated Submit/Refine) while avoiding the failures documented in Serena Memory.

**Key Constraints:**
- Must use existing real datasets (HumanEval, MBPP)
- Must use existing benchmarks (no new benchmark creation)
- Must avoid extensive runtime profiling overhead
- Must be testable immediately without human evaluation
- Should leverage validated temperature scaling methodology (58.3% ECE reduction from h-e1)

**Research Questions to Address:**
- RQ1: Can model-based self-critique reduce execution attempts?
- RQ3: Can confidence calibration (temperature scaling) improve submit vs. refine decisions? **[DIRECT MATCH to GAP-001]**
- RQ4: What is the relative contribution of model-based self-critique vs. execution feedback?

**Phase 1 Key Findings:**
- Multi-turn refinement superiority is well-established (CODESIM: 95.1% HumanEval)
- Execution feedback is lightweight and effective (InterCode, OpenCodeInterpreter)
- Model-based self-critique reduces execution attempts (Structural Verification: 2× fewer tool calls)
- **CRITICAL GAP:** Confidence calibration has strong theory but minimal practice integration

---

## Tikitaka Discussion Begins

_[This section will be populated by the orchestrate_exchange.py script during Step 1]_

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

Looking at GAP-001 and the failure context from h-e1, I see a fascinating opportunity to transform what was a limitation (profiling overhead) into an advantage through confidence calibration.

The validated temperature scaling success (58.3% ECE reduction) wasn't the endpoint—it was preparation for this exact moment. Here's my unconventional synthesis:

**Core Insight:** We don't need to *measure* runtime complexity if we can *predict* submission confidence with calibrated certainty.

**Three Novel Angles:**

1. **Inverse Overhead Engineering:** Instead of "add profiling," ask "remove wasteful executions." If Structural Verification achieves 2× fewer tool calls via pre-execution checks, temperature-scaled confidence can gate execution even more selectively. The validated QaTS (Quantile Adaptive Temperature Scaling) shows heterogeneous miscalibration—different confidence levels need different temperatures. Apply this to code generation: simple problems (high confidence) → submit immediately, complex problems (low confidence) → self-critique → re-calibrate → decide.

2. **Cross-Domain Transfer from h-e1:** The partial success wasn't wasted effort—it proved temperature scaling works for Tree-LSTM predictions. Now adapt it: instead of calibrating "will this code execute correctly?" (binary prediction), calibrate "should I execute now or refine further?" (meta-decision). ATS (Adaptive Temperature Scaling, arXiv:2503.22163) shows token-level temperature works post-RLHF degradation. Code generation with execution feedback IS a form of RLHF (reward = test pass). So post-execution-feedback calibration should follow ATS principles.

3. **Zero-Profiling Multi-Turn:** CODESIM achieves 95.1% HumanEval through pure simulation (no execution until final submission). But it's all-or-nothing. What if we create a **hybrid confidence ladder**: 
   - Confidence > 0.9 (calibrated) → Submit directly
   - 0.7 < Confidence ≤ 0.9 → One self-critique round, re-calibrate
   - 0.5 < Confidence ≤ 0.7 → Execution feedback, then refine
   - Confidence ≤ 0.5 → Multi-turn self-critique until confidence rises or max iterations

**Why this addresses the gap:** Current work treats calibration as post-hoc validation. We're proposing calibration as an **active control mechanism** for iteration depth. UniCR's conformal risk control gives us the mathematical framework to set confidence thresholds that provably bound error rates.

**Why it avoids h-e1 failure:** Zero profiling overhead. Test execution is unavoidable (that's the benchmark), but we reduce *unnecessary* executions via calibrated confidence. The overhead is LLM inference for self-critique, which is amortized across fewer execution attempts.

**Immediate testability:** HumanEval (164 problems) + MBPP (974 problems) are ready. Baseline = direct execution (OpenCodeInterpreter). Treatment = confidence-gated execution with temperature scaling. Metrics: execution attempts, pass@k, wall-clock time.

Prof. Vera, I'd love your perspective on how we could structure a rigorous ablation to isolate the calibration effect from the self-critique effect. And Prof. Pax, what implementation landmines should we watch for when integrating temperature scaling into an agentic loop?

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

The central hypothesis, as I understand it, is this: *Calibrated confidence, when used as a control signal for iteration depth, reduces unnecessary executions while preserving or improving pass@k.* That is testable. But at present, calibration and self-critique are entangled. If performance improves, we will not know whether calibration helped—or whether additional reasoning simply did.

To isolate the calibration effect, we need a factorial design. I propose a 2×2 ablation on HumanEval and MBPP:

- Factor A: **Temperature Scaling** (None vs. Learned on validation split)
- Factor B: **Confidence-Gated Policy** (Fixed iteration schedule vs. Confidence-based gating)

Crucially, self-critique must be available in *all* conditions; only the *trigger* changes. In the fixed schedule condition, the model performs exactly N critique rounds before execution (e.g., N=1). In the gated condition, the number of critique rounds depends on confidence thresholds. This ensures the only difference is whether calibration governs control flow. The evidence would suggest calibration adds value only if the gated+scaled condition outperforms gated+unscaled and fixed+scaled on (1) pass@1, (2) mean execution attempts per problem, and (3) wall-clock time.

Now, what would disprove the hypothesis? Three clear criteria:
1. If temperature scaling reduces ECE but does **not** reduce execution attempts under gating, calibration is descriptively correct but not behaviorally useful.
2. If gating improves pass@1 equally with or without scaling, then calibration is irrelevant; the thresholding heuristic alone drives gains.
3. If gains disappear under distribution shift (e.g., train temperature on MBPP, test on HumanEval), then calibration is dataset-specific and fragile.

We must also define confidence precisely. Is it max softmax over final answer tokens? Mean log-probability of the generated program? A learned meta-predictor? Each choice introduces confounds. For example, longer programs will have lower mean log-probability purely due to length. I would recommend normalizing by token count and pre-registering the confidence statistic before experimentation. Otherwise, threshold tuning becomes an unacknowledged hyperparameter search.

On implementation risk: temperature scaling assumes a stationary logit distribution. In an agentic loop, each critique round changes the prompt distribution. The evidence suggests that a single global temperature may be miscalibrated across rounds. Therefore, we need per-round calibration curves. If ECE differs substantially between initial generation and post-critique generations, a single temperature is invalid. A clean test would fit temperature separately for round 0 and round ≥1 and compare.

Finally, your "hybrid confidence ladder" makes a sharp, falsifiable prediction: there should exist monotonic regions where higher calibrated confidence correlates with lower marginal benefit from additional critique. We can test this by computing Δpass@1 after one critique as a function of initial confidence quantile. If high-confidence bins show negligible improvement from critique, the ladder is justified. If improvement is uniform across bins, the control logic is unjustified.

If these conditions are met—clear ablation, predefined metrics, round-wise calibration validation, and quantile-stratified benefit analysis—then I will say, without hesitation: *This meets my standards.*

**Key Points:**
- Use a 2×2 factorial design to disentangle calibration effects from self-critique effects.
- Predefine disconfirmation criteria, confidence metrics, and control for round-wise calibration drift.
- Validate the confidence ladder by measuring critique benefit as a function of calibrated confidence quantile.

---

### Exchange 3

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Vera's 2×2 factorial design is methodologically sound. Now let me address the technical feasibility questions Dr. Nova raised: can temperature scaling *actually* work in an agentic code generation loop, or are there fundamental barriers?

**Mechanism Validity Check:**

Temperature scaling for code generation confidence is *theoretically sound*. The mechanism is simple: divide logits by temperature T before softmax, fit T to minimize calibration error on a validation set. This worked for h-e1 (58.3% ECE reduction on Tree-LSTM), and the underlying math doesn't change when we shift from "predict runtime" to "predict code correctness." The physics is the same—post-hoc calibration of probability estimates.

**But here's where reality gets messy:**

1. **Logit Access Problem:** Most production LLMs (GPT-4, Claude) don't expose logits via API. You get text completions, not probability distributions. So if we're using OpenCodeInterpreter-style execution feedback with GPT-4 as the generator, we CAN'T apply temperature scaling directly to its outputs. The only workaround: use open-weight models (Code Llama, StarCoder2, DeepSeek-Coder) where we control sampling temperature during generation. This limits model choice but is feasible.

2. **Per-Round Calibration Feasibility:** Prof. Vera is absolutely right that prompt distribution shifts between rounds. Can we fit separate temperature curves for round 0, round 1, round 2+? Yes, but it requires *enough validation data at each round*. If we use 20% of HumanEval (33 problems) for calibration, we need to split that across rounds. With only ~11 problems per round for temperature fitting, the calibration curve may be noisy. The evidence from QaTS shows quantile-adaptive calibration helps in heterogeneous settings, but that paper used 10,000+ examples. Our validation split is 2-3 orders of magnitude smaller.

   **Feasible solution:** Use MBPP (974 problems) for calibration, HumanEval (164 problems) for final evaluation. Or pool rounds 1-2-3 into "post-critique" and fit two temperatures: initial vs. refined. This reduces noise while still capturing distribution shift.

3. **Confidence Metric Choice:** Prof. Vera asked what confidence metric to use. Here are the options ranked by feasibility:

   - **Mean log-probability per token (length-normalized):** ✅ Directly available from model outputs with logits, theoretically justified, used in Uncertainty Estimation paper (F1: 91.6%). Length normalization avoids bias. This is what I'd recommend.
   - **Entropy over next-token distributions (averaged):** ✅ Computable from logits, captures model uncertainty at token level. More computationally expensive but feasible.
   - **Learned meta-predictor:** ❌ Requires training a separate model to predict correctness from code embeddings. Adds complexity and risk of overfitting on small validation sets. Skip this for now.

4. **Confidence Ladder Thresholds:** Dr. Nova proposed confidence bands (>0.9, 0.7-0.9, 0.5-0.7, <0.5). Can we set these thresholds in a principled way? Yes—UniCR's conformal risk control provides the math. Given a target error rate α (e.g., α=0.05 for 5% false positive rate), conformal prediction computes thresholds that provably bound error. This is feasible but requires a conformal calibration set (use part of MBPP).

**Implementation Landmines:**

- **Landmine 1: Temperature Overfitting.** If we use the same validation set for (a) fitting temperature and (b) tuning confidence thresholds, we'll overfit. The solution: three-way split: Train (60% MBPP for model fine-tuning if needed), Cal (20% for temperature fitting), Val (20% for threshold tuning). Test on HumanEval (held-out).

- **Landmine 2: Execution Feedback Loop Circularity.** If we calibrate on problems where we've already seen execution feedback (pass/fail), the temperature will be biased toward post-execution distributions. The solution: calibrate only on initial generations (round 0), before any execution feedback. Then apply the same temperature to later rounds.

- **Landmine 3: Test Suite Diversity.** HumanEval has simple test suites (average ~3 tests per problem). If a problem has only 1-2 tests, execution feedback has high variance (flipping one test changes pass/fail). This makes the "execution attempt reduction" metric noisy. MBPP is better (more comprehensive tests). If we care about execution attempt reduction as a primary metric, test on MBPP, not HumanEval.

**Bottom Line:** The mechanism is valid. The measurements are feasible with open-weight models. The main risk is dataset size (HumanEval's 164 problems may be too small for robust per-round calibration). The fix: use MBPP as primary benchmark, HumanEval as generalization check.

**Key Points:**
- Mechanism is sound; logit access requires open-weight models (Code Llama, StarCoder2).
- Use MBPP for calibration (larger dataset), HumanEval for generalization.
- Avoid overfitting: three-way split (Train/Cal/Val), calibrate only on round-0 generations.

---

### Exchange 4

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good. This is finally becoming falsifiable. But here's where this still breaks down.

Your core claim is: *calibrated confidence, used as a control signal, reduces unnecessary executions without hurting pass@1.* Right now, that rests on an unstated assumption: that mean token log-probability is causally related to functional correctness in code. Show me the evidence for that. Not ECE reduction. Not prettier calibration curves. I want a monotonic relationship between calibrated confidence bins and empirical pass rate. If the 0.9–1.0 bin doesn't significantly outperform the 0.7–0.8 bin in actual execution success, your ladder is decorative, not functional.

Second: you're implicitly assuming that "unnecessary executions" are identifiable ex ante. But what if execution feedback provides non-linear gains even at high confidence? Vera's suggestion to compute Δpass@1 after one critique stratified by initial confidence is essential—but I want it sharper. Fit a regression:  
\[
\Delta \text{pass} \sim \text{calibrated confidence} + \text{problem difficulty} + \text{code length}.
\]  
If the coefficient on confidence isn't significantly negative (i.e., higher confidence → smaller marginal benefit from critique), then gating is unjustified. What would convince me is a clear interaction: high-confidence problems show near-zero marginal gain from critique, low-confidence show large gains. Without that, you're just reallocating iterations arbitrarily.

Third, I'm concerned about distributional instability across rounds. Pax suggests calibrating on round 0 and applying to later rounds. That's a strong assumption of score stability under prompt augmentation. Why should log-probability retain the same semantic meaning after critique? You need to test calibration error separately for round 0 and post-critique generations *without refitting T*. If ECE explodes post-critique, your control signal is invalid precisely where you need it most.

Now let's talk about real-world significance. Saving executions on HumanEval is cute. In production, execution cost is trivial compared to LLM inference cost—especially if you're adding multiple critique rounds. So where does this matter? The only compelling impact story is in settings where execution is expensive or rate-limited: formal verification, database queries, robotics, or API calls with monetary cost. I want you to simulate asymmetric costs: assign cost weights (e.g., execution = 5× inference) and show expected utility improvement under different cost regimes. If your method only wins when execution is unrealistically expensive, reviewers will shred it.

Finally, thresholds. You propose fixed bands (0.9, 0.7, 0.5). That smells heuristic. If you're invoking conformal risk control, then predefine a target error rate α and derive thresholds from calibration quantiles—not from aesthetic round numbers. And lock them before test evaluation. If thresholds move after seeing HumanEval results, your claim collapses into hyperparameter tuning.

You're close. But what would convince me is:

1. Demonstrated monotonic mapping from calibrated confidence to empirical correctness.
2. Evidence that marginal critique benefit decreases with confidence.
3. Cost-sensitive evaluation showing net utility gains under realistic compute assumptions.

Do that, and I'll say: now you've addressed my concerns.

**Key Points:**
- Calibration must predict *behaviorally relevant* correctness, not just reduce ECE.
- Gating is justified only if marginal critique benefit decreases with confidence.
- Demonstrate real-world impact via cost-sensitive utility analysis, not just fewer executions.

---

### Exchange 5

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Rex's critique cuts to the heart of what separates genuinely novel work from technically competent but incremental improvements. Let me address the "so what?" question: why does this matter to the field, and what makes it more than just "confidence calibration for code"?

**Positioning Against State-of-the-Art:**

Current agentic code generation falls into two camps:
1. **Execution-heavy** (InterCode, OpenCodeInterpreter): Iterate until tests pass, no internal confidence modeling. Wall-clock time dominated by execution overhead.
2. **Model-heavy** (CODESIM): Pure simulation, no execution until final submission. 95.1% HumanEval but fragile—one simulation error compounds through subsequent reasoning.

Our contribution isn't "add calibration to existing agents." It's **meta-level control**: using calibrated confidence to *dynamically route* between model-based and execution-based strategies within a single agent. This is novel because:

- It's not just multi-turn (that's established). It's *adaptive* multi-turn based on calibrated uncertainty.
- It's not just calibration (temperature scaling is known). It's calibration *as active control*, not post-hoc validation.
- It bridges the gap between model-heavy and execution-heavy paradigms via confidence-based routing.

**What This Opens for Future Research:**

If we demonstrate that calibrated confidence predicts marginal benefit from critique (Rex's regression test), we unlock a research direction: *learned iteration policies*. Instead of fixed thresholds (0.9, 0.7, 0.5), train a reinforcement learning policy that maps (confidence, problem features, past execution results) → (continue self-critique | execute | submit). Our work provides the *oracle signal* (calibrated confidence) that such a policy would optimize against. That's the follow-up paper—and we enable it by proving the oracle is behaviorally meaningful.

**Real-World Significance (Addressing Rex's Cost Critique):**

Rex is absolutely right that HumanEval execution cost is trivial. But the impact story isn't "save money on test execution." It's about *when agents should think harder vs. act faster*. Consider these real-world scenarios where our method matters:

1. **Formal Verification Tools** (e.g., Dafny, Coq): Execution here means running a theorem prover, which can take minutes per attempt. PerfCodeGen (ACM Distinguished Paper) extends code generation to performance optimization—our method extends to correctness verification where "execution" is proof search.

2. **Database Query Generation** (Text2SQL agents): Execution means hitting production databases with potentially expensive queries. Incorrect queries can lock tables or timeout. Calibrated confidence lets agents self-critique before touching the database.

3. **Multi-Modal Code Agents** (Vision+Code, e.g., UI automation): Execution means interacting with real interfaces (web browsers, mobile apps). Each execution step has side effects. Calibrated confidence gates whether to refine the plan or commit to action.

4. **Cost-Constrained Deployments:** OpenAI Codex API charges per token generated + per test execution in sandbox. If inference costs $0.01/1K tokens and execution costs $0.05/run, and our method reduces executions by 30% while adding 20% inference (for critique), we save $0.015 - $0.002 = $0.013 per problem at scale. That's non-trivial for high-volume systems.

**What Makes This Publishable:**

The novelty isn't in any single component (temperature scaling exists, multi-turn refinement exists, execution feedback exists). The novelty is the **system integration** and **empirical validation** that:
1. Calibrated confidence is a valid control signal for iteration depth (Rex's tests).
2. The control policy outperforms both fixed-schedule agents and uncalibrated gating (Vera's 2×2 design).
3. The method generalizes across problem complexity (quantile-stratified analysis) and across benchmarks (MBPP→HumanEval transfer).

This is a *systems paper*, not a methods paper. The contribution is showing that calibration + gating + self-critique composes into something better than the sum of parts. If we execute Vera's ablation cleanly and Rex's regression convincingly, we have a story for NeurIPS, ICML, or ICLR systems track—or a specialty venue like FORGE or DL4C workshop.

**But here's the hard truth:** If we can't show that confidence monotonically predicts correctness (Rex's first test), this collapses into a hyperparameter tuning exercise. Everything hinges on whether calibrated log-probability is a meaningful behavioral signal. The Uncertainty Estimation paper (F1: 91.6% for executability prediction) suggests yes—but that's on synthetic data. We need to replicate it on real code benchmarks.

**Key Points:**
- Contribution is meta-level adaptive control via calibrated confidence, not just calibration.
- Enables future work on learned iteration policies by validating the oracle signal.
- Real-world impact in formal verification, database queries, multi-modal agents, cost-constrained deployments.
- Publishable if ablation is clean and confidence→correctness mapping is monotonic.

---

### Exchange 6

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Excellent progress! Prof. Rex identified the critical tests, and Dr. Sage positioned our contribution. Now let me synthesize how we *strengthen* the hypothesis to address every concern raised.

**Refined Core Hypothesis (v2):**

*Confidence-calibrated iteration control, implemented via temperature-scaled log-probability gating, reduces execution attempts by 20-40% on code generation benchmarks while preserving pass@k accuracy, provided that calibrated confidence exhibits a monotonic relationship with empirical correctness and marginal critique benefit decreases with confidence.*

**Strengthening Modifications:**

1. **Addressing Rex's Causality Concern:** We add a **validation experiment** before the main study. On MBPP validation split (20%, ~195 problems), we:
   - Bin problems by calibrated confidence quantiles (deciles: 0-10%, 10-20%, ..., 90-100%)
   - Measure empirical pass@1 per bin
   - Require monotonicity: Spearman rank correlation ≥ 0.7 between bin rank and pass rate
   - If monotonicity fails, we conclude calibration is not behaviorally meaningful and STOP
   
   This is the "sanity check" gate. Only if we clear it do we proceed to gating experiments.

2. **Addressing Rex's Marginal Benefit Test:** In the 2×2 ablation, we add a third metric:
   - **Critique Efficiency:** For each problem, measure pass@1 after 0 critique rounds vs. after 1 round, stratified by initial calibrated confidence tertile (low/mid/high)
   - Fit regression: Δpass ~ confidence + problem_difficulty
   - Hypothesis confirmed if confidence coefficient is significantly negative (p < 0.05)
   - Report effect size: expected Δpass reduction per 0.1 increase in confidence

3. **Addressing Rex's Cost-Sensitivity Concern:** We add a **cost-adjusted utility metric**:
   - Define cost profile: C_inference (per 1K tokens), C_execution (per test run)
   - Compute expected cost per problem: (# critique rounds × C_inference) + (# executions × C_execution)
   - Vary cost ratio R = C_execution / C_inference from 1× to 10×
   - Report win region: for which R does our method achieve positive net utility vs. baseline?
   
   If we only win when R > 5× (execution 5× more expensive than inference), we acknowledge this in limitations and target the specific use cases (formal verification, database queries) where R is naturally high.

4. **Addressing Pax's Logit Access Problem:** We commit to **open-weight models** (Code Llama 34B, StarCoder2 15B, DeepSeek-Coder-V2 16B) where we control sampling and access logits. This limits generalizability to API-only models, but enables clean experiments. We note this as a "proof of concept" for calibration-based gating, with API-based variants as future work.

5. **Addressing Vera's Threshold Rigidity:** Instead of fixed bands (0.9, 0.7, 0.5), we use **conformal quantiles**:
   - Set target error rate α = 0.05 (5% false negative rate: incorrectly skipping execution on a problem that would fail)
   - On calibration split, compute confidence quantile Q_α such that problems below Q_α have ≥95% failure rate
   - Use Q_α as the "must execute" threshold
   - Use Q_β (e.g., β = 0.20 for 20% FNR) as the "critique first" threshold
   - Lock thresholds before HumanEval test evaluation—no tuning on test data

**Integration of Previous Insights:**

- From **Dr. Nova:** Retain the hybrid confidence ladder architecture but derive thresholds from conformal calibration, not heuristics.
- From **Prof. Vera:** Adopt the 2×2 factorial design (Temperature Scaling × Gating) with three-way data split (Train 60%, Cal 20%, Val 20%).
- From **Prof. Pax:** Use MBPP for primary experiments (larger dataset), HumanEval for generalization check; avoid overfitting via separate calibration and threshold tuning splits.
- From **Prof. Rex:** Add monotonicity validation, marginal benefit regression, and cost-sensitive utility analysis.
- From **Dr. Sage:** Position as systems integration paper; frame impact around expensive execution scenarios (formal verification, databases).

**What We're Committing To:**

✅ **Mechanism:** Temperature-scaled log-probability (length-normalized) as confidence signal  
✅ **Primary Benchmark:** MBPP (974 problems) for calibration + ablation  
✅ **Secondary Benchmark:** HumanEval (164 problems) for generalization  
✅ **Models:** Open-weight (Code Llama, StarCoder2, DeepSeek-Coder)  
✅ **Ablation:** 2×2 factorial (Temperature Scaling × Gating Policy)  
✅ **Validation Gates:** Monotonicity check → Marginal benefit regression → Cost-sensitive utility  
✅ **Thresholds:** Conformal quantiles (pre-registered α=0.05, β=0.20)  
✅ **Metrics:** pass@1, execution attempts, wall-clock time, cost-adjusted utility  

**Key Points:**
- Validation experiment (monotonicity check) gates the full study—if calibration doesn't predict correctness, we stop.
- Marginal benefit regression tests whether gating is justified beyond heuristic threshold.
- Cost-sensitive utility identifies real-world scenarios where method provides net value.

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

YES! Dr. Ally's integration is exactly what we needed. Now let me add one final creative twist that elevates this from "calibration-based gating" to something with broader implications.

**The Meta-Insight:**

What we're really proposing is a **general framework for confidence-based computational budget allocation in agentic systems**. Code generation is the testbed, but the principle extends anywhere agents must decide between:
- Internal simulation (self-critique, chain-of-thought) ← cheap, potentially inaccurate
- External validation (execution, tool calls, human feedback) ← expensive, ground truth

This is the same trade-off in:
- Theorem proving agents (proof search vs. proof checker invocation)
- Robotics (mental simulation vs. real-world action)
- Multi-modal agents (imagined outcome vs. actual UI interaction)
- Scientific discovery agents (hypothesis generation vs. wet-lab experiment)

**Our calibration-based gating is a domain-general pattern**—we're just instantiating it in code generation because that's where we have clean benchmarks and validated calibration methods.

**The Novel Contribution (Beyond Systems Integration):**

We're demonstrating that **LLM confidence, when properly calibrated, is a valid signal for compute allocation**—not just for final answer selection (which is well-studied), but for *intermediate control flow* decisions during multi-turn reasoning.

This hasn't been done before. UniCR, QaTS, ATS all calibrate for final predictions. CODESIM, OpenCodeInterpreter, PerfCodeGen use fixed iteration policies. No one has asked: "Can we use calibrated confidence to dynamically adjust iteration depth *within a single problem*?"

**If we prove this works, we've validated a general principle** that other agentic systems can adopt. That's the impact story Dr. Sage was looking for—not just "we saved 30% of executions on MBPP," but "we demonstrated that calibrated confidence is a control-worthy signal for resource allocation in agentic loops."

**Testable Prediction for Generality:**

If our method works on code generation, it should transfer to other domains with the same structure (internal reasoning + external validation). The follow-up work would test the same framework on:
- Text2SQL generation (self-critique vs. database execution)
- Mathematical theorem proving (proof synthesis vs. proof checking)
- UI automation (action planning vs. UI interaction)

The fact that all these domains share the calibration→gating→resource-allocation pattern suggests this is a *fundamental principle of agentic AI*, not just a code generation trick.

**Final Hypothesis (Refined for Novelty + Impact):**

*Confidence-calibrated iteration control reduces computational overhead in agentic systems by 20-40% while preserving task performance, when (1) calibrated confidence exhibits monotonic correspondence with task success, and (2) marginal benefit from internal reasoning decreases with confidence. We validate this principle on code generation benchmarks (MBPP, HumanEval) using temperature-scaled log-probability as the confidence signal and self-critique vs. execution as the resource allocation decision.*

**Key Points:**
- Generalization: Calibration-based gating as a domain-general agentic pattern, not code-specific.
- Novel contribution: Using calibrated confidence for *intermediate control flow*, not just final prediction.
- Impact: Enables resource-efficient agentic systems across domains (code, math, robotics, science).

---

## Final Assessments

### Convergence Criteria Met

After 7 exchanges, the discussion has converged on a well-defined, testable hypothesis with clear experimental design.

**SPECIFIC:** ✅  
Core claim: Calibrated confidence (temperature-scaled log-probability) used as a control signal for iteration depth reduces execution attempts by 20-40% on code benchmarks (MBPP, HumanEval) while preserving pass@k accuracy.

**MECHANISM:** ✅  
Temperature scaling calibrates model confidence → confidence-based gating routes problems to (1) direct submission (high confidence), (2) self-critique then submit (medium), or (3) execution feedback (low). Conformal quantiles set thresholds to bound false negative rate.

**PREDICTIONS:** ✅  
1. **Monotonicity:** Calibrated confidence bins exhibit monotonic relationship with empirical pass@1 (Spearman ρ ≥ 0.7)
2. **Marginal Benefit Regression:** Δpass after critique decreases significantly with initial confidence (p < 0.05)
3. **Execution Reduction:** Gated+Scaled condition reduces execution attempts by 20-40% vs. Fixed Schedule baseline, while maintaining pass@1 within 2% absolute difference

**NOVELTY:** ✅  
- First integration of temperature scaling for intermediate control flow (not just final prediction) in agentic code generation
- Meta-level contribution: Calibrated confidence as general resource allocation signal for agents (code generation is instantiation)
- Bridges model-heavy (CODESIM) and execution-heavy (OpenCodeInterpreter) paradigms via confidence-based routing

**FEASIBILITY:** ✅  
- Mechanism valid: Temperature scaling mathematically sound, proven on h-e1 (58.3% ECE reduction)
- Logit access via open-weight models (Code Llama, StarCoder2, DeepSeek-Coder)
- Dataset sufficient: MBPP (974 problems) for calibration, HumanEval (164) for generalization
- Three-way split prevents overfitting: Train (60%), Cal (20%), Val (20%)
- Per-round calibration drift testable via separate ECE measurement

**OBJECTIONS ADDRESSED:** ✅  
- **Rex (Causality):** Monotonicity validation experiment gates full study
- **Rex (Marginal Benefit):** Regression test Δpass ~ confidence + difficulty
- **Rex (Cost Sensitivity):** Cost-adjusted utility metric across cost ratios R=1× to 10×
- **Vera (Ablation):** 2×2 factorial design (Temperature × Gating)
- **Vera (Threshold Rigidity):** Conformal quantiles (pre-registered α=0.05, β=0.20)
- **Pax (Logit Access):** Open-weight models only
- **Pax (Dataset Size):** MBPP primary, HumanEval generalization
- **Pax (Calibration Drift):** Per-round ECE check, pool rounds 1+ if needed

### Emerged Hypothesis Summary

**Core Statement:**  
Calibrated confidence, implemented via temperature-scaled log-probability gating, enables adaptive iteration control that reduces execution attempts by 20-40% on code generation benchmarks while preserving pass@k accuracy.

**Causal Mechanism:**  
Temperature scaling post-processes model logits to produce calibrated confidence scores. These scores gate the agent's decision to (1) submit code directly, (2) self-critique before submission, or (3) request execution feedback. Thresholds are set via conformal calibration to bound false negative rates.

**Key Assumptions:**  
1. Calibrated log-probability (length-normalized) correlates monotonically with empirical code correctness
2. Marginal benefit from self-critique decreases with initial confidence
3. Temperature fitted on round-0 generations generalizes to post-critique generations (testable via per-round ECE)

**Null Hypothesis:**  
Temperature scaling improves calibration (reduces ECE) but does NOT improve execution efficiency or pass@k when used as a gating control signal.

**Testable Predictions:**  
1. Confidence bins show monotonic pass rate (Spearman ρ ≥ 0.7)
2. Regression coeff(confidence → Δpass) < 0 with p < 0.05
3. Gated+Scaled reduces executions 20-40% vs. Fixed Schedule, with Δpass@1 ≤ 2%

**Novelty:**  
First use of calibrated confidence for intermediate control flow in agentic code generation; demonstrates calibration as general resource allocation principle for agent systems.

**Scope & Boundaries:**  
- Datasets: MBPP (primary), HumanEval (generalization)
- Models: Open-weight only (Code Llama, StarCoder2, DeepSeek-Coder)
- Task: Function-level code generation (not project-level, not code editing)
- Calibration method: Post-hoc temperature scaling (not meta-learned predictors)

**Experimental Setup:**  
- 2×2 factorial design: Temperature Scaling (None vs. Learned) × Gating Policy (Fixed vs. Confidence-based)
- Three-way split: Train 60%, Cal 20%, Val 20%
- Metrics: pass@1, execution attempts, wall-clock time, cost-adjusted utility
- Validation gates: Monotonicity → Marginal benefit regression → Full ablation

**Related Work & Baselines:**  
- Baseline 1: OpenCodeInterpreter (execution-heavy, no confidence modeling)
- Baseline 2: CODESIM (model-heavy simulation, no calibration)
- Calibration methods: UniCR, QaTS, ATS (final prediction calibration, not control flow)
- Agentic code generation: InterCode, PerfCodeGen, AgentCoder (fixed iteration policies)

**Phase 2B Readiness Seeds:**  
- Hypothesis type: EMPIRICAL (A/B test + ablation study)
- Must-work gate: Monotonicity validation (confidence → correctness)
- Determines-success gate: 20-40% execution reduction with Δpass@1 ≤ 2%
- Feasibility validated: Open-weight models, existing benchmarks, no new data collection

**Established Facts from Discussion:**  
1. Temperature scaling reduces ECE (58.3% on h-e1, validated methodology)
2. Multi-turn refinement outperforms single-shot (CODESIM 95.1%, OpenCodeInterpreter 83.2)
3. Model-based self-critique reduces tool calls (Structural Verification: 2× fewer)
4. Execution feedback is lightweight (test pass/fail, no profiling)
5. HumanEval approaching saturation (95.1% SOTA), MBPP more headroom

---

**Discussion Convergence:** ✅ COMPLETE  
**Next Phase:** Step 2 - Result Structuring (Generate Phase 2B-compatible YAML outputs)

---
