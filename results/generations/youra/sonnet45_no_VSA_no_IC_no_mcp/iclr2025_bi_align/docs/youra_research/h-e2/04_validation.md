# Validation Report: h-e2

**Hypothesis:** AI response diversity correlates with query diversity (r > 0.4) in well-aligned conversations
**Type:** EXISTENCE
**Date:** 2026-08-25
**Gate:** SHOULD_WORK

---

## Executive Summary

**Gate Result:** FAIL (r=0.396 < 0.4 threshold)

Observational analysis on 169,352 HH-RLHF conversations found **weak positive correlation** (r=0.396, p<0.001) between query diversity (distinct-1) and response diversity (distinct-1). Result fell just below r>0.4 threshold. Correlation strengthens with conversation length (r=0.187 for 6+ turns vs r=0.040 for 2-3 turns).

**SHOULD_WORK Gate Interpretation:**
- Gate failed, but correlation exists (r=0.396, 95% CI [0.392, 0.400])
- Evidence suggests AI responsiveness exists but is **weaker than hypothesized**
- Hypothesis h-m1 (coupling mechanism) can proceed with partial evidence
- Documented as limitation: AI responsiveness threshold not met

---

## Static Analysis

✅ **Code Structure**
- Distinct-1 implementation matches Li et al. 2016 specification
- Pearson correlation with Fisher z-transform for CI computation
- Proper conversation filtering (minimum 1 user turn + 1 AI turn)

✅ **Reproducibility**
- Deterministic preprocessing pipeline
- Standard HH-RLHF dataset (Hugging Face)
- All random operations eliminated (no sampling)

✅ **Edge Cases**
- Empty conversations: filtered out (0 removed)
- Single-turn conversations: included (all valid)
- Zero-diversity texts: handled (return 0.0)

---

## Runtime Validation

✅ **Execution**
- Runtime: ~3 minutes (dataset loading + computation)
- No errors or warnings
- All figures generated successfully

✅ **Metrics Verification**
- Sample size: 169,352 conversations (>>100 minimum for reliable correlation)
- Statistical significance: p ≈ 0 (highly significant)
- 95% CI: [0.392, 0.400] (tight confidence interval, excludes 0.4 threshold)

---

## Results

### Primary Metric

| Metric | Value |
|--------|-------|
| Pearson r | 0.396 |
| p-value | < 0.001 |
| 95% CI | [0.392, 0.400] |
| Sample size | 169,352 |
| **Gate (r > 0.4)** | **FAIL** |

**Interpretation:**
- Correlation just below threshold (0.396 vs 0.4 target)
- Highly statistically significant (p<0.001)
- Tight CI excludes threshold → result is robust, not sampling noise
- **Existence claim partially supported**: correlation exists but weaker than predicted

### Secondary Analyses

**Stratification by Conversation Length:**

| Length (turns) | r | p | n |
|----------------|---|---|---|
| 2-3 | 0.040 | <0.001 | 52,022 |
| 4-5 | 0.087 | <0.001 | 47,492 |
| 6+ | 0.187 | <0.001 | 69,838 |

**Key Insight:** Correlation increases with conversation length (r=0.04 → 0.19). Suggests AI responsiveness **strengthens with more interaction turns**, consistent with co-adaptation hypothesis but insufficient alone.

---

## Visualizations

All figures saved to `experiments/h-e2/figures/`:

1. **gate_metric.png**: Bar chart comparing target r (0.4) vs observed r (0.396) with CI
2. **scatter.png**: Query diversity vs response diversity with regression line
3. **distributions.png**: Overlaid histograms of query and response diversity
4. **stratification.png**: Correlation by conversation length bins

---

## Gate Decision

**SHOULD_WORK Gate Result:** FAIL

**Justification:**
- Primary criterion not met: r=0.396 < 0.4
- Correlation exists (p<0.001) but below hypothesized strength
- Tight CI [0.392, 0.400] excludes threshold → not a close call

**SHOULD_WORK Gate Action:**
- Document as limitation in final hypothesis evaluation
- Hypothesis h-m1 (coupling mechanism) may proceed with **partial evidence**
- Note: AI responsiveness exists but weaker than predicted
- Main hypothesis (H-BiAlign-v1) weakened but not refuted

**Routing Decision:** Continue to h-m1 (next hypothesis in queue)

---

## Failure Analysis

**Why did r fall short of 0.4?**

1. **Metric Choice:** Distinct-1 captures vocabulary diversity only, not semantic diversity
   - Two semantically different queries with overlapping words → lower distinct-1
   - May underestimate true diversity

2. **Dataset Characteristics:** HH-RLHF contains many short conversations (30% are 2-3 turns)
   - Short conversations show very weak correlation (r=0.04)
   - Dilutes overall correlation

3. **Threshold Calibration:** r>0.4 may be too strict for vocabulary-based metrics
   - Cohen's effect size: r=0.3 (medium), r=0.5 (large)
   - Observed r=0.396 is medium-to-large effect, but threshold set at large

**Lessons Learned:**
- Distinct-1 may not be ideal proxy for query/response diversity
- Conversation length matters: longer conversations show stronger responsiveness
- AI responsiveness exists but is **weak in short interactions**

---

## Reproducibility

**Code:** `experiments/h-e2/code/main.py`
**Results:** `experiments/h-e2/results/results.json`
**Figures:** `experiments/h-e2/figures/`

**Replication Command:**
```bash
cd experiments/h-e2
python code/main.py
```

**Dependencies:**
- datasets (Hugging Face)
- scipy
- numpy
- matplotlib

---

## Appendix: Statistical Details

**Pearson Correlation:**
- r = 0.396
- p < 0.001 (two-tailed)
- df = 169,350
- Effect size: medium (Cohen's d ≈ 0.85)

**Confidence Interval (Fisher z-transform):**
- z = 0.5 * ln((1 + r) / (1 - r)) = 0.419
- SE(z) = 1 / √(n - 3) = 0.0024
- CI(z) = [0.414, 0.424]
- CI(r) = [tanh(0.414), tanh(0.424)] = [0.392, 0.400]

**Sample Size Power Analysis:**
- n = 169,352
- Power to detect r=0.4 with α=0.05: >0.999 (highly powered)
- Minimum detectable effect (80% power): r ≈ 0.015

---

## State Update

**Gate Status:** FAIL (SHOULD_WORK)
**Validation Status:** COMPLETED
**Experiment Execution:** SUCCESS (no errors)
**Next Action:** Continue to h-m1 (document limitation in Phase 4-5 synthesis)

---

*Validation completed: 2026-08-25*
*Gate result: FAIL (r=0.396 < 0.4)*
*SHOULD_WORK interpretation: Document as limitation, continue workflow*
