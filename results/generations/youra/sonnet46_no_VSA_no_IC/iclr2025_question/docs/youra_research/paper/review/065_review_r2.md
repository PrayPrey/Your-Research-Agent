# Adversarial Review - Round 2

**Paper:** Hallucination Type Determines Optimal Token Log-Probability Aggregation: A Mechanism-Grounded Ablation
**Reviewed:** 2026-08-21T15:30:00+00:00
**Reviewer:** Adversary Agent v2 (R2 — Numerical Verification + Credibility)
**Round:** R2 — Verification and Credibility
**Input:** 06_paper_r1.md

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Accuracy (Numerical) | 0 | 0 | OK |
| Credibility | 0 | 1 | NEEDS_WORK |
| **TOTAL** | **0** | **1** | NEEDS_WORK |

**Recommendation:** CONDITIONAL_ACCEPT (one remaining MAJOR is verification-deferred)

---

## Part 1: Numerical Verification (Accuracy Checker + Serena MCP)

### Ground Truth Verification Table

Verified against `h-m3/experiment_results.json` (actual computed values):

| Claim | Paper (R1) | Actual JSON | Match? |
|-------|-----------|-------------|--------|
| LLaMA TriviaQA AUROC(min) | 0.849 | 0.8493 | ✓ |
| LLaMA TriviaQA AUROC(mean) | 0.730 | 0.7299 | ✓ |
| LLaMA TriviaQA AUROC(raw_sum) | 0.896 | 0.8964 | ✓ |
| LLaMA TruthfulQA AUROC(min) | 0.601 | 0.6010 | ✓ |
| LLaMA TruthfulQA AUROC(mean) | 0.721 | 0.7207 | ✓ |
| LLaMA TruthfulQA AUROC(raw_sum) | 0.459 | 0.4589 | ✓ |
| Mistral TriviaQA AUROC(min) | 0.892 | 0.8924 | ✓ |
| Mistral TriviaQA AUROC(mean) | 0.836 | 0.8362 | ✓ |
| Mistral TriviaQA AUROC(raw_sum) | 0.895 | 0.8946 | ✓ |
| Mistral TruthfulQA AUROC(min) | 0.538 | 0.5382 | ✓ |
| Mistral TruthfulQA AUROC(mean) | 0.649 | 0.6492 | ✓ |
| Mistral TruthfulQA AUROC(raw_sum) | 0.417 | 0.4173 | ✓ |
| LLaMA P1 ΔAUROC | 0.119 | 0.1194 | ✓ |
| LLaMA P1 CI | [+0.083, +0.153] | [+0.083, +0.153] | ✓ |
| Mistral P1 ΔAUROC | 0.056 | 0.0562 | ✓ |
| Mistral P1 CI | [+0.032, +0.082] | [+0.032, +0.082] | ✓ |
| LLaMA P2 ΔAUROC | 0.120 | 0.1198 | ✓ |
| LLaMA P2 CI | [+0.084, +0.157] | [+0.084, +0.157] | ✓ |
| Mistral P2 ΔAUROC | 0.111 | 0.1109 | ✓ |
| Mistral P2 CI | [+0.071, +0.147] | [+0.071, +0.147] | ✓ |
| Peakedness hallucinated | 2.936 | 2.9355 | ✓ |
| Peakedness correct | 2.533 | 2.5329 | ✓ |
| p-value | 0.002 | 0.00206 | ✓ |
| n (h-m1) | 488 | 488 | ✓ |

**All numerical claims in R1 paper verified against actual Phase 4 result files. ZERO remaining discrepancies.**

---

### Mathematical Validity Checks

#### Check 1: P2 Direction Consistent with Absolute AUROC Values?

**Paper claims:** mean > min on TruthfulQA by 0.120 (LLaMA), 0.111 (Mistral).
**Actual:** LLaMA: 0.721 − 0.601 = 0.120 ✓; Mistral: 0.649 − 0.538 = 0.111 ✓.
**Verdict:** Internally consistent.

#### Check 2: P1 Direction Consistent with Absolute AUROC Values?

**Paper claims:** min > mean on TriviaQA by 0.119 (LLaMA), 0.056 (Mistral).
**Actual:** LLaMA: 0.849 − 0.730 = 0.119 ✓; Mistral: 0.892 − 0.836 = 0.056 ✓.
**Verdict:** Internally consistent.

#### Check 3: raw_sum comparison to SE is directionally valid?

**Paper claims:** raw_sum (0.895–0.896) > SE (≈0.79).
**Actual raw_sum:** 0.8946–0.8964 > 0.79. ✓
**Cross-pipeline caveat:** Now properly stated in both Abstract and Introduction.
**Verdict:** Claim valid with appropriate caveats now in place.

#### Check 4: Dataset n consistency

**h-m3 actual:** LLaMA TriviaQA n=488, Mistral TriviaQA n=476.
**Paper (R1):** "~476–488" and explicit note. ✓
**Verdict:** Fixed correctly in R1.

---

### FATAL Issues — Numerical

None.

### MAJOR Issues — Numerical

None. All numerical values verified against actual Phase 4 JSON results.

---

## Part 2: Credibility Check (Skeptical Expert)

### Baseline Fairness Re-Audit

| Baseline | Our Protocol | Literature | Gap | Caveat? |
|----------|-------------|------------|-----|---------|
| SE AUROC ≈0.79 | Single-pipeline | Multi-pipeline | ~0.10 | ✓ (now in Abstract + Intro + §6.3) |
| CCP 0.72–0.80 | Literature cited | Literature range | — | ✓ |
| SelfCheckGPT 0.72–0.78 | Literature cited | Literature range | — | ✓ |

**Assessment:** Cross-pipeline caveat now appropriately placed. Baseline fairness: PASS.

### Unverified Citations — Status

Citations flagged in R1 as unverified: Ma2025Semantic, Moslonka2025Learned, Zhang2025Robust.

R1 partial fix: identified as arXiv preprints.

**R2 assessment:** The usage of these three citations in Related Work does NOT affect any core quantitative claims. They are used to position supervised/probe-based methods as a category. Even if all three are missing or incorrect, the paper's mechanism claims (P1, P2, peakedness) are unaffected. The risk is primarily reputational (appears uninformed if arXiv IDs are wrong).

**Remaining MAJOR:**

#### MAJOR-CRED-001 (Carried from R1): Three Unverified Citations

**Status:** Partially addressed — labeled as arXiv preprints, full verification not performed.
**Impact:** Submission risk — not a paper quality issue but a due-diligence issue.
**Required action:** Verify before submission. Cannot be auto-fixed in-pipeline without live Semantic Scholar MCP search for these specific arXiv IDs.
**Mitigation already in paper:** The citations are used in a non-central position (establishing a related work category). If any prove problematic, they can be removed without affecting the paper's contributions.

---

### Persuasiveness Re-Check (after R1 fixes)

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | ✓ | Now has SE cross-pipeline caveat without weakening the finding |
| Problem clear in 1 min? | ✓ | Unchanged — still strong |
| Novelty clear in 2 min? | ✓ | Unchanged |
| raw_sum finding clearly framed? | ✓ | R1 added wider gap note in §5.4 |
| Limitations complete? | ✓ | TruthfulQA label protocol limitation added |

**Persuasiveness: PASSED.**

---

## Summary for Revision Agent (R2)

### Issues to Address

1. **MAJOR-CRED-001 (carried):** Cannot fully auto-fix. Add explicit note in paper that Ma2025, Moslonka2025, Zhang2025 are arXiv preprints requiring pre-submission verification. This is already partially done — confirm the note is visible in Related Work or References.

### What Changed for the Better in R1

- All TruthfulQA AUROC values now correct
- Dataset n properly documented
- SE cross-pipeline caveat appropriately placed
- TruthfulQA label limitation acknowledged

### No New FATAL or MAJOR Issues Found in R2

All numerical claims verified against actual Phase 4 JSON. Mathematical consistency confirmed. Baseline fairness confirmed. Persuasiveness maintained.

---

## R2 Return Summary

```yaml
agent: "adversary-v2"
round: "R2"
status: "COMPLETED"
output_file: "docs/youra_research/paper/review/065_review_r2.md"

numerical_verifications_performed: 23
numerical_discrepancies_found: 0
mathematical_impossibilities: 0
baseline_fairness_issues: 0

summary:
  accuracy:
    fatal: 0
    major: 0
    ground_truth_discrepancies: 0

  credibility:
    fatal: 0
    major: 1  # Carried: unverified citations (verification-deferred)

  totals:
    fatal: 0
    major: 1

  persuasiveness_passed: true
  human_review_notes_count: 0

  recommendation: "CONDITIONAL_ACCEPT"
  note: "Remaining MAJOR is a pre-submission due-diligence item, not a paper quality issue"
```
