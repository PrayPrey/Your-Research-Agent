# Phase 2A Discussion Log
**Workflow:** phase2a-dialogue  
**Architecture:** Self-Contained Tikitaka Loop (Independent-Controller Ablation)  
**Execution Mode:** UNATTENDED  
**Date:** 2026-08-26  

---

## Briefing: Selected Research Gap

**Gap ID:** gap-1  
**Gap Title:** Lack of Controlled Multi-Benchmark Comparison of RLEF vs SFT Across Difficulty Levels  
**Priority:** Critical (PRIMARY, High Impact)  
**Relevance:** Directly blocks answering main research question  

### Research Question
Does reinforcement learning from execution feedback (RLEF) — using unit test pass/fail signals as rewards — significantly improve LLM code generation performance compared to supervised fine-tuning (SFT) baselines, and does the improvement generalize across benchmark difficulty levels (HumanEval, MBPP, CodeContests)?

### Gap Description
No single study systematically compares RLEF vs SFT across the full difficulty progression (HumanEval → MBPP → CodeContests → LiveCodeBench) using the same model, training data, and evaluation protocol. Existing works (CodeRL, PPOCoder, RLTF) each compare on subsets using different base models, training datasets, and evaluation protocols — no apples-to-apples comparison exists.

### Key Papers (Self-Written Summaries)

**P1: CodeRL (Le et al., 2022) — arXiv:2207.01780**
- **Core Contribution:** First end-to-end RLEF framework for code generation using actor-critic RL with program execution feedback. Uses CodeT5 as base model.
- **Methodology:** Actor (generator) trained with REINFORCE; Critic network predicts test outcome before execution to provide dense reward signal. Evaluated on APPS and HumanEval.
- **Key Results:** +4.3% pass@1 on HumanEval vs SFT baseline; significant gains on APPS (which tests harder competitive programming). Binary + critic reward.
- **Limitation:** Uses APPS/HumanEval only; no MBPP/CodeContests/LiveCodeBench evaluation. Different base model than later works. Critic adds architectural complexity.
- **Relevance to Gap:** Establishes RLEF superiority over SFT on HumanEval but cannot answer whether gains hold at CodeContests difficulty.

**P2: PPOCoder (Majeed et al., 2023) — arXiv:2301.13379**
- **Core Contribution:** PPO-based RLEF for code generation; compares directly against SFT on HumanEval and MBPP with a CodeGen base model.
- **Methodology:** Standard PPO with binary execution reward (pass/fail). KL penalty to SFT reference. Reports pass@1 and pass@10.
- **Key Results:** +5-8% pass@1 over SFT on HumanEval; +3-5% on MBPP. No hard benchmark evaluation.
- **Limitation:** Binary reward only; no partial credit ablation. Limited to function-level easy benchmarks.
- **Relevance to Gap:** Provides clean SFT comparison on easy benchmarks but leaves hard benchmark (CodeContests/LiveCodeBench) question unanswered.

**P3: RLEF (Gehring et al., 2024) — arXiv:2410.02089**
- **Core Contribution:** Most systematic RLEF vs SFT comparison to date; tests partial credit vs binary reward. Uses Meta's internal Code Llama variant.
- **Methodology:** GRPO/PPO with both binary and fraction-of-tests-passing reward. Multi-benchmark: HumanEval, MBPP, and harder problems. Key finding: partial > binary on hard problems.
- **Key Results:** Partial credit reward yields +10-15% over binary on harder problems; RLEF vs SFT gap wider at harder benchmarks. Non-reproducible (Meta internal model).
- **Limitation:** Internal model — not publicly reproducible. Does not include LiveCodeBench or CodeContests official benchmark.
- **Relevance to Gap:** Strongest evidence that RLEF generalizes to harder benchmarks, but non-reproducibility is the core problem this gap aims to address.

**P4: LiveCodeBench (Jain et al., 2024) — arXiv:2403.07974**
- **Core Contribution:** Contamination-free hard code evaluation benchmark using problems from Codeforces, LeetCode, and AtCoder. Temporal filtering prevents data leakage.
- **Methodology:** Rolling update benchmark; pass@1 primary metric; problems rated easy/medium/hard.
- **Key Results:** Strong SFT models (DeepSeek-Coder-V2, Claude) score 20-40% on hard problems. No RLEF-trained model baselines exist.
- **Limitation:** No RLEF baselines — complete gap in the literature.
- **Relevance to Gap:** This is exactly the hard benchmark missing from RLEF studies. Evaluating RLEF-trained models here would directly answer Q2.

### Feasibility Constraints (Pipeline-Enforced)
- REJECT: New benchmarks, rubrics, scoring frameworks
- REJECT: Synthetic data, future data, human evaluation
- ACCEPT ONLY: Hypotheses testable on existing real datasets and existing benchmarks

### Available Infrastructure
- TRL (PPOTrainer/GRPOTrainer) — reward function hooks
- bigcode-evaluation-harness — unified eval: HumanEval, MBPP, LiveCodeBench
- DeepSeek-Coder weights — public multi-scale SFT baseline (1.3B/6.7B/33B)
- salesforce/CodeRL — adaptable RLEF training loop
- SWE-bench Docker — repo-level evaluation (optional)

---

## Previous Failure / Routing Context

*No previous failure contexts found. This is version 1, first Phase 2A execution.*

---

## Discussion Transcript

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we stop thinking of this as "does RLEF work?" and instead ask: "at what difficulty level does the execution feedback signal become *irreplaceable*?" That reframe is everything here. We have good evidence from CodeRL and PPOCoder that RLEF beats SFT on easy benchmarks — HumanEval, MBPP — by 5-15%. Fine. But those benchmarks are nearly saturated for frontier models. The REAL question is whether the execution reward signal — that beautiful, hard, ground-truth signal — provides training information that SFT simply *cannot* provide at harder difficulty levels.

Imagine this: at HumanEval difficulty, a strong SFT model can often generate correct code from patterns in training data. The execution feedback adds a correctness check but doesn't drastically change what the model can learn. Now scale the difficulty to CodeContests or LiveCodeBench. Here, solutions require novel algorithmic composition — combinatorics, dynamic programming, graph algorithms in novel configurations. SFT can't teach what isn't in its training distribution. But execution feedback can! A partially correct solution that passes 3/5 tests tells the model *exactly* where its reasoning breaks down. This is a qualitatively different learning signal.

So here's my proposed hypothesis kernel: **Execution feedback rewards provide qualitatively superior training signal at higher difficulty levels, causing RLEF's performance advantage over SFT to *widen* with benchmark difficulty** — not just maintain. This is a testable, falsifiable claim using existing benchmarks (HumanEval → MBPP → CodeContests → LiveCodeBench) with a fixed model (DeepSeek-Coder-7B, publicly available) and fixed training data (APPS dataset, public). The novelty isn't just "RLEF > SFT" — it's the *difficulty-scaling relationship* of that gap.

What I love about this: if the gap doesn't widen, that's also a publishable finding — it would mean RLEF's benefit is uniform regardless of difficulty, which challenges the intuition about reward signal quality. Either direction advances the field.

**Key Points:**
- Core claim: RLEF's advantage over SFT scales with benchmark difficulty (gap widens, not constant)
- Execution feedback becomes irreplaceable at higher difficulty where SFT can't cover training distribution
- Testable immediately: fixed model (DeepSeek-Coder-7B) + fixed data (APPS) + existing benchmarks (HumanEval → LiveCodeBench)
- Novelty is the *difficulty-scaling relationship*, not just RLEF > SFT

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's enthusiasm is infectious, but let me immediately sharpen the claim into something actually testable. "Gap widens with difficulty" is directionally interesting but scientifically imprecise. We need to operationalize this as a falsifiable prediction with *specific* criteria.

Here's the precision problem: "difficulty" is a confound-ridden variable. HumanEval, MBPP, CodeContests, and LiveCodeBench differ not just in problem difficulty but in problem type (function-level vs. algorithmic), test coverage quality (HumanEval has 7-10 tests/problem vs. APPS has 1-10), contamination risk, and evaluation protocol. If we see a larger RLEF-SFT gap on CodeContests, is it because difficulty is higher, or because APPS training data overlaps with CodeContests problem styles? That's a confound we must control.

So the testable version of Dr. Nova's hypothesis requires: (1) **same base model** — DeepSeek-Coder-7B works, weights are public; (2) **same training data** — APPS dataset for both SFT and RLEF fine-tuning; (3) **same evaluation protocol** — bigcode-evaluation-harness for all benchmarks; (4) **matched training compute** — same number of gradient steps or wall-clock equivalent. With those four controls, the comparison becomes scientifically clean.

The specific prediction: measure pass@1 (and pass@10 as secondary) for SFT-fine-tuned model and RLEF-fine-tuned model on each benchmark. Compute Δ = pass@1(RLEF) - pass@1(SFT) at each difficulty level. The hypothesis predicts Δ increases monotonically from HumanEval → MBPP → CodeContests → LiveCodeBench. Falsification: Δ is approximately constant across difficulty levels, or decreases. **What result would convince me this hypothesis is wrong?** If Δ_CodeContests ≤ Δ_HumanEval, the difficulty-scaling claim fails.

One concern I must flag: the sample sizes are very different. HumanEval has 164 problems, MBPP 374, CodeContests thousands, LiveCodeBench hundreds. We need bootstrap confidence intervals on Δ to claim statistical significance at each level. This is doable with existing tools — bigcode-harness supports this.

**Key Points:**
- Falsification criterion: Δ_CodeContests ≤ Δ_HumanEval (gap does not widen)
- Four critical controls: same model, same data, same eval protocol, matched compute
- Statistical rigor: bootstrap CIs on Δ at each benchmark difficulty level
- Confound warning: benchmark differences beyond difficulty (test coverage, contamination) must be acknowledged

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

What does this mean for the field? Let me assess the significance of what's emerging here. The difficulty-scaling relationship Dr. Nova proposed and Prof. Vera sharpened is genuinely important — but I want to make sure we understand *why* it matters and whether it opens new questions or merely confirms intuition.

The significance case is strong. The current state of code generation research has a troubling pattern: papers compare RLEF vs SFT using different models, different datasets, and different benchmarks. This makes it impossible to isolate the training method effect from model capacity and data effects. A single controlled study with fixed model + data that evaluates across the full difficulty spectrum would be the *reference experiment* the field has been missing. Every future RLEF paper would need to position against it.

But here's what would make this *more* than just a clean replication: if we can show *why* the gap widens (or doesn't). The mechanism matters. Dr. Nova's intuition — that execution feedback provides training signal covering out-of-distribution difficulty — is theoretically grounded in the exploration-exploitation tradeoff. SFT is purely supervised: it interpolates within the training distribution. RLEF via PPO/GRPO with execution rewards can *explore* solution space beyond the supervised signal. At hard benchmarks, this exploration bonus becomes critical because the SFT signal is weaker (fewer training examples cover CodeContests-difficulty problems).

The question I must ask: what new research directions does this open? I see at least three: (1) optimal curriculum design for RLEF (does training order easy→hard matter?); (2) reward signal quality as a function of test coverage; (3) whether the scaling relationship holds across model sizes. Any of these would be follow-on papers enabled by our controlled baseline.

The significance is high — but only if we publish with the complete controlled methodology so it's actually reproducible. Reproducibility is the scientific contribution, not just the result.

**Key Points:**
- Significance: this becomes the reference controlled experiment the field lacks — high impact regardless of direction
- Mechanism matters: RLEF's exploration benefit over SFT's interpolation matters more at harder difficulty (out-of-distribution problems)
- Opens 3 follow-on directions: curriculum design, test coverage effects, model-scale consistency
- Reproducibility IS the contribution — full code + model weights + eval pipeline must be public

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic about whether this can actually work — and I mean technically/theoretically realistic, not resource-realistic. The mechanism is sound in principle: PPO/GRPO with execution rewards is mathematically well-defined, the reward function (fraction of tests passing) is bounded [0,1], differentiable in expectation, and the KL penalty prevents policy collapse. TRL implements all of this with custom reward hooks. So yes, this can work in principle.

But I see a fundamental technical concern that no one has raised: **test quality degrades at higher difficulty benchmarks**. LiveCodeBench problems from competitive programming typically have exhaustive test suites (tens of tests, corner cases, edge cases). APPS test suites vary wildly — some problems have 1-2 tests, some have 20. If the training reward is computed on APPS tests (which we're using for RLEF fine-tuning), and evaluation is on LiveCodeBench (which has different test structures), we're testing generalization of a reward-tuned model across different test *coverage densities*. That's not a confound, it's actually part of the scientific question — but it needs to be explicitly modeled, not swept under the rug.

The second concern: CodeContests and LiveCodeBench have time and memory limits. An RLEF-trained model that generates syntactically correct, test-passing code on APPS might generate inefficient solutions (O(n³) where O(n log n) is needed) that fail on competitive programming evaluators. This is a genuine technical barrier: the execution reward during training on APPS doesn't penalize inefficiency because APPS's test scripts often don't enforce time limits the way competitive programming judges do. So the model can't learn efficiency from APPS rewards.

What this means for the hypothesis: we should scope it carefully. The claim "RLEF gap widens with difficulty" should be tested on LiveCodeBench's *correctness* metrics (whether code produces correct output on provided tests), not on full competitive programming judge evaluation with time/memory limits. This is a scope reduction that makes the experiment cleaner and more feasible.

**Key Points:**
- Mechanism is technically sound: PPO/GRPO + fraction-of-tests reward is mathematically valid
- Scope constraint: evaluate on LiveCodeBench *correctness* (no time limits), not full competitive judge — training reward (APPS) and eval reward (LiveCodeBench) coverage differ
- APPS test quality variability is a known issue — must report per-problem test count statistics
- Efficiency gap: APPS training can't teach time complexity; this limits what RLEF-vs-SFT comparison at CodeContests-level tells us

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Excellent — the foundations are solid. Let me synthesize what's emerged and strengthen the hypothesis to address Prof. Pax's scope constraint while preserving the core novelty Dr. Nova and Dr. Sage identified.

The strengthened hypothesis: **Under controlled fine-tuning conditions (same base model, training data, and evaluation protocol), RLEF with fraction-of-tests-passing reward achieves a progressively larger performance advantage over SFT as benchmark difficulty increases from HumanEval (easy) to MBPP (medium-easy) to LiveCodeBench-Easy/Medium (medium-hard) to APPS Hard problems, because execution feedback provides learning signal for out-of-distribution problem structures that SFT-only training cannot encode.**

Prof. Pax's concern about time limits is now addressed by scoping to *correctness-only* evaluation on LiveCodeBench (which bigcode-harness supports without competitive judge time limits). This is a cleaner experiment than full judge evaluation anyway. Prof. Vera's four controls (model, data, eval, compute) are preserved. Dr. Sage's reproducibility point is elevated to a core contribution.

YES, AND we can strengthen this further: include a partial reward ablation within the same controlled setup. Train three models: (1) SFT baseline, (2) RLEF with binary reward, (3) RLEF with fraction-of-tests reward. This directly addresses Gap 2 (reward formulation) within the same experimental framework — one experiment, two gaps addressed. The prediction now has internal structure:

- **P1 (Primary):** Fraction-RLEF > Binary-RLEF > SFT, with the Fraction-RLEF advantage growing with difficulty
- **P2 (Secondary):** The Binary-RLEF vs SFT gap is approximately constant across difficulty (binary reward doesn't scale)
- **P3 (Tertiary):** Fraction-RLEF shows larger gap over SFT on LiveCodeBench-Hard than on HumanEval

The hypothesis is now stronger AND more parsimonious — fewer experiments needed to test more claims.

**Key Points:**
- Strengthened scope: correctness-only eval on LiveCodeBench (no time-limit confound)
- Reward ablation embedded: SFT vs Binary-RLEF vs Fraction-RLEF in one framework
- Three predictions with clear falsification criteria (P1-P3 above)
- Addresses Gap 1 AND Gap 2 simultaneously — efficient experimental design

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down. I have three concerns that need answers before I'd call this hypothesis bulletproof.

**Concern 1: The base model choice (DeepSeek-Coder-7B) may not be valid for this claim.** DeepSeek-Coder-7B was trained with extensive code data including competitive programming. Its SFT baseline may already be near-optimal on HumanEval/MBPP, making the SFT ceiling too high to see RLEF's benefit clearly. The 5-15% gains seen in PPOCoder and CodeRL were on weaker base models (CodeGen, CodeT5). If we use a strong base model, the RLEF vs SFT gap might be *smaller* on easy benchmarks precisely because SFT is already strong there — which would make the "gap widens with difficulty" claim trivially true due to a floor effect on SFT at hard benchmarks, not because RLEF is genuinely better at hard difficulty. That's an alternative explanation we must rule out.

**Concern 2: The APPS training dataset doesn't have representative coverage of LiveCodeBench problem difficulty.** APPS Hard problems top out around Codeforces Div 2 difficulty. LiveCodeBench Hard includes Div 1 problems. If both SFT and RLEF are trained on APPS, neither has seen difficulty-level examples equivalent to LiveCodeBench Hard. The "RLEF gap widens at hard" observation could reflect that RLEF is better at *interpolating beyond training difficulty* — which is a different (and stronger) claim than "RLEF is better at harder difficulty in general." These are scientifically distinct claims that need to be distinguished.

**Concern 3: N=1 model size is insufficient for the generalization claim.** The hypothesis is stated about RLEF performance in general, but one experiment with DeepSeek-Coder-7B only licenses conclusions about 7B-scale models. A reviewer will immediately ask: does this hold for 1.3B and 13B? The hypothesis needs to explicitly scope to 7B-scale, or add a mini-scale experiment at 1.3B as a sanity check.

**What would convince me:** Add a SFT ceiling analysis (show that HumanEval SFT performance is not saturated), explicitly distinguish "difficulty generalization" from "difficulty extrapolation" in the mechanism, and scope the claim to 7B-scale or add a 1.3B replication.

**Key Points:**
- Concern 1: Strong base model (DeepSeek-Coder-7B) may create floor effect on easy benchmarks — confounds "gap widens" claim
- Concern 2: APPS training difficulty ceiling doesn't reach LiveCodeBench Hard — claim may be about difficulty extrapolation, not generalization
- Concern 3: N=1 model size — scope explicitly to 7B or add 1.3B sanity check
- Mitigation: SFT ceiling analysis + explicit mechanism distinction + model scope statement

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex, NOW we're onto something! Your critique is sharp and I love it. But here's the thing — concern 1 and concern 2 don't weaken the hypothesis, they *refine it into something even more interesting*.

The floor effect concern is actually testable: if DeepSeek-Coder-7B SFT is near-ceiling on HumanEval, we'll see it in the results (pass@1 ≥ 90%). We can simply report the SFT ceiling and note that the hypothesis applies in the regime where SFT is not already saturated. That's a scope boundary, not a failure. We can add DeepSeek-Coder-1.3B (publicly available) as a secondary model that definitely has headroom on HumanEval — this addresses concern 3 (model size sanity check) and concern 1 (non-saturated SFT baseline) simultaneously.

The "generalization vs. extrapolation" distinction Prof. Rex raised is genuinely novel and I want to preserve it. Let me restate the mechanism more precisely: RLEF provides learning signal *conditioned on execution outcomes*, which is fundamentally different from SFT's maximum likelihood objective. At problems within the training difficulty distribution, both SFT and RLEF learn from the same distributional patterns, so their gap is small. At problems that *extrapolate beyond* training difficulty — where SFT has no successful examples to learn from — RLEF can still learn from *partially correct* solutions (those that pass some tests). This is the mechanism: **RLEF learns from partial success; SFT requires full success.**

This is testable via a mechanism check: count how many training problems each model generates fully correct solutions for during training. SFT (teacher forcing) uses all problems; RLEF can learn from problems where it generates partial solutions. If RLEF at CodeContests-level has more learning signal from partial solutions than SFT, that's direct mechanistic evidence.

For scope: claim holds for 7B-scale models with APPS training. Add 1.3B sanity check. Explicitly note that LiveCodeBench Hard may be difficulty *extrapolation*, not generalization, and test this as a separate prediction.

**Key Points:**
- Addresses concern 1: SFT ceiling check built in; add DeepSeek-Coder-1.3B as secondary
- Addresses concern 3: 1.3B replication is both a scope sanity check and a non-saturated SFT baseline
- Mechanism sharpened: "RLEF learns from partial success; SFT requires full success in training examples"
- Testable mechanism check: compare fraction of training problems where RLEF has non-zero reward vs SFT

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

The evidence suggests we have converged on a well-structured hypothesis. Let me finalize the prediction structure to ensure every claim is precisely testable.

**Refined Prediction Set:**

**P1 (Primary — gap scaling):** Under controlled conditions (DeepSeek-Coder-7B + APPS training + bigcode-harness evaluation), Δ(Fraction-RLEF, SFT) > Δ(Binary-RLEF, SFT) on hard benchmarks, and Δ at LiveCodeBench-Medium/Hard ≥ 1.5× Δ at HumanEval. Falsification: Δ_LiveCodeBench ≤ Δ_HumanEval.

**P2 (Secondary — reward formulation):** Fraction-of-tests reward provides strictly larger Δ over SFT than binary reward at CodeContests-equivalent difficulty. Falsification: binary and fraction rewards produce equal Δ on hard problems.

**P3 (Tertiary — mechanism):** The fraction of training problems with non-zero RLEF reward (partial success) is higher at hard problems than at easy problems, while SFT training signal is uniform across difficulty. This provides direct mechanism evidence. Falsification: non-zero reward rates are equal across difficulty levels.

**P4 (Sanity — model scale):** Pattern holds directionally (not necessarily magnitudinally) for DeepSeek-Coder-1.3B. Falsification: pattern inverts at 1.3B scale.

What specific, measurable predictions can we make? All four are now operationalized. The statistical test for P1: two-sample bootstrap test on Δ values with Bonferroni correction for multiple benchmarks. Significance level: α = 0.05 per comparison. The confounds Prof. Pax raised (test coverage variability, time limits) are controlled by using bigcode-harness correctness-only evaluation, which I confirm is appropriate given the scope.

**Key Points:**
- P1: Gap scaling (primary) — 1.5× threshold on hard vs easy Δ
- P2: Reward formulation (secondary) — fraction > binary at hard difficulty
- P3: Mechanism check — partial success rate as training signal proxy
- P4: Scale sanity — directional replication at 1.3B
- All four predictions have explicit falsification criteria — this meets my standards

---

### Exchange 9

🎯 **Dr. Sage** (Research Impact Evaluator):

The question I must ask: is the 1.5× threshold in P1 well-justified? And is this a contribution the DL4C community needs now?

On the threshold: 1.5× is slightly arbitrary, but defensible. It means the RLEF advantage at hard difficulty is 50% larger than at easy difficulty — a practically significant effect that can't be explained by noise. Alternative thresholds (1.3×, 2×) could be argued either way. I'd recommend reporting the actual ratio as a continuous outcome and pre-specifying 1.5× as the minimum meaningful effect. This is standard practice in pre-registered experiments.

On significance: yes, the DL4C community needs this. The timing is perfect — 2024-2025 saw an explosion of code generation papers (DeepSeekCoder-V2, Qwen2.5-Coder, GPT-4o for code) but almost none directly address RLEF vs SFT under controlled conditions with difficulty stratification. A 2026 paper that provides this controlled comparison, with full reproducible pipeline and code release, would fill a genuine empirical gap. The fact that we're using existing infrastructure (TRL, bigcode-harness, public DeepSeek-Coder weights) means the community can reproduce and extend this immediately.

What new research directions does this open? (1) Curriculum learning for RLEF (does starting with easy problems and moving to hard improve the difficulty-scaling relationship?); (2) Reward signal quality as function of test coverage density; (3) RLEF at model scales beyond 7B (does the difficulty-scaling relationship hold at 70B?). These are well-motivated follow-on questions our controlled baseline enables.

The research is significant, timely, and feasible. The pipeline constraint (APPS → TRL RLEF → bigcode-harness eval) uses nothing not available today.

**Key Points:**
- 1.5× threshold justified as minimum meaningful effect; report actual ratio as continuous outcome
- Timing: 2026 controlled comparison fills 2024-2025 empirical gap; reproducibility is the differentiator
- Opens curriculum learning, test coverage density, and scale follow-on questions
- Full feasibility on existing infrastructure — no blocking dependencies

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Okay, this could work. Let me validate the complete experimental pipeline against technical concerns.

**Training pipeline:** TRL GRPOTrainer with custom reward function (fraction-of-tests passing). DeepSeek-Coder-7B as base. APPS training set (~5000 problems with test cases). This is technically sound — TRL's GRPOTrainer has been validated for code generation tasks, reward function returns scalar in [0,1], KL divergence penalty standard. One technical detail: APPS test execution requires a secure sandbox (Docker or subprocess with timeout) to prevent malicious code injection and infinite loops during reward computation. This is already solved in the TRL reward server pattern.

**Evaluation pipeline:** bigcode-evaluation-harness supports HumanEval (164 problems), MBPP (374), and LiveCodeBench (rolling, use 2024-Q1 to Q4 snapshot for reproducibility). CodeContests evaluation requires specific infrastructure but bigcode-harness has a CodeContests backend. All three needed benchmarks are accessible. For LiveCodeBench, specify the snapshot date for reproducibility — CRITICAL for contamination control.

**Mechanism check (P3):** Logging non-zero reward fractions per batch by problem difficulty is standard TRL monitoring — just add a custom callback. This is zero additional implementation cost.

**1.3B sanity check (P4):** DeepSeek-Coder-1.3B weights public. Same training pipeline, smaller model. Trivially parallelizable with the 7B experiment.

Technical soundness: confirmed. The only remaining implementation detail is the APPS sandbox for reward execution — solved pattern. The mechanism is sound, measurements are valid, interventions work in principle.

**Key Points:**
- GRPO + fraction-of-tests reward: technically valid, TRL-implemented, sandbox required for safe execution
- bigcode-harness covers all needed benchmarks; LiveCodeBench snapshot date must be specified
- P3 mechanism check: zero-cost TRL monitoring callback
- P4 sanity check: DeepSeek-Coder-1.3B parallelizes trivially with 7B experiment

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

We're very close. Let me write the final refined hypothesis that incorporates everything.

**FINAL CONSENSUS HYPOTHESIS:**

*Under controlled fine-tuning conditions (fixed base model: DeepSeek-Coder-7B; fixed training data: APPS dataset; fixed evaluation: bigcode-evaluation-harness correctness-only), training with RLEF using fraction-of-tests-passing reward yields a progressively larger performance advantage over SFT as benchmark difficulty increases from HumanEval → MBPP → LiveCodeBench-Easy/Medium/Hard, because execution feedback enables learning from partially-correct solutions at difficulty levels where SFT has no fully-correct training examples to learn from, while binary reward provides a weaker version of this same benefit.*

**Mechanism:** RLEF with fraction reward → non-zero gradient signal from partially-correct solutions at high difficulty → model learns algorithmic structure incrementally. SFT → zero gradient from hard problems where no fully-correct solution appears in training → no learning signal at high difficulty. Binary reward → cliff effect at 0/1 → weaker intermediate signal at moderate difficulty.

**Three Testable Predictions:**
- P1: Δ(Fraction-RLEF, SFT) at LiveCodeBench ≥ 1.5× Δ at HumanEval
- P2: Δ(Fraction-RLEF, SFT) > Δ(Binary-RLEF, SFT) at hard benchmarks
- P3: Non-zero reward fraction during training correlates with problem difficulty (harder problems → higher partial-success rate in RLEF, zero in SFT)

**Novelty:** No prior work provides this difficulty-stratified controlled comparison with a reproducible open-source pipeline. The mechanistic explanation (partial-success learning signal) is novel and directly testable.

**Feasibility:** Confirmed by Prof. Pax — TRL + APPS sandbox + bigcode-harness + public DeepSeek-Coder weights. All components exist and are validated.

**Objections addressed:** SFT ceiling check via 1.3B secondary model; scope limited to correctness-only (no time limits); scope explicitly 7B primary + 1.3B sanity.

The hypothesis is strong. I'm satisfied.

**Key Points:**
- Final hypothesis: difficulty-scaling RLEF advantage with partial-success mechanism
- All 6 convergence criteria met: SPECIFIC ✓, MECHANISM ✓, PREDICTIONS ✓, NOVELTY ✓, FEASIBILITY ✓, OBJECTIONS ✓
- Pipeline: TRL GRPO + APPS + bigcode-harness — all public, all today
- Ready for Phase 2B

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Show me the evidence for the scope claim — and I believe you've addressed my concerns.

Concern 1 (SFT ceiling): addressed by including DeepSeek-Coder-1.3B as secondary, which will have clear headroom on HumanEval. SFT ceiling analysis is now P0 (prerequisite check), not an afterthought.

Concern 2 (generalization vs extrapolation): addressed by reframing the mechanism as "partial-success learning signal at high difficulty" — this works whether it's generalization or extrapolation; the mechanism is the same. The distinction now informs interpretation, not experimental design.

Concern 3 (model scale): addressed by 1.3B sanity check.

One final stress test: the claim assumes APPS training provides adequate coverage of problem types that appear at LiveCodeBench-Medium/Hard. If APPS is biased toward Python-specific algorithmic patterns and LiveCodeBench-Hard requires general CS theory problems, there's a domain mismatch. I'd recommend reporting the problem-type distribution of APPS vs LiveCodeBench as a supplementary analysis — not a blocker, but important for interpretation.

Now you've addressed my concerns. This hypothesis is ready for experimental verification.

**Key Points:**
- All three concerns addressed — hypothesis is bulletproof
- One remaining note: report APPS vs LiveCodeBench problem-type distribution as supplementary
- Mitigation: problem-type distribution analysis (zero additional experiment, just descriptive statistics)
- Ready for Phase 2B


## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The difficulty-scaling relationship of RLEF's advantage over SFT is genuinely novel — no prior work has characterized this as a systematic function of benchmark difficulty. The mechanism (partial-success learning signal) reframes existing observations into a testable causal explanation. The dual-gap design (addressing Gap 1 and Gap 2 simultaneously) is an elegant and unexplored experimental structure.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** All four predictions (P1-P4) have explicit quantitative falsification criteria. P1 has a pre-specified 1.5× threshold; P2 is a direct comparison with defined levels; P3 is a mechanistic proxy testable via training monitoring; P4 is a directional replication. The four controls (model, data, eval, compute) make confounds manageable. This meets scientific standards.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** The field lacks a reproducible controlled comparison of RLEF vs SFT across benchmark difficulty — this paper would become the reference experiment. Timing is excellent (2024-2025 RLEF/code generation surge makes the gap visible). The open-source pipeline (TRL + bigcode-harness + public weights) ensures community reproducibility and immediate follow-on work.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Technical pipeline confirmed: TRL GRPOTrainer + APPS sandbox + bigcode-evaluation-harness + public DeepSeek-Coder weights. All components exist, are validated for code generation, and require no new infrastructure. Correctness-only evaluation scope eliminates the time-limit confound. The mechanism check (P3) adds zero implementation cost.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The hypothesis that emerged from this discussion is both scientifically sound and practically executable. Under controlled fine-tuning conditions — fixing the base model (DeepSeek-Coder-7B), training data (APPS), and evaluation protocol (bigcode-evaluation-harness correctness-only) — we predict that RLEF with fraction-of-tests-passing reward achieves a progressively larger performance advantage over SFT as benchmark difficulty increases from HumanEval (easy) through MBPP (medium-easy) to LiveCodeBench Easy/Medium/Hard.

The causal mechanism is: execution feedback enables gradient signal from partially-correct solutions at difficulty levels where SFT's fully-supervised objective receives zero signal (no fully-correct solutions in training data at that difficulty). Binary reward is a weaker version of this — it provides some signal but collapses partial information into 0/1, losing the incremental structure that fraction reward preserves.

The key experimental predictions are: (P1) the RLEF-SFT gap at LiveCodeBench is ≥1.5× the gap at HumanEval; (P2) fraction reward outperforms binary reward at hard benchmarks more than at easy ones; (P3) the non-zero reward fraction during training correlates with problem difficulty; (P4) the directional pattern holds at DeepSeek-Coder-1.3B scale. All predictions use existing benchmarks and existing infrastructure. No new benchmarks, no human evaluation, no synthetic data — fully within pipeline feasibility constraints.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Report APPS vs LiveCodeBench problem-type distribution (Python algorithmic bias check) as supplementary analysis
- SFT ceiling at DeepSeek-Coder-7B on HumanEval should be checked pre-experiment; if ≥90%, 1.3B becomes primary model
- The 1.5× threshold in P1 is pre-specified but should be justified in the paper with power analysis or effect size literature
- **Mitigation Strategy:** Pre-register predictions before running experiments; include problem-type distribution and SFT ceiling report in Section 3.1 of the paper; cite effect size standards from related RLEF papers for threshold justification
