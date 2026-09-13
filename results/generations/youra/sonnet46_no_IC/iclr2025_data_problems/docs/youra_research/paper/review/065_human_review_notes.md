# Human Review Notes — Round 1

**Paper:** One Size Does Not Fit All: Scale-Dependent Optimal Perplexity Filtering  
**Date:** 2026-08-04  
**For:** Next human reviewer or R2 adversarial agent

These issues were NOT auto-fixed. They require human judgment or access to primary data.

---

## MINOR-1: Test count attribution (§A.2)

**Location:** Appendix A.2  
**Issue:** "23/23 pytest tests pass (h-e1 pipeline)" — the 23/23 count is attributed to the h-e1 pipeline, but the sentence then says "h-e1-v2 pipeline validated end-to-end." If h-e1-v2 has its own pytest suite with a different count, the paper should report that count separately.  
**Action needed:** Verify whether h-e1-v2 has its own pytest count. If so, report it separately. If h-e1-v2 reuses the h-e1 tests, clarify that the 23/23 applies to the shared test suite.

---

## MINOR-2: Na et al. Spearman r=0.81 citation accuracy

**Location:** Section 2.3  
**Issue:** The paper states Na et al. [2024] report "Spearman r=0.81 correlation between proxy-model performance and full-scale benchmark outcomes." This number is used as a foil to motivate why proxy models were expected to work (and then shown insufficient). The exact r=0.81 value should be verified against the actual Na et al. paper before submission.  
**Action needed:** Verify r=0.81 from Na et al. (2024) EMNLP paper. If incorrect, update the value.

---

## MINOR-3: Gao et al. (2021) reference status

**Location:** References  
**Issue:** The original paper flagged this citation as "[UNVERIFIED in Scholar]" — this annotation was removed in R1 (submission risk). However, the underlying verification status is still unknown. The lm-evaluation-harness citation by Gao et al. is widely used in the field; the correct citation should be verified (the primary reference may now be a 2024 paper or a different venue than "EleutherAI").  
**Action needed:** Verify Gao et al. (2021) lm-evaluation-harness correct citation format and venue before final submission.

---

## MINOR-4: Standard deviation values in Table 1

**Location:** Section 5.1, Table 1  
**Issue:** All 12 entries show identical "±0.001" standard deviation across all conditions and both scales. With n=2 seeds, standard deviations should in principle vary across conditions. The uniform ±0.001 may be a rounded estimate rather than computed values.  
**Action needed:** Verify whether ±0.001 was computed from the 2-seed runs or is a uniform estimate. If computed, confirm the values are correctly rounded. If estimated, note this in the table caption (e.g., "std estimated at ±0.001 from 2 seeds").

---

## MINOR-5: τ=35 retention count approximation

**Location:** Section 3.2, Appendix A.1  
**Issue:** τ=20 and τ=50 use exact counts (176 and 2,074), while τ=35 uses "approximately 800" (~16%). The asymmetry between exact and approximate values within the same table may invite reviewer questions.  
**Action needed:** If the exact count for τ=35 is available from curate.py outputs or results.csv, replace "~800" with the exact number. If not available, consider adding a note that the τ=35 count was not separately logged.

---

## MINOR-6: Section 4.1 condition count notation

**Location:** Section 4.1  
**Issue:** "Each condition run for 2 model scales × 2 seeds = 24 total runs" is slightly imprecise — the math is 6 conditions × 2 scales × 2 seeds = 24. Section 3.1 correctly states 3 PPL × 2 dedup × 2 scales × 2 seeds = 24. The notation shift (6 conditions vs. 3×2) is not wrong but may be mildly confusing.  
**Action needed:** Consider changing to "Each of the 6 conditions × 2 model scales × 2 seeds = 24 total runs" for consistency.

---

## MINOR-7: Abstract "24 experimental conditions" vs "24 runs"

**Location:** Abstract  
**Issue:** Abstract says "consistent across all 24 experimental runs" (fixed from "conditions" in R1). Verify this is the right term — the paper has 6 *conditions* and 24 *runs* (each condition × 2 scales × 2 seeds). The Abstract now correctly says "runs."  
**Status:** Already fixed in R1 (changed from "conditions" to "runs"). Flagged here for completeness.

---

---

# Human Review Notes — Round 2 Additions

**Added:** 2026-08-04 | Source: R2 adversarial review (065_review_r2.md)

---

## MINOR-R2-002: Table 1 uniform ±0.001 std may reflect rounding

**Location:** Section 5.1, Table 1  
**Issue:** All 12 entries show identical ±0.001 standard deviation. R2 reviewer notes this is consistent with rounding (with n=2 seeds, each per-condition std is a single value: |seed1 − seed2| / √2). The uniform value is plausible but may invite reviewer questions.  
**Action needed:** Same as MINOR-4 from R1 notes — verify whether ±0.001 was computed or estimated. Consider adding "std rounded to ±0.001 across all conditions" to table caption if values were rounded.

---

## MINOR-R2-003: Footnote ¹ for parameter counts placed after first use of ratio

**Location:** §1 (Introduction) and §3.1 (footnote definition)  
**Issue:** The phrase "2.2× scale difference" appears in §1 (first paragraph) before footnote ¹ is defined in §3.1. A reader parsing linearly sees the ratio before the actual-count clarification. The footnote correctly documents the 7.9M/18.1M actual counts and 2.29× actual ratio.  
**Action needed:** Consider moving footnote ¹ to first occurrence of "14M" or "2.2×" in §1 rather than §3.1, so the clarification arrives at the reader's first encounter with the nominal values.

---

## MINOR-R2-004: "12×" ratio arithmetic check (no issue)

**Location:** §1 (Introduction), §5.3  
**Note:** Paper states practitioners training at τ=50 use "12× more data than optimal." Arithmetic: 2,074/176 = 11.77× ≈ 12×. This rounding is correct and standard. No fix needed; documented here for completeness in case a reviewer asks.

---

## MINOR-R2-005: 31M τ=35 condition values vs. 04_validation average

**Location:** Table 1 (C3, C4 for 31M)  
**Issue:** Table 1 reports 31M C3=0.2535, C4=0.2538 (average 0.2537). The 04_validation.md τ=35 average for 31M = 0.2529. Gap = 0.0008 — within the ±0.001 reported std but slightly inconsistent with the independent validation summary. Likely due to averaging order (per-J then per-seed vs. flat average across all J and seeds).  
**Action needed:** If raw results.csv is accessible, recompute the 31M τ=35 per-condition means to confirm. The discrepancy does not affect any primary claim (τ*(31M)=50 is unambiguous), but a thorough reviewer may probe it.

---

## MINOR-8: "23/23 pytest tests" in limitations section (L1, §6.2)

**Location:** Section 6.2, L1  
**Issue:** The limitations section uses "23/23 pytest tests passing" as evidence that "the full pipeline is implemented and validated, requiring only compute to run at 70M/160M × 50B tokens." A skeptical reviewer may note that pipeline tests passing does not guarantee the 70M/160M experiment will succeed (different infrastructure, memory requirements, etc.).  
**Action needed:** This is low priority — the qualification is already a limitation discussion, so some hedging is expected. Consider adding "assuming hardware scaling" or similar qualifier if desired.
