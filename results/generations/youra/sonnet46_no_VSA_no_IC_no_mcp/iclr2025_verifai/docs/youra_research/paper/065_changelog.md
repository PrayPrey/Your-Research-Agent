# Phase 6.5 Changelog

**Generated:** 2026-08-26
**Base file:** 06_paper.md → 06_paper_final.md

---

## Changes Applied

### R1 — Round 1 (Adversarial Review)

| ID | File | Location | Change | Reason |
|----|------|----------|--------|--------|
| R1-01 | 06_paper.md | Abstract, line ~13 | "suggesting mypy functions as a general diagnostic context enricher" → "consistent with mypy functioning as a general diagnostic context enricher (this mechanism remains unconfirmed via ablation; see Section 6)" | MAJOR: mechanism claim stronger than evidence supports |
| R1-02 | 06_paper.md | Results §RQ4, Table 2 caption | Added "(seed std: A=±1.56pp, B=±0.49pp; delta range: 6.7pp to 11.0pp)" | MAJOR: primary claim lacked variance reporting |
| R1-03 | 06_paper.md | Introduction, ~line 93 | "The most parsimonious explanation is" → "The most parsimonious interpretation — though not yet confirmed via ablation —" | MAJOR: consistent with Abstract fix |
| R1-04 | 06_paper.md | Discussion §Key Findings | Added "pending ablation confirmation (see L2)" to mechanism sentence | MAJOR: consistency with L2 limitation |
| R1-05 | sections/05_results.md | RQ2, Spearman line | "p < 0.01 by rank correlation against round index" → "p=0.182; p-value is uninformative with n=5 rounds..." | FATAL (section file): incorrect p-value claim |

### R2 — Round 2 (Numerical Verification)

| ID | File | Location | Change | Reason |
|----|------|----------|--------|--------|
| R2-01 | 06_paper.md | Results §RQ4 | "B = ±0.64pp" → "B = ±0.49pp" | Arithmetic correction: std([86.6,87.8,87.2])=0.49, not 0.64 |

---

## Files Generated

| File | Description |
|------|-------------|
| paper/06_paper_final.md | Final reviewed paper (copy of revised 06_paper.md) |
| paper/065_review_summary.md | Full review summary with all findings |
| paper/065_human_review_notes.md | Minor issues deferred for human review |
| paper/065_changelog.md | This file |

---

## Minor Issues Deferred (Human Review)

- M1: Related work coverage thin — consider adding test-based repair paragraph
- M2: Table 1 non-type-error values approximate (~78%/~79%); exact values are 83.8%/84.4%
- M3: "general diagnostic context enricher" term may need inline definition
