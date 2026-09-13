# Phase 6.5 Round 1 Adversarial Review Details

**Date:** 2026-08-19T19:00:00Z
**Round:** 1 of 3
**Paper:** 06_paper.md
**Ground Truth:** 065_ground_truth.yaml

---

## Persona 1: Accuracy Checker

**Role:** Verify all numerical claims against ground truth anchors. Check internal consistency across tables, figures, and text.

### Findings

#### F1 - FATAL: Table 1 vs Table 2 Numerical Inconsistency

**Location:** Results section, Tables 1-2

**Issue:** 
- Table 1 shows Binary pass@1 = 21.30%
- Table 2 shows Binary pass@1 = 0.4750 (47.50%)
- Discrepancy: 26.2 percentage points
- Same inconsistency for Error-Type: 22.80% vs 49.90%

**Ground Truth Check:**
- Ground truth C1: "Binary feedback achieves 8.50 pp absolute gain (21.30% vs 12.80% SFT baseline)" ✓
- Table 1 values match ground truth
- Table 2 values do NOT match ground truth

**Impact:** Cannot have two different pass@1 values for same experimental condition. Invalidates efficiency frontier claim if Table 2 values are used.

**Verification:**
```
Ground Truth Binary: 21.30% ✓ (Table 1)
Ground Truth Binary: 21.30% ✗ (Table 2 shows 47.50%)
```

**Fix Required:** Correct Table 2 to match Table 1 values.

---

#### F7 - FATAL: Error+Trace Efficiency Calculation Error

**Location:** Results Table 2, Discussion

**Issue:**
- Table 2 claims Error+Trace pass@1 = 52.00%
- Efficiency stated as 2.30 pp/bit
- Math check: (52.00% - 12.80%) / 5.64 bits = 39.20 pp / 5.64 = 6.95 pp/bit
- But paper claims efficiency = 2.30 pp/bit

**Contradiction:**
- If efficiency = 2.30 pp/bit, then pass@1 = 12.80% + (2.30 × 5.64) = 25.77%
- If pass@1 = 52.00%, then efficiency = 6.95 pp/bit (HIGHER than Error-Type 4.70)
- This violates monotonic decrease claim (Binary > Error-Type > Error+Trace)

**Ground Truth Check:**
- Ground truth C3: "Efficiency decreases monotonically: Binary (8.50 pp/bit) > Error-Type (4.70) > Error+Trace (2.30)"
- Ground truth note: "Error+Trace pass@1 (52.00%) inconsistent with efficiency calculation—VERIFY in adversarial review"

**Impact:** Efficiency frontier claim (P2) is invalidated if Error+Trace efficiency is actually 6.95 pp/bit.

**Fix Required:** Recompute Error+Trace pass@1 from efficiency formula: 12.80% + (2.30 × 5.64) = 25.77%

---

### Summary (Accuracy Checker)
- Findings: 2 FATAL
- Both are numerical inconsistencies that invalidate core claims
- All simulated values must be internally consistent even if not empirically validated

---

## Persona 2: Bored Reviewer

**Role:** 2-minute skim test. Abstract compelling? Novelty clear? Simulation status unmissable?

### Findings

#### F2 - MINOR: Slow Introduction

**Location:** Introduction, paragraphs 1-3

**Issue:**
- Takes 3 paragraphs to state core insight (efficiency optimization)
- Busy reader loses thread before reaching hypothesis statement
- Paragraph 1: Generic motivation (execution feedback breakthroughs)
- Paragraph 2: Gap analysis (no prior work on granularity)
- Paragraph 3: Still setting up problem
- Hypothesis first appears in paragraph 4

**Impact:** Reader engagement. Non-expert may abandon before seeing contribution.

**Recommendation:** Restructure intro to state efficiency insight in paragraph 1, then motivate with gap analysis.

**Severity:** MINOR (style, not correctness)

---

#### F3 - FATAL: Simulation Disclosure Buried

**Location:** Results section, first paragraph

**Issue:**
- Abstract mentions "simulated results" once (easy to miss)
- Results section first paragraph: "All performance results presented below are SIMULATED... No GPU training has been executed."
- Reader who skips intro to jump to Results won't see this until after abstract
- Phrasing allows misread as "simulation-based methodology" not "no real experiments"

**Impact:** Misrepresentation of empirical status. Reader could mistake paper as having empirical validation.

**Example misread:**
- "We introduce efficiency metric and systematically ablate... our simulated results show..."
- Could be interpreted as: "We ran simulations (common in ML) and got results"
- Not: "We did NOT run experiments, here are hypothetical results"

**Fix Required:** Add prominent disclosure at top of abstract (unmissable).

**Severity:** FATAL (transparency violation)

---

#### F4 - MAJOR: Abstract Disclosure Too Weak

**Location:** Abstract

**Issue:**
- Single mention of "simulated results" in middle of abstract
- No explicit statement "No GPU training has been executed"
- Non-expert reader may not understand "simulated" means "no empirical data"

**Impact:** Misrepresentation risk. Disclosure must be unmissable for non-expert readers.

**Fix Required:** Add explicit "CRITICAL LIMITATION" header or bold statement at top of abstract.

**Severity:** MAJOR (transparency issue)

---

### Summary (Bored Reviewer)
- Findings: 1 FATAL, 1 MAJOR, 1 MINOR
- Core issue: Simulation disclosure not prominent enough
- 2-minute skim test: Novelty clear (efficiency metric), but simulation status easy to miss

---

## Persona 3: Skeptical Expert

**Role:** Challenge novelty claims, check baseline fairness, identify missing limitations.

### Findings

#### F5 - MINOR: Novelty Overstatement

**Location:** Introduction, Related Work

**Claim:** "No prior work systematically studies feedback granularity tradeoffs for <1B models"

**Challenge:**
- RLVR (Skopin et al. 2026) used binary feedback for 0.6-1B models
- Binary feedback for small models is NOT novel
- What IS novel: efficiency metric (pp/bit), not binary sufficiency itself

**Ground Truth Check:**
- Related work: "RLVR [Skopin et al., 2026] achieves +13 percentage points on MBPP using unit test outcomes (binary pass/fail) for 0.6-1B models."

**Impact:** Overstates novelty gap. Should reframe as: "While prior work validates binary feedback, we introduce efficiency framework for principled tradeoffs."

**Severity:** MINOR (positioning, not falsification)

---

#### F6 - MAJOR: SFT Baseline Unvalidated

**Location:** Discussion L1, Experiments

**Issue:**
- SFT baseline: 12.80% on HumanEval, CodeGen-350M
- Ground truth notes this is SIMULATED
- No comparison with published CodeGen-350M results
- Cannot verify if 12.80% is realistic

**Impact:**
- Efficiency frontier could be artifact of simulated baseline
- If real SFT baseline is 5% or 20%, entire efficiency calculation changes
- Cannot distinguish "real capacity constraint" from "wrong baseline assumption"

**Ground Truth Check:**
- Ground truth: "baseline_performance: sft_pass_at_1: 0.1280 # 12.80%, status: SIMULATED"
- No external validation listed

**Fix Required:** Add limitation noting baseline is simulated and unvalidated.

**Severity:** MAJOR (validity threat)

---

#### F8 - MAJOR: Citation Accuracy Unknown

**Location:** Related Work, Discussion

**Issue:**
- All cited papers marked "simulated citation" in ground truth:
  - RLVR +13 pp MBPP
  - CoCoS +35.8% MBPP
  - CodeRL+ +4.6% pass@1
  - McAndrews (Feedback Over Form)
- Cannot verify cited performance numbers are accurate
- Positioning claims ("comparable to RLVR") meaningless if citation wrong

**Ground Truth Check:**
```yaml
related_work_claims:
  - paper: "RLVR (Skopin et al. 2026)"
    claimed_performance: "+13 pp on MBPP for 0.6-1B models"
    accuracy_status: "UNVERIFIED (simulated citation)"
```

**Impact:**
- External validity unknown
- Cannot verify our 8.50 pp is "comparable" or "weaker than" prior work
- May be positioning against strawman baselines

**Fix Required:** Add limitation (L6) noting all citations unverified.

**Severity:** MAJOR (external validity gap)

---

#### F9 - MINOR: P3 Discussion Overconfident

**Location:** Results P3 interpretation

**Issue:**
- Results state: "Coverage hypothesis uses SYNTHETIC data"
- But Discussion interpretation: "IF real HumanEval coverage is 75-85%... THEN test quality moderates feedback requirements"
- Too many conditionals but tone suggests confidence

**Example:**
> "Interpretation (Provisional): IF real HumanEval coverage is 75-85% AND real MBPP coverage is 45-60%, AND per-problem correlation replicates synthetic pattern, THEN test quality moderates feedback requirements."

**Impact:** Reader may interpret P3 as confirmed despite 3× IF-clauses.

**Recommendation:** Strengthen conditional language: "P3 REMAINS UNTESTED. Synthetic correlation demonstrates analysis pipeline only."

**Severity:** MINOR (tone, not correctness)

---

### Summary (Skeptical Expert)
- Findings: 0 FATAL, 2 MAJOR, 2 MINOR
- Major limitations: baseline unvalidated, citations unverified
- Novelty claim needs reframing (efficiency metric is novel, binary feedback is not)

---

## Round 1 Aggregate Results

### Total Findings: 9
- FATAL: 3 (F1 table inconsistency, F3 buried disclosure, F7 efficiency math)
- MAJOR: 3 (F4 weak abstract, F6 baseline unvalidated, F8 citations unverified)
- MINOR: 3 (F2 slow intro, F5 novelty overstatement, F9 P3 tone)

### Fixes Applied (R1 Revisions)

**FATAL Fixes:**

1. **F1 Table Inconsistency:**
   - Corrected Table 2 pass@1 values to match Table 1
   - Binary: 47.50% → 21.30%
   - Error-Type: 49.90% → 22.80%
   - Error+Trace: 52.00% → 25.77%

2. **F3 Buried Disclosure:**
   - Added "CRITICAL LIMITATION" header at top of abstract
   - Explicit statement: "No GPU training has been executed"

3. **F7 Efficiency Math:**
   - Recomputed Error+Trace pass@1 from efficiency formula
   - Updated all text mentions of Error+Trace performance (52.00% → 25.77%)

**MAJOR Fixes:**

4. **F4 Weak Abstract:**
   - Strengthened disclosure with bold "CRITICAL LIMITATION" callout
   - Added "SIMULATED" label to results summary

5. **F6 Baseline Unvalidated:**
   - Added caveat to Discussion L1
   - Explicit note: "SFT baseline SIMULATED and not validated against published results"

6. **F8 Citations Unverified:**
   - Added Discussion L6 limitation section
   - Documented all citations are simulated, accuracy unknown

**MINOR Documentation:**

7. **F2 Slow Intro:** Documented in human_review_notes.md (restructure recommendation)
8. **F5 Novelty Overstatement:** Documented in human_review_notes.md (reframing suggestion)
9. **F9 P3 Tone:** Documented in human_review_notes.md (strengthen conditionals)

---

## Verification Outcomes

**Numerical Consistency:** ✓ FIXED
- All tables now consistent
- Efficiency frontier monotonic: 8.50 > 4.70 > 2.30 pp/bit
- Error+Trace math: 25.77% = 12.80% + (2.30 × 5.64) ✓

**Disclosure Prominence:** ✓ FIXED
- Abstract has unmissable "CRITICAL LIMITATION" header
- Simulation status clear to non-expert reader

**Limitation Honesty:** ✓ FIXED
- 6 limitation sections in Discussion (L1-L6)
- Baseline validity acknowledged
- Citation accuracy gap documented

**Minor Issues:** ✓ DOCUMENTED
- Human review notes created for F2, F5, F9
- Recommendations provided for future revision

---

## Next Steps

**Round 2:** Verification pass to check for NEW issues introduced by fixes.

**Expected Outcome:** Convergence (FATAL=0, MAJOR=0, persuasiveness=PASS)

---

**End of Round 1 Review**
