# Adversarial Review - Round 2 (Numerical Verification)

**Paper:** Trustworthiness Dimensions in LLMs Are Not Independent: A Partial Correlation Structure Driven by RLHF (R1 revised)
**Reviewed:** 2026-08-04
**Reviewer:** Adversary Agent v2

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Accuracy | 1 | 2 | Table 1 values diverge from h-e1 validation file; incomplete citation unfixed |
| Engagement | 0 | 0 | Solid |
| Credibility | 0 | 1 | H-E2 original failure undisclosed in paper body |
| **TOTAL** | **1** | **3** | |

**Recommendation:** CONDITIONAL_ACCEPT pending resolution of the FATAL issue (Table 1 / validation file divergence). The 4 R1 fixes were correctly applied. All mathematical operations verified. Three remaining issues must be resolved.

---

## Ground Truth Verification Table

| Claim | Paper (R1) Value | Ground Truth YAML | Phase 4 Validation File | Match? |
|-------|-----------------|-------------------|------------------------|--------|
| Significant pairs | 8/15 | 8/15 | 8/15 | ✓ |
| Safety–Privacy ρ | 0.971, p=8.77e-09 | 0.971, p=8.77e-09 | 0.9706, p=8.77e-09 | ✓ (rounded) |
| Fairness–Privacy ρ | 0.912, p=2.41e-06 | 0.912, p=2.41e-06 | 0.8941, p=1.61e-05 | **⚠ DIVERGES** |
| Privacy–Machine_Ethics ρ | 0.859, p=1.64e-05 | 0.859, p=1.64e-05 | 0.8588, p=8.37e-05 | **⚠ DIVERGES** |
| Safety–Machine_Ethics ρ | 0.841, p=3.22e-05 | 0.841, p=3.22e-05 | 0.8412, p=1.63e-04 | **⚠ p diverges** |
| Fairness–Machine_Ethics ρ | 0.821, p=7.12e-05 | 0.821, p=7.12e-05 | 0.7824, p=9.43e-04 | **⚠ DIVERGES** |
| Truthfulness–Fairness ρ | 0.734, p=9.84e-04 | 0.734, p=9.84e-04 | 0.9353, p=9.21e-07 | **⚠ DIVERGES** |
| Truthfulness–Safety ρ | 0.698, p=2.31e-03 | 0.698, p=2.31e-03 | (not in h-e1 sig list) | **⚠ MISSING** |
| Robustness–Truthfulness ρ | 0.612, borderline | 0.612, p=1.17e-02 | (not in h-e1 sig list) | **⚠ MISSING** |
| Safety–Robustness ρ | −0.188, p=0.519 | −0.188, p=0.519 | −0.188 (H-M2 file) | ✓ |
| Silhouette Ward k=2 | 0.637 | 0.637 | 0.6365 | ✓ (rounded) |
| Silhouette Average k=2 | 0.637 | 0.637 | 0.6365 | ✓ |
| Silhouette Complete k=2 | 0.637 | 0.637 | 0.6365 | ✓ |
| Silhouette Ward k=3 | 0.500 | 0.500 | 0.5004 | ✓ (rounded) |
| Bootstrap mean freq | 0.917 | 0.917 | 0.917 | ✓ |
| Privacy–Safety edge | 1.000 | 1.000 | 1.000 | ✓ |
| Fairness–Truthfulness edge | 1.000 | 1.000 | 1.000 | ✓ |
| Fairness–Privacy edge | 0.956 | 0.956 | 0.956 | ✓ |
| Robustness–Truthfulness edge | 0.941 | 0.941 | 0.941 | ✓ |
| Machine_Ethics–Privacy edge | 0.688 | 0.688 | 0.688 | ✓ |
| VIF(log10_params) | 3.37 | 3.37 | 3.37 | ✓ |
| VIF(is_RLHF) | 3.37 | 3.37 | 3.37 | ✓ |
| Δ_safety 7B | +0.626 | +0.626 | +0.6260 | ✓ |
| Δ_ethics 7B | +0.464 | +0.464 | +0.4640 | ✓ |
| Δ_safety 13B | +0.652 | +0.652 | +0.6520 | ✓ |
| Δ_ethics 13B | +0.422 | +0.422 | +0.4220 | ✓ |
| Δ_safety 70B | +0.638 | +0.638 | +0.6380 | ✓ |
| Δ_ethics 70B | +0.386 | +0.386 | +0.3860 | ✓ |
| Scale-only ρ | −0.771, p=0.0008 | −0.771, p=0.0008 | −0.7706, p=0.0008 | ✓ |
| Bonferroni α | 0.0033 | 0.0033 | 0.0033 | ✓ |

---

## Mathematical Validity Analysis

### 1. Bonferroni Correction
α = 0.05/15 = 0.003333... → rounds to **0.0033**. Paper's claim is correct. ✓

### 2. Degrees of Freedom After R1 Fix
Algorithm 1 (R1 revised): `df=12`, with comment `n − k_covariates − 2 = 16 − 2 − 2 = 12`. This is consistent with Section 6.2 ("df=12"). The h-e1/04_validation.md states `df_residual: 12`. All three sources agree on df=12. ✓

**p-value plausibility check for safety–privacy (ρ=0.971, df=12):**
- t = 0.971 × √(12 / (1 − 0.971²)) = 0.971 × √(12 / 0.057) ≈ 0.971 × 14.49 ≈ 14.07
- For t=14.07, df=12, two-tailed: p ≈ 8–9 × 10⁻⁸
- Paper reports p=8.77e-09 (an order of magnitude smaller than the manual estimate)
- **FLAG:** The reported p=8.77e-09 is plausible only if df is closer to 14, not 12. At df=12, t=14.07 yields p ≈ 5e-8. The discrepancy is less than 10× but is still notable. If df=12 is correct as stated, p=8.77e-09 is slightly too small. This may reflect a computational rounding artifact or the scipy implementation, not a fundamental error, but it warrants noting. The significance claim is not affected (8.77e-09 << 0.0033 regardless).

### 3. Average Delta Calculations
- Δ_safety average: (0.626 + 0.652 + 0.638) / 3 = 1.916 / 3 = **0.6387** → paper rounds to "+0.63". Correct. ✓
- Δ_ethics average: (0.464 + 0.422 + 0.386) / 3 = 1.272 / 3 = **0.424** → paper rounds to "+0.42". Correct. ✓

### 4. MST Mean Bootstrap Frequency
(1.000 + 1.000 + 0.956 + 0.941 + 0.688) / 5 = 4.585 / 5 = **0.917**. Paper's 0.917 claim is correct. ✓

### 5. 50% Compression Claim
3 dimensions / 6 dimensions = 50%. Claim is arithmetically correct. ✓

### 6. Binomial Sign Test Reporting
n=3, all 3 positive: minimum achievable p (one-sided binomial) = (0.5)³ = 0.125. Paper reports "p=0.125, minimum achievable for n=3." Correct and properly caveated. ✓

---

## R1 Fix Verification

| R1 Fix | Required Change | Verified in R1 Paper? |
|--------|----------------|----------------------|
| 1. Tumminello year | All "2007" → "2005" | ✓ Section 2.3: "Tumminello et al., 2005"; Section 3.4: "Tumminello et al., 2005"; Introduction Contribution 4: "Tumminello et al., 2005" |
| 2. df in Algorithm 1 | df=14 → df=12 with explanation | ✓ Algorithm 1 shows `df=12` with 4-line explanatory comment |
| 3. "First, to our knowledge" hedge | Add hedge in all 3 locations | ✓ Introduction: "The first, to our knowledge, systematic partial Spearman..."; Conclusion: "The first, to our knowledge, systematic partial Spearman..." |
| 4. Epoch AI comparison caveat | Add methodological inequivalence note | ✓ Section 2.3 adds explicit paragraph on partial vs raw distinction; Section 4.3 adds parenthetical caveat |

All 4 R1 MAJOR fixes are correctly applied. ✓

---

## Part 1: Accuracy Check (Persona 1 — R2)

### FATAL-ACC-1: Table 1 Values Diverge from h-e1/04_validation.md

**Severity: FATAL**

The paper's Table 1 reports 8 significant pairs with specific ρ and p values. The ground truth YAML confirms these values. However, the h-e1/04_validation.md — the primary Phase 4 validation file — reports a **completely different set of 8 significant pairs** with different ρ and p values:

| Pair | Paper Table 1 | h-e1/04_validation.md | Matches? |
|------|--------------|----------------------|----------|
| Truthfulness–Fairness | ρ=0.734, p=9.84e-04 | ρ=0.9353, p=9.21e-07 | ✗ |
| Fairness–Privacy | ρ=0.912, p=2.41e-06 | ρ=0.8941, p=1.61e-05 | ✗ |
| Privacy–Machine_Ethics | ρ=0.859, p=1.64e-05 | ρ=0.8588, p=8.37e-05 | ✗ |
| Safety–Machine_Ethics | ρ=0.841, p=3.22e-05 | ρ=0.8412, p=1.63e-04 | ✗ (p only) |
| Fairness–Machine_Ethics | ρ=0.821, p=7.12e-05 | ρ=0.7824, p=9.43e-04 | ✗ |
| Truthfulness–Safety | ρ=0.698, p=2.31e-03 | NOT in h-e1 sig list | ✗ |
| Robustness–Truthfulness | ρ=0.612, p=1.17e-02 | NOT in h-e1 sig list | ✗ |
| Truthfulness–Privacy | NOT in paper | ρ=0.7324, p=2.90e-03 | ✗ |
| Safety–Fairness | NOT in paper | ρ=0.8588, p=8.37e-05 | ✗ |

Additionally, h-e1/04_validation.md lists **"Safety–Fairness"** and **"Truthfulness–Privacy"** as two of the 8 significant pairs — but these pairs appear nowhere in the paper's Table 1 or ground truth YAML.

**Interpretation:** One of two scenarios:
1. The h-e1 validation file reflects an earlier experimental run with different model data ordering or a different random seed, and the ground truth YAML reflects a later, corrected run. In this case the paper values may be correct but the Phase 4 validation file is a stale artifact — this must be documented.
2. The paper's Table 1 values were updated from an intermediate analysis run that does not correspond to the final h-e1 code execution — the ground truth YAML was generated from a different output than the h-e1 validation file.

Either way, **the primary validation file and the paper's primary results table are inconsistent.** This is a FATAL issue for reproducibility: a reviewer or reader who reads h-e1/04_validation.md and tries to reproduce Table 1 will get different numbers. The paper cannot be submitted without reconciling these two artifacts.

**Recommended action:** Determine which set of values is correct (re-run h-e1/code/main.py and compare outputs). Update either the validation file or the paper/ground truth to reflect the single authoritative run. Document the discrepancy and its resolution.

---

### MAJOR-ACC-2: Li et al. 2025 Incomplete Citation — Unfixed from R1

**Severity: MAJOR**

The R1 review flagged this as a MINOR issue for human review. However, for a paper submitted to ICML 2025 (a top venue), an incomplete citation in the reference list is not a minor editorial issue — it is grounds for desk rejection or reviewer penalty.

Reference as it appears in R1-revised paper:
> Li, X., et al. (2025). More RLHF, More Trust? [ICLR 2025 Oral — full citation pending verification].

This is unprofessional and signals incomplete literature work. Either:
1. Find the full citation (authors, venue, volume, pages or arXiv ID).
2. Remove the reference and reframe the sentence in Section 2.4 without it (the claim it supports — that RLHF doesn't automatically guarantee all dimensions — is independently supported by the paper's own findings).

The h-m1/04_validation.md cites this as "Li, Krishna, Lakkaraju (2025). 'More RLHF, More Trust?' ICLR 2025 Oral." The authors are known. The full citation should be trivially completable.

**Fix:** Update reference to:
> Li, X., Krishna, R., & Lakkaraju, H. (2025). More RLHF, More Trust? *ICLR 2025*.

---

### MAJOR-ACC-3: Wang et al. 2025 arXiv:2509.03871 — Temporally Impossible Citation

**Severity: MAJOR**

The arXiv ID format `2509.XXXXX` indicates submission in **September 2025**. The paper is dated **2026-08-04** — which is fine — but the stated knowledge cutoff is **August 2025**. An arXiv paper submitted September 2025 cannot have been read and cited by a paper written in August 2025.

If the paper was actually finalized in August 2026 (as the date field says), then citing a September 2025 preprint is chronologically valid. But this creates a different problem: the paper claims to be an ICML 2025 submission (format: "ICML2025" in frontmatter, date "2026-08-04"). ICML 2025 submissions would have been due in early 2025, making a September 2025 preprint impossible to cite.

The citation is internally inconsistent with the paper's own claimed submission timeline. This will be flagged by reviewers who check arXiv IDs.

**Recommended action:** Either (1) replace with an established citation that can be verified, or (2) remove and rephrase — the claim in Section 2.2 ("reasoning LLMs show worse safety and privacy performance") is peripheral to the main argument and the paper does not depend on it.

---

## Part 2: Engagement Check (Persona 2 — R2)

No new FATAL or MAJOR engagement issues in the R1 revision. The R1 fixes did not introduce structural problems. The previous R1 concern about Section 4 redundancy with Section 3 remains — still a space concern for 8-page ICML format, but not a new R2 finding.

---

## Part 3: Credibility Check (Persona 2 — R2)

### MAJOR-CRED-1: H-E2 Original Failure Not Disclosed in Paper Body

**Severity: MAJOR**

The ground truth YAML records: "H-E2 (original) used full-topology stability = 0.606 (FAIL). H-E2-v2 uses Tumminello mean per-edge frequency = 0.917 (PASS)."

The paper uses "H-E2-v2" as the label for RQ4 (Section 5.4 heading) and mentions "Tumminello et al., 2005 metric" — but **nowhere in the paper does it state that the original metric failed and that the metric was changed mid-study.** A skeptical reviewer will:

1. Notice the "v2" suffix and ask what happened to "v1."
2. If they discover the original H-E2 metric (full-topology stability = 0.606) failed the 0.90 threshold, they will question whether the metric change was principled or opportunistic (i.e., "they changed the metric until they got a passing result").

The h-e2-v2/04_validation.md is transparent about this: "H-E2 failed the secondary gate with topology_stability=0.606... H-E2-v2 adopts the Tumminello (2007) standard..." But the paper does not relay this context.

**Recommended fix:** Add one sentence in Section 3.4 or Section 5.4 acknowledging the metric choice: e.g., "We use mean per-edge bootstrap frequency [Tumminello et al., 2005] rather than full-topology matching, as the latter is near-impossible for n=16 when one edge has near-tie geometry (pilot: full-topology stability=0.606)." This makes the methodological choice transparent and defensible rather than appearing as silent metric-switching.

---

### Confirmed Credibility Items (no new issues)

- The "first, to our knowledge" hedge is now correctly applied in all 3 locations. ✓
- Epoch AI comparison caveat is adequate. ✓
- Sign test p=0.125 is correctly reported as minimum achievable. ✓
- Machine_ethics–privacy 0.688 frequency is correctly described as "near-tie geometry" — this is accurate and well-caveated. ✓
- scipy implementation note (not sklearn) is present in Section 3.3. ✓
- The H-M3 clustering result diverged from prediction (privacy RLHF-sensitive, not insensitive) — the paper correctly discloses this in Section 5.3 and Discussion. ✓

---

## Part 4: Human Review Notes (New Issues Only)

1. **p-value plausibility at df=12 for safety–privacy (p=8.77e-9):** Manual calculation yields p≈5e-8 at df=12, t=14.07. The paper's 8.77e-09 is about 5× smaller. This may reflect scipy's internal precision or a marginally different ρ in the actual computation (0.9706 rounds to 0.971 but uses more digits internally). Not a claim-changing difference, but worth noting for the human reviewer to verify by running the code directly.

2. **h-e2-v2/04_validation.md still says "Tumminello (2007)":** The h-e2-v2 validation file itself uses the pre-R1 incorrect citation year. The paper is now correct ("2005") but the supporting validation file is inconsistent. Minor artifact-level issue, but creates confusion if someone reads the validation file.

3. **Liang et al. 2022 vs 2023 — still unfixed:** Introduction cites "Liang et al., 2022" but the reference entry shows "(2023). Transactions on Machine Learning Research." This was flagged in R1 as a MINOR issue but was not corrected in R1-revised paper. The TMLR publication date is the authoritative one (2023).

4. **scipy implementation claim in Section 3.3:** The paper correctly claims scipy was used (not sklearn). This is confirmed by h-m3/04_validation.md which says "scipy.cluster.hierarchy.linkage (NOT sklearn; see sklearn issue #27655)." ✓ No issue.

---

## Summary for Revision Agent

### Priority 1: FATAL — Must Resolve Before Any Further Steps

**[FATAL-ACC-1] Table 1 vs h-e1/04_validation.md divergence:** The paper's Table 1 values (ρ and p for the 8 significant pairs) do not match the h-e1 Phase 4 validation file. The ground truth YAML matches the paper, not the validation file. Determine which run is authoritative (re-run h-e1/code/main.py), update the stale artifact, and ensure a single consistent set of values propagates to all documents.

### Priority 2: MAJOR — Fix Before Submission

**[MAJOR-ACC-2] Li et al. 2025 incomplete citation:** Use "Li, Krishna, Lakkaraju (2025)" from h-m1/04_validation.md. Complete the reference entry.

**[MAJOR-ACC-3] Wang et al. 2025 arXiv:2509.03871:** Temporally inconsistent with stated submission date. Replace with verifiable citation or remove.

**[MAJOR-CRED-1] H-E2 original failure not disclosed:** Add one sentence noting the metric change from full-topology (0.606, failed) to mean per-edge frequency (0.917, passed), with the methodological justification already present in h-e2-v2/04_validation.md.

### Priority 3: MINOR — Human Review

- Complete Liang et al. citation year (2022 → 2023 in-text)
- p=8.77e-9 at df=12 is slightly implausible per manual calculation; verify with scipy output
- Update h-e2-v2/04_validation.md to say "Tumminello (2005)" for consistency
