# Adversarial Review Round 1: Three-Persona Review
# Paper: Per-Sample Hessian Trace as Annotation-Free Minority Group Proxy Under ERM Training
# Date: 2026-08-04
# Mode: UNATTENDED

---

## Ground Truth Summary

| Claim Type | Paper States | Ground Truth | Match |
|---|---|---|---|
| AUROC(t*) seeds 1-5 | 0.850, 0.885, 0.897, 0.903, 0.890 | 0.850, 0.885, 0.897, 0.903, 0.890 | ✓ |
| AUROC(t=0) mean | 0.577 | 0.577 | ✓ |
| Seeds passing H-E3 gate | 4/5 | 4/5 | ✓ |
| Spearman ρ seed 1 | 0.70 | 0.70 | ✓ |
| p_minority(t*) range | 0.9678–0.9999 | 0.9678–0.9999 | ✓ |
| Mean p_minority(t*) | 0.9919 | 0.9919 | ✓ |
| H-M1 gate | FAIL 0/5 | FAIL 0/5 | ✓ |
| CV max | 0.0283 | 0.0283 | ✓ |
| R(t*) range | 4.09–8.89 | 4.09–8.89 | ✓ |
| Minority samples | 240 (5.0%) | 240 (5.0%) | ✓ |
| Total training samples | 4795 | 4795 | ✓ |
| Implemented gate threshold | ≥4/5 (paper) vs 3/5 (code) | DISCREPANCY | ✗ |
| Abstract confidence lower bound | ≥0.97 (abstract) vs 0.9678 (table) | DISCREPANCY | ✗ |

---

## Executive Summary

| Severity | Count | Resolved |
|---|---|---|
| FATAL | 0 | N/A |
| MAJOR | 4 | 0 (to be fixed in Revision R1) |
| MINOR | 4 | 0 (collected for human review) |

**Recommendation**: CONTINUE — fix 4 MAJOR issues before convergence check.

**Persuasiveness**: FAIL — abstract overclaims "across five seeds" and lacks comparative baseline.

---

## FATAL Issues

*None found.*

---

## MAJOR Issues

### CRED-MAJOR-001: Abstract "AUROC 0.88 across five random seeds" — misleading framing
- **Category**: accuracy / overclaiming_tone
- **Evidence**: Seed 1 AUROC(t*)=0.850 but fails Spearman gate (ρ=0.70). Only 4/5 seeds pass all criteria simultaneously. The phrase "across five random seeds" implies consistent performance across all 5.
- **Section**: Abstract
- **Fix required**: Change to "in 4/5 random seeds" or "mean AUROC 0.885 across 4 passing seeds."

### CRED-MAJOR-002: Gate threshold discrepancy — paper says ≥4/5, code config says 3/5
- **Category**: methodology_contradiction
- **Evidence**: Section 3.6 states "The H-E3 gate requires ≥4/5 seeds to pass all three criteria simultaneously." Phase 4 04_validation.md code config shows `min_seeds_passing: 3`. The result (4/5) satisfies either threshold, but the stated threshold in the paper does not match the implemented threshold.
- **Section**: Section 3.6, Section 4.5 (gate descriptions)
- **Fix required**: Clarify whether the pre-registered gate was 3/5 or 4/5 and state consistently. If the gate was 3/5 and 4/5 passed, report both (stated threshold and achieved result).

### CRED-MAJOR-003: Abstract confidence lower bound "≥0.97" inconsistent with seed 5 value 0.9678
- **Category**: numerical_inconsistency
- **Evidence**: Abstract states "minority training confidence saturates to ≥0.97 at t*." Section 5.2 table correctly shows seed 5 p_minority(t*=5)=0.9678, which is < 0.97. Ground truth confirms 0.9678.
- **Section**: Abstract vs. Section 5.2
- **Fix required**: Change abstract to "≥0.967" or "≥97%" → "~97%" with footnote, or simply cite the correct range "0.97–1.0 for seeds with t*≥20; 0.97 for t*=5."

### CRED-MAJOR-004: No comparative baseline AUROC for minority detection
- **Category**: baseline_fairness
- **Evidence**: Section 5 presents AUROC>0.85 for the Hessian trace method but provides no comparison against first-order baselines (JTT proxy AUROC, SELF proxy AUROC, loss-value thresholding AUROC). The epoch-0 AUROC<0.70 is a control for ERM-induction, not a competitive baseline.
- **Section**: Section 5, Section 2.3
- **Fix required**: Add at least one comparative reference — either (a) a brief mention of what AUROC JTT/SELF achieve on the same minority detection task, or (b) an explicit statement that this comparison is out of scope for the existence result and deferred to future work with explicit justification.

---

## MINOR Issues (for Human Review)

| ID | Category | Description |
|---|---|---|
| MINOR-001 | clarity | "0.88" in abstract is unlabeled as mean — add "(mean)" or state "mean AUROC 0.885" |
| MINOR-002 | style | EVaLS cited as "[sharif-ml-lab]" without formal author/year/title — needs proper BibTeX entry |
| MINOR-003 | clarity | Compute cost (8 min/seed/checkpoint on A100) not acknowledged as scalability limitation |
| MINOR-004 | formatting | Section 3.6 repeats gate threshold language with slight variations across two paragraphs |

---

## Persuasiveness Assessment

| Check | Result | Notes |
|---|---|---|
| abstract_compelling | PASS | Clear hook, concrete number, mystery element |
| problem_clear_in_1_minute | PASS | Spurious correlations + annotation burden well framed |
| novelty_clear_in_2_minutes | PASS | "First per-sample second-order annotation-free proxy" stated explicitly |
| figure_1_self_explanatory | N/A | Figures referenced but not in document |
| would_continue_reading | YES | Dual-result framing is genuinely interesting |
| attention_lost_at | never | Technical but clear |
| false_novelty_claims_found | 0 | |
| unfair_baseline_comparisons | 1 | No comparative AUROC vs first-order baselines |
| overclaims_found | 1 | Abstract "across five seeds" when only 4/5 pass |
| tone_overclaiming_found | 1 | Abstract "≥0.97" vs actual 0.9678 |
| missing_limitations | false | Section 6.4 is comprehensive |

**Persuasiveness verdict**: FAIL (overclaim + missing baseline comparison)

---

## Summary for Revision Agent

**Priority 1 (MUST fix):**
1. CRED-MAJOR-001: Fix abstract to say "4/5 seeds" not "across five random seeds"
2. CRED-MAJOR-003: Fix abstract confidence lower bound from "≥0.97" to "≥0.967" or correct range

**Priority 2 (MUST fix with nuance):**
3. CRED-MAJOR-002: Clarify gate threshold — paper says 4/5, code says 3/5. State correct pre-registered threshold and achieved result clearly.
4. CRED-MAJOR-004: Add comparative context for AUROC>0.85 — cite what first-order baselines achieve or explicitly scope to "existence result only."

**Collect for human review (do NOT auto-fix):**
- MINOR-001 through MINOR-004 (typo/style/clarity/formatting issues)

---

*Review by: Accuracy Checker + Bored Reviewer + Skeptical Expert (R1)*
*Round: 1 | Focus: Accuracy and Engagement*
