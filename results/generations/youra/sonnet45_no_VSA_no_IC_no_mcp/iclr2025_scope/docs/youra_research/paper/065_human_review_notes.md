# Phase 6.5 Human Review Notes
**Generated:** 2026-08-25  
**Purpose:** Collect MINOR issues for human review (typos, style, grammar)

---

## MINOR Issues (Not Auto-Fixed)

### 1. Abstract Density
**Location:** `00_abstract.md`  
**Issue:** 183 words, 14 sentences — acceptable but dense.  
**Recommendation:** Consider breaking into 2 paragraphs (hook+context | results+impact).  
**Status:** OPTIONAL — current version passes readability test.

---

### 2. Redundant Hook in Introduction
**Location:** `01_introduction.md`, paragraph 1  
**Issue:** "Researchers spend 2-4 weeks..." repeated verbatim from abstract.  
**Recommendation:** Rephrase for variety OR keep for emphasis (acceptable).  
**Status:** OPTIONAL — repetition serves rhetorical emphasis.

---

### 3. Novelty Claim Unchallenged
**Location:** `01_introduction.md`, contribution 1  
**Issue:** "First demonstration of temporal persistence" — strong claim, no prior work cited for contrast.  
**Recommendation:** Add sentence: "While prior work [X, Y] describes benchmark usage patterns retrospectively, no work predicts future suitability via historical train/test split."  
**Status:** LOW PRIORITY — acceptable if claim is factually true.

---

### 4. Pilot Sample Acknowledgment
**Location:** `00_abstract.md`, `06_discussion.md`  
**Issue:** "20 benchmarks" acknowledged as "pilot study" — honest limitation.  
**Recommendation:** None (already handled correctly).  
**Status:** RESOLVED — no action needed.

---

## Auto-Fixed Issues (R1 Revision)

### Fixed: 585% Calculation Error (FATAL)
**Location:** `00_abstract.md`, `01_introduction.md`, `05_results.md`, `07_conclusion.md`  
**Change:** "585%" → "298%" (correct relative improvement: (78.07-19.61)/19.61 = 2.98 = 298%)  
**Status:** ✅ FIXED in R1

---

### Fixed: Random Baseline Definition (MAJOR)
**Location:** `03_methodology.md`  
**Change:** Added explicit definition — "permute family assignments 1000 times, compute average overlap (null hypothesis)".  
**Status:** ✅ FIXED in R1

---

### Fixed: H-E1 Caveat Visibility (MAJOR)
**Location:** `05_results.md`  
**Change:** Added "Synthetic only" row to table + moved caveat to Interpretation opening sentence.  
**Status:** ✅ FIXED in R1

---

### Fixed: "78% Automatable" Confusion (MAJOR)
**Location:** `00_abstract.md`, `01_introduction.md`, `07_conclusion.md`  
**Change:** Removed claim "78% of effort could be automated" (conflates automation percentage with prediction accuracy). Now states fact without percentage.  
**Status:** ✅ FIXED in R1

---

## Review Summary

**Total Issues Found:** 7  
- FATAL: 1 (585% calculation)  
- MAJOR: 3 (baseline definition, H-E1 caveat, 78% confusion)  
- MINOR: 3 (abstract density, redundant hook, novelty claim)

**Auto-Fixed:** 4 (all FATAL + MAJOR)  
**Human Review Required:** 3 (all MINOR, optional)

---

**Next Step:** Proceed to Convergence Check (Step 04).
