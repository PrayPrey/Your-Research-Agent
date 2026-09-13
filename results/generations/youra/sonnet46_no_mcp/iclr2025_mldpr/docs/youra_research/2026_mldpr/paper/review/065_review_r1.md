# Adversarial Review — Round 1 (R1)
# Three-Persona Review: Accuracy Checker + Bored Reviewer + Skeptical Expert
# Paper: "When Confounding Hides the Signal..."
# Generated: 2026-05-04T09:20:00Z

---

## Ground Truth Summary

| Metric | Ground Truth Value | Source |
|--------|-------------------|--------|
| Matched KM log-rank p | 0.0053 | h-m1/04_validation.md |
| Unadjusted KM log-rank p | 0.583 | h-m1/04_validation.md |
| Cox HR | 3.159 | h-m1/04_validation.md |
| Cox CI | [1.032, 9.672] | h-m1/04_validation.md |
| Cox p | 0.044 | h-m1/04_validation.md |
| Median TTFR high-FAIR | 158 days | h-m1/04_validation.md |
| Median TTFR low-FAIR | 202 days | h-m1/04_validation.md |
| TTFR reduction (absolute) | 44 days | calculated |
| TTFR reduction (relative to low-FAIR) | 21.8% = 44/202 | calculated |
| TTFR reduction (relative to high-FAIR) | 27.8% = 44/158 | calculated — paper's "28%" |
| CV | 0.1597 | h-e1/04_validation.md |
| n_high | 720 (14.4%) | h-e1/04_validation.md |
| n_low | 4,280 (85.6%) | h-e1/04_validation.md |
| n matched pairs | 35 | h-m1/04_validation.md |
| SMD max | 0.098 | h-m1/04_validation.md |
| Ablation A: log-rank p / HR | 0.697 / 1.06 | h-m1/04_validation.md |
| SA-2 p / HR | 0.006 / 3.00 | h-m1/04_validation.md |
| SA-3 p / HR | 0.005 / 2.93 | h-m1/04_validation.md |

---

## Executive Summary

| Severity | Count |
|----------|-------|
| FATAL | 0 |
| MAJOR | 4 |
| MINOR | 4 (collected for human review) |

**Recommendation: MAJOR REVISION** — No fatal issues. Four major issues must be fixed before R2:
1. "28% faster" ambiguous framing (misleads on TTFR reduction denominator)
2. Two "[CITATION NEEDED]" placeholders in Related Work (instant credibility failure)
3. Abstract disclaimer positioning undermines hook
4. PH violation not listed as named limitation in Discussion 6.2

---

## FATAL Issues

*None.*

---

## MAJOR Issues

### MAJOR-001: "28% faster" — Ambiguous Denominator
**Personas:** Accuracy Checker + Skeptical Expert  
**Location:** Abstract ("28% faster"), Introduction ("28% faster"), Results 5.2 ("a 44-day (28%) reduction")

**Issue:** The "28%" figure is computed as (202-158)/158 = 27.8% — the reduction relative to the *high-FAIR* group's own median (158 days). This is an unusual denominator. The more conventional interpretation of "X% faster" is the savings off the *slower* group's time: (202-158)/202 = 21.8%.

**Ground Truth:** Median TTFR: high=158d, low=202d. Reduction=44d.
- As % of low-FAIR time: 44/202 = 21.8%
- As % of high-FAIR time: 44/158 = 27.8% ≈ 28% (paper's value)

**Why it matters:** A reviewer calculating from the numbers (202-158)/202 will get 21.8%, not 28%, and call out a discrepancy. The paper should either:
(a) Use 21.8% with denominator explicitly stated, OR
(b) State "28% relative to the high-FAIR group's own median" with formula shown, OR
(c) Simply report "44 days faster" without a percentage (clearest option)

**Required fix:** Clarify the denominator OR use the more conventional 21.8% figure OR drop the percentage and report only "44 days faster."

---

### MAJOR-002: "[CITATION NEEDED]" Placeholders in Section 2
**Persona:** Bored Reviewer  
**Location:** Section 2.1 (line: "...download counts [CITATION NEEDED]"), Section 2.3 (line: "...dataset popularity [CITATION NEEDED]")

**Issue:** Two explicit "[CITATION NEEDED]" placeholders remain in the submitted text. Any reviewer will see these as evidence the paper is incomplete and not ready for submission. This would cause immediate desk rejection or the most severe review penalty.

**Required fix:**  
- Option A: Replace with actual citations if sources are known
- Option B: Reframe the claim to not require citation: "To our knowledge, no systematic empirical validation of FAIR compliance effects on download counts has been published for ML-specific repositories" — this converts the unsupported claim into a gap statement, which is actually stronger for the paper's positioning
- Option C: Remove the claim entirely if no support exists

---

### MAJOR-003: Abstract Disclaimer Positioning
**Persona:** Bored Reviewer  
**Location:** Abstract, final sentence

**Issue:** Current ending: "All mechanism results are preliminary (proof-of-concept cohort, n=35 matched pairs) pending production-scale replication."

After a strong hook and compelling results, this disclaimer lands as an anti-climax that invites the reviewer to wonder: "if everything is preliminary, why should I read this?" The disclaimer is *honest and necessary* — but its placement and framing undermine the paper's persuasive impact.

**Required fix:** Reframe the preliminary nature as part of the contribution rather than a retreat. Suggested revision:
> "We contribute the first matched survival analysis of this kind at proof-of-concept scale (n=35 matched pairs), establishing the methodological template for production-scale replication."

This preserves honesty while positioning the preliminary nature as a methodological foothold, not a weakness.

---

### MAJOR-004: PH Violation Not Listed as Named Limitation
**Persona:** Skeptical Expert  
**Location:** Discussion Section 6.2 (Limitations list)

**Issue:** The Schoenfeld test flags a proportional hazards violation in the smoke-test cohort (confirmed in h-m1/04_validation.md "What Didn't Work" and Methodology 3.4). When PH is violated, the Cox HR=3.159 cannot be interpreted as a constant hazard ratio across time — it is an average effect that may vary substantially at different time points. This is a non-trivial limitation of the key reported result.

The paper mentions PH violation in Methodology 3.4 but Discussion 6.2 lists only four limitations (L1–L4) and omits this as a named limitation.

**Required fix:** Add as L5 in Discussion 6.2:
> "L5: Proportional hazards violation. The Schoenfeld residuals test flags a potential PH assumption violation in our smoke-test cohort, suggesting the hazard ratio may not be constant over the observation window. The reported Cox HR=3.159 should be interpreted as an average effect; time-varying hazard models are warranted at production scale."

---

## MINOR Issues (for Human Review)

These are collected in `065_human_review_notes.md` — NOT auto-fixed.

| ID | Severity | Location | Issue |
|----|----------|----------|-------|
| MIN-001 | MINOR | Abstract + Results | HR notation: "3.16" (Abstract/Intro) vs "3.159" (Results). Standardize to "3.16" throughout or "3.159" throughout. |
| MIN-002 | MINOR | Abstract + Results | p-value: "p=0.005" (Abstract) vs "p=0.0053" (Results). Standardize to "p=0.0053" or "p<0.01". |
| MIN-003 | MINOR | References | Lv et al. (2022) "Are We Really Achieving Progress in Heterogeneous Graph Neural Networks?" — no connection to FAIR data principles or survival analysis. Appears to be a pipeline artifact from different research. Remove or replace. |
| MIN-004 | MINOR | Methods 3.3 | The age-FAIR correlation (high-FAIR = newer datasets) is asserted as the suppressor mechanism but not quantified. Adding a single sentence with the correlation coefficient would strengthen the methodological claim. |

---

## Persuasiveness Assessment

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS ✅ | Strong hook with concrete numbers |
| Problem clear in 1 minute? | PASS ✅ | Intro paragraph 1 executes perfectly |
| Novelty clear in 2 minutes? | PASS ✅ | Three contributions clearly stated |
| Would continue reading? | PASS ✅ | Yes — despite minor concerns |
| Attention lost at? | Section 2.1 | [CITATION NEEDED] breaks trust |
| False novelty claims? | 0 | "First" claim appropriately qualified |
| Unfair baselines? | 0 | Unadjusted KM + aggregate FAIR are appropriate |
| Overclaims? | 1 | "28% faster" denominator ambiguity |
| Missing limitations? | YES | PH violation missing from Discussion 6.2 |
| Tone overclaiming? | 0 | Tone is appropriately qualified throughout |

**Persuasiveness: PARTIALLY PASSED** — would continue reading, but [CITATION NEEDED] and 28% framing must be fixed before this is conference-ready.

---

## Summary for Revision Agent

**Fix in this priority order:**

1. **MAJOR-002 (URGENT):** Remove both "[CITATION NEEDED]" placeholders — reframe as gap statements
2. **MAJOR-001 (HIGH):** Clarify "28% faster" denominator — recommend using "44 days faster (22%)" or add explicit denominator note
3. **MAJOR-003 (MEDIUM):** Reframe abstract disclaimer as methodological contribution statement
4. **MAJOR-004 (MEDIUM):** Add PH violation as L5 in Discussion 6.2

**Do NOT auto-fix MINOR issues** — collect in human_review_notes.md.
