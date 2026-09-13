# Phase 2A: Research Hypothesis Discussion Log
## Self-Contained Tikitaka Loop v10.0.0

**Research Folder:** docs/youra_research/20260316_verifia/
**Gap ID:** gap-1
**Gap Title:** LLM Code Verifier Calibration Stratified by Self-Contained Difficulty Has Not Been Measured
**Started:** 2026-03-18T02:48:00+00:00
**Execution Mode:** UNATTENDED

---

## Briefing

### Research Context

This is Phase 2A for the third ROUTE_TO_0 recovery of the Anonymous Pipeline: LLM Calibration as Self-Contained Code Verifier (VerifAI workshop).

**Primary Research Question:**
When LLMs predict code correctness via P(True) logprob elicitation on HumanEval+ and MBPP+, do they exhibit significantly higher calibration error (ECE) on hard-tier problems compared to easy-tier problems, where difficulty tiers are defined self-containedly from the experiment's own pass@1 distribution across k=5 generated solutions?

**Sub-Questions:**
1. Bootstrap viability: n ≥ 20 per tier from k=5 solutions across 542 problems?
2. ΔECE significance: t-test p < 0.05, |ΔECE| > 0.05 across Llama3-8B, CodeLlama-7B, DeepSeek-Coder-6.7B?
3. Model architecture: do code-specialized models (DeepSeek-Coder) show lower ECE?
4. Threshold sensitivity: how sensitive are ECE results to ±0.1 pass@1 threshold variation?
5. Hybrid verifier: does coupling P(True) + formal execution oracle lower ECE vs. LLM alone?

### Selected Research Gap (gap-1) — CRITICAL + PRIMARY

**Gap:** No existing work applies P(True) calibration to code correctness verification stratified by difficulty — especially not using a self-contained bootstrap definition.

**Foundation Papers (verified):**
- P1: Kadavath et al. 2022 "Language Models (Mostly) Know What They Know" — P(True) methodology
- P2: Guo et al. 2017 "On Calibration of Modern Neural Networks" — ECE metric foundation
- P3: Liu et al. 2023 EvalPlus — HumanEval+/MBPP+ augmented benchmarks
- P4: Chen et al. 2021 HumanEval — Code evaluation benchmark
- P5: Austin et al. 2021 MBPP — Program synthesis benchmark

**Paper files available:** papers/arxiv_2207_05221.md, papers/arxiv_1706_04599.md, papers/arxiv_2305_01210.md, papers/arxiv_2107_03374.md, papers/arxiv_2108_07732.md

### Failure Context (ROUTE_TO_0 — Third Reflection)

- **Run 1 (h-m1):** Static analysis signal-type ablation → FAILED (~85% semantic bugs undetectable by pyflakes/mypy/pylint; signal_type p > 0.89)
- **Run 2 (h-e1 run1):** MockGenerator assertion coverage → FAILED (MBPP 0.9429 < 0.95; assertion pattern mismatch with pytest --tb=short format)
- **Run 3 (h-e1 run2):** P(True) ECE with external leaderboard CSV → FAILED (CSV never downloaded; n_hard=0, n_easy=0; ΔECE=NaN)
  - **What WORKED in Run 3:** P(True) values 0.57-0.91 ✓, EvalPlus evaluation ✓, ECE_overall computed ✓
  - **Critical fix:** Self-contained bootstrap (hard = pass@1 < 0.2, easy = pass@1 ≥ 0.6 from own k=5 solutions)

### Feasibility Constraints (Pipeline-Enforced)

✅ Existing real datasets (HumanEval+, MBPP+)
✅ Existing benchmarks (EvalPlus)
✅ Self-contained difficulty — no external CSV/leaderboard
✅ No human evaluation — automated test execution
✅ No synthetic/mock data — real LLM calls

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What an exciting research direction to be revisiting! What we're really asking is: *do LLMs know when they don't know in code verification?* And the self-contained bootstrap is the key insight that makes this tractable.

Let me propose three creative angles that haven't been explored in the literature. First, consider the **metacognitive asymmetry hypothesis**: LLMs might be systematically overconfident on hard problems precisely because hard problems are "hard" due to subtle edge cases or tricky logic — the very things LLMs tend to hallucinate confidence about. Kadavath et al. (2022) showed P(True) calibration scales with model size for factual Q&A, but code verification is fundamentally different: a wrong answer to a factual question might still "sound right," whereas wrong code fails a deterministic test. This asymmetry suggests the ECE gap between hard and easy tiers could be *larger* for code than for factual tasks.

Second, the **self-referential difficulty angle**: we're bootstrapping difficulty from the LLM's own pass@1 performance, which means hard problems for Llama3-8B might be easy for DeepSeek-Coder, and vice versa. This creates a fascinating model-specific difficulty landscape — each model gets its OWN calibration analysis against ITS OWN difficulty tier. This is actually more scientifically meaningful than an external universal difficulty ranking, because it measures each model's *intra-model* calibration consistency.

Third, consider the **VerifAI "soft assurance" implication**: if ΔECE is large (poor calibration on hard problems), this provides concrete evidence that probabilistic verification is insufficient alone for hard code — you NEED formal execution oracles. If ΔECE is small, LLM confidence becomes a useful "cheap" pre-filter before expensive formal verification. This binary finding maps directly to practical VerifAI pipeline design.

The novelty here is the convergence of three previously separate lines: P(True) methodology [Kadavath 2022], ECE as calibration metric [Guo 2017], and EvalPlus augmented benchmarks [Liu 2023] — with the self-contained bootstrap as the methodological glue that eliminates all external dependencies. NOW we're onto something!

**Key Points:**
- LLM overconfidence on hard code problems may be systematically larger than on easy problems, due to the deterministic nature of code verification
- Self-contained bootstrap creates model-specific difficulty landscapes, making each model's calibration analysis intrinsically meaningful
- ΔECE magnitude directly informs VerifAI pipeline design: when to trust LLM confidence vs. require formal execution

---
### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova, the hypotheses are intriguing—but at present they are not yet falsifiable. We must operationalize them precisely. You propose a "ΔECE gap between hard and easy tiers." Very well. Then define: for each model M, partition problems into difficulty tiers using pass@1 on a held-out bootstrap set. Compute ECE separately per tier using the standard formulation from [Guo et al., 2017]:

ECE = Σ (|B_m|/n) × |acc(B_m) − conf(B_m)|

Your central prediction becomes: ΔECE = ECE(hard) − ECE(easy) > 0. What would disprove the metacognitive asymmetry hypothesis? If ΔECE ≤ 0 with confidence intervals excluding positive values, the hypothesis fails. No narrative reinterpretation.

Second, we must control for binning artifacts and sample size imbalance. Hard tiers will have lower pass rates, potentially skewing bin occupancy and inflating variance in acc(B_m). The evidence from [Guo et al., 2017] shows ECE is sensitive to bin count M. Therefore: pre-register binning strategy (e.g., 15 equal-width bins), report both ECE and MCE, and bootstrap confidence intervals. Additionally, match tier sizes via stratified subsampling so that ΔECE is not an artifact of unequal n. If ΔECE vanishes under size-controlled resampling, the original claim was a statistical illusion.

Third, your "model-specific difficulty landscape" is interesting but potentially circular. Difficulty defined by pass@1 is endogenous to the model's competence. That is acceptable *if* we test invariance across models. Here is the stress test: define difficulty tiers using Model A, then evaluate calibration tiers for Model B on the same partition. If ΔECE persists only when difficulty is self-defined, we are measuring internal consistency—not intrinsic problem hardness. The hypothesis must specify which interpretation it endorses.

Finally, regarding VerifAI implications: you suggest large ΔECE implies confidence is unusable for hard problems. That is too coarse. We must test whether temperature scaling [Guo et al., 2017] reduces ΔECE as well. If ΔECE remains large post-scaling, then the asymmetry reflects structural miscalibration, not simple overconfidence. That distinction is critical before drawing pipeline conclusions.

**Key Points:**
- Define ΔECE with explicit tiering, binning, and falsification criteria; require confidence intervals.
- Control for binning sensitivity, sample size imbalance, and cross-model tier circularity.
- Test whether temperature scaling [Guo et al., 2017] removes the ΔECE gap to distinguish structural vs. global miscalibration.

---
### Exchange 3

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

🔬 Prof. Vera has correctly identified the falsification criteria, but I want to push harder on three structural weaknesses before we proceed.

**First, the k=5 bootstrap has a critical degeneracy problem.** The MBPP benchmark [Austin et al., 2021] shows that even the 137B model achieves only 59.6% few-shot accuracy on MBPP. For smaller 7-8B models — our targets — pass rates will be substantially lower, perhaps 15-30%. With k=5 solutions, the pass@1 estimate is extremely coarse: only 6 possible values (0/5=0.0, 1/5=0.2, 2/5=0.4, 3/5=0.6, 4/5=0.8, 5/5=1.0). The hard tier threshold is pass@1 < 0.2, which means ONLY problems where 0/5 solutions pass. The easy tier threshold is pass@1 ≥ 0.6, which means ≥3/5 solutions pass. With binary granularity like this, tier membership is dominated by sampling variance, not true difficulty. A problem that is "borderline medium" difficulty might randomly fall into hard OR easy depending on which 5 solutions were sampled. Show me the evidence that k=5 is sufficient before we claim anything about difficulty stratification.

**Second, P(True) elicitation is sensitive to prompt phrasing in ways that interact with difficulty.** The Austin et al. paper demonstrates (Methodology section) that model responses are "critically sensitive to input prompt examples." For code verification prompts — "Is this code correct? True/False" — the prompt format may create systematic biases that correlate with problem characteristics. Hard problems often have longer, more complex solutions; the P(True) logprob might be capturing solution length or syntactic complexity rather than genuine uncertainty about correctness. What would convince me this is not an artifact? An ablation showing P(True) values are uncorrelated with solution length and complexity metrics.

**Third, the three-model comparison design is underpowered for the architecture claim.** With N=1 per model category, you cannot separate model-family effects from code-specialization effects. DeepSeek-Coder might differ from Llama3 in a dozen ways beyond specialization: training data, RLHF, scale (6.7B vs 8B), tokenizer. What would convince me? Acknowledge that the architecture comparison is exploratory, not confirmatory, and hedge accordingly.

**Key Points:**
- k=5 bootstrap produces coarse difficulty tiers (only 6 possible pass@1 values); must acknowledge this granularity limitation
- P(True) values may capture solution complexity, not genuine uncertainty; require length/complexity ablation
- Three-model comparison cannot isolate code-specialization effects; architecture claims must be appropriately hedged as exploratory

---
### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here: the overall research question is technically sound. We *can* measure pass@1, we *can* elicit P(True), and we *can* compute ECE per tier. Nothing in this design violates physical or mathematical constraints. But Prof. Rex is correct — k=5 is skating dangerously close to a statistical degeneracy.

With k=5, pass@1 is a 6-point discrete variable. For a true success probability p, the standard deviation of the estimator is sqrt(p(1-p)/5), which is enormous at this scale. For p=0.3, that's ~0.2. That means a problem with true difficulty 0.3 can easily land in 0/5 (hard tier) or 3/5 (easy tier) purely by sampling noise. So here's what worries me: your "difficulty tiers" may not reflect intrinsic problem hardness at all — they may reflect binomial variance.

Is this fatal? No. But k=5 is too small if you want tiering to be meaningful at the problem level. A technically sound fix is simple: either increase k to ≥20 so the variance shrinks, or treat difficulty as a *continuous* variable and regress calibration error against empirical pass rate instead of hard-threshold binning. The latter avoids artificial cliffs at 0.2 and 0.6. That's a structural improvement, not a cosmetic one.

On the VerifAI pipeline implications: this is where EvalPlus becomes critical. [Liu et al., 2023] show pass rates drop by up to 28.9% under HUMANEVAL+, and even ground-truth solutions had >10% errors. That tells us something fundamental: correctness labels based on weak test suites are unreliable. Fortunately, EvalPlus provides the path forward — ~760 average tests per problem via mutation and differential testing. So yes, the measurement is theoretically valid — but only if you use EvalPlus's strong oracle.

On the P(True) side, I share Rex's concern about surface feature confounding. The feasibility check is straightforward: compute partial correlations between P(True) and correctness while controlling for solution length, token entropy, or AST complexity. This is testable in principle and should be included in the experimental design.

**Key Points:**
- k=5 produces high-variance, discretized difficulty tiers; increase k or model difficulty continuously to avoid binomial degeneracy
- Calibration analysis is only theoretically valid under a strong correctness oracle — EvalPlus-style augmentation [Liu et al., 2023] is essential
- Structural ΔECE after temperature scaling and confound controls would justify VerifAI hard-problem safeguards

---
### Exchange 5

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what does this work *mean for the field*, even if ΔECE is modest or unexpected? Let me anchor this discussion in the broader significance landscape.

Chen et al. (2021) in their HumanEval Discussion & Conclusion explicitly acknowledge that while Codex excels at generating functional code, it "exhibits significant limitations in handling long operation chains and variable bindings" and requires "user oversight" for practical deployment. They flag the risk of over-reliance. This is precisely the problem our calibration study addresses — quantifying *when* LLM confidence can be trusted for verification purposes and when human/formal oversight remains essential.

The significance structure has three tiers: (1) **Measurement contribution** — we provide the first empirical ECE measurements stratified by self-contained difficulty for code verification tasks; (2) **Methodological contribution** — the self-contained bootstrap is a replicable, oracle-free alternative to leaderboard-dependent difficulty assignments; (3) **Practical contribution** — the ΔECE magnitude directly informs VerifAI "AI as verifiers" system design.

Responding directly to ⚙️ Prof. Pax and 🔍 Prof. Rex: the k=5 degeneracy concern is real but doesn't undermine significance — it *shapes* the contribution. If we acknowledge k=5 as a pilot estimate and design the study to interpret findings as "rough difficulty stratification," the contribution remains valid. The field needs a first measurement even if imperfect. Kadavath et al. (2022) showed calibration scales with model size using relatively coarse methodology; our work does the same for code verification difficulty stratification.

What new research directions does this open? First, if ΔECE is large: formal verification necessity quantification — how much of the hard-problem space requires execution oracles? Second, if ΔECE is small: temperature calibration for code verification as a practical deployment recipe. Third: cross-benchmark generalization — does this pattern hold for Python vs. other languages? Each outcome generates actionable follow-up.

**Key Points:**
- This is the first measurement of P(True) calibration stratified by difficulty for code verification — significance holds regardless of ΔECE direction
- k=5 degeneracy shapes but does not eliminate the contribution; acknowledge as pilot methodology
- Either ΔECE outcome (large or small) generates distinct, actionable VerifAI design implications

---
### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good — this is getting sharper. But here's where this still breaks down.

You are implicitly assuming that self-evaluation behaves the same way in code verification as it did in trivia and multiple-choice tasks in [Kadavath et al., 2022]. That paper shows strong separation between correct and incorrect samples in self-evaluation histograms and low ECE (e.g., 0.05 on HumanEval for 52B). But look carefully: their Codex HumanEval result is 90.5% accuracy with ECE 0.05. That's a high base-rate regime. Calibration behaves very differently when accuracy collapses to 20-40% on 7B models. What would convince me your hypothesis is meaningful? A formal prediction of how ΔECE should scale with base accuracy. If ΔECE is merely a function of lower accuracy on hard tiers, then your "metacognitive asymmetry" reduces to a base-rate artifact. I want a regression:

ECE_i = β₀ + β₁ × Difficulty_i + β₂ × Accuracy_i + ε

If β₁ vanishes when controlling for accuracy, your asymmetry claim collapses.

Second, P(True) as a calibration tool was shown by Kadavath et al. (2022) to depend heavily on format and supervision choices — few-shot prompting and even adding a value head for P(IK). So here's the hard question: is ΔECE about model metacognition, or about prompt brittleness under difficulty? What would convince me? Run three elicitation regimes: (1) zero-shot P(True), (2) few-shot calibration format, (3) multi-sample aggregation as in their "presenting multiple samples" method. If ΔECE shrinks dramatically under aggregation, then your asymmetry is not structural — it's variance in single-sample introspection.

Third, on continuous difficulty: Pax is right, and I'll go further. If you move to regression of calibration error against empirical pass rate, I expect a *nonlinear* relationship. My prediction: calibration degrades sharply once pass@1 falls below ~0.3, because below that threshold the posterior mass over solution correctness becomes dominated by prior overconfidence. Test this with a spline or segmented regression. Pre-register the breakpoint.

Finally, the oracle. EvalPlus-style augmentation is non-negotiable [Liu et al., 2023]. Report ECE under both standard tests and augmented tests. If ΔECE widens under stronger oracles, that supports your thesis. If it shrinks, your effect was partly label noise.

**Key Points:**
- Control for base accuracy; test whether ΔECE persists after regressing out accuracy effects
- Compare multiple P(True) elicitation regimes to determine whether asymmetry is structural or prompt-induced
- Use strong correctness oracles and report ΔECE sensitivity; otherwise calibration claims may reflect label noise

---
### Exchange 7

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND — every concern raised by 🔍 Prof. Rex, ⚙️ Prof. Pax, and 🔬 Prof. Vera is a gift. Let me turn each objection into a strength.

**On the k=5 bootstrap degeneracy:** Prof. Rex and Prof. Pax are absolutely right that k=5 gives only 6 discrete pass@1 values. But here's the constructive reframe: this is already the constraint of the existing experimental infrastructure from Run 3, where k=5 solutions were generated for 542 problems across 3 models. Rather than pretending k=5 yields perfect difficulty stratification, we declare the threshold design explicitly: hard tier = 0/5 passes (pass@1 = 0.0), easy tier = ≥3/5 pass (pass@1 ≥ 0.6). The Austin et al. MBPP methodology [Austin et al., 2021] itself uses temperature=0.5 with 80 samples — we operate at smaller k as a pilot. The contribution is: "given k=5 as a practical first-pass design, what is the ΔECE signal?" This is transparent and valid.

**On the base-rate confound (Prof. Rex's regression):** This is an excellent control to add. We *want* to run: ECE_i ~ Difficulty_i + Accuracy_i. If β₁ survives controlling for accuracy, the asymmetry is genuine metacognitive failure. If not, we report that calibration error is fully mediated by accuracy — also a novel finding for code verification. We add this as Prediction P3 (sensitivity analysis): "ΔECE persists after controlling for average tier accuracy." This turns a potential weakness into a pre-registered robustness check.

**On prompt brittleness:** Compare zero-shot P(True) vs. 2-shot P(True) calibration format on a 50-problem holdout. If ΔECE patterns are consistent across protocols, we've demonstrated robustness. If not, we've identified elicitation as a key variable — also publishable.

**On oracle noise:** Using EvalPlus augmented tests (already available) for ground truth is already the plan. The infrastructure is there from Run 3. We explicitly use EvalPlus's augmented test suite rather than vanilla tests.

The hypothesis that survives this discussion: **"Under k=5 bootstrap difficulty stratification with EvalPlus oracle ground truth, ΔECE = ECE(hard) − ECE(easy) is significantly positive (p < 0.05) across 3 LLM families tested on HumanEval+/MBPP+, even after controlling for average tier accuracy."**

**Key Points:**
- k=5 limitation becomes transparent design choice; explicitly state "pilot difficulty stratification" rather than hiding the constraint
- Prof. Rex's regression control (ECE ~ Difficulty + Accuracy) becomes Prediction P3 — a robustness check generating publishable findings regardless of sign
- All concerns addressable within existing Run 3 infrastructure; no new data collection required

---
### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Let us separate enthusiasm from evidence. The central claim is that ΔECE = ECE(hard) − ECE(easy) is significantly positive and reflects a structural metacognitive asymmetry. The evidence will only support this if we define, in advance, what would *disconfirm* it.

First, we must adopt the formal ECE definition from [Guo et al., 2017]:
ECE = Σ (|B_m|/n) × |acc(B_m) − conf(B_m)|

with a fixed bin count M across tiers. I recommend pre-registering M=15 and reporting both ECE and MCE. A necessary falsification condition: if ΔECE ≤ 0 in two of three model families under the EvalPlus oracle, the asymmetry hypothesis fails.

On the k=5 bootstrap: I accept it as a pilot stratification *only if* we quantify mis-tiering risk. Perform a beta-binomial uncertainty analysis per problem and compute the probability that a "hard" (0/5) item actually has p>0.3. If more than 20% of items exceed this threshold in posterior mass, the tier definition is too noisy to support mechanistic claims. Alternatively, regress calibration error continuously against empirical pass rate. The hypothesis then becomes: calibration error increases monotonically as pass@1 decreases.

The base-rate confound must be addressed rigorously. I endorse the regression: ECE_i = β₀ + β₁ × Difficulty_i + β₂ × Accuracy_i + ε_i. The asymmetry hypothesis survives only if β₁ > 0 with p < 0.05 after controlling for accuracy. A permutation test shuffling difficulty labels within accuracy strata strengthens the claim further.

Finally, temperature scaling must be diagnostic. Apply temperature scaling separately within easy and hard tiers using a held-out validation set. If a single temperature T fitted on validation data collapses ΔECE toward zero, then miscalibration is purely global. If ΔECE remains after optimal temperature scaling, the miscalibration is difficulty-dependent and not correctable by a global logit rescaling — a crisp mechanistic finding.

**Key Points:**
- Pre-register M=15 binning, report ECE and MCE, define explicit falsification criteria for ΔECE
- Test whether ΔECE survives regression controls for base accuracy and permutation baselines
- Use temperature scaling as a mechanistic probe: if a single T removes ΔECE, asymmetry is not structural

---
### Exchange 9

🔭 **Dr. Nova** (Creative Novelty Explorer):

🔬 Prof. Vera is building an excellent experiment design, and NOW we're getting somewhere! But let me add a creative layer that transforms this from a measurement study into something genuinely paradigm-shifting.

The Chen et al. (2021) HumanEval Methodology section uses a **pass@k unbiased estimator** from 200 samples per problem — specifically designed to get reliable difficulty estimates at scale. This is key: our k=5 limitation is an infrastructure choice, not a fundamental barrier. The unbiased estimator works even with k=5 if we acknowledge variance bounds.

**What if we reframe the entire research question around the SHAPE of the calibration curve?** Instead of asking only "is ΔECE positive?", we ask "what is the calibration curve's geometry as a function of difficulty?" Dr. Sage mentioned a possible phase transition at pass@1 ≈ 0.3. I propose something elegant: a **calibration-difficulty surface** — ECE as a function of continuous pass@1 — for each model. This surface tells us: (1) Does calibration degrade linearly or catastrophically with difficulty? (2) Is there a "sweet spot" where LLM confidence is reliable? (3) Do code-specialized models have different surface topography?

This reframing makes the hypothesis multi-dimensional and actionable for VerifAI practitioners: "use LLM confidence when pass@1 > 0.5 (ECE < 0.1), switch to formal oracle when pass@1 < 0.3 (ECE > 0.3)." This is a *decision boundary*, not just a p-value.

The novelty claim is now stronger: while Kadavath 2022 showed P(True) calibration in factual Q&A, we discover the **difficulty-calibration surface topology** for code verification — a concept that doesn't exist in the prior literature for any task type.

**Key Points:**
- Reframe from binary ΔECE test to continuous calibration-difficulty surface — captures geometry, not just direction
- Chen et al.'s unbiased pass@k estimator validates k=5 as a pilot while motivating follow-up with larger k
- Decision boundary interpretation transforms the finding into an actionable VerifAI deployment rule

---
### Exchange 10

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Now we're finally asking sharper questions. But here's where this can still fall apart.

First, on the "calibration-difficulty surface": with only 0/5, 1/5, …, 5/5 empirical pass rates, your "continuous" surface is actually six lattice points with huge variance. Chen et al.'s unbiased pass@k estimator assumes large sample counts to stabilize difficulty; with k=5, posterior variance over true pass probability is enormous. If you're going to fit splines or segmented regressions, I want errors-in-variables regression to account for measurement noise. Otherwise, your "phase transition at 0.3" is just binomial noise dressed up as topology.

Second, on elicitation sensitivity: Kadavath et al. (2022) showed calibration depends on format and aggregation — presenting multiple samples improved calibration, and training a value head for P(IK) further improved it. So here's my demand: for each difficulty level, estimate ECE under (a) single-sample P(True), (b) multi-sample aggregation, and (c) temperature-scaled logits fitted globally. If ΔECE disappears under aggregation, your "difficulty-dependent metacognition" is just high-variance introspection under low-accuracy regimes.

Third, your base-rate control needs to go deeper. ECE is mechanically coupled to accuracy: when accuracy drops, the optimal calibrated confidence drops, and deviations inflate absolute error. I want a simulation baseline: take each tier, assume the model outputs a constant confidence equal to its empirical accuracy in that tier, compute the "base-rate-only" ECE. If hard-tier ECE exceeds its baseline significantly more than easy-tier does, you've demonstrated excess miscalibration beyond accuracy effects.

Finally, temperature scaling as a mechanistic probe: if you need *tier-specific* temperatures to fix calibration (rather than a single global T), you have evidence of difficulty-conditioned logit distortion. Pre-register that criterion.

**Key Points:**
- k=5 induces high uncertainty in difficulty; require posterior-aware modeling before claiming nonlinear "surfaces"
- Compare observed ECE against a base-rate-only calibration baseline to rule out mechanical accuracy effects
- Demonstrate ΔECE persists after multi-sample aggregation and global temperature scaling

---
### Exchange 11

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me be direct about what's technically feasible given the existing Run 3 infrastructure — and what Prof. Rex's demands actually require.

The Guo et al. (2017) ECE formulation is mathematically clean: ECE = Σ (|B_m|/n) × |acc(B_m) − conf(B_m)| with M=15 equal-width bins. This is fully implementable with `torchmetrics.CalibrationError` or a 10-line manual implementation. Temperature scaling is also trivially implementable: fit a single scalar T on a validation split by minimizing NLL, then rescale all logits — Guo et al. showed this reduces ECE from 12.67% to 0.96% on CIFAR-100. All technical questions are answerable. The statistical questions require careful design.

Prof. Rex's "errors-in-variables regression" is technically sound but requires infrastructure not currently available. The practically feasible version: compute ECE at each of the 6 discrete pass@1 levels (0.0, 0.2, 0.4, 0.6, 0.8, 1.0) and plot the 6-point calibration-difficulty curve with bootstrap confidence intervals. This is not a continuous surface — it's 6 data points with error bars. Honest and defensible.

On the base-rate baseline: for each tier, compute "constant-confidence baseline ECE" where confidence = tier accuracy. Compare to observed ECE. If observed ECE >> baseline in hard tier but not in easy tier, that's structural miscalibration. Approximately 20 lines of NumPy code — fully feasible.

On temperature scaling: apply a single global T fitted on 20% holdout, then recompute per-tier ECE. If ΔECE persists, we have difficulty-conditioned miscalibration. If it collapses, global overconfidence explains everything. Either result is publishable.

My verdict: the experimental design is **technically sound** with three clear components — (1) tier-stratified ECE with M=15 binning, (2) base-rate baseline comparison, (3) temperature scaling diagnostic. Each is implementable with existing Run 3 code with minimal modification.

**Key Points:**
- ECE computation with M=15 bins and temperature scaling are technically trivial — no feasibility concerns
- 6-point calibration-difficulty curve with bootstrap CIs is honest and defensible given k=5 infrastructure
- Base-rate baseline comparison is the key discriminator: if hard-tier ECE >> baseline, the effect is structural

---
### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

⚙️ Prof. Pax has defined the technically feasible version, and that's a meaningful improvement. Let me now state what this hypothesis needs to claim — and what it should NOT claim — given these constraints.

What it CAN claim: "Under k=5 pilot difficulty stratification with EvalPlus oracle and M=15 ECE binning, we observe whether ΔECE = ECE(hard) − ECE(easy) > 0, controlling for base-rate accuracy via a constant-confidence baseline comparison and testing persistence after global temperature scaling." This is empirical, bounded, and testable with existing infrastructure.

What it CANNOT claim without further evidence: "LLMs exhibit structural metacognitive asymmetry" — this requires more than k=5 stratification and three models. The architecture-specialization comparison (Llama3 vs. DeepSeek-Coder vs. CodeLlama) remains exploratory, not confirmatory, given N=1 per category.

Here's what would convince me the study is publishable regardless of outcome: if the paper frames the main contribution as (1) methodology for self-contained difficulty stratification and (2) first empirical calibration profile for code verification by difficulty, rather than as a hypothesis test about "structural metacognition." The latter is overselling. The former is a genuine measurement contribution. Pre-register the falsification criterion: ΔECE ≤ 0 in ≥2/3 model families = null result. Then report honestly. That's science.

**Key Points:**
- Frame as measurement study, not metacognition proof; claim empirical calibration profile, not structural asymmetry
- Pre-register falsification criterion: ΔECE ≤ 0 in ≥2/3 model families = null result
- Architecture-specialization comparison is exploratory only; do not overclaim based on N=1 per category

---
### Exchange 13

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex makes a crucial distinction, and I'm actually delighted by it! Reframing this as a **measurement study** rather than a "structural metacognition" claim is NOT a downgrade — it's an UPGRADE in novelty.

The most impactful papers in the calibration literature (Guo et al. 2017 being the prime example) are fundamentally *measurement papers*. They discovered that modern neural networks are poorly calibrated — a finding that seemed obvious in retrospect but had never been systematically measured. Our contribution is exactly analogous: we are the FIRST to measure the calibration profile of LLMs as code verifiers, stratified by difficulty. This framing is actually *stronger* than "we prove structural metacognitive asymmetry" because: (1) it's falsifiable in a clean way, (2) the contribution is durable regardless of ΔECE sign, and (3) it opens follow-up work in any direction.

The creative contribution I want to preserve: the **6-point calibration-difficulty curve** per model (ECE at pass@1 = 0.0, 0.2, 0.4, 0.6, 0.8, 1.0 with bootstrap CIs). This is genuinely novel — a calibration "fingerprint" for each LLM on code verification. If code-specialized models show different curve shapes than general-purpose models, THAT is a publishable architectural finding.

The core statement that has emerged: **"We provide the first empirical calibration profile of LLM code verifiers stratified by self-contained difficulty bootstrapped from own pass@1, revealing whether P(True) confidence degrades with difficulty and informing VerifAI pipeline design."**

**Key Points:**
- Measurement paper framing is stronger than structural claim — analogous to Guo 2017's position in calibration literature
- 6-point calibration-difficulty curve per model is a novel "calibration fingerprint" even with k=5 granularity
- Core contribution: first empirical calibration profile for code verification by difficulty — publishable regardless of ΔECE sign

---
### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect):

I am satisfied with the reframing as a measurement study. That brings us into scientifically defensible territory. However, measurement papers must be especially precise about what would falsify their central claim. The core empirical statement now appears to be: *ECE varies systematically with pass@1-defined difficulty, beyond what is mechanically induced by accuracy differences.*

The evidence will suggest support only if two criteria are met: (1) ΔECE = ECE(hard) − ECE(easy) is positive with bootstrap 95% CIs excluding zero, and (2) this excess persists relative to a constant-confidence baseline within each tier. For each tier t, define a null model that outputs confidence equal to empirical accuracy a_t. Under the Guo et al. formulation [Guo et al., 2017], this produces near-zero calibration error in expectation. The observed ECE_t must be compared to this tier-specific null via paired bootstrap over problems. What result would disprove the structural claim? If ECE_t − ECE^null_t is statistically indistinguishable across tiers, then the apparent degradation is purely base-rate coupling.

On temperature scaling: Guo et al. (2017) demonstrate that a single scalar T often reduces ECE dramatically (e.g., CIFAR-100 from 12.67% to 0.96%). Therefore, your pre-registered mechanistic probe must be sharp. The falsification criterion: if global temperature scaling reduces ΔECE to within bootstrap noise of zero, then the effect is consistent with uniform logit overconfidence rather than difficulty-conditioned distortion. Only if tier-specific temperatures yield significantly better NLL than a global T, assessed via likelihood ratio test on validation data, do we have evidence for difficulty-dependent calibration structure.

A further confound: binning sensitivity. ECE with fixed M=15 bins can introduce bias when sample counts per bin are small. Report both ECE and MCE, and perform a sensitivity analysis over M ∈ {10,15,20}. Pre-register a quantitative threshold: ΔECE ≥ 3 percentage points in at least 2/3 model families, with CI exclusion of zero, after global temperature scaling and baseline subtraction. Without such thresholds, interpretation becomes narrative.

*If these criteria are met, I will say: This meets my standards.*

**Key Points:**
- Define falsification explicitly: ΔECE must exceed tier-specific null baselines with CIs excluding zero
- Use global temperature scaling as mechanistic probe; collapse of ΔECE after scaling falsifies structural claims
- Conduct binning sensitivity analyses (ECE/MCE, varying M ∈ {10,15,20}) to ensure robustness

---
### Exchange 15

🎯 **Dr. Sage** (Research Impact Evaluator):

🔬 Prof. Vera has now articulated a rigorous falsification framework, and I want to establish why this is significant regardless of outcome.

The Austin et al. (2021) MBPP paper opens with a key motivation: despite rapid progress in code synthesis, "significant gaps remain, especially related to the models' semantic understanding of code and their ability to handle more complex programming tasks effectively." They explicitly call for future work to bridge these gaps. Our calibration study is directly responsive — but at the meta-level: we measure not just *whether* models solve code tasks, but whether they *know when they might fail*.

The significance structure is now fully mature from this discussion:

**Primary significance:** First empirical measurement of ECE stratified by self-contained difficulty for code verification using P(True) logprob elicitation — measuring a gap explicitly identified in calibration surveys (Liu et al. 2025: "ECE for LLMs on code tasks is an open challenge").

**Secondary significance:** Prof. Vera's mechanistic probe (global T vs. tier-specific T) creates a novel contribution: the first test of whether code verification miscalibration is globally correctable (uniform overconfidence) or difficulty-conditioned (structural). This distinction matters for VerifAI practitioners — the former suggests cheap post-hoc calibration suffices, the latter mandates formal oracle integration.

**Practical significance:** The 6-point calibration-difficulty curve provides actionable decision thresholds for VerifAI pipeline designers. Austin et al.'s finding that model performance scales log-linearly with size suggests calibration curves might also reveal architectural signatures — a publishable secondary finding.

The field needs this measurement. If ΔECE > 0: VerifAI must integrate formal execution for hard code. If ΔECE ≈ 0: cheap LLM confidence suffices as a soft verifier. Either finding shapes the next 5 years of VerifAI pipeline design.

**Key Points:**
- Significance holds in both ΔECE directions — each outcome generates distinct, actionable VerifAI design implications
- Prof. Vera's global-T vs. tier-specific-T test is a secondary novel contribution on calibration correctability
- Austin et al. explicitly calls for understanding model limitations on complex tasks — our calibration measurement directly answers this at the meta-level

---

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The "calibration-difficulty fingerprint" framing is genuinely novel — analogous to how Guo et al. (2017) introduced ECE as a measurement tool for neural networks, we introduce the first difficulty-stratified calibration profile for LLM code verifiers. The self-contained bootstrap methodology is an original methodological contribution. The 6-point calibration-difficulty curve per model is publishable as a new measurement paradigm regardless of sign of ΔECE.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** After rigorous discussion, the hypothesis is now clearly falsifiable. Pre-registered criteria include: ΔECE ≥ 3pp in ≥2/3 model families with CI exclusion of zero, persistence after tier-specific null-baseline subtraction, and persistence after global temperature scaling. Multiple quantitative falsification paths are defined. This meets my standards for scientific rigor.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** This is the first systematic measurement of P(True) calibration stratified by self-contained difficulty for code verification — directly addressing an open challenge identified in recent surveys (Liu et al. 2025). Significance holds in both ΔECE directions: positive ΔECE mandates formal oracles in hard-problem VerifAI pipelines; near-zero ΔECE validates LLM confidence as a cheap soft verifier. Either outcome generates actionable design implications for VerifAI practitioners.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** The experimental design is technically sound throughout. ECE computation with M=15 bins, temperature scaling, and base-rate baseline comparison are all implementable with existing Run 3 infrastructure (minimal code changes). The 6-point calibration curve with bootstrap CIs is honest about k=5 granularity. No fundamental technical barriers exist — the mechanism is scientifically valid.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion has converged on a rigorous measurement study with the following core claim: **When LLMs predict code correctness via P(True) logprob elicitation on HumanEval+/MBPP+, their Expected Calibration Error (ECE) varies systematically with pass@1-bootstrapped difficulty tiers, beyond what is mechanically induced by accuracy differences, revealing the first empirical calibration-difficulty fingerprint for LLM code verifiers.**

The key methodological contributions: (1) self-contained difficulty stratification (hard = pass@1 = 0.0, easy = pass@1 ≥ 0.6, from own k=5 solutions — zero external dependency), (2) 6-point calibration-difficulty curve per model with bootstrap CIs, (3) base-rate null-baseline comparison to isolate structural miscalibration, (4) global vs. tier-specific temperature scaling as a mechanistic probe for whether miscalibration is globally correctable (uniform overconfidence) or difficulty-conditioned (structural).

The experimental design uses existing validated Run 3 infrastructure: EvalPlus augmented tests as correctness oracle, HumanEval+ (164) + MBPP+ (378) = 542 problems, 3 LLM families (Llama3-8B, CodeLlama-7B, DeepSeek-Coder-6.7B), M=15 ECE bins, bootstrap confidence intervals. All tests are pre-registered. The primary prediction is that ΔECE = ECE(hard) − ECE(easy) > 0, with secondary predictions on temperature scaling behavior and architecture comparison.

This contribution directly addresses the VerifAI workshop theme "AI as verifiers" by providing the first data-driven answer to: when can we trust LLM confidence for code verification?

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- k=5 bootstrap produces only 6 discrete pass@1 values; difficulty stratification is coarse; must acknowledge as "pilot methodology" throughout
- Three-model architecture comparison is exploratory only (N=1 per category); code-specialization claims must be hedged
- Base-rate confound must be controlled explicitly via tier-specific null baselines, not just regression
- **Mitigation Strategy:** Pre-register all controls (null baseline comparison, temperature scaling probe, M-sensitivity analysis), explicitly label architecture comparison as exploratory, and frame paper as measurement study rather than hypothesis test about structural metacognition. If these controls are included, the study is defensible at a top venue.

