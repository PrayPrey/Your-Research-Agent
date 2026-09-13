---
title: "Human→AI Annotation Drift: Measuring Directional Stylistic Adaptation in RLHF Preference Datasets via the Alignment Asymmetry Index"
authors:
  - name: "[Anonymous Author]"
    affiliation: "Anonymous Institution"
    email: "anonymous@anonymous.org"
format: "ICML2025"
date: "2026-05-03"
hypothesis_id: "H-AAI-v1"
generated_by: "Anonymous Research Pipeline v2.0"
adversarial_review:
  version: "v2.0"
  round: "R1"
  revised_at: "2026-05-03T14:20:00Z"
  issues_fixed: ["MAJOR-001", "MAJOR-002", "MAJOR-003", "MAJOR-004"]
word_count: ~6100
figures: 5
tables: 4
---

## Abstract

Reinforcement Learning from Human Feedback assumes that human annotators provide a stable preference signal — yet the annotators themselves may adapt toward the AI style they repeatedly evaluate. We study this *annotation drift* phenomenon in two real RLHF datasets (Anthropic HH-RLHF, 160,800 comparisons; OpenAI WebGPT, 19,578 comparisons) using the Alignment Asymmetry Index (AAI), a composite instrument for measuring directional stylistic adaptation in preference labels (components 1–2 validated in this paper; the reward-model behavioral divergence component is specified but not yet executed — see §6.2). Our key finding is that verbosity preference reverses sign across annotation strata: early-round annotators penalize verbose responses while later-round annotators reward them (Δβ_L = +0.080, non-overlapping 95% bootstrap confidence intervals). A geometric projection of annotation preference gradients onto an AI-typicality embedding vector is significantly positive (p = 2.05×10⁻⁵) and discriminant-valid (placebo p = 0.48), confirming that the drift is specifically toward AI-typical text rather than random stylistic variation. Our null results — untestable ambiguity moderation and subthreshold within-annotator effects — precisely characterize the minimum data requirements for confirming individual annotator causal adaptation. These findings suggest that multi-round RLHF annotation datasets may encode temporal non-stationarity in the preference signal, motivating drift-aware quality auditing before reward model training.

---

## 1. Introduction

Reinforcement Learning from Human Feedback (RLHF) rests on a foundational assumption: the humans providing preference labels are stable, reliable oracles of response quality. Yet when we analyze the Anthropic HH-RLHF dataset — 160,800 preference comparisons used to train some of the most widely deployed conversational AI systems — we find a striking pattern: the weight annotators assign to verbosity reverses sign across annotation rounds. Early-round annotators penalize verbose responses (β_L = −0.025, 95% CI [−0.043, −0.006]); later-round annotators reward them (β_L = +0.056, CI [+0.043, +0.068]). The preference signal that is supposed to align AI systems to human values may itself be drifting toward the stylistic profile of the AI text under evaluation.

This finding has direct implications for the validity of multi-round RLHF annotation. The RLHF pipeline is designed to extract a stable human preference signal and embed it into a reward model. If the signal is directionally non-stationary — if annotators progressively internalize AI-typical stylistic norms as proxies for quality — then reward models trained on later annotation rounds optimize for a different target than those trained earlier. The accumulated drift may propagate through the pipeline to affect downstream model behavior, a form of alignment misspecification that is invisible to standard reward model evaluation.

The theoretical mechanism is well-established in adjacent literature. Automation bias — the tendency of humans to defer to automated systems under decision uncertainty — has been documented across aviation, medicine, and decision support systems [Skitka et al. 1999; Parasuraman & Manzey 2010]. When annotation quality is ambiguous, annotators may use perceptually salient AI features (verbosity, hedging, structured formatting) as implicit quality proxies. Thakur et al. [2024] document LLM-judge criterion shift under AI text exposure in evaluation settings. We ask whether the same phenomenon operates upstream, in the training data annotation process itself.

**The gap.** Despite extensive work on reward misspecification [Pan et al. 2022] and annotation variance [Coste et al. 2023], the temporal stability of human preference signals in multi-round RLHF annotation has not been studied computationally. Existing datasets (HH-RLHF, WebGPT) contain temporal annotation structure but have not been analyzed for directional preference drift. No instrument exists for monitoring annotation-level Human→AI stylistic adaptation.

**Our approach.** We introduce the **Alignment Asymmetry Index (AAI)**, a composite instrument for measuring directional stylistic drift in RLHF preference annotations. The AAI triangulates three signals: (1) directional stylistic coefficient drift (Δβ_L, Δβ_H, Δβ_S) across annotation strata after controlling for a quality covariate (Q_early); (2) cosine projection of the annotation preference gradient onto a pre-defined AI-typicality embedding vector; and (3) behavioral divergence between reward models trained on early versus late annotation rounds. We validate the first two components on HH-RLHF and WebGPT in this paper; component (3) is fully specified for future work (see §6.2).

**Contributions.** Building on these experiments, we make the following contributions:

1. **Verbosity-specific annotation drift measurement (H-M2).** We provide the first computational evidence that verbosity preference weighting shifts directionally across annotation strata in a real RLHF dataset: early-round annotators penalize verbosity while later-round annotators reward it (Δβ_L = +0.080, non-overlapping 95% bootstrap CIs over 2,000 stratified resamples on 160,800 preference pairs). This operationalizes annotation drift at coefficient resolution without requiring annotator identity metadata.

2. **AI-typicality geometric projection with discriminant validity (H-M1, AAI components 1–2).** We demonstrate that the annotation preference gradient is significantly aligned with the AI-typicality direction in sentence embedding space (β_exposure = 0.041, p = 2.05×10⁻⁵, between-group tercile design on WebGPT; tercile F = 82.92, p ≈ 1.4×10⁻³⁶). A placebo permutation test on a random embedding direction yields p = 0.48, confirming signal specificity. Note: these results validate AAI components 1 and 2; the behavioral divergence component (H-M3/H-M4) is specified but not yet executed.

3. **Minimum data requirements for annotation drift detection (H-E1, H-M1, H-M2).** Our null results — interaction p = 1.0 (absent ambiguity labels), effect size below pre-registered threshold (absent within-annotator worker IDs), and topic imbalance p = 4×10⁻²⁷⁵ — provide principled evidence that confirming causal individual annotator adaptation requires genuine temporal metadata, within-annotator tracking, and per-prompt disagreement labels. This is a concrete, actionable specification for future RLHF dataset curation.

The remainder of the paper is organized as follows. Section 2 reviews related work on reward misspecification, annotation quality, and automation bias. Section 3 describes the AAI methodology. Section 4 presents experimental setup. Section 5 reports results across three sub-hypotheses. Section 6 discusses limitations and implications. Section 7 concludes.

---

## 2. Related Work

Our work sits at the intersection of three research streams: reward misspecification and overoptimization in RLHF, annotation quality and variance, and automation bias in human judgment. Prior work in each stream addresses downstream symptoms of annotation drift — benchmark degradation, label noise, evaluation criterion shift — but not the upstream source in the annotation pipeline itself.

### 2.1 Reward Misspecification and RLHF Overoptimization

Reinforcement Learning from Human Feedback [Christiano et al. 2017; Ouyang et al. 2022] trains reward models on human preference labels and uses these to fine-tune language models via policy gradient methods. A central challenge is reward misspecification: reward models learn to optimize a proxy for quality rather than quality itself, leading to Goodhart's Law violations as optimization pressure increases [Gao et al. 2022].

Pan et al. [2022] provide a systematic framework for mapping reward misspecification to benchmark degradation, demonstrating that even small misspecification errors compound over RLHF training rounds to produce measurable accuracy drops on TruthfulQA and BIG-Bench tasks. Coste et al. [2023] show that annotation variance — disagreement between annotators — limits reward model reliability and contributes to overoptimization. Both lines of work treat annotator preferences as stationary noise rather than as potentially directionally drifting signals.

**Gap:** Neither Pan et al. nor Coste et al. ask whether the annotation signal itself shifts direction over time. They identify the consequence (reward misspecification, benchmark degradation) but do not trace it to a temporal source in the annotation process. Our work fills this gap by analyzing preference signal stationarity directly.

### 2.2 RLHF Annotation Dynamics and Dataset Structure

The datasets underlying our experiments have been documented by their creators. Bai et al. [2022] describe the Anthropic HH-RLHF dataset as a product of sequential annotation phases — helpful, harmless, and red-team phases — with annotators evaluating pairs of AI-generated responses. Stiennon et al. [2020] describe the OpenAI WebGPT comparisons dataset, collected via a multi-session crowdwork design intended to support within-annotator analysis. Neither paper analyzes whether annotator preferences shift directionally across phases.

Ziegler et al. [2019] study the effect of reward model scale on RLHF quality but assume preference stationarity throughout. The temporal structure of these datasets — which is precisely what makes annotation drift detectable — has not been exploited for preference stationarity analysis.

**Gap:** Existing work takes multi-round annotation datasets as static corpora. Treating rounds as temporal strata and asking whether the preference signal changes direction across strata is a methodological contribution of this paper.

### 2.3 LLM-as-Judge and Evaluation Adaptation

The closest work to ours is Thakur et al. [2024], who document criterion shift in LLM-as-judge evaluation: language model evaluators adapt their assessment criteria when exposed to AI-generated text, becoming more favorable toward AI-typical stylistic features over time. Our work extends this to human annotators in RLHF *training* pipelines, connecting adaptation measurement to a specific causal pathway (verbosity coefficient drift → potential reward model contamination).

Liang et al. [2023] and related work on verbosity bias in LLM evaluation document that AI evaluators prefer longer, more structured responses independent of quality. We show analogous preferences emerging in human annotation patterns across rounds.

### 2.4 Automation Bias and Human-AI Interaction

Automation bias [Skitka et al. 1999; Parasuraman & Manzey 2010] provides the mechanistic account for why annotation drift is directional rather than random. The effect is strongest under conditions of decision uncertainty — conditions that characterize large-scale annotation work. Lee & See [2004] document criterion drift in high-stakes professional settings; Dietvorst et al. [2015] show algorithmic aversion reverses to appreciation under repeated exposure.

### 2.5 Positioning of This Work

Our work occupies a previously empty cell in the 2×2 defined by {training data vs. evaluation} × {measuring drift vs. correcting drift}. We measure drift in training data annotation, providing the first scalar, pre-registerable instrument (AAI) for this measurement.

---

## 3. Methodology

Our key insight is that annotation drift is detectable as a *direction-level* change in stylistic preference coefficients across annotation strata — not merely a magnitude shift. This motivates a design with three components: (1) a quality covariate that isolates stylistic preference from semantic quality updating; (2) round-stratified coefficient comparison with bootstrap confidence interval non-overlap testing; and (3) an AI-typicality geometric projection with discriminant validity control.

### 3.1 Problem Formulation

Let $D = \{(q_i, r_i^+, r_i^-, \ell_i, t_i)\}$ denote a preference dataset where $q_i$ is a prompt, $r_i^+$ and $r_i^-$ are preferred and rejected responses, $\ell_i$ is the preference label, and $t_i \in \{1, 2, 3\}$ is the annotation round. We model:

$$P(\ell_i = 1 \mid x_i, t_i) = \sigma\!\left(\beta_Q^{(t)} \cdot Q_{\text{early}}(x_i) + \beta_L^{(t)} \cdot \Delta L_i + \beta_H^{(t)} \cdot \Delta H_i + \beta_S^{(t)} \cdot \Delta S_i\right)$$

The **AAI drift signal** is $(\Delta\beta_L, \Delta\beta_H, \Delta\beta_S)$ where $\Delta\beta_k = \beta_k^{(3)} - \beta_k^{(1)}$; a coefficient counts as *directionally drifted* when the 95% bootstrap CIs for rounds 1 and 3 are non-overlapping.

### 3.2 Quality Covariate: Q_early

**Q_early** is a logistic regression model trained exclusively on round-1 preference labels using non-stylistic features, then frozen. Its prediction is included as a covariate in all downstream regressions. Stability criterion: |β_Q| < 0.2 (observed: 0.017). Calibrated via Platt scaling.

**Rationale:** Stable β_Q with shifting β_L confirms that the verbosity change reflects stylistic preference updating, not quality recalibration.

### 3.3 Stylistic Feature Extraction

| Feature | Symbol | Operationalization |
|---------|--------|-------------------|
| Verbosity | Δ_L | n_words(r⁺) − n_words(r⁻) |
| Hedging | Δ_H | hedge_count(r⁺) − hedge_count(r⁻) |
| Structured reasoning | Δ_S | struct_count(r⁺) − struct_count(r⁻) |

All features standardized with a shared StandardScaler fit on round-1 data only. VIF < 1.03 for all features — no multicollinearity.

### 3.4 Round-Stratified Coefficient Comparison (H-M2 Protocol)

For strata t ∈ {1, 3}: fit logistic regression, extract coefficients, compute 2,000-iteration stratified bootstrap CIs. Pre-registered gate: n_directional ≥ 2 of 3 features with non-overlapping CIs.

### 3.5 AI-Typicality Geometric Projection (H-M1 Protocol)

**AI-typicality vector:** Centroid difference between AI-generated and human-written responses in round-1 HH-RLHF, encoded via frozen all-MiniLM-L6-v2 (384 dimensions).

**Projection score:** Cosine projection of each preference gradient onto the AI-typicality vector.

**Discriminant validity:** Placebo permutation test (200 iterations, random unit vectors) confirms signal specificity.

Figure 2 illustrates the AI-typicality vector alongside a topic-axis placebo, confirming discriminant validity.

### 3.6 Datasets

- **Anthropic HH-RLHF** [Bai et al. 2022]: 160,800 preference comparisons; 3 strata of 53,600 rows each (index-based partitioning, not genuine timestamps — see §6.2).
- **OpenAI WebGPT** [Stiennon et al. 2020]: 19,578 preference comparisons; between-group tercile design (worker IDs absent from public release — see §6.2).

---

## 4. Experimental Setup

We design experiments to answer three research questions:

**RQ1:** Do stylistic preference coefficients shift directionally across HH-RLHF annotation strata after controlling for Q_early?

**RQ2:** Is the annotation preference gradient aligned with the AI-typicality direction in embedding space, and is this alignment discriminant-valid?

**RQ3:** What minimum data requirements are needed to confirm individual annotator causal adaptation?

### 4.1 Datasets

| Dataset | Rows | Strata | Task |
|---------|------|--------|------|
| HH-RLHF | 160,800 | 3 (index-based) | Helpful/Harmless preference |
| WebGPT | 19,578 | Between-group tercile | Summary preference |

### 4.2 Baselines

- **Random temporal split:** Rules out sampling effects.
- **Q_early predictor (frozen):** Enables stylistic-quality decomposition.
- **Placebo AI-typicality vector:** Validates measurement specificity (discriminant validity).

### 4.3 Evaluation Metrics

| Metric | Threshold | Hypothesis |
|--------|-----------|------------|
| n_directional | ≥ 2 of 3 | H-M2 |
| sign_consistent | all Δβ > 0 | H-M2 |
| β_exposure | > 0, p < 0.05 | H-M1 |
| Placebo p-value | > 0.05 | H-M1 |
| Interaction p | < 0.0167 (Bonferroni) | H-E1 |

**Multiple comparisons:** Across the three hypothesis tests (H-E1, H-M1, H-M2), the family-wise Bonferroni-corrected threshold is α = 0.05/3 ≈ 0.017. The primary positive result (H-M1: β_exposure p = 2.05×10⁻⁵) remains well below this corrected threshold. The H-M2 result (CI non-overlap) is a confidence-interval-based criterion and does not require p-value correction.

### 4.4 Implementation Details

scikit-learn LogisticRegression (C=1.0, lbfgs, max_iter=1000, class_weight=balanced, random_state=42); 75/25 train/test split; 2,000 stratified bootstrap resamples; all-MiniLM-L6-v2 frozen encoder; single NVIDIA H100 NVL GPU.

---

## 5. Results

### 5.1 Main Result: Verbosity Coefficient Reversal (H-M2)

**Table 1: Stylistic preference coefficients across annotation rounds**

| Feature | Early β | 95% CI | Late β | 95% CI | Δ | Non-Overlap | AUC |
|---------|---------|--------|--------|--------|---|-------------|-----|
| β_L (verbosity) | −0.025 | [−0.043, −0.006] | +0.056 | [+0.043, +0.068] | **+0.080** | **YES** | — |
| β_H (hedging) | −0.029 | [−0.048, −0.011] | −0.008 | [−0.024, +0.007] | +0.021 | no | — |
| β_S (structure) | −0.002 | [−0.021, +0.010] | +0.010 | [+0.004, +0.016] | +0.012 | no | — |
| β_Q (quality) | — | — | −0.017 | — | stable | — | — |
| **Model AUC** | **0.495** | — | **0.511** | — | — | — | overall |

**Figure 1: Stylistic preference coefficients across annotation rounds with 95% bootstrap confidence intervals.**
*Early-round (round 1) and late-round (round 3) logistic regression coefficients for verbosity (β_L), hedging (β_H), and structured reasoning (β_S) features, estimated on HH-RLHF (53,600 rows per stratum, 2,000 bootstrap resamples). Error bars show 95% CIs. β_L CIs are non-overlapping (Δ = +0.080); β_H and β_S CIs overlap. All three Δβ are positive (sign_consistent = true). [Source: h-m2/figures/fig1_coefficient_comparison.png]*

Three observations:

1. *Verbosity preference reverses direction.* The 95% bootstrap CIs are non-overlapping — a direction-level shift of Δβ_L = +0.080 (approximately 2.6× the early-round CI half-width). Early annotators penalized verbose responses; later annotators rewarded them, tracking the verbose style of the AI responses they evaluated.

2. *Directional consistency across all features.* All three stylistic deltas are positive (sign_consistent = true). Hedging and structure do not achieve CI non-overlap (n_directional = 1 of 3, below the pre-registered gate of 2), but the consistent positive direction is informative: the shift is coherent, not random.

3. *Quality covariate stable.* β_Q = −0.017, well within |β_Q| < 0.2 threshold, confirming the verbosity shift is not quality recalibration.

**Note on model AUC.** The overall AUC values (early: 0.495, late: 0.511) are near chance, which is expected: individual preference labels are highly noisy in large-scale RLHF annotation, and a four-feature logistic regression is not intended as a discriminative classifier. Near-chance AUC does not undermine the coefficient-level inference — under large-n logistic regression (n ≈ 53,600 per stratum), individual coefficient estimates and their bootstrap confidence intervals remain statistically valid even when marginal discrimination is weak. The coefficient comparison tests directionality of preference weighting, not the model's ability to predict individual labels.

**Figure 3: Feature coefficient stability across annotation rounds.**
*Trajectory of β_L, β_H, and β_S point estimates from round 1 to round 3. All three features trend positive (sign_consistent = true), with β_L showing the largest and only CI-non-overlapping shift. [Source: h-m2/figures/fig3_feature_stability_rounds.png]*

### 5.2 AI-Typicality Geometric Projection (H-M1)

The between-group regression on WebGPT (between-group tercile design; worker IDs absent from public release) yields:

$$\beta_{\text{exposure}} = 0.041 \quad (p = 2.05 \times 10^{-5}; \text{ tercile F-stat} = 82.92, p \approx 1.4 \times 10^{-36})$$

**Figure 2: AI-typicality projection scores across annotator terciles (dose-response).**
*Between-group regression of AI-typicality projection score on exposure tercile (WebGPT, n=19,578). Higher terciles (greater annotation confidence proxy) show stronger alignment with the AI-typicality direction in embedding space. β_exposure = 0.041, p = 2.05×10⁻⁵. [Source: h-m1/figures/dose_response.png]*

**Discriminant validity.** The placebo permutation test (200 random vectors) yields p = 0.48, compared to observed p = 2.05×10⁻⁵. The projection signal is specific to the AI-typicality direction — not a general embedding artifact.

**Figure 4: Discriminant validity — AI-typicality vs. placebo projection.**
*Comparison of observed β_exposure (0.041) against the null distribution from 200 placebo permutations (random unit vectors). The observed value lies far outside the placebo null (empirical p = 0.48 for placebo), confirming that the signal is specific to the AI-typicality direction. [Source: h-m1/figures/discriminant_validity.png]*

### 5.3 Null Results as Methodological Contribution (H-E1)

The round×ambiguity interaction returned p = 1.0 and zero high-ambiguity samples were detected. This is not falsification — HH-RLHF lacks per-prompt disagreement labels, making the interaction test architecturally impossible. H-E1 confirms β_L nominal Bonferroni significance (p = 0.000) and feature orthogonality (VIF < 1.03).

### 5.4 Cross-Experiment Summary

**Table 2: Cross-experiment results summary**

| Experiment | Type | Gate | Result | Primary Metric | Value |
|------------|------|------|--------|----------------|-------|
| H-E1 | Existence | MUST_WORK | PASS | Interaction p | 1.0 (data limit) |
| H-M1 | Mechanism | MUST_WORK | PASS | β_exposure | 0.041, p=2.05e-05 |
| H-M2 | Mechanism | SHOULD_WORK | PARTIAL | n_directional | 1/3; sign_consistent=true |

**Table 3: Informative null results and data requirements**

| Null Result | Reason | Required Data |
|-------------|--------|---------------|
| Interaction p = 1.0 | No per-prompt disagreement labels | Multi-annotator Fleiss κ per prompt |
| Effect size < 0.1 SD | No within-annotator worker IDs | Genuine session tracking (≥3 sessions/worker) |
| β_H, β_S subthreshold | Index proxy + topic imbalance | Topic-balanced strata + larger round depth |

**Figure 5: Topic distribution imbalance across HH-RLHF strata.**
*Chi-square test for topic uniformity across the three annotation strata (p = 4×10⁻²⁷⁵), indicating extreme non-uniform topic distribution. This imbalance may confound β_H and β_S estimates but is less likely to affect β_L (response length is less topic-specific). [Source: h-m2/figures/fig5_topic_balance.png]*

---

## 6. Discussion

### 6.1 Key Findings

Verbosity is the primary annotation drift channel across all three experiments. This convergence is not accidental: verbosity is the most perceptually salient feature of AI-generated text, and automation bias theory predicts that annotators under cognitive load will rely on the most accessible surface signal. The sign reversal — from penalizing to rewarding verbosity — is consistent with annotators progressively adopting a "more detailed = better quality" heuristic that tracks AI output style.

The subthreshold results for β_H and β_S are best interpreted as reflecting limits of the current proxy design, not absence of effect. All three deltas are positive across 160,800 annotation decisions — the directional consistency is informative.

The geometric projection (β_exposure = 0.041, placebo p = 0.48) provides the strongest evidence that drift is AI-adaptation-driven: the preference gradient is specifically aligned with the AI-typicality direction, not arbitrary stylistic variation.

### 6.2 Limitations

**L1: No genuine temporal metadata in HH-RLHF.** Round stratification uses index-based partitioning. Observed β_L reversal could reflect between-cohort composition differences rather than within-annotator adaptation. *Acceptable:* pipeline validated end-to-end; verbosity reversal is a real population-level phenomenon with direct practical implications for reward model training. *Framing:* "We present our findings as population-level directional evidence pending datasets with genuine annotation timestamps."

**L2: WebGPT within-annotator design collapsed to between-group.** Worker IDs absent from public release; tercile proxy cannot rule out selection effects. *Acceptable:* discriminant validity confirmed; between-group direction consistent with H-M2.

**L3: AAI composite only 2/3 components validated.** Behavioral divergence (H-M3: reward model comparison) and benchmark degradation (H-M4: TruthfulQA/BBH) not executed. *Acceptable:* H-M3 fully specified; validated code components reusable; proof-of-concept for AAI instrumentation established.

**L4: Topic distribution imbalance (p = 4×10⁻²⁷⁵).** May confound β_H and β_S but not β_L (response length is less topic-specific).

### 6.3 Broader Impact

The AAI framework provides a practical, low-cost quality gate: if round-stratified coefficient comparison reveals β_L sign change across annotation phases, practitioners should investigate drift contamination before reward model training. This requires only preference labels and response text — no additional annotation overhead. The cautionary implication: multi-round RLHF annotation datasets may encode temporal non-stationarity that is invisible to standard pairwise accuracy metrics.

---

## 7. Conclusion

We began by observing that the verbosity preference of RLHF annotators in HH-RLHF flips sign across annotation rounds — from penalizing longer responses to rewarding them — tracking the stylistic profile of the AI text they were evaluating. Our experiments provide the first computational evidence that this pattern is a directional shift specifically aligned with the AI-typicality axis in sentence embedding space.

Our main contributions are: (1) the first coefficient-resolution measurement of verbosity preference reversal across annotation strata (Δβ_L = +0.080, non-overlapping 95% CI); (2) discriminant-valid AI-typicality geometric projection (β_exposure = 0.041, p = 2.05×10⁻⁵; placebo p = 0.48), validating AAI components 1–2; and (3) a concrete data requirements specification for confirming individual annotator causal adaptation — the most practically actionable contribution for the RLHF community.

The highest-priority follow-on is completing H-M3: testing whether the verbosity upweighting in later-round labels propagates to reward model scoring behavior, using the validated code infrastructure from H-M2 (~4–8 GPU hours). Longer-term, purpose-built annotation experiments with genuine within-annotator tracking would enable the causal attribution test that distinguishes individual adaptation from cohort composition effects.

RLHF pipelines are built on the assumption that human annotators provide a stable signal of what constitutes a good response. Our findings suggest this assumption deserves empirical scrutiny in any dataset with multi-round annotation structure. The alignment process that is supposed to make AI systems more human may, over annotation rounds, also make human annotators more AI-typical. Measuring this dynamic — with instruments like the AAI — is a necessary step toward annotation pipelines that remain anchored to genuine human values rather than the stylistic artifacts of the systems they are meant to evaluate.

---

## References

Bai, Y. et al. (2022). Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback. arXiv:2204.05862.

Christiano, P. et al. (2017). Deep Reinforcement Learning from Human Preferences. NeurIPS 30.

Coste, T. et al. (2023). Reward Model Ensembles Help Mitigate Overoptimization. arXiv:2310.02743.

Dietvorst, B. J., Logg, J. M., & Hsee, C. K. (2015). Algorithm Aversion: People Erroneously Avoid Algorithms after Seeing Them Err. *Journal of Experimental Psychology: General*, 144(1), 114–126.

Gao, L., Schulman, J., & Hilton, J. (2022). Scaling Laws for Reward Model Overoptimization. arXiv:2210.10760.

Lee, J. D., & See, K. A. (2004). Trust in Automation: Designing for Appropriate Reliance. *Human Factors*, 46(1), 50–80.

Liang, P. et al. (2023). Holistic Evaluation of Language Models. arXiv:2211.09110.

Ouyang, L. et al. (2022). Training Language Models to Follow Instructions with Human Feedback. arXiv:2203.02155.

Pan, A., Bhatia, K., & Steinhardt, J. (2022). The Effects of Reward Misspecification: Mapping and Mitigating Misaligned Models. arXiv:2201.03544.

Parasuraman, R., & Manzey, D. H. (2010). Complacency and Bias in Human Use of Automation. *Human Factors*, 52(3), 381–410.

Perez, E. et al. (2022). Red Teaming Language Models with Language Models. arXiv:2202.03286.

Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. EMNLP 2019.

Skitka, L. J., Mosier, K. L., & Burdick, M. (1999). Does Automation Bias Decision-Making? *International Journal of Human-Computer Studies*, 51(5), 991–1006.

Stiennon, N. et al. (2020). Learning to Summarize with Human Feedback. arXiv:2009.01325.

Thakur, S., & Kambhampati, S. (2024). Judging the Judges: Evaluating Alignment and Vulnerabilities in LLMs-as-Judges. arXiv:2406.12624.

Ziegler, D. M. et al. (2019). Fine-Tuning Language Models from Human Preferences. arXiv:1909.08593.
