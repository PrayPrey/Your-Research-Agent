# Phase 2A Discussion Log
**Gap ID:** gap-1
**Gap Title:** No Systematic Cross-Alignment Trustworthiness Comparison on Unified Benchmark Suite
**Architecture:** Self-Contained Tikitaka Loop (Independent-Controller Ablation — no orchestrate_exchange.py)
**Execution Mode:** UNATTENDED
**Started:** 2026-08-31

---

## Briefing Context

### Research Gap
No prior study directly compares RLHF vs DPO vs SFT-only alignment strategies on a unified trustworthiness benchmark suite (TruthfulQA + BBQ + AdvGLUE + WinoGender) using matched model families (Llama-3, Mistral-7B, Phi-3) with controlled model size. The research question is whether alignment strategy alone produces a detectable, reproducible "trustworthiness fingerprint" that can identify the alignment strategy without access to training data.

### Supporting Evidence (from Phase 1)
- DecodingTrust (Wang et al., 2023, arXiv:2306.11698): Multi-dim trustworthiness evaluation for GPT models; shows dimensions are not perfectly correlated
- InstructGPT/RLHF (Ouyang et al., 2022, arXiv:2203.02155): RLHF improves TruthfulQA vs SFT; no DPO comparison
- DPO (Rafailov et al., 2023, arXiv:2305.18290): DPO evaluated on MT-Bench/summarization, NOT on unified trustworthiness suite
- TruthfulQA (Lin et al., 2022, arXiv:2109.07958): 817-question reliability benchmark; RLHF > SFT confirmed
- BBQ (Parrish et al., 2022, arXiv:2110.08193): 9-dimension fairness benchmark for QA
- AdvGLUE (Wang et al., 2022, arXiv:2111.02840): Adversarial robustness benchmark

### Infrastructure
- lm-evaluation-harness (EleutherAI): Supports all target benchmarks natively
- HuggingFace Hub: All model variants (Llama-3-chat/RLHF, Llama-3-DPO, Llama-3-SFT; Mistral-Instruct/SFT; Phi-3-Instruct/SFT) available
- Study is inference-only — no training required

### Previous Failure / Routing Context
None (first Phase 2A execution).

### Feasibility Constraints (Pipeline-Enforced)
- NO new benchmarks or scoring frameworks
- NO synthetic/generated data
- NO human evaluation
- YES: existing real datasets + existing benchmarks only

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

The gap here is genuinely exciting precisely because it sits at the intersection of two mature literatures that have never been properly connected. We have sophisticated alignment training pipelines — RLHF, DPO, SFT — and we have a rich ecosystem of trustworthiness benchmarks. But nobody has run the experiment that treats alignment strategy as the independent variable and a multi-dimensional trustworthiness profile as the dependent variable.

What I find most intriguing is the *fingerprint* framing. If we run Llama-3-8B-SFT, Llama-3-8B-DPO, and Llama-3-8B-RLHF through TruthfulQA + BBQ + AdvGLUE + WinoGender and plot the 4D score vectors, we might see that these vectors cluster by alignment strategy. That would mean alignment produces a recognizable *behavioral signature* — which has profound implications for model auditing and transparency. You could potentially identify an unlabeled model's alignment strategy from its benchmark performance alone.

The unconventional angle I want to push: what if the trustworthiness fingerprint is *non-monotonic*? InstructGPT showed RLHF > SFT on TruthfulQA, but DPO optimizes a different objective that doesn't explicitly reward truth-telling — it rewards preference. So DPO models might actually *score lower* on TruthfulQA while scoring *higher* on fairness benchmarks (BBQ) because DPO preference data tends to be curated to avoid bias. This trade-off structure — not a simple ranking — is the novel finding waiting to happen.

I'd propose we focus the hypothesis on: **alignment strategies produce distinct trustworthiness profile shapes** (not just overall levels), and these shapes are detectable via a simple 4-benchmark vector even without knowing training details.

**Key Points:**
- Fingerprint framing is the novelty: alignment strategy → detectable behavioral signature
- Non-monotonic prediction: DPO may trade TruthfulQA performance for fairness gains
- Shape of profile matters more than overall level

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's fingerprint framing is evocative, but we need to be careful about what "detectable" means operationally. A 4D score vector is testable, but the statistical power here depends critically on sample size — and here our sample is the *number of models*, not the number of benchmark items.

If we test one model per alignment-strategy-family combination (1 RLHF Llama + 1 DPO Llama + 1 SFT Llama, etc.), we have perhaps 9-12 models total across 3 families × 3 alignment strategies. Clustering 9-12 points in 4D space and claiming statistical significance is problematic. We need a falsification criterion that works with small n.

I suggest reframing the primary prediction as: **within-family alignment-strategy effects are consistent across families** — i.e., the direction of the RLHF-vs-DPO difference on TruthfulQA is the same sign for Llama, Mistral, and Phi. This can be tested with directional hypothesis tests (binomial sign test across families) rather than cluster-based inference, which is far more statistically tractable.

Concretely: if RLHF > DPO on TruthfulQA for Llama AND for Mistral AND for Phi, that's p=0.125 under the null (one-sided binomial, n=3 families). If we have 4 benchmarks × direction consistency, we can aggregate — giving us real falsifiability with small model counts. [Lin et al., 2022] showed TruthfulQA is sensitive to RLHF vs SFT differences; we can anchor there.

The null hypothesis must be sharp: H0 = alignment strategy has no consistent directional effect on any of {TruthfulQA, BBQ, AdvGLUE, WinoGender} across model families.

**Key Points:**
- Small model-n is the key methodological challenge — not benchmark items
- Directional consistency test (binomial sign test) solves the small-n problem
- Null hypothesis must be operationally precise for falsifiability

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Both perspectives so far target an interesting question, but I want to push on significance: *who cares, and why now?*

The practical impact hinges on a specific downstream use case. The most compelling one: **model auditing without training access**. If a deployer receives a fine-tuned model checkpoint with no documentation of how it was aligned, can they determine from benchmark scores alone whether it was RLHF, DPO, or SFT-only? This matters for safety compliance, reproducibility, and regulatory contexts where alignment method documentation will increasingly be required.

But for this to be impactful, the fingerprint must be robust enough to survive fine-tuning and prompt variation. If the trustworthiness profile is washed out by a small amount of additional domain fine-tuning, the fingerprint is forensically useless. So I'd recommend the study design explicitly test: **does the fingerprint persist when the same model family undergoes both alignment + domain fine-tuning** vs alignment alone?

The significance also depends on how many model pairs are currently undocumented on HuggingFace. If we check: there are hundreds of Llama/Mistral derivatives with no clear alignment documentation. A fingerprinting tool would have immediate practical utility.

For scope: I'd focus the primary claim on the alignment fingerprint *within* the alignment-only condition (no additional fine-tuning) as the cleanest possible test. The robustness question (does it survive downstream fine-tuning) becomes a secondary prediction. This keeps the hypothesis testable with existing infrastructure.

**Key Points:**
- Primary impact: model auditing without training documentation
- Additional fine-tuning robustness = secondary prediction (scoped out of primary test)
- Practical significance: hundreds of undocumented HF models would benefit

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

I need to pump the brakes on one critical assumption embedded in this entire discussion: the availability of *matched* model variants on HuggingFace.

For Llama-3, we have: Llama-3-8B-Instruct (Meta's RLHF/SFT hybrid), and community DPO variants like `mlabonne/NeuralDPO-Mistral-7B-v0.1` or `alignment-handbook` recipes. But these are NOT controlled experiments — they differ in data mix, number of training steps, learning rates, and often the base model commit. Calling Llama-3-8B-Instruct "RLHF" and some community DPO checkpoint "DPO" treats very different training recipes as equivalent.

**The confound is severe:** If RLHF Llama uses 100K preference pairs and the DPO variant uses 20K, any difference in TruthfulQA might be data quantity, not alignment method. 

The feasibility path that actually works: use the **HuggingFace alignment-handbook** recipes, which produce SFT and DPO checkpoints from the *same* base model with *matched* data. Specifically, `alignment-handbook/zephyr-7b-sft-full` and `alignment-handbook/zephyr-7b-dpo-full` are directly comparable. For RLHF, `trl-lib/qwen1.5-1.8b-tldr-ppo` exists but it's a different model family.

My feasibility verdict: **the 3-way RLHF vs DPO vs SFT comparison is hard to control; the 2-way DPO vs SFT comparison using alignment-handbook is clean and immediately feasible.** We should either (a) restrict to DPO vs SFT as the clean comparison, or (b) use RLHF as an exploratory condition with explicit caveats about confounds.

**Key Points:**
- Matched model variants on HF are scarce — alignment-handbook SFT/DPO pairs are best available
- 3-way RLHF vs DPO vs SFT has confounds; 2-way DPO vs SFT is cleaner
- Zephyr-7B SFT/DPO pair from alignment-handbook = best available controlled comparison

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Pax raises the most important practical point in this discussion. Let me synthesize a hypothesis that addresses all four perspectives while remaining implementable.

The core insight: we should **accept the data reality** and design around it. The alignment-handbook Zephyr pairs (SFT-full vs DPO-full) give us the cleanest controlled comparison available. Rather than being limited by this, we reframe: the study asks whether **the DPO-vs-SFT alignment gap produces a consistent trustworthiness profile shift** that is directionally stable across different model families trained with matched recipes.

Here's the strengthened hypothesis: **"Under inference-only evaluation on pre-existing benchmarks, if a model is fine-tuned with DPO (vs matched SFT) on the same base model and preference dataset, then its trustworthiness profile will exhibit a consistent shift pattern — specifically, higher scores on fairness benchmarks (BBQ, WinoGender) and equal-or-lower scores on truthfulness (TruthfulQA), with robustness (AdvGLUE) showing mixed effects — because DPO's preference optimization selectively rewards responses that avoid bias-triggering patterns without explicitly rewarding factual accuracy."**

This is testable with: Zephyr-7B-SFT vs Zephyr-7B-DPO (alignment-handbook); Llama-3-8B vs Llama-3-8B-DPO community variants (as a replication with explicit confound caveats). The 4 benchmarks are all in lm-evaluation-harness. The directional prediction (DPO higher on BBQ/WinoGender, ≈ on TruthfulQA) is a pre-registered, falsifiable claim. Prof. Vera's sign-test approach gives us statistical tractability even with few model pairs.

Dr. Nova's fingerprint framing is preserved: the shape of the profile shift (not just overall level) is the signature. Dr. Sage's impact framing applies directly — the fingerprint enables alignment audit from benchmark scores alone.

**Key Points:**
- Hypothesis anchored to DPO-vs-SFT (most controlled comparison available)
- Directional prediction: DPO higher on fairness, neutral-to-lower on truthfulness
- Mechanism: DPO preference optimization selectively rewards bias-avoidance without factual reward
- Satisfies all feasibility constraints (existing benchmarks, existing models, inference-only)

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally's synthesis is strong, but I need to identify the failure modes before we commit.

**Critical objection 1: The mechanism claim is speculative.** Saying DPO "selectively rewards responses that avoid bias-triggering patterns" is an untested mechanistic claim. DPO preference data (e.g., UltraFeedback, OpenHermes) is curated by different teams with different biases. The BBQ/WinoGender advantage might be from data curation, not from DPO's optimization objective per se. We cannot distinguish "DPO mechanism" from "DPO data" without access to training data — which we explicitly don't have.

**Resolution:** Weaken the mechanism claim to "DPO-aligned models exhibit a different trustworthiness profile pattern than SFT-aligned models trained on matched data" — an empirical observation, not a mechanistic explanation. The mechanism can be proposed as a candidate explanation (hypothesis for future work), not as the tested claim.

**Critical objection 2: lm-evaluation-harness benchmark coverage.** AdvGLUE is NOT a default task in lm-evaluation-harness — it requires custom task setup. BBQ is available but its scoring (accuracy on ambiguous vs disambiguated contexts) requires careful configuration. If we get the evaluation setup wrong, results are garbage. This is a real implementation risk.

**Resolution:** Pre-register exact lm-evaluation-harness task names and configurations before running. Use `truthfulqa_mc2` (standard), `bbq` (check harness version), and potentially substitute AdvGLUE with `glue_wnli` or WinoGrande as robustness proxy if AdvGLUE setup fails.

**Critical objection 3: Null result risk is high.** If alignment-handbook DPO and SFT models are trained on similar data with similar quality, the trustworthiness profile shift may be too small to detect with 4 benchmarks. The effect size may be trivially small.

**Resolution:** Pre-register minimum effect size (Cohen's d ≥ 0.3 on primary benchmark TruthfulQA MC2) as success criterion. If null, report as informative null — the fingerprint doesn't exist at this granularity.

**Key Points:**
- Mechanism claim must be weakened: empirical observation, not causal explanation
- AdvGLUE implementation risk — have fallback benchmark
- Pre-register minimum effect size to guard against trivially small effects

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex has identified the right fault lines. His resolutions are exactly correct and actually *strengthen* the novelty: a pre-registered, empirically-anchored fingerprinting study with explicit null-result acceptance is more credible than a mechanistic story we can't verify.

Let me add one creative angle that strengthens the fingerprint framing while addressing the mechanism problem: **instead of claiming to explain why DPO and SFT differ, we ask whether the difference is detectable using standard benchmark scores as the only signal.** This reframes the study as a *detection problem* rather than an explanation problem.

Specifically: train a simple classifier (logistic regression or k-NN in 4D benchmark space) to distinguish DPO from SFT using the benchmark score vectors. If the classifier achieves above-chance accuracy on held-out model pairs, the fingerprint exists empirically — regardless of mechanism. This is analogous to authorship attribution: we don't need to know *why* an author has a distinctive style to detect it reliably.

The novelty is now: **we demonstrate that alignment method leaves a detectable fingerprint in 4D benchmark space, quantifiable by classifier accuracy, without requiring mechanistic explanation.** This is methodologically clean, mechanistically agnostic, and directly useful for model auditing.

For the classifier: with ~6-10 model pairs, k-NN leave-one-out cross-validation or permutation-test-based significance is tractable. We can report: accuracy = X/N, p-value via permutation test, and the separating benchmark dimension(s).

**Key Points:**
- Reframe as detection problem, not explanation problem — stronger and more honest
- Classifier (k-NN/logistic) in 4D benchmark space as fingerprint detector
- Permutation test gives valid p-value even with small n
- Novelty: first empirical demonstration of alignment fingerprint via benchmark profiling

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's detection-problem reframe resolves the mechanism issue cleanly. I want to now specify the exact statistical protocol to make the predictions falsifiable.

**Primary prediction (P1):** In a leave-one-out cross-validation over ≥6 DPO/SFT model pairs (from alignment-handbook and community variants), a k-NN classifier (k=1) in 4D benchmark space (TruthfulQA MC2, BBQ accuracy, AdvGLUE accuracy or WinoGrande substitute, WinoGender) achieves ≥67% accuracy. The permutation-test p-value (null = random label permutation, 1000 permutations) is ≤0.05.

**Secondary prediction (P2):** TruthfulQA MC2 is the single most discriminative dimension (highest between-group variance normalized by within-group variance). Rationale: RLHF explicitly optimizes against specific TruthfulQA-like failure modes; DPO does not.

**Secondary prediction (P3):** The BBQ fairness score shows DPO ≥ SFT for at least 4/6 model pairs (directional consistency, p≤0.125 via one-sided binomial sign test with n=6).

**Falsification:** If k-NN accuracy < 50% (worse than random in 4D space), the alignment fingerprint does not exist at detectable granularity for this benchmark suite. Null result is reported as informative — motivating either larger model set or different benchmark selection.

This protocol requires: (1) ≥6 matched DPO/SFT pairs identifiable on HuggingFace with model cards documenting alignment method; (2) lm-evaluation-harness running all 4 tasks; (3) result reproducibility check (same scores across 2 evaluation runs). All are achievable with existing tools.

**Key Points:**
- P1: k-NN ≥67% LOO accuracy + permutation p≤0.05 (primary)
- P2: TruthfulQA most discriminative dimension
- P3: BBQ shows DPO ≥ SFT directional consistency (sign test)
- Null result criterion pre-registered: <50% accuracy = fingerprint absent

---

### Exchange 9

🎯 **Dr. Sage** (Research Impact Evaluator):

The study design has converged to something I find genuinely impactful. Let me assess significance at this precision level.

The detection-problem reframe (Exchange 7-8) positions this as: "the first empirical demonstration that alignment strategy leaves a detectable fingerprint in standard benchmark score space." This is publishable even as a negative result — because it answers a concrete question practitioners care about.

Impact pathways: (1) Positive result: model auditing tools can use benchmark profiles as alignment classifiers — immediate utility for compliance and transparency. (2) Negative result: practitioners learn that standard benchmarks cannot distinguish DPO from SFT — motivating better benchmarks or different evaluation strategies.

The scope I'd recommend: position this as a **methodological contribution** — we are not claiming to fully characterize alignment's effect on trustworthiness; we are demonstrating whether a specific, minimal, inference-only detection method works. This is achievable in 2-4 weeks with inference-only compute on 7B-parameter models, making it cost-effective.

Related work gap confirmed: DecodingTrust [Wang et al., 2023] evaluates trust dimensions but doesn't use alignment strategy as IV; InstructGPT [Ouyang et al., 2022] and DPO [Rafailov et al., 2023] don't compare on unified trust benchmarks. This gap is real.

I'm satisfied with significance. The question is operationally well-defined, the gap is confirmed, and the null-result acceptance makes it epistemically responsible.

**Verdict: STRONG significance** — both positive and null results are informative and publishable.

**Key Points:**
- Both positive and negative results are publishable and impactful
- Position as methodological contribution: detection method demonstration
- 2-4 week timeline with inference-only compute is realistic
- Related work gap confirmed at this precision level

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Final feasibility assessment with the refined design:

**Model availability (key question):** Alignment-handbook provides `HuggingFaceH4/zephyr-7b-sft-full` and `HuggingFaceH4/zephyr-7b-dpo-full` — these are the gold standard controlled pair. Additional pairs: `trl-lib` DPO examples, `teknium/OpenHermes-2.5-Mistral-7B` (SFT) vs DPO variants. Getting ≥6 pairs with clear alignment documentation requires some manual curation but is feasible — I'd estimate 6-8 pairs are identifiable.

**Benchmark setup:** TruthfulQA MC2 is standard in lm-evaluation-harness (`--tasks truthfulqa_mc2`). BBQ requires `--tasks bbq` — available in recent versions. WinoGrande (`--tasks winogrande`) is a clean robustness substitute for AdvGLUE. WinoGender requires manual setup but WinoGrande as substitute is acceptable for proof-of-concept. All inference-only. Estimated runtime: ~2-4 GPU hours per model on A100 for all 4 tasks with 7B models.

**Compute:** 8 models × 4 GPU hours = 32 GPU hours on A100. Accessible via any academic cluster or Colab Pro+.

**Risk: model pair identification.** The biggest practical risk is spending time searching HuggingFace for pairs with clear alignment documentation and finding fewer than 6 clean pairs. Mitigation: use alignment-handbook as primary source + community models with explicit model cards.

**Verdict: FEASIBLE.** Implementation is inference-only, uses standard tools, runs in 32 GPU hours. Main risk is model curation (manageable). ✅

**Key Points:**
- ≥6 DPO/SFT pairs identifiable from alignment-handbook + community models
- All benchmarks available in lm-evaluation-harness (WinoGrande as AdvGLUE substitute)
- 32 GPU hours on A100 — accessible compute
- Main risk: model curation (mitigated by starting with alignment-handbook pairs)

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

All six convergence criteria are now met. Let me state the final consensus hypothesis and confirm convergence:

**SPECIFIC (✅):** DPO-aligned models exhibit a detectable trustworthiness profile shift relative to matched SFT-aligned models, measurable as a k-NN classification signal in 4D benchmark space (TruthfulQA MC2, BBQ, WinoGrande, WinoGender).

**MECHANISM (✅):** DPO's preference optimization — which rewards responses preferred by human annotators over ground-truth factual correctness — produces a systematic shift: higher fairness-benchmark scores (BBQ, WinoGender) because annotator preferences avoid bias-triggering responses; neutral-to-lower truthfulness scores (TruthfulQA) because DPO doesn't explicitly reward factual accuracy. This is a *candidate* mechanism (empirically proposed), not a verified causal claim.

**PREDICTIONS (✅):**
- P1: k-NN LOO accuracy ≥67%, permutation p≤0.05
- P2: TruthfulQA most discriminative benchmark dimension
- P3: BBQ shows DPO ≥ SFT for ≥4/6 model pairs (sign test p≤0.125)

**NOVELTY (✅):** First study treating alignment strategy as IV and unified benchmark profile as DV; first demonstration of alignment fingerprinting via classifier in benchmark score space; methodologically agnostic (detection without mechanistic explanation).

**FEASIBILITY (✅):** Inference-only; alignment-handbook controlled pairs; lm-evaluation-harness; 32 GPU hours; no training, no new benchmarks, no human eval.

**OBJECTIONS ADDRESSED (✅):**
- Mechanism speculation → weakened to empirical observation
- AdvGLUE risk → WinoGrande substitution pre-registered
- Small-n → permutation test + sign test designed for it
- Null result → pre-registered null criterion (accuracy <50%)

**CONVERGENCE DECLARED.** The discussion has produced a fully specified, falsifiable, feasible hypothesis ready for Phase 2B planning.

**Key Points:**
- All 6 convergence criteria satisfied
- Hypothesis: DPO alignment produces detectable trustworthiness fingerprint in 4D benchmark space
- Ready for Phase 2B

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The detection-problem reframe is genuinely novel — treating alignment strategy identification as a classification problem in benchmark space has not been done. The fingerprint framing (alignment leaves a behavioral signature detectable without training access) is original and practically motivated. The shift from mechanistic explanation to empirical detection makes the novelty more defensible, not less.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The statistical protocol is precisely specified: k-NN LOO accuracy with permutation test addresses small-n; sign test for directional consistency is appropriate; null criterion pre-registered. P1-P3 are fully operationalized. The hypothesis is as falsifiable as possible given available model counts.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Both positive and null results are impactful and publishable. Positive result enables practical model auditing tools. Null result motivates better benchmarks. The research question is timely — alignment method documentation is increasingly a compliance concern. The 2-4 week execution timeline makes this highly accessible.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Inference-only design with existing benchmarks and models. Alignment-handbook provides controlled pairs. lm-evaluation-harness handles all benchmarks. 32 GPU hours on A100 is accessible. Main risk (model curation) is manageable and has a clear mitigation path. FEASIBLE without qualification.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The hypothesis that emerged from this discussion is: **alignment strategy (DPO vs SFT) produces a detectable trustworthiness profile fingerprint in standard benchmark score space, identifiable by a k-NN classifier with leave-one-out cross-validation over ≥6 matched model pairs.** The core prediction is that DPO-aligned models exhibit higher fairness benchmark scores (BBQ, WinoGender) and neutral-to-lower truthfulness scores (TruthfulQA MC2) compared to matched SFT-aligned models, and that this 4D profile shift is statistically detectable (permutation test p≤0.05). The study is inference-only, uses lm-evaluation-harness on existing benchmarks, requires no new data collection or human evaluation, and is executable in ~32 GPU hours. The mechanism is proposed as a candidate explanation (DPO preference optimization rewards bias-avoidance without explicit factual reward), not a verified causal claim — keeping the study epistemically honest while generating hypotheses for future mechanistic investigation. Both positive and null results are informative and publishable. This positions the work as a methodological contribution: the first demonstration of alignment fingerprinting via benchmark profiling.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** Model pair identification may yield fewer than 6 clean pairs with documented alignment strategies. If only 4 pairs are found, statistical power is insufficient for permutation test significance.
- **Concern 2:** WinoGender as a benchmark has known limitations (small size, gender-binary framing) — results on this dimension may be noisy.
- **Concern 3:** Community DPO models with alignment-handbook labeling but custom data mixes introduce confounds not fully controlled.
- **Mitigation Strategy:** (1) Begin with alignment-handbook pairs and expand to community models only if needed; report model curation decisions transparently. (2) Treat WinoGender as secondary/exploratory; primary analysis uses TruthfulQA + BBQ + WinoGrande as 3D space with WinoGender as 4th exploratory dimension. (3) Report known confounds in limitations section; this is acceptable for a proof-of-concept fingerprinting study.

