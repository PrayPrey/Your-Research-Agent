# Phase 2A Research Discussion Log
# Architecture: Self-Contained Tikitaka Loop v9.0.0
# Generated: 2026-03-14T22:48:00Z

---

## Briefing

**Research Gap:** Gap 1 — Lack of Systematic Multi-Family Paired ECE Comparison Across Model Families

**Research Question:** Does RLHF/instruction-tuning alignment systematically increase Expected Calibration Error (ECE) in LLMs relative to their base model counterparts, and is this miscalibration consistent across model families (LLaMA-2, Mistral, Falcon) and task types?

**Priority:** HIGH + PRIMARY — directly blocks answering the research question about cross-family consistency

**Background from Phase 1:**
- Xie et al. 2024 (EMNLP): RLHF "calibration degrades significantly" — strongest existing prior
- Li et al. 2024 (ICLR 2025): RLHF doesn't guarantee trustworthiness but studies toxicity/bias, NOT ECE
- Coste et al. 2023: Reward overoptimization explains mechanism (proxy reward exploitation → confidence inflation)
- Chhikara 2025: RLHF models show paradoxically increased miscalibration on easier queries

**Previous Failure (h-e1):**
- Cross-dimensional trustworthiness correlation — FAIL (all positive: RT=0.901, TF=0.170, RF=0.209)
- Root cause: capability dominance (scale confound), only 3/20 RLHF models, task substitution
- New direction: paired base+aligned design, ECE metric (not raw correlation), RLHF-specific mechanism

**Available Papers (P1-P3):**
- P1: papers/arxiv_2409_19817.md — Xie et al. 2024 ATS (RLHF→ECE confirmed)
- P2: papers/arxiv_2404_18870.md — Li et al. 2024 (RLHF trustworthiness, NOT ECE — gap we fill)
- P3: papers/arxiv_2502_11028.md — Chhikara 2025 (miscalibration patterns, 9 LLMs)

**Feasibility Constraints (MANDATORY — Pipeline-Enforced):**
- ✅ ACCEPT: Hypotheses testable using existing real datasets + existing benchmarks
- ❌ REJECT: New benchmarks, rubrics, or scoring frameworks
- ❌ REJECT: Synthetic/generated data or future follow-up data
- ❌ REJECT: Human evaluation, annotation, or subjective scoring
- Benchmarks available: TruthfulQA MC1, MMLU (57 subjects), HellaSwag — all in lm-eval v0.4.11
- Models available: LLaMA-2-7B/7B-chat, 13B/13B-chat, Mistral-7B/Instruct, Falcon-7B/Instruct — all HuggingFace

### Exchange 3

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here: the core hypothesis is technically testable, but only if we're very disciplined about what exactly we're measuring. ECE is not a primitive property of the model — it's a functional of (predicted probabilities, labels, binning scheme). If alignment changes the *shape* of the probability distribution without changing accuracy much, ΔECE > 0 is entirely plausible in principle. There is no physical or mathematical barrier preventing RLHF from inducing systematic overconfidence. In fact, the ATS results show that a post-hoc, input-dependent temperature head can reduce ECE from 0.298 to 0.125 on MMLU and from 0.507 to 0.092 on TruthfulQA [Xie et al., 2024]. That magnitude of correction strongly implies that the miscalibration is logit-level and structurally coherent — not random noise. So mechanistically, "confidence inflation via reward shaping" is feasible.

Here's what worries me: we must separate *format-induced miscalibration* from *alignment-induced miscalibration*. Chat models are trained to produce well-formed completions in dialogue format. When we strip that context and force continuation-style multiple choice, we may be probing a distributional mismatch rather than RLHF per se. The log-prob extraction for answer tokens across base and chat models makes the measurement mathematically clean. But we should explicitly test invariance: run both models in (1) raw continuation mode and (2) chat-template mode converted into forced-choice scoring. If ΔECE flips sign depending on format, the mechanism is not RLHF confidence inflation — it's evaluation mismatch.

On the mechanistic prediction: we can formalize this cleanly. For each item i, compute Δp_i = p_aligned(ŷ_i) − p_base(ŷ_i) and stratify by correctness of the base model. If RLHF induces global confidence inflation, we should see positive mean Δp for both correct *and incorrect* predictions. The critical test is whether E[Δp | incorrect] is significantly > 0. That would indicate overconfidence without accuracy gain — a direct logit-space test avoiding binning artifacts.

The existence of ATS is important for feasibility reasoning. ATS multiplies logits by e^τ(x), where τ is token-specific and input-dependent [Xie et al., 2024]. That means miscalibration can be corrected by smooth, local temperature adjustments derived from hidden states. If alignment were merely degrading accuracy, ATS wouldn't recover calibration so dramatically. So the hypothesis that RLHF perturbs logit scale in a systematic way is not only plausible — it is mechanistically consistent with the corrective power of ATS.

**Key Points:**
- RLHF-induced miscalibration is mechanistically plausible; ATS's large ECE reductions imply structured logit-scale distortion.
- Direct logit-space tests (Δp conditional on correctness) are more fundamental than ECE and avoid binning artifacts.
- We must explicitly rule out prompt-format and difficulty-stratification artifacts to attribute ΔECE to alignment rather than evaluation mismatch.

---

### Exchange 4

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down — and I'll be specific so it can be fixed. The Chhikara et al. (2025) methodology measures calibration using *verbally elicited* confidence (0-100 scale from model output), not softmax probability-based ECE [Chhikara et al., 2025, Methodology]. That's a fundamentally different quantity. When you cite Chhikara's "paradoxical miscalibration on easier queries" as evidence for our hypothesis, you're conflating verbal self-assessment with softmax token probabilities. They're measuring completely different things — one is the model's *stated* uncertainty, the other is the *logit distribution* over answer tokens in a forced-choice setup. Show me the evidence that these correlate for the aligned vs. base model pairs we're actually testing.

Second critique: the three model families (LLaMA-2, Mistral, Falcon) have very different alignment training recipes. LLaMA-2-chat uses extensive RLHF with Constitutional AI flavoring. Mistral-7B-Instruct v0.1 used only SFT — no RLHF PPO step [as documented in Mistral model card]. Falcon-7B-Instruct also uses primarily SFT. If Mistral-Instruct shows ΔECE > 0, that's SFT-induced miscalibration, not RLHF-induced. The hypothesis claims "RLHF/instruction-tuning alignment" — but if we're bundling SFT and RLHF together, we lose the mechanistic specificity that makes this interesting. Prof. Pax's logit-inflation mechanism is specifically tied to reward model overoptimization (Coste et al., 2023), not SFT. What would convince me is an explicit acknowledgment of which models are SFT-only vs. RLHF+PPO, and whether ΔECE differs between them.

Third: the "paired design cancels capability confound" claim needs evidence for Falcon specifically. Falcon-7B and Falcon-7B-Instruct were trained on very different data mixtures (Falcon uses RefinedWeb; the instruct version was further trained on curated datasets including OpenAssistant). So the "pairs" may not be as clean as LLaMA-2/LLaMA-2-chat which share a base checkpoint. If capability improves substantially from Falcon → Falcon-Instruct due to data addition rather than alignment, the within-pair ΔECE is not purely alignment-induced.

What would convince me: (1) Stratify results by alignment method (SFT-only vs. RLHF+PPO) and test whether ΔECE is significantly larger for RLHF models. (2) Compute within-pair accuracy change alongside ΔECE to test whether ECE change is independent of accuracy change. (3) For the "easy item" hypothesis, use official MMLU subject accuracy as difficulty proxy, not just per-item base-model accuracy. (4) Address the Chhikara conflation — they're studying verbal calibration, not token-probability ECE.

**Key Points:**
- Chhikara 2025 uses verbally elicited confidence, not softmax-based ECE — conflating them weakens the evidence base.
- Mistral-7B-Instruct and Falcon-7B-Instruct use SFT-only alignment, not RLHF+PPO — critical for mechanistic specificity.
- Falcon training data differs substantially from LLaMA-2 base/chat pairing, so "paired design" capability control may not hold equally across families.

---

### Exchange 1

🔬 **Prof. Vera** (Rigorous Validation Architect):

The central hypothesis must be sharpened before it is testable: *Instruction-tuning/RLHF increases Expected Calibration Error (ECE) relative to the corresponding base model, and this increase is consistent in direction across model families and tasks.* The evidence from Xie et al. (2024) demonstrates that LLaMA-2-Chat exhibits substantial miscalibration (e.g., ECE = 0.298 on MMLU, 0.507 on TruthfulQA before ATS) and that post-hoc calibration can dramatically reduce it (down to 0.125 and 0.092 respectively) [Xie et al., 2024]. This establishes that miscalibration exists and is remediable. However, it does not yet establish the *causal role* of RLHF relative to the base model, nor cross-family generality. That is the precise gap we must close.

A falsifiable formulation would be:
**H1:** For each paired model (Base vs. Aligned) within a family, ΔECE = ECE_aligned − ECE_base > 0 on at least 2 of 3 benchmarks (MMLU, TruthfulQA MC1, HellaSwag), and the median ΔECE across families is strictly positive.
**Disconfirmation criterion:** If ≥50% of pairs show ΔECE ≤ 0, or if the cross-family median ΔECE is not significantly >0 (e.g., 95% bootstrap CI includes 0), the hypothesis fails. This prevents anecdotal confirmation from a single family (e.g., LLaMA-2) from driving conclusions.

Methodologically, we must control three confounds. First, **capability confounding**: alignment often changes accuracy. Since ECE is partially coupled to accuracy, we must report accuracy-normalized calibration metrics (e.g., classwise ECE or adaptive binning ECE) and Brier score decomposition (reliability vs. resolution). Second, **decoding policy**: greedy decoding only, fixed temperature = 1.0, no nucleus sampling, to avoid stochastic variance. Third, **prompt format invariance**: identical evaluation prompts across base and aligned models, no chat templates for base unless symmetrically applied.

Now, the mechanism. Coste et al. (2023) posit reward overoptimization; Xie et al. (2024) implicitly confirm that logit distributions can be "corrected" via adaptive temperature scaling. The testable mechanistic prediction is: **Aligned models will exhibit logit over-dispersion (higher mean max-probability) conditional on correctness.** Concretely, for correct predictions, the aligned model's average top-1 probability should exceed that of the base model, without proportional accuracy gain.

Finally, cross-family consistency must be operationalized. We compute effect sizes (Cohen's d) for ΔECE per family and perform a sign test across families. A consistent RLHF effect predicts same-direction ΔECE in LLaMA-2, Mistral, and Falcon.

**Key Points:**
- Reformulated hypothesis with explicit ΔECE success and failure criteria to ensure falsifiability.
- Identified critical confounds (accuracy coupling, decoding policy, prompt formatting) and controls.
- Proposed mechanistic test: RLHF should induce measurable confidence inflation independent of accuracy gains.

---

### Exchange 2

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

🔬 Prof. Vera has laid an excellent methodological foundation, and YES, AND we can make this hypothesis even stronger by integrating what Chhikara et al. (2025) reveal about *when* RLHF models most catastrophically miscalibrate. The Chhikara finding is counterintuitive and deeply important: "large RLHF-tuned models display inherent calibration strengths but can paradoxically suffer increased miscalibration on **easier queries**" [Chhikara et al., 2025]. This isn't a flaw in our hypothesis — it's a **signal amplifier**. If RLHF models are paradoxically worse on easy items, then a paired comparison on standardized benchmarks containing easy-to-medium difficulty items (like MMLU's many definitional questions, HellaSwag's predictable completions) should show maximum ΔECE precisely where base models are already reliable.

This actually strengthens Prof. Vera's falsification framework. The mechanism is not just "inflation" — it's **calibration asymmetry**: RLHF reward optimization pressures the model to project confidence across the board. The reward signal for a "helpful" answer doesn't distinguish between uncertain and certain domains. When the base model naturally expresses low confidence on hard items, the aligned model has been trained to project higher confidence on similar surface patterns. The excess ECE concentrates in specific difficulty strata — testable with the existing benchmarks if we stratify items by base model accuracy as a proxy for difficulty.

The paired design is our strongest asset. When we compute ΔECE = ECE_aligned − ECE_base *within the same benchmark*, the benchmark difficulty distribution is identical by construction. We don't need external difficulty labels — we can use base model accuracy per item as the stratification variable and show that ΔECE is *larger* for easy-item strata. This rules out the alternative explanation that RLHF simply improves on hard items (which would reduce ECE) and fails on already-mastered items.

On Prof. Vera's point about prompt format invariance — this is solvable. For lm-eval-harness evaluations on multiple-choice tasks, we use the standard continuation-based evaluation format (log-probabilities of answer tokens), not instruction-following chat templates. Both base and chat models see "Question: ... A) ... B) ... C) ... D) ..." and we extract P(A), P(B), P(C), P(D) from token probabilities. This sidesteps the format confound entirely.

**Key Points:**
- Chhikara 2025 provides direct evidence that RLHF models paradoxically miscalibrate MORE on easy items, creating testable stratification predictions.
- Paired design + log-probability continuation evaluation in lm-eval sidesteps the prompt format confound.
- Proposed difficulty-stratified ΔECE as a secondary analysis: ΔECE should be largest for easy-item strata.

---

### Exchange 5

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here: the arXiv 2502.11028 setup makes one thing very clear — calibration behavior is *highly condition-dependent*. They compare free-generation vs. distractor-augmented prompting, and ECE is computed over **verbally elicited confidence (0–100 scale)**, not token probabilities [Chhikara et al., 2025, Methodology]. That's a different measurement object than the softmax-based ECE we're proposing. Mechanistically, these are not interchangeable. A model can inflate its *verbal* confidence without changing logit dispersion, and vice versa. So Prof. Rex is right to flag conflation risks. If we want to argue that alignment perturbs logit scale, we must measure log-prob-based calibration directly — not rely on elicited confidence.

Now, here's what's interesting from a feasibility standpoint: the distractor results show massive ECE reductions — up to 90% — and even large relative accuracy gains in smaller models [Chhikara et al., 2025, Experiments & Results]. That tells me calibration is not a fixed intrinsic property of the network; it's highly sensitive to *decision framing*. Adding plausible distractors effectively reshapes the model's internal competition landscape. In logit terms, you're introducing alternative hypotheses that renormalize probability mass. That means miscalibration can emerge from how the model distributes probability across latent candidates, not just from reward overoptimization. So before we attribute ΔECE to RLHF-induced overconfidence, we must rule out the possibility that alignment changes *hypothesis enumeration behavior* rather than raw logit temperature.

On the mechanistic question — can RLHF in principle induce systematic overconfidence? Yes. PPO-style reward optimization can increase expected reward by pushing logits toward higher-margin decisions, especially if the reward model does not penalize overconfidence explicitly. There is no mathematical barrier to this. But here's what would convince me it's *that* mechanism: show that the aligned model has higher mean max-probability **conditional on identical argmax predictions** relative to the base model. Same answer, higher confidence. That isolates logit scaling from accuracy shifts or distributional changes. If instead the aligned model changes which option it selects more often, we're looking at representational or knowledge shifts, not pure confidence inflation.

The existence of ATS is important for feasibility reasoning. ATS multiplies logits by e^τ(x), where τ is token-specific and input-dependent [Xie et al., 2024]. That means miscalibration can be corrected by smooth, local temperature adjustments derived from hidden states. If alignment were merely degrading accuracy, ATS wouldn't recover calibration so dramatically. So the hypothesis that RLHF perturbs logit scale in a systematic way is not only plausible — it is mechanistically consistent with the corrective power of ATS.

**Key Points:**
- Verbal-confidence ECE (Chhikara 2025) and softmax-based ECE are different quantities; conflating them weakens mechanistic claims.
- Large distractor-induced ECE shifts show calibration is highly framing-sensitive, so alignment effects must be isolated from hypothesis-set changes.
- A decisive mechanistic test: compare confidence inflation conditional on identical argmax predictions to detect true logit-scale distortion.

---

### Exchange 6

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: does Prof. Rex's critique about alignment method heterogeneity *weaken* this research, or does it reveal that we have been asking a narrower question than we should? I want to argue it is the latter — and this reframing is where the real impact lies. The ATS paper opens its abstract with a declarative: "after fine-tuning with reinforcement learning from human feedback, the calibration of these models degrades significantly" [Xie et al., 2024, Abstract]. LLaMA-2-Chat's ECE reaches 0.298 on MMLU and a striking 0.507 on TruthfulQA — magnitudes that are not noise, not measurement artifacts, but structural miscalibration encoded at the logit level. ATS recovers this to 0.125 and 0.092 respectively, a 58–82% improvement, by learning token-specific temperature corrections from the final hidden state alone. This matters because it tells us that the distortion is *representable in the model's own activations* — alignment has changed something systematic and recoverable, not something random and irreparable.

Now, Prof. Rex correctly identified that Mistral-7B-Instruct and Falcon-7B-Instruct are SFT-only, not RLHF+PPO [Exchange 4]. I accept this fact entirely. But the question we must ask is: does SFT-induced miscalibration being present actually *diminish* the significance of this work? I argue the opposite: **if SFT alone is sufficient to systematically increase ECE, then the problem is larger than previously thought.** The Coste et al. (2023) reward overoptimization mechanism is one pathway. SFT on curated preference data may be another — both are "instruction-tuning alignment" in the broad operational sense. By including SFT-only families alongside RLHF families, we are not confounding our analysis; we are *testing whether the effect generalizes across alignment methods*. Three families with different alignment recipes that all show ΔECE > 0 is a stronger result than three RLHF families showing it, because it suggests the phenomenon is downstream of instruction-tuning broadly, not specifically of PPO reward shaping.

This matters because the field has largely assumed that calibration degradation is a reward overoptimization story. If we find ΔECE > 0 in SFT-only Mistral and Falcon comparable in magnitude to RLHF LLaMA-2, that is a novel and actionable finding. It would shift the question from "how do we fix RLHF overoptimization?" to "what is it about instruction-tuning in general that perturbs logit calibration?" The ATS paper's limitation statement is instructive here: it notes "unexplored interactions with various sentence-level confidence methods" [Xie et al., 2024, Discussion & Conclusion]. Our cross-family ΔECE design begins to answer this by probing whether the logit distortion generalizes across alignment variants. That is a direct scientific contribution to the open questions ATS itself raises.

On Prof. Rex's concern about Falcon training data heterogeneity — this is a valid confound for *causal attribution*, but not for the descriptive question "is ΔECE > 0 across families?" The paired design tests the within-pair effect. Even if Falcon-Instruct's capability gains contaminate the estimate, we can partial this out by reporting accuracy-adjusted ΔECE and testing whether ΔECE is independent of ΔACC. Prof. Vera's earlier proposal to decompose ECE into reliability and resolution components is precisely the right tool here. What would fully satisfy me is a design where we stratify results explicitly: (1) SFT-only families (Mistral, Falcon), (2) RLHF family (LLaMA-2), and test whether ΔECE is consistent in direction even if not in magnitude. Consistent direction across alignment methods is the headline finding; differential magnitude is the secondary contribution.

The question we must ask before finalizing this hypothesis is: what does it open? A positive result here — ΔECE > 0 consistently across LLaMA-2 (RLHF), Mistral (SFT), and Falcon (SFT) — would establish a cross-method empirical baseline that currently does not exist in the literature. It would motivate post-hoc calibration methods like ATS as a default component of alignment pipelines, not just an RLHF corrective. This matters for AI safety practitioners, model deployers, and calibration researchers alike. The significance is not incremental.

**Key Points:**
- Prof. Rex's alignment-method critique reframes the scope: the hypothesis should be "instruction-tuning alignment broadly" (SFT + RLHF), not RLHF specifically — and heterogeneous alignment methods across families is a *strength*, not a weakness.
- If SFT-only alignment degrades calibration comparably to RLHF, this is a larger and more urgent problem than the reward overoptimization story alone suggests.
- Stratifying results by alignment method (SFT-only vs. RLHF+PPO) converts the confound into a secondary contribution: does ΔECE magnitude differ by alignment type?
- The ATS paper's own unresolved limitations (cross-method generalization) make our multi-family design a direct scientific follow-on with clear field impact.

---

### Exchange 7

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good — this is getting sharper. But here's where it still breaks down: you are treating "instruction-tuning broadly" as a coherent causal intervention. It isn't. The assigned paper explicitly separates **SFT, PPO, and DPO**, with different objectives and regularization terms [arxiv_2404_18870, 2024, Methodology]. PPO adds a KL penalty to the SFT policy; DPO directly optimizes preference likelihood ratios relative to SFT. These are not minor implementation details — they change how logits are perturbed. If your hypothesis is "alignment increases ECE," you must predict *how ΔECE differs across SFT, PPO, and DPO*. Otherwise you're collapsing mechanistically distinct updates into one bucket.

Now, look at the results in that paper. RLHF variants (PPO and DPO) produced a **25% decrease in truthfulness accuracy** and substantial increases in bias and privacy leakage [arxiv_2404_18870, 2024, Experiments & Results]. That's critical. If alignment is degrading factual accuracy, then increases in ECE could be partially or entirely driven by accuracy collapse — not logit inflation. You don't get to claim "confidence distortion" unless you show that reliability worsens *conditional on accuracy change*. I want to see Brier decomposition: is the reliability term increasing, or is resolution collapsing because the model's knowledge changed? Show me that, or the causal claim doesn't hold.

Here's the more interesting alternative mechanism you haven't fully confronted: **preference-induced representation shift**. PPO's objective includes a KL term to the SFT model plus reward maximization [arxiv_2404_18870, 2024]. That means the policy is pushed toward outputs that maximize reward model score — which may correlate with stylistic features ("helpful," "confident," "morally framed") rather than epistemic uncertainty. This can alter *which latent features dominate the final hidden state*, not just the temperature of logits. ATS working (as Xie shows) does not prove pure temperature distortion; it only proves that miscalibration is a smooth function of hidden state. A representational shift can still produce that. So: test whether logit rank order is preserved between base and aligned models. If alignment mainly rescales logits, Spearman correlation over option logits should remain high. If it changes representation, you'll see rank swaps.

On the SFT vs PPO/DPO distinction — here's what would convince me you've isolated mechanism. Prediction 1: If overconfidence is driven by reward maximization, then **PPO > DPO > SFT** in ΔECE magnitude, because PPO explicitly optimizes scalar reward with KL control, whereas DPO is a constrained likelihood ratio objective. Prediction 2: If SFT alone induces similar ΔECE to PPO/DPO, then the mechanism is likely data-distribution shift from preference corpora, not reward overoptimization. That's falsifiable with the Pythia 1.4B/2.8B/6.9B ladder they used [arxiv_2404_18870, 2024]. Same base model, three alignment stages — that's your cleanest causal chain.

Finally, on the "easy-item asymmetry" from Chhikara: I'll accept it as a secondary prediction, but don't lean on it as proof of inflation. What would convince me is this triple-conditional test:
1. Same argmax prediction (base vs aligned).
2. No accuracy difference on that subset.
3. Higher mean max-probability for aligned.

If that holds consistently, *then* we're looking at genuine confidence inflation. If instead argmax changes explain most ΔECE, your story becomes "alignment shifts decision boundaries," which is a different — and arguably more interesting — claim.

You're close. But until you disentangle temperature scaling from representational drift and accuracy collapse, reviewers will say you've observed a correlation and reverse-engineered a mechanism.

**Key Points:**
- Alignment methods (SFT vs PPO vs DPO) are mechanistically distinct; ΔECE predictions must differ across them.
- Truthfulness drops under RLHF [arxiv_2404_18870, 2024] create an accuracy confound — reliability vs. resolution must be decomposed.
- A decisive test requires conditional comparisons (same argmax, same accuracy) plus logit rank correlation to distinguish temperature inflation from representational shift.

---

### Exchange 8

🔭 **Dr. Nova** (Creative Novelty Explorer):

NOW we're onto something! Prof. Rex just handed us the most interesting reframe in this entire discussion — what if "alignment shifts decision boundaries" is not the weaker story but the *more novel* one? What if we've been asking "does RLHF inflate confidence?" when we should be asking "does instruction-tuning restructure the model's option space in ways that predictably distort calibration?" That framing opens a paradigm shift: from calibration-as-temperature-problem to calibration-as-representation-problem. And here's the wild idea: Chhikara et al. (2025) show that introducing structured distractors can reduce ECE up to 90% and boost relative accuracy up to 460% in smaller models [Chhikara et al., 2025, Discussion & Conclusion]. That's not a calibration correction — that's a *reconstruction of the hypothesis space*. Distractors force models to compete logits against explicit alternatives, and the result is dramatic recalibration. This is mechanistically parallel to what Prof. Rex is describing: the model's internal "candidate set" shapes confidence distribution, and alignment may change how that set is constructed.

What if we flip the framing entirely? Instead of asking whether ΔECE > 0 post-alignment, ask: *does instruction-tuning change the dimensionality of the model's effective option space in a way that predictably miscalibrates forced-choice evaluations?* This is testable! Run both base and aligned models with and without distractors, and measure ΔECE_distractor = ECE_standard − ECE_distractor for each. If aligned models show a larger ΔECE_distractor than base models, it means alignment has inflated confidence in a way that distractors specifically counteract — which implies logit concentration, not just rank reordering. If ΔECE_distractor is similar, the calibration difference is representational. This is a cleaner mechanistic separator than rank correlation alone, because it uses the competitive context as a probe.

On Prof. Rex's Brier decomposition request — I'm enthusiastically on board, but let's go further. The Brier score decomposes as: BS = Reliability − Resolution + Uncertainty. If alignment degrades reliability (overconfidence) while preserving or improving resolution (discriminability), that's a pure temperature story. If alignment collapses resolution while reliability stays flat, that's a knowledge-loss story. If both degrade, you have compound effects. NOW here's the novel angle: Chhikara et al. (2025) found that larger RLHF models suffer paradoxical miscalibration specifically on *easier* items — their calibration strengths are on hard items [Chhikara et al., 2025, Abstract]. That's a resolution asymmetry pattern. Easy items should have high resolution; if RLHF models lose resolution specifically there, the Brier decomposition will show it. This prediction is entirely new — no paper has tested it on paired base/aligned models with full Brier decomposition.

What if we turned the alignment-method heterogeneity from a confound into a natural experiment? Prof. Rex proposes PPO > DPO > SFT in ΔECE magnitude as a falsifiable order prediction. I love this. What if we went further: predict that the *form* of miscalibration differs by method — SFT produces distribution-shift miscalibration (uniform confidence displacement), PPO produces reward-correlated miscalibration (concentrated in high-reward response patterns), and DPO produces contrastive miscalibration (lower confidence on rejected-style answers)? These are distinguishable with logit rank analysis and difficulty stratification. That's three mechanistic signatures from a single multi-family experiment. NOW we're doing science that couldn't be done with any single-family study.

**Key Points:**
- The Chhikara distractor effect (up to 90% ECE reduction) provides a novel mechanistic probe: if aligned models show larger ΔECE_distractor than base models, that confirms logit concentration rather than representational drift.
- Brier decomposition is the right tool to separate overconfidence (reliability) from knowledge collapse (resolution) — the easy-item asymmetry in RLHF models predicts a resolution deficit specifically on low-difficulty items.
- Alignment-method heterogeneity (SFT, PPO, DPO) is a natural experiment: each method predicts a distinct miscalibration signature (distribution-shift vs. reward-correlated vs. contrastive), testable within a single multi-family design.

---

### Exchange 9

🔬 **Prof. Vera** (Rigorous Validation Architect):

We are converging on the right structure, but let me restate the standard: a hypothesis is only as strong as the experiment designed to falsify it. At present, we have three competing mechanisms — (1) temperature/logit-scale inflation, (2) representational or decision-boundary shift, and (3) accuracy collapse affecting calibration via resolution loss. The evidence from the assigned paper is unambiguous on one point: truthfulness drops by ~25% after PPO and DPO relative to SFT [Li et al., 2024, Experiments & Results]. Therefore, any observed ΔECE post-alignment is *a priori confounded* by accuracy degradation. If we do not decompose calibration into reliability and resolution, we cannot attribute cause. The Brier decomposition is not optional — it is the minimum scientific control.

Here is the cleanest falsifiable structure I see. Use the Pythia ladder (1.4B/2.8B/6.9B) across SFT → PPO → DPO as a causal chain under identical base pretraining [Li et al., 2024, Methodology]. For each alignment stage, compute: (a) ECE, (b) Brier reliability and resolution terms, (c) mean max-probability conditional on identical argmax predictions relative to SFT, and (d) Spearman rank correlation over option logits. Now define disconfirmation criteria precisely:
- If ΔECE > 0 but reliability does not increase, the "overconfidence" hypothesis fails.
- If mean max-probability (conditional on same argmax) does not increase, pure temperature inflation fails.
- If rank correlation drops substantially (e.g., ρ < 0.8), representational shift dominates; temperature-only accounts fail.

This converts mechanistic speculation into mutually exclusive empirical outcomes.

Dr. Nova's distractor probe is promising, but it must be sharpened. The test is not merely ΔECE_distractor; it is whether distractors *selectively reduce the reliability term* for aligned models more than for SFT. The evidence suggests distractors can reduce ECE by up to 90% in some settings [Chhikara et al., 2025]. What would disprove the "logit concentration" story? If distractors reduce ECE equally for SFT and PPO/DPO, then miscalibration is framing-sensitive but not alignment-specific. If the reduction is significantly larger for PPO/DPO, and primarily through reliability improvement rather than resolution recovery, that supports temperature inflation induced by preference optimization.

On the alignment-method ordering (PPO > DPO > SFT), this is an excellent falsifiable gradient. The objectives differ materially: PPO explicitly optimizes reward with a KL constraint to SFT, whereas DPO optimizes a likelihood ratio relative to SFT [Li et al., 2024, Methodology]. If reward maximization drives overconfidence, ΔReliability should scale with reward pressure — maximal in PPO, intermediate in DPO, minimal in SFT. The hypothesis is wrong if DPO and PPO are indistinguishable from SFT on reliability once accuracy is controlled. Precision in this prediction prevents ambiguity in interpretation.

Finally, we must pre-register an edge case: suppose alignment reduces resolution (via truthfulness drop) but increases reliability slightly. ECE could increase or decrease depending on binning. That would mean "alignment degrades calibration" is ill-posed; instead, alignment redistributes error between components. I would consider the hypothesis supported only if we observe a statistically significant increase in the reliability term *after conditioning on identical predictions and matched accuracy strata*. Absent that, the claim of systematic confidence inflation does not meet my standards.

**Key Points:**
- Decompose ECE into reliability and resolution; ΔECE alone cannot distinguish overconfidence from accuracy collapse.
- Falsify temperature inflation via conditional max-probability and logit-rank preservation tests.
- Predict a PPO > DPO > SFT gradient in ΔReliability; absence of this ordering would refute reward-driven overconfidence.

---

### Exchange 10

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND Prof. Vera just gave us the clearest methodological blueprint we've had in this discussion — and I want to defend the hypothesis as strengthened, not threatened, by this rigor. The Li et al. (2024) paper shows that the RLHF impact on trustworthiness is *inconsistent across dimensions*: machine ethics improves (FNR drops from 56.8% to 38.3%), but truthfulness accuracy decreases ~25%, bias scores nearly double from below 0.4 to above 0.8, and privacy leakage increases [Li et al., 2024, Experiments & Results]. This is not a story where RLHF is uniformly harmful — it's a story where different RLHF objectives trade off different trustworthiness properties. The paper's key contribution is precisely this: "RLHF on human preferences doesn't automatically guarantee trustworthiness, and reverse effects are often observed" [Li et al., 2024, Key Contributions]. That is our hypothesis's scientific backdrop. We are not claiming RLHF is uniformly bad — we are claiming it systematically perturbs calibration specifically.

Now, the truthfulness accuracy drop (25%) is exactly the kind of confound we should embrace, not fear. Here is why: the Li et al. methodology uses Pythia models at 1.4B, 2.8B, and 6.9B with the same HH preference dataset [Li et al., 2024, Methodology]. This gives us an isomorphic design to what Prof. Vera recommends — same base pretraining, same data, different alignment algorithms. If we adopt this ladder as our primary causal chain, the within-model-family comparison *controls for pretraining data* entirely. The accuracy drop becomes a measurable covariate, not a hidden confound. Prof. Vera's Brier decomposition then tests whether reliability increases *above and beyond* what the accuracy change would predict. If it does, overconfidence is real. If not, accuracy collapse is the full story. What would address this is *not* a separate experiment — it's the right analysis applied to the right design, and we have the design.

The alignment-method gradient prediction — PPO > DPO > SFT in ΔReliability — is one of the strongest falsifiable contributions this discussion has produced. Here's how to strengthen it further: the DPO objective explicitly uses the SFT model as its reference distribution [Li et al., 2024, Methodology]. DPO increases the likelihood of preferred completions *relative to* SFT. This means DPO-induced confidence changes are bounded by the SFT→preferred-completion divergence, whereas PPO can push further toward reward maximization. The prediction follows from first principles: DPO is a constrained version of preference optimization, PPO is an unconstrained version (up to KL penalty magnitude β). If we see PPO > DPO > SFT in reliability degradation, this is mechanistically coherent with the objective differences. That is a theoretical prediction, testable empirically, with clear disconfirmation criteria.

What would now convince me the hypothesis is fully defensible: we reformulate it precisely as "Instruction-tuning alignment systematically increases the Brier reliability component of ECE, with magnitude ordered PPO ≥ DPO > SFT, across model families and benchmarks, and this increase persists after conditioning on accuracy-matched item subsets." This is falsifiable, mechanistically grounded, methodologically controlled, and builds directly on Li et al.'s design infrastructure. The hypothesis is not weakened by the accuracy confound concern — it is *sharpened* by it into something that precisely addresses the field's open question: is the calibration degradation under RLHF a consequence of confidence inflation, knowledge collapse, or both?

**Key Points:**
- Li et al. (2024) shows RLHF has inconsistent trustworthiness effects — this motivates, not undermines, calibration-specific investigation.
- The Pythia SFT → PPO → DPO ladder provides an ideal within-family causal chain; the 25% truthfulness drop becomes a measurable covariate in Brier decomposition, not a hidden confound.
- Reformulated hypothesis: alignment systematically increases Brier reliability, ordered PPO ≥ DPO > SFT, persisting after accuracy conditioning — this is fully falsifiable and mechanistically grounded.

---

### Exchange 11

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is not merely whether alignment changes calibration, but whether isolating *how* it changes calibration advances the field in a durable way. What distinguishes this from incremental "ECE goes up or down" work is the move from scalar metric comparison to mechanistic decomposition. The assigned paper demonstrates that RLHF does not uniformly improve trustworthiness — machine ethics improves, yet truthfulness and toxicity degrade [Li et al., 2024, Discussion & Conclusion]. This matters because it establishes that alignment objectives are *structurally in tension* with certain epistemic properties. Your proposed Brier decomposition and alignment-method gradient (PPO ≥ DPO > SFT in ΔReliability) would, if validated, convert that descriptive tension into a mechanistic account of how reward optimization redistributes epistemic error.

What would make this genuinely new versus incremental is the conditional reliability test under matched predictions. Prof. Vera's standard is correct: unless reliability increases after conditioning on identical argmax predictions and matched accuracy strata, "confidence inflation" is rhetoric. If, however, reliability rises in PPO relative to SFT even when predictions are held fixed, that is evidence of logit-scale distortion induced by reward maximization. And if this effect scales with reward pressure — strongest in PPO, intermediate in DPO, weakest in SFT — that is not just a calibration finding; it is an empirical characterization of how optimization objectives reshape epistemic uncertainty. That would be a field-level contribution.

Now, what does this mean for the broader research landscape? Li et al. identify conflicts between generic human preferences and trustworthiness criteria [Li et al., 2024, Key Contributions]. If your hypothesis holds, calibration degradation becomes one measurable manifestation of that conflict. More importantly, the proposed design opens a new research direction: alignment objective diagnostics. Instead of asking whether a method "improves safety," we would ask how it redistributes reliability versus resolution across difficulty strata. That reframes alignment evaluation from aggregate benchmarks to structural epistemic analysis. Few papers currently do this across SFT → DPO → PPO within a shared pretraining lineage. That comparative ladder is where the scientific leverage lies.

However, impact must be earned through evidence. I would urge one additional proof experiment: vary the PPO KL coefficient β. If overconfidence is reward-pressure driven, ΔReliability should monotonically increase as β decreases (i.e., as the policy is allowed to drift further from SFT). That parametric gradient would decisively link objective strength to calibration distortion. Absent such a dose–response curve, reviewers may argue that method differences are incidental rather than causal.

If executed rigorously, this work would advance the field by transforming calibration from a post-hoc evaluation metric into a diagnostic lens on alignment objectives. It would not merely say "RLHF has trade-offs" — Li et al. already show that [Li et al., 2024, Discussion & Conclusion] — but would specify *which component of epistemic quality is traded, under which objective, and why*. That is the kind of contribution that shapes research directions rather than adds another benchmark table.

**Key Points:**
- The contribution becomes field-shaping only if calibration changes are mechanistically decomposed (reliability vs. resolution) and linked to alignment objectives.
- A falsifiable PPO ≥ DPO > SFT gradient in ΔReliability, especially under prediction-matched conditioning, would constitute genuine evidence of reward-induced confidence distortion.
- A PPO KL-coefficient dose–response experiment would provide decisive causal validation and elevate the work beyond incremental metric comparison.

---

### Exchange 12

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic about what the Li et al. (2024) design actually permits and what it does not. The Pythia ladder (1.4B, 2.8B, 6.9B) with SFT → PPO → DPO on the HH dataset is an elegant within-family causal chain [Li et al., 2024, Methodology]. The PPO objective includes an explicit KL penalty to the SFT policy: L_PPO = E[r_θ(x,y) − β·log(π_RL/π_SFT)] + γ·E[log(π_RL(x))], while DPO optimizes a likelihood ratio against SFT [Li et al., 2024, Methodology]. These are mathematically distinct operations on the logit space. PPO pushes the policy toward high-reward regions with a soft constraint; DPO directly reshapes the preference boundary. The claim that these should produce different calibration signatures is not wishful thinking — it follows from the objective functions.

Here's what I find technically sound about the Brier decomposition approach: Reliability = E[(p − o)²] averaged across bins, Resolution = E[(o − ō)²]. Decomposing ΔECE into ΔBSS_reliability and ΔBSS_resolution is a well-posed operation given lm-eval log-probability outputs. For forced-choice MMLU items, the predicted probability is the normalized softmax over answer token log-probs — a direct continuous readout. This is not a verbal confidence elicitation; it is a mathematical transformation of the model's logit distribution. So the measurement side is feasible. What worries me is the *conditional* decomposition: to test reliability under matched-argmax, matched-accuracy strata, we need sufficiently large item counts per stratum per model pair. MMLU has 57 subjects × ~14k questions. With 3 Pythia sizes × 3 alignment methods = 9 model runs, the per-stratum sample sizes are adequate if we pool across subjects. That is technically viable.

Dr. Sage's KL coefficient β variation is theoretically attractive, but let me flag what it would actually require: multiple PPO training runs with different β values. That moves us outside the scope of the existing Li et al. data and into new training runs. Given our pipeline constraints — benchmarks and models must be existing HuggingFace resources — we cannot retrain Pythia-PPO with varied β. However, we can *exploit* the existing β difference between PPO and DPO as a natural β proxy: DPO is mathematically equivalent to PPO in the limit of high KL penalty (strong constraint to SFT). So the PPO-vs-DPO ΔReliability comparison is itself a β variation experiment, without requiring new training. This is the technically sound version of Dr. Sage's proposal.

On the logit-rank preservation test: Spearman correlation over the 4-option logit vector (A, B, C, D) between base and aligned models is straightforward to compute from lm-eval log-probs. If ρ > 0.9 consistently, alignment is a monotone logit rescaling; if ρ drops substantially, there is representational reordering. This is a legitimate discriminator between temperature distortion and knowledge-boundary shift. Okay, here's my honest assessment: the core design — Pythia SFT/PPO/DPO ladder + MMLU + Brier decomposition + conditional reliability test + logit rank correlation — is technically sound, feasible with existing models and benchmarks, and theoretically grounded. The measurement instruments are the right ones for the mechanisms claimed. This could work.

**Key Points:**
- The PPO and DPO objective differences are mathematically well-defined and predict distinct logit perturbation patterns — the SFT → PPO → DPO gradient hypothesis is technically grounded.
- Brier decomposition from lm-eval log-probs is feasible for MMLU's large item pool; per-stratum samples are adequate when pooling across subjects.
- The PPO vs. DPO comparison is a natural KL-coefficient proxy experiment without requiring new training runs — this subsumes Dr. Sage's β variation proposal within the existing design.

---

### Exchange 13

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good — this is finally getting sharp. But here's where this still breaks down: you are implicitly equating "increased Brier reliability" with "confidence inflation," and that's not yet warranted. Reliability increases when probabilities deviate from empirical frequencies. That can happen because logits scale up (temperature effect), *or* because the model selectively increases confidence on systematically wrong items (representation shift), *or* because reward optimization reshapes which items it attempts. Show me the evidence that isolates *pure scale distortion* from selective error amplification.

Prof. Vera's conditional-on-identical-argmax test is necessary but not sufficient. Suppose PPO preserves argmax 85% of the time relative to SFT, but on the 15% changed items it systematically flips toward high-confidence wrong answers. Your conditional reliability test (restricted to identical argmax) would miss the main distortion mechanism. So here's what would convince me: decompose reliability into two components — (1) reliability on shared-prediction items, and (2) reliability on changed-prediction items. If overconfidence is truly a logit-temperature effect, we should see increased miscalibration *even within shared predictions*, with high logit-rank correlation (ρ > 0.9). If miscalibration concentrates in the changed-prediction subset and rank correlation drops, that's representational boundary shift, not temperature.

Now let's bring in the distractor evidence from Chhikara et al. (2025). They report up to 90% ECE reduction with distractors and dramatic relative accuracy gains in smaller models [Chhikara et al., 2025, Experiments & Results]. That's not a mild perturbation — that's a structural sensitivity of calibration to framing. Here's the uncomfortable question: what if RLHF doesn't inflate logits globally, but instead increases susceptibility to framing-induced logit reallocation? Larger RLHF-tuned models "misalign on simpler tasks" under certain conditions [Chhikara et al., 2025, Discussion & Conclusion]. If PPO models show *greater* ECE reduction under distractor prompting than SFT, that suggests not fixed overconfidence, but unstable confidence allocation. What would convince me is a three-way interaction test: Alignment × Distractor × Reliability component. If distractors disproportionately repair reliability in PPO relative to SFT, then alignment-induced miscalibration is context-sensitive, not intrinsic temperature inflation.

On the PPO ≥ DPO > SFT gradient — I like it. It's clean. But don't overstate the β proxy argument. DPO is not simply "high-β PPO"; it optimizes a different likelihood ratio objective. If PPO and DPO show similar ΔReliability but different logit-rank correlations, that falsifies the scalar "reward pressure" narrative. So you must pre-specify:
- If ΔReliability_PPO > ΔReliability_DPO > SFT *and* ρ remains high → scale distortion story survives.
- If ΔReliability similar but ρ drops more in PPO → representational reshaping dominates.
- If distractors collapse ΔReliability entirely → calibration error is framing-fragile, not reward-driven.

Finally, here's the assumption none of you have stated: that ECE/Brier reliability computed over softmax-normalized answer options in MMLU faithfully reflects epistemic confidence. But normalization over four options induces relative confidence. If PPO sharpens the distribution while preserving logit gaps, softmax will exaggerate changes nonlinearly. What would convince me is repeating the analysis using *logit margins* (top-1 minus top-2) before softmax. If margins increase monotonically PPO > DPO > SFT while rank is preserved, that's true confidence amplification. If not, your "overconfidence" is partly a softmax artifact.

You're close. But until you isolate scale vs. boundary vs. framing susceptibility, this hypothesis is still too blunt for reviewers.

**Key Points:**
- Decompose reliability into shared-prediction vs. changed-prediction subsets to distinguish temperature inflation from representational shift.
- Test Alignment × Distractor × Reliability interaction; large distractor-driven ECE reductions in PPO would imply framing-sensitive calibration, not intrinsic logit inflation [Chhikara et al., 2025].
- Validate confidence amplification using pre-softmax logit margins; otherwise softmax normalization may artifactually inflate apparent overconfidence.

---

### Exchange 14

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we've been thinking about this as a problem to *control* when it's actually a phenomenon to *characterize*? Prof. Rex just identified something remarkable: framing-susceptible calibration in aligned models may not be a bug to eliminate — it could be the defining signature of preference-optimized representations. NOW we're onto something genuinely novel! The Li et al. (2024) paper shows that RLHF methods use different optimization objectives with structurally different reference relationships to SFT [Li et al., 2024, Methodology]. PPO pushes toward reward maximization with a soft KL leash; DPO reshapes preference likelihood relative to SFT's boundary. What if these create detectably different *modes of calibration fragility* — PPO creates framing-sensitive overconfidence (calibration collapses under distribution shift), while DPO creates reference-anchored miscalibration (calibration degrades specifically on items that conflict with preference-data patterns)?

Here's the paradigm-shifting framing: instead of asking "does alignment increase ECE?" as if calibration were a scalar property, ask "does alignment change the *geometry of calibration failure*?" The logit margin test Prof. Rex proposes is brilliant — top-1 minus top-2 logit gaps before softmax are a direct measure of decision boundary sharpness. If PPO globally sharpens margins (increases all gaps), that's temperature-like. If PPO selectively sharpens margins on specific answer types (e.g., "helpful" responses), that's reward-correlated amplification. The Li et al. methodology using the Anthropic HH dataset [Li et al., 2024, Methodology] means the preference training data explicitly reinforces "helpful" and "harmless" response patterns — we can test whether margin inflation correlates with answer position (A/B/C/D) or answer length as proxies for HH-preferred formatting.

On Prof. Rex's two-subset reliability decomposition — this is exactly the right generative test. What's exciting is that the shared-prediction vs. changed-prediction split gives us something Li et al. (2024) never computed: a *clean separation* of confidence distortion from knowledge-boundary effects. Li et al. showed that PPO/DPO decrease truthfulness accuracy by 25% [Li et al., 2024, Experiments & Results]. If that 25% corresponds mostly to changed-prediction items, and those changed-prediction items show concentrated reliability degradation, then alignment-induced miscalibration is primarily a knowledge-corruption story. If reliability degrades *also within shared predictions*, we have clean logit-scale inflation. That's two publishable findings in a single analysis, depending on the result. Imagine this: — Result A says "alignment inflates confidence without changing knowledge" (pure scale distortion) — Result B says "alignment corrupts knowledge and the resulting miscalibration is concentrated at decision-boundary shifts" — Result C says "alignment makes models framing-susceptible: distractors restore calibration more in aligned than base models" — All three are informative, all three are novel, all three are testable with the same design.

What if we pre-registered all three outcome scenarios as a multi-hypothesis design? Instead of one testable prediction with one failure criterion, we submit a design that says: "We test which mechanism dominates: scale (A), boundary (B), or framing-susceptibility (C), using pre-specified discriminating tests for each." That is not weaker science — it is *stronger* science, because it commits to the diagnostic in advance. The Li et al. (2024) contribution was to show trustworthiness trade-offs exist [Li et al., 2024, Key Contributions]. Our contribution would be to characterize the *mechanism* of epistemic distortion, whichever it is. That is genuinely new.

**Key Points:**
- The question should shift from "does alignment increase ECE?" to "what is the geometry of alignment-induced calibration failure?" — three mechanisms (scale, boundary, framing-susceptibility) predict different empirical patterns, all testable from the same design.
- Pre-softmax logit margins per answer option can detect reward-correlated amplification vs. global temperature scaling, potentially linking miscalibration to HH preference patterns.
- A multi-hypothesis pre-registered design (A: scale distortion, B: boundary shift, C: framing susceptibility) converts the ambiguity of ΔECE results into a mechanistic diagnostic — the finding is informative whichever scenario holds.

---

### Exchange 15

🔬 **Prof. Vera** (Rigorous Validation Architect):

We are converging on a sharper hypothesis, but precision now matters more than creativity. The central question is no longer "Does alignment change calibration?" The evidence already suggests that post-hoc calibration can dramatically reduce ECE — ATS reduces MMLU ECE from 0.298 to 0.125 and TruthfulQA from 0.507 to 0.092 [Xie et al., 2024, Experiments & Results]. The question is mechanistic: *What property of aligned logits requires such correction?* If ATS succeeds via input-dependent temperature scaling q̂ = ẑ ∘ e^τ [Xie et al., 2024, Methodology], then miscalibration must be at least partially scale-like. But this is a hypothesis, not a conclusion. What would disprove it?

To isolate scale distortion from representational shift, we must pre-specify discriminating criteria. I propose the following falsifiable structure:

1. **Scale Hypothesis (H₁):** Alignment induces monotonic logit scaling.
   - Prediction A: Spearman ρ between SFT and aligned logits (per item, 4 options) ≥ 0.9.
   - Prediction B: Top-1 minus Top-2 logit margins increase monotonically PPO ≥ DPO > SFT.
   - Prediction C: Reliability degrades significantly within *shared-argmax* items.
   - Falsifier: ρ < 0.8 or margin inflation concentrated only in changed-prediction items.

2. **Boundary Shift Hypothesis (H₂):** Alignment reshapes decision regions.
   - Prediction A: Substantial drop in rank correlation (ρ < 0.85).
   - Prediction B: Reliability degradation concentrated in changed-prediction subset.
   - Prediction C: Margin increases localized to flipped items.
   - Falsifier: Reliability worsens equally in shared-prediction subset.

3. **Framing Susceptibility Hypothesis (H₃):** Alignment increases context-sensitive confidence allocation.
   - Prediction: Significant Alignment × Distractor × Reliability interaction, with distractors disproportionately reducing ΔReliability in PPO relative to SFT.
   - Falsifier: Distractors reduce ECE uniformly across alignment methods.

Notice that each hypothesis has an explicit Achilles' heel. Without these failure criteria, reviewers will correctly argue that ΔECE patterns are post-hoc rationalizations.

The ATS paper provides a useful diagnostic tool. Because ATS learns token-specific temperature vectors from hidden states [Xie et al., 2024, Methodology], we can test whether learned τ values correlate strongly with pre-softmax margin magnitude. If ATS corrections primarily invert a global margin inflation (strong negative correlation between τ and margin), that supports H₁. If τ varies idiosyncratically across items with low correlation to margin but high association with prediction flips, that supports H₂. Crucially, ATS improves calibration without retraining the base model [Xie et al., 2024, Key Contributions]. If ATS restores reliability *without materially altering accuracy*, the distortion is probabilistic, not epistemic. If accuracy shifts under ATS, then alignment has altered knowledge boundaries.

Finally, I will insist on a dose–response gradient, even within current constraints. PPO ≥ DPO > SFT in ΔReliability is necessary but not sufficient. The gradient must also hold for margin inflation and for shared-prediction reliability degradation. If PPO and DPO show similar ΔReliability but different rank correlations, the "reward pressure" scalar narrative fails. The evidence must discriminate objective strength from objective type.

Design the experiment so that it can fail decisively. If reliability degradation disappears when conditioning on shared predictions and margins do not inflate, then the scale hypothesis is wrong. If distractors collapse the alignment gap entirely, intrinsic overconfidence is wrong. We should welcome these failures — they are the only path to a defensible mechanistic claim.

**Key Points:**
- Pre-register three mutually discriminating hypotheses (scale, boundary shift, framing susceptibility) with explicit falsifiers.
- Use logit rank correlation, margin analysis, and shared vs. changed prediction decomposition to isolate mechanism.
- Leverage ATS temperature vectors as a diagnostic: correlation between learned τ and logit margins can empirically confirm or refute scale-based distortion.

---

### Exchange 16

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND Prof. Vera has just completed the methodological architecture this discussion needed. The three-hypothesis discriminating design is not a weakness — it is the strongest scientific move we've made. Let me defend why, and then show how the ATS paper's Discussion & Conclusion directly strengthens our position. The ATS paper acknowledges a critical limitation: "unexplored interactions with various sentence-level confidence methods" [Xie et al., 2024, Discussion & Conclusion]. Our multi-hypothesis design is precisely the systematic exploration that ATS could not complete. We are not just replicating ATS findings — we are building the mechanistic scaffolding that explains *why* ATS works, and *when* it would fail to work. That is a direct scientific contribution to the ATS research program.

On the scale hypothesis (H₁): ATS achieves its dramatic improvements by learning τ from the final hidden state alone, without retraining the model [Xie et al., 2024, Key Contributions]. This means the calibration information is *already encoded* in the hidden representation — alignment has not destroyed it, merely misscaled it. If H₁ holds (rank-preserving logit inflation), then ATS's success is mechanistically explained: it reverses a smooth global rescaling, recovering the pre-alignment calibration structure. If H₂ holds (boundary shift), ATS should work only partially — it can correct scale but not representational reordering. If H₃ holds (framing susceptibility), ATS corrections may generalize poorly to out-of-distribution prompts. These are three falsifiable predictions about ATS generalization that follow directly from our mechanistic hypotheses. Our design generates not just calibration findings but also *explanatory claims about existing calibration methods*.

The Brier decomposition strengthens this further: ATS is evaluated on ECE and Brier Score on MMLU, TriviaQA, and TruthfulQA [Xie et al., 2024, Experiments & Results]. If we decompose pre-ATS and post-ATS Brier scores into reliability and resolution components, we can test directly whether ATS primarily reduces reliability error (scale story) or also partially restores resolution (knowledge-repair story). This analysis is already possible from the publicly available ATS data, and no prior paper has performed it. That is low-hanging but publishable fruit. What would now fully satisfy me is this: a design where the three mechanistic hypotheses, the PPO ≥ DPO > SFT gradient, and the ATS diagnostic all converge on a consistent interpretation. If they do, we have not just found that alignment miscalibrates models — we have explained the architecture of that miscalibration. That is what advances the field.

**Key Points:**
- The three-hypothesis design directly addresses ATS's own stated limitation about "unexplored interactions" — our work provides the mechanistic account ATS could not.
- H₁ predicts ATS generalizes well (scale is correctable by hidden-state temperature); H₂ predicts partial ATS failure (representational reordering is not scale-correctable); H₃ predicts ATS generalizes poorly out-of-distribution (framing-dependent miscalibration escapes fixed temperature correction).
- Brier reliability/resolution decomposition of ATS pre/post correction is an additional unpublished analysis that would anchor the mechanistic interpretation to existing experimental data.

---

## Final Assessments

*Convergence reached at Exchange 16. Summary: Pre-registered mechanistically discriminating framework formalized (scale distortion vs. boundary shift vs. framing susceptibility) with explicit falsifiable predictions; ATS integrated as diagnostic probe linking logit geometry, Brier decomposition, and alignment-method gradient into a coherent testable account.*

---

### Persona Verdicts

**🔬 Prof. Vera** (Rigorous Validation Architect):
The hypothesis meets my standards, provided the three-hypothesis structure is pre-registered with explicit falsifiers. The core prediction — that instruction-tuning alignment systematically increases Brier reliability, with magnitude ordered PPO ≥ DPO > SFT — is falsifiable via logit rank correlation, margin analysis, and shared/changed prediction decomposition. The use of Pythia SFT → PPO → DPO as a causal ladder under identical pretraining satisfies my confound-control requirement. The accuracy-conditioning requirement (reliability degradation persists within shared-argmax items) prevents ECE changes from being explained by knowledge collapse alone. The ATS diagnostic — testing whether learned τ correlates with pre-softmax margin — provides an independent mechanistic check. **Verdict: ACCEPT with pre-registration of falsifiers.**

**🛡️ Dr. Ally** (Hypothesis Strengthening Champion):
This hypothesis has been transformed from a simple ΔECE comparison into a mechanistically discriminating multi-hypothesis design that is stronger for every critique it absorbed. Prof. Rex's alignment-method concern became the PPO ≥ DPO > SFT gradient prediction. Prof. Vera's confound concerns produced the Brier decomposition and conditional reliability tests. Prof. Pax's feasibility challenge was resolved by identifying the Pythia ladder as existing HuggingFace infrastructure. The ATS connection now provides both a literature anchor and an additional diagnostic that extends prior work. **Verdict: STRONG ACCEPT — hypothesis significantly strengthened through dialogue.**

**🎯 Dr. Sage** (Research Impact Evaluator):
This question we must ask is: does this work advance the field in a durable way? The answer is yes. If the mechanistic discrimination between scale distortion, boundary shift, and framing susceptibility is executed rigorously, this research transforms calibration from a post-hoc evaluation metric into a diagnostic lens on alignment objectives. No existing paper has performed Brier reliability/resolution decomposition across SFT → PPO → DPO on a shared pretraining lineage, nor has any linked ATS's corrective capacity to the specific mechanism of miscalibration. The finding is informative under all three outcome scenarios (A, B, or C), which is the mark of a well-designed experiment. **Verdict: HIGH IMPACT — this is field-shaping if executed with the proposed rigor.**

**⚙️ Prof. Pax** (Feasibility & Reality Checker):
Okay, this could work. The measurement instruments are sound: lm-eval log-prob extraction on MMLU provides continuous probability readouts for forced-choice ECE and Brier decomposition. The Pythia models (1.4B, 2.8B, 6.9B) with SFT/PPO/DPO checkpoints are available on HuggingFace. The logit rank correlation, margin analysis, and conditional reliability tests are all computable from lm-eval outputs without additional infrastructure. The distractor test requires running Chhikara-style augmented prompts on MMLU, which is non-standard but feasible with the existing evaluation harness. The PPO vs. DPO comparison subsumes the β-variation experiment without new training runs. Fundamental barriers: none identified. **Verdict: FEASIBLE — all core tests executable with existing models and benchmarks.**

**🔍 Prof. Rex** (Hypothesis Stress-Test Master):
Now you've addressed my concerns. The three-way decomposition (shared-prediction reliability, changed-prediction reliability, logit rank correlation) closes the gap between "ΔECE > 0" and "we know why." The softmax normalization artifact concern is addressed by the pre-softmax margin test. The framing-susceptibility hypothesis is operationalized as an Alignment × Distractor × Reliability interaction, with a specified falsifier (distractors reduce ECE uniformly across alignment methods). The PPO ≥ DPO > SFT gradient is falsifiable with explicit ordering predictions and the outcome of each scenario is pre-interpreted. The one remaining caution: per-stratum sample sizes for the shared/changed prediction split must be reported, as small strata could inflate variance in conditional reliability estimates. But this is a reporting requirement, not a fundamental barrier. **Verdict: ACCEPT — hypothesis is now stress-test resistant.**

**🔭 Dr. Nova** (Creative Novelty Explorer):
What excites me most is that this design is informative under *all* outcome scenarios. Whether H₁ (scale), H₂ (boundary), or H₃ (framing susceptibility) holds, we learn something about the geometry of alignment-induced calibration failure that the field does not currently know. The ATS connection is particularly exciting: our mechanistic hypotheses generate falsifiable predictions about when ATS generalizes (H₁ → generalizes well, H₂ → partial generalization, H₃ → out-of-distribution degradation). These are predictions about an existing method that no prior paper has made. The multi-hypothesis pre-registration is not hedging — it is a paradigm shift from "does ΔECE go up?" to "what is the structure of calibration distortion under alignment?" **Verdict: ENTHUSIASTIC ACCEPT — this opens entirely new research directions regardless of which mechanism dominates.**

---

### Consensus Hypothesis

**Formal Statement:**
Instruction-tuning alignment systematically perturbs the calibration of large language models by altering the logit distribution in ways that increase Expected Calibration Error (ECE) and, specifically, the Brier reliability component. The mechanism is empirically discriminable among three candidates — (H₁) monotonic logit-scale inflation (temperature distortion), (H₂) decision-boundary shift (representational reordering), and (H₃) framing-susceptibility (context-sensitive confidence reallocation) — via pre-specified tests: logit rank correlation (Spearman ρ), pre-softmax margin analysis, shared/changed prediction reliability decomposition, and Alignment × Distractor × Reliability interaction. The magnitude of miscalibration is predicted to follow a gradient ordered PPO ≥ DPO > SFT, reflecting the degree of reward-pressure optimization relative to the SFT reference policy. This gradient is directly testable using existing Pythia (1.4B/2.8B/6.9B) SFT, PPO, and DPO checkpoints on MMLU with lm-eval log-probability extraction.

**Primary Prediction:**
Alignment increases Brier reliability (overconfidence), with PPO ≥ DPO > SFT in magnitude, and this increase persists within shared-argmax item subsets.

**Secondary Predictions:**
1. If H₁: Spearman ρ ≥ 0.9 across alignment stages and logit margins inflate monotonically PPO ≥ DPO > SFT.
2. If H₂: Reliability degradation concentrates in changed-prediction items; ρ drops below 0.85 in PPO.
3. If H₃: Distractor prompts disproportionately reduce ΔReliability in PPO relative to SFT; interaction term is significant.

**Disconfirmation Criteria:**
- H₁ fails if ρ < 0.8 or reliability does not increase within shared-argmax items.
- H₂ fails if reliability worsens equally in shared-prediction and changed-prediction subsets.
- H₃ fails if distractors reduce ECE uniformly across all alignment methods.
- Global failure: if ΔECE ≤ 0 in all three alignment families (PPO, DPO, SFT), the hypothesis is rejected.

---

### Remaining Concerns

1. **Softmax normalization artifact (Prof. Rex):** ECE computed over softmax-normalized 4-option probabilities may amplify apparent overconfidence nonlinearly if PPO sharpens logit gaps. *Mitigation:* pre-softmax margin analysis is pre-specified as a diagnostic alongside ECE/Brier.

2. **Per-stratum sample size (Prof. Rex):** Conditional reliability decomposition (shared vs. changed predictions) may yield small strata for individual Pythia model sizes. *Mitigation:* pool across subjects within MMLU and report stratum sizes; use bootstrap CIs for small strata.

3. **Falcon training data heterogeneity (Prof. Rex):** Falcon-Instruct's additional training data may introduce capability confounds beyond alignment. *Mitigation:* report within-pair ΔACC alongside ΔECE; treat Falcon as a sensitivity check rather than a primary causal chain (primary chain = Pythia SFT → PPO → DPO).

4. **Verbal vs. softmax ECE conflation risk (Prof. Pax, Prof. Rex):** The Chhikara (2025) distractor-augmented prompts use verbally elicited confidence, not log-prob ECE. *Mitigation:* our primary ECE measure uses lm-eval log-prob continuation; distractor analysis is a secondary framing-susceptibility test and should be reported with explicit measurement-object labeling.

5. **ATS training data overlap (Dr. Ally note):** ATS's calibration head is trained on Alpaca GPT-4 data; if our MMLU evaluation overlaps with ATS's training distribution, the ATS diagnostic comparison may be confounded. *Mitigation:* use ATS as a diagnostic probe only, not as a baseline; report ATS τ-margin correlations on held-out MMLU subjects.

6. **DPO ≠ high-β PPO (Prof. Rex):** The β-proxy argument (DPO ≈ high-β PPO) is mathematically approximate. If PPO and DPO show similar ΔReliability but different rank correlations, the scalar reward-pressure narrative fails. *This is a feature, not a bug:* divergent rank correlations would indicate that objective *type* (not just strength) matters for miscalibration geometry — itself a novel finding.

---

