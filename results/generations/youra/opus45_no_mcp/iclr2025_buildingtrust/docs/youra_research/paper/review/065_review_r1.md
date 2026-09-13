# Adversarial Review Round 1

## Accuracy Checker Findings

All numerical claims verified against ground truth:

| Claim | Paper Value | Ground Truth | Status |
|-------|-------------|--------------|--------|
| Spearman r | -0.315 | -0.315 | MATCH |
| p-value | p<1e-16 (9.22e-17 in results) | 9.22e-17 | MATCH |
| Sample size | n=664 | 664 | MATCH |
| Hedging presence rate | 82% | 82% | MATCH |
| Mean hedging markers | 2.84 | 2.84 | MATCH |
| CoT reasoning rate | 100% | 100% | MATCH |
| Mean reasoning steps | 4.49 | 4.49 | MATCH |
| Ordering compliance | 100% | 100% | MATCH |
| "may" occurrences | 787 | 787 | MATCH |
| "could" occurrences | 619 | 619 | MATCH |

**No FATAL numerical accuracy issues found.**

MINOR: Abstract says "p<1e-16" while Results section shows exact value "9.22 x 10^-17". Consistent but could standardize.

## Bored Reviewer Assessment

- abstract_compelling: true
- problem_clear_in_1_minute: true
- novelty_clear_in_2_minutes: true
- would_continue_reading: true
- attention_lost_at: "never"

The abstract hooks with "something unexpected happens" framing. Problem (calibration gap) is stated clearly. Novelty (mechanism decomposition into 4 verified steps) is distinct from prior work. Structure is clean: Intro -> Related -> Method -> Setup -> Results -> Discussion -> Conclusion.

No major engagement issues.

## Skeptical Expert Findings

### Novelty Assessment
MINOR: The mechanism decomposition is methodologically novel, but the core finding (CoT helps calibration) is not surprising. Paper appropriately frames contribution as "systematic verification" rather than discovery.

### Baseline Fairness
MAJOR: Token-padding control mentioned in Section 3 but **no results reported**. Paper claims it rules out token-count artifacts but shows no data from this condition.

### Overclaims
MAJOR: Paper title includes "Calibration" but H-E1 (ECE comparison) ran in MOCK mode per ground truth. The paper does NOT demonstrate calibration improvement with real ECE measurements. Limitation section mentions "P1 Untested" but does NOT mention H-E1 ran in mock mode.

MINOR: "Self-reading" is a mechanistic interpretation, not proven. Paper acknowledges "correlational evidence" in limitations but uses causal language ("enables", "leverage") throughout.

### Missing Limitations
- H-E1 mock mode NOT acknowledged (ground truth says paper_mentions: true, but paper only mentions "P1 Untested" not "H-E1 mock mode")
- No discussion of whether hedging markers are meaningful or learned artifacts
- No discussion of prompt sensitivity

## Issue Summary

| ID | Severity | Category | Description |
|----|----------|----------|-------------|
| 1 | MAJOR | Missing Results | Token-padding control results not reported despite being described in methodology |
| 2 | MAJOR | Overclaim | Title claims "Calibration" but ECE was never measured with real API calls (H-E1 mock mode) |
| 3 | MINOR | Incomplete Limitation | H-E1 mock mode not explicitly acknowledged in limitations |
| 4 | MINOR | Consistency | p-value notation varies (p<1e-16 vs 9.22e-17) |
| 5 | MINOR | Interpretation | Causal language ("enables", "leverage") when evidence is correlational |

## Human Review Notes (MINOR only)

- Line 98: "gpt-3.5-turbo" inconsistently capitalized vs "GPT-3.5-turbo" elsewhere
- Line 145: Extra hyphen in "widely-deployed" (compound adjective before noun is correct, but inconsistent with style elsewhere)
- Line 294: Word count note (~3,200) could be removed for final submission
- References section incomplete: "See 06_references.bib" placeholder should be expanded

---

**Recommendation: ADDRESS MAJOR ISSUES before publication.**

The token-padding control is central to the "not merely artifact" claim and must show results. The H-E1 mock mode limitation must be explicit since the title mentions "Calibration" but ECE was never actually measured.
