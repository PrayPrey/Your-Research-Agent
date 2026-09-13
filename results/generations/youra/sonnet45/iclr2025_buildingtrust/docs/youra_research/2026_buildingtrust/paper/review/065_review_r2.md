# Adversarial Review — Round 2
**Paper**: Geometric Fingerprints of Alignment: Pre-Alignment Confidence Margin Predicts Argmax Instability After RLHF
**Round**: R2 — Numerical Verification and Credibility
**Completed**: 2026-03-17T07:30:00Z
**Personas**: Accuracy Checker, Skeptical Expert
**Reviewer**: Adversary Agent (Anonymous Pipeline v2.0)

---

## Serena MCP Verification Log

| # | Search | Pattern | File | Result |
|---|--------|---------|------|--------|
| 1 | AUROC values | `AUROC\|auroc\|0\.867\|0\.803\|0\.909\|0\.8668\|0\.8034\|0\.9086` | h-e1/04_validation.md | Found: MMLU=0.8668, TruthfulQA=0.8034, ARC=0.9086 |
| 2 | Beta coefficient | `beta\|β\|coefficient\|-4\.33\|-4\.3295` | h-e1/04_validation.md | Found: β₁=-4.3295 (pair2 DPO) |
| 3 | p-values | `p.value\|p=\|pvalue\|1\.000\|0\.0028\|0\.0047\|10\^-227` | h-e1/04_validation.md | Found: p≈10⁻²²⁷ (pair2), p=0.00195 (pair4) |
| 4 | Anisotropy ratios | `anisotropy\|eigenvalue\|2\.89\|4\.57\|2\.8996\|4\.5789\|1\.13` | h-m1/04_validation.md | Found: pair2=2.8996 p=0.0028, pair4=4.5789 p=0.0047, control=1.13 |
| 5 | Quintile variances | `quintile\|variance\|Q1\|Q5\|0\.707\|3\.384\|4\.79\|4\.785` | h-m2/04_validation.md | Found: DPO Q1=0.707, Q5=3.384; SFT Q1=0.223, Q5=0.281 |
| 6 | Flip rate | `flip.rate\|12\.5\|0\.125` | h-e1/04_validation.md | Found: flip_rate=12.5% |
| 7 | Dataset sizes | `14,042\|14042\|817\|1,172\|1172` | h-e1/04_validation.md | Found: MMLU=14,042, TruthfulQA=817, ARC=1,172 |

**Total Serena searches performed: 7**

---

## Ground Truth Verification Table (R2)

| Claim ID | Claim | Paper (R1) | Ground Truth | Serena Verified | Match |
|----------|-------|-----------|--------------|-----------------|-------|
| C1 | AUROC=0.91 in abstract | "AUROC of 0.91 (range 0.80–0.91)" | ARC=0.9086 rounds to 0.91; range 0.8034–0.9086 → 0.80–0.91 ✓ | h-e1 line 58: ARC=0.9086 | PASS |
| C2 | β₁ = −4.33 | "β₁ = −4.33" | exact: −4.3295, rounds to −4.33 ✓ | h-e1 line 49: **-4.3295** | PASS |
| C3 | p ≈ 10⁻²²⁷ | "p ≈ 10⁻²²⁷" | exact: 4.13×10⁻²²⁷; representation correct ✓ | h-e1 line 49: ~10⁻²²⁷ | PASS |
| C4 | η² = 0.289 | "η² = 0.289" | exact: 0.2892, rounds to 0.289 ✓ | h-e1 line 49: 0.2892 | PASS |
| C5 | AUROC range 0.867–0.909 | "AUROC values of 0.867–0.909" | MMLU=0.8668→0.867, ARC=0.9086→0.909; excludes TruthfulQA=0.8034 | h-e1 lines 56–58 confirm all three | PASS (see note) |
| C6 | Anisotropy 2.9–4.6× | "2.9–4.6 times larger than remaining axes" | pair2=2.8996≈2.90; pair4=4.5789≈4.58; range 2.9–4.6 ✓ | h-m1 lines 72,75 | PASS |
| C7 | DPO Q1=0.71, Q5=3.38, 4.79× | Table 3 shows Q1=0.707, Q5=3.384, ratio=4.79× | exact Q1=0.707, Q5=3.384, ratio=4.785; all correct ✓ | h-m2 line 98: Q1=0.707, Q5=3.384 | PASS |
| C8 | SFT Q5/Q1 ≈ 1.26× | "SFT flat… Q5/Q1 ratio ≈ 1.26×" | Q1=0.223, Q5=0.281; ratio=0.281/0.223=1.260 ✓ | h-m2 line 99 | PASS |
| C9 | 14,042 MMLU items | "14,042 MMLU items" | exact: 14,042 ✓ | h-e1 line 36 | PASS |
| C10 | Isotropic control ≈ 1.13 | "isotropic control of approximately 1.13" | exact: 1.13 ✓ | h-m1 line 60 | PASS |
| C13 | SFT AUROC=0.609 | "AUROC = 0.609" | exact: 0.6087; rounds to 0.609 ✓ | h-e1 line 51: 0.6087 | PASS |

**Note on C5**: The paper's "range 0.867–0.909" is the MMLU-to-ARC span, excluding TruthfulQA (0.8034). This is an acceptable selective framing — but it requires scrutiny. See Persona 2 discussion.

---

## R1 Fixes Verification

| Fix | Status | Evidence |
|-----|--------|---------|
| Abstract now includes AUROC range "(range 0.80–0.91)" | PASS | Abstract line: "AUROC of 0.91 (range 0.80–0.91 across benchmarks)" — TruthfulQA=0.8034→0.80, ARC=0.9086→0.91. Range now correctly encompasses all three benchmarks including TruthfulQA. |
| Results RQ2 no longer claims "2.6× to 4.1× above isotropic reference" | PASS | Results RQ2 says: "anisotropy ratios of 2.8996 (p=0.0028) for DPO… and 4.5789 (p=0.0047) for SFT… both values substantially above the isotropic control of approximately 1.13" — table values used correctly, no erroneous "2.6× to 4.1×" range. |
| Related work boilerplate sentence appears only once | PASS | No repeated boilerplate sentence detected in Related Work section (Section 2). Each paragraph has unique framing. |
| Discussion Limitation 2 has bounding argument | PASS | Limitation 2 now includes: "the 3.8-fold ratio difference… would need to account for… which is implausible given that the two models have similar parameter counts (~7B and ~6.9B)." Bounding argument present. |
| SFT weak result uses multi-factor explanation | PASS | "The weaker SFT result is consistent with multiple explanations: SFT does not optimize a pairwise preference objective… but differences in model scale, architecture, or training data quality… could also contribute." Multi-factor explanation present. |

All five R1 fixes verified as correctly applied.

---

## PERSONA 1: Accuracy Checker (R2)

### FATAL Issues

None found.

All key numerical claims in the paper match the ground truth (065_ground_truth.yaml) and Serena-verified validation files (h-e1, h-m1, h-m2 04_validation.md files) to within acceptable rounding. No fabricated, inflated, or misattributed numbers were detected.

### MAJOR Issues

**M-AC-1 (MINOR boundary): Table 1 AUROC columns do not include TruthfulQA and ARC columns for pair4 (SFT)**

Table 1 shows AUROC (TruthfulQA) and AUROC (ARC) columns as "—" for pair4. This is acceptable if pair4 was only run on MMLU (AUROC=0.609). The validation file (h-e1 line 51) confirms pair4 gate result was based on MMLU only; TruthfulQA/ARC cross-benchmark values for pair4 are not in the validation data. The paper correctly shows "—" rather than fabricating values. No issue.

**M-AC-2 (MINOR): Abstract AUROC range "0.80–0.91" slightly imprecise**

The abstract states "AUROC of 0.91 (range 0.80–0.91 across benchmarks)". Ground truth shows TruthfulQA=0.8034 (→0.80) and ARC=0.9086 (→0.91). The range is numerically correct. However, stating the range ends at 0.91 while also using 0.91 as the headline figure risks implying the maximum is more extreme than it is. Acceptable per ground truth's "known_acceptable_simplifications" but worth flagging as a transparency note for human review. Severity: MINOR.

**M-AC-3 (MINOR): Table 3 Q5/Q1 ratio reported as 4.79× but arithmetic gives 4.785×**

Paper Table 3 states "4.79×" for DPO Q5/Q1. Ground truth gives Q5=3.384, Q1=0.707, ratio_exact=4.785. Conclusion repeats "4.79× gradient." 4.785 rounds to 4.79 at 3 significant figures — arithmetically correct. The ground truth explicitly accepts "ratio≈4.79×" as acceptable rounded form. No issue.

### MINOR Issues

None requiring corrections. The two items above are flagged for human awareness but do not require paper revisions.

---

## PERSONA 2: Skeptical Expert (R2)

### FATAL Issues

None found.

### MAJOR Issues

**M-SE-1: "Range 0.867–0.909" in Section 5 and Discussion is the MMLU-to-ARC range — TruthfulQA (0.803) is below this range**

The paper uses "AUROC values for pair 2 span 0.8034–0.9086 across the three benchmarks" correctly in Results (Section 5). But the Introduction (§1.3 Contributions) states "achieves AUROC 0.87–0.91 across three benchmarks" — this explicitly excludes TruthfulQA (0.803). The Discussion Finding 1 says "AUROC = 0.867–0.909 for DPO-aligned models" with no qualifier that TruthfulQA is below this range.

**Assessment**: The paper does handle this correctly in two places: (a) the abstract now correctly uses "range 0.80–0.91" encompassing all three benchmarks; (b) Section 5 Results correctly states "span 0.8034–0.9086." The problem is that Introduction and Discussion use the narrower "0.867–0.909" range without clarifying it excludes TruthfulQA. A reader scanning the Introduction or Discussion alone would believe all three benchmarks fell in the 0.867–0.909 range, which is false for TruthfulQA (0.803).

**Severity**: MAJOR. The abstract correctly includes TruthfulQA in the range (0.80–0.91), but this is not consistently maintained in the Introduction and Discussion where "0.867–0.909" appears without qualification. The R1 fix applied the correction only to the abstract; the Introduction and Discussion still contain the narrower framing. This is not fabrication but is misleading selective reporting.

**Required fix**: Introduction §1.3 and Discussion Finding 1 should either use "0.80–0.91 across all three benchmarks" or explicitly note "AUROC 0.867–0.909 for MMLU and ARC; TruthfulQA at 0.803."

**M-SE-2: RQ2 text contains minor framing ambiguity about what "2.9–4.6 times larger" means**

Section 5 RQ2 states: "The observed non-isotropy corresponds to dominant eigenvalues of 2.8996 (DPO) and 4.5789 (SFT) relative to the isotropic control baseline of 1.13." This sentence is technically imprecise: the anisotropy ratio is λ₁/mean(λ₂,λ₃,λ₄), not a ratio relative to the isotropic control. The values 2.8996 and 4.5789 are already the ratios, not values to be divided by 1.13 again. The sentence makes it sound like 2.8996 and 4.5789 are raw ratios measured against isotropic control=1.13, which is how they should be read — but the phrasing "relative to the isotropic control baseline of 1.13" is grammatically ambiguous and could be read as "2.8996/1.13 ≈ 2.57 is the true ratio."

**Assessment**: The methodology section (§3) correctly defines ρ = λ₁/mean(λ₂,λ₃,λ₄) and the isotropic control yields ρ≈1.13. The reported values 2.8996 and 4.5789 are the ρ values for the actual models, correctly computed. The abstract and conclusion use "2.9–4.6 times larger than remaining axes" which is accurate. The confusing sentence in RQ2 should be clarified for publication but does not misrepresent the data.

**Severity**: MINOR — clarification needed but no numerical error.

### MINOR Issues

**m-SE-3: Figure renumbering consistency**

The paper references figures as: Figure 1 (fig3_roc_curves.png), Figure 2 (fig2_quintile_flip_pair2.png), Figure 3 (fig4_margin_dist_pair2.png), Figure 4 (fig2_quintile_trend.png), Figure 5 (fig1_anisotropy_gate_metrics.png), Figure 6 (fig2_eigenvalue_spectrum.png). The figure numbers in the paper text (1–6) do not match the filenames (fig1, fig2, fig3, fig4 from different analyses). This is expected renumbering for the paper. However, the Figure captions are not shown in the paper markdown — only the filename references. A reader cannot independently verify the figure content. This is a formatting issue for LaTeX phase, not a numerical accuracy concern. Flagged for human review.

**m-SE-4: H-M2 null result framing is honest but the "confidence-dependent amplification" discovery claim requires caveat**

The paper correctly discloses the H-M2 null result and reframes the finding as "confidence-dependent amplification." Limitation 2 includes a bounding argument about model identity confound. However, the Introduction §1.3 (third contribution) describes this as a "previously unreported asymmetry" that "reveals a fundamental difference in how preference-optimization and supervised fine-tuning restructure the logit space" — strong causal language for a finding with a known model-identity confound. The Conclusion also states this "previously unreported asymmetry reveals a fundamental difference." The ground truth (contributions.C_BEHAVIORAL.strength = NOVEL_UNEXPECTED, caveat = "Model identity confound possible; controlled experiment required") confirms the caveat exists but is only fully articulated in the Limitations section, not where the claim is first made.

**Assessment**: The paper would benefit from a hedging phrase in the Introduction where the finding is first characterized — e.g., "consistent with, though not yet causally attributable to, the preference-optimization mechanism." Current framing in the Introduction overstates causal confidence.

---

## Mathematical Validity Analysis

### Check 1: Q5/Q1 ratio arithmetic
- Q5 (exact) = 3.384; Q1 (exact) = 0.707
- Ratio = 3.384 / 0.707 = 4.7878...
- Paper reports 4.79× → rounds correctly ✓
- Alternative check with rounded table values: 3.38/0.71 = 4.76 — this would give a slightly different rounded ratio (4.76 vs 4.79). The paper uses full-precision values for ratio computation and rounds only the final ratio, which is the correct approach. No inconsistency.
- Ground truth ratio_exact = 4.785, which confirms 3.384/0.707 = 4.785... rounded to 4.79 ✓

### Check 2: Anisotropy ratios vs isotropic control framing
- pair2 DPO anisotropy ratio ρ = 2.8996 (this IS λ₁/mean(λ₂,λ₃,λ₄), not λ₁ alone)
- pair4 SFT anisotropy ratio ρ = 4.5789
- Isotropic Gaussian control: ρ ≈ 1.13
- The paper says ratios are "2.9–4.6 times larger than remaining axes" — this is accurate because ρ = λ₁/mean(λ₂,λ₃,λ₄), so ρ>1 directly means the dominant eigenvalue is ρ× the average of remaining eigenvalues.
- "Above the isotropic control of 1.13" is framed correctly: 2.90 > 1.13 ✓; 4.58 > 1.13 ✓
- Mathematical framing is valid.

### Check 3: AUROC range "0.867–0.909" vs actual values
- MMLU: 0.8668 → rounds to 0.867 ✓
- TruthfulQA: 0.8034 → rounds to 0.803 (BELOW the stated range minimum of 0.867)
- ARC: 0.9086 → rounds to 0.909 ✓
- Conclusion: "0.867–0.909" is mathematically the MMLU-to-ARC range (2 of 3 benchmarks). TruthfulQA (0.803) falls below this range. Abstract correctly uses "0.80–0.91" to include TruthfulQA. Introduction and Discussion use the narrower range without explicit caveat — this is the M-SE-1 issue above.

### Check 4: SFT Q5/Q1 ratio
- SFT Q5 = 0.281, Q1 = 0.223
- Ratio = 0.281/0.223 = 1.260... ≈ 1.26 ✓
- Paper states "Q5/Q1 ratio ≈ 1.26×" — correct ✓

### Check 5: η² rounding
- Exact: 0.2892
- Reported: 0.289
- Rounding: 0.2892 → 0.289 (3 decimal places) ✓

### Check 6: SFT β₁ rounding
- Validation file shows β₁ = −0.0617 (pair4 SFT, line 51)
- Paper reports β₁ = −0.062
- Rounding: −0.0617 rounds to −0.062 ✓

All mathematical checks pass.

---

## Round 2 Summary

| Severity | Total | Items |
|----------|-------|-------|
| FATAL | 0 | — |
| MAJOR | 1 | M-SE-1 (TruthfulQA range exclusion in Introduction and Discussion) |
| MINOR (→ human review) | 4 | M-AC-2, M-SE-2, m-SE-3, m-SE-4 |

**Recommendation**: CONTINUE_R3

**Rationale**: One MAJOR issue found — the inconsistent AUROC range reporting between the abstract (correctly "0.80–0.91") and the Introduction/Discussion (uses narrower "0.867–0.909" without flagging TruthfulQA exclusion). This requires a targeted text fix in two locations before the paper can be considered fully accurate. No FATAL numerical discrepancies were found; all core quantitative claims are verified against Serena ground truth files.

---

**Return Summary**:
```yaml
serena_searches_performed: 7
numerical_discrepancies_found: 0
fatal_count: 0
major_count: 1
minor_count: 4
new_human_review_notes: 2
  - note_1: "Introduction §1.3 and Discussion Finding 1 use 0.867–0.909 range without noting TruthfulQA=0.803 is excluded; abstract correctly uses 0.80–0.91"
  - note_2: "Introduction and Conclusion use causal language ('reveals a fundamental difference') for DPO amplification finding that ground truth labels MEDIUM confidence with model-identity confound caveat"
persuasiveness_passed: true  # unchanged from R1; geometric framing compelling, narrative coherent
r1_fixes_verified: 5_of_5_pass
core_numbers_match_ground_truth: true
math_checks_pass: 6_of_6
```
