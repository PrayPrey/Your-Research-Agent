# Adversarial Review — Round 1 (R1)

**Paper:** Do Architecture Families Leave Fingerprints in Adversarial Failures? Measuring Δ*-Vector Profiles Across Transformer Families  
**Reviewed:** 2026-08-02T00:00:00  
**Reviewer:** Adversary Agent v2  
**Round:** R1 — Accuracy and Engagement

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Accuracy | 1 | 1 | CRITICAL |
| Engagement | 0 | 1 | NEEDS_WORK |
| Credibility | 1 | 2 | CRITICAL |
| **TOTAL** | **2** | **4** | **MAJOR_REVISION** |

**Recommendation:** MAJOR_REVISION — Two FATAL issues must be fixed before paper is credible. All MAJOR issues addressable without changing findings.

---

## Part 1: Accuracy Check (Persona 1 — Accuracy Checker)

### Ground Truth Summary

| Metric | Paper Claims (pre-fix) | Ground Truth (065_ground_truth.yaml) | Match? |
|--------|------------------------|--------------------------------------|--------|
| η²=0.293 | 0.293 | 0.293 | ✓ |
| adv_rte η² | 0.592 | 0.592 | ✓ |
| LOMO accuracy | 0.333 | 0.333 | ✓ |
| N=9 → 40% power | ~40% | ~40% | ✓ |
| N≥15 for 80% power | 15 | 15 | ✓ |
| adv_qqp p-value | **~0.12** | **0.265** | ✗ |
| adv_qnli p-value | **~0.12** | **0.295** | ✗ |
| adv_sst2 p-value | **~0.15** | **0.360** | ✗ |
| adv_mnli p-value | **~0.20** | **0.695** | ✗ |
| 5/6 categories above η²=0.15 | 83% | 83% | ✓ |

### FATAL Issues — Accuracy

#### FATAL-ACC-001: Fabricated Per-Category p-Values in Table 1

**Location:** Section 5.1 Results, Table 1  
**Issue:** Four per-category p-values in Table 1 are approximations inconsistent with actual permutation MANOVA results. The paper reports `~0.12, ~0.12, ~0.15, ~0.20` for adv_qqp, adv_qnli, adv_sst2, adv_mnli respectively. Actual values from ground truth / stats_results.json are `0.265, 0.295, 0.360, 0.695`.  
**Evidence:** Ground truth `065_ground_truth.yaml` → per-category p-values listed under confirmed sources. Paper claims `~0.12` for adv_qqp vs actual `0.265` — factor of 2× discrepancy.  
**Impact:** FATAL — fabricated p-values falsely suggest near-significance for four categories. Actual values are all non-significant (0.265–0.695). A reviewer checking against raw output would immediately flag this as a credibility-destroying error.  
**Required Fix:** Replace all approximated p-values with exact permutation p-values from stats_results.json.

### MAJOR Issues — Accuracy

#### MAJOR-ACC-001: Mixed-Effects Sensitivity Check Results Missing from Paper

**Location:** Section 3.5 Statistical Methods (mentions mixed-effects model) / Section 5 Results (no corresponding result section)  
**Issue:** Section 3.5 describes a mixed-effects sensitivity check but Section 5 contains no corresponding results. The mixed-effects model was run (per ground truth Phase 4 validation) and produced an `encoder×adv_mnli p=0.014` interaction — a notable result (though confounded by model degeneracy at N=9). Omitting it entirely looks like selective reporting.  
**Evidence:** Ground truth indicates the mixed-effects check was part of methodology. The absence in results creates an asymmetry between promised methods and delivered results.  
**Suggested Fix:** Add Section 5.2b reporting mixed-effects results with appropriate degeneracy caveats: "The mixed-effects model reached convergence but is severely underdetermined at N=9 — most interaction terms show p≈1.0 or NaN due to collinearity. The encoder×adv_mnli interaction (p=0.014) is consistent with the MANOVA direction but should not be read as independent confirmation given model degeneracy."

---

## Part 2: Engagement Check (Persona 2 — Bored Reviewer)

### Bored Reviewer Verdict

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | ✓ | Opens with a concrete puzzle question; gives numeric result immediately |
| Problem clear in 1 min? | ✓ | Security auditor motivating example is crisp |
| Novelty clear in 2 min? | ✓ | Four-part contribution list is unambiguous |
| Figure 1 self-explanatory? | ✓ | Heatmap shows family clustering visually |
| Would continue reading? | ✓ | Yes — opening question is distinctive |

**Attention Lost At:** Introduction paragraph 3 ("The core problem runs deeper...") — mechanism description before reader buy-in is slightly premature

**Overall engagement verdict:** NEEDS_WORK (one MAJOR engagement issue)

### MAJOR Issues — Engagement

#### MAJOR-ENG-001: Approximate p-Values Unprofessional (Same Root as FATAL-ACC-001)

**Location:** Section 5.1, Table 1  
**Issue:** A bored reviewer scanning Table 1 will immediately notice `~0.12, ~0.12, ~0.15, ~0.20` — the tilde prefixes signal that these are rounded guesses, not actual results. This raises immediate questions about rigor. "If the authors don't have their own p-values, what else is approximate?"  
**Reader Impact:** Loss of confidence in the entire results section.  
**Required Fix:** Same as FATAL-ACC-001 — replace with exact values.

### Human Review Notes (Engagement — MINOR)

| Location | Note | Type |
|----------|------|------|
| Intro para 3 | Mechanism description (bidirectional attention redistribution) appears before reader buy-in; consider reordering | clarity |

---

## Part 3: Credibility Check (Persona 3 — Skeptical Expert)

### Novelty Claims Audit

| Claim | Location | Verified? | Prior Work |
|-------|----------|-----------|------------|
| "first formal effect-size measurement" of between-family Δ* clustering | Introduction, Section 1 | ✓ | Neerudu et al. (2023) does directional comparison but no η² — claim holds |
| Permutation MANOVA as novel choice for small N | Section 3.5 | ✓ | Standard method, not overclaimed |
| Δ*-vector framework introduced here | Section 3.2 | ✓ | Framework itself appears novel as defined |

### Baseline Fairness Audit

Not applicable — this is not a baseline comparison study. Statistical reference points (chance, η²=0.15 threshold) are theoretically grounded and properly specified as pre-specified criteria.

### FATAL Issues — Credibility

#### FATAL-CRED-001: Pillai's Trace Claimed Equivalent to η² ("≡")

**Location:** Section 3.5 Statistical Methods  
**Issue:** The paper states "Test statistic: Pillai's trace (≡ η² in three-group case)." This is mathematically incorrect. Pillai's trace and η² are both bounded [0,1] and monotonically related in the balanced three-group case, but they are not identical (≡). Pillai's trace = Σ(λ_i/(1+λ_i)); η² = SS_between/SS_total. The claim of exact equivalence is false and any reviewer with multivariate statistics background will flag this immediately.  
**Evidence:** Standard multivariate statistics (Johnson & Wichern, Applied Multivariate Statistical Analysis).  
**Impact:** FATAL — false mathematical equivalence claim directly undermines methodological credibility. A statistics-literate reviewer would reject on this basis alone.  
**Required Fix:** Correct to: "Test statistic: Pillai's trace; effect size: η² = SS_between/SS_total. In the balanced three-group case, Pillai's trace and η² are monotonically related (both bounded [0,1]) but not identical — we report η² throughout for interpretability."

### MAJOR Issues — Credibility

#### MAJOR-CRED-001: CheckList Absence Unexplained

**Location:** Section 4.1 Datasets  
**Issue:** Section 2.1 Related Work cites Ribeiro et al. (2020) CheckList as a key evaluation paradigm and includes it in the survey of adversarial benchmarks. The experimental setup (Section 4) does not include CheckList, with no explanation. A skeptical reviewer will ask: "Why discuss CheckList in Related Work but not evaluate it? Did they try and fail? Did it give inconvenient results?"  
**Evidence:** Related Work section includes CheckList as a relevant benchmark, yet Datasets table contains only AdvGLUE and ANLI.  
**Impact:** Selective reporting concern — appears to cherry-pick benchmarks.  
**Suggested Fix:** Add a note to Section 4.1: "CheckList was included in the original design but not evaluated in this experiment due to [missing package installation / scope limitation]; it is included in the h-e1-v2 design."

#### MAJOR-CRED-002: Mixed-Effects Model Omitted from Results (Same as MAJOR-ACC-001)

**Location:** Section 5 Results  
**Issue:** Methodological commitment in Section 3.5 not fulfilled in results. Same fix as MAJOR-ACC-001 — add Section 5.2b with degeneracy caveat.  
**Suggested Fix:** See MAJOR-ACC-001.

### Human Review Notes (Credibility — MINOR)

| Location | Note | Type |
|----------|------|------|
| Section 3.5 | MANOVA rank-deficiency caveat absent; at N=9, K=6, technically fine but worth one sentence | clarity |
| Section 2.2 | Zhang et al. (2026) / Arora et al. (2026) citation inconsistency between main paper and section files | style |

---

## Part 4: Human Review Notes

> These are minor issues for human review during final polish. NOT fixed by Revision Agent.

| Location | Note | Type |
|----------|------|------|
| Intro para 3 | Mechanism description premature; consider reordering within paragraph | clarity |
| Section 2.2 | Zhang et al. (2026) — anachronistic citation risk for 2026-08-02 submission | style |
| Section 3.5 | MANOVA rank note for pedantic reviewer | clarity |
| Various | Citation inconsistency: Wang et al. (2021) vs Zeng et al. (2021) for AdvGLUE between main paper and section files | style |

---

## Summary for Revision Agent

### Priority Fix List

1. **FATAL-ACC-001 / MAJOR-ENG-001:** Replace approximate p-values (~0.12, ~0.12, ~0.15, ~0.20) in Table 1 with exact permutation values (0.265, 0.295, 0.360, 0.695) — MUST FIX
2. **FATAL-CRED-001:** Correct "Pillai's trace ≡ η²" to accurate monotone-relationship description — MUST FIX
3. **MAJOR-ACC-001 / MAJOR-CRED-002:** Add Section 5.2b with mixed-effects results and degeneracy caveat — SHOULD FIX
4. **MAJOR-CRED-001:** Add CheckList absence explanation to Section 4.1 — SHOULD FIX

### Key Concerns

- Approximate p-values are the most urgent fix — they are the most obvious error a reviewer will catch
- Pillai's trace equivalence claim will draw immediate fire from any statistician reviewer

### What's Working

- Abstract is excellent: opens with a crisp question, delivers numeric result, quantifies the limitation honestly
- LOMO null result is framed correctly with N-degeneracy caveat — no overclaiming
- Power analysis as a "design contribution" framing is clever and accurate
- All required limitations from ground truth are present and correctly framed
- The four-contribution structure is clear and non-redundant
