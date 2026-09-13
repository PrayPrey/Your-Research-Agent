# Adversarial Review Changelog
**Paper**: "Language-Family Retention Bias from Global CCNet Perplexity Thresholding"
**Started**: 2026-07-30
**Execution mode**: UNATTENDED

---

## Round 1 Revisions

### Fix 1: BR-MAJOR-001 — Abstract overclaim narrowed
**Location**: Abstract, sentence 1
**Severity**: MAJOR
**Issue**: "never been precisely quantified" overclaims beyond the paper's actual scope (specific dataset+signal+threshold combination). Contradicts the more precise claim in Section 2.5.

**Before**:
> "Multilingual pretraining datasets routinely use CCNet-style perplexity quality filters, but the consequences of applying a single global threshold to per-language perplexity scores have never been precisely quantified."

**After**:
> "Multilingual pretraining datasets routinely use CCNet-style perplexity quality filters, but the magnitude of the language-group retention disparity produced by applying a single global threshold to pre-computed ccnet_perplexity scores on RedPajama-V2 has not been precisely quantified using a standard association metric."

**Rationale**: Aligns Abstract scope with the precise claim in Section 2.5 ("first to quantify the language-group retention disparity (Cramér's V) from global ccnet_perplexity thresholding on RedPajama-V2"). Prevents reviewer attack on "never been quantified" as an absolute.

---

### Fix 2: SE-MAJOR-001 — Contingency table dimension transposition corrected
**Location**: Methodology Section 3.4; Abstract/Introduction formula context
**Severity**: MAJOR
**Issue**: "2×5 contingency table" with rows=languages, columns=retained/removed is by convention a 5×2 table (5 rows × 2 columns). The formula correctly uses r=5, c=2, but the table descriptor was inverted.

**Before**:
> "we construct a 2×5 contingency table (language × retained/removed)"
> "r = 5 languages, c = 2 (retained/removed)"

**After**:
> "we construct a 5×2 contingency table (5 languages × 2 outcomes: retained/removed)"
> "r = 5 (languages, the row dimension), c = 2 (retained/removed, the column dimension)"

**Rationale**: The formula and computation were always correct. Only the textual description was inverted. Now consistent: 5 rows (languages) × 2 columns (retained/removed) = 5×2 table, min(r,c)=min(5,2)=2. ✅

---

## Round 1 Summary

| Category | Count |
|----------|-------|
| MAJOR issues fixed | 2/2 |
| MINOR issues collected for human review | 6 |
| Numerical values changed | 0 |
| Sections modified | Abstract, Methodology (Sec 3.4) |
| Word count delta | +18 words (Abstract expanded for precision) |

---

---

## Round 2 Revisions

### Fix 3: NUM-MAJOR-001 — Chi² values corrected to authoritative results.json
**Location**: Results Table 1 (5 rows)
**Severity**: MAJOR
**Issue**: Chi² values in Table 1 (and in 065_ground_truth.yaml) were sourced from an earlier hypothesis iteration (h-e1-v3), not the authoritative final run (h-e1-v3-v4). Cramér's V values were correct throughout; only chi² differed.

**Before** (from h-e1-v3 / stale ground truth):
| k | Chi² |
|---|------|
| 10 | 33,674 |
| 20 | 56,076 |
| 30 | 66,156 |
| 40 | 67,752 |
| 50 | 58,570 |

**After** (from h-e1-v3-v4/results.json — authoritative):
| k | Chi² |
|---|------|
| 10 | 33,675 |
| 20 | 56,153 |
| 30 | 66,000 |
| 40 | 67,572 |
| 50 | 58,342 |

**Rationale**: All values verified against h-e1-v3-v4/results.json (the experiment run that passed the gate). Cramér's V is unchanged and correct. The chi² values are auxiliary statistics but must match the code output for reproducibility claims.

---

## Round 2 Summary

| Category | Count |
|----------|-------|
| MAJOR issues fixed | 1/1 |
| MINOR issues collected for human review | 1 |
| Numerical values changed | 4 chi² values in Table 1 |
| Sections modified | Results Table 1 |
| Word count delta | 0 (table values only) |

---

## Final Summary

**Total Revisions Made**: 3 (2 from R1 + 1 from R2)
**Sections Modified**: Abstract, Methodology (Sec 3.4), Results (Table 1)
**Word Count Change**: ~+18 words (Abstract precision expansion)

**Review Process**:
- Started: 2026-07-30
- Completed: 2026-07-30
- Rounds: 2 (R1 + R2)
- Personas: accuracy_checker, bored_reviewer, skeptical_expert

**Files Generated**:
- 06_paper_r1.md (R1 fixes: Abstract scope, contingency table dimensions)
- 06_paper_r2.md (R2 fix: chi² values corrected)
- 06_paper_final.md (copy of r2 — final version)
- 065_review_r1.md (R1 adversary report)
- 065_review_r2.md (R2 adversary report)
- 065_review_summary.md (consolidated review summary)
- 065_human_review_notes.md (7 MINOR issues for human review)
- 065_changelog.md (this file)

**Next Phase**: Phase 6.5.1 (Overleaf LaTeX/PDF generation)
