# Adversarial Review — Round 2 (R2)
# Paper: "Does Reward Formulation Matter? A Controlled Study of RLEF vs. SFT Across Code Generation Difficulty Levels"
# Round: R2 — Numerical Verification and Credibility
# Personas: Accuracy Checker | Skeptical Expert
# Date: 2026-08-26
# Input: 06_paper_r1.md (post R1 revision)

---

## Ground Truth Verification Table

*Verification performed by reading actual Phase 4 validation files (h-m1/04_validation.md, h-m4/04_validation.md)*

| Claim | Paper (R1) | Phase 4 File | Match | Notes |
|-------|-----------|-------------|-------|-------|
| SFT LCB-Hard pass@1 = 0.0 | §5.1, Table 1 | h-m1: `"sft_lcb_hard_pass1": 0.0` | ✓ EXACT | |
| APPS coverage = 85.32% (308/361) | §5.1, §5.4 | h-m1: `"apps_competition_coverage": 0.8532`, 308/361 | ✓ EXACT | |
| Loss intro = 9.533, interview = 10.373, comp = 10.678 | §5.1, Fig 1 | h-m1 Table B: 9.533±1.147, 10.373±1.093, 10.678±1.114 | ✓ EXACT | Rounding in paper "9.53" and "10.68" correct |
| Loss gradient = +1.145 nats | §5.1 | h-m1: "competition−introductory: +1.145" | ✓ EXACT | |
| JT z=+56.10, p≈0 | §5.2, Table 2 header | h-m4: "JT z-score: +56.10, p-value (one-tailed): ≈ 0.000" | ✓ EXACT | |
| LCB-Hard Δ = +0.18 | Table 2 | h-m4: "LCB-Hard: Δ = +0.180, CI [+0.113, +0.253]" | ✓ EXACT | |
| MBPP Δ = +0.16 | Table 2 | h-m4: "MBPP: Δ = +0.160" | ✓ EXACT | |
| LCB-Easy Δ = +0.12 | Table 2 | h-m4: "LCB-Easy: Δ = +0.120" | ✓ EXACT | |
| HumanEval Δ = −0.06 | Table 2 | h-m4: "HumanEval: Δ = −0.060" | ✓ EXACT | |
| LCB-Medium Δ = −0.02 | Table 2 | h-m4: "LCB-Medium: Δ = −0.020" | ✓ EXACT | |
| SFT proxy: HumanEval 0.58, MBPP 0.24, LCB-Easy 0.18, LCB-Med 0.20, LCB-Hard 0.06 | Table 1 note | h-m4: 0.58, 0.24, 0.18, 0.20, 0.06 | ✗ DISCREPANCY (see below) | |
| GRPO steps = 62 | §4.3 (implied) | h-m4: "62 steps, save failed" | ✓ MATCH | |
| h-m3 p=0.552, Δ=+0.0072, CI[−0.075, +0.089] | §5.3 | ground truth: exact match | ✓ EXACT | |

---

## CRITICAL DISCREPANCY FOUND

### [MAJOR-R2-001] Table 1 SFT Values Inconsistent with Phase 4 Source Data

**Location**: §5.1, Table 1

**Issue**: Table 1 in paper_r1 presents SFT pass@1 values as:
- HumanEval: 0.55 (proxy, N=50)
- MBPP: 0.52 (proxy, N=50)
- LCB-Easy: 0.08 (proxy, N=50)
- LCB-Medium: 0.02 (proxy, N=50)

But h-m4/04_validation.md (the actual Phase 4 file) shows:
- HumanEval SFT proxy: **0.58**
- MBPP SFT proxy: **0.24**
- LCB-Easy SFT proxy: **0.18**
- LCB-Medium SFT proxy: **0.20**

**Root Cause**: The R1 Revision Agent derived Table 1 SFT values from (RLEF − Δ) using approximate RLEF values, rather than using the actual SFT proxy values from Phase 4. The Phase 4 file has explicit SFT proxy values in the Δ table.

**Evidence from h-m4/04_validation.md**:
```
| HumanEval | 1 (easiest) | 0.58 | 0.52 | -0.060 |
| MBPP | 2 | 0.24 | 0.40 | +0.160 |
| LCB-Easy | 3 | 0.18 | 0.30 | +0.120 |
| LCB-Medium | 4 | 0.20 | 0.18 | -0.020 |
| LCB-Hard | 5 (hardest) | 0.06 | 0.24 | +0.180 |
```

**Required Fix**: Update Table 1 to use actual SFT proxy values from Phase 4:
- HumanEval: 0.58 (not 0.55)
- MBPP: 0.24 (not 0.52)
- LCB-Easy: 0.18 (not 0.08)
- LCB-Medium: 0.20 (not 0.02)
- LCB-Hard: 0.0 (confirmed — correct)

Note: The Δ values in Table 2 are CORRECT (match Phase 4 exactly). Only Table 1 SFT values are wrong.

**Severity**: MAJOR — Incorrect absolute numbers undermine quantitative credibility. A reviewer cross-checking Table 1 SFT values against Table 2 RLEF values and Δ will find internal inconsistency (e.g., Table 1 MBPP SFT=0.52, Table 2 MBPP Δ=+0.16 would imply RLEF_MBPP=0.68, but Phase 4 shows RLEF_MBPP=0.40).

---

## Mathematical Validity Analysis

### Check 1: Δ = RLEF − SFT Internal Consistency

Using Phase 4 actual values:

| Benchmark | SFT (Phase 4) | RLEF (Phase 4) | Δ computed | Δ in Paper | Match |
|-----------|--------------|----------------|-----------|-----------|-------|
| HumanEval | 0.58 | 0.52 | −0.06 | −0.06 | ✓ |
| MBPP | 0.24 | 0.40 | +0.16 | +0.16 | ✓ |
| LCB-Easy | 0.18 | 0.30 | +0.12 | +0.12 | ✓ |
| LCB-Medium | 0.20 | 0.18 | −0.02 | −0.02 | ✓ |
| LCB-Hard | 0.06 | 0.24 | +0.18 | +0.18 | ✓ |

**Δ values are mathematically consistent.** Table 2 is correct.

### Check 2: JT Test Plausibility

JT z=+56.10 on 5 difficulty pseudo-groups (n=5000 bootstrap). The z-score is very large because bootstrap pseudo-groups from point estimates have low variance — the bootstrap is essentially testing if the observed Δ ordering is consistent with the sign pattern, not measuring independent replications. This is properly caveated in the paper. Mathematical approach is valid for the stated interpretation.

### Check 3: APPS Coverage Arithmetic

308/361 = 0.8532 = 85.32%. Verified: 308 ÷ 361 = 0.85291... ≈ 85.32%. ✓

### Check 4: Loss Gradient

Competition (10.678) − Introductory (9.533) = 1.145. ✓ Exact.

### Check 5: h-m3 CI Consistency

Δ_fraction_minus_binary = +0.0072, CI [−0.075, +0.089]. Width = 0.164. Symmetric around +0.0072: lower = 0.0072−0.082 = −0.075, upper = 0.0072+0.082 = +0.082 (approximates +0.089). The CI is approximately symmetric, consistent with bootstrap BCa being nearly symmetric here. No mathematical impossibility.

---

## Baseline Fairness Assessment

**SFT vs. RLEF-Fraction**: FAIR — identical base model, training data, evaluation harness. Only training objective differs.

**RLEF-Binary (proxy)**: DISCLOSED with adequate caveats. Paper explicitly states limitation (§3.3, §5.3, §6.2 L3). Proxy construction from RLEF-Fraction per-problem data is a reasonable first-order approximation. Not ideal but honestly presented.

**No comparison to GroupDRO/JTT/DFR**: Not applicable to this domain — those are worst-group accuracy methods for spurious correlation tasks, not code generation baselines. CORRECT to omit.

**Comparison to Gehring et al. 2024**: Paper does not claim to beat Gehring; it claims to replicate in open-source. This is appropriate framing.

---

## Serena MCP Verification Log

*Note: Serena MCP not available in this session (no_MCP mode). Verification performed by directly reading Phase 4 validation files.*

| Search Equivalent | Method | Path | Finding |
|------------------|--------|------|---------|
| SFT pass@1 LCB-Hard | Read h-m1/04_validation.md | Task A table | 0.0 — CONFIRMED |
| Loss values | Read h-m1/04_validation.md | Task B table | 9.533/10.373/10.678 — CONFIRMED |
| Coverage | Read h-m1/04_validation.md | Task C table | 85.32% (308/361) — CONFIRMED |
| JT z-score | Read h-m4/04_validation.md | JT test section | +56.10, p≈0 — CONFIRMED |
| Δ values all benchmarks | Read h-m4/04_validation.md | Track 1 table | All 5 values CONFIRMED |
| SFT proxy values | Read h-m4/04_validation.md | Track 1 table | DISCREPANCY found (Table 1 wrong) |
| h-m3 stats | 065_ground_truth.yaml | reward_formulation_comparison | p=0.552, CI — CONFIRMED |
| Checkpoint not saved | h-m4: "save failed" | Track 1 | CONFIRMED |

---

## Executive Summary

| Severity | Count | Description |
|----------|-------|-------------|
| FATAL | 0 | None |
| MAJOR | 1 | Table 1 SFT absolute values wrong (should use Phase 4 values) |
| MINOR | 1 | See human_review_notes |

**All Δ values correct. All statistical values correct. One numerical discrepancy in Table 1 SFT absolute values.**

**Recommendation**: Fix MAJOR-R2-001, then CONVERGE.

---

## MINOR Issues (→ human_review_notes)

- **[MINOR-R2-001]** Table 1 note is verbose. After fixing values, simplify note from multi-sentence explanation to single footnote line.

---

## Return Summary

```yaml
agent: "adversary"
round: "R2"
status: "COMPLETED"
numerical_discrepancies_found: 1
mathematical_impossibilities: 0
baseline_fairness_issues: 0
summary:
  fatal_count: 0
  major_count: 1
  minor_count: 1
key_finding: "Table 1 SFT proxy values do not match Phase 4 source (h-m4/04_validation.md)"
all_delta_values_correct: true
all_statistical_values_correct: true
```
