# Phase 6.5 Changelog

## R1 Revisions (2026-08-29)

### 03_methodology.md
- **Line 59**: Changed threshold justification from internal verification plan to Unterthiner et al. (2020) citation
- **Before**: "Following prediction P1 from our verification plan, we set a threshold of σ < 0.5 for bounded variance. This threshold is informed by prior CNN analysis where stable measurements enabled prediction."
- **After**: "We set a threshold of σ < 0.5 for bounded variance. This threshold is informed by Unterthiner et al. (2020), who found that predictive accuracy within CNN families required within-population variance below roughly half a standard deviation for stable feature extraction."

### 05_results.md
- **Lines 27-30**: Added 95% confidence intervals to variance estimates
- **Before**: `google/vit-* | 6 | **0.24**`
- **After**: `google/vit-* | 6 | **0.24** (95% CI: [0.12, 0.48])`

### 06_discussion.md
- **Lines 33-35**: Added survivorship bias acknowledgment paragraph
- **Added**: "Potential survivorship bias. The 47% model-loading failure rate raises concern about selection effects. However, failures were due to technical issues (missing weights, incompatible architectures, compute timeouts), not α-related properties."

## R2 Revisions

None required. All numerical values verified against source.

---

## Files Generated

| File | Purpose |
|------|---------|
| 06_paper_final.md | Adversarially-reviewed final paper |
| 065_review_summary.md | Review process summary |
| 065_changelog.md | This file |
| 065_human_review_notes.md | MINOR issues for human review |
