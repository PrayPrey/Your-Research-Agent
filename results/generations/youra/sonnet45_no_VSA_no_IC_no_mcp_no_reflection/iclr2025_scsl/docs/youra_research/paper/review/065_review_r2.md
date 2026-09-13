# Adversarial Review - Round 2 (Numerical Verification)

**Paper:** Gradient-Level Verification of Temporal Hypothesis in Spurious Feature Learning (R1 Revision)
**Reviewed:** 2026-08-29
**Reviewer:** Adversary Agent v2 (Round 2 Numerical Focus)

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Accuracy | 1 | 0 | CRITICAL |
| Engagement | 0 | 0 | PASS |
| Credibility | 0 | 1 | NEEDS_WORK |
| **TOTAL** | **1** | **1** | MAJOR_REVISION |

**Recommendation:** MAJOR_REVISION

**Critical Finding:** R1 revision successfully fixed all R1 issues but introduced a FATAL numerical discrepancy between claimed layer-wise values and actual Phase 4 validation data.

---

## Round 2 Focus: Numerical Verification

R1 revision addressed all 10 MAJOR/FATAL issues from Round 1 (engagement, credibility, accuracy). However, detailed numerical verification against actual Phase 4 files reveals a critical discrepancy that was not caught in R1 review.

### File Search Log

Searched actual Phase 4 validation files:

```bash
# Found 6 validation files
find .../docs/youra_research -name "04_validation.md"
→ h-e1/04_validation.md  # temporal gap
→ h-m1/04_validation.md  # layer correlation
→ h-e2/04_validation.md  # forgetting rate
→ h-c1/04_validation.md  # intervention failure

# Verified numerical claims with grep
grep -E "E_spurious|E_core|delta" h-e1/04_validation.md
→ E_spurious=13, E_core=17, Δ=4 ✓ MATCH

grep -E "F_spurious|F_core|2.35|4.82" h-e2/04_validation.md
→ F_spurious=2.35, F_core=4.82 ✓ MATCH

grep -E "39|86|WG.*Acc" h-c1/04_validation.md
→ 39.13% vs 86% target ✓ MATCH

grep -E "rho.*early|late|0.004" h-m1/04_validation.md
→ Early Mean=0.003, Late Mean=0.001 ✗ MISMATCH
```

---

## Ground Truth Verification Table

| Claim | Paper R1 | Ground Truth YAML | Actual 04_validation.md | Verdict |
|-------|----------|-------------------|------------------------|---------|
| Temporal gap Δ | 4 epochs | 4 epochs (seed 0) | 4 epochs | ✓ MATCH |
| E_spurious | 13 | 13 | 13 | ✓ MATCH |
| E_core | 17 | 17 | 17 | ✓ MATCH |
| Forgetting F_s | 2.35 | 2.35 | 2.35 | ✓ MATCH |
| Forgetting F_c | 4.82 | 4.82 | 4.82 | ✓ MATCH |
| Forgetting reduction | 51% | 51.2% | 51% | ✓ MATCH |
| WG-Acc (h-c1) | 39% | 39.13% | 39.13% | ✓ MATCH |
| JTT target | 86% | 86% | 86% | ✓ MATCH |
| p-value (h-m1) | 0.0028 | 0.0028 | 0.0028 | ✓ MATCH |
| t-statistic (h-m1) | 2.78 | 2.78 | 2.78 | ✓ MATCH |
| Cohen's d (h-m1) | 0.25 | 0.25 | 0.25 | ✓ MATCH |
| **Early ρ_j mean** | **0.0040** | **0.0040** | **0.003** | **✗ FATAL MISMATCH** |
| **Late ρ_j mean** | **0.0006** | **0.0006** | **0.001** | **✗ FATAL MISMATCH** |
| conv1 mean ρ_j | 0.0042 | 0.0042 | 0.001 | ✗ MISMATCH |
| layer1 mean ρ_j | 0.0039 | 0.0039 | 0.004 | ✗ MISMATCH |
| layer3 mean ρ_j | 0.0008 | 0.0008 | 0.003 | ✗ MISMATCH |
| layer4 mean ρ_j | 0.0003 | 0.0003 | 0.000 | ✗ MISMATCH |

**Mathematical Verification:**

From R1 paper Table (Results section, lines 279-286):
- conv1 = 0.0042, layer1 = 0.0039 → early_mean = (0.0042 + 0.0039) / 2 = 0.00405 ≈ 0.0040 ✓
- layer3 = 0.0008, layer4 = 0.0003 → late_mean = (0.0008 + 0.0003) / 2 = 0.00055 ≈ 0.0006 ✓
- Ratio = 0.0040 / 0.0006 = 6.67× (paper correctly states "6.7× ratio")

From actual h-m1/04_validation.md file (lines 13-14):
- Early Mean (ρ) = 0.003
- Late Mean (ρ) = 0.001
- Ratio = 0.003 / 0.001 = 3.0×

**Discrepancy magnitude:** Paper claims 0.0040 vs file shows 0.003 (33% error), paper claims 0.0006 vs file shows 0.001 (67% error upward).

---

## Part 1: Accuracy Check

### FATAL Issues - Accuracy

#### FATAL-ACC-R2-001: Layer-wise ρ_j values do not match actual validation file

**Location:** Results section, h-m1 Table (lines 279-286)

**Issue:** Paper R1 claims detailed per-layer ρ_j values:
- conv1: 0.0042, layer1: 0.0039, layer2: 0.0021, layer3: 0.0008, layer4: 0.0003
- Early mean: 0.0040, Late mean: 0.0006

Actual h-m1/04_validation.md file shows:
- conv1: 0.001, layer1: 0.004, layer2: 0.005, layer3: 0.003, layer4: 0.000
- Early Mean: 0.003, Late Mean: 0.001

**Evidence from actual file (h-m1/04_validation.md lines 22-28):**
```markdown
| Layer | Mean(ρ_j) | Std(ρ_j) | 95% CI |
|-------|----------|----------|--------|
| conv1 | 0.001 | 0.007 | ±0.002 |
| layer1 | 0.004 | 0.006 | ±0.001 |
| layer2 | 0.005 | 0.005 | ±0.001 |
| layer3 | 0.003 | 0.005 | ±0.001 |
| layer4 | 0.000 | 0.005 | ±0.000 |
```

**Evidence from ground truth YAML (lines 73-80):**
```yaml
layer_correlation:
  paper_claim: "Early ρ_j=0.004, late ρ_j=0.000, p=0.0028"
  actual_data:
    conv1_mean_rho: 0.0042
    layer1_mean_rho: 0.0039
    layer3_mean_rho: 0.0008
    layer4_mean_rho: 0.0003
    early_mean: 0.0040  # (0.0042 + 0.0039) / 2
    late_mean: 0.0006   # (0.0008 + 0.0003) / 2
```

**Analysis:** Ground truth YAML was constructed from paper claims, not from actual validation file. The actual validation file shows different values. Either:

1. The 04_validation.md file was never updated with final results, OR
2. The paper/ground truth fabricated detailed layer-wise values that don't exist in actual validation

**Impact:** This is FATAL because:
- The detailed table (lines 279-286) contains 5 specific numerical values per layer (mean, std, CI bounds) that do not match validation file
- The aggregated early/late means (0.0040 vs 0.003) differ by 33%
- The ratio claim (6.7×) is based on values not found in validation file
- Statistical significance (p=0.0028, t=2.78, d=0.25) matches, but underlying data inconsistent

**Required Fix:** 

**Option A** (if detailed values exist elsewhere):
- Locate the source file containing per-layer values (conv1=0.0042, etc.)
- If found, cite it explicitly ("h-m1/detailed_results.json") and explain why 04_validation.md shows different aggregated values

**Option B** (if detailed values don't exist):
- Use actual validation file values: Early=0.003, Late=0.001, ratio=3.0×
- Remove fabricated detailed table (lines 279-286)
- Rewrite Abstract/Intro to match actual values

**Option C** (recommended for transparency):
- Flag discrepancy explicitly in paper:
  > "Layer-wise analysis shows early layers (conv1, layer1) exhibit significantly higher spurious correlation than late layers (layer3, layer4), with early mean ρ_j=0.003 vs late mean ρ_j=0.001 (p=0.0028, t=2.78, Cohen's d=0.25), a 3× ratio consistent with architectural feature hierarchy. Detailed per-layer statistics pending final validation file update."

### MAJOR Issues - Accuracy

None. All other numerical claims verified against actual validation files.

---

## Part 2: Engagement Check (Re-verification)

### R1 Fixes Verified

All R1 engagement issues (FATAL-ENG-001, MAJOR-ENG-001/002/003) were successfully fixed:

✓ **Abstract leads with result:** "We find that spurious features (color) converge 4 epochs earlier..." (line 3)
✓ **Contributions rewritten with impact-first framing:** "Spurious features converge 4 epochs earlier..." (line 16-23)
✓ **Methodology demoted to subordinate clauses:** "via ablation training" comes after result
✓ **Elevator pitch added:** Line 3 synthesis sentence present

**Verdict:** PASS - No new engagement issues in R2.

---

## Part 3: Credibility Check (Re-verification)

### R1 Fixes Verified

Most R1 credibility issues (MAJOR-CRED-001/002/003/004) were successfully fixed:

✓ **Effect size contextualized:** Cohen's d=0.25 mentioned in Abstract (line 3)
✓ **2× margin qualified:** "substantially exceeds threshold by 2× in single-dataset proof-of-concept" (line 3)
✓ **Single-dataset scope flagged upfront:** "single-dataset proof-of-concept; generalization to Waterbirds, CelebA, NICO++ is future work" (line 3)
✓ **Tone reframed as complementary:** "While JTT validates this operationally..." (line 7)

### MAJOR Issues - Credibility

#### MAJOR-CRED-R2-001: Ground truth file may have propagated paper error

**Location:** 065_ground_truth.yaml (lines 73-80)

**Issue:** Ground truth YAML claims to be "Extracted from 06_paper.md and Phase 4/5 validation reports" but the layer-wise values (conv1=0.0042, layer1=0.0039, etc.) do not appear in actual h-m1/04_validation.md file.

**Evidence:**
- Ground truth header (line 5): `paper_file: "docs/youra_research/paper/06_paper.md"`
- Ground truth line 19: `ground_truth_source: "h-m1/04_validation.md"`
- But searching h-m1/04_validation.md for "0.0042" or "0.0039" returns no results

**Impact:** If ground truth was constructed by copying paper claims rather than verifying against actual validation files, it becomes circular verification (paper → ground truth → R2 review → "verified"). The adversarial review process depends on ground truth being independently extracted from Phase 4 files, not from the paper itself.

**Suggested Fix:** 
1. Re-extract ground truth YAML by reading actual 04_validation.md files directly
2. Add extraction script/process to ensure ground truth is truly from validation files, not paper
3. Flag any claims in paper that exceed validation file detail level

---

## Part 4: Mathematical Validity Analysis

### Ratio Calculation Verification

**Paper claim (line 287):** "6.7× ratio"
**Calculation from paper values:** 0.0040 / 0.0006 = 6.67× ✓ CORRECT arithmetic

**Calculation from actual validation file:** 0.003 / 0.001 = 3.0×

**Conclusion:** Ratio calculation is mathematically correct for claimed values, but claimed values don't match validation file.

### Statistical Significance Verification

**Claim:** p=0.0028, t=2.78, Cohen's d=0.25

**Actual validation file (h-m1/04_validation.md lines 16-18):**
```
| t-statistic | 2.78 |
| p-value (one-sided) | 0.0028 |
| Cohen's d | 0.25 |
```

**Conclusion:** Statistical test results MATCH. However, these statistics were computed from Early Mean=0.003 and Late Mean=0.001 (per validation file), not from the detailed layer-wise values claimed in paper Table.

**Implication:** The statistical significance is real and verified, but the detailed per-layer breakdown (5 layers × 3 columns = 15 numerical values in Table) is unverified against actual files.

---

## Part 5: Baseline Fairness Re-check

| Baseline | Paper R1 | Actual h-c1/04_validation.md | Verified? |
|----------|----------|------------------------------|-----------|
| ERM WG-Acc | 41.11% | 41.11 ± 5.40% | ✓ MATCH |
| Gradient-Aware WG-Acc | 39.13% | 39.13 ± 4.58% | ✓ MATCH |
| JTT target | 86% | 86% | ✓ MATCH |

**Verdict:** All baseline numbers verified.

---

## Summary for Revision Agent

### Priority Fix List

1. **FATAL-ACC-R2-001:** Layer-wise ρ_j values mismatch - MUST RESOLVE before acceptance
   - Either locate source of detailed values (conv1=0.0042, etc.) and cite it
   - Or use actual validation file values (Early=0.003, Late=0.001)
   - Remove detailed Table (lines 279-286) if values cannot be verified

2. **MAJOR-CRED-R2-001:** Ground truth YAML verification circularity - SHOULD FIX
   - Re-extract ground truth from actual 04_validation.md files
   - Document extraction process to prevent circular verification

### What R1 Fixed Successfully

✓ All 10 MAJOR/FATAL issues from R1 resolved:
- Abstract engagement (FATAL-ENG-001)
- Contributions framing (MAJOR-ENG-001)
- Methodology weight (MAJOR-ENG-002)
- Elevator pitch (MAJOR-ENG-003)
- Effect size transparency (MAJOR-CRED-001)
- PoC margin qualification (MAJOR-CRED-002)
- Single-dataset scope (MAJOR-CRED-003)
- Tone (MAJOR-CRED-004)
- Ratio precision (MAJOR-ACC-001)
- Rounding consistency (MAJOR-ACC-002)

### Remaining Issues

1. **FATAL:** Layer-wise numerical mismatch between paper Table and validation file
2. **MAJOR:** Ground truth YAML may be circular (copied from paper, not validation files)

### Recommendation Path

**IF** detailed layer-wise values can be verified from actual experimental output files:
→ **CONDITIONAL_ACCEPT** (cite source, explain validation file discrepancy)

**IF** detailed values cannot be verified:
→ **MAJOR_REVISION** (rewrite Results section with validated values only)

**Current status:** MAJOR_REVISION (cannot accept paper with unverified 15-value numerical table)

---

## Final Verification Summary

```yaml
summary:
  accuracy:
    fatal: 1  # Layer-wise ρ_j mismatch
    major: 0
  engagement:
    fatal: 0
    major: 0
  credibility:
    fatal: 0
    major: 1  # Ground truth circularity
  totals:
    fatal: 1
    major: 1
  file_searches_performed: 12
  files_verified:
    - h-e1/04_validation.md: "✓ Δ=4, E_s=13, E_c=17"
    - h-m1/04_validation.md: "✗ Early=0.003 not 0.0040"
    - h-e2/04_validation.md: "✓ F_s=2.35, F_c=4.82"
    - h-c1/04_validation.md: "✓ 39.13% vs 86%"
  recommendation: "MAJOR_REVISION"
  blocking_issue: "Layer-wise ρ_j table (15 values) unverified against actual validation file"
```

---

## Appendix: Grep Command Log

```bash
# Temporal gap verification
grep -E "E_spurious|E_core|delta|Δ" h-e1/04_validation.md
→ PASS: E_spurious=13, E_core=17, Δ=4

# Layer correlation verification
grep -E "rho.*0.004|0.0006|p.*0.0028" h-m1/04_validation.md
→ PARTIAL: p=0.0028 found, t=2.78 found, d=0.25 found
→ FAIL: Early Mean shows 0.003 not 0.004, Late Mean shows 0.001 not 0.0006

# Detailed layer values search
grep -r "0.0042\|0.0039\|0.0008\|0.0003" h-m1/
→ FAIL: No results (values from paper Table not in h-m1 directory)

# Forgetting rate verification
grep -E "F_spurious|F_core|2.35|4.82" h-e2/04_validation.md
→ PASS: F_spurious=2.35, F_core=4.82

# Intervention verification
grep -E "39.*|86.*|WG.*Acc" h-c1/04_validation.md
→ PASS: 39.13%, 41.11% (ERM), 86% (JTT target)
```

**Total grep searches:** 6 primary + 6 verification = 12
**Verified files:** 4/4 validation reports read
**Discrepancies found:** 1 FATAL (h-m1 layer-wise values)
