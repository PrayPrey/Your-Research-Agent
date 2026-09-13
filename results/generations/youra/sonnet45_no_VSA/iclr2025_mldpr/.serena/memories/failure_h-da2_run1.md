# Phase 4 Failure Record: h-da2 (Run 1)

**Date:** 2026-07-12T18:31:03Z
**Hypothesis:** h-da2
**Run:** 1
**Final Status:** FAIL
**Failure Type:** EXTRACTION_METHODOLOGY_FAILURE

## Performance Gap

| Metric | Ours | Baseline | Gap |
|--------|------|----------|-----|
| Coverage Rate | 0.0% | 80.0% (target) | -80.0% (100% failure) |
| Temporal Consistency | r=0.000, p=1.000 | r≥0.70, p<0.05 (target) | Failed both criteria |
| Contamination Ratio | 1.00 | ≥0.80 (target) | ✅ PASS (only passing criterion) |

## Root Cause Analysis

### 1. Sample Selection Error
- **Issue:** Used ML framework repositories (pytorch, transformers) instead of dataset repositories
- **Impact:** 100% of sample was wrong repository type
- **Evidence:** Hardcoded repository list in config.py contains frameworks, not datasets from Papers with Code

### 2. Temporal Mismatch
- **Issue:** Artificial publication dates don't align with repository creation dates
- **Impact:** GitHub commit history extraction found 0 commits in T0 window for all 50 repositories
- **Evidence:** Repository creation predates assigned "publication dates"

### 3. External API Dependency Failure
- **Issue:** Wayback Machine CDX API connection refused/timeout
- **Impact:** 100% fallback extraction failure
- **Evidence:** Network restrictions or service unavailability blocked all archive queries

## Lessons Learned

1. **DTS_T0 extraction requires accurate temporal metadata** - Cannot use artificial publication dates when repository history predates them
2. **Sample selection must match experimental design** - Dataset repositories ≠ ML framework repositories
3. **External API dependencies introduce brittleness** - Wayback Machine unavailability = complete fallback failure
4. **Temporal precedence validation needs realistic data** - Current approach infeasible without proper dataset release dates

## Feedback for Next Phase

### Suggested Modifications
- Replace hardcoded repository list with Papers with Code API query for actual dataset repositories
- Extract real publication dates from paper metadata or dataset release information
- Add local documentation snapshot caching to reduce external API dependency
- Consider using dataset release dates directly instead of documentation snapshot timestamps

### What NOT To Do
- Don't use ML framework repositories as proxies for dataset repositories
- Don't rely solely on Wayback Machine without local fallback
- Don't assign artificial publication dates that conflict with repository history

### What Showed Promise
- Contamination test infrastructure works correctly (passed with ratio=1.00)
- DTS scoring rubric (Rondina 2025) is well-defined and ready for use
- Multi-source extraction strategy (GitHub + Wayback) is sound in principle, just needs correct sample

---

## Routing Decision

**Gate Result:** FAIL (MUST_WORK gate)  
**Route To:** Phase 2A-Dialogue  
**Reason:** Fundamental methodological issues prevent DTS_T0 extraction feasibility. Requires protocol redesign with correct sampling and realistic temporal metadata.

**Blocking Downstream:** This failure blocks H-E1 (causal effect estimation) and H-R1-4 (robustness checks) until extraction feasibility is resolved.

---
*For cross-phase reference*
*Written at: 2026-07-12T18:31:03Z*
