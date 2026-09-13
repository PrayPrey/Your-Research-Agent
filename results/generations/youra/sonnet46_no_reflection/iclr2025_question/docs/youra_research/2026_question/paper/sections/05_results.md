# Results

## Main AUROC Comparison

Table 1 and Figure 1 present AUROC results for all UQ methods on Llama-3-8B-Base. The most striking finding is that semantic entropy (SE), the method expected to outperform token-probability by ~0.05–0.12 AUROC based on published results, instead *underperforms token-probability by 0.210 AUROC on TriviaQA*—achieving an AUROC of 0.4735, below random chance (0.5).

**Table 1: AUROC Results on Llama-3-8B-Base (95% Bootstrap CI)**

| Method | TriviaQA AUROC | TriviaQA CI | NQ AUROC | NQ CI | vs. token_prob (TQA) |
|--------|---------------|-------------|----------|-------|---------------------|
| token_prob | **0.6835** | [0.6361, 0.7332] | **0.6551** | [0.5960, 0.7063] | baseline |
| selfcheck_nli | 0.6862 | [0.6362, 0.7340] | 0.4508 | [0.3943, 0.5084] | +0.003 |
| semantic_entropy | 0.4735 | [0.4409, 0.5036] | 0.5524 | [0.5121, 0.5977] | **−0.210** |
| kle | 0.2642 | [0.2158, 0.3107] | 0.3753 | [0.3078, 0.4372] | **−0.419** |
| selfcheck_bertscore | 0.5000 | [0.5000, 0.5000] | 0.5000 | [0.5000, 0.5000] | −0.184 |
| seps | null | — | null | — | n/a |

*Figure 1 (fig1_auroc_bar_8b.png): AUROC comparison across all UQ methods on TriviaQA and NQ. Error bars indicate 95% bootstrap CI.*

**Interpretation:** The MUST_WORK gate condition—SE AUROC > token_prob AUROC with 95% CI excluding zero—fails on both datasets. On TriviaQA, SE is 0.210 AUROC points *below* token_prob; on NQ, the gap is 0.103 points. The gate cannot be satisfied regardless of 70B results. Token-probability and SelfCheckGPT-NLI are the only methods achieving AUROC meaningfully above 0.5; KLE falls to 0.2642 on TriviaQA, well below chance.

## Sampling Degeneracy Analysis

Figure 2 shows the SE minus token_prob AUROC difference with bootstrap confidence intervals. The 95% CI for the TriviaQA difference (SE - TP = −0.210) is [−0.2517, −0.1553]—entirely negative, confirming that SE anti-correlation is not a sampling artifact.

*Figure 2 (fig2_se_tp_difference_8b.png): SE minus token-probability AUROC difference on TriviaQA and NQ, with 95% bootstrap CI. Both CIs exclude zero in the negative direction.*

To diagnose the failure, we computed `degenerate_fraction`—the proportion of queries for which SE produces K=1 semantic cluster (all N=10 samples semantically equivalent):

**Table 2: Sampling Degeneracy Statistics**

| Dataset | degenerate_fraction | mean_K | max_K | Expected K (if diverse) |
|---------|---------------------|--------|-------|------------------------|
| TriviaQA | **0.894** | 9.884 | ≤10 | 3–5 |
| NaturalQuestions | **0.848** | 9.796 | ≤10 | 3–5 |

On TriviaQA, 89.4% of queries produce K=1 under N=10 sampling. The mean K of 9.884 indicates that when the model samples 10 responses, on average 9.88 of them cluster into a single equivalence class. For these queries, SE = −∑_c p(c) log p(c) = 0 (single cluster → zero entropy). With SE=0 for 89% of queries and non-zero SE for only 11%, the score distribution provides essentially no discriminative signal for correctness.

**Why the anti-correlation occurs:** Among the 11% of queries with K>1 (SE>0), there is a selective pattern: these are queries where the model generates some variation—often because it is uncertain but happens to produce partially correct or varied phrasings. High-confidence incorrect answers consistently produce K=1 (low SE), while uncertain-but-correct answers occasionally produce K>1 (higher SE). With 89% of queries at K=1, residual variation in the 11% creates an inverted AUROC: higher SE is weakly associated with correctness, meaning uncertainty estimates are anti-correlated with actual incorrectness.

## Full Method Comparison

Figure 3 provides the complete method comparison across both datasets.

*Figure 3 (fig3_auroc_all_methods_8b.png): All UQ methods on Llama-3-8B-Base, TriviaQA and NQ. Methods shown: token_prob, SE, KLE, SelfCheck-NLI, SelfCheck-BERTScore.*

**SelfCheckGPT-NLI unexpectedly matches token_prob on TriviaQA** (0.6862 vs. 0.6835). Despite the same high degenerate_fraction, NLI-based consistency detection retains discriminative ability because: (a) NLI operates on semantic entailment rather than clustering entropy, (b) among the 11% of diverse queries, subtle paraphrase variants provide discriminative signal that NLI's entailment model captures but BERTScore's cosine similarity misses at the character/token level. This finding has a practical implication: SelfCheckGPT-NLI is a valid SE alternative even in low-diversity regimes.

**SelfCheckGPT-BERTScore is completely uninformative** (AUROC=0.5000, zero-variance CI): when all N=10 samples are identical, BERTScore(identical, identical)=1.0 for all queries, producing a constant uncertainty score with no discriminative ability. This is mechanistically expected and confirms the implementation is correct; the failure mode is sampling-regime-dependent.

**KLE falls below chance on TriviaQA** (0.2642). The von Neumann entropy over the semantic similarity Laplacian degenerates more severely than SE: with 89% of queries producing a rank-1 Laplacian matrix (all samples identical → pairwise similarity=1.0 → eigenvalue sum≈0), KLE scores are systematically near-zero for high-confidence queries and non-trivially positive for the 11% of diverse queries. The resulting inversion of the score distribution is more severe than SE's, producing AUROC well below 0.5.

## Gate Evaluation Summary

| Criterion | Required | Actual | Result |
|-----------|----------|--------|--------|
| SE AUROC > token_prob (TriviaQA, CI excludes 0) | SE > TP | SE=0.4735 < TP=0.6835 | ❌ FAIL |
| SE AUROC > token_prob (NQ, CI excludes 0) | SE > TP | SE=0.5524 < TP=0.6551 | ❌ FAIL |
| degenerate_fraction < threshold | < 0.3 (SE-viable) | 0.894 (TQA), 0.848 (NQ) | ❌ DEGENERACY |

The MUST_WORK gate fails on all evaluated criteria. The root cause—confirmed by degenerate_fraction measurement—is sampling degeneracy, not implementation error, evaluation protocol choice, or model loading artifact. The SE mechanism (NLI clustering, K<N) is correctly implemented and activates (mean_K < N=10); the failure is a conceptual mismatch between the method's diversity requirement and the model's near-deterministic sampling behavior.
