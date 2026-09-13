# H-M2 Validation Report

**Hypothesis ID:** H-M2
**Date:** 2026-08-18
**Gate Type:** SHOULD_WORK

---

## Hypothesis Statement

BiDPO models generate responses with higher collaboration scores than DPO.

---

## Experiment Status

**Status:** COMPLETED
**Result:** FAILED

---

## Results Summary

| Metric | Value |
|--------|-------|
| DPO Mean | 0.3728 |
| DPO Std | 0.3294 |
| BiDPO Mean | 0.3782 |
| BiDPO Std | 0.3333 |
| Mean Difference | +0.0054 |
| t-statistic | 0.684 |
| p-value (one-sided) | 0.247 |
| Cohen's d | 0.016 |
| N Samples | 500 |

---

## Gate Evaluation

**Gate Type:** SHOULD_WORK
**Gate Criteria:**
- p < 0.05 (one-sided)
- BiDPO mean > DPO mean
- Cohen's d >= 0.2 (small effect)

**Results:**
- BiDPO mean > DPO mean: PASS (0.3782 > 0.3728)
- p < 0.05: FAIL (p = 0.247)
- Cohen's d >= 0.2: FAIL (d = 0.016)

**Gate Verdict:** FAILED

BiDPO shows a marginal improvement in collaboration scores (+0.54%), but the effect is not statistically significant and the effect size is negligible.

---

## Timing

| Phase | Duration |
|-------|----------|
| DPO generation | 66.4 min |
| BiDPO generation | 50.9 min |
| Total experiment | ~2 hours |

---

## Figures Generated

- `score_comparison_bar.png` - Mean score comparison
- `score_distributions.png` - Distribution histograms
- `per_prompt_scatter.png` - Per-prompt correlation
- `component_breakdown.png` - Score component analysis
- `length_vs_score.png` - Response length vs score

---

## Interpretation

The BiDPO model shows a small positive direction (+0.54% higher mean collaboration score), but:
1. The difference is not statistically significant (p=0.247)
2. The effect size is negligible (Cohen's d=0.016, far below the 0.2 threshold)

This suggests that while BiDPO training integrates stably (H-M1 passed), the collaboration score signal may not transfer effectively to generation quality at inference time on this task.

---

## Artifacts

### Output Files
- `code/outputs/results.json` - Statistical results
- `code/outputs/responses.json` - Raw responses (500 prompts x 2 models)
- `figures/*.png` - Visualization suite

### Code Modules
- `code/config.py` - Configuration constants
- `code/data.py` - Prompt extraction
- `code/models.py` - Model loading
- `code/generate.py` - Response generation
- `code/collab_score.py` - Scoring function
- `code/analysis.py` - Statistical tests
- `code/visualize.py` - Figure generation
- `code/run_experiment.py` - Main orchestration
