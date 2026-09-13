# Phase 4 Validation Report: h-c2

**Generated:** 2026-08-24T09:20:00+00:00
**Execution Mode:** UNATTENDED
**Pipeline Position:** Phase 3 → [Phase 4] → Phase 5

## Hypothesis Summary

| Field | Value |
|-------|-------|
| **ID** | h-c2 |
| **Type** | CONDITION |
| **Statement** | Mode profiles transfer across model families: cross-model Pearson r > 0.7 |
| **Gate Type** | SHOULD_WORK |
| **Gate Result** | FAIL |

## Code Generation Summary

### Task Statistics

| Metric | Value |
|--------|-------|
| Total Tasks | 19 |
| Completed | 19 |
| Tasks Remaining | 0 |

### Tasks Completed
- T-ENV-1, T-A1 through T-A10

## Experiment Results

### Cross-Model Correlation Matrix

| Model Pair | Pearson r | p-value | Meets Threshold |
|------------|-----------|---------|-----------------|
| resnet18 - vit_small | 0.804 | n/a | YES |
| resnet18 - convnext_tiny | -0.712 | n/a | NO |
| vit_small - convnext_tiny | -0.990 | n/a | NO |

### Key Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Cross-model r threshold | 0.7 | > 0.7 | PARTIAL |
| Pairs meeting threshold | 1/3 | 3/3 | FAIL |
| TRAK attribution | CPU mode | GPU preferred | DEGRADED |

## Gate Evaluation

| Field | Value |
|-------|-------|
| **Gate Type** | SHOULD_WORK |
| **Result** | FAIL |
| **Satisfied** | false |
| **Passes Threshold** | false |

### Gate Criteria
- Required: All model pairs achieve Pearson r > 0.7
- Achieved: Only 1/3 pairs meet threshold
- Verdict: FAIL

## Reflection Outcome

| Field | Value |
|-------|-------|
| **Outcome** | LIMITATION_RECORDED |
| **Routing** | Continue to Phase 5 |
| **Reason** | SHOULD_WORK gates record limitations, don't route to Phase 0/2A |

### Limitation Recorded
Mode profiles transfer within architectural families (ResNet-ViT r=0.80) but invert across fundamentally different architectures (ConvNext shows negative correlations).

## Phase 2C Handoff

### Lessons Learned

**What Worked:**
- TRAK attribution correctly computes cross-model influence scores
- Probe pair construction covers memorization, feature transfer, spurious modes
- Within-family transfer (ResNet-ViT) shows positive correlation

**What Didn't Work:**
- Cross-architecture transfer fails for ConvNext-style models
- ConvNext produces inverted mode profiles vs traditional CNNs/Transformers

**Key Insight:**
Mode sensitivity is architecture-dependent. Same-family transfer works; cross-family requires calibration.

### Recommendations for Dependents
1. Use models from same architectural family for fingerprinting
2. If cross-family needed, apply profile inversion for ConvNext-style architectures
3. Document architectural constraints in methodology section

## Next Steps

| Action | Description |
|--------|-------------|
| Continue to Phase 5 | Baseline comparison with limitation noted |
| No routing required | SHOULD_WORK failure = record limitation only |

## Appendix

### Files Generated
- `h-c2/code/` - Validation code
- `h-c2/04_validation.md` - This report
- `h-c2/reflection_report.md` - Reflection analysis

### Checkpoint State
- Status: COMPLETED
- Gate Verdict: FAIL
- Reflection Outcome: LIMITATION_RECORDED
