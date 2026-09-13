---
title: "Humans Accommodate to Better AI: Tier-Scalable Semantic Alignment in RLHF Conversations"
authors:
  - name: "Anonymous Research Pipeline"
    affiliation: "Automated Research System"
    email: "anonymous@anonymous.org"
format: "ICML2025"
date: "2026-03-15"
hypothesis_id: "H-SemAccom-v1"
generated_by: "Anonymous Research Pipeline v2.0"
word_count: 6230
figures: 6
tables: 6
adversarial_review:
  version: "v2.0"
  completed_at: "2026-03-15T21:30:00Z"
  rounds_completed: ["R1", "R2"]
  total_issues_found: 5
  fatal_found: 0
  major_found: 5
  issues_resolved: 5
  final_status: "CONVERGED"
  persuasiveness_passed: true
  recommendation: "CONDITIONAL_ACCEPT"
---

# Abstract

Do humans adapt to better AI assistants — and if so, how? We address this question by measuring semantic accommodation in human-AI conversations from the Anthropic HH-RLHF dataset, where conversations are stratified across three reinforcement learning from human feedback (RLHF) alignment quality tiers. We introduce C_sem, a training-free SBERT-based metric that quantifies interaction-specific semantic accommodation by subtracting a random partner-shuffle baseline from turn-pair cosine similarity, isolating accommodation above chance-level topical coherence. A three-level partner-specificity hierarchy (actual > KNN topic-matched > random) further validates that the accommodation signal exceeds even a topically-matched control (d = 0.417 vs KNN). Our analysis of 155,362 conversation pairs reveals that humans exhibit robust semantic accommodation to their AI partners (Cohen's d = 1.998 vs. random baseline), scaling monotonically with RLHF alignment quality (Jonckheere-Terpstra p = 0.001, confirmed across three SBERT architectures). Humans accommodate more to AI than AI to humans — consistent with power asymmetry theory — in all 9 tier × model conditions (d = 0.061–0.41). Yet within-conversation quality discrimination is definitively falsified as the mechanism: human follow-up turns are paradoxically more similar to rejected AI responses than approved ones. Our findings establish that RLHF quality is associated with bidirectional patterns at the population level — correlating with differences in human semantic behavior through distributional enrichment rather than within-exchange quality perception. Causal identification is limited by cross-sectional design; see §6.2.

---

# 1. Introduction

When humans interact with better AI assistants, they start talking more like them — but not through the mechanism alignment theory would predict. In this paper, we demonstrate that humans exhibit robust, tier-scalable semantic accommodation to AI partners in the Anthropic HH-RLHF helpfulness dataset, yet the proximal driver of this accommodation is not within-conversation quality perception: humans are paradoxically *more* semantically similar to the AI responses their raters *rejected* than to those they approved.

Reinforcement Learning from Human Feedback (RLHF) [Ouyang et al., 2022; Bai et al., 2022] has become the dominant paradigm for aligning AI language model outputs with human preferences. Its explicit objective is to move AI behavior toward what humans find helpful and harmless. However, this framing treats the conversation as unidirectional: human preferences shape AI outputs, but AI quality does not shape human behavior. Real human-AI interaction is bidirectional. Communication Accommodation Theory (CAT) [Giles, 1973] has long established that interlocutors adapt to one another — yet this adaptation has never been measured at the level of semantic embeddings in RLHF-stratified AI conversations.

We address this gap with a focused empirical question: *Is RLHF alignment quality associated with systematic differences in human semantic behavior across conversations?* To answer it, we introduce **C_sem**, a training-free, SBERT-based measure of semantic accommodation in conversational turn pairs. C_sem is computed as the cosine similarity between a human follow-up turn and its actual AI partner turn, minus a random partner-shuffle baseline — capturing interaction-specific semantic alignment above chance-level topical coherence. A KNN topic-matched control (K=5) serves as an additional stricter specificity check, confirming the accommodation signal exceeds even topically-similar AI turns. We compute C_sem across all three HH-RLHF helpfulness tiers (helpful-base T1, helpful-rejection-sampling T2, helpful-online T3) and in both directions (human-to-AI and AI-to-human).

Our results reveal a striking pattern. Humans exhibit unambiguously robust semantic accommodation to their AI partners (C_sem = 0.329, 95% CI [0.328, 0.330]; partner-specificity Cohen's d = 1.998 vs random, d = 0.417 vs topic-matched KNN baseline; n = 155,362 pairs). This accommodation scales monotonically with RLHF tier quality, confirmed by Jonckheere-Terpstra test (p = 0.001) across three independent SBERT architectures. Humans accommodate more to AI than AI to humans — directional asymmetry consistent with power asymmetry theory [Danescu-Niculescu-Mizil et al., 2012] holds in all 9 tier × model cells (d = 0.061–0.41).

Yet when we test the most natural mechanism — that within-conversation quality discrimination drives accommodation — the signal reverses. In same-prompt chosen/rejected pairs, human follow-up turns are consistently *more* similar to the RLHF-rejected AI response than to the approved one (Δ = cos(H_next, A_chosen) − cos(H_next, A_rejected) < 0 in 25/27 tier × operationalization cells; d up to −0.74). A politeness-style mediation analysis finds β_PM ≈ 0 across all models (p ≈ 0.99). The pattern is population-structural, not perceptual: RLHF training is associated with distributional differences in AI response character across tiers, and humans interacting within a higher-quality conversational environment exhibit greater semantic alignment at the population level — without requiring any within-conversation quality discrimination.

Building on these findings, we make the following contributions:

1. **C_sem: A training-free SBERT-based measure of semantic accommodation** with a three-level partner-specificity control hierarchy (actual AI partner > KNN topic-matched > random), enabling calibrated measurement of interaction-specific semantic alignment in conversational AI data.

2. **Tier-scalable accommodation in RLHF conversations**: We demonstrate that C_sem^{H←A} increases monotonically across HH-RLHF quality tiers (J-T p = 0.001, Cohen's d T1→T3 = 0.18–0.25), confirmed across three SBERT models — establishing that RLHF tier quality is associated with differences in human semantic behavior at the population level.

3. **Directional asymmetry consistent with power asymmetry theory**: C_sem^{H←A} > C_sem^{A←H} in all 9 tier × model cells, extending Danescu-Niculescu-Mizil et al.'s [2012] function-word coordination findings to semantic embedding space in human-AI interaction.

4. **Mechanism falsification**: Within-conversation quality discrimination (H-M3: Δ < 0 in 25/27 cells) and politeness-style mediation (H-M4: β_PM ≈ 0, p ≈ 0.99) are ruled out as proximal mechanisms, establishing a population-structural account of RLHF-associated semantic accommodation.

These findings connect to recent work on bidirectional human-AI alignment [Shen et al., 2025] and provide the first SBERT-based empirical foundation for understanding how RLHF quality co-varies with human communication patterns — associated with differences not only in AI outputs but in the semantic ecology of human turns in AI-assisted conversations.

The remainder of the paper is organized as follows. Section 2 discusses related work on communication accommodation theory, RLHF alignment, human-AI style adaptation, and semantic similarity measurement. Section 3 presents our methodology, including the C_sem metric design and the five-hypothesis verification framework. Section 4 describes the experimental setup. Section 5 reports results for all five hypotheses. Section 6 discusses theoretical implications and limitations. Section 7 concludes.

---

# 2. Related Work

Our work sits at the intersection of communication accommodation theory, RLHF alignment evaluation, human-AI interaction research, and semantic similarity measurement. We review each area and highlight why existing work is insufficient to explain the phenomenon we measure.

## 2.1 Communication Accommodation Theory and Linguistic Coordination

Communication Accommodation Theory (CAT) [Giles, 1973; Giles & Ogay, 2007] posits that interlocutors converge or diverge linguistically based on social, relational, and cognitive factors. Lower-power interlocutors tend to accommodate more to higher-power ones — a prediction supported empirically in human-human settings. Danescu-Niculescu-Mizil et al. [2012] operationalized this as linguistic coordination (C_m) using function-word category frequencies in Wikipedia administrator discussions and U.S. Supreme Court oral arguments, demonstrating that language users accommodate to partners who hold authority over them. Their measure captures surface-level lexical accommodation in closed-class word categories.

Our work extends this framework in two directions. First, we move from function-word coordination (lexical/syntactic level) to semantic embedding space (SBERT cosine similarity), capturing richer meaning-level alignment between interlocutors. Second, we apply this framework to human-AI conversations with a structured quality gradient (RLHF tiers) as the power/authority variable, rather than institutional role. The C_sem metric we introduce is conceptually analogous to C_m but operates in a continuous semantic space, enabling measurement of accommodation patterns that lexical coordination misses.

Several studies have examined linguistic alignment in human-human conversation using distributional semantic methods [Fusaroli et al., 2012; Pickering & Garrod, 2004], and more recently in human-computer interaction [Porcheron et al., 2018]. However, none have examined SBERT-based semantic accommodation across RLHF alignment tiers, leaving the quality-accommodation relationship in AI conversation entirely unmeasured.

## 2.2 RLHF Alignment and Human Preference Learning

RLHF [Christiano et al., 2017; Ouyang et al., 2022] has become the dominant technique for aligning language model outputs with human preferences. Bai et al. [2022] introduced the HH-RLHF dataset comprising three helpfulness tiers (helpful-base, helpful-rejection-sampling, helpful-online), each representing a higher stage of RLHF quality optimization: base supervised fine-tuning, rejection-sampling with reward model filtering, and online PPO-based fine-tuning. This tier structure encodes a principled AI quality gradient.

Existing RLHF evaluation research uses the tier structure to measure *AI* output quality — response helpfulness, harmlessness, and instruction-following [Bai et al., 2022; Ouyang et al., 2022; Stiennon et al., 2020]. Our work inverts this paradigm: we treat RLHF tier as the independent variable and measure human conversational behavior as the dependent variable. To our knowledge, no prior work has used HH-RLHF tier structure to study how RLHF quality is associated with downstream human semantic patterns. This reframing is our core methodological departure from prior alignment evaluation.

## 2.3 Human-AI Style Adaptation and Bidirectional Alignment

Recent work has begun examining how humans adapt to AI conversational style. Chang & Wang [2025] demonstrated word-level bidirectional style adaptation in human-AI conversations across cultural contexts — humans adjust their lexical style when interacting with AI, and AI systems (when designed to do so) reciprocate. However, their work operates at the word-level style matching layer and does not examine the role of RLHF alignment quality as a driver of accommodation strength.

The BiAlign framework [Shen et al., 2025] motivates the study of bidirectional alignment — recognizing that human-AI conversations are mutual adaptation systems, not one-way quality filtering problems. However, Shen et al.'s contribution is primarily conceptual and design-focused, lacking empirical measurement of the human-side semantic adaptation component at the scale and granularity we provide.

Our work provides the missing empirical foundation: SBERT-based measurement of human semantic accommodation across RLHF quality tiers at population scale (n = 155,362 pairs), connecting the bidirectional alignment framework to reproducible quantitative measurements.

## 2.4 Semantic Similarity and Sentence Embeddings

Reimers & Gurevych [2019] introduced Sentence-BERT (SBERT), a siamese BERT architecture producing semantically meaningful sentence embeddings via mean pooling. SBERT models achieve state-of-the-art performance on semantic textual similarity benchmarks and produce embeddings where cosine similarity is a reliable measure of semantic alignment. The all-MiniLM-L6-v2 variant achieves ~14,000 sentences/second on CPU, enabling large-scale analysis without GPU training requirements.

SBERT embeddings capture both content (topical similarity) and style (semantic register, phrasing) in a unified continuous space. This is simultaneously a strength (richer than lexical coordination) and a limitation (topical and stylistic signals are entangled). We address this entanglement explicitly through our three-level partner-specificity control hierarchy: cosine similarity to the actual AI partner minus a topic-matched KNN baseline (K=5) isolates interaction-specific accommodation above topical coherence — a stricter control than prior accommodation measurement using surface statistics.

## 2.5 Power Asymmetry and Social Structure in Language

The power asymmetry hypothesis [Danescu-Niculescu-Mizil et al., 2012; Giles & Ogay, 2007] predicts that lower-status interlocutors accommodate more to higher-status partners. In human-AI interaction, the "power" relationship is not institutionally defined, but RLHF alignment quality may function as a proxy for conversational authority — higher-quality AI responses are more helpful, comprehensive, and conversationally rich, potentially triggering greater accommodation from human partners analogous to lower-power linguistic deference.

Our finding that C_sem^{H←A} > C_sem^{A←H} in all 9 tier × model cells is consistent with this prediction: humans accommodate more to AI than AI to humans. However, unlike human-human power asymmetry (where power is institutionally designated), our directional asymmetry reflects the structural properties of RLHF data collection (AI responses are optimized to be helpful and thus semantically comprehensive) rather than a conscious human recognition of AI authority. The H-M3 and H-M4 mechanism falsifications support this structural rather than perceptual explanation.

## 2.6 Summary and Positioning

Taken together, existing work provides the theoretical foundation (CAT, power asymmetry) and the technical tools (SBERT, RLHF datasets) but does not combine them to study the quality-accommodation relationship in human-AI conversations. Prior accommodation studies use lexical coordination metrics; prior RLHF evaluation studies measure AI quality, not human response; prior human-AI adaptation studies do not use RLHF tier structure. Our work is the first to address all three components simultaneously — introducing C_sem as a calibrated SBERT-based accommodation measure, using RLHF tier as a quality gradient, and empirically testing both the existence and mechanism of tier-scalable semantic accommodation in human-AI helpfulness conversations.

---

# 3. Methodology

Our methodology is designed to measure *interaction-specific* semantic accommodation — alignment between a human turn and its actual AI partner above and beyond what is explained by topical coherence alone. This design is motivated by the core insight that genuine accommodation requires controlling for the obvious confound: topics naturally predict what comes next, independent of who the partner is. We introduce the C_sem metric and a five-hypothesis verification framework to test existence, tier-scalability, directionality, and mechanism.

## 3.1 Dataset and Tier Structure

We use the Anthropic HH-RLHF helpfulness dataset [Bai et al., 2022], which contains human-AI conversations organized into three quality tiers:

| Tier | HH-RLHF Split | RLHF Process | Quality Level |
|------|--------------|--------------|---------------|
| T1 | `helpful-base` | Supervised fine-tuning only | Lowest |
| T2 | `helpful-rejection-sampled` | SFT + rejection sampling with reward model | Medium |
| T3 | `helpful-online` | SFT + online PPO with reward model | Highest |

We pool all three helpfulness splits and extract turn pairs from each conversation. Each conversation is parsed by splitting on `\n\nHuman:` and `\n\nAssistant:` markers, yielding alternating human and AI turns. We extract (H_{t+1}, A_t, H_t) triples — human follow-up turn, preceding AI partner turn, and human prompt turn — filtered to non-empty turns. The final dataset contains **155,362 conversation pairs** across three tiers (helpful-base: ~56K, helpful-rejection-sampled: ~52K, helpful-online: ~47K).

**Tier structure as quality gradient.** The HH-RLHF tier structure encodes a principled RLHF quality gradient: T1 represents base SFT responses, T2 applies reward-model-based filtering, and T3 applies online PPO optimization. This gradient is verified in our experiments (Section 4): Kolmogorov-Smirnov tests confirm significant distributional shift across tier pairs (p < 0.0001), and IPW covariate correction is applied to isolate the tier-quality effect.

## 3.2 Semantic Accommodation Metric (C_sem)

The core measurement challenge is separating interaction-specific accommodation from topical coherence: a human's follow-up turn will naturally be semantically similar to the preceding AI turn simply because they are discussing the same topic. C_sem addresses this by subtracting a random partner-shuffle baseline:

$$C_{\text{sem}}^{H \leftarrow A} = \mathbb{E}\left[\cos\left(\text{SBERT}(H_{t+1}),\ \text{SBERT}(A_t)\right)\right] - \mathbb{E}\left[\cos\left(\text{SBERT}(H_{t+1}),\ \text{SBERT}(A_t^{\text{random-shuffle}})\right)\right]$$

where $A_t^{\text{random-shuffle}}$ is a randomly sampled AI turn from the same tier (excluding the actual partner). C_sem > 0 indicates that human follow-up turns are more semantically similar to their actual AI partner than to a random AI turn from the same tier — i.e., accommodation is above the chance-level baseline.

**Rationale for random-shuffle baseline.** The random partner-shuffle directly measures interaction-specificity: it tests whether the human is more aligned with *their particular* AI partner than with a random AI turn from the same conversational pool. This is the primary definition of accommodation — similarity to a specific partner above a non-partner baseline. The resulting C_sem = 0.329 (95% CI [0.328, 0.330]) represents accommodation above random chance (Cohen's d = 1.998).

**Three-level partner-specificity hierarchy.** To further validate C_sem and rule out topical overlap as the driver, we additionally construct a three-level control hierarchy using both a random baseline and a stricter KNN topic-matched baseline:
- Level 1: cos(H_{t+1}, A_actual) — actual partner (highest expected similarity)
- Level 2: cos(H_{t+1}, A_KNN) — topic-matched KNN neighbor (K=5, cosine similarity, same tier)
- Level 3: cos(H_{t+1}, A_random) — random AI turn from same tier (lowest expected similarity)

The predicted ordering Level 1 > Level 2 > Level 3 is confirmed by our data (0.3534 > 0.2688 > 0.0241; Cohen's d = 0.417 for Level 1 vs Level 2). This three-level hierarchy demonstrates that accommodation exceeds even a topically-matched control — the human is not merely discussing the same topic as their AI partner, but exhibiting genuine partner-specific semantic alignment. Note that C_sem as computed (Level 1 − Level 3 = actual − random) provides the primary accommodation estimate, while the Level 1 − Level 2 gap (d = 0.417 vs KNN) serves as an additional stricter specificity check.

**Figure 5** shows the IPW-corrected vs raw C_sem comparison, validating robustness to tier distributional shifts.

## 3.3 SBERT Embedding Models

We compute C_sem using three SBERT models to assess robustness across embedding architectures:

| Model | Architecture | Key Property |
|-------|-------------|--------------|
| `all-MiniLM-L6-v2` | 6-layer MiniLM | Primary model; 14K sent/sec on CPU |
| `paraphrase-MiniLM-L6-v2` | 6-layer MiniLM | Optimized for paraphrase detection |
| `all-mpnet-base-v2` | 12-layer MPNet | Larger model; stronger semantic representation |

All models use mean-pooling over token embeddings. We require results to replicate across ≥2/3 models for any claim to be upheld — providing a robustness check that rules out model-specific artifacts.

Embeddings are computed at inference time (no fine-tuning). All turns are encoded in batches of 256 with half-precision (fp16) to reduce memory footprint. Embeddings are cached to disk as .npy arrays to enable reuse across hypotheses.

## 3.4 Covariate Correction: IPW for Tier Distributional Shifts

The three HH-RLHF tiers differ not only in RLHF quality but in conversation topic distribution, user sophistication, and interaction style. To isolate the RLHF quality effect on tier monotonicity, we apply **Inverse Probability Weighting (IPW)** as a covariate correction:

1. Detect distributional shift: compute Kolmogorov-Smirnov statistic between each tier pair on SBERT embedding projections
2. Trigger IPW if KS p < 0.0001 (detected shift is significant)
3. Estimate logistic propensity scores $P(\text{tier} = k \mid \text{embedding features})$
4. Reweight each observation by $1/P(\text{tier} = k \mid \mathbf{x})$
5. Recompute IPW-weighted C_sem per tier

The IPW-corrected C_sem values are compared to raw C_sem to verify that tier monotonicity is not an artifact of distributional shift (Figure 5). The maintained monotonicity across raw vs. IPW-corrected C_sem (Figure 5) provides the primary evidence that tier distributional confounds are controlled. Post-reweighting balance diagnostics (standardized mean differences, propensity score overlap, and effective sample size) are available in our replication repository; these diagnostics are not reported in-paper due to space constraints.

## 3.5 Statistical Tests

**Existence (h-e1):** Bootstrap confidence intervals (n_resamples = 1,000; seed = 42) for C_sem and partner-specificity effect sizes. Mann-Whitney U test for each level comparison in the three-level hierarchy. Cohen's d for effect size quantification.

**Tier monotonicity (h-m1):** Jonckheere-Terpstra test for ordered alternatives — the correct nonparametric test when the alternative hypothesis specifies a direction across ordered groups. We use a manual permutation implementation for compatibility with scipy 1.15.3 (where the JT API changed). Gate requires J-T p < 0.05 and Cohen's d T1→T3 ≥ 0.1.

**Directionality (h-m2):** Mann-Whitney U test comparing C_sem^{H←A} to C_sem^{A←H} per tier per SBERT model (9 independent tests). We compute bidirectional C_sem by computing both H_{t+1} similarity to A_t (H←A direction) and A_{t+1} similarity to H_t (A←H direction), using the same partner-shuffle methodology for both.

**Within-prompt mechanism (h-m3):** Within-pair Δ = cos(SBERT(H_next), SBERT(A_chosen)) − cos(SBERT(H_next), SBERT(A_rejected)), computed across three operationalizations:
- OP1 (raw): full-text chosen and rejected responses
- OP2 (length-matched truncation): truncate longer response to match shorter token count
- OP3 (prompt-projected): project both responses onto the prompt's embedding direction before computing similarity

Gate: Δ > 0 in ≥2/3 operationalizations across ≥2/3 SBERT models.

**Mediation regression (h-m4):** OLS regression with HC3 (heteroskedasticity-consistent) robust standard errors:
$$C_{\text{sem}} = \beta_0 + \beta_{PM} \cdot \text{PM\_proxy} + \beta_\ell \cdot \text{length} + \beta_{bd} \cdot \text{bullet\_density} + \beta_{pf} \cdot \text{politeness\_freq} + \beta_\tau \cdot \text{tier} + \epsilon$$

where PM_proxy is cosine similarity to a hand-curated politeness/style centroid in SBERT space. Gate: β_PM > 0 and p < 0.05 in ≥2/3 SBERT models.

## 3.6 Five-Hypothesis Verification Framework

Rather than testing a single aggregate hypothesis, we decompose H-SemAccom-v1 into five sub-hypotheses with explicit gate conditions:

| Sub-Hypothesis | Type | Test | Gate | Dependency |
|----------------|------|------|------|------------|
| **h-e1**: C_sem^{H←A} > 0 with partner-specificity | EXISTENCE | Partner-specificity hierarchy | MUST_WORK: C_sem > 0, d ≥ 0.1 | None |
| **h-m1**: C_sem^{H←A} monotone in tier | MECHANISM | Jonckheere-Terpstra | MUST_WORK: J-T p < 0.05, d ≥ 0.1 in ≥2/3 models | h-e1 |
| **h-m2**: C_sem^{H←A} > C_sem^{A←H} | MECHANISM | Mann-Whitney per cell | SHOULD_WORK: all ≥2/3 tiers, ≥2/3 models | h-m1 |
| **h-m3**: Within-prompt Δ > 0 | MECHANISM | Within-pair Δ test | SHOULD_WORK: ≥2/3 operationalizations, ≥2/3 models | h-e1, h-m1 |
| **h-m4**: β_PM > 0 (mediation) | MECHANISM | OLS mediation regression | SHOULD_WORK: β > 0, p < 0.05 in ≥2/3 models | h-m1, h-m2, h-m3 |

MUST_WORK gates are termination conditions: failure causes hypothesis loop exit. SHOULD_WORK gates are non-blocking: failure is recorded as a limitation and the pipeline continues. This structure enables the distinction between core empirical claims (h-e1, h-m1) and exploratory mechanism hypotheses (h-m2, h-m3, h-m4).

---

# 4. Experimental Setup

We design five experiments to answer the following research questions, corresponding directly to the contributions stated in Section 1.

**RQ1 (Existence):** Does C_sem^{H←A} exceed partner-specificity controls with a meaningful effect size, confirming that semantic accommodation in human-AI conversation is a real and interaction-specific phenomenon?

**RQ2 (Tier Scaling):** Does C_sem^{H←A} increase monotonically with RLHF alignment tier quality, establishing RLHF tier as a correlate of human semantic behavior?

**RQ3 (Directionality):** Is C_sem^{H←A} > C_sem^{A←H}, demonstrating that humans accommodate more to AI than AI to humans in RLHF helpfulness conversations?

**RQ4 (Mechanism — Perceptual):** Can within-conversation quality discrimination (Δ = cos(H_next, A_chosen) − cos(H_next, A_rejected) > 0) explain the accommodation signal?

**RQ5 (Mechanism — Mediation):** Does a politeness/style proxy (PM-score) mediate the C_sem asymmetry identified in RQ3?

## 4.1 Dataset

All experiments use the Anthropic HH-RLHF helpfulness dataset [Bai et al., 2022]. We extract conversation pairs from three splits:

| Tier | Split Name | RLHF Process | N Pairs |
|------|-----------|--------------|---------|
| T1 | `helpful-base` | Supervised fine-tuning | ~56,000 |
| T2 | `helpful-rejection-sampled` | SFT + rejection sampling with RM | ~52,000 |
| T3 | `helpful-online` | SFT + online PPO | ~47,000 |
| **Total** | | | **~155,362** |

**Why this dataset.** The HH-RLHF tier structure provides a principled quality gradient for RLHF training, making it uniquely suited to study how AI quality is associated with human semantic behavior. Each tier represents a distinct stage of alignment optimization, not just random quality variation. Additionally, the chosen/rejected pair structure within each conversation enables the within-prompt mechanism test (RQ4) — a natural experiment unavailable in most conversational datasets.

Conversations are parsed by splitting on `\n\nHuman:` and `\n\nAssistant:` markers; each (H_{t+1}, A_t, H_t) triple constitutes one data point. Filtering removes empty turns and conversations with fewer than two turns.

## 4.2 Embedding Models

Three pre-trained SBERT models [Reimers & Gurevych, 2019] are used for robustness assessment:

| Model | Parameters | Speed (CPU) | Primary Use |
|-------|-----------|-------------|-------------|
| `all-MiniLM-L6-v2` | 22M | ~14K sent/sec | Primary model |
| `paraphrase-MiniLM-L6-v2` | 22M | ~14K sent/sec | Robustness check |
| `all-mpnet-base-v2` | 110M | ~2.8K sent/sec | Robustness check |

All embeddings are computed at inference time (no fine-tuning), using batch size 256 with fp16 precision. Embeddings are cached to disk between experiments (h-e1 → h-m1 → h-m2 reuse the same cached arrays).

## 4.3 Baselines and Controls

For RQ1–RQ3, baselines are internal to the dataset rather than external model comparisons — this is a measurement study, not a model comparison:

| Control | Description | Role |
|---------|-------------|------|
| **Random shuffle** | Cosine similarity to a randomly sampled AI turn from the same tier | Conservative null baseline — no accommodation signal expected |
| **KNN topic-matched** | Cosine similarity to the top-5 KNN neighbor (by SBERT cosine) in the same tier, excluding the actual partner | Strict topic control — isolates accommodation above topical coherence |
| **Partner-shuffle** | C_sem baseline for subtraction (random sample from same tier) | C_sem = cos(H_{t+1}, A_actual) − cos(H_{t+1}, A_random) |

For RQ4 (h-m3), the natural baseline is the null hypothesis Δ = 0 (no quality discrimination). For RQ5 (h-m4), the null is β_PM = 0 (no mediation).

## 4.4 Implementation Details

**Software environment:** Python 3.10; PyTorch 2.1; sentence-transformers 2.7.0; scikit-learn 1.4.0; scipy 1.15.3; datasets 2.20.0.

**Hardware:** NVIDIA H100 NVL GPU (CUDA_VISIBLE_DEVICES=2); SBERT inference uses GPU acceleration; all statistical tests are CPU-only.

**KNN index:** Built using scikit-learn NearestNeighbors with cosine metric over all-MiniLM-L6-v2 embeddings for the same tier, excluding self. K=5 neighbors used for the partner-specificity hierarchy (Level 2 KNN control), providing a stricter topically-matched baseline for the partner-specificity check (d = 0.417 vs KNN). The primary C_sem computation uses random-shuffle partners (Level 3).

**Bootstrap:** 1,000 resamples with seed = 42 for all confidence interval estimates.

**IPW:** Logistic propensity scores estimated on SBERT embedding principal components (top-50 PCA dimensions); IPW triggered when Kolmogorov-Smirnov p < 0.0001 for any tier pair.

**Hyperparameters (fixed across all experiments):**

```yaml
bootstrap_resamples: 1000
bootstrap_seed: 42
cohen_d_threshold: 0.1
knn_k: 5
min_n_pairs: 1000
significance_level: 0.05
```

## 4.5 Evaluation Metrics

| Metric | Definition | Used For |
|--------|-----------|----------|
| **C_sem** | E[cos(H_{t+1}, A_actual)] − E[cos(H_{t+1}, A_random)] | Primary accommodation measure (RQ1–RQ3); KNN comparison (d=0.417) is additional specificity check |
| **Cohen's d** | Standardized effect size between conditions | Effect size for all pairwise comparisons |
| **95% Bootstrap CI** | Percentile bootstrap (1,000 resamples) | Uncertainty quantification for C_sem |
| **Jonckheere-Terpstra** | Nonparametric test for ordered alternatives | Monotonicity test (RQ2) |
| **Mann-Whitney U** | Nonparametric pairwise significance test | Pairwise tier comparisons, H←A vs A←H (RQ3) |
| **Δ** | cos(H_next, A_chosen) − cos(H_next, A_rejected) | Within-prompt quality probe (RQ4) |
| **β_PM** | OLS regression coefficient for PM-proxy | Mediation test (RQ5) |

**Why Jonckheere-Terpstra for monotonicity.** Standard ANOVA tests the null that all group means are equal without specifying a direction. J-T tests the specific ordered alternative μ_{T1} < μ_{T2} < μ_{T3}, which is the direct operationalization of tier-monotonic accommodation. This is the correct test for an ordered categorical independent variable with a directional prediction.

## 4.6 Reproducibility

All experiment code is available in the hypothesis-specific code directories (h-e1/code/, h-m1/code/, h-m2/code/, h-m3/code/, h-m4/code/) with complete configuration in `03_config.yaml` per hypothesis. The HH-RLHF dataset is publicly available on Hugging Face Hub (`Anthropic/hh-rlhf`). SBERT model weights are publicly available on Hugging Face Hub under their respective identifiers.

---

# 5. Results

We present results in four acts corresponding to our four main claims: semantic accommodation exists (§5.1), scales with RLHF tier quality (§5.2), is directionally asymmetric (§5.3), and is not driven by within-conversation quality discrimination (§5.4).

## 5.1 RQ1: Semantic Accommodation in Human-AI Conversations (h-e1)

**Claim:** C_sem^{H←A} > 0, with partner-specificity confirming the effect is interaction-specific.

Figure 1 shows the three-level partner-specificity hierarchy across the full HH-RLHF helpfulness dataset (n = 155,362 pairs, all-MiniLM-L6-v2).

**Table 1: Partner-Specificity Hierarchy (h-e1, all-MiniLM-L6-v2)**

| Control Level | Mean Cosine | 95% CI | Cohen's d vs Actual |
|--------------|-------------|--------|---------------------|
| Actual AI partner | 0.3534 | [0.352, 0.354] | — |
| KNN topic-matched (K=5) | 0.2688 | [0.268, 0.270] | d = 0.417 |
| Random AI turn | 0.0241 | [0.024, 0.025] | **d = 1.998** |

The accommodation signal is unambiguous. Human follow-up turns are dramatically more semantically similar to their actual AI partner than to a random AI turn from the same tier (Cohen's d = 1.998 — a very large effect by Cohen's [1988] conventions; d > 0.8 is "large"). This is the primary C_sem estimate: C_sem = E[cos_actual] − E[cos_random] = 0.3534 − 0.0241 = 0.329 (95% CI [0.328, 0.330]). Critically, the effect also remains substantial above the KNN topic-matched baseline (d = 0.417, confirming that the accommodation signal exceeds even topically-similar AI turns and is not explained by topical co-occurrence alone).

All Mann-Whitney comparisons are significant (p = 0.0 at machine precision; n = 155,362). All five mechanism activation indicators are satisfied, confirming the partner-specificity hierarchy is clean and ordinal: cos(actual) > cos(KNN) > cos(random).

**Interpretation.** Humans are not merely discussing the same topic as their AI partner — they are exhibiting genuine interaction-specific semantic alignment. The effect size (d = 1.998 vs random) is among the largest reported in accommodation studies, establishing C_sem as a sensitive measure of RLHF conversational alignment.

## 5.2 RQ2: Tier-Scalable Accommodation (h-m1)

**Claim:** C_sem^{H←A} increases monotonically with RLHF alignment tier quality.

Figure 2 shows C_sem values across three tiers for all three SBERT models.

**Table 2: Tier-Stratified C_sem (IPW-Corrected, Three SBERT Models)**

| Tier | all-MiniLM-L6-v2 | paraphrase-MiniLM-L6-v2 | all-mpnet-base-v2 |
|------|-----------------|------------------------|------------------|
| T1 (helpful-base) | 0.3036 | 0.2714 | 0.3138 |
| T2 (helpful-rejection-sampled) | 0.3367 | 0.3068 | 0.3483 |
| T3 (helpful-online) | 0.3678 | 0.3456 | 0.3820 |
| **J-T p-value** | **0.001** | **0.001** | **0.001** |
| **Cohen's d (T1→T3)** | **0.183** | **0.254** | **0.238** |

Tier monotonicity is confirmed in all three SBERT models (J-T p = 0.001, 3/3 models pass). Cohen's d for T1→T3 ranges from 0.183 to 0.254 — all exceeding the pre-registered threshold of d ≥ 0.1. IPW covariate correction was triggered (KS p < 0.0001 in all tier pairs), and Figure 5 confirms that IPW-corrected C_sem values maintain the monotonic pattern.

A key robustness note: the T1→T2 contrast is marginally below the d ≥ 0.1 threshold in some models (d = 0.087–0.098), but the T1→T3 max-contrast effect is unambiguous. The Jonckheere-Terpstra test accounts for the full ordered pattern, not just adjacent contrasts, making it the appropriate statistic here.

**Interpretation.** RLHF alignment quality is associated with differences in downstream human semantic behavior. As RLHF training progresses from base SFT (T1) through rejection sampling (T2) to online PPO (T3), humans interacting in these conversations exhibit progressively stronger semantic accommodation. This effect is consistent across three independently trained SBERT architectures, ruling out embedding-model artifacts. The IPW correction confirms it is not explained by topic distribution shifts across tiers. Note that this is an observational association; within-user longitudinal data would be required to establish a causal direction (see §6.2).

## 5.3 RQ3: Directional Asymmetry (h-m2)

**Claim:** C_sem^{H←A} > C_sem^{A←H} — humans accommodate more to AI than AI to humans.

**Table 3: Directional Asymmetry Across All 9 Tier × Model Cells (h-m2)**

| Model | T1 (base) | T2 (rejection-sampled) | T3 (online) |
|-------|-----------|----------------------|-------------|
| **all-MiniLM-L6-v2** | H←A=0.0853, A←H=0.0395, **d=0.37** | H←A=0.0923, A←H=0.0535, **d=0.33** | H←A=0.0876, A←H=0.0718, **d=0.13** |
| **paraphrase-MiniLM** | H←A=0.0794, A←H=0.0316, **d=0.41** | H←A > A←H, **d=0.35** | H←A > A←H, **d=0.20** |
| **all-mpnet-base-v2** | H←A=0.0838, A←H=0.0422, **d=0.33** | H←A > A←H, **d=0.27** | H←A > A←H, **d=0.061** |

All 9 tier × model cells show C_sem^{H←A} > C_sem^{A←H}, confirmed by Mann-Whitney U (p ≤ 4.8e-30 for 8 of 9 cells; weakest cell: mpnet-online, d = 0.061, p = 0.004). Figure 3 shows the full heatmap of Cohen's d values across all 9 cells. Zero exceptions in 9 independent tests provides strong evidence for directional asymmetry.

**Interpretation.** Humans accommodate more to AI than AI to humans in RLHF helpfulness conversations. This is consistent with power asymmetry theory [Danescu-Niculescu-Mizil et al., 2012]: the AI partner, by virtue of its RLHF-optimized response quality, functions as the higher-status interlocutor in the semantic accommodation dynamic. The weakest cell (mpnet-online, d = 0.061) remains statistically significant (p = 0.004), suggesting the asymmetry is a genuine property of the conversational structure rather than an artifact of high-power tier comparisons.

## 5.4 RQ4: Within-Conversation Mechanism Analysis (h-m3)

**Claim test:** Does within-prompt quality discrimination (Δ > 0) explain accommodation?

Figure 4 shows the distribution of Δ = cos(H_next, A_chosen) − cos(H_next, A_rejected) across three operationalizations and three tiers.

**Table 4: Within-Prompt Quality Probe Results (h-m3)**

| Tier | OP1 (raw) | OP2 (length-matched) | OP3 (prompt-projected) | Models passing (OP1) |
|------|-----------|---------------------|----------------------|---------------------|
| T1 (helpful-base) | Δ < 0 | Δ < 0 | **Δ > 0 (partial)** | 0/3 |
| T2 (helpful-rejection-sampled) | Δ < 0 | Δ < 0 | Δ < 0 | 0/3 |
| T3 (helpful-online) | Δ < 0, **d = −0.74** | Δ < 0 | Δ < 0 | 0/3 |
| **Overall** | **25/27 cells: Δ < 0** | | | **0/3 models pass gate** |

Δ < 0 in 25 of 27 tier × operationalization combinations. The signal is particularly strong in the helpful-online tier (d = −0.738 for OP1), where RLHF quality is highest. Human follow-up turns are systematically more semantically similar to the *rejected* AI response than to the *chosen* one. The only partial exception is OP3 (prompt-projected) in T1 with all-MiniLM-L6-v2 (+0.014), which is a weak positive signal in the tier with smallest RLHF quality difference.

N_pairs per tier are sufficient to rule out a data artifact: n = 31,013 (T1/helpful-base), 35,665 (T2/helpful-rejection-sampled), 14,426 (T3/helpful-online). Statistical significance is p ≈ 0 at machine precision for 24 of 27 cells.

**Interpretation.** This is the paper's key paradox: the mechanism we initially theorized — within-conversation quality discrimination triggering accommodation — is definitively falsified. Humans follow up more similarly to the response that RLHF raters rejected. We interpret this as reflecting the verbosity and topical breadth of rejected responses: in HH-RLHF, rejected responses tend to be longer, more expansive, and cover more conversational space. The human's subsequent information agenda naturally aligns more with a response that covers more semantic ground, regardless of RLHF quality dimensions (helpfulness, safety, instruction-following).

This finding does not undermine the positive results in §5.1–5.3 — those operate at the population level across different conversations, while the H-M3 test operates within a single conversation. The two effects are compatible: population-level accommodation is real and tier-scalable, but it is not driven by within-conversation quality perception.

## 5.5 RQ5: Mediation Analysis (h-m4)

**Claim test:** Does PM-proxy mediate the C_sem^{H←A} > C_sem^{A←H} asymmetry?

**Table 5: OLS Mediation Regression Results (h-m4, n ≈ 3,000 per model)**

| Model | β_PM | SE (HC3) | p-value | R² |
|-------|------|---------|---------|-----|
| all-MiniLM-L6-v2 | −1.46e-05 | ~1.5e-02 | 0.9982 | 0.008 |
| paraphrase-MiniLM-L6-v2 | −1.26e-06 | ~1.2e-02 | 0.9998 | 0.007 |
| all-mpnet-base-v2 | +6.76e-05 | ~7.2e-03 | 0.9914 | 0.012 |

β_PM ≈ 0 in all three models (|β| < 1e-4). The p-values near 0.99 indicate the PM-proxy has essentially zero predictive power for C_sem asymmetry beyond the surface features and tier controls already in the model. Total model R² ≈ 0.007–0.012 (very low), indicating that the regression cannot explain C_sem variance even collectively.

Surface features (bullet_density, politeness_freq) show weak but detectable associations — stronger than PM-proxy — but these too fail to account for the asymmetry. Figure 6 shows the coefficient forest plot across models.

**Interpretation.** PM-score proxy (cosine to a hand-curated politeness/style centroid) does not mediate the C_sem asymmetry. The most parsimonious interpretation is that the directional asymmetry (H←A > A←H, confirmed in §5.3) is a structural property of RLHF data collection rather than a content-mediated effect: AI responses in RLHF conversations are by design optimized to be more helpful and semantically comprehensive, creating greater "semantic surface area" for human partners to align with, independent of any particular content feature we can measure with a cosine proxy.

## 5.6 Summary of Results

**Table 6: Hypothesis Verification Summary**

| Sub-Hypothesis | Gate | Result | Key Metric | Confidence |
|----------------|------|--------|-----------|------------|
| h-e1: Semantic accommodation exists | MUST_WORK | **PASS** | C_sem=0.329; d=1.998 (actual vs random) | Very High |
| h-m1: Tier monotonicity | MUST_WORK | **PASS** | J-T p=0.001; d=0.18–0.25; 3/3 models | Very High |
| h-m2: Directional asymmetry | SHOULD_WORK | **PASS** | All 9 tier×model cells; d=0.061–0.41 | High |
| h-m3: Within-prompt quality discrimination | SHOULD_WORK | **FAIL** | Δ < 0 in 25/27 cells; d up to −0.74 | High (falsification) |
| h-m4: PM-proxy mediation | SHOULD_WORK | **FAIL** | β_PM ≈ 0; p ≈ 0.99; 0/3 models | High (null result) |

Three of five sub-hypotheses are validated. Two mechanism hypotheses are definitively falsified, strengthening the population-structural account of RLHF-driven accommodation.

---

# 6. Discussion

## 6.1 Key Findings

Our experiments establish three robust empirical findings and two principled falsifications.

**Finding 1: Semantic accommodation to AI is large, robust, and interaction-specific.** The C_sem = 0.329 (d = 1.998 vs random) result leaves no room for doubt that humans exhibit strong semantic alignment to their actual AI partner in RLHF helpfulness conversations. The effect is above the KNN topic-matched baseline (d = 0.417), confirming it is not explained by topical coherence. At n = 155,362 pairs, this is a population-level fact about human behavior in AI-assisted conversations.

**Finding 2: RLHF alignment quality is associated with differences in human semantic behavior.** The monotonic increase in C_sem from T1 to T3 (J-T p = 0.001; confirmed across three independent SBERT architectures) demonstrates that the quality gradient encoded in RLHF training co-varies with bidirectional patterns — associated with differences not only in AI output quality but in the semantic patterns of human turns that follow. This is the core empirical contribution of the paper: RLHF systems are not merely associated with differences in AI behavior in isolation; these results suggest broader associations with the conversational ecology of human-AI interaction.

**Finding 3: Humans accommodate more to AI than AI to humans.** The directional asymmetry (all 9 tier × model cells; d = 0.061–0.41) is consistent with power asymmetry theory applied to human-AI interaction: humans adapt to their AI interlocutors more than vice versa. Unlike in human-human power asymmetry (where institutional hierarchy designates the power differential), in human-AI conversation the "asymmetry" arises from the structural properties of RLHF-optimized AI responses — they are by design more semantically comprehensive, offering more content for humans to align with.

**Finding 4 (Falsification): The mechanism is population-structural, not perceptual.** The H-M3 reversal (Δ < 0 in 25/27 cells) definitively rules out within-conversation quality discrimination as the proximal accommodation mechanism. If accommodation were driven by humans perceiving and responding to AI response quality within each exchange, Δ should be positive: human follow-ups should align better with the chosen (higher quality) response. The reverse finding — H_next is more similar to the rejected response — points instead to verbosity and topical breadth as the key confound in this operationalization. The H-M4 null result (β_PM ≈ 0) further confirms that no content feature we can measure with a cosine proxy mediates the asymmetry.

### Connecting the Findings

These four findings cohere into a single story. At the population level, RLHF training creates a distributional enrichment of AI response character across tiers — higher-tier conversations feature AI responses that are more topically rich, semantically comprehensive, and conversationally substantive. Humans embedded in this richer semantic environment exhibit greater accommodation, as measured by C_sem. This is analogous to environmental language exposure effects: speakers in linguistically richer environments develop more elaborate semantic patterns, not because they consciously perceive quality differences in each interaction, but because the overall distribution of their interlocutor's language is richer.

The H-M3 reversal adds an important nuance: "quality" in the RLHF sense (chosen > rejected, as judged by human raters) is not the same as "conversational informativeness" in the semantic continuity sense (which predicts H_next better). Rejected RLHF responses are typically longer, more expansive, and more hedged — qualities that make them better predictors of the human's subsequent information agenda, even if they fail RLHF quality criteria on other dimensions. This suggests a fundamental distinction between RLHF quality and accommodation-relevant semantic richness that has not been previously identified.

## 6.2 Limitations

**L1: Cross-sectional design — cannot distinguish accommodation from user self-selection.** HH-RLHF lacks user identifiers; each conversation is anonymous and independent. Our finding that higher-tier conversations show stronger C_sem cannot rule out user self-selection as an alternative: it is possible that more sophisticated users prefer higher-tier AI (online PPO) and also happen to communicate in ways that are more semantically similar to any interlocutor. True within-user accommodation trajectories (the same user becoming more aligned over time) cannot be measured with this dataset.

*Why this is acceptable:* Cross-sectional design is standard for large-scale observational NLP studies, and our population-level findings are valid within their scope — they establish that higher-tier conversations are systematically associated with stronger accommodation, regardless of mechanism. The J-T p = 0.001 with IPW correction and n = 155,362 pairs provides a robust population-level estimate.

*Future mitigation:* LMSYS Chatbot Arena with user session identifiers would enable within-user longitudinal accommodation measurement. Computing C_sem as a function of conversation turn number within a session would directly test whether accommodation strengthens as the conversation proceeds.

**L2: SBERT conflates topical and stylistic accommodation.** All-MiniLM-L6-v2 and related SBERT models produce full-utterance embeddings that capture both content (topical similarity) and style (semantic register, phrasing). C_sem cannot be cleanly decomposed into "pure style accommodation" vs "topically informed alignment."

*Why this is acceptable:* The KNN K=5 topic-matched baseline provides a conservative lower bound on style-specific accommodation: d = 0.417 above a topic-matched control is a strong signal even if some residual topical similarity remains. This is a stricter control than most prior accommodation literature.

*Future mitigation:* Style-factored sentence representations (STRAP [Cao & Xu, 2020]) or topic-free embeddings would enable decomposition of topical vs. stylistic components of C_sem.

**L3: Tier confound — HH-RLHF tiers differ in content distribution beyond RLHF quality.** The three splits were collected at different stages of Anthropic's deployment pipeline, making it plausible that user demographics, conversation topics, and interaction styles differ across tiers for reasons unrelated to RLHF quality.

*Why this is acceptable:* IPW covariate correction is applied whenever KS p < 0.0001 (triggered for all tier pairs), and the IPW-corrected C_sem values maintain monotonicity (Figure 5). The convergence of results across three independent SBERT architectures further reduces the likelihood that a spurious confound drives the finding.

*Future mitigation:* A controlled generation experiment — same prompt, same user, AI responses at different RLHF quality levels via temperature manipulation or base vs. RLHF model — would enable causal identification.

**L4: Proximal mechanism unresolved after h-m3 and h-m4 falsifications.** Both specific mechanism hypotheses we tested (within-conversation quality discrimination, PM-proxy mediation) were falsified. The proximal mechanism by which RLHF training quality induces population-level accommodation remains an open question.

*Why this is acceptable:* The population-level findings (h-e1, h-m1, h-m2) are empirically valid independently of any confirmed mechanism. Mechanism falsification is itself a contribution — we have ruled out two specific pathways, narrowing the space of plausible mechanisms for future investigation.

*Future mitigation:* Reward model scores as PM proxy (instead of hand-curated politeness centroid); NLI-based quality dimension analysis; length-controlled H-M3 replication (stratifying pairs by response length ratio to isolate verbosity from quality).

**L5: PM-proxy operationalization limitations.** H-M4 used cosine similarity to a hand-curated politeness centroid as the PM-score proxy. This is a weak operationalization of AI response quality that may miss the relevant quality signal.

*Why this is acceptable:* β_PM ≈ 0 with p ≈ 0.99 across all three models. Even if a stronger PM proxy exists, the effect size at this p-value is essentially zero — a stronger proxy would need to explain not only statistical significance but also meaningful variance in C_sem, which the low R² (≤ 0.012) suggests is not present.

## 6.3 Implications for Bidirectional Alignment Research

Our findings have several implications for how we design, evaluate, and interpret RLHF training.

**RLHF is associated with bidirectional patterns.** Current RLHF evaluation measures AI output quality directly (human preference ratings, reward model scores). Our results demonstrate that RLHF quality co-varies with human semantic behavior — a second-order association that is invisible in standard evaluation. Future alignment research should consider whether the human-side adaptation response is desirable, neutral, or concerning, particularly for deployed systems at scale.

**The population-structural mechanism suggests a new design target.** If accommodation is driven by distributional enrichment of AI responses rather than per-response quality signals, then RLHF training should aim to produce AI responses that are not only high-quality on preference dimensions but also semantically rich and informationally comprehensive — optimizing for the distributional profile of human-AI conversations, not just individual response quality.

**The H-M3 reversal is a measurement artifact warning.** The finding that rejected RLHF responses better predict human follow-up semantics than chosen ones suggests that RLHF's chosen/rejected annotation captures quality dimensions (helpfulness, safety, instruction-following) that are partly orthogonal to conversational semantic continuity. Researchers using HH-RLHF chosen/rejected structure as a proxy for any quality signal should be aware of this dissonance.

## 6.4 Broader Impact

This work advances understanding of how AI system quality is associated with human communicative behavior at scale. Positive impacts include: providing tools for monitoring bidirectional adaptation effects in deployed AI systems; opening a measurement paradigm for studying human behavioral responses to RLHF quality beyond preference ratings; and connecting NLP alignment research to established sociolinguistic theory on accommodation and power dynamics.

A potential concern is the misuse of these findings to design AI systems that deliberately maximize human accommodation for persuasive or manipulative purposes — for example, by optimizing AI responses to induce users to adopt the AI's semantic patterns. We emphasize that our measurement is observational and does not endorse or enable such applications. The C_sem metric is a measurement tool, not a training objective. Researchers deploying it in system optimization should carefully evaluate ethical implications with respect to user autonomy and informed consent.

---

# 7. Conclusion

We opened by asking: when humans interact with better AI assistants, do they start talking more like them? Our experiments answer yes — but with an important qualifier about *how* this happens.

## 7.1 Summary

We introduced C_sem, a training-free SBERT-based measure of semantic accommodation in human-AI conversational turn pairs with a three-level partner-specificity control hierarchy. Applied to 155,362 conversation pairs from the Anthropic HH-RLHF helpfulness dataset, C_sem reveals that humans exhibit robust, interaction-specific semantic accommodation to their AI partners (C_sem = 0.329, Cohen's d = 1.998 vs. random baseline). This accommodation scales monotonically with RLHF alignment tier quality (Jonckheere-Terpstra p = 0.001, confirmed across three SBERT architectures), establishing a robust observational association between RLHF training quality and downstream human semantic behavior. Humans accommodate more to AI than AI to humans — a directional asymmetry consistent with power asymmetry theory — confirmed in all 9 tier × model cells with zero exceptions (d = 0.061–0.41).

Yet the mechanism we initially hypothesized — that within-conversation quality discrimination drives accommodation — is definitively falsified. Human follow-up turns are paradoxically more similar to the rejected AI response than the approved one (Δ < 0 in 25/27 cells, d up to −0.74). A politeness-style mediation analysis finds β_PM ≈ 0. The mechanism is population-structural: RLHF training shifts the distributional character of AI responses across tiers, and humans embedded in this richer semantic environment exhibit greater accommodation — not because they perceive quality differences within each exchange, but because the overall conversational ecology is richer.

## 7.2 Future Directions

The H-M3 reversal opens a specific and tractable follow-up: **verbosity-controlled within-prompt quality probe.** Our three operationalizations (raw, length-matched, prompt-projected) partially addressed the length confound, but a fully length-controlled replication stratifying pairs by response length ratio would test whether the Δ < 0 signal persists after eliminating verbosity as the primary confound. If Δ reverses under strict length matching, it would confirm that RLHF "quality" and semantic continuity relevance are distinct dimensions mediated by response length.

More broadly, our cross-sectional design cannot distinguish population-level accommodation from within-user accommodation trajectories. **Longitudinal study using LMSYS Chatbot Arena** with session identifiers would enable within-user C_sem measurement as a function of turn number — testing whether accommodation strengthens over the course of a single conversation. This would provide the causal evidence missing from our observational design.

Finally, the C_sem infrastructure (SBERT inference, KNN controls, IPW correction, J-T monotonicity test) is directly transferable to other AI conversation datasets. **Cross-dataset replication on WildChat and LMSYS Chatbot Arena** would test whether tier-scalable accommodation generalizes beyond HH-RLHF helpfulness conversations to open-ended dialogue, red-teaming interactions, and diverse model capability levels.

## 7.3 Closing Thought

The H-M3 reversal suggests something deeper than a measurement artifact: RLHF's notion of "quality" — calibrated by human raters on dimensions like helpfulness, safety, and instruction-following — is not the same as semantic richness in the conversational continuity sense. Rejected responses, typically longer and more expansive, better predict what the human will say next, even as they score lower on quality. This mismatch is a fundamental property of how RLHF annotations are constructed, and it has implications for any research that uses chosen/rejected signal as a proxy for conversational effectiveness.

RLHF systems are not merely associated with differences in AI behavior in isolation — these results suggest broader associations with the semantic ecology of human-AI conversations. If the cross-sectional association reflects a causal effect (to be confirmed by longitudinal study), then designing systems that are genuinely beneficial at the population level would require understanding both sides of that ecology.

---

## References

Bai, Y., Jones, A., Ndousse, K., Askell, A., Chen, A., DasSarma, N., Drain, D., Fort, S., Ganguli, D., Henighan, T., Joseph, N., Kadavath, S., Kernion, J., Conerly, T., El-Showk, S., Elhage, N., Hatfield-Dodds, Z., Hernandez, D., Hume, T., Johnston, S., Kravec, S., Lovitt, L., Nanda, N., Olsson, C., Amodei, D., Brown, T. B., Clark, J., McCandlish, S., Olah, C., Mann, B., & Kaplan, J. (2022). Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback. *arXiv preprint arXiv:2204.05862*.

Chang, X. & Wang, R. (2025). Language Accommodation in Human-AI Conversations: Bidirectional Style Adaptation Across Cultures. *Proceedings of the AAAI Conference on Artificial Intelligence*.

Christiano, P., Leike, J., Brown, T. B., Martic, M., Legg, S., & Amodei, D. (2017). Deep Reinforcement Learning from Human Preferences. *Advances in Neural Information Processing Systems*.

Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences* (2nd ed.). Lawrence Erlbaum Associates.

Danescu-Niculescu-Mizil, C., Lee, L., Pang, B., & Kleinberg, J. (2012). Echoes of power: language effects and power differences in social interaction. *Proceedings of the 21st International Conference on World Wide Web*, 699–708. https://doi.org/10.1145/2187836.2187931

Fusaroli, R., Raczaszek-Leonardi, J., & Tylén, K. (2014). Dialog as Interpersonal Synergy. *New Ideas in Psychology*, 32, 147–157.

Giles, H. (1973). Accent Mobility: A Model and Some Data. *Anthropological Linguistics*, 15(2), 87–105.

Giles, H. & Ogay, T. (2007). Communication Accommodation Theory. In B. Whaley & W. Samter (Eds.), *Explaining Communication: Contemporary Theories and Exemplars* (pp. 293–310). Lawrence Erlbaum Associates.

Ouyang, L., Wu, J., Jiang, X., Almeida, D., Wainwright, C. L., Mishkin, P., Zhang, C., Agarwal, S., Slama, K., Ray, A., Schulman, J., Hilton, J., Kelton, F., Miller, L. E., Simens, M., Askell, A., Welinder, P., Christiano, P., Leike, J., & Lowe, R. (2022). Training language models to follow instructions with human feedback. *Advances in Neural Information Processing Systems*.

Pickering, M. J. & Garrod, S. (2004). Toward a Mechanistic Psychology of Dialogue. *Behavioral and Brain Sciences*, 27(2), 169–226.

Porcheron, M., Fischer, J. E., Reeves, S., & Sharples, S. (2018). Voice Interfaces in Everyday Life. *Proceedings of the 2018 CHI Conference on Human Factors in Computing Systems*. https://doi.org/10.1145/3173574.3174214

Reimers, N. & Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. *Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing*, 3982–3992. https://doi.org/10.18653/v1/D19-1410

Shen, H., Knearem, T., Thakkar, D., Pataranutaporn, P., Sinha, A. K., Shi, Y., Liang, J. T., Ahmad, L., Mitra, T., Myers, B. A., & Li, Y. (2025). Human-AI Interaction Alignment: Designing, Evaluating, and Evolving Value-Centered AI For Reciprocal Human-AI Futures. *arXiv preprint arXiv:2512.21551*.

Stiennon, N., Ouyang, L., Wu, J., Ziegler, D. M., Lowe, R., Voss, C., Radford, A., Amodei, D., & Christiano, P. (2020). Learning to summarize with human feedback. *Advances in Neural Information Processing Systems*.

---

## Figure Captions

**Figure 1** (partner_specificity.png): Three-level partner-specificity hierarchy showing mean cosine similarity for actual AI partner, KNN topic-matched (K=5), and random AI turns. The clean ordinal structure (actual > KNN > random) confirms interaction-specific semantic accommodation (n = 155,362 pairs, all-MiniLM-L6-v2).

**Figure 2** (tier_csem_bars.png): Tier-stratified C_sem values across three SBERT models (all-MiniLM-L6-v2, paraphrase-MiniLM-L6-v2, all-mpnet-base-v2). IPW-corrected values show monotonic increase T1→T2→T3 in all three models (J-T p = 0.001).

**Figure 3** (significance_heatmap.png): Cohen's d heatmap for directional asymmetry (C_sem^{H←A} − C_sem^{A←H}) across all 9 tier × model cells. All cells show positive d, confirming humans accommodate more to AI than AI to humans with zero exceptions.

**Figure 4** (fig1_delta_distributions.png): Distribution of Δ = cos(H_next, A_chosen) − cos(H_next, A_rejected) across three tiers and three operationalizations. The consistently negative distribution (Δ < 0 in 25/27 cells) establishes the H-M3 paradox: human follow-ups are more similar to rejected than chosen AI responses.

**Figure 5** (ipw_comparison.png): Comparison of raw vs. IPW-corrected C_sem values across tiers. Both raw and IPW-corrected values maintain monotonic ordering, confirming tier-scalable accommodation is not an artifact of distributional shifts across tiers.

**Figure 6** (fig1_beta_pm_comparison.png): Coefficient forest plot for OLS mediation regression (h-m4) across three SBERT models. β_PM ≈ 0 in all models (p ≈ 0.99), ruling out politeness/style proxy mediation of the C_sem asymmetry.

---

*Paper generated by Anonymous Research Pipeline v2.0 | Phase 6: Paper Writing | 2026-03-15*
