# 5. Results

## 5.1 H-E1: Metric Computability

Both uncertainty metrics achieved 100% computation success across all generated responses, satisfying the MUST_WORK gate.

**Entropy Statistics:**
- Mean: 0.1224
- Standard deviation: 0.0395
- Range: [0.04, 0.25]

**Consistency Statistics:**
- Mean: 0.8693
- Standard deviation: 0.0748
- Range: [0.65, 0.98]

The low mean entropy (0.12) indicates that Llama-2-7B-chat generates responses with relatively high confidence on TriviaQA. The high mean consistency (0.87) suggests stable response patterns, though variance exists across questions.

**Gate Verdict: PASS**

## 5.2 H-M1: Entropy Predicts Correctness

Token entropy significantly discriminates between correct and incorrect answers on the 100-question evaluation set.

| Metric | Correct (n=60) | Incorrect (n=40) |
|--------|----------------|------------------|
| Mean entropy | 0.1104 | 0.1342 |
| Std entropy | 0.035 | 0.042 |

**Statistical Results:**

| Test | Value | Threshold | Status |
|------|-------|-----------|--------|
| t-statistic | 2.28 | - | - |
| p-value (one-sided) | 0.0246 | < 0.05 | PASS |
| AUROC | 0.6454 | > 0.55 | PASS |
| Cohen's d | 0.47 | > 0 | PASS |
| Direction | 0.1342 > 0.1104 | incorrect > correct | PASS |

The medium effect size (d=0.47) indicates a practically meaningful difference: incorrect answers exhibit approximately 22% higher mean entropy than correct answers. The AUROC of 0.65 demonstrates moderate discriminative ability, consistent with prior work on uncertainty-based hallucination detection (Kuhn et al., 2023).

**Gate Verdict: PASS** (all MUST_WORK criteria satisfied)

## 5.3 H-M2: Consistency Predicts Correctness

Semantic consistency achieves stronger discrimination than entropy on the 20-question proof-of-concept set.

| Metric | Correct (n=11) | Incorrect (n=9) |
|--------|----------------|-----------------|
| Mean consistency | 0.896 | 0.826 |
| Std consistency | 0.05 | 0.08 |

**Statistical Results:**

| Test | Value | Threshold | Status |
|------|-------|-----------|--------|
| t-statistic | 2.644 | - | - |
| p-value (one-sided) | 0.0083 | < 0.05 | PASS |
| AUROC | 0.808 | > 0.55 | PASS |
| Cohen's d | 1.19 | > 0 | PASS |
| Direction | 0.896 > 0.826 | correct > incorrect | PASS |

The large effect size (d=1.19) substantially exceeds that of entropy (d=0.47). Consistency's AUROC of 0.81 outperforms entropy's 0.65 by 16 percentage points, suggesting that behavioral signals (response agreement) capture hallucination risk more directly than internal uncertainty estimates.

**Entropy-Consistency Correlation:** Pearson r = -0.54, indicating moderate negative correlation. Higher-confidence responses (low entropy) tend toward higher consistency, as expected. This correlation informs the fusion hypothesis.

**Gate Verdict: PASS** (all SHOULD_WORK criteria satisfied)

## 5.4 H-M3: Fusion Does Not Improve Over Consistency

Linear fusion of entropy and consistency failed to improve upon consistency alone.

**Grid Search Results:**

| Variant | Alpha | Beta | AUROC |
|---------|-------|------|-------|
| Entropy only | 1.0 | 0.0 | 0.675 |
| Consistency only | 0.0 | 1.0 | 0.812 |
| Equal weights | 0.5 | 0.5 | 0.800 |
| Optimal | 0.0 | 0.1 | 0.812 |

The optimal weights (alpha=0.0, beta=0.1) effectively collapse to pure consistency scoring. At N=20, adding entropy provides no discriminative benefit.

**Improvement Analysis:**

| Metric | Value |
|--------|-------|
| AUROC_combined | 0.8125 |
| AUROC_best_single | 0.8125 |
| Improvement | 0.0000 |
| Bootstrap 95% CI | [0.000, 0.000] |

The validation set (n=2) is too small to learn meaningful fusion weights, resulting in overfitting that selects near-zero entropy contribution.

**Gate Verdict: FAIL** (no improvement over best single metric)

## 5.5 Summary Comparison

Table 1 presents the primary results across all hypotheses.

**Table 1: Summary of hypothesis validation results**

| Hypothesis | Gate Type | p-value | AUROC | Cohen's d | N | Verdict |
|------------|-----------|---------|-------|-----------|---|---------|
| H-E1 | MUST_WORK | - | - | - | 100 | PASS |
| H-M1 | MUST_WORK | 0.0246 | 0.645 | 0.47 | 100 | PASS |
| H-M2 | SHOULD_WORK | 0.0083 | 0.808 | 1.19 | 20 | PASS |
| H-M3 | SHOULD_WORK | - | 0.812 | - | 20 | FAIL |

Key findings:

1. **Both metrics work:** Entropy and consistency each significantly predict correctness.

2. **Consistency dominates:** AUROC 0.81 vs 0.65 represents a substantial advantage for behavioral over internal signals.

3. **Fusion is neutral:** At proof-of-concept scale, combination provides no benefit.

## 5.6 Figure References

The following visualizations support these results:

- **Figure 2:** Entropy distribution histograms by correctness (h-m1/figures/entropy_distribution.png)
- **Figure 3:** ROC curves comparing entropy and consistency (h-m2/figures/roc_curve.png)
- **Figure 4:** Scatter plot of entropy vs consistency colored by correctness (h-m2/figures/entropy_vs_consistency.png)
- **Figure 5:** Fusion weight heatmap showing AUROC across (alpha, beta) grid (h-m3/figures/weight_heatmap.png)

The ROC curves clearly illustrate consistency's superior discriminative ability, with the consistency curve dominating the entropy curve at nearly all operating points.
