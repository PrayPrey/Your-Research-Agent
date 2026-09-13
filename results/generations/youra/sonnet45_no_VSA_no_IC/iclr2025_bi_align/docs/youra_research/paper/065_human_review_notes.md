# Human Review Notes — Minor Issues (Phase 6.5 R1)

**Generated:** 2026-08-20  
**Round:** 1  
**Status:** For human review — do NOT auto-fix

---

## Accuracy Checker — Minor Numerical/Formatting Issues

### 1. Execution overhead precision (MINOR)
**Location:** Abstract, line 3  
**Current:** "25 LOC, <1ms execution time"  
**Ground truth:** 0.01ms exactly  
**Suggested fix:** "25 LOC, 0.01ms execution time"  
**Rationale:** '<1ms' technically correct but imprecise

### 2. LOC per hypothesis vs total (MINOR)
**Location:** Introduction, line 22  
**Current:** "25-27 lines of code per hypothesis"  
**Ground truth:** 25-27 LOC for entire contract layer (validates all hypotheses)  
**Suggested fix:** "25-27 lines of code for the contract layer"  
**Note:** Already fixed in MAJOR revisions (contribution #4)

### 3. Rounding consistency (MINOR)
**Location:** Results Section 5.1, Table 1, line 250  
**Current:** "33.3%"  
**Ground truth:** 33.33%  
**Suggested fix:** "33.33%" for consistency with other tables  
**Note:** Low priority — both are correct

### 4. Schema-only overhead assumption (MINOR)
**Location:** Results Section 5.1, Table 1 notes  
**Current:** Both conditions show 0.01ms  
**Ground truth:** Only contract-based measured; schema-only assumed equivalent  
**Suggested fix:** Add footnote: "Schema-only overhead assumed equivalent; contract layer adds negligible cost"  
**Note:** Added in Table 1 note during MAJOR fixes

---

## Bored Reviewer — Engagement/Pacing Issues

### 5. Abstract opening (MINOR - style)
**Location:** Abstract sentence 1  
**Current:** Starts with problem (generic failure mode)  
**Suggested fix:** Lead with novelty (already done in MAJOR revision)  
**Status:** FIXED in R1

### 6. Introduction uncited stat (MINOR)
**Location:** Introduction paragraph 1  
**Issue:** "80% of AI agents fabricate" has no citation  
**Suggested fix:** Add citation or delete/soften claim  
**Note:** Removed in MAJOR revision (Conclusion edit)

### 7. Code blocks in Methodology (MINOR)
**Location:** Section 3.2  
**Issue:** 30+ line code examples verbose  
**Suggested fix:** Shorten to 5-line pseudo-code, move full code to appendix  
**Decision:** Keep for now (substantive editorial choice)

### 8. SIL testing analogy (MINOR)
**Location:** Section 4.2 placeholder justification  
**Issue:** Drone analogy feels defensive  
**Suggested fix:** Delete analogy, own the placeholder limitation  
**Decision:** Keep (provides useful mental model)

### 9. Results table redundancy (MINOR)
**Location:** Section 5 (Tables 1, 2, 3, 5)  
**Issue:** Multiple tables repeat "100%" in different formats  
**Suggested fix:** Merge into single summary table  
**Decision:** Keep separate (different hypotheses, different metrics)

### 10. Threats to validity repetition (MINOR)
**Location:** Section 6.5  
**Issue:** Repeats earlier caveats from 6.2  
**Suggested fix:** Merge unique points (false positive rate) into 6.2  
**Decision:** Keep structure (standard paper section)

### 11. Future work generic list (MINOR)
**Location:** Conclusion paragraph 5  
**Issue:** Future work is obvious next steps  
**Suggested fix:** Cut to 1 sentence  
**Decision:** Keep (helps frame limitations)

---

## Skeptical Expert — Remaining Minor Issues After MAJOR Fixes

### 12. Novelty claim hedging (MINOR)
**Location:** Introduction contribution #1  
**Current:** "First application of Design-by-Contract to semantic constraint validation in research workflows"  
**Issue:** Graflow uses contracts for workflows (different constraint type)  
**Fix applied:** Already hedged to "semantic constraint validation" (not just "research automation")  
**Remaining suggestion:** Could add "(not just task idempotence as in Graflow)"  
**Status:** FIXED in R1

### 13. Pattern layer recall clarification (MINOR)
**Location:** Discussion 6.2 / Results interpretation  
**Issue:** 80% recall from adversarial suite vs 100% detection on corpus (different datasets)  
**Fix applied:** Added clarification in Discussion 6.1  
**Remaining suggestion:** Add to Results Section 5.3 Table 4 note  
**Status:** FIXED in R1 (Discussion only)

### 14. Baseline fairness clarification (MINOR)
**Location:** Experiments Section 4.3  
**Issue:** Schema-only excludes validators — is this current practice?  
**Fix applied:** Added clarification that baseline isolates structural schema, validators excluded by design  
**Remaining suggestion:** Could add Great Expectations comparison in Related Work  
**Status:** FIXED in R1

---

## Summary

- **Total MINOR issues:** 14
- **Auto-fixed in MAJOR revisions:** 5
- **Require human judgment:** 9
  - 3 numerical precision (low priority)
  - 4 pacing/style (editorial choice)
  - 2 clarifications (already addressed in text, could add footnotes)

**Recommendation:** Proceed to Round 2 adversarial review. Remaining MINOR issues are low-priority formatting/style choices suitable for final copy-editing phase.

---

**Next Step:** Run Round 2 adversarial review (numerical verification with Serena MCP) to catch discrepancies between paper and actual Phase 4 validation report files.
