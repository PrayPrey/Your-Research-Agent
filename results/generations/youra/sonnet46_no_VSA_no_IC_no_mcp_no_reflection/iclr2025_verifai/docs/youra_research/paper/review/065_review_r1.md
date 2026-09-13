# Adversarial Review — Round 1
**Paper:** More Feedback, Worse Repair: An Overhead-Normalized Comparison of Formal Feedback for LLM Code Repair  
**Round:** R1 — Accuracy and Engagement  
**Personas:** Accuracy Checker, Bored Reviewer, Skeptical Expert  
**Date:** 2026-08-31  

---

## Ground Truth Summary

| Metric | Ground Truth Value | Source |
|---|---|---|
| Spearman ρ | -1.0000 | h-m3/04_validation.md |
| Static efficiency ratio | 6.637 | h-m4/04_validation.md (MOCK) |
| Execution efficiency ratio | 0.409 | h-m4/04_validation.md (MOCK) |
| Improvement factor | 16.2× | computed: 6.637/0.409 |
| Speed factor (static/exec) | 17.4× | computed: 0.801/0.046 |
| Pyright mean chars | 24,358.7 | h-m2/04_validation.md |
| Execution mean chars | 201.8 | h-m2/04_validation.md |
| KW H-stat | 338.78 | h-m2/04_validation.md |
| KW p-value | 4.01e-73 | h-m2/04_validation.md |
| ε² | 0.880 | h-m2/04_validation.md |
| Z3 coverage | 6.3% (8/126) | h-m2, h-e1 |
| Logic errors | 65.9% (83/126) | h-m1/04_validation.md |
| Total problems | 421 | h-m1/04_validation.md |
| Failing solutions | 126 | h-m1/04_validation.md |
| h-m4 status | MOCK MODE | 065_ground_truth.yaml |

---

## Executive Summary

| Severity | Count | Requires |
|---|---|---|
| FATAL | 0 | — |
| MAJOR | 1 | Must fix before submission |
| MINOR | 4 | Collected in human_review_notes |

**Recommendation:** PROCEED TO R2 (one MAJOR issue must be fixed; persuasiveness passes)

---

## MAJOR Issues

### CRED-MAJOR-001: Abstract efficiency claims unqualified as mock-derived

**Location:** Abstract, paragraph 3  
**Text:** "static analysis runs seventeen times faster and returns sixteen times more correctness per second"  

**Issue:** The abstract states specific quantitative claims ("seventeen times faster", "sixteen times more correctness per second", implicitly referencing 6.64 vs 0.41 efficiency ratios) with no qualification that these numbers come from calibrated mock overhead data, not a live API run. The body properly discloses this in Sections 4.4 (note on overhead measurements), 5.5 (overhead table caveat), and 6.2 (limitations). A reader who reads only the abstract — which is how most papers are initially evaluated — sees hard quantitative efficiency claims with no indication they are estimates.

**Evidence from ground truth:** `h-m4` status = MOCK MODE. `065_ground_truth.yaml` caveat: "MOCK MODE — no live API key; synthetic log-normal overhead calibrated to h-m2 empirical priors. Ordering robust, absolute magnitudes are estimates."

**Required fix:** Add a parenthetical or brief qualifier in the abstract indicating that overhead figures are from a calibrated simulation. Example:

> "static analysis runs seventeen times faster and returns sixteen times more correctness per second (overhead from calibrated mock run; ordering robust, magnitudes are estimates pending live replication)"

or more concisely:

> "static analysis runs an estimated seventeen times faster and returns an estimated sixteen times more correctness per second [mock overhead; see §4.4]"

**Why MAJOR, not FATAL:** The ordering is structurally robust per ground truth. The paper self-discloses fully in the body. The issue is selective non-disclosure in the highest-visibility location (abstract), not a false claim.

---

## MINOR Issues (→ human_review_notes)

### MIN-001: Section 7.1 summary omits Z3 from ordered range

**Location:** Section 7.1, paragraph 1  
**Text:** "repair success falls monotonically as feedback volume rises, from mypy's 6.35% down to Pyright's 4.76%"  
**Issue:** Z3's 7.94% is the top of the repair-rate range and anchors the inverse ordering. "From mypy's 6.35% down to Pyright's 4.76%" describes only 3 categories, skipping the Z3 endpoint. A reader of the conclusion alone sees only a partial ordering.  
**Suggested fix:** "from Z3's 7.94% down to Pyright's 4.76%"

### MIN-002: Abstract opener length

**Location:** Abstract, sentence 1  
**Text:** "Systems that repair language-model-generated code by feeding verifier output back into the prompt must choose what goes in the verify stage, and that choice currently rests on an untested intuition: that a more formally rigorous verifier produces more precise feedback and therefore better repair."  
**Issue:** 48-word setup before the research framing begins. Tightening optional — "The verify stage in LLM repair loops rests on an untested assumption: more formally rigorous feedback produces better repair." The current version is not wrong.

### MIN-003: Two inversions in abstract may momentarily confuse

**Location:** Abstract, paragraph 3  
**Text:** "The intuition inverts. Repair success falls monotonically as feedback grows longer... Cost inverts the ranking again"  
**Issue:** The word "invert" appears in two different senses (repair↓ as feedback↑, then efficiency↑ despite repair↓) within the same paragraph. A first read may require a second pass. Could label them explicitly ("first inversion", "second inversion") or restructure. Style issue only — content is clear.

### MIN-004: Conclusion restates ρ = -1.0 without n=4 caveat

**Location:** Section 7.3  
**Text:** "a Spearman correlation of -1.0 later, that expectation is not weakly supported but exactly inverted"  
**Issue:** Section 5.4 carefully notes "ρ computed over four points is a coarse statistic; it can only take a handful of values, and -1.0 means 'perfectly ordered,' not 'strongly correlated'." The Conclusion does not repeat this nuance, ending on the strongest possible rhetorical note. For a non-technical reader or a skeptical reviewer who reads Conclusion first, this could set an inflated expectation. Suggested: add brief hedge ("the ordering was perfectly monotone (ρ = -1.0, n = 4 categories)") in Section 7.1 or 7.3.

---

## Ground Truth Verification Log

All 25 numerical claims checked against `065_ground_truth.yaml`:
- ✓ 25/25 numerical claims match ground truth exactly
- ✓ All 8 required limitations present in paper body (L1–L8)
- ✓ Dataset numbers (421, 126, 164, 257) consistent
- ✓ Bug distribution fractions consistent
- ✓ Bootstrap CIs match h-m3 validation report
- ✓ Efficiency ratio arithmetic correct (0.801/0.046 = 17.4×; 6.637/0.409 = 16.2×)
- ⚠ Efficiency ratios are MOCK MODE — not flagged in abstract (CRED-MAJOR-001)
- ⚠ 14 citations self-declared [UNVERIFIED] — needs manual check before submission

---

## Persuasiveness Assessment

| Check | Result | Notes |
|---|---|---|
| Abstract compelling? | PASS | Strong hook, concrete quantitative punch line |
| Problem clear in 1 minute? | PASS | Paragraph 1 states problem and finding simultaneously |
| Novelty clear in 2 minutes? | PASS | Gap named explicitly in paragraph 5 of Introduction |
| Figure 1 self-explanatory? | PASS | Caption is self-contained |
| Would continue reading? | YES | — |
| Attention lost at? | Never | Related Work concise; Results well-structured |
| Hook avoids "X is important"? | PASS | "We set out to measure a precision hierarchy" — problem-first |
| False novelty claims? | 0 | "First controlled overhead-normalized comparison" defensible |
| Unfair baseline comparisons? | 0 | Within-subjects paired design, no external baseline comparison |
| Overclaims? | 1 | Abstract efficiency numbers unqualified as mock (CRED-MAJOR-001) |
| Tone overclaiming? | No | Mechanism framed as "Our reading" / "Our account" throughout |
| Missing limitations? | No | All 8 required limitations present in body |

**Persuasiveness: PASSED** (all checks pass; one MAJOR overclaim in abstract fixable)

---

## Summary for Revision Agent

**Fix this (FATAL = 0, so no fatal fixes needed):**

1. **MUST FIX — CRED-MAJOR-001:** Add mock-mode qualifier to abstract efficiency claims.
   - Target: Abstract paragraph 3
   - Change "seventeen times faster and returns sixteen times more correctness per second" to include a brief qualifier that these come from calibrated mock overhead
   - Do NOT change the numbers themselves — they are correctly computed
   - Preserve the rhetorical impact while adding epistemic honesty

**Collect for human review (do not auto-fix):**
- MIN-001: Z3 omitted in Section 7.1 ordered summary
- MIN-002: Abstract opener tightening (optional style)
- MIN-003: Two "invert" uses in abstract (style)
- MIN-004: Conclusion ρ = -1.0 without n=4 caveat

**Agent return summary:**
```yaml
agent: adversary
round: R1
status: COMPLETED
fatal_count: 0
major_count: 1
minor_count: 4
citation_risk_count: 14  # pre-existing, paper self-discloses
persuasiveness_passed: true
recommendation: PROCEED_TO_R2
```
