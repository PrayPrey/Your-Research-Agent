# Adversarial Review Round 1

**Date:** 2026-08-29  
**Focus:** Accuracy and Engagement  
**Personas:** Accuracy Checker, Bored Reviewer, Skeptical Expert

---

## Summary

| Severity | Count |
|----------|-------|
| FATAL | 0 |
| MAJOR | 1 |
| MINOR | 2 |

---

## FATAL Issues

None.

---

## MAJOR Issues

### MAJOR-001: Missing Limitation — ImageNet-V2 Construction Methodology

**Persona:** Skeptical Expert  
**Location:** Section 6 (Discussion), Limitations subsection  
**Category:** missing_limitations

**Issue:** The paper acknowledges only testing ImageNet → ImageNet-V2, but does NOT discuss that ImageNet-V2 was designed to replicate ImageNet's collection methodology. This construction choice may preserve ranking stability BY DESIGN rather than demonstrating genuine robustness to distribution shift.

**Ground Truth Reference:** `065_ground_truth.yaml` lists this under `potential_objections`: "V2 construction methodology may have preserved ranking by design"

**Required Fix:** Add explicit limitation acknowledging that V2's construction methodology (replicating ImageNet's protocol) may contribute to the observed stability, and that more distant distribution shifts may show different patterns.

---

## MINOR Issues (Collected for Human Review)

### MINOR-001: Imprecise Confidence Language

**Persona:** Skeptical Expert  
**Location:** Section 7 (Conclusion), paragraph 1  
**Text:** "with 96% confidence"

**Issue:** Conflates Kendall-τ correlation value (0.96) with statistical confidence. τ = 0.96 is the correlation coefficient, not a confidence level.

**Suggested Fix:** Change to "with τ = 0.96 correlation" or "with high statistical confidence (p < 10⁻⁴⁰)"

### MINOR-002: Section Redundancy

**Persona:** Bored Reviewer  
**Location:** Sections 3 and 4

**Issue:** Section 4 (Experimental Setup) repeats some information already covered in Section 3 (Methodology), creating minor redundancy.

**Suggested Fix:** Consolidate or differentiate the sections more clearly.

---

## Persuasiveness Checks (Bored Reviewer)

| Check | Result |
|-------|--------|
| Abstract compelling? | ✓ PASS |
| Problem clear in 1 minute? | ✓ PASS |
| Novelty clear in 2 minutes? | ✓ PASS |
| Figure 1 self-explanatory? | ✓ PASS (caption adequate) |
| Would continue reading? | ✓ PASS |
| Attention lost at? | Never |

**Overall:** PASSED

---

## Accuracy Verification (Accuracy Checker)

| Claim | Paper Value | Ground Truth | Match |
|-------|-------------|--------------|-------|
| Kendall-τ | 0.9647 | 0.9647 | ✓ |
| 95% CI | [0.9454, 0.9795] | [0.9454, 0.9795] | ✓ |
| p-value | 1.58e-43 | 1.58e-43 | ✓ |
| Spearman-ρ | 0.9964 | 0.9964 | ✓ |
| Mean accuracy drop | 11.68% | 11.68 | ✓ |
| SD | 1.87% | 1.87 | ✓ |
| Sample size | 96 | 96 | ✓ |
| Max rank change | 9 | 9 | ✓ |

**Overall:** All numerical claims verified. No discrepancies.

---

## Next Steps

1. **Fix MAJOR-001** in Revision R1
2. **Collect MINOR issues** in human_review_notes
3. **Proceed to Convergence Check** (Step 04)
