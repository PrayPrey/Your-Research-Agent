# Phase 2A Research Discussion Log

**Date:** 2026-03-24
**Gap ID:** gap-1
**Gap Title:** Limited Qwen-Family Calibration Studies
**Status:** In Progress

---

## Discussion Briefing

### Research Context

**Main Research Question:** Can population-level confidence frequency analysis reveal systematic miscalibration patterns in instruction-tuned LLMs, and does post-hoc temperature scaling significantly reduce Expected Calibration Error (ECE) on standard QA benchmarks without requiring task-specific modifications?

**Selected Gap:** Gap 1 - Limited Qwen-Family Calibration Studies (CRITICAL priority)

**Gap Description:** Existing LLM calibration studies (Tian 2023, DACA 2025, Revisiting UE 2025) primarily evaluate GPT-3.5/4, Llama-2/3, and Claude families. Qwen models have limited calibration characterization. Missing piece: Baseline ECE measurements and reliability diagram patterns specifically for Qwen2.5-7B-Instruct on MMLU and TruthfulQA benchmarks.

### Background (8th Attempt - ROUTE_TO_0)

This is the 8th research attempt after 7 previous failures:
1. Entropy-based UQ (confounds explain 99.99%)
2. H_rest sharpening falsified (CoT INCREASES entropy)
3. Attention consistency (CFS AUROC marginal, CI includes random chance)
4. Residualized entropy variance too weak (4.98% < 10% threshold)
5. Self-Consistency Disagreement (routed back to Phase 0)
6. Verbalized Confidence Calibration (routed back to Phase 0 after h-e1 FAILED)
7. Selective Prediction via p_max (55.6% pass rate, complete failure on GSM8K)

**Paradigm Shift:** Moving from per-instance uncertainty quantification to population-level aggregate statistics (ECE, reliability diagrams).

### Key Papers

1. **Guo et al. 2017** - "On Calibration of Modern Neural Networks" (7,452 citations)
   - Foundational temperature scaling + ECE framework
   - arXiv: 1706.04599

2. **Tian et al. 2023** - "Just Ask for Calibration" (598 citations)
   - Verbalized confidence outperforms token probs for RLHF models
   - arXiv: 2305.14975

3. **DACA (Luo et al. 2025)** - "Your Pre-trained LLM is Secretly an Unsupervised Confidence Calibrator"
   - PLM-PoLM disagreement; 15% ECE improvement
   - arXiv: 2505.16690

4. **CCPS (Khanmohammadi et al. 2025)** - Perturbation-based calibration
   - 55% ECE reduction on MMLU
   - arXiv: 2505.21772

5. **Flex-ECE (de Oliveira et al. 2025)** - Post-hoc calibration study
   - Reduces ECE from 24-47% to 0.1-4%

### Implementation Resources

- **gpleiss/temperature_scaling** (1,167 stars) - Canonical Guo et al. implementation
- **probmetrics** - Modern streaming ECE
- **TorchMetrics** - PyTorch ecosystem ECE

### Feasibility Constraints (MANDATORY)

- ✅ Uses existing benchmarks (MMLU, TruthfulQA)
- ✅ Uses existing metrics (ECE, reliability diagrams)
- ✅ No new benchmark or rubric creation
- ✅ No human evaluation needed
- ✅ No synthetic data generation
- ✅ Testable immediately with existing datasets

---

## Discussion Transcript

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What an exciting opportunity we have here! After seven attempts that got tangled in per-instance uncertainty signals, we're finally looking at the problem from the right angle. Let me share some creative perspectives on confidence frequency calibration for Qwen models.

First, what strikes me as particularly novel about this direction is the **paradigm shift from prediction to measurement**. Previous attempts tried to *create* or *extract* uncertainty signals that could predict individual outcomes. But calibration analysis asks a fundamentally different question: "When the model says it's 80% confident, is it correct 80% of the time?" This is an aggregate, population-level property that sidesteps the confound saturation that plagued entropy-based approaches.

Second, I'm excited about the **Qwen-specific angle**. Looking at the literature, Guo et al. 2017 established temperature scaling for CNNs, and recent work like DACA and CCPS has evaluated GPT and Llama families. But Qwen2.5-7B-Instruct represents a distinct training paradigm - Alibaba's RLHF approach may produce different miscalibration patterns than OpenAI's or Meta's. What if Qwen models have a unique "calibration fingerprint" that differs from Western-trained models?

Third, here's a wild idea: **Domain-conditioned temperature scaling**. Rather than learning a single temperature T across all domains, what if STEM subjects require T_STEM while humanities require T_humanities? The gap analysis suggests domain-wise calibration breakdown is missing - this could be our novel contribution beyond just "measuring ECE on Qwen."

**Key Points:**
- Population-level calibration measurement avoids per-instance confound issues
- Qwen family is under-characterized - opportunity for first systematic study
- Domain-conditioned temperature scaling could be a novel methodological contribution

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

The shift from per-instance uncertainty to population-level calibration is methodologically sound. The evidence from Guo et al. (2017) suggests that modern neural networks are often miscalibrated even when accurate, and temperature scaling can correct this at low cost. However, we must be precise: calibration is only meaningful if we define *exactly* how confidence is extracted from Qwen2.5-7B-Instruct. Are we using the maximum softmax probability of the final token? Sequence-level joint probability? Mean token probability? Each choice produces a different calibration curve. If the measurement definition is unstable, any downstream claim collapses. What operational definition of "confidence" would remain invariant under prompt paraphrase?

On the claim of a "Qwen-specific calibration fingerprint," the evidence suggests this is plausible but unproven. To test it, we require a controlled cross-model comparison under identical prompts, decoding settings, and datasets. A falsifiable prediction would be: *Qwen2.5-7B-Instruct exhibits statistically significantly higher Expected Calibration Error (ECE) than Llama-2-7B and Mistral-7B on the same benchmark, after identical temperature scaling procedures.* Failure to detect a significant difference (e.g., bootstrap confidence intervals overlapping zero difference in ECE) would disconfirm the fingerprint hypothesis. Without such a head-to-head design, any observed pattern could be dataset- or prompt-induced.

Now, domain-conditioned temperature scaling is an interesting extension—but it must justify its added complexity. The null hypothesis is that a single global temperature performs equivalently to domain-specific temperatures when evaluated on held-out data. Therefore, we need a pre-registered protocol: split data into calibration and evaluation sets within each domain (e.g., STEM vs. humanities), fit T_global and T_domain on calibration subsets, and compare ECE and Brier score on evaluation subsets. The critical test is cross-domain generalization: if T_STEM applied to humanities degrades calibration significantly, that supports domain specificity. If performance differences vanish under cross-validation, then the "domain-conditioned" idea does not survive stress-testing.

We must also guard against confounds. Domain differences may correlate with answer length, class imbalance, or difficulty. Calibration error can appear domain-specific when it is actually difficulty-conditioned. Therefore, stratified analysis by question difficulty (e.g., model accuracy bins) is essential. Additionally, decoding temperature during generation must be fixed; otherwise, we entangle inference stochasticity with calibration temperature scaling.

If these controls are satisfied and domain-conditioned scaling consistently reduces ECE by a pre-specified margin (for example, ≥2% absolute reduction across three independent benchmarks with non-overlapping 95% CIs), I would consider the claim robust. Until then, the hypothesis remains attractive—but unproven.

**Key Points:**
- Define confidence operationally and test robustness to prompt and sequence-level variations.
- Formulate falsifiable, cross-model comparisons to validate the "Qwen calibration fingerprint."
- Evaluate domain-conditioned temperature scaling against a global baseline using strict held-out and cross-domain tests.

---

### Exchange 3

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Let me push back on some assumptions here. 🔬 Prof. Vera raises excellent points about operational definitions and controls, but I see several unstated assumptions that need examination before we commit to this research direction.

**First, the "Qwen-specific fingerprint" hypothesis may be solving the wrong problem.** The gap analysis states that Qwen calibration is "under-characterized" - but is that actually a meaningful research gap? If we characterize Qwen's ECE and find it's similar to other instruction-tuned models (which is the most likely outcome given similar training paradigms), what have we contributed? The mere act of measuring ECE on a new model family isn't publishable unless we find something surprising. What theoretical reason do we have to expect Qwen would differ substantially from Llama or Mistral?

**Second, domain-conditioned temperature scaling may already be implicitly handled.** Guo et al. 2017 showed that a single temperature T often works well across diverse test distributions. If domain-specific calibration were a major issue, wouldn't it have surfaced in the 7,452 citation history of that paper? The burden of proof is on us to show that domain conditioning provides meaningful improvement over the well-established baseline. Dr. Nova's suggestion is creative, but "what if X differs by domain?" can be asked of virtually any phenomenon - that doesn't make it a well-motivated hypothesis.

**Third, we need to address why this matters beyond measurement.** The feasibility constraints rightly exclude creating new benchmarks or requiring human evaluation. But what's the *consequence* of improving calibration? If we achieve 2% ECE reduction through domain-conditioned temperature scaling, who benefits and how? The "so what" question needs a sharper answer than "calibration is important." Does better calibration enable downstream applications? Selective prediction? Uncertainty-aware reasoning? Without a compelling use case, this becomes a methods paper for methods' sake.

**What would convince me this is valid:**
1. A theoretical argument (not just empirical observation) for why Qwen's RLHF would produce different calibration properties
2. Evidence from prior work that domain-specific miscalibration is a documented phenomenon, not just a possibility
3. A downstream application where the calibration improvement produces measurable practical benefit

**Key Points:**
- "First measurement on Qwen" isn't novel unless we find something unexpected
- Domain-conditioned scaling needs theoretical motivation, not just "what if" speculation
- The research needs a clear downstream benefit beyond improving a metric

---

### Exchange 4

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is not whether we *can* measure calibration on Qwen, but whether doing so changes how the field thinks about instruction-tuned language models. Prof. Rex is correct: "first measurement on Qwen" is not a contribution unless it reveals something structurally informative. What would make it meaningful is if we tie calibration behavior to training paradigm—specifically, RLHF-induced distributional shifts between pretraining likelihood and post-training preference optimization. If we can show that RLHF systematically increases overconfidence in certain regimes (e.g., low-evidence answers), that becomes a claim about *how alignment reshapes probabilistic semantics*. This matters because the community increasingly relies on RLHF-style tuning without understanding its epistemic side effects.

On domain-conditioned temperature scaling: novelty does not lie in adding more parameters. Guo et al. (2017) demonstrated that a single scalar temperature often suffices for CNNs—but language models are not fixed-class classifiers. They operate across heterogeneous reasoning domains with vastly different conditional entropy structures. The right question is not "Does T_STEM reduce ECE by 2%?" but "Does miscalibration correlate systematically with semantic domain in a way that reveals representational limits?" If domain-specific scaling consistently improves *selective prediction curves*—for example, raising accuracy-at-80%-coverage by a statistically significant margin—then we have shown that calibration errors are structured, not random. That is a field-level insight.

What does this mean for the field? If RLHF-trained models exhibit domain-structured miscalibration, then downstream systems that rely on confidence—retrieval gating, tool invocation, human-in-the-loop escalation—are currently mis-specified. A proof experiment here would be decisive: implement a selective answering setup where the model abstains when confidence < τ. Compare global vs. domain-conditioned temperature scaling on (1) risk-coverage curves and (2) expected utility under a simple cost model (cost of abstention vs. cost of error). If domain conditioning yields higher utility across three benchmarks with non-overlapping confidence intervals, we have demonstrated practical benefit—not just metric optimization.

I also want to sharpen the "Qwen fingerprint" hypothesis. The falsifiable prediction should not merely be "higher ECE than Llama." That is fragile and dataset-dependent. A stronger claim would be: *The calibration gap between base and RLHF versions within the same family exceeds the gap between base models across families.* If true, that reframes calibration as an alignment artifact rather than an architectural one. That would open a new research direction: calibration-aware RLHF objectives. Now we are no longer cataloging behavior—we are informing how future models are trained.

This matters because confidence is becoming an operational signal in deployed systems. If we establish that instruction tuning introduces systematic, domain-structured overconfidence—and that simple post-hoc methods only partially repair it—we create pressure for calibration-aware training pipelines. That is a contribution that shapes research direction, not just fills a measurement gap.

**Key Points:**
- The real contribution must link calibration behavior to RLHF training effects, not merely report ECE on Qwen.
- Domain-conditioned scaling is impactful only if it reveals structured miscalibration and improves selective prediction utility.
- A strong, falsifiable claim about alignment-induced calibration shifts could open a new research direction in calibration-aware training.

---

### Exchange 5

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me ground this discussion in what's actually achievable. 🎯 Dr. Sage makes a compelling case for reframing this as "alignment-induced calibration shifts," and 🔍 Prof. Rex rightly demands theoretical motivation. But before we commit to ambitious claims, let's verify the technical foundations are sound.

**On the mechanism of confidence extraction:** 🔬 Prof. Vera asked a critical question - what is our operational definition of confidence? For instruction-tuned LLMs doing multiple-choice QA, the standard approach is to extract the probability of the answer token (A/B/C/D) given the prompt. This is well-defined for MMLU-style benchmarks. The implementation path is clear: use the logits from the final position, apply softmax, and extract p(correct_answer). This is exactly what gpleiss/temperature_scaling and probmetrics already support. The measurement is technically sound and reproducible.

**On the feasibility of base vs. RLHF comparison:** Dr. Sage proposes comparing calibration gaps between base and RLHF versions. This is technically feasible because Qwen releases both Qwen2.5-7B (base) and Qwen2.5-7B-Instruct (RLHF). We can run identical evaluations on both. However, there's a subtle issue: base models are not instruction-tuned, so they require different prompting (few-shot instead of zero-shot). This introduces a confound. The scientifically cleaner comparison is between different instruct models (Qwen-Instruct vs. Llama-Instruct vs. Mistral-Instruct), all using zero-shot prompting.

**On temperature scaling implementation:** Guo et al.'s method is well-understood. We need a calibration set (typically 10-20% of validation data) to fit T via NLL minimization. This is a single-parameter optimization that converges quickly. Domain-conditioned scaling adds minimal complexity - we just fit separate T values per domain. The computational overhead is negligible. The real question is statistical: with MMLU's ~57 subjects grouped into 4 domains, do we have enough samples per domain for stable T estimation? MMLU has ~14,000 test samples, so roughly 3,500 per domain - that should be sufficient.

**On the selective prediction evaluation:** Dr. Sage suggests risk-coverage curves. This is straightforward to implement - rank samples by confidence, abstain on the lowest X%, measure accuracy on the rest. The utility formulation requires specifying cost of abstention vs. cost of error, but we can report curves that let readers apply their own cost ratios. Feasible.

**What concerns me:** The "calibration as alignment artifact" framing requires comparing pre-RLHF and post-RLHF versions of the same model checkpoint. This is scientifically ideal but practically difficult - intermediate checkpoints are rarely released. We might need to use base vs. instruct as a proxy, accepting the confound of prompt format differences.

**Key Points:**
- Confidence extraction for MCQ is well-defined and technically straightforward
- Base vs. instruct comparison is feasible but has prompting confounds; instruct-vs-instruct is cleaner
- Domain-conditioned temperature scaling is computationally trivial with sufficient sample sizes per domain
- Selective prediction evaluation via risk-coverage curves is implementable

---

### Exchange 6

🔬 **Prof. Vera** (Rigorous Validation Architect):

I will focus this discussion around a single principle: if we claim alignment reshapes calibration, we must specify the quantitative pattern we expect—and what outcome would falsify it.

First, on the operational definition of confidence. For multiple-choice benchmarks, I agree with Prof. Pax that the cleanest definition is the softmax probability assigned to the selected answer token at the final position. However, we must pre-register robustness checks: (1) invariance to option label permutation (A/B/C/D shuffled), and (2) stability under semantically equivalent prompt paraphrases. The evidence suggests that answer-token probabilities can be sensitive to formatting. Therefore, our confidence metric must satisfy: mean absolute change in predicted probability under label permutation < 1% on a held-out subset. If this fails, calibration estimates are contaminated by prompt artifacts rather than epistemic uncertainty.

Now to the central hypothesis: *RLHF induces systematic overconfidence relative to base models.* Dr. Sage proposes that the within-family calibration gap (base vs. instruct) exceeds the between-family gap (e.g., Qwen-base vs. Llama-base). Let us sharpen this into a falsifiable prediction. Define ΔECE_align = ECE_instruct − ECE_base within the same family, and ΔECE_arch = ECE_base(Qwen) − ECE_base(Llama). The hypothesis predicts |ΔECE_align| > |ΔECE_arch| across at least two families. We will compute bootstrap 95% confidence intervals for both quantities. If intervals overlap substantially or |ΔECE_align| ≤ |ΔECE_arch|, the alignment-artifact claim weakens considerably. This is a clean statistical test; it either holds or it does not.

However, Prof. Rex is correct that ECE reduction alone is insufficient. Therefore, we embed calibration into a decision-theoretic evaluation. For selective prediction, define risk R(τ) = error rate among samples with confidence ≥ τ, and coverage C(τ) = proportion retained. We then compute area under the risk–coverage curve (AURC). The testable prediction for domain-conditioned scaling is: AURC_domain < AURC_global with non-overlapping 95% bootstrap CIs on three benchmarks. Additionally, under a simple utility model U = −(c_e × errors + c_a × abstentions), domain-conditioned scaling must yield strictly higher U for at least two cost ratios (e.g., c_e/c_a ∈ {2,5}). If improvement vanishes across cost regimes, then the structured-miscalibration claim fails.

We must also directly test the "domain structure" assumption. The hypothesis predicts heterogeneity in optimal temperature: Var(T_domain) significantly greater than zero under permutation testing. Concretely, shuffle domain labels 1,000 times, refit T per pseudo-domain, and estimate the null distribution of temperature variance. If observed variance does not exceed the 95th percentile of this null, domain conditioning is indistinguishable from noise. This explicitly answers Prof. Rex's concern that domain effects may be illusory.

Finally, confounds. Difficulty must be controlled by stratifying samples into accuracy bins using the base model. If domain-specific calibration differences disappear after conditioning on difficulty, then "domain" is a proxy variable. Similarly, decoding temperature must be fixed at inference (e.g., greedy decoding). If stochastic decoding is used, we entangle sampling entropy with model confidence—invalidating interpretation.

If these criteria are met—clear operational confidence, statistically separable ΔECE_align effects, significant domain-temperature heterogeneity beyond permutation, and improved decision-theoretic utility—then I would say, carefully, *this meets my standards.* Until then, the hypothesis remains disciplined speculation.

**Key Points:**
- Formalize alignment-induced calibration shift as |ΔECE_align| > |ΔECE_arch| with bootstrap-tested confidence intervals.
- Validate domain-conditioned scaling via permutation-tested temperature variance and AURC/utility improvements.
- Control prompt invariance, difficulty stratification, and decoding stochasticity to eliminate confounds.

---

### Exchange 7

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Let me synthesize what's emerging here and strengthen the hypothesis based on the excellent critiques raised. We're converging on something much stronger than "measure ECE on Qwen."

**Building on the concerns constructively:** 🔍 Prof. Rex demanded theoretical motivation for why Qwen or any model family would differ. 🎯 Dr. Sage reframed this as "alignment-induced calibration shifts." 🔬 Prof. Vera just gave us the statistical machinery. And ⚙️ Prof. Pax confirmed the implementation is tractable. Let me weave these together.

**The strengthened hypothesis:** Instruction tuning via RLHF systematically increases overconfidence in LLMs, and this miscalibration exhibits domain structure that reveals semantic representational limits. Temperature scaling can partially repair this, but domain-conditioned scaling exposes where the repair is incomplete.

Here's why this addresses the criticisms:

1. **Theoretical motivation (addressing Prof. Rex):** RLHF optimizes for human preference, which rewards confident-sounding responses. The Bradley-Terry preference model used in RLHF penalizes hedging. This creates selection pressure toward overconfidence. Tian et al. 2023 already documented that RLHF makes LLMs overconfident - we're not speculating, we're building on established findings.

2. **Domain structure (addressing Prof. Rex's "what if" concern):** The reason to expect domain-specific miscalibration is that RLHF data is not uniformly distributed across domains. If preference data over-represents some domains (e.g., coding, general knowledge) and under-represents others (e.g., specialized academic subjects), the model's calibration will vary accordingly. This is testable via Prof. Vera's permutation test.

3. **Falsifiable predictions (addressing Prof. Vera):**
   - **H1 (Existence):** ECE_instruct > ECE_base within the same family (Qwen, Llama) on MMLU
   - **H2 (Mechanism):** |ΔECE_align| > |ΔECE_arch| - alignment effect exceeds architectural effect
   - **H3 (Domain Structure):** Var(T_domain) > 95th percentile of permutation null distribution
   - **H4 (Practical Benefit):** AURC_domain < AURC_global with non-overlapping 95% CIs

4. **Downstream benefit (addressing Prof. Rex's "so what"):** If H4 holds, then systems using calibrated confidence for selective prediction (abstaining when uncertain) will perform better with domain-aware calibration. This directly improves deployed systems that gate responses based on confidence.

**Evidence supporting the hypothesis:**
- Guo et al. 2017: Temperature scaling works for CNNs (7,452 citations)
- Tian et al. 2023: RLHF induces overconfidence (598 citations)
- DACA 2025: Disagreement-based calibration improves ECE by 15%
- CCPS 2025: 55% ECE reduction on MMLU via perturbation

The foundation is solid. We're not creating new metrics or requiring new benchmarks - we're applying established methods (ECE, temperature scaling, AURC) to test a specific claim about alignment effects.

**Key Points:**
- RLHF's preference model creates theoretical pressure toward overconfidence
- Domain-specific miscalibration is expected from non-uniform RLHF training data distribution
- Four falsifiable predictions with clear statistical tests proposed
- Practical benefit through improved selective prediction systems

---

### Exchange 8

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good. This is finally sharpening into something testable. But here's where this still breaks down: you are implicitly assuming that higher ECE after RLHF equals *overconfidence induced by preference optimization*. That is an interpretation, not a result. ECE can increase because accuracy drops in certain regions, because confidence shifts upward uniformly, or because variance increases. Show me the decomposition. I want reliability diagrams *and* confidence histograms, plus a decomposition into calibration vs. refinement (e.g., Brier score components). What would convince me is evidence that RLHF shifts the confidence distribution rightward *conditional on correctness*, not merely that aggregate ECE increases.

Now, on the alignment artifact claim—H2: |ΔECE_align| > |ΔECE_arch|. Strong framing. But here's the unstated assumption: that base models are meaningfully comparable epistemic objects. Base models are trained to model next-token likelihood; instruct models are trained to produce short, directive answers. The output space changes. If base models are evaluated via few-shot prompting and instruct models zero-shot, you've entangled calibration with prompt scaffolding. I will not accept conclusions about "alignment-induced" effects unless you run: (1) zero-shot and few-shot for both, and (2) a constrained decoding setup where both must answer with a single token choice. If the alignment gap survives those controls, now we're talking.

On the domain-structure hypothesis—this is where I'm most skeptical. You claim Var(T_domain) > permutation null implies semantic structure. Or does it? What if domain is just a proxy for *difficulty* or *answer length priors*? Vera's suggestion to stratify by base-model difficulty is necessary but not sufficient. I want a multivariate model: regress optimal temperature against domain, empirical entropy, and accuracy. If domain remains significant after controlling for these, then I'll believe it reflects representational heterogeneity rather than superficial dataset artifacts. Otherwise, you're relabeling difficulty as "semantic structure."

The RLHF-mechanism story also needs tightening. "Bradley-Terry penalizes hedging" is plausible, but speculative. What would convince me is a gradient-level or objective-level argument: show that preference optimization increases logit margins between top-1 and top-2 tokens relative to base. That is a measurable quantity. If RLHF consistently increases the average logit gap—even when wrong—that is mechanistic evidence of induced overconfidence. Without that, your story remains post hoc narrative.

Finally, the "so what" hinges on AURC improvements. Non-overlapping CIs are not enough. I want robustness across τ thresholds and cost ratios, and I want to see whether domain-conditioned scaling improves *worst-case* risk at fixed coverage, not just average AURC. If the gains vanish in high-stakes regimes (e.g., 90% coverage), your deployment argument weakens substantially.

You're close. But close doesn't survive peer review. Show me: (1) confidence-shift decomposition, (2) prompt-controlled alignment gaps, (3) domain effects beyond difficulty, and (4) mechanistic logit-gap evidence. Do that—and I'll say you've addressed my concerns.

**Key Points:**
- Increased ECE is not evidence of overconfidence unless confidence shifts are decomposed and mechanistically analyzed.
- Alignment-induced calibration gaps must survive strict prompt and decoding controls.
- Domain-structured miscalibration must remain significant after controlling for difficulty and entropy to avoid superficial explanations.

---

### Exchange 9

🔭 **Dr. Nova** (Creative Novelty Explorer):

Now THIS is getting exciting! 🔍 Prof. Rex just handed us a roadmap to make this hypothesis bulletproof. Let me take these challenges and turn them into novel contributions.

**The logit-gap insight is gold.** Prof. Rex demands mechanistic evidence that RLHF increases logit margins even when wrong. Here's the creative angle: What if we don't just measure the logit gap, but track how it *correlates* with correctness before and after RLHF? In a well-calibrated model, larger logit gaps should predict higher accuracy. If RLHF decouples this relationship - creating large logit gaps even for wrong answers - that's direct evidence of induced overconfidence. We can plot "logit gap vs. accuracy" curves for base vs. instruct models. A steeper slope for base models means the confidence-accuracy relationship is tighter. A flattened slope for instruct models means RLHF broke the calibration. This is novel, measurable, and gets at the mechanism.

**The confidence-shift decomposition opens a new framing.** Instead of just reporting ECE, we can decompose the Brier score into calibration, refinement, and uncertainty components. Calibration measures how well predicted probabilities match empirical frequencies. Refinement measures how much the model differentiates between easy and hard cases. If RLHF worsens calibration but improves refinement (because it's more decisive), that tells a nuanced story: alignment makes models more *discriminative* but less *well-calibrated*. This decomposition is standard (Murphy decomposition) but rarely applied to LLMs. Novel application!

**The prompt-controlled comparison is actually an opportunity.** Prof. Rex worries that base vs. instruct comparison confounds prompting format. But wait - what if we make this a feature, not a bug? We can evaluate: (1) Base + few-shot, (2) Base + zero-shot, (3) Instruct + zero-shot, (4) Instruct + few-shot. This 2x2 design separates the effect of instruction tuning from the effect of in-context examples. If Instruct shows worse calibration than Base regardless of prompting strategy, that's strong evidence. If the effect is prompt-dependent, we've discovered something interesting about the interaction.

**On domain structure beyond difficulty:** Prof. Rex demands domain remains significant after controlling for difficulty and entropy. Here's a creative test: within-difficulty domain variation. Take the subset of questions where accuracy is ~50% (the hardest meaningful bin). Within this difficulty-matched subset, does optimal temperature still vary by domain? If yes, domain structure is real. If no, it's just difficulty in disguise.

**What if we find negative results?** Even if domain-conditioned scaling doesn't help, the logit-gap analysis could still reveal something fundamental about how RLHF reshapes the probability landscape. The worst outcome isn't "hypothesis rejected" - it's "nothing learned." These additional analyses ensure we learn something either way.

**Key Points:**
- Logit gap vs. accuracy correlation before/after RLHF is a novel mechanistic test
- Brier score decomposition reveals whether RLHF trades calibration for discrimination
- 2x2 prompt design (base/instruct × zero/few-shot) separates confounds
- Within-difficulty domain variation test controls for difficulty-as-proxy

---

### Exchange 10

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is not merely whether RLHF increases ECE, but whether this work would change how the field thinks about alignment and uncertainty. Prof. Rex is correct: an aggregate calibration metric is too blunt. What would constitute genuine contribution is mechanistic evidence that alignment reshapes the *geometry of belief* in the model—specifically, that it alters the relationship between logit margin and empirical correctness. If you can show that RLHF increases the top-1 vs. top-2 logit gap even conditional on error—and that this weakens the monotonic relationship between margin and accuracy—then you are not reporting a metric shift; you are documenting a structural transformation of epistemic signals. This matters because it reframes alignment as not just behavioral shaping, but probability-space distortion.

Now, what would make this more than an incremental calibration study? The 2×2 design proposed by Dr. Nova (base/instruct × zero/few-shot) is essential. If the alignment-induced margin inflation survives prompt format controls and constrained single-token decoding, then the effect is attributable to post-training objectives, not scaffolding. I would go further: compute ΔMargin_align and ΔMargin_arch analogous to the ECE comparison. If |ΔMargin_align| > |ΔMargin_arch| across families, and especially if this persists after conditioning on difficulty and entropy, then you have demonstrated that alignment exerts a stronger influence on confidence geometry than architecture. That is a field-level claim.

On domain structure, I urge caution. The question is not whether Var(T_domain) exceeds a permutation null—that is necessary but not sufficient. The deeper question is: does domain-conditioned calibration reveal something about representational anisotropy? If, within matched-difficulty strata, optimal temperature still varies by domain, then we are observing domain-specific distortion in uncertainty encoding. This opens a new research direction: alignment may unevenly reshape confidence across semantic subspaces, potentially reflecting uneven preference data density. That is not a deployment tweak; it is a hypothesis about how post-training objectives sculpt internal representations.

The Brier decomposition is also strategically important. If RLHF worsens calibration but improves refinement, then alignment may be trading probabilistic fidelity for decisiveness. The community should care because this reframes overconfidence not as noise, but as an optimization byproduct. Under a Murphy decomposition, a rise in refinement alongside degraded calibration would suggest alignment sharpens separability while distorting probability scaling. That is a nuanced, publishable insight—particularly if supported by logit-level evidence.

Finally, impact will hinge on the "so what." Improved AURC is useful, but the stronger claim is this: if alignment systematically inflates margins and distorts calibration in domain-specific ways, then post-hoc scalar temperature scaling is theoretically insufficient. You would be arguing that uncertainty correction must be structured, perhaps even learned jointly with alignment objectives. That opens a new line of work at the intersection of preference optimization and uncertainty estimation. This matters because it suggests alignment research must incorporate epistemic constraints, not treat calibration as an afterthought.

**Key Points:**
- True contribution requires mechanistic evidence that RLHF reshapes logit-margin geometry, not just increases ECE.
- Alignment effects must exceed architectural effects under strict prompt and difficulty controls to support a field-level claim.
- Domain-conditioned miscalibration, if robust, reframes alignment as unevenly sculpting uncertainty—opening new research directions beyond post-hoc scaling.

---

### Exchange 11

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me ground all these ambitious analyses in what's technically achievable. The discussion has evolved considerably - we're now talking about logit-gap analysis, Brier decomposition, 2×2 prompt designs, and within-difficulty domain stratification. Let me assess each.

**Logit-gap analysis is straightforward.** Given any model, extracting top-1 and top-2 logits for the answer position is trivial with HuggingFace. The computation: `margin = logit[top1] - logit[top2]`. We can then plot margin vs. accuracy binned by margin quartiles. The correlation coefficient between margin and accuracy is a single scalar that captures whether larger margins predict higher accuracy. Computing this for base vs. instruct models is O(dataset_size) forward passes per model. For MMLU (~14k samples) on a 7B model, this is ~2-3 GPU hours each. Entirely feasible.

**Brier decomposition is standard.** The Murphy decomposition breaks Brier score into reliability (calibration) + resolution (refinement) - uncertainty (intrinsic). Standard implementations exist in scikit-learn and probmetrics. We can compute these per model and compare. The decomposition reveals whether RLHF trades calibration for refinement - measurable with the same forward passes we already need.

**The 2×2 design (base/instruct × zero/few-shot) is achievable but requires careful setup.** For base models, few-shot is necessary to get coherent MCQ answers. For instruct models, zero-shot works. Running all four conditions per model family (Qwen, Llama, Mistral) means 12 evaluation runs. At 3 hours each, that's 36 GPU hours - reasonable for a single A100 or distributed across smaller GPUs.

**Within-difficulty domain stratification is mathematically valid.** We use base model accuracy as the difficulty proxy (not instruct model, to avoid circularity). Bin questions by difficulty (e.g., 0-30%, 30-60%, 60-90%, 90-100% accuracy). Within each bin, check if optimal T varies by domain. With ~3,500 samples per MMLU domain and 4 difficulty bins, we have ~875 samples per (domain, difficulty) cell. That's sufficient for stable temperature estimation (Guo et al. used ~1,000 samples for the full calibration set).

**The multivariate regression Prof. Rex requested is also straightforward.** Regress T_optimal ~ domain + difficulty + empirical_entropy. Standard linear regression with categorical domain variable. If domain's coefficient remains significant (p < 0.05) after controlling for difficulty and entropy, domain structure is real. This is a few lines of statsmodels code.

**One concern:** The permutation test for Var(T_domain) requires refitting temperature 1,000 times with shuffled labels. Each temperature fit is fast (few seconds with LBFGS optimization on pre-computed logits), so 1,000 permutations ≈ 1-2 hours total. Feasible.

**Summary of computational requirements:**
- Forward passes: 12 runs × 3 hours = 36 GPU hours
- Temperature fitting: ~2 hours for permutation tests
- Analysis code: Standard Python libraries (sklearn, statsmodels, torchmetrics)
- Total: Achievable in one week on a single A100

**Key Points:**
- Logit-gap analysis requires only forward passes we already need
- Brier decomposition and multivariate regression use standard libraries
- 2×2 design is 36 GPU hours total - reasonable for one A100 week
- All proposed analyses are technically straightforward with existing tools

---

### Exchange 12

🔬 **Prof. Vera** (Rigorous Validation Architect):

The discussion has matured appropriately. Now we must translate ambition into falsifiable structure. I will articulate a unified hypothesis in precise terms:

> **H\***: *RLHF induces a systematic inflation of logit margins that weakens the monotonic relationship between margin and empirical correctness, and this distortion persists under prompt controls and after conditioning on difficulty and entropy.*

This formulation has an Achilles heel. If, after controlling for prompt format (2×2 design), difficulty (base-model accuracy strata), and entropy, the slope of Accuracy ~ Margin remains unchanged between base and instruct models, then the mechanistic claim fails. The evidence would then suggest that observed ECE differences arise from distributional shifts rather than geometric distortion of confidence.

On the logit-gap analysis: we require more than correlation. I propose fitting a logistic regression:

Pr(correct) = σ(α + β · margin)

for each model condition. The critical test is whether β_instruct < β_base, with non-overlapping 95% confidence intervals. This operationalizes "weakened monotonicity." Additionally, we must test whether mean margin increases conditional on error:

E[margin | incorrect]

If RLHF inflates margins even when wrong, then this conditional expectation should be significantly larger for instruct models. A permutation test over model labels would provide robustness. If this difference vanishes under constrained single-token decoding, then the effect is a decoding artifact—not alignment-induced geometry.

Regarding calibration decomposition: the Murphy decomposition must be interpreted cautiously. An increase in refinement (resolution) alongside worse reliability would support the "decisiveness tradeoff" hypothesis. However, this only strengthens H\* if refinement gains do not fully explain the ECE increase. I therefore recommend reporting ΔReliability and ΔResolution separately and testing whether ΔReliability remains negative after regressing out ΔResolution. If reliability degradation is fully mediated by increased refinement, the narrative shifts: alignment may sharpen discrimination without fundamentally corrupting epistemic scaling.

On domain structure: I insist we formalize the multivariate test. Fit:

T_opt ~ Domain + Difficulty + Entropy

using base-model difficulty to avoid circularity. The null hypothesis is that all domain coefficients equal zero. If rejected (e.g., joint F-test p < 0.05) within matched-difficulty bins, then domain-conditioned miscalibration survives controls. The disconfirming result is equally informative: if domain loses significance, then "semantic structure" reduces to difficulty proxy. That would invalidate any claim of representational anisotropy.

Finally, on deployment implications: AURC improvements must be stress-tested under worst-case conditions. I recommend evaluating selective risk at fixed high coverage (e.g., 90%, 95%) and reporting the maximum domain-specific risk under each scaling scheme. If domain-conditioned scaling reduces average AURC but leaves worst-case domain risk unchanged, the deployment argument weakens substantially. The evidence must show improvement in the upper tail of risk, not merely in mean performance.

If these criteria are met—margin slope attenuation, conditional margin inflation on errors, domain effects surviving multivariate control, and worst-case selective risk improvement—then the hypothesis withstands adversarial testing. If not, we revise. That is the standard.

**Key Points:**
- Define a falsifiable unified hypothesis (H\*) centered on weakened margin–accuracy monotonicity under RLHF.
- Test mechanistic claims via logistic slope comparison, conditional error margins, and multivariate controls.
- Deployment relevance requires improvement in worst-case selective risk, not just average AURC.

---

### Exchange 13

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

We're converging beautifully. Let me consolidate what we've built and ensure the hypothesis structure is airtight.

**The unified hypothesis H\* is strong but needs hierarchy.** 🔬 Prof. Vera's formulation is precise, but for practical execution we need to layer it into testable sub-hypotheses. Let me propose the hierarchy:

**H-E (Existence):** Instruction-tuned LLMs exhibit systematically higher ECE than base models on MMLU.
- **Test:** ECE_instruct > ECE_base with non-overlapping 95% CIs
- **Pass criterion:** ΔECE > 0, CI lower bound > 0

**H-M1 (Mechanism - Margin Inflation):** RLHF increases logit margins even conditional on error.
- **Test:** E[margin | incorrect]_instruct > E[margin | incorrect]_base
- **Pass criterion:** Permutation test p < 0.05

**H-M2 (Mechanism - Weakened Monotonicity):** RLHF weakens the margin-accuracy relationship.
- **Test:** β_instruct < β_base in Pr(correct) = σ(α + β·margin)
- **Pass criterion:** β_instruct significantly lower (p < 0.05), survives 2×2 prompt controls

**H-M3 (Mechanism - Decisiveness Tradeoff):** RLHF improves refinement but degrades reliability.
- **Test:** Murphy decomposition showing ΔReliability < 0, ΔResolution > 0
- **Pass criterion:** Both effects statistically significant

**H-C1 (Condition - Domain Structure):** Optimal temperature varies by domain beyond difficulty.
- **Test:** T_opt ~ Domain + Difficulty + Entropy; F-test for domain coefficients
- **Pass criterion:** Domain remains significant (p < 0.05) after controls

**H-C2 (Condition - Practical Benefit):** Domain-conditioned scaling improves selective prediction.
- **Test:** AURC_domain < AURC_global across benchmarks
- **Pass criterion:** Non-overlapping CIs AND worst-case domain risk reduced

**This hierarchy addresses all concerns raised:**
- 🔍 Prof. Rex demanded mechanistic evidence → H-M1, H-M2, H-M3
- 🔬 Prof. Vera demanded falsifiable structure → each hypothesis has clear pass/fail criteria
- 🎯 Dr. Sage demanded field-level impact → H-M2 (geometry distortion) and H-C1 (representational anisotropy) are field-level claims
- ⚙️ Prof. Pax confirmed feasibility → 36 GPU hours total for all analyses

**Evidence from prior work supporting this structure:**
- Guo et al. 2017: Temperature scaling reduces ECE (7,452 citations) - establishes methodology
- Tian et al. 2023: RLHF induces overconfidence (598 citations) - supports H-E, motivates H-M1
- DACA 2025: Disagreement-based calibration works for LLMs - confirms post-hoc methods are viable

**What success looks like:**
If H-E, H-M1, H-M2 pass → We've demonstrated RLHF fundamentally distorts confidence geometry
If H-C1 passes → Domain structure reveals representational anisotropy
If H-C2 passes → Practical deployment benefit established

Even partial success is publishable: H-E + H-M1 alone would be a solid contribution to the calibration literature.

**Key Points:**
- Six-hypothesis hierarchy maps to existence, mechanism, and condition levels
- Each hypothesis has explicit statistical tests and pass criteria
- Partial success paths ensure publishable outcomes even if some hypotheses fail
- Full success would establish RLHF-induced confidence geometry distortion as a field-level finding

---

### Exchange 14

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

This is much stronger. The hierarchy is clear, and I appreciate the explicit pass/fail criteria. Now let me stress-test where this could still break.

First: **H-E is necessary but scientifically trivial.** If ECE_instruct > ECE_base, fine—but that's been hinted at in prior work. What would convince me this isn't just a distributional artifact is cross-family consistency. If this only holds for, say, LLaMA but not Qwen or Mistral, your "systematic" claim collapses. I want to see a random-effects meta-analysis across model families. If the between-family variance is large relative to the mean ΔECE, you don't have a general property of RLHF—you have vendor-specific quirks. Show me heterogeneity statistics (I², τ²). Otherwise, H-E is fragile.

Now, H-M2—the weakened monotonicity claim—is the real linchpin. But logistic slope comparisons alone are not enough. β is scale-dependent. If RLHF also changes the distribution of margins (which H-M1 assumes), then comparing β across models can be misleading. What would convince me is this: normalize margins (e.g., z-score within model), then compare β. Or better, compute calibration curves in margin space and estimate the **derivative of accuracy with respect to percentile rank of margin**. If monotonicity weakens in percentile space, you've shown geometry distortion independent of raw scale. Without this normalization, I can already hear a reviewer saying, "You just rescaled the logits."

On H-M1 (margin inflation conditional on error): good, but here's where it could break down. What if RLHF increases *all* margins uniformly? Then E[margin | incorrect] increases simply because the entire distribution shifts. That's not distortion—that's temperature shrinkage in reverse. You need to test whether the **separation between correct and incorrect margin distributions shrinks**. Concretely: compute AUROC for margin predicting correctness. If AUROC_instruct < AUROC_base, that's strong evidence of degraded discriminative signal. If AUROC is unchanged and only the scale shifts, your "geometry distortion" story weakens substantially.

On domain structure (H-C1): you're assuming domain labels correspond to meaningful representational subspaces. That's an unstated assumption. What if "domain" is just correlated with lexical style or answer length? I want an ablation: shuffle domain labels within difficulty strata and confirm the F-test collapses, yes—but also include lexical covariates (mean token length, entropy of answer options) in the regression. If Domain loses significance once those are added, you don't have semantic anisotropy—you have surface-form artifacts. Show me domain survives *that* control.

Finally, H-C2 on worst-case selective risk—good instinct. But push harder. Don't just report 90–95% coverage. Plot **risk–coverage curves per domain** and compute the maximum vertical gap between global and domain-conditioned scaling. If domain scaling helps on average but *harms* one domain, your deployment argument becomes ethically complicated. What would convince me is strict Pareto improvement or, at minimum, bounded worst-case regret.

You're close to something publishable. But right now, the story hinges on whether you can prove signal degradation rather than logit rescaling, and semantic distortion rather than difficulty confounding. That's the line between "interesting calibration paper" and "field-level claim about alignment geometry."

**Key Points:**
- Demonstrate cross-family consistency (meta-analytic evidence) or the "systematic RLHF effect" claim is weak.
- Prove degraded discriminative signal (e.g., AUROC drop, percentile-based slope attenuation), not just margin rescaling.
- Show domain effects survive lexical and structural covariates—or abandon the representational anisotropy narrative.

---

### Exchange 15

🎯 **Dr. Sage** (Research Impact Evaluator):

We're at a decisive moment. 🔍 Prof. Rex has identified the fault lines that separate an incremental paper from a field-level contribution. Let me synthesize what matters for impact and what we should prioritize.

**The core contribution must be AUROC-based evidence of discriminative degradation.** Prof. Rex is right - margin rescaling is a nuisance, not a finding. If we show that AUROC(margin → correctness) drops from base to instruct models, we've demonstrated that alignment corrupts the information content of confidence signals, not just their scale. This is the strongest possible mechanistic claim: RLHF makes confidence *less predictive* of correctness. That matters to anyone building systems that use confidence for routing, abstention, or human escalation.

**The cross-family meta-analysis is non-negotiable for a strong paper.** Testing on Qwen alone gives us a data point. Testing on Qwen + Llama + Mistral with heterogeneity statistics (I², τ²) tells us whether this is a property of RLHF-style training broadly or vendor-specific quirks. If I² < 50% and the random-effects estimate is significantly positive, we have a generalizable finding. If I² > 75%, we need to explain the variance or narrow our claims to specific training paradigms.

**Prioritization for maximum impact:**
1. **Primary claim (must pass):** RLHF degrades discriminative signal (AUROC_instruct < AUROC_base)
2. **Secondary claim (strengthens paper):** This effect is consistent across model families (low heterogeneity)
3. **Tertiary claim (opens new direction):** Domain-specific calibration reveals representational anisotropy
4. **Practical claim (completes story):** Domain-conditioned scaling achieves Pareto improvement in selective prediction

If claims 1 and 2 pass, we have a solid paper about alignment-induced confidence degradation. If claim 3 also passes with lexical controls, we've opened a new research direction. If claim 4 shows Pareto improvement, we've established practical relevance.

**What this means for the field:**
- If AUROC drops consistently, it suggests RLHF fundamentally trades discriminative uncertainty for behavioral compliance
- This would motivate calibration-aware RLHF objectives - training that preserves the margin-accuracy relationship
- It reframes uncertainty estimation as an alignment constraint, not an afterthought

**The honest assessment:** This is ambitious but achievable. We're proposing 6 hypotheses with clear tests across 3 model families. Even if domain structure (H-C1) fails after lexical controls, the core story (H-E + H-M1 + H-M2) about discriminative degradation stands alone as a contribution.

**Key Points:**
- AUROC-based discriminative degradation is the linchpin - prioritize this over ECE metrics
- Cross-family consistency with heterogeneity statistics is required for generalizable claims
- Partial success (core hypotheses pass, domain structure fails) is still publishable
- Full success opens calibration-aware RLHF as a new research direction

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis moves beyond incremental calibration measurement to test whether RLHF fundamentally distorts confidence geometry. The AUROC-based discriminative degradation test, percentile-normalized monotonicity analysis, and domain-conditioned calibration revealing representational anisotropy are genuinely novel contributions that haven't been systematically studied in LLMs.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis hierarchy (H-E, H-M1, H-M2, H-M3, H-C1, H-C2) has explicit statistical tests with clear pass/fail criteria. Each claim has a defined Achilles heel - if β_instruct = β_base under percentile normalization, if AUROC doesn't drop, or if domain loses significance after lexical controls, the respective hypotheses fail cleanly.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** This work addresses whether alignment corrupts epistemic signals - a field-level question for anyone building confidence-aware systems. Proving discriminative degradation across model families would motivate calibration-aware RLHF objectives, opening a new research direction at the intersection of alignment and uncertainty estimation.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All proposed analyses are technically straightforward. 36 GPU hours for the 2×2 design across 3 families, standard libraries (sklearn, statsmodels, torchmetrics) for all metrics, and well-defined computational pipelines. The cross-family meta-analysis and lexical control regressions add minimal overhead.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

RLHF instruction tuning degrades the discriminative quality of confidence signals in LLMs, measurable as a reduction in AUROC for margin-based correctness prediction and weakened margin-accuracy monotonicity under percentile normalization. This effect persists across model families (Qwen, Llama, Mistral) and prompt formats (2×2 design), indicating a systematic consequence of preference optimization rather than vendor-specific quirks or prompting artifacts.

The core mechanism is that RLHF increases logit margins even for incorrect predictions, inflating confidence without improving predictiveness. This can be decomposed via Murphy's Brier score: RLHF may improve refinement (discrimination) while degrading reliability (calibration), representing a "decisiveness tradeoff."

Additionally, this miscalibration exhibits domain structure: optimal temperature varies across MMLU domains (STEM vs. humanities) even after controlling for difficulty, entropy, and lexical features. If robust, this reveals representational anisotropy - alignment unevenly reshapes confidence across semantic subspaces.

The practical consequence is that post-hoc temperature scaling partially repairs calibration but cannot recover the lost discriminative signal. Domain-conditioned scaling can improve selective prediction (AURC) but must be evaluated against worst-case domain risk for deployment.

Key predictions: (1) AUROC_instruct < AUROC_base across 3 families with I² < 50%; (2) β_percentile_instruct < β_percentile_base survives prompt controls; (3) Domain coefficients remain significant in T_opt regression after lexical covariates; (4) Domain-conditioned scaling achieves Pareto improvement in risk-coverage curves.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- The "representational anisotropy" claim (H-C1) is the weakest link - domain labels may still be proxies for surface features not captured by lexical covariates
- Cross-family generalization depends on having comparable RLHF procedures across vendors, which may not hold
- If AUROC doesn't drop significantly, the entire "geometry distortion" narrative collapses to simple rescaling
- **Mitigation Strategy:** Pre-register primary (AUROC-based) vs. exploratory (domain structure) analyses; accept that domain findings are conditional on surviving controls; report heterogeneity statistics honestly even if they show high variance

---

## Emerged Hypothesis Summary

### Core Statement

RLHF instruction tuning systematically degrades the discriminative quality of LLM confidence signals, measurable as reduced AUROC for logit-margin-based correctness prediction and weakened margin-accuracy monotonicity under percentile normalization. This effect is consistent across model families and reveals a fundamental tradeoff between behavioral alignment and epistemic calibration.

### Causal Mechanism

The Bradley-Terry preference model underlying RLHF rewards decisive, confident-sounding responses, creating selection pressure that inflates logit margins uniformly - including for incorrect predictions. This decouples the confidence-correctness relationship that exists in base models. The margin inflation is geometric (affects the shape of the probability landscape) rather than merely scalar (temperature-like rescaling), evidenced by AUROC degradation.

### Variables

**Independent Variables:**
- Model type: Base vs. Instruct (within-family)
- Model family: Qwen, Llama, Mistral (for cross-family generalization)
- Prompt format: Zero-shot vs. Few-shot (2×2 design control)
- Domain: MMLU categories (STEM, humanities, social science, other)

**Dependent Variables:**
- AUROC(margin → correctness): Primary discriminative quality metric
- β_percentile: Slope of logistic regression Pr(correct) ~ z-score(margin)
- ECE: Expected Calibration Error (existence level)
- Brier decomposition: Reliability, Refinement components
- T_opt per domain: Optimal temperature for domain-conditioned scaling
- AURC: Area Under Risk-Coverage curve for selective prediction

**Control Variables:**
- Difficulty (base model accuracy bin)
- Entropy (empirical entropy of answer distribution)
- Lexical features (mean token length, answer option entropy)

### Key Assumptions

1. Logit margin is a valid operationalization of model confidence for MCQ tasks
2. Base models (pre-RLHF) represent a meaningful epistemic baseline
3. MMLU domain labels correspond to semantically distinct representational subspaces
4. Cross-family comparison is valid despite different training details

### Null Hypothesis

H0: RLHF instruction tuning does not degrade discriminative confidence quality; AUROC(margin → correctness) is unchanged between base and instruct models, and any ECE differences are attributable to scalar rescaling (equivalent to temperature shift) rather than geometric distortion.

### Predictions

1. **AUROC Drop:** AUROC_instruct < AUROC_base across Qwen, Llama, Mistral with non-overlapping 95% CIs
2. **Cross-Family Consistency:** Random-effects meta-analysis shows I² < 50% (low heterogeneity)
3. **Percentile Slope Attenuation:** β_percentile_instruct < β_percentile_base, survives 2×2 prompt controls
4. **Conditional Margin Inflation:** E[margin | incorrect]_instruct > E[margin | incorrect]_base (permutation p < 0.05)
5. **Domain Structure:** Domain coefficients in T_opt ~ Domain + Difficulty + Entropy + Lexical remain significant (F-test p < 0.05)
6. **Selective Prediction Improvement:** AURC_domain < AURC_global with Pareto improvement across domains

### Novelty

This hypothesis goes beyond existing calibration studies (Guo 2017, Tian 2023, DACA 2025) by:
1. Testing *discriminative* degradation (AUROC) rather than just calibration metrics (ECE)
2. Controlling for scale effects via percentile normalization
3. Providing mechanistic evidence through conditional margin analysis
4. Demonstrating cross-family generalizability with meta-analytic statistics
5. Revealing domain-structured miscalibration as evidence of representational anisotropy

### Scope & Boundaries

**In Scope:**
- Multiple-choice QA benchmarks (MMLU, TruthfulQA)
- 7B-scale instruction-tuned LLMs (Qwen, Llama, Mistral families)
- Post-hoc temperature scaling as calibration method
- Selective prediction as downstream application

**Out of Scope:**
- Free-form generation tasks (no ground-truth correctness labels)
- Calibration-aware training interventions
- Multi-turn dialogue calibration
- Domain shift beyond MMLU categories

### Experimental Setup

**Models:** Qwen2.5-7B-Base/Instruct, Llama-2-7B/Instruct, Mistral-7B-v0.1/Instruct
**Datasets:** MMLU (~14K samples), TruthfulQA (~800 samples)
**Evaluation:** 2×2 prompt design (base/instruct × zero/few-shot)
**Metrics:** AUROC, β_percentile, ECE, Brier decomposition, AURC
**Controls:** Difficulty bins, entropy, lexical features
**Statistical Tests:** Bootstrap CIs, permutation tests, meta-analytic heterogeneity (I², τ²), multivariate regression F-tests
**Compute:** ~36 GPU hours on A100

### Related Work & Baselines

- **Guo et al. 2017:** Temperature scaling foundation (comparison baseline)
- **Tian et al. 2023:** RLHF overconfidence evidence (motivation)
- **DACA 2025:** LLM-specific calibration method (alternative approach)
- **CCPS 2025:** Perturbation-based calibration (comparison method)

### Phase 2B Readiness Seeds

**Hypothesis Dependencies:**
- H-E (Existence) → H-M1, H-M2, H-M3 (Mechanism) → H-C1, H-C2 (Condition)

**Verification Ordering:**
1. H-E: ECE comparison (quick sanity check)
2. H-M1 + H-M2: AUROC and slope analysis (core mechanism)
3. H-M3: Brier decomposition (refinement tradeoff)
4. H-C1: Domain structure regression (conditional claim)
5. H-C2: Selective prediction evaluation (practical benefit)

**Success Gates:**
- H-E + H-M1 + H-M2 passing = Publishable core finding
- H-C1 passing = Opens new research direction
- H-C2 passing = Establishes practical relevance

### Established Facts

1. Temperature scaling effectively reduces ECE in CNNs (Guo et al. 2017, 7,452 citations)
2. RLHF induces overconfidence in LLMs (Tian et al. 2023, 598 citations)
3. Post-hoc calibration methods (DACA, CCPS) achieve 15-55% ECE reduction on LLMs
4. MMLU provides domain-labeled MCQ samples suitable for stratified analysis
5. Logit margin is accessible via standard inference with HuggingFace models

---

