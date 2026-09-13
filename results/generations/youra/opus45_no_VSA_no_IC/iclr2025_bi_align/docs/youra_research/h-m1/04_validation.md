# H-M1 Validation Report

**Hypothesis:** Mode 3 response pairs have lower semantic similarity than Mode 1 response pairs (Cohen's d > 0.3)

**Gate Type:** SHOULD_WORK

**Result:** FALSIFIED

---

## Summary

Mode 3 (Misaligned-Confident) response pairs do **not** have lower semantic similarity than Mode 1 (Aligned-Confident) pairs. The observed effect is negligible and in the **opposite direction** — Mode 3 has slightly higher similarity.

---

## Statistical Results

| Metric | Value |
|--------|-------|
| Mode 1 (Aligned) n | 15,107 |
| Mode 3 (Misaligned) n | 13,632 |
| Mode 1 mean similarity | 0.7031 |
| Mode 3 mean similarity | 0.7125 |
| Mode 1 std | 0.1926 |
| Mode 3 std | 0.1945 |
| **Cohen's d** | **-0.0487** |
| 95% CI for d | [-0.0725, -0.0261] |
| Welch's t-statistic | -4.12 |
| p-value | 3.79e-05 |
| Effect interpretation | Negligible |

---

## Gate Evaluation

**Success Criteria:** Cohen's d > 0.3 (Mode 1 similarity > Mode 3 similarity)

**Falsification Criteria:** Cohen's d < 0.1 OR opposite direction

**Observed:** Cohen's d = -0.0487

- |d| = 0.0487 < 0.1 ✓ (negligible effect)
- d < 0 ✓ (opposite direction: Mode 3 has *higher* similarity)
- p < 0.05 (statistically significant, but effect is trivially small)

**Gate Verdict:** FALSIFIED

---

## Interpretation

The hypothesis that misaligned-confident (Mode 3) battles would show *lower* semantic similarity between response pairs is **not supported**. In fact:

1. **Effect is negligible**: The 0.94% difference in mean similarity (0.7031 vs 0.7125) is practically meaningless despite statistical significance.

2. **Direction is opposite**: Mode 3 responses are slightly *more* similar to each other than Mode 1 responses, contradicting the expectation that misalignment implies semantic divergence.

3. **Semantic similarity does not distinguish modes**: Response pair similarity as measured by sentence embeddings does not capture the mechanism behind human-RM disagreement.

---

## Implications

The mechanism behind Mode 3 (high human entropy, low RM variance) is **not** explained by semantic divergence between response pairs. Alternative mechanisms to investigate:

- Style/tone differences rather than semantic content
- Subtle quality differences not captured by embedding similarity
- Human evaluation factors beyond response content (presentation, formatting)
- RM sensitivity to specific features humans ignore (or vice versa)

---

## Files Generated

- `code/outputs/embeddings.npz` — Cached sentence embeddings
- `code/outputs/similarity_scores.parquet` — Per-battle similarity scores
- `code/outputs/statistical_results.json` — Full statistical results

---

## Methodology

1. Loaded h-e1 mode classifications (57,477 battles)
2. Filtered to Mode 1 (n=15,107) and Mode 3 (n=13,632)
3. Computed sentence embeddings using `all-MiniLM-L6-v2`
4. Calculated cosine similarity between response_a and response_b for each battle
5. Performed Welch's t-test and calculated Cohen's d with bootstrap 95% CI

---

**Completed:** 2026-08-24
