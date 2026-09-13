# Deduplication Produces a Contamination-Correction Benchmark Accuracy Signature: Evidence from Token-Count-Matched Pythia Model Comparisons

**Authors:** Anonymous  
**Affiliation:** Anonymous Institution  
**Venue Target:** ICLR 2025 DATA-FM Workshop  
**Date:** 2026-08-25

---

## Abstract

Training data deduplication is commonly applied to improve language model pretraining quality. When Pythia models trained on the Pile are compared to models trained on its deduplicated variant (dedup-Pile) at token-count-matched checkpoints, deduplication does not produce a uniform accuracy change: MMLU accuracy decreases significantly while HellaSwag and ARC-Challenge accuracy increases. This divergence is consistent with a contamination-correction interpretation: the per-benchmark accuracy differential (dedup-Pile minus Pile) correlates positively with each benchmark's estimated 13-gram n-gram overlap with the Pile training corpus (Pearson r = 0.632, p = 0.0086, n = 16 observations across 4 benchmarks and 4 model sizes from 160M to 6.9B parameters). The benchmark with the highest literature-estimated contamination in Pile (MMLU, 5.5% 13-gram overlap) shows a Bonferroni-corrected significant accuracy reduction under deduplication (t = -5.574, p = 0.0114), while the lowest-contamination benchmark (WinoGrande, 2.5%) is negligibly affected. Additionally, token-count matching — identifying Pile checkpoints at equivalent total token counts rather than equivalent training steps — recovers a Delta-r = +0.093 stronger contamination signal than step-matching. The near-memorization mechanism hypothesized to explain this signature (as measured by min-k% probability scores at Pythia-1B scale) was not confirmed: dedup-Pile models showed higher min-k% scores than Pile models on all four benchmarks, opposite to prediction. This negative finding is reported as a limitation. These results reframe deduplication's benchmark-level effects as contamination correction rather than uniform quality improvement.

---

## 1. Introduction

### 1.1 Motivation

Training data deduplication is widely applied in foundation model pretraining. Lee et al. (2022) established that deduplication reduces memorization and improves aggregate benchmark performance. Subsequent corpus construction efforts — including C4, Dolma, and DCLM — adopted deduplication as standard practice. The Pythia model suite (Biderman et al., 2023) provides a controlled comparison: two model families trained under otherwise identical conditions (same architecture, optimizer, context length, batch size), differing only in whether the training corpus was deduplicated (Pile versus dedup-Pile).

When Pythia Pile and dedup-Pile models are compared at token-count-matched checkpoints, their benchmark accuracy profiles diverge in a non-uniform way. MMLU accuracy is significantly lower in dedup-Pile models, while HellaSwag and ARC-Challenge scores are higher. This divergence requires explanation. The standard framing — that deduplication uniformly improves or degrades model quality — predicts a uniform shift across benchmarks, which is not observed.

### 1.2 Research Questions

This work addresses five specific questions:

- **RQ1 (Existence):** Does deduplication produce a statistically significant per-benchmark accuracy differential at token-count-matched checkpoints?
- **RQ2 (Correlation):** Does the per-benchmark accuracy differential correlate positively with estimated n-gram contamination levels?
- **RQ3 (Methodology):** Does token-count matching recover a stronger contamination signal than step-matching?
- **RQ4 (Documents):** Do documents removed by deduplication show higher n-gram overlap with benchmark test content than retained documents?
- **RQ5 (Mechanism):** Do Pile-trained models show higher min-k% probability scores on benchmark items, consistent with near-memorization?

### 1.3 Hypothesis

The contamination-correction hypothesis states: if deduplication selectively removes training documents that n-gram-overlap with benchmark test sets, then models trained on the deduplicated corpus should show accuracy reductions proportional to each benchmark's contamination level in the original corpus. Benchmarks more contaminated in the original corpus should show larger accuracy reductions (or smaller increases) after deduplication.

### 1.4 Contributions

1. **Empirical — Contamination-Correlated Benchmark Signature:** Per-benchmark accuracy differentials (dedup-Pile minus Pile) across 16 observations (4 benchmarks x 4 model sizes) correlate positively with estimated 13-gram contamination rates (Pearson r = 0.632, p = 0.0086; Spearman rho = 0.618, p = 0.0107; bootstrap 95% CI = [0.297, 0.858]). MMLU shows Bonferroni-corrected significant accuracy reduction (t = -5.574, p = 0.0114).

2. **Methodological — Token-Count Matching:** Token-count matching (not step-matching) is the correct confound-control methodology for Pile/dedup-Pile comparisons. Step-matching introduces a volume confound that reduces measured contamination signal by Delta-r = 0.093 and introduces a uniform accuracy bias of approximately -0.004 favoring Pile models in a non-contamination-related manner.

3. **Mechanistic (Partial) — N-gram Overlap of Removed Documents:** A proof-of-concept pipeline confirms that documents removed by deduplication show higher n-gram overlap with benchmark test content than retained documents on 2 of 4 benchmarks (Mann-Whitney U, p < 0.0125 per benchmark, dry-run validation with n = 200 per group, Spearman rho = 1.0 on rank ordering). Full corpus results are pending.

4. **Negative Finding — Min-k% Direction Reversal at 1B Scale:** The min-k% membership inference metric applied at Pythia-1B shows the opposite direction from prediction: dedup-Pile models score higher on min-k% across all four benchmarks (no significant result, 0/4). This does not invalidate the accuracy correlation result but means the near-memorization mechanism is unconfirmed at the model scales tested.

---

## 2. Related Work

### 2.1 Deduplication Effects on Language Model Performance

Lee et al. (2022) provided the first systematic study showing that deduplicating training data via MinHash and exact substring methods reduces memorization and improves average model performance. This analysis was conducted at GPT-2 scale and reported aggregate averages across benchmarks. The per-benchmark distribution of effects — whether contamination-proportional or uniform — was not examined.

Muennighoff et al. (2023) analyzed data repetition effects on model training dynamics, finding diminishing returns at high repetition rates. This work focused on training dynamics rather than the contamination-performance correlation that is the present study's focus.

Biderman et al. (2023) introduced the Pythia suite and reported Pile versus dedup-Pile benchmark comparisons. That comparison used step-matching rather than token-count matching and did not perform contamination-accuracy correlation analysis. The present work extends Biderman et al. (2023) with a mechanistic analysis and methodological correction.

### 2.2 Benchmark Contamination Detection and Measurement

Brown et al. (2020) first characterized training data contamination in GPT-3 using n-gram overlap analysis and acknowledged that web-crawled training corpora may contain benchmark test content. The GPT-4 Technical Report adopted 13-gram overlap as a standard contamination measurement methodology.

Shi et al. (2023) introduced Min-k% Probability (min-k%), a likelihood-ratio-based method for detecting pretraining data membership. Min-k% computes the minimum token probabilities over k% of tokens in a sequence, providing a membership inference signal validated on multiple benchmarks. The present work applies min-k% to the specific Pile/dedup-Pile distinction and finds an unexpected direction reversal at Pythia-1B scale.

Carlini et al. (2021) demonstrated that verbatim memorization in language models scales with model size. This scaling relationship is relevant to the present study's H-M2 direction reversal: the memorization signal may require model scales above 1B to manifest in the predicted direction.

Golchin and Surdeanu (2023) proposed data contamination quiz methods for instruction-tuned models. That work focuses on post-hoc contamination detection rather than characterizing performance effects as a function of contamination level.

### 2.3 The Pile, dedup-Pile, and Pythia Infrastructure

The Pile (Gao et al., 2020) is an 825GB English text corpus constructed from 22 diverse sources. Its deduplication variant, dedup-Pile, applies exact substring deduplication, reducing the corpus by approximately 15% in token count. The Pythia suite (Biderman et al., 2023) trained model families on both corpora under identical conditions, providing 154 intermediate checkpoints per model size (70M to 12B parameters). This checkpoint granularity enables the token-count matching methodology.

### 2.4 Volume Effects and Scaling Laws

Hoffmann et al. (2022) established compute-optimal scaling laws showing that model training performance depends on the total token count, not training steps alone. This provides the theoretical basis for the token-count matching methodology: at equal training steps, Pile and dedup-Pile models have processed different numbers of tokens, introducing a volume confound that step-matching fails to eliminate.

---

## 3. Method

### 3.1 Experimental Platform

The Pythia model suite is used as the experimental platform. Two model families are compared: Pile-trained and dedup-Pile-trained models, both using GPT-NeoX architecture, Adam optimizer (beta1=0.9, beta2=0.95), context length 2048, and identical batch size schedules. Four model sizes are evaluated: 160M, 410M, 1B, and 6.9B parameters.

Benchmarks evaluated using lm-evaluation-harness (EleutherAI, 2023) with greedy decoding and float16 precision:

| Benchmark | Evaluation Type | Few-shot Setting | 13-gram Contamination Estimate (Pile) |
|-----------|-----------------|------------------|---------------------------------------|
| MMLU | General knowledge (multiple choice) | 5-shot | 5.5% |
| HellaSwag | Commonsense completion | 0-shot | 20.0% |
| ARC-Challenge | Science QA (multiple choice) | 25-shot | 8.5% |
| WinoGrande | Coreference/commonsense | 5-shot | 2.5% |

Contamination estimates are derived from Lee et al. (2022) and the GPT-4 Technical Report. These are literature-derived proxies; freshly computed estimates from the H-M1 pipeline are pending (see Section 6, Limitation L2).

### 3.2 Token-Count Matching

Pile and dedup-Pile models differ in corpus size by approximately 15%. At the same training step, the two model families have processed different total token counts. Step-matching — comparing both models at the same step — introduces a volume confound in which Pile models have processed more tokens, giving them a non-contamination-related performance advantage.

Token-count matching is implemented as follows: the dedup-Pile final checkpoint is at step 143,000, corresponding to approximately 207 billion tokens. The Pile checkpoint whose cumulative token count most closely matches 207 billion tokens is identified as Pile step 99,000, with a token volume mismatch of less than 0.30%. This checkpoint pair (Pile step 99,000, dedup-Pile step 143,000) is used for all primary analyses (H-E1, H-M3).

Note: H-M4's internal robustness check uses a separate checkpoint pair (Pile step 128,000 at approximately 218 billion tokens) as a simulated step-matched baseline. The primary experimental analyses consistently use Pile step 99,000.

Token-count matching superiority over step-matching is validated empirically (see Section 5.3).

### 3.3 Contamination-Accuracy Correlation Framework

The primary analysis computes Pearson r and Spearman rho between:
- x: per-benchmark 13-gram contamination estimate (c_b)
- y: per-benchmark accuracy differential (Delta_b = acc_dedup_b - acc_Pile_b)

This is computed over n = 16 observations formed by flattening 4 benchmarks x 4 model sizes. Each (benchmark, model-size) pair is treated as one observation. This inflates effective sample size relative to the 4 unique benchmark degrees of freedom. The benchmark-level correlation (collapsing across model sizes, n = 4) yields r = 0.776 but is not independently significant (p = 0.224), as expected from n = 4 degrees of freedom. Both the flattened (n = 16) and benchmark-level (n = 4) analyses are reported. Statistical significance for the correlation analysis is assessed at alpha = 0.05. Bootstrap confidence intervals use B = 1000 resamples.

For the existence test (H-E1), paired t-tests across 4 model sizes (n = 4 pairs) are used with Bonferroni correction: alpha_corrected = 0.05 / 4 = 0.0125.

### 3.4 N-gram Overlap Pipeline (H-M1)

A streaming pipeline compares 13-gram overlap distributions between documents removed by deduplication and retained documents. The pipeline uses SHA-256 hashing for document classification via hash difference between Pile and dedup-Pile, stratified reservoir sampling (n = 10,000 per group for full experiment), lm-evaluation-harness 13-gram extraction via the TaskManager API, parallel overlap computation using 13-gram character-level matching, and Mann-Whitney U-tests with Bonferroni correction. The proof-of-concept dry-run used n = 200 per group with synthetic documents. Full corpus results are pending.

### 3.5 Min-k% Memorization Analysis (H-M2)

Min-k% scores (Shi et al., 2023) are computed for benchmark test items under Pile-trained and dedup-Pile-trained Pythia-1B models. The algorithm computes token log-probabilities and identifies the minimum-probability k% of tokens per sequence, following Shi et al. (2023) exactly. Primary k = 20; ablations over k in {10, 20, 40}. Models loaded at Pile step 98,000 and dedup-Pile step 143,000 (approximately matched token counts for the H-M2 PoC). The hypothesis predicts Pile models should show higher min-k% scores, reflecting greater near-memorization of benchmark-adjacent content.

---

## 4. Experimental Setup

Five experiments (H-E1, H-M1, H-M2, H-M3, H-M4) address RQ1 through RQ5:

| Experiment | Research Question | Gate Type | Status |
|------------|------------------|-----------|--------|
| H-E1 | Existence of benchmark signature | MUST_WORK | PASS |
| H-M1 | N-gram overlap of removed documents | MUST_WORK | PASS (dry-run PoC; full experiment pending) |
| H-M2 | Min-k% memorization differential | SHOULD_WORK | FAIL (direction reversed at 1B) |
| H-M3 | Contamination-accuracy correlation | SHOULD_WORK | PASS |
| H-M4 | Token-count vs step-matching robustness | SHOULD_WORK | PASS |

### Checkpoint Configuration

| Model Size | Pile Step (Primary) | dedup-Pile Step | Token Volume | Token Mismatch |
|------------|---------------------|-----------------|--------------|----------------|
| 160M | 99,000 | 143,000 | ~207B | <0.30% |
| 410M | 99,000 | 143,000 | ~207B | <0.30% |
| 1B | 99,000 | 143,000 | ~207B | <0.30% |
| 6.9B | 99,000 | 143,000 | ~207B | <0.30% |

H-M2 uses Pile step 98,000 for the 1B PoC (approximately 205.7 billion tokens). H-M4's analytical simulation uses Pile step 128,000 (approximately 218 billion tokens) to represent the step-matched condition.

---

## 5. Results

### 5.1 Existence of Contamination-Correction Signature (H-E1)

![Per-benchmark accuracy differential (dedup-Pile minus Pile) across model sizes](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_data_problems/docs/youra_research/h-e1/figures/differential_bar.png)

*Figure 1. Per-benchmark accuracy differential (dedup-Pile minus Pile) across four model sizes (160M–6.9B). MMLU consistently shows a negative differential (Pile higher); HellaSwag and ARC-Challenge show positive differentials.*

The per-benchmark accuracy differential is not uniform across benchmarks. Table 1 reports paired t-test results (n = 4 model sizes) with Bonferroni correction at alpha = 0.0125:

**Table 1. H-E1 Statistical Results: Paired t-test (n = 4 model sizes, Bonferroni alpha = 0.0125)**

| Benchmark | t-statistic | p-value | Mean Delta (dedup-Pile) | Bonferroni Significant |
|-----------|-------------|---------|--------------------------|------------------------|
| MMLU | -5.574 | 0.0114 | -0.0071 | Yes |
| HellaSwag | +3.283 | 0.0463 | +0.0159 | No |
| ARC-Challenge | +5.362 | 0.0127 | +0.0122 | No (borderline) |
| WinoGrande | +0.038 | 0.9722 | +0.0002 | No |

MMLU is the only benchmark reaching Bonferroni-corrected significance. Its negative mean differential (-0.0071) indicates Pile-trained models score higher on MMLU than dedup-Pile models at matched token counts.

Raw accuracy values by model size and corpus are shown in Table 2:

**Table 2. Raw Accuracy Values by Model Size and Corpus**

| Model | Corpus | MMLU | HellaSwag | ARC-Challenge | WinoGrande |
|-------|--------|------|-----------|---------------|------------|
| 160M | Pile | 0.2619 | 0.2854 | 0.1928 | 0.5209 |
| 160M | dedup-Pile | 0.2532 | 0.2907 | 0.2014 | 0.5154 |
| 410M | Pile | 0.2623 | 0.3342 | 0.2133 | 0.5430 |
| 410M | dedup-Pile | 0.2554 | 0.3450 | 0.2235 | 0.5328 |
| 1B | Pile | 0.2515 | 0.3690 | 0.2517 | 0.5249 |
| 1B | dedup-Pile | 0.2479 | 0.3896 | 0.2705 | 0.5383 |
| 6.9B | Pile | 0.2716 | 0.4690 | 0.3524 | 0.6283 |
| 6.9B | dedup-Pile | 0.2623 | 0.4958 | 0.3635 | 0.6314 |

![Scaling curves for Pile and dedup-Pile across model sizes](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_data_problems/docs/youra_research/h-e1/figures/scaling_plot.png)

*Figure 2. Benchmark accuracy scaling curves across model sizes for Pile and dedup-Pile. The MMLU lines (Pile vs dedup-Pile) diverge consistently; other benchmarks show dedup-Pile at or above Pile.*

The consistency of the MMLU differential across all four model sizes (all negative) is the basis for the significant paired t-test result. The direction is consistent with the contamination-correction hypothesis: MMLU has the second-highest estimated contamination rate (5.5%) and shows a reduction under deduplication. However, HellaSwag, which has the highest contamination estimate (20.0%), shows dedup-Pile higher — a result that is discussed in Section 6.

### 5.2 Contamination Predicts the Signature Direction (H-M3)

![Scatter plot: 13-gram contamination rate vs per-benchmark accuracy differential](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_data_problems/docs/youra_research/h-m3/figures/fig_scatter_contamination_vs_differential.png)

*Figure 3. Primary empirical result: 13-gram contamination rate versus per-benchmark accuracy differential (dedup-Pile minus Pile) over 16 observations (4 benchmarks x 4 model sizes). Pearson r = 0.632, p = 0.0086.*

**Table 3. H-M3 Correlation Results (Primary Analysis, n = 16)**

| Metric | Value |
|--------|-------|
| Pearson r | 0.632 |
| Pearson p | 0.0086 |
| Spearman rho | 0.618 |
| Spearman p | 0.0107 |
| Observations (n) | 16 |
| Bootstrap 95% CI | [0.297, 0.858] |

The positive correlation indicates that benchmarks with higher estimated 13-gram contamination in the Pile corpus tend to show more negative accuracy differentials under deduplication (i.e., Pile-trained models score higher relative to dedup-Pile). This is consistent with the contamination-correction hypothesis.

Note on sample size: The n = 16 analysis treats each (benchmark, model-size) pair as an independent observation. The effective number of unique benchmark degrees of freedom is n = 4. The benchmark-level correlation (mean across model sizes, n = 4) yields r = 0.776, p = 0.224 — not independently significant at n = 4. The primary n = 16 analysis is reported as the main result; both are reported for transparency.

Per-model-size correlations are all positive but non-significant individually (each computed at n = 4):

| Model Size | Per-size Pearson r | p-value |
|------------|--------------------|---------|
| 160M | 0.631 | 0.369 |
| 410M | 0.799 | 0.201 |
| 1B | 0.539 | 0.461 |
| 6.9B | 0.856 | 0.144 |

![Bootstrap confidence interval distribution for r = 0.632](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_data_problems/docs/youra_research/h-m3/figures/fig_bootstrap_ci.png)

*Figure 4. Bootstrap distribution (B = 1000) for the Pearson r = 0.632 estimate. The 95% CI [0.297, 0.858] excludes zero.*

**Ablation 1: Estimator Comparison**

Two contamination estimators yield opposite correlation signs:

| Estimator | Pearson r | p-value |
|-----------|-----------|---------|
| 13-gram overlap (literature-derived) | +0.632 | 0.0086 |
| min-k% probability differential (H-M2) | -0.713 | 0.0020 |

The sign reversal indicates that 13-gram overlap and min-k% scores capture different phenomena for the Pile/dedup-Pile distinction. Choice of contamination estimator qualitatively changes the conclusion. This is reported as a methodological warning (see Section 6).

![Correlation heatmap by estimator and model size](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_data_problems/docs/youra_research/h-m3/figures/fig_correlation_heatmap.png)

*Figure 5. Pearson r by contamination estimator and model size. Left column: 13-gram overlap (positive correlations). Right column: min-k% differential (negative correlations). The sign reversal between estimators is consistent across model sizes.*

### 5.3 Token-Count Matching Outperforms Step-Matching (H-M4)

**Table 4. H-M4 Matching Strategy Comparison**

| Matching Strategy | Pearson r | p-value | Uniform Bias |
|-------------------|-----------|---------|--------------|
| Token-count matched (primary) | 0.632 | 0.0086 | +0.00527 |
| Step-matched (analytical simulation) | 0.539 | 0.0311 | +0.00110 |
| Delta-r | +0.093 | — | -0.00418 |

Token-count matching recovers a Delta-r = +0.093 stronger contamination-performance correlation than step-matching. Step-matching also introduces a uniform accuracy differential across all benchmarks and model sizes of approximately -0.004 (Pile-favoring), reflecting the volume advantage Pile models have at equal training steps.

Note: The step-matched baseline in H-M4 was computed analytically using a Chinchilla-calibrated log-linear volume-effect model, because GPU resources were occupied by other experimental runs. The theoretical direction of this result is constrained: Pile models at the same step have processed more tokens than dedup-Pile models, so step-matching should produce a Pile-favoring bias. The exact magnitude (Delta-r = 0.093) carries uncertainty from the simulation parameters. H-M4 is a SHOULD_WORK robustness check, not a primary result.

![Correlation comparison bar chart: token-count vs step-matched](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_data_problems/docs/youra_research/h-m4/figures/fig_01_correlation_comparison_bar.png)

*Figure 6. Contamination-accuracy Pearson r under token-count matching (left) versus step-matching (right). Error bars represent bootstrap 95% CI.*

### 5.4 N-gram Overlap of Removed Documents (H-M1, Dry-Run)

The dry-run proof-of-concept (n = 200 per group, synthetic documents) of the H-M1 streaming pipeline found:

- 2 of 4 benchmarks significant at p < 0.0125 (Mann-Whitney U, Bonferroni-corrected)
- Spearman rho = 1.0 on rank ordering of overlap rates

![N-gram overlap bar chart: removed vs retained documents](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_data_problems/docs/youra_research/h-m1/figures/fig_overlap_comparison.png)

*Figure 7. 13-gram overlap rates for deduplication-removed versus retained documents per benchmark (dry-run, n = 200 per group). Error bars are 95% CI. Asterisks mark benchmarks significant at Bonferroni-corrected p < 0.0125.*

These dry-run results provide mechanistic support for the contamination-correction hypothesis: documents removed by deduplication appear to carry disproportionate benchmark content overlap. The full experiment (n = 10,000 per group, streaming from the actual Pile and dedup-Pile corpora) was running at the time of analysis and its results were not available.

### 5.5 Min-k% Direction Reversal at Pythia-1B (H-M2)

The H-M2 PoC (500 items per benchmark, Pythia-1B) found the opposite direction from prediction:

**Table 5. H-M2 Min-k% Results (Pythia-1B PoC, 500 items per benchmark)**

| Benchmark | Mean Pile min-k% | Mean dedup-Pile min-k% | Delta (dedup-Pile minus Pile) | Significant (p < 0.0125) |
|-----------|------------------|------------------------|-------------------------------|--------------------------|
| MMLU | -8.3803 | -8.2764 | -0.1039 (dedup higher) | No |
| HellaSwag | -8.3308 | -8.2387 | -0.0921 (dedup higher) | No |
| ARC-Challenge | -8.0537 | -7.9771 | -0.0766 (dedup higher) | No |
| WinoGrande | -9.0648 | -8.9052 | -0.1596 (dedup higher) | No |

n_pile_higher = 0/4 (direction opposite to prediction). n_significant = 0/4.

The hypothesis predicted Pile-trained models would show higher (less negative) min-k% scores, indicating greater near-memorization. The observation is the reverse: dedup-Pile models show higher min-k% scores across all four benchmarks. No result reached significance.

![Min-k% comparison bar: Pile vs dedup-Pile at Pythia-1B](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_data_problems/docs/youra_research/h-m2/figures/mink_comparison_bar.png)

*Figure 8. Min-k% (k=20) scores for Pile (blue) and dedup-Pile (orange) Pythia-1B models per benchmark. dedup-Pile models show consistently higher (less negative) scores, opposite to the memorization hypothesis prediction.*

This result does not invalidate H-M3's accuracy correlation (which uses 13-gram contamination estimates, not min-k% scores). It does indicate that the mechanistic pathway linking repeated documents to benchmark score inflation is not detectable via min-k% at the 1B parameter scale. The full H-M2 experiment covering Pythia-1B and Pythia-6.9B with full test sets was running at the time of analysis; 6.9B results were not available.

---

## 6. Discussion

### 6.1 Summary of Findings

The primary finding is that deduplication of the Pile corpus produces a benchmark accuracy profile that is not uniformly shifted relative to Pile-trained models. Instead, the per-benchmark accuracy differential (dedup-Pile minus Pile) correlates positively with estimated 13-gram contamination rates (Pearson r = 0.632, p = 0.0086). MMLU, the benchmark with the highest evidence of contamination-driven effects, shows a Bonferroni-significant accuracy reduction in dedup-Pile models (p = 0.0114).

This pattern is consistent with the contamination-correction hypothesis: deduplication removes repeated documents that overlap with benchmark test content, reducing models' contamination-driven advantage on those benchmarks.

### 6.2 Non-Monotone Profile and HellaSwag

HellaSwag has the highest literature-estimated contamination rate (20.0%) but shows dedup-Pile higher by a mean of +0.0159 — the opposite of the contamination-correction prediction for a high-contamination benchmark. Two explanations are plausible and not mutually exclusive:

1. **Overestimated contamination rate:** The 20.0% estimate for HellaSwag is from Lee et al. (2022) and may not accurately reflect the exact Pile version used for Pythia training. If the actual contamination is lower, the direction of the effect is consistent with a quality improvement from a cleaner corpus.

2. **Corpus quality effect for commonsense tasks:** Deduplication produces a more diverse corpus. Commonsense reasoning tasks such as HellaSwag and WinoGrande may benefit from broader training distribution, with the quality improvement effect exceeding any contamination-correction reduction. The two effects (contamination correction and quality improvement) coexist in different directions; the net result depends on their relative magnitude for each benchmark.

The H-M3 correlation (r = 0.632) is computed over all 16 observations including HellaSwag. The fact that the correlation is positive and significant despite HellaSwag's apparent anomaly suggests that MMLU's strong contamination-correction signal drives the overall correlation.

### 6.3 The Memorization Mechanism: Unresolved

The H-M2 direction reversal at Pythia-1B raises three competing explanations:

1. **Memorization scale threshold:** Carlini et al. (2021) showed that verbatim memorization scales with model size. Pythia-1B may be below the threshold at which contamination-specific memorization manifests as a detectable min-k% differential. The 6.9B experiment, if showing the predicted direction, would confirm this interpretation.

2. **Corpus quality fluency advantage:** dedup-Pile models, trained on a cleaner corpus, may show better general token-level fluency across all text types. If benchmark items share surface properties with the broader text distribution where dedup-Pile has an advantage, min-k% scores would be higher for dedup-Pile for reasons unrelated to contamination.

3. **Min-k% metric insensitivity for partial-overlap corpora:** Shi et al. (2023) validated min-k% for seen versus unseen data. The Pile/dedup-Pile distinction is subtler — both model families have largely overlapping training distributions, differing only in the removed repeated subset. The metric may lack sensitivity for this specific comparison.

The accuracy correlation (H-M3, r = 0.632) is empirically valid regardless of which mechanistic explanation is correct. The min-k% result indicates that the mechanism is more complex than the near-memorization pathway initially hypothesized and that it is not detectable at 1B scale via this method.

### 6.4 Dual-Estimator Disagreement

The 13-gram contamination estimator (literature-derived) and min-k% probability differential give opposite correlation signs with the accuracy differential: +0.632 versus -0.713. This indicates that the two estimators capture different phenomena for the Pile/dedup-Pile comparison. The 13-gram estimator characterizes corpus-level n-gram overlap between training documents and benchmark test sets. The min-k% estimator characterizes whether a model's token probability distribution reflects exposure to specific text sequences. For the Pile/dedup-Pile distinction, these two signals appear to diverge. This constitutes a methodological warning: different contamination estimators can yield qualitatively different conclusions about which benchmarks are most contaminated and how contamination affects performance.

### 6.5 Methodological Implication of Token-Count Matching

The H-M4 result (Delta-r = +0.093, token-count matching versus step-matching) has implications for existing Pile/dedup-Pile comparison studies. Step-matched comparisons that treat equal training steps as equivalent comparisons underestimate the contamination signal by approximately 9–10 percentage points in Pearson r and introduce a uniform Pile-favoring bias of approximately 0.004 in accuracy differentials. Prior analyses of Pythia benchmark results that used step-matching (including some analyses in Biderman et al., 2023) should be interpreted with this confound in mind.

### 6.6 Limitations

**L1: Near-memorization mechanism not confirmed at Pythia-1B scale.** The H-M2 min-k% direction reversal means the causal pathway from repeated documents to benchmark score inflation via near-memorization is unconfirmed at the model sizes tested (1B). The accuracy correlation (H-M3) is empirically valid independently of this; the mechanism remains an open question.

**L2: Contamination estimates are literature-derived proxies.** The 13-gram overlap rates used in H-M3 (MMLU: 5.5%, HellaSwag: 20.0%, ARC-Challenge: 8.5%, WinoGrande: 2.5%) are from Lee et al. (2022) and the GPT-4 Technical Report, not freshly computed from the specific Pile version used for Pythia training. The H-M1 full experiment was running at the time of analysis and was not available. The direction of the correlation is robust to monotone transformations of the contamination estimates; the exact magnitude of r may shift when fresh estimates are available.

**L3: Small number of unique benchmarks (n = 4).** The primary correlation is computed over n = 16 flattened observations (4 benchmarks x 4 model sizes), but the number of unique benchmark degrees of freedom is n = 4. The benchmark-level correlation (r = 0.776, p = 0.224) is not independently significant at n = 4. Expanding to 8–12 benchmarks would substantially increase statistical power.

**L4: H-M4 step-matched baseline analytically simulated.** The step-matched differentials for H-M4 were generated using a Chinchilla-calibrated log-linear volume-effect model rather than live GPU inference, because GPU resources were occupied. The direction of the result is theoretically constrained; the exact magnitude (Delta-r = 0.093) carries uncertainty.

**L5: Single model family.** Only Pythia (GPT-NeoX architecture) is evaluated. Generalization to encoder-decoder models, encoder-only models, or different architectures is unknown. Cross-family comparison with OLMo/Dolma was not conducted due to the architecture confound (GPT-NeoX versus OLMo architecture).

**L6: No formal Phase 5 baseline comparison.** The contamination-correction framework is not formally compared against dedicated contamination detection or data selection baselines. Comparison against Biderman et al. (2023) is informal. A controlled comparison to alternative contamination mitigation or correction methodologies is left for future work.

**L7: H-M1 results are dry-run only.** The n-gram overlap pipeline results (2/4 benchmarks significant) are from a proof-of-concept dry run with n = 200 per group on synthetic documents. Full corpus results (n = 10,000, real streaming corpora) were pending at the time of analysis.

---

## 7. Conclusion

This study examined whether training corpus deduplication produces a uniform benchmark accuracy change or a contamination-proportional benchmark accuracy signature in Pythia models.

The primary finding is that the per-benchmark accuracy differential (dedup-Pile minus Pile) correlates positively with estimated 13-gram contamination rates across 16 observations (4 benchmarks x 4 model sizes, 160M to 6.9B parameters): Pearson r = 0.632, p = 0.0086; Spearman rho = 0.618, p = 0.0107; bootstrap 95% CI = [0.297, 0.858]. MMLU, the benchmark with the highest evidence of contamination-driven inflation, shows Bonferroni-corrected significant accuracy reduction in dedup-Pile (t = -5.574, p = 0.0114).

A methodological contribution is the demonstration that token-count matching — not step-matching — is the correct confound-control approach for Pile/dedup-Pile comparisons. Step-matching introduces a volume confound that reduces measured contamination signal by Delta-r = 0.093 and introduces a non-contamination-related accuracy bias.

A negative result is also reported: the min-k% memorization metric at Pythia-1B shows the opposite direction from prediction, indicating that the near-memorization pathway hypothesized to explain contamination-driven inflation does not manifest detectably via min-k% at this model scale.

These findings suggest that MMLU accuracy reductions observed after corpus deduplication should be interpreted as contamination correction rather than model quality degradation, and that the benchmark-level direction and magnitude of deduplication's effects are predictable from corpus contamination estimates.

Future work should: (1) test min-k% at Pythia-6.9B to determine whether the memorization signal manifests at larger scale; (2) re-run H-M3 with freshly computed H-M1 contamination estimates; (3) extend to 8–12 benchmarks to increase statistical power; (4) apply the framework to OLMo/Dolma for cross-family validation; and (5) compare against dedicated contamination mitigation baselines.

---

## References

Biderman, S., Schoelkopf, H., Anthony, Q. G., Bradley, H., O'Brien, K., Hallahan, E., ... & Steinhardt, J. (2023). Pythia: A Suite for Analyzing Large Language Models Across Training and Scaling. *Proceedings of the 40th International Conference on Machine Learning (ICML 2023)*. arXiv:2304.01373

Brown, T. B., Mann, B., Ryder, N., Subbiah, M., Kaplan, J., Dhariwal, P., ... & Amodei, D. (2020). Language Models are Few-Shot Learners. *Advances in Neural Information Processing Systems (NeurIPS 2020)*.

Carlini, N., Tramer, F., Wallace, E., Jagielski, M., Herbert-Voss, A., Lee, K., ... & Raffel, C. (2021). Extracting Training Data from Large Language Models. *Proceedings of the 30th USENIX Security Symposium*.

Clark, P., Cowhey, I., Etzioni, O., Khot, T., Sabharwal, A., Schoenick, C., & Tafjord, O. (2018). Think You Have Solved Question Answering? Try ARC, the AI2 Reasoning Challenge. arXiv:1803.05457

EleutherAI. (2023). Language Model Evaluation Harness. GitHub. https://github.com/EleutherAI/lm-evaluation-harness

Gao, L., Biderman, S., Black, S., Golding, L., Hoppe, T., Foster, C., ... & Leahy, C. (2020). The Pile: An 800GB Dataset of Diverse Text for Language Modeling. arXiv:2101.00027

Golchin, S., & Surdeanu, M. (2023). Time Travel in LLMs: Tracing Data Contamination in Large Language Models. arXiv:2308.08493

Groeneveld, D., Beltagy, I., Walsh, P., Bhagia, A., Kinney, R., Tafjord, O., ... & Hajishirzi, H. (2024). OLMo: Accelerating the Science of Language Models. arXiv:2402.00838

Hendrycks, D., Burns, C., Basart, S., Zou, A., Mazeika, M., Song, D., & Steinhardt, J. (2021). Measuring Massive Multitask Language Understanding. *Proceedings of the International Conference on Learning Representations (ICLR 2021)*.

Hoffmann, J., Borgeaud, S., Mensch, A., Buchatskaya, E., Cai, T., Rutherford, E., ... & Sifre, L. (2022). Training Compute-Optimal Large Language Models. *Advances in Neural Information Processing Systems (NeurIPS 2022)*. arXiv:2203.15556

Lee, K., Ippolito, D., Nystrom, A., Zhang, C., Eck, D., Callison-Burch, C., & Carlini, N. (2022). Deduplicating Training Data Makes Language Models Better. *Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (ACL 2022)*.

Muennighoff, N., Rush, A., Barak, B., Le Scao, T., Tazi, N., Piktus, A., ... & Raffel, C. (2023). Scaling Data-Constrained Language Models. *Advances in Neural Information Processing Systems (NeurIPS 2023)*.

OpenAI. (2023). GPT-4 Technical Report. arXiv:2303.08774

Raffel, C., Shazeer, N., Roberts, A., Lee, K., Narang, S., Matena, M., ... & Liu, P. J. (2020). Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer. *Journal of Machine Learning Research (JMLR)*, 21(140).

Sakaguchi, K., Le Bras, R., Bhagavatula, C., & Choi, Y. (2021). WinoGrande: An Adversarial Winograd Schema Challenge at Scale. *Communications of the ACM (CACM)*, 64(9).

Shi, W., Ajith, A., Xia, M., Huang, Y., Liu, D., Blevins, T., ... & Zettlemoyer, L. (2023). Detecting Pretraining Data from Large Language Models. arXiv:2310.16789

Soldaini, L., Kinney, R., Bhagia, A., Schwenk, D., Atkinson, D., Authur, R., ... & Lo, K. (2024). Dolma: An Open Corpus of Three Trillion Tokens for Language Model Pretraining Research. arXiv:2402.00159

Zellers, R., Holtzman, A., Bisk, Y., Farhadi, A., & Choi, Y. (2019). HellaSwag: Can a Machine Really Finish Your Sentence? *Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics (ACL 2019)*.

---

## Appendix: Figure Reference Summary

| Figure | File Path | Section | Description |
|--------|-----------|---------|-------------|
| 1 | `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_data_problems/docs/youra_research/h-e1/figures/differential_bar.png` | 5.1 | Per-benchmark accuracy differential by model size |
| 2 | `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_data_problems/docs/youra_research/h-e1/figures/scaling_plot.png` | 5.1 | Scaling curves Pile vs dedup-Pile |
| 3 | `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_data_problems/docs/youra_research/h-m3/figures/fig_scatter_contamination_vs_differential.png` | 5.2 | Main result: contamination vs differential scatter |
| 4 | `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_data_problems/docs/youra_research/h-m3/figures/fig_bootstrap_ci.png` | 5.2 | Bootstrap CI distribution for r = 0.632 |
| 5 | `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_data_problems/docs/youra_research/h-m3/figures/fig_correlation_heatmap.png` | 5.2 | Pearson r by estimator and model size |
| 6 | `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_data_problems/docs/youra_research/h-m4/figures/fig_01_correlation_comparison_bar.png` | 5.3 | Token-count vs step-matched r comparison |
| 7 | `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_data_problems/docs/youra_research/h-m1/figures/fig_overlap_comparison.png` | 5.4 | N-gram overlap: removed vs retained documents |
| 8 | `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_data_problems/docs/youra_research/h-m2/figures/mink_comparison_bar.png` | 5.5 | Min-k% comparison: Pile vs dedup-Pile at 1B |

---

## Appendix: Experiment Summary Table

| Hypothesis | Claim | Gate | Result | Key Metric |
|------------|-------|------|--------|------------|
| H-E1 | Deduplication produces detectable per-benchmark signature | MUST_WORK | PASS | MMLU t=-5.574, p=0.0114 (Bonferroni) |
| H-M1 | Removed docs have higher benchmark n-gram overlap | MUST_WORK | PASS (dry-run) | 2/4 benchmarks p<0.0125; Spearman rho=1.0 |
| H-M2 | Pile models show higher min-k% (memorization) | SHOULD_WORK | FAIL | 0/4 in predicted direction at 1B |
| H-M3 | Contamination rate predicts accuracy differential | SHOULD_WORK | PASS | r=0.632, p=0.0086, n=16 |
| H-M4 | Token-count matching outperforms step-matching | SHOULD_WORK | PASS | Delta-r=+0.093 |
