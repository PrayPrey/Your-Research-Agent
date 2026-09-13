# Phase 6.5 Adversarial Review — Round 1 (R1) Full Report

**Generated:** 2026-08-26
**Paper:** paper/06_paper.md
**Ground truth:** paper/065_ground_truth.yaml

---

## Persona 1: Accuracy Checker

### Quantitative Claims Verification

| Claim | Paper Location | Ground Truth | Status |
|-------|---------------|--------------|--------|
| +8.94pp pass@1 (87.20% vs 78.25%) | Abstract, Table 2 | mean_b=87.20, mean_a=78.25, delta=8.94 | ✅ VERIFIED |
| Seed 42: A=79.9%, B=86.6%, Δ=+6.7pp | Table 2 | seed_42: a=79.9, b=86.6, delta=6.7 | ✅ VERIFIED |
| Seed 123: A=76.8%, B=87.8%, Δ=+11.0pp | Table 2 | seed_123: a=76.8, b=87.8, delta=11.0 | ✅ VERIFIED |
| Seed 456: A=78.1%, B=87.2%, Δ=+9.2pp | Table 2 | seed_456: a=78.1, b=87.2, delta=9.2 | ✅ VERIFIED |
| 70% of HumanEval+ failing have mypy errors | Abstract, RQ1 | humaneval_fraction=0.70 (21/30) | ✅ VERIFIED |
| 0% of MBPP+ failing have mypy errors | Abstract, RQ1 | mbpp_fraction=0.00 (0/21) | ✅ VERIFIED |
| Errors 1.55→0.00 by round 2 | Introduction, RQ2 | round_1_mean=1.55, round_2_mean=0.00 | ✅ VERIFIED |
| Spearman ρ=−0.707 | Introduction, RQ2 | spearman_rho=−0.707 | ✅ VERIFIED |
| n=20 eligible problems (h-m1) | Results §RQ2 | eligible_problems=20 | ✅ VERIFIED |
| 90.9% repair rate both conditions (type-error) | Abstract, Table 1 | repair_rate_a=0.909, repair_rate_b=0.909 | ✅ VERIFIED |
| Type-specificity differential=0.000 | Table 1, Discussion | differential_type=0.000 | ✅ VERIFIED |
| n=22 type-error problems (h-m2) | Table 1 | type_error_problems_n=22 | ✅ VERIFIED |
| 123 arithmetic problems curated | RQ5, Figure 6 | arithmetic_subset_total=123 | ✅ VERIFIED |
| 112 valid Z3 specs (91.1%) | RQ5, Figure 6 | valid_specs=112, spec_validity_rate=0.911 | ✅ VERIFIED |
| CE rate 16.1% (18/112) | Abstract, RQ5 | problems_with_ce=18, ce_rate=0.161 | ✅ VERIFIED |
| Condition B pass@1=86.6% (arithmetic) | Table 3 | pass_at_1_condition_b=0.866 | ✅ VERIFIED |
| Condition C pass@1=85.7% (arithmetic) | Table 3 | pass_at_1_condition_c=0.857 | ✅ VERIFIED |
| Delta C−B=−0.9pp | Table 3 | delta_c_minus_b=−0.009 | ✅ VERIFIED |
| 100% name-defined error category | RQ1 | error_categories="100% name-defined" | ✅ VERIFIED |

**Accuracy verdict:** All quantitative claims verified. No numerical errors in 06_paper.md.

**Additional finding:** sections/05_results.md line 54 contains "p < 0.01 by rank correlation against round index" — incorrect. Actual p=0.182 (n=5 rounds; p<0.05 mathematically unachievable). This is FATAL in the section file (though not in 06_paper.md which does not state a p-value for h-m1).

---

## Persona 2: Bored Reviewer

### Abstract Engagement
- Hook: "we set out to test X, yes — but mechanism is wrong" — strong counterintuitive framing. ✅
- Primary result front-loaded (+8.94pp). ✅
- Novelty stated: "first controlled evidence." ✅
- "general diagnostic context enricher" — jargon without inline definition; may confuse readers. MINOR.
- Length (~180 words) appropriate for ICML. ✅

### Introduction
- "The gap matters for a practical reason" — clear motivation. ✅
- "The results surprised us" — engagement hook. ✅
- Contributions 1–4 clearly delineated. ✅
- ~850 words, well-scoped.

### Related Work
- Four families covered: repair loops, static analysis, benchmarks, formal verification. Adequate but thin. MINOR.
- Missing: test-based repair as alternative structured feedback (ChatUniTest, CodaMosa), broader benchmarks (SWE-bench).

### Conclusion
- "We began by asking whether adding mypy was worth the one-subprocess-call investment. The answer is yes." — strong callback. ✅

**Bored reviewer verdict:** No FATAL or MAJOR engagement issues. Two MINOR items.

---

## Persona 3: Skeptical Expert

### Novelty Assessment
- "First controlled empirical comparison of execution+mypy vs execution-only" — plausible, no counter-evidence. Claim appropriately scoped to HumanEval+/GPT-4o-mini. ✅
- Properly positioned against Self-Debug (no ablation of feedback type). ✅

### Baseline Fairness
- Condition A = Self-Debug baseline. ✅
- No SOTA comparison claimed — scope is marginal contribution of mypy, not beating SOTA. ✅
- MBPP+ restricted correctly (L1 limitation). ✅

### Required Limitations Check
| Required Limitation | Present in Paper | Location |
|--------------------|-----------------|----------|
| MBPP+ pass@1 not completed | ✅ | Section 6, L1 |
| Type-specificity mechanism unverified via ablation | ✅ | Section 6, L2 |
| Single model (GPT-4o-mini) | ✅ | Section 6, L3 |
| Z3 feedback at high base pass@1 | ✅ | Section 6, L4 |

### Forbidden Claims Check
| Forbidden Claim | Absent from Paper |
|-----------------|------------------|
| "mypy provides type-specific correction signal" | ✅ Absent (refuted explicitly) |
| "execution+mypy outperforms execution-only on MBPP+" | ✅ Absent (restricted to HumanEval+) |
| "Z3 counterexample feedback improves repair" | ✅ Absent (−0.9pp reported) |
| "improvement narrows next-attempt distribution toward type-correct solutions" | ✅ Absent (replaced with general enrichment framing) |

### Issues Found

**MAJOR-1: Mechanism language too confident (Abstract, Introduction, Discussion)**
- "suggesting mypy functions as a general diagnostic context enricher" (Abstract)
- "The most parsimonious explanation is *general diagnostic context enrichment*" (Introduction)
- "The most parsimonious interpretation is *general diagnostic context enrichment*" (Discussion)
- Ground truth C6: `verified: false, confidence: MEDIUM` — ablation not executed.
- Fix required: hedge to "consistent with" / "most parsimonious interpretation — not yet confirmed via ablation."

**MAJOR-2: No variance/significance for primary +8.94pp claim**
- Three seeds is modest evidence. No seed std, CI, or significance test reported.
- Delta range spans 6.7pp to 11.0pp (4.3pp spread) — reviewer will notice.
- Fix required: report seed std for A and B, and delta range.

**MINOR-1:** Table 1 uses "~78%" and "~79%" for non-type-error Condition A/B. Exact values in h-m2 source: 83.8% / 84.4%.

**MINOR-2:** Related work thin (see Bored Reviewer).

**MINOR-3:** "general diagnostic context enricher" needs inline definition on first use.

---

## R1 Issue Summary

| ID | Severity | Location | Issue |
|----|----------|----------|-------|
| R1-F1 | FATAL (section file) | sections/05_results.md line 54 | p < 0.01 stated for Spearman with n=5; actual p=0.182 |
| R1-M1 | MAJOR | Abstract, Introduction, Discussion | Mechanism claim "mypy functions as" too confident without ablation |
| R1-M2 | MAJOR | Results §RQ4, Abstract | No seed variance for primary +8.94pp claim |
| R1-m1 | MINOR | Table 1 | Non-type-error values approximate (~78%/~79%) vs exact 83.8%/84.4% |
| R1-m2 | MINOR | Section 2 | Related work coverage thin for main-track ICML |
| R1-m3 | MINOR | Abstract, Discussion | "general diagnostic context enricher" lacks inline definition |

**FATAL count:** 1 (section file only; not in 06_paper.md)
**MAJOR count:** 2
**MINOR count:** 3
**Proceed to Revision R1:** YES
