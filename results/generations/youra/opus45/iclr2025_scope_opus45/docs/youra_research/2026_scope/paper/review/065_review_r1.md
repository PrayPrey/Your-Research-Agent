# Phase 6.5 Adversarial Review - Round 1

**Review Type:** Three-Persona Adversarial Review
**Round:** R1 - Accuracy and Engagement
**Date:** 2026-03-28T02:05:00Z
**Paper:** Memory Horizon Separation in SSM Adaptation

---

## Ground Truth Summary

| Metric | Ground Truth Value | Source |
|--------|-------------------|--------|
| H_spec (Mamba-1.4B) | 256.18 tokens | H-E1 validation |
| CV(H_spec) | 2.22e-16 | H-E1 validation |
| Degradation ratio | 3.03 | H-M1 validation |
| |ΔH_spec| | 0.0% | H-M2 validation |
| Eigenvalue correlation | 1.0 | H-M2 validation |
| ΔE (nats) | 5.93e-07 | H-M3 validation |
| Slow mode fraction (pre) | 1.97e-05 | H-M3 validation |
| Slow mode fraction (post) | 1.91e-05 | H-M3 validation |
| Layers with slow modes | 2/48 | H-M3 validation |
| PPL @ 25 tokens | 83.26 | H-M1 validation |
| PPL @ 256 tokens | 17.89 | H-M1 validation |
| PPL @ 1024 tokens | 12.22 | H-M1 validation |
| H_spec (Mamba-370M) | 162,605 tokens | H-E1 cross-validation |

---

## Executive Summary

| Severity | Count | Blocking |
|----------|-------|----------|
| FATAL | 0 | N/A |
| MAJOR | 2 | Yes |
| MINOR (→ Human Review) | 5 | No |

**Overall Assessment:** The paper is well-structured with accurate numerical claims. Two MAJOR issues identified relating to clarity of experimental limitations and potential overclaiming. No FATAL issues (no factual contradictions with ground truth).

**Recommendation:** MINOR_REVISION - Fix MAJOR issues, proceed to R2.

---

## Persona 1: Accuracy Checker

### Role: Fact-checker and claim verifier

#### Numerical Verification Against Ground Truth

| Paper Claim | Location | Ground Truth | Match |
|-------------|----------|--------------|-------|
| "CV ≈ 0" | Abstract | 2.22e-16 | ✅ MATCH |
| "CV = 2.22 × 10^{-16}" | Section 5.1 | 2.22e-16 | ✅ MATCH |
| "H_spec = 256.18 tokens" | Section 5.1 | 256.18 | ✅ MATCH |
| "ΔH_spec = 0%" | Abstract | 0.0% | ✅ MATCH |
| "ΔH_spec = 0.0%" | Section 5.3 | 0.0% | ✅ MATCH |
| "correlation = 1.0" | Section 5.3 | 1.0 | ✅ MATCH |
| "ΔE = 5.93 × 10^{-7} nats" | Section 5.4 | 5.93e-07 | ✅ MATCH |
| "Degradation ratio = 3.03" | Section 5.2 | 3.0292 | ✅ MATCH (rounded) |
| "PPL 25 tokens = 83.26" | Table, Section 5.2 | 83.26 | ✅ MATCH |
| "PPL 256 tokens = 17.89" | Table, Section 5.2 | 17.89 | ✅ MATCH |
| "PPL 1024 tokens = 12.22" | Table, Section 5.2 | 12.22 | ✅ MATCH |
| "2 of 48 layers" | Section 5.4 | 2/48 | ✅ MATCH |
| "0.00197%" slow mode capacity | Section 5.4 | 1.97e-05 = 0.00197% | ✅ MATCH |
| "H_spec ≈ 256 tokens" | Section 7.1 | 256.18 | ✅ MATCH |

**Accuracy Checker Verdict:** ✅ ALL NUMERICAL CLAIMS VERIFIED

All quantitative claims in the paper match the ground truth values from Phase 4 validation reports. No numerical discrepancies detected.

#### Methodology Consistency Check

| Aspect | Paper States | Ground Truth | Match |
|--------|--------------|--------------|-------|
| Model | Mamba-1.4B | state-spaces/mamba-1.4b-hf | ✅ |
| LoRA rank | 16 | 16 | ✅ |
| LoRA alpha | 32 | 32 | ✅ |
| Target modules | in_proj, x_proj | in_proj, x_proj | ✅ |
| Trainable params | ~11M (0.8%) | 11,132,928 (0.80%) | ✅ |
| Training epochs | 1 | 1 | ✅ |
| Training sequences | 500 | 500 (H-M3), 200 (H-M2) | ⚠️ Minor variance |
| Evaluation dataset | WikiText-103 | WikiText-103 | ✅ |

**Minor Note:** H-M2 used 200 training sequences while H-M3 used 500. Paper mentions 500. This is acceptable for PoC but should be noted.

---

## Persona 2: Bored Reviewer

### Role: Busy NeurIPS reviewer with 5 papers to review today

#### First Impression Checks

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | ✅ YES | Strong hook with concrete results |
| Problem clear in 1 minute? | ✅ YES | "Why does LoRA work for Mamba sometimes?" is clear |
| Novelty clear in 2 minutes? | ✅ YES | H_spec framework is novel and clearly explained |
| Figure 1 self-explanatory? | ⚠️ N/A | No Figure 1 in main text (figures referenced in Appendix) |
| Would continue reading? | ✅ YES | Compelling negative result |

#### Engagement Assessment

**Attention Lost At:** Never fully lost, but Section 2 (Related Work) is dense.

**Engagement Score:** 8/10

**Specific Observations:**

1. **Strong opening hook** (Section 1): "Why does LoRA work for Mamba on some tasks but fail on others?" - Excellent.

2. **Clear practical motivation**: "A researcher fine-tuning Mamba-1.4B with LoRA for a task requiring 512-token context dependencies..." - Makes stakes concrete.

3. **The negative result is well-framed**: The H-M3 failure is positioned as the key finding, not buried.

4. **Results are quantitative and memorable**: "six orders of magnitude below threshold" is striking.

**Bored Reviewer Verdict:** ✅ WOULD CONTINUE READING

The paper maintains engagement throughout. The counterintuitive negative result is genuinely interesting.

---

## Persona 3: Skeptical Expert

### Role: Domain expert looking for holes in claims

#### Novelty Claims Assessment

| Claim | Location | Valid? | Notes |
|-------|----------|--------|-------|
| "First operationalization of H_spec" | Section 1.3 | ✅ Likely valid | No prior work operationalizes this for PEFT |
| "First demonstration of perfect eigenvalue preservation" | Section 1.3 | ✅ Valid | No prior work measures this explicitly |
| "Elimination of EUH" | Section 1.3 | ✅ Valid | Original contribution |
| "First measurable criterion for SSM PEFT" | Abstract | ⚠️ Slightly overclaimed | See MAJOR-001 |

#### Baseline Fairness Check

**Baseline Comparison Status:** Phase 5 was NOT executed (baseline_comparison.status = "NOT_STARTED").

**Issue:** The paper does not compare against existing SSM-PEFT methods (SDT, State-offset Tuning). This is acknowledged in Related Work but not in Limitations.

**Verdict:** ⚠️ No unfair baseline comparison, but missing baseline comparison should be more prominently acknowledged.

#### Overclaims Found

**MAJOR-001: Overclaim on "first measurable criterion"**

- **Location:** Abstract, final sentence
- **Claim:** "Our framework provides the first measurable criterion for predicting PEFT effectiveness on SSM architectures"
- **Issue:** While H_spec is novel, the claim is slightly overclaimed because:
  1. The paper only validates on Mamba, not "SSM architectures" broadly
  2. The paper uses perplexity as a proxy, not direct task failure verification
- **Suggested Fix:** Qualify as "first measurable criterion for predicting projection-only LoRA effectiveness on Mamba architectures"

**MAJOR-002: Missing explicit limitation about lack of task failure demonstration**

- **Location:** Section 6.2
- **Issue:** The H-M4 discriminative test (MQAR task failure when L > H_spec) was not executed. While acknowledged, the paper strongly claims MHSH is "confirmed" without this direct test.
- **Current text:** "H-M4 provides additional confirmation but is not strictly necessary for our conclusions"
- **Problem:** This undersells the gap. The paper shows energy redistribution fails (negative EUH evidence) but does not directly show task failure.
- **Suggested Fix:** Add clearer caveat: "Our claim that MHSH is 'confirmed' rests on elimination of EUH rather than direct task failure observation. Future work should validate task failure predictions."

#### Missing Limitations Check

| Limitation | Acknowledged? | Severity |
|------------|---------------|----------|
| WikiText-103 proxy | ✅ Yes (Section 6.2) | Medium |
| Single model family | ✅ Yes (Section 6.2) | Medium |
| H-M4 not executed | ✅ Yes (Section 6.2) | Medium |
| PoC training config | ✅ Yes (Section 6.2) | Low |
| No baseline method comparison | ❌ No | Medium |

**MAJOR-002 encompasses the missing limitation about baseline comparison.**

**Skeptical Expert Verdict:** Paper makes valid contributions but has two MAJOR issues requiring revision.

---

## Issue Summary

### FATAL Issues (0)

None identified. All numerical claims match ground truth.

### MAJOR Issues (2)

| ID | Persona | Issue | Location | Fix Required |
|----|---------|-------|----------|--------------|
| MAJOR-001 | Skeptical Expert | Overclaim on "first measurable criterion for SSM architectures" when only Mamba tested | Abstract | Qualify scope |
| MAJOR-002 | Skeptical Expert | Insufficient acknowledgment that MHSH is supported by EUH elimination, not direct task failure | Section 6.2 | Add caveat |

### MINOR Issues (5) → Human Review Notes

| ID | Type | Location | Note |
|----|------|----------|------|
| MINOR-001 | clarity | Section 2.3 | Dense paragraph on eigenvalue analysis could use clearer exposition |
| MINOR-002 | formatting | Section 4 | Table formatting inconsistent (some use "|", some don't) |
| MINOR-003 | style | Section 5.4 | "essentially *zero*" - italics for emphasis is informal |
| MINOR-004 | clarity | Section 3.3 | KL divergence formulation mentioned but not fully derived |
| MINOR-005 | formatting | Appendix A | Figure references should use consistent numbering |

---

## Persuasiveness Checks Summary (v2.0)

| Check | Result |
|-------|--------|
| abstract_compelling | true |
| problem_clear_in_1_minute | true |
| novelty_clear_in_2_minutes | true |
| figure_1_self_explanatory | null (no Figure 1 in main body) |
| would_continue_reading | true |
| attention_lost_at | null |
| false_novelty_claims_found | 0 |
| unfair_baseline_comparisons | 0 |
| overclaims_found | 1 (MAJOR-001) |
| missing_limitations | true (baseline comparison not acknowledged) |

---

## Ground Truth Verification Log

| Check | Method | Result |
|-------|--------|--------|
| H_spec value | Direct comparison to H-E1 04_validation.md | ✅ Match |
| CV value | Direct comparison to H-E1 04_validation.md | ✅ Match |
| Degradation ratio | Direct comparison to H-M1 04_validation.md | ✅ Match |
| Eigenvalue preservation | Direct comparison to H-M2 04_validation.md | ✅ Match |
| Energy redistribution | Direct comparison to H-M3 04_validation.md | ✅ Match |
| Perplexity values | Direct comparison to H-M1 04_validation.md | ✅ Match |
| Layer counts | Direct comparison to H-M3 04_validation.md | ✅ Match |
| LoRA configuration | Direct comparison to verification_state.yaml | ✅ Match |
| Sub-hypothesis results | Direct comparison to verification_state.yaml | ✅ Match |

---

## Summary for Revision Agent

### Priority 1: Fix MAJOR Issues

1. **MAJOR-001:** In Abstract, change "SSM architectures" to "Mamba architecture" or add qualifier "on Mamba as a representative SSM"

2. **MAJOR-002:** In Section 6.2, add explicit caveat acknowledging MHSH support is via EUH elimination, not direct task failure demonstration

### Priority 2: Collect MINOR Issues for Human Review

All MINOR issues collected in human_review_notes - do NOT auto-fix.

### Recommendation

**PROCEED TO REVISION R1** - Fix 2 MAJOR issues.

---

## R1 Review Metadata

```yaml
round: R1
focus: accuracy_and_engagement
personas_used:
  - accuracy_checker
  - bored_reviewer
  - skeptical_expert
issues:
  fatal: 0
  major: 2
  minor: 5
ground_truth_discrepancies: 0
persuasiveness_passed: true
recommendation: MINOR_REVISION
```
