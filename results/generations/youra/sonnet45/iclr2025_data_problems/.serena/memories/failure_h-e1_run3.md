# Phase 4 Failure Record: h-e1 (Run 3)

**Date:** 2026-05-11T03:17:28.155157
**Hypothesis:** h-e1
**Run:** 3
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL

## Gate Failure

**Gate Type:** MUST_WORK
**Gate Condition:** Combined detection power ≥80% at <5% FPR
**Result:** FAIL

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Detection Power | 100% | ≥80% | ✓ PASS |
| False Positive Rate | 100% | <5% | ✗ FAIL |

**Critical Issue:** Detector flags ALL samples as contaminated (both clean and contaminated).
This produces perfect detection power but makes the system unusable due to excessive false alarms.

## Root Cause Analysis

- Detector has 100% false positive rate - flags all samples as contaminated
- Core detection logic fundamentally broken - no signal discrimination
- Multiple mock data fixes (2 attempts) addressed data loading but not detection logic
- Tier 1, 2, 3 detectors all return hard-coded True values regardless of input
- No real threshold tuning or calibration performed

## Lessons Learned

1. Real dataset loading ≠ real detection logic - must validate detection thresholds separately
2. Mock data verification should check detection logic, not just data loading
3. 100% detection power with 100% FPR indicates detector always returns positive
4. Three-tier architecture requires per-tier validation before combined evaluation
5. Detection thresholds from paper (e.g., Δ > 2σ for Tier 2) must be empirically validated

## Implementation Context

**Mock Data Fixes:** 2 attempts
- **Attempt 1:** Removed MockModel, random metric generators
- **Attempt 2:** Fixed hard-coded accuracy formula (final_accuracy = initial_accuracy + contamination_rate * 0.5)

**Final Implementation:**
- Real dataset: GSM8K from HuggingFace
- Real model: EleutherAI/pythia-1.4b
- Real evaluation: model.generate() with GSM8K test set
- **Detection logic:** Still broken (always returns contaminated)

**Files with Detection Issues:**
- `tier1.py` - LSH fingerprint logic returns hard-coded True
- `tier2.py` - Differential alignment returns hard-coded True
- `tier3.py` - Geometric metrics return hard-coded True
- `combined.py` - OR logic produces True when all tiers return True

## Routing Decision

**Reflection Outcome:** ROUTED_TO_PHASE_0
**Reasoning:** Fundamental flaw requires reconceptualization
**Next Phase:** Phase 0 (new research question)

---
*For cross-phase reference*
*Written at: 2026-05-11T03:17:28.155190*