# Human Review Notes — Phase 6.5 Adversarial Review

> **Purpose:** Minor issues collected during adversarial review for human inspection. These were NOT auto-fixed; they require editorial judgment.

**Date:** 2026-08-31  
**Rounds Completed:** 2 (R1, R2)  
**Status:** CONVERGED (all FATAL/MAJOR issues resolved)

---

## Summary by Category

| Category | Count |
|---|---|
| Clarity | 2 |
| Style | 1 |
| Completeness | 1 |
| **Total** | **4** |

---

## Round 1 Issues

### MIN-001 — Clarity: Section 7.1 omits Z3 from ordered range

**Location:** Section 7.1, paragraph 1  
**Current text:** "repair success falls monotonically as feedback volume rises, from mypy's 6.35% down to Pyright's 4.76%"  
**Issue:** The full inverse ordering is Z3 (7.94%) → mypy (6.35%) → execution (5.56%) → Pyright (4.76%). The Conclusion's summary says "from mypy's 6.35%" which omits Z3 as the top endpoint, understating the range and skipping the most extreme data point.  
**Suggested fix:** "from Z3's 7.94% at the top of the repair range down to Pyright's 4.76%, giving ρ = -1.0"  
**Priority:** Medium — readers of the Conclusion alone would miss Z3's role

---

### MIN-002 — Style: Abstract opener length

**Location:** Abstract, sentence 1  
**Current text:** "Systems that repair language-model-generated code by feeding verifier output back into the prompt must choose what goes in the verify stage, and that choice currently rests on an untested intuition: that a more formally rigorous verifier produces more precise feedback and therefore better repair." (48 words)  
**Issue:** Long setup before the research frame. The current version is not wrong — it provides useful context. Tightening is optional.  
**Suggested alternative:** "The verify stage in LLM repair loops rests on an untested assumption: more formally rigorous feedback produces better repair."  
**Priority:** Low — style preference only

---

### MIN-003 — Clarity: Two "invert" uses may momentarily confuse

**Location:** Abstract, paragraph 3  
**Current text:** "The intuition inverts... Cost inverts the ranking again"  
**Issue:** The word "invert" describes two distinct phenomena in adjacent sentences (repair ↓ as feedback ↑, then efficiency ↑ despite repair ↓). A first-time reader may need a second pass to track which inversion is which.  
**Suggested fix:** Explicitly label: "This is the first inversion... Cost produces a second inversion..." Or restructure to lead with "Two inversions define our results."  
**Priority:** Low — content is clear on re-read

---

### MIN-004 — Completeness: Conclusion restates ρ = -1.0 without n=4 caveat

**Location:** Sections 7.1 and 7.3  
**Current text (7.3):** "a Spearman correlation of -1.0 later, that expectation is not weakly supported but exactly inverted"  
**Issue:** Section 5.4 carefully notes "ρ computed over four points is a coarse statistic; it can only take a handful of values, and -1.0 means 'perfectly ordered,' not 'strongly correlated'." The Conclusion repeats ρ = -1.0 without this nuance. A reader who encounters the Conclusion first (common for reviewers) may form an inflated impression of statistical strength.  
**Suggested fix:** In Section 7.1 or 7.3, add parenthetical: "(ρ = -1.0, n = 4 categories; see §5.4 for caveats)"  
**Priority:** Medium — important for managing reviewer expectations

---

## Round 2 Issues

No new MINOR issues found in Round 2.

---

## Citation Issues (Pre-existing — Not Auto-Fixed)

**14 citations are marked [UNVERIFIED] in the paper** (disclosed in References section). Per `065_ground_truth.yaml` citation_status, known internal inconsistencies include:

| Citation | Issue |
|---|---|
| Gazzola et al. 2019 | Venue disputed: IEEE TSE vs. ACM Computing Surveys |
| Monperrus 2023 | Title and year uncertain |
| Poesia et al. 2021 | arXiv ID implies 2022, record says 2021 |
| Olausson et al. 2023 | Two different paper titles appear across pipeline artifacts |

**Action required before submission:** Verify all 14 citations against a live bibliographic index (Semantic Scholar, DBLP, or arXiv). Correct venue, year, title, and author lists as needed.

---

## Recommended Priority

1. **Fix first (medium priority):** MIN-001 (Z3 omitted in Conclusion), MIN-004 (ρ caveat in Conclusion)
2. **Verify before submission (CRITICAL):** All 14 [UNVERIFIED] citations
3. **Optional style:** MIN-002 (abstract opener), MIN-003 (double "invert")

---

*Note: These issues do not block paper convergence but improve clarity and citation integrity.*
