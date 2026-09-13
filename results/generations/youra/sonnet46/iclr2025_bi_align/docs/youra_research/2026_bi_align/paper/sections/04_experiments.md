# Experimental Setup

We design five experiments to answer the following research questions, corresponding directly to the contributions stated in Section 1.

**RQ1 (Existence):** Does C_sem^{H←A} exceed partner-specificity controls with a meaningful effect size, confirming that semantic accommodation in human-AI conversation is a real and interaction-specific phenomenon?

**RQ2 (Tier Scaling):** Does C_sem^{H←A} increase monotonically with RLHF alignment tier quality, establishing RLHF tier as a driver of human semantic behavior?

**RQ3 (Directionality):** Is C_sem^{H←A} > C_sem^{A←H}, demonstrating that humans accommodate more to AI than AI to humans in RLHF helpfulness conversations?

**RQ4 (Mechanism — Perceptual):** Can within-conversation quality discrimination (Δ = cos(H_next, A_chosen) − cos(H_next, A_rejected) > 0) explain the accommodation signal?

**RQ5 (Mechanism — Mediation):** Does a politeness/style proxy (PM-score) mediate the CSEM asymmetry identified in RQ3?

## 4.1 Dataset

All experiments use the Anthropic HH-RLHF helpfulness dataset [Bai et al., 2022]. We extract conversation pairs from three splits:

| Tier | Split Name | RLHF Process | N Pairs |
|------|-----------|--------------|---------|
| T1 | `helpful-base` | Supervised fine-tuning | ~56,000 |
| T2 | `helpful-rejection-sampled` | SFT + rejection sampling with RM | ~52,000 |
| T3 | `helpful-online` | SFT + online PPO | ~47,000 |
| **Total** | | | **~155,362** |

**Why this dataset.** The HH-RLHF tier structure provides a principled quality gradient for RLHF training, making it uniquely suited to study how AI quality affects human semantic behavior. Each tier represents a distinct stage of alignment optimization, not just random quality variation. Additionally, the chosen/rejected pair structure within each conversation enables the within-prompt mechanism test (RQ4) — a natural experiment unavailable in most conversational datasets.

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
| **Partner-shuffle** | C_sem baseline for subtraction (KNN K=5) | C_sem = cos(H_{t+1}, A_actual) − cos(H_{t+1}, A_KNN) |

For RQ4 (h-m3), the natural baseline is the null hypothesis Δ = 0 (no quality discrimination). For RQ5 (h-m4), the null is β_PM = 0 (no mediation).

## 4.4 Implementation Details

**Software environment:** Python 3.10; PyTorch 2.1; sentence-transformers 2.7.0; scikit-learn 1.4.0; scipy 1.15.3; datasets 2.20.0.

**Hardware:** NVIDIA H100 NVL GPU (CUDA_VISIBLE_DEVICES=2); SBERT inference uses GPU acceleration; all statistical tests are CPU-only.

**KNN index:** Built using scikit-learn NearestNeighbors with cosine metric over all-MiniLM-L6-v2 embeddings for the same tier, excluding self. K=5 neighbors used for partner-shuffle baseline construction.

**Bootstrap:** 1,000 resamples with seed = 42 for all confidence interval estimates.

**IPW:** Logistic propensity scores estimated on SBERT embedding principal components (top-50 PCA dimensions); IPW triggered when Kolmogorov-Smirnov p < 0.0001 for any tier pair.

**Hyperparameters (fixed across all experiments):**

```yaml
bootstrap_resamples: 1000
bootstrap_seed: 42
cohen_d_threshold: 0.1
knn_k: 5
min_n_pairs: 1000     # Minimum per tier for RQ4
significance_level: 0.05
```

## 4.5 Evaluation Metrics

| Metric | Definition | Used For |
|--------|-----------|----------|
| **C_sem** | E[cos(H_{t+1}, A_actual)] − E[cos(H_{t+1}, A_KNN)] | Primary accommodation measure (RQ1–RQ3) |
| **Cohen's d** | Standardized effect size between conditions | Effect size for all pairwise comparisons |
| **95% Bootstrap CI** | Percentile bootstrap (1,000 resamples) | Uncertainty quantification for C_sem |
| **Jonckheere-Terpstra** | Nonparametric test for ordered alternatives | Monotonicity test (RQ2) |
| **Mann-Whitney U** | Nonparametric pairwise significance test | Pairwise tier comparisons, H←A vs A←H (RQ3) |
| **Δ** | cos(H_next, A_chosen) − cos(H_next, A_rejected) | Within-prompt quality probe (RQ4) |
| **β_PM** | OLS regression coefficient for PM-proxy | Mediation test (RQ5) |

**Why Jonckheere-Terpstra for monotonicity.** Standard ANOVA tests the null that all group means are equal without specifying a direction. J-T tests the specific ordered alternative μ_{T1} < μ_{T2} < μ_{T3}, which is the direct operationalization of tier-monotonic accommodation. This is the correct test for an ordered categorical independent variable with a directional prediction.

**Why Mann-Whitney for pairwise tests.** SBERT cosine similarity distributions are not guaranteed to be normally distributed. Mann-Whitney U is a nonparametric test that makes no distributional assumptions, appropriate for large-n, non-Gaussian data.

## 4.6 Reproducibility

All experiment code is available in the hypothesis-specific code directories (h-e1/code/, h-m1/code/, h-m2/code/, h-m3/code/, h-m4/code/) with complete configuration in `03_config.yaml` per hypothesis. The HH-RLHF dataset is publicly available on Hugging Face Hub (`Anthropic/hh-rlhf`). SBERT model weights are publicly available on Hugging Face Hub under their respective identifiers.
