# Phase 4 Validation Report: H-M4

**Date:** 2026-08-19
**Hypothesis:** Bidirectional Tasks Show Miscalibrated Confidence
**Gate Type:** SHOULD_WORK
**Result:** FAIL

---

## Executive Summary

H-M4 tested whether tasks requiring bidirectional adaptation correlate with calibration inversion clusters from H-E1. The experiment computed point-biserial correlation, Cohen's d effect size, and partial correlation (controlling for confounds) between bidirectional feature scores and cluster membership.

**Gate Condition:** (r > 0.4) OR (d > 0.3 AND partial_r > 0.3)
**Outcome:** FAIL - No significant correlation found.

---

## Experiment Results

### Primary Metrics

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Point-biserial r | -0.0271 | > 0.4 | FAIL |
| Cohen's d | -0.0584 | > 0.3 | FAIL |
| Partial r | -0.0094 | > 0.3 | FAIL |
| p-value (r) | 0.203 | < 0.05 | Not significant |

### Dataset Statistics

- **Total tasks analyzed:** 2212
- **Tasks with bidirectional features:** 51 (2.3%)
- **Cluster 0 (normal):** 1519 tasks
- **Cluster 1 (inverted):** 693 tasks

### Feature Prevalence by Cluster

| Feature | Cluster 0 | Cluster 1 (Inverted) |
|---------|-----------|---------------------|
| User belief reference | 1.78% | 0.87% |
| Context dependent | 0.13% | 0.43% |
| Hedged answer | 0.72% | 0.43% |

---

## Analysis

### Why the Gate Failed

1. **Low feature prevalence:** Only 2.3% of tasks contained any bidirectional feature markers. The keyword-based detection (e.g., "you think", "you believe") was too restrictive for the RLHF benchmark datasets.

2. **Near-zero correlations:** Point-biserial r = -0.027 indicates essentially no relationship between bidirectional feature presence and calibration inversion cluster membership.

3. **Effect size negligible:** Cohen's d = -0.058 is far below even a "small" effect threshold (0.2), indicating no practical difference between clusters.

4. **Not statistically significant:** p-value = 0.203 means results could easily arise by chance.

### Interpretation

The failure of H-M4 suggests:

1. **Keyword features may not capture bidirectionality:** The simple keyword matching approach (belief markers, context markers, hedge markers) may not effectively identify tasks requiring bidirectional adaptation.

2. **Alternative mechanism needed:** The causal chain H-E1 → H-M1 → H-M2 → H-M3 → H-M4 is not supported at this final step. Calibration inversion clusters may be explained by other factors than bidirectional task requirements.

3. **Dataset limitation:** TruthfulQA, MMLU moral scenarios, and Anthropic HH-RLHF may not contain sufficient natural variation in bidirectional features to test this hypothesis.

---

## Gate Decision

**FAIL** - Mechanism doesn't explain calibration patterns.

Per verification_state.yaml failure_response for H-M4: **ABANDON** - consider alternative explanations for calibration inversion.

---

## Files Generated

| File | Description |
|------|-------------|
| code/outputs/results.json | Full metrics and feature analysis |
| figures/gate_metrics.png | Bar chart comparing metrics to thresholds |
| figures/score_by_cluster.png | Score distribution by cluster |
| figures/feature_breakdown.png | Feature prevalence by cluster |

---

## Recommendations for Future Work

1. **Semantic feature detection:** Use embedding-based or LLM-based classification for bidirectional features instead of keyword matching.

2. **Expanded feature set:** Include additional markers such as pronoun analysis, dialog structure, and question complexity metrics.

3. **Alternative hypotheses:** Explore other mechanisms for calibration inversion:
   - Task difficulty gradients
   - Answer format patterns
   - Topic-specific calibration biases

---

## Cross-References

- **H-E1:** Calibration inversion clusters exist (silhouette=0.6016) - PASS
- **H-M1:** RLHF optimizes for annotator approval (overlap=0.647) - PASS  
- **H-M2:** Annotators conflate correctness with user-state modeling (rate_diff=0.001) - PASS
- **H-M3:** Single reward signal misses bidirectional nuance (separation=0.024) - PASS
- **H-M4:** Bidirectional tasks show miscalibrated confidence - **FAIL**

---

*Report generated: 2026-08-19*
*Seed: 42*
