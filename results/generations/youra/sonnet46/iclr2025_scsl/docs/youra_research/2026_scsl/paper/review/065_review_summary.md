# Phase 6.5 Adversarial Review — Summary
**Paper:** Gradient Norms as Label-Free Minority Proxies: A Mechanistic Study of the Prediction-Residual Signal for Spurious Correlation Robustness
**Hypothesis:** H-GNR-LLR-v1
**Review Date:** 2026-03-16
**Rounds Completed:** 2 (R1: Accuracy & Engagement, R2: Verification & Credibility)
**Final Recommendation:** CONDITIONAL_ACCEPT

---

## Convergence Status

| Criterion | Status |
|-----------|--------|
| FATAL issues = 0 | ✅ PASS |
| MAJOR issues = 0 | ✅ PASS (all fixed through R1+R2 revisions) |
| Persuasiveness passed | ✅ PASS |
| Rounds ≥ 2 | ✅ PASS (2 rounds completed) |

**Decision: CONVERGED → CONDITIONAL_ACCEPT**

---

## Round-by-Round Summary

### Round 1 — Accuracy and Engagement

**Personas:** Accuracy Checker, Bored Reviewer, Skeptical Expert

**Issues found:**
- FATAL: 2
- MAJOR: 6
- MINOR (human review): 7

**Key findings:**
1. FATAL-1: Paper titled and framed as "GNR-LLR" (two-stage method) but Stage 2 never executed — systematic framing mismatch
2. FATAL-2: NHT [Khanh & Hoa, 2026] cited as theoretical grounding with [UNVERIFIED] tag appearing in own reference list — desk-reject risk
3. MAJOR-1: JTT AUC comparison "estimated 0.70-0.80" without citation or derivation
4. MAJOR-2: DFR 92.9% WGA comparison with no WGA results in paper
5. MAJOR-3: Multiple [UNVERIFIED] tags in reference list
6. MAJOR-4: Minority recall not computed
7. MAJOR-5: EL2N (Paul et al. 2021) not cited — novelty claim at risk
8. MAJOR-6: Single seed (42) not disclosed as limitation

**Engagement:** Would continue reading (AUC=0.914 and outer-product story engaging); attention declined at Section 6.1 Discussion (repetitive).

**R1 Revision:** All 2 FATAL + 6 MAJOR issues fixed. Human review notes collected.

---

### Round 2 — Verification and Credibility (with Serena MCP)

**Personas:** Accuracy Checker, Skeptical Expert
**Serena MCP verification:** 11 tool calls; all numerical values verified against `h-e1/experiment_results.json`

**Numerical verification results:**
- All 18 numerical values in R1 paper verified ✅
- Ratio 8.805 independently recomputed: 8.806 (match) ✅
- Outer-product decomposition mathematically valid ✅
- h_norm_std_ratio ≈ 0.10 confirmed from JSON data ✅
- AUC=0.914 internally consistent with per-group structure ✅

**Issues found:**
- FATAL: 0
- MAJOR: 3 (all fixed in R2 revision)
- MINOR (human review): 7

**Key R2 findings:**
1. MAJOR-R2-1: "≥90%" minority recall claim uncomputed — softened to "high minority recall" with AUC-based evidence
2. MAJOR-R2-2: GNR-LLR name retained in Section 3.4 with full Stage 2 spec — added explicit scope disclaimer
3. MAJOR-R2-3: JTT +21pp not pinned to specific table — added "(Table 1, Liu et al. 2021)"
4. Additional: g̃>0.2 boundary claim scoped to epoch-5 only

**Persuasiveness:** PASSED — core claims verified; framing honest about scope limitations; mathematical validity strong.

---

## Persuasiveness Assessment (Final)

| Check | Result |
|-------|--------|
| Abstract compelling | ✅ Yes — AUC=0.914 is arresting; scope limitation disclosed |
| Problem clear in 1 minute | ✅ Yes — spurious correlation / minority identification well framed |
| Novelty clear in 2 minutes | ✅ Yes — gradient domain + outer-product decomposition story clear |
| Figure 1 self-explanatory | ✅ Yes — 3-bar chart with targets; design mismatch labeled |
| Would continue reading | ✅ Yes |
| Attention lost at | Section 6.1 Discussion (minor) |
| False novelty claims | 0 (EL2N comparison added; novelty appropriately scoped) |
| Unfair baseline comparisons | 0 (DFR WGA comparison removed; JTT comparison now theory-based) |
| Overclaims resolved | ✅ All major overclaims removed |
| Missing limitations | 0 (single seed added; WGA not measured prominent) |

---

## Total Issues Found and Resolved

| Category | Found | Resolved | Remaining in Paper |
|----------|-------|----------|--------------------|
| FATAL | 2 | 2 | 0 |
| MAJOR | 9 | 9 | 0 |
| MINOR (human review) | 14 | 0 | 14 (for human review) |

**All FATAL and MAJOR issues resolved through R1+R2 revision cycle.**

---

## Final Paper Version

**File:** `docs/youra_research/20260315_scsl/paper/06_paper_final.md`
**Source:** 06_paper_r2.md (R2 revision)
**Scope:** Stage 1 proxy signal study (H-E1 execution only)
**Core claims status:** All verified against ground truth

**Verified claims:**
- AUC = 0.914 for minority group prediction at T_id=5 ✅
- Minority/majority ratio = 8.8x at T_id=5 ✅
- Temporal persistence: ratio = 8.5x at T_id=10 ✅
- h_norm_std_ratio ≈ 0.10 (BatchNorm equalization) ✅
- Outer-product decomposition mathematical validity ✅
- 67/67 tests passed; 8/8 SDD tasks compliant ✅

**Claims correctly absent from paper:**
- WGA (Stage 2 not executed) ✅
- Multi-seed results (h-m4 not executed) ✅
- Baseline WGA comparison (Phase 5 not executed) ✅

---

## Human Review Notes

**File:** `docs/youra_research/20260315_scsl/paper/review/065_human_review_notes.md`
**Total items:** 14 (7 from R1 + 7 from R2)
**Categories:** notation, formatting, metadata removal, citation year, boundary scope, YAML cleanup

Key items requiring human attention before submission:
1. Remove YAML header metadata (pipeline attribution)
2. Remove footer attribution lines
3. Kirichenko et al. [2022] citation year — standardize to publication year
4. PyTorch 2.10+cu128 version — verify actual version used
5. "criterion design flaw" vs. "criterion design lesson" — standardize terminology
6. Outer-product notation (⊗ vs. uv^T) — consider explicit notation for clarity

---

## Paper Disposition

**Recommendation:** CONDITIONAL_ACCEPT

**Condition:** Human review of 14 MINOR items (see `065_human_review_notes.md`) before final submission.

**Paper status:** Ready for human editorial review and submission preparation.
**Next steps:** Phase 6.5.1 (Overleaf LaTeX/PDF generation) + human review of MINOR items.

---

*Phase 6.5 Adversarial Review completed | 2026-03-16*
*Rounds: 2 | Total issues: 25 (2 FATAL + 9 MAJOR + 14 MINOR) | Resolved: 11 (2 FATAL + 9 MAJOR)*
