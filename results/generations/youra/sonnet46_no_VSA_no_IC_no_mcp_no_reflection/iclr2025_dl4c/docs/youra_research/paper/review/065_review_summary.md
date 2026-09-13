# Adversarial Review Summary

**Paper:** When Reward Granularity Matters: Mechanistic Analysis of Ratio vs. Binary Reward in GRPO Post-Training for Code LLMs  
**Review Completed:** 2026-08-31  
**Rounds Completed:** 2 (R1 + R2)  
**Final Status:** CONVERGED  
**Persuasiveness Check:** PASSED  

---

## Executive Summary

This paper underwent 2 rounds of adversarial review with three-persona analysis (accuracy_checker, bored_reviewer, skeptical_expert). The paper's core claims are mathematically sound and fully verified against ground truth. One FATAL issue (experimental configuration discrepancy) and four MAJOR issues (scope overclaim, figure misplacement, table precision, stale limitation text) were identified in R1 and resolved. R2 found no new FATAL or MAJOR issues.

| Severity | Found | Resolved | Remaining |
|----------|-------|----------|-----------|
| FATAL | 1 | 1 | 0 |
| MAJOR | 4 | 4 | 0 |
| MINOR | 8 | 0 (human review) | 8 (in notes) |

**MINOR Issues:** Collected in `065_human_review_notes.md` (NOT auto-fixed)

---

## Persuasiveness Assessment

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | Strong "98.7% zero gradient" hook with mathematical guarantee |
| Problem clear by paragraph 2? | PASS | Dead zone explained clearly with concrete example |
| Novelty clear by page 1? | PASS | Contribution list is concrete and falsifiable |
| Figure 1 self-explanatory? | UNCERTAIN | Cannot verify without rendered figure; description sufficient |
| Hook avoids "X is important"? | PASS | Opens with striking statistic, not importance claim |
| "Every published paper" scope | FIXED → PASS | Qualified to 4 named papers |
| Would continue reading? | YES | Null result framing is compelling and honest |

---

## Round-by-Round Summary

### Round 1: Three-Persona Review

**Accuracy Checker Findings:**

| Category | Issues Found |
|----------|--------------|
| max_new_tokens discrepancy (FATAL) | 1 |
| Figure 2 misplacement (MAJOR) | 1 |
| Table 2 grad_norm precision (MAJOR) | 1 |

**Bored Reviewer Findings:**

| Category | Issues Found |
|----------|--------------|
| Scope overclaim "every paper" (MAJOR) | 1 |
| Minor clarity/style | 4 |

**Skeptical Expert Findings:**

| Category | Issues Found |
|----------|--------------|
| Stale §6.3 "pending CI" (MAJOR) | 1 |
| Minor clarity | 2 |

**Key Issues Addressed:**
1. FATAL-001: h-e1 smoke test used max_new_tokens=256, not 512. Added footnote to §5.3 and split notation in §3.5 table.
2. MAJOR-ENG-001: "Every published paper" → "All major published papers (CodeRL, PPOCoder, RLEF/Gehring, DAPO)"
3. MAJOR-ACC-001: Figure 2 reference in §5.2 → forward reference to §5.4
4. MAJOR-ACC-002: Table 2 grad_norm "~10⁻³" → actual CI values (mean: +0.000730; 95% CI: [−0.000253, +0.002561])
5. MAJOR-SKE-001: §6.3 "pending CI" limitation → replaced with accurate description of available CI

### Round 2: Numerical Verification

**Accuracy Checker:** All 20 ground truth claims verified. Mathematical derivations M1–M4 independently computed and confirmed exact. Omitted claims O1–O4 confirmed absent from paper.

**Skeptical Expert:** No baseline fairness issues (paper makes no external baseline comparisons). Signal-performance gap (null result) correctly explained in §6.1–6.2. 

R2 found 0 FATAL, 0 MAJOR issues. 2 additional MINOR items collected.

---

## Sections Modified

| Section | Modifications |
|---------|---------------|
| Abstract | "Every published paper" → "All major published papers" |
| §1 Introduction | Same scope fix; "exclusive" → "used by all major"; "ubiquitous" → "widespread" |
| §3.5 Table | max_new_tokens split: "512 (h-m1); 256 (h-e1 smoke test)¹" |
| §5.2 | Figure 2 reference → forward reference to §5.4 |
| §5.3 | Footnote ¹ explaining h-e1 used 256-token configuration |
| §5.4 Table 2 | grad_norm row updated with actual measured CI values |
| §6.3 | "Pending CI" limitation rewritten with accurate, available CI |
| §7 Conclusion | "Every published RLEF paper" → "All major published RLEF papers (CodeRL, PPOCoder, RLEF/Gehring, DAPO)" |

---

## Quality Improvements

- **Logical Consistency:** Improved (§6.3 stale text removed)
- **Numerical Accuracy:** Improved (Table 2 grad_norm, §3.5 max_new_tokens)
- **Novelty Claims:** Refined (scope qualified to reviewed papers)
- **Baseline Comparison:** N/A (no external baselines)
- **Persuasiveness:** Maintained (hook and structure already strong)

---

## Reviewer Preparation Notes

Potential remaining attack surfaces for real reviewers:

1. **"Every published paper" claim (qualified but still broad):** Even with qualification to 4 papers, reviewers may know of niche works using partial-credit reward. Suggested response: "We reviewed the four major RLEF-for-code papers. We are not aware of published work using partial-credit reward in GRPO for code LLMs; we welcome counterexamples."

2. **Single model, single dataset:** Addressed in §6.3 but reviewers may push for generalization evidence. Suggested response: "The mechanistic claim (h-e1) is model-agnostic — it is a property of GRPO normalization, not model internals. The policy-level null result (h-m1) is precisely characterized and points to the corrective experiment."

3. **Null result publication value:** Some reviewers may question whether a paper with a null policy result deserves publication. Suggested response: "The mechanistic proof is a positive result. The null result is a precision finding that identifies a prerequisite. Together they are more informative than a positive result without mechanistic grounding."

4. **Citation verification (all marked INFERRED):** The references.bib file notes all arXiv IDs are inferred. These should be verified against Semantic Scholar before final submission.

---

## Files Generated

| File | Path | Status |
|------|------|--------|
| Final Paper | paper/06_paper_final.md | ✓ |
| Review R1 | paper/review/065_review_r1.md | ✓ |
| Review R2 | paper/review/065_review_r2.md | ✓ |
| Review Summary | paper/review/065_review_summary.md | ✓ (this file) |
| Human Review Notes | paper/review/065_human_review_notes.md | ✓ |
| Changelog | paper/review/065_changelog.md | ✓ |
| Checkpoint | paper/review/065_review_checkpoint.yaml | ✓ |

**Next Phase:** Phase 6.5.1 (Overleaf LaTeX/PDF generation)
