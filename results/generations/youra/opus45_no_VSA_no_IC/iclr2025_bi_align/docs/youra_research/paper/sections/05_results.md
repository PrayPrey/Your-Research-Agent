# Results

## H-E1: Mode 3 Existence — CONFIRMED

Analyzing 57,477 Chatbot Arena battles, we find the four alignment modes distribute near-uniformly:

| Mode | Description | Count | Proportion |
|------|-------------|-------|------------|
| 1 | Aligned-Confident | 15,107 | 26.3% |
| 2 | Aligned-Uncertain | 13,714 | 23.9% |
| **3** | **Misaligned-Confident** | **13,632** | **23.7%** |
| 4 | Misaligned-Uncertain | 15,024 | 26.1% |

Mode 3 constitutes **23.7%** of battles (95% CI: 23.4%–24.0%). A one-sided binomial test against the null hypothesis p ≤ 0.10 yields p < 0.001. The lower bound of the 95% CI (23.4%) is well above the 10% threshold.

**Result**: Overconfident misalignment is not a fringe phenomenon. Approximately one in four preference battles exhibits high human disagreement coupled with high reward model confidence—a systematic failure pattern in real-world alignment data.

## H-M1: Semantic Similarity Mechanism — FALSIFIED

We compare semantic similarity between response pairs in Mode 1 (Aligned-Confident) and Mode 3 (Misaligned-Confident):

| Mode | n | Mean Similarity | Std |
|------|---|-----------------|-----|
| 1 (Aligned) | 15,107 | 0.7031 | 0.1926 |
| 3 (Misaligned) | 13,632 | 0.7125 | 0.1945 |

**Effect size**: Cohen's d = −0.049 (95% CI: −0.073 to −0.026)

**Statistical test**: Welch's t = −4.12, p = 3.79×10⁻⁵

The effect is **opposite to prediction**: Mode 3 response pairs have *higher* semantic similarity than Mode 1 pairs, not lower. The effect size is negligible (|d| < 0.1), indicating no practically meaningful difference despite statistical significance.

**Interpretation**: The hypothesis that RMs become overconfident when responses are semantically divergent is falsified. If anything, Mode 3 involves *more similar* responses—suggesting that misalignment arises when responses are alike in semantic content but differ in dimensions embeddings fail to capture (style, tone, formatting, subtle quality differences).

## H-C1: Prompt Type Condition — INCONCLUSIVE

Stratifying by prompt type:

| Category | Mode 3 Count | Total | Mode 3 Proportion |
|----------|--------------|-------|-------------------|
| Subjective | 2,184 | 9,839 | 22.2% |
| Objective | 901 | 4,349 | 20.7% |
| Ambiguous (excluded) | — | 43,289 | — |

**Ratio** (subjective / objective): 1.07 (95% CI: 1.00–1.15)

**Effect size**: Cohen's h = 0.036 (negligible)

**Statistical test**: z = 1.97, p = 0.024

The direction is correct (subjective > objective) but the magnitude is far below the predicted 1.5 ratio. Cohen's h indicates negligible practical effect.

**Interpretation**: Mode 3 is not concentrated in subjective prompt types. Overconfident misalignment pervades all task categories, occurring at roughly similar rates regardless of whether prompts involve creative/subjective tasks or objective/analytical tasks. This refutes the hypothesis that human disagreement stems primarily from inherent subjectivity of certain task types.

## Summary Table

| Hypothesis | Prediction | Threshold | Observed | Verdict |
|------------|------------|-----------|----------|---------|
| H-E1 (Existence) | Mode 3 > 10% | >10% | 23.7% | **CONFIRMED** |
| H-M1 (Mechanism) | Mode 3 similarity < Mode 1 | d > 0.3 | d = −0.049 | **FALSIFIED** |
| H-C1 (Condition) | Subjective/Objective ratio > 1.5 | ratio > 1.5 | ratio = 1.07 | **INCONCLUSIVE** |

**Overall hypothesis status**: PARTIALLY SUPPORTED. The phenomenon exists at substantial scale; proposed mechanisms are not supported.
