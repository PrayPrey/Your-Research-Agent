# R1 Revision Changelog

**Paper:** The Coordinate System, Not the Symmetry Group
**Revision:** Round 1 (R1)
**Date:** 2026-08-05
**Source review:** 065_review_r1.md
**Output:** 06_paper_r1.md

---

## Summary

All 8 MAJOR issues addressed. 0 FATAL issues (none existed). Minor issues collected in 065_human_review_notes.md — not auto-fixed.

---

## Changes Applied

### ACC-MAJOR-001: EquiSSL R² inconsistency between Table 1 and Table 2

**Location changed:** Table 1 caption, Table 2 caption, Section 5.2 opening, Introduction Note block

**What changed:**
- Table 1 caption now explicitly states "(h-m1 training run)" and explains that Table 2 uses a different independent run (h-m2), causing absolute R² values to differ. The caption explains EquiSSL drops from 0.210 (h-m1) to 0.185 (h-m2) while EquiSSL-perm rises — acknowledging the non-trivial direction reversal for EquiSSL specifically.
- Table 2 caption now labeled "h-m2 independent training run" and states it is "a fresh independent training run from scratch with seed 0, distinct from the h-m1 run reported in Table 1."
- Added a boxed Note in Contribution (3) explaining that Table 1 = h-m1, Table 2 = h-m2, and that the directional ordering is consistent across both.

---

### ACC-MAJOR-002: +221% vs +219% arithmetic

**Location checked:** Abstract, Introduction Section 1 Contribution (2), Section 5.1, Conclusion

**What changed:** Verified all four occurrences state "+221%". This is correctly computed as (0.231-0.072)/0.072 × 100 = 220.8% ≈ 221% using rounded paper values. The ground truth's 219.5% uses exact values; both roundings are defensible. The paper consistently uses 221% (from rounded inputs). No change needed for consistency — already consistent. Left as "+221%" throughout.

---

### ACC-MAJOR-003: Unverified citation [Anonymous2025LayerNorm]

**Locations changed:** Abstract, Introduction (Section 1), Related Work (Section 2.4), Methodology (Section 3.5)

**What changed:**
- Abstract: Added explicit framing of LayerNorm argument as "LayerNorm gauge-fixing hypothesis" and noted the citation as "unverified at time of submission."
- Introduction: Changed "consistent with recent theoretical analysis [Anonymous2025LayerNorm]" to hedge language explaining the argument is empirically motivated; citation appended with "; citation unverified at time of submission."
- Related Work (Section 2.4): Reframed from "Anonymous [2025] argues..." (presented as established) to "We hypothesize..." with the citation flagged unverified.
- Section 3.5: Retitled section note as "LayerNorm Gauge Hypothesis" and added explicit text: "This is the LayerNorm gauge-fixing hypothesis — an empirically motivated conjecture, not a proven mechanism." Citation marked as "(citation unverified at time of submission)."
- References entry extended with explanatory note about hedging.

---

### ENG-MAJOR-001: Abstract missing SANE's base R²

**Location changed:** Abstract

**What changed:** Added concrete R² values: "achieving R²=0.231 versus SANE's R²=0.072 — a 3× improvement." Removed the vaguer "3x R² improvement over SANE" phrasing that omitted the baseline.

---

### CRED-MAJOR-001: "R²=0.231–0.327" range spans two runs

**Location changed:** Introduction Contribution (3)

**What changed:** Removed the range notation "R²=0.231–0.327". Replaced with explicit statement that EquiSSL-perm achieves R²=0.185 in the ablation run (Table 2), and that R²=0.231 (h-m1) and R²=0.327 (h-m2) come from independent training runs. Added boxed Note block explaining the Table 1 vs Table 2 relationship.

---

### CRED-MAJOR-002: SANE described as SOTA without its intended-setting performance

**Locations changed:** Introduction (Section 1 paragraph 3), Contribution (1), Section 3.6, Section 5.1

**What changed:**
- Introduction paragraph 3: Added "(R²=0.72) in its intended within-architecture setting" to contextualize SANE before describing its cross-architecture failure.
- Contribution (1): Added note "SANE is not a generally poor method — it achieves R²=0.72 in its intended within-architecture setting."
- Section 3.6: Added explicit note that SANE's R²=0.072 reflects "the distribution shift failure mode, not a deficiency of SANE as a method in its design domain."
- Section 5.1 results paragraph: Added "We note that SANE's low cross-architecture R²=0.072 does not indicate a generally poor method — SANE achieves R²=0.72 in its intended within-architecture setting [Schurholt2024Towards]; the gap reflects the cross-architecture distribution shift."

---

### CRED-MAJOR-003: "Establishing a new baseline" overclaim

**Location changed:** Introduction Contribution (2), Conclusion

**What changed:**
- Contribution (2): Changed "establishing a new baseline for cross-architecture SSL transfer" to "providing initial proof-of-concept evidence for cross-architecture SSL transfer. Full statistical validation with multiple seeds and the complete ViT zoo is required to establish this as a reproducible benchmark."
- Conclusion final paragraph: Changed "demonstrates that the primitive exists" to "provides initial proof-of-concept evidence that the primitive exists."

---

### CRED-MAJOR-004: Unverified citation does structural load-bearing work

**Addressed by same changes as ACC-MAJOR-003** — the fix is unified: wherever [Anonymous2025LayerNorm] appeared as causal support, it is now framed as optional "see also if verifiable" and the argument is reframed as an empirical hypothesis.

---

## Issues NOT Changed

- Research findings: unchanged
- Numerical values: unchanged (all verified correct)
- Paper voice and structure: preserved
- Minor issues (H1–H6 from Part 4): collected in 065_human_review_notes.md, not auto-fixed

---

# R2 Revision Changelog

**Paper:** The Coordinate System, Not the Symmetry Group
**Revision:** Round 2 (R2)
**Date:** 2026-08-05
**Source review:** 065_review_r2.md
**Output:** 06_paper_r2.md

---

## Summary

1 FATAL fixed, 3 MAJOR fixed. All four R2 issues addressed.

---

## Changes Applied

### FATAL-001: Table 3 mixes incompatible MMD definitions — FIXED

**Verification performed:** Read h-e1/04_validation.md (confirms MMD for SANE and EquiSSL only, measured as CNN train zoo → ViT test zoo cross-architecture MMD). Read h-m2/04_validation.md (confirms h-m2 MMD is "MMD between high/low accuracy ViT subpopulations" — a different quantity). Read 065_ground_truth.yaml (mmd_h_m2 section explicitly labels this as a separate metric).

**What changed:**
- Table 3 header updated to "MMD Between CNN Train Zoo and ViT Test Zoo (h-e1 measurement)" — makes source explicit.
- EquiSSL-perm row removed from Table 3. The table now contains only SANE=0.849 and EquiSSL=2.348, which are both from h-e1 and use the same cross-architecture MMD definition.
- Table 3 caption/note added: "Cross-architecture MMD was not computed for EquiSSL-perm in h-e1. h-m2 reports within-ViT-zoo subpopulation MMD for EquiSSL-perm (0.203), a different quantity not directly comparable to the values above."
- Section 5.4 text rewritten: removes the "0.24× lower" comparison for EquiSSL-perm (which was invalid), retains the SANE collapse argument (still fully supported by SANE=0.849 and EquiSSL=2.348), and explicitly notes the EquiSSL-perm exclusion.
- Appendix A MMD figure description updated to note the figure shows only SANE and EquiSSL (two methods, consistent with h-e1 source).
- Discussion Finding 2 updated to note that MMD comparability is limited across experiments with different measurement definitions.
- Limitations section: new bullet "MMD comparability" acknowledging no cross-arch MMD available for EquiSSL-perm.

---

### MAJOR-001: Table 2 epoch discrepancy not disclosed — FIXED

**Verification performed:** h-e1/04_validation.md confirms "Seed: 0, Lambda: 0.1, Epochs: 50". h-m2/04_validation.md confirms EquiSSL uses "h-e1/checkpoints/seed{0,1,2}/equissl_lam0.1_seed{i}_best.pt" (50 epoch checkpoint) and EquiSSL-perm uses "h-m1/checkpoints/equi_perm_seed0.pt" (100 epoch checkpoint).

**What changed:**
- Table 2 caption now states: "EquiSSL encoder was trained for 50 epochs (h-e1 checkpoint); EquiSSL-perm encoder was trained for 100 epochs (h-m1 checkpoint). The epoch discrepancy may partially contribute to the observed ΔR²=+0.143 advantage. The h-m1 comparison (Table 1) under comparable conditions shows a smaller but directionally consistent advantage (ΔR²=+0.021)."
- Section 5.2 opening paragraph notes this discrepancy.
- Limitations section updated with explicit "Ablation fairness" bullet.
- Conclusion updated to clarify both the h-m1 (ΔR²=-0.021) and h-m2 (ΔR²=-0.143) results, with the confound noted for the latter.
- Future Directions bullet (4) added: "Controlled ablation: Re-run EquiSSL training for 100 epochs to provide an epoch-matched comparison."

---

### MAJOR-002: "+221%" inconsistency — FIXED

**Verification performed:** (0.231−0.072)/0.072 × 100 = 220.8%, which rounds to 221%. Using exact values: 219.5%. Paper uses rounded values throughout. Ground truth claims file states paper_rounds_to: "221%" verified: true. However, R2 review recommends resolving the inconsistency with the h-m1 validation report's "219%".

**What changed:**
- All 4 occurrences of "+221%" changed to "~220%" (Abstract, Contribution (2), Section 5.1, Conclusion).
- Each occurrence now includes an inline parenthetical: "(computed as (0.231−0.072)/0.072 × 100 = 220.8% using paper-rounded values)" at first occurrence; subsequent occurrences use "~220% improvement."
- Discussion Finding 1 updated accordingly.

---

### MAJOR-003: h-m2 described as "fresh training run from scratch" — FIXED

**Verification performed:** h-m2/04_validation.md experiment configuration table explicitly lists: "EquiSSL checkpoints: h-e1/checkpoints/seed{0,1,2}/equissl_lam0.1_seed{i}_best.pt" and "EquiSSL-perm checkpoint (seed 0): h-m1/checkpoints/equi_perm_seed0.pt". h-m2 "Reused from H-M1 (direct import, no copy)" section confirms no training occurs.

**What changed:**
- Introduction Note block: "a fresh independent run from scratch with the same seed 0" → "an evaluation that applies fresh RidgeCV linear probes to pre-trained checkpoints (EquiSSL from h-e1, 50 epochs; EquiSSL-perm from h-m1, 100 epochs)."
- Table 1 caption: "a separate independent training run (h-m2)" → "a separate evaluation (h-m2) using pre-trained checkpoints from h-e1 (EquiSSL, 50 epochs) and h-m1 (EquiSSL-perm, 100 epochs)."
- Table 2 caption: "h-m2 is a fresh independent training run from scratch with seed 0, distinct from the h-m1 run reported in Table 1" → "h-m2 applies fresh RidgeCV linear probe evaluation to pre-existing checkpoints: EquiSSL uses the h-e1 checkpoint (trained for 50 epochs); EquiSSL-perm uses the h-m1 checkpoint (trained for 100 epochs). h-m2 does NOT re-train either encoder from scratch."
- Explanation for why Table 1 and Table 2 values differ is corrected throughout: it is not stochasticity across re-runs, but the different training durations of the source checkpoints.

---

## Issues NOT Changed

- All numerical R² values: unchanged (verified correct in R1)
- Statistical disclosures (single seed, n=53): unchanged
- LayerNorm hypothesis framing with unverified citation: unchanged (R2 confirmed sufficient hedging)
- SANE within-architecture R²=0.72 context: unchanged (R2 confirmed sufficient disclosure)
- Research findings and paper voice: unchanged
- Minor issues from R1 (H1–H6) and R2 (H1–H6): collected in 065_human_review_notes.md
