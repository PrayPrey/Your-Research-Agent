# Results

We present results in four layers, each addressing one experimental question from Section 4.

## Primary Result: Both Metrics at Chance Level

**Figure 1** (auroc_comparison.png) shows the AUROC comparison across SMC-NLI, SMC-Embed, and the random baseline.

| Metric | AUROC | Target | Status |
|--------|-------|--------|--------|
| SMC-NLI | **0.4933** | >0.60 | ❌ FAIL |
| SMC-Embed | **0.4859** | >0.60 | ❌ FAIL |
| Random baseline | 0.50 | — | — |

Both SMC-NLI (AUROC=0.4933) and SMC-Embed (AUROC=0.4859) are statistically indistinguishable from a random classifier (AUROC=0.50). Both are substantially below the MUST_WORK gate threshold of 0.60.

**Interpretation:** The primary detection task fails. A system using SMC-NLI to filter Llama-3-8B-Instruct outputs on HaluEval QA would achieve no improvement over random selection.

## ROC Curve Analysis

**Figure 2** (roc_curves.png) shows the full ROC curves for both metrics across all decision thresholds.

Both ROC curves are near-diagonal — confirming that the chance-level AUROC is not an artifact of threshold selection. There is no operating point at which either metric achieves meaningful sensitivity-specificity trade-off. The curves for SMC-NLI and SMC-Embed nearly overlap, already suggesting a shared failure mode.

## Mechanism Analysis: Score Distribution by Label

**Figure 3** (smc_nli_distribution.png) shows the SMC-NLI score histograms split by HaluEval label (correct vs. hallucinated).

| Label | Mean SMC-NLI | SMC-NLI Std |
|-------|-------------|-------------|
| Correct (n=500) | **0.6236** | — |
| Hallucinated (n=500) | **0.6299** | — |
| Gap | **0.006** | — |
| Overall std | **0.3388** | ✅ >0.05 |

The overall SMC-NLI standard deviation is 0.3388 — well above the 0.05 threshold, confirming that scores vary meaningfully across questions. This is a critical diagnostic: the mechanism produces a signal. But the signal carries no information about the label.

The per-label distributions overlap almost completely. The mean SMC-NLI score for correctly-labeled questions (0.6236) is essentially identical to hallucinated-labeled questions (0.6299), with a gap of only 0.006 — noise level over N=1000 questions. The direction is also inverted from the theoretical prediction: hallucinated questions show *slightly higher* consistency (0.6299 > 0.6236), though this difference is not statistically meaningful.

**Interpretation:** The mechanism assumption — that hallucinated outputs produce lower consistency than correct outputs — is empirically falsified. Both label categories produce similar high-consistency outputs in Llama-3-8B-Instruct. The model is "confidently consistent" regardless of factual accuracy.

## Mechanism Verification: Local vs. Global

The 5-question mechanism verification (detailed in Section 3) passed:

```
Q: "What year was the composed of Lux Aurunque born?"   SMC-NLI: 0.9530 | Label: 0 (correct)
Q: "What is the birthdate of this monarch of three...?"  SMC-NLI: 0.3875 | Label: 1 (hallucinated)
Q: "What US Air Force installation was last...?"         SMC-NLI: 0.9853 | Label: 0 (correct)
Q: "Esther Norma Arrostito is a founder of a...?"       SMC-NLI: 0.6162 | Label: 1 (hallucinated)
Q: "What is the birthdate of this American actor...?"   SMC-NLI: 0.4881 | Label: 1 (hallucinated)
✅ Mechanism verification PASSED (range: 0.3875–0.9853, all in [0,1])
```

The mechanism check shows SMC-NLI varies substantially on 5 questions, and appears directionally correct locally (question 1: high consistency, label=correct; question 2: lower consistency, label=hallucinated). This local appearance is misleading: across 1,000 questions, the discriminative signal collapses to AUROC=0.49.

This juxtaposition — local mechanism functioning, global discriminative failure — is the defining characteristic of the systematic confabulation regime. The scorer works correctly; the assumed signal does not exist at scale.

## Dual-Metric Correlation Analysis

**Figure 4** (nli_vs_embed_scatter.png) shows per-question SMC-NLI vs. SMC-Embed scatter.

The two metrics are strongly correlated across questions: questions with high NLI consistency also tend to have high embedding consistency, and vice versa. This strong correlation confirms that SMC-NLI and SMC-Embed are measuring the same underlying property — the output consistency of Llama-3-8B-Instruct — and that property is uniformly present regardless of factual accuracy.

The equal failure of both metrics, and their high correlation, is the strongest evidence for the regime-level interpretation: the failure is not in how consistency is measured (NLI vs. embedding) but in whether consistency discriminates labels in this model-task combination.

## Implementation Validation Summary

| Check | Result |
|-------|--------|
| Unit tests | 14/14 ✅ |
| Mechanism verification | PASSED ✅ |
| Coder-Validator cycles | 1/5 ✅ |
| Total tasks completed | 15/15 ✅ |
| LLM samples generated | 10,000 ✅ |
| NLI pairs scored | 45,000 ✅ |

All implementation checks pass. The negative AUROC result is not attributable to implementation error.

## Summary of Results

| Question | Answer |
|----------|--------|
| Q1: Does SMC-NLI achieve AUROC>0.60? | **No** (AUROC=0.4933) |
| Q2: Does SMC-Embed rule out NLI OOD? | **Yes** (SMC-Embed=0.4859, equal failure) |
| Q3: Is implementation correct? | **Yes** (14/14 tests, mechanism check passes) |
| Q4: What does the distribution reveal? | **Mechanism failure** (gap=0.006, distributions overlap completely) |

The results consistently point to a single interpretation: Llama-3-8B-Instruct on HaluEval QA operates in the systematic confabulation regime, producing consistent outputs for both correct and incorrect beliefs, eliminating the discriminative signal that SMC-based methods require.
