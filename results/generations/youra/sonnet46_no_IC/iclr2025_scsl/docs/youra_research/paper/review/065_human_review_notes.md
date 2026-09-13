# Human Review Notes — Round 1 MINOR Issues
**Paper**: Where Does WGA Improvement Come From? Backbone vs. Head Robustification in ResNet-50 on Waterbirds  
**Source**: `06_paper_r1.md`  
**Date**: 2026-08-05  
**Note**: These are MINOR issues identified during adversarial review. They were NOT auto-fixed in `06_paper_r1.md`. Address at author discretion before Round 2 submission.

---

## HRN-1: Figure 1 Caption Not Verified

**Location**: Section 5.1, reference to `figures/cosine_similarity_per_seed.png`  
**Issue**: The paper text references Figure 1 but the figure caption content is not included in the paper source. The Bored Reviewer persona flagged that Figure 1's caption could not be assessed for self-containedness.  
**Action required**: Confirm that the Figure 1 caption (in the actual figure file or a figures section) is self-explanatory and includes: (a) cosine similarity values per seed, (b) variance values (~1e-14), (c) the interpretation (DFR backbone = ERM backbone at float32 precision). Caption should be readable without the main text.

---

## HRN-2: Contribution #2 Uses Procedural Framing

**Location**: Introduction, Contributions, item #2  
**Current text**: "Quantified GroupDRO backbone effect. We provide the first per-seed, per-method spurious attribute linear probe accuracy for the izmailovpavel checkpoints with paired statistical testing — filling the measurement gap in Izmailov et al. [2022]..."  
**Issue**: "Quantified GroupDRO backbone effect" is a "we did X" framing rather than insight framing. Contribution #1 uses the stronger insight framing ("Empirical backbone-vs-head typology"). Consistency improves persuasiveness with busy reviewers.  
**Suggested reframe**: "GroupDRO substantially modifies backbone weights; DFR leaves them numerically identical. We establish this distinction with the first per-seed, per-method spurious attribute linear probe accuracy for the izmailovpavel checkpoints (backbone/head L2 ratio = 6.47–7.03 for GroupDRO vs. 0.000 for DFR), filling the measurement gap in Izmailov et al. [2022]."

---

## HRN-3: Section 3 Hypothesis Gate Taxonomy is Dense

**Location**: Section 3 (Methodology), Sections 3.1–3.8  
**Issue**: Five hypothesis gate labels (H-P0, H-M1, H-M2, H-M3, H-P2) are introduced and used throughout Sections 3–5 without an upfront decoder. A busy reviewer reading at pace may lose track of which gate corresponds to which substantive claim.  
**Suggested fix**: Add a small decoder table at the start of Section 3.1 (or as a new Section 3.1 before the current Overview text):

| Gate | Substantive claim | Type |
|------|-------------------|------|
| H-P0 | DFR backbone = ERM backbone | MUST_WORK |
| H-M1 | GroupDRO minority upweighting exists | MUST_WORK |
| H-M2 | GroupDRO modifies backbone weights | SHOULD_WORK |
| H-M3 | GroupDRO reduces background linear decodability | MUST_WORK (primary) |
| H-P2 | Probe accuracy correlates with WGA | SHOULD_WORK (exploratory) |

---

## HRN-4: Large Effect Size d=6.48 Unexplained

**Location**: Results 5.3, Discussion 6.2 (L1)  
**Issue**: Cohen's d = 6.48 is exceptionally large. The paper notes "primary finding d=6.48 unaffected" by the n=3 power concern but does not explain *why* d is so large. Expert reviewers may suspect probe overfitting, data leakage, or methodological artifact.  
**Suggested addition** (in Discussion 6.1 or 6.2): "The large effect size (d=6.48) likely reflects that GroupDRO's minority upweighting consistently and substantially reshapes backbone representations across all three seeds, rather than methodological artifact — DFR's cosine similarity = 1.000000 across all seeds provides a clean negative control confirming the probe is detecting genuine backbone differences."  
**Rationale**: This pre-empts expert skepticism and strengthens the paper's credibility.

---

# Round 2 Additional MINOR Issues

## HRN-5: Bootstrap NaN Filtering Not Documented in Paper

**Location**: H-P2 analysis (Section 5.4, Section 3.7)
**Issue**: h-p2/04_validation.md reports "2 of 1000 bootstrap samples produced NaN and were filtered; CI computed from 998 clean samples." The paper does not mention this filtering. Numerically inconsequential (CI bounds unaffected), but a thorough reviewer may ask about bootstrap implementation details.
**Suggested fix**: Optionally add footnote: "2 degenerate bootstrap samples (constant input) were excluded; CI computed from 998 samples." Low priority.

## HRN-6: Internal h-m3 Diagnostic Value (Informational)

**Location**: h-m3/04_validation.md (internal, not in paper)
**Issue**: h-m3 validation file contains a preliminary probe-vs-WGA figure annotated with r=-0.626, which differs from H-P2's pre-registered r=-0.504. This is a preliminary diagnostic from H-M3's exploratory phase, superseded by the dedicated H-P2 experiment. No paper change needed; flagging for awareness.
**Suggested fix**: Optional note in h-m3/04_validation.md clarifying the r=-0.626 is a preliminary internal diagnostic.

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 2 (HRN-2, HRN-3) |
| Clarity | 3 (HRN-1, HRN-4, HRN-5) |
| Formatting | 0 |
| Informational | 1 (HRN-6) |
| **Total** | **6** |

## Recommended Priority

1. **Fix First**: HRN-4 — Explain large d=6.48 in Discussion (prevents expert skepticism)
2. **Fix Second**: HRN-1 — Verify Figure 1 caption is self-explanatory
3. **Consider**: HRN-3 — Add hypothesis gate decoder table at start of Section 3
4. **Consider**: HRN-2 — Reframe Contribution #2 as insight not procedure
5. **Optional**: HRN-5 — Bootstrap filtering footnote
6. **Optional**: HRN-6 — Internal diagnostic documentation only

*Note: These issues do not block paper acceptance but improve overall quality.*
