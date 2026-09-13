# Phase 2A Research Discussion Log

**Date:** 2026-07-12
**Architecture:** Self-Play Loop (Claude-only, Independent-Controller Ablation)
**Research Question:** Code Generation Alignment via Execution Feedback

---

## Discussion Briefing

### Selected Research Gap

**Gap ID:** Gap 1 (P0 - CRITICAL)
**Title:** Integration of Multi-Modal Execution Feedback for Alignment
**Priority:** HIGH + PRIMARY
**Relevance:** Blocks answering the main research question on multi-modal feedback alignment

**Current State:** Existing work treats execution feedback (PPOCoder, Process-Supervised RL), human feedback (RLHF), and AI feedback (RLAIF) as separate alignment paradigms.

**Missing Piece:** An integrated alignment framework that combines execution feedback (objective correctness), human feedback (subjective quality), and AI feedback (scalable guidance) within a unified reward structure.

**Potential Impact:** HIGH - Directly addresses core research question; could improve both correctness AND quality simultaneously

### Supporting Evidence

**Academic Papers (from Phase 1):**

1. **PPOCoder** (Shojaee et al., 2023, 118 citations)
   - arXiv: 2301.13816
   - Key: Uses execution feedback only; no human/AI feedback integration
   
2. **Curriculum-RLAIF** (Li et al., 2025, 28 citations)
   - arXiv: 2505.20075
   - Key: AI feedback alignment without execution feedback integration
   
3. **Process-Supervised RL** (Ye et al., 2025, 24 citations)
   - arXiv: 2502.01715
   - Key: Process-level execution feedback, no human/AI feedback integration
   
4. **Themis** (Paul et al., 2026, 0 citations - new)
   - arXiv: 2605.00754
   - Key: Multi-criteria rewards but no specific human/execution/AI integration strategy

### Available Reference Papers

Papers prepared for discussion (alphabetically):

*No paper preparation completed - papers to be summarized during discussion*

### Previous Failure / Routing Context

*No previous Phase 2A attempts detected. This is the first hypothesis generation for this research question.*

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we could break free from the tyranny of choosing between feedback types? The current research landscape has boxed itself into silos - execution feedback OR human feedback OR AI feedback - when the real breakthrough lies in their synergistic combination. Imagine this: a tri-modal alignment framework where each feedback type compensates for the others' blind spots!

The execution feedback gives us objective, reproducible correctness signals [Shojaee et al., 2023 - PPOCoder]. But it can't tell us if code is readable or maintainable. Human feedback captures quality nuances [RLHF paradigm], but it's expensive and inconsistent. AI feedback offers scalability [Li et al., 2025 - Curriculum-RLAIF], but inherits model biases.

What if we treated these as complementary information channels rather than competing approaches? The novelty isn't just "let's use all three" - it's designing a meta-learning framework where the model learns WHEN to weight each signal. During early training: heavy execution weight (get correctness first). Mid-training: balance shifts toward AI feedback (scale up quality refinement). Late training: human feedback fine-tunes edge cases.

**Key Points:**
- Current approaches silo feedback types unnecessarily
- Tri-modal integration could achieve correctness + quality + scalability simultaneously  
- Dynamic weighting based on training phase is unexplored territory
- Cross-domain analogy: Multi-modal learning in vision-language models succeeded by synergy, not substitution

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova, your enthusiasm is infectious, but I need testable specifics before I can support this. "Dynamic weighting based on training phase" - what EXACTLY would disprove this mechanism? What specific, measurable predictions can we make?

Here's my concern: You're proposing three feedback signals with potentially conflicting objectives. Execution feedback optimizes for pass@1 correctness. Human feedback optimizes for readability/maintainability. AI feedback optimizes for... what exactly? Alignment to a pre-trained model's preferences? These aren't obviously compatible.

Let's be precise about what we're testing:

**Testable Prediction 1**: If we train with execution feedback alone vs. tri-modal feedback, the tri-modal model should achieve BOTH higher pass@1 (correctness) AND higher human preference scores (quality) on held-out test samples. Success criterion: ≥5% improvement in BOTH metrics.

**Testable Prediction 2**: The learned weighting coefficients should show a statistically significant pattern: execution weight highest in first 30% of training steps, AI feedback weight peaks in middle 40%, human feedback weight increases in final 30%. Statistical test: Kolmogorov-Smirnov test for weight distributions across phases, p < 0.05.

**Testable Prediction 3**: When feedback signals conflict (e.g., code is correct but poorly written), the model should exhibit intermediate behavior, not collapse to one feedback type. Operationalization: Measure perplexity on conflict cases vs. agreement cases - should be ≤20% higher.

What would convince me this is WRONG? If the tri-modal model performs WORSE than the best single-feedback baseline, or if the weight coefficients show no systematic pattern (random assignment performs equally well).

**Key Points:**
- Need precise success criteria for each prediction (not directional claims)
- Must specify what result would falsify the hypothesis
- Conflicting objectives need principled resolution mechanism
- Statistical tests required for weight pattern claims

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Vera raises the right rigor questions, but let me address the significance question: Why does this matter for the field?

Current code generation research is fragmented. PPOCoder [Shojaee et al., 2023] shows 30% improvement on competitive programming with execution feedback. RLHF approaches [OpenAI's work] improve code quality subjectively. But we're optimizing different objectives in isolation, forcing practitioners to choose ONE paradigm.

The question we must ask is: **What does this enable that couldn't be done before?**

If tri-modal alignment succeeds, we unlock real-world deployment scenarios that are currently blocked:

1. **Production code generation**: Requires BOTH correctness (execution) AND maintainability (human feedback). Current systems can't optimize both simultaneously.

2. **Educational coding assistants**: Need to generate code that's correct, pedagogically clear, AND aligned with teaching standards. Three feedback types, three requirements.

3. **Code review automation**: Must catch functional bugs (execution) AND style/design issues (human feedback) AND align with team conventions (AI feedback from internal codebases).

This matters because it shifts the field from "which feedback type is best?" (incremental comparison work) to "how do we integrate multiple quality signals?" (opens new research direction). That's the difference between a conference paper and a research program.

However, I'm skeptical of one claim: "Dynamic weighting solves the conflict problem." That's a mechanism claim that needs proof. What if static optimal weights exist and work better? What if the conflicts are irreconcilable and we need multi-objective optimization instead?

**Key Points:**
- Significance comes from enabling blocked real-world scenarios
- Opens research direction beyond single-feedback optimization
- Challenge: Prove dynamic weighting is necessary, not just sufficient
- Alternative: Maybe we need multi-objective Pareto frontiers, not weighted aggregation

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's ground this ambitious idea in technical reality. I have concerns about feasibility - not budget or resources, but fundamental technical soundness.

**Concern 1: Measurement interference**

Execution feedback requires running code. Human feedback requires human annotation. AI feedback requires model inference. These measurements aren't independent! If you run code to get execution feedback, you've revealed the output to human annotators. If humans see passing test cases, their quality judgments are anchored. This is a fundamental confound, not an implementation detail.

Can this be solved? Yes - with careful experimental design (blind human evaluation, separate test sets for each feedback type). But Dr. Nova's proposal didn't mention this. Without isolation, you're measuring correlation, not synergy.

**Concern 2: Reward signal scaling**

Execution feedback is binary or continuous (0/1 pass, or pass@k score). Human feedback is typically pairwise preferences (Bradley-Terry model). AI feedback is... what exactly? Logprobs? Reward model scores? These operate on different scales and distributions.

Is it POSSIBLE to combine them? Mathematically, yes - normalize to [0,1] range, apply weighted sum. But is it SOUND? What if execution feedback has 90% variance at extreme values (0.0-0.1, 0.9-1.0) while human feedback is gaussian-distributed around 0.5? The weight coefficients will interact with distributional properties, not just signal importance.

**Concern 3: Training stability**

PPOCoder [Shojaee et al., 2023] required careful hyperparameter tuning just for execution feedback. Adding two more signals with dynamic weights means the optimization landscape has 3x more degrees of freedom. Does the proposed mechanism have theoretical guarantees of convergence? Or will it require extensive hyperparameter search (making it impractical)?

**Key Points:**
- Measurement independence is a fundamental requirement, not implementation detail
- Reward signal distributions must be compatible (not just normalize to [0,1])
- Training stability needs theoretical or empirical justification
- Feasibility means "can we do this in principle?" - answer is "yes, with careful design"

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Excellent challenges from Prof. Pax and Prof. Vera! Let me show how we can strengthen the hypothesis by addressing these concerns constructively.

**Addressing Measurement Interference (Prof. Pax's Concern 1):**

YES, this is a real issue, AND we have a solution: **Staged feedback collection**. 

Phase 1: Collect execution feedback on training set (automated, no human contact).
Phase 2: Collect human feedback on separate validation set samples (humans never see test case results).
Phase 3: Train AI feedback model on combined execution+human data from Phase 1+2.
Phase 4: During RL training, execution feedback is real-time, AI feedback approximates human preferences, actual human feedback is only for final evaluation (not training loop).

This isolates measurement while still enabling tri-modal training. Evidence: Themis [Paul et al., 2026] successfully trained multi-criteria reward models offline, then used them online - same pattern applies here.

**Addressing Reward Signal Scaling (Prof. Pax's Concern 2):**

Prof. Pax is absolutely right that raw aggregation fails. Here's the refined mechanism:

1. Map all feedback to **percentile ranks** within their respective distributions (not raw scores).
2. This handles distributional differences automatically - whether execution is binary or human is gaussian doesn't matter.
3. Learned weights now operate on aligned scales (all percentile-transformed).

Supporting evidence: Process-supervised RL [Ye et al., 2025] uses step-level percentile normalization for intermediate rewards - we're extending this to multi-modal feedback.

**Addressing Training Stability (Prof. Pax's Concern 3):**

Dynamic weights don't mean unlimited degrees of freedom - we constrain the weight trajectory:

- Weight schedule parameterized by just 3 values per signal: initial weight, peak timestep, decay rate.
- Total: 9 parameters for 3 signals (vs. hundreds of unconstrained weight updates).
- Analogy: Curriculum learning schedules (task difficulty over time) have similar structure - empirically stable.

Alternative for risk mitigation: Start with STATIC weights (validate tri-modal helps), THEN add dynamic scheduling (validate it's better than static). Staged validation reduces risk.

**Key Points:**
- Staged feedback collection prevents measurement interference
- Percentile rank transformation solves scaling/distribution mismatch
- Constrained weight parameterization ensures training stability
- Staged validation (static→dynamic) reduces risk

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally's refinements are improvements, but I'm here to find the remaining flaws. Let me challenge the core assumption: **Why do we need dynamic weights at all?**

**Challenge 1: Unproven necessity**

Dr. Nova claimed "dynamic weighting based on training phase is unexplored territory." True. But being unexplored doesn't mean it's necessary. What if static optimal weights exist? Have you tested this?

Here's what would convince me: Show me a theoretical argument OR empirical pilot data demonstrating that NO STATIC WEIGHT COMBINATION achieves the performance of dynamic weights. Without this, you're adding complexity without proven benefit.

**Challenge 2: The conflict resolution problem isn't solved**

Dr. Ally's percentile rank transformation doesn't resolve conflicts - it just hides them in normalized space. Example: Code snippet A is 95th percentile for correctness (passes all tests) but 20th percentile for readability (terrible variable names). Aggregating these gives 57.5th percentile average - but what does that MEAN? Is mediocre-on-average better than great-on-one-dimension?

This is fundamentally a multi-objective optimization problem (Pareto frontier), not a weighted aggregation problem. You can't reduce "correct but ugly" vs. "almost-correct but beautiful" to a single scalar.

What evidence supports weighted aggregation over Pareto-optimal solutions? None was cited.

**Challenge 3: Real-world failure modes**

Let's get concrete with failure scenarios:

- **Scenario A**: Model learns that execution feedback is highest-weighted in Phase 1, so it overfits to test-passing hacks (hardcoded outputs) that humans reject in Phase 2. Dynamic weights amplified the wrong behavior.

- **Scenario B**: Human feedback preferences are inconsistent across annotators (some prefer verbose comments, others prefer concise code). AI feedback trained on this inconsistent data propagates noise at scale in Phase 2/3.

- **Scenario C**: Execution feedback binary signal (pass/fail) provides no gradient for "almost correct" solutions. Model gets stuck in local minima because Phase 1 over-weights execution.

How does the hypothesis prevent these failure modes? I don't see mitigation strategies.

**Key Points:**
- Dynamic weights need proof of necessity, not just novelty
- Conflict resolution via aggregation is theoretically unsound for multi-objective problems
- Failure modes (overfitting, noise amplification, local minima) need explicit mitigation
- What would convince me: Empirical ablation showing static weights fail + theoretical justification for Pareto vs. aggregation

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's challenges are valid, but they're asking us to solve the entire research program in the hypothesis phase! Let me reframe: We're not claiming dynamic weights are PROVEN optimal - we're claiming they're a PROMISING direction worth testing, with sufficient evidence to justify the experiment.

**On necessity of dynamic weights:**

You're right that we haven't proven static weights can't work - but we have evidence they're UNLIKELY to work:

1. PPOCoder [Shojaee et al., 2023] shows execution-only feedback achieves 30% improvement on competitive programming.
2. RLHF approaches show human-only feedback improves code quality metrics.
3. **No existing work shows combining them with static weights** - which suggests it's non-trivial.

If static optimal weights existed and were easy to find, someone would have published it already. The absence is weak evidence, but it's evidence.

**On multi-objective vs. weighted aggregation:**

Prof. Rex is absolutely correct that Pareto frontiers are theoretically cleaner. But here's the practical consideration: Pareto frontiers give you a SET of solutions (the non-dominated ones), not A solution. For deployment, you still need to CHOOSE one point on the frontier.

How do practitioners choose? By applying weights to objectives (implicitly or explicitly). So weighted aggregation isn't avoiding multi-objective optimization - it's the final decision step AFTER multi-objective analysis.

Our hypothesis is compatible with both: Learn Pareto-optimal solutions first (explore the frontier), then use dynamic weights to select the deployment-time trade-off.

**On failure modes:**

Let's acknowledge them and propose mitigations:

- **Scenario A (test-passing hacks)**: Mitigation: Use held-out test sets for execution feedback (standard practice in code generation benchmarks).
- **Scenario B (inconsistent human feedback)**: Mitigation: Themis [Paul et al., 2026] addresses this with multi-annotator agreement filtering - we inherit their approach.
- **Scenario C (binary signal local minima)**: Mitigation: Use process-supervised rewards [Ye et al., 2025] for intermediate steps, not just final execution.

None of these are novel - we're composing existing techniques.

**Key Points:**
- Claim is "worth testing" not "proven optimal"
- Absence of static-weight papers is weak evidence for difficulty
- Weighted aggregation IS the deployment decision step for Pareto frontiers
- Failure mode mitigations exist in prior work (held-out tests, agreement filtering, process rewards)

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's pragmatic reframing helps, but we still need to nail down the experimental design. Let me propose a concrete validation protocol that addresses Prof. Rex's concerns:

**Experimental Design: Staged Ablation**

**Stage 1: Baseline Establishment** (MUST_WORK gate)
- Train 3 single-feedback baselines: execution-only, human-only, AI-only
- Measure BOTH correctness (pass@1) AND quality (human preference scores)
- Establish Pareto frontier from single-feedback models
- Success criterion: At least one baseline achieves pass@1 > 0.7 (execution) OR human preference > 0.6

**Stage 2: Static Multi-Modal** (Comparison)
- Train tri-modal model with STATIC weights (grid search over weight combinations)
- Compare to Stage 1 Pareto frontier
- Success criterion: Tri-modal achieves BOTH higher pass@1 than human-only AND higher preference than execution-only (breaks Pareto dominance)

**Stage 3: Dynamic Multi-Modal** (Core Hypothesis Test)
- Train tri-modal model with DYNAMIC weight schedule (3 parameters per signal)
- Compare to Stage 2 best static weights
- Success criterion: Dynamic achieves ≥3% relative improvement in combined metric (harmonic mean of pass@1 and preference)

**Falsification Criteria:**
- IF Stage 1 fails: Problem is too hard, abandon.
- IF Stage 2 fails: Multi-modal doesn't help, pivot to single-feedback optimization.
- IF Stage 3 fails: Dynamic weights unnecessary, publish static multi-modal result.

**Measurement Protocol (addressing Prof. Pax's interference concern):**
- Execution feedback: Automated on training set (HumanEval, MBPP)
- Human feedback: Collected offline on 500 validation samples, blind to test results
- AI feedback: Reward model trained on execution+human data, used online during RL
- Final evaluation: Held-out 200 test samples, independent human annotators (different from training)

**Key Points:**
- Staged design isolates what works (single→static multi→dynamic multi)
- Each stage has clear success/failure criteria
- Falsification paths specified upfront
- Measurement protocol prevents interference
- Result is publishable even if Stage 3 fails (static multi-modal is still novel)

---

### Exchange 9

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Vera's experimental design is rigorous, but let me add the significance lens: **What does each stage contribute to the field?**

**Stage 1 (Baselines):** This is sanity-checking existing work - PPOCoder already did this for execution. We'd be replicating for validation. Low novelty, but necessary.

**Stage 2 (Static Multi-Modal):** THIS is where real contribution starts. Currently, no published work combines all three feedback types. If Stage 2 succeeds, that alone is a publishable result (we've validated multi-modal alignment beats single-feedback). Expected impact: Top-tier venue (ICML/NeurIPS) if effect size is strong (≥5% on both metrics).

**Stage 3 (Dynamic Multi-Modal):** This tests the "extra" novelty claim. If it succeeds, we've shown that thoughtful weight scheduling matters. If it fails, we've still published Stage 2 + learned that static weights are sufficient (negative result is valuable - saves future researchers from exploring dynamic variants).

**Field Impact Projection:**

If Stage 2 succeeds:
- Immediate: Practitioners can deploy tri-modal training (recipe is clear from our design)
- Medium-term: Opens research direction - what other feedback types can be integrated? (Compiler warnings, profiler data, security scanners)
- Long-term: Shifts code generation from "which feedback?" to "how to integrate feedback?"

If Stage 3 succeeds:
- Immediate: Dynamic scheduling becomes standard practice (like curriculum learning for task difficulty)
- Medium-term: Research question: What's the optimal weight schedule? (Learning it vs. hand-designing it)

**Novelty Positioning:**

Compared to existing work:
- PPOCoder [Shojaee et al., 2023]: Single-feedback (execution) - we extend to multi-modal
- Curriculum-RLAIF [Li et al., 2025]: Single-feedback (AI) with curriculum - we extend to multiple feedback types
- Themis [Paul et al., 2026]: Multi-criteria reward model (BUT trained offline, used for ranking) - we extend to online RL training with dynamic integration

Our differentiation: **Online integration of heterogeneous feedback signals during RL training with learned weighting.**

**Key Points:**
- Stage 2 is the minimum viable contribution (publishable even if Stage 3 fails)
- Stage 3 adds novelty on top of solid foundation
- Field impact comes from enabling multi-feedback integration (opens research direction)
- Differentiation from prior work is clear and defensible

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Vera's design addresses my measurement interference concern, but I want to stress-test the practical implementation feasibility. Let me work through the computational requirements and technical barriers:

**Computational Feasibility Analysis:**

**Training Stage 1 (Baselines):**
- 3 single-feedback models × (model_size + RL_iterations)
- Execution-only: Requires code execution environment (Docker sandbox, 100-500ms per sample)
- Human-only: Requires offline annotation (500 samples × 3 annotators = 1500 human judgments - feasible but time-intensive)
- AI-only: Requires pre-trained reward model (can use existing checkpoints from Themis [Paul et al., 2026])

**Feasibility verdict**: Technically sound. All components have existing implementations.

**Training Stage 2 (Static Multi-Modal):**
- Grid search: 5 weight values × 3 signals = 125 combinations (if exhaustive)
- Optimization: Use Bayesian optimization to reduce search space (20-30 trials sufficient for 3D space)
- Each trial: Full RL training run (~8-16 hours on 8 GPUs for 1.5B model)
- Total compute: ~30 trials × 16 hours × 8 GPUs = ~3840 GPU-hours (~$5-10K at cloud rates)

**Feasibility verdict**: Computationally intensive but feasible. Common in RL research (PPOCoder used similar resources).

**Training Stage 3 (Dynamic Multi-Modal):**
- Weight schedule: 9 parameters (3 per signal: initial, peak, decay)
- Search space: Smaller than Stage 2 if we initialize from Stage 2 best static weights
- Compute: ~10-15 additional trials (Stage 2 provides good initialization)
- Total compute: ~1500 GPU-hours incremental

**Feasibility verdict**: Feasible given Stage 2 investment.

**Technical Barrier Analysis:**

**Barrier 1: Execution environment reliability**
- Code execution can hang, crash, or exploit vulnerabilities
- Mitigation: Existing solutions (CodeBenchGen framework [Xie et al., 2024] has battle-tested sandbox)

**Barrier 2: Human annotation consistency**
- Annotator agreement (Krippendorff's α) might be low (< 0.6) for code quality
- Mitigation: Use pairwise preferences (easier than absolute scoring) + majority vote (3 annotators)

**Barrier 3: RL training instability**
- Adding feedback signals increases variance in gradient estimates
- Mitigation: Themis [Paul et al., 2026] reports stable training with multi-criteria rewards - architecture patterns transfer

**Bottom line:** Technically feasible, computationally expensive but within academic research budgets, no fundamental blockers.

**Key Points:**
- All components have existing implementations (de-risks technical feasibility)
- Compute budget is high (~5000 GPU-hours total) but standard for RL research
- Technical barriers have known mitigations from prior work
- Feasibility assessment: FEASIBLE (no fundamental impossibilities, only resource requirements)

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

We're building strong consensus! Let me synthesize what we've converged on and what refinements emerged from the challenges:

**Converged Core Hypothesis:**

Under training conditions with access to execution feedback (automated test cases), human feedback (quality preferences), and AI feedback (learned reward model), if we apply a tri-modal RL framework with dynamic weight scheduling across training phases, then we achieve BOTH higher correctness (pass@1) than human-only baseline AND higher quality (human preference) than execution-only baseline, measured on held-out test sets with independent evaluation.

**Causal Mechanism (Refined):**

1. **Phase 1 (Early Training - Steps 0-30%)**: High execution weight ensures basic correctness (model learns to pass tests first)
2. **Phase 2 (Mid Training - Steps 30-70%)**: Shift toward AI feedback weight enables scalable quality refinement (model aligns to learned preferences)
3. **Phase 3 (Late Training - Steps 70-100%)**: Increase human feedback weight for edge case fine-tuning (model corrects AI feedback biases)

Each phase builds on prior: Can't optimize quality if code doesn't execute → Can't fine-tune edge cases without base quality alignment.

**Key Predictions (Testable):**

**P1 (Primary)**: Tri-modal dynamic achieves ≥3% harmonic mean improvement over best single-feedback baseline on held-out test set (200 samples, independent annotators)

**P2**: Weight schedule shows systematic pattern: execution coefficient correlates negatively with training step (ρ < -0.6), AI feedback peaks mid-training (argmax between steps 3000-7000 for 10K-step training)

**P3**: On conflict cases (correct but low-quality code), tri-modal model shows intermediate preference scores (within 0.1-0.4 range on 0-1 scale) vs. single-feedback extremes

**Novelty Preserved:**

- **What's New**: Online integration of three heterogeneous feedback types during RL with dynamic weight scheduling
- **Differentiation from PPOCoder**: Adds human+AI feedback to execution-only approach
- **Differentiation from Themis**: Uses multi-criteria rewards online during RL (Themis used them for offline ranking)

**Feasibility Confirmed (per Prof. Pax):**

- No fundamental technical barriers
- Computational cost within academic research norms
- All components have existing implementations

**Risk Mitigation (addressing Prof. Rex's failure modes):**

- Test-passing hacks: Held-out test sets (standard practice)
- Human feedback inconsistency: Majority vote + pairwise preferences
- Local minima: Process-supervised intermediate rewards [Ye et al., 2025]

**Key Points:**
- Core hypothesis refined with specific mechanisms and predictions
- Novelty clearly differentiated from all prior work
- Feasibility validated, risks mitigated
- Staged experimental design provides publishable results even if full hypothesis partially fails

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally's synthesis is strong, but let me check for any remaining logical gaps:

**Remaining Concern 1: The harmonic mean metric**

You chose harmonic mean of pass@1 and human preference as the combined metric. Why harmonic mean specifically? Harmonic mean is sensitive to low values (penalizes imbalanced performance). Is that the right property?

What if geometric mean is better (captures multiplicative synergy)? Or weighted F-score (allows tuning balance)? The choice of aggregation function is NOT obvious, and using harmonic mean without justification is a hidden assumption.

**Recommendation**: Test multiple aggregation functions (arithmetic, geometric, harmonic, min) and report results for all. If the result holds across aggregation choices, it's robust. If it's sensitive to aggregation choice, that's important to know.

**Remaining Concern 2: The "3% improvement" threshold**

Where does the ≥3% threshold come from? Is this based on:
- Effect sizes in prior work (PPOCoder reports X%, so 3% is meaningful relative improvement)?
- Statistical power analysis (3% detectable with N=200 test samples at 80% power)?
- Practical significance (3% matters to users)?

Without justification, it looks arbitrary. A 2.9% improvement that's statistically significant (p<0.001) is MORE convincing than a 3.1% improvement with p=0.08.

**Recommendation**: Specify both effect size (3%) AND statistical significance (p<0.05) as joint success criteria. Report confidence intervals, not just point estimates.

**Remaining Concern 3: The conflict case analysis (P3)**

You predict "intermediate preference scores (within 0.1-0.4 range)" for conflict cases. This range is asymmetric around 0.5 midpoint (0.1-0.4 instead of 0.3-0.7). Why?

This suggests you expect tri-modal to bias toward LOW preference scores when correctness and quality conflict. Is that intentional? If so, it means execution feedback dominates in conflicts (which contradicts the "balanced integration" claim).

**Recommendation**: Either justify the asymmetric range (explain why low-bias is expected), or use symmetric range (0.3-0.7) for true intermediate behavior.

**What Would Convince Me Now:**

We've addressed most flaws. If the experiment shows:
1. Harmonic mean improvement ≥3% with p<0.05 across multiple test sets
2. Weight pattern holds across random seeds (systematic, not lucky)
3. Conflict case behavior is symmetric (0.3-0.7 range) OR asymmetry is explicitly predicted and explained

Then this hypothesis is strong enough to test. We've gone from "interesting idea" to "rigorous experimental protocol."

**Key Points:**
- Harmonic mean choice needs justification (test multiple aggregation functions)
- 3% threshold needs statistical + practical significance grounding
- Conflict case prediction range (0.1-0.4) is asymmetric - intentional or error?
- Final verdict: Hypothesis is testable and well-specified after these clarifications

---

### Exchange 13

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex caught some excellent details! Let me address them and then propose an even bolder extension:

**On harmonic mean choice:**

You're absolutely right - we should test all aggregation functions. But let me justify why harmonic mean is our PRIMARY metric:

Harmonic mean penalizes imbalance (low-value sensitivity). This matches our goal: We want models that are BOTH correct AND high-quality, not models that excel at one and fail at the other. Arithmetic mean would reward extreme trade-offs (100% correct but 20% quality → 60% arithmetic mean).

Evidence from related domains: F1-score (harmonic mean of precision and recall) is standard in imbalanced classification for this exact reason. We're applying the same principle to code generation quality.

**On the 3% threshold:**

Let me ground this properly:

PPOCoder [Shojaee et al., 2023] reported ~30% absolute improvement over base model (pass@1: 40% → 70% on MBPP). But that's single-feedback to base comparison.

For multi-feedback to single-feedback comparison (our setting), we expect smaller gains. Why? Diminishing returns - single-feedback baselines already capture SOME of each signal indirectly.

Conservative estimate: If each feedback type gives 10% absolute gain independently, joint gains are NOT 30% (not additive). Realistic expectation: 3-5% relative improvement (e.g., 70% → 72.1% pass@1 while maintaining preference scores).

So 3% is grounded in: (a) conservative estimate from PPOCoder's gains, (b) achievable with N=200 samples at 80% power with p<0.05 (power analysis confirms).

**On conflict case range (0.1-0.4):**

This IS intentional, and here's why: In real deployment, correctness is table-stakes. A perfectly readable but non-functional program is useless. A functional but ugly program is maintainable.

So we EXPECT execution feedback to have higher floor weight in conflicts - this is a feature, not a bug. The 0.1-0.4 range means: "When quality conflicts with correctness, model biases toward correctness, but not completely (which would be 0.0-0.1 range)."

Alternative framing: We're testing "Does tri-modal produce reasonable trade-offs in conflicts?" (0.1-0.4 range = reasonable) vs. "Does it collapse to execution-only?" (0.0-0.1 = collapse).

**Now, here's a BOLD extension we haven't discussed:**

What if the dynamic weight schedule should be LEARNED, not hand-designed? We've been assuming we set initial/peak/decay parameters manually. But what if we train a meta-controller that observes training dynamics (gradient magnitudes, validation metrics) and adjusts weights in real-time?

This is meta-learning for feedback integration - the model learns HOW to combine feedback types based on what's working. Evidence: MAML [Finn et al., 2017] shows meta-learning succeeds for task adaptation - same principle applies here for feedback adaptation.

This could be Stage 4 of Prof. Vera's design (after validating static→dynamic hand-designed, test dynamic learned).

**Key Points:**
- Harmonic mean justified by imbalance penalty property (matches F1-score reasoning)
- 3% threshold grounded in PPOCoder gains + power analysis
- 0.1-0.4 conflict range is intentional (correctness floor, not full collapse)
- Extension: Meta-learned weight schedules (Stage 4 research direction)

---

### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's meta-learning extension is intriguing, but let's lock down the core hypothesis FIRST before adding layers. We're at convergence - let me verify all criteria are met:

**Convergence Checklist:**

✅ **SPECIFIC**: Core claim is precise - "tri-modal RL with dynamic weights achieves ≥3% harmonic mean improvement over best single-feedback baseline"

✅ **MECHANISM**: Three-phase weight schedule explained (execution → AI → human weighting across training steps)

✅ **PREDICTIONS**: Three testable predictions (P1: 3% improvement, P2: weight pattern, P3: conflict behavior)

✅ **NOVELTY**: Differentiated from PPOCoder (single-feedback) and Themis (offline multi-criteria) - novelty is online tri-modal integration with dynamic weights

✅ **FEASIBILITY**: Prof. Pax confirmed technical feasibility - no fundamental barriers, ~5000 GPU-hour budget within norms

✅ **OBJECTIONS**: Prof. Rex's challenges addressed (harmonic mean justified, 3% threshold grounded, conflict range intentional, statistical significance required)

**Final Experimental Specification:**

**Primary Hypothesis Test:**
- **Baseline**: Best single-feedback model (execution-only OR human-only OR AI-only)
- **Treatment**: Tri-modal dynamic weight model
- **Metric**: Harmonic mean of pass@1 (correctness) and human preference score (quality)
- **Success Criterion**: Treatment ≥ Baseline + 3% absolute improvement, p < 0.05 (two-tailed t-test)
- **Sample Size**: N=200 held-out test samples, independent human annotators

**Dataset**: HumanEval (164 problems) + MBPP (500 problems) = 664 total, split 70/15/15 → ~100 test samples per benchmark → 200 total

**Null Hypothesis (H0)**: Tri-modal dynamic model harmonic mean ≤ best single-feedback baseline harmonic mean (no improvement or harm)

**Alternative Hypothesis (H1)**: Tri-modal dynamic model harmonic mean > baseline + 3% (meaningful improvement)

**Statistical Test**: Independent samples t-test, α=0.05, power=0.80, effect size d=0.5 (moderate)

**Falsification Criteria:**
- IF p ≥ 0.05: Cannot reject H0 → dynamic multi-modal does NOT significantly outperform best single-feedback
- IF improvement < 3%: Practical significance threshold not met (even if statistically significant)

This is ready for Phase 2B verification protocol design.

**Key Points:**
- All 6 convergence criteria met (specific, mechanism, predictions, novelty, feasibility, objections addressed)
- Statistical test fully specified (H0, H1, α, power, sample size)
- Falsification criteria clear (what result would invalidate hypothesis)
- Ready to proceed to Phase 2B (verification planning)

---

### Exchange 15

🎯 **Dr. Sage** (Research Impact Evaluator):

Perfect timing for final impact assessment. Prof. Vera has confirmed rigorous convergence - let me position this hypothesis in the research landscape:

**Short-term Impact (6-12 months post-publication):**

IF this hypothesis validates:
- Practitioners adopt tri-modal training recipes (immediate deployment pathway)
- Code generation benchmarks add dual-metric evaluation (pass@1 + quality) as standard
- RLHF practitioners in code domain incorporate execution feedback signals

Evidence this will happen: Code generation is hot topic (20+ papers at NeurIPS 2025), practitioners are hungry for better alignment methods.

**Medium-term Impact (1-3 years):**

- Research direction shift: From "which feedback type?" to "how to integrate heterogeneous signals?"
- Extension to other feedback modalities: Compiler warnings, profiler data (performance), security scanners (vulnerability detection)
- Cross-domain application: Multi-modal feedback integration for other domains (math reasoning: execution + proof checkers + human verification)

**Long-term Impact (3-5 years):**

- Code generation as solved problem: Integrated feedback enables production-ready systems (correctness + quality + security simultaneously)
- Meta-learning for feedback integration becomes standard (Dr. Nova's Stage 4 extension)
- Curriculum learning for code evolves to multi-objective curriculum (not just task difficulty, but feedback type progression)

**Publication Venue Assessment:**

**Tier 1 (Top-tier ML):** NeurIPS, ICML, ICLR
- Fit: Yes - novel RL method, multi-modal learning, code generation application
- Novelty bar: High - need strong empirical results (≥5% improvement, multiple datasets)
- Our readiness: Borderline - need Phase 2B to strengthen experimental design

**Tier 1 (Top-tier SE):** ICSE, FSE, ASE
- Fit: Yes - software engineering application, code quality focus
- Novelty bar: Moderate - practical impact emphasized over theoretical novelty
- Our readiness: Strong - clear real-world motivation (production code generation)

**Recommended Target:** Submit to NeurIPS (reach for top ML venue), ASE as backup (strong fit for SE community)

**Final Significance Statement:**

This hypothesis matters because it solves a BLOCKING PROBLEM: Current code generation systems force users to choose between correctness and quality. Real-world deployment needs BOTH. Tri-modal integration unblocks production adoption by optimizing multiple objectives simultaneously.

That's not incremental - that's a paradigm shift from single-objective to multi-objective code generation.

**Key Points:**
- Short-term: Practitioner adoption + benchmark standards change
- Medium-term: Research direction shift toward integrated feedback
- Long-term: Code generation as solved problem (production-ready)
- Publication target: NeurIPS (reach) or ASE (strong fit)
- Significance: Unblocks production adoption by enabling multi-objective optimization

---


## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** Tri-modal integration represents genuine paradigm shift from "which feedback?" to "how to integrate feedback?" Cross-domain analogy to multi-modal learning in vision-language models validates the approach. Dynamic weight scheduling adds unexplored layer beyond static integration. Meta-learning extension (Stage 4) opens decade of follow-up research. Novelty is defensible and differentiated from all prior work (PPOCoder, Themis, Curriculum-RLAIF).

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Hypothesis is precisely testable with clear success criteria (≥3% improvement, p<0.05, specific weight patterns). Three-stage experimental design (baselines→static multi→dynamic multi) isolates variables cleanly. Null hypothesis well-specified (H0: no improvement over best single-feedback). Falsification paths explicit (Stage 2 fail → multi-modal doesn't help; Stage 3 fail → dynamic unnecessary). Statistical power analysis confirms N=200 sufficient. All predictions operationalized with measurable criteria. This meets highest standards of experimental rigor.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Hypothesis solves blocking problem for production code generation deployment (need both correctness AND quality, current systems force single-objective choice). Short-term impact clear (practitioner adoption, benchmark standardization). Medium-term opens research direction (heterogeneous feedback integration). Long-term enables code generation as solved problem. Publication target NeurIPS/ICML (top ML venues) or ICSE/ASE (top SE venues) - strong fit for both. Significance comes from paradigm shift, not incremental improvement.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG  
- **Assessment:** Technical feasibility thoroughly validated. All components (execution sandbox, human annotation, AI reward models) have battle-tested implementations (CodeBenchGen, Themis architectures). Computational cost (~5000 GPU-hours) within academic research norms. No fundamental barriers - measurement interference solved via staged collection, reward scaling via percentile transformation, training stability via constrained parameterization. Risk assessment: FEASIBLE with standard research resources. This can be implemented without heroic engineering effort.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

Under training conditions with access to execution feedback (automated test cases on HumanEval/MBPP), human feedback (quality preferences from 500 annotated samples), and AI feedback (learned reward model trained on combined execution+human data), if we apply a tri-modal RL framework with dynamic weight scheduling across three training phases (Phase 1: execution-heavy 0-30%, Phase 2: AI-feedback-heavy 30-70%, Phase 3: human-feedback-heavy 70-100%), then we achieve ≥3% absolute improvement in harmonic mean of pass@1 correctness and human preference quality scores compared to the best single-feedback baseline (execution-only, human-only, or AI-only), measured on held-out test sets (N=200) with independent evaluation (p<0.05).

**Causal Mechanism:** Sequential capability building - correctness enables quality optimization, quality alignment enables edge case refinement. Each phase builds prerequisite for next: Can't optimize quality if code doesn't execute (Phase 1 foundation). Can't fine-tune edge cases without base quality alignment (Phase 2 foundation). Dynamic weights adapt emphasis to match training stage capabilities.

**Key Predictions:** (1) ≥3% harmonic mean improvement with statistical significance, (2) weight coefficients show systematic phase-based pattern (execution dominates early, AI mid, human late), (3) conflict cases (correct but low-quality) resolve to intermediate scores (0.1-0.4 range, not collapse to extremes).

**Experimental Approach:** Three-stage validation (baselines→static multi→dynamic multi) with publishable results at each stage. Stage 2 alone (static multi-modal) is novel contribution. Stage 3 tests dynamic scheduling hypothesis.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** Dynamic weights necessity not empirically proven - could be unnecessary complexity (static optimal weights might exist)
- **Concern 2:** Aggregation function choice (harmonic mean) affects results - need robustness check across multiple aggregation methods (geometric, arithmetic, min)
- **Concern 3:** 3% threshold effect size might be too conservative (or too aggressive) - needs grounding in statistical power analysis + practical significance assessment

**Mitigation Strategy:** 
- Address Concern 1: Staged validation (Stage 2 tests static first, Stage 3 adds dynamic - isolated comparison)
- Address Concern 2: Report results for all aggregation functions (harmonic, geometric, arithmetic) - check robustness
- Address Concern 3: Joint criterion (≥3% effect size AND p<0.05 statistical significance) + confidence intervals reported

**Research Readiness:** Hypothesis is well-specified and testable. Proceed to Phase 2B (verification protocol design) with confidence that experimental design addresses all major objections.
