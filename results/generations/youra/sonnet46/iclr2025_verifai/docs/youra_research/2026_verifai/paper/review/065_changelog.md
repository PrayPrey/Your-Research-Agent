# Phase 6.5 Adversarial Review Changelog

## Round 1 Revisions

**Date:** 2026-03-23
**Input:** 06_paper.md
**Output:** 06_paper_r1.md

### MAJOR-001: Abstract Hook Revised
- **Section:** Abstract
- **Issue:** First sentence used "LLMs are increasingly deployed..." (anti-pattern)
- **Fix:** Replaced with concrete question hook matching narrative blueprint design
- **Status:** RESOLVED

### MAJOR-002: Contribution 3 Mechanism Claim Reframed
- **Sections:** Introduction (Contribution 3), Conclusion (item 3)
- **Issue:** "Evidence for mechanism" overclaimed; Discussion hedges appropriately but Introduction/Conclusion did not
- **Fix:** Changed to "observations consistent with... hypothesis" with explicit "(exploratory, N=1 per category)" qualifier
- **Status:** RESOLVED

### MAJOR-003: Base Model P(True) Validity Added
- **Sections:** §3.2 (new "Base model applicability" paragraph), §6.4 (new L5 limitation)
- **Issue:** No explicit discussion of methodological validity for applying P(True) to base (non-instruction-tuned) models
- **Fix:** Added justification paragraph in §3.2 and new L5 limitation entry in §6.4
- **Status:** RESOLVED

### MINOR Issues (NOT auto-fixed — collected in 065_human_review_notes.md)
- Rounding inconsistency: text says ECE(hard)=0.657 vs table 0.6565 for DeepSeek
- §5.5 M-stability: "exactly stable" without explanation of why
- §5.3: "MBPP-only" → "MBPP+ only"
- Abstract: "practitioners typically assume" uncited

## Round 2 Revisions

**Date:** 2026-03-23
**Input:** 06_paper_r1.md
**Output:** 06_paper_r2.md
**Serena MCP Searches:** 7 (h-m4, h-m3, h-m2, h-e1 validation files)

### MAJOR-R2-001: Jaccard Table Values Corrected (§5.1.3)
- **Issue:** Llama3∩CodeLlama and CodeLlama∩DeepSeek Jaccard values were swapped
- **Before:** Llama3∩CodeLlama=0.456, CodeLlama∩DeepSeek=0.546
- **After:** Llama3∩CodeLlama=0.546, CodeLlama∩DeepSeek=0.456
- **Evidence:** Serena search of h-m2/04_validation.md confirms actual values
- **Impact on conclusions:** None — all values still exceed 0.30 threshold; range 0.456–0.546 unchanged
- **Status:** RESOLVED

### MAJOR-R2-002: Per-Benchmark Tier Sizes Corrected (§5.1.1 Table)
- **Issue:** Per-benchmark n_hard/n_easy values in Table 5.1.1 did not match h-e1 actual results
- **Evidence:** Serena search of h-e1/04_validation.md confirms actual values
- **Key corrections:** Llama3 HumanEval+ n_easy: 72→39; DeepSeek MBPP+ n_easy: 95→176; CodeLlama HumanEval+ n_hard: 186→142; etc.
- **Note:** Combined totals in main ΔECE Table 1 remain correct and unchanged
- **Status:** RESOLVED

### MINOR Issues (added to human_review_notes.md)
- Null baseline description clarification (§4.2)


## Final Summary (v2.0)

**Total Revisions Made:** 5 (3 in R1, 2 in R2)
**Sections Modified:** Abstract, Introduction, §3.2, §5.1.1, §5.1.3, §6.4, Conclusion
**Word Count Change:** ~6385 → ~6550 (estimated +165 words from L5 and §3.2 additions)

**Review Process:**
- Started: 2026-03-23T08:00:00Z
- Completed: 2026-03-23T09:00:00Z
- Rounds: 2 (R1: three-persona; R2: numerical verification with Serena MCP)
- Personas Used: accuracy_checker, bored_reviewer, skeptical_expert

**Files Generated:**
- 06_paper_r1.md (R1 revised paper — MAJOR-001/002/003 fixed)
- 06_paper_r2.md (R2 revised paper — MAJOR-R2-001/002 fixed)
- 06_paper_final.md (= 06_paper_r2.md, final)
- paper/review/065_review_r1.md
- paper/review/065_review_r2.md
- paper/review/065_review_summary.md
- paper/review/065_human_review_notes.md (6 MINOR issues)
- paper/review/065_changelog.md (this file)
- paper/review/065_review_checkpoint.yaml

**Final Status:** CONVERGED — CONDITIONAL_ACCEPT
**Next Phase:** Phase 6.5.1 (Overleaf LaTeX/PDF generation)
