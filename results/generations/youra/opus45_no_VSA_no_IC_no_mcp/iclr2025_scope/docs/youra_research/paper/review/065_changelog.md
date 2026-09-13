# Phase 6.5 Changelog

**Paper:** TC-SSM
**Review Date:** 2026-08-28

## Summary

| Round | Changes Made |
|-------|--------------|
| R1 | 1 edit (baseline explanation) |
| R2 | 0 edits (numerical verification only) |
| **Total** | **1 edit** |

---

## Round 1 Changes

### Change 1: Baseline Comparison Explanation

**Issue ID:** R1-01  
**Severity:** MAJOR  
**Category:** baseline_fairness

**Location:** Section 5 Results, "Adaptation Preservation (RQ4)" subsection

**Before:**
```
TC-SSM achieves 0.25% accuracy gap versus transformer—20× better than the 5% threshold. Adaptation completes in just 14 gradient steps—7× faster than the 100-step threshold.
```

**After:**
```
TC-SSM achieves 0.25% accuracy gap versus transformer—20× better than the 5% threshold. Adaptation completes in just 14 gradient steps—7× faster than the 100-step threshold. The gap between TC-SSM and post-hoc approaches (Mamba + LoRA: 1.92%, standard distillation: 3.54%) reflects the key insight: adaptation capability must be preserved *during* conversion, not recovered afterward. Post-hoc LoRA operates on degraded representations from which task structure has already been stripped.
```

**Rationale:** Skeptical Expert flagged that baseline underperformance was unexplained, potentially appearing as a strawman. Added explanation tying the performance gap to the paper's central thesis.

---

## Round 2 Changes

None. All numerical claims verified against Phase 4 source files.

---

## Issues Deferred to Human Review

| ID | Type | Description | Location |
|----|------|-------------|----------|
| R1-02 | clarity | Memory bandwidth hypothesis could use elaboration | Section 6 Discussion |

See `065_human_review_notes.md` for details.

---

## Verification Trail

All numerical claims in final paper traced to:
- `h-e1/04_validation.md` — cluster metrics
- `h-m1/04_validation.md` — embedding probe accuracy
- `h-m2/04_validation.md` — overhead, F-statistic
- `h-m3/04_validation.md` — accuracy, adaptation steps
- `065_ground_truth.yaml` — consolidated reference
