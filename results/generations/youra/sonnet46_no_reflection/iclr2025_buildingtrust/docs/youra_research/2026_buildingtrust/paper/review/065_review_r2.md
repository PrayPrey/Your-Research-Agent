# Adversarial Review — Round 2

**Paper:** Adversarial Fragility and Calibration Are Anticorrelated After Capability Control: A Residual Instability Analysis Across 30 Large Language Models
**Reviewed:** 2026-05-12T17:30:00
**Reviewer Version:** Adversary Agent v2.0 (inline execution)
**Round:** R2 — Numerical Verification and Credibility
**Input Paper:** paper/06_paper_r1.md
**Personas:** Accuracy Checker, Skeptical Expert

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Accuracy (numerical) | 0 | 0 | ✓ OK |
| Credibility (baselines, scope) | 0 | 0 | ✓ OK |
| **TOTAL** | **0** | **0** | ✓ CLEAN |

**Recommendation:** CONDITIONAL_ACCEPT — All numerical claims verified against source files. No new FATAL or MAJOR issues found. R1 fixes confirmed correctly applied.

---

## Serena MCP Verification Log

> Note: `mcp__serena__search_for_pattern` was not available in this session.
> Equivalent verification performed using Grep against actual Phase 4/5 result files.
> All searches conducted against: h-e1/04_validation.md, h-m1/04_validation.md, h-e1/03_config.md, 045_validated_hypothesis.md

| Search | Pattern | File | Result |
|--------|---------|------|--------|
| Primary correlation | `ρ(RI, ECE\|PC1)` | h-m1/04_validation.md | ρ=−0.5347 ✓ |
| p-value | `p.*0.0034` | h-m1/04_validation.md | p=0.0034 ✓ |
| Bootstrap CI | `[-0.782, -0.101]` | h-m1/04_validation.md | confirmed ✓ |
| SD gate | `0.1212` | h-e1/04_validation.md | 0.1212 ✓ |
| R² gate | `0.5285` | h-e1/04_validation.md | 0.5285 ✓ |
| VIF | `VIF.*1.000` | h-e1/04_validation.md | 1.000 ✓ |
| PC1 variance | `68.5%\|68.54` | h-e1/04_validation.md | 0.6854 ✓ |
| Bootstrap samples | `10.000\|10,000` | h-e1/03_config.md | 10000 ✓ |
| Seed | `seed.*42` | h-e1/04_validation.md | 42 ✓ |
| Mistral ρ | `-0.827` | h-m1/04_validation.md | −0.827 ✓ |
| Mistral raw p | `p.*0.173` | h-m1/04_validation.md | 0.173 ✓ |
| Mistral Holm p | `Holm.*0.519` | h-m1/04_validation.md | 0.519 ✓ |
| Outlier removal ρ | `-0.498` | h-m1/04_validation.md | −0.498 ✓ |
| Baseline ρ(PC1,ECE) | `-0.511` | h-m1/04_validation.md | −0.511 ✓ |
| n models | `30` | h-e1/04_validation.md | 30 ✓ |
| n families | `9` | h-e1/04_validation.md | 9 ✓ |

---

## Ground Truth Verification Table

| Claim | Paper (r1) | Source File | Verified | Match |
|-------|-----------|-------------|----------|-------|
| ρ(RI, ECE\|PC1) = −0.535 | −0.535 | h-m1/04_validation.md (−0.5347) | ✓ | ✓ rounds correctly |
| p = 0.0034 | 0.0034 | h-m1/04_validation.md | ✓ | ✓ |
| 95% CI = [−0.782, −0.101] | [−0.782, −0.101] | h-m1/04_validation.md | ✓ | ✓ |
| n = 30 | 30 | h-e1/04_validation.md | ✓ | ✓ |
| SD = 0.1212 | 0.1212 | h-e1/04_validation.md | ✓ | ✓ |
| R² = 0.5285 | 0.5285 | h-e1/04_validation.md | ✓ | ✓ |
| VIF = 1.000 | 1.000 | h-e1/04_validation.md | ✓ | ✓ |
| PC1 = 68.5% | 68.5% | h-e1/04_validation.md (0.6854) | ✓ | ✓ |
| Bootstrap = 10,000 | 10,000 | h-e1/03_config.md | ✓ | ✓ |
| seed = 42 | 42 | h-e1/04_validation.md | ✓ | ✓ |
| Mistral ρ = −0.827 | −0.827 | h-m1/04_validation.md | ✓ | ✓ |
| Mistral p(raw) = 0.173 | 0.173 (now stated) | h-m1/04_validation.md | ✓ | ✓ (R1 fix applied) |
| Mistral p(Holm) = 0.519 | 0.519 | h-m1/04_validation.md | ✓ | ✓ (R1 fix applied) |
| LLaMA ρ = −0.244 | −0.244 | h-m1/04_validation.md | ✓ | ✓ |
| Qwen ρ = +0.364 | +0.364 | h-m1/04_validation.md | ✓ | ✓ |
| Outlier removal ρ = −0.498 | −0.498 | h-m1/04_validation.md | ✓ | ✓ |
| Baseline ρ(PC1, ECE) = −0.511 | −0.511 | h-m1/04_validation.md | ✓ | ✓ |
| 73% OLS-estimated | 73%/22 of 30 | h-e1/04_validation.md | ✓ | ✓ |
| 11 anchor models | 11 | h-e1/04_validation.md | ✓ | ✓ |
| ECE range 0.175–0.472 | 0.175–0.472 | h-m1/04_validation.md | ✓ | ✓ |
| arc_challenge n=1,172 | 1,172 | h-m1/04_validation.md | ✓ | ✓ |

**All 21 numerical claims verified. Zero discrepancies.**

---

## Mathematical Validity Analysis

### Check 1: ρ rounding consistency
Paper reports ρ=−0.535; source shows −0.5347. Round(−0.5347, 3) = −0.535. ✓ Correct rounding.

### Check 2: p-value Holm correction consistency
Primary p=0.0034 with Holm correction threshold α=0.0125 for 4 pre-registered predictions: 0.0034 < 0.0125 ✓. Family-level Holm corrections all non-significant (correct, n=6–9 is underpowered). ✓

### Check 3: SD bootstrap CI consistency
SD=0.1212, 95% CI=[0.093, 0.138]. CI lower bound 0.093 > threshold 0.05. SD is 2.4× threshold. Mathematically consistent. ✓

### Check 4: R² bootstrap CI consistency
R²=0.5285, 95% CI=[0.275, 0.721]. CI upper bound 0.721 < threshold 0.80. Mathematically consistent. ✓

### Check 5: Outlier removal effect
Full sample: ρ=−0.535, n=30. After removing 3 outliers: ρ=−0.498, n=27. Direction preserved, magnitude slightly attenuated. Mathematically plausible. ✓

### Check 6: ρ(PC1,ECE) vs ρ(RI,ECE|PC1) comparison
Both ≈ −0.51 to −0.54. Fisher z-test non-significant (z=−0.561, p=0.575). Paper's claim of "similar magnitude" is mathematically supported. ✓

---

## Baseline Fairness Assessment

The study's "baselines" are statistical predictors, not competing ML models:
- **PC1-only predictor**: Same data, same models, computed from same pipeline. Fair. ✓
- **Raw AdvGLUE-ECE correlation**: Same data without residualization. Fair. ✓

No literature-reported baseline numbers to verify (this is a correlation study, not a benchmark comparison).

---

## R1 Fix Verification

| Fix | Location | Applied? | Correct? |
|-----|----------|----------|----------|
| Narrowed abstract scope | Abstract final sentence | ✓ | ✓ |
| Narrowed conclusion scope | Section 7 | ✓ | ✓ |
| Added arc_challenge circularity L7 | Section 6.2 | ✓ | ✓ |
| Figure 1 caption note | Section 3.4 | ✓ | ✓ |
| Section 5.2 reframe | Section 5.2 observation 2 | ✓ | ✓ |
| Mistral p-value clarification | Section 5.3 table + prose | ✓ | ✓ |

**All 6 R1 fixes correctly applied.**

---

## FATAL Issues — R2

*None found.*

---

## MAJOR Issues — R2

*None found.*

---

## Human Review Notes (R2 additions)

| Location | Note | Type |
|----------|------|------|
| Section 3.3 | "ARC-Challenge" capitalization inconsistent (sometimes "arc_challenge", sometimes "ARC-Challenge") | formatting |
| Section 5.2 | "ρ(RI, ECE\|PC1) = −0.535" — consider using consistent notation throughout (sometimes written with \|PC1, mean_confidence\|) | clarity |

---

## Summary

Round 2 numerical verification found **zero discrepancies** between paper claims and source validation files. All 21 checked values match. All 6 Round 1 fixes are correctly applied. The paper is numerically accurate and ready for finalization.

```yaml
agent: "adversary-v2"
round: "R2"
status: "COMPLETED"
output_file: "paper/review/065_review_r2.md"
verification_method: "Grep against Phase 4/5 validation files (Serena search_for_pattern unavailable)"

summary:
  accuracy:
    fatal: 0
    major: 0
    ground_truth_discrepancies: 0
    claims_verified: 21

  credibility:
    fatal: 0
    major: 0
    false_novelty_claims: 0
    unfair_baselines: 0

  totals:
    fatal: 0
    major: 0

  human_review_notes_count: 2

  recommendation: "CONDITIONAL_ACCEPT"

  key_findings:
    - "All 21 numerical claims verified against source files"
    - "All R1 fixes correctly applied"
    - "No new issues found in R2"
```
