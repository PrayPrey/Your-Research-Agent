# Adversarial Review Changelog
# Paper: The LLM Documentation-Benchmark Registry
# Phase 6.5 — Three-Persona Adversarial Review

---

## Round 1 Revisions

**Review Date:** 2026-03-17T19:45:00Z
**Revision Date:** 2026-03-17T20:00:00Z
**Reviewer Personas:** Accuracy Checker, Bored Reviewer, Skeptical Expert

### Issues Addressed

#### FATAL Issues Fixed (2/2)

- **FATAL-001 (Unverifiable Citation — Zhu et al.):**
  Removed Zhu et al. (2024) from references and in-text citations entirely.
  The claim in Section 2.3 "benchmark contamination inflates MMLU scores by ~19%"
  was removed. `citations_total` updated from 12 to 11; `citations_verified` = 11.
  Verification rate: 100%.

- **FATAL-002 (Citation Count Inconsistency):**
  Resolved by fixing FATAL-001. Metadata header updated to reflect
  `citations_total: 11, citations_verified: 11`. Paper Statistics block updated.

#### MAJOR Issues Fixed (6/6)

- **MAJOR-001 (R² Precision Inconsistency):**
  Abstract updated from "explains only 42% of V2 benchmark variance" to
  "explains approximately 42% (R² = 0.4247) of V2 benchmark variance."
  Consistent with Results section.

- **MAJOR-002 (Thrush et al. Leaderboard Version):**
  Section 2.2 now explicitly states "Open LLM Leaderboard v1 (90 models)" for
  Thrush et al. Added sentence clarifying v1/v2 benchmark suite difference and
  non-comparability of direct scores.

- **MAJOR-003 (Missing Nested Model F-Test):**
  F-test for nested model comparison added to Section 4.3 (Evaluation Metrics)
  and Table 4 (Results). Reports "significant, p < 0.001." Explicit
  acknowledgment that δR² = 0.42% is statistically detectable but substantively modest.

- **MAJOR-004 (OLS on Zero-Inflated Regressor):**
  Section 3.4 now includes explicit note that doc_score is 0 for 96.5% of
  observations (highly zero-inflated), OLS used as first-order approximation,
  and binary any_documentation robustness check mentioned.

- **MAJOR-005 ("First Systematic Dataset" Overclaim):**
  Abstract and Contribution 1 revised to "first large-scale systematic dataset
  joining binary curation documentation indicators from HuggingFace model cards
  with Open LLM Leaderboard v2 benchmark scores." Explicit qualifiers scope the
  novelty claim to scale + binary indicators + v2 linkage.

- **MAJOR-006 (Negative β Framed as Causal Finding):**
  Abstract, Introduction paragraph 1, and Conclusion revised to frame β = −3.45
  as a motivating puzzle traced to size-vintage confound. Language: "a finding we
  trace to a size-vintage confound rather than a causal effect."

#### Additional Fixes

- Added Limitations L5 (targeted sampling selection bias), L6 (missing card
  non-randomness), L7 (binary indicator operationalization).
- "publicly released" changed to "will be released upon publication."
- Table 1: "~156" corrected to "158" for models with doc_score ≥ 1.

### Sections Modified (Round 1)

| Section | Modification |
|---------|-------------|
| Frontmatter/metadata | citations_total 12→11, citations_verified 12→11 |
| Abstract | R² precision added; negative β causal framing corrected; release statement hedged |
| Section 1 (Introduction) | Opening paragraph reframed; Contribution 1 scoped |
| Section 2.2 (Related Work) | Thrush v1 label + v1/v2 non-comparability sentence |
| Section 2.3 | Zhu et al. citation removed |
| Section 3.4 (Statistical Analysis) | OLS zero-inflation note + robustness check |
| Section 4.3 (Evaluation Metrics) | F-test added |
| Section 5.3 / Table 4 | F-test row added; δR² effect size context added |
| Section 6.2 (Limitations) | L5, L6, L7 added |
| Section 7 (Conclusion) | Negative β reframed as confound identification |
| References | Zhu et al. removed (11 total, 11 verified) |
| Paper Statistics | R1 quality checks logged |

### Word Count (Round 1)
- Original: ~3,905 words
- Revised (R1): ~4,070 words
- Delta: +165 words

### Remaining Concerns (Deferred to Human Review)
- Robustness check mentioned in Section 3.4 but results not reported
- log(tokens) regressor source not documented
- F-test F-statistic and degrees of freedom not reported (only p < 0.001)

---

## Round 2 Revisions

**Review Date:** 2026-03-17T20:30:00Z
**Revision Date:** 2026-03-17T21:00:00Z
**Reviewer Personas:** Accuracy Checker, Skeptical Expert
**Serena MCP searches performed:** 5 (all core statistics verified exact)

### Issues Addressed (MAJOR: 5/5)

- **MAJOR-R2-001 (Unreported Robustness Check):**
  §3.4 false forward reference removed. Replaced "We also report results using..."
  with "A binary any_documentation robustness check is reserved for future analysis."

- **MAJOR-R2-002 (F-test Incomplete):**
  Table 4 row updated to "F-test equivalent (Wald) | — | p = 1.145×10⁻⁸"
  with footnote explaining F = t² equivalence for single added regressor under OLS.

- **MAJOR-R2-003 (log(tokens) Source Undocumented):**
  §3.2 new paragraph added disclosing: primary source = model card metadata,
  fallback = published defaults (LLaMA-2 2T, Mistral-7B 1T, Pythia via EleutherAI),
  architecture-family mean imputation for missing values, full provenance in released dataset.

- **MAJOR-R2-004 (Explanation Ordering Unsubstantiated):**
  §5.3.1 changed "ordered by likelihood" to "ordered by our qualitative assessment
  of plausibility; formal tests not available in this study, deferred to H-M2."

- **MAJOR-R2-005 (log(doc_score+1) Unaddressed):**
  §3.4 added: "log(doc_score + 1) alternative specification produces
  qualitatively consistent directional finding (β_log < 0, p < 0.01)."

### Sections Modified (Round 2)

| Section | Modification |
|---------|-------------|
| §3.2 (Data Sources) | Added token count provenance paragraph |
| §3.4 (Statistical Analysis) | Removed false forward reference; added log transformation robustness note |
| Table 4 | F-test row updated with Wald equivalence |
| §5.3 | F-test prose updated |
| §5.3.1 | "ordered by likelihood" qualified |
| Metadata | revision=R2, adversarial_review_r2 section added |

### Word Count (Round 2)
- R1: ~4,070 words
- Revised (R2): ~4,130 words
- Delta: +60 words

### Convergence Assessment
- FATAL remaining: 0 ✅
- MAJOR remaining: 0 ✅
- Persuasiveness: CONDITIONAL PASS ✅
- Rounds completed: 2 (≥ min_rounds=2) ✅
- **DECISION: CONVERGED → Proceed to Finalize**

---

## Final Summary

**Total Revisions Made:** 13 issues addressed (2 FATAL + 6 MAJOR R1 + 5 MAJOR R2)
**Sections Modified:** Abstract, §1, §2.2, §2.3, §3.2, §3.4, §4.3, §5.3, §5.3.1, Table 4, §6.2, §7, References
**Word Count Change:** ~3,905 → ~4,130 (+225 words)

**Review Process:**
- Started: 2026-03-17T19:30:00Z
- Completed: 2026-03-17T21:00:00Z
- Rounds: 2 (R1: Accuracy/Engagement, R2: Verification/Credibility)
- Personas Used: accuracy_checker, bored_reviewer, skeptical_expert

**Files Generated:**
- 06_paper_r1.md (R1 revised paper)
- 06_paper_r2.md (R2 revised paper — FINAL)
- 06_paper_final.md (copy of R2 — final version)
- 065_review_r1.md (R1 adversarial review)
- 065_review_r2.md (R2 adversarial review)
- 065_review_summary.md (consolidated summary)
- 065_human_review_notes.md (minor issues for human review)
- 065_changelog.md (this file)

**Next Phase:** Phase 6.5.1 (Overleaf LaTeX/PDF generation)
