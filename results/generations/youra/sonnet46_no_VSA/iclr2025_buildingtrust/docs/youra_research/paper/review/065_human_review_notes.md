# Human Review Notes — Phase 6.5 Minor Issues

These are MINOR issues not auto-fixed. Human judgment required.

---

## B1: Introduction paragraph 3 density

**Location:** Section 1, paragraph 3 ("The core problem runs deeper...")

**Issue:** The paragraph front-loads the mechanism description ("Encoder-only models with bidirectional attention globally redistribute attention mass toward perturbed tokens...") before establishing why readers should care. Some reviewers may find this premature.

**Suggested fix:** Consider moving the mechanism description to after the "we hypothesize" clause, or breaking the paragraph into two — one establishing the problem (scalar aggregation discards structure), one introducing the mechanistic hypothesis.

**Risk level:** Low — current version is defensible, just dense.

---

## B2: Zhang et al. (2026) / Arora et al. (2026) citation timing

**Location:** Section 2.2 Related Work (in section files: `02_related_work.md` references "Arora et al. (2026)"; original `06_paper.md` references "Zhang et al. (2026)")

**Issue:** A paper submitted ~2026-08-02 citing ACL 2026 (Industry) proceedings may raise reviewer skepticism about citation access and timing. The section files cite "Arora et al. (2026)" while the main paper body cited "Zhang et al. (2026)" — there is inconsistency between the section files and the original paper body.

**Suggested fix:** (a) Verify which citation is correct (Arora or Zhang) and make consistent. (b) If this is a real 2026 paper, confirm it is actually in the proceedings and add the arXiv preprint link as fallback. (c) If timing is problematic for submission, consider cutting this citation and relying on Yoo et al. (2024) for the architecture comparison point.

**Risk level:** Medium — reviewers may flag anachronistic citations.

---

## S4: MANOVA rank note

**Location:** Section 3.5 Statistical Methods

**Issue:** The paper does not note that permutation MANOVA sidesteps the distributional assumptions (including rank sufficiency of the within-group scatter matrix) that standard parametric MANOVA requires. At N=9, K=6, a technically careful reviewer might ask whether the within-group scatter matrix W is full-rank (it has rank ≤ 6, which is fine given 6 dimensions, but worth noting).

**Suggested fix:** Add one sentence: "With N=9 and K=6, the within-group scatter matrix W has sufficient rank for Pillai's trace computation; the permutation approach eliminates the distributional assumptions that would otherwise make N=9 invalid for parametric MANOVA."

**Risk level:** Low — only the most methodologically pedantic reviewers will raise this.

---

## Citation inconsistency note

**Location:** `06_paper.md` vs section files

**Issue:** The Introduction in `06_paper.md` uses "Wang et al. (2021)" for AdvGLUE; the section files (`01_introduction.md`, `02_related_work.md`) use "Zeng et al. (2021)". The final paper (`06_paper_final.md`) uses "Zeng et al. (2021)" throughout (from the section files). The `06_references.bib` should be verified to contain the correct AdvGLUE citation (NeurIPS 2021 AdvGLUE paper) and author attribution.

**Risk level:** Medium — citation accuracy is expected for camera-ready.
