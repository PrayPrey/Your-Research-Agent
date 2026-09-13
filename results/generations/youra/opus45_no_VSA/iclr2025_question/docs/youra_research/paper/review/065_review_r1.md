# Adversarial Review - Round 1

**Paper:** Cross-Layer Trajectory Instability for Single-Pass Hallucination Detection in Large Language Models
**Reviewed:** 2026-08-09T14:15:00Z
**Reviewer:** Adversary Agent v2

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Accuracy | 0 | 0 | OK |
| Engagement | 0 | 0 | OK |
| Credibility | 0 | 1 | NEEDS_WORK |
| **TOTAL** | **0** | **1** | MINOR_REVISION |

**Recommendation:** MINOR_REVISION

---

## Part 1: Accuracy Check (Persona 1)

### Ground Truth Summary

| Metric | Paper Claims | Ground Truth | Match? |
|--------|--------------|--------------|--------|
| NTI AUROC | 0.5657 | 0.5657 | ✓ |
| Combined gain | +7.1% (+0.0712) | 0.0712 | ✓ |
| LRT p-value | 1.15e-05 | 1.15e-05 | ✓ |
| Low-entropy AUROC | 0.5136 | 0.5136 | ✓ |
| Low-entropy CI | [0.4639, 0.5628] | [0.4639, 0.5628] | ✓ |
| RCI flip halluc | 95.1% | 95.1% (0.951) | ✓ |
| RCI flip correct | 90.9% | 90.9% (0.909) | ✓ |
| RCI separation | 4.2% | 4.2% (0.042) | ✓ |
| Min fold AUROC | 0.5356 | 0.5356 (fold_1) | ✓ |
| Layers analyzed | 24-31 | 24-31 | ✓ |
| Dataset size | 817 questions | 817 | ✓ |
| Prompt-choice pairs | 4114 | 4114 | ✓ |
| CV folds | 5-fold | 5 | ✓ |

**All numerical claims verified against ground truth. No discrepancies found.**

### FATAL Issues - Accuracy

None.

### MAJOR Issues - Accuracy

None.

### Minor Observations

- Abstract says "layers 24-32" but methodology says "layers 24-31 (8 late layers)". The 8-layer count (24,25,26,27,28,29,30,31) is consistent with 24-31, not 24-32. This is **cosmetic** — the equations and results use 24-31 correctly.

---

## Part 2: Engagement Check (Persona 2)

### Bored Reviewer Verdict

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | ✓ | Clear problem, concrete numbers, honest negative results |
| Problem clear in 1 min? | ✓ | Hallucination + computational overhead framed in first paragraph |
| Novelty clear in 2 min? | ✓ | "Trajectory of representations" distinct from prior work |
| Figure 1 self-explanatory? | N/A | No figures in this paper version |
| Would continue reading? | ✓ | Yes — honest framing with validated + refuted claims is engaging |

**Attention Lost At:** N/A — maintained throughout

### FATAL Issues - Engagement

None.

### MAJOR Issues - Engagement

None.

### Strengths

- **Honest framing**: Abstract directly states what worked AND what failed
- **Concrete results**: Numbers in abstract, not vague claims
- **Clear structure**: Sub-hypotheses table makes validation status transparent

---

## Part 3: Credibility Check (Persona 3)

### Novelty Claims Audit

| Claim | Location | Verified? | Prior Work |
|-------|----------|-----------|------------|
| "Single-pass trajectory metrics" | §1 | ✓ | END (Wu 2025) explores cross-layer entropy; CLTI formalizes into NTI/CMI |
| "Trajectory instability correlates with hallucination" | §1 | ✓ | Novel operationalization of prior intuition |

No false "first to" claims found.

### Baseline Fairness Audit

| Baseline | Our Number | Literature | Fair? |
|----------|------------|------------|-------|
| Entropy only | AUROC 0.50 | N/A (reference) | ✓ |
| END (Wu 2025) | Cited | 6 citations (nascent) | ✓ |

Note: Paper compares against entropy baseline within same framework, not external methods. This is appropriate for a first validation study.

### FATAL Issues - Credibility

None.

### MAJOR Issues - Credibility

#### MAJOR-CRED-001: Null Model AUROC Annotation Ambiguity

**Location:** Section 4.2, Results Table
**Issue:** Table shows "Null AUROC (H_L only)† = 0.5000" with dagger footnote explaining logistic regression collapses to intercept-only. This is technically correct but potentially confusing — readers may misinterpret 0.50 as "entropy baseline AUROC" when it's actually "degenerate model returning constant prediction."
**Evidence:** Footnote explains: "Logistic regression with H_L alone collapses to intercept-only; the gain reflects trajectory features' incremental validity over entropy within the same classifier framework."
**Impact:** Expert reviewers may question whether entropy alone has *zero* discriminative power (AUROC exactly 0.50). The explanation is present but buried.
**Suggested Fix:** Rephrase table header to "Intercept-only baseline" or add clarifying sentence in main text: "When H_L is the sole feature, logistic regression coefficients fail to converge, yielding intercept-only predictions (AUROC = 0.50 by construction)."

---

## Part 4: Human Review Notes

| Location | Note | Type |
|----------|------|------|
| Abstract | "layers 24-32" should be "layers 24-31" for consistency | typo |
| §3.1 | Equations use l=24 to 31, matching 8 layers | verify consistency |

---

## Summary for Revision Agent

### Priority Fix List

1. **MAJOR-CRED-001:** Clarify null model AUROC annotation — add text explaining intercept-only collapse - SHOULD FIX

### Key Concerns

- Minor: "24-32" vs "24-31" notation inconsistency in abstract

### What's Working

- All numerical claims match ground truth exactly
- Honest reporting of refuted hypotheses (h-m2, h-m3)
- Clear methodology-results alignment
- Appropriate scope for single-model validation study
- Statistical significance properly reported (p < 0.001)

---

## Persuasiveness Checks

| Check | Result |
|-------|--------|
| abstract_compelling | true |
| problem_clear_in_1_minute | true |
| novelty_clear_in_2_minutes | true |
| figure_1_self_explanatory | N/A |
| would_continue_reading | true |
| attention_lost_at | null |
| false_novelty_claims_found | 0 |
| unfair_baseline_comparisons | 0 |
| overclaims_found | 0 |
| missing_limitations | false |

---

## Agent Return Summary

```yaml
agent: "adversary-v2"
round: "R1"
status: "COMPLETED"
output_file: "paper/review/065_review_r1.md"

summary:
  accuracy:
    fatal: 0
    major: 0
    ground_truth_discrepancies: 0

  engagement:
    fatal: 0
    major: 0
    would_continue_reading: true
    attention_lost_at: null

  credibility:
    fatal: 0
    major: 1
    false_novelty_claims: 0
    unfair_baselines: 0

  totals:
    fatal: 0
    major: 1

  human_review_notes_count: 2

  recommendation: "MINOR_REVISION"

  key_concerns:
    - "Null model AUROC annotation may confuse reviewers"
```
