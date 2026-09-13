# Human Review Notes (Phase 6.5)

These MINOR issues were collected for human review. NOT auto-fixed to preserve author discretion.

---

## Issue 1: MBPP Sample Count Clarification
**Section:** 3.5 (Methodology - Dataset) vs 4.1 (Experiments - Datasets)
**Type:** clarity
**Issue:** Section 3.5 states "591 unique problem-solution pairs" (164 HumanEval + 427 MBPP sanitized), but Table 4.1 states 421 samples (164 HumanEval + 257 MBPP sanitized test). Different MBPP subsets.
**Suggested Fix:** Clarify that 257 is the "sanitized test" subset used for experiments, vs 427 total sanitized problems. The 421 number is correct for the actual experiments.
**Severity:** MINOR

---

## Issue 2: "First Quantified" Claim Hedge
**Section:** Abstract, Introduction
**Type:** style
**Issue:** "first quantified correlation study" is strong language. While Table 1 shows no prior r-values in literature, a skeptic could argue qualitative correlation claims existed.
**Suggested Fix:** Add hedge: "to our knowledge, the first..." 
**Severity:** MINOR

---

## Summary
- Total MINOR issues: 2
- By type: clarity (1), style (1)
- Recommended action: Human author review before final submission
