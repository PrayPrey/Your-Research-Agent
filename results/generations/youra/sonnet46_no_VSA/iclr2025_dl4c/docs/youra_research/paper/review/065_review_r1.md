# Adversarial Review — Round 1
**Paper**: What Does Code SFT Actually Teach? Source Identity Governs Benchmark Performance via Distributional Alignment  
**Date**: 2026-08-03  
**Round**: R1 — Accuracy and Engagement  
**Personas**: Accuracy Checker, Bored Reviewer, Skeptical Expert

---

## Ground Truth Summary

| Metric | Ground Truth Value | Source |
|--------|-------------------|--------|
| HE-only 1.3B mean pass@1 | 35.0% (seeds: 39.6, 25.6, 39.6) | h-e2/results/all_results.csv |
| MBPP-only 1.3B mean pass@1 | 27.6% (seeds: 29.3, 27.4, 26.2) | h-e2 CSV |
| LeetCode-only 1.3B per-seed | seed_42=0.0%, seed_123=0.0%, seed_777=9.15% → mean=3.05% | h-e2 CSV |
| Equal-mix 1.3B per-seed | seed_42=10.4%, seed_123=9.8%, seed_777=10.4% → mean=10.2% | h-e2 CSV |
| ANOVA F=11.37, p=0.020 | CONFIRMED | ground_truth.yaml |
| Spearman ρ=1.0, p=0.0417 | CONFIRMED | h-m2/04_validation.md |
| HE-only 7B mean | 38.6% | h-c1/04_validation.md |
| Equal-mix 7B mean | 39.6% (highest) | h-c1/04_validation.md |
| HE-only MBPP+ per-seed | 52.4%, 51.9%, 51.6% | h-m1/04_validation.md |

---

## Executive Summary

| Severity | Count |
|----------|-------|
| FATAL | 2 |
| MAJOR | 3 |
| MINOR | 4 |

**Recommendation**: MUST REVISE before submission. Two fatal contradictions in Introduction (wrong numbers). Three major issues affecting credibility.

**Persuasiveness**: PASS — paper is engaging, hook is strong, structure is clear.

---

## FATAL Issues

### FATAL-001: Introduction reports 32.6% for HumanEval-only mean — contradicts Table 1 (35.0%) and CSV (35.0%)

**Location**: Section 1 (Introduction), paragraph beginning "Under identical token budgets"  
**Text**: "HumanEval-only training achieves 32.6% HumanEval+ pass@1 while LeetCode-only training achieves 3.0%"  
**Ground Truth**: h-e2 CSV: HE-only seeds = 39.6%, 25.6%, 39.6% → mean = 35.0%  
**Contradiction**: 32.6% appears nowhere in the ground truth. Table 1 (same paper) shows 35.0%.  
**Impact**: Reviewer reads Introduction, notes 32.6%. Reads Table 1, sees 35.0%. Immediate credibility loss.  
**Fix**: Replace "32.6%" with "35.0%" throughout Introduction.

### FATAL-002: Introduction bullet 3 reports "HumanEval-only achieves 35.9%" — contradicts Table 1 (35.0%)

**Location**: Section 1 (Introduction), contributions bullet 3  
**Text**: "HumanEval-only training achieves the highest pass@1 on both HumanEval+ (35.9%)"  
**Ground Truth**: Mean = 35.0% (h-e2 CSV). h-m1 transfer table shows 35.9% but h-m1 notes it used the same seeds — the discrepancy is unexplained.  
**Contradiction**: 35.9% vs 35.0% within same paper.  
**Impact**: Three different numbers for the same quantity (32.6%, 35.0%, 35.9%) in the same paper — catastrophic for credibility.  
**Fix**: Unify all references to HumanEval-only 1.3B mean as 35.0% (h-e2 CSV is ground truth). Remove or correct the 35.9% reference. Note: h-m1 shows 35.9% in its transfer matrix — check if h-m1 used different evaluation or rounding; if so, clarify or use consistent source.

---

## MAJOR Issues

### MAJOR-001: LeetCode per-seed values wrong in Table 1

**Location**: Section 5.1, Table 1  
**Text**: Seeds shown as "~3.1% | ~3.1% | ~3.1%"  
**Ground Truth**: seed_42=0.0%, seed_123=0.0%, seed_777=9.15%  
**Error**: The per-seed values are incorrect. Only seed 777 has non-zero performance; seeds 42 and 123 are exactly 0%.  
**Mean is correct** (3.05% ≈ ~3.1%) but presenting per-seed as three identical ~3.1% values is factually wrong.  
**Impact**: Reviewers checking seed variance will find this. A skeptical reviewer may compute the mean from the displayed per-seed values and get 3.1% (consistent), but the variance pattern would look suspicious.  
**Fix**: Correct Table 1 to show: "seed_42: 0.0% | seed_123: 0.0% | seed_777: 9.1% | Mean: ~3.1%"

### MAJOR-002: Equal-mix Seed 42 and Seed 123 values transposed in Table 1

**Location**: Section 5.1, Table 1  
**Text**: "Equal-mix | 9.8% | 10.4% | 10.4%"  
**Ground Truth**: seed_42=10.4% (0.1037), seed_123=9.8% (0.0976), seed_777=10.4% (0.1037)  
**Error**: Seed 42 shows 9.8% in Table 1 but is actually 10.4%. Seed 123 shows 10.4% but is actually 9.8%.  
**Mean is correct** (10.2%) but seed-level values are swapped.  
**Fix**: Correct Table 1 to: "seed_42: 10.4% | seed_123: 9.8% | seed_777: 10.4%"

### MAJOR-003: LeetCode near-zero performance unaddressed as potential training failure

**Location**: Section 5.1, Section 6.4 (Limitations)  
**Issue**: LeetCode-only training achieves 0.0% on seeds 42 and 123 — not merely "low performance" but complete failure. The paper frames this as a "source identity effect" without verifying that LeetCode SFT training converged (loss curves, training stability).  
**Risk**: If LeetCode training failed/collapsed, the 29.6pp gap reflects training failure confounding source identity — a fundamental validity threat.  
**Current text**: No acknowledgment of this concern.  
**Fix**: Add to Section 6.4 (Limitations): "LeetCode-only training achieved 0.0% on 2/3 seeds at 1.3B scale (seed_42 and seed_123), with only seed_777 showing 9.1%. While the interpretation as a source identity effect is plausible, we did not verify training convergence (loss curves) for LeetCode conditions separately. Future work should confirm LeetCode SFT training stability at this scale."

---

## MINOR Issues (for human review — NOT auto-fixed)

1. **MINOR-001** (style): Introduction: "This effect dwarfs most reported architectural improvements" — unsupported comparative claim. Needs citation or softer language ("may dwarf" or "exceeds many").
2. **MINOR-002** (clarity): Abstract mentions "by up to 1.5 percentage points" for MBPP+ cross-benchmark advantage (in Introduction hook), then later uses "~52% vs ~50.5%". Consistent framing would help.
3. **MINOR-003** (style): "dwarfs" is informal for ICML — consider "exceeds" or "substantially exceeds."
4. **MINOR-004** (formatting): Table 1 caption doesn't mention that LeetCode values are approximate (~). The table header should clarify this.

---

## Ground Truth Verification Log

| Claim | Source Checked | Match |
|-------|---------------|-------|
| HE-only mean 35.0% (Table 1) | h-e2/results/all_results.csv | ✓ |
| MBPP-only mean 27.6% (Table 1) | h-e2 CSV | ✓ |
| LeetCode mean ~3.1% (Table 1) | h-e2 CSV | ✓ (mean correct, per-seed wrong) |
| Equal-mix mean 10.2% (Table 1) | h-e2 CSV | ✓ (mean correct, per-seed swapped) |
| ANOVA F=11.37, p=0.020 | ground_truth.yaml | ✓ |
| Spearman ρ=1.0, p=0.0417 | h-m2/04_validation.md | ✓ |
| CodeBERT sim values (Table 3) | h-e1/04_validation.md | ✓ |
| 7B Table 4 values | h-c1/04_validation.md | ✓ |
| MBPP+ Table 2 values | h-m1/04_validation.md | ✓ |
| HE-only 32.6% (Intro text) | h-e2 CSV | ✗ FATAL: actual 35.0% |
| HE-only 35.9% (Intro bullet 3) | h-e2 CSV | ✗ FATAL: actual 35.0% |

---

## Persuasiveness Check (Bored Reviewer)

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | Counterintuitive finding + specific numbers |
| Problem clear in 1 minute? | PASS | Hook paragraph is effective |
| Novelty clear in 2 minutes? | PASS | Contributions clearly stated |
| Figure 1 self-explanatory? | LIKELY PASS | Caption adequate; cannot verify actual figure |
| Would continue reading? | YES | |
| Attention lost at? | Table 1 LeetCode row | Inconsistent per-seed values would catch attentive reviewer |
| False novelty claims? | 0 | |
| Unfair baseline comparisons? | 0 | |
| Overclaims found? | 1 (MINOR-001) | "dwarfs architectural improvements" |
| Missing limitations? | 1 (MAJOR-003) | LeetCode training failure not acknowledged |

---

## Summary for Revision Agent

**Priority 1 — FATAL (must fix)**:
1. Replace all instances of "32.6%" with "35.0%" in Introduction
2. Replace "35.9%" in contributions bullet 3 with "35.0%"
3. Verify and reconcile the 35.9% figure from h-m1 — if h-m1 is authoritative, update Table 1 instead; but h-e2 CSV is ground truth

**Priority 2 — MAJOR (must fix)**:
4. Fix Table 1 LeetCode per-seed values: show 0.0%, 0.0%, 9.1%
5. Fix Table 1 Equal-mix per-seed values: swap seed_42 (10.4%) and seed_123 (9.8%)
6. Add limitation note about LeetCode training convergence not verified

**Priority 3 — MINOR (collect for human review)**:
7. Soften "dwarfs" claim or add citation
8. Style: "dwarfs" → "exceeds"
