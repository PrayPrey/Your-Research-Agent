# Phase 2A Discussion Log
## Initialized: 2026-03-15T15:16:00
## Workflow: phase2a-dialogue v10.0.0
## Architecture: Self-Contained Tikitaka Loop
## Execution Mode: UNATTENDED

---

## BRIEFING CONTEXT

### Research Gap Selected
**Gap ID:** gap-1
**Title:** Ratio vs Binary Reward Comparison Under Partial-Tractability GRPO Training
**Priority:** HIGH + PRIMARY
**Relevance:** CRITICAL — directly blocks answering the main research question

### Research Question
In GRPO-based RLEF for code generation with Qwen2.5-Coder-7B-Instruct on APPS introductory problems (difficulty=0, empirically filtered to S_term ∈ [0.3, 0.55] via pass@8 prescreening), does ratio reward (R_ratio = k_pass/k_total) reduce the zero-reward fraction (ZRF) by ≥20% and improve gradient SNR by ≥1.5× compared to binary reward (R_binary), in the first 25% of training steps?

### Failure Context (5 Prior Failures — ROUTE_TO_0)
This research direction was redesigned after 5 Phase 4 failures of hypothesis h-e1:
1. **S_term > 0.85 completely intractable**: Competition/interview APPS problems yield k_pass=0 for ALL rollouts with Qwen2.5-Coder-7B. R_ratio ≡ R_binary ≡ 0 — the reward distinction was mathematically vacuous.
2. **max_completion_length=512 too short**: Competition problems require 100–400+ lines. All completions truncated.
3. **Prescreening conflated with GRPO training**: EXISTENCE hypothesis (does k_pass>0 exist?) was incorrectly evaluated using GRPO ZRF/SNR gates.
4. **S_term from category labels, not empirical**: Labels (competition=0.95) not calibrated to actual model pass rates.
5. **Cascade failure**: h-m1, h-m2, h-m3, h-c1 all CASCADE_FAILED.

**New Direction:** S_term ∈ [0.3, 0.55] on APPS introductory (difficulty=0), with decoupled prescreening (pass@8 inference, max_new_tokens=1024) before GRPO training. Existing infrastructure (TRL v0.29.0, SFT checkpoint at h-e1/code/sft_checkpoint/) is reusable.

### Available Papers (6 prepared)
- **P1**: DeepSeekMath (Shao et al., 2024) — arXiv 2402.03300 — Introduces GRPO algorithm; 4955 citations
- **P2**: GHPO (Liu et al., 2025) — arXiv 2507.10628 — Capacity-difficulty mismatch → sparse rewards in GRPO; directly relevant
- **P3**: DRIVE (Zhu et al., 2025) — arXiv 2511.06307 — Difficulty-aware curriculum for GRPO competitive code
- **P4**: PPOCoder (Shojaee et al., 2023) — arXiv 2301.13816 — Binary execution reward for RL code generation
- **P5**: APPS Benchmark (Hendrycks et al., 2021) — arXiv 2105.09938 — 10k problems, difficulty tiers, pass@k evaluation
- **P6**: Process-RL Code (Ye et al., 2025) — arXiv 2502.01715 — Process-level reward granularity for code RL

### Feasibility Constraints (MANDATORY)
**REJECT** ideas requiring: new benchmarks, rubrics, synthetic/generated data, human evaluation/annotation.
**ACCEPT** only hypotheses testable with existing APPS dataset, existing model (Qwen2.5-Coder-7B-Instruct + SFT checkpoint), and automated pass@k evaluation.

---

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we're looking at this backwards? Everyone in the GRPO-for-code literature — PPOCoder, DRIVE, G2RPO-A — treats binary execution reward as the *natural* baseline, the default. But I want to challenge that assumption. What's the *informational geometry* of these two reward functions in the partial-tractability regime?

Here's the key insight: R_binary is a **clipping** operation on k_pass. When k_pass ∈ {1,2,3,4,5,6,7} out of k_total=8, R_binary treats ALL of these identically — reward 1. But R_ratio = k_pass/k_total preserves the full ordinal structure: 1/8 ≠ 4/8 ≠ 7/8. The question is whether GRPO's advantage normalization can *actually use* this richer structure.

GHPO [Liu et al., 2025] is fascinating here — they explicitly identify capacity-difficulty mismatch as why GRPO stalls, with sparse rewards the primary symptom. But their solution is to inject guidance (hints) rather than reshape the reward. What if reward reshaping from binary → ratio is a *lighter-weight alternative* requiring no oracle hints? The GRPO advantage A_i = (r_i - mean(r)) / std(r) uses WITHIN-GROUP variance. R_ratio increases this variance when rollouts have heterogeneous k_pass values — that's the core mechanism.

The novel mechanism I propose: R_ratio's benefit is **conditional on within-group diversity of partial success** — it only matters when 2+ rollouts have DIFFERENT k_pass values. This explains why S_term ∈ [0.3, 0.55] is the sweet spot: problems hard enough that not all rollouts succeed but tractable enough that different rollouts achieve different partial success counts. GRPO learns WHICH generation styles produce better partial solutions, not just that some succeed.

**Key Points:**
- R_ratio's core advantage is within-group variance amplification from heterogeneous partial rollout success
- This is more precise than "non-zero gradients": graded policy learning via graded advantages
- The prescreening gate S_term ∈ [0.3, 0.55] naturally maximizes rollout k_pass diversity
- Prediction: ZRF reduction from R_ratio should correlate with Var(k_pass across rollouts) — directly measurable

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Your central claim is precise enough to test: *R_ratio improves GRPO only when there is within-group heterogeneity in k_pass, because advantage normalization can exploit graded variance.* The evidence suggests this is plausible given GRPO's formulation. In DeepSeekMath, GRPO computes advantages from group-relative scores without a critic [DeepSeekMath, 2024]. Therefore, the *only* learning signal is the within-group dispersion of rewards. If R_binary collapses {1,…,k_total} into a single value, then for groups where all rollouts pass at least one test, the standard deviation is zero and the gradient vanishes. That is a clear, mechanistic prediction.

However, we must formalize the falsifiable core. Your hypothesis implies a quantitative relationship: ΔPerformance(R_ratio - R_binary) ∝ E[Var(k_pass | group)]. What would disprove this? If we observe substantial gains from R_ratio in regimes where within-group Var(k_pass)=0 (e.g., all rollouts either pass all tests or fail all tests identically), then your mechanism is incomplete or incorrect. Conversely, if we artificially increase within-group k_pass variance — holding mean pass rate constant — and performance does *not* improve under R_ratio relative to binary, the variance-amplification story fails.

I propose three controlled experiments. First, a *variance-stratified evaluation*: bin training batches by empirical Var(k_pass) across rollouts and measure per-bin policy improvement rate. The hypothesis predicts monotonic improvement of R_ratio over R_binary as variance increases, with a crossover near zero variance. Second, a check against the APPS benchmark data: Hendrycks et al. [2021] report that GPT-Neo achieves ~15% test case average on introductory problems — this means *heterogeneous partial success is already documented at the introductory level*, which is precisely the variance we need. Third, an adversarial homogenization condition: if all rollouts within a group receive identical k_pass despite different code paths, does R_ratio's advantage disappear? If not, some other signal is driving learning.

There are confounds. Higher within-group variance from R_ratio can destabilize training unless learning rates are adapted — recall DeepSeekMath's carefully tuned AdamW schedule [DeepSeekMath, 2024]. Thus, performance gains could stem from altered gradient magnitudes rather than informational geometry per se. We must log effective step norms and KL divergence per update to separate "more information" from "larger updates."

**Key Points:**
- The hypothesis is falsifiable: ΔPerformance(R_ratio - R_binary) ∝ E[Var(k_pass | group)] — testable via batch stratification
- APPS benchmark data [Hendrycks et al., 2021] already confirms heterogeneous partial success at introductory level (~15% test case average for GPT-Neo), validating that the required variance condition exists
- Controlled confounds needed: log gradient step norms and KL divergence to separate information richness from optimization instability

---

### Exchange 3

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Let me push on both of you. The variance-amplification mechanism is elegant, but here's where it breaks down — and the APPS benchmark data [Hendrycks et al., 2021] is actually the problem, not just the solution.

Prof. Vera points to GPT-Neo achieving ~15% test case average on introductory problems as evidence of heterogeneous partial success. But look at WHAT that actually means. APPS evaluates via "Test Case Average" — the fraction of individual test cases passed, averaged across problems. A 15% test case average on introductory problems means: on average, a solution passes 15% of the individual test cases of each problem. This is NOT the same as k_pass/k_total for the GRPO rollout. In GRPO, k_pass = number of rollouts (whole solutions) that pass ALL test cases, not the fraction of test cases that a single solution passes. Dr. Nova's variance mechanism assumes we're measuring rollout-level pass/fail diversity, but the APPS "Test Case Average" measures token-level test case fraction within a single solution.

Here's the critical question: will Qwen2.5-Coder-7B + SFT checkpoint actually achieve *rollout-level* partial success (k_pass ∈ {1,...,7} out of 8) on APPS introductory problems at S_term ∈ [0.3, 0.55]? The prescreening tells us fraction(k_pass ≥ 1) ≥ 10%. But fraction(k_pass ≥ 1) could be almost entirely concentrated at k_pass=1, with k_pass ∈ {2,...,7} being extremely rare. In that case, within-group variance of k_pass for most training batches is low: most groups have {0,...,0,1,...} or {0,...,0}. The "sweet spot" for variance would require problems where 2-5 of 8 rollouts succeed, which is a much stronger condition than fraction(k_pass ≥ 1) ≥ 10%.

What would convince me? The prescreening data needs to show the *distribution* of k_pass, not just fraction(k_pass ≥ 1). Specifically: we need E[Var(k_pass across 8 rollouts | k_pass > 0)] > 0 as a prerequisite for the variance mechanism to function. If k_pass is bimodal ({0,1} values only with no intermediate values), the within-group variance calculation under R_ratio yields the same advantages as R_binary up to a constant scaling. The hypothesis needs to be conditional on this distributional check.

A second concern: the ZRF metric is defined at the batch level (fraction of training steps with zero mean reward in the group). Under R_ratio, a group has mean reward = E[k_pass/k_total] across 8 rollouts. ZRF occurs iff ALL 8 rollouts have k_pass=0. This is identical for R_binary and R_ratio — ZRF is the same under both reward functions by definition! The ≥20% ZRF reduction claim as stated cannot be achieved by simply switching reward functions unless the training dynamics cause the policy to learn differently and thus increase the rate of k_pass > 0 rollouts over time. This is a training dynamics hypothesis, not a reward function property.

**Key Points:**
- APPS test-case average (~15% from GPT-Neo) measures intra-solution test coverage, NOT rollout-level diversity — these are different quantities
- Within-group k_pass variance is the true prerequisite: fraction(k_pass ≥ 1) ≥ 10% is insufficient to guarantee the variance mechanism
- ZRF is a function of ALL rollouts having k_pass=0 — this is identical under R_ratio and R_binary unless training dynamics differ; the ≥20% ZRF reduction must be a *downstream* training effect claim, not an immediate reward function property

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here: the core mechanism — variance amplification under GRPO — is *theoretically sound*, but only under stricter conditions than currently stated. In DeepSeekMath's GRPO, the advantage is computed from group-relative normalized rewards without a critic [DeepSeekMath, 2024]. That means the *only* learning signal is within-group dispersion. If reward variance is zero, the gradient is zero. That part is mathematically clean. So yes — in principle — replacing a clipped binary reward with a ratio reward can increase informational resolution **if and only if** it increases within-group variance of rewards.

Here's what worries me: we need to distinguish two levels of granularity. Dr. Nova's argument relies on diversity in *rollout-level partial success* (e.g., some solutions pass 3/8 tests, others 6/8). But as Prof. Rex correctly notes, in execution-based code RL, k_pass = number of rollouts passing ALL test cases. If in practice k_pass is almost always {0 or 1 full pass among 8 rollouts}, then R_ratio collapses to a near-linear rescaling of R_binary. In that regime, the mechanism cannot produce qualitatively new gradient directions — only magnitude changes.

Now, on the ZRF issue: Rex is right — ZRF (all rollouts zero reward) is definitionally identical under both reward functions at a fixed policy. Switching reward definitions does not alter whether all solutions fail. Any reduction in ZRF must arise from *training dynamics*: ratio reward must enable earlier policy differentiation, which then increases the probability of at least one partially correct rollout in future batches. That's a second-order effect. It is plausible — but it is not a direct property of the reward function. So the ≥20% ZRF reduction claim is a *dynamical hypothesis*, not an algebraic one. This is critically important for experimental design.

The feasibility hinge: does Qwen2.5-Coder-7B in S_term ∈ [0.3, 0.55] produce a multimodal distribution over test-case pass counts across 8 rollouts? The prerequisite check: log the histogram of per-rollout test-case pass counts during prescreening. If distributions are degenerate (mostly 0s with rare perfect solves), the mechanism collapses. PRLCoder [Ye et al., 2025] shows process supervision (+5.1% over outcome supervision on MBPP/HumanEval) — but they label at the *statement level*, not at the rollout-solution level. The analogy is instructive: R_ratio is a kind of "partial outcome supervision" that only has value when partial outcomes are diverse.

**Key Points:**
- R_ratio is theoretically sound for GRPO variance amplification, but only if rollout-level test-case pass counts are heterogeneous within groups (NOT just k_pass ∈ {0,1})
- ZRF reduction is a *dynamical* hypothesis: reward redefinition alone cannot reduce ZRF; early gradient differentiation must shift the policy to produce more partially-correct rollouts over training steps
- Process supervision literature [Ye et al., 2025] confirms reward granularity matters (+5.1%) — but granularity only helps when intermediate signals exist; prescreening must validate this prerequisite before GRPO training

---

### Exchange 5

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what does this *mean for the field*, even after Prof. Rex and Prof. Pax have correctly identified the mechanism gap?

Let me reframe what's happening here. The discussion has surfaced something important: there are actually TWO distinct hypotheses embedded in the original research question, and the field needs both.

**Hypothesis A (Mechanistic):** R_ratio increases GRPO training effectiveness *during* training by providing graded within-group advantage signals, which biases policy updates toward generation styles that partially satisfy test cases — leading to improved rollout diversity and ZRF reduction as a downstream training dynamic effect.

**Hypothesis B (Prescreening):** The pass@k prescreening protocol at S_term ∈ [0.3, 0.55] is a necessary and sufficient gate for ensuring that the GRPO training regime operates in the partial-tractability zone where ANY reward function (including R_binary) provides meaningful gradient signal.

The significance lies in their interaction. Process-RL Code [Ye et al., 2025] achieved +5.1% over outcome supervision — but on HumanEval/MBPP, which are much simpler than APPS introductory, AND required constructing a per-statement reward model. R_ratio is far simpler: no reward model training, no statement-level annotations, just a ratio of test cases. If R_ratio captures even 30-50% of the benefit of process supervision at zero additional labeling cost, that's a genuinely impactful result for the field.

The real contribution here is not "R_ratio > R_binary" as a binary comparison. It's: **"Prescreening-gated GRPO with R_ratio is a minimal-complexity intervention for the sparse-reward problem in RLEF code generation."** The counterfactual is GHPO's adaptive guidance — which requires an oracle hint generator — versus R_ratio, which requires only test case evaluation infrastructure that already exists. This matters because: (1) APPS test cases are already available, (2) no additional model or annotation is needed, (3) the mechanism is interpretable.

What the field needs to know: can the sparse-reward problem in GRPO-based code generation be addressed by a reward engineering choice rather than curriculum or guidance engineering? That's a clean research question with a clear answer from the proposed experiment. The significance scales if the answer is yes — because it changes how practitioners set up GRPO pipelines for code.

**Key Points:**
- Two distinct hypotheses need separation: (A) R_ratio enables graded advantage signals during training, and (B) prescreening at S_term ∈ [0.3, 0.55] ensures meaningful gradient signal exists
- The field significance is: prescreening-gated R_ratio vs prescreening-gated R_binary as a minimal-cost intervention for the ZRF/sparse-reward problem, compared to GHPO's oracle-guided approach
- Process-RL Code [Ye et al., 2025] proves reward granularity helps (+5.1% on MBPP/HumanEval) — R_ratio is the simplest granular reward that doesn't require a reward model, making the comparison scientifically clean and practically valuable

---

### Exchange 6

🔬 **Prof. Vera** (Rigorous Validation Architect):

We are converging, but the hypothesis must now be conditionally scoped with precision. The evidence suggests that under GRPO, the *only* source of gradient signal is within-group reward dispersion, because the baseline is computed from group scores rather than a learned critic [DeepSeekMath, 2024]. Therefore, any claim about R_ratio must reduce to a statement about how it alters the distribution of group-normalized rewards relative to R_binary. If reward vectors are affinely equivalent within each group, then the resulting normalized advantages are identical up to scale, and learning trajectories should not differ beyond step-size effects. That is the algebraic constraint.

Accordingly, I propose the following falsifiable, conditionally-scoped hypothesis:

**H1 (Variance-Conditional Efficacy):** R_ratio yields greater cumulative policy improvement than R_binary *if and only if* the expected within-group variance of per-rollout test-case pass fractions exceeds that of the binary full-pass indicator, and this variance is not degenerate to a {0,1}-only support.

This directly addresses Prof. Rex's distributional objection. We measure the empirical distribution of per-rollout test-case pass fractions *before* RL, at the SFT checkpoint. Let r_i^ratio = (# test cases passed)/(# total test cases) per rollout, and r_i^bin = 1[all test cases passed]. Compute, for each problem group of size G=8: ΔVar = Var(r_ratio 1:G) - Var(r_bin 1:G). The hypothesis predicts: if E[ΔVar] ≈ 0, then downstream performance differences should vanish. If E[ΔVar] > ε for some measurable threshold, R_ratio should outperform R_binary in cumulative reward gain and final pass@1.

On the ZRF issue — I agree with Prof. Rex and Prof. Pax: ZRF at a fixed policy is invariant to reward definition. Therefore, the ≥20% ZRF reduction must be reformulated as a *time-to-escape* prediction: there exists t* such that ZRF_ratio(t*) < 0.8 × ZRF_binary(t*) with identical initialization and hyperparameters. Crucially, we must log KL divergence per step and effective gradient norm to ensure any ZRF divergence is not merely due to larger step magnitudes under R_ratio.

PPOCoder [Shojaee et al., 2023] on APPS program synthesis achieved 17.77% pass rate across all levels using binary execution reward — this establishes that binary reward does produce learning signal on APPS. R_ratio's potential advantage is specifically in the partial-tractability regime where individual rollouts pass *some* but not *all* test cases — a regime PPOCoder didn't specifically analyze.

**Key Points:**
- Reformulated hypothesis: R_ratio helps only when E[Var(r_ratio) - Var(r_bin)] > 0; null ΔVar predicts null performance gap; this is the core testable claim
- ZRF reduction must be tested as a training-dynamics inequality over time with gradient norm controlled; it is NOT an instantaneous reward property
- PPOCoder [Shojaee et al., 2023] proves binary execution reward produces learning on APPS (17.77% pass) — R_ratio's advantage is conditional on within-group test-case pass fraction diversity

---

### Exchange 7

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can strengthen this by incorporating everything the discussion has uncovered — this is actually coalescing into a cleaner, stronger hypothesis than we started with!

Let me synthesize what's emerged. The original research question asked whether R_ratio reduces ZRF by ≥20% and improves gradient SNR by ≥1.5×. The discussion has revealed that this framing is slightly underspecified. Here's what I propose as the refined, strengthened hypothesis that addresses all major criticisms:

**The Core Claim (refined):** Under GRPO-based RLEF training on APPS introductory problems prescreened to S_term ∈ [0.3, 0.55], R_ratio (defined as fraction of test cases passed per rollout, not fraction of rollouts passing ALL test cases) increases within-group reward variance relative to R_binary, and this variance increase produces earlier ZRF escape and higher gradient SNR than R_binary under identical hyperparameters — *conditional on the within-group variance being non-degenerate*.

**Three key clarifications Prof. Rex and Prof. Pax forced:**
1. **R_ratio definition must be per-test-case fraction, not per-rollout all-pass fraction.** Specifically: R_ratio(rollout_i) = (# test cases passed by rollout_i) / (# total test cases). This is different from k_pass/k_total (# rollouts passing all tests). The reward is at the individual rollout level, measuring partial test-case coverage. This definition guarantees within-group variance exists whenever rollouts produce code that partially satisfies the test suite.

2. **ZRF reduction is a dynamical, not instantaneous effect.** PPOCoder [Shojaee et al., 2023] proved binary execution reward with PPO produces learning on APPS (17.77% pass), so the baseline is validated. R_ratio's advantage is specifically that it provides non-zero gradient even for rollouts that pass SOME test cases but not ALL — which is the exact regime at S_term ∈ [0.3, 0.55]. After prescreening confirms these rollouts exist, R_ratio should allow the policy to learn "better code" (more test cases passing) before it achieves "perfect code" (all test cases passing).

3. **The prescreening gate serves dual purposes:** (a) confirming partial tractability (fraction(k_pass ≥ 1) ≥ 10%), AND (b) confirming within-group test-case pass fraction variance (E[Var(r_ratio within group)] > 0). Both must be validated from the same prescreening run.

What would convince me this hypothesis is ready for Phase 2B: We have specific, falsifiable, measurable predictions. We have a clear causal mechanism (within-group variance amplification). We have an existing baseline (PPOCoder, R_binary). We have a feasibility argument (existing APPS, existing SFT checkpoint, existing TRL infrastructure). The only remaining uncertainty is empirical: does the prescreening data confirm within-group test-case pass diversity? That question can and should be answered by the prescreening protocol itself.

**Key Points:**
- R_ratio redefined at rollout level as fraction of test cases passed (not fraction of rollouts passing all tests) — this guarantees within-group variance exists whenever partial execution occurs
- The two-phase prescreening check validates both S_term tractability AND within-group variance before any GRPO training begins
- The hypothesis is now mechanistically precise, falsifiable, and experimentally tractable using existing infrastructure from PPOCoder and TRL GRPOTrainer baselines

---

### Exchange 8

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good — this is much sharper than where we started. But here's where this still breaks down if we're not careful.

First, the variance argument is necessary but not sufficient. You've now defined R_ratio(i) = (#tests_passed_i) / (#tests). Fine. That guarantees *potential* within-group variance whenever partial correctness exists. But GRPO doesn't use raw variance — it uses **group-normalized advantages**. If all rollouts cluster tightly (e.g., 0.0, 0.125, 0.125, 0.25, 0.25), your variance exists — but the signal-to-noise ratio of the *normalized* advantage may still be tiny. Show the expected magnitude of standardized advantage under realistic APPS pass-count histograms. Prescreening must log: (1) mean and variance of per-rollout pass fraction, (2) resulting normalized advantage distribution under GRPO, (3) effective gradient norm per update.

Second, I want to interrogate your implicit assumption about **test-case informativeness**. PPOCoder layered compiler feedback, AST matching, DFG semantic scores, and KL penalty [Shojaee et al., 2023] — dense structural signal — and still only reached 17.77% pass rate on APPS program synthesis. Ask yourself: are APPS test cases smooth with respect to semantic proximity? If passing 3/10 tests is weakly correlated with passing 4/10, ratio reward provides learning gradient. If instead failures are combinatorial (one logic branch flips many tests), ratio reward becomes jagged and misleading. Show empirical monotonicity: is Δ(pass fraction) positively correlated with future full-pass probability?

Third, the ZRF escape claim still smells under-specified. Binary reward under PPOCoder *also* produced learning on APPS, meaning full-pass events occurred. The real question: does R_ratio increase the *hazard rate* of first full-pass rollout per problem? Not ZRF percentage in isolation — time-to-first-success curves under matched KL and learning rate. If curves overlap within confidence intervals, the thesis reduces to step-size scaling.

Three-layer validation that would convince me: (1) E[ΔVar] > 0 AND standardized advantage magnitudes ≥1.3× under R_ratio; (2) monotonicity test: higher pass fraction at step t predicts higher probability of full pass at t+Δ; (3) hazard-rate comparison: statistically significant reduction in time-to-first-full-pass under identical KL budgets.

**Key Points:**
- Raw within-group variance is insufficient; show standardized advantage magnitude and gradient norm under GRPO to prove usability of signal
- Validate that partial test-case pass fraction is semantically monotonic toward full correctness — critical assumption not yet tested
- Replace vague ZRF claims with hazard-rate analysis of time-to-first-full-pass under matched KL constraints

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic about Prof. Rex's three-layer validation — it's scientifically rigorous but I need to check if it's actually implementable with the existing infrastructure.

The good news: all three of Prof. Rex's validation checks can be computed from data that's ALREADY generated by the prescreening run and the early GRPO training. Let me be concrete. Prescreening runs pass@8 inference (k=8, temperature=0.8). That gives us, per problem, 8 code completions. For each completion, we execute against test cases. Standard APPS evaluation returns (tests_passed, total_tests) per solution — that IS R_ratio per rollout. So E[ΔVar] computation is free from prescreening data. Standardized advantage distribution computation requires: compute group mean and std of R_ratio values, then normalize — this is what GRPO does internally, we just need to log it.

For the monotonicity test — this is the expensive one. We need to check whether higher per-rollout pass fraction predicts higher future full-pass probability. The simplest operationalization: from prescreening data, for each problem, plot the correlation between rollout_i pass fraction and whether that rollout passed ALL tests. This is computable from the prescreening outputs — it's just a correlation coefficient across the prescreened problem set. We don't need additional experiments. PRLCoder [Ye et al., 2025] explicitly demonstrates that per-statement pass/fail signals (generated via mutation testing) are semantically informative — their process supervision outperformed outcome supervision by +5.1% on MBPP. The analog is: if per-line execution signals are monotone, per-test-case pass fractions should be too.

For the hazard-rate comparison — this IS a training dynamics measurement, but it's computed from the training logs we'd generate anyway. Time-to-first-full-pass per problem is just: for each problem in the training set, at what training step did the policy first generate a solution with pass fraction = 1.0? This is loggable during GRPO training with zero additional overhead.

So here's my updated feasibility verdict: the hypothesis as refined by Dr. Ally and validated by Prof. Vera's H1 (Variance-Conditional Efficacy) is technically sound and measurably testable. The prescreening protocol generates evidence for E[ΔVar]. The GRPO training logs generate hazard-rate data. The tests are automatable. No new benchmarks. No human evaluation. Existing APPS test cases. Existing SFT checkpoint.

**Key Points:**
- All three of Prof. Rex's validation checks are computable from prescreening + GRPO training logs — no additional experiments or infrastructure required
- Monotonicity test uses prescreening data directly: correlation between per-rollout pass fraction and full-pass probability within the prescreened problem set
- Process supervision literature [Ye et al., 2025] provides empirical support that per-test-case signals are semantically informative (+5.1% on MBPP) — the monotonicity assumption is well-grounded

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Following up on the feasibility discussion — I want to address the remaining open issue: the **definition of gradient SNR** as a metric.

Prof. Vera and Prof. Rex have been clear about what we need to measure, but gradient SNR as used in the original research question hasn't been operationalized. Let me propose the most technically sound definition given the GRPO infrastructure.

In GRPO, the policy gradient is: ∇θ J ≈ (1/G) Σ_i A_i ∇θ log π_θ(o_i | q). The "gradient signal" is the mean of A_i ∇θ log π_θ across rollouts; the "noise" is the variance. A practical proxy: SNR = |E[A_i]| / std(A_i) per training step, where A_i = (r_i - mean(r)) / std(r) is the normalized advantage. Under R_binary, if the group has M successes out of G=8 rollouts: A_success = (1 - M/G) / sqrt(M/G × (1-M/G)) and A_failure = -(M/G) / sqrt(M/G × (1-M/G)). Under R_ratio, the A_i values are more spread and non-binary. The SNR under R_ratio should be higher when within-group variance of raw rewards is higher — this is precisely the E[ΔVar] condition.

**The key technical claim:** SNR_ratio / SNR_binary ≥ 1.5× is equivalent to: Var(r_ratio across group) / Var(r_binary across group) ≥ 1.5× in expectation, when both reward distributions have similar mean. This is testable from prescreening data alone — no GRPO training required for the initial SNR estimate.

**Key Points:**
- Gradient SNR operationalized as |E[A_i]| / std(A_i) per training step, or equivalently via within-group reward variance ratio
- The 1.5× SNR target translates to Var(r_ratio)/Var(r_binary) ≥ 1.5×, computable from prescreening statistics before any GRPO training
- This makes the ≥1.5× SNR criterion falsifiable and measurable without training infrastructure

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Now THAT's stronger! Prof. Pax has just given us the key insight that makes this hypothesis bulletproof from a measurement perspective.

The gradient SNR operationalization — Var(r_ratio across group) / Var(r_binary across group) ≥ 1.5× — is elegant because it: (1) is computable from prescreening data, (2) is algebraically grounded in GRPO's advantage normalization, (3) directly connects to the training dynamics hypothesis, and (4) provides a pre-training check that the ≥1.5× SNR criterion will be met.

Let me now propose the final hypothesis structure that I believe is ready for Phase 2B:

**Hypothesis (H-RatioReward-v1):**
Under GRPO-based RLEF training on APPS introductory problems prescreened to S_term ∈ [0.3, 0.55] with Qwen2.5-Coder-7B-Instruct + SFT checkpoint (max_new_tokens=1024):
- IF the prescreening run confirms E[Var(r_ratio within group)] / E[Var(r_binary within group)] ≥ 1.5× AND the within-group pass fraction distribution is non-degenerate (not purely binary {0,1})
- THEN during GRPO training: (a) the policy trained with R_ratio will show earlier ZRF escape (there exists training step t* where ZRF_ratio(t*) < 0.8 × ZRF_binary(t*)), (b) gradient SNR under R_ratio exceeds that under R_binary by ≥1.5× in the first 25% of training steps
- BECAUSE R_ratio preserves within-group reward heterogeneity that R_binary clips to {0,1}, enabling GRPO's advantage normalization to produce informative policy gradients at training steps where all rollouts have k_pass < k_total

**Why this is ready for Phase 2B:**
- Existence gate: prescreening confirms S_term ∈ [0.3, 0.55] problems satisfy partial tractability
- Mechanism gate: the Var(r_ratio)/Var(r_binary) ratio is the measurable causal mechanism
- Comparison: GRPO training comparison R_ratio vs R_binary under identical hyperparameters
- All measurable with existing APPS test cases, existing SFT checkpoint, existing TRL GRPOTrainer

**Key Points:**
- Full hypothesis framed as IF-precondition THEN-consequence BECAUSE-mechanism — all three testable
- Prescreening validates BOTH the tractability gate AND the variance condition before any expensive GRPO training
- The hypothesis is self-consistent across all six personas' requirements: novel (Dr. Nova), falsifiable (Prof. Vera), significant (Dr. Sage), technically sound (Prof. Pax), stress-tested (Prof. Rex), and strengthened (Dr. Ally)

---

### Exchange 12

🔬 **Prof. Vera** (Rigorous Validation Architect):

We are now close to a scientifically defensible hypothesis, but I want to tighten two logical gaps before I will consider this robust. First, the proposed proxy SNR = Var(r_ratio)/Var(r_binary) ≥ 1.5× requires careful interpretation under GRPO. In DeepSeekMath's formulation [Shao et al., 2024], what matters is the *covariance* between reward and ∇θ log πθ(o|q). If higher reward variance occurs on tokens with negligible policy gradient norm, the effective gradient SNR will not increase. What result would disprove the mechanism? If Var(r_ratio)/Var(r_binary) ≥ 1.5× but gradient SNR does *not* increase by ≥1.5×, the variance-based causal story fails.

Second, I remain cautious about monotonicity. We need *predictive monotonicity under policy improvement*: bin rollouts by pass fraction at step t; for each bin measure P(full pass within Δ updates | initial bin). The hypothesis predicts strict stochastic dominance. If curves overlap within confidence intervals, ratio reward may introduce misleading gradients.

Third, ZRF escape must be controlled: identical initialization, KL penalty, batch size G, learning rate schedule, and token budget. The falsifier: if time-to-first-full-pass survival curves under R_ratio and R_binary are statistically indistinguishable (log-rank test p > 0.05), the hazard-rate advantage does not exist. The APPS benchmark [Hendrycks et al., 2021] establishes that models can achieve partial success on introductory problems — this provides the empirical prior that monotonicity *should* hold on APPS introductory, but it must be confirmed experimentally.

Pre-register edge cases: problems with within-group std(r_ratio) < ε excluded from causal analysis to prevent null results being misattributed.

If ≥1.5× gradient SNR increase AND statistically significant hazard-rate reduction are both observed with these controls, then — *this meets my standards.*

**Key Points:**
- Full gradient SNR must be measured via covariance with policy gradients, not just reward variance
- Pre-register falsifiers: log-rank test for survival curves, gradient SNR threshold, low-variance problem exclusions
- APPS benchmark [Hendrycks et al., 2021] provides empirical prior for partial correctness at introductory level, but monotonicity must be confirmed

---

### Exchange 13

🎯 **Dr. Sage** (Research Impact Evaluator):

This matters because of what the field gets if the answer is yes. Let me be explicit.

APPS [Hendrycks et al., 2021] was explicitly designed to track progress in code generation over time. The authors conclude that models face increasing challenges with complex tasks while showing improvement in simpler ones — GPT-Neo at 15% test case average on introductory problems (2021). Qwen2.5-Coder-7B-Instruct in 2024-2025 should be considerably stronger, which is exactly why S_term ∈ [0.3, 0.55] is the right regime: it's where the model has meaningful but not trivial capability. The benchmark was designed for this kind of tracking.

What does the field get? Here is the research contribution stated precisely:

1. **The first empirical comparison of R_ratio vs R_binary under GRPO on a standard code benchmark (APPS)**, with controlled prescreening to ensure the experiment is in the partial-tractability regime where the comparison is meaningful. This fills Gap 1 from Phase 1 completely.

2. **A formal prescreening protocol** that prevents the kind of wasted experiments we saw in 5 prior runs — this is the "defensive research practice" contribution of Gap 2. Any future GRPO-for-code paper should cite this protocol.

3. **An operational definition of gradient SNR** as a diagnostic for reward function comparison in GRPO, which Prof. Pax and Prof. Vera have now fully specified. This fills Gap 3.

The significance claim: if R_ratio wins, practitioners should prescreening-gate their GRPO pipelines AND use ratio rewards. If R_ratio loses (ZRF escape curves overlap), then the field learns that binary reward is already optimal in the partial-tractability regime, and the research community should focus on other interventions (GHPO-style guidance, curriculum, etc.). Either outcome advances the field.

This is what good research looks like: clean comparisons with pre-registered falsifiers, in a regime where the comparison is interpretable. The APPS benchmark was built for this. Our SFT checkpoint is ready. Our infrastructure is proven (5 prior runs, all with ZRF=1.0 which was WRONG regime — now we're in the right regime).

**Key Points:**
- The research contribution is three-fold: (1) first controlled R_ratio vs R_binary comparison under GRPO on APPS, (2) formal prescreening protocol as a field best-practice contribution, (3) operational gradient SNR definition for reward function comparison
- Either result (R_ratio wins OR loses) advances the field — both outcomes eliminate uncertainty for future practitioners
- The APPS benchmark [Hendrycks et al., 2021] was designed precisely to track this kind of progress; using it in the partial-tractability regime completes its intended scientific purpose

---

### Exchange 14

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good. This is finally looking like something I can't dismiss in 30 seconds. But here's where this still breaks down.

The SNR equivalence claim — Var(r_ratio)/Var(r_binary) ≥ 1.5× implies SNR_ratio/SNR_binary ≥ 1.5× — is not guaranteed under GRPO. The effective signal is E[A_i ∇ log π], not just Var(r). If reward variance is driven by completions in low-gradient regions of the policy (near-deterministic decoding under SFT), the covariance collapses. We need to compute empirically: Cov(r_i, ||∇θ log π(o_i)||) over prescreened rollouts. If that covariance is not larger under R_ratio, the mechanism is cosmetic.

The advantage normalization subtlety matters: A_i is z-scored within group. In binary reward with M successes, A_success and A_failure already scale inversely with √(p(1-p)). Near p=0.5, binary reward *maximizes* post-normalization variance. So the 1.5× condition may only hold in skewed-p regimes. We need an analytic closed-form comparison: assume k_i ~ Binomial(T, q_i). Derive E[Var(r_ratio)] and E[Var(r_binary)] as functions of pass fraction p and test-case granularity T.

On ZRF escape survival curves: unit of analysis matters — problem-level or batch-level. If ZRF escape depends on rare prompts with high intrinsic solvability, the variance story is confounded by prompt heterogeneity. Stratify survival curves by initial pass-fraction bin per problem. PRLCoder [Ye et al., 2025] ran on MBPP/HumanEval — simpler than APPS. The statistical approach there was straightforward pass rate comparison. Our hazard-rate analysis is more rigorous and appropriate for the partial-tractability regime.

Four elements that would convince me: (1) analytic toy model showing parameter regions where Cov(r, ∇logπ)_ratio > 1.5× binary; (2) empirical prescreening evidence for covariance gap; (3) early-phase GRPO logs (first 10-20% steps) confirming measured gradient SNR aligns with prescreen prediction; (4) stratified survival curves showing stochastic dominance under R_ratio with log-rank p < 0.05.

**Key Points:**
- Reward variance alone is insufficient; the mechanism requires higher covariance between reward and policy gradient norm under R_ratio — empirically verifiable from prescreening
- Advantage normalization may erase variance gains at intermediate p; derive analytic conditions (Binomial(T, q) model) where ratio reward strictly dominates binary
- Pre-register early-phase, stratified survival diagnostics; use PRLCoder [Ye et al., 2025] MBPP/HumanEval as methodological precedent for pass-rate comparison framing

---

### Exchange 15

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Rex's final challenge — the Cov(r, ||∇logπ||) computation and the analytic Binomial(T, q) model — is the most technically demanding point. Let me assess feasibility honestly.

The covariance computation Cov(r_i, ||∇θ log π(o_i)||) requires computing per-rollout gradient norms during inference. This is feasible with Qwen2.5-Coder-7B on H100 NVL but will approximately double compute time for prescreening (need backward pass per rollout, not just forward). It is technically implementable but should be flagged as an additional compute requirement. It is NOT infeasible — it's just not free. PyTorch's autograd can compute this with a custom prescreening loop.

For the analytic Binomial(T, q) model: this is a clean theoretical exercise. Under GRPO group normalization, if rollout_i passes t_i out of T test cases, with t_i ~ Binomial(T, q_i): E[Var(r_ratio)] = (1/T²) × Σ_i E[t_i(T-t_i)/T] = q(1-q) for homogeneous q. E[Var(r_binary)] = p(1-p) where p = P(all T tests pass | q) = q^T. So ΔVar = q(1-q) - q^T(1-q^T). This is positive whenever q^T(1-q^T) < q(1-q), which holds whenever T > 1 and 0 < q < 1. In other words: R_ratio ALWAYS has higher within-group variance than R_binary under the Binomial model, for any p ∈ (0,1) and T > 1. The advantage normalization concern is valid but the variance gap in expectation is always positive — the question is magnitude, not sign.

For the advantage normalization at p=0.5 binary: Rex is right that binary reward maximizes variance at p=0.5. But at p=0.5 (M=4 successes per group of G=8), R_binary std = √(0.5×0.5) = 0.5, while R_ratio std (with T test cases) = √q(1-q) / T × something larger. The comparison depends on T (number of test cases per APPS problem). APPS introductory problems typically have T=5-30 test cases. At T=10, q=0.5 gives q(1-q) = 0.25, while q^T = 0.5^10 ≈ 0.001 ≈ 0. So p_binary ≈ 0 and Var(r_binary) ≈ 0, while Var(r_ratio) ≈ 0.25. R_ratio dominates strongly.

The theoretical analysis shows R_ratio dominates binary variance EXCEPT when q is close to 1.0 (problem nearly trivially solved) or 0.0 (completely intractable). The S_term ∈ [0.3, 0.55] prescreening gate is specifically designed to be in the regime where R_ratio dominates.

**Key Points:**
- Analytic Binomial(T, q) model confirms: E[Var(r_ratio)] > E[Var(r_binary)] for any T > 1 and 0 < q < 1; the sign is always positive, magnitude depends on T and q
- At typical APPS introductory test-case counts (T=5-30), R_ratio's variance advantage over R_binary is large in the partial-tractability regime (q ∈ [0.3, 0.6])
- Covariance computation (Cov(r, ||∇logπ||)) is technically feasible with one backward pass per rollout during prescreening — implementable on existing H100 NVL infrastructure

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The within-group variance amplification mechanism is a genuinely novel framing that reinterprets R_ratio vs R_binary comparison through GRPO's group-relative advantage normalization. No prior work (DRIVE, GHPO, PPOCoder) has framed the reward design question in terms of within-group reward heterogeneity under GRPO. The Binomial(T, q) analytic model confirming R_ratio's variance dominance is new to the literature.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis has explicit pre-registered falsifiers: (1) if Var(r_ratio)/Var(r_binary) ≥ 1.5× but gradient SNR does not increase, mechanism is cosmetic; (2) if log-rank survival curves overlap (p > 0.05), the ZRF escape claim fails; (3) if Cov(r, ||∇logπ||) is not larger under R_ratio, the informational advantage is illusory. All falsifiers are computable from prescreening + early training logs.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** The research resolves a clean empirical question (R_ratio vs R_binary under GRPO on APPS) that fills Gap 1 from Phase 1 completely, AND contributes a prescreening protocol (Gap 2) and gradient SNR definition (Gap 3) as field best-practices. Both possible outcomes (R_ratio wins or loses) advance the field by reducing uncertainty for future practitioners.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All required components exist: Qwen2.5-Coder-7B SFT checkpoint at h-e1/code/sft_checkpoint/, APPS introductory split via codeparrot/apps, TRL v0.29.0 GRPOTrainer. The analytic Binomial model confirms R_ratio's variance advantage is theoretically guaranteed in the prescreened regime. The covariance computation (backward pass per rollout) adds overhead but is implementable on H100 NVL.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The hypothesis that emerged from 15 exchanges of multi-perspective debate is ready for Phase 2B. Here is the complete statement:

**H-RatioReward-v1:** Under GRPO-based RLEF training on APPS introductory problems (difficulty=0) prescreened to S_term ∈ [0.3, 0.55] with Qwen2.5-Coder-7B-Instruct + SFT checkpoint (max_new_tokens=1024, temperature=0.8, k=8), if the prescreening run confirms E[Var(r_ratio within group)] / E[Var(r_binary within group)] ≥ 1.5× (analytically guaranteed by Binomial(T, q) model for typical APPS test-case counts T ∈ [5, 30]) and within-group pass fraction distribution is non-degenerate, then during GRPO training: (a) R_ratio will show earlier ZRF escape (there exists training step t* where ZRF_ratio(t*) < 0.8 × ZRF_binary(t*)) with log-rank p < 0.05 under matched hyperparameters, and (b) gradient SNR under R_ratio exceeds that under R_binary by ≥1.5× in the first 25% of training steps — BECAUSE R_ratio (defined as per-rollout fraction of test cases passed) preserves within-group reward heterogeneity that R_binary clips to {0,1}, enabling GRPO's group-relative advantage normalization to produce informative, graded policy gradients at training steps where all rollouts have k_pass < k_total.

The null hypothesis H0: there is no significant difference in ZRF trajectory or gradient SNR between R_ratio and R_binary on the prescreened APPS introductory subset (i.e., the Binomial(T, q) variance advantage does not translate to improved training dynamics). The experiment fills all three research gaps from Phase 1 simultaneously, requires no new benchmarks or human evaluation, and is executable with existing infrastructure.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- The Cov(r, ||∇logπ||) computation adds meaningful prescreening overhead; if resource-constrained, this diagnostic may need to be approximated or deferred to training-phase logging rather than prescreening phase
- The Binomial(T, q) model assumes independence between test cases; APPS test cases for a single problem may be correlated (e.g., if passing test 1 is a prerequisite for test 2), which could reduce the effective T and diminish the variance advantage — should be verified empirically
- Early-phase (first 25%) SNR advantage may not persist into later training as the policy shifts; the hypothesis should explicitly scope its claims to the first 25% of training steps only
- **Mitigation Strategy:** Pre-register all diagnostics (variance ratio, covariance, survival curves) in the Phase 2B experiment protocol; accept that gradient SNR and ZRF claims are scoped to the first 25% of training only; treat test-case correlation as an assumption to verify in prescreening data

EXCHANGE_EOF_EOF

