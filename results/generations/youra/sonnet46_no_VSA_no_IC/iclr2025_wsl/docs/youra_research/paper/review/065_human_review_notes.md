# Human Review Notes — Round R1

**Paper:** "When Symmetry Hurts: Data-Regime-Dependent Sample Efficiency of Equivariant Weight-Space Encoders"  
**For:** Human reviewer or author — these MINOR issues were NOT auto-fixed in R1 revision  
**Date:** 2026-08-21

---

## MINOR Issues (Require Author Judgment)

These issues were identified in the adversarial review (065_review_r1.md) but were not auto-fixed per the revision protocol. Each requires author judgment before final submission.

---

### m1 — Abstract: Dayan et al. [2026] cited as "established theory"

**Location:** Abstract, final sentence; also Section 2.3 and Section 5.4  
**Issue:** The paper cites Dayan, Eitan, and Maron [2026] as supporting "expressivity equivalence theory" without flagging that this is a 2026 preprint. A submission to ICML 2025 or ICML 2026 that cites a concurrent or future-dated preprint as established background theory may raise questions from reviewers about the timing and peer-review status of the citation.  
**Suggested fix:** Add "recently proposed" or "as shown by the concurrent" before the reference. For example: "consistent with the recently proposed expressivity equivalence theory [Dayan et al., 2026]."  
**Risk if unfixed:** Reviewer may question whether the cited theoretical grounding is established or speculative. Low risk of rejection but may generate a review comment requiring response.

---

### m2 — Section 4.3: Overly specific GPU memory specification

**Location:** Section 4.3 Implementation Details, last line  
**Issue:** "All experiments run on NVIDIA H100 NVL GPUs (5× 95,830 MiB)" — the MiB specification is unconventional in a research paper and slightly distracting. Standard practice is to write "5× NVIDIA H100 NVL GPUs" or simply "NVIDIA H100 GPUs."  
**Suggested fix:** Remove the MiB spec: "All experiments run on 5× NVIDIA H100 NVL GPUs."  
**Risk if unfixed:** Cosmetic; unlikely to affect reviewer judgment but adds noise.

---

### m3 — Section 5.1: "reducing zoo collection burden by ~7×" conflation

**Location:** Section 5.1, paragraph after efficiency ratio derivation  
**Current text (in original 06_paper.md):** "reducing zoo collection burden by ~7×"  
**Note:** This phrase was updated in R1 as part of F2 revisions (the "7×" claim is now superseded by the ~47× efficiency ratio). The R1 text no longer contains this exact phrasing. However, if the efficiency ratio framing is later revised back toward the conservative 6.8× lower bound, the "zoo collection burden" framing should use the more precise language: "reducing the minimum zoo size requirement" rather than "burden," since zoo collection cost is not purely linear in model count (curation, training time, and storage scale differently).  
**Action needed:** Confirm that the R1 text does not reintroduce this conflation. If the ~47× framing is retained, this note is moot.

---

### m4 — PermAug 11× expansion factor not ablated

**Location:** Section 3.3, Section 5.3, Discussion  
**Issue:** The 11× expansion factor for PermAug is stated as a fixed design choice but never ablated. A reviewer will likely ask: does the crossover between PermAug and GNN-NFN at N=100 depend on the expansion factor? Would 2× or 20× expansion shift the crossover threshold? The current paper cannot answer this question.  
**Suggested fix:** Add to Section 7 Conclusion future work directions: "Ablating the PermAug expansion factor (currently 11×) to determine whether the N=100 crossover is driven by the augmentation strategy or purely by effective dataset size."  
**Risk if unfixed:** A reviewer who suspects the crossover is explained by the 11× expansion (rather than structural differences) will have grounds for a reject. The current text acknowledges PermAug's benefit "appears primarily due to data quantity (11× expansion per gradient step)" — this is honest but may need more explicit treatment.

---

### m5 — Limitations: no formal CI on efficiency ratio (partially addressed in R1)

**Location:** Section 6.2 Limitations  
**Status:** R1 added a Limitations bullet on the CI issue ("No formal CI on efficiency ratio"). However, the full uncertainty range was not given a formal bootstrap treatment — only an interpolation-bounds estimate (101–249 for N_equiv_90). A formal bootstrap CI on the efficiency ratio would require resampling the test set, not just the training curve points.  
**Suggested fix:** Consider whether a bootstrap CI on the efficiency ratio (resampling the R² estimates at each N) would be feasible with the stored experimental outputs. If so, reporting it would substantially strengthen the claims. If not, acknowledge this explicitly: "A formal bootstrap CI on the efficiency ratio requires test-set resampling at each N, which we defer to a full multi-seed replication study."  
**Risk if unfixed:** The current interpolation-bounds statement in R1 is an improvement over the original. A statistics-focused reviewer may still flag the absence of a formal CI.

---

### m6 — Section 2.1: DWSNets R²≈0.89 attribution

**Location:** Section 2.1, first paragraph  
**Issue:** The paper states "achieving R²≈0.89 for accuracy prediction on a private MNIST model zoo." The R1 revision changed this to "with Navon et al. reporting R²≈0.89 for accuracy prediction on a private MNIST model zoo" — improving attribution. However, if a reviewer cross-checks this value against the DWSNets paper and finds a different number (different metric, different zoo, different split), it could raise a verification question.  
**Suggested fix:** Consider adding "approximately" and a footnote: "R²≈0.89 as reported in Table 2 of Navon et al. [2023]; exact value may vary by split and evaluation protocol."  
**Risk if unfixed:** Low; the R1 text already adds "Navon et al. reporting" which is the minimal attribution fix. Further qualification may be unnecessary.

---

## Summary Table

| ID | Location | Issue | Auto-fixed? | Priority |
|----|----------|-------|-------------|----------|
| m1 | Abstract, Sec 2.3, 5.4 | Dayan 2026 preprint cited as established theory | No | Medium |
| m2 | Sec 4.3 | GPU MiB spec is non-standard | No | Low |
| m3 | Sec 5.1 | "zoo collection burden" conflation (superseded in R1) | No (moot in R1) | Low |
| m4 | Sec 3.3, 5.3, Discussion | PermAug 11× factor not ablated | No | High |
| m5 | Sec 6.2 | No formal CI on efficiency ratio (partially addressed) | Partial | Medium |
| m6 | Sec 2.1 | DWSNets R²≈0.89 attribution | Partial (R1 improved) | Low |

---

*Generated by YouRA Phase 6.5 Revision Agent — Round R1*  
*These notes are for human review only and were NOT applied to 06_paper_r1.md*
