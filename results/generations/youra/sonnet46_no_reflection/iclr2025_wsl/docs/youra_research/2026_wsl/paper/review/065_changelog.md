# Phase 6.5 Adversarial Review Changelog

## Round 1 Revisions

**Date:** 2026-05-21
**Issues Addressed:** 2 FATAL, 4 MAJOR
**Sections Modified:** Abstract, Section 1 (Introduction), Section 2.3, Section 4, Section 5.3, Section 6.1, Section 6.2, Section 7, Figure Captions

---

### FATAL-1: "43-point gap persistent across all current methods" — unsupported universal claim

**Location:** Introduction, paragraph 1

**Before:**
> "This 43-point performance gap, persistent across all current weight space learning methods, is the puzzle we resolve."

**After:**
> "This 43-point performance gap, observed in our evaluation of permutation-equivariant methods applied cross-architecture (see Section 5), is the puzzle we resolve."

**Rationale:** The original phrasing made a universal empirical claim ("all current methods") without a supporting citation or table. No meta-analysis or survey table is available in this paper to substantiate the universal scope. The fix scopes the claim to "our evaluation" and directs readers to Section 5, where the H-M2 evidence lives. This preserves the quantitative hook while eliminating the unsupported universal claim that would trigger desk-rejection from a skeptical reviewer.

---

### FATAL-2: "Explains why" — mechanistic overclaim in Abstract and Section 6.2

**Location (a):** Abstract, sentence beginning "This bimodal stratification..."

**Before:**
> "This bimodal stratification explains why permutation equivariant methods achieve τ > 0.93 within CNN Zoo but fail cross-architecture..."

**After:**
> "This bimodal stratification is consistent with why permutation equivariant methods achieve τ > 0.93 within CNN Zoo but struggle cross-architecture..."

**Location (b):** Section 6.2

**Before:**
> "NFN's CNN Zoo success (τ > 0.93) is directly explained by the Conv2d ratio of 0.637: permutation equivariance captures the dominant variation in CNN-Zoo-specific layers."

**After:**
> "NFN's CNN Zoo success (τ > 0.93) is consistent with the Conv2d ratio of 0.637: permutation equivariance captures the dominant variation in CNN-Zoo-specific convolutional layers."

**Rationale:** H-M3 was never run, so no causal mechanism between variance ratio and τ has been empirically tested. "Explains why" implies a causal mechanism that has been verified, which is overclaiming. "Is consistent with" accurately conveys correlation without asserting causation. Also removed "directly" from Section 6.2 to further moderate the strength of the mechanistic claim.

---

### MAJOR-1: Phase 5 baseline comparison skipped — not disclosed

**Location:** Added to Section 4 (Experimental Setup), new final paragraph

**Before:** No disclosure of Phase 5 skip anywhere in the paper.

**After:** Added paragraph:
> "**Note on baseline τ comparison.** Formal Phase 5 cross-architecture τ comparison against published NFN/SANE baseline values was not conducted in this work (H-M3 was blocked by the H-M2 FAIL gate; see Section 5.4). The paper's contribution is mechanistic — variance stratification explaining the structural source of the transfer gap — rather than performance-competitive (a τ improvement demonstration). Cross-architecture τ quantification remains future work."

**Rationale:** Reviewers familiar with the pipeline or with WSL benchmarks may expect a head-to-head τ comparison. Without this disclosure, the paper implies completeness of the evaluation chain. The added sentence correctly frames the paper's contribution as mechanistic and prevents reviewer surprise.

---

### MAJOR-2: "Linear/attention" attribution scope — 6.6× figure from CNN Zoo Linear only

**Locations:** Introduction (Section 1), Section 6.1, Section 6.2, Section 7, Figure 1 caption

**Before (Section 1):**
> "...but only 13.3% for Linear/attention layers, where GL-orbit variance dominates by a factor of 6.6×."

**After (Section 1):**
> "...but only 13.3% for Linear (FC) layers in CNN Zoo, where GL-orbit variance dominates by a factor of 6.6×."

**Before (Section 1, contribution bullet):**
> "GL variance dominates Linear/attention (ratio = 0.133)"

**After:**
> "GL variance dominates Linear (FC) layers in CNN Zoo (ratio = 0.133)"

**Before (Section 5.3 discussion):**
> "This explains NFN's CNN Zoo success... while cross-architecture transfer fails (Linear/attention dominant in transformers, ratio = 0.133)."

**After:**
> "This provides an empirical basis for understanding NFN's CNN Zoo success... while cross-architecture transfer fails (Linear layers GL-dominant in CNN Zoo at ratio = 0.133; Transformer Zoo attention variance not directly measured — see L3 in Section 6.4)."

**Before (Section 6.1):**
> "The 6.6× GL dominance for Linear/attention..." [implicit in discussion]

**After (Section 6.1):**
> "The 6.6× GL dominance for Linear (FC) layers in CNN Zoo (derived from Table 4: 223.52/33.84 ≈ 6.6) is consistent with the theoretical expectations from prior work. Whether this ratio extends to attention layers in Transformer Zoo is an open measurement question (see L3, Section 6.4)."

**Rationale:** H-M2 only measured CNN Zoo, which contains Conv2d and Linear (FC) layers. Transformer Zoo attention layer variance was not measured (L3 limitation). Conflating "Linear/FC" with "Linear/attention" implies the 6.6× measurement covers attention layers, which it does not. All instances of "Linear/attention" where the figure refers to the CNN Zoo measurement have been scoped to "Linear (FC) layers in CNN Zoo."

---

### MAJOR-3: arXiv:2410.04207 vs 2410.04209 citation ambiguity

**Location:** Section 2.3

**Before:**
> "arXiv:2410.04209 [Tran-Viet et al., 2024] proposes GL-invariant polynomial trace features..."

The original Section 6.2 (in the draft under review) referenced "arXiv:2410.04207" as a distinct work for GL trace features, while Section 2.1 and 2.3 used "arXiv:2410.04209" for Transformer-NFN. The review flagged this as a potential companion-paper aliasing issue.

**After (Section 2.3):**
> "Transformer-NFN [Tran-Viet et al., 2024] (arXiv:2410.04209) proposes GL-invariant polynomial trace features (tr(WW^T) and tr(W^Q W^{K,T})) for attention weights..."

**Rationale:** The paper now cites only arXiv:2410.04209 (Transformer-NFN) for the GL trace features, consolidating to a single canonical reference. The ambiguous arXiv:2410.04207 alias is eliminated. If these prove to be distinct companion papers upon author verification, the reference entry should be split and differentiated before final submission.

---

### MAJOR-4: Section 4 (Experimental Setup) was a redundant engagement cliff

**Location:** Section 4

**Before:** Three sub-sections — §4.1 with Q1/Q2/Q3 narrative restating §3, §4.2 with dataset descriptions, §4.3 with a metric table, §4.4 with implementation notes. ~400 words of mostly redundant content.

**After:** Single-section format with four short paragraphs — dataset bullet list, metrics table (retained), implementation details (retained), and the new baseline-skip disclosure paragraph. Removed the Q1/Q2/Q3 sub-section headers and the narrative restatement of Section 3 questions. All unique content (checkpoint counts per hypothesis, metric thresholds, seed protocol, code paths) is preserved.

**Rationale:** The original §4.1 asked "Q1 (H-E1): Is the input/output channel permutation group a functionally exact symmetry..." — verbatim content already covered in §3.1 and §1. A bored reviewer encountering this after the compelling Introduction would disengage. The revised Section 4 is ~40% shorter with no information loss, improving engagement flow.

---

## Issues Not Fixed

None — all 2 FATAL and 4 MAJOR issues have been addressed. MINOR issues (1–6) are collected in `065_human_review_notes.md` for human review.

---

## Statistics

- **issues_addressed:** 6 (2 FATAL + 4 MAJOR)
- **issues_deferred:** 6 MINOR (collected in human review notes)
- **sections_modified:** Abstract, §1, §2.3, §4, §5.3, §6.1, §6.2, §7, Figure Captions
- **word_count_delta:** approx −120 words (§4 collapse −180, additions +60 for disclosures and scoping language)
- **numerical_values_changed:** 0 (no data values were altered)

---

## Round 2 Revisions

**Date:** 2026-05-21
**Issues Addressed:** 0 FATAL, 2 MAJOR
**Sections Modified:** §5.2 (Table 3), §6.3, §7, Figure Captions (Figure 7)

---

### MAJOR-R2-1: MHA Overhead Discrepancy

**Location:** Table 3 (§5.2), §7 Conclusion, Figure 7 caption

**Issue:** The R1 paper reported MultiheadAttention overhead as 1.147× in Table 3, §7, and
Figure 7 caption. The h-m1/04_validation.md Per-Layer Overhead table shows the actual measured
value as 1.1264. Per task instructions, the validation file is the primary source. The ground
truth yaml lists 1.147 with "source: h-m1/04_validation.md," which appears to be a transcription
error in the ground truth file.

**Resolution:** Updated all instances of MHA overhead from 1.147× to 1.126× (1.1264 rounded
to 3 decimal places, consistent with rounding convention used for Conv2d/Linear values).

**Before (Table 3):**
> MultiheadAttention | 1.147×

**After (Table 3):**
> MultiheadAttention | 1.126×

**Before (§7):**
> "...consistent across Conv2d (1.168×), Linear (1.168×), and MultiheadAttention (1.147×)."

**After (§7):**
> "...consistent across Conv2d (1.168×), Linear (1.168×), and MultiheadAttention (1.126×)."

**Before (Figure 7 caption):**
> "...Conv2d (1.168×), Linear (1.168×), MultiheadAttention (1.147×)."

**After (Figure 7 caption):**
> "...Conv2d (1.168×), Linear (1.168×), MultiheadAttention (1.126×)."

**MHA overhead final value used:** 1.126× (from h-m1/04_validation.md: 1.1264, rounded to 3 d.p.)

---

### MAJOR-R2-2: §6.3 Linear/Attention Qualifier

**Location:** Section 6.3 (Implications for Cross-Architecture Design)

**Issue:** Section 6.3 described the hybrid encoding using "GL-invariant trace features
(tr(WW^T), tr(W^Q W^{K,T})) for Linear/attention" without noting that the attention layer
extension is inferred rather than measured. The §6.4 L3 limitation covers this globally, but
§6.3 alone gave no in-line qualifier, potentially misleading readers who do not read §6.4.

**Fix:** Added parenthetical clarification after "Linear/attention":

**Before:**
> "...GL-invariant trace features (tr(WW^T), tr(W^Q W^{K,T})) for Linear/attention — is the
> pre-specified pivot from H-M2, not post-hoc rationalization."

**After:**
> "...GL-invariant trace features (tr(WW^T), tr(W^Q W^{K,T})) for Linear/attention (where
> attention layers follow by inference from Linear layer GL dominance; direct Transformer Zoo
> measurement not conducted — see L3, Section 6.4) — is the pre-specified pivot from H-M2,
> not post-hoc rationalization."

---

## Round 2 Statistics

- **issues_addressed:** 2 MAJOR (MAJOR-R2-1 and MAJOR-R2-2)
- **sections_modified:** §5.2 (Table 3), §6.3, §7, Figure Captions (Figure 7)
- **new_human_review_notes:** 5 (MINOR-R2-1 through MINOR-R2-5)
- **numerical_values_changed:** 1 (MHA overhead: 1.147× → 1.126×)
- **remaining_fatal:** 0
- **remaining_major:** 0

---

## Final Summary (v2.0)

**Total Revisions Made:** 8 (2 FATAL + 6 MAJOR)
**Sections Modified:** Abstract, §1, §2.3, §4, §5.2, §5.3, §6.1, §6.2, §6.3, §7, Fig 7 caption
**Human Review Notes:** 11 MINOR issues (not auto-fixed)

**Review Process:**
- Started: 2026-05-21T06:45:00Z
- Completed: 2026-05-21T07:45:00Z
- Rounds: 2 (R1 + R2)
- Personas Used: accuracy_checker, bored_reviewer, skeptical_expert

**Files Generated:**
- 06_paper_final.md (final paper, based on 06_paper_r2.md)
- 065_review_summary.md (review summary)
- 065_human_review_notes.md (11 MINOR issues for human review)
- 065_changelog.md (this file)

**Next Phase:** Phase 6.5.1 (Overleaf LaTeX/PDF generation)
