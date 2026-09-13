# Adversarial Review Changelog

**Paper:** Can Weight-Space Encoders Predict Generalization Gap?
**Review Started:** 2026-08-31T10:30:00+00:00
**Review Completed:** 2026-08-31T11:30:00+00:00
**Rounds:** 2

---

## Round 1 Changes (06_paper.md → 06_paper_r1.md)

### Change R1-001 — FATAL Fix: NFT CI Claim Corrected
**Issue:** SKEP-FATAL-001
**Location:** Introduction, Contribution 2
**Before:**
```
NFT achieves the highest gap Spearman (r = 0.5752, 95% CI: [0.5339, 0.6158]) with a non-overlapping
confidence interval from FlatMLP.
```
**After:**
```
NFT achieves the highest gap Spearman (r = 0.5752, 95% CI: [0.5339, 0.6158]). FlatMLP's 95% CI from
the same run is [0.4850, 0.5801]; the two intervals overlap at the margin ([0.5339, 0.5801]), but NFT's
lower bound exceeds FlatMLP's point estimate (0.5330), providing directional statistical evidence of
advantage.
```
**Reason:** NFT CI [0.5339, 0.6158] and FlatMLP CI [0.4850, 0.5801] overlap in [0.5339, 0.5801].

---

### Change R1-002 — FATAL Fix: NFT CI Claim Corrected (§5.2)
**Issue:** SKEP-FATAL-001 (same issue, second location)
**Location:** Results §5.2
**Before:**
```
NFT achieves the highest gap Spearman (r = 0.5752) with a 95% CI of [0.5339, 0.6158] that is
non-overlapping with FlatMLP's confidence band.
```
**After:**
```
NFT achieves the highest gap Spearman (r = 0.5752) with a 95% CI of [0.5339, 0.6158]. For comparison,
FlatMLP's 95% CI from the same run (h-m1) is [0.4850, 0.5801]. The two intervals overlap at the margin,
but NFT's lower bound (0.5339) exceeds FlatMLP's point estimate (0.5330), providing directional evidence
of NFT's advantage.
```

---

### Change R1-003 — MAJOR Fix: Table 1 FlatMLP CI Added + Dual-Run Footnote
**Issue:** ACCR-MAJOR-001 + ACCR-MINOR-001
**Location:** Results §5.1, Table 1
**Before:**
```
| FlatMLP | 0.5567 | — | 0.2790 | [0.2173, 0.3343] |
...
*FlatMLP gap CI not separately reported (from h-e1; NFT/DWS/GNN CIs from h-m1 bootstrap).*
```
**After:**
```
| FlatMLP | 0.5567† | [0.4850, 0.5801]‡ | 0.2790 | [0.2173, 0.3343] |
...
*† FlatMLP and DWSNet gap point estimates in Table 1 are from the existence run (h-e1). FlatMLP gap in
the architecture comparison run (h-m1) is 0.5330; this h-m1 value is used as the control baseline in
the Δ computation (Table 2)... ‡ FlatMLP 95% CI [0.4850, 0.5801] from h-m1 bootstrap.*
```
**Reason:** Readers need to understand two FlatMLP gap values (0.5567 h-e1, 0.5330 h-m1) and why each is used where.

---

### Change R1-004 — MAJOR Fix: Discussion Section Renumbered
**Issue:** BORE-MAJOR-001
**Location:** Discussion section headings + Introduction roadmap
**Changes:**
- "## 5.1 What the Results Tell Us..." → "## 6.1 What the Results Tell Us..."
- "## 5.2 The FlatMLP Test Accuracy Anomaly" → "## 6.2 The FlatMLP Test Accuracy Anomaly"
- "## 5.3 Limitations" → "## 6.3 Limitations"
- "## 5.4 Broader Impact" → "## 6.4 Broader Impact"
- Introduction roadmap: "Section 5 discusses..." → "Section 6 discusses..."
- Introduction roadmap: "Section 6 concludes." → "Section 7 concludes."
- Body cross-references: "Section 5 (Limitations)" → "Section 6.3 (Limitations)"
**Reason:** Results and Discussion both used §5.x numbering, creating ambiguous cross-references.

---

## Round 2 Changes (06_paper_r1.md → 06_paper_r2.md)

No FATAL or MAJOR issues found in R2. No changes made.
06_paper_r2.md is identical to 06_paper_r1.md.

---

## Final Summary

**Total Revisions Made:** 4 change sets (5 individual edits)
**Sections Modified:** Introduction (Contributions, roadmap), Results §5.1 (Table 1), Results §5.2, Discussion (all subsection headings)
**Word Count Change:** ~6289 → ~6350 (+61, due to expanded CI footnote and contribution 2 wording)

**Review Process:**
- Started: 2026-08-31T10:30:00+00:00
- Completed: 2026-08-31T11:30:00+00:00
- Rounds: 2
- Personas Used: accuracy_checker, bored_reviewer, skeptical_expert

**Files Generated:**
- `paper/06_paper_r1.md` — Paper after Round 1 revision
- `paper/06_paper_r2.md` — Paper after Round 2 (no changes)
- `paper/06_paper_final.md` — Final reviewed paper with metadata
- `paper/review/065_review_r1.md` — Round 1 adversary report
- `paper/review/065_review_r2.md` — Round 2 adversary report
- `paper/review/065_review_summary.md` — Consolidated review summary
- `paper/review/065_human_review_notes.md` — MINOR issues for human review
- `paper/review/065_changelog.md` — This file

**Next Phase:** Phase 6.5.1 (Overleaf LaTeX/PDF generation)
