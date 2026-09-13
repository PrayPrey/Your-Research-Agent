# Phase 6.5 Adversarial Review — Human Review Notes (MINOR Issues)

**Paper:** Measuring Structural Efficiency of Policy Movement
**Revision:** R1
**Date:** 2026-05-19

These MINOR issues were NOT fixed in the R1 automated revision. They require human judgment before final submission.

---

## ACC-MINOR-001: Figure 4 caption — asymmetric rounding of SEP values

- **Location:** Figure Captions section, Figure 4 caption
- **Current text:** "...the proportion of edits targeting semantic (control-flow + data-flow) AST nodes is nearly identical between methods (GRPO: 0.237, DPO: 0.238)."
- **Issue:** The values 0.237 and 0.238 use asymmetric precision — Table 1 reports GRPO Mean SEP as 0.2371 and DPO as 0.2377. Rounding to 3 decimal places gives 0.237 and 0.238 respectively, which is technically correct but visually implies a larger gap than exists (0.0007 actual difference). The Abstract uses "≈0.237" for both, which is more accurate to the spirit of the finding.
- **Recommended action:** Consider changing Figure 4 caption to use "≈0.237 for both" or "GRPO: ≈0.237, DPO: ≈0.238" to match the Abstract's framing and avoid implying false precision.

---

## BORED-MINOR-001: Abstract last sentence — potentially self-congratulatory tone

- **Location:** Abstract, final sentence
- **Current text:** "The framework is ready for deployment; the empirical question awaits a corrected run."
- **Issue:** "Ready for deployment" may read as overconfident or self-congratulatory given that the paper's empirical results are preliminary and compromised by checkpoint aliasing. Reviewers sensitive to framing may flag this as overclaiming.
- **Recommended action:** Consider softening to: "The framework is validated end-to-end; the empirical question awaits a corrected experimental run." Alternatively, keep as-is if the authors judge that "ready for deployment" accurately describes the framework's validated state and is appropriately scoped by the second clause.

---

## SKEPT-MINOR-001: Elhage et al. year mismatch between in-text and reference list

- **Location:** Section 2.4 in-text citation vs. References section
- **In-text:** "[Elhage et al., 2022]"
- **Reference entry:** "[Elhage et al., 2022] Nelson Elhage et al. A Mathematical Framework for Transformer Circuits. Transformer Circuits Thread, **2021**."
- **Issue:** The in-text citation uses year 2022, but the reference entry lists 2021 as the publication year. These are inconsistent.
- **Recommended action:** Verify the actual publication/release year of "A Mathematical Framework for Transformer Circuits" and make the in-text citation and reference entry consistent. The Transformer Circuits Thread paper was first posted in 2021; if using 2021, update the in-text citation to [Elhage et al., 2021].

---

*These issues require human review before final submission. Do not auto-fix.*

---

## Round 2 (R2) MINOR Issues

*Added from 065_review_r2.md — 2026-05-19*

---

### MINOR-R2-001: Abstract final sentence — potentially overconfident framing

- **Location:** Abstract, final sentence
- **Current text:** "The framework is ready for deployment; the empirical question awaits a corrected run."
- **Issue:** "Ready for deployment" may read as overconfident given that L4 (DPO stub pairs) and L1 (synthetic data) have not been resolved in actual experiments. Reviewers sensitive to framing may flag this as overclaiming relative to the preliminary and compromised empirical state.
- **Recommended action:** Consider softening to: "The measurement framework is validated end-to-end; a corrected full-scale run with real training data and execution-oracle pairs is required to answer the empirical question."

---

### MINOR-R2-002: Elhage et al. citation year inconsistency (2021 vs 2022)

- **Location:** References section, [Elhage et al., 2022] entry
- **Issue:** Ground truth flags this citation as "PARTIAL (likely arXiv:2112.00114, 2021)". The in-text citation uses year 2022, but the paper was likely first posted in 2021. The reference entry already lists "2021" as the publication year inside the entry text, creating an internal inconsistency between the citation key year (2022) and the entry content (2021).
- **Recommended action:** Verify the actual publication/release year of "A Mathematical Framework for Transformer Circuits" and make the in-text citation key and reference entry year consistent. If 2021, update in-text citation to [Elhage et al., 2021]. (Note: this is also logged as SKEPT-MINOR-001 from R1 with slightly different framing — these are the same underlying issue.)

---

### MINOR-R2-003: Section 4.3 forward reference to aliasing — two distinct GRPO conditions

- **Location:** Section 4.3 (Alignment Methods), GRPO-binary and GRPO-error-type rows
- **Issue:** Section 4.3 presents GRPO-binary and GRPO-error-type as distinct experimental conditions with different reward signals. The note in Section 5.2 explains why they produce identical SEP statistics (both aliased to checkpoint-100). A reviewer may ask why two conditions are presented as distinct in Section 4 if the actual analysis collapses them.
- **Recommended action:** Consider adding a forward reference in Section 4.3 after the table: "(Note: in the preliminary h-m1 run, both GRPO conditions produced identical SEP statistics due to checkpoint aliasing described in Section 5.3.)"

---

### MINOR-R2-004: Tilde notation inconsistency in Section 5.1 table

- **Location:** Section 5.1, Table, rows "Mean edit-per-KL"
- **Issue:** The table shows "~25.9 (low-KL pairs)" and "~3.7 (low-KL pairs)" with tilde notation, while the bootstrap CI and mean differential rows use precise values (4.6500, 8.7314, 6.5047). The tilde values are less precisely stated without explanation of why they are approximate.
- **Recommended action:** Clarify whether these approximate values are derived from the same bootstrap analysis or a different calculation. If approximate, state "approx." explicitly rather than using tilde notation, and note the source of the approximation.
