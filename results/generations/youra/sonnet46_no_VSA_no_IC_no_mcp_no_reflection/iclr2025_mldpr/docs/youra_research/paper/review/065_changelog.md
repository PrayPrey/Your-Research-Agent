# Adversarial Review Changelog
# Phase 6.5 | H-E1 Paper
# Started: 2026-08-31T07:00:00+00:00

---

## Round 1 (R1) Changes

**Source:** 06_paper.md → 06_paper_r1.md  
**Issues Fixed:** 2 MAJOR (MAJOR-001, MAJOR-002)  
**Sections Modified:** Abstract, Introduction, Section 2.1, Section 5.2, Discussion 6.1, Contributions

---

### Fix 1: MAJOR-002 — Overclaim in Section 2.1

**Location:** Section 2.1, paragraph 3 (last sentence of ML Reproducibility Challenges discussion)

**Before:**
> "Our work provides the empirical link that would ground these normative interventions."

**After:**
> "Our work provides the first empirical characterization of *why* this linkage cannot yet be tested with existing APIs — and identifies the infrastructure prerequisites for grounding these normative interventions in evidence."

**Rationale:** The paper reports an infrastructure characterization, not an empirical confirmation of the documentation-reproducibility linkage. The original sentence overclaimed the contribution.

---

### Fix 2: MAJOR-001 — Domain Classification Inconsistency

**Location:** Abstract, Introduction paragraph 4, Section 5.2 domain table, Discussion Finding 1, Contribution C1, C2

**Root cause:** The paper claimed "all 15 HF-found datasets are NLP benchmarks" and "DL vision: 0 found," but the raw `04_validation.md` found list includes `cifar10`, `cifar100`, and `svhn` — image datasets. These datasets are present on HF Hub because they are widely used in NLP-adjacent research and benchmarking. The paper's domain table needed to reflect this nuance.

**Changes made:**

1. **Abstract:** "concentrated in NLP benchmarks" → "concentrated in NLP benchmarks and small-scale image classification benchmarks, with large-scale DL vision, speech, and graph datasets absent"

2. **Introduction paragraph 4 (key finding):** Added clarification that small-scale image benchmarks (CIFAR-10/100, SVHN) are partially present on HF Hub, while large-scale DL vision (ImageNet, COCO) remain absent.

3. **Section 5.2 domain table:** Revised from 5-row simple table to 6-row table distinguishing:
   - NLP/text classification (~10 queried, ~12 found on HF)
   - Small-scale image (MNIST, CIFAR-10/100, SVHN: ~4 queried, ~3 found on HF)
   - Large-scale DL vision (ImageNet, COCO, KITTI, etc.: ~11 queried, 0 found)
   - Speech/audio (~5 queried, 0 found)
   - Graph (~5 queried, 0 found)
   - Classical tabular/UCI (~15 queried, 10 found on OpenML)

4. **Section 5.2 narrative:** Revised "HF Hub returns results only for NLP benchmarks" → "HF Hub returns results primarily for NLP benchmarks and small-scale image classification benchmarks... Large-scale DL vision datasets... return no HF cards."

5. **Contribution C1:** Updated domain bias description to include CIFAR/SVHN partial presence nuance.

6. **Discussion Finding 1:** Revised to accurately describe HF coverage as NLP + small-scale image, with large-scale DL absent.

**Net effect:** The core finding (30% coverage, systematic bias toward founding-community datasets) is unchanged. The description is now more accurate: the bias is specifically against large-scale DL vision/speech/graph datasets, not against all image datasets.

---

## Round 2 (R2) Changes

**Source:** 06_paper_r1.md → 06_paper_r2.md  
**Issues Fixed:** 1 MAJOR (MAJOR-003)  
**Sections Modified:** Section 5.2 domain table, Discussion Finding 1

---

### Fix 3: MAJOR-003 — OpenML Domain Characterization

**Location:** Section 5.2 domain table, Discussion 6.1 Finding 1

**Root cause:** The paper claimed "all OpenML-found are tabular" but raw `04_validation.md` found list includes IMDB, 20newsgroups (NLP), and MNIST (image) with pre-publication OpenML entries. The domain table only credited 1 NLP dataset (IMDB) to the NLP row and assigned all remaining 10 to tabular.

**Changes made:**

1. **Section 5.2 domain table:**
   - NLP/OpenML column: 1 → 2 (IMDB, 20newsgroups)
   - Small-scale image/OpenML column: 0 → 1 (MNIST)
   - Classical tabular/OpenML column: 10 → 8
   (Total still = 11)

2. **Section 5.2 narrative:** Revised "OpenML returns results only for classical tabular datasets" → "predominantly classical tabular datasets, with NLP benchmarks (IMDB, 20newsgroups) and MNIST also present"

3. **Discussion Finding 1:** Revised "22% OpenML coverage consists entirely of classical tabular datasets" → "predominantly classical tabular datasets, with NLP benchmarks and MNIST also present; large-scale DL vision benchmarks absent from both platforms"

**Net effect:** The core finding (22% coverage, large-scale DL vision absent) is unchanged. The characterization of what OpenML does cover is now more accurate: tabular-dominant but including some NLP and image benchmarks.

---

## Final Summary

**Total Revisions Made**: 3 MAJOR fixes across 6+ locations  
**Sections Modified**: Abstract, Introduction, Section 2.1, Section 5.2, Contribution C1, Discussion 6.1  
**Word Count Change**: +~120 words (domain table expanded, clarifications added)

**Review Process:**
- Started: 2026-08-31T07:00:00+00:00
- Completed: 2026-08-31T07:30:00+00:00
- Rounds: 2
- Personas Used: accuracy_checker, bored_reviewer, skeptical_expert

**Files Generated:**
- 06_paper_final.md (final paper, from 06_paper_r2.md)
- 065_review_summary.md (review summary)
- 065_human_review_notes.md (MINOR issues for human review)
- 065_changelog.md (this file)
- 065_review_r1.md (R1 adversary report)
- 065_review_r2.md (R2 adversary report)

**Next Phase:** Phase 6.5.1 (Overleaf LaTeX/PDF generation)
