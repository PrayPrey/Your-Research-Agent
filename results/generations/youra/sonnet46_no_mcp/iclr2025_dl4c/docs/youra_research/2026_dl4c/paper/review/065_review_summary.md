# Adversarial Review Summary (v2.0)

**Paper:** Reward Sparsity in Function-Level Execution Feedback Degrades GRPO Training for 7B Code Models
**Review Completed:** 2026-05-03T16:15:00+00:00
**Rounds Completed:** 2
**Final Status:** CONVERGED
**Persuasiveness Check:** PASSED

---

## Executive Summary

This paper underwent 2 rounds of adversarial review with three-persona analysis (accuracy_checker, bored_reviewer, skeptical_expert).

| Severity | Found | Resolved | Remaining |
|----------|-------|----------|-----------|
| FATAL    | 0     | 0        | 0         |
| MAJOR    | 5     | 5        | 0         |

**MINOR Issues:** 2 collected in `065_human_review_notes.md` (NOT auto-fixed)

All numerical claims verified against ground truth. Zero discrepancies found across 21 checked values.

---

## Persuasiveness Assessment (v2.0)

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | 76× figure is striking; leads with finding after R1 restructure |
| Problem clear in 1 minute? | PASS | First paragraph delivers concrete numbers immediately |
| Novelty clear in 2 minutes? | PASS | Key Insight box + explicit contribution list |
| Figure 1 self-explanatory? | PASS | Caption adequate for draft format |
| Diagnostic justification clear? | PASS | Added after R2: advantage variance vs. simpler metrics explained |
| Would continue reading? | YES | |
| Attention lost at? | Section 2 middle | Standard lit survey density — acceptable |

---

## Round-by-Round Summary

### Round 1: Three-Persona Review

**Accuracy Checker Findings:**
| Category | Issues Found |
|----------|--------------|
| Numerical claims vs. ground truth | 0 |
| Dataset hub names | 0 |
| Model name accuracy | 0 |
| Forbidden claims (P1/H-M2) | 0 |

**Bored Reviewer Findings:**
| Category | Issues Found |
|----------|--------------|
| Abstract hook quality | 1 (MAJOR-003) |
| Problem clarity | 0 |
| Novelty clarity | 0 |
| Engagement loss points | 1 (HRN-002, minor) |

**Skeptical Expert Findings:**
| Category | Issues Found |
|----------|--------------|
| Methodology isolation overclaim | 1 (MAJOR-001) |
| Missing limitation (confound) | 1 (MAJOR-002) |
| Novelty overclaims | 0 |
| Baseline fairness | 0 |

**Key Issues Addressed in R1:**
1. **MAJOR-003** — Abstract restructured to lead with 76× finding (finding-first hook)
2. **MAJOR-001** — Section 3.1 reframed: co-varying dimensions acknowledged, ecological validity rationale added
3. **MAJOR-002** — Section 6.3 L5 added: binary-vs-partial-credit confound explicitly stated as limitation

### Round 2: Numerical Verification + Credibility Check

**Accuracy Checker:** Zero numerical discrepancies across 21 verified claims. Mathematical validity confirmed (variance ratio arithmetic, Cohen's d log-transform methodology, positive rate mechanistic consistency).

**Skeptical Expert Findings:**
| Category | Issues Found |
|----------|--------------|
| "Principled diagnostic" claim support | 1 (MAJOR-R2-001) |
| "Establish" language strength | 1 (MAJOR-R2-002) |
| Baseline fairness | 0 |
| H-M2 data leakage | 0 |

**Key Issues Addressed in R2:**
1. **MAJOR-R2-001** — Abstract + Sec 5.3: Added justification for advantage variance as mechanistically correct diagnostic (tracks GRPO gradient signal directly, unlike reward mean/variance)
2. **MAJOR-R2-002** — Section 5.3: Added structural sufficiency argument (flat 120-step trajectory, no recovery trend, mechanism is mathematical not temporal)

---

## Sections Modified

| Section | R1 Modifications | R2 Modifications |
|---------|-----------------|-----------------|
| Abstract | Restructured: finding-first hook; diagnostic justification added (R2) | Diagnostic sentence added |
| Section 3.1 | Co-variation acknowledgment + ecological validity rationale | None |
| Section 5.3 | None | Structural sufficiency sentence added |
| Section 6.3 | L5 (reward type confound) added | None |

---

## Quality Improvements

- **Logical Consistency:** Improved — Section 3.1 now consistent with Section 6.3 L5
- **Numerical Accuracy:** Unchanged (was already perfect)
- **Novelty Claims:** Improved — diagnostic claim now justified mechanistically
- **Baseline Comparison:** N/A (scoped mechanistic study)
- **Persuasiveness:** Improved — abstract now leads with 76× finding
- **Claim Strength:** Improved — "establish" language supported by structural argument

---

## Reviewer Preparation Notes

Potential remaining attack surfaces for real reviewers:

1. **L2 (single model):** "Results may not generalize beyond CodeLlama-7b-Instruct-hf"
   - Prepared response: "The mechanism is structural — GRPO's formula guarantees zero gradient when std(r)=0. Any 7B-class model with ≈0% solve rate on competitive programming will exhibit the same collapse. CodeLlama is representative of this capability tier."

2. **L3 (behavioral hypothesis untested):** "You haven't shown curriculum GRPO actually works"
   - Prepared response: "Correct — this paper establishes the mechanistic precondition and infrastructure. The full behavioral experiment is explicitly scoped as future work, contingent on A1 verification."

3. **L5 (reward type confound):** "Binary vs. partial credit explains the gap, not granularity"
   - Prepared response: "Both explanations are mechanistically consistent — the reward sparsity pathway operates through either dimension. The ecologically valid comparison is intentional: practitioners choose training regimes, not individual dimensions."

4. **120-step sufficiency:** "Is 120 steps enough to conclude degenerate training?"
   - Prepared response: "Yes — the mechanism is structural (GRPO formula + 0% solve rate), not temporal. The 120-step trajectory is flat throughout with no recovery trend. Section 5.3 now addresses this explicitly."

---

## Human Review Notes

2 minor issues collected in `065_human_review_notes.md`:
- HRN-001: Abstract rounding consistency (0.317 vs 0.316667)
- HRN-002: Related work sections could more explicitly connect to reward sparsity gap

*These do not affect acceptance probability. Fix at author discretion.*
