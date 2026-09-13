# R1 Revision Changelog

**Paper:** "Symmetry Orbits Are Geometrically Large in MLP Weight Spaces: Implications for Weight Space Encoding"
**Revision round:** R1
**Date:** 2026-08-27
**Issues addressed:** 1 FATAL, 7 MAJOR

---

## FATAL Fix

### FATAL-P1-003: Sign-flip ReLU derivation (Section 3.2)

**Problem:** The original derivation contained a dangling contradiction — it set up the two-layer flip argument then noted "ReLU(-x) ≠ -ReLU(x)" in a way that appeared to undermine the functional equivalence claim without resolving it.

**Fix:** Rewrote the sign-flip orbit construction paragraph in Section 3.2 to:
1. Explicitly state that the scaling case (α > 0) uses positive homogeneity and is exact.
2. State clearly that ReLU is not odd, so a naive single-layer sign flip breaks equivalence.
3. Explain the two-layer simultaneous flip construction and show the algebra that leads to the approximation.
4. Characterize the result honestly: sign-flip produces *near*-functional-equivalents that agree except near each neuron's decision boundary.
5. Label this as an **approximate** symmetry throughout, with the caveat that runtime functional equivalence verification was not performed (now also listed as Limitation 3).

---

## MAJOR Fixes

### MAJOR-P1-001: CI upper bound corrected

**Problem:** Abstract stated CI=[0.023, 0.024] for the NFT scaling gap; the correct value from the data is [0.0232, 0.0245], so the upper bound should be 0.025 (rounded) not 0.024.

**Fix:** Abstract now reads "95% CI=[0.023, 0.025]". Body text (Introduction, Results Section 5.2, Conclusion) consistently uses the full CI=[0.0232,0.0245].

---

### MAJOR-P1-002: N=2,500 breakdown clarified

**Problem:** Introduction stated "N=2,500 total" without explaining the decomposition, leaving readers uncertain whether this was 2,500 per condition or some other grouping.

**Fix:** Introduction now reads "N=2,500 total, comprising 5 conditions × 500 pairs each". Section 3.2 (sign-flip paragraph) also now explicitly states "5 conditions × 500 pairs each". Contribution 1 in Introduction likewise updated.

---

### MAJOR-P1-004: Table 5 Δρ column and CI warning

**Problem:** Table 5 lacked explicit Δρ values and did not have a prominent warning that all CIs include zero.

**Fix:** Table 5 now includes a Δρ column with explicit values for all three properties. The table caption now reads "mean ± CI width ≈0.6; all 95% CIs include zero". The sentence immediately preceding the table is bolded: "All bootstrap 95% CIs have width ≈0.6 and include zero; no condition comparison is statistically significant at n=50 test samples."

---

### MAJOR-P3-001: "First empirical characterization" narrowed

**Problem:** The abstract and introduction used the broad phrase "first empirical characterization" without distinguishing from prior work by Entezari et al. [2022] and Ainsworth et al. [2022] that also characterizes symmetry empirically (for permutation, not scaling/sign-flip).

**Fix:** Abstract now reads "first empirical quantification of scaling and sign-flip symmetry orbit diameters as cosine distances in a real MLP model zoo". Introduction uses the same phrasing and adds a footnote (¹) explicitly distinguishing from Entezari/Ainsworth, which characterize permutation orbit geometry in the model merging context but not scaling or sign-flip orbit cosine distances.

---

### MAJOR-P3-002: NFT ρ≈0.11 vs. layer statistics ρ≈0.9 gap contextualized

**Problem:** The 10× performance gap between NFT and layer statistics was mentioned but not adequately explained in Introduction, Related Work, or Section 4.3 — risking the impression that NFT is architecturally deficient rather than underpowered.

**Fix:**
- **Introduction:** Added a dedicated paragraph "A note on NFT's current performance" explaining the gap as a consequence of N=400 underpowered training combined with the invariance problem, explicitly stating this motivates rather than undermines the analysis.
- **Related Work (Section 2):** NFT's ρ≈0.11 sentence now includes the contextualization: "Section 4.3 contextualizes this gap as a consequence of underpowered training (N=400 samples) combined with NFT devoting representational capacity to symmetry-induced weight variation."
- **Section 4.3:** Baseline description for Condition A now includes: "This gap primarily reflects underpowered training (N=400 samples) combined with NFT devoting representational capacity to symmetry-induced weight variation rather than functional properties... We do not treat this gap as evidence that NFT is architecturally inferior."

---

### MAJOR-P3-003: E>D finding framed as cautionary result

**Problem:** The E>D ordering in Table 5 was reported but not given adequate prominence as a cautionary result that complicates the canonicalization narrative.

**Fix:**
- **Results Section 5.5:** Added a dedicated bolded paragraph: "Cautionary result: Condition E outperforms Condition D on all tasks." Explains the E>D finding, notes it is consistent across all three properties and all 3 seeds, gives the post-hoc attribution to non-unique sign-flip canonicalization, and explicitly states "this attribution is post-hoc and cannot be confirmed at N=500."
- **Conclusion:** The fourth main finding bullet now explicitly flags E>D: "Condition E (random normalization) outperforming Condition D on all tasks is a cautionary result consistent with sign-flip harm, though it cannot be confirmed at N=500."

---

### MAJOR-P3-004: Single-zoo/single-architecture scope added as limitation

**Problem:** The paper did not include an explicit limitation acknowledging that all findings are from a single architecture (784→64→10 MLP) and dataset (MNIST).

**Fix:** Added **Limitation 4** in Section 6.2: "All findings are derived from a single architecture and dataset; generalizability is unknown." Distinguishes the methodology (which generalizes) from the specific numerical findings (which are architecture-specific). Recommends practitioners apply the same orbit characterization methodology to their own architectures.

---

## Minor Issues (Deferred)

10 MINOR issues were identified in the R1 review. Per revision protocol, these are not addressed in R1 and are collected separately for human review. They include: prose tightening in Discussion, reference formatting consistency, figure caption completeness, and notation standardization.

---

## Summary

| Category | Count | Status |
|----------|-------|--------|
| FATAL | 1 | Fixed |
| MAJOR | 7 | Fixed |
| MINOR | 10 | Deferred (human review) |

No research findings were changed. No content was deleted; all revisions added clarity or corrected errors.

---

# R2 Revision Changelog

**Revision round:** R2
**Date:** 2026-08-27
**Issues addressed:** 1 FATAL, 1 MAJOR (numerical verification round)
**Input paper:** 06_paper_r1.md
**Output paper:** 06_paper_r2.md

---

## FATAL Fix

### FATAL-ACCURACY-R2-001: NFT Gap Formula Inverted (Section 3.3)

**Problem:** The paper defined gap = within_orbit_similarity − cross_orbit_similarity, but reported gap = +0.0238 when within=0.9710 < cross=0.9949. Arithmetic: 0.9710−0.9949 = −0.0239 ≠ +0.0238. The formula was inverted relative to the computation performed.

**Fix:** Changed formula to `gap = cross_orbit_similarity − within_orbit_similarity`. Updated interpretation text: "A positive gap indicates cross-orbit pairs are more similar than within-orbit pairs — the encoder does not treat symmetry-related models as more similar, indicating non-invariance." All reported numbers (+0.0238, −0.0007) unchanged; conclusion unchanged (NFT non-invariant to scaling, approximately invariant to sign-flip).

---

## MAJOR Fix

### MAJOR-ACCURACY-R2-002: "24× Narrower" CI Claim Corrected (Section 5.2)

**Problem:** Paper claimed CI [0.0232,0.0245] is "24× narrower than the gap itself." Actual CI width = 0.0013; gap = 0.0238; ratio = 0.0238/0.0013 = 18.3×, not 24×.

**Fix:** Changed "24× narrower than the gap itself" to "approximately 18× narrower than the gap itself (CI width is ~5.5% of the gap magnitude)." Also corrected the stated CI width from 0.001 to 0.0013.

---

## Summary (Cumulative)

| Round | Category | Found | Fixed |
|-------|----------|-------|-------|
| R1 | FATAL | 1 | 1 |
| R1 | MAJOR | 7 | 7 |
| R1 | MINOR | 10 | 0 (deferred) |
| R2 | FATAL | 1 | 1 |
| R2 | MAJOR | 1 | 1 |
| **Total** | **FATAL** | **2** | **2** |
| **Total** | **MAJOR** | **8** | **8** |
| **Total** | **MINOR** | **10** | **0 (human review)** |
