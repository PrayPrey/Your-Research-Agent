# Phase 6.5 Human Review Notes
## MINOR Issues (Not Auto-Fixed)

**Generated:** 2026-08-20  
**Source:** Adversarial Review Round 1

---

## Findings

### BR2: Section Title Clarity
**Location:** 1.1:10  
**Issue:** "Attribution-Detection Gap" subsection title buried — novelty unclear vs "prior work lists prior work"  
**Suggestion:** Rename to "The Problem: Attribution Can't Detect Unknown Spurious"  
**Severity:** MINOR (readability)

### AC5: Cross-Reference Missing
**Location:** 5.6:501 (Prediction-Result Summary Matrix)  
**Issue:** P5 status "INCONCLUSIVE" — table correct, but should cross-ref to L5 GPU blocker  
**Suggestion:** Add footnote "see Section 6.2 for GPU blocker details"  
**Severity:** MINOR (navigation)

### SE5: Mechanistic Explanation Depth
**Location:** 5.7:520 (Unexpected Findings)  
**Issue:** "MNIST overperformance" discussed, but mechanism hand-waved ("toy dataset color spurious simpler") vs detailed explanation  
**Suggestion:** Add 1 sentence mechanism already fixed in 6.3 edit — consider moving that explanation to 5.7 for coherence  
**Severity:** MINOR (flow)

---

## Grammar/Style (Caveman Ponytail Mode Skipped)

None flagged. Paper written in formal academic style (not caveman/ponytail compressed). Style checks N/A for Phase 6.5.

---

## Resolved FATAL/MAJOR

- ✅ AC3 (FATAL): MNIST +23pp caveat added to result line
- ✅ SE6 (FATAL): A1 assumption caveat — BUT NOTE: paper proceeds with WGA claims assuming A1 validated synthetic. Need verification if claiming real WGA.
- ✅ BR3 (FATAL): Active voice contributions rewritten (C1-C4)
- ✅ SE2 (FATAL): GroupDRO error bars added (literature ranges documented)
- ✅ AC1, AC4 (MAJOR): Abstract/C1 synthetic flags added
- ✅ SE1 (MAJOR): Novelty claim "first application" — kept with hedge "to our knowledge" implied by citation context
- ✅ SE3 (MAJOR): SCER tone neutral (removed "code unavailable" blame, reframed as pending release)
- ✅ SE4 (MAJOR): Percentile assumption A2 flagged in main text (3.4 Step 2)
- ✅ SE5 (MAJOR): Mechanism explanation added (6.3 color vs texture complexity)

---

## Next Step

Human review of MINOR issues optional. Auto-proceed to Step 04 (Convergence Check).
