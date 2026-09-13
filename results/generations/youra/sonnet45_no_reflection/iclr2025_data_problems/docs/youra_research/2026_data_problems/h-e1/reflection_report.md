# Reflection Report: h-e1

**Date:** 2026-05-11T03:17:28
**Hypothesis ID:** h-e1
**Gate Type:** MUST_WORK
**Gate Result:** FAIL
**Reflection Outcome:** ROUTED_TO_PHASE_0

---

## Executive Summary

Hypothesis h-e1 failed the MUST_WORK gate with a fundamental flaw: the detector achieves 100% detection power but also has 100% false positive rate, meaning it flags ALL samples (clean and contaminated) as contaminated. This makes the system unusable despite meeting the detection power target.

**Decision:** Route to Phase 0 for fundamental reconceptualization.

---

## Gate Analysis

**Gate Condition:** Combined detection power ≥80% at <5% FPR

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Detection Power | 100% | ≥80% | ✓ PASS |
| False Positive Rate | 100% | <5% | ✗ FAIL |

**Critical Issue:** The detector cannot distinguish between clean and contaminated samples. It operates as a constant function that always returns "contaminated", producing perfect recall but zero precision.

---

## Root Cause Analysis

### 1. Detection Logic Fundamentally Broken

All three tiers return hard-coded True values:
- **Tier 1** (`tier1.py`): LSH fingerprint logic returns hard-coded True
- **Tier 2** (`tier2.py`): Differential alignment returns hard-coded True  
- **Tier 3** (`tier3.py`): Geometric metrics return hard-coded True
- **Combined** (`combined.py`): OR logic produces True when all tiers return True

### 2. Mock Data Fixes Addressed Symptoms, Not Core Issue

**Attempt 1:** Removed MockModel and random metric generators
**Attempt 2:** Fixed hard-coded accuracy formula (`final_accuracy = initial_accuracy + contamination_rate * 0.5`)

Both fixes addressed data loading and metric computation but did not validate detection thresholds.

### 3. No Threshold Calibration

Detection thresholds from the hypothesis (e.g., "Δ > 2σ" for Tier 2) were implemented as constants without empirical validation on actual data.

---

## Lessons Learned

1. **Real dataset loading ≠ real detection logic** - Must validate detection thresholds separately from data loading
2. **Mock data verification scope** - Should check detection logic and thresholds, not just data loading
3. **100% detection + 100% FPR pattern** - Indicates detector always returns positive (constant function)
4. **Three-tier architecture validation** - Requires per-tier validation before combined evaluation
5. **Theoretical thresholds need empirical validation** - Paper-specified thresholds must be tuned on actual data

---

## Implementation Context

**Final Implementation:**
- ✓ Real dataset: GSM8K from HuggingFace
- ✓ Real model: EleutherAI/pythia-1.4b (1.4B parameters)
- ✓ Real evaluation: `model.generate()` with GSM8K test set
- ✗ Detection logic: Always returns contaminated (no signal discrimination)

**Mock Data Fixes:** 2 attempts completed, both successful at fixing data loading but missed detection logic issues.

---

## Routing Decision

**Reflection Outcome:** ROUTED_TO_PHASE_0

**Reasoning:**
- MUST_WORK gate with FAIL result
- Fundamental flaw: detector cannot distinguish clean from contaminated data
- Not a tuning problem - core detection mechanism is broken
- Requires reconceptualization of detection approach

**Dependent Hypotheses Impact:**
- h-m1 (Tier 1 mechanism): CASCADE_FAILED
- h-m2 (Tier 2 mechanism): CASCADE_FAILED
- h-m3 (Tier 3 mechanism): CASCADE_FAILED

**Next Action:** Execute `/phase0-brainstorm` to develop new research question addressing contamination detection with validated detection mechanisms.

---

## Serena Memory Record

**Memory File:** `failure_h-e1_run3.md`
**Type:** Phase 4 Failure Record
**Content:** Full failure analysis, root causes, lessons learned, and routing decision

---

*Reflection completed at: 2026-05-11T03:17:28*
*Next step: Step 07 (Report Generation)*
