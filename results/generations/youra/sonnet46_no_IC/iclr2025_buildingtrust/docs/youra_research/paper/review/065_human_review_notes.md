# Human Review Notes — Round 1

**Paper:** Trustworthiness Dimensions in LLMs Are Not Independent: A Partial Correlation Structure Driven by RLHF
**Date:** 2026-08-04
**Source:** Adversary Agent R1 review (`065_review_r1.md`) — MINOR issues section

These issues were NOT auto-fixed in the paper. They require human judgment before final submission.

---

## MINOR-1: Li et al. 2025 Incomplete Citation

**Location:** References section
**Current text:** `Li, X., et al. (2025). More RLHF, More Trust? [ICLR 2025 Oral — full citation pending verification].`
**Issue:** An incomplete citation in brackets is unprofessional in a submitted paper. This must be resolved before submission.
**Action required:** Either find the full citation (authors, title, venue, pages/URL) or remove the reference entirely. If removed, also remove the in-text mention in Section 2.4.

---

## MINOR-2: Liang et al. 2022 vs 2023 Year Inconsistency

**Location:** Introduction (§1) in-text citation; References section
**Current state:** Introduction cites "Liang et al., 2022"; References entry shows "(2023). Transactions on Machine Learning Research."
**Issue:** The TMLR publication year (2023) is the authoritative published date; the 2022 citation in-text likely reflects the arXiv preprint date.
**Action required:** Pick one year and be consistent throughout. TMLR 2023 is the published version; recommend updating in-text citation to "Liang et al., 2023."

---

## MINOR-3: Wang et al. 2025 (arXiv:2509.03871) Verifiability

**Location:** Section 2.2; References section
**Issue:** This is a September 2025 arXiv paper. The paper's knowledge cutoff is August 2025, so this reference cannot be verified. The content cited ("reasoning LLMs show worse safety and privacy than standard models") is not central to the paper's claims.
**Action required:** Determine if this arXiv paper is verifiable. If not, consider replacing with an established citation or removing the claim. Do not cite unverifiable future preprints in a submitted paper.

---

## MINOR-4: Section 4 Redundancy with Section 3

**Location:** Sections 3.1–3.5 and Sections 4.1–4.2
**Issue:** Sections 4.1 (Research Questions) and 4.2 (Dataset and Models) partially repeat Section 3.1 (Data) and 3.5 (RLHF mechanism framing). This structural redundancy is a space concern for the 8-page ICML format.
**Action required:** Consider merging Section 4 into Section 3 (Methods) or converting Section 4 to cross-references with new material only. Not urgent if within page limit.

---

## MINOR-5: Figure 3 vs Figure 10 Dendrogram Redundancy

**Location:** Appendix figure captions (Figure 3 and Figure 10)
**Issue:** Figure 3 caption says "Average-linkage hierarchical clustering dendrogram" and Figure 10 says "Ward-linkage dendrogram." Both claim to show the 2-cluster structure. If both are included, the paper should clarify which is the primary visualization and why both are needed.
**Action required:** Either remove one figure (if within the 12-figure count is a concern) or add a sentence in the Methodology or Results section explaining why both linkage dendrograms are shown (e.g., to demonstrate robustness of the cluster structure across linkage methods).

---

## MINOR-6: 91.7% vs 0.917 Representation Inconsistency

**Location:** Abstract ("91.7% bootstrap stability") vs Results §5.4 ("mean per-edge bootstrap frequency: 0.917")
**Issue:** Same number presented as percentage in abstract and decimal in results. Not an error, but may briefly confuse readers skimming between sections.
**Action required:** Optional — consider making consistent (either always percentage or always decimal). Low priority.

---

## MINOR-7: Contribution 2 Phrasing — "negative safety-to-robustness deltas"

**Location:** Introduction, Contribution #2
**Current text:** "3/3 LLaMA-2 within-family pairs showing negative safety-to-robustness deltas after RLHF fine-tuning"
**Issue:** "negative safety-to-robustness deltas" is ambiguous — it could mean "the delta from safety to robustness is negative" (which is odd phrasing) or "RLHF produces negative changes in robustness." The revised R1 paper changed this to "negative robustness deltas after RLHF fine-tuning" which is clearer, but the human reviewer should confirm this phrasing accurately reflects the finding.
**Note:** This was partially addressed in R1 (the Contribution 2 text now reads "negative robustness deltas after RLHF fine-tuning"). Human review should verify the final phrasing is satisfactory.

---

## Summary

| # | Issue | Location | Urgency |
|---|---|---|---|
| MINOR-1 | Incomplete Li et al. citation | References | High — must fix before submission |
| MINOR-2 | Liang et al. 2022 vs 2023 | Intro + References | Medium — pick one year |
| MINOR-3 | Wang et al. arXiv:2509.03871 verifiability | §2.2 + References | Medium — verify or remove |
| MINOR-4 | Sections 4 vs 3 redundancy | §3, §4 | Low — space concern only |
| MINOR-5 | Figure 3 vs Figure 10 both show dendrograms | Appendix | Low — clarify or remove one |
| MINOR-6 | 91.7% vs 0.917 format inconsistency | Abstract + §5.4 | Very low — cosmetic |
| MINOR-7 | Contribution 2 phrasing | §1 | Low — partially addressed in R1 |

---

# Human Review Notes — Round 2

**Source:** Adversary Agent R2 review (`065_review_r2.md`) — Part 4: Human Review Notes
**Date:** 2026-08-04

New issues from R2 review (not duplicated from R1 above):

---

## R2-MINOR-1: p-value Plausibility at df=12 for Safety–Privacy (p=8.77e-9)

**Location:** Table 1 (§5.1); Algorithm 1 (§3.2)
**Issue:** Manual calculation using t = ρ × √(df / (1 − ρ²)) = 0.971 × √(12 / 0.057) ≈ 14.07 yields p ≈ 5×10⁻⁸ at df=12, which is roughly 5× larger than the reported p=8.77e-9. The discrepancy likely reflects scipy's internal higher-precision ρ (0.97060... rather than rounded 0.971) used in its t-distribution calculation, but the human reviewer should verify by running the final code and checking the raw scipy output. The significance claim is unaffected (8.77e-9 << 0.0033 regardless of which is exact).
**Action required:** Run `h-e1/code/main.py` and print raw scipy p-values to confirm 8.77e-9 is the actual scipy output. If scipy returns a different value, update Table 1 accordingly.

---

## R2-MINOR-2: h-e2-v2/04_validation.md Still Says "Tumminello (2007)"

**Location:** Supporting validation file (not the paper itself)
**Issue:** The h-e2-v2/04_validation.md validation artifact uses the pre-R1 incorrect citation year "Tumminello (2007)". The paper itself is now correct ("2005"), but the validation file is inconsistent. Creates confusion if someone reads the validation file alongside the paper.
**Action required:** Update h-e2-v2/04_validation.md to read "Tumminello (2005)" for consistency. Minor artifact maintenance; does not affect the paper.

---

## R2-MINOR-3: Liang et al. 2022 vs 2023 — Still Unfixed (Carried from R1 MINOR-2)

**Location:** Introduction (§1) in-text citation
**Issue:** Still reads "Liang et al., 2022" in-text while the reference entry shows "(2023). Transactions on Machine Learning Research." This was MINOR-2 in R1 notes and was not fixed in R1 or R2 (it is a human judgment call on arXiv vs. published year). The R2 review confirmed this is still present.
**Action required:** Pick one consistent year. TMLR 2023 is the published version; recommend updating in-text to "Liang et al., 2023."

---

## R2 Human Review Summary

| # | Issue | Location | Urgency |
|---|---|---|---|
| R2-MINOR-1 | p=8.77e-9 vs manual ≈5e-8 at df=12 | Table 1 + Algorithm 1 | Medium — verify with code output |
| R2-MINOR-2 | h-e2-v2/04_validation.md says Tumminello 2007 | Validation file | Low — artifact consistency |
| R2-MINOR-3 | Liang et al. 2022 vs 2023 (carried from R1) | §1 + References | Medium — fix before submission |
