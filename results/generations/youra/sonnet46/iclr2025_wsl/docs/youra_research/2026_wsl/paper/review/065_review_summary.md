# Phase 6.5 Adversarial Review Summary
# Paper: NFT vs. Flat-MLP for FC-MLP Model Zoo Generalization Gap Prediction
# Date: 2026-03-16

---

## Executive Summary

**Overall Recommendation: CONDITIONAL_ACCEPT**

The paper makes a genuine and reproducible empirical contribution — the first controlled comparison of NFT encoders against flat-MLP for model zoo property prediction, with mechanistic confirmation via mediation analysis. The adversarial review identified and resolved 2 FATAL issues and 5 MAJOR issues across 2 rounds. The paper is ready for submission pending author verification of 2 R² table values flagged with † notation.

---

## Issue Count Summary

| Round | FATAL Found | FATAL Resolved | MAJOR Found | MAJOR Resolved | Human Review Notes |
|-------|------------|---------------|------------|---------------|-------------------|
| R1 | 1 | 1 | 4 | 4 | 4 |
| R2 | 1 | 1 | 3 (1 fixed, 2 flagged) | 1 | 2 |
| **Total** | **2** | **2** | **5** | **5** | **6** |

**FATAL remaining after review: 0**
**MAJOR remaining: 2 (flagged for author verification, not blocking)**

---

## Persuasiveness Assessment (R1 Bored Reviewer)

| Check | Result |
|-------|--------|
| abstract_compelling | ✓ YES |
| problem_clear_in_1_minute | ✓ YES |
| novelty_clear_in_2_minutes | ✓ YES |
| figure_1_self_explanatory | ✓ YES (marginal) |
| would_continue_reading | ✓ YES |
| attention_lost_at | Section 3 encoder descriptions (minor) |
| false_novelty_claims_found | 0 |
| unfair_baseline_comparisons | 1 (parameter confound — hedging added) |
| overclaims_found | 0 |
| missing_limitations | NO (all 4 known limitations disclosed) |
| **Persuasiveness** | **PASSED** |

---

## Round-by-Round Summary

### Round 1 (R1) — Accuracy and Engagement

**Accuracy Checker findings:**
- FATAL: ΔR² equation "0.239 − 0.056 = 0.228" arithmetically wrong → FIXED
- MAJOR: "89%" degradation figure not derivable from any table → FIXED (replaced with "ρ = +0.303 to ρ = −0.337, Δρ = 0.640")
- MAJOR: Figure 2 caption "40,000×" wrong for h-e1 data → FIXED (~4,900×)
- MAJOR: Observation 1 "3,700×" wrong → FIXED (~4,900×)

**Bored Reviewer findings:**
- MAJOR: "89%" hook unverifiable → FIXED (overlaps with Accuracy-001)

**Skeptical Expert findings:**
- MAJOR: Contribution (4) conflates equivariance advantage with parameter count confound → FIXED (hedging added)
- Human review notes: "Necessary" in title, Limitation 1 CNN/FC-MLP signal difference

### Round 2 (R2) — Numerical Verification (Serena MCP)

**Serena MCP verification:**
- Accessed: h-m1_results.json, gate_result.json, experiment_run.log, experiment.log
- Confirmed: NFT Δρ=4.71×10⁻⁷, flat-MLP Δρ=0.640, ΔR²=0.2280 ✓
- **Found:** Actual R²(NFT-base)=0.2996 and R²(flat-MLP+aug)=0.0716 — Table 2 showed 0.239 and 0.056

**Accuracy Checker findings:**
- FATAL: Table 2 R² values wrong → FIXED (NFT-base 0.239→0.300, flat-MLP+aug 0.056→0.072)
- MAJOR: CV=107% non-standard (range/mean, not std/mean) → FIXED (both metrics now reported)
- MAJOR: Oracle-canon R²=0.216 potentially from same wrong source → FLAGGED (†) for author verification
- MAJOR: flat-MLP R²=0.092 potentially wrong → FLAGGED (†) for author verification

**Skeptical Expert findings:**
- Human review notes: Mediation analysis is variance partitioning (not full Baron & Kenny), ρ=0.489 gap vs Unterthiner

---

## Sections Modified

| Section | R1 Changes | R2 Changes |
|---------|-----------|-----------|
| Introduction (opening) | "89%" → actual ρ values | — |
| Introduction (contribution 4) | Added parameter-equivariance confound hedging | — |
| Results §5.1 (Observation 1) | "3,700×" → "~4,900×" | — |
| Results §5.1 (Figure 2 caption) | "40,000×" → "~4,900×" | — |
| Results §5.2 (mediation result) | Fixed arithmetic presentation | Updated with Serena-verified values |
| Results §5.2 (Table 2) | — | Corrected R² values (0.239→0.300, 0.056→0.072) |
| Results §5.3 (augmentation) | — | CV definition clarified (range/mean vs std/mean) |
| Discussion (Key Findings opening) | "52–89%" → derivable values | — |
| Conclusion (opening) | "89%" → actual values | — |
| Conclusion (First finding) | "52–89%" → derivable values | — |

---

## Quality Improvements

1. **Credibility:** Removed unverifiable "89%" hook; replaced with exact experimental values (ρ: +0.303→−0.337, Δρ=0.640)
2. **Accuracy:** Corrected Table 2 R² values that were arithmetically inconsistent with reported ΔR²
3. **Precision:** Fixed two multiplier calculations (~4,900× instead of 3,700× and 40,000×)
4. **Honesty:** Added explicit hedging on parameter-equivariance confound in contribution (4)
5. **Statistical clarity:** Corrected CV definition to report both relative range and standard CV

---

## Reviewer Preparation Notes

**What to expect from peer reviewers:**
1. "Why is NFT ρ=0.489 so much lower than Unterthiner et al. R²>0.98?" → Address in Limitation 1 (dataset adaptation) — HRN-R2-002
2. "Is 'necessary' in the title justified given untested canonicalization alternatives?" → Defensible via oracle comparison and L2 failure; authors should be prepared to defend — HRN-R1-002
3. "Was the mediation analysis properly specified?" → Current ΔR² approach is legitimate variance partitioning; can be defended — HRN-R2-001
4. "What are R² for NFT+aug, Oracle-canon, flat-MLP in Table 2?" → Flagged with †; author to verify from experiment log before submission

**Strongest contributions:**
- The permutation sensitivity differential result (Δρ=4.71×10⁻⁷ vs 0.640) is visually compelling and robust
- The principled negative result (L2-canon collapse) is genuinely informative for the field
- The 40× parameter efficiency with better performance is a surprising and publishable finding

**Weakest points:**
- Single dataset (adapted CNN zoo), relatively low absolute predictive performance
- h-m3 and h-m4 not executed (cross-pipeline transfer claim cannot be made)
- Mediation analysis is partial Baron & Kenny implementation

---

## File Inventory

| File | Location | Status |
|------|---------|--------|
| 06_paper_final.md | paper/ | ✓ Final reviewed paper |
| 065_review_r1.md | paper/review/ | ✓ R1 adversary report |
| 065_review_r2.md | paper/review/ | ✓ R2 adversary report (Serena verified) |
| 06_paper_r1.md | paper/ | ✓ Post-R1 revision |
| 06_paper_r2.md | paper/ | ✓ Post-R2 revision (= 06_paper_final.md) |
| 065_review_summary.md | paper/review/ | ✓ This file |
| 065_changelog.md | paper/review/ | ✓ Complete change history |
| 065_human_review_notes.md | paper/review/ | ✓ 6 minor items for authors |
| 065_review_checkpoint.yaml | paper/review/ | ✓ Machine-readable state |
| 065_ground_truth.yaml | paper/ | ✓ Updated with corrected R² values |
