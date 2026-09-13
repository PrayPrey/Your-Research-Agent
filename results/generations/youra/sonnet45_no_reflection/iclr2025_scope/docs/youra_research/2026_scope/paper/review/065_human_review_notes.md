# Phase 6.5 Round 1 - Human Review Notes (MINOR Issues)

**Paper:** Computational Feasibility Validation: A Missing Checkpoint in Large-Model Research Workflows  
**Revision:** Round 1  
**Date:** 2026-05-12  
**Status:** Collected for human review - NOT fixed by automated revision

---

## Purpose

This document collects all MINOR issues (grammar, style, formatting, typos) identified in Round 1 adversarial review. Per Phase 6.5 protocol, the Revision Agent addresses only FATAL and MAJOR issues. MINOR issues require human judgment and should be fixed by human reviewer.

**Total MINOR Issues:** 6

---

## Category 1: Grammar and Style Issues

### H1: Grammar/Awkward Phrasing

**Location:** Conclusion, final line (line 712 in original)

**Original:** "Measure twice, cut once—especially when cutting costs weeks of work."

**Issue:** Grammatically awkward. "Cutting costs weeks" is confusing construction.

**Suggested Fix:** "Measure twice, cut once—especially when the work costs weeks of effort."

**Alternative:** "Measure twice, cut once—especially when a mistake costs weeks of work."

**Severity:** Low - Meaning is clear but phrasing could be smoother

---

### H2: Missing Specificity - Conference Years

**Location:** Related Work, line 73-75 (original)

**Original:** "The ML community has growing recognition of negative results' value. NeurIPS and ICML introduced negative results tracks."

**Issue:** "Introduced" needs temporal context - when did this happen? Recent? Years ago?

**Suggested Fix:** 
- Option 1: "NeurIPS and ICML have recently introduced negative results tracks" (if recent)
- Option 2: "NeurIPS (2019) and ICML (2020) introduced negative results tracks" (if specific years known)
- Option 3: "In recent years, NeurIPS and ICML introduced negative results tracks"

**Severity:** Low - Not critical but adds precision

---

## Category 2: Formatting and Structure Issues

### H3: Section Numbering Mismatch

**Location:** Introduction, line 44 (original)

**Original:** "Section 7 concludes with a vision for feasibility-aware research pipelines."

**Issue:** Paper only has 6 main sections (Introduction, Related Work, Methodology, Experimental Setup, Results, Discussion, Conclusion). There is no "Section 7."

**Fix Required:** Change "Section 7" → "Section 6" or adjust section numbering

**Severity:** Medium - Factual error but doesn't affect content

**Note:** This may have been correct in original draft but became incorrect after section reorganization.

---

### H4: Text-Based Figures Should Be Actual Figures

**Location:** Results section, lines 447-466 (Figure 1), 482-544 (Figure 2)

**Original:** ASCII-art style text diagrams labeled as "Figure 1" and "Figure 2"

**Issue:** These are placeholder-style text representations, not publication-quality figures. Makes paper feel incomplete or draft-stage.

**Suggested Fix:**
- Option 1: Generate actual visual figures (bar charts, flowcharts) for publication
- Option 2: Rename as "Box 1" / "Box 2" or "Example 1" / "Example 2" to set expectations correctly
- Option 3: Keep as-is if journal accepts text-based figures (verify submission guidelines)

**Severity:** Medium - Affects polish and professionalism

**Context:** For ICML submission, visual figures are typically expected. Text representations are acceptable in preprints or technical reports.

---

## Category 3: Terminology and Consistency

### H5: MoE Acronym Not Introduced

**Location:** Multiple locations, first use at line 221

**Original:** "Model: Mixtral-8x7B-v0.1 (47 billion parameters, native 8-expert MoE architecture)"

**Issue:** "MoE" acronym used without definition. First appearance should spell out "Mixture-of-Experts (MoE)" before using acronym.

**Fix Required:** 
- Find first use of "MoE" (likely in Experimental Setup or Introduction)
- Change to: "Mixture-of-Experts (MoE)" on first use
- Then use "MoE" consistently afterward

**Severity:** Low - Most ML readers know MoE, but proper style requires definition

**Note:** Also applies to any other acronyms (LoRA should be defined: "Low-Rank Adaptation (LoRA)")

---

### H6: Inconsistent Terminology - "Test Files" vs "Test Suites"

**Location:** Multiple locations

**Original:** 
- Abstract/Results Table: "10 test files"
- Experimental Setup line 238: "10 test suites"

**Issue:** Are these 10 files containing 1 suite each, or 10 files containing multiple suites? Terminology inconsistency creates ambiguity.

**Suggested Fix:**
- If each file is one suite: Use "10 test suites (10 files)" consistently
- If files contain multiple suites: Clarify "10 test files containing X test suites"
- Recommend: Use "10 test files" consistently for simplicity

**Severity:** Low - Doesn't affect core argument but improves precision

---

## Category 4: Citation Issues (Lower Priority)

### H7: Citation Verification Status

**Location:** Throughout paper, all 14 citations

**Issue:** Ground truth notes indicate "citations_verified: 0" - citations have not been verified for accuracy

**Required Actions:**
1. Verify all author names, years, and titles in references.bib match actual publications
2. Verify citation format matches ICML style guidelines
3. Ensure all cited works exist and are correctly attributed

**Citations to Verify:**
- Dettmers et al. 2022, 2023 (quantization)
- Chen et al. 2016 (gradient checkpointing)
- Rasley et al. 2020 (DeepSpeed)
- Shoeybi et al. 2019 (Megatron-LM)
- Zhao et al. 2023 (FSDP)
- Moritz et al. 2018 (Ray)
- Kwon et al. 2023 (vLLM)
- Zaharia et al. 2018 (MLflow)
- Biewald 2020 (Weights & Biases)
- Dmitry et al. 2020 (DVC)
- Lipton & Steinhardt 2018 (negative results)
- Bender et al. 2021 (unexpected findings)
- Pineau et al. 2021 (reproducibility)

**Severity:** Medium - Critical for publication but doesn't affect revision logic

**Note:** Some citations may need specific sources for NeurIPS/ICML negative results tracks (H2 above)

---

## Summary for Human Reviewer

**Total MINOR Issues:** 6

**Priority Order:**
1. **High Priority:**
   - H3: Fix section numbering (Section 7 → 6) - factual error
   - H7: Verify all citations - required for publication

2. **Medium Priority:**
   - H4: Convert text figures to visuals or rename as boxes - affects professionalism
   - H5: Define MoE acronym on first use - style requirement

3. **Low Priority:**
   - H1: Improve final sentence grammar - stylistic
   - H2: Add temporal context to NeurIPS/ICML mention - adds precision
   - H6: Standardize "test files" vs "test suites" - consistency

**Estimated Time:** 30-45 minutes for human reviewer to address all issues

**Recommendation:** Address H3 and H7 before submission. H1, H2, H4, H5, H6 can be deferred to final polish pass.

---

## Issues NOT Included (Correctly Handled)

The following were raised in review but are NOT minor polish issues - they were correctly addressed in revision:

- Title being "boring" - This is subjective and structural; title conveys content accurately
- Introduction front-loading negativity - Restructured in revision (MAJOR fix)
- Related Work being mechanical - Language improved in revision (MAJOR fix)
- Abstract being too dense - Revised for clarity (MAJOR fix)

---

**Document Status:** ✅ COMPLETE  
**Next Action:** Human reviewer addresses minor issues before Round 2 or publication  
**Note:** All FATAL (1) and MAJOR (14) issues already fixed in revision

---

# Round 2 Additional Human Review Notes

**Review Round:** 2  
**Date:** 2026-05-12  
**Status:** CONDITIONAL_ACCEPT - Publication ready

---

## R2 Fixes Applied

### 1. Activation Memory Range (FIXED in R2)
- **Issue:** 75GB appeared without explaining source
- **Fix:** Added explanation throughout that it's midpoint of 50-100GB range
- **Status:** ✅ No longer needs human attention

### 2. Framework Overhead Percentage (FIXED in R2)
- **Issue:** Formula said "10-15%" but used 10% without explanation
- **Fix:** Clarified 10% is conservative choice within range
- **Status:** ✅ No longer needs human attention

---

## R1 Fixes Verification

All 15 R1 fixes remain intact:
- ✅ Memory consistency (489GB throughout)
- ✅ Tone calibration (conditional language)
- ✅ Scope narrowing (automated pipelines)
- ✅ Limitations upfront (Introduction paragraph)
- ✅ Cost-benefit assumptions stated
- ✅ Informal practices acknowledged
- ✅ SDD compliance distinction clear
- ✅ 85% threshold marked as proposed
- ✅ Solution effectiveness qualified
- ✅ Mixtral choice justified
- ✅ Underestimate percentage clarified
- ✅ All other major issues addressed

---

## Final Polish Items (Optional)

### Very Minor Items from R1 Still Applicable

1. **Line numbering:** Paper uses "line X" references that may need updating for final submission format

2. **MoE acronym:** First use in abstract ("LoRA-MoE") but formally introduced later - consider defining at first use if venue requires

3. **Number formatting:** Generally consistent, minor polish for submission:
   - "~8,200 LOC" could be "~8200 LOC" (no comma, US format consistency)

4. **Citation verification:** Not done in automated review - human should verify all citations exist and are formatted correctly

5. **Figure placeholders:** Paper uses text-based figures - venue may require actual figure files

---

## Publication Readiness Assessment

**Content Quality:** ✅ READY
- All substantive issues addressed (1 fatal + 14 major in R1, 2 minor in R2)
- Properly scoped claims matching evidence strength
- Comprehensive limitations acknowledged
- Appropriate tone for single-case meta-contribution

**Technical Accuracy:** ✅ VERIFIED
- All numerical calculations consistent and correct
- Memory estimates match ground truth
- Cost-benefit arithmetic accurate with assumptions stated

**Scientific Rigor:** ✅ APPROPRIATE
- Conditional language matches n=1 evidence
- Limitations stated upfront and in detail
- No overclaiming or false novelty
- Contribution clearly positioned as process improvement proposal

**Formatting:** ⚠️ NEEDS VENUE-SPECIFIC POLISH
- Core content ready
- May need venue-specific formatting (ICML template, figure files, etc.)
- Citation formatting to verify
- Minor grammar polish if desired

---

## Recommendation for Human Reviewer

**Action:** APPROVE FOR SUBMISSION after venue-specific formatting

**Priority Items:**
1. Apply ICML LaTeX template
2. Verify all citations
3. Convert text figures to proper figure files if required
4. Final grammar/style pass (optional)

**No Substantive Content Changes Needed** - All scientific/technical issues resolved

---

**Review Complete:** 2026-05-12  
**Rounds Completed:** 2 (R1: 15 issues fixed, R2: 2 issues fixed, all R1 fixes preserved)  
**Final Status:** Publication-ready with minor formatting polish
