# Revision Changelog — R1 Round
**Paper**: BCBHS: Benchmark-Calibrated Health Score for Cross-Domain Discriminative Collapse Detection
**Input**: `06_paper.md`
**Output**: `06_paper_r1.md`
**Date**: 2026-05-19
**Issues addressed**: 5/5 MAJOR

---

## MAJOR-001: Replace "causal" language with Granger-predictive language

**Sections modified**: Abstract, Section 1 (Introduction), Section 2.1, Section 2.5, Section 3.1, Section 3.5, Section 4.2, Section 5.1 (Table 2 caption), Section 5.2, Section 5.5 (Table 5), Section 6.1, Section 6.2 (L4), Section 7

**Changes made**:

1. **Abstract**: "it is causally driven by submission accumulation, confirmed via Granger causality" → "submission accumulation is demonstrated to temporally precede score compression via Granger causality test ($p = 1.854 \times 10^{-5}$)"; "causal and empirical grounding" → "Granger-predictive and empirical grounding"

2. **Section 1 (Introduction)**:
   - "causal mechanism" → "temporal mechanism"
   - "causally driven by submission accumulation" → "Granger-predictively linked"
   - Parenthetical "(synthetic panel PoC)" added to the d > 5 claim
   - Contribution #1: "First Granger causal confirmation of the benchmark compression mechanism" → "First Granger-test confirmation of temporal precedence in the benchmark compression mechanism"; "This upgrades benchmark saturation from descriptive observation to causal mechanism" → "This upgrades benchmark saturation from descriptive observation to a temporally-ordered Granger-predictive relationship"
   - "causal mechanism of $H_d$ signals" → "Granger-predictive mechanism of $H_d$ signals"
   - "no cross-domain causal framework has been established" → "no cross-domain framework with temporal Granger-predictive validation has been established"

3. **Section 2.1**: "does not validate a causal mechanism linking submission accumulation to compression" → "does not validate a temporal Granger-predictive mechanism linking submission accumulation to compression"; "Granger causal validation of the compression mechanism" → "Granger-test confirmation of temporal precedence of the compression mechanism"

4. **Section 2.5**: "The Granger causal validation we provide" → "The Granger causality test we provide" (also resolves MINOR-003); "Summary" sentence updated to "Granger-predictive validation"

5. **Section 3.1**: "causally linked to submission accumulation" → "Granger-predictively linked to submission accumulation"; "causal mechanism validation via Granger causality" → "Granger-predictive mechanism validation via Granger causality"

6. **Section 3.5**: Added sentence: "We note that Granger causality establishes temporal predictability — that past values of submission count improve forecasts of score compression beyond compression's own history — but does not rule out confounding variables (e.g., benchmark age, task adoption lifecycle) or establish structural causation in the econometric sense." Changed "causally drives" → "Granger-predictively precedes"

7. **Pipeline summary (Section 3.6)**: "Causal: submissions → compression" → "Granger-predictive: submissions → compression"

8. **Section 4 header**: "RQ2 (Causal Mechanism)" → "RQ2 (Granger-Predictive Mechanism)"

9. **Section 4.2**: "vs. the lagged causal structure tested by Granger" → "vs. the lagged Granger-predictive structure"; "falsification check for causal directionality" → "falsification check for temporal directionality"

10. **Section 5.2 header/subheadings**: "Causal Mechanism" → "Granger-Predictive Mechanism"; "Causal direction is confirmed" → "Granger-predictive temporal direction is confirmed"; "causal finding" → "Granger-predictive finding"; "leading causal relationship" → "leading Granger-predictive relationship"

11. **Table 5 (Section 5.5)**: "Submission accumulation causally precedes compression" → "Submission accumulation Granger-predictively precedes compression"

12. **Section 6.1**: "causally-validated" → "Granger-predictively-validated"; "The causal confirmation upgrades..." → "The Granger-predictive confirmation upgrades..."; added note that "Granger causality establishes temporal predictability but does not rule out confounding variables"

13. **Section 6.2 (L4)**: "causal effect" → "Granger-predictive effect"; "primary causal claim" → "primary Granger-predictive claim"

14. **Section 7 (Conclusion)**: "we know why" → "we know why in a Granger-predictive sense"; "causally drives" → "Granger-predictively precedes"; "first directional causal validation" → "first directional Granger-test confirmation of temporal precedence"; "Granger-predictive and empirical foundation" replaces "causal and empirical foundation"; "confirmed the Granger-predictive foundation" replaces "confirmed the causal foundation"

---

## MAJOR-002: Add synthetic data caveat to abstract and introduction; clarify CV AUC inversion

**Sections modified**: Abstract, Section 1 (Introduction), Section 5.1 (Table 1 and text below it)

**Changes made**:

1. **Abstract**: After "very large effect sizes ($|\text{Cohen's d}| > 5$ in all three domains)" added: "(validated on synthetic benchmark panels calibrated to real PWC statistics; real-data replication is planned as future work)"

2. **Section 1 (Introduction)**: Added "(synthetic panel PoC)" qualifier to the d > 5 claim; "discriminate compressed from healthy benchmarks with very large effect sizes ($|\text{Cohen's d}| > 5$ in all three domains, $p < 0.0001$)" now ends with "on synthetic panels calibrated to real PWC statistics (real-data validation is FW1)"

3. **Table 1 (Section 5.1)**:
   - CV AUC cell changed from "— (direction inverted)" to "0.000 (direction inverted; direction-corrected AUC = 1.000)" for clarity
   - Added footnote row: "†Effect sizes computed on synthetic benchmark panels (20 saturated + 20 healthy per domain) calibrated to real PWC statistical properties. Real-data validation is future work (FW1)."

4. **Section 5.1 main text**: Added explicit paragraph after Table 1: "Note on CV AUC direction inversion. CV AUC appears as 0.000 in the standard direction because CV $H_d$ (score variance) is *lower* for saturated benchmarks — the opposite direction from NLP/tabular. The direction-corrected AUC for CV is 1.000 (i.e., the signal perfectly discriminates in the inverted direction), consistent with the $|d| = 5.267$ effect size."

5. **Section 5.1 main finding**: Added "(on synthetic benchmark panels calibrated to real PWC statistics)" qualifier

6. **Table 2 caption/context**: "consistent with the causal accumulation mechanism" → "consistent with the Granger-predictive accumulation mechanism"

---

## MAJOR-003: Explain 7,592 vs. 466 benchmark count discrepancy

**Section modified**: Section 3.4

**Changes made**:

Added explanatory sentences after "The median $\hat{\sigma}_\text{measurement}$ across 7,592 benchmarks is 0.3323.":

> "This sigma estimation uses the broader pre-filter set of all benchmarks with any repeated submissions (across the full 1,120-task archive before applying the $\geq 20$ submission and $\geq 2$ year qualifying filters), providing a more stable population-level noise estimate. The resulting sigma map is then applied as the compression threshold for the 466 qualifying panel benchmarks; using the broader estimate avoids overfitting the threshold to the smaller qualified subset."

---

## MAJOR-004: Add H-M3/H-M4 non-execution caveat to abstract

**Sections modified**: Abstract, Section 1 (Introduction — already had appropriate framing)

**Changes made**:

1. **Abstract**: Added before the final sentence:
   > "We note that the Cox proportional hazards survival prediction component (H-M3/H-M4) was not executed in this work due to a collapse operationalization incompatibility; BCBHS is presented as an empirical foundations paper establishing the Granger-predictive grounding and discriminative signals, not a validated prediction system."

2. **Abstract**: Final sentence changed from "BCBHS establishes the causal and empirical grounding for benchmark retirement monitoring at field scale." → "BCBHS establishes the Granger-predictive and empirical grounding for benchmark retirement monitoring at field scale."

3. **Section 5.5 (Table 5)**: H-E1 footnote added "(H-E1, synthetic panels)" to clarify the evidence source for the discriminability claim.

---

## MAJOR-005: Add Bonferroni correction argument

**Sections modified**: Section 5.2, Section 6.2 (L4)

**Changes made**:

1. **Section 5.2**: Added paragraph after reporting Granger $p = 1.854 \times 10^{-5}$:
   > "We note that this panel-level result is the minimum $p$-value across 41 independent Granger tests. A Bonferroni correction for 41 simultaneous tests yields a corrected significance threshold of $\alpha/41 = 0.05/41 \approx 0.00122$; the minimum $p = 1.854 \times 10^{-5}$ passes this correction, confirming the result is robust to multiple-comparison adjustment."

2. **Section 6.2 (L4)**: Added at end of L4 text: "The panel-level Granger result ($p = 1.854 \times 10^{-5}$) is the primary Granger-predictive claim; this result is the minimum $p$-value across 41 independent tests and passes Bonferroni correction ($\alpha/41 \approx 0.00122$)."

---

## Summary of All Modified Sections

| Section | MAJOR Issues Addressed |
|---------|----------------------|
| Abstract | MAJOR-001, MAJOR-002, MAJOR-004 |
| Section 1 (Introduction) | MAJOR-001, MAJOR-002 |
| Section 2.1 | MAJOR-001 |
| Section 2.5 | MAJOR-001 (also resolves MINOR-003) |
| Section 3.1 | MAJOR-001 |
| Section 3.4 | MAJOR-003 |
| Section 3.5 | MAJOR-001 |
| Section 3.6 (pipeline) | MAJOR-001 |
| Section 4 (RQ2 header) | MAJOR-001 |
| Section 4.2 | MAJOR-001 |
| Section 5.1 | MAJOR-002 |
| Section 5.2 | MAJOR-001, MAJOR-005 |
| Section 5.5 (Table 5) | MAJOR-001, MAJOR-004 |
| Section 6.1 | MAJOR-001 |
| Section 6.2 | MAJOR-001, MAJOR-005 |
| Section 7 | MAJOR-001 |

---

## What Was NOT Changed

- All quantitative values (p-values, Cohen's d, AUC, compression rates, counts) — unchanged
- Paper structure and section numbering — unchanged
- All table data values — unchanged (only footnotes and cell clarifications added)
- Research findings — unchanged
- Figure placeholder references — unchanged (MINOR-006, deferred to human review)
- Table 2 rounding (6.91/6.52) — unchanged (MINOR-001, deferred to human review)
- Section 4.2 baselines reporting — unchanged (MINOR-004, deferred to human review)

---

# Revision Changelog — R2 Round
**Paper**: BCBHS: Benchmark-Calibrated Health Score for Cross-Domain Discriminative Collapse Detection
**Input**: `06_paper_r1.md`
**Output**: `06_paper_r2.md`
**Date**: 2026-05-19
**Issues addressed**: 2/2 MAJOR

---

## R2-MAJOR-001: Table 2 Intermediate Lookback Values Corrected

**Section modified**: Section 5.1, Table 2 (Effect Sizes by Lookback Window)

**Changes made**: Replaced incorrect intermediate values with exact values from h-e1/04_validation.md:

| Cell | Old Value | Corrected Value |
|------|-----------|----------------|
| CV t-12mo | 3.40 | 3.42 |
| CV t-18mo | 4.21 | 4.35 |
| NLP t-12mo | 4.65 | 4.49 |
| NLP t-18mo | 5.80 | 5.70 |
| Tabular t-12mo | 4.22 | 4.24 |
| Tabular t-18mo | 5.50 | 5.38 |

Anchor values (t-6mo and t-24mo) were already correct and unchanged. Monotonicity conclusion ("Effect sizes increase monotonically in all three domains") remains valid with the corrected values.

---

## R2-MAJOR-002: Residual "Temporal Causal Explanation" in Abstract Replaced

**Section modified**: Abstract, second sentence

**Change made**:
- Old: "Yet until now, this phenomenon has lacked systematic cross-domain measurement or temporal causal explanation."
- New: "Yet until now, this phenomenon has lacked systematic cross-domain measurement or temporally-ordered Granger-predictive explanation."

This resolves the last remaining "causal" language instance in the paper, achieving full consistency with the R1 Granger-predictive language sweep throughout the body.

---

## Summary of All Modified Sections

| Section | R2 Issues Addressed |
|---------|---------------------|
| Abstract | R2-MAJOR-002 |
| Section 5.1 (Table 2) | R2-MAJOR-001 |

---

## What Was NOT Changed

- All other quantitative values — unchanged
- Paper structure and section numbering — unchanged
- All R1 fixes preserved intact
- Monotonicity conclusion text — unchanged (correct regardless)
- t-6mo and t-24mo anchor values — already correct, unchanged

---

# Final Summary (v2.0)

**Total Revisions Made**: 7 MAJOR issues addressed across 2 rounds
**Sections Modified**: Abstract, §1, §2.1, §2.5, §3.1, §3.4, §3.5, §3.6, §4, §4.2, §5.1, §5.2, §5.5, §6.1, §6.2, §7
**Word Count Change**: Increased by ~350 words (added qualifications, Bonferroni paragraph, explanatory sentences)

**Review Process**:
- Started: 2026-05-19T14:30:00Z
- Completed: 2026-05-19T16:30:00Z
- Rounds: 2 (R1: Accuracy+Engagement, R2: Numerical Verification)
- Personas Used: accuracy_checker, bored_reviewer, skeptical_expert

**Files Generated**:
- `paper/06_paper_final.md` (final paper = 06_paper_r2.md)
- `paper/review/065_review_summary.md` (consolidated review summary)
- `paper/review/065_human_review_notes.md` (8 MINOR issues for human review)
- `paper/review/065_changelog.md` (this file)
- `paper/review/065_review_r1.md` (R1 adversarial review)
- `paper/review/065_review_r2.md` (R2 adversarial review)

**MINOR Issues for Human Review**: 8 issues in `065_human_review_notes.md`
**Convergence**: CONVERGED (FATAL=0, MAJOR=0, persuasiveness PASSED, 2 rounds)
**Recommendation**: CONDITIONAL_ACCEPT

**Next Phase**: Phase 6.5.1 (Overleaf LaTeX/PDF generation)
