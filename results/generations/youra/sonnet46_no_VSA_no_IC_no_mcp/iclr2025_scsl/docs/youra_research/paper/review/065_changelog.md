# Adversarial Review Changelog

**Paper**: Pretraining Paradigm Determines Spurious Feature Encoding  
**Started**: 2026-08-26T14:45:00+00:00  

---

## Round 1 Changes (R1 → 06_paper_r1.md)

**Source**: 065_review_r1.md  
**MAJOR issues addressed**: 7 of 7  

### Change 1: d=0.595 → d=0.60 (MAJOR-ACC-001)
- **Section**: Introduction, Contribution 3
- **Before**: `ERM ≈ DINO similarity (d = 0.595, p_bonf = 1.0)`
- **After**: `ERM ≈ DINO similarity (d = 0.60, p_bonf = 1.0)`
- **Reason**: Ground truth and Table 2 both report d=0.60; 0.595 was an inconsistent intermediate value.

### Change 2: Contribution 4 demoted to Preliminary Finding (MAJOR-ENG-001)
- **Section**: Introduction, Contributions list
- **Before**: `4. **Methodological contribution:** Background-replacement augmentation... with full statistical characterization ongoing.`
- **After**: `4. **Preliminary finding:** Background-replacement augmentation... verified as an active causal lever... proof-of-concept result (see Discussion 6.3).`
- **Reason**: Claiming a "contribution" when statistics are pending overstates the finding. Demoted to "Preliminary finding" to accurately reflect PoC-level status.

### Change 3: Abstract scope made explicit (MAJOR-SKE-002)
- **Section**: Abstract, sentence 3
- **Before**: `supervised ERM encodes spurious background features *more* strongly than contrastive MoCo-v3 on Waterbirds`
- **After**: `supervised ERM encodes spurious background features *more* strongly than contrastive MoCo-v3 on frozen ResNet-50 representations`
- **Reason**: Scope (ResNet-50) not explicit in Abstract — added to avoid overgeneralization.

### Change 4: "explicit class labels" precision in Abstract (MAJOR-SKE-002 adjacent)
- **Section**: Abstract
- **Before**: `while self-distillation (DINO) matches ERM despite using no explicit labels`
- **After**: `while self-distillation (DINO) matches ERM despite using no explicit class labels`
- **Reason**: Precision — DINO uses soft labels via momentum teacher; "explicit class labels" is accurate.

### Change 5: CelebA p-value disambiguation (MAJOR-ACC-003)
- **Section**: Results 5.2
- **Before**: `ERM vs MoCo-v3 on CelebA: p_bonf = 0.120, d = 1.83 — not significant.`
- **After**: Added note distinguishing pairwise Bonferroni (p_bonf=0.120, d=1.83) from directional test (p=0.917, d=0.068).
- **Reason**: Ground truth contained both values from different tests; paper only reported one; added clarification.

### Change 6: "first" → "to the best of our knowledge, first" (MAJOR-ENG-002)
- **Sections**: Introduction (gap paragraph), Related Work (Our position)
- **Before**: `the first controlled 4-paradigm comparison`
- **After**: `to the best of our knowledge, the first controlled 4-paradigm comparison`
- **Reason**: Izmailov et al. [2022] citation is unverified; softened novelty claim appropriately.

### Change 7: ERM≈DINO mechanistic claim softened (MAJOR-SKE-001)
- **Sections**: Results 5.1 and Discussion 6.1
- **Before**: `This is consistent with DINO's momentum teacher generating class-correlated soft-targets...`
- **After**: `This is most parsimoniously explained by DINO's momentum teacher... but alternative explanations exist... Testing via mutual information is an important future experiment.`
- **Reason**: ERM≈DINO supports but does not prove the mechanism; alternative explanations not eliminated.

### Change 8: Izmailov citation corrected (MAJOR-SKE-003)
- **Section**: References
- **Before**: `Izmailov, P. et al. (2022). Feature Learning in Infinite-Width Neural Networks. [UNVERIFIED]`
- **After**: `Izmailov, P. et al. (2022). On Feature Learning in the Presence of Spurious Correlations. NeurIPS 2022. [citation unverified — verify before submission]`
- **Reason**: Original title was almost certainly the wrong paper; corrected to most likely correct title per author list and year.

---

---

## Round 2 Changes (R2 → 06_paper_r2.md)

**Source**: 065_review_r2.md  
**MAJOR issues addressed**: 0 (none found)  
**MINOR notes added to human_review_notes**: 3  

### Change 9: Cohen's d formula made explicit (MINOR-R2-003)
- **Section**: Methodology 3.4
- **Before**: `Cohen's d with pooled standard deviation measures effect size.`
- **After**: Added explicit formula `d = (μ₁ − μ₂)/s_pooled, s_pooled = √((s₁² + s₂²)/2)` to eliminate any ambiguity.
- **Reason**: R2 plausibility check found slight discrepancy between reported d and back-calculation; explicit formula resolves interpretation ambiguity.

---

## Final Summary

**Total Revisions Made**: 9  
**Sections Modified**: Abstract, Introduction, Methodology (3.4), Results (5.1, 5.2), Discussion (6.1), References  
**Word Count Change**: ~4975 → ~5025 (+50 words net)  

**Review Process**:
- Started: 2026-08-26T14:45:00+00:00
- Completed: 2026-08-26T15:30:00+00:00
- Rounds: 2 (R1 + R2)
- Personas Used: accuracy_checker, bored_reviewer, skeptical_expert

**Files Generated**:
- 06_paper_r1.md (R1 revised paper)
- 06_paper_r2.md (R2 revised paper — final)
- 06_paper_final.md (copy of R2, final paper)
- 065_review_r1.md (Round 1 adversary report)
- 065_review_r2.md (Round 2 adversary report)
- 065_review_summary.md (consolidated review report)
- 065_human_review_notes.md (MINOR issues for human review)
- 065_changelog.md (this file)

**Next Phase**: Phase 6.5.1 (Overleaf LaTeX/PDF generation)

## Word Count Delta (R1)

- **Original**: ~4975 words
- **After R1**: ~5020 words (+45 words, net additions from clarifications)
- **Sections modified**: Abstract, Introduction (Contributions), Results (5.1, 5.2), Discussion (6.1), References
