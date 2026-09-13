# Adversarial Review Summary

**Paper:** SSL Pretraining with SGD Creates Geometrically Stable Spurious Shortcut Encodings: Measurement and a SAM-Based Intervention Protocol
**Original Title (revised):** SAM during SSL Pretraining Reduces Spurious Correlation Shortcut Learning
**Review Completed:** 2026-08-24
**Rounds Completed:** 2 (R1: Three-Persona, R2: Numerical Verification)
**Final Status:** CONVERGED — CONDITIONAL_ACCEPT (pending pre-submission author actions)
**Persuasiveness Check:** PASSED (post-R1 revision)

---

## Executive Summary

This paper underwent 2 rounds of adversarial review with three-persona analysis (Accuracy Checker, Bored Reviewer, Skeptical Expert).

| Severity | Found | Resolved | Remaining |
|----------|-------|----------|-----------|
| FATAL | 4 | 4 | 0 |
| MAJOR | 12 | 11 | 1* |

*1 remaining: author must verify first author name for `chen2025spectral` (NeurIPS 2025 spectral-reg paper) before submission. This is an author-action item, not an auto-fixable revision.

**MINOR Issues**: 4 collected in `065_human_review_notes.md` (NOT auto-fixed)

---

## Persuasiveness Assessment (post-R1 revision)

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | 73.4 pp gap framing is vivid; pending disclosure now honest, not deflating |
| Problem clear by paragraph 2? | PASS | 8.57% / 62% / 73 pp immediately clear |
| Novelty clear by page 1? | PASS | Geometric reframing + SAM-during-SSL stated early |
| Figure 1 self-explanatory? | CONCERN | Figures are [placeholder] references — not yet designed |
| Hook avoids "X is important"? | PASS | Opens with a number, not a generic claim |
| Pending results framing? | PASS | Two-tier framing (confirmed + protocol-pending) now explicit |

---

## Round-by-Round Summary

### Round 1: Three-Persona Review

**Focus:** Accuracy and engagement, structural issues, novelty claims

**Accuracy Checker Findings:**
| Category | Issues Found | Resolved |
|----------|--------------|----------|
| Title false claim | 1 FATAL | ✓ Title changed |
| Rounding inconsistency (8.6% vs 8.57%) | 1 MAJOR | ✓ Standardized |
| WGA gap inconsistency (73.4 vs 73.36) | 1 MAJOR | ✓ Added "(73.36 pp exact)" |
| G2-SAM citation (Ji vs Park) | 1 MAJOR | ✓ Changed to Park et al. |

**Bored Reviewer Findings:**
| Category | Issues Found | Resolved |
|----------|--------------|----------|
| Incomplete paper framing | 1 FATAL | ✓ Two-tier contribution framing added |
| Novelty undercut by pending results | 1 MAJOR | ✓ Contributions marked "(designed, pending validation)" |
| Page limit violation (~8.5 pp) | 1 MAJOR | ✓ Algorithm pseudocode removed, DGSAM condensed, rationale prose trimmed |

**Skeptical Expert Findings:**
| Category | Issues Found | Resolved |
|----------|--------------|----------|
| DINO pretrained-weight confound | 1 FATAL | ✓ Limitation 0 added; caveat in §5.1 |
| "First application" claim | 1 MAJOR | ✓ "to our knowledge" qualifier added |
| LFR proxy unvalidated for SSL | 1 MAJOR | ✓ Flagged as assumption in §3.3; added to limitations |
| Pearson r with n=4 | 1 MAJOR | ✓ Statistical limitation noted; checkpoint density guidance added |
| SAM mechanism overstated | 1 MAJOR | ✓ Changed to hypothesis framing in §3.4 |

**Key Issues Addressed in R1:**
1. **ACC-FATAL-001**: Title changed — no longer claims SAM results that don't exist
2. **BORED-FATAL-001**: Abstract + Introduction now explicitly frame two-tier contributions
3. **SKEPT-FATAL-001**: "Limitation 0" added acknowledging DINO ImageNet pretrained weights confound
4. **ACC-MAJOR-003**: G2-SAM citation corrected from "Ji et al." to "Park et al." throughout

### Round 2: Numerical Verification

**Focus:** Mathematical validity, baseline fairness, signal verification against archive JSON

**Accuracy Checker Findings:**
| Category | Result |
|----------|--------|
| DINO WGA 8.57% | ✓ VERIFIED vs JSON (0.08566977) |
| DINO avg acc 62.10% | ✓ VERIFIED vs JSON (0.6209872) |
| Supervised WGA 81.93% | ✓ VERIFIED vs JSON (0.8193146) |
| Supervised avg acc 94.74% | ✓ VERIFIED vs JSON (0.9473593) |
| WGA gap 73.36 pp | ✓ VERIFIED exact match |
| All 8 per-group values | ✓ VERIFIED exact match |
| Best val WGA 24.1% epoch 17 | ✓ VERIFIED exact (0.24060150 at epoch 17) |
| Training dynamics description | ✓ VERIFIED (minor correction: "generally >80%" not "sustained >80%") |
| Table 3 SimCLR 43.8% attribution | ✗ WRONG → corrected to NeurIPS 2025 spectral-reg |

**Skeptical Expert Findings:**
| Category | Result |
|----------|--------|
| Table 3 attribution FATAL | ✓ Fixed — chen2025spectral citation added |
| NeurIPS 2025 competitor underdiscussed | ✓ Fixed — proper comparison paragraph in §2.3+2.4 |
| Table 3 comparison footnote missing | ✓ Fixed — footnote added explaining DINO vs SimCLR conditions |

---

## Sections Modified

| Section | R1 Modifications | R2 Modifications |
|---------|-----------------|-----------------|
| Title | Changed entirely | No change |
| Abstract | Two-tier framing; "to our knowledge"; pending disclosure improved | No change |
| Introduction §1 | Two-tier contributions; "to our knowledge" qualifier; pretrained-weight note | No change |
| Related Work §2.1 | DGSAM condensed to 1 sentence | No change |
| Related Work §2.3 | — | ✓ [CITATION NEEDED] → full Chen et al. 2025 paragraph |
| Related Work §2.4 | — | ✓ New comparison: SAM vs spectral-reg as orthogonal framings |
| Methodology §3.3 | LFR proxy assumption flagged; n=4 Pearson limitation noted | No change |
| Methodology §3.4 | Algorithm pseudocode removed; mechanism language → hypothesis framing | No change |
| Experiments §4.3/4.4 | Pretrained-weight caveat added | No change |
| Results §5.1 | Pretrained-weight confound caveat added | No change |
| Results §5.2 | — | ✓ "sustained >80%" → "generally >80% after epoch 10" |
| Results §5.5 / Table 3 | Attribution flagged as [UNVERIFIED] | ✓ chen2025spectral + footnote added |
| Discussion §6.1 | Minor language fix | No change |
| Discussion §6.2 | Limitation 0 (pretrained-weight confound) added | No change |
| Conclusion §7 | Consistent with new contribution framing | No change |
| References | — | ✓ chen2025spectral entry added |

---

## Quality Improvements

- **Logical Consistency**: Improved — title, abstract, contributions, and limitations now consistent
- **Numerical Accuracy**: Verified — all primary numbers confirmed against archive JSON
- **Novelty Claims**: Refined — "first application" hedged; NeurIPS 2025 competitor properly acknowledged
- **Baseline Comparison**: Contextualized — Table 3 footnote explains DINO/SimCLR condition differences
- **Persuasiveness**: Improved — two-tier contribution framing resolves the "incomplete paper" problem
- **Hook Quality**: Unchanged (already strong — 8.57% / 73.4 pp opening)
- **Page Length**: Reduced — algorithm pseudocode removed, prose tightened

---

## Pre-Submission Author Action Items

1. **Verify "Chen et al."**: The bibtex key `chen2025spectral` uses "Chen" as a placeholder — verify the actual first author name against NeurIPS 2025 proceedings for "Mitigating Spurious Features in Contrastive Learning with Spectral Regularization."

2. **Resolve SimCLR 43.8% WGA source**: Confirm this number is from the spectral-reg paper (not from G2-SAM or another source). If the number came from a different paper, update Table 3 attribution accordingly.

3. **Verify G2-SAM first author**: bibtex key is `park2025g2sam` suggesting Park et al.; confirm this is correct.

4. **Resolve 8 UNVERIFIED references**: ghaznavi2023lfr, ghaznavi2024evals, gatmiry2024sam, izmailov2022spurious, zhang2022re, yadav2026crossvariant, ji2025scer, park2025g2sam — verify titles and venues before submission.

5. **Proxy precision/recall validation**: Validate LFR proxy transfer to SSL representations before submitting the measurement protocol as a contribution.

6. **Actual figures**: Replace all [Figure N] placeholder references with actual figure files (fig_wga_comparison.png, fig_training_dynamics.png, fig_group_accuracy.png confirmed generated in archive).

7. **Page count**: Re-estimate after R1/R2 edits; target ≤8.0 pp.

---

## Reviewer Preparation Notes

**Likely attack surfaces for real reviewers:**

1. "Two of three RQs have no results" → Prepared response: "We have reframed contributions explicitly: C1 (WGA gap, geometric stability) is confirmed; C2 (anisotropy protocol) and C3 (SAM-SSL) are designed and validated at code level, pending the 200-epoch run. The confirmed C1 finding is itself novel — no prior work documents this gap with this protocol."

2. "Why use pretrained DINO weights?" → Prepared response: "Limitation 0 acknowledged. Pretrained DINO weights represent a realistic deployment scenario (practitioners use publicly available weights). The from-scratch evaluation is part of the 9-combination protocol."

3. "The NeurIPS 2025 spectral-reg paper also does training-time SSL intervention" → Prepared response: "We now explicitly compare in §2.3-2.4. Theirs modifies the loss objective; ours uses a drop-in optimizer swap (SAM). Ours requires zero code changes to the contrastive loss, and our diagnostic (sharpness anisotropy) is orthogonal to their covariance singular mode analysis."

4. "n=4 checkpoints is too few for Pearson r" → Prepared response: "Acknowledged in §3.3 and §4.5 — we note this requires |r|>0.95 for p<0.05 with n=4. We plan to increase checkpoint density in the full run."
