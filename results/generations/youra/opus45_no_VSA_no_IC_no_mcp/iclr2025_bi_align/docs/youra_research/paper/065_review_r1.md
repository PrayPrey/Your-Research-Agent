# Phase 6.5 Adversarial Review Round 1

**Date:** 2026-08-26
**Paper:** Different Dynamics, Similar Destinations: RLHF and DPO Training Signatures at 7B Scale

---

## Persona 1: Accuracy Checker

### Numerical Claims Verification

| Claim ID | Paper Claim | Ground Truth | Source | Status |
|----------|-------------|--------------|--------|--------|
| Q1 | Reward range 0.83 units | 0.83 ([-0.47, 0.36]) | h-m1/04_validation.md | ✓ MATCH |
| Q2 | Sharpness ratio 1.65 | 1.65 (0.343/0.208) | h-m2/04_validation.md | ✓ MATCH |
| Q3 | Max |r| = 0.040 | 0.040 | h-e1/04_validation.md | ✓ MATCH |
| Q4 | Clustering gap -0.016 | -0.0162 | h-m3/04_validation.md | ✓ MATCH (rounded) |
| Q5 | Max |d| = 0.194 | 0.194 | h-m4/04_validation.md | ✓ MATCH |
| Q6 | Profile correlation 0.978 | 0.978 | h-m4/04_validation.md | ✓ MATCH |
| - | Pass rate 60% | 3/5 hypotheses | 045_validated_hypothesis.md | ✓ MATCH |

### Calculation Verification

- Sharpness ratio: 0.343 / 0.208 = 1.649 ≈ 1.65 ✓
- Clustering gap: 0.967 - 0.983 = -0.016 ✓
- Pass rate: H-E1 + H-M1 + H-M2 = 3 PASSED / 5 total = 60% ✓

**FATAL issues:** 0
**MAJOR issues:** 0
**MINOR issues:** 0

---

## Persona 2: Bored Reviewer

### First Impression (2-minute scan)

| Aspect | Assessment |
|--------|------------|
| Abstract hook | "different dynamics, similar destinations" — compelling, memorable |
| Novelty claim visible | Yes, within first 2 paragraphs |
| Main finding clear | Yes — mechanistic differences don't manifest downstream |
| Reading engagement | Good — negative result framed as important finding |

### Structure Check

- Clear hypothesis table: ✓
- Results summary table: ✓
- Figures referenced: Not checked (paper text only)

### Issues Found

**MINOR-1:** "Predictions supported: 1/3" in Results summary is potentially confusing alongside "Overall pass rate: 60%". Casual reader may not understand these refer to different things.

---

## Persona 3: Skeptical Expert

### Novelty Claims Audit

| Claim | Assessment |
|-------|------------|
| N1: First smoothness vs sharpness comparison | Plausible — no obvious prior work on identical data/model comparison |
| N2: Falsification of attractor hypothesis | Valid contribution — negative results are publishable |
| N3: Benchmark sensitivity limitation | Reasonable secondary finding |

### Baseline Fairness

| Factor | RLHF | DPO | Fair? |
|--------|------|-----|-------|
| Base model | Llama-2-7B | Llama-2-7B | ✓ |
| Dataset | HH-RLHF | HH-RLHF | ✓ |
| LoRA config | r=16, alpha=32 | r=16, alpha=32 | ✓ |
| Training epochs | 1 | 1 | ✓ |

**Verdict:** Fair comparison

### Limitations Check

| Expected Limitation | Documented? |
|---------------------|-------------|
| Scale (7B only) | ✓ Section 5 |
| LoRA vs full fine-tuning | ✓ Section 5 |
| Single dataset | ✓ Section 5 |
| Simulation mode for H-M3/H-M4 | ✓ Section 5 |

### Issues Found

**MAJOR-1:** Inconsistent framing between "Predictions supported: 1/3" and "Overall pass rate: 60%" — needs clarification that 1/3 refers to causal chain predictions specifically.

**MINOR-2:** Abstract mentions "five-hypothesis experiment" without noting that 2 are partial — could mislead casual readers.

---

## Round 1 Summary

| Severity | Count | Details |
|----------|-------|---------|
| FATAL | 0 | — |
| MAJOR | 1 | Inconsistent prediction/pass-rate framing |
| MINOR | 2 | Results table clarity; abstract framing |

### Required Actions

1. **MAJOR-1 FIX:** Clarify "1/3 predictions" refers to causal chain, "60%" to overall hypotheses

### Deferred to Human Review

- MINOR-1, MINOR-2: Collected in 065_human_review_notes.md
