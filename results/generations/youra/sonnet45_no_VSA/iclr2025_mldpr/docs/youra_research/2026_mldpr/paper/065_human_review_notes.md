# Human Review Notes - MINOR Issues for Manual Correction

**Generated:** 2026-07-12  
**Phase:** 6.5 Adversarial Review Round 1  
**Purpose:** Collect non-critical issues flagged by adversary but not auto-fixed

---

## MINOR Issues (Not Auto-Fixed)

### M1: Typographical Consistency
**Location:** Abstract line 3, multiple sections  
**Issue:** DCS\_3 has escaped underscore (DCS\_3) in some places, inconsistent formatting  
**Fix:** Human editor should search-replace with consistent notation (recommend DCS₃ with subscript or DCS_3 without escape)  
**Severity:** MINOR (cosmetic)

### M2: Engagement - Related Work Dryness
**Location:** Section 2 (Related Work)  
**Issue:** Related Work reads as catalog of papers without narrative thread  
**Fix:** Add 1-2 sentence transitions between subsections explaining why each paper matters to our story  
**Example:** After Documentation Framework Design subsection, add: "These frameworks establish *what* to document, but adoption rates remain unmeasured—motivating our empirical focus."  
**Severity:** MINOR (readability)

### M3: Inter-Rater Reliability Explanation
**Location:** Methodology, Experiments sections  
**Issue:** κ = 1.00 (perfect agreement) is suspiciously perfect. Skeptical reviewer will question independence  
**Fix:** Add brief explanation: "The perfect agreement (κ = 1.00) reflects the binary simplicity of the 3-component rubric at the ≥0.5 threshold level, not a failure of independence. The dual-coded sample (N=20) included both edge cases and clear-cut examples."  
**Severity:** MINOR (transparency)

### M4: Citation Count Verification
**Location:** Introduction line 1, Abstract  
**Issue:** Citation counts (3,142 for Gebru, 2,899 for Mitchell) should be verified as of submission date  
**Fix:** Before final submission, verify citation counts from Google Scholar as of 2026-07  
**Severity:** MINOR (accuracy)

### M5: Figure Placement Consistency
**Location:** Results section  
**Issue:** Figure captions use placeholder text "\[Figure placement here\]"  
**Fix:** Replace with actual figure references once figures are finalized  
**Severity:** MINOR (formatting)

---

## Recommendations for Human Editor

1. **Abstract Length:** Consider trimming abstract to 150 words (currently ~180 after revision). Focus on: (1) hook (7% vs 3,142 cites), (2) method (T0+90 temporal), (3) finding (ρ = 0.951), (4) implication (workflow integration).

2. **Notation Consistency:** Choose one notation for DCS_3 and apply globally. Recommend "DCS₃" with subscript for readability.

3. **Synthetic Data Disclosure:** Verify synthetic data caveat is visible in Abstract (✅ added in revision), Introduction (✅ added), Methodology (✅ already present), and Discussion L1 (✅ already present). Do NOT hide in appendix.

4. **"First" Claim Verification:** Introduction claims "first temporal precedence validation." Before publication, conduct citation search to confirm no prior work measured documentation at T0+90 days. If found, revise to "Among the first to measure..." or remove claim.

5. **Baseline Comparison Gap:** Skeptical reviewer noted lack of baseline. Consider adding 1-2 sentences in Discussion acknowledging this: "A limitation is the absence of baseline comparison: we cannot distinguish whether 7% compliance is specific to repositories *claiming* to use Datasheets vs. field-wide. Multi-tier sampling (framework-adopters vs. non-adopters) would isolate framework-specific effects."

---

## Next Steps

- [ ] Human editor reviews and applies fixes  
- [ ] Verify citation counts before submission  
- [ ] Replace figure placeholders with actual references  
- [ ] Conduct "first temporal precedence validation" citation search  
- [ ] Final proofread for notation consistency

---

**Status:** MINOR issues documented for manual review. FATAL and MAJOR issues addressed in Round 1 revision.
