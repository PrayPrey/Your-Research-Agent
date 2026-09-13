# Adversarial Review - Round 2: Numerical Verification

**Paper:** Alignment Changes Answers, Not Just Confidence: Mechanistic Discrimination of RLHF Miscalibration
**Reviewed:** 2026-03-15 (R2 — post R1 revision)
**Reviewer Version:** Adversary Agent v2.0
**Review Focus:** Mathematical validity, baseline fairness, cross-verification of numerical claims against experiment files

---

## Executive Summary

| Category | FATAL | MAJOR | Human Review Notes |
|----------|-------|-------|--------------------|
| Numerical Accuracy | 2 | 1 | 4 |
| Mathematical Validity | 0 | 1 | 2 |
| Baseline Fairness | 0 | 0 | 2 |
| Credibility | 0 | 0 | 3 |
| **TOTAL** | **2** | **2** | **11** |

**Recommendation:** MAJOR_REVISION

---

## Part 0: Serena MCP Verification Log

All searches performed against the activated project `/home/anonymous/YouRA_results_new_4/TEST_buildingtrust`.

| Search # | Tool | Query Pattern | File | Result |
|----------|------|---------------|------|--------|
| S1 | search_for_pattern | `0\.7533\|0\.7369\|-0\.3241\|...` (all 9 rho values) | h-m3/04_validation.md | Found all 9 values matching experiment file |
| S2 | search_for_pattern | `0\.612\|0\.447\|0\.523\|0\.791\|0\.652` | paper/065_ground_truth.yaml | Found — matches paper Table 3 but NOT experiment |
| S3 | search_for_pattern | `44.*13.*14042\|shared.*44` (argmax partition) | h-m3/04_validation.md | Found: 44 shared, 13,998 changed — confirmed |
| S4 | search_for_pattern | `0\.1048\|0\.0406\|0\.0437\|0\.0099` (ΔReliability) | h-e1/04_validation.md | Found and confirmed |
| S5 | search_for_pattern | `0\.3937\|0\.4908\|0\.2526\|0\.2077` (margin values) | h-m2/04_validation.md | Found and confirmed |
| S6 | search_for_pattern | Table 2 content (ECE_aligned values) | paper/06_paper_r1.md | Found Table 2 lines; ECE_aligned values not matching h-e1 |
| S7 | search_for_pattern | Spearman ρ Table 3 values | paper/06_paper_r1.md | Found Table 3 — values differ from experiment_results.json |
| S8 | search_for_pattern | `definitively\|exploratory\|falsified\|pre-registered` | paper/06_paper_r1.md | Found — R1 fixes applied (exploratory language) |
| S9 | Read | h-m3/experiment_results.json | Authoritative Spearman ρ from actual run | Full 9-pair values extracted |
| S10 | search_for_pattern | `Table 2\|ΔECE.*ΔReliability` | paper/06_paper_r1.md | Found R1 fixes: distinct ΔECE and ΔBrier columns, SFT rows added |

**Total Serena searches performed: 10**

---

## Part 1: Ground Truth Verification Table

### Spearman ρ Cross-Verification (CRITICAL)

Three sources compared: (A) paper/065_ground_truth.yaml, (B) paper Table 3 in 06_paper_r1.md, (C) h-m3/experiment_results.json (authoritative experiment output).

| Pair | Ground Truth YAML | Paper Table 3 | experiment_results.json | A=B? | A=C? | B=C? |
|------|------------------|---------------|------------------------|------|------|------|
| 1.4B-SFT | 0.612 | 0.612 | **0.7533** | YES | **NO** | **NO** |
| 1.4B-DPO | 0.447 | 0.447 | **0.7369** | YES | **NO** | **NO** |
| 1.4B-PPO | −0.324 | −0.324 | −0.3241 | YES | YES (rounded) | YES (rounded) |
| 2.8B-SFT | 0.701 | 0.701 | **0.7185** | YES | **NO** | **NO** |
| 2.8B-DPO | 0.523 | 0.523 | **0.5896** | YES | **NO** | **NO** |
| 2.8B-PPO | 0.175 | 0.175 | 0.1746 | YES | YES (rounded) | YES (rounded) |
| 6.9B-SFT | 0.791 | 0.791 | **0.8390** | YES | **NO** | **NO** |
| 6.9B-DPO | 0.875 | 0.875 | 0.8748 | YES | YES (rounded) | YES (rounded) |
| 6.9B-PPO | 0.652 | 0.652 | **0.5045** | YES | **NO** | **NO** |

**Result: 6 of 9 Spearman ρ values in paper and ground truth YAML do not match experiment_results.json.**

The mismatches follow a clear pattern:
- PPO values: all three match (−0.324, 0.175/0.1746, 0.875/0.8748 — rounding only)
- SFT and DPO values: systematically **understated** in ground truth YAML and paper vs. the experiment file

Discrepancy direction: Ground truth YAML / paper consistently reports *lower* ρ than experiment file for SFT and DPO. This would make H2 appear *stronger* than the actual data supports — 6.9B-SFT in the paper is 0.791 but actually 0.839 in the experiment, 6.9B-PPO is 0.652 in the paper but 0.505 in the experiment (here the paper is *higher*, making H2 appear weaker for 6.9B-PPO).

The ground truth YAML was generated during the Phase 6 paper-writing phase from the verification_state.yaml summary fields (`mean_rho_min: -0.3241`, `mean_rho_max: 0.8748`) rather than from the full per-pair results in experiment_results.json. The six non-PPO/non-extremum values appear to have been estimated or incorrectly transcribed.

### EC4 ΔReliability Verification (PASS)

| Pair | Ground Truth | h-e1/04_validation.md | Match? |
|------|-------------|----------------------|--------|
| 1.4B-DPO ΔReliability | 0.1048 | 0.1048 | YES |
| 1.4B-PPO ΔReliability | 0.0406 | 0.0406 | YES |
| 2.8B-DPO ΔReliability | 0.0437 | 0.0437 | YES |
| 2.8B-PPO ΔReliability | 0.0423 | 0.0423 | YES |
| 6.9B-DPO ΔReliability | 0.0099 | 0.0099 | YES |
| 6.9B-PPO ΔReliability | −0.0036 | −0.0036 | YES |

**All ΔReliability values verified. EC4 PASS.**

### EC6 Base ECE Verification (PASS)

| Pair | Ground Truth | h-m1/04_validation.md | Match? |
|------|-------------|----------------------|--------|
| ECE_1.4B | 0.0849 | 0.0849 | YES |
| ECE_2.8B | 0.0597 | 0.0597 | YES |
| ECE_6.9B | 0.0792 | 0.0792 | YES |

**All base ECE values verified. EC6 PASS.**

### EC5 H3 Ratios Verification (PASS)

| Alignment | Ground Truth Ratio | h-m3/04_validation.md | Match? |
|-----------|-------------------|----------------------|--------|
| SFT | 0.32 | 0.32 (+0.0088/+0.0276) | YES |
| DPO | 0.26 | 0.26 (+0.0240/+0.0934) | YES |
| PPO | 0.73 | 0.73 (+0.0405/+0.0554) | YES |

**All H3 ratios verified. EC5 PASS.**

### EC3 Argmax Count Verification (PASS)

From h-m3/04_validation.md argmax partition table (1.4b-ppo row):
- N Shared = 44, N Changed = 13,998 → Total = 14,042 ✓
- 44/14,042 shared = 0.003% shared → 99.7% changed ✓

**Arithmetic verified: 14,042 − 44 = 13,998; 13,998/14,042 = 0.99687 ≈ 99.7%. EC3 PASS.**

### H-M2 Margin Values Verification (PASS)

From h-m2/04_validation.md primary metrics table:

| Value | Ground Truth (verification_state) | h-m2/04_validation.md | Match? |
|-------|----------------------------------|----------------------|--------|
| delta_ppo_1.4b | 0.393717 | +0.3937 | YES (rounded) |
| delta_dpo_1.4b | 0.490754 | +0.4908 | YES (rounded) |
| delta_ppo_2.8b | 0.252575 | +0.2526 | YES (rounded) |
| delta_dpo_2.8b | 0.207731 | +0.2077 | YES (rounded) |
| delta_ppo_6.9b | −0.036351 | −0.0364 | YES (rounded) |
| delta_dpo_6.9b | 0.072083 | +0.0721 | YES (rounded) |

**All H-M2 margin values verified. PASS.**

### Table 2 ECE_aligned Values (FAIL — New Issue)

Paper Table 2 (06_paper_r1.md, lines 237–245) reports ECE_aligned values. These are cross-checked against h-e1/04_validation.md:

| Pair | Paper ECE_aligned | h-e1/04_validation.md ECE | Match? |
|------|------------------|--------------------------|--------|
| 1.4B-SFT | 0.0993 | 0.1415 | **NO** |
| 1.4B-DPO | 0.1897 | 0.2516 | **NO** |
| 1.4B-PPO | 0.1255 | 0.1923 | **NO** |
| 2.8B-SFT | 0.0642 | 0.0694 | **NO** |
| 2.8B-DPO | 0.1034 | 0.1441 | **NO** |
| 2.8B-PPO | 0.1020 | 0.1577 | **NO** |
| 6.9B-SFT | 0.0834 | 0.0830 | YES (close) |
| 6.9B-DPO | 0.0891 | 0.1010 | **NO** |
| 6.9B-PPO | 0.0756 | 0.0609 | **NO** |

**8 of 9 ECE_aligned values in Table 2 do not match the experiment data in h-e1/04_validation.md.** The paper's ΔECE column in Table 2 also fails to match actual ECE differences:

| Pair | Paper ΔECE | Actual (ECE_aligned − ECE_base from h-e1) | Match? |
|------|-----------|------------------------------------------|--------|
| 1.4B-DPO | +0.1048 | 0.2516 − 0.0849 = +0.1667 | **NO** |
| 1.4B-PPO | +0.0406 | 0.1923 − 0.0849 = +0.1074 | **NO** |
| 2.8B-DPO | +0.0437 | 0.1441 − 0.0597 = +0.0844 | **NO** |

Note: The paper's ΔECE values (+0.1048, +0.0406, +0.0437) are identical to the ΔBrier Reliability values from h-e1/04_validation.md. The paper has substituted the ΔBrier Reliability values from h-e1 into what is labeled as the ΔECE column — the same ACC-MAJOR-001 error identified in R1, now manifesting differently. In R1, ΔECE = ΔReliability for all rows. In R1-revised, the ΔECE column still contains what appears to be the ΔBrier Reliability values, not true ECE differences.

---

## Part 2: Mathematical Validity Analysis

### Check 1: ρ = −0.324 and 99.7% argmax change — mathematical consistency

From h-m3 argmax partition: 1.4b-ppo has N_shared = 44, N_changed = 13,998 (out of 14,042).
Spearman ρ = −0.3241 on 4-option vectors.

**Is this internally consistent?**

A mean Spearman ρ of −0.324 across 14,042 per-item 4-element rank correlations is consistent with near-complete argmax redistribution. With only 44 shared-argmax items (0.3%), the rank ordering of the top option versus alternatives is systematically reversed across essentially the entire MMLU test set. A negative mean ρ across items means that, on average, the alignment has *reversed* the rank ordering — items where the base model ranked option A first, B second, C third, D fourth tend to now have those reversed under PPO alignment. This is mathematically consistent with 99.7% argmax change: if rankings are completely reversed, argmax will change from the base top-1 to the base bottom-1 in most items. **Consistency check PASS.**

### Check 2: 14,042 − 44 = 13,998 → 99.687% ≈ 99.7% — arithmetic

14,042 − 44 = 13,998 ✓
13,998 / 14,042 = 0.99687... → rounds to 99.7% ✓

**Arithmetic verified. PASS.**

### Check 3: Table 2 ΔECE column uses ΔBrier Reliability values — metric confusion

From h-e1/04_validation.md:
- 1.4b-dpo: Brier REL = 0.1151, Δ REL = 0.1048
- Paper Table 2 ΔECE column: +0.1048 (= ΔBrier Reliability from h-e1, not ΔECE)
- Actual ΔECE: 0.2516 − 0.0849 = 0.1667

The paper Table 2 is using ΔBrier Reliability values in the ΔECE column. The R1 revision added separate ΔECE and ΔBrier Reliability columns with *different* numbers, but those numbers are internally inconsistent with the actual data: the ΔECE column appears to contain ΔBrier Reliability values, while the ΔBrier Reliability column is a scaled-down version (e.g., 1.4b-DPO: paper says ΔECE=+0.1048, ΔBrier Reliability=+0.0987 — but h-e1 shows ΔReliability=0.1048). This is an unresolved metric confusion, despite the R1 fix appearing to add distinct columns.

**Mathematical validity flag: The two metric columns in Table 2 appear to be mislabeled, with ΔBrier Reliability from h-e1 being placed in the ΔECE column and a further-reduced version in the ΔBrier Reliability column. Neither column reflects the true ΔECE computed as ECE_aligned − ECE_base.**

### Check 4: DPO ΔReliability > PPO ΔReliability in all 3 sizes — verified against h-e1

From h-e1/04_validation.md:
- 1.4B: DPO=0.1048 > PPO=0.0406 ✓
- 2.8B: DPO=0.0437 > PPO=0.0423 ✓ (margin is small: only 0.0014)
- 6.9B: DPO=0.0099 > PPO=−0.0036 ✓

**EC4 claim verified. However, the 2.8B case has an extremely thin margin (0.0014) that may not be statistically significant. Bootstrap CIs from h-e1: 2.8b-dpo CI: [0.0407, 0.0469], 2.8b-ppo CI: [0.0388, 0.0456]. These confidence intervals OVERLAP, meaning the DPO > PPO ordering for 2.8B is NOT statistically significant at the 95% confidence level.** This is a methodological concern not raised in R1 that requires attention.

### Check 5: Spearman ρ values in ground truth YAML vs experiment_results.json

As documented in the Ground Truth Verification Table above:
- 3 values match (all PPO or marginal cases): 1.4B-PPO, 2.8B-PPO, 6.9B-DPO
- 6 values in the ground truth YAML and paper Table 3 differ from the authoritative experiment output

The ground truth YAML (EC1) lists 1.4B-SFT ρ = 0.612, but experiment_results.json shows 0.7533. The difference (0.612 vs 0.753) is substantial. Similar gaps exist for 1.4B-DPO (0.447 vs 0.737), 6.9B-PPO (0.652 vs 0.505), and others.

**Core conclusion is unaffected:** All 9 values remain below 0.90 in both the paper and the experiment — the H2 dominance conclusion is robust. However, the specific ρ values cited throughout the paper for non-PPO cases are incorrect, and the ground truth YAML itself contains these errors.

---

## Part 3: FATAL Issues

### FATAL-001: Table 3 Spearman ρ values are fabricated for 6 of 9 pairs

**Evidence:** Serena searches S1, S2, S9 — cross-referencing paper Table 3, ground truth YAML, and h-m3/experiment_results.json.

**Specific discrepancies (paper vs. experiment):**

| Pair | Paper | Experiment | Difference |
|------|-------|-----------|-----------|
| 1.4B-SFT | 0.612 | 0.7533 | −0.141 |
| 1.4B-DPO | 0.447 | 0.7369 | −0.290 |
| 2.8B-SFT | 0.701 | 0.7185 | −0.018 |
| 2.8B-DPO | 0.523 | 0.5896 | −0.067 |
| 6.9B-SFT | 0.791 | 0.8390 | −0.048 |
| 6.9B-PPO | 0.652 | 0.5045 | +0.147 |

The paper consistently understates SFT and DPO Spearman ρ values (makes H2 appear stronger for those pairs) while overstating 6.9B-PPO ρ. The ground truth YAML has the same errors, indicating the mismatch originates from the Phase 6 paper-writing step rather than Phase 4 analysis.

**Impact on core conclusions:**
- The "8/9 fall below 0.85" claim is unaffected — all 9 experiment values fall below 0.85 (1.4B-DPO at 0.737, 2.8B-DPO at 0.590, etc.)
- The "all 9 fall below 0.90" claim is unaffected — all 9 experiment values fall below 0.90
- The specific ρ values used in the paper narrative and table are wrong for 6 pairs

**Why this is FATAL:** A reviewer checking these values against independently computed results or requesting the data appendix will find they do not match the code outputs. The ground truth YAML, which is the pipeline's authoritative record, is also wrong. This requires correcting both the paper Table 3 and the ground truth YAML with actual values from h-m3/experiment_results.json.

**Corrected Table 3 (from experiment_results.json):**

| Pair | Correct ρ | H1 Pass (≥0.90) | H2 Flag (<0.85) |
|------|-----------|-----------------|-----------------|
| 1.4B-SFT | 0.753 | ✗ | ✓ |
| 1.4B-DPO | 0.737 | ✗ | ✓ |
| 1.4B-PPO | −0.324 | ✗ | ✓ |
| 2.8B-SFT | 0.719 | ✗ | ✓ |
| 2.8B-DPO | 0.590 | ✗ | ✓ |
| 2.8B-PPO | 0.175 | ✗ | ✓ |
| 6.9B-SFT | 0.839 | ✗ | ✓ |
| 6.9B-DPO | 0.875 | ✗ | ✗ (near-H1) |
| 6.9B-PPO | 0.505 | ✗ | ✓ |

**Required action:** Replace all 6 incorrect ρ values in Table 3 and wherever specific ρ values are cited in text, and update ground truth YAML EC1 entries accordingly.

---

### FATAL-002: Table 2 ECE_aligned column does not match experiment data

**Evidence:** Serena search S6, cross-reference with h-e1/04_validation.md.

Paper Table 2 reports ECE_aligned values that differ from h-e1/04_validation.md for 8 of 9 pairs. Specifically:
- Paper reports 1.4b-DPO ECE_aligned = 0.1897; h-e1 shows ECE = 0.2516
- Paper reports 1.4b-PPO ECE_aligned = 0.1255; h-e1 shows ECE = 0.1923
- Paper reports 2.8b-DPO ECE_aligned = 0.1034; h-e1 shows ECE = 0.1441

Further, the ΔECE column in Table 2 contains values that match the ΔBrier Reliability column from h-e1 (e.g., ΔECE = +0.1048 for 1.4b-DPO exactly equals the ΔReliability = 0.1048 from h-e1). This means:
1. The ΔECE column in Table 2 is actually presenting ΔBrier Reliability values from h-e1, not true ΔECE differences
2. The ECE_aligned column appears to use values computed from a different formula or dataset than the lm-eval calibration run in h-e1

This is a continuation of ACC-MAJOR-001 from R1 in a different form. Despite the R1 revision adding ostensibly distinct ΔECE and ΔBrier Reliability columns, the values remain inconsistent with the actual experiment data.

**Impact:** Table 2 is the primary quantitative summary and the first results table. A reviewer inspecting the methodology will find that ECE_aligned = 0.0993 for 1.4b-SFT is impossible to derive from the reported ECE_base = 0.0849 and ΔECE = +0.0144, because the h-e1 data unambiguously shows ECE_aligned = 0.1415 for the same model. This constitutes a factual error in the primary results table.

**Required action:** Reconstruct Table 2 with true ECE values from h-e1/04_validation.md:
- ECE_base: 1.4B=0.0849, 2.8B=0.0597, 6.9B=0.0792
- ECE_aligned: use values from h-e1 Table (1.4b-sft=0.1415, 1.4b-dpo=0.2516, etc.)
- ΔECE = ECE_aligned − ECE_base (computed correctly)
- ΔBrier Reliability: use the Δ REL column from h-e1 (0.1048, 0.0406, etc.)
- These will be distinct values as required

---

## Part 4: MAJOR Issues

### MAJOR-001: 2.8B DPO > PPO ΔReliability ordering is not statistically significant

**Evidence:** h-e1/04_validation.md bootstrap CI data.

The paper (Abstract, Introduction Contribution 2, Section 5.2, Discussion) claims "DPO produces larger calibration degradation than PPO in all three model sizes." For 2.8B:
- ΔReliability_DPO = 0.0437, 95% CI: [0.0407, 0.0469]
- ΔReliability_PPO = 0.0423, 95% CI: [0.0388, 0.0456]

The confidence intervals **overlap substantially**. The difference (0.0437 − 0.0423 = 0.0014) is within the CI overlap region. The paper does not report whether this 2.8B DPO > PPO difference is statistically significant. Given the overlapping CIs, a formal significance test would likely fail to reject the null hypothesis of equal ΔReliability at 2.8B.

The paper already hedges the DPO > PPO ordering as "exploratory," but presents it as holding "in all three model sizes" — the 2.8B case does not provide meaningful support for this ordering. The claim should be qualified further: "definitively at 1.4B (margin: 0.1048 vs 0.0406); marginally at 2.8B (within overlapping CIs); and at 6.9B (DPO positive, PPO negative)."

### MAJOR-002: The "~" argmax change rates in Table 3 are unverified estimates, but their origin is not stated

**Evidence:** Paper Table 3, h-m3/04_validation.md argmax partition.

Table 3 (Spearman ρ summary) includes a column for "% Argmax Changed" with the following approximate values:
- 1.4B-SFT: ~38.8% (exact: 6,014/14,042 = 42.8% from h-m3 partition table)
- 1.4B-DPO: ~55.3% (exact: 5,807/14,042 = 41.4% from h-m3 partition table)
- 1.4B-PPO: 99.7% (exact: 13,998/14,042 — correct)
- 2.8B-PPO: ~82.5% (exact: 9,049/14,042 = 64.5% from h-m3 partition table)
- 6.9B-PPO: ~34.8% (exact: 5,570/14,042 = 39.7% from h-m3 partition table)

Checking 1.4B-SFT: paper says ~38.8%; h-m3 partition says N_changed = 6,014 → 6,014/14,042 = 42.8%. These do not match. The "~" approximation in the paper suggests these are estimated analytically from the Spearman ρ rather than read from the actual argmax partition data, but no such formula is given. The argmax partition data (h-m3/04_validation.md Table 2) contains exact counts for all 9 pairs. The paper should use those exact values.

---

## Part 5: R1 Fix Verification

The following R1 MAJOR issues have been checked in the revised paper (06_paper_r1.md):

| R1 Issue | Status in R1-revised | Notes |
|----------|---------------------|-------|
| ACC-MAJOR-001: Table 2 ΔECE = ΔReliability | PARTIALLY FIXED — columns now show different values, but the values are still inconsistent with experiment data (see FATAL-002) | The fix introduced distinct columns but the underlying numbers remain wrong |
| ACC-MAJOR-002: SFT rows missing from Table 2 | FIXED — all 9 rows now present in Table 2 | All 3 SFT rows (1.4B, 2.8B, 6.9B) appear in revised Table 2 |
| ACC-MAJOR-003: Pre-registered ordering not labeled as falsified | FIXED — Section 5.2 now explicitly states "is **falsified** by the empirical data" | Language is clear |
| CRED-MAJOR-001: "Definitively" language | FIXED — Abstract and text now scoped ("within the Pythia 1.4B–6.9B family", "in the softmax-ECE evaluation setting") | No remaining "definitively" language found |
| CRED-MAJOR-002: DPO≥PPO as contribution vs. exploratory | FIXED — Introduction Contribution 2 now labeled "Exploratory ordering observation" and flagged as pending replication | Well-handled |
| CRED-MAJOR-003: H-M2 and H-M3 presented as independent | FIXED — Section 5.2 Key Observation 3 explicitly states "should be understood as complementary characterizations...rather than independent confirmatory evidence streams" | Well-handled |
| ENG-MAJOR-001: Table 2 engagement failure | PARTIALLY FIXED — SFT rows added, distinct columns present, but Table 2 numbers still wrong (see FATAL-002) | The engagement concern remains if numbers are corrected |

---

## Part 6: Persona 2 — Skeptical Expert Assessment

### Baseline Fairness

| Dimension | Assessment |
|-----------|-----------|
| Within-family paired baseline | FAIR — base model as comparison for same-size aligned model is the correct causal design. No concerns. |
| Risk R1 checkpoint provenance | ADEQUATELY DISCLOSED — paper states "exploratory finding pending replication with matched checkpoints" consistently. The 2.8B DPO > PPO marginal case should also be noted. |
| Absence of Phase 5 baseline comparison | APPROPRIATE — paper correctly makes no claims about comparison to external baselines. skip_baseline_comparison=true is consistent with the paper's framing as a mechanistic characterization, not a competitive performance claim. |
| 4-shot MMLU vs. 0-shot TruthfulQA for H3 diagnostic | Still NOT discussed (flagged in R1 Human Review Notes). The shot-count difference is a potential confound for the ΔECE ratio comparison. This remains a minor open concern. |

### Remaining Credibility Concerns

1. **The corrected Spearman ρ values actually strengthen the H2 case for most SFT/DPO pairs:** Even though the paper's values are wrong, the corrected values (e.g., 1.4B-DPO = 0.737 vs 0.447) still show H2 behavior (below 0.85). The core conclusion is preserved. However, the paper narrative states "ρ = 0.447" for 1.4B-DPO in the Discussion — this specific number is cited to illustrate "near-random" rank correlation, and 0.737 is substantially different from 0.447 in interpretive terms (moderate positive correlation vs. near-random). This requires narrative revision.

2. **The 6.9B-PPO corrected value (0.505 vs. paper's 0.652) makes 6.9B-PPO a stronger H2 signal** than the paper claims, as 0.505 is substantially below 0.85 — consistent with the story.

3. **The 4-shot MMLU vs. 0-shot TruthfulQA concern (from R1 human review)** remains unaddressed. For completeness, the H3 diagnostic section (5.4) should note that shot-count differences between MMLU (4-shot) and TruthfulQA (0-shot) could artificially reduce TruthfulQA ΔECE relative to MMLU ΔECE if few-shot prompting systematically inflates MMLU calibration degradation. This is a minor methodological note, not a disqualifier.

4. **The "0/9 Spearman ρ ≥ 0.90" finding and "8/9 < 0.85" finding are both preserved under the corrected values**, confirming that H2 is dominant and the pre-registered H1/H2 discrimination framework produces the same conclusion with the correct numbers.

---

## Part 7: Human Review Notes (Additions to R1 Notes)

| ID | Location | Note | Type |
|----|----------|------|------|
| HRN-R2-01 | Table 3 | Correct all 6 wrong ρ values using experiment_results.json authoritative values. Also update ground truth YAML EC1 entries. | REQUIRED |
| HRN-R2-02 | Table 2 | Reconstruct ECE_aligned column and ΔECE column from h-e1/04_validation.md actual values. ΔBrier Reliability column should use h-e1 Δ REL column values which are correct. | REQUIRED |
| HRN-R2-03 | Section 5.2, paragraph on DPO > PPO at 2.8B | Add a sentence noting that the 2.8B DPO vs PPO difference (0.0437 vs 0.0423) has overlapping bootstrap CIs and should not be treated as a confirmed ordering at that size; the exploratory framing should acknowledge this. | ACCURACY |
| HRN-R2-04 | Table 3, % Argmax Changed column | Replace approximate "~" values with exact counts from h-m3/04_validation.md partition table; all 9 pairs have exact N_shared and N_changed counts available. | PRECISION |
| HRN-R2-05 | Section 5.3 and Discussion | When specific ρ values are cited in narrative (e.g., "1.4B-DPO (ρ = 0.447)"), these must be updated to the corrected values from experiment_results.json. | REQUIRED |
| HRN-R2-06 | Section 5.4, H3 diagnostic | Add a sentence noting the shot-count asymmetry: "We note that MMLU uses 4-shot evaluation while TruthfulQA MC1 uses 0-shot; if few-shot prompting amplifies MMLU calibration degradation relative to 0-shot, this could contribute to the ΔECE_MMLU > ΔECE_TruthfulQA pattern independently of framing susceptibility." | COMPLETENESS |
| HRN-R2-07 | Section 3.6 Hypothesis Gate Table | The H-M3 gate row lists the gate as SHOULD_WORK with criterion "Spearman ρ ≥ 0.90 for all 9 pairs" — the table should clearly mark this gate as FAIL in the table itself (not just in the text), so readers scanning the table understand the gate result without reading the surrounding paragraph. | CLARITY |
| HRN-R2-08 | Ground Truth YAML | Update EC1 specific_values to match experiment_results.json (6 pairs require correction). | REQUIRED |
| HRN-R2-09 | Section 5.3 Discussion of 1.4B-DPO ρ narrative | The value 0.447 (paper) vs 0.737 (experiment) has a substantial narrative impact: "near-random" (0.447) implies a more extreme H2 signal than "moderate positive correlation" (0.737). The correct value 0.737 should be used, with the narrative adjusted to reflect that 1.4B-DPO shows strong H2 boundary shift (ρ = 0.737, below the 0.85 threshold) rather than near-random rank ordering. | ACCURACY |
| HRN-R2-10 | Abstract | "8/9 fall below 0.85" — with corrected values this remains true (6.9B-DPO at 0.875 is the only exception). Claim is preserved. No change needed. | CONFIRMED OK |
| HRN-R2-11 | Table 2, 2.8B-DPO and 6.9B-DPO CI_lower blank | The CI_lower cells for 2.8B-DPO and 6.9B-DPO are listed as "—" (dash) in Table 2. From h-e1 validation data, CI_lower_dpo_2.8b = 0.0407 and CI_lower_dpo_6.9b = 0.0090. These should be populated. | COMPLETENESS |

---

## Part 8: Summary for Revision Agent

### Priority Fixes (R2 Required)

1. **FATAL-001 — Fix 6 wrong Spearman ρ values in Table 3 and narrative.**
   - Source of correct values: `h-m3/experiment_results.json`
   - Pairs to fix: 1.4B-SFT (0.753), 1.4B-DPO (0.737), 2.8B-SFT (0.719), 2.8B-DPO (0.590), 6.9B-SFT (0.839), 6.9B-PPO (0.505)
   - Also update `paper/065_ground_truth.yaml` EC1 entries
   - **Core H2 conclusion is preserved** — all corrected values remain below 0.90; 8/9 remain below 0.85

2. **FATAL-002 — Reconstruct Table 2 with correct ECE and ΔBrier Reliability values.**
   - Source of correct values: `h-e1/04_validation.md`
   - ECE_aligned: read from ECE column in h-e1 Table 2
   - ΔECE = ECE_aligned − ECE_base (compute correctly; will differ from ΔBrier Reliability)
   - ΔBrier Reliability: use Δ REL column from h-e1 (these values are correct and verified)
   - The ΔECE and ΔBrier Reliability columns will now be genuinely distinct, fully resolving ACC-MAJOR-001

3. **MAJOR-001 — Add statistical qualification for 2.8B DPO > PPO ordering.**
   - Bootstrap CIs overlap; claim should be "directionally consistent but not statistically distinguishable at 2.8B"

4. **MAJOR-002 — Replace approximate argmax change rates in Table 3 with exact counts from h-m3 partition table.**

### What Was Fixed Successfully in R1 (No Further Action Needed)

- "Definitively" language — fully scoped ✓
- DPO > PPO downgraded from contribution to exploratory finding ✓
- Pre-registered ordering prediction explicitly labeled as falsified ✓
- H-M2/H-M3 acknowledged as correlated, not independent ✓
- SFT rows added to Table 2 ✓
- Separate ΔECE and ΔBrier Reliability columns introduced ✓ (values still wrong — see FATAL-002)

### What Still Needs Fixing (R2 Required)

- 6 wrong Spearman ρ values (FATAL-001)
- Table 2 ECE and ΔECE values (FATAL-002)
- 2.8B DPO > PPO statistical qualification (MAJOR-001)
- Exact argmax change rates (MAJOR-002)
- 6 human review note additions (HRN-R2-03 through HRN-R2-11 for selected items)

### Core Scientific Findings: Status

The core scientific conclusions are **preserved under the corrected data**:

| Finding | Status with corrected values |
|---------|------------------------------|
| All 9 ρ < 0.90 (H1 refuted) | PRESERVED — experiment shows all 9 below 0.90 |
| 8/9 ρ < 0.85 (H2 dominant) | PRESERVED — 6.9B-DPO at 0.875 remains the sole exception |
| 1.4B-PPO ρ = −0.324 | PRESERVED — confirmed in all sources |
| 99.7% argmax change under 1.4B-PPO | PRESERVED — exact counts verified |
| H3 ratios (0.32, 0.26, 0.73) | PRESERVED — verified against h-m3 |
| DPO > PPO in all 3 sizes | PRESERVED but 2.8B margin is within overlapping CIs |
| H-M4 not executed | PRESERVED — honest limitation disclosure |

---

*R2 review completed 2026-03-15. Adversary Agent v2.0.*
