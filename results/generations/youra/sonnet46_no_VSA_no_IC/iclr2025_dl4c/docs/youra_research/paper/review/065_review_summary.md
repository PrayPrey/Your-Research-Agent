# Adversarial Review Summary

**Paper:** "When the Signal is Real but the Training is Not: Variance-Guided RLEF Data Selection and the Cold-Start Problem"
**Review Completed:** 2026-08-21
**Rounds Completed:** 2 (R1, R2)
**Final Status:** CONVERGED
**Persuasiveness Check:** PASSED

---

## Executive Summary

This paper underwent 2 rounds of adversarial review with three-persona analysis (Accuracy Checker, Bored Reviewer, Skeptical Expert) in R1, and focused numerical/credibility verification in R2.

| Severity | Found | Resolved | Remaining |
|----------|-------|----------|-----------|
| FATAL | 0 | 0 | 0 |
| MAJOR | 6 | 6 | 0 |

**MINOR Issues:** 5 collected in `065_human_review_notes.md` (NOT auto-fixed)

All numerical claims verified against ground truth. No fundamental factual errors found. Paper converged after 2 rounds.

---

## Persuasiveness Assessment

| Check | R1 | R2 | Notes |
|-------|----|----|-------|
| Abstract compelling? | PASS | PASS | Strong puzzle hook maintained |
| Problem clear by paragraph 2? | PASS | PASS | Gradient starvation framed clearly |
| Novelty clear by page 1? | FAIL | PASS | Fixed by "Why this negative result..." paragraph |
| Would continue reading? | marginal | PASS | Improved by honest negative-result framing |
| Attention lost at? | Section 4 | Section 5.3 | Improved |

---

## Round-by-Round Summary

### Round 1: Three-Persona Review

**Accuracy Checker Findings (2 MAJOR, 2 MINOR):**
| Issue | Severity | Resolution |
|-------|----------|------------|
| "~13 unique rollouts" unverified | MAJOR | Removed from paper |
| Root cause framed as confirmed (single hypothesis) | MAJOR | 4 ranked candidates added in Section 6.2 |
| "40,000+" undercounting | MINOR→factual | Corrected to "50,000+" |
| k=4 vs k=8 resolution implications | MINOR | Collected in human_review_notes |

**Bored Reviewer Findings (1 MAJOR, 1 MINOR):**
| Issue | Severity | Resolution |
|-------|----------|------------|
| Paper framing too weak for ICML full paper | MAJOR | "Why this negative result is worth reporting" paragraph added |
| Section 3 design-vs-execution confusion | MINOR | Collected in human_review_notes |

**Skeptical Expert Findings (3 MAJOR, 2 MINOR):**
| Issue | Severity | Resolution |
|-------|----------|------------|
| "First empirical characterization" overclaim | MAJOR | "To our knowledge" hedging added throughout |
| Resolution protocol unexecuted | MAJOR | Explicitly acknowledged as proposed future work |
| Single-seed training experiments | MAJOR→downgraded | Paper justifies: negative result doesn't require multi-seed |
| Cold-start framed as novel precondition | MINOR | Collected in human_review_notes |
| Training-stage validation absent | MINOR | Explicitly acknowledged in limitations |

### Round 2: Numerical Verification

**Accuracy Checker (1 MAJOR, 2 MINOR):**
| Issue | Severity | Resolution |
|-------|----------|------------|
| 69.25% vs 91.7% unit mismatch in Section 5.1 | MAJOR | Section 5.1 sentence revised with parenthetical and "suggesting" |
| mean_p_top50 ground truth inconsistency | MINOR | Ground truth spec issue; paper not affected |
| "To our knowledge" without comparison citations | MINOR | Collected in human_review_notes |

---

## Key Issues Addressed

1. **Root cause analysis (MAJOR-2/AC-3):** Section 6.2 restructured with four ranked candidate root causes, each with explicit evidence-for/against. Prevents reviewers from attacking "you only considered one explanation."

2. **Negative result framing (MAJOR-5/BR-1):** New "Why this negative result is worth reporting" paragraph establishes the contribution as "precisely characterized failure mode" that prevents 50,000 wasted computation attempts.

3. **Novelty hedging (MAJOR-3/OC-1):** "To our knowledge" added to all "first characterization" claims. Reduces exposure to reviewer counter-examples.

4. **Unit mismatch fix (R2-MAJOR-1):** Section 5.1 comparison of 91.7% (per-problem) to 69.25% (per-training-group) now correctly identifies the different units and softens "confirming" to "suggesting."

---

## Sections Modified

| Section | Modifications |
|---------|---------------|
| Abstract | Added negative-result framing; "50,000+"; "to our knowledge"; "proposed but not empirically validated" |
| Introduction | Added "Why this negative result is worth reporting" paragraph; "50,000+" |
| Related Work | Added "to our knowledge" hedging in §2.2, §2.4 |
| Results §5.1 | Fixed 69.25% vs 91.7% unit-mismatch framing |
| Results §5.3 | Removed unverified "~13 unique rollouts" claim |
| Discussion §6.2 | Restructured with 4 ranked root cause candidates |
| Discussion §6.3 | Added Limitation 5 (root cause inferred, not confirmed) |
| Conclusion | Added "to our knowledge" hedging; "50,000+" |

---

## Quality Improvements

- **Logical Consistency:** Improved (root cause enumeration, unit clarification)
- **Numerical Accuracy:** Corrected (50,000 vs 40,000 generation attempts)
- **Novelty Claims:** Refined ("to our knowledge" throughout)
- **Persuasiveness:** Improved (negative result framing, attention held through Section 5.3)
- **Reviewer Attack Surface:** Reduced (4 root causes, explicit limitations, hedged firsts)

---

## Reviewer Preparation Notes

Remaining attack surfaces for real reviewers:

1. **"Workshop not full paper" concern** — The paper proposes but does not execute the fix. Response: the negative result with precise diagnosis is itself the contribution; executing the fix is the next paper.

2. **Single model/dataset** — DeepSeek-Coder-7B on MBPP only. Response: the cold-start finding is deterministic (σ=0 identity), not stochastic, so generalization follows from the math.

3. **Prior work on curriculum learning** — The selection method is not novel in isolation. Response: the offline+binary-reward+code-generation combination and the cold-start precondition diagnosis are the novel elements.

Prepared responses to these are supported by the paper's current Discussion and Limitations sections.
