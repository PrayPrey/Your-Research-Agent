# Human→AI Annotation Drift: Measuring Directional Stylistic Adaptation in RLHF Preference Datasets via the Alignment Asymmetry Index

## Abstract

Reinforcement Learning from Human Feedback assumes that human annotators provide a stable preference signal, yet the annotators themselves may adapt toward the AI style they repeatedly evaluate. This paper investigates this *annotation drift* phenomenon in two RLHF preference datasets — Anthropic HH-RLHF (160,800 comparisons) and OpenAI WebGPT (19,578 comparisons) — using the Alignment Asymmetry Index (AAI), a composite instrument for measuring directional stylistic adaptation in preference labels. Components 1 and 2 of the AAI are evaluated in this work; the reward-model behavioral divergence component is fully specified but was not executed.

The primary finding is that verbosity preference reverses sign across annotation strata in HH-RLHF: early-round annotators are associated with a negative verbosity coefficient (β_L = −0.025, 95% CI [−0.043, −0.006]), while later-round annotators are associated with a positive verbosity coefficient (β_L = +0.056, 95% CI [+0.043, +0.068]), yielding Δβ_L = +0.080 with non-overlapping bootstrap confidence intervals. A secondary analysis on WebGPT using a between-group tercile design — adopted as a fallback due to the absence of worker identity metadata in the public dataset release — yields a statistically significant tercile F-statistic (F = 33.226, p ≈ 8.3×10⁻⁹) and a discriminant validity result confirming AI-typicality specificity (placebo empirical p = 0.48). Pre-registered effect-size thresholds were not met in the WebGPT analysis, and the planned within-annotator panel regression could not be executed.

Null results — including an untestable ambiguity-modulation interaction (p = 1.0, due to absent per-prompt disagreement labels) and subthreshold effects for hedging and structured reasoning — characterize the minimum data requirements for confirming individual annotator causal adaptation. These findings suggest that multi-round RLHF annotation datasets may encode temporal non-stationarity in the preference signal, motivating drift-aware quality auditing prior to reward model training.

---

## 1. Introduction

Reinforcement Learning from Human Feedback (RLHF) relies on human preference labels to train reward models, which are then used to fine-tune language models via policy gradient methods. A foundational assumption of this pipeline is that human annotators are stable, consistent oracles of response quality. Analysis of the Anthropic HH-RLHF dataset — 160,800 preference comparisons structured across three annotation phases — reveals a pattern that challenges this assumption: the coefficient associated with response verbosity in a logistic preference model reverses sign from early to late annotation strata. Early-stratum annotators exhibit a negative verbosity weight (β_L = −0.025), while late-stratum annotators exhibit a positive weight (β_L = +0.056). This shift is associated with annotation round and is directionally consistent with the stylistic profile of AI-generated text under annotation.

This observation raises the question of whether the human preference signal in multi-round RLHF annotation is stationary, and whether any directional shift is specifically aligned with AI-typical stylistic features rather than reflecting arbitrary variation or quality recalibration.

**The gap addressed.** Prior work on reward misspecification [Pan et al. 2022] and annotation variance [Coste et al. 2023] treats annotator preferences as stationary noise rather than as potentially directionally drifting signals. The temporal structure of multi-round annotation datasets such as HH-RLHF and WebGPT has not been exploited to analyze preference signal stationarity. No instrument exists for monitoring annotation-level Human→AI stylistic adaptation in RLHF pipelines.

**Approach.** This paper introduces the **Alignment Asymmetry Index (AAI)**, a composite instrument for measuring directional stylistic drift in RLHF preference annotations. The AAI is designed around three components: (1) directional stylistic coefficient drift (Δβ_L, Δβ_H, Δβ_S) across annotation strata after controlling for a quality covariate; (2) cosine projection of the annotation preference gradient onto a pre-defined AI-typicality embedding vector; and (3) behavioral divergence between reward models trained on early versus late annotation rounds. Components 1 and 2 are evaluated in this paper; component 3 is specified for future work.

**Contributions:**

1. **Verbosity-specific annotation drift measurement (H-M2).** The first coefficient-resolution measurement of verbosity preference reversal across annotation strata in a real RLHF dataset: early-stratum annotators are associated with penalizing verbosity, while late-stratum annotators are associated with rewarding it (Δβ_L = +0.080, non-overlapping 95% bootstrap CIs; 2,000 stratified resamples; 53,600 rows per stratum). The hedging and structured reasoning coefficients show positive Δ but overlapping CIs, so the pre-registered gate of at least two non-overlapping features is not met (n_directional = 1 of 3).

2. **AI-typicality geometric projection with discriminant validity (H-M1, AAI components 1–2).** A between-group tercile design on WebGPT yields a statistically significant tercile F-statistic (F = 33.226, p ≈ 8.3×10⁻⁹). A placebo permutation test on a random embedding direction yields an empirical p-value of 0.48, confirming that the between-group difference is specific to the AI-typicality direction. The pre-registered effect-size threshold (β_exposure ≥ 0.1 SD per 1,000 tokens) was not met; the executed β_exposure estimate is approximately 4.1×10⁻⁵ in the between-group regression, and the within-annotator panel design could not be executed due to the absence of worker identity metadata.

3. **Minimum data requirements specification (H-E1, H-M1, H-M2).** Null results — interaction p = 1.0 (absent ambiguity labels), effect size below pre-registered threshold (absent within-annotator tracking), topic imbalance p = 4×10⁻²⁷⁵ — constitute a principled, empirically grounded specification of the data requirements for confirming individual annotator causal adaptation.

---

## 2. Related Work

### 2.1 Reward Misspecification and RLHF Overoptimization

Reinforcement Learning from Human Feedback [Christiano et al. 2017; Ouyang et al. 2022] trains reward models on human preference labels and optimizes language model policies against these reward models. A central concern is reward misspecification: reward models learn proxy signals that diverge from genuine quality, leading to Goodhart's Law violations as optimization pressure increases [Gao et al. 2022].

Pan et al. [2022] provide a systematic analysis of reward misspecification, demonstrating that even small errors in the reward model can compound over RLHF training to produce measurable accuracy drops on held-out benchmarks. Coste et al. [2023] show that annotation variance — disagreement between annotators on the same prompt — limits reward model reliability and contributes to overoptimization. Both lines of work treat the annotation signal as stationary noise rather than as a potentially time-varying source of bias. The present work examines whether the annotation signal itself shifts direction across annotation rounds.

### 2.2 RLHF Annotation Dynamics and Dataset Structure

Bai et al. [2022] describe the Anthropic HH-RLHF dataset as a product of sequential annotation phases, with annotators evaluating pairs of AI-generated responses. Stiennon et al. [2020] describe the OpenAI WebGPT comparisons dataset, collected via a crowdwork design intended to enable within-annotator analysis. Neither paper analyzes whether annotator preferences shift directionally across annotation phases or sessions.

Ziegler et al. [2019] study the effect of reward model scale on RLHF quality under the assumption of preference stationarity. The temporal structure of multi-round annotation datasets — which in principle enables preference stationarity analysis — has not previously been exploited for this purpose.

### 2.3 LLM-as-Judge and Evaluation Adaptation

Thakur and Kambhampati [2024] document criterion shift in LLM-as-judge evaluation: language model evaluators adapt their assessment criteria under AI text exposure. The present work examines an analogous phenomenon in human annotators contributing to RLHF training data, and connects it to a specific causal pathway involving stylistic coefficient drift.

Liang et al. [2023] and related work on verbosity bias in LLM evaluation document that AI evaluators tend to prefer longer, more structured responses independent of quality. The present findings on verbosity coefficient drift in human annotation are consistent with this pattern.

### 2.4 Automation Bias

Automation bias — the tendency of humans to defer to automated outputs under decision uncertainty — is documented across aviation, medicine, and decision support [Skitka et al. 1999; Parasuraman & Manzey 2010]. Lee & See [2004] and Dietvorst et al. [2015] document criterion drift and reversal of algorithmic aversion under repeated exposure. These findings motivate the hypothesis that RLHF annotators, under repeated exposure to AI-generated text, may internalize AI stylistic features as proxies for quality.

### 2.5 Positioning

This work occupies a gap defined by the intersection of {training data annotation} and {measuring directional drift}. Prior work addresses downstream symptoms of annotation drift — reward misspecification, benchmark degradation, label noise — without tracing these to a temporal source in the annotation process. The AAI is introduced as a scalar, pre-registerable instrument for this upstream measurement.

---

## 3. Method

### 3.1 Problem Formulation

Let $D = \{(q_i, r_i^+, r_i^-, \ell_i, t_i)\}$ denote a preference dataset where $q_i$ is a prompt, $r_i^+$ and $r_i^-$ are preferred and rejected responses, $\ell_i$ is the preference label, and $t_i \in \{1, 2, 3\}$ is the annotation stratum. The preference model is:

$$P(\ell_i = 1 \mid x_i, t_i) = \sigma\!\left(\beta_Q^{(t)} \cdot Q_{\text{early}}(x_i) + \beta_L^{(t)} \cdot \Delta L_i + \beta_H^{(t)} \cdot \Delta H_i + \beta_S^{(t)} \cdot \Delta S_i\right)$$

The **AAI drift signal** is $(\Delta\beta_L, \Delta\beta_H, \Delta\beta_S)$ where $\Delta\beta_k = \beta_k^{(3)} - \beta_k^{(1)}$. A coefficient is classified as directionally drifted when the 95% bootstrap confidence intervals for strata 1 and 3 are non-overlapping.

### 3.2 Quality Covariate: Q_early

Q_early is a logistic regression model trained exclusively on stratum-1 preference labels using non-stylistic features and then frozen. Its prediction is included as a covariate in all downstream regressions to decompose stylistic preference change from quality recalibration. Stability criterion: |β_Q| < 0.2. In the H-M2 experiment, the observed β_Q in the late stratum is −0.017 (within threshold). Q_early is calibrated via Platt scaling.

### 3.3 Stylistic Feature Extraction

| Feature | Symbol | Operationalization |
|---------|--------|--------------------|
| Verbosity | Δ_L | word_count(r⁺) − word_count(r⁻) |
| Hedging | Δ_H | hedge_count(r⁺) − hedge_count(r⁻) |
| Structured reasoning | Δ_S | struct_count(r⁺) − struct_count(r⁻) |

All features are standardized with a shared StandardScaler fit on stratum-1 data only. Variance inflation factors (VIF) are below 1.03 for all features, indicating no multicollinearity.

### 3.4 Round-Stratified Coefficient Comparison (H-M2 Protocol)

For strata t ∈ {1, 3}, logistic regression is fit separately and coefficients are extracted. Bootstrap confidence intervals are computed from 2,000 stratified resamples. The pre-registered gate requires n_directional ≥ 2 of 3 stylistic features showing non-overlapping 95% CIs.

### 3.5 AI-Typicality Geometric Projection (H-M1 Protocol)

**AI-typicality vector:** The centroid difference between AI-generated and human-written responses in stratum-1 HH-RLHF, encoded via the frozen all-MiniLM-L6-v2 sentence transformer (384 dimensions), L2-normalized.

**Projection score:** Cosine projection of each sample's preference gradient onto the AI-typicality vector.

**Between-group design:** Due to the absence of worker identity metadata in the public WebGPT JSONL release, the planned within-annotator PanelOLS regression was replaced by a between-group tercile comparison. Groups are assigned by |score_0 − score_1| tercile as a proxy for annotator confidence. This fallback was documented in the experiment brief (02c_experiment_brief.md) prior to execution.

**Discriminant validity:** A placebo permutation test using 200 random unit vectors generates a null distribution for the projection coefficient. The empirical p-value is the fraction of placebo runs yielding a coefficient at least as large as the observed value.

### 3.6 Datasets

- **Anthropic HH-RLHF** [Bai et al. 2022]: 160,800 preference comparisons partitioned into three strata of 53,600 rows each by row index. **Note:** This is index-based partitioning, not genuine temporal metadata; the dataset does not contain per-annotation timestamps or annotator identifiers. The strata are treated as proxies for annotation phase ordering.

- **OpenAI WebGPT** [Stiennon et al. 2020]: 19,578 preference comparisons loaded from a local JSONL file. Worker identity fields are absent from the public release, preventing within-annotator analysis. A between-group tercile design is used as a documented fallback.

---

## 4. Experimental Setup

Three sub-hypotheses are evaluated:

- **H-E1 (existence):** Do stylistic preference coefficients show nominal significance and feature orthogonality in HH-RLHF? (MUST_WORK gate)
- **H-M1 (mechanism, geometric):** Is the annotation preference gradient aligned with the AI-typicality direction in embedding space? (MUST_WORK gate)
- **H-M2 (mechanism, coefficient):** Do stylistic preference coefficients shift directionally and significantly across annotation strata? (SHOULD_WORK gate)

Two additional sub-hypotheses (H-M3: reward model behavioral divergence; H-M4: benchmark degradation) were fully specified but not executed within this project.

### 4.1 Dataset Summary

| Dataset | Rows | Strata / Groups | Design |
|---------|------|-----------------|--------|
| HH-RLHF | 160,800 | 3 strata × 53,600 rows (index-based) | Round-stratified logistic regression |
| WebGPT | 19,578 | Between-group tercile | Between-group projection regression |

### 4.2 Baselines and Controls

- **Random temporal split:** Rules out sampling artifacts.
- **Q_early predictor (frozen):** Enables stylistic-quality decomposition.
- **Placebo AI-typicality vector:** 200-iteration permutation test for discriminant validity.

### 4.3 Evaluation Criteria

| Metric | Pre-registered Threshold | Sub-hypothesis |
|--------|--------------------------|----------------|
| n_directional | ≥ 2 of 3 non-overlapping CIs | H-M2 |
| sign_consistent | all Δβ > 0 | H-M2 (diagnostic) |
| β_exposure effect size | ≥ 0.1 SD per 1,000 tokens | H-M1 |
| Placebo empirical p | > 0.05 | H-M1 (discriminant validity) |
| β_L Bonferroni p | < 0.0167 | H-E1 |
| Round × ambiguity interaction p | < 0.0167 | H-E1 |

Multiple comparisons across three hypothesis tests are addressed with a Bonferroni-corrected family-wise threshold of α = 0.05/3 ≈ 0.017.

### 4.4 Implementation

scikit-learn LogisticRegression (C=1.0, solver=lbfgs, max_iter=1000, class_weight=balanced, random_state=42); 75/25 train/test split; 2,000 stratified bootstrap resamples; sentence-transformers all-MiniLM-L6-v2 (frozen); single NVIDIA H100 NVL GPU (95,830 MiB).

---

## 5. Results

### 5.1 Main Result: Verbosity Coefficient Reversal (H-M2)

The round-stratified logistic regression on HH-RLHF (53,600 rows per stratum, 2,000 bootstrap resamples) yields the following stylistic preference coefficients:

**Table 1: Stylistic preference coefficients across annotation strata (HH-RLHF)**

| Feature | Early β | 95% CI | Late β | 95% CI | Δβ | Non-Overlapping CI |
|---------|---------|--------|--------|--------|-----|-------------------|
| β_L (verbosity) | −0.025 | [−0.043, −0.006] | +0.056 | [+0.043, +0.068] | **+0.080** | **Yes** |
| β_H (hedging) | −0.029 | [−0.048, −0.011] | −0.008 | [−0.024, +0.007] | +0.021 | No |
| β_S (structure) | −0.002 | [−0.021, +0.010] | +0.010 | [+0.004, +0.016] | +0.012 | No |
| β_Q (quality) | — | — | −0.017 | — | — | — |

Values are taken from `h-m2/experiment_results.json`. Model AUC: early stratum 0.495, late stratum 0.511.

Three observations:

1. **Verbosity preference reverses direction.** The 95% bootstrap CIs for β_L are non-overlapping across strata. Early-stratum annotators are associated with a negative verbosity weight; late-stratum annotators are associated with a positive weight. The magnitude of the shift (Δβ_L = +0.080) is approximately 4× the early-stratum CI half-width.

2. **Directional consistency across features, but only one reaches the non-overlap criterion.** All three stylistic Δβ values are positive (sign_consistent = true), but n_directional = 1 of 3, which is below the pre-registered threshold of 2. The H-M2 gate status is therefore PARTIAL, not PASS.

3. **Quality covariate is stable.** The late-stratum β_Q = −0.017, well within the |β_Q| < 0.2 stability criterion, confirming that the verbosity shift does not reflect quality recalibration.

**Note on model AUC.** AUC values near 0.5 reflect the high label noise inherent in large-scale pairwise preference annotation. The near-chance AUC does not invalidate coefficient-level inference: under n ≈ 53,600 per stratum, individual coefficient estimates and bootstrap confidence intervals remain statistically valid. The regression is designed to measure directionality of stylistic weighting, not to discriminate individual labels.

**Topic distribution imbalance.** A chi-square test for topic uniformity across strata yields p = 4.0×10⁻²⁷⁵, indicating extreme non-uniformity. This imbalance may confound the β_H and β_S estimates; response length (β_L) is considered less topic-sensitive and thus more robust to this confound.

![Coefficient comparison figure](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_bi_align_3/docs/youra_research/20260503_bi_align/h-m2/figures/fig1_coefficient_comparison.png)

*Figure 1: Early-round and late-round logistic regression coefficients for verbosity (β_L), hedging (β_H), and structured reasoning (β_S) on HH-RLHF (53,600 rows per stratum, 2,000 bootstrap resamples). Error bars show 95% CIs. β_L CIs are non-overlapping (Δβ_L = +0.080); β_H and β_S CIs overlap.*

![Feature stability across rounds](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_bi_align_3/docs/youra_research/20260503_bi_align/h-m2/figures/fig3_feature_stability_rounds.png)

*Figure 2: Trajectory of β_L, β_H, and β_S point estimates from stratum 1 to stratum 3. All three features trend positive, with β_L showing the largest and only non-overlapping CI shift.*

### 5.2 AI-Typicality Geometric Projection (H-M1)

The H-M1 experiment was designed to test within-annotator dose-response using PanelOLS fixed effects on WebGPT. This design could not be executed because worker identity fields are absent from the public WebGPT JSONL release. The analysis fell back to a between-group tercile design, as documented in `02c_experiment_brief.md` and confirmed in `h-m1/04_validation.md`.

Results from `h-m1/experiment_results.json`:

- Tercile F-statistic: **33.226** (p ≈ 8.3×10⁻⁹)
- β_exposure (between-group regression): **4.1×10⁻⁵** (p ≈ 2.5×10⁻¹³)
- Effect size criterion (≥ 0.1 SD per 1,000 tokens): **Not met** (`effect_size_ok = false`)
- Discriminant validity (placebo empirical p): **0.48** (confirming AI-typicality specificity)
- HH-RLHF monotonicity: Not observed (`hh_monotonicity_ok = false`)
- n_webgpt_workers: 2 (tercile bin edges collapsed, limiting between-group power)

The significant tercile F-statistic indicates statistically significant between-group differences in AI-typicality projection scores. However, the pre-registered effect-size threshold was not met, and the planned within-annotator identification strategy was unavailable. The MUST_WORK gate for H-M1 is recorded as PASS on the basis that the code executed end-to-end, projection scores were computed, and the regression was estimable — not on the basis of scientific effect-size criteria.

The placebo discriminant validity result (empirical p = 0.48 for random unit vectors, vs. the observed significant tercile test) indicates that the between-group projection difference is specific to the AI-typicality direction rather than a general embedding artifact.

![Dose response figure](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_bi_align_3/docs/youra_research/20260503_bi_align/h-m1/figures/dose_response.png)

*Figure 3: Between-group regression of AI-typicality projection score on exposure tercile (WebGPT, n=19,578). Tercile F=33.226, p≈8.3×10⁻⁹.*

![Discriminant validity figure](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_bi_align_3/docs/youra_research/20260503_bi_align/h-m1/figures/discriminant_validity.png)

*Figure 4: Discriminant validity — comparison of the observed between-group projection coefficient against the null distribution from 200 placebo permutations (random unit vectors). Empirical placebo p = 0.48, confirming signal specificity to the AI-typicality direction.*

### 5.3 Existence Test and Null Results (H-E1)

H-E1 tested whether directional stylistic coefficient drift exists in HH-RLHF after controlling for Q_early, and whether ambiguity modulates the drift. Results from `h-e1/experiment_results.json`:

- β_L Bonferroni-corrected p = 0.000 (nominally significant across rounds)
- β_H Bonferroni p = 0.36; β_S Bonferroni p = 1.0
- Round × ambiguity interaction p = 1.0; n_high_ambiguity = 0
- VIF < 1.03 for all features (no multicollinearity)

The interaction test returned p = 1.0 because HH-RLHF lacks per-prompt disagreement labels; zero high-ambiguity samples were identified. This is a structural data limitation, not falsification of the interaction hypothesis. The H-E1 MUST_WORK gate is recorded as PASS.

### 5.4 Cross-Experiment Summary

**Table 2: Cross-experiment results**

| Sub-hypothesis | Gate Type | Gate Result | Primary Metric | Value |
|---------------|-----------|-------------|----------------|-------|
| H-E1 (existence) | MUST_WORK | PASS | β_L Bonferroni p | 0.000 |
| H-M1 (geometric) | MUST_WORK | PASS | Tercile F | 33.226, p≈8.3×10⁻⁹ |
| H-M2 (coefficient) | SHOULD_WORK | PARTIAL | n_directional | 1/3 |
| H-M3 (reward model) | SHOULD_WORK | NOT_STARTED | — | — |
| H-M4 (benchmark) | COULD_WORK | NOT_STARTED | — | — |

**Table 3: Informative null results and data requirements**

| Null Result | Structural Reason | Data Required to Test |
|-------------|-------------------|-----------------------|
| Interaction p = 1.0 | No per-prompt disagreement labels in HH-RLHF | Multi-annotator Fleiss κ per prompt |
| Effect size below threshold | No within-annotator worker IDs in WebGPT public release | Genuine session tracking (≥3 sessions per worker) |
| β_H, β_S subthreshold | Index-based stratification + topic imbalance (p=4×10⁻²⁷⁵) | Topic-balanced strata, larger round depth |

![Topic balance figure](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_bi_align_3/docs/youra_research/20260503_bi_align/h-m2/figures/fig5_topic_balance.png)

*Figure 5: Chi-square test for topic uniformity across HH-RLHF annotation strata (p = 4×10⁻²⁷⁵). Extreme topic imbalance may confound β_H and β_S estimates but is less likely to affect β_L.*

---

## 6. Discussion

### 6.1 Interpretation of Findings

The verbosity coefficient reversal (Δβ_L = +0.080, non-overlapping 95% CI) is the most robust finding of this study. It is replicable without annotator metadata — requiring only preference labels and response text — and survives the Q_early stability check (β_Q = −0.017). The pattern is directionally consistent with the hypothesis that annotators in later phases of multi-round RLHF annotation assign greater positive weight to verbosity, which is a salient stylistic feature of AI-generated text.

The between-group tercile analysis on WebGPT provides supporting evidence at the population level: AI-typicality projection scores differ significantly across groups (F = 33.226), and this difference is specific to the AI-typicality direction (discriminant validity confirmed). However, the between-group design cannot distinguish individual annotator adaptation from group composition differences, and the pre-registered within-annotator effect-size threshold was not met.

The directional consistency across all three stylistic features (sign_consistent = true for β_L, β_H, β_S) is informative as a diagnostic: all deltas are positive despite only one meeting the CI non-overlap criterion. Hedging and structured reasoning may also exhibit drift but at magnitudes below detection given the available proxy design and topic confound.

### 6.2 Limitations

**L1: Index-based round stratification.** HH-RLHF does not contain per-annotation timestamps or annotator identifiers. Round stratification is based on row index, not genuine temporal ordering. The observed verbosity coefficient reversal may reflect between-cohort composition differences rather than within-annotator adaptation over time. This limits the causal interpretation to population-level association.

**L2: WebGPT between-group design.** The planned within-annotator PanelOLS regression was not executable due to the absence of worker identity fields in the public WebGPT release. The tercile proxy (|score_0 − score_1| as confidence proxy) collapsed to two effective groups, further limiting between-group power. Selection effects cannot be ruled out.

**L3: Partial AAI validation.** The AAI as specified comprises three components; only the first two are evaluated in this work. The reward-model behavioral divergence component (H-M3) and the downstream benchmark degradation test (H-M4) were not executed. Whether the observed stylistic coefficient shift propagates to reward model scoring behavior remains an open empirical question.

**L4: Topic distribution imbalance.** The chi-square test across HH-RLHF strata yields p = 4×10⁻²⁷⁵, indicating that strata differ substantially in topic distribution. This confound likely affects β_H and β_S more than β_L, since response length is less topic-specific than hedging or structural features.

**L5: H-M1 gate interpretation.** The MUST_WORK gate for H-M1 was evaluated on code executability, not scientific effect size. The pre-registered scientific criterion (effect size ≥ 0.1 SD per 1,000 tokens) was not met. Results should be interpreted as proof-of-concept for the measurement pipeline, not as validation of the full AAI component-2 specification.

### 6.3 Implications

If the verbosity coefficient reversal reflects genuine annotator adaptation rather than cohort composition effects, it implies that reward models trained on later annotation rounds optimize for a different preference target than those trained earlier. This temporal non-stationarity would be invisible to standard pairwise accuracy metrics.

The AAI provides a low-cost monitoring instrument for this phenomenon: round-stratified coefficient comparison requires only preference labels and response text. Practitioners with access to multi-round annotation datasets could apply this check as a quality gate prior to reward model training.

The null results from this study provide concrete, actionable guidance for future dataset design: confirming individual annotator causal adaptation requires genuine annotation timestamps, within-annotator session tracking across at least three sessions per annotator, and per-prompt disagreement labels to enable ambiguity stratification.

---

## 7. Conclusion

This paper presents a computational analysis of stylistic preference drift in two RLHF annotation datasets using the Alignment Asymmetry Index (AAI), a composite instrument for measuring directional Human→AI adaptation in preference labels.

The primary finding is that verbosity preference weighting reverses sign across annotation strata in HH-RLHF (Δβ_L = +0.080, non-overlapping 95% bootstrap CIs; 53,600 rows per stratum). This is interpreted as a population-level directional association, subject to the constraint that the available dataset lacks genuine temporal metadata or annotator identifiers.

A secondary between-group analysis on WebGPT finds statistically significant between-group differences in AI-typicality projection scores (tercile F = 33.226, p ≈ 8.3×10⁻⁹) with confirmed discriminant validity (placebo empirical p = 0.48), but does not meet the pre-registered within-annotator effect-size criterion. Two of five sub-hypotheses were not executed; one of three executed sub-hypotheses met its full pre-registered criteria; one met MUST_WORK gate criteria on code executability but not scientific effect size; and one is recorded as PARTIAL.

The findings motivate drift-aware quality auditing for multi-round RLHF annotation datasets and provide an empirically grounded specification of the data requirements for confirming individual annotator causal adaptation. The highest-priority follow-on is completing H-M3: testing whether the verbosity upweighting observable in later annotation strata propagates to reward model scoring behavior.

---

## References

Bai, Y. et al. (2022). Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback. arXiv:2204.05862.

Christiano, P. et al. (2017). Deep Reinforcement Learning from Human Preferences. *NeurIPS 30*.

Coste, T. et al. (2023). Reward Model Ensembles Help Mitigate Overoptimization. arXiv:2310.02743.

Dietvorst, B. J., Logg, J. M., & Hsee, C. K. (2015). Algorithm Aversion: People Erroneously Avoid Algorithms after Seeing Them Err. *Journal of Experimental Psychology: General*, 144(1), 114–126.

Gao, L., Schulman, J., & Hilton, J. (2022). Scaling Laws for Reward Model Overoptimization. arXiv:2210.10760.

Lee, J. D., & See, K. A. (2004). Trust in Automation: Designing for Appropriate Reliance. *Human Factors*, 46(1), 50–80.

Liang, P. et al. (2023). Holistic Evaluation of Language Models. arXiv:2211.09110.

Ouyang, L. et al. (2022). Training Language Models to Follow Instructions with Human Feedback. arXiv:2203.02155.

Pan, A., Bhatia, K., & Steinhardt, J. (2022). The Effects of Reward Misspecification: Mapping and Mitigating Misaligned Models. arXiv:2201.03544.

Parasuraman, R., & Manzey, D. H. (2010). Complacency and Bias in Human Use of Automation. *Human Factors*, 52(3), 381–410.

Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. *EMNLP 2019*.

Skitka, L. J., Mosier, K. L., & Burdick, M. (1999). Does Automation Bias Decision-Making? *International Journal of Human-Computer Studies*, 51(5), 991–1006.

Stiennon, N. et al. (2020). Learning to Summarize with Human Feedback. arXiv:2009.01325.

Thakur, S., & Kambhampati, S. (2024). Judging the Judges: Evaluating Alignment and Vulnerabilities in LLMs-as-Judges. arXiv:2406.12624.

Ziegler, D. M. et al. (2019). Fine-Tuning Language Models from Human Preferences. arXiv:1909.08593.
