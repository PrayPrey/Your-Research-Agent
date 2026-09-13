# Results

We present results following our hypothesis structure: first validating the clustering foundation (H-E1), then the entropy signal (H-M1), distribution similarity (H-M2), and finally the transfer predictions (H-M3, H-M4).

## Benchmark Clustering (H-E1)

Hierarchical clustering on the JS-divergence matrix reveals two distinct benchmark families with silhouette score **0.8245**, substantially exceeding our 0.5 threshold.

**Cluster 1 (Factual Recall):** TriviaQA, Natural Questions, SQuAD
**Cluster 2 (Entity/Claim):** PopQA, HaluEval-QA, FEVER

Figure 2 shows the dendrogram with clear separation between clusters. Within-cluster JS-divergence averages 0.08 versus 0.48 cross-cluster—a 6× difference indicating genuine family structure.

This clustering aligns with our intuited error-type families: Cluster 1 benchmarks test factual recall from parametric memory, while Cluster 2 benchmarks test entity knowledge and claim verification against evidence.

## Entropy-Error Correlation (H-M1)

Semantic entropy strongly separates correct from incorrect responses on TriviaQA:

| Metric | Value |
|--------|-------|
| Mean entropy (correct) | 0.418 |
| Mean entropy (incorrect) | 1.252 |
| Mann-Whitney p-value | 0.000144 |
| Cohen's d | 1.325 |
| AUROC | 0.793 |

Incorrect responses show 3× higher entropy than correct responses, confirming that semantic entropy is a strong hallucination signal. Cohen's d = 1.33 indicates a large effect size substantially exceeding our 0.3 threshold.

Figure 3 shows the entropy distribution by correctness with clear separation between populations.

## Distribution Similarity by Family (H-M2)

Same-family benchmark pairs show significantly lower JS-divergence than cross-family pairs:

| Comparison | Mean JS-div | n pairs |
|------------|-------------|---------|
| Same-family | 0.0823 | 6 |
| Cross-family | 0.4813 | 9 |
| Mann-Whitney p | 0.0002 | — |
| Cliff's delta | -1.0 | — |

The perfect Cliff's delta (-1.0) indicates complete separation: every same-family pair has lower JS-divergence than every cross-family pair. This exceeds our expectations and suggests the family structure is more robust than hypothesized.

Figure 4 shows the boxplot comparison with no overlap between distributions.

## Within-Cluster Transfer Success (H-M3)

Within-cluster threshold transfer shows minimal degradation:

| Transfer Pair | Source AUROC | Target AUROC | Degradation |
|---------------|--------------|--------------|-------------|
| TriviaQA → SQuAD | 0.793 | 0.761 | 0.032 |
| SQuAD → TriviaQA | 0.785 | 0.751 | 0.034 |
| **Mean** | — | — | **0.032** |
| **95% CI upper** | — | — | 0.047 |

Mean degradation of **0.032** is well below our 0.08 threshold, confirming that thresholds calibrated on one within-cluster benchmark transfer effectively to another. The CI upper bound (0.047) remains below threshold, indicating robust success.

## Cross-Cluster Transfer Failure (H-M4)

Cross-cluster threshold transfer shows substantial degradation:

| Transfer Pair | Source AUROC | Target AUROC | Degradation |
|---------------|--------------|--------------|-------------|
| TriviaQA → PopQA | 0.793 | 0.583 | 0.210 |
| TriviaQA → HaluEval | 0.793 | 0.556 | 0.237 |
| **Mean** | — | — | **0.223** |
| **95% CI lower** | — | — | 0.210 |

Mean degradation of **0.223** substantially exceeds our 0.15 failure threshold, confirming that cross-cluster transfer fails as predicted. The ratio of cross-cluster to within-cluster degradation is **7×** (0.223/0.032), demonstrating that cluster membership is the critical factor.

Figure 5 shows the stark contrast between within-cluster and cross-cluster degradation.

## Summary of Hypothesis Tests

| Hypothesis | Gate | Criterion | Result | Status |
|------------|------|-----------|--------|--------|
| H-E1 | MUST_WORK | Silhouette > 0.5 | 0.8245 | **PASS** |
| H-M1 | MUST_WORK | p < 0.05, d > 0.3 | p=0.0001, d=1.33 | **PASS** |
| H-M2 | SHOULD_WORK | Same-family JS < 0.15 | 0.082 | **PASS** |
| H-M3 | SHOULD_WORK | Degradation ≤ 0.08 | 0.032 | **PASS** |
| H-M4 | SHOULD_WORK | Degradation > 0.15 | 0.223 | **PASS** |

All five sub-hypotheses pass their gate conditions, providing strong support for our central claim that distribution similarity predicts transfer success.
