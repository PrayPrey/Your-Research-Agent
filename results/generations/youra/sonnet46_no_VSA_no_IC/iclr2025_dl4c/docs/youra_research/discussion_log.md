# Phase 2A Discussion Log
# Gap: Variance-Guided vs Random Data Selection for Binary Execution Reward RLEF
# Architecture: Self-Contained Tikitaka Loop (Claude plays ALL personas)
# Date: 2026-08-21
# Execution: UNATTENDED

## Research Briefing

**Selected Gap:** Gap 2 — Variance-Guided vs Random Data Selection for Binary Execution Reward RLEF Has Not Been Directly Compared

**Research Question:** Does variance-guided training data selection for RLEF (selecting top-N MBPP problems by per-problem binary reward variance p*(1-p) computed on a frozen code LLM) yield higher pass@1 improvement on HumanEval+ per gradient step at 20–50 GRPO steps compared to random-N subset RLEF and full-set RLEF?

**Sub-Questions Addressed:**
- SQ2: Does variance-selected RLEF (top-N=50, 20–50 GRPO steps) outperform random-N=50 subset RLEF at same gradient budget?
- SQ3: Does variance-selected N=50 achieve pass@1 improvement within 80% of full-set RLEF (374 problems, same steps)?

**Key Evidence from Phase 1:**
- GRPO gradient magnitude = σ = √(k(G-k))/G — directly governed by within-group reward variance
- 69.25% of groups produce zero gradient at G=4 (Gradient Starvation paper, arXiv:2605.07689)
- VIGOR: variance-utility selection proves exponential speedup over GRPO
- Sun et al. 2025: difficulty-targeted selection yields 23–62% compute reduction (math domain)
- Prompt Replay: pass rate ≈ 0.5 (maximum binary variance) prioritization for GRPO
- LZE: outcome-uncertainty + pass-rate momentum selection
- DeepSeek-Coder-7B-Instruct + MBPP (374 problems) + HumanEval+ (EvalPlus) confirmed infrastructure
- Constraints: use_vllm=False, generation_batch_size=4, ≤50 GRPO steps

**Available Papers (Phase 1 Verified):**
- P1: Sun et al. 2025 (arXiv:2506.05316) — Difficulty-targeted online data selection for GRPO; 23–62% compute reduction
- P2: VIGOR (arXiv:2607.22002) — Variance as GRPO selection signal; gradient ∝ within-group variance
- P3: Gradient Starvation (arXiv:2605.07689) — 69.25% zero-gradient groups at G=4 empirical characterization
- P4: LZE (arXiv:2605.17003) — Learning-Zone Energy: pass-rate momentum + outcome-uncertainty selection
- P5: RLEF (Gehring et al., arXiv:2410.02089) — Seminal RLEF paper; execution feedback RL for code

**Feasibility Constraints (Pipeline-Enforced):**
- NO new benchmarks or rubrics
- NO synthetic/generated data
- NO human evaluation/annotation
- ONLY existing real datasets (MBPP, HumanEval+) and existing benchmarks (EvalPlus)

### Previous Failure / Routing Context

No Serena memory files found. First Phase 2A attempt.

h-e1 failures (documented in Phase 1):
- Run 1 & 2: Only 5 gradient steps on 40 MBPP examples + crash-only eval (not EvalPlus) → both pass@1 = 0.0000
- Root cause: measurement artifact, not algorithm failure
- Variance-guided selection hypothesis was NEVER tested in prior runs
- Direction pivot: from "GRPO vs SFT" → "variance-guided subset selection efficiency"

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we think about this problem as *gradient diet* rather than gradient starvation? Everyone is talking about the 69.25% zero-gradient groups at G=4 as a pathology to fix inside the optimizer. But what if the real opportunity is upstream — choosing which problems to feed the optimizer in the first place, using a frozen model snapshot to identify the learning frontier before we commit to any expensive training?

What I find genuinely exciting about this research direction is the separation of concerns it creates. The profiling phase is cheap inference — you run a frozen DeepSeek-Coder-7B-Instruct through 374 MBPP problems, sample k=8 completions per problem, compute p_i*(1-p_i) for each, rank them, and take top-50. The training phase is then concentrated entirely on the problems where the model is genuinely uncertain — where GRPO gradients are nonzero. You've effectively pre-filtered to the learning frontier.

What's novel here, and what no prior paper has done, is the *offline frozen-model profiling* paradigm for binary execution reward code generation. VIGOR, Sun et al., Prompt Replay — they all do online selection, updating their selection signal as the model trains. That requires entangling profiling and training. This research separates them completely: profile once with a frozen model, then train exclusively on the selected subset. The snapshot variance is a static proxy for the initial gradient signal landscape.

The cross-domain connection that excites me: this is exactly how active learning works with a cheap oracle. Before you pay for expensive labels, you use a cheap model to estimate uncertainty. Here, the "label" is the expensive GRPO training step, and the "uncertainty" is binary execution reward variance. We're doing active learning for RLEF data selection — that's a paradigm shift in how we think about data curation for RL fine-tuning.

**Key Points:**
- Frozen-model offline profiling separates cheap selection from expensive training — novel paradigm vs. all existing online selection methods
- p*(1-p) binary variance is a direct proxy for per-problem GRPO gradient magnitude (σ = √(k(G-k))/G)
- 3-condition experiment (variance-50 vs random-50 vs full-374) provides clean causal evidence unavailable in prior work
- Analogy to active learning with cheap oracle provides theoretical framing beyond code-specific motivation

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's enthusiasm is well-placed, but let me stress-test the experimental design before we commit to a hypothesis. The core claim needs to be very precise: we're not claiming frozen-model variance predicts training-time variance after optimization has begun. We're claiming that *initial* variance — measured on the frozen model — is a sufficient proxy for *which problems will remain in the learning zone* across 20–50 GRPO steps.

This is the key testability issue: the variance distribution is not static. As the model trains, p_i for each problem shifts. A problem that was at p_i=0.5 at step 0 may have p_i=0.8 by step 20, moving it out of the learning zone. So our hypothesis must be framed carefully: we're claiming that frozen-model variance ranking is a *good enough* proxy for the initial-gradient-rich learning frontier over the SHORT training regime (20–50 steps), not over a full epoch.

What would falsify the hypothesis? If random-N=50 achieves equal or better HumanEval+ pass@1 improvement per gradient step than variance-N=50 at 50 GRPO steps, the hypothesis fails. If full-set-374 outperforms variance-50 by more than 20%, hypothesis partially fails. These are clean, measurable binary outcomes on existing EvalPlus infrastructure.

What would disprove the mechanism? If the variance-selected top-50 problems have the same average `frac_reward_zero_std` (TRL metric) as random-50 during actual GRPO training, the profiling failed to identify genuinely informative problems. The confound I'm most worried about: DeepSeek-Coder-7B-Instruct may already perform very well on MBPP, meaning most problems may have p_i close to 1.0 (too easy), making variance-selection and hard-problem-selection confounded.

**Key Points:**
- Hypothesis scope: frozen-model variance is a *sufficient proxy* for LEARNING ZONE identification over 20–50 steps (not full training)
- Primary falsification: random-N=50 ≥ variance-N=50 in HumanEval+ pass@1 improvement per gradient step
- Mechanism validation: compare `frac_reward_zero_std` between variance-50 and random-50 during GRPO runs
- Confound control: report p_i distribution for selected vs random subsets to separate variance-selection from hard-problem-selection

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what does this research contribute beyond "another data selection paper"? The field already has Sun et al. 2025 (55 citations), VIGOR, Prompt Replay, LZE — all addressing data selection or rollout efficiency for RLVR.

What makes this genuinely new? The combination of three specific properties: (1) binary execution reward specifically (not scalar reward); (2) code generation domain (MBPP + HumanEval+, not math reasoning); (3) *offline* frozen-model profiling before training begins. No existing paper has this exact combination. Sun et al. uses online selection with attention-based difficulty estimation. VIGOR uses online variance selection during training. Prompt Replay uses running pass rate. All three require the training loop to be already running. This work does profiling before training — enabling "profile once on a frozen model, train on any machine, resume anywhere."

The significance escalates if we find that frozen-model variance predicts training efficiency even under h-e1 technical constraints (use_vllm=False, generation_batch_size=4). The research also opens the question of whether variance computed offline generalizes across RLEF iterations.

**Key Points:**
- Triple novelty: binary execution reward + code domain + offline frozen profiling (no prior paper has all three)
- Practical deployment value: "profile once, train anywhere" enables resumable, reproducible RLEF experiments
- Field positioning: extends Sun et al. 2025 to code domain with a methodologically distinct (offline vs online) selection paradigm
- Opens new research direction: frozen inference as a cheap oracle for RLEF experiment design

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic about what the mechanism actually claims and whether it's sound. The formal identity σ = √(k(G-k))/G holds for a fixed group of G samples where k are correct. When we profile with k=8 i.i.d. completions per problem on a frozen model, we compute an empirical pass rate p_i = k_i/8. The variance estimate from k=8 samples is noisy, particularly at extreme p values — but this doesn't break the mechanism, it means the variance ranking is noisy at the extremes.

Second: the "frozen model at step 0" assumption. GRPO training with even 20–50 steps can significantly shift the model's capability distribution. The mechanism claim is therefore: "problems with intermediate frozen-model variance will *remain* learnable for a sufficient fraction of the 50 steps to produce net positive gradient contribution relative to random selection." Testable — you can check whether TRL `frac_reward_zero_std` is consistently lower for variance-50 vs random-50 throughout training.

Third: the confound between variance-selection and difficulty-selection. If DeepSeek-Coder-7B-Instruct has high pass rates on most MBPP problems, top-50 by variance automatically selects the hardest remaining problems. The cleaner hypothesis is: we're claiming that filtering near-zero-variance problems improves efficiency — not necessarily that variance is *better than* difficulty alone.

**Key Points:**
- Mechanism is sound: σ = √(k(G-k))/G holds exactly; k=8 frozen profiling introduces estimation noise but doesn't break the mechanism
- Key testable mechanistic prediction: variance-50 should have consistently lower `frac_reward_zero_std` than random-50 throughout training
- Confound to control: report variance distribution of selected vs random subsets; distinguish variance-selection from hard-problem-selection
- Scope refinement: primary claim should be "filtering near-zero-variance problems" not "variance predicts full training trajectory"

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, and let me build on Prof. Pax's mechanistic refinement to formalize a hypothesis that addresses all the concerns raised so far. The refinement actually *strengthens* the hypothesis by making it more precisely falsifiable. We shouldn't claim that frozen-model variance perfectly predicts the full training trajectory — that's an overclaim. The stronger, cleaner claim is: **variance-guided subset selection, using k=8 frozen-model completions per problem to compute p_i*(1-p_i), concentrates GRPO gradient steps on problems with nonzero initial gradient signal, yielding higher pass@1 improvement on HumanEval+ per gradient step than random-N subset RLEF over 20–50 GRPO steps.**

The mechanistic sub-prediction: the variance-selected subset should have lower `frac_reward_zero_std` during actual GRPO training than the random subset. This connects the selection criterion to the training mechanism through a directly observable TRL metric — no new instrumentation needed.

The confound (variance vs difficulty) is addressable through experimental design: report (a) mean and distribution of p_i for variance-50 vs random-50, (b) `frac_reward_zero_std` for both throughout training, (c) HumanEval+ pass@1 improvement curves. If variance-50 outperforms random-50 on pass@1 AND has lower `frac_reward_zero_std`, mechanistic hypothesis confirmed.

**Key Points:**
- Formalized hypothesis: variance-guided selection (k=8 frozen profiling) yields higher HumanEval+ pass@1 improvement per gradient step than random-N at 20–50 GRPO steps
- Mechanistic sub-prediction: variance-50 has lower TRL `frac_reward_zero_std` than random-50 during training
- Three-condition experiment (variance-50 vs random-50 vs full-374) provides necessary baselines for both efficiency and effectiveness claims
- No new benchmark required: MBPP training split + HumanEval+ EvalPlus evaluation, EvalPlus correctness scoring

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down — and I mean this constructively.

**Concern 1: The 80% efficiency claim is mathematically risky.** If both full-set and variance-50 improve by only 0.5 absolute pass@1 points (within EvalPlus measurement noise), "within 80%" becomes meaningless. The hypothesis needs a minimum effect size pre-specification.

**Concern 2: The HumanEval+ sample size issue.** HumanEval+ has 164 problems. Standard error on pass@1 ≈ √(p(1-p)/n) ≈ √(0.25/164) ≈ 3.9 percentage points. A 2–3 point improvement is within measurement noise for a single evaluation run. Need multi-checkpoint evaluation or multiple eval runs.

**Concern 3: k=8 profiling noise.** For a problem with true p=0.1, the variance estimate p̂*(1-p̂) from k=8 completions ranges widely — low-variance and high-variance problems can be confused. k=16 would substantially reduce this noise; k=8 is a deliberate tradeoff.

**Concern 4: "Per gradient step" metric operationalization.** Compare pass@1 at steps 10, 20, 50 for all three conditions — not just final value. This controls for learning rate differences between conditions.

**Mitigation Strategies:**
- Pre-specify minimum detectable effect ≥ 2 absolute pass@1 points on HumanEval+
- Multi-checkpoint evaluation (steps 10, 20, 50) with EvalPlus correctness scoring
- Acknowledge k=8 noise limitation; k=8 aligns with GRPO group size G=4-8 (architecturally justified)
- Operationalize efficiency as pass@1 at step 50 (primary) + learning curve slope steps 10→50 (secondary)

**Key Points:**
- Pre-specify minimum effect size ≥ 2 absolute pass@1 points to avoid unfalsifiable SQ3
- Multi-checkpoint evaluation (steps 10, 20, 50) stabilizes measurement vs single-eval noise
- k=8 noise is a limitation but justified by architectural alignment with GRPO group size; acknowledge in paper
- "Per gradient step" metric operationalized as multi-checkpoint pass@1 curves

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Now we're onto something! Let me build on Prof. Rex's concerns to propose a refined hypothesis frame. What if we think about this not just as a data selection paper, but as the first characterization of the *MBPP learning landscape* under binary execution reward GRPO?

The frozen-model profiling phase (374 problems × k=8 completions) produces a distribution: p_i*(1-p_i) for each problem. This distribution is itself a novel scientific contribution — it tells us what fraction of MBPP is learnable vs too-easy vs too-hard for DeepSeek-Coder-7B at this capability level. That's publishable data that doesn't require any training to run!

The 80% efficiency threshold in SQ3 is connected to the variance distribution shape. If X% of MBPP problems are near-zero-variance, then selecting top-50 by variance gives you the learnable cluster. If that cluster is ~13% of MBPP (50/374), the hypothesis predicts that the "learnable cluster" is approximately 13% of MBPP. The variance distribution shape makes the 80% efficiency claim *interpretable* — not just "did it work?" but "why?"

The multi-checkpoint evaluation also enables a secondary contribution: mapping the *learning dynamics* of variance-selected vs random RLEF. If variance-50 shows faster early improvement (step 10) but plateaus sooner, that tells us about learning zone exhaustion — a novel finding independent of whether the overall pass@1 claim holds.

**Key Points:**
- Frozen-model variance distribution across MBPP is itself a novel contribution (first for DeepSeek-Coder-7B on MBPP)
- Multi-checkpoint learning curves reveal whether variance-50 shows faster early convergence and later plateau
- Variance distribution shape makes the 80% efficiency claim interpretable: predicts the size of the learnable cluster
- Proposed frame: "offline variance profiling characterizes the MBPP learning landscape, and learning-zone subset selection yields higher HumanEval+ improvement per gradient step than random selection over 20–50 steps"

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's reframe is scientifically elegant — but let me ensure we don't expand scope beyond what's testable. Let me consolidate the hypothesis to its most testable, falsifiable form.

**Primary Hypothesis (H1):** Under fixed GRPO hyperparameters (use_vllm=False, G=4, generation_batch_size=4, 50 training steps), variance-selected RLEF (top-50 MBPP problems by frozen-model binary reward variance p*(1-p), k=8 completions) achieves strictly higher HumanEval+ pass@1 improvement over baseline than random-50 RLEF, measured by EvalPlus correctness evaluation at the 50-step checkpoint.

**Secondary Hypothesis (H2 — mechanism):** Throughout GRPO training, variance-selected problems exhibit lower mean `frac_reward_zero_std` than random-selected problems, confirming that variance profiling successfully identifies learnable examples with nonzero GRPO gradient signal.

**Tertiary Hypothesis (H3 — efficiency):** HumanEval+ pass@1 improvement from variance-50 at 50 steps is ≥ 80% of HumanEval+ pass@1 improvement from full-374 at 50 steps, provided both conditions achieve ≥ 2 absolute pass@1 points improvement over baseline.

Multi-checkpoint evaluation (steps 10, 20, 50) becomes a secondary analysis to characterize learning dynamics — not required for H1/H2/H3 falsification but scientifically valuable.

**Key Points:**
- H1 (primary): variance-50 > random-50 in HumanEval+ pass@1 improvement at 50 GRPO steps
- H2 (mechanism): variance-50 has lower `frac_reward_zero_std` than random-50 throughout training
- H3 (efficiency): variance-50 achieves ≥ 80% of full-374 performance (conditional on ≥ 2pp improvement)
- All three testable with MBPP + DeepSeek-Coder-7B + TRL GRPO + EvalPlus — no new infrastructure

### Exchange 9

🎯 **Dr. Sage** (Research Impact Evaluator):

This matters because the three-hypothesis structure Prof. Vera formalized creates a research contribution that survives under any outcome:

**If H1 succeeds:** Clear positive result — variance-guided frozen profiling outperforms random selection for binary execution reward RLEF in code generation. Practical, deployable method with empirical evidence in a new domain (code gen vs math reasoning in all prior work).

**If H1 fails but H2 succeeds:** The mechanism holds (variance-selected problems do have lower `frac_reward_zero_std`) but doesn't translate to final pass@1 improvement. Still publishable as "variance profiling identifies learnable examples but short RLEF on a small subset doesn't reliably transfer to HumanEval+." Opens follow-up question about required step budget.

**If both H1 and H2 fail:** Null result — closes the question of whether offline variance profiling is a viable substitute for online selection methods. Publishable as negative result.

Under any outcome, the MBPP variance distribution data is novel empirical data about code LLM RLEF learning landscapes that benefits future researchers.

**Key Points:**
- Experiment survives under any outcome — all three H1/H2/H3 conditions produce publishable findings
- Core impact: first empirical characterization of binary execution reward variance distribution across MBPP for a 7B code LLM
- Field contribution survives null H1: negative result closes the offline-vs-online selection question for code RLEF
- Novelty confirmed: no prior paper tests offline frozen-model variance profiling for binary execution reward code RLEF

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's verify the experiment is technically sound. Running through the implementation requirements:

**Profiling Phase:** DeepSeek-Coder-7B-Instruct on MBPP (374 problems), k=8 i.i.d. completions per problem, no gradient computation. At generation_batch_size=4: 374 × 8 / 4 = 748 forward passes ≈ 748 × 1.5s ≈ 19 minutes. Feasible.

**Training Phase (3 conditions):**
- Variance-50: 50 problems × 50 steps × G=4 completions per step; at generation_batch_size=4: ~3.5h per condition
- Random-50: same cost as variance-50
- Full-374: ~6.5h at generation_batch_size=4
- Total: ~13.5 hours on H100 NVL — within a single session

**EvalPlus Evaluation:** 164 × 8 = 1,312 forward passes per checkpoint ≈ 5 min per eval. Negligible cost.

**TRL `frac_reward_zero_std` metric:** Already logged by TRL during training. Zero additional implementation cost.

**Conclusion:** Fully feasible under h-e1 constraints. Profiling phase is ~19 minutes, not 30 min (the "< 30 min" claim assumed faster hardware) — but still clearly cheap relative to training.

**Key Points:**
- Profiling phase: ~19 min with generation_batch_size=4
- Training phase: ~3.5h/condition × 3 conditions + eval ≈ 13h H100 total
- TRL `frac_reward_zero_std` mechanism test is zero additional implementation cost
- Experiment fully feasible under h-e1 environment constraints; no new infrastructure needed

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Pax's feasibility analysis confirms the experiment is tractable. Let me now synthesize the complete, convergence-ready hypothesis.

**Core Hypothesis Statement:**

Under the constraint of short RLEF (20–50 GRPO steps, use_vllm=False, G=4, generation_batch_size=4) for code generation, selecting the top-50 MBPP training problems by per-problem binary execution reward variance (p_i*(1-p_i), computed via k=8 i.i.d. completions from a frozen DeepSeek-Coder-7B-Instruct model) achieves higher HumanEval+ pass@1 improvement per gradient step than random-50 subset RLEF, because variance profiling concentrates GRPO gradient steps on problems within the model's current learning zone (nonzero within-group reward variance), while random selection includes ~69% zero-gradient problems that waste training capacity.

**Testable Predictions:**
1. **(P1 — Primary):** Variance-50 achieves ≥ 2 absolute pass@1 points improvement on HumanEval+ at 50 GRPO steps, and this improvement exceeds random-50's improvement by ≥ 1 absolute pass@1 point.
2. **(P2 — Mechanism):** Mean `frac_reward_zero_std` is lower for variance-50 than random-50 throughout GRPO training (at checkpoints step 10, 20, 50).
3. **(P3 — Efficiency):** If both variance-50 and full-374 achieve ≥ 2pp HumanEval+ improvement, variance-50 achieves ≥ 80% of full-374's improvement using only ~13% of training problems.

**Null Hypothesis (H0):** There is no significant difference in HumanEval+ pass@1 improvement between variance-selected and random-selected RLEF subsets of equal size (N=50) at 50 GRPO steps.

**Key Points:**
- Hypothesis addresses ALL persona concerns: measurement noise (multi-checkpoint eval), confound control (reporting p_i distribution), mechanism validation (frac_reward_zero_std), feasibility (13h H100 budget), scope (short RLEF)
- Three predictions: P1 effectiveness, P2 mechanism, P3 efficiency — each independently falsifiable
- H0 null is clean and testable with a two-sample test on HumanEval+ pass@1 improvement
- ALL convergence criteria now met: SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

I've pushed hard on this hypothesis, and Dr. Ally's synthesis has addressed my core concerns. Final stress-test to confirm convergence is warranted.

**Remaining concern: SQ4 (Code-LLaMA-7B replication).** Correctly scoped out of the primary hypothesis. Can be extension experiment if H100 budget allows (~7h additional compute). Flag as "stretch goal."

**Remaining concern: k=8 profiling vs G=4 training group-size mismatch.** Should be quantified by checking ranking stability between k=4, k=8, k=16 — computable from profiling data at zero extra cost.

**Status: ALL six convergence criteria satisfied.**
- SPECIFIC ✅: "top-50 MBPP by frozen-model binary variance outperforms random-50 in HumanEval+ pass@1 per GRPO step"
- MECHANISM ✅: "variance profiling concentrates GRPO steps on nonzero-gradient problems via p*(1-p) approximation of σ = √(k(G-k))/G"
- PREDICTIONS ✅: P1 (effectiveness), P2 (mechanism via frac_reward_zero_std), P3 (efficiency ≥ 80% of full-374)
- NOVELTY ✅: "first offline frozen-model variance profiling for binary execution reward code RLEF on MBPP/HumanEval+"
- FEASIBILITY ✅: "13h H100, TRL GRPO, EvalPlus, no new benchmark or annotation"
- OBJECTIONS ✅: measurement noise (multi-checkpoint), confound (report p_i distribution), efficiency threshold (conditional on ≥ 2pp)

**I'm satisfied. This hypothesis is ready for Phase 2B.**

**Key Points:**
- SQ4 (Code-LLaMA-7B) deferred to extension experiment — optional if H100 budget allows
- k=8 vs G=4 mismatch: note as deliberate design decision, quantify ranking stability
- All 6 convergence criteria met — discussion CONVERGED
- Proceed to Final Assessments

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The offline frozen-model profiling paradigm is a genuine paradigm shift in RLEF data selection — all prior work (VIGOR, Sun et al., Prompt Replay, LZE) requires the training loop to be running to compute the selection signal. Separating "profile once, train anywhere" creates a new deployment pattern for RLEF experiments. The secondary contribution — first empirical characterization of MBPP binary reward variance distribution for a 7B code LLM — stands independently of the training outcome and opens new research directions on frozen inference as a cheap RLEF oracle.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The three-hypothesis structure (H1 effectiveness, H2 mechanism, H3 efficiency) is precisely falsifiable. H1 has a clear pre-specified minimum effect size (≥ 2pp on HumanEval+, ≥ 1pp gap over random). H2 is testable via TRL's built-in `frac_reward_zero_std` metric at zero implementation cost. H3 is conditional on both conditions showing meaningful improvement, avoiding the unfalsifiable-efficiency-claim failure mode. Multi-checkpoint evaluation (steps 10, 20, 50) controls for single-eval measurement noise.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** The experiment produces publishable findings under any outcome: positive result contributes a practical offline selection method for code RLEF; negative result closes the offline-vs-online selection question for binary execution rewards. The primary novel contribution — first offline variance profiling for binary execution reward RLEF in code generation — fills a gap not covered by Sun et al. 2025, VIGOR, or any existing data selection paper. The MBPP learning landscape characterization is a standalone dataset contribution.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** The experiment is fully feasible under verified h-e1 constraints. Profiling phase: ~19 min at generation_batch_size=4 (embarrassingly parallel, no gradient computation). Training phase: ~3.5h/condition × 3 conditions = ~10.5h. EvalPlus evaluation: ~5 min per checkpoint. Total: ~13h H100 NVL — within a single session. TRL `frac_reward_zero_std` mechanism test is zero additional implementation cost. Mechanism is mathematically sound.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The hypothesis that emerged from this discussion is both novel and rigorously testable. Under the constraint of short RLEF (20–50 GRPO steps, use_vllm=False, G=4), selecting top-50 MBPP training problems by per-problem binary execution reward variance — computed via k=8 frozen DeepSeek-Coder-7B-Instruct completions, yielding p_i*(1-p_i) — achieves higher HumanEval+ pass@1 improvement per gradient step than random-50 RLEF, because variance profiling concentrates training on the model's current learning zone.

The mechanism is exact: GRPO gradient magnitude is directly governed by within-group reward variance (σ = √(k(G-k))/G), which is zero when all G completions succeed or all fail. With 69.25% of groups producing zero gradient at G=4 (Gradient Starvation paper), random selection wastes ~69% of gradient steps. Variance-guided selection preferentially includes problems where k ∈ {1,2,3} of G=4 completions succeed — concentrating gradient signal across all training steps.

The contribution is three-fold: (1) first offline frozen-model profiling approach for binary execution reward RLEF selection in code generation; (2) first characterization of per-problem binary reward variance distribution across MBPP for a 7B code LLM; (3) a 3-condition controlled experiment (variance-50, random-50, full-374) providing clean causal evidence unavailable in all prior online selection work.

Three testable predictions: P1 — variance-50 achieves ≥ 2pp HumanEval+ improvement and ≥ 1pp gap over random-50 at 50 steps; P2 — variance-50 shows lower mean TRL `frac_reward_zero_std` than random-50 throughout training; P3 — if both conditions improve by ≥ 2pp, variance-50 achieves ≥ 80% of full-374's improvement using only 13% of training problems.

All three testable with MBPP + HumanEval+ + EvalPlus + TRL GRPO + DeepSeek-Coder-7B-Instruct — no new benchmark, no annotation, no synthetic data.

### Emerged Hypothesis Summary

#### Core Statement
**Hypothesis ID:** H-VarianceGuidedRLEF-v1
**Confidence Level:** 0.78

Under short RLEF (20–50 GRPO steps, use_vllm=False, G=4), if variance-guided subset selection is applied (top-50 MBPP problems by frozen-model binary reward variance p_i*(1-p_i), k=8 completions), then HumanEval+ pass@1 improvement per gradient step will exceed random-50 subset RLEF, because variance profiling concentrates GRPO gradient steps on problems with nonzero within-group reward variance, while random selection includes ~69% zero-gradient problems.

**Null Hypothesis:** There is no significant difference in HumanEval+ pass@1 improvement between variance-selected and random-selected RLEF subsets of equal size (N=50) at 50 GRPO steps.

#### Causal Mechanism
Per-problem binary reward variance p*(1-p) is a monotone proxy for the GRPO group gradient magnitude σ = √(k(G-k))/G. Frozen-model profiling with k=8 completions approximates p_i for each MBPP problem. Top-50 selection by p_i*(1-p_i) preferentially includes problems where G=4 GRPO groups are likely to have k ∈ {1,2,3} correct completions — nonzero gradient. This concentrates gradient signal in the training subset, reducing wasted computation from all-correct/all-incorrect groups.

#### Variables
- **Independent Variable:** Data selection method (3 levels: variance-50, random-50, full-374)
- **Dependent Variable (Primary):** HumanEval+ pass@1 improvement over baseline at 50 GRPO steps (EvalPlus correctness)
- **Dependent Variable (Secondary):** Mean TRL `frac_reward_zero_std` during GRPO training
- **Controlled:** Model (DeepSeek-Coder-7B-Instruct), hyperparameters (G=4, use_vllm=False, generation_batch_size=4), step budget (50), evaluation (EvalPlus)

#### Key Assumptions
- A1: k=8 frozen-model completions are sufficient to estimate per-problem pass rates with adequate ranking stability
- A2: The frozen-model variance ranking is stable enough over 20–50 GRPO steps to distinguish learnable from non-learnable problems
- A3: HumanEval+ pass@1 improvement is a valid proxy for code generation capability improvement (established by RLEF paper)
- A4: The MBPP training split (374 problems) is heterogeneous enough in difficulty to produce meaningful variance stratification for DeepSeek-Coder-7B

#### Predictions
- **P1 (Primary):** Variance-50 achieves ≥ 2 absolute pass@1 points improvement on HumanEval+ at 50 GRPO steps, with improvement ≥ 1pp greater than random-50
- **P2 (Mechanism):** Mean `frac_reward_zero_std` is lower for variance-50 than random-50 at all checkpoint evaluations (steps 10, 20, 50)
- **P3 (Efficiency):** Conditional on both achieving ≥ 2pp improvement, variance-50 achieves ≥ 80% of full-374's HumanEval+ improvement

#### Novelty
- No prior paper has applied offline frozen-model variance profiling to binary execution reward RLEF for code generation
- All prior data selection work (VIGOR, Sun et al., Prompt Replay, LZE) uses online selection requiring active training
- First characterization of per-problem binary reward variance distribution across MBPP for a 7B code LLM

#### Scope & Boundaries
- Applies to: short RLEF (≤50 GRPO steps) on MBPP with binary execution reward and DeepSeek-Coder-7B-Instruct
- Does not apply to: full-epoch RLEF, scalar reward functions, non-code domains, models already fine-tuned extensively on MBPP
- Known limitations: k=8 profiling noise at extremes; frozen-model variance drifts as model trains; group-size mismatch (k=8 profiling vs G=4 training)

#### Experimental Setup
- **Dataset:** MBPP training split (374 problems, existing standard benchmark)
- **Evaluation:** HumanEval+ via EvalPlus correctness scoring (164 problems)
- **Model:** DeepSeek-Coder-7B-Instruct (HuggingFace)
- **Training:** TRL GRPO trainer, use_vllm=False, G=4, generation_batch_size=4
- **Baselines:** Random-50 RLEF, Full-374 RLEF
- **Checkpoints:** Steps 10, 20, 50

#### Phase 2B Readiness Seeds
- **SH1 (Existence):** Per-problem binary reward variance distribution is heterogeneous across MBPP for DeepSeek-Coder-7B (testable via profiling alone)
- **SH2 (Mechanism):** Variance-guided selection reduces `frac_reward_zero_std` relative to random selection
- **SH3 (Comparison):** Variance-50 outperforms random-50 on HumanEval+ pass@1 improvement at 50 steps

#### Established Facts
- GRPO gradient magnitude ∝ within-group reward variance σ = √(k(G-k))/G (formal identity, bay-yearick-lab)
- 69.25% of GRPO groups produce zero gradient at G=4 under binary rewards (Gradient Starvation paper, arXiv:2605.07689)
- Difficulty-targeted selection reduces compute by 23–62% on math reasoning (Sun et al. 2025, arXiv:2506.05316)
- RLEF with binary execution reward on code generation is effective (Gehring et al. 2024, arXiv:2410.02089)
- EvalPlus correctness-based pass@1 evaluation is operational in h-e1 environment (confirmed)
- TRL GRPO trainer (use_vllm=False, generation_batch_size=4) is operational in h-e1 environment (confirmed)

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** k=8 profiling vs G=4 training creates a group-size mismatch — should be quantified via ranking stability analysis (k=4, k=8, k=16 comparison, computable from profiling data)
- **Concern 2:** SQ4 (cross-architecture Code-LLaMA-7B replication) is out of scope for primary hypothesis — extension experiment only if compute budget allows
- **Mitigation Strategy:** Document k-sensitivity as profiling diagnostic; pre-register Code-LLaMA-7B as stretch goal. Both are acknowledged limitations, not hypothesis-breaking concerns.
