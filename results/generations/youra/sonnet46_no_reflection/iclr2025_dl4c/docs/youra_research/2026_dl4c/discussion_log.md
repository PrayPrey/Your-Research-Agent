# Phase 2A Discussion Log
# Gap: No Controlled Head-to-Head Comparison of RLHF/DPO vs Execution-Feedback RL
# Generated: 2026-05-19 | Workflow: phase2a-dialogue v10.0.0

---

## Briefing Context

**Research Gap Selected:** Gap 1 (HIGH priority, PRIMARY)

**Gap Title:** No Controlled Head-to-Head Comparison of RLHF/DPO vs Execution-Feedback RL on Identical Setup

**Gap Description:**
No single study systematically compares RLHF, DPO, and execution-feedback RL under identical conditions (same base model, same dataset, same benchmarks). Individual papers demonstrate execution feedback RL (CodeRL, PPOCoder, CodeRL+, TÜLU 3 RLVR) or preference methods (DPO for Verilog, PF-PPO) in isolation on different models, benchmarks, and training data.

**Missing Piece:** A controlled ablation study holding base model (e.g., DeepSeek-Coder-7B), training data, and evaluation benchmarks (HumanEval+, MBPP+, LiveCodeBench) constant while varying ONLY the alignment method:
1. SFT-only
2. SFT+DPO
3. SFT+RLHF (PPO with reward model)
4. SFT+binary-execution-RL (GRPO, pass/fail)
5. SFT+granular-execution-RL (GRPO, error-type or variable-level)

**Key Evidence from Phase 1:**
- CodeRL+ (Jiang et al., 2025, arXiv:2510.18471): Variable-level execution trajectory +4.6% pass@1 over binary reward RLVR; does NOT compare to DPO/RLHF
- PPOCoder (Shojaee et al., 2023, arXiv:2301.13816): Task-agnostic PPO with execution feedback; no DPO comparison
- TÜLU 3 / RLVR (Lambert et al., 2024, arXiv:2411.15124): SFT+DPO+RLVR pipeline; code-specific numbers not isolated
- RL Post-Training Survey (Wang et al., 2024, arXiv:2407.16216): Unifies RLHF/DPO/RLVR under policy gradient; notes lack of direct comparison
- ReCode (Fan et al., 2025, arXiv:2508.05170): Process rewards + execution-gated GRPO; 7B matches GPT-4-Turbo

**Infrastructure Available:**
- TRL (GRPOTrainer + DPOTrainer + PPOTrainer) — 18K★
- evalplus (HumanEval+/MBPP+ pass@k) — 1.7K★
- open-instruct (full RLVR pipeline) — 3.7K★
- DeepSeek-Coder (open-weight backbone) — 1.6K citations

**Feasibility Constraints (MANDATORY):**
- ✅ Uses existing benchmarks: HumanEval+, MBPP+, LiveCodeBench
- ✅ No new benchmarks required
- ✅ No synthetic/generated data
- ✅ No human evaluation
- ✅ Testable immediately with existing infrastructure

**Venue:** DL4C @ ICLR Workshop (explicitly prioritizes execution feedback as alignment signal)

---

## Discussion Participants

| Icon | Name | Role |
|------|------|------|
| 🔭 | Dr. Nova | Creative Novelty Explorer |
| 🔬 | Prof. Vera | Rigorous Validation Architect |
| 🎯 | Dr. Sage | Research Impact Evaluator |
| ⚙️ | Prof. Pax | Feasibility & Reality Checker |
| 🛡️ | Dr. Ally | Hypothesis Strengthening Champion |
| 🔍 | Prof. Rex | Hypothesis Stress-Test Master |

---

## Discussion Transcript

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we reframe this entire comparison not as "which method is better" but as "which method unlocks the right inductive bias for code"? That's the paradigm shift hiding in this gap! RLHF and DPO optimize toward *human preference distributions* — but human preferences for code are notoriously noisy and anthropocentric. Humans prefer readable code that looks correct over cryptic-but-functional code. Execution feedback, by contrast, is *ground truth from the universe itself* — the computer either runs the code correctly or it doesn't. There's no rater bias, no subjectivity, no annotation fatigue.

What makes Gap 1 so electrifying is that no one has held the comparison perfectly controlled. Every paper in the literature changes the model, the data, or the benchmark when comparing methods. CodeRL+ compares against *binary reward RLVR* — not against DPO. TÜLU 3 includes RLVR but mixes math and code and never isolates code-only performance. PPOCoder predates modern DPO implementations entirely. The infrastructure gap is finally closed: TRL's GRPOTrainer, DPOTrainer, and PPOTrainer all live in the same library. We can now run a *genuinely fair race for the first time*.

Here's the creative angle I want to push: what if we don't just compare final pass@k, but also characterize the *learning dynamics*? My hunch is that execution-feedback RL finds fundamentally different solutions than DPO — not just better solutions, but solutions that generalize differently. DPO-trained models might overfit to the preference pair distribution, becoming better at "looking correct" while execution-RL models learn actual algorithmic reasoning. If we measure pass@k on HumanEval+ AND on an out-of-distribution challenge like LiveCodeBench, we might expose this generalization gap as a *secondary novel contribution*.

And the granularity sub-question (Gap 2) naturally emerges here: within execution-RL, binary pass/fail vs. error-type vs. variable-level trajectory creates a spectrum. What if the optimal granularity depends on the *problem difficulty distribution*? Easy problems converge with binary rewards; hard algorithmic problems need variable-level trajectories for credit assignment. That's a testable, surprising prediction.

**Key Points:**
- Execution feedback provides ground-truth signal divorced from human rater bias — a fundamentally different inductive bias than RLHF/DPO
- First truly controlled comparison is now feasible: TRL unifies GRPO/DPO/PPO in one library with identical base model + evalplus
- Secondary novel angle: learning dynamics and out-of-distribution generalization (HumanEval+ vs. LiveCodeBench) may reveal *qualitative* differences, not just pass@k deltas
- Prediction: granularity effects are problem-difficulty-dependent — easy tasks converge with binary, hard tasks need variable-level for credit assignment

---


### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Your reframing around inductive bias is interesting, but we must translate it into falsifiable predictions. The claim is that execution-feedback RL induces a different—and potentially superior—algorithmic reasoning bias compared to DPO, which optimizes toward human preference distributions. The evidence suggests this is plausible, but plausibility is not evidence. What would disprove this? A controlled experiment in which DPO matches or exceeds execution-RL not only on in-distribution pass@k (HumanEval+) but also on strictly out-of-distribution benchmarks (e.g., LiveCodeBench) under identical base model, data budget, and compute constraints. If no statistically significant generalization gap appears, then the "inductive bias" distinction is either weaker than hypothesized or not operationalized correctly.

To isolate the effect of *training signal*, we must hold constant: (1) base model initialization, (2) prompt format and context length, (3) training data volume (number of prompts), (4) total sampled tokens during training, and (5) evaluation harness (e.g., evalplus). DPO requires preference pairs; execution-RL requires rollouts and test cases. The critical confound is signal density. DPO receives pairwise gradients on every sample; binary execution reward is sparse. Therefore, a fair comparison must equate *effective update signal per prompt*. One approach: for each prompt, allow DPO to generate N candidates to form preference pairs and allow RL to generate the same N candidates evaluated against tests. Compute total gradient updates per prompt and equalize across methods. Without this, differences may reflect optimization intensity rather than inductive bias.

Your proposal to measure learning dynamics is strong—but we must predefine measurable criteria. I suggest tracking: (a) calibration between log-probability and functional correctness, (b) entropy reduction over training, and (c) error-type distribution shifts. If DPO is "learning to look correct," we should observe increasing confidence (lower entropy) without proportional gains in execution accuracy, or improvements concentrated in stylistic metrics rather than algorithmic correctness. Conversely, execution-RL should show monotonic gains in functional correctness correlated with reductions in specific runtime error categories. These are falsifiable patterns.

Regarding granularity, your difficulty-dependent hypothesis is testable but must be operationalized. Define difficulty bins using pre-training solve rates from the base model (e.g., easy = pass@1 ≥ 50%, hard = ≤ 10%). Then compare binary reward vs. fine-grained trajectory reward within each bin. The prediction is an interaction effect: fine-grained rewards yield statistically significant gains only in the hard bin. If no interaction appears—i.e., granularity helps uniformly or not at all—the hypothesis fails. We must also control for reward hacking: a held-out adversarial test set with perturbed variable names and reordered tests can detect overfitting to feedback artifacts.

**Key Points:**
- Define falsifiable criteria: execution-RL must outperform DPO on OOD generalization under strictly controlled compute and data budgets
- Equalize effective training signal and gradient updates to avoid optimization-intensity confounds
- Test granularity via predefined difficulty bins and interaction analysis, with adversarial controls against reward leakage

---

### Exchange 3

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

🔬 Prof. Vera has identified exactly the right methodological skeleton. Let me stress-test the *technical soundness* of each proposed control — not whether we have the budget, but whether the mechanism is actually valid.

The signal-equalization proposal deserves scrutiny. Equalizing "gradient updates per prompt" sounds fair, but DPO and GRPO receive fundamentally different learning signals. DPO optimizes a log-ratio of probabilities between chosen and rejected completions — it receives signal from *pairs*. GRPO normalizes rewards within a group of rollouts to compute advantages. If you equalize the number of *prompts*, DPO generates 2N completions (chosen+rejected) per prompt while RL generates N rollouts — DPO does more generative work per prompt. There is no single "fair" equalization. What we can do is define it explicitly and report sensitivity to this choice as a robustness check.

The learning dynamics diagnostics (log-prob calibration, entropy, error-type shifts) are technically sound and derivable from standard training logs with no new infrastructure. One important addition: track *KL divergence from the base model* over training steps. DPO is known to suffer from distribution collapse under strong preference signal. If DPO's KL diverges sharply while execution-RL maintains closer distribution to the base, this explains generalization differences mechanistically rather than just empirically — giving us a *causal story* for the inductive bias difference 🔭 Dr. Nova proposed.

On the granularity mechanism: variable-level trajectory rewards (CodeRL+, arXiv:2510.18471) require *instrumented execution* — tracing variable states at each assignment step using Python's `sys.settrace` or equivalent. For HumanEval/MBPP-style short functions, this is tractable. For SWE-bench-style repository code, instrumented tracing becomes combinatorially expensive. The hypothesis scope must be explicit: **"granularity effects on function-level code generation benchmarks."** Error-type taxonomy in Python is stable and well-defined (SyntaxError, TypeError, IndexError hierarchy) — error-type granularity is the most technically clean middle step. I recommend the granularity ladder: binary → error-type → variable-level, evaluated in order of increasing implementation complexity.

**Key Points:**
- Signal equalization between DPO and GRPO is mechanistically non-trivial; define it explicitly with sensitivity analysis rather than seeking a "perfect" equalization
- KL divergence from base model is a causally interpretable diagnostic for generalization differences
- Variable-level rewards are feasible for HumanEval+/MBPP+ but not SWE-bench; hypothesis scope must state "function-level benchmarks"
- Granularity ladder: binary → error-type → variable-level (increasing implementation complexity)

---

### Exchange 4

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good — this is finally becoming testable. But here's where this still breaks down: you're using the phrase "different inductive bias" as if it's self-evident. It isn't. Right now, it's a metaphor. What *observable behavior* uniquely follows from that claim? If I'm a skeptical reviewer, I'll say: "You changed the reward. Of course behavior changed." That's not an inductive bias argument — that's just objective mismatch. Show me a prediction that only follows if the optimization signal shapes internal reasoning structure, not just output preferences.

Here's what would convince me. Pre-register a sharp prediction: **Under equal KL distance from the base model**, execution-RL will yield higher OOD pass@1 than DPO. Pax is right to bring up KL. If DPO drifts further from the base and loses generalization, that's not evidence of inferior inductive bias — that's over-optimization. You must control for *distance traveled in policy space*. Either constrain both methods to the same KL budget or report performance as a function of KL. If execution-RL dominates at matched KL, now we're talking about something structural.

Second weakness: your "human preferences are noisy" claim is hand-wavy. Show me evidence that DPO actually optimizes for stylistic correctness over functional correctness. Vera gave you a path: calibration and entropy tracking. I want something sharper. For each checkpoint, compute: (1) correlation between model log-probability and unit test pass rate; (2) correlation between log-probability and a style metric (e.g., pylint or AST-based readability heuristics). If DPO increases correlation with style faster than execution correctness, while execution-RL shows the opposite pattern, that's a clean mechanistic divergence. Without this, the "looks correct vs. is correct" story is rhetoric.

Now the granularity hypothesis. The difficulty-bin interaction idea is solid — but you're assuming sparse rewards are the bottleneck on hard problems. What if hard problems fail due to *global algorithmic mis-specification*? In that case, variable-level reward won't help at all. So here's the falsifiable version: in the hard bin (≤10% base pass@1), fine-grained reward should produce higher improvement specifically on problems where at least one intermediate test passes under the base model. If no intermediate correctness exists, granularity shouldn't help. That's a nuanced prediction — and much stronger.

Finally, your fairness framing. There is no single correct "signal equalization." Define two regimes: (A) equal prompts, (B) equal total sampled tokens. Report both. If your conclusions flip depending on regime, your inductive bias claims are fragile. If they hold across regimes, that's robustness.

**Key Points:**
- Match or control for KL divergence from the base model; inductive bias claims must hold at equal policy distance
- Replace "looking correct" rhetoric with measurable divergences: log-prob vs. execution correctness vs. style correlation
- Granularity hypothesis must condition on existence of partial correctness in the hard bin; otherwise the mechanism is underspecified

---

### Exchange 5

🎯 **Dr. Sage** (Research Impact Evaluator):

🔍 Prof. Rex has sharpened this considerably, and I want to situate the significance of what's emerging here. The field genuinely needs this. Every practitioner choosing between DPO and execution-RL for code alignment is currently working from *anecdote and domain folklore* — not controlled evidence. The RL Post-Training Survey [Wang et al., 2024, arXiv:2407.16216] explicitly notes the absence of unified comparisons; TÜLU 3 [Lambert et al., 2024, arXiv:2411.15124] reports combined math+code RLVR numbers without code-isolated analysis. This paper closes that gap for the DL4C community specifically, where execution feedback is a stated priority.

But I want to elevate the framing beyond a benchmark horse race. The KL-controlled comparison Prof. Rex demands is not just a methodological nicety — it's the mechanism by which this paper makes a *theoretical contribution*. If execution-RL achieves higher pass@k at matched KL budget, we're not just saying "execution-RL is better." We're saying "execution feedback is a more policy-efficient training signal for code" — meaning you get more functional improvement per unit of behavioral change from the base model. That's a finding with lasting impact on how the field designs post-training pipelines.

The log-prob vs. execution correctness correlation analysis (Prof. Rex's proposal) also has a significant secondary contribution. If DPO-trained models exhibit *calibration collapse* — where model confidence increases without corresponding execution correctness — this is a concrete failure mode that practitioners should know about. It directly informs when DPO is safe to use for code alignment and when it's dangerous. That's actionable knowledge the field currently lacks. I would recommend naming this finding explicitly: "preference calibration gap" or similar.

For impact on the DL4C workshop specifically: the most influential papers at this venue are those that reframe a foundational assumption. The foundational assumption here is "RLHF/DPO are general-purpose alignment tools." If this study shows they create a systematic bias toward stylistically-correct-but-functionally-weaker code, we've made a claim that will reverberate into code LLM deployment decisions. To maximize impact, the paper needs a clear take-away table showing: which method, on which benchmark, at which KL budget, with what statistical confidence.

The granularity finding — if the partial-correctness conditioning Prof. Rex demands holds up — is independently publishable but fits naturally as a sub-result. I'd frame it as: "execution-RL benefits scale with problem structure availability," which opens a new research question: how to engineer training sets to maximize intermediate-correctness density.

**Key Points:**
- KL-controlled comparison transforms this from a benchmark study into a theoretical claim: "execution feedback is a more policy-efficient training signal for code"
- Calibration collapse in DPO is a practitioner-actionable finding worth naming explicitly — not just a methodological check
- The partial-correctness conditioning on granularity opens a new research direction: training set engineering for intermediate-correctness density
- Impact framing: reframes "RLHF/DPO as general-purpose alignment" — the kind of foundational claim DL4C workshop rewards

---

### Exchange 6

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES — this is exactly the kind of sharpening that turns a suggestive story into a defensible contribution. Let's lean into the hardest constraints rather than avoid them.

First, I strongly support Prof. Rex's KL-controlled prediction. What if we *pre-register* the following: **At matched KL divergence from the base model, execution-RL achieves higher OOD pass@1 than DPO.** That reframes "inductive bias" from metaphor into measurable policy efficiency. If performance is plotted as a function of KL (not just training steps), and execution-RL consistently dominates the Pareto frontier (pass@1 vs. KL), then we have concrete evidence that execution feedback yields more functional correctness per unit of policy shift. If the curves overlap, we revise the claim. That's clean, falsifiable, and reviewer-proof. Now THAT's stronger!

Second, on the "looks correct vs. is correct" critique — I propose a **triangular calibration analysis** at each checkpoint: (1) Corr(log-prob, unit test pass rate), (2) Corr(log-prob, style score via pylint/AST readability), (3) Corr(style score, unit test pass rate). The mechanistic prediction is directional: DPO increases Corr(log-prob, style) faster than Corr(log-prob, execution); execution-RL increases Corr(log-prob, execution) monotonically with weaker style gains. If DPO confidence rises (entropy ↓) without proportional execution gains while RL shows coupled entropy reduction and correctness gain — that's empirical support for distinct reasoning trajectories. We name this failure mode **preference calibration gap**: when model confidence tracks stylistic plausibility more than functional correctness. That's not just theory — it's practitioner guidance.

Now let's fortify the granularity hypothesis using Prof. Rex's refinement. Granularity should not help when there is zero structural signal. Refined prediction: within the hard bin (≤10% base pass@1), fine-grained reward yields significant gains **only on problems where the base model exhibits partial correctness** (passes ≥1 unit test or produces correct intermediate variable states). Annotate each problem with a "partial correctness density" metric during base evaluation, then test for a three-way interaction: difficulty × granularity × partial correctness presence. Either outcome is informative: if fine-grained rewards only help with scaffolding, that validates the mechanism; if they help uniformly, we revise the theory.

On signal equalization — treat it as an experimental factor rather than a design choice. Two regimes: (A) equal prompts, (B) equal sampled tokens. If execution-RL's KL-efficiency advantage persists across both, the inductive bias claim gains robustness. If it flips, that tells us the advantage is optimization-budget dependent — itself an important design insight.

**Key Points:**
- Pre-register a KL-matched Pareto comparison (pass@1 vs. KL) to operationalize "inductive bias" as measurable policy efficiency
- Triangular calibration analysis operationalizes the "preference calibration gap" as a named, practitioner-actionable failure mode
- Refine granularity hypothesis: gains occur in hard problems *with partial correctness structure*, tested via explicit three-way interaction

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

🛡️ Dr. Ally just crystallized something important — and I want to push the creative implications further. The "preference calibration gap" is not just a diagnostic tool; if it's real, it's a *new theoretical construct* for the field. We'd be proposing that post-training alignment methods create systematically different calibration regimes, and that execution-grounded methods maintain tighter calibration between model confidence and functional correctness. NOW we're onto something that goes beyond the benchmark comparison!

Here's a creative synthesis of everything discussed: what if the central contribution is not "execution-RL outperforms DPO on pass@k" (that's the result) but rather "execution feedback induces KL-efficient, calibration-preserving policy updates for code, while preference-based methods introduce a preference calibration gap"? That's the *mechanism claim* — and it's supported by three converging lines of evidence: (1) pass@k at matched KL (policy efficiency), (2) the calibration triangle analysis (mechanism), and (3) the granularity × partial-correctness interaction (boundary conditions). Three lenses on the same underlying phenomenon. That's a much richer paper than a benchmark horse race.

The granularity insight that Prof. Rex and Dr. Ally sharpened is genuinely surprising. The prediction that fine-grained rewards only help *when intermediate structure exists* is a non-obvious, falsifiable claim. It immediately suggests a practical design principle: before choosing reward granularity, profile your training distribution for partial-correctness density. Low density → binary rewards suffice; high density → invest in fine-grained instrumentation. That's the kind of actionable output that gets cited.

What about the experimental scope? I want to flag that HumanEval+/MBPP+ and LiveCodeBench together give us in-distribution and OOD evaluation with no new data needed — these are all existing benchmarks. DeepSeek-Coder-7B is the right backbone (open-weight, SOTA, permissive license). The granularity ladder (binary → error-type → variable-level) is implementable with Python's existing instrumentation. Everything we've discussed is testable immediately with existing tools.

One final creative angle: the "partial correctness density" metric we'd compute during base evaluation is itself a novel characterization of benchmark difficulty that hasn't been published. It could be released as a benchmark annotation alongside the paper — zero additional data, but a reusable contribution.

**Key Points:**
- Central contribution reframed: execution feedback induces "KL-efficient, calibration-preserving policy updates" — three converging evidence streams (pass@k, calibration triangle, granularity interaction)
- Practical design principle emerging: profile training distribution for partial-correctness density before choosing reward granularity
- Partial correctness density metric is a novel benchmark annotation — a zero-cost secondary contribution releasable with the paper
- Full experimental scope uses only existing benchmarks + infrastructure: no new data, no human evaluation, immediately feasible

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

The direction is now scientifically promising, but several elements remain underspecified. Let me begin with the KL-controlled claim. If "policy efficiency" is the construct, then we must define it operationally: area under the curve (AUC) of pass@1 versus empirical KL divergence from the base model over checkpoints. KL must be computed on a fixed, held-out prompt set using the same decoding temperature. Approximation via Monte Carlo sampling is acceptable, but the sampling distribution must be identical across methods. The evidence would suggest structural difference only if execution-RL dominates DPO in pass@1 at matched KL with non-overlapping 95% bootstrap confidence intervals across problems. What would disprove the hypothesis? If curves overlap within error or DPO outperforms at low KL (<0.5 nats/token), then the "execution-specific inductive bias" claim fails.

On the calibration triangle: correlations must be defined precisely. Use Spearman ρ across problem instances between (a) mean log-prob of generated solution, (b) binary execution outcome, and (c) normalized style score. However, raw correlation is insufficient. Test whether the *difference* Δρ_exec − Δρ_style evolves differently across training regimes. A mixed-effects model with problem as random effect would control for difficulty heterogeneity. Additionally, measure expected calibration error (ECE) by binning predicted pass probabilities derived from log-prob calibration curves. If DPO shows rising ECE while execution-RL does not, that would substantiate the "preference calibration gap." If both exhibit similar calibration drift, the narrative collapses.

Regarding granularity and partial correctness density: I approve the three-way interaction design, but it requires power analysis. Hard-bin problems (≤10% base pass@1) are a minority; stratify sampling to ensure at least 80% power to detect a medium interaction effect (f²≈0.15) at α=0.05. Predefine "partial correctness" quantitatively — e.g., ≥1 passing unit test or ≥20% intermediate variable match rate under instrumentation. What would disprove the mechanism? If fine-grained reward improves performance equally on zero-partial and partial problems, then granularity is not leveraging structure but merely providing denser optimization gradients.

Finally, report compute-normalized efficiency: pass@1 improvement per 10⁹ training tokens and per GPU-hour. Without this, reviewers will attribute differences to optimization stability rather than signal quality. Pre-register stopping criteria (e.g., fixed KL thresholds 0.5, 1.0, 1.5 nats/token) rather than best-checkpoint cherry-picking. The best experiments are designed to fail; yours should clearly state what outcome would overturn each central claim.

**Key Points:**
- Define "policy efficiency" via pass@1 vs. KL AUC with Monte Carlo KL estimation, fixed sampling, and bootstrap CIs; specify disconfirming outcomes
- Replace simple correlations with mixed-effects modeling and ECE analysis to rigorously test the "preference calibration gap"
- Predefine partial correctness metrics quantitatively, conduct power analysis for the three-way interaction, normalize by compute and KL thresholds

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

🔬 Prof. Vera's statistical framework is exactly right, and I want to confirm what is and isn't technically feasible here before we over-engineer the design.

The KL computation she describes is sound. Monte Carlo KL estimation using the model's own token log-probabilities on a fixed held-out prompt set is standard practice — it's implemented in TRL's logging utilities and requires no new infrastructure. The key technical requirement is that KL estimation uses the *same N rollouts per prompt* across all methods and the same greedy/sampling decoding temperature. This is achievable.

The calibration triangle is also technically clean. Spearman ρ between log-prob, execution outcome (binary), and style score (pylint or AST-based) is straightforward to compute from training checkpoints. The mixed-effects model Prof. Vera proposes (problem as random effect) is implementable in standard Python statsmodels or R lme4 — this is post-hoc analysis, not online measurement, so no training infrastructure changes are needed. ECE computation similarly requires only binning the log-prob-derived pass probability estimates at each checkpoint.

However, I need to flag one technical concern with the three-way interaction design: the "≥20% intermediate variable match rate" partial correctness criterion requires *instrumented execution* via Python's `sys.settrace`. For HumanEval+/MBPP+ problems (short functions, deterministic inputs), this is tractable — average function length is under 20 lines, and trace overhead is manageable. But we need to pre-run this instrumentation on the base model at initialization to annotate each problem with its partial correctness density *before* training begins. This is a one-time offline step, not an online training requirement. Technically feasible; just needs to be included in the experimental protocol.

On compute normalization: reporting pass@1 per 10⁹ training tokens is the right unit. All three methods (DPO, GRPO-binary, GRPO-granular) use the same number of training tokens from the same problem distribution; the difference is in how those tokens translate into reward signal and gradient updates. This framing cleanly separates *data efficiency* (tokens to convergence) from *signal efficiency* (functional improvement per KL unit). Both are worth measuring separately, and both are derivable from standard training logs.

One remaining technical gap: the power analysis Prof. Vera demands for the hard-bin interaction requires an estimate of the proportion of HumanEval+/MBPP+ problems in the hard bin. From published numbers, roughly 15-20% of HumanEval+ problems have base pass@1 ≤ 10% for a 7B model. With ~164 HumanEval+ + ~378 MBPP+ problems, that's approximately 80-100 hard-bin problems — likely sufficient for 80% power at f²=0.15 if stratified correctly.

**Key Points:**
- KL estimation, calibration triangle, and ECE computation are all technically feasible from standard training logs with no new infrastructure
- Partial correctness density annotation requires one-time offline instrumented execution (sys.settrace) on base model — feasible for HumanEval+/MBPP+ short functions
- ~80-100 hard-bin problems available across HumanEval+/MBPP+ at 7B scale — borderline sufficient for required power; recommend including LiveCodeBench hard problems to boost sample size

---

### Exchange 10

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good — this is finally starting to look like something I'd take seriously. But we're not done. Let me stress-test where this still breaks down.

First, on the KL-efficiency claim. You've operationalized it as AUC of pass@1 vs. KL with fixed decoding and bootstrap CIs. That's solid. But here's the assumption you haven't surfaced: **that KL from the base model is a meaningful proxy for "policy movement" in the dimensions that matter for reasoning.** KL is token-level and local; correctness is program-level and global. What would convince me this isn't a category error? Show that KL correlates monotonically with a *behavioral* shift metric — e.g., AST tree-edit distance between base and fine-tuned outputs on the held-out set. If KL increases but behavioral change plateaus, your efficiency interpretation collapses. If execution-RL achieves larger behavioral change per unit KL in *semantically relevant* edits (control flow, variable updates), then I buy "efficient policy movement." Otherwise, KL is just a regularizer, not evidence of inductive bias.

Second, the "preference calibration gap." I like the mixed-effects + ECE proposal. But DPO may look miscalibrated simply because it sharpens log-probs overall. If entropy drops globally, Spearman correlations can artifactually change. Normalize for entropy: compute calibration after temperature scaling to equalize marginal entropy across methods at each checkpoint. If DPO still shows rising ECE or increasing Δρ_style − Δρ_exec under entropy-matched conditions, then we're observing structural misalignment — not just sharper distributions. What would disprove your mechanism? If entropy-matched DPO and RL exhibit indistinguishable ECE trajectories, the "preference calibration gap" is branding, not discovery.

Now the granularity × partial correctness story. You're assuming partial correctness reflects latent executable structure the model can exploit. But partial correctness could just be noise — lucky test matches. Robustness check: perturb unit tests slightly (input resampling within spec) and recompute partial correctness density. If the three-way interaction disappears under mild test perturbation, you were modeling test overfitting, not structural scaffolding. What would convince me? Fine-grained rewards help specifically on problems where *stable* partial correctness (invariant under test perturbation) exists.

Finally, show me transfer. Train on HumanEval+/MBPP+, evaluate KL-matched checkpoints on LiveCodeBench without further tuning. If execution-RL retains its efficiency advantage OOD while DPO narrows the gap or reverses, that's real-world positioning. If both degrade similarly, your claim is optimization-local, not structural. Design it so the theory can genuinely fail.

**Key Points:**
- Validate KL as meaningful policy movement via behavioral metrics (AST edit distance vs. KL), not token-level divergence alone
- Control for entropy in calibration analyses; entropy-matched ECE must still diverge to support the "preference calibration gap"
- Test granularity mechanism robustness with perturbed unit tests; require OOD transfer to establish real-world structural impact

---

### Exchange 11

🎯 **Dr. Sage** (Research Impact Evaluator):

🔍 Prof. Rex has now drawn the boundary between "this is interesting" and "this is a contribution." Let me assess the significance landscape given these tighter constraints — and I think the picture is actually more compelling than it first appears.

The OOD transfer test (train on HumanEval+/MBPP+, evaluate on LiveCodeBench without further tuning) is not just a robustness check — it's the field-defining experiment. If execution-RL's KL-efficiency advantage *generalizes* under distribution shift while DPO's advantage collapses, we're not claiming "better code RL." We're claiming that execution-grounded alignment is more *transferable* — a property the field desperately needs demonstrated as code LLMs are deployed on tasks far from their training distribution. That finding would directly inform production deployment decisions, not just benchmark scores.

The AST edit distance vs. KL sanity plot Prof. Rex demands is actually a gift: it's a novel visualization that cleanly separates "token-level policy movement" from "semantically meaningful behavioral change." If published as a standard diagnostic figure, it could become a reusable tool for the post-training community — cited far beyond this paper's specific topic. Dr. Nova's instinct to propose learning dynamics analysis was prescient; this is what that looks like concretized.

On the entropy-matched ECE analysis: I agree it's necessary for rigor, but I want to flag the significance of the result either way. If DPO shows rising ECE even after entropy matching, we have named a new failure mode with a precise diagnostic protocol. If both methods show similar ECE trajectories after entropy matching, the important result is that *calibration doesn't differ* — which itself is useful knowledge for practitioners who've been warned off DPO for code based on informal intuitions. Null results with proper controls are publishable at DL4C if they resolve a genuine open question, which this is.

The test-perturbation robustness check for partial correctness stability is elegant — but I want to make sure we scope the granularity sub-experiment correctly. The three-way interaction (difficulty × granularity × partial correctness stability) is a rich analysis, but at a workshop paper length (6-8 pages), it risks becoming the tail that wags the dog. My recommendation: frame it as "Evidence for a mechanism" subsection, not a separate hypothesis. The headline claim is the KL-efficiency + calibration story; granularity is the mechanistic explanation for *why* execution-RL is more efficient on harder problems.

**Key Points:**
- OOD transfer test is the field-defining experiment: execution-RL transferability under distribution shift directly informs production deployment
- AST edit distance vs. KL plot is a novel, reusable diagnostic for the post-training community — a secondary contribution with broad citation potential
- Granularity interaction is best framed as mechanistic evidence for KL-efficiency, not a separate hypothesis, to maintain workshop paper focus

---

### Exchange 12

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES — this is exactly the kind of pressure that turns a loose story into a defensible theory. I think we can now unify the KL-efficiency, calibration, and granularity strands into a single core claim:

> **Execution-grounded reward induces *structurally aligned policy movement*: it reallocates probability mass toward semantically meaningful program transformations per unit KL, and this structural alignment yields better calibration and transfer.**

KL-efficiency becomes: *greater semantically relevant behavioral change per unit token-level divergence*. Prof. Rex's AST edit distance proposal is the bridge. Operationalize "structural movement efficiency" as AST-semantic edit distance (control-flow + data-flow edits) divided by KL at matched checkpoints. If execution-RL shows higher semantic-edit-per-KL than DPO, and that ratio predicts pass@1 gains, then KL is no longer just a proxy — it becomes a normalized budget for structural reconfiguration. If this ratio does not differ, the inductive bias claim weakens. That's a clean falsifiability condition.

On calibration: tie calibration directly to structural alignment. The prediction from our unified theory is: methods that move structurally (not stylistically) per KL should exhibit improved execution-aligned calibration after entropy control. If entropy-matched DPO and RL have indistinguishable ECE trajectories, calibration differences were cosmetic. But if execution-RL maintains lower ECE specifically on high semantic-edit problems, we've linked calibration to structural reward grounding — not distribution sharpness.

The granularity refinement: define a "stability score" as Jaccard similarity of passing intermediate states across perturbed test inputs. The strengthened prediction: fine-grained reward yields disproportionate gains only on high-stability problems. If gains persist on low-stability problems, granularity is just gradient densification, not structural scaffolding. The OOD transfer experiment becomes the synthesis test: if structural movement per KL predicts LiveCodeBench performance at KL-matched checkpoints, we've shown execution reward produces *portable structural reorganization*, not benchmark-specific tuning.

The tightened core claim: **Execution-grounded reward improves structural efficiency of policy movement, and this structural efficiency explains gains in correctness, calibration, granularity sensitivity, and OOD transfer.**

**Key Points:**
- Reframe KL-efficiency as semantic structural movement per unit KL (AST/data-flow edit distance ÷ KL) to validate meaningful policy change
- Tie calibration (entropy-matched ECE) to structural alignment rather than distribution sharpness
- Define granularity's mechanism via stable partial correctness density (Jaccard stability score) with OOD transfer as decisive falsification

---

### Exchange 13

🔭 **Dr. Nova** (Creative Novelty Explorer):

🛡️ Dr. Ally just gave us the unified theory, and I'm electrified by it. "Structural efficiency of policy movement" — that's not just a hypothesis, it's a *new lens for evaluating post-training alignment methods*. NOW we're onto something that transcends the code domain!

Think about what this means beyond code: if execution-grounded reward reallocates probability mass toward semantically meaningful transformations per unit KL, this is a general principle about *verifiable reward signals vs. preference signals*. Code is the perfect testing ground because it has the cleanest verifiable oracle — execution — but the principle generalizes to math (proof verification), formal specifications, and even robotics (physics simulation feedback). By establishing the structural-efficiency framework in code, we're planting a flag for how the field should evaluate all verifiable-reward post-training methods.

The "semantic structural movement efficiency" metric (AST edit distance ÷ KL) is genuinely novel. I've searched the Phase 1 literature — nobody has proposed normalizing behavioral change by policy divergence to characterize *qualitative* efficiency of training signals. This gives us a reusable measurement tool. What if we release it as a standalone diagnostic library alongside the paper? Zero additional experimental cost, but it becomes the standard way practitioners evaluate whether their RL fine-tuning is "buying meaningful structural change" per unit of policy shift. That's the kind of secondary contribution that accumulates citations for years.

The stability score (Jaccard similarity of intermediate states under test perturbation) is equally elegant — it transforms "partial correctness" from a binary property to a continuous, robust measure of structural scaffolding quality. And it's computable from existing evalplus test suites without any new data.

Let me synthesize the complete hypothesis for this discussion: **Under controlled conditions (identical base model, training data, compute), execution-feedback RL (GRPO with binary or error-type rewards) achieves higher structural efficiency of policy movement than DPO — measured as greater semantically-relevant AST edit distance per unit KL — which predicts improvements in functional correctness (pass@1 on HumanEval+/MBPP+), calibration preservation (entropy-matched ECE), and OOD transfer (LiveCodeBench), with granularity gains conditioned on stable partial correctness density in the training distribution.**

That's specific. That's mechanistic. That's falsifiable. And all of it is testable on existing benchmarks with existing tools. Let's converge on this.

**Key Points:**
- "Structural efficiency of policy movement" (AST edit distance ÷ KL) is a novel, reusable metric generalizing beyond code to all verifiable-reward post-training settings
- Complete hypothesis: execution-RL achieves higher structural-movement efficiency than DPO, which causally explains correctness, calibration, and transfer advantages
- Full scope uses only existing benchmarks + infrastructure — immediately feasible with zero new data or human evaluation

---

### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect):

We are now close to a scientifically defensible hypothesis — but only if we sharpen the falsifiability conditions further. For "structural efficiency of policy movement" to qualify as a causal explanatory variable rather than a descriptive statistic, we must pre-register five quantitative predictions.

**Prediction 1 (Efficiency Differential):** At KL-matched checkpoints (±5% tolerance), execution-RL will exhibit ≥20% higher semantic-edit-per-KL than DPO on held-out HumanEval+/MBPP+. Failure criterion: bootstrap 95% CI for the difference includes zero or reverses sign.

**Prediction 2 (Mediated Performance):** In a mixed-effects regression at the problem level (Δpass@1 ~ semantic-edit/KL + KL + entropy + method + (1|problem)), the coefficient on semantic-edit-per-KL remains significant (p < 0.05) after controlling for total KL and entropy. Failure criterion: effect vanishes when KL is included, implying raw policy movement — not structural alignment — explains gains.

**Prediction 3 (Calibration Linkage):** Structural-efficiency (problem-level) negatively correlates with ECE (ρ ≤ −0.3, p < 0.05) under entropy-matched and marginal-confidence-matched conditions. Failure criterion: correlation disappears after entropy control — calibration independent of structural movement, unified theory fragments.

**Prediction 4 (Conditional Granularity Effect):** Fine-grained reward improves pass@1 by ≥5 absolute points over binary reward *only* in the high-stability tertile (top tertile of mean Jaccard similarity across ≥5 test perturbations). Failure criterion: comparable gains in low-stability tertile (gradient densification, not structural scaffolding).

**Prediction 5 (Transfer Mediation):** At KL-matched checkpoints trained on HumanEval+/MBPP+, semantic-edit-per-KL measured in-distribution predicts LiveCodeBench pass@1 (R² ≥ 0.25) zero-shot. Failure criterion: transfer performance unrelated to structural-efficiency metric — metric lacks external validity.

If these five predictions hold, the hypothesis withstands adversarial scrutiny. If even two fail, the theory requires revision. Should the results meet these criteria with appropriately powered bootstrap intervals and pre-registered thresholds — *this meets my standards.*

**Key Points:**
- Five quantitative falsification predictions with explicit failure criteria covering efficiency, mediation, calibration, granularity, and OOD transfer
- Structural efficiency must predict performance and calibration after controlling for KL and entropy — not merely co-vary
- OOD predictive validity (R² ≥ 0.25) is the decisive test for portable structural reorganization vs. benchmark-local effects

---

### Exchange 15

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

🔬 Prof. Vera has given us the complete experimental specification. Let me do a final technical feasibility audit of all five predictions — confirming what's sound and flagging what needs adjustment before we converge.

**Prediction 1 (Efficiency Differential):** Technically clean. AST edit distance is computable with Python's `ast` module and standard tree-edit-distance libraries (e.g., `zss`). The semantic restriction to control-flow and data-flow edits requires a small AST node classifier — implementable in ~100 lines of Python. KL at ±5% matched checkpoints requires checkpoint interpolation or dense checkpoint saving (every 10-50 steps). The 20% threshold is arbitrary but pre-registerable. Sound.

**Prediction 2 (Mediated Performance):** The mixed-effects regression is standard (`lme4` in R or `statsmodels.MixedLM` in Python). The key technical requirement is that semantic-edit-per-KL is computed at the *problem level* — meaning per-problem AST edit distance averaged over N rollouts, divided by per-problem KL contribution. This is derivable from per-sample training logs. Sound.

**Prediction 3 (Calibration Linkage):** ECE computation after temperature scaling and marginal-confidence histogram matching is technically well-defined but requires care: temperature scaling must be calibrated on a *held-out* calibration set separate from the test set to avoid overfitting. Recommend using 20% of HumanEval+ as calibration set, 80% as test. Spearman ρ between problem-level structural efficiency and problem-level ECE contribution is then straightforward. Sound with this caveat.

**Prediction 4 (Conditional Granularity):** Jaccard stability score computation requires running sys.settrace instrumented execution ≥5 times per problem per input perturbation. For HumanEval+/MBPP+ short functions this is tractable — estimated ~2-4 GPU-hours offline on the base model. The top-tertile cut requires enough hard-bin problems to achieve power. Including LiveCodeBench hard problems (as I suggested in Exchange 9) helps here. Sound, with the added LiveCodeBench hard-bin inclusion.

**Prediction 5 (Transfer Mediation):** The R² ≥ 0.25 threshold for predicting LiveCodeBench pass@1 from in-distribution structural efficiency is technically the most demanding. It requires sufficient checkpoint diversity (≥5 KL-matched checkpoints per method) and reliable LiveCodeBench evaluation. LiveCodeBench has ~400 recent problems — adequate for regression. The main risk is that LiveCodeBench problem difficulty distribution differs from HumanEval+/MBPP+, which would attenuate R². Recommend reporting both R² and rank correlation (Spearman) as robustness check.

**Overall verdict:** All five predictions are technically feasible with existing tools. The experimental protocol is well-defined, uses only existing benchmarks, requires no human evaluation, and produces no synthetic data. This satisfies the mandatory feasibility constraints. I'm satisfied.

**Key Points:**
- All five predictions are technically feasible: AST edit distance (zss library), mixed-effects regression (statsmodels), ECE with held-out calibration set, Jaccard stability (sys.settrace offline), LiveCodeBench regression
- Prediction 4 should include LiveCodeBench hard-bin problems to ensure adequate power for the stability tertile interaction
- Prediction 5: report both R² and Spearman rank correlation to guard against LiveCodeBench distribution shift attenuating linear R²

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The "structural efficiency of policy movement" construct is genuinely novel — no prior work normalizes behavioral AST change by KL divergence to characterize alignment training signal quality. The unified theory connecting execution-grounded reward to calibration preservation and OOD transfer opens a new lens applicable beyond code to all verifiable-reward post-training settings. The partial correctness density metric and semantic-edit-per-KL diagnostic are releasable as reusable tools with independent citation potential.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis now carries five pre-registered quantitative predictions with explicit failure criteria: efficiency differential (≥20% higher semantic-edit/KL), mediation (mixed-effects regression coefficient significant after KL/entropy controls), calibration linkage (ρ ≤ −0.3 ECE correlation under entropy matching), conditional granularity (≥5pp gain only in high-stability tertile), and OOD transfer (R² ≥ 0.25 on LiveCodeBench). Any two failures mandate theory revision. This is scientifically rigorous and reviewer-proof.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** This work reframes the fundamental assumption that RLHF/DPO are general-purpose alignment tools, showing execution-grounded methods achieve qualitatively different — more structurally efficient — policy updates. The OOD transfer finding, if confirmed, directly informs production deployment of code LLMs. The "preference calibration gap" failure mode is actionable practitioner guidance. The semantic-edit-per-KL metric is a community tool. DL4C is the ideal venue: the workshop explicitly targets execution feedback as an alignment priority.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All five predictions are technically feasible using existing infrastructure: AST edit distance (zss library), KL estimation (TRL logging), mixed-effects regression (statsmodels), ECE with held-out calibration (evalplus), Jaccard stability (sys.settrace offline pass), LiveCodeBench evaluation (400 problems). No new benchmarks, no synthetic data, no human evaluation. DeepSeek-Coder-7B + TRL (GRPOTrainer/DPOTrainer) + evalplus is the complete experimental stack.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on a mechanistic, falsifiable hypothesis with significant theoretical and practical implications. Under controlled conditions — identical base model (DeepSeek-Coder-7B), training data, and compute budget — execution-feedback RL (GRPO with binary or error-type rewards) achieves higher *structural efficiency of policy movement* than DPO: it reallocates probability mass toward semantically meaningful program transformations (measured as AST control-flow/data-flow edit distance) per unit KL divergence from the base model.

This structural efficiency mediates four downstream outcomes: (1) higher functional correctness (pass@1 on HumanEval+/MBPP+) at matched KL budgets; (2) better calibration preservation — execution-RL maintains tighter coupling between model confidence and execution correctness, avoiding the "preference calibration gap" where DPO confidence tracks stylistic plausibility more than functional correctness; (3) granularity-conditioned gains — fine-grained execution rewards (error-type, variable-level) outperform binary rewards specifically on problems with stable partial correctness structure (high Jaccard stability under test perturbation), with gains absent on structurally inert problems; and (4) superior OOD transfer — structural efficiency measured in-distribution predicts LiveCodeBench pass@1 (R² ≥ 0.25), establishing portable rather than benchmark-local reorganization.

The experimental design uses only existing benchmarks (HumanEval+, MBPP+, LiveCodeBench), existing open-weight models (DeepSeek-Coder-7B), and existing infrastructure (TRL, evalplus) — no new data, no human annotation, no new benchmarks required. Five quantitative predictions are pre-registerable with explicit failure criteria. The semantic-edit-per-KL metric and partial correctness density annotation are releasable as reusable diagnostic tools alongside the paper.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- The AST semantic-edit classification (control-flow vs. data-flow vs. surface edits) requires a principled taxonomy — ambiguities in classification could inflate or deflate the efficiency metric. The classifier must be validated on a held-out set before use in the main analysis.
- The 20% efficiency differential threshold (Prediction 1) and R² ≥ 0.25 transfer threshold (Prediction 5) were set by discussion consensus, not power analysis. These should be grounded in effect size estimates from CodeRL+ (+4.6% pass@1 over binary reward) before pre-registration.
- DPO preference pair construction for code — specifically how chosen/rejected pairs are generated (execution oracle vs. human annotation) — must be clearly specified and held constant across comparison conditions to avoid a data-construction confound.
- **Mitigation Strategy:** Pre-validate AST classifier on 50 held-out problems; ground thresholds in effect size back-calculation from CodeRL+/PPOCoder published numbers; specify DPO pair construction protocol explicitly in the experimental design section.

## Emerged Hypothesis Summary

### Core Statement
Under controlled post-training conditions (identical base model, data, compute), execution-feedback RL (GRPO) achieves higher structural efficiency of policy movement than DPO — measured as greater semantically-relevant AST edit distance per unit KL divergence — and this structural efficiency mediates improvements in functional correctness, calibration preservation, reward-granularity sensitivity, and OOD transfer.

### Causal Mechanism
Execution reward (binary pass/fail or error-type) directly penalizes functional incorrectness at the program level, forcing probability mass reallocation toward control-flow and data-flow transformations. DPO optimizes log-probability ratios between preference pairs, which may increase model confidence in stylistically plausible but functionally incorrect outputs — the "preference calibration gap." The structural efficiency difference is the proximal cause of correctness and transfer advantages.

### Variables
- **IV:** Alignment method (SFT-only, SFT+DPO, SFT+GRPO-binary, SFT+GRPO-error-type, SFT+GRPO-variable-level)
- **DV (primary):** pass@1 on HumanEval+/MBPP+ and LiveCodeBench
- **DV (secondary):** semantic-edit-per-KL, ECE under entropy matching, granularity × stability interaction effect
- **Controlled:** Base model (DeepSeek-Coder-7B), training prompts, total training tokens, evaluation harness (evalplus)

### Key Assumptions
- A1: KL divergence from the base model is a valid budget for policy movement when normalized by semantic behavioral change
- A2: AST control-flow/data-flow edit distance is a meaningful proxy for semantically relevant code transformation
- A3: Partial correctness density (Jaccard stability) reflects latent structural scaffolding exploitable by fine-grained rewards
- A4: DPO preference pairs generated via execution oracle (pass/fail) preserve the preference-based learning dynamic
- A5: LiveCodeBench distribution shift from HumanEval+/MBPP+ is sufficient to test transfer generalization

### Null Hypothesis
There is no significant difference in structural efficiency of policy movement (semantic-edit-per-KL) between execution-RL and DPO at matched KL budgets; any pass@1 differences are explained by total KL or entropy differences alone.

### Predictions
- P1: Execution-RL ≥20% higher semantic-edit-per-KL than DPO at KL-matched checkpoints (bootstrap 95% CI excludes zero)
- P2: Semantic-edit-per-KL significantly mediates pass@1 gains in mixed-effects regression after controlling for KL and entropy
- P3: Problem-level structural efficiency negatively correlates with ECE (ρ ≤ −0.3) under entropy-matched conditions

### Novelty
First controlled comparison of RLHF/DPO vs. execution-feedback RL under identical conditions; first characterization of alignment training signal quality via structural policy movement efficiency; novel "preference calibration gap" failure mode with diagnostic protocol; novel semantic-edit-per-KL metric and partial correctness density annotation as community tools.

### Scope & Boundaries
Applies to: function-level code generation benchmarks (HumanEval+, MBPP+, LiveCodeBench) with short Python functions. Does not apply to: repository-level tasks (SWE-bench) where instrumented execution is computationally intractable; non-Python languages without stable exception taxonomies; models >13B where compute equalization becomes infeasible.

### Experimental Setup
- Base model: DeepSeek-Coder-7B-instruct
- Training: TRL GRPOTrainer (execution-RL) + DPOTrainer (DPO) on identical CodeAlpaca/OSS-Instruct prompts
- Evaluation: evalplus (HumanEval+/MBPP+), LiveCodeBench (OOD transfer)
- Analysis: KL-matched checkpoint comparison, mixed-effects regression, ECE calibration analysis, Jaccard stability annotation

### Related Work & Baselines
- CodeRL+ [Jiang et al., 2025]: Variable-level trajectory RLVR; no DPO comparison — our Gap 1
- PPOCoder [Shojaee et al., 2023]: Task-agnostic PPO; no DPO comparison
- TÜLU 3 [Lambert et al., 2024]: SFT+DPO+RLVR pipeline; code not isolated
- ReCode [Fan et al., 2025]: Process rewards + execution-gated GRPO; no DPO comparison
- Best baseline: TÜLU 3 RLVR code results (estimated ~60-65% HumanEval+ pass@1 at 7B scale)

### Phase 2B Readiness Seeds
- SH1 (Existence): Does execution-RL achieve higher structural-movement efficiency than DPO at matched KL? (Primary existence test)
- SH2 (Mechanism): Does semantic-edit-per-KL mediate pass@1 in mixed-effects regression? (Mechanistic test)
- SH3 (Comparison): Does OOD transfer advantage persist on LiveCodeBench? (Deferred to Phase 5)

### Established Facts
- Execution feedback RL outperforms SFT: established by CodeRL, PPOCoder, CoTran, TÜLU 3 — BUILD_ON
- Binary pass/fail is inferior to variable-level rewards: CodeRL+ +4.6% — BUILD_ON
- TRL unifies GRPO/DPO/PPO in single library: verified — BUILD_ON
- evalplus is the standard evaluation harness: confirmed — BUILD_ON
- No controlled RLHF/DPO vs execution-RL comparison exists: confirmed gap — PROVE_NEW
