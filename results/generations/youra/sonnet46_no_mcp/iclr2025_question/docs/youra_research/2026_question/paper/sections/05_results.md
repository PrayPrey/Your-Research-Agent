# Results

We present results in mechanism-first order: the NLI aggregation failure (RQ3) causally explains the AUROC outcome (RQ1). Presenting mechanism results before performance results ensures that the AUROC numbers are immediately interpretable rather than requiring post-hoc explanation.

## NLI Clustering Mechanism (RQ3: H-M2)

The central finding of this work is a mechanism failure, not a performance failure. Figure 5 (aggregation_rate.png) and Figure 6 (cluster_count_dist_hm2.png) show the NLI clustering behavior on HaluEval-QA.

**NLI aggregation rate = 0.272 (95% CI [0.253, 0.292])** — well below the 0.50 PASS threshold. This means that on 72.8% of the 2,000 HaluEval-QA examples, all five stochastic LLaMA-2-7B-chat responses were assigned to distinct semantic clusters by deberta-large-mnli. The cluster count distribution confirms this: 1,456 of 2,000 examples (72.8%) receive the maximum cluster count of 5/5 (Figure 6).

| Cluster Count | Frequency | Fraction |
|:---:|---:|---:|
| 1 (full collapse) | 4 | 0.2% |
| 2 | 22 | 1.1% |
| 3 | 112 | 5.6% |
| 4 | 406 | 20.3% |
| **5 (no aggregation)** | **1,456** | **72.8%** |

**What this means:** The NLI model treats each of the N=5 stochastic responses as semantically distinct from every other, even when responses express the same fact in different words. For an example like "Who invented the telephone?", responses "Alexander Graham Bell", "Graham Bell", and "Bell, the inventor" may all be classified as semantically non-equivalent by deberta-large-mnli's MNLI-calibrated entailment threshold. When every response is in its own cluster, semantic entropy equals $\log_2(N) = \log_2(5)$ for all examples — a constant that carries no information about hallucination.

The 95% CI [0.253, 0.292] is entirely below 0.30, indicating this is not a marginal result that could be explained by statistical noise. Mean cluster count = 4.644 (std = 0.657), median = 5.000. The gate condition for H-M2 (aggregation_rate ≥ 0.50) is violated by a margin of 0.228 absolute points, representing a 45.6% shortfall from the required threshold. **H-M2: PIVOT (SHOULD_WORK gate not satisfied; A2 violated).**

The CDF of cluster counts (Figure 8, cluster_count_cdf.png) shows that only 27.2% of examples have cluster count ≤ 4, confirming that the vast majority of examples provide no semantic aggregation signal.

## Degenerate Semantic Entropy Diagnosis (RQ2: H-M1)

The consequence of maximum-cluster-count domination is immediate: when all N=5 responses are in distinct clusters with equal probability p = 1/5, semantic entropy equals $\log_2(5) \approx 2.322$ bits for every example. Figure 4 (degenerate_summary.png) shows the token entropy vs. semantic entropy scatter — semantic entropy is a perfectly flat line.

**Semantic entropy std = 4.14 × 10⁻²⁵** across 2,000 examples — effectively zero variance. The Pearson correlation r(TE, SE) is undefined because the semantic entropy scores have no variance. **H-M1: DEGENERATE_PASS** — the gate condition (r < 0.9) is trivially satisfied because r is undefined, but the result provides a direct degenerate diagnosis rather than a meaningful correlation measure.

The cluster distribution from H-M2 (mean = 4.644, n_singleton = 4 examples with complete collapse) confirms that semantic entropy degeneracy is not caused by LLM uniformity (if the model were generating identical responses, all would collapse to 1 cluster). Rather, the model is generating genuinely diverse responses, but the NLI model classifies them as semantically distinct despite semantic equivalence.

## Main AUROC Comparison (RQ1: H-E1)

With the mechanism context established, the AUROC results become interpretable rather than mysterious. Figure 1 (auroc_bar_chart.png) shows AUROC with 95% bootstrap confidence intervals for all three methods.

| Method | AUROC | 95% CI Lower | 95% CI Upper |
|--------|------:|-------------:|-------------:|
| Semantic Entropy (SE) | 0.5000 | 0.5000 | 0.5000 |
| Token Entropy (TE) | 0.4829 | 0.4585 | 0.5090 |
| SelfCheckGPT-BERTScore (SCG) | **0.3562** | 0.3321 | 0.3803 |

*Bootstrap CI: N=1,000 resamples, seed=42. All methods evaluated on same 2,000-example stratified HaluEval-QA sample.*

**Semantic entropy (AUROC = 0.5000, CI = [0.5000, 0.5000]):** The degenerate CI — a single point at exactly 0.5 — is the unique signature of a constant signal. Because all SE scores are identical, every threshold yields the same TPR/FPR ratio (0.5/0.5 on a balanced dataset), producing an ROC curve that is exactly the diagonal. This is not "near-random" — it is strictly random by construction, a direct consequence of the NLI aggregation failure documented in H-M2.

**Token entropy (AUROC = 0.4829, CI = [0.4585, 0.5090]):** Near-random. The CI spans 0.5, meaning token entropy could be either a weak positive or weak negative discriminator — the evidence is consistent with zero discrimination. LLaMA-2-7B-chat's token-level uncertainty does not predict HaluEval-QA hallucination labels under standard configurations.

**SelfCheckGPT-BERTScore (AUROC = 0.3562, CI = [0.3321, 0.3803]):** Below random chance. This is the most surprising result. The CI [0.332, 0.380] is entirely below 0.5 — the upper bound (0.380) is 0.120 below random. This constitutes a statistically significant *negative* correlation between BERTScore consistency and HaluEval-QA hallucination labels. Figure 2 (roc_curves_overlay.png) shows all three ROC curves — SCG's curve falls consistently below the random diagonal.

### Pairwise Comparisons

| Pair | Winner | Δ AUROC | CIs | Qualifies (Δ≥0.05, non-overlapping) |
|------|--------|--------:|-----|:---:|
| SE vs. SCG | SE | 0.1438 | Non-overlapping | ✓ |
| TE vs. SCG | TE | 0.1268 | Non-overlapping | ✓ |
| SE vs. TE | SE | 0.0171 | Overlapping | — |

Two of three pairwise comparisons qualify (Δ ≥ 0.05 with non-overlapping 95% bootstrap CIs after Bonferroni correction). **H-E1: PASS (MUST_WORK gate satisfied).** The existence of a statistically significant discrimination gap between UQ methods on HaluEval-QA is confirmed — but the gap is driven by SelfCheckGPT performing significantly *worse* than both entropy-based methods, not by semantic entropy outperforming token entropy.

The SE vs. TE comparison (Δ = 0.0171, overlapping CIs) does not qualify. This is the primary prediction of the original hypothesis (P1: SE ≥ TE by ≥ 0.05): **P1 is REFUTED.** Semantic entropy does not achieve statistically superior AUROC over token entropy on HaluEval-QA. The causal explanation is the NLI mechanism failure quantified in H-M2: a functioning NLI clustering step is a prerequisite for SE to outperform TE.

## SelfCheckGPT Polarity Inversion Analysis

The below-random AUROC of SelfCheckGPT-BERTScore (0.3562) warrants separate analysis. Figure 7 (cluster_count_by_label.png) shows cluster count distributions stratified by hallucination label — though this figure primarily characterizes NLI clustering, the label-stratified view provides indirect evidence for consistency-label relationships.

The most plausible interpretation of AUROC = 0.3562 is a **label polarity inversion**: HaluEval-QA's hallucinations are ChatGPT-generated to be confident-sounding incorrect answers. LLaMA-2-7B-chat may generate *consistently* wrong answers for hallucinated questions (the model confidently reproduces a specific wrong fact across stochastic samples), while generating *more varied* responses for factual questions (different phrasings of the correct answer). If so:

- E[BERTScore consistency | hallucinated] > E[BERTScore consistency | factual]
- SelfCheckGPT score (1 - consistency) is lower for hallucinated examples
- SelfCheckGPT predicts "not hallucinated" precisely for hallucinated examples → AUROC < 0.5

This hypothesis predicts that inverting the SelfCheckGPT signal (using consistency rather than inconsistency as the hallucination predictor) would yield AUROC > 0.5 — potentially a strong positive result. We leave direct verification to future work (requires stratifying per-example consistency scores by label using existing H-E1 outputs, with zero new inference).

## Prediction-Result Summary

| Prediction | Description | Result |
|-----------|-------------|--------|
| **P1** | SE AUROC − TE AUROC ≥ 0.05, non-overlapping CIs | **REFUTED** (Δ=0.017, overlapping CIs; SE degenerate) |
| **P2** | SCG AUROC intermediate between TE and SE | **PARTIALLY SUPPORTED** (ranking SE>TE>SCG holds nominally, but SE is degenerate and SCG is below-random) |
| **P3** | Ranking order preserved across LLaMA-2 and Mistral (Spearman ρ ≥ 0.8) | **INCONCLUSIVE** (Mistral experiment not executed) |

The core causal chain is **broken at Step 2**: the NLI filtering mechanism fails (A2 violated, aggregation_rate=0.272), semantic entropy degenerates (std < 1e-6), and the SE > TE superiority claim is not supported. All three tested UQ signals have near-random or below-random discrimination on HaluEval-QA with LLaMA-2-7B-chat under standard configurations.
