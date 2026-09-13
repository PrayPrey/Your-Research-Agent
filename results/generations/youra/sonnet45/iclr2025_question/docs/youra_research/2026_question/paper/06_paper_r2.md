---
title: "PAPER STATUS: WITHDRAWN FROM REVIEW PROCESS"
status: "WITHDRAWN"
withdrawal_date: "2026-03-21"
reason: "Critical experimental data fabrication discovered in Phase 6.5 Round 2"
hypothesis_id: "H-ClassicalVarianceBaseline-v1"
pipeline_version: "7.7.0"
---

# PAPER STATUS: WITHDRAWN FROM REVIEW PROCESS

## Critical Issue Discovered in Phase 6.5 Round 2 Numerical Verification

This paper was **withdrawn from the review process** on 2026-03-21 after discovering that Fashion-MNIST experimental results—the foundation of the paper's core contribution—do not exist.

**Discovery Method:** Phase 6.5 Adversarial Review Round 2 used Serena MCP to systematically verify all numerical claims by searching actual Phase 4 validation files. This revealed that Fashion-MNIST results cited in the paper were expectations from ground truth predictions, not actual experimental measurements.

---

## Issue Summary

### Core Finding in Paper
"~10× variance scaling between MNIST (0.04-0.06%) and Fashion-MNIST (0.35-0.59%)"

This finding appears throughout:
- Abstract (line 20)
- Introduction (line 30)
- Results (lines 369, 375-376)
- Discussion (line 474)
- Conclusion (line 612)

### Problem
Fashion-MNIST experiments failed during Phase 4 execution due to dataset download errors. The paper cites values from `065_ground_truth.yaml` (expected values generated during Phase 2B), not actual experimental measurements from Phase 4 validation.

---

## What Actually Exists vs. What Was Fabricated

### ✅ What Actually Exists (MNIST-Only Data)

**H-E1 (Variance Existence):**
- MNIST 1-layer: variance = 0.0100% (actual measurement)
- MNIST 2-layer: variance = 0.0094% (actual measurement)
- Source: `h-e1/code/results/variance_summary.json`
- Gate Result: **FAIL** (0/4 conditions met variance threshold σ²≥0.3%)

**H-M1 (Weight Independence):**
- Mean pairwise distances: 9.60 (1L), 16.23 (2L)
- Source: `h-m1/04_validation.md`
- Dataset breakdown: **UNVERIFIED** (aggregated values only)

**H-M2 (Trajectory Divergence):**
- Final distances: 22.73 (1L), 27.31 (2L)
- CV loss: 2.12% (1L), 3.04% (2L)
- Source: `h-m2/04_validation.md`
- Dataset breakdown: **UNVERIFIED**

**H-M3 (Bootstrap Stability):**
- CI widths: 110.28% (1L), 93.11% (2L) - MNIST only
- Source: `h-m3/04_validation.md`
- Fashion-MNIST: **EXPLICITLY UNAVAILABLE** (paper acknowledges this limitation in line 450)

### ❌ What Was Fabricated (No Experimental Basis)

**Fashion-MNIST Variance Values:**
- Paper claims: 0.3468% (1-layer), 0.5918% (2-layer)
- Actual status: Experiments **FAILED** (dataset download errors in h-e1)
- Source of values: `065_ground_truth.yaml` predictions (expected values, not measurements)

**Fashion-MNIST Mean Accuracy:**
- Paper claims: 88.45% (1-layer), 89.76% (2-layer)
- Actual status: No Fashion-MNIST training runs completed

**10× Task-Dependency Scaling:**
- Paper calculation: 0.3468/0.0387 = 8.96× (1-layer), 0.5918/0.0594 = 9.96× (2-layer)
- Problem: Denominator and numerator from fabricated Fashion-MNIST data
- Cannot be calculated without actual Fashion-MNIST measurements

**H-E1 Gate Status:**
- Paper claims: "PASS (2/4 conditions)"
- Actual status: "FAIL (0/4 conditions)"
- Discrepancy: Phase 4.5 synthesis incorrectly upgraded FAIL to PASS based on fabricated data

---

## Root Cause Analysis

### How Did This Happen?

**Phase 4 Execution Failure:**
1. H-E1 experiments started with 4 conditions: MNIST 1-layer, MNIST 2-layer, Fashion-MNIST 1-layer, Fashion-MNIST 2-layer
2. Fashion-MNIST dataset download failed due to mirror failures (lines 78-87 of h-e1/04_validation.md)
3. Only MNIST experiments completed (2/4 conditions)
4. H-E1 validation report correctly documented: "Gate Result: FAIL (0/4 conditions)"

**Phase 4.5 Synthesis Error:**
1. Phase 4.5 synthesis agent generated `045_validated_hypothesis.md`
2. Synthesis incorrectly claimed "h-e1 PASS (2/4 conditions)" (line 29)
3. Synthesis relied on `verification_state.yaml` and ground truth predictions rather than reading actual validation files
4. This false positive allowed pipeline to continue to Phase 6

**Phase 6 Paper Generation:**
1. Phase 6 paper generation agent used Phase 4.5 synthesis as source of truth
2. Paper cited Fashion-MNIST values from `065_ground_truth.yaml` (expected values from Phase 2B)
3. Ground truth file falsely claimed `source: "h-e1/code/results/experiment_results.json"` for Fashion-MNIST data
4. Paper presented these expected values as actual experimental measurements

**Phase 6.5 Adversarial Review Detection:**
1. Round 1 (accuracy review) caught numerical errors (parameter counts, rounding) but did not verify data existence
2. Round 2 (numerical verification) used Serena MCP to systematically search actual validation files
3. Search for Fashion-MNIST variance in h-e1 files returned: **NO DATA FOUND**
4. Cross-check with `h-e1/code/results/variance_summary.json` confirmed only MNIST entries exist

---

## Impact on Paper Claims

### Core Claims Invalidated (No Experimental Support)

1. **Abstract Key Finding:**
   - Claim: "~10× task-dependency scaling between easy tasks (MNIST: 0.04-0.06%, 98% accuracy) and medium-difficulty tasks (Fashion-MNIST: 0.35-0.59%, 88% accuracy)"
   - Status: **FABRICATED** - Fashion-MNIST data does not exist

2. **Introduction Insight:**
   - Claim: "variance from seed-controlled initialization is task-dependent"
   - Status: **UNVERIFIABLE** - Cannot compare tasks without Fashion-MNIST data

3. **Results Table (H-E1):**
   - Rows 3-4 (Fashion-MNIST 1-layer, 2-layer): **FABRICATED**
   - Rows 1-2 (MNIST 1-layer, 2-layer): ✅ VERIFIED

4. **Ceiling Effect Explanation:**
   - Claim: "ceiling effects that compress variance when baseline accuracy exceeds 95%"
   - Status: **UNVERIFIABLE** - Requires comparison with Fashion-MNIST (88% accuracy) to validate

5. **Architecture Sensitivity:**
   - Claim: "~2× architecture sensitivity (2-layer vs. 1-layer)"
   - Status: **CONTRADICTED** - Actual MNIST data shows 2-layer has LOWER variance (0.0094% vs. 0.0100% = 0.94×, not 2×)

6. **H-E1 Gate Result:**
   - Claim: "PASS (2/4 conditions meet σ²≥0.3% threshold)"
   - Actual: "FAIL (0/4 conditions)" - MNIST variance (0.01%, 0.0094%) below 0.3% threshold

### Claims That Remain Valid (MNIST-Only)

1. **MNIST Variance Measurements:**
   - 1-layer: 0.0100% (p < 0.05)
   - 2-layer: 0.0094% (p < 0.05)
   - Both statistically significant but below practical threshold (0.3%)

2. **Mechanism Validation (H-M1, H-M2):**
   - Mean pairwise distances: 9.60, 16.23
   - Final distances: 22.73, 27.31
   - CV loss: 2.12%, 3.04%
   - **Caveat:** Dataset-specific breakdowns (MNIST vs. Fashion-MNIST) unverified

3. **Bootstrap Stability (H-M3) - MNIST Only:**
   - CI widths: 110.28% (1L), 93.11% (2L)
   - N=30 insufficient for stable estimation (>50% threshold)
   - **Limitation:** Only validated on low-variance MNIST data (0.01%)

---

## Scope of Required Rework

This is **not a fixable revision issue**. The paper requires complete experimental rerun before submission.

### Required Actions

**1. Return to Phase 4:**
- Fix Fashion-MNIST dataset download issue (use alternative mirrors or local dataset)
- Re-run H-E1 with all 4 conditions (60 training runs total: 30 per dataset × 2 architectures)
- Verify Fashion-MNIST variance actually exists and measure actual values

**2. Re-validate Mechanism Hypotheses:**
- H-M1: Run with Fashion-MNIST data, verify weight independence holds
- H-M2: Run with Fashion-MNIST data, verify trajectory divergence holds
- H-M3: Run with Fashion-MNIST data, verify bootstrap instability for higher-variance conditions

**3. Re-synthesize Findings (Phase 4.5):**
- Generate new `045_validated_hypothesis.md` using actual complete data
- Correct gate results based on actual validation outcomes
- Update `verification_state.yaml` with accurate status

**4. Regenerate Paper (Phase 6):**
- If Fashion-MNIST variance confirms predictions (0.35-0.59%), paper structure can largely remain
- If Fashion-MNIST variance differs significantly, paper may require complete reframing
- Update all tables, figures, and discussion based on actual data

**5. Add Pipeline Safeguards:**
- Phase 4.5 synthesis must directly read all h-*/04_validation.md files (not rely on cached state)
- Add validation step: cross-check synthesis claims against validation reports
- Flag discrepancies between `verification_state.yaml` and actual validation files for human review

### Estimated Scope
- Computational cost: ~2 hours (60 training runs on single GPU)
- Revision scope: Potentially complete paper rewrite depending on actual Fashion-MNIST values
- Risk: Actual Fashion-MNIST variance may not match predictions (0.35-0.59%), requiring hypothesis revision

---

## Why This Matters (Research Integrity)

### This is Scientific Misconduct (Unintentional)

The paper presents fabricated experimental results as actual measurements. While this was unintentional (pipeline error), the impact is the same as intentional fabrication:

1. **Readers cannot reproduce the key finding** (10× scaling) because the data cited does not exist
2. **Peer reviewers cannot validate claims** because cited source files (experiment_results.json) lack Fashion-MNIST entries
3. **Follow-up work would build on false foundation** if they assume 10× task-dependency is validated

### Why YouRA's Adversarial Review Caught This

**Traditional peer review would likely miss this because:**
- Reviewers typically do not have access to raw experimental files
- Paper citations appear credible (lists specific file paths)
- Ground truth file claims data exists with proper source attribution
- Phase 4.5 synthesis provides consistent narrative across documents

**Phase 6.5 Round 2 caught this because:**
1. Serena MCP tool provides direct file search capability
2. Adversary agent systematically verified every numerical claim against actual validation files
3. Search for Fashion-MNIST variance in h-e1 returned zero results
4. Cross-check with experiment output JSON files confirmed absence
5. Adversary explicitly checked gate result in h-e1/04_validation.md (found FAIL, not PASS)

**This demonstrates the value of automated adversarial review with source-level verification.**

---

## Process Improvement Recommendations

### For Anonymous Pipeline

**Phase 4.5 Synthesis:**
1. **REQUIRE** direct reading of all h-*/04_validation.md files (not just verification_state.yaml)
2. **FORBID** synthesis from ground truth predictions alone
3. **ADD** validation step: cross-check every gate result claim against actual validation files
4. **FLAG** any discrepancy between synthesis and validation files for human review

**Phase 6 Paper Generation:**
1. **VERIFY** all cited data sources actually contain the claimed values before writing paper
2. **SEARCH** all results JSON files to confirm numerical claims exist in raw data
3. **CROSS-CHECK** paper claims against actual validation reports (not just Phase 4.5 synthesis)

**Phase 6.5 Adversarial Review:**
1. **EXPAND** Round 2 to include data existence verification (not just numerical accuracy)
2. **REQUIRE** Serena MCP search for all key claims in actual validation/results files
3. **ADD** gate result verification as mandatory check (compare paper claim to actual 04_validation.md status)

---

## Next Steps

**DO NOT proceed with revision or submission.** This paper requires experimental rerun, not editorial fixes.

**Immediate Actions:**
1. Fix Fashion-MNIST dataset download issue in Phase 4 experimental code
2. Re-run H-E1 experiments with all 4 conditions (2 datasets × 2 architectures)
3. Verify actual Fashion-MNIST variance values and compare to predictions
4. Re-run H-M1, H-M2, H-M3 with complete Fashion-MNIST data
5. Regenerate Phase 4.5 synthesis using actual validation files
6. Regenerate Phase 6 paper with complete experimental data
7. Re-run Phase 6.5 adversarial review on new paper version

**Timeline Estimate:**
- Dataset fix: 1 hour
- H-E1 rerun: 1 hour (60 training runs)
- H-M1/M2/M3 rerun: 1 hour
- Phase 4.5 synthesis: 15 minutes
- Phase 6 paper generation: 30 minutes
- Phase 6.5 review: 1 hour
- **Total:** ~4-5 hours end-to-end

**Risk Assessment:**
- **Low risk:** Fashion-MNIST variance matches predictions (0.35-0.59%) → paper structure largely valid, just replace expected with actual values
- **Medium risk:** Fashion-MNIST variance differs by 20-50% from predictions → requires discussion/limitation updates
- **High risk:** Fashion-MNIST variance <0.1% (similar to MNIST) → invalidates task-dependency hypothesis, requires complete reframing or hypothesis rejection

---

## For Actual Paper Content

For the last successfully revised paper (before this withdrawal), see:
- **`06_paper_r1.md`** - Round 1 revision with editorial fixes (parameter counts, rounding, engagement improvements)

For complete review history, see:
- **`paper/review/065_review_r1.md`** - Round 1 accuracy review (3 FATAL, 7 MAJOR issues)
- **`paper/review/065_review_r2.md`** - Round 2 numerical verification (4 FATAL, 2 MAJOR issues - data fabrication discovery)
- **`paper/review/065_changelog.md`** - Complete revision changelog

---

## Acknowledgment

**This adversarial review system worked as designed.** Catching data fabrication before submission—even if unintentional—is exactly what Phase 6.5 is meant to do. The discovery of this issue is a success for the pipeline's integrity mechanisms, not a failure.

---

**Document Generated:** 2026-03-21
**Status:** PAPER WITHDRAWN - RETURN TO PHASE 4
**Reason:** Fashion-MNIST experimental data does not exist; core findings fabricated
**Required Action:** Fix dataset download, re-run experiments, regenerate paper with actual data
