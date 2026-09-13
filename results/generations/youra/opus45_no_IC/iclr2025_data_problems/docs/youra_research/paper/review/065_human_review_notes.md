# Human Review Notes - Phase 6.5

These are MINOR issues collected during adversarial review that require human judgment to fix.
Do NOT auto-fix these issues.

## Round 1 Notes

### 1. [MINOR] "Transfer Function" in title never defined
- **Location:** Title, throughout paper
- **Type:** definition_inconsistency
- **Issue:** Title promises "A Transfer Function Approach" but paper never defines what the transfer function is or how it differs from simple correlation analysis
- **Suggested Action:** Either define transfer function mathematically or consider alternative title

### 2. [MINOR] Corpus coverage limitation buried
- **Location:** Section 4 (Experimental Setup)
- **Type:** clarity
- **Issue:** Critical limitation that only 0.006% of The Pile was analyzed appears briefly but isn't prominently flagged
- **Suggested Action:** Consider elevating to prominent limitation status

### 3. [MINOR] 2/4 benchmarks not statistically significant
- **Location:** Section 5 (Per-Benchmark Analysis)
- **Type:** clarity
- **Issue:** HellaSwag (p=0.08) and WinoGrande (p=0.15) not significant at p<0.05; this is mentioned but could be clearer
- **Suggested Action:** Explicitly state "correlation significant for 2/4 benchmarks only"
- **Status:** PARTIALLY ADDRESSED in R1 revision (added to Limitations section)

---

## Round 2 Notes

### 4. [MINOR] MMLU p-value precision inconsistency
- **Location:** Abstract vs Section 5 table
- **Type:** metric_consistency
- **Issue:** Abstract uses "p < 0.01" but table shows exact "p = 0.002"
- **Suggested Action:** Use consistent precision throughout

### 5. [MINOR] Max overlap rounding inconsistency  
- **Location:** Abstract (17.4%) vs table (17.41%)
- **Type:** mathematical_validity
- **Issue:** Inconsistent decimal places
- **Suggested Action:** Use consistent precision

### 6. [MINOR] N-gram index size not mentioned
- **Location:** Section 4 Experimental Setup
- **Type:** missing_limitations
- **Issue:** Paper mentions 50k documents but not the 37.7M unique hashes index size
- **Suggested Action:** Add index size for reproducibility

### 7. [MINOR] H-M1 gate failure not explicitly mentioned
- **Location:** Section 5.2 and Discussion
- **Type:** signal_performance_gap
- **Issue:** H-M1 technically FAILED its >1% mean overlap threshold; paper frames 17.4% max as success
- **Suggested Action:** Add note: "While mean overlap fell below threshold, individual items confirm mechanism validity"

---

## Summary
- **Total MINOR issues:** 7
- **By type:**
  - definition_inconsistency: 1
  - clarity: 2
  - metric_consistency: 1
  - mathematical_validity: 1
  - missing_limitations: 1
  - signal_performance_gap: 1
