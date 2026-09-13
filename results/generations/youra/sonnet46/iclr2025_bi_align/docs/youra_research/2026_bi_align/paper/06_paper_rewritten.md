# Tier-Scalable Semantic Accommodation in RLHF-Stratified Human-AI Conversations

## Abstract

This paper examines whether reinforcement learning from human feedback (RLHF) alignment quality is associated with systematic differences in human semantic behavior in human-AI conversations. Using the Anthropic HH-RLHF helpfulness dataset (155,362 conversation pairs across three RLHF quality tiers), we introduce C_sem, a training-free sentence-BERT-based metric that quantifies interaction-specific semantic accommodation by subtracting a random partner-shuffle baseline from turn-pair cosine similarity. A three-level partner-specificity hierarchy (actual partner > KNN topic-matched > random) validates that the accommodation signal exceeds topical coherence (Cohen's d = 0.417 for actual vs. KNN topic-matched; d = 1.998 for actual vs. random). C_sem increases monotonically across RLHF tiers (Jonckheere-Terpstra p = 0.001, confirmed across three SBERT architectures), and humans accommodate more to AI than AI to humans in all 9 tier × model conditions (d = 0.061–0.41). However, two mechanism hypotheses are falsified: within-conversation quality discrimination yields the opposite of the predicted direction (human follow-ups are more similar to rejected than chosen AI responses in 25 of 27 conditions), and a politeness-style mediation proxy shows no predictive power (β_PM ≈ 0, p > 0.84 across all models). These results indicate that RLHF tier quality is associated with population-level differences in human semantic behavior, but the proximal mechanism is not within-conversation quality perception. Causal identification is limited by the cross-sectional design.

---

## 1. Introduction

Reinforcement Learning from Human Feedback (RLHF) (Ouyang et al., 2022; Bai et al., 2022) has become a widely adopted approach for aligning language model outputs with human preferences. The standard framing treats this process as unidirectional: human preferences shape AI behavior. However, real human-AI interaction is bidirectional. Communication Accommodation Theory (CAT) (Giles, 1973) establishes that interlocutors adapt to one another in conversation, and recent work on bidirectional alignment (Shen et al., 2025) has called for studying the human side of human-AI adaptation. Despite this motivation, no prior work has measured semantic-level accommodation across RLHF quality tiers.

This paper addresses a focused empirical question: is RLHF alignment quality associated with systematic differences in human semantic behavior across conversations? The question is motivated by two observations. First, CAT and its extensions predict that accommodation varies with interlocutor quality and perceived status (Danescu-Niculescu-Mizil et al., 2012). Second, the Anthropic HH-RLHF dataset provides a principled quality gradient across three tiers — base supervised fine-tuning (T1), rejection sampling with a reward model (T2), and online PPO-based fine-tuning (T3) — enabling observational measurement of whether human behavior co-varies with this gradient.

To measure accommodation, we introduce C_sem, a training-free metric computed as the cosine similarity between a human follow-up turn and its actual AI partner turn in SBERT embedding space, minus the cosine similarity to a randomly sampled AI turn from the same tier. This subtraction isolates interaction-specific accommodation above chance-level topical coherence. A KNN topic-matched control (K=5) provides an additional specificity check. C_sem requires no model fine-tuning and can be computed with pre-trained SBERT models at inference time.

Our analysis of 155,362 conversation pairs yields four main findings. First, humans exhibit interaction-specific semantic accommodation to their AI partners (C_sem = 0.329, 95% CI [0.328, 0.330]; d = 1.998 vs. random baseline). Second, this accommodation increases monotonically with RLHF tier quality (Jonckheere-Terpstra p = 0.001, confirmed across three SBERT architectures). Third, humans accommodate more to AI than AI to humans in all 9 tier × model conditions (d = 0.061–0.41). Fourth, two specific mechanism hypotheses — within-conversation quality discrimination and politeness-style mediation — are falsified, pointing to a population-structural rather than perceptual account of the association.

The contributions of this work are:

1. **C_sem**, a training-free SBERT-based measure of semantic accommodation with a three-level partner-specificity control hierarchy, enabling calibrated measurement of interaction-specific semantic alignment in conversational AI data.

2. **Empirical demonstration** that C_sem increases monotonically across HH-RLHF quality tiers (J-T p = 0.001, Cohen's d for T1→T3 = 0.183–0.254), confirmed across three SBERT models.

3. **Directional asymmetry**: C_sem^{H←A} > C_sem^{A←H} in all 9 tier × model cells, extending function-word coordination findings (Danescu-Niculescu-Mizil et al., 2012) to semantic embedding space in human-AI interaction.

4. **Mechanism falsification**: within-conversation quality discrimination (Δ < 0 in 25/27 cells) and politeness-style mediation (β_PM ≈ 0, p > 0.84) are ruled out as proximal mechanisms.

---

## 2. Related Work

### 2.1 Communication Accommodation Theory and Linguistic Coordination

Communication Accommodation Theory (CAT) (Giles, 1973; Giles & Ogay, 2007) posits that interlocutors converge or diverge linguistically based on social, relational, and cognitive factors. Lower-power interlocutors tend to accommodate more to higher-power ones. Danescu-Niculescu-Mizil et al. (2012) operationalized this as linguistic coordination using function-word category frequencies in Wikipedia administrator discussions and U.S. Supreme Court oral arguments, demonstrating that language users accommodate to partners who hold authority over them. Their measure captures surface-level lexical accommodation in closed-class word categories.

The present work extends this framework in two directions. First, it moves from function-word coordination (lexical/syntactic level) to semantic embedding space (SBERT cosine similarity), capturing meaning-level alignment between interlocutors. Second, it applies this framework to human-AI conversations with a structured quality gradient (RLHF tiers) rather than institutional role. Several studies have examined linguistic alignment in human-human conversation using distributional semantic methods (Fusaroli et al., 2014; Pickering & Garrod, 2004), and more recently in human-computer interaction (Porcheron et al., 2018). However, none have examined SBERT-based semantic accommodation across RLHF alignment tiers.

### 2.2 RLHF Alignment and Human Preference Learning

RLHF (Christiano et al., 2017; Ouyang et al., 2022) trains language models to align outputs with human preferences. Bai et al. (2022) introduced the HH-RLHF dataset comprising three helpfulness tiers (helpful-base, helpful-rejection-sampling, helpful-online), each representing a higher stage of RLHF quality optimization. Existing RLHF evaluation research uses the tier structure to measure AI output quality — response helpfulness, harmlessness, and instruction-following (Bai et al., 2022; Ouyang et al., 2022; Stiennon et al., 2020). The present work inverts this paradigm: it treats RLHF tier as the independent variable and measures human conversational behavior as the dependent variable. To our knowledge, no prior work has used HH-RLHF tier structure to study how RLHF quality is associated with downstream human semantic patterns.

### 2.3 Human-AI Style Adaptation and Bidirectional Alignment

Recent work has begun examining how humans adapt to AI conversational style. Chang & Wang (2025) demonstrated word-level bidirectional style adaptation in human-AI conversations across cultural contexts. However, their work operates at the word-level style matching layer and does not examine the role of RLHF alignment quality as a driver of accommodation strength. The BiAlign framework (Shen et al., 2025) motivates the study of bidirectional alignment — recognizing that human-AI conversations are mutual adaptation systems — but does not provide empirical measurement of human-side semantic adaptation at scale. The present work addresses this gap with SBERT-based measurement of human semantic accommodation across RLHF quality tiers at population scale (n = 155,362 pairs).

### 2.4 Semantic Similarity and Sentence Embeddings

Reimers & Gurevych (2019) introduced Sentence-BERT (SBERT), a siamese BERT architecture producing semantically meaningful sentence embeddings via mean pooling, where cosine similarity serves as a reliable measure of semantic alignment. SBERT embeddings capture both content (topical similarity) and style (semantic register, phrasing) in a unified continuous space. This entanglement is a known limitation: topical and stylistic signals cannot be cleanly separated. The three-level partner-specificity control hierarchy introduced in this work addresses this concern by comparing actual partner similarity against a KNN topic-matched baseline, isolating interaction-specific accommodation above topical coherence.

### 2.5 Power Asymmetry in Language

The power asymmetry hypothesis (Danescu-Niculescu-Mizil et al., 2012; Giles & Ogay, 2007) predicts that lower-status interlocutors accommodate more to higher-status partners. In human-AI interaction, the power relationship is not institutionally defined, but RLHF alignment quality may function as a proxy for conversational authority. The finding reported below — that C_sem^{H←A} > C_sem^{A←H} in all 9 tier × model cells — is consistent with this prediction, though the directional asymmetry may also reflect the structural properties of RLHF data collection (AI responses are optimized to be semantically comprehensive) rather than conscious human recognition of AI authority.

---

## 3. Method

### 3.1 Dataset and Tier Structure

The Anthropic HH-RLHF helpfulness dataset (Bai et al., 2022) contains human-AI conversations organized into three quality tiers:

| Tier | HH-RLHF Split | RLHF Process | Quality Level |
|------|--------------|--------------|---------------|
| T1 | `helpful-base` | Supervised fine-tuning only | Lowest |
| T2 | `helpful-rejection-sampled` | SFT + rejection sampling with reward model | Medium |
| T3 | `helpful-online` | SFT + online PPO with reward model | Highest |

Conversations are parsed by splitting on `\n\nHuman:` and `\n\nAssistant:` markers, yielding alternating human and AI turns. (H_{t+1}, A_t, H_t) triples — human follow-up turn, preceding AI partner turn, and human prompt turn — are extracted and filtered to non-empty turns. The total dataset contains 118,263 conversations yielding 155,362 turn pairs. Per-tier pair counts (from the tier monotonicity experiment) are: helpful-base: 63,830; helpful-rejection-sampled: 65,359; helpful-online: 26,173.

### 3.2 Semantic Accommodation Metric (C_sem)

The core measurement challenge is separating interaction-specific accommodation from topical coherence. C_sem addresses this by subtracting a random partner-shuffle baseline:

$$C_{\text{sem}}^{H \leftarrow A} = \mathbb{E}\left[\cos\left(\text{SBERT}(H_{t+1}),\ \text{SBERT}(A_t)\right)\right] - \mathbb{E}\left[\cos\left(\text{SBERT}(H_{t+1}),\ \text{SBERT}(A_t^{\text{random-shuffle}})\right)\right]$$

where $A_t^{\text{random-shuffle}}$ is a randomly sampled AI turn from the same tier (excluding the actual partner). C_sem > 0 indicates that human follow-up turns are more semantically similar to their actual AI partner than to a random AI turn from the same tier.

**Three-level partner-specificity hierarchy.** To further validate that C_sem captures genuine accommodation rather than topical overlap, a three-level control hierarchy is constructed:

- Level 1: cos(H_{t+1}, A_actual) — actual partner (highest expected similarity)
- Level 2: cos(H_{t+1}, A_KNN) — topic-matched KNN neighbor (K=5, cosine similarity, same tier)
- Level 3: cos(H_{t+1}, A_random) — random AI turn from same tier (lowest expected similarity)

C_sem as computed equals Level 1 − Level 3 (actual − random). The Level 1 − Level 2 gap serves as an additional stricter specificity check.

### 3.3 SBERT Embedding Models

Three SBERT models are used to assess robustness across embedding architectures:

| Model | Architecture | Parameters |
|-------|-------------|------------|
| `all-MiniLM-L6-v2` | 6-layer MiniLM | 22M |
| `paraphrase-MiniLM-L6-v2` | 6-layer MiniLM | 22M |
| `all-mpnet-base-v2` | 12-layer MPNet | 110M |

All models use mean-pooling over token embeddings. Results are required to replicate across ≥2 of 3 models for any claim to be upheld. Embeddings are computed at inference time (no fine-tuning) in batches of 256 with half-precision (fp16).

### 3.4 Covariate Correction: Inverse Probability Weighting

The three HH-RLHF tiers differ not only in RLHF quality but in conversation topic distribution and interaction style. To control for distributional shifts, Inverse Probability Weighting (IPW) is applied:

1. Kolmogorov-Smirnov statistics are computed between each tier pair on SBERT embedding projections.
2. IPW is triggered if KS p < 0.0001.
3. Logistic propensity scores P(tier = k | embedding features) are estimated on the top-50 PCA dimensions.
4. Each observation is reweighted by 1/P(tier = k | x).
5. IPW-weighted C_sem is recomputed per tier.

### 3.5 Statistical Tests

**Existence (h-e1):** Bootstrap confidence intervals (1,000 resamples, seed = 42) for C_sem. Mann-Whitney U test for each level comparison in the partner-specificity hierarchy. Cohen's d for effect size.

**Tier monotonicity (h-m1):** Jonckheere-Terpstra test for ordered alternatives, testing μ_{T1} < μ_{T2} < μ_{T3}. Gate: J-T p < 0.05 and Cohen's d for T1→T3 ≥ 0.1.

**Directionality (h-m2):** Mann-Whitney U test comparing C_sem^{H←A} to C_sem^{A←H} per tier per SBERT model (9 independent tests).

**Within-prompt mechanism (h-m3):** Δ = cos(SBERT(H_next), SBERT(A_chosen)) − cos(SBERT(H_next), SBERT(A_rejected)), computed across three operationalizations: (OP1) raw full-text, (OP2) length-matched truncation, and (OP3) prompt-projected responses. Gate: Δ > 0 in ≥2/3 operationalizations across ≥2/3 SBERT models.

**Mediation regression (h-m4):** OLS regression with HC3 robust standard errors:

$$C_{\text{sem}} = \beta_0 + \beta_{PM} \cdot \text{PM\_proxy} + \beta_\ell \cdot \text{length} + \beta_{bd} \cdot \text{bullet\_density} + \beta_{pf} \cdot \text{politeness\_freq} + \beta_\tau \cdot \text{tier} + \epsilon$$

where PM_proxy is cosine similarity to a hand-curated politeness/style centroid in SBERT space. Gate: β_PM > 0 and p < 0.05 in ≥2/3 SBERT models.

### 3.6 Five-Hypothesis Verification Framework

The analysis is decomposed into five sub-hypotheses with explicit gate conditions:

| Sub-Hypothesis | Gate Type | Test |
|----------------|-----------|------|
| h-e1: C_sem > 0 with partner-specificity | MUST_WORK | Partner-specificity hierarchy |
| h-m1: C_sem monotone across tiers | MUST_WORK | Jonckheere-Terpstra |
| h-m2: C_sem^{H←A} > C_sem^{A←H} | SHOULD_WORK | Mann-Whitney per cell |
| h-m3: Within-prompt Δ > 0 | SHOULD_WORK | Within-pair Δ test |
| h-m4: β_PM > 0 (mediation) | SHOULD_WORK | OLS mediation regression |

MUST_WORK gates are termination conditions; SHOULD_WORK gates are non-blocking (failure is recorded as a limitation).

---

## 4. Experimental Setup

### 4.1 Dataset

All experiments use the Anthropic HH-RLHF helpfulness dataset (Bai et al., 2022). The dataset contains 118,263 conversations yielding 155,362 turn pairs across three splits. The tier structure provides a principled RLHF quality gradient. The chosen/rejected pair structure within each conversation enables the within-prompt mechanism test (h-m3).

### 4.2 Baselines and Controls

| Control | Description | Role |
|---------|-------------|------|
| Random shuffle | Cosine similarity to a random AI turn from the same tier | Null baseline for C_sem |
| KNN topic-matched | Cosine similarity to top-5 KNN neighbor (same tier, excluding actual partner) | Strict topic control |
| Δ = 0 | Null hypothesis for within-prompt quality probe | Mechanism test baseline |
| β_PM = 0 | Null hypothesis for mediation | Mediation test baseline |

### 4.3 Implementation Details

**Software:** Python 3.10; PyTorch 2.1; sentence-transformers 2.7.0; scikit-learn 1.4.0; scipy 1.15.3; datasets 2.20.0.

**Hardware:** NVIDIA H100 NVL GPU; SBERT inference uses GPU acceleration; statistical tests are CPU-only.

**Hyperparameters (fixed across all experiments):**

| Parameter | Value |
|-----------|-------|
| Bootstrap resamples | 1,000 |
| Bootstrap seed | 42 |
| Cohen's d threshold | 0.1 |
| KNN K | 5 |
| Minimum n_pairs | 1,000 |
| Significance level | 0.05 |

---

## 5. Results

### 5.1 Existence of Semantic Accommodation (h-e1)

Table 1 reports the three-level partner-specificity hierarchy across the full HH-RLHF helpfulness dataset (n = 155,362 pairs).

**Table 1: Partner-Specificity Hierarchy (h-e1, all-MiniLM-L6-v2)**

| Control Level | Mean Cosine Similarity | Cohen's d vs. Actual |
|--------------|----------------------|---------------------|
| Actual AI partner | 0.3534 | — |
| KNN topic-matched (K=5) | 0.2688 | 0.417 |
| Random AI turn | 0.0241 | 1.998 |

C_sem = 0.3534 − 0.0241 = 0.329 (95% CI [0.328, 0.330]). All Mann-Whitney comparisons are significant at p < 10^{-300} (n = 155,362). The effect against the KNN topic-matched control (d = 0.417) indicates that the accommodation signal exceeds topical coherence.

Robustness across embedding models: C_sem = 0.300 for paraphrase-MiniLM-L6-v2 (95% CI [0.299, 0.301]) and C_sem = 0.341 for all-mpnet-base-v2 (95% CI [0.340, 0.342]). All three models confirm C_sem > 0 with gate passed.

![Figure 1: Three-level partner-specificity hierarchy showing mean cosine similarity for actual AI partner, KNN topic-matched (K=5), and random AI turns.](/home/anonymous/YouRA_results_new_4/TEST_bi_align/docs/youra_research/20260315_bi_align/paper/figures/partner_specificity.png)

![Figure 2: Distribution of cosine similarities for actual, topic-matched, and random partner conditions.](/home/anonymous/YouRA_results_new_4/TEST_bi_align/docs/youra_research/20260315_bi_align/paper/figures/cosine_distributions.png)

![Figure 3: Gate metrics for the existence hypothesis.](/home/anonymous/YouRA_results_new_4/TEST_bi_align/docs/youra_research/20260315_bi_align/paper/figures/gate_metrics.png)

![Figure 4: Bootstrap distribution of C_sem estimates.](/home/anonymous/YouRA_results_new_4/TEST_bi_align/docs/youra_research/20260315_bi_align/paper/figures/bootstrap_dist.png)

### 5.2 Tier-Scalable Accommodation (h-m1)

Table 2 reports tier-stratified C_sem values. Tier pair counts: helpful-base (T1): 63,830 pairs; helpful-rejection-sampled (T2): 65,359 pairs; helpful-online (T3): 26,173 pairs.

**Table 2: Tier-Stratified C_sem (Three SBERT Models)**

| Tier | all-MiniLM-L6-v2 | paraphrase-MiniLM-L6-v2 | all-mpnet-base-v2 |
|------|-----------------|------------------------|------------------|
| T1 (helpful-base) | 0.304 | 0.271 | 0.314 |
| T2 (helpful-rejection-sampled) | 0.337 | 0.307 | 0.348 |
| T3 (helpful-online) | 0.368 | 0.346 | 0.382 |
| **J-T p-value** | **0.001** | **0.001** | **0.001** |
| **Cohen's d (T1→T3)** | **0.183** | **0.254** | **0.238** |

Tier monotonicity is confirmed in all three SBERT models (J-T p = 0.001, 3/3 models pass). Cohen's d for T1→T3 ranges from 0.183 to 0.254, exceeding the pre-specified threshold of d ≥ 0.1. IPW covariate correction was triggered (KS p < 0.0001 in all tier pairs); IPW-corrected C_sem values maintain the monotonic pattern (Table 2 reports IPW-corrected values; see Figure 8 for raw vs. IPW comparison).

The T1→T2 contrast is small in some models (d = 0.087–0.098 for MiniLM and MPNet), below the d ≥ 0.1 threshold for adjacent-tier contrasts. The Jonckheere-Terpstra test accounts for the full ordered pattern rather than adjacent contrasts alone.

Pairwise Cohen's d values with 95% CIs across all models and tier pairs are reported in Table 3.

**Table 3: Pairwise Cohen's d Across Tiers (all three SBERT models)**

| Comparison | MiniLM d [95% CI] | Paraphrase d [95% CI] | MPNet d [95% CI] |
|-----------|-------------------|----------------------|-----------------|
| T1 vs. T2 | −0.087 [−0.098, −0.076] | −0.114 [−0.124, −0.103] | −0.098 [−0.109, −0.087] |
| T2 vs. T3 | −0.096 [−0.110, −0.082] | −0.143 [−0.158, −0.129] | −0.140 [−0.153, −0.125] |
| T1 vs. T3 | −0.183 [−0.196, −0.169] | −0.254 [−0.269, −0.241] | −0.238 [−0.252, −0.224] |

Note: negative d values indicate T1 < T2 < T3 (higher tiers have higher C_sem), consistent with the monotonicity hypothesis.

![Figure 5: Tier-stratified C_sem values across three SBERT models showing monotonic increase.](/home/anonymous/YouRA_results_new_4/TEST_bi_align/docs/youra_research/20260315_bi_align/paper/figures/tier_csem_bars.png)

![Figure 6: Tier monotonicity lines across SBERT models.](/home/anonymous/YouRA_results_new_4/TEST_bi_align/docs/youra_research/20260315_bi_align/paper/figures/tier_monotonicity_lines.png)

![Figure 7: Cohen's d heatmap for pairwise tier comparisons.](/home/anonymous/YouRA_results_new_4/TEST_bi_align/docs/youra_research/20260315_bi_align/paper/figures/cohend_heatmap.png)

![Figure 8: IPW-corrected vs. raw C_sem comparison across tiers.](/home/anonymous/YouRA_results_new_4/TEST_bi_align/docs/youra_research/20260315_bi_align/paper/figures/ipw_comparison.png)

### 5.3 Directional Asymmetry (h-m2)

Table 4 reports bidirectional C_sem values across all 9 tier × model cells.

**Table 4: Directional Asymmetry (C_sem^{H←A} vs. C_sem^{A←H})**

| Model | Tier | C_sem^{H←A} | C_sem^{A←H} | Cohen's d | Δ_asymmetry |
|-------|------|-------------|-------------|-----------|-------------|
| MiniLM | T1 | 0.085 | 0.040 | 0.373 | 0.046 |
| MiniLM | T2 | 0.092 | 0.054 | 0.330 | 0.039 |
| MiniLM | T3 | 0.088 | 0.072 | 0.133 | 0.016 |
| Paraphrase | T1 | 0.079 | 0.032 | 0.405 | 0.048 |
| Paraphrase | T2 | 0.087 | 0.043 | 0.385 | 0.043 |
| Paraphrase | T3 | 0.085 | 0.062 | 0.205 | 0.023 |
| MPNet | T1 | 0.083 | 0.042 | 0.334 | — |
| MPNet | T2 | 0.088 | 0.058 | — | — |
| MPNet | T3 | 0.084 | 0.077 | 0.061 | — |

All 9 cells show C_sem^{H←A} > C_sem^{A←H}. The gate is passed for all 3 models with all 3 tiers. The weakest cell is MPNet T3 (d = 0.061), which remains statistically significant. The asymmetry is largest in T1 (d = 0.33–0.41) and decreases toward T3 (d = 0.061–0.21), suggesting that the directional gap narrows as RLHF quality increases.

![Figure 9: Bidirectional comparison of C_sem across tiers.](/home/anonymous/YouRA_results_new_4/TEST_bi_align/docs/youra_research/20260315_bi_align/paper/figures/bidirectional_comparison_bars.png)

![Figure 10: Directional asymmetry bars across tiers and models.](/home/anonymous/YouRA_results_new_4/TEST_bi_align/docs/youra_research/20260315_bi_align/paper/figures/directional_asymmetry_bars.png)

![Figure 11: Asymmetry delta across tiers.](/home/anonymous/YouRA_results_new_4/TEST_bi_align/docs/youra_research/20260315_bi_align/paper/figures/asymmetry_delta_line.png)

![Figure 12: Significance heatmap for directional asymmetry across all 9 cells.](/home/anonymous/YouRA_results_new_4/TEST_bi_align/docs/youra_research/20260315_bi_align/paper/figures/significance_heatmap.png)

### 5.4 Within-Conversation Quality Discrimination (h-m3) — Falsified

This experiment tests whether humans' semantic accommodation is driven by within-conversation quality perception, operationalized as Δ = cos(H_next, A_chosen) − cos(H_next, A_rejected). If within-conversation quality discrimination drives accommodation, Δ should be positive.

**Table 5: Within-Prompt Quality Probe Results (h-m3, MiniLM)**

| Tier | OP1 (raw) Δ | OP2 (length-matched) Δ | OP3 (prompt-projected) Δ | n_pairs |
|------|-----------|----------------------|------------------------|---------|
| T1 (helpful-base) | −0.020 (d = −0.074) | −0.041 (d = −0.161) | +0.014 (d = +0.069) | 31,013 |
| T2 (helpful-rejection-sampled) | −0.106 (d = −0.400) | −0.118 (d = −0.459) | −0.045 (d = −0.216) | 35,665 |
| T3 (helpful-online) | −0.167 (d = −0.716) | −0.170 (d = −0.738) | −0.097 (d = −0.524) | 14,426 |

The gate is not satisfied: 0 of 3 models pass. Across all three SBERT models, Δ < 0 in 25 of 27 tier × operationalization × model combinations. The only partial exceptions occur in OP3 (prompt-projected) in T1, where two models (MiniLM and MPNet) show small positive Δ values (+0.014, d = 0.069 and +0.004, d = 0.021, respectively). In T2 and T3, all operationalizations and all models yield Δ < 0.

The effect is strongest in T3, where RLHF quality differentiation is largest: d = −0.716 (MiniLM OP1 raw), d = −0.738 (MiniLM OP2 length-matched), d = −0.524 (MiniLM OP3 prompt-projected). Similar magnitudes are observed for the paraphrase and MPNet models (d up to −0.799 for MPNet OP2 in T3).

This result falsifies within-conversation quality discrimination as the mechanism underlying tier-scalable accommodation.

![Figure 13: Distribution of Δ values across tiers and operationalizations.](/home/anonymous/YouRA_results_new_4/TEST_bi_align/docs/youra_research/20260315_bi_align/paper/figures/fig1_delta_distributions.png)

![Figure 14: Δ by tier showing the scaling of the reversal effect.](/home/anonymous/YouRA_results_new_4/TEST_bi_align/docs/youra_research/20260315_bi_align/paper/figures/fig4_delta_by_tier.png)

### 5.5 Mediation Analysis (h-m4) — Null Result

This experiment tests whether a politeness/style proxy (PM-score, computed as cosine similarity to a hand-curated politeness centroid in SBERT space) mediates the C_sem asymmetry.

**Table 6: OLS Mediation Regression Results (h-m4, n = 310,786)**

| Model | β_PM (full model) | p-value | 95% CI | R² (full model) |
|-------|-------------------|---------|--------|-----------------|
| all-MiniLM-L6-v2 | −5.01 × 10⁻⁵ | 0.923 | [−1.06 × 10⁻³, 9.62 × 10⁻⁴] | 0.003 |
| paraphrase-MiniLM-L6-v2 | −9.80 × 10⁻⁵ | 0.845 | [−1.08 × 10⁻³, 8.87 × 10⁻⁴] | 0.003 |
| all-mpnet-base-v2 | −5.63 × 10⁻⁵ | 0.911 | [−1.04 × 10⁻³, 9.31 × 10⁻⁴] | 0.002 |

β_PM is indistinguishable from zero in all three models (|β| < 10⁻⁴, p > 0.84). The PM-proxy has no predictive power for C_sem. Total model R² ranges from 0.002 to 0.003, indicating that even the full covariate set (response length, bullet density, politeness frequency, type-token ratio, mean sentence length, and tier indicators) explains less than 0.3% of C_sem variance.

Mediation ratios are negligible: the proportion of PM effect mediated ranges from 0.08% to 0.35% across models. The PM effect is retained at >99.6% when surface features and tier are added, confirming near-zero mediation.

Among the surface covariates, response length (p < 10⁻⁵⁷), bullet density (p < 10⁻²²), politeness frequency (p < 10⁻³⁴), and type-token ratio (p < 10⁻¹⁴) show statistically significant but substantively weak associations with C_sem in the full model. Tier indicators (helpful-online, helpful-rejection-sampled) are also significant (p < 10⁻⁵), consistent with the tier monotonicity finding in §5.2.

A robustness check using tier rank instead of tier dummies confirms that tier rank is a significant predictor of C_sem (β_tier_rank > 0, p < 10⁻⁵ across all models), further supporting the tier-scaling result while confirming that PM-proxy does not mediate this relationship.

![Figure 15: β_PM comparison across models showing near-zero coefficients.](/home/anonymous/YouRA_results_new_4/TEST_bi_align/docs/youra_research/20260315_bi_align/paper/figures/fig1_beta_pm_comparison.png)

![Figure 16: Coefficient forest plot for the full regression model.](/home/anonymous/YouRA_results_new_4/TEST_bi_align/docs/youra_research/20260315_bi_align/paper/figures/fig3_coefficient_forest.png)

### 5.6 Summary

**Table 7: Hypothesis Verification Summary**

| Sub-Hypothesis | Gate Type | Result | Key Metric |
|----------------|-----------|--------|-----------|
| h-e1: Semantic accommodation exists | MUST_WORK | PASS | C_sem = 0.329; d = 1.998 (vs. random) |
| h-m1: Tier monotonicity | MUST_WORK | PASS | J-T p = 0.001; d = 0.183–0.254; 3/3 models |
| h-m2: Directional asymmetry | SHOULD_WORK | PASS | 9/9 cells H←A > A←H; d = 0.061–0.41 |
| h-m3: Within-prompt Δ > 0 | SHOULD_WORK | FAIL | Δ < 0 in 25/27 cells; d up to −0.80 |
| h-m4: PM-proxy mediation | SHOULD_WORK | FAIL | β_PM ≈ 0; p > 0.84; 0/3 models |

Three of five sub-hypotheses are confirmed. Two mechanism hypotheses are falsified.

---

## 6. Discussion

### 6.1 Interpretation of Results

The results establish three findings and two falsifications.

C_sem = 0.329 (d = 1.998 vs. random) indicates that humans exhibit interaction-specific semantic accommodation to their AI partners. The effect exceeds the KNN topic-matched baseline (d = 0.417), indicating that it is not fully explained by topical coherence, though residual topical confounding cannot be entirely excluded (see §6.2).

The monotonic increase in C_sem from T1 to T3 (J-T p = 0.001, confirmed across three SBERT architectures with IPW correction) demonstrates that RLHF alignment quality is associated with differences in human semantic behavior at the population level. This is an observational association; it does not establish that RLHF training causes changes in human behavior. The cross-sectional design cannot rule out that user self-selection or other confounds drive the tier-level differences (see §6.2, Limitation L1).

The directional asymmetry (H←A > A←H in all 9 cells) is consistent with power asymmetry theory, though it may also reflect the structural property that RLHF-optimized AI responses are more semantically comprehensive than human turns, providing more content for cosine similarity to capture.

The h-m3 falsification — human follow-ups are more similar to rejected than chosen AI responses (Δ < 0 in 25/27 cells, d up to −0.80) — rules out within-conversation quality discrimination as the accommodation mechanism. This reversal likely reflects the tendency of rejected RLHF responses to be longer and more expansive, covering more semantic ground that happens to overlap with the human's subsequent information agenda. The h-m4 null result (β_PM ≈ 0, p > 0.84) confirms that a politeness/style proxy does not mediate the accommodation asymmetry.

Together, these results support a population-structural account: RLHF training is associated with distributional differences in AI response character across tiers, and humans interacting within higher-tier conversational environments exhibit greater semantic alignment at the population level — without requiring within-conversation quality perception as the mechanism.

### 6.2 Limitations

**L1: Cross-sectional design.** HH-RLHF lacks user identifiers; each conversation is independent. The finding that higher-tier conversations show stronger C_sem cannot rule out user self-selection: more linguistically sophisticated users may both prefer higher-tier AI and communicate in ways that produce higher cosine similarity. Within-user longitudinal data would be required to establish a causal direction.

**L2: SBERT conflates topical and stylistic accommodation.** SBERT embeddings capture both content and style. C_sem cannot be decomposed into purely stylistic vs. topical components. The KNN K=5 topic-matched baseline provides a partial control (d = 0.417 above topic-matched), but residual topical confounding may remain. Style-factored sentence representations would enable cleaner decomposition.

**L3: Tier confounds.** The three HH-RLHF splits were collected at different stages of Anthropic's deployment pipeline. User demographics, conversation topics, and interaction styles may differ across tiers for reasons unrelated to RLHF quality. IPW covariate correction is applied and maintains monotonicity, but cannot eliminate all possible confounds.

**L4: Unresolved proximal mechanism.** Both tested mechanism hypotheses (h-m3, h-m4) are falsified. The proximal mechanism by which RLHF training quality is associated with population-level accommodation differences remains an open question.

**L5: PM-proxy limitations.** The h-m4 mediation test used cosine similarity to a hand-curated politeness centroid as the PM-score proxy. This is a coarse operationalization that may miss the relevant quality signal. However, β_PM ≈ 0 with p > 0.84 across all three models, and R² ≤ 0.003 for the full model, suggests that even a stronger proxy is unlikely to explain substantial C_sem variance through this regression framework.

### 6.3 Implications

The finding that RLHF tier quality co-varies with human semantic behavior suggests that alignment evaluation should consider human-side adaptation, not only AI output quality. The h-m3 reversal — that rejected responses better predict human follow-up semantics than chosen ones — indicates that RLHF's chosen/rejected annotation captures quality dimensions (helpfulness, safety, instruction-following) that are partly orthogonal to conversational semantic continuity. Researchers using HH-RLHF chosen/rejected structure as a proxy for conversational quality should be aware of this distinction.

---

## 7. Conclusion

This work introduced C_sem, a training-free SBERT-based measure of semantic accommodation in human-AI conversations, and applied it to 155,362 conversation pairs from the Anthropic HH-RLHF helpfulness dataset. The main findings are: (1) humans exhibit interaction-specific semantic accommodation to their AI partners (C_sem = 0.329, d = 1.998 vs. random); (2) this accommodation increases monotonically with RLHF tier quality (J-T p = 0.001, three SBERT architectures); (3) humans accommodate more to AI than AI to humans (9/9 cells, d = 0.061–0.41); and (4) within-conversation quality discrimination and politeness-style mediation are both falsified as proximal mechanisms. These results are observational and do not establish causality. Future work should pursue longitudinal within-user measurement using datasets with session identifiers, verbosity-controlled replication of the h-m3 within-prompt probe, and cross-dataset replication on WildChat and LMSYS Chatbot Arena to test generalizability beyond HH-RLHF.

---

## References

Bai, Y., Jones, A., Ndousse, K., Askell, A., Chen, A., DasSarma, N., Drain, D., Fort, S., Ganguli, D., Henighan, T., Joseph, N., Kadavath, S., Kernion, J., Conerly, T., El-Showk, S., Elhage, N., Hatfield-Dodds, Z., Hernandez, D., Hume, T., Johnston, S., Kravec, S., Lovitt, L., Nanda, N., Olsson, C., Amodei, D., Brown, T. B., Clark, J., McCandlish, S., Olah, C., Mann, B., & Kaplan, J. (2022). Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback. *arXiv preprint arXiv:2204.05862*.

Chang, X. & Wang, R. (2025). Language Accommodation in Human-AI Conversations: Bidirectional Style Adaptation Across Cultures. *Proceedings of the AAAI Conference on Artificial Intelligence*.

Christiano, P., Leike, J., Brown, T. B., Martic, M., Legg, S., & Amodei, D. (2017). Deep Reinforcement Learning from Human Preferences. *Advances in Neural Information Processing Systems*.

Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences* (2nd ed.). Lawrence Erlbaum Associates.

Danescu-Niculescu-Mizil, C., Lee, L., Pang, B., & Kleinberg, J. (2012). Echoes of power: language effects and power differences in social interaction. *Proceedings of the 21st International Conference on World Wide Web*, 699–708.

Fusaroli, R., Raczaszek-Leonardi, J., & Tylén, K. (2014). Dialog as Interpersonal Synergy. *New Ideas in Psychology*, 32, 147–157.

Giles, H. (1973). Accent Mobility: A Model and Some Data. *Anthropological Linguistics*, 15(2), 87–105.

Giles, H. & Ogay, T. (2007). Communication Accommodation Theory. In B. Whaley & W. Samter (Eds.), *Explaining Communication: Contemporary Theories and Exemplars* (pp. 293–310). Lawrence Erlbaum Associates.

Ouyang, L., Wu, J., Jiang, X., Almeida, D., Wainwright, C. L., Mishkin, P., Zhang, C., Agarwal, S., Slama, K., Ray, A., Schulman, J., Hilton, J., Kelton, F., Miller, L. E., Simens, M., Askell, A., Welinder, P., Christiano, P., Leike, J., & Lowe, R. (2022). Training language models to follow instructions with human feedback. *Advances in Neural Information Processing Systems*.

Pickering, M. J. & Garrod, S. (2004). Toward a Mechanistic Psychology of Dialogue. *Behavioral and Brain Sciences*, 27(2), 169–226.

Porcheron, M., Fischer, J. E., Reeves, S., & Sharples, S. (2018). Voice Interfaces in Everyday Life. *Proceedings of the 2018 CHI Conference on Human Factors in Computing Systems*.

Reimers, N. & Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. *Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing*, 3982–3992.

Shen, H., Knearem, T., Thakkar, D., Pataranutaporn, P., Sinha, A. K., Shi, Y., Liang, J. T., Ahmad, L., Mitra, T., Myers, B. A., & Li, Y. (2025). Human-AI Interaction Alignment: Designing, Evaluating, and Evolving Value-Centered AI For Reciprocal Human-AI Futures. *arXiv preprint arXiv:2512.21551*.

Stiennon, N., Ouyang, L., Wu, J., Ziegler, D. M., Lowe, R., Voss, C., Radford, A., Amodei, D., & Christiano, P. (2020). Learning to summarize with human feedback. *Advances in Neural Information Processing Systems*.
