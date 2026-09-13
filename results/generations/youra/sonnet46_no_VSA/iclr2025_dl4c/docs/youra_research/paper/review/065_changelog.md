# Adversarial Review Changelog
**Paper**: What Does Code SFT Actually Teach?  
**Started**: 2026-08-03  
**Pipeline**: Phase 6.5 Adversarial Review

---

## Round 1 Revisions (06_paper.md → 06_paper_r1.md)

### FATAL-001 Fix: Corrected HumanEval-only 1.3B mean (Introduction body)
- **Before**: "HumanEval-only training achieves 32.6% HumanEval+ pass@1 ... a 29.6 percentage point gap"
- **After**: "HumanEval-only training achieves 35.0% HumanEval+ pass@1 ... a ~32 percentage point gap"
- **Rationale**: h-e2/results/all_results.csv: seeds 39.6+25.6+39.6=mean 35.0%. 32.6% is not supported by any data source. Gap corrected to ~31.9pp (35.0−3.1).

### FATAL-002 Fix: Corrected HumanEval-only 1.3B mean in Contribution bullet 3 (Introduction)
- **Before**: "HumanEval-only training achieves the highest pass@1 on both HumanEval+ (35.9%)"
- **After**: "HumanEval-only training achieves the highest pass@1 on both HumanEval+ (35.0%)"
- **Rationale**: 35.9% appears in h-m1 transfer matrix but is an internal calculation error; h-e2 CSV is ground truth = 35.0%.

### FATAL-002 Side-effect: Updated all "29.6pp" gap references to "31.9pp"
- **Locations changed**: Abstract, Contribution 1, Table 1 narrative (Section 5.1), Conclusion
- **Before**: "29.6 percentage points"
- **After**: "31.9 percentage points" (35.0% − 3.1% = 31.9pp)
- **Note**: The original 29.6pp derived from the incorrect 32.6% base (32.6−3.0=29.6). Correct value is ~31.9pp using actual means.

### MAJOR-001 Fix: Corrected LeetCode per-seed values in Table 1
- **Before**: "~3.1% | ~3.1% | ~3.1%"
- **After**: "0.0% | 0.0% | 9.1%"
- **Rationale**: h-e2 CSV: seed_42=0.0, seed_123=0.0, seed_777=0.0915. Mean=3.05%≈3.1% was correct; per-seed were wrong.

### MAJOR-002 Fix: Corrected Equal-mix seed 42/123 swap in Table 1
- **Before**: "9.8% | 10.4% | 10.4%" (seed 42=9.8%, 123=10.4%)
- **After**: "10.4% | 9.8% | 10.4%" (seed 42=10.4%, 123=9.8%)
- **Rationale**: h-e2 CSV: seed_42=0.1037(10.4%), seed_123=0.0976(9.8%)

### MAJOR-003 Fix: Added LeetCode training convergence limitation
- **Section**: 6.4 Limitations
- **Added**: New paragraph acknowledging that LeetCode achieved 0% on 2/3 seeds; training convergence not separately verified; potential confound noted.

### Style Fix: "dwarfs" → "substantially exceeds" (Introduction)
- Minor tone improvement

---

## Round 1 Summary

| Category | Found | Fixed | Remaining |
|----------|-------|-------|-----------|
| FATAL | 2 | 2 | 0 |
| MAJOR | 3 | 3 | 0 |
| MINOR | 4 | 0 (collected for human review) | 4 |

---

## Round 2 Revisions (06_paper_r1.md → 06_paper_r2.md)

### MINOR-R2-001 Fix: Notation inconsistency in Section 5.4 η² note
- **Before**: "Absolute spread (0.055pp vs 0.319pp)"
- **After**: "Absolute spread (5.5pp vs 31.9pp)"
- **Rationale**: Previous notation mixed decimal fractions (0.055) with "pp" (percentage points) unit suffix, making the values appear as 0.055 percentage points rather than 5.5 percentage points. Corrected to percentage notation consistent with rest of paper.

### Round 2 Summary

| Category | Found | Fixed | Remaining |
|----------|-------|-------|-----------|
| FATAL | 0 | 0 | 0 |
| MAJOR | 0 | 0 | 0 |
| MINOR | 1 | 0 (collected for human review) | 1 |

**All FATAL and MAJOR issues resolved. Convergence criteria met.**

---

## Final Summary

**Total Revisions Made**: 8 (5 fixes + 1 addition + 1 notation + 1 wording)  
**Sections Modified**: Abstract, Introduction, Results (Table 1, Section 5.4 note), Discussion (Section 6.4), Conclusion  
**Word Count Change**: Original ~5800 → Final ~5900 (+~100 words, limitation addition)

**Review Process**:
- Started: 2026-08-03
- Rounds: 2
- Personas Used: accuracy_checker, bored_reviewer, skeptical_expert

**Files Generated**:
- 06_paper_final.md (final paper)
- 065_review_summary.md (review summary)
- 065_human_review_notes.md (MINOR issues for human review)
- 065_changelog.md (this file)

**Next Phase**: Phase 6.5.1 (Overleaf LaTeX/PDF generation)
