# Methodology

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

The core measurement challenge is separating interaction-specific accommodation from topical coherence: a human's follow-up turn will naturally be semantically similar to the preceding AI turn simply because they are discussing the same topic. C_sem addresses this by subtracting a topic-matched baseline:

$$C_{\text{sem}}^{H \leftarrow A} = \mathbb{E}\left[\cos\left(\text{SBERT}(H_{t+1}),\ \text{SBERT}(A_t)\right)\right] - \mathbb{E}\left[\cos\left(\text{SBERT}(H_{t+1}),\ \text{SBERT}(A_t^{\text{matched-shuffle}})\right)\right]$$

where $A_t^{\text{matched-shuffle}}$ is a topic-matched AI turn sampled from the same tier using KNN retrieval (K=5, cosine similarity in SBERT space), excluding the actual partner turn. The subtraction isolates accommodation above topical coherence: if the human's follow-up is specifically similar to *their* AI partner beyond what topic alone predicts, C_sem > 0.

**Rationale for partner-shuffle baseline.** A random shuffle baseline (computing cosine to a randomly sampled AI turn from the same tier) would leave a large topical confound in C_sem — pairs discussing cooking will be more similar to any cooking AI turn than to a random medical discussion turn. The KNN topic-matched baseline provides a stricter control by sampling AI turns that are semantically similar to the actual partner (top-5 cosine neighbors), then subtracting this similarity. This ensures C_sem measures genuine interaction-specific accommodation, not topic-level co-occurrence.

**Three-level partner-specificity hierarchy.** To validate C_sem as a measure of accommodation rather than topical overlap, we construct a three-level control hierarchy:
- Level 1: cos(H_{t+1}, A_actual) — actual partner (highest expected similarity)
- Level 2: cos(H_{t+1}, A_KNN) — topic-matched KNN neighbor (K=5)
- Level 3: cos(H_{t+1}, A_random) — random AI turn from same tier (lowest expected similarity)

Genuine accommodation predicts: Level 1 > Level 2 > Level 3, with the Level 1 − Level 2 gap representing interaction-specific accommodation above topical coherence.

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

The IPW-corrected C_sem values are compared to raw C_sem to verify that tier monotonicity is not an artifact of distributional shift (Figure 5).

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

**Figure 5** shows the IPW-corrected vs raw C_sem comparison, validating robustness to tier distributional shifts.
