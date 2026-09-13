# Adversarial Review - Round 2 (Numerical Verification)

**Paper:** MMLU Scale Confounding in Alignment Benchmark Correlations: A Partial Spearman Diagnostic
**Reviewed:** 2026-07-30
**Round:** R2 — Numerical Verification and Credibility
**Reviewer:** Adversary Agent v2

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Mathematical Validity | 0 | 1 | Fisher z formula mismatch: paper states wrong formula |
| Baseline Fairness | 0 | 0 | N/A (observational study, no method baselines) |
| Signal Consistency | 0 | 0 | All core statistics verified against result JSONs |
| Metric Consistency | 0 | 0 | All rounding and proportion checks pass |
| RLHF Background Claim | 0 | 0 | Appropriately flagged as "prior iterations"; not in Phase 4 JSONs |
| **TOTAL** | **0** | **1** | **MINOR_REVISION** |

**Recommendation:** MINOR_REVISION — one formula correction required; all numerical values verified correct

---

## Serena MCP Verification Log

Serena MCP `list_dir` and `search_for_pattern` were unavailable via deferred tool schema. Direct bash searches and file reads were used instead — equivalent coverage.

| Search | Target | Method | Result |
|--------|--------|--------|--------|
| Search 1 | H-M2 raw_rho, partial_rho | Read `h-m2/code/results/h_m2_results.json` | FOUND: raw_rho=0.7321908..., partial_rho=0.3432340... |
| Search 2 | Fisher z / z_diff | Read `h-m2/code/results/h_m2_results.json` | FOUND: z_diff=6.967867..., p=3.2179e-12 |
| Search 3 | H-M1 R² values | Read `h-m1/code/results/h_m1_results.json` | FOUND: R2_mmlu_truthqa=0.4927, R2_mmlu_bbq=0.7634 |
| Search 4 | H-M3 sign test | Read `h-m3/code/results/h_m3_results.json` | FOUND: k_positive=146, n=300, p=0.6862 |
| Search 5 | H-E1 N values | Read `h-e1/experiment_results.json` | FOUND: N_complete=297, N_exact=296 |
| Search 6 | Fisher z code formula | Read `h-m2/code/analyze.py` lines 134–149 | FOUND: `SE = sqrt(2/(N-3))` (same-sample formula) |
| Search 7 | RLHF 3.406/321 claim | grep across all non-archive JSONs | NOT FOUND in Phase 4 result files; found in 045_validated_hypothesis.md as "prior pipeline" |

**Total searches performed:** 7

---

## Ground Truth Verification Table (R2)

All values read directly from Phase 4 result JSON files and compared to paper claims.

| Claim | Paper (R1) | Phase 4 JSON Value | Ground Truth YAML | Match? |
|-------|-----------|-------------------|-------------------|--------|
| N analysis | 296 | 296 (`h_m2_results.json`) | 296 | ✓ |
| N after join | 297 | 297 (`h-e1/experiment_results.json`: N_complete=297) | 297 | ✓ |
| raw_rho | 0.732 | 0.7321908219457882 | 0.7322 | ✓ (rounded) |
| partial_rho | 0.343 | 0.3432340664199131 | 0.3432 | ✓ (rounded) |
| fisher_z | 6.9679 / 6.97 | 6.967867265799412 | 6.9679 | ✓ |
| fisher_z_p | 3.22 × 10⁻¹² | 3.2178704145735537e-12 | 3.22e-12 | ✓ |
| reduction_pct | 53.1% / 53% | (0.7322−0.3432)/0.7322 = 53.1% | 53.1% | ✓ |
| raw_ci | (0.670, 0.780) | [0.67, 0.78] | [0.670, 0.780] | ✓ |
| partial_ci | (0.180, 0.492) | [0.18049, 0.49247] | [0.180, 0.492] | ✓ |
| raw_rho_p | 5.83 × 10⁻⁵¹ | 5.826760798468454e-51 | 5.83e-51 | ✓ |
| partial_rho_p | 1.40 × 10⁻⁹ | 1.4028822086390533e-09 | 1.40e-09 | ✓ |
| R²(MMLU×TruthfulQA) | 0.493 / 49.3% | 0.4926646001396736 | 0.4927 | ✓ |
| R²(MMLU×BBQ) | 0.763 / 76.3% | 0.7634225385589838 | 0.7634 | ✓ |
| rho(MMLU×TruthfulQA) | 0.702 | 0.7019007053278075 | 0.7019 | ✓ |
| rho(MMLU×BBQ) | 0.874 | 0.8737405441885959 | 0.8737 | ✓ |
| p(MMLU×TruthfulQA) | 3.15 × 10⁻⁴⁵ | 3.1478414281140597e-45 | 3.15e-45 | ✓ |
| p(MMLU×BBQ) | 5.01 × 10⁻⁹⁴ | 5.007790019017035e-94 | 5.01e-94 | ✓ |
| k_positive (sign test) | 146 | 146 | 146 | ✓ |
| N sign test | 300 | 300 | 300 | ✓ |
| proportion | 0.487 | 0.4866666... (= 146/300, rounds to 0.487) | 0.487 | ✓ |
| binomtest_p | 0.686 | 0.6861754232113881 | 0.686 | ✓ |
| CI overlap status | non-overlapping | "non-overlapping" | non-overlapping | ✓ |
| scenario | AMBIGUOUS | "ambiguous" | AMBIGUOUS | ✓ |
| N model families | 51 | — (in 045_validated_hypothesis.md) | 51 | ✓ |
| N families (≥3) | 30 | — | 30 | ✓ |
| **Fisher z formula** | √(1/(N−3) + 1/(N−4)) | **√(2/(N−3))** in code | N/A | **✗ MISMATCH** |

**Discrepancies found:** 1 (formula notation; does not affect numerical results)

---

## Mathematical Validity Analysis

### Check A: Reduction Percentage

(0.7322 − 0.3432) / 0.7322 = 0.3890 / 0.7322 = **0.5313 = 53.1%**

Paper claims 53.1%. **PASS ✓**

### Check B: R² from rho

- rho(MMLU×TruthfulQA) = 0.7019 → R² = 0.7019² = **0.4927**. Paper says 0.493. **PASS ✓**
- rho(MMLU×BBQ) = 0.8737 → R² = 0.8737² = **0.7634**. Paper says 0.763. **PASS ✓**

### Check C: Proportion in Sign Test

k=146, N=300 → 146/300 = 0.48667. Rounded to 3 decimal places = **0.487**. Paper says 0.487. **PASS ✓**

### Check D: CI Consistency

- Raw rho BCa 95% CI: JSON = [0.67, 0.78]. Paper says (0.670, 0.780). **PASS ✓**
- Partial rho BCa 95% CI: JSON = [0.18049, 0.49247]. Paper says (0.180, 0.492). **PASS ✓**

### Check E: Non-Overlapping CI Test

Raw CI lower = 0.670. Partial CI upper = 0.492. Since 0.492 < 0.670, the intervals do NOT overlap. The paper's claim of "non-overlapping BCa 95% CIs" is **mathematically verified ✓**.

### Check F: Fisher Z Formula (CRITICAL ISSUE)

**The paper presents an incorrect formula.**

**Paper states (Section 3.1, post-R1 revision):**
> z = (z_raw − z_partial) / √(1/(N−3) + 1/(N−4))

This is the **independent-samples** Fisher z difference formula, applicable when comparing correlations from two *independent* samples.

**Actual code (`h-m2/code/analyze.py`, lines 134–139):**
```python
def fisher_z_difference_test(raw_rho: float, partial_rho: float, N: int) -> dict:
    """Same-sample Fisher z difference test. SE=sqrt(2/(N-3))."""
    se = float(np.sqrt(2.0 / (N - 3)))
    z_diff = float((z_raw - z_partial) / se)
```

This is the **same-sample** (correlated/dependent) Fisher z difference formula.

**Numerical verification:**

| Formula | SE | z value |
|---------|-----|---------|
| √(2/(N−3)) — same-sample [CODE] | √(2/293) = 0.08257 | **6.9679** ← matches JSON |
| √(1/(N−3) + 1/(N−4)) — independent [PAPER] | √(1/293 + 1/292) = 0.08266 | 6.9619 ← does NOT match |

The reported z = 6.9679 is computed from `√(2/(N−3))`, not from the formula printed in the paper. **The formula in the paper is wrong.**

**Severity assessment:** MAJOR. The formula determines which statistical test was actually performed. The same-sample formula is arguably MORE appropriate here (raw_rho and partial_rho are computed on the same N=296 models, so they are correlated — the same-sample correction is theoretically correct). However:
1. The R1 review (ACC-MAJOR-002) flagged that the original `N−3−1` notation was misleading; the revision replaced it with `1/(N−3) + 1/(N−4)` which is a *different wrong formula* — it's the independent-samples formula, not what the code computes.
2. A reviewer who recomputes the z-statistic using the formula printed in the paper will get z = 6.9619 instead of 6.9679 — a small but verifiable discrepancy that will flag as a reproducibility concern.
3. The code's docstring correctly documents the formula as `SE=sqrt(2/(N-3))`, providing the ground truth.

**Fix required:** Replace the formula in Section 3.1 with:
> z = (z_raw − z_partial) / √(2/(N−3))

Add a note that this is the same-sample (dependent-correlations) formula, appropriate because raw_rho and partial_rho are both estimated from the same N=296 models.

---

## Baseline Fairness Assessment

This paper is **observational and descriptive**, not a comparative ML method paper. It does not benchmark YouRA or any proposed model against baselines in a table. Therefore, traditional "baseline fairness" checks (hyperparameter parity, same train/test split, cherry-picking of comparison metrics) do not apply.

What applies instead: is the **population characterization fair**? Checks:
- N=296 is the complete set after inner join and dropna — no cherry-picking of convenient model subsets. **FAIR ✓**
- ARC Challenge proxy limitation is disclosed repeatedly. **FAIR ✓**
- Model family clustering for BCa bootstrap accounts for within-family correlation. **FAIR ✓**
- No specific model families are compared against others in a way that could be unfair. **N/A**

**Baseline fairness: no issues found.**

---

## RLHF Background Claim Verification

**Claim:** "Prior iterations of this research pipeline established a confirmed RLHF improvement on TruthfulQA MC2 of +3.406 points (BCa CI [+2.589, +4.212]) across 321 base/chat pairs"

**Search result:** This value does NOT appear in any Phase 4 experiment result JSON files (h-e1, h-m1, h-m2, h-m3). It appears only in:
- `045_validated_hypothesis.md` (validated hypothesis document, not Phase 4 code output)
- `03_refinement.yaml` and related discussion documents

**Assessment:** The paper correctly labels this as coming from "prior iterations of this research pipeline" and does not claim it as a result of the current experiment. The ground truth YAML (`065_ground_truth.yaml`) lists it under `background_claims`, not `primary_results`. This framing is appropriate. The values cannot be verified against current Phase 4 JSONs but their source is clearly scoped.

**Status: ACCEPTABLE — appropriately flagged as background claim from prior iterations ✓**

---

## Scenario Boundary Check

partial_rho = 0.343 (from JSON: 0.3432340664199131)
Pre-specified grey zone: −0.20 < partial_rho < 0.40
0.343 ∈ (−0.20, 0.40) → **AMBIGUOUS ✓**

BCa CI [0.180, 0.492] spans the +0.40 boundary (lower 0.180 < 0.40 < upper 0.492), confirming the ambiguity is genuine, not due to a point estimate near the boundary.

Robustness checks from JSON (`h_m3_results.json`):
- `ablation_boundary_tight`: scenario = "ambiguous" ✓
- `ablation_boundary_wide`: scenario = "ambiguous" ✓

**Scenario boundary check: PASS ✓**

---

## FATAL Issues

**None found.**

---

## MAJOR Issues

### MATH-MAJOR-001: Fisher Z Formula in Paper Does Not Match Code Implementation

**Location:** Section 3.1, equation block for z-statistic  
**Severity:** MAJOR (formula reproducibility)

**What the paper says (R1 revision):**
> z = (z_raw − z_partial) / √(1/(N−3) + 1/(N−4))

**What the code actually computes** (`h-m2/code/analyze.py`, line 138):
```python
se = float(np.sqrt(2.0 / (N - 3)))
```

**Numerical consequence:** z from paper formula = 6.9619; z from code = 6.9679 (matches reported value). The discrepancy is 0.006 — small, but a careful reader who recomputes will notice.

**Why the code formula is defensible:** raw_rho and partial_rho are computed on the *same* N=296 observations, making them statistically dependent. The same-sample formula √(2/(N−3)) is standard for testing H₀: ρ₁ = ρ₂ when both correlations share the same sample (Meng et al., 1992; Steiger, 1980). The R1 revision introduced a superficially-plausible independent-samples formula that is technically less correct for this use case.

**Fix:** Change Section 3.1 formula to:
> z = (z_raw − z_partial) / √(2/(N−3))

Add: "where we use the same-sample (dependent-correlations) Fisher z standard error appropriate when both ρ estimates are computed from the same N observations (Steiger, 1980)."

This change actually *strengthens* the paper's methodological transparency, because the same-sample formula is the theoretically appropriate choice.

---

## Minor Issues (Carried Forward from R1 / New)

**From R1 (status check):**
- R1-ACC-MAJOR-001 (N=299 in section file): Verify that `/docs/youra_research/paper/sections/` files are updated if they are used to regenerate the paper.
- R1-CRED-MAJOR-001 ("first" without hedge in Conclusion): Paper R1 Section 7 still uses "the first direct application" — check if this was fixed in R1 revision. The compiled `06_paper_r1.md` Section 7 reads "Our work provides, to our knowledge, the first direct application" — **this appears FIXED** in R1. ✓

**New minor issues:**
- **MATH-MINOR-001:** The formula correction (MATH-MAJOR-001) should add a citation: Steiger (1980) "Tests for comparing elements of a correlation matrix" — standard reference for the same-sample z-test. Without it, the formula is correct but uncited.

---

## Human Review Notes

1. **Formula fix is net positive for the paper:** The same-sample Fisher z formula `√(2/(N−3))` is not only correct for the code but also theoretically superior to the independent-samples formula (since raw and partial correlations are estimated from the same sample). The R1 revision accidentally introduced a formula that is both wrong and suboptimal. Fixing this should be framed as a methodological clarification, not a correction.

2. **Numerical results are all verified:** Every primary quantitative claim in the R1 paper was checked against Phase 4 result JSONs. No numerical errors were found beyond the formula notation issue.

3. **CI rounding subtlety in H-M2 results:** The JSON records `ci_raw = [0.67, 0.78]` (2 decimal places) while `ci_partial = [0.18049431509038102, 0.4924694713121477]` (full precision). The paper rounds partial CI to [0.180, 0.492] — correct. The raw CI is stored as [0.67, 0.78] in the JSON itself (already rounded), reported in paper as [0.670, 0.780] — trailing zero added but numerically equivalent. No issue.

4. **H-M3 proportion rounding:** 146/300 = 0.48667, rounded to 0.487 in paper. Correct standard rounding. Ground truth confirms 0.487.

---

## Summary

| Prediction | Status | Key Metric |
|------------|--------|------------|
| All primary numerics verified against Phase 4 JSONs | **VERIFIED** | 24/24 numerical claims match |
| Mathematical derivations correct | **VERIFIED** | Checks A–E all pass |
| Fisher z formula matches code | **FAIL** | Paper states independent-samples formula; code uses same-sample formula |
| CI non-overlap claim | **VERIFIED** | 0.492 < 0.670 confirms non-overlap |
| RLHF background claim appropriately scoped | **VERIFIED** | Framed as prior iterations; not in Phase 4 JSONs |
| Scenario boundary check | **VERIFIED** | AMBIGUOUS confirmed by robustness ablations |

**One required fix before publication:** Correct Fisher z formula in Section 3.1 from `√(1/(N−3) + 1/(N−4))` to `√(2/(N−3))` with same-sample citation.

---

*Adversarial Review R2 — Numerical Verification*
*Completed: 2026-07-30*
