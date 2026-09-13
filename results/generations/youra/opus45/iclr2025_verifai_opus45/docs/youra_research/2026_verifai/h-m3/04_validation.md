# Phase 4 Validation Report: H-M3

**Hypothesis:** Non-Monotonicity Confirmation (G3 >= G4)
**Statement:** G4 (full trace) does not significantly outperform G3 (G4 <= G3 + 2%), confirming non-monotonic relationship
**Date:** 2026-03-30
**Gate Type:** SHOULD_WORK

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Gate Result** | **FAIL** |
| **Gate Type** | SHOULD_WORK |
| **G3 Success Rate** | 16.78% (51/304) |
| **G4 Success Rate** | 22.70% (69/304) |
| **Difference (G4-G3)** | +5.92% |
| **Threshold** | ≤ 2% |
| **McNemar p-value** | 4.0e-05 (significant) |
| **TOST Equivalent** | No |

**Conclusion:** G4 significantly outperforms G3 by 5.92% (p<0.0001), which contradicts the non-monotonicity hypothesis. The data shows that more detailed error feedback (G4 full trace) actually helps more than simpler feedback (G3 error+line).

---

## Hypothesis Details

### Statement
G4 (full trace) does not significantly outperform G3 (G4 <= G3 + 2%), confirming non-monotonic relationship

### Gate Condition
- **Primary:** G4 ≤ G3 + 2% (practical equivalence or G3 superiority)
- **Statistical:** McNemar p-value interpretation
  - If p < 0.05 AND G4 > G3: Gate **FAILS** (G4 significantly better)
  - If p >= 0.05: Gate PASS (no significant difference)
  - If p < 0.05 AND G3 > G4: Gate PASS (G3 significantly better)

### Prerequisites
- H-M1: COMPLETED (PASS) - ANOVA showed significant granularity effect

---

## Experimental Results

### Data Summary

| Metric | Value |
|--------|-------|
| Total Paired Samples | 304 |
| G3 Successes | 51 |
| G4 Successes | 69 |
| Both Success | 50 |
| G3 Only Success | 1 |
| G4 Only Success | 19 |
| Both Fail | 234 |

### Contingency Table (2x2 McNemar)

|           | G4 Success | G4 Fail |
|-----------|------------|---------|
| G3 Success | 50 | 1 |
| G3 Fail | 19 | 234 |

The off-diagonal cells (b=1, c=19) show asymmetry: G4 uniquely succeeds on 19 problems while G3 uniquely succeeds on only 1.

### Statistical Tests

#### McNemar's Test
- **Statistic:** 19.0
- **p-value:** 4.0e-05
- **Significant:** Yes (p < 0.05)
- **Interpretation:** G4 significantly outperforms G3

#### TOST Equivalence Test (±2% margin)
- **G3 Rate:** 16.78%
- **G4 Rate:** 22.70%
- **Difference:** +5.92%
- **TOST p-value:** >0.05
- **Equivalent:** No
- **Interpretation:** G4 exceeds G3 by more than 2% margin

#### Confidence Interval
- **Point Estimate:** +5.92%
- **95% CI:** [-0.39%, 12.23%]
- **Interpretation:** CI includes 0 but point estimate exceeds 2% margin

---

## Gate Evaluation

### Gate Logic Applied
```
IF McNemar p < 0.05 AND G4 > G3:
    → FAIL: G4 significantly outperforms G3, contradicts non-monotonicity
```

### Result
- **Gate Passed:** No
- **Reason:** G4 significantly outperforms G3 (p=0.0000, diff=5.92%): contradicts non-monotonicity

### Limitation Recorded (SHOULD_WORK Gate)
Since this is a SHOULD_WORK gate, the result is recorded as a **limitation** rather than blocking the pipeline:

> **Limitation:** The hypothesis that G3 >= G4 (non-monotonicity) was not supported. Statistical analysis shows G4 (full trace) significantly outperforms G3 (error+line) by 5.92% (McNemar p=4.0e-05). This suggests that for the specific LLM and task configuration tested, more detailed feedback is beneficial.

---

## Figures Generated

1. **gate_comparison.png** - Bar chart comparing G3 vs G4 success rates with 2% margin threshold
2. **contingency_heatmap.png** - 2x2 heatmap of paired outcomes
3. **confidence_interval.png** - 95% CI for G4-G3 difference
4. **granularity_curve.png** - G0-G4 success rates showing overall pattern

---

## Interpretation and Implications

### Key Findings

1. **G4 > G3 with statistical significance:** McNemar's test (p=4.0e-05) confirms that G4 (full trace) performs significantly better than G3 (error+line).

2. **Difference exceeds practical threshold:** The 5.92% difference exceeds the 2% equivalence margin specified in the hypothesis.

3. **Non-monotonicity NOT confirmed:** The original hypothesis expected G3 >= G4 or equivalence. The data shows the opposite.

### Contextual Notes

From H-M1 results, we observed:
- G0: 41.8%, G1: 40.8%, G2: 18.4%, G3: 16.8%, G4: 22.7%
- The non-monotonic pattern exists at the G0/G1 → G2/G3 transition
- However, G4 does show improvement over G3

This suggests:
- **Information overload effect exists** (G0/G1 > G2/G3)
- **But full traces help recover** (G4 > G3)
- The non-monotonicity is partial, not complete

### Impact on Research

This result modifies the research narrative:
- Non-monotonicity exists in intermediate levels (G2-G3)
- Full traces (G4) provide recovery, not degradation
- Optimal feedback may be G0/G1 (minimal) or G4 (full), with G2-G3 being suboptimal

---

## Output Files

| File | Path |
|------|------|
| Contingency Table | `code/results/contingency_table.json` |
| Statistical Tests | `code/results/statistical_tests.yaml` |
| Gate Metrics | `code/results/metrics.yaml` |
| Gate Comparison | `code/figures/gate_comparison.png` |
| Contingency Heatmap | `code/figures/contingency_heatmap.png` |
| Confidence Interval | `code/figures/confidence_interval.png` |
| Granularity Curve | `code/figures/granularity_curve.png` |
| Experiment Log | `code/experiment.log` |

---

## State Updates

### verification_state.yaml
- `sub_hypotheses.h-m3.validation.status`: COMPLETED
- `sub_hypotheses.h-m3.validation.result`: FAIL - G4 significantly outperforms G3
- `sub_hypotheses.h-m3.gate.satisfied`: false
- `sub_hypotheses.h-m3.completed`: true

### Pipeline Continuation
- **Gate Type:** SHOULD_WORK (optional)
- **Action:** Record limitation and continue to Phase 5
- **Limitation:** Non-monotonicity hypothesis not supported by statistical analysis

---

*Generated by Phase 4 Workflow*
*Completed: 2026-03-30T10:27:30Z*
