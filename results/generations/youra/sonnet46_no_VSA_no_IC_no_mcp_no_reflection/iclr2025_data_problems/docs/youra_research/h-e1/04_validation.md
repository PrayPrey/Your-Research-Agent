# H-E1 Phase 4 Validation Report

**Hypothesis**: At matched training scale (~300B tokens), OLMo-7B achieves a higher MMLU/HellaSwag ratio than Pythia-6.9B, reflecting OLMo's curated corpus producing better generalization balance.

**Date**: 2026-08-31  
**Status**: COMPLETED — Gate FAILED

---

## 1. Experimental Setup

| | Pythia-6.9B | OLMo-7B |
|---|---|---|
| Model ID | `EleutherAI/pythia-6.9b` | `allenai/OLMo-7B` |
| Revision | `step143000` | `step68000-tokens301B` |
| Training tokens | ~299.9B | ~301B |
| Token deviation | −0.03% | +0.33% |

Evaluation: lm-evaluation-harness v0.4.12, `--limit 500` fast eval on H100 NVL.

Tasks: MMLU (5-shot), HellaSwag (0-shot), ARC-Easy (25-shot), ARC-Challenge (25-shot).

---

## 2. Raw Results

| Metric | Pythia-6.9B | OLMo-7B |
|--------|------------|---------|
| MMLU mean acc | 0.2588 | 0.2463 |
| HellaSwag acc | 0.4580 | 0.4580 |
| ARC-Easy acc | 0.6700 | 0.6400 |
| ARC-Challenge acc_norm | 0.3360 | 0.2960 |

---

## 3. Derived Metrics

| Metric | Value |
|--------|-------|
| Pythia MMLU/HellaSwag ratio | 0.5650 |
| OLMo MMLU/HellaSwag ratio | 0.5383 |
| Ratio difference (OLMo − Pythia) | **−0.0265** |
| Bootstrap mean diff | −0.0265 |
| Bootstrap 95% CI | [−0.0447, −0.0069] |
| Bootstrap p-value (one-sided) | 0.996 |
| Cohen's d | −2.732 |
| ARC delta Pythia | −0.334 |
| ARC delta OLMo | −0.344 |

---

## 4. MUST_WORK Gate

| Criterion | Threshold | Result | Pass? |
|-----------|-----------|--------|-------|
| ratio_diff > 0.02 | > 0.02 | −0.0265 | ✗ FAIL |
| p-value < 0.05 | < 0.05 | 0.996 | ✗ FAIL |
| Cohen's d > 0.2 | > 0.2 | −2.732 | ✗ FAIL |
| **Primary gate** | ALL above | — | **FAILED** |
| ARC delta OLMo > ARC delta Pythia | secondary | −0.344 < −0.334 | ✗ FAIL |
| **Secondary gate** | above | — | **FAILED** |

**Verdict: FAILED**

---

## 5. Interpretation

Contrary to the hypothesis, Pythia-6.9B achieves a *higher* MMLU/HellaSwag ratio (0.565) than OLMo-7B (0.538) at matched training scale. The difference is statistically significant in the *wrong* direction (p=0.996 for the one-sided test that OLMo > Pythia; CI entirely negative). OLMo also performs worse on ARC-Challenge.

Possible explanations:
- OLMo's curated corpus may improve downstream fine-tuning rather than zero/few-shot generalization balance at 300B tokens.
- The MMLU/HellaSwag ratio is not a robust proxy for "generalization balance" at this scale.
- 500-sample fast eval may introduce noise; but the direction is consistent and CI does not include 0.

---

## 6. Figures

- `figures/absolute_scores.png` — Bar chart of task accuracies for both models
- `figures/ratio_delta.png` — MMLU/HellaSwag ratio with 95% CI
- `figures/mmlu_heatmap.png` — Per-subject MMLU accuracy heatmap (61 subjects)
- `figures/bootstrap_dist.png` — Bootstrap distribution of ratio differences

---

## 7. Outputs

- `experiment_results.json` — Full metrics JSON
- `results/pythia-6.9b-300B-fast/` — Pythia lm-eval outputs
- `results/olmo-7b-300B-fast/` — OLMo lm-eval outputs
- `code/` — All experiment code (config.py, evaluator.py, metrics.py, figures.py, run.py)
- `code/tests/` — 19 unit tests (all passing)

---

## 8. Conclusion

H-E1 hypothesis **not confirmed**. At ~300B training tokens, OLMo-7B does not achieve higher MMLU/HellaSwag ratio than Pythia-6.9B. The null hypothesis cannot be rejected; evidence points the opposite direction.
