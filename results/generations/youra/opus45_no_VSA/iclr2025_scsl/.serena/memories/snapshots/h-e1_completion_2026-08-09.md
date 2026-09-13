# Hypothesis Completion Snapshot: h-e1

**Date:** 2026-08-09T11:00:00+00:00
**Hypothesis:** h-e1
**Statement:** Final-layer gradient cosine similarity is significantly lower on Waterbirds (spurious) than Shuffled Waterbirds (decorrelated) during early training, with non-overlapping 95% CIs
**Final Status:** FAILED
**Gate Result:** FAIL

## Results
- Validation: FAIL
- Gate Type: MUST_WORK
- Reflection: Direction of effect reversed from prediction
- Lessons: Gradient cosine similarity shows HIGH alignment under spurious correlation, not low

## Key Findings
- Spurious (Waterbirds): cosine_sim = 0.926
- Control (Shuffled): cosine_sim = 0.393
- Hypothesis predicted opposite direction

## Routing
- Route to: Phase 0
- Reason: Core existence hypothesis falsified

---
*Per-hypothesis snapshot for Phase 2A reference*
