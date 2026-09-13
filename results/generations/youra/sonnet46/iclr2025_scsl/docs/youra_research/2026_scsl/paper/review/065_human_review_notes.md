# Phase 6.5 Human Review Notes — Round 1

**Paper:** 06_paper_r1.md (revised)
**Date:** 2026-03-16
**Source review:** 065_review_r1.md

These are MINOR issues identified by the adversary agent (Personas 1–3) that were NOT auto-fixed in Round 1. Each item requires human judgment before submission.

---

## MINOR-1 (Grammar/Style): Ratio Range Notation in Contribution 1

**Location:** Section 1, Contribution 1: "ratio 6.5x–8.8x"

**Issue:** The notation "ratio 6.5x–8.8x" could imply a monotone increase from 6.5x to 8.8x. However, Table 2 shows: epoch 1 = 6.513, epoch 3 = 7.493, epoch 5 = 8.805, epoch 10 = 8.509. The ratio at epoch 10 (8.509) is *below* the epoch 5 peak (8.805), meaning the range notation slightly misrepresents the trajectory (it peaked at 8.8x then slightly declined to 8.5x — still within range but not a simple monotone ascent to 8.8x).

**Options for human reviewer:**
1. Leave as-is — "6.5x–8.8x" is technically accurate as the observed range of values.
2. Change to "ratio 6.5x–8.8x (peaking at epoch 5, stable through epoch 10)" for precision.
3. Add a clarifying note near Table 2: "range denotes minimum-to-peak across epochs 1–10; epoch 10 = 8.5x."

**Severity:** Style only. Does not affect scientific validity.

---

## MINOR-2 (Formatting): Kirichenko et al. Citation Year Inconsistency

**Location:** References section: `[Kirichenko et al., 2022]` cites the paper as "ICLR 2023" but the citation key uses year 2022 (the preprint year).

**Issue:** The in-text citations use `[Kirichenko et al., 2022]` but the reference entry lists venue as ICLR 2023. This is a year inconsistency: either the citation key should be `[Kirichenko et al., 2023]` (publication year) or the reference should note both years (2022 preprint, 2023 publication).

**Options for human reviewer:**
1. Change in-text citations to `[Kirichenko et al., 2023]` and update reference accordingly.
2. Keep `[Kirichenko et al., 2022]` and add "(preprint 2022, published ICLR 2023)" to reference entry.
3. Check actual arxiv/ICLR publication dates and use the convention of the target venue.

**Severity:** Formatting only. Consistent with common practice of citing preprint year; human reviewer should align with target venue citation style.

---

## MINOR-3 (Clarity): "Pseudo-Balanced" Terminology in Section 3.3

**Location:** Section 3.3, title "Pseudo-Minority Subset Construction" and body: the subset is constructed by combining S_min ∪ S_maj and called a "balanced subset."

**Issue:** The subset S = S_min ∪ S_maj is called "balanced" in the Section 3.3 body but Section 5.2 extensively demonstrates that it is NOT class-balanced (balance_deviation = 0.379). The terminology "pseudo-balanced" (from the original paper) and "minority-enriched subset" are used in different places. The section title was updated to "Pseudo-Minority Subset Construction" in R1 but the body still refers to "S = S_min ∪ S_maj" as a "balanced subset."

**Options for human reviewer:**
1. Replace all instances of "balanced subset" in Section 3.3 body with "minority-enriched subset" for consistency.
2. Use "pseudo-balanced" throughout (acknowledges the intent even if class balance is not achieved).
3. Introduce precise terminology: "minority-enriched subset (hereafter pseudo-balanced subset)" at first use.

**Severity:** Clarity. Minor risk of reviewer confusion given the paper's explicit discussion of balance failure.

---

## MINOR-4 (Style): Colloquial Conclusion Sentence

**Location:** Section 7, Conclusion: "The signal was there in the gradient norms of every training run."

**Issue:** This sentence (simplified from the original "The signal was always there — in the gradient norms of every training run") is colloquial for an academic paper. While evocative, some reviewers may flag it as informal.

**Options for human reviewer:**
1. Remove or replace with a more formal equivalent: "The gradient norm signal is present in every standard ERM training run, requiring no additional computation or experimental infrastructure to access."
2. Retain — the colloquial tone may be appropriate for some venues (e.g., NeurIPS, which often accepts expressive writing in conclusions).
3. Keep as a penultimate sentence and follow with a formal closing statement.

**Severity:** Style preference. No scientific validity impact.

---

## MINOR-5 (Terminology): "Criterion Design Flaw" vs. "Criterion Design Lesson"

**Location:** Section 1 Contribution 4: "Identification of a criterion design flaw" vs. Section 6.1 Finding 2: "criterion design lesson" vs. the phrase "criterion design insight" appears in various places.

**Issue:** Three different terms are used for the same concept: "flaw," "lesson," and "insight." This inconsistency could create the impression of imprecision. The R1 revision did not address this (MINOR only).

**Options for human reviewer:**
1. Standardize to "criterion design lesson" (most neutral — acknowledges learning without being self-critical).
2. Standardize to "criterion design insight" (more positive framing).
3. Use "criterion design error" in Contribution 4 (most transparent) and "criterion design lesson" in Discussion.

**Severity:** Style/consistency. Human reviewer should choose a single consistent term before final submission.

---

## MINOR-6 (Appendix): PyTorch Version Verification

**Location:** Appendix C: "PyTorch 2.10+cu128, Python 3.10"

**Issue:** PyTorch 2.10 with CUDA 12.8 support (+cu128) represents a future or bleeding-edge version as of typical 2025–2026 timelines. The exact version string should be verified against the actual environment used in the experiment. An incorrect version number in the reproducibility checklist undermines reproducibility claims.

**Action required for human reviewer:**
1. Run `python -c "import torch; print(torch.__version__)"` in the experiment environment.
2. Confirm the exact version string and update Appendix C to match.
3. If PyTorch 2.10 is correct, no change needed. If the actual version differs, update accordingly.

**Severity:** Factual accuracy of appendix. Does not affect results but important for reproducibility claims.

---

## MINOR-7 (Meta): Pipeline Attribution Markers

**Location:**
- YAML header: `generated_by: "Anonymous Research Pipeline v2.0 — Phase 6"`
- Footer: `*Generated by Anonymous Research Pipeline v2.0 — Phase 6 Paper Writing*`
- Footer: `*Citation verification: 7/13 verified via Semantic Scholar MCP*`

**Issue:** These pipeline attribution markers must be removed before submission to any venue. Leaving them in the paper would reveal the automated pipeline origin and may be inconsistent with venue policies on AI-assisted writing disclosure (depending on venue). The "7/13 verified via Semantic Scholar MCP" note is particularly inappropriate for submission as it reveals the automated citation-checking process.

**Action required for human reviewer:**
1. Remove all three attribution lines from the YAML front matter and paper footer before submission.
2. If the venue requires AI-assisted writing disclosure, replace with an appropriate acknowledgment per the venue's policy.
3. Review whether any venue-specific metadata needs to be added to the YAML header.

**Severity:** Must-fix before submission (meta/administrative), but flagged as MINOR since it does not affect scientific content.

---

## Additional Expert Observations (Not in MINOR list but flagged for awareness)

### Single Architecture Dependency (Skeptical Expert Section 3.4)

The normalization argument (g̃ = ‖pᵢ − yᵢ‖ only when feature norms are equalized) depends on BatchNorm. For architectures without BatchNorm (e.g., ViT with LayerNorm, early convolutional networks without BN), the normalization step may not produce a clean residual signal. The paper currently limits claims to "FC + BatchNorm architectures (standard ResNet family)" but does not explicitly call out why other architectures may not generalize. Human reviewer may wish to add a sentence to Limitation 2 or Section 3.1 noting this architectural dependency.

### k=0.25 Sensitivity Not Reported

Table 2 shows epoch sensitivity but not k-sensitivity. Section 3.3 states k=25% is "primary configuration" but no ablation on k (e.g., k ∈ {10%, 25%, 50%}) is presented. A reviewer may ask about k sensitivity. Human reviewer should decide whether to add a brief note acknowledging this as future work or run the ablation.

### "First Experimental Confirmation" Claim (Conclusion)

With the addition of EL2N discussion in Section 2.4 (MAJOR-5 fix), the "first experimental confirmation of gradient norms as a minority proxy signal" claim in the Conclusion now needs to be read in context of the EL2N distinction. The claim is valid (EL2N was not used for minority identification) but should be read as "first application of EL2N-equivalent signal to minority group identification in spuriously correlated settings," not "first use of gradient-adjacent signals in training dynamics analysis." Human reviewer may wish to add this qualifier to Conclusion contribution (1).

---

*Human review notes generated by Revision Agent — Phase 6.5 Round 1*
*Source: 065_review_r1.md MINOR issues + Skeptical Expert observations*
*Date: 2026-03-16*
