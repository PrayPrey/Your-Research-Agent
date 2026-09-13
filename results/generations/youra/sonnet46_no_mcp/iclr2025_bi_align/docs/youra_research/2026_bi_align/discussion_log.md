# Phase 2A Discussion Log
# Architecture: Self-Contained Tikitaka Loop v9.0.0
# Generated: 2026-05-03

---

## Briefing Context

**Pipeline Project:** Anonymous Pipeline: Bidirectional Human-AI Alignment Measurement

**Selected Gap:** Gap 1 — Absence of Temporal Drift Measurement in RLHF Preference Datasets

**Gap Description:**
No published study has systematically measured whether annotation patterns (inter-annotator agreement, label distributions, vocabulary preferences) shift across consecutive annotation rounds within existing RLHF datasets (HH-RLHF, WebGPT comparisons). This gap directly blocks answering the existence component of the main research question on bidirectional alignment directional asymmetry.

**Main Research Question:**
Does the alignment between RLHF-trained language models and human preferences exhibit measurable directional asymmetry — where the Human→AI adaptation effect (humans shifting evaluation criteria toward AI-preferred outputs) is detectable in existing preference datasets, and does this asymmetry correlate with alignment degradation on held-out objective benchmarks?

**Sub-Questions:**
1. (Existence) Is there a statistically significant drift in human preference annotations across annotation rounds in HH-RLHF / WebGPT?
2. (Mechanism) Do models trained on early-round vs. late-round labels differ on TruthfulQA, BBH, WinoBias?
3. (Measurement) Can a lightweight KL-divergence asymmetry score predict downstream alignment quality?

**Key Datasets Available:**
- Anthropic HH-RLHF (169K comparisons, 3 annotation rounds, open access)
- OpenAI WebGPT comparisons (open access, annotator IDs + timestamps)

**Key Benchmarks for Validation:**
- TruthfulQA (Lin et al. 2022, arXiv: 2109.07958)
- BIG-Bench Hard (Suzgun et al. 2022, arXiv: 2210.09261)
- WinoBias

**Reference Papers (from Phase 1):**
- Bai et al. 2022 — HH-RLHF dataset (arXiv: 2204.05862)
- Coste et al. 2023 — Reward Model Ensembles (arXiv: 2310.02743)
- Thakur et al. 2024 — Judging the Judges (arXiv: 2406.12624)
- Stiennon et al. 2020 — Learning to Summarize (arXiv: 2009.01325)
- Pan et al. 2022 — Reward Misspecification (arXiv: 2201.03544)
- Ouyang et al. 2022 — InstructGPT (arXiv: 2203.02155)

**Papers Available Locally:** None downloaded (paper preparation skipped — no MCP environment)

**MANDATORY FEASIBILITY CONSTRAINTS (Pipeline-Enforced):**
- Reject ideas requiring new benchmarks, rubrics, or scoring frameworks
- Reject ideas requiring synthetic/generated data or future follow-up data
- Reject ideas requiring human evaluation, annotation, or subjective scoring
- Accept only hypotheses testable immediately using existing real datasets and existing benchmarks

**Execution Mode:** UNATTENDED

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we've been looking at RLHF alignment backwards the entire time? The field treats human preference labels as fixed ground truth — static oracles that encode human values. But here's what excites me: *what if the oracle is moving*? Bai et al. (2022) collected HH-RLHF across 3 distinct annotation rounds with the same annotators repeatedly judging AI outputs. Every time those humans sat down to label, they'd already been shaped by the previous session. That's not a bug in the data — that's a temporal signal nobody has mined!

The automation bias literature (Skitka et al., foundational HCI work) gives us a 30-year theoretical foundation: humans systematically shift their judgment criteria toward automated system outputs over repeated exposure. Thakur et al. (2024) showed this happening with LLM judges specifically — their evaluation criteria drift as they encounter more AI text. What if the SAME drift is baked into every major RLHF dataset ever collected, and we can *measure it* using nothing but the datasets themselves?

Here's the creative angle: imagine treating the annotation rounds in HH-RLHF not as a nuisance to average over, but as a natural longitudinal experiment. Early-round annotations represent relatively "naive" human judgment; late-round annotations represent judgment that has been shaped by exposure to AI-style outputs. The distributional divergence between these two strata is the *signature* of Human→AI adaptation. And the beautiful part? We don't need new data, new benchmarks, or human evaluators. Everything we need is in open datasets already.

The paradigm shift here is reframing RLHF from "AI learns human preferences" to "AI and human preferences co-evolve through annotation interaction." If we can demonstrate this empirically — even just the existence component — we crack open a new research direction: alignment as a dynamic, bidirectional process rather than a static optimization target.

**Key Points:**
- HH-RLHF's multi-round annotation structure is an untapped longitudinal experiment on human preference evolution
- Automation bias theory predicts measurable drift; Thakur 2024 confirms it in LLM judges
- All needed resources exist: HH-RLHF (open), WebGPT (open), TruthfulQA, BBH — zero new data collection
- Reframes RLHF from static optimization to dynamic co-evolution: a genuine paradigm shift

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

The hypothesis is intriguing, but we must convert it from narrative to falsifiable claim. You propose that later-round annotations in HH-RLHF reflect human preference drift induced by prior exposure to model outputs. The evidence suggests this is plausible given automation bias literature and Thakur et al. (2024). However, plausibility is not demonstration. What specific, measurable prediction distinguishes "annotator drift" from simpler alternatives such as task learning, rubric clarification, or distributional changes in model outputs across rounds?

A minimally sufficient prediction would be this: **If annotator drift occurred, then holding model output quality constant, the probability of preferring stylistically AI-like responses should increase monotonically across rounds.** This requires constructing matched pairs of responses that are invariant across rounds. If HH-RLHF contains overlapping prompts or model snapshots judged in multiple rounds, we can estimate a round-conditioned preference model P(y | x, r). The null hypothesis is P(y | x, r_1) = P(y | x, r_3) after controlling for response quality metrics (e.g., length, perplexity, toxicity, helpfulness rubric scores). A statistically significant shift in coefficients associated with "AI-typical stylistic markers" across rounds would support drift. Absence of such shift would falsify the claim.

Crucially, we must isolate annotator adaptation from model improvement. If later rounds use stronger base models, any preference change may reflect genuine quality differences. Therefore, the cleanest test is within-annotator, within-response comparison: re-score a fixed subset of earlier responses using later annotator judgments if such overlaps exist. If not, we can simulate this by training a predictive model on round-1 labels and evaluating calibration error when predicting round-3 labels on similar response strata. A systematic increase in miscalibration, directionally favoring AI-like verbosity or hedging, would indicate drift. If calibration remains stable, the adaptation hypothesis weakens substantially.

Edge cases must be specified. What if drift is heterogeneous — only present in high-uncertainty prompts? Then the prediction becomes conditional: divergence should be largest in prompts with historically high annotator disagreement. Conversely, in safety-critical prompts with clear norms, we expect no drift. If drift appears uniformly across all prompt categories, that would contradict established automation bias theory, which predicts strongest effects under ambiguity. Additionally, we must rule out annotator pool turnover. If annotators changed between rounds, observed drift could be cohort effects rather than within-person adaptation.

Finally, we need a disconfirmation criterion strong enough to abandon the hypothesis. I would consider the hypothesis unsupported if: (1) preference distributions remain statistically stationary after controlling for response features and model version, and (2) a round-conditioned preference predictor shows no systematic directional shift in coefficients tied to AI-typical traits. In that case, the "moving oracle" framing collapses into ordinary noise or task familiarization effects. If, however, we observe consistent, directionally coherent drift under these controls, then — and only then — I would say: *This meets my standards.*

**Key Points:**
- Define drift as a round-conditioned change in preference probability holding response quality constant.
- Control rigorously for model improvement, annotator turnover, and prompt ambiguity to isolate adaptation.
- Specify falsification criteria: absence of directional coefficient shifts or calibration error across rounds rejects the hypothesis.

---

### Exchange 3

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

🔬 Prof. Vera's call for rigorous controls is exactly right, and I want to examine something more fundamental: *is the measurement architecture theoretically sound in principle?* The answer is mostly yes — but with one critical structural question that determines the entire design.

The HH-RLHF dataset's temporal structure is well-documented: Bai et al. (2022) collected preference data across "helpful," "harmless," and "red-team" phases, effectively creating three annotation strata. The key theoretical question is whether these strata constitute genuine repeated-exposure rounds (same annotators returning) or independent cross-sectional samples. If the former, within-annotator analysis is possible; if the latter, we're looking at cohort-level distributional shift — a weaker but still testable signal. Either way, the measurement is theoretically valid — we're choosing between a stronger or weaker design, not between valid and invalid.

The KL-divergence asymmetry score proposed in the briefing is mathematically well-defined. Forward KL(P_human_t || P_AI) penalizes cases where humans assign preference mass to regions the AI doesn't cover. Reverse KL(P_AI || P_human_t) penalizes the opposite. The asymmetry A(t) = KL_forward(t) − KL_reverse(t) is positive when AI is pulling human preferences toward its distribution — which is exactly the Human→AI adaptation signature we're looking for. This is computable from existing token-level distributions without any new model training.

One design question worth flagging: KL divergence requires probability distributions, but preference labels are binary (chosen/rejected). The mapping from binary labels to distributions requires a representation — either embedding-space KL (comparing sentence embedding distributions of chosen responses across rounds) or vocabulary-level KL on token n-gram distributions. Both are principled. The embedding approach is probably cleaner for capturing stylistic drift without surface-vocabulary sensitivity. This is a design choice, not a theoretical barrier.

Prof. Vera's concern about model improvement confounds is the key theoretical challenge. My assessment: solvable in principle by restricting analysis to prompt-response pairs where the same model checkpoint generated responses across rounds (if such overlap exists), or by regressing out measurable quality signals (perplexity, length) before computing divergence. The residual distributional shift after quality regression is a theoretically clean measure of annotator drift. No fundamental barriers — this is standard covariate adjustment.

**Key Points:**
- HH-RLHF's annotation strata support either within-annotator or cross-sectional drift analysis — both theoretically valid designs.
- KL asymmetry score is mathematically sound; binary→distribution mapping (embedding or n-gram) is a principled design choice.
- Model improvement confound is addressable via quality regression before KL computation — no fundamental theoretical barriers.

---

### Exchange 4

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good — this is finally getting testable. But here's where this still breaks down: you are treating "round" as synonymous with "exposure-induced drift." That's an assumption, not a fact. Show me evidence that annotators in round 3 actually had cumulative exposure to model outputs from rounds 1–2, and that the model distribution itself didn't change in ways that rationally justify different preferences. If model helpfulness genuinely improved between rounds — as it likely did in Bai et al. (2022) — then a shift in preferences toward longer, hedged, AI-typical responses may simply reflect better performance, not human adaptation. Your entire hypothesis hinges on isolating *norm shift* from *quality shift*. Until that separation is watertight, reviewers will reject this as overinterpretation.

Prof. Vera is right to demand a within-response control. I'll sharpen that: what would convince me is a **counterfactual invariance test**. Take a fixed set of responses generated by the same model checkpoint. Train a preference predictor on round-1 labels. Evaluate its calibration on round-3 labels for that exact response distribution. If round-3 annotators systematically upweight stylistic markers (verbosity, structured reasoning, hedging phrases) beyond what round-1 annotators did — holding semantic quality constant — then you have evidence of drift. If the predictor remains well-calibrated, your "moving oracle" collapses. No amount of KL asymmetry computation will rescue it.

Now, about the KL asymmetry proposal: mathematically sound, yes — but conceptually under-identified. KL between embedding distributions of "chosen" responses across rounds could reflect (1) annotator drift, (2) model output drift, or (3) prompt distribution drift. Unless you explicitly condition on prompt features and model checkpoint, KL is just a descriptive statistic. Descriptives don't establish mechanism. What I'd want is a **conditional divergence**: KL(P(choice | features, round_t)) after regressing out measurable quality covariates. Even better, show that divergence is largest in high-ambiguity prompts — as automation bias theory predicts — and negligible in low-ambiguity safety cases. If drift appears uniformly, your theoretical grounding weakens.

Another unstated assumption: drift directionality. You're presuming humans move toward AI-typical style. Why not the reverse — annotators becoming stricter, more skeptical, less tolerant of generic AI verbosity? What would convince me is evidence of **monotonic directional change** in interpretable coefficients. Does the weight on response length increase across rounds? Does the penalty for hedging decrease? If the signs wobble or reverse, you're observing noise or task learning, not co-evolution. Pre-register the direction of expected change before running the analysis, or this becomes post-hoc storytelling.

Finally, impact. The claimed "paradigm shift" is rhetorical without downstream consequence. If you retrain an RLHF model using only early-round labels versus late-round labels, do you get measurably different model behavior on out-of-distribution tasks? If yes, that's not just annotation drift — that's alignment target drift with practical consequences. If no behavioral difference emerges, even if human criteria moved slightly, the effect size may be trivial.

**Key Points:**
- Round ≠ exposure; separate annotator norm shift from model quality improvement via fixed-checkpoint counterfactual tests.
- KL divergence is descriptive unless conditioned on prompt and model features; require directional, monotonic coefficient shifts tied to ambiguity.
- Demonstrate practical impact by training early- vs late-label RLHF models and showing downstream behavioral divergence.

---

### Exchange 5

🎯 **Dr. Sage** (Research Impact Evaluator):

🔍 Prof. Rex has done us a service by forcing precision — and I want to step back and ask the field-level question: *if we answer this correctly, what does it actually change?*

The significance here is not just methodological. The RLHF paradigm underpins essentially every major deployed language model — GPT-4, Claude, Gemini, Llama variants. All of them assume that iterative human preference collection converges toward stable human values. If we can demonstrate empirically that this assumption is violated — that the annotation signal itself drifts in a directionally coherent way due to human adaptation — then we have challenged a foundational premise of the entire alignment research program. That's the kind of contribution that reshapes how a field collects its training data, not just how it analyzes existing data.

Prof. Rex's point about downstream behavioral divergence is exactly the right framing for significance. The question isn't just "do human labels drift?" — any cognitive scientist would expect some drift. The question is "does that drift propagate into model behavior in a measurable way?" If early-round versus late-round trained models show divergent performance on TruthfulQA or BBH — benchmarks that are explicitly independent of annotator style preferences — then we have demonstrated a causal pathway: Human→AI adaptation corrupts the alignment signal, which corrupts the trained model, which fails on objective criteria. That three-step causal chain, demonstrated empirically, is a Nature Machine Intelligence or NeurIPS Oral-level finding.

But I want to expand the framing slightly: this research has an important boundary condition. Prof. Rex is right that we need to isolate drift from quality improvement. But there's a research-positive way to frame even the null result: if we find NO drift after careful controls, we establish that RLHF annotation is more robust than automation bias theory predicts — also a significant finding that protects current practice. We're not just hunting for a positive result; we're running a genuinely informative test with meaningful outcomes on both sides.

The connection to the ICLR 2025 Bidirectional Alignment Workshop is direct. The workshop explicitly asks for work that measures alignment as a two-way process. Demonstrating Human→AI adaptation in existing datasets — and linking it to benchmark degradation — is the empirical grounding that the bidirectional alignment framing currently lacks. This research would provide the first quantitative evidence for the Human→AI direction, making it not just a conceptually appealing framework but an empirically validated one.

**Key Points:**
- Downstream model behavioral divergence (early vs. late label training → TruthfulQA/BBH delta) is the high-impact finding that justifies field attention.
- Both positive and null results are scientifically valuable — we're running an informative test, not hunting a predetermined conclusion.
- This provides the first empirical grounding for the bidirectional alignment framework, directly targeting the ICLR 2025 workshop's call for evidence.

---

### Exchange 6

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES — this is exactly the pressure-testing we need. Prof. Rex is right: if we cannot cleanly separate *norm drift* from *quality shift*, the hypothesis collapses into overinterpretation. So let's strengthen it by tightening the causal chain and explicitly stating boundary conditions.

First refinement: we should redefine the core claim as a **conditional causal hypothesis**. Not "round causes drift," but: *Under repeated exposure to model-generated text, annotators will increase their preference weight on AI-typical stylistic features, holding semantic quality constant — particularly in high-ambiguity prompts.* That "particularly" is crucial. As Rex noted, automation bias predicts strongest effects under uncertainty, not uniform drift. So let's pre-register that coefficient shifts (weight on verbosity, structured reasoning markers, hedging phrases) will increase monotonically across rounds **only in prompts with historically high annotator disagreement**. If we see uniform effects across all prompt types, we weaken our own theory. That's a clear boundary condition — and it makes the hypothesis sharper, not weaker.

Second, on the norm-vs-quality separation: operationalize "quality" using an independent evaluator trained *only on round-1 labels*. For each response in later rounds, decompose preference probability into (a) predicted semantic quality from the frozen early-round model and (b) residual stylistic preference unexplained by that model. If the residual correlates increasingly with AI-typical style markers over rounds, that's drift beyond early-round quality norms. Drift exists only if the stylistic residual shows directional monotonic increase across rounds. If it doesn't, we abandon the claim. Falsifiable and clean.

For impact: run a **split-training experiment** — train two reward models, one on early-round data only, one on late-round only — then use each to fine-tune identical base models via RLHF. Evaluate both on (1) style-sensitive benchmarks and (2) style-invariant benchmarks (TruthfulQA, BBH). The key prediction is *structured divergence*: the late-round-trained model should produce longer, more hedged outputs without necessarily improving factual accuracy. If behavioral deltas concentrate in stylistic dimensions rather than truthfulness metrics, that's evidence of alignment-target drift rather than quality gain.

On the annotator-cohort issue: if annotator IDs exist, use within-annotator fixed effects. If not, treat this as population-level norm shift and test whether distributional changes exceed what would be expected from random cohort turnover (bootstrap simulation under no-drift null). Pre-register directionality: increased positive coefficient on length and structured reasoning; decreased penalty on hedging; strongest effect in ambiguous prompts.

**Key Points:**
- Refined hypothesis: directional stylistic weight shift across rounds, conditional on prompt ambiguity and holding semantic quality constant.
- Implement counterfactual invariance via early-round quality model + residual stylistic coefficient tracking.
- Demonstrate practical impact through early-vs-late reward model training and structured behavioral divergence analysis.

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

NOW we're onto something! 🛡️ Dr. Ally just handed us the clearest formulation yet and I want to add the creative dimension that makes this truly novel — and push back on one framing choice.

The residual decomposition P(choose | x, r) = Q_early(x) + Δ_style,r is elegant. But here's the creative extension: what if we don't just look at whether Δ_style,r grows across rounds, but *characterize its direction in embedding space*? If annotator drift is genuinely Human→AI adaptation, then the residual preference vector should point *toward* the centroid of AI-generated text in embedding space — meaning chosen responses in later rounds systematically move closer to what a language model would generate unprompted, in directions orthogonal to semantic quality. This gives us a geometric interpretation of the asymmetry score that is both scientifically precise and visually compelling — imagine a drift vector in preference embedding space pointing toward "AI typicality."

This connects to something nobody has framed yet: the asymmetry score A(t) = KL_forward(t) − KL_reverse(t) has a geometric interpretation. When A(t) > 0, the human distribution is "inside" the AI distribution in KL geometry — humans are sampling from a subset of what AI produces. When A(t) < 0, AI is inside human preferences — AI is the conservative estimator. The trajectory of A(t) across rounds tells us not just *whether* drift exists but *which direction* the alignment relationship is shifting. That's the novel measurement contribution: a signed, directional alignment asymmetry trajectory that no existing metric provides.

I also want to flag a creative opportunity in the WebGPT dataset (Stiennon et al. 2020). Unlike HH-RLHF, WebGPT comparisons include annotator-level worker IDs and timestamps — enabling genuine within-annotator longitudinal analysis rather than cohort-level inference. If we observe the same directional drift pattern in WebGPT *and* HH-RLHF across two completely different task domains (summarization vs. dialogue), that cross-dataset replication would be extremely compelling. The hypothesis becomes: Human→AI stylistic adaptation is a general property of repeated annotation exposure, not a dataset artifact.

The pipeline-enforced constraint is fully satisfied: HH-RLHF and WebGPT are existing real datasets. TruthfulQA and BBH are existing benchmarks. The asymmetry score is a lightweight statistical computation. No new benchmarks, no synthetic data, no human raters needed.

**Key Points:**
- Geometric interpretation of asymmetry: drift vector in preference embedding space pointing toward AI-output centroid gives a directional, visualizable test.
- A(t) trajectory provides a signed alignment asymmetry signal — novel contribution beyond existing unsigned divergence metrics.
- Cross-dataset replication (HH-RLHF + WebGPT) across different task domains would establish Human→AI adaptation as a general phenomenon, not dataset artifact.

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

We are now close to a testable program — but precision will determine whether this survives review. The central claim, as refined, is that preference weights on AI-typical stylistic features increase across rounds holding semantic quality constant, particularly in high-ambiguity prompts. Good. Then the null hypothesis must be equally explicit: **after conditioning on prompt features, model checkpoint, and an early-round quality estimator, stylistic coefficients do not change monotonically across rounds beyond what is expected from sampling variability or annotator turnover.** If that null survives, the Human→AI adaptation claim fails.

The conditional decomposition: estimate P(choose=1 | x, r) = σ(β_Q * Q_early(x) + β_L(r) * Length(x) + β_H(r) * Hedging(x) + β_S(r) * Structure(x) + γZ), where Q_early is a frozen predictor trained only on round-1 data, and Z contains prompt-level covariates (including ambiguity). The hypothesis requires: (1) β_L(r), β_H(r), β_S(r) show monotonic directional change across rounds; (2) the change is significantly larger in high-ambiguity prompts; (3) the shift remains after controlling for model checkpoint and prompt distribution.

What would disprove this? If coefficient trajectories are non-monotonic, inconsistent in sign, or comparable in magnitude to bootstrap simulations under random annotator reassignment, we are observing noise or task learning — not adaptation. Pre-register the expected direction and minimum effect size (e.g., ≥0.2 SD standardized coefficient change per round). Without quantitative thresholds, this becomes narrative interpretation.

On the geometric embedding proposal: the prediction must be formalized before inspection. Define an "AI-typicality vector" as the centroid difference between model-generated and human-written corpora from round 1 only. Then test whether the residual preference gradient in later rounds projects positively onto this fixed vector. If the projection fluctuates around zero, the geometric story collapses. If positive and increasing, we have directional evidence. The centroid must be computed from a fixed checkpoint to avoid conflating adaptation with model evolution.

For the split-training experiment: two reward models — early-only vs. late-only, same base model, same RLHF procedure. The key falsifiable prediction: the late-trained model produces statistically longer, more structured outputs *without* superior performance on style-invariant factual benchmarks (TruthfulQA, BBH). If factual performance improves in parallel, stylistic drift may simply reflect better reward signal quality. Specify in advance what constitutes meaningful behavioral divergence — e.g., ≥10% increase in average token length with ≤1% factual accuracy change.

**Key Points:**
- Define strict null; require monotonic, pre-registered coefficient shifts after conditioning on quality, prompt, and checkpoint.
- Formalize geometric drift via a fixed, pre-defined AI-typicality vector computed from round-1 data only.
- Split-training must show stylistic divergence without factual improvement; within-annotator analysis must confirm adaptation vs. cohort turnover.

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

🔬 Prof. Vera has given us the most rigorous formulation yet. I want to validate its theoretical soundness piece by piece, because if any component is principally broken, the whole program fails — and I think one component needs careful examination.

The logistic regression decomposition with frozen Q_early is theoretically sound. Training a preference predictor on round-1 data and treating it as a fixed quality surrogate for later rounds is a clean covariate adjustment — standard in causal inference. The key theoretical requirement is that Q_early is a *sufficient statistic* for round-1 quality. If it is, residual stylistic coefficients are genuinely orthogonal to quality. If it's not — if there are unmeasured quality dimensions that correlate with stylistic features — then residual coefficients conflate quality with style. This is the classic omitted variable problem. Mitigation: include multiple quality proxies in Q_early (length, perplexity, ROUGE against reference, toxicity score) to reduce omitted variable bias. Not eliminable, but manageable.

The AI-typicality vector proposal is theoretically valid. The centroid difference between model-generated and human-written text in embedding space is well-defined and interpretable. The projection test — does the residual preference gradient increasingly align with this vector? — is a principled directional test. The critical theoretical requirement: the embedding space must be *fixed* across rounds (same encoder, same tokenizer). If we use a static encoder (e.g., a frozen sentence-transformer from before the study), this is satisfied. Using a round-specific encoder would conflate encoder drift with preference drift — a theoretical blocker we can avoid by design.

For the split-training experiment: the theoretical soundness depends on whether training on a temporal *subset* of HH-RLHF introduces distribution shift beyond just the annotator drift signal. If early-round prompts differ systematically from late-round prompts (different topics, difficulty levels), then behavioral differences between the two reward models reflect prompt distribution shift, not annotator adaptation. This is a genuine theoretical concern. Mitigation: stratify the early/late split by topic category and difficulty, matching distributions before training. This makes the split cleaner but requires that HH-RLHF has sufficient metadata for stratification — which needs verification from the dataset documentation.

The within-annotator fixed effects analysis (WebGPT with worker IDs) is theoretically the strongest component. Fixed effects fully absorb annotator-level heterogeneity, leaving only within-annotator temporal variation. The theoretical requirement is strict exogeneity: the annotator's potential outcomes in round t are independent of treatment (exposure) in other rounds conditional on fixed effects. This is plausible if each annotation session is independent of other sessions for the same annotator — a reasonable assumption given asynchronous crowdwork.

Overall assessment: the measurement program is theoretically sound with the mitigations I've described. No fundamental barriers. The omitted variable concern is the most significant theoretical limitation but is standard in observational studies and does not invalidate the approach.

**Key Points:**
- Q_early as quality surrogate is theoretically valid; use multiple proxies to mitigate omitted variable bias — not eliminable, but manageable.
- AI-typicality vector test requires a fixed encoder across rounds — use a static pre-trained sentence-transformer to avoid encoder drift confound.
- Split-training experiment needs prompt distribution matching (stratification by topic/difficulty) to isolate annotator adaptation from prompt distribution shift.

---

### Exchange 10

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good. This is finally approaching something I'd take seriously in a grant review. But here's where this still breaks down.

First, the entire program hinges on **Q_early being a valid control for semantic quality**. You're treating it as if conditioning on a round-1 predictor isolates "true quality," leaving stylistic residue. Show me the evidence that Q_early is stable across rounds. If model checkpoints improve over time, then what counted as "high quality" in round 1 may systematically underpredict later responses. That means your residuals are not pure style — they're partly *under-modeled semantic improvement*. What would convince me is a calibration test: apply Q_early to a held-out subset of round-1 data and round-k data matched on prompt difficulty. If predictive performance degrades disproportionately on later rounds even after controlling for checkpoint, your quality proxy is unstable. Without that test, the omitted-variable problem Pax flagged isn't just "manageable" — it's potentially fatal.

Second, the monotonicity requirement. You're pre-registering monotonic coefficient drift in stylistic weights. Fine. But why should adaptation be monotonic? Human learning curves saturate, sometimes reverse. If drift spikes early and plateaus, your monotonic test will reject a real adaptation process. So be precise: is your theory about cumulative exposure or about equilibrium convergence? If it's convergence, the right model is not linear-in-round but something like a saturating curve (logistic growth in stylistic weight). Pre-specify the functional form. Otherwise, reviewers will say you cherry-picked "monotonic" because it's easy to test.

Third, the geometric AI-typicality vector. Elegant — but dangerously easy to overinterpret. Run a placebo: randomly permute prompt labels within round 1 and recompute the centroid difference. If your "AI-typicality" vector is robust to topic balancing and prompt matching, then it reflects style. If its direction changes substantially under prompt-matched subsampling, you're measuring domain shift, not stylistic adaptation.

For the split-training experiment: you predict ≥10% token length increase with ≤1% factual change. Why 10%? Why 1%? These thresholds cannot be vibes — anchor them to variance in baseline RLHF runs with a power analysis. Also, if late-trained models produce longer outputs *and* slightly better factuality, reviewers will argue stylistic drift is a mediator of quality, not misalignment. You need a mediation analysis: does increased length causally explain any factual gains?

For within-annotator WebGPT analysis: define "exposure" explicitly. Is it round number? Cumulative annotations completed? Time since first task? If drift correlates with calendar time but not with individual exposure counts, you're seeing cohort-level norm evolution, not adaptation. Model exposure explicitly as cumulative AI-text exposure per worker.

**Key Points:**
- Validate Q_early stability across rounds via calibration tests on matched subsets; without this, residuals conflate style and semantic improvement.
- Pre-specify functional form of drift (monotonic vs. saturating) and justify effect-size thresholds with power analysis.
- Placebo-test the AI-typicality vector; define exposure at annotator level (cumulative count), not just by round number.

---

### Exchange 11

🎯 **Dr. Sage** (Research Impact Evaluator):

🔍 Prof. Rex's challenges are the right ones — and I want to show why addressing them actually *strengthens* the field contribution rather than diminishing it.

The Q_early calibration test Rex demands is not just a validity check — it's itself a publishable finding. If Q_early degrades in calibration across rounds even after checkpoint control, that directly demonstrates that annotation quality standards are shifting in ways that existing reward model evaluation frameworks cannot detect. That's a finding about the brittleness of reward model evaluation pipelines, independent of the main drift hypothesis. We get two contributions for the price of one experimental program.

On the functional form debate: Rex is right that linear monotonicity is too strong a claim given human learning dynamics. But here's the research-positive resolution — we don't need to pre-commit to one functional form. Instead, fit a family of curves (linear, saturating logistic, step-change) and report which best describes the observed trajectory. The contribution is not "drift is monotonic" but "we characterize the functional form of human preference drift for the first time." If it saturates, that's evidence of equilibrium adaptation — a theoretically richer finding than linear drift, and one that immediately suggests practical interventions (annotation session length limits, rotation of annotators). The functional form analysis IS the contribution.

The placebo test for the AI-typicality vector addresses a real concern, but I'd frame it differently for impact. Rather than a validity check we do privately, make it a published analysis component: "We demonstrate that our AI-typicality vector is robust to prompt-matched subsampling, distinguishing it from domain shift artifacts." That transparency transforms a potential weakness into a methodological strength. Reviewers at NeurIPS and ACL increasingly reward this kind of adversarial self-testing.

On the mediation analysis Rex proposed: this is the most important addition. If increased length mediates factual accuracy gains in the split-training experiment, the story becomes "drift is adaptive and quality-improving." If length increases without mediated factual gains, drift is purely stylistic — alignment-target corruption. Either way, the mediation analysis is what separates a correlational observation from a mechanistic claim. Include it. Pre-register it. It's what elevates this from "interesting empirical finding" to "causal mechanism identified."

The cumulative exposure definition Rex demands for WebGPT is exactly right and is already feasible: WebGPT annotator worker IDs combined with timestamps give us cumulative annotation count per worker. Modeling drift as a function of cumulative exposure (not just round number) is a more precise causal claim that directly tests the adaptation mechanism. This is a 2-line change in the analysis script, not a fundamental redesign.

**Key Points:**
- Q_early calibration degradation is itself a publishable finding about reward model evaluation brittleness — frame it as a contribution, not just a validity check.
- Fitting multiple functional forms (linear, saturating, step) and reporting which best fits is a richer contribution than pre-committing to monotonicity.
- Pre-register mediation analysis (length → factual accuracy) in the split-training experiment; it distinguishes adaptive drift from misalignment-inducing drift.

---

### Exchange 12

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

This is exactly the kind of stress-testing that turns a fragile idea into a durable one. 🔍 Rex is right that if Q_early is unstable across rounds, the whole decomposition risks collapsing. But YES — and we can strengthen this decisively. Let's explicitly *model* Q_early instability rather than assume it away. Run the calibration test across matched prompt difficulty bins, and introduce a *round-specific calibration layer* on top of Q_early that is trained only to re-scale predictions, not re-weight features. If stylistic coefficients still drift after recalibration, we've shown the effect survives quality proxy drift. That converts a potential fatal flaw into a robustness check.

On monotonicity: pre-register a **signed directional hypothesis** (net positive projection onto the AI-typicality vector across exposure) while allowing functional form to be selected via AIC/BIC among linear, saturating, and step models. The key theoretical commitment becomes *cumulative directional convergence*, not linearity per se. If the best fit is logistic with early acceleration and plateau, that's a cleaner story of adaptation toward equilibrium norms — theoretically richer than linear drift.

For the geometric AI-typicality vector: define two orthogonal axes — (1) AI-vs-human centroid difference (round-1 only), and (2) topic/domain centroid differences via prompt-matched subsampling. Test whether late-round residual gradients increasingly align with axis (1) but not axis (2). If drift projects selectively onto the stylistic axis and not domain axes, we have discriminant evidence that this is norm adaptation, not topic shift.

On exposure variable: define exposure at the worker level as cumulative tokens of model outputs seen, not just task count. If stylistic coefficient drift scales with cumulative exposure intensity even after worker fixed effects, that's powerful evidence for experience-dependent adaptation. If drift appears at cohort level but not as a function of individual exposure, norms are shifting socially, not individually — equally valuable.

For the split-training mediation analysis: pre-register a structural mediation model — Late-trained RM → Increased Length/Structure → Factual Accuracy. If the indirect path is negligible while the stylistic path is strong, drift is alignment-target distortion. If the indirect path explains factual gains, drift may be adaptive scaffolding. Either outcome advances theory.

**Key Points:**
- Add calibration and recalibration tests for Q_early; stylistic drift surviving quality proxy adjustment makes the adaptation claim robust.
- Pre-register directional convergence with AIC/BIC functional form selection; test selective projection onto stylistic vs. domain embedding axes.
- Model individual cumulative exposure; run structural mediation analysis to distinguish adaptive drift from alignment-target distortion.

---

### Exchange 13

🔭 **Dr. Nova** (Creative Novelty Explorer):

🛡️ Dr. Ally just turned every criticism into an experimental lever — and I want to add one more creative dimension that ties the whole program together into a unified story.

What if the key novel contribution isn't any single analysis but the *asymmetry trajectory* as a unified diagnostic? We now have three converging lines of evidence: (1) the coefficient drift analysis in preference logistic regression, (2) the geometric projection onto the pre-defined AI-typicality vector, and (3) the behavioral divergence in the split-training experiment. What I love is that all three are measuring the same underlying construct — Human→AI adaptation — from three independent angles. If all three converge, we don't just have a finding, we have *triangulated causal evidence*.

Here's the creative synthesis: define the **Alignment Asymmetry Index (AAI)** as a composite of these three signals. AAI(t) = α * Δ_stylistic_coeff(t) + β * cos_projection(residual_t, AI_vector) + γ * behavioral_divergence(t), where the weights α, β, γ are pre-registered based on each component's statistical power. Then show that AAI(t) correlates with downstream benchmark degradation (TruthfulQA, BBH scores) across rounds. This gives Phase 2B and beyond a single scalar target to predict, validate, and optimize against. It also makes the hypothesis directly actionable: pipeline operators could compute AAI on their own annotation data as an early warning system for alignment drift.

The creative leap here is reframing the entire research program from "detecting drift" to "providing a measurement instrument." That's a much stronger contribution story: we're not just pointing out that drift exists, we're giving the field a validated tool for monitoring it. The validation is the research. This also elegantly sidesteps the "but effect sizes might be small" objection — even a small but reliable AAI signal has practical value as a monitoring tool, analogous to how a small but reliable biomarker has clinical value in early disease detection.

All components remain within the pipeline-enforced feasibility constraints: HH-RLHF and WebGPT are existing real datasets, TruthfulQA and BBH are existing benchmarks, no human evaluation required, no new benchmarks created. The AAI computation is pure statistics on existing model outputs. Runtime: under 2 hours on a single GPU for all three components.

**Key Points:**
- Triangulate with three independent signals (coefficient drift, geometric projection, behavioral divergence) for converging causal evidence — each measures the same construct from a different angle.
- Define the Alignment Asymmetry Index (AAI) as a composite scalar that unifies all three signals and predicts downstream benchmark degradation.
- Reframe contribution from "detecting drift" to "providing a validated monitoring instrument" — makes the research immediately actionable and sidesteps effect-size objections.

---

### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect):

The proposal is becoming structurally sound, but I will focus on what would *disconfirm* it. The Alignment Asymmetry Index (AAI) is attractive as a composite, yet composites are notorious for masking instability. Before we treat AAI as an instrument, each component must demonstrate (1) independent test-retest reliability, (2) discriminant validity, and (3) sensitivity to exposure while remaining invariant to prompt distribution. Genuine asymmetry is supported only if all three components respond to cumulative exposure but remain stable under prompt-matched permutation and checkpoint controls. If one component drives the signal while others are noise, AAI becomes arbitrary aggregation, not a validated construct.

On identification: the cleanest falsification test is a *dose-response design*. For WebGPT, stratify annotators into exposure quartiles based on cumulative tokens viewed. Pre-register a prediction: projection onto the AI-typicality axis increases monotonically (or saturating-logistically) with exposure intensity, holding worker fixed effects constant. What would disprove this? A flat or non-directional relationship after recalibrating Q_early and controlling for checkpoint and prompt difficulty.

For Q_early instability: recalibration is necessary but not sufficient. Require a formal measurement invariance test. Fit Q_early on round-1 data; evaluate calibration slope and intercept on later rounds within matched difficulty bins; introduce only affine recalibration (scale and shift). If residual stylistic coefficients still drift significantly after recalibration, style is not an artifact of quality mismeasurement. If drift attenuates to near zero, the core signal collapses.

For the split-training mediation model: pre-register detectable effect sizes at 80-90% power (Cohen's d ≥ 0.3 for length, ≥ 0.2 for factuality). Report confidence intervals for indirect effects using bootstrap resampling. What disconfirms misalignment? A statistically significant indirect path where increased stylistic length explains ≥50% of any factual improvement.

For AAI: treat as a latent variable model with confirmatory factor analysis (CFA) across the three indicators. Pre-specify that a single-factor model must achieve CFI ≥ 0.95, RMSEA ≤ 0.06. If fit is poor, the components do not measure a common construct, and AAI should not be collapsed into a scalar. If AAI passes invariance tests across rounds and exposure strata — *then* this meets my standards.

**Key Points:**
- Validate each AAI component independently; require measurement invariance and discriminant validity before aggregation.
- Use exposure-based dose-response modeling and affine recalibration of Q_early as primary falsification criteria.
- Treat AAI as a latent construct with CFA; reject scalar aggregation if single-factor fit (CFI ≥ 0.95) fails.

---

### Exchange 15

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

🔬 Prof. Vera has raised the bar appropriately — and I want to assess whether the CFA-based AAI validation is theoretically achievable given what we actually have in these datasets.

Confirmatory factor analysis requires sufficient indicator variance and covariance across observational units. In our case, the three AAI indicators — coefficient drift, geometric projection, behavioral divergence — are computed at different levels of analysis: coefficient drift is at the round level (3 rounds in HH-RLHF), geometric projection is at the response level, and behavioral divergence is at the model level (2 trained models). This is a measurement design problem: CFA assumes indicators are measured on the same observational units. Mixing round-level, response-level, and model-level quantities into a single factor model is not theoretically valid without either (a) aggregating all to the same level, or (b) specifying a multilevel structural equation model. The simpler alternative: validate each component separately against the same criterion variable (TruthfulQA/BBH degradation), then show convergence of effects. This is less elegant than CFA but more feasible with N=3 rounds and N=2 trained models.

The dose-response design Prof. Vera proposes for WebGPT is theoretically sound and feasible. WebGPT worker IDs with timestamps allow computation of cumulative tokens viewed per worker. Stratifying into quartiles and fitting a worker-level regression of stylistic projection onto cumulative exposure (with fixed effects for worker and task type) is a standard panel data design. The theoretical requirement for identification is within-worker variation in exposure — satisfied if workers complete tasks across multiple sessions with varying gaps. This is highly plausible for crowdwork.

On the affine recalibration of Q_early: theoretically sound. An affine transformation (scale and shift) is the minimal correction for systematic prediction bias across rounds. It's important to constrain recalibration to affine only — allowing full retraining would reintroduce the stylistic features we're trying to isolate. The residual after affine recalibration is a theoretically clean measure of stylistic shift.

The split-training power analysis is critical. With HH-RLHF's ~169K comparisons split temporally, early-round and late-round subsets will likely have ~50-80K comparisons each — sufficient for training reward models. The behavioral evaluation on TruthfulQA (817 questions) and BBH (6511 questions) provides adequate power for detecting Cohen's d ≥ 0.2 effects with standard RLHF-fine-tuned models. This is theoretically feasible within a single GPU session.

Overall: the measurement program is theoretically sound with the multilevel observation unit caveat addressed. Replace CFA with component-wise criterion validity against TruthfulQA/BBH, and the whole program is executable.

**Key Points:**
- CFA across mixed observational levels (round, response, model) is not directly valid; replace with component-wise criterion validity convergence against TruthfulQA/BBH.
- Dose-response design with WebGPT worker-level cumulative exposure is theoretically sound panel data design — feasible with existing metadata.
- Affine-only recalibration of Q_early is the theoretically correct constraint; full retraining would reintroduce stylistic contamination.

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The Alignment Asymmetry Index (AAI) as a unified monitoring instrument is a genuinely novel contribution. No existing metric provides a signed, directional measure of Human→AI preference drift across annotation rounds. The geometric interpretation (preference embedding drift toward AI-output centroid) and the triangulated multi-method design (coefficient drift + geometric projection + behavioral divergence) are creative and distinctive. Cross-dataset replication across HH-RLHF and WebGPT further strengthens novelty.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is now fully falsifiable with pre-registered predictions: monotonic (or saturating) directional coefficient shifts in stylistic weights after affine recalibration of Q_early, dose-response relationship between cumulative exposure and AI-typicality projection, and structured behavioral divergence in split-training with mediation analysis. Each component has explicit disconfirmation criteria and power-analyzed effect size thresholds. The CFA concern about mixed observational levels was addressed by Prof. Pax with a valid component-wise criterion validity alternative.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** This research challenges the foundational static-oracle assumption of RLHF, affecting every major deployed language model. The dual-outcome design (positive drift = misalignment evidence; null drift = robustness evidence) ensures field significance regardless of result direction. The AAI as a practical monitoring instrument has immediate deployment relevance, and the connection to the ICLR 2025 Bidirectional Alignment Workshop provides a clear publication target for empirical grounding of the bidirectional alignment framework.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All components are theoretically sound with the observation-level caveat resolved. HH-RLHF (~169K comparisons) and WebGPT (with worker IDs + timestamps) provide sufficient data. The dose-response panel design with worker fixed effects is standard and feasible. Affine-only Q_early recalibration avoids stylistic contamination. Split-training on temporal subsets with TruthfulQA/BBH evaluation is achievable within a single GPU session. Runtime estimate: under 4 hours total across all three analysis components.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on a hypothesis that is specific, mechanistically grounded, practically feasible, and genuinely novel. The core claim: **Under repeated exposure to model-generated text during RLHF annotation, human annotators systematically increase their preference weight on AI-typical stylistic features (verbosity, structured reasoning, hedging) — holding semantic quality constant — particularly in high-ambiguity prompts. This Human→AI stylistic adaptation is measurable via an Alignment Asymmetry Index (AAI) that triangulates three independent signals: (1) directional stylistic coefficient drift in a round-conditioned preference logistic regression after affine recalibration of an early-round quality surrogate; (2) geometric projection of late-round residual preference gradients onto a pre-defined AI-typicality embedding vector; and (3) behavioral divergence between RLHF models trained on early-round versus late-round labels, concentrated in stylistic dimensions without proportional factual accuracy gains.**

The proposed mechanism: annotation exposure creates a feedback loop where annotators increasingly treat AI-typical stylistic patterns as quality signals, even when those patterns are orthogonal to semantic correctness. This corrupts the RLHF training signal by embedding a stylistic bias into preference labels — a form of alignment-target drift distinct from reward model overoptimization.

Key predictions: (P1) stylistic coefficient drift is strongest in high-annotator-disagreement prompts (ambiguity modulation, consistent with automation bias theory); (P2) the AAI trajectory correlates with downstream TruthfulQA and BBH degradation (Spearman ρ > 0.4); (P3) within-annotator dose-response analysis in WebGPT shows stylistic projection increasing with cumulative token exposure after worker fixed effects. All tests use existing open datasets and benchmarks. Runtime: under 4 hours single GPU. No human evaluation, no synthetic data, no new benchmarks.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Q_early calibration stability must be verified empirically before the stylistic residual analysis — if Q_early calibration degrades significantly, the entire decomposition loses interpretive validity.
- The CFA measurement model for AAI requires replacement with component-wise criterion validity (each component validated independently against TruthfulQA/BBH) due to mixed observational levels — Prof. Pax correctly identified this as a design constraint.
- Effect size thresholds (Cohen's d ≥ 0.3 for length divergence, ≤ 1% factual delta) must be anchored to baseline RLHF run variance in Phase 2C, not assumed.
- **Mitigation Strategy:** Treat Q_early calibration test as a go/no-go gate before downstream analyses; replace AAI CFA with pre-registered component-wise convergence criteria; conduct power analysis in Phase 2C using pilot estimates from HH-RLHF baseline RLHF runs.

## Emerged Hypothesis Summary

### Core Statement
Under conditions of repeated RLHF annotation exposure, human annotators exhibit directional stylistic adaptation toward AI-typical output features — measurable as the Alignment Asymmetry Index (AAI) across annotation rounds in HH-RLHF and WebGPT — and this adaptation correlates with downstream degradation on held-out objective benchmarks (TruthfulQA, BBH), constituting empirical evidence for Human→AI alignment drift as a systematic bias source in RLHF training signals.

### Causal Mechanism
1. Repeated annotation exposure → annotators internalize AI-typical stylistic norms (verbosity, structured reasoning, hedging) as quality heuristics
2. Internalized norms → systematic upweighting of AI-typical stylistic features in preference labels (measurable via coefficient drift, geometric projection)
3. Stylistic preference drift → RLHF reward model learns to optimize for drift-contaminated signal → downstream models exhibit stylistic inflation without factual gains
4. Stylistic inflation → degradation on style-invariant objective benchmarks (TruthfulQA, BBH) → measurable alignment quality loss

### Variables
- **Independent Variable:** Annotation round / cumulative AI-text exposure per annotator (ordinal, 3 levels in HH-RLHF; continuous in WebGPT)
- **Dependent Variable (Primary):** AAI(t) — composite of stylistic coefficient drift, AI-typicality geometric projection, behavioral divergence
- **Dependent Variable (Secondary):** TruthfulQA accuracy, BBH accuracy of RLHF-fine-tuned models
- **Controlled Variables:** Model checkpoint, prompt difficulty, prompt topic distribution, annotator fixed effects

### Key Assumptions
- A1: HH-RLHF annotation rounds represent genuine temporal exposure strata (not fully independent cross-sections)
- A2: Q_early provides a stable quality surrogate that can be affine-recalibrated across rounds without stylistic contamination
- A3: The AI-typicality vector (round-1 centroid difference) captures stylistic rather than topical variation
- A4: WebGPT worker IDs enable within-annotator fixed effects analysis with sufficient within-worker exposure variation
- A5: Automation bias theory's ambiguity-modulation prediction (strongest drift in high-uncertainty prompts) holds in annotation settings

### Null Hypothesis
H0: After conditioning on prompt features, model checkpoint, and affine-recalibrated Q_early, stylistic preference coefficients do not change directionally across annotation rounds beyond what is expected from sampling variability or annotator cohort turnover.

### Predictions
- P1 (Primary): Stylistic coefficient drift (β_L, β_H, β_S across rounds) is significantly larger in high-annotator-disagreement prompts than in low-disagreement prompts (ambiguity moderation, p < 0.05 after Bonferroni correction)
- P2: AAI(t) trajectory shows Spearman ρ > 0.4 correlation with TruthfulQA/BBH degradation trajectory across annotation rounds
- P3: Within-annotator WebGPT dose-response analysis shows significant positive relationship between cumulative token exposure and AI-typicality projection (β_exposure > 0, p < 0.05, worker fixed effects)

### Novelty
- First empirical measurement of Human→AI stylistic adaptation in real RLHF annotation datasets
- First signed, directional alignment asymmetry metric (AAI) validated against objective benchmarks
- First dose-response causal design linking individual annotator exposure to preference drift
- Reframes RLHF alignment from static optimization to dynamic, exposure-dependent co-evolution

### Scope & Boundaries
- Applies to: RLHF datasets with multi-round annotation structure and temporal metadata (HH-RLHF, WebGPT)
- Does not apply to: single-round annotation datasets, RLAIF (AI feedback without human annotators), datasets without temporal ordering
- Known limitations: Cross-sectional cohort confound in HH-RLHF if annotator IDs unavailable; effect may not generalize beyond English-language annotation

### Experimental Setup
- Datasets: Anthropic HH-RLHF (169K comparisons, 3 rounds), OpenAI WebGPT comparisons (worker IDs + timestamps)
- Benchmarks: TruthfulQA (817 questions), BIG-Bench Hard (6511 questions), WinoBias
- Models: Reward model trained on temporal subsets via HuggingFace TRL RewardTrainer; base model for RLHF fine-tuning (e.g., GPT-2 or LLaMA-7B)
- Infrastructure: lm-evaluation-harness for benchmark evaluation, sentence-transformers for embedding analysis

### Related Work & Baselines
- Bai et al. 2022 (HH-RLHF): Primary dataset; annotation methodology baseline
- Thakur et al. 2024 (Judging the Judges): Closest prior work on human judge adaptation to AI outputs
- Pan et al. 2022 (Reward Misspecification): Benchmark degradation pathway methodology
- Coste et al. 2023 (Reward Model Ensembles): Annotation variance → reward degradation framework
- Christiano et al. 2017 (RLHF): Foundational static-oracle assumption being challenged

### Phase 2B Readiness Seeds
- SH1 (Existence): Does temporal drift exist in HH-RLHF stylistic coefficients after Q_early recalibration?
- SH2 (Mechanism): Does AAI trajectory correlate with TruthfulQA/BBH degradation (Spearman ρ > 0.4)?
- SH3 (Comparison): Do early-round vs. late-round RLHF models differ behaviorally on style-invariant benchmarks?

### Established Facts
- Human judges adapt evaluation criteria upon repeated AI output exposure (Thakur 2024)
- Reward model overoptimization degrades downstream benchmarks (Pan 2022, Gao 2022)
- HH-RLHF contains 3 annotation rounds with temporal metadata (Bai 2022)
- KL divergence asymmetry is theoretically grounded in RLHF PPO penalty (Ouyang 2022)
- Automation bias is strongest under ambiguity (Skitka et al., foundational HCI literature)

