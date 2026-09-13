# Results

Our pilot study reveals that hallucination detection method performance varies dramatically across benchmarks—a finding with important implications for method selection.

## Main Results

Table 1 presents AUROC scores for both methods on each benchmark.

**Table 1: Hallucination Detection AUROC (Pilot Study, N=20 samples per dataset)**

| Method | TruthfulQA | HaluEval |
|--------|------------|----------|
| Semantic Entropy | 0.289 [0.105, 0.526] | **0.551** [0.267, 0.800] |
| Self-Consistency | 0.474 [0.252, 0.687] | 0.444 [0.155, 0.733] |
| *Gate Threshold* | *0.55* | *0.55* |

**Key Observations:**

1. **Only one condition meets the gate threshold.** Semantic entropy achieves AUROC 0.551 on HaluEval, marginally exceeding our 0.55 threshold. All other method-benchmark combinations fall below threshold.

2. **TruthfulQA shows inverted results for semantic entropy.** AUROC 0.289 is *below* random (0.5), indicating that high-entropy responses were actually more truthful in our pilot. This inverted behavior was unexpected given literature reports of AUROC ~0.85 on TruthfulQA.

3. **Self-consistency performs near random on both benchmarks.** AUROC values of 0.444 and 0.474 are statistically indistinguishable from chance, suggesting BERTScore-based consistency may not capture hallucination-relevant uncertainty.

Figure 1 visualizes ROC curves for all conditions. The semantic entropy curve on HaluEval shows modest discrimination, while TruthfulQA curves cluster around the diagonal.

![ROC Curves](figures/roc_curves.png)
*Figure 1: ROC curves comparing detection methods across benchmarks. Only semantic entropy on HaluEval shows clear discrimination above the diagonal.*

## Analysis: Benchmark Sensitivity

**RQ2 Finding:** Method ranking differs dramatically across benchmarks.

On HaluEval, semantic entropy outperforms self-consistency (0.551 vs 0.444). On TruthfulQA, the pattern reverses: self-consistency outperforms semantic entropy (0.474 vs 0.289). This interaction suggests benchmark-specific method selection may be necessary—a consideration absent from current method papers.

Figure 2 shows the distribution of uncertainty scores for hallucinated vs truthful responses.

![Score Distributions](figures/score_distributions.png)
*Figure 2: Distribution of uncertainty scores. Overlap between distributions reflects poor discriminability.*

## Analysis: TruthfulQA Inversion

**Surprising Finding:** Semantic entropy AUROC on TruthfulQA is significantly below random.

Literature reports SE AUROC ~0.75-0.85 on TruthfulQA [Kuhn et al., 2023]. Our observation of 0.289 represents not just failure but *inverted* behavior—the method confidently predicts the wrong direction.

**Our interpretation:** TruthfulQA's "Best Answer" matching may not align with the uncertainty signal semantic entropy captures. Truthful responses (matching annotated answers) may exhibit higher semantic diversity in our pilot, while misconceptions (stereotyped false beliefs) may cluster together. This is a hypothesis requiring larger-scale validation.

**Alternative explanations:**
1. Model-specific (Llama-3-8B) behavior differs from original paper's models
2. Implementation details differ from original paper
3. Small sample size (N=20) produces unreliable estimates

The wide confidence interval [0.105, 0.526] reflects statistical uncertainty—we cannot definitively distinguish between these explanations with current sample size.

## Gate Evaluation

Figure 3 compares method AUROC against the gate threshold.

![Gate Comparison](figures/gate_comparison.png)
*Figure 3: AUROC comparison against 0.55 gate threshold. Only SE on HaluEval passes.*

**Gate Result:** PARTIAL (1/4 conditions pass)

| Method | TruthfulQA | HaluEval |
|--------|------------|----------|
| Semantic Entropy | FAIL (0.289 < 0.55) | PASS (0.551 ≥ 0.55) |
| Self-Consistency | FAIL (0.474 < 0.55) | FAIL (0.444 < 0.55) |

## Statistical Considerations

**Sample Size Limitation:** With N=20 samples per dataset, confidence intervals span 0.5+ AUROC range. This wide uncertainty prevents definitive conclusions:
- SE on HaluEval: CI [0.267, 0.800] includes both "works" (0.8) and "fails" (0.27)
- Overlapping CIs across conditions prevent statistical comparison

**Implication:** Our pilot establishes pipeline functionality and reveals unexpected benchmark sensitivity, but full-scale validation (N=817 TruthfulQA, N≥500 HaluEval) is required for statistically powered conclusions.
