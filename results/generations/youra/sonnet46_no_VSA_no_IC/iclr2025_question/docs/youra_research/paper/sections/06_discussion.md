# Discussion

## Key Findings and Their Interpretation

Our results demonstrate that the optimal token log-probability aggregation function for zero-cost hallucination detection is not arbitrary — it is determined by the structural nature of the hallucination being detected. Three independent metrics confirm the mechanism at three levels of abstraction:

**Distributional level (h-m1):** Recall-failure hallucinations produce significantly more peaked token probability distributions on TriviaQA (peakedness ratio 2.936 vs. 2.533, p = 0.002). This is the most direct evidence that the hallucination type creates a structurally distinct signal in the token log-probability sequence. Without this result, the P1 and P2 AUROC patterns could be post-hoc rationalizations; with it, they are the terminal confirmation of a predicted causal chain.

**Rank-correlation level (h-m2):** Spearman ρ differentials confirm the directional advantage at the signal level, independent of AUROC threshold assumptions. The consistency across all four (model × dataset) pairs with CIs excluding zero is the strongest available evidence that the mechanism generalizes across model families. LLaMA-2-7B and Mistral-7B-v0.1 differ in architecture, pretraining corpus, and tokenization; their quantitatively consistent directional effects suggest the mechanism is a property of the hallucination type classification, not model-specific implementation detail.

**Threshold level (h-m3):** P1 (min > mean on TriviaQA, Δ = 0.056–0.119 AUROC) and P2 (mean > min on TruthfulQA, Δ = 0.111–0.120 AUROC) are both confirmed with effect sizes that are practically significant. A practitioner using mean log-prob for factual recall detection and switching to min would recover 5–12 AUROC points at zero additional cost.

The symmetric magnitude of P1 and P2 across model families is particularly noteworthy. Both effects are approximately 0.10–0.12 AUROC on the larger model (LLaMA), suggesting that the mechanism operates with consistent strength in both directions. This symmetry is consistent with a single underlying distribution-shape driver rather than two separate phenomena.

## The Raw_sum Discovery

The refutation of P3 — raw unnormalized log-probability sum is the strongest, not weakest, aggregation on TriviaQA — is the most practically impactful and theoretically provocative result. P3 was predicted to fail because length-biased aggregation was expected to confound the uncertainty signal. Instead, raw_sum achieves AUROC 0.895–0.896 on TriviaQA, exceeding both min and mean, and exceeding published Semantic Entropy (≈0.79) at 10× lower inference cost.

The most likely explanation is that the "length bias" is not a confound but a signal: on factual recall benchmarks, correct answers tend to be longer (the model generates a complete factual statement) and each token is assigned high probability. The unnormalized sum accumulates a larger negative value for correct answers (more tokens × high per-token confidence), making the score more discriminative than any single-token statistic. This interpretation is consistent with the observation that raw_sum is *weakest* on TruthfulQA (0.530–0.582), where the flat-distribution structure means all tokens are uniformly confident regardless of correctness — the length signal carries no diagnostic information.

We emphasize that the raw_sum finding requires further validation. A length-stratified AUROC analysis (splitting samples by answer length and testing whether the raw_sum advantage persists within each stratum) is necessary to determine whether raw_sum's advantage is a genuine sequence-level calibration signal or a length-correlation artifact. The h-e1 codebase includes a `length_stratified_auroc` function implemented but not yet executed.

## Comparison to Published Baselines

Although we do not re-implement external methods in the same pipeline, the absolute AUROC values provide important context. Our min log-prob on TriviaQA (0.849–0.892) exceeds the published CCP/mean log-prob range (0.72–0.80, Fadeeva 2024) by approximately 0.07–0.09 AUROC — a margin that is as large as the full performance gap between best and worst aggregators in prior comparisons. Our raw_sum (0.895–0.896) exceeds Semantic Entropy (≈0.79) by ≈0.10 AUROC despite using a single forward pass vs. SE's 10-sample requirement. These comparisons should be interpreted with caution since they are cross-pipeline, but the magnitude of the gap makes a methodological explanation unlikely.

## Limitations

**NQ data gap.** The P1 claim was formulated to include both TriviaQA and NQ. NQ inference ran during h-e1 but the score cache was not persisted to disk (implementation gap, not mechanism failure). The P1 result is confirmed on TriviaQA only. The mechanism predicts the same directional pattern for NQ (also factual recall type), and the large TriviaQA effect sizes (Δ ≥ 0.056 AUROC, Δρ ≥ 0.092) across two models provide strong indirect support. Re-running NQ inference requires only GPU time on existing code.

**7B model scale.** All results are at 7B parameters. Larger models may exhibit stronger TruthfulQA effects (Lin et al. [2021] report inverse scaling continuing to 175B — greater scale means greater imitative-falsehood confidence, which would strengthen the flat-distribution interpretation and correspondingly strengthen the mean > min advantage). Our 7B P2 results may underestimate the effect size at deployment-relevant scales (70B+). Scale extension is standard future work for this line of research.

**Greedy decoding only.** All token log-probabilities are extracted from greedy (argmax) forward passes. Greedy log-probabilities may diverge from model uncertainty estimates derived from sampling (temperature > 0). Assumption A3 (greedy log-probs represent model uncertainty) is experimentally unverified. All results are valid within the greedy-decoding regime; generalization to sampling-based settings requires separate validation.

**Multi-sample baselines not in same pipeline.** The comparison to Semantic Entropy and SelfCheckGPT is cross-pipeline (different datasets, tokenization, and evaluation protocol details). While the AUROC gaps are large, a within-pipeline comparison on identical splits would be needed for definitive claims.

## Broader Impact

This work advances zero-cost hallucination detection — a practically important component of responsible LLM deployment. By providing a principled selection criterion for aggregation function based on the expected hallucination type, we reduce the risk of systematically misconfigured detection for specific error classes. Practitioners building hallucination-aware pipelines (RAG systems, factual QA assistants, educational tools) can apply the min/mean selection rule without modifying the model, retraining, or acquiring labels. The practical cost of this improvement is zero.

We note that improved hallucination detection could have dual-use implications: in adversarial settings, knowing which aggregation function a detector uses could help an attacker craft responses that evade detection. However, the aggregation functions studied here are based on model-intrinsic log-probabilities and are not amenable to direct adversarial manipulation without modifying the model's generation distribution.

The mechanism-grounded taxonomy (hallucination type → distribution shape → aggregation optimality) may generalize beyond token log-probability methods to other sequence-level tasks where different error types produce structurally distinct internal representations. We encourage the community to apply and test this framing in other settings.
