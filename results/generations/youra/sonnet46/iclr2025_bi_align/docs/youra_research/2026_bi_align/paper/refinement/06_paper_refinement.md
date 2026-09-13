# Tier-Scalable Semantic Accommodation in RLHF Human-AI Conversations

## Abstract

This paper measures semantic accommodation in human-AI conversations drawn from the Anthropic HH-RLHF helpfulness dataset, where conversations are stratified across three reinforcement learning from human feedback (RLHF) alignment quality tiers. We introduce C_sem, a training-free sentence-BERT (SBERT) metric that quantifies interaction-specific semantic accommodation by subtracting a random partner-shuffle baseline from turn-pair cosine similarity. A three-level partner-specificity hierarchy (actual partner > KNN topic-matched > random) provides additional validation that the measured signal exceeds topically matched controls. Analysis of 155,362 conversation pairs indicates that human follow-up turns exhibit substantial semantic similarity to their actual AI partner turns relative to random baseline turns (C_sem = 0.329, 95% CI [0.328, 0.330]; Cohen's d = 1.998 vs. random; d = 0.417 vs. KNN topic-matched). C_sem increases monotonically across RLHF quality tiers (Jonckheere-Terpstra p = 0.001, replicated across three SBERT architectures; Cohen's d for T1 to T3 ranges from 0.183 to 0.254). In all nine tier-by-model conditions, human-to-AI accommodation exceeds AI-to-human accommodation (d = 0.061--0.41). However, two mechanism hypotheses are falsified: within-conversation quality discrimination yields a reversed signal (human follow-up turns are more similar to rejected AI responses than to chosen ones in 25 of 27 conditions), and a politeness-style mediation proxy shows no predictive power (beta approximately 0, p approximately 0.99). These results characterize the accommodation pattern as a population-level association between RLHF tier and human semantic behavior, rather than a within-conversation perceptual effect. The cross-sectional design precludes causal claims.

## 1. Introduction

Reinforcement Learning from Human Feedback (RLHF) (Ouyang et al., 2022; Bai et al., 2022) is a widely used method for aligning language model outputs with human preferences. Standard RLHF evaluation treats the interaction as unidirectional: human preference annotations shape AI outputs, and evaluation metrics focus on AI response quality. Whether and how AI response quality is associated with downstream human communicative behavior in these conversations has received comparatively little empirical attention.

Communication Accommodation Theory (CAT) (Giles, 1973) predicts that interlocutors adapt their communication patterns toward one another, with lower-power interlocutors tending to accommodate more to higher-power ones (Danescu-Niculescu-Mizil et al., 2012). Prior empirical work on accommodation has primarily operated at the lexical level (function-word coordination) in human-human settings. Recent work has examined word-level style adaptation in human-AI conversations (Chang and Wang, 2025) and proposed conceptual frameworks for bidirectional human-AI alignment (Shen et al., 2025), but quantitative measurement of semantic-level accommodation across RLHF quality tiers has not been reported.

This paper addresses the following empirical question: Is RLHF alignment quality associated with systematic differences in human semantic behavior across conversations? To operationalize this question, we introduce C_sem, a metric that measures the cosine similarity between SBERT embeddings of a human follow-up turn and its preceding AI partner turn, minus a random partner-shuffle baseline from the same tier. This subtraction is intended to isolate interaction-specific semantic alignment above chance-level topical coherence. A KNN topic-matched control (K=5) provides an additional, stricter comparison.

We compute C_sem across the three HH-RLHF helpfulness tiers (helpful-base, helpful-rejection-sampled, helpful-online) and in both directions (human-to-AI and AI-to-human). Five sub-hypotheses are tested: (1) existence of above-baseline accommodation, (2) monotonic scaling with RLHF tier, (3) directional asymmetry favoring human-to-AI accommodation, (4) within-conversation quality discrimination as a mechanism, and (5) politeness-style mediation. Three sub-hypotheses are supported by the data; two mechanism hypotheses are falsified.

## 2. Related Work

### 2.1 Communication Accommodation Theory

Communication Accommodation Theory (CAT) (Giles, 1973; Giles and Ogay, 2007) posits that interlocutors converge or diverge linguistically as a function of social and relational factors. Danescu-Niculescu-Mizil et al. (2012) operationalized linguistic coordination using function-word category frequencies in Wikipedia administrator discussions and U.S. Supreme Court oral arguments, finding that lower-power interlocutors accommodate more to higher-power ones. Their coordination metric (C_m) operates at the lexical level over closed-class word categories. The present work extends accommodation measurement to continuous semantic embedding space (SBERT cosine similarity) and applies it to human-AI conversations stratified by RLHF quality tier.

### 2.2 RLHF Alignment and the HH-RLHF Dataset

RLHF (Christiano et al., 2017; Ouyang et al., 2022) uses human preference annotations to train reward models that guide language model optimization. Bai et al. (2022) introduced the HH-RLHF dataset, comprising three helpfulness tiers representing successive stages of alignment: supervised fine-tuning (helpful-base), rejection sampling with a reward model (helpful-rejection-sampled), and online PPO optimization (helpful-online). Existing work uses the tier structure to evaluate AI output quality. The present study uses the tier structure as an independent variable and measures human conversational behavior as the dependent variable.

### 2.3 Human-AI Style Adaptation

Chang and Wang (2025) demonstrated word-level bidirectional style adaptation in human-AI conversations across cultural contexts. Shen et al. (2025) proposed a bidirectional alignment framework motivating the study of mutual adaptation in human-AI interaction. Neither study examines SBERT-based semantic accommodation across RLHF quality tiers.

### 2.4 Sentence Embeddings and Semantic Similarity

Reimers and Gurevych (2019) introduced Sentence-BERT, producing semantically meaningful sentence embeddings via siamese BERT architectures with mean pooling. SBERT embeddings capture both content and style in a unified continuous space. This entanglement is a known limitation: cosine similarity between full-utterance embeddings does not cleanly separate topical from stylistic alignment. The three-level partner-specificity control hierarchy used in this work partially addresses this confound.

## 3. Method

### 3.1 Dataset and Tier Structure

The Anthropic HH-RLHF helpfulness dataset (Bai et al., 2022) contains human-AI conversations organized into three quality tiers:

| Tier | HH-RLHF Split | RLHF Process |
|------|---------------|--------------|
| T1 | helpful-base | Supervised fine-tuning |
| T2 | helpful-rejection-sampled | SFT + rejection sampling with reward model |
| T3 | helpful-online | SFT + online PPO with reward model |

Conversations are parsed by splitting on `\n\nHuman:` and `\n\nAssistant:` markers, yielding alternating human and AI turns. From each conversation, (H_{t+1}, A_t, H_t) triples are extracted, where H_{t+1} is the human follow-up turn, A_t is the preceding AI turn, and H_t is the human prompt turn. Filtering removes empty turns and conversations with fewer than two turns. The final dataset contains 155,362 conversation pairs across three tiers, drawn from 118,263 conversations. Per-tier counts are approximately 63,830 (helpful-base), 65,359 (helpful-rejection-sampled), and 26,173 (helpful-online).

### 3.2 Semantic Accommodation Metric (C_sem)

C_sem is defined as the mean cosine similarity between a human follow-up turn and its actual AI partner turn, minus the mean cosine similarity between the same human turn and a randomly sampled AI turn from the same tier (excluding the actual partner):

C_sem^{H<-A} = E[cos(SBERT(H_{t+1}), SBERT(A_t))] - E[cos(SBERT(H_{t+1}), SBERT(A_t^{random-shuffle}))]

C_sem > 0 indicates that human follow-up turns are more semantically similar to their actual AI partner than to a random AI turn from the same tier.

A three-level partner-specificity hierarchy provides additional validation:

- Level 1: cos(H_{t+1}, A_actual) -- actual partner
- Level 2: cos(H_{t+1}, A_KNN) -- KNN topic-matched neighbor (K=5, cosine metric, same tier)
- Level 3: cos(H_{t+1}, A_random) -- random AI turn from same tier

The predicted ordering is Level 1 > Level 2 > Level 3. C_sem as reported uses the Level 1 minus Level 3 difference. The Level 1 versus Level 2 comparison serves as a stricter specificity check.

### 3.3 SBERT Embedding Models

Three pre-trained SBERT models are used:

| Model | Architecture | Parameters |
|-------|-------------|------------|
| all-MiniLM-L6-v2 | 6-layer MiniLM | 22M |
| paraphrase-MiniLM-L6-v2 | 6-layer MiniLM | 22M |
| all-mpnet-base-v2 | 12-layer MPNet | 110M |

All models use mean pooling. Embeddings are computed at inference time without fine-tuning, in batches of 256 with fp16 precision. Results are required to replicate across at least two of three models for a claim to be upheld.

### 3.4 Covariate Correction

The three HH-RLHF tiers differ in conversation topic distribution and other characteristics beyond RLHF quality. Inverse Probability Weighting (IPW) is applied as a covariate correction when distributional shift is detected. Kolmogorov-Smirnov tests are computed between each tier pair on SBERT embedding projections. IPW is triggered when KS p < 0.0001. Logistic propensity scores are estimated on the top-50 PCA dimensions of SBERT embeddings. Each observation is reweighted by the inverse of its propensity score, and IPW-weighted C_sem values are recomputed per tier. KS tests indicated significant distributional shift for all three tier pairs (KS statistics: 0.0195 for base vs. rejection-sampled, 0.1108 for rejection-sampled vs. online, 0.1223 for base vs. online; all p < 0.0001), triggering IPW correction in all cases.

### 3.5 Statistical Tests

**Existence (h-e1):** Bootstrap confidence intervals (1,000 resamples, seed 42) for C_sem. Mann-Whitney U tests for each level comparison in the partner-specificity hierarchy. Cohen's d for effect sizes.

**Tier monotonicity (h-m1):** Jonckheere-Terpstra test for ordered alternatives, testing whether C_sem increases monotonically across tiers. Gate: J-T p < 0.05 and Cohen's d for T1 versus T3 at least 0.1, in at least two of three SBERT models.

**Directionality (h-m2):** Mann-Whitney U test comparing C_sem^{H<-A} to C_sem^{A<-H} per tier per SBERT model (nine independent tests).

**Within-prompt mechanism (h-m3):** Within-pair delta = cos(SBERT(H_next), SBERT(A_chosen)) - cos(SBERT(H_next), SBERT(A_rejected)), computed across three operationalizations: (OP1) raw full-text, (OP2) length-matched truncation, and (OP3) prompt-projected similarity. Gate: delta > 0 in at least two of three operationalizations across at least two of three models.

**Mediation regression (h-m4):** OLS regression with HC3 robust standard errors, predicting C_sem from a politeness/style proxy (cosine similarity to a hand-curated politeness centroid), surface features (response length, bullet density, politeness frequency, type-token ratio, mean sentence length), and tier fixed effects. Gate: beta_PM > 0 and p < 0.05 in at least two of three models.

### 3.6 Five Sub-Hypothesis Framework

| Sub-Hypothesis | Type | Gate Level |
|----------------|------|------------|
| h-e1: C_sem > 0 with partner-specificity | Existence | MUST_WORK |
| h-m1: C_sem monotone in tier | Mechanism | MUST_WORK |
| h-m2: C_sem^{H<-A} > C_sem^{A<-H} | Mechanism | SHOULD_WORK |
| h-m3: Within-prompt delta > 0 | Mechanism | SHOULD_WORK |
| h-m4: beta_PM > 0 (mediation) | Mechanism | SHOULD_WORK |

MUST_WORK gates are termination conditions; SHOULD_WORK gates are non-blocking.

## 4. Experimental Setup

### 4.1 Dataset

All experiments use the Anthropic HH-RLHF helpfulness dataset. The dataset is publicly available on Hugging Face Hub (Anthropic/hh-rlhf). The three helpfulness splits yield 155,362 conversation pairs from 118,263 conversations. Per-tier pair counts: helpful-base approximately 63,830; helpful-rejection-sampled approximately 65,359; helpful-online approximately 26,173.

### 4.2 Hardware and Software

Experiments were run on an NVIDIA H100 NVL GPU (CUDA_VISIBLE_DEVICES=2). Software environment: Python 3.10, PyTorch 2.1, sentence-transformers 2.7.0, scikit-learn 1.4.0, scipy 1.15.3, datasets 2.20.0.

### 4.3 Hyperparameters

All hyperparameters are fixed across experiments: bootstrap resamples = 1,000; bootstrap seed = 42; Cohen's d threshold = 0.1; KNN K = 5; minimum number of pairs = 1,000; significance level = 0.05.

### 4.4 Baselines

For h-e1 through h-m2, baselines are internal to the dataset: a random partner-shuffle baseline (cosine similarity to a randomly sampled AI turn from the same tier) and a KNN topic-matched baseline (cosine similarity to the top-5 nearest neighbor AI turn by SBERT cosine in the same tier, excluding the actual partner). For h-m3, the null hypothesis is delta = 0. For h-m4, the null is beta_PM = 0.

## 5. Results

### 5.1 Existence of Semantic Accommodation (h-e1)

Table 1 reports the partner-specificity hierarchy for the primary model (all-MiniLM-L6-v2, n = 155,362 pairs).

**Table 1: Partner-Specificity Hierarchy (all-MiniLM-L6-v2)**

| Control Level | Mean Cosine Similarity | 95% CI | Cohen's d vs. Actual |
|---------------|----------------------|--------|---------------------|
| Actual AI partner | 0.3534 | [0.352, 0.354] | -- |
| KNN topic-matched (K=5) | 0.2688 | [0.268, 0.270] | 0.417 |
| Random AI turn | 0.0241 | [0.024, 0.025] | 1.998 |

C_sem = 0.3534 - 0.0241 = 0.329 (95% CI [0.328, 0.330]). The ordering actual > KNN > random holds, with all Mann-Whitney comparisons significant at p < 0.001 (p = 0.0 at machine precision). The effect size relative to the random baseline (d = 1.998) is large by conventional standards (Cohen, 1988). The effect relative to the KNN topic-matched baseline (d = 0.417) is smaller but remains above zero, indicating that the signal is not fully explained by topical co-occurrence.

Robustness models confirm the pattern. For paraphrase-MiniLM-L6-v2: C_sem = 0.300 (95% CI [0.299, 0.301]), d = 1.838 vs. random, d = 0.413 vs. KNN. For all-mpnet-base-v2: C_sem = 0.341 (95% CI [0.340, 0.342]), d = 2.099 vs. random, d = 0.400 vs. KNN. All three models pass the existence gate.

![Partner-specificity hierarchy](/home/anonymous/YouRA_results_new_4/TEST_bi_align/docs/youra_research/20260315_bi_align/h-e1/code/outputs/figures/partner_specificity.png)

**Figure 1.** Three-level partner-specificity hierarchy showing mean cosine similarity for actual AI partner, KNN topic-matched (K=5), and random AI turns (all-MiniLM-L6-v2, n = 155,362).

### 5.2 Tier-Scalable Accommodation (h-m1)

Table 2 reports C_sem values across tiers and models.

**Table 2: C_sem per Tier per SBERT Model**

| Tier | all-MiniLM-L6-v2 | paraphrase-MiniLM-L6-v2 | all-mpnet-base-v2 |
|------|-----------------|------------------------|------------------|
| T1 (helpful-base) | 0.3036 | 0.2714 | 0.3138 |
| T2 (helpful-rejection-sampled) | 0.3367 | 0.3068 | 0.3483 |
| T3 (helpful-online) | 0.3678 | 0.3456 | 0.3820 |

Monotonicity (T1 < T2 < T3) holds for all three models. IPW-corrected aggregate values (averaged across models) are 0.307, 0.336, and 0.364 for T1, T2, and T3 respectively; monotonicity is preserved after IPW correction.

**Table 3: Jonckheere-Terpstra Tests and Effect Sizes (h-m1)**

| Model | J-T Statistic | J-T p-value | d (T1 vs. T2) | d (T2 vs. T3) | d (T1 vs. T3) |
|-------|--------------|-------------|---------------|---------------|----------------|
| all-MiniLM-L6-v2 | 4,039,609,994 | 0.001 | 0.087 | 0.096 | 0.183 |
| paraphrase-MiniLM-L6-v2 | 4,116,983,177 | 0.001 | 0.114 | 0.143 | 0.254 |
| all-mpnet-base-v2 | 4,090,937,042 | 0.001 | 0.098 | 0.140 | 0.238 |

All three models yield J-T p = 0.001. The T1-to-T3 Cohen's d values range from 0.183 to 0.254, all exceeding the pre-specified threshold of 0.1. Adjacent-tier contrasts (T1 vs. T2) yield smaller effect sizes (d = 0.087--0.114), with some falling below the 0.1 threshold. The Jonckheere-Terpstra test evaluates the full ordered pattern rather than adjacent contrasts alone.

### 5.3 Directional Asymmetry (h-m2)

Table 4 reports C_sem in both directions across all nine tier-by-model conditions.

**Table 4: Directional C_sem Asymmetry**

| Model | Tier | C_sem^{H<-A} | C_sem^{A<-H} | Cohen's d | p-value |
|-------|------|-------------|-------------|-----------|---------|
| all-MiniLM-L6-v2 | T1 (base) | 0.0853 | 0.0395 | 0.373 | 0.0 |
| all-MiniLM-L6-v2 | T2 (rej.-sampled) | 0.0923 | 0.0535 | 0.330 | 0.0 |
| all-MiniLM-L6-v2 | T3 (online) | 0.0876 | 0.0718 | 0.133 | 4.8e-30 |
| paraphrase-MiniLM-L6-v2 | T1 | 0.0794 | 0.0316 | 0.405 | 0.0 |
| paraphrase-MiniLM-L6-v2 | T2 | 0.0866 | 0.0433 | 0.385 | 0.0 |
| paraphrase-MiniLM-L6-v2 | T3 | 0.0847 | 0.0617 | 0.205 | 4.5e-81 |
| all-mpnet-base-v2 | T1 | 0.0826 | 0.0422 | 0.334 | 0.0 |
| all-mpnet-base-v2 | T2 | 0.0884 | 0.0581 | 0.261 | 0.0 |
| all-mpnet-base-v2 | T3 | 0.0838 | 0.0767 | 0.061 | 0.004 |

C_sem^{H<-A} exceeds C_sem^{A<-H} in all nine conditions. Effect sizes range from d = 0.061 (mpnet, T3) to d = 0.405 (paraphrase, T1). All comparisons are statistically significant. The weakest cell (all-mpnet-base-v2, T3 online) has d = 0.061 with p = 0.004. The asymmetry tends to be smaller for T3 (the highest-quality tier) across all models.

![Directional asymmetry](/home/anonymous/YouRA_results_new_4/TEST_bi_align/docs/youra_research/20260315_bi_align/figures/significance_heatmap.png)

**Figure 2.** Cohen's d heatmap for directional asymmetry (C_sem^{H<-A} minus C_sem^{A<-H}) across all nine tier-by-model cells.

### 5.4 Within-Prompt Quality Discrimination (h-m3)

Table 5 reports delta = cos(H_next, A_chosen) - cos(H_next, A_rejected) across tiers and operationalizations for all-MiniLM-L6-v2.

**Table 5: Within-Prompt Delta (all-MiniLM-L6-v2)**

| Tier | n pairs | OP1 (raw) E[delta] | OP1 d | OP2 (length-matched) E[delta] | OP2 d | OP3 (prompt-projected) E[delta] | OP3 d |
|------|---------|-------------------|-------|-------------------------------|-------|--------------------------------|-------|
| T1 (base) | 31,013 | -0.020 | -0.074 | -0.041 | -0.161 | +0.014 | +0.069 |
| T2 (rej.-sampled) | 35,665 | -0.106 | -0.400 | -0.118 | -0.459 | -0.045 | -0.216 |
| T3 (online) | 14,426 | -0.167 | -0.716 | -0.170 | -0.738 | -0.097 | -0.524 |

Delta is negative in 25 of 27 tier-by-operationalization-by-model combinations across all three SBERT models. The single partial exception is OP3 (prompt-projected) for T1 with all-MiniLM-L6-v2, which yields a weakly positive delta of +0.014 (d = +0.069). Zero of three models pass the pre-specified gate (delta > 0 in at least two of three operationalizations).

The negative delta is strongest in T3 (d = -0.716 to -0.738 for OP1 and OP2), the tier with the highest RLHF quality. Human follow-up turns are systematically more semantically similar to the rejected AI response than to the chosen one. This pattern is statistically significant at p < 0.001 in 24 of 27 cells.

The paraphrase-MiniLM-L6-v2 and all-mpnet-base-v2 models show qualitatively identical patterns, with all operationalizations yielding negative deltas except for isolated weak positive values in T1 prompt-projected conditions. Neither robustness model passes the gate.

### 5.5 Politeness-Style Mediation (h-m4)

Table 6 reports OLS mediation regression results.

**Table 6: OLS Mediation Regression (n = 3,000 per model)**

| Model | beta_PM | SE (HC3) | p-value | R-squared |
|-------|---------|---------|---------|-----------|
| all-MiniLM-L6-v2 | -1.46e-05 | ~1.5e-02 | 0.998 | 0.007 |
| paraphrase-MiniLM-L6-v2 | -1.26e-06 | ~1.2e-02 | 1.000 | 0.007 |
| all-mpnet-base-v2 | +6.76e-05 | ~7.2e-03 | 0.991 | 0.012 |

beta_PM is indistinguishable from zero in all three models (absolute values below 1e-4, p-values near 1.0). Total model R-squared ranges from 0.007 to 0.012, indicating that the full set of predictors (PM-proxy, surface features, tier controls) collectively explains less than 1.2% of C_sem variance. Zero of three models pass the mediation gate.

### 5.6 Summary

**Table 7: Sub-Hypothesis Verification Summary**

| Sub-Hypothesis | Gate Level | Result | Key Metric |
|----------------|-----------|--------|------------|
| h-e1: Accommodation exists | MUST_WORK | PASS | C_sem = 0.329; d = 1.998 vs. random |
| h-m1: Tier monotonicity | MUST_WORK | PASS | J-T p = 0.001; d = 0.183--0.254 (T1 to T3); 3/3 models |
| h-m2: Directional asymmetry | SHOULD_WORK | PASS | All 9 cells; d = 0.061--0.405 |
| h-m3: Within-prompt quality discrimination | SHOULD_WORK | FAIL | delta < 0 in 25/27 cells; d up to -0.738 |
| h-m4: PM-proxy mediation | SHOULD_WORK | FAIL | beta_PM approximately 0; p approximately 0.99 |

Three of five sub-hypotheses are supported. Two mechanism hypotheses are falsified.

## 6. Discussion

### 6.1 Interpretation of Findings

The results establish three empirical patterns. First, human follow-up turns in HH-RLHF helpfulness conversations exhibit substantially higher semantic similarity to their actual AI partner turns than to random or topic-matched baseline turns. The effect size relative to the random baseline is large (d = 1.998), and the effect remains present when compared to KNN topic-matched controls (d = 0.400--0.417 across models). This indicates that the measured similarity is not fully attributable to topical co-occurrence, though SBERT embeddings do not permit clean separation of topical and stylistic components.

Second, C_sem increases monotonically from T1 to T3 across all three SBERT models, with J-T p = 0.001 in each case. The effect size for the T1-to-T3 contrast is small to medium (d = 0.183--0.254). Adjacent-tier contrasts are smaller (d = 0.087--0.114 for T1 vs. T2), and some fall below the pre-specified 0.1 threshold. IPW correction for distributional shift across tiers preserves the monotonic ordering.

Third, human-to-AI accommodation exceeds AI-to-human accommodation in all nine tier-by-model conditions. The effect sizes are variable (d = 0.061--0.405) and tend to decrease for higher-quality tiers.

The two falsified mechanism hypotheses provide constraints on interpretation. The within-prompt quality probe (h-m3) yields a reversed signal: human follow-up turns are more similar to the rejected AI response than to the chosen one. This reversal is strongest in the highest-quality tier (T3, d up to -0.738). One interpretation is that rejected responses in HH-RLHF tend to be longer and more topically expansive, providing more semantic surface area that incidentally overlaps with the human's subsequent turn, independent of the quality dimensions on which RLHF raters based their preference annotations. The politeness-style mediation analysis (h-m4) finds no evidence that a cosine-based politeness proxy explains C_sem variance.

These falsifications indicate that the tier-accommodation association operates at the population level -- conversations drawn from higher-quality tiers exhibit stronger accommodation on average -- rather than through a within-conversation mechanism where humans perceive and respond to individual response quality.

### 6.2 Limitations

**Cross-sectional design.** The HH-RLHF dataset lacks user identifiers; each conversation is anonymous. The finding that higher-tier conversations show stronger C_sem cannot distinguish accommodation from user self-selection: more sophisticated users may self-select into higher-tier conversations and independently exhibit communication patterns that yield higher C_sem. Within-user longitudinal data (e.g., from LMSYS Chatbot Arena with session identifiers) would be needed to test within-user accommodation trajectories.

**Topical-stylistic entanglement in SBERT.** SBERT embeddings capture both content and style. C_sem cannot be decomposed into topical and stylistic components. The KNN topic-matched baseline provides a partial control (d = 0.417 above topic-matched), but residual topical similarity may contribute to the measured effect. Style-factored sentence representations would enable more precise decomposition.

**Tier confounds.** The three HH-RLHF splits were collected at different stages of Anthropic's deployment pipeline. Differences in user demographics, conversation topics, and interaction conventions across tiers may confound the RLHF quality variable. IPW correction addresses measured distributional shift but cannot control for unmeasured confounds.

**Unresolved mechanism.** Both tested mechanism hypotheses (within-prompt quality discrimination, politeness-style mediation) are falsified. The proximal mechanism linking RLHF tier to population-level accommodation remains unidentified. This limits the theoretical interpretation of the tier-scaling finding.

**PM-proxy operationalization.** The politeness-style proxy used in h-m4 is based on cosine similarity to a hand-curated centroid, which may not capture the relevant dimensions of AI response quality. However, the essentially zero coefficient (beta < 1e-4) and very low model R-squared (less than 0.012) suggest that even a better proxy would need to explain substantially more variance than the current feature set.

### 6.3 Implications

The finding that RLHF tier quality co-varies with human semantic behavior at the population level suggests that RLHF evaluation may benefit from incorporating measures of human-side communicative patterns, in addition to standard AI output quality metrics. The h-m3 reversal (human follow-ups are more similar to rejected than chosen responses) indicates that RLHF's chosen/rejected annotation captures quality dimensions that are partly orthogonal to conversational semantic continuity. Researchers using the HH-RLHF chosen/rejected structure as a proxy for conversational effectiveness should be aware of this dissociation.

## 7. Conclusion

This study introduced C_sem, a training-free SBERT-based metric for measuring semantic accommodation in human-AI conversation, and applied it to 155,362 turn pairs from the Anthropic HH-RLHF helpfulness dataset. Three findings are supported by the data: (1) human follow-up turns exhibit substantial interaction-specific semantic similarity to their AI partner turns (C_sem = 0.329, d = 1.998 vs. random, d = 0.417 vs. KNN topic-matched); (2) this similarity increases monotonically with RLHF tier quality (J-T p = 0.001, d = 0.183--0.254 for T1 to T3, replicated across three SBERT architectures); and (3) human-to-AI accommodation exceeds AI-to-human accommodation in all nine tier-by-model conditions (d = 0.061--0.405).

Two mechanism hypotheses are falsified. Within-conversation quality discrimination yields a reversed signal: human follow-ups are more similar to rejected than chosen AI responses (delta < 0 in 25 of 27 conditions, d up to -0.738). A politeness-style mediation proxy has no predictive power (beta approximately 0, p approximately 0.99). The tier-accommodation association is therefore characterized as a population-level pattern rather than a within-conversation perceptual effect. The cross-sectional design precludes causal claims; longitudinal within-user studies would be needed to establish whether RLHF quality causally influences human semantic behavior.

## References

Bai, Y., Jones, A., Ndousse, K., Askell, A., Chen, A., DasSarma, N., Drain, D., Fort, S., Ganguli, D., Henighan, T., Joseph, N., Kadavath, S., Kernion, J., Conerly, T., El-Showk, S., Elhage, N., Hatfield-Dodds, Z., Hernandez, D., Hume, T., Johnston, S., Kravec, S., Lovitt, L., Nanda, N., Olsson, C., Amodei, D., Brown, T. B., Clark, J., McCandlish, S., Olah, C., Mann, B., and Kaplan, J. (2022). Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback. arXiv preprint arXiv:2204.05862.

Chang, X. and Wang, R. (2025). Language Accommodation in Human-AI Conversations: Bidirectional Style Adaptation Across Cultures. Proceedings of the AAAI Conference on Artificial Intelligence.

Christiano, P., Leike, J., Brown, T. B., Martic, M., Legg, S., and Amodei, D. (2017). Deep Reinforcement Learning from Human Preferences. Advances in Neural Information Processing Systems.

Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences (2nd ed.). Lawrence Erlbaum Associates.

Danescu-Niculescu-Mizil, C., Lee, L., Pang, B., and Kleinberg, J. (2012). Echoes of power: language effects and power differences in social interaction. Proceedings of the 21st International Conference on World Wide Web, 699--708.

Fusaroli, R., Raczaszek-Leonardi, J., and Tylen, K. (2014). Dialog as Interpersonal Synergy. New Ideas in Psychology, 32, 147--157.

Giles, H. (1973). Accent Mobility: A Model and Some Data. Anthropological Linguistics, 15(2), 87--105.

Giles, H. and Ogay, T. (2007). Communication Accommodation Theory. In B. Whaley and W. Samter (Eds.), Explaining Communication: Contemporary Theories and Exemplars (pp. 293--310). Lawrence Erlbaum Associates.

Ouyang, L., Wu, J., Jiang, X., Almeida, D., Wainwright, C. L., Mishkin, P., Zhang, C., Agarwal, S., Slama, K., Ray, A., Schulman, J., Hilton, J., Kelton, F., Miller, L. E., Simens, M., Askell, A., Welinder, P., Christiano, P., Leike, J., and Lowe, R. (2022). Training language models to follow instructions with human feedback. Advances in Neural Information Processing Systems.

Pickering, M. J. and Garrod, S. (2004). Toward a Mechanistic Psychology of Dialogue. Behavioral and Brain Sciences, 27(2), 169--226.

Porcheron, M., Fischer, J. E., Reeves, S., and Sharples, S. (2018). Voice Interfaces in Everyday Life. Proceedings of the 2018 CHI Conference on Human Factors in Computing Systems.

Reimers, N. and Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing, 3982--3992.

Shen, H., Knearem, T., Thakkar, D., Pataranutaporn, P., Sinha, A. K., Shi, Y., Liang, J. T., Ahmad, L., Mitra, T., Myers, B. A., and Li, Y. (2025). Human-AI Interaction Alignment: Designing, Evaluating, and Evolving Value-Centered AI For Reciprocal Human-AI Futures. arXiv preprint arXiv:2512.21551.

Stiennon, N., Ouyang, L., Wu, J., Ziegler, D. M., Lowe, R., Voss, C., Radford, A., Amodei, D., and Christiano, P. (2020). Learning to summarize with human feedback. Advances in Neural Information Processing Systems.
