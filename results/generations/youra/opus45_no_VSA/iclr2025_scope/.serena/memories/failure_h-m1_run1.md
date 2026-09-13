# Phase 4 Failure Record: h-m1 (Run 1)

**Date:** 2026-08-09T15:45:00+00:00
**Hypothesis:** h-m1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** HYPOTHESIS_NOT_SUPPORTED
**Gate Type:** MUST_WORK

## Hypothesis Statement

Boundary-state AUROC for span prediction exceeds local-token AUROC by ≥0.10 (three-way comparison with oracle)

## Performance Gap

| Metric | Boundary | Local | Delta | Threshold |
|--------|----------|-------|-------|-----------|
| AUROC | 0.9849 | 0.9729 | +0.012 | ≥0.10 |

Oracle AUROC: 0.7899 (sanity check failed: oracle < boundary)

## Root Cause Analysis

- Span-predictive information is distributed across SSM hidden states, NOT concentrated at chunk boundaries
- Local mid-chunk positions encode equally informative hidden states for answer proximity prediction
- High AUROC for both boundary (0.98) and local (0.97) confirms h-e1 finding, but refutes boundary-specific mechanism
- Oracle underperformance (0.79) suggests task measures proximity context rather than direct answer localization

## Lessons Learned

1. SSM hidden states encode span-predictive information throughout sequence, not just at boundaries
2. Boundary accumulation hypothesis for state-guided routing is not supported
3. Alternative mechanisms should explore content-based routing rather than position-based

## Feedback for Next Phase

### Suggested Modifications
- Consider content-based routing using hidden state features regardless of position
- Explore temporal attention patterns rather than boundary accumulation
- Re-examine whether chunk boundaries provide any unique routing signal

### What NOT To Do
- Do not assume boundary positions have privileged access to span-relevant context
- Do not design routing mechanisms that rely on boundary-specific features

### What Showed Promise
- High overall AUROC confirms SSM states carry span-predictive information (h-e1 validated)
- Linear probes successfully decode proximity information from hidden states

---
*For cross-phase reference*
*Written at: 2026-08-09T15:45:00+00:00*