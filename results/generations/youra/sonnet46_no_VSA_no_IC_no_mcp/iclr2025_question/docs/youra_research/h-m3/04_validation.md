---
hypothesis_id: h-m3
phase: validation
generated_at: "2026-08-25"
author: yoon303@ust.ac.kr
---

# Validation Report: H-M3 — SelfCheckGPT BERTScore Uncertainty Estimation

## Hypothesis

Under Llama-2-7B on TriviaQA dev, if SelfCheckGPT BERTScore consistency is computed across K=10 samples, then SCG achieves AUROC within 0.03 of SE (|SCG-SE| <= 0.03), because BERTScore agreement implicitly captures semantic consistency without requiring NLI inference.

## Gate

- Type: SHOULD_WORK
- Criterion: |auroc_scg - auroc_se| <= 0.03
- **Result: FAIL**

## Experimental Setup

| Parameter | Value |
|-----------|-------|
| Model | Llama-2-7B |
| Dataset | TriviaQA dev (h-e2-v2 cache) |
| N questions | 98 |
| K samples | 10 |
| seed | 42 |
| n_bootstrap | 1000 |
| BERTScore model | default (bert-base-multilingual-cased via selfcheckgpt) |
| rescale_with_baseline | True |

## Results

| Method | AUROC | 95% CI |
|--------|-------|--------|
| SCG (BERTScore) | 0.3779 | [0.3085, 0.4450] |
| SE (NLI clustering) | 0.2860 | [0.1806, 0.3922] |
| TE (Token Entropy) | 0.4381 | [0.3286, 0.5586] |

**delta = |SCG - SE| = 0.0920** (threshold: 0.03) → **FAIL**

SCG vs TE advantage: -0.0602 (SCG performs worse than TE)

## Mechanism Indicators

| Indicator | Result |
|-----------|--------|
| scores_in_range [0,1] | False (some scores outside range due to rescaling) |
| scores_have_variance (std > 0.01) | True |
| auroc_computable (both label classes present) | True |
| auroc_not_random (auroc > 0.45) | False (SCG AUROC = 0.38) |

**Mechanism activated: False**

## Analysis

**Gate failure root cause:** SCG BERTScore produces AUROC = 0.378 while SE produces 0.286, giving delta = 0.092 — 3x above the 0.03 gate. The hypothesis that SCG and SE capture similar semantic consistency fails: they diverge substantially.

**Secondary finding:** SCG AUROC = 0.378 is below 0.5, meaning SCG scores are *anti-correlated* with uncertainty (higher SCG score → more likely correct). This is expected given BERTScore measures semantic *similarity* (higher = more consistent = more certain), but the direction was correct as passed: higher SCG score = more uncertain = should predict incorrectness. The anti-correlation suggests BERTScore fails to discriminate confident-wrong from uncertain-correct answers on this dataset.

**SE AUROC = 0.286** is similarly poor (also anti-correlated), consistent with h-m2 findings. Both SE and SCG fail as uncertainty estimators on this N=98 subset, but they fail *differently* — their AUROC gap is 0.092, not near zero.

**Why SCG ≠ SE:** BERTScore captures lexical-semantic overlap between surface strings, while SE groups samples via NLI entailment. For short QA answers (1-3 words), BERTScore is dominated by word overlap rather than semantic equivalence. Two answers can be paraphrases (NLI-entailed) but have low BERTScore (different words), causing SCG and SE to diverge.

## Implementation Notes

- SelfCheckBERTScore requires spacy `en_core_web_sm` for sentence splitting; installed during ENV-1
- Short QA answers (<10 chars) were padded before passing to `selfcheck.predict()` to avoid empty sentence-split crash in selfcheckgpt internals
- `rescale_with_baseline=True` caused some scores slightly outside [0,1]; no impact on AUROC computation

## Figures

- `figures/auroc_comparison.png` — bar chart: SCG vs SE vs TE AUROC with 95% CI
- `figures/scg_score_distribution.png` — SCG score distribution by correctness
- `figures/scg_vs_se_scatter.png` — per-question scatter: SCG vs SE scores
- `figures/roc_curves.png` — ROC curves for all three methods

## Gate Verdict

**FAIL** — |auroc_scg - auroc_se| = 0.0920 > 0.03

SCG BERTScore does not approximate SE on this task. The mechanism hypothesis (BERTScore implicitly captures NLI-level consistency) is not supported.

## Recommendation for H-M4

H-M4 should investigate why SE AUROC is low (0.286). Options:
1. Use SE with correct sign convention (h-e1 negates scores for AUROC; h-m2/h-m3 do not)
2. Test whether SE AUROC improves to h-e1's reported value (~0.57) after sign correction
3. If SE itself is broken in this pipeline, fix it before comparing SCG to SE
