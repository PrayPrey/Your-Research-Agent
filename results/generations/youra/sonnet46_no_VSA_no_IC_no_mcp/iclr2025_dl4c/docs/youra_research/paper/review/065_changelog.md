# Adversarial Review Changelog
# Phase 6.5 — 2026-08-26

---

## Round 1 Changes (06_paper.md → 06_paper_r1.md)

**Issues Addressed: 4 MAJOR**

### MAJOR-AC-001 Fixed: Table 1 Proxy Value Standardization
- **Before**: Table 1 used inconsistent ranges "~0.52–0.58 (proxy)" and point estimates mixed
- **After**: All proxy rows standardized to single point estimates with "(proxy, N=50)" notation; removed ambiguous ranges
- **Sections**: §5.1, Table 1

### MAJOR-AC-002 Fixed: RLEF Checkpoint-Not-Saved Disclosure
- **Before**: Abstract and §5.2 presented Δ=+0.18 without prominent disclosure that RLEF checkpoint was lost after training
- **After**:
  - Abstract: Added "proxy from smoke-scale evaluation" qualifier to Δ=+0.18
  - §5.2: Added "(proxy from smoke-scale, N=50; checkpoint evaluated immediately post-training — see Note)" to Table 2 header
  - Table 2: Added explicit note "RLEF checkpoint not saved after 62 GRPO steps"
  - Contributions list §1: Added "proxy from smoke-scale evaluation" qualifier
- **Sections**: Abstract, §1, §5.2, Table 2

### MAJOR-BR-001 Fixed: Duplicate Figure Reference Removed
- **Before**: Figure count = 11; Figures 1 and 10 both listed as "apps_difficulty_loss.png" (same file)
- **After**: Figure count = 10; Figure 10 changed to "fig1_nonzero_fraction_bar.png" (h-m2 monitoring artifact figure — distinct content)
- **Sections**: Paper Statistics block, figure metadata

### MAJOR-SE-001 Fixed: Mechanistic Claims Softened
- **Before**: §1 para 2, §5.4, §7 stated mechanism as established fact ("SFT…cannot transfer…RLEF…naturally operates")
- **After**:
  - Abstract: Added "though the precise mechanism remains under investigation"
  - §1 para 2: Added parenthetical "(the precise mechanism remains under investigation; see §6.2, L2)"
  - §1 contribution 4: Changed to "suggesting (pending mechanism verification) a reframing"
  - §5.4: Changed "cannot transfer" to "fails to transfer…consistent with generalization difficulty, though not a direct measurement of it"
  - §6.1: Added "We emphasize this is a hypothesis suggested by our data, not a mechanism we have directly measured"
  - §7: Added "— though directly confirming the precise mechanism awaits future experimentation (§6.2, L2)"
- **Sections**: Abstract, §1, §5.4, §6.1, §7

---

## Round 2 Changes (06_paper_r1.md → 06_paper_r2.md)

**Issues Addressed: 1 MAJOR**

### MAJOR-R2-001 Fixed: Table 1 SFT Absolute Values Corrected
- **Root Cause**: R1 revision derived Table 1 SFT values by approximation rather than reading Phase 4 source data
- **Actual Phase 4 source**: h-m4/04_validation.md, Track 1 table
- **Before** (incorrect):
  - HumanEval SFT: 0.55
  - MBPP SFT: 0.52
  - LCB-Easy SFT: 0.08
  - LCB-Medium SFT: 0.02
- **After** (correct, from Phase 4):
  - HumanEval SFT: 0.58
  - MBPP SFT: 0.24
  - LCB-Easy SFT: 0.18
  - LCB-Medium SFT: 0.20
  - LCB-Hard SFT: 0.0 (unchanged — confirmed)
- **Verification**: SFT values now internally consistent with Table 2 Δ values (e.g., MBPP: SFT=0.24, RLEF=0.40, Δ=+0.16 ✓)

### Table 2 Enhancement
- **Before**: Table 2 showed only Δ column
- **After**: Table 2 expanded to 5 columns (Benchmark, Difficulty, SFT pass@1, RLEF pass@1, Δ) for full transparency and internal consistency verification by readers
- **Sections**: §5.2, Table 2

---

## Final Summary

**Total Revisions Made**: 5 MAJOR issues × multiple edit points ≈ 15 specific text changes

**Sections Modified**:
- Abstract: 2 qualifiers added
- §1 Introduction: 3 locations softened/qualified
- §5.1 Results: Table 1 values corrected
- §5.2 Results: Table 2 expanded, disclosure added
- §5.4 Results: Mechanistic language softened
- §6.1 Discussion: Hypothesis-vs-measurement distinction added
- §7 Conclusion: Mechanism caveat added
- Paper Statistics: Figure count 11→10, Figure 10 file corrected

**Word Count**: 6455 (original) → ~6575 (final, ~+120 words from qualifiers and expanded table)

**Figure Count**: 11 (original) → 10 (final, duplicate removed)

**Review Process**:
- Started: 2026-08-26
- Completed: 2026-08-26
- Rounds: 2 (R1: structural + engagement; R2: numerical verification)
- Personas Used: Accuracy Checker, Bored Reviewer, Skeptical Expert

**Files Generated**:
- 06_paper_r1.md (R1 revision)
- 06_paper_r2.md (R2 revision)
- 06_paper_final.md (final paper, copy of R2)
- paper/review/065_review_r1.md (R1 adversarial review)
- paper/review/065_review_r2.md (R2 numerical verification)
- paper/review/065_review_summary.md (consolidated summary)
- paper/review/065_human_review_notes.md (MINOR issues for human review)
- paper/review/065_changelog.md (this file)
- paper/review/065_review_checkpoint.yaml (review state)

**Next Phase**: Phase 6.5.1 (Overleaf LaTeX/PDF generation)
