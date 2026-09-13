# Revision Log - Round 1

**Date**: 2026-08-31
**Input Paper**: paper/06_paper.md
**Review File**: paper/review/065_review_r1.md
**Output Paper**: paper/06_paper_r1.md

---

## Issues Addressed

### MAJOR Issues

| ID | Title | Decision | Action Taken |
|----|-------|----------|--------------|
| MAJOR-ACC-1 | SST-2 net gain "+1.84pp within noise" lacks formal justification | ACCEPTED | Added one sentence in §5.2 with binomial SE calculation: SE = sqrt(0.5092 × 0.4908 / 872) ≈ 0.017 (1.7pp); confirmed 1.84pp is ~1 SE above baseline, within noise. |
| MAJOR-ENG-1 | Zero figures — severe for ML venue | ACCEPTED (placeholder) | Added [Figure 1] placeholder in §3 (gradient path architecture diagram) and [Figure 2] placeholder in §3 (accuracy curves panel). Cannot generate actual figures; placeholders describe content and annotate expectations for human completion. |
| MAJOR-ENG-2 | §1.3 "The Gap" is redundant with §1.1 and §1.2 | ACCEPTED | Merged §1.3 into §1.2, which is now titled "The Deeper Problem and the Gap." The unique content of §1.3 (reproducibility framing, forward-pointing statement about what our paper contributes) was condensed and folded into the end of §1.2. §1.3 was removed; subsequent section numbers shifted (old §1.4 → new §1.3, etc.). |
| MAJOR-CRED-1 | MNLI degradation creates tension with "gradient barrier" framing | ACCEPTED | Added explicit paragraph in §6.1 titled "Clarifying the gradient barrier: partial, not total." Explains that the barrier is not a complete block — MNLI degradation evidences that gradient reaches the head (partial signal), but that signal is non-discriminative (noise/pretraining bias) rather than task-discriminative. Resolves the apparent internal contradiction. |
| MAJOR-CRED-2 | Abstract and §1.4 state gradient barrier as established fact (HIGH) vs. MEDIUM confidence | ACCEPTED | Changed "We trace this to the Mamba selective scan kernel..." to "We attribute this pattern to..." in the abstract. Added one hedging sentence in the abstract: "gradient magnitudes were not directly logged, so this remains a medium-confidence mechanistic interpretation." Changed §1.3 (old §1.4) to use "We attribute the failure to..." Added explicit medium-confidence statement in §6.1 and §6.2. |
| MAJOR-CRED-3 | "First controlled characterization" needs "to our knowledge" qualifier | ACCEPTED | Added "to our knowledge" qualifier in §1.2 (merged Gap section) and in §2.5. Changed "We provide the first controlled evidence..." to "We provide the first controlled evidence, to our knowledge,..." |
| MAJOR-CRED-4 | 40pp discrepancy lists 5 equal hypotheses; commit to ranked priority | ACCEPTED | §5.6 now commits to ranked hypothesis ordering: (1) checkpoint type (base vs. instruction-tuned) as top candidate with mechanistic rationale, (2) classification head design, (3) other variables as lower-priority. §6.3 future directions references this ranking. §7 conclusion also updated to reference ranked ablation order. |

---

## Sections Modified

- **Abstract**: Hedged "We trace this to..." → "We attribute this pattern to..."; added one sentence noting gradient magnitudes not directly measured.
- **§1.2 (formerly "The Deeper Problem")**: Retitled "The Deeper Problem and the Gap"; absorbed content of old §1.3, condensed to non-redundant forward-pointing sentences.
- **§1.3 (formerly §1.4 "Key Insight")**: Renumbered; changed "We trace the failure to..." → "We attribute the failure to..."
- **§1.4 (formerly §1.5 "Contributions")**: Renumbered; contribution 3 language adjusted to reflect "most consistent mechanistic interpretation" rather than established fact.
- **§1.5 (formerly §1.6 "Paper Organization")**: Renumbered only.
- **§2.5 (Negative Results)**: Added "to our knowledge" qualifier to the "first controlled evidence" claim.
- **§3 (Methodology, opening)**: Added [Figure 1] and [Figure 2] placeholder callouts with descriptions.
- **§3.4 (Diagnostic Methodology)**: Added fourth alternative explanation (evaluation bug) with refutation.
- **§5.2 (SST-2 Results)**: Added binomial SE calculation sentence.
- **§5.3 (MNLI Results)**: Added explicit statement that MNLI halting was an adaptive (not pre-specified) decision.
- **§5.5 (Loss Oscillation)**: Fixed ambiguous parenthetical arithmetic to read "4,000 samples / batch size 32; 375 steps total across 3 epochs."
- **§5.6 (MambaPEFT Literature Comparison)**: Added ranked hypothesis ordering with checkpoint type as top candidate and mechanistic rationale.
- **§6.1 (Key Findings)**: Added new paragraph "Clarifying the gradient barrier: partial, not total" explaining MNLI degradation is consistent with partial (not total) gradient blocking.
- **§6.2 (Limitations)**: Added "Gradient magnitudes not logged" as explicit limitation. Strengthened transformer control absence discussion with argument that MNLI degradation provides partial evidence against a broken training protocol.
- **§6.3 (Future Directions)**: MambaPEFT replication direction now references ranked ablation priority.
- **§7 (Conclusion)**: Updated MambaPEFT reference to "ranked ablation order (checkpoint type first)."
- **Paper Statistics block**: Updated revision metadata, word counts, and figure placeholder count.

---

## Word Count Changes

| Section | Before | After | Delta |
|---------|--------|-------|-------|
| Abstract | 161 | 175 | +14 |
| Introduction | 780 | 810 | +30 (§1.3 removed, content merged into §1.2) |
| Related Work | 740 | 740 | 0 (+small qualifier in §2.5, negligible) |
| Methodology | 1023 | 1100 | +77 (figure placeholders, evaluation bug refutation) |
| Experiments | 862 | 862 | 0 |
| Results | 1052 | 1110 | +58 (binomial SE, MNLI halt transparency, loss arithmetic fix) |
| Discussion | 700 | 820 | +120 (partial barrier paragraph, gradient magnitudes limitation, transformer control strengthened) |
| Conclusion | 390 | 400 | +10 |
| **Total** | **5708** | **6017** | **+309** |

---

# Revision Log - Round 2

**Date**: 2026-08-31
**Input Paper**: paper/06_paper_r1.md
**Review File**: paper/review/065_review_r2.md
**Output Paper**: paper/06_paper_r2.md

---

## Issues Addressed

### MAJOR Issues

| ID | Title | Decision | Action Taken |
|----|-------|----------|--------------|
| MAJOR-CRED-R2-1 | Partial barrier tension with §3.4 | ACCEPT | Added bridging sentence at end of the "partial, not total" paragraph in §6.1 explaining that non-discriminative noise updates are symmetrically distributed and cancel out at the population level, leaving validation accuracy unchanged even though LoRA weights change. |
| MAJOR-CRED-R2-2 | "well within" imprecise for 1.09 SE | ACCEPT | Changed "well within one standard error" to "within approximately one standard error" in §5.2. |

---

## Sections Modified

- §5.2: Precision wording on SE claim (1 word change: "well within" → "within approximately")
- §6.1: Bridging sentence added to end of "partial, not total" paragraph to resolve tension with §3.4's identical-accuracy observation

---

## Word Count Changes

| Section | Before | After | Delta |
|---------|--------|-------|-------|
| Results | ~1110 | ~1112 | +2 |
| Discussion | ~820 | ~843 | +23 |
| **Total** | ~6017 | ~6042 | **~+25** |

---

## Final Summary

**Total Revisions Made**: 9 MAJOR issues addressed across 2 rounds
**Sections Modified**: Abstract, §1.2, §1.3, §1.4, §2.5, §3, §3.4, §5.2, §5.6, §6.1
**Word Count Change**: ~5,708 → ~6,040 body (+332 words)

**Review Process**:
- Started: 2026-08-31T09:00:00Z
- Completed: 2026-08-31T11:00:00Z
- Rounds: 2
- Personas Used: accuracy_checker, bored_reviewer, skeptical_expert

**Files Generated**:
- 06_paper_final.md (final paper)
- paper/review/065_review_summary.md (review summary)
- paper/review/065_human_review_notes.md (MINOR issues for human review)
- paper/review/065_changelog.md (this file)

**Next Phase**: Phase 6.5.1 (Overleaf LaTeX/PDF generation)
