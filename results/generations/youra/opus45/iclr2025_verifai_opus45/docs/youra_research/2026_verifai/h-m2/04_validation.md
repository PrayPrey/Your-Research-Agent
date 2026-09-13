# Phase 4 Validation Report: H-M2

**Hypothesis:** G3 Superiority Over Minimal Feedback
**Date:** 2026-03-30
**Status:** COMPLETED
**Gate Result:** FAIL (SHOULD_WORK)

---

## Executive Summary

H-M2 tested whether G3 (error+line) achieves at least 10 percentage points higher repair success than G0 (pass/fail only). This hypothesis was **PRE-FALSIFIED** based on H-M1 results, which showed the opposite relationship.

**Result:** The hypothesis **FAILED**. G0 significantly outperforms G3 by 25 percentage points (41.8% vs 16.8%), with McNemar's test p-value of 5.23e-22. This is the opposite of the hypothesized direction.

---

## Hypothesis Details

| Field | Value |
|-------|-------|
| ID | h-m2 |
| Type | MECHANISM |
| Statement | G3 (error+line) achieves at least 10 percentage points higher repair success than G0 (pass/fail only) |
| Gate Type | SHOULD_WORK |
| Prerequisites | h-m1 (PASSED) |

---

## Experiment Configuration

### Analysis Type
- **Method:** Post-hoc statistical analysis of H-M1 repair results
- **Test:** McNemar's exact test for paired binary data
- **Data Source:** h-m1/results/repair_results.json

### Dataset
- **Name:** MBPP Runtime Error Cases (from H-M1)
- **Size:** 304 paired samples
- **Structure:** Each sample has G0 and G3 repair outcomes

### Gate Condition
- **Requirement:** (G3 success rate) - (G0 success rate) >= 10 percentage points
- **Additional:** McNemar's test p < 0.05 with G3 favored

---

## Results

### Success Rates

| Granularity | Success Rate | Successes | Total |
|-------------|--------------|-----------|-------|
| G0 (pass/fail only) | **41.8%** | 127 | 304 |
| G3 (error+line) | **16.8%** | 51 | 304 |

**Difference (G3 - G0):** -25.0 percentage points
**95% CI:** [-32.0, -18.0] pp

### Contingency Table

|              | G3 Fail | G3 Success |
|--------------|---------|------------|
| G0 Fail      | 176     | 1          |
| G0 Success   | 77      | 50         |

- **Discordant pairs (G0 fail → G3 success):** 1
- **Discordant pairs (G0 success → G3 fail):** 77

### McNemar's Test

| Metric | Value |
|--------|-------|
| Statistic | 1.0 |
| p-value | **5.23e-22** |
| Favors | G0 |
| Significant | Yes |

---

## Gate Evaluation

### Condition Checks

| Condition | Required | Actual | Status |
|-----------|----------|--------|--------|
| Difference >= 10pp | +10.0pp | -25.0pp | **FAIL** |
| McNemar p < 0.05 | Yes | Yes (5.23e-22) | PASS |
| Favors G3 | Yes | No (favors G0) | **FAIL** |

### Verdict

**GATE RESULT: FAIL**

**Reason:** difference=-25.0pp (need >= 10pp); favors G0 not G3

---

## Mechanism Verification

| Check | Result |
|-------|--------|
| N pairs verified | 304 ✓ |
| G0 has successes | Yes (127) ✓ |
| G3 has successes | Yes (51) ✓ |
| McNemar test ran | Yes ✓ |
| Mechanism verified | **True** |

---

## Generated Figures

1. **g0_vs_g3_comparison.png** - Bar chart comparing success rates
2. **contingency_heatmap.png** - 2x2 contingency table visualization
3. **difference_ci.png** - Difference estimate with 95% CI
4. **gate_summary.png** - Gate evaluation summary

---

## Scientific Interpretation

### Key Finding

The data strongly contradicts the hypothesis that detailed error feedback (G3) improves repair success. Instead, **minimal feedback (G0) significantly outperforms detailed feedback (G3)** by 25 percentage points.

### Statistical Significance

- McNemar's test p-value (5.23e-22) indicates extremely strong evidence against the null hypothesis of no difference
- The discordant pair ratio (77:1) strongly favors G0
- The 95% CI [-32.0, -18.0] pp excludes zero and the +10pp threshold

### Implications

1. **Detailed error messages may confuse the LLM** rather than help it
2. **Simple pass/fail feedback** provides sufficient signal for repair
3. This finding is consistent with H-M1's observation that simpler feedback (G0, G1) outperforms detailed feedback (G2-G4)

---

## Limitation Note

This hypothesis was **PRE-FALSIFIED** by H-M1 results but was formally tested for scientific completeness. The SHOULD_WORK gate failure does not block pipeline continuation but is documented as a limitation of the original hypothesis.

**Limitation:** G3 (error+line) does not outperform G0 (pass/fail). The inverse relationship holds - simpler feedback is more effective for LLM code repair.

---

## Output Files

| File | Path | Description |
|------|------|-------------|
| Results JSON | `code/results/comparison_results.json` | Full analysis results |
| Metrics YAML | `code/results/metrics.yaml` | Key metrics summary |
| Figures | `figures/*.png` | 4 visualization figures |
| Experiment Log | `code/experiment.log` | Execution log |

---

## Next Steps

As a SHOULD_WORK gate failure:
1. **Document limitation** - This finding contradicts the hypothesis
2. **Continue pipeline** - SHOULD_WORK failures do not block
3. **Proceed to Phase 5** - For baseline comparison (if applicable)
4. **Include in paper** - Document unexpected inverse relationship

---

## Validation Checklist

- [x] Experiment code runs without errors
- [x] McNemar's test produces valid p-value
- [x] Difference calculated correctly
- [x] All 304 paired samples processed
- [x] Gate evaluation complete
- [x] Figures generated
- [x] Results persisted
- [x] Limitation documented

---

*Generated by Phase 4 Validation Workflow*
*Timestamp: 2026-03-30T11:02:00Z*
