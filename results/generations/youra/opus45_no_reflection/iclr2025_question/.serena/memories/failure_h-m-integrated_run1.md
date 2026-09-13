# Phase 4 Failure Record: h-m-integrated (Run 1)

**Date:** 2026-08-19T22:15:00Z
**Hypothesis:** h-m-integrated
**Run:** 1
**Final Status:** FAILED
**Failure Type:** MUST_WORK_GATE_NOT_SATISFIED

## Performance Gap

| Metric | Ours | Baseline | Gap |
|--------|------|----------|-----|
| Test AUROC | 0.462 | 0.70 (threshold) | -0.238 (-33.9%) |
| CV AUROC | 0.612 | 0.68 (threshold) | -0.068 (-10.0%) |
| Random Baseline | 0.462 | 0.475 | -0.013 (indistinguishable from random) |

## Root Cause Analysis

- **Linear classifier insufficient**: Logistic regression assumes linear separability in 3D feature space (G-NLL, perplexity mean, attention entropy). Signal-correctness relationship may be nonlinear or require feature interactions. Single-signal ablation shows no strong univariate correlation (all AUROC < 0.46).
- **GPT-2 signals weakly correlated with correctness**: 124M parameter model may lack capacity for nuanced uncertainty representation. Signal extraction verified (100% rate, 4/6 signals with CV > 0.1), but signals do not predict correctness. Attention max/min degenerate (CV=0), suggests GPT-2 attention patterns uninformative.
- **Cross-dataset generalization failure**: Three-way CV shows all AUROCs < 0.56 (threshold 0.65), indicating severe dataset-specific overfitting or lack of generalizable signal-correctness mapping (TQ→HE: 0.521, HE→TQ: 0.545, Mixed: 0.556).
- **No sample efficiency gain**: Learning curve flat or declining (n=50: 0.463, n=300: 0.466, plateau gain -0.003). More data does not improve performance, ruling out sample size as root cause.

## Lessons Learned

1. **Signal existence ≠ signal discriminativeness**: h-e1 showed signal extraction works (non-degenerate signals with CV>0.1), but validation shows signals do NOT correlate with correctness at GPT-2 scale. Extraction mechanism verified, but predictive power absent.
2. **Linear alignment assumption invalid**: Phase 2A prediction assumed linear mapping between signals and correctness. Actual outcome shows no linear alignment (AUROC ~0.46 = random). Dimensional alignment (both measure correctness) insufficient for supervised learning.
3. **PoC scale model insufficient**: GPT-2 (124M) signals too weak for correctness prediction. Scaling to 7B model premature without evidence that mechanism works at ANY scale with alternative approaches (MLP, semantic signals).
4. **Three failure modes combined**: (1) Linear classifier limitation, (2) GPT-2 signal weakness, (3) Feature selection suboptimal. Most likely: combination of (1) and (2) — signals weakly correlated, linear classifier cannot extract discriminative patterns.
5. **Cross-dataset transfer fails**: GSM8K transfer not evaluable (all labels=1, only correct answers in dataset). Three-way CV shows no generalization across TruthfulQA/HaluEval datasets. Signal-correctness correlation does NOT reflect model internal representations, contradicts hypothesis step (3).

## Feedback for Next Phase

### Suggested Modifications
- Test MLP (2-layer, 16 hidden units, ReLU) on same 3D features to capture nonlinear mapping (~1 hour PoC)
- Explore semantic signals (logit entropy over next-token distribution, variance in hidden states) instead of token-level NLL/perplexity (~2 days implementation)
- Do NOT scale to 7B model until PoC shows AUROC ≥ 0.60 with MLP or alternative signals

### What NOT To Do
- Do not assume signal extraction success implies predictive power (h-e1 validated extraction, NOT discrimination)
- Do not scale to larger models without evidence mechanism works at current scale
- Do not add more training samples (learning curve shows no gain)
- Do not expand to full 6D features (attention max/min degenerate, unlikely to help)

### What Showed Promise
- Signal extraction mechanism robust (100% extraction rate across 930 samples)
- Data pipeline works (TruthfulQA, HaluEval, GSM8K all accessible)
- 4/6 signals non-degenerate (CV>0.1), infrastructure ready for alternative signal types

---

## Pivot Options Evaluated

1. **Option A (RECOMMENDED)**: Test MLP for nonlinear mapping (cheap, 1 hour, addresses linearity assumption)
2. **Option C (IF MLP FAILS)**: Explore semantic signals (logit entropy, hidden-state variance)
3. **Option D (PREMATURE)**: Scale to 7B model without PoC validation
4. **Option E (FALLBACK)**: Abandon supervised UQ, return to h-m2 variance oracle (unsupervised, Phase 1 showed ~0.55-0.60 AUROC)

---
*For cross-phase reference*
*Written at: 2026-08-19T22:15:00Z*