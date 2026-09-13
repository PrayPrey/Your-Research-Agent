# Phase 6.5 Adversarial Review — Summary

**Paper:** Quality Filters as Demographic Reweighting: Auditable Corpus-Level Fairness Signals in Pretraining Data Curation
**Hypothesis:** H-PCFH-v1
**Review completed:** 2026-03-15
**Rounds executed:** 2 (R1 + R2)
**Final status:** CONVERGED

---

## Review Process

### Round 1 (R1) — Three-Persona Review

**Persona 1: Accuracy Checker**

Cross-checked every numerical claim in the paper against:
- h-e1/04_validation.md (actual experimental output)
- h-m1/04_validation.md
- h-m2/04_validation.md
- verification_state.yaml
- 065_ground_truth.yaml

Key findings:
- MAJOR: Table 2 entropy values for C0, C2, C3, C4, C6 did not match h-e1/04_validation.md actual experimental output. The values in 065_ground_truth.yaml (which the paper used) were inconsistent with the validation report. The headline claim (-22.41% relative change C1→C5) was correct since C1 and C5 values matched across all sources.
- MAJOR: As a result, the DoReMi relative change claim (-6.61%) was also incorrect; actual value is -1.51%.
- All H-M1 log-odds values verified as correct (rounded).
- H-M2 Spearman ρ=0.357 (validation report) correctly used over ρ=-0.2143 (verification_state.yaml discrepancy).
- Negative control |C7-C0|=0.495 verified correct; paper's PASS interpretation is correct despite h-m2/04_validation.md's misleading "FAIL" label.
- Bootstrap CI [-1.154, -0.330] verified.
- All probe counts (2,160 per config), training steps (95,368), and gate thresholds verified.

**Persona 2: Bored Reviewer**

- Abstract compelling; hook effective.
- "p≈0" notation informal; should cite exact p-value. (MINOR — not auto-fixed)
- Novel framing ("fastText as demographic reweighting mechanism") is punchy and memorable.
- Results section engaging; "Surprising Finding: ρ=1.0" subsection adds intellectual interest.
- Limitation section appropriately honest.

**Persona 3: Skeptical Expert**

- Novelty claims appropriately scoped to corpus-level; no overreach to downstream fairness outcomes.
- H-M3 not executed — correctly acknowledged in limitations.
- H-M2 FAIL_EXPLORE classified correctly as underpowered, not null.
- Negative control design is sound; C7 properly destroys conditional associations while preserving entropy.
- ρ=1.0 saturation caveat present in Section 5.3.
- No overreach in abstract or introduction.

### Round 2 (R2) — Numerical Verification

Re-verified all numbers in the revised paper post-R1 fixes. All values consistent with validation reports. No additional discrepancies found.

---

## Issues Found and Resolved

### FATAL Issues (0)

None. The headline claims are correct.

### MAJOR Issues (2 — both FIXED)

**M1: Table 2 entropy values incorrect for C0, C2, C3, C4, C6**
- Source: h-e1/04_validation.md shows different values than 065_ground_truth.yaml for 5 of 7 configs
- Resolution: Corrected Table 2 to use h-e1/04_validation.md values (actual experimental output)
- Impact: Core claim (-22.41% C1→C5) unchanged; intermediate values and relative percentages corrected
- Discovery: Effect is nonlinear — modest reductions C2-C4 (0.5–4.9%), dramatic drop C4→C5 (-18.4% step)

**M2: DoReMi relative change incorrect**
- Was: -6.61% (from wrong C6 value)
- Corrected to: -1.51% (from actual C6=3.2209 bits)
- Context updated: DoReMi actually shows minimal entropy reduction vs. unfiltered — preserves demographic diversity better than fastText at equivalent scale

### MINOR Issues (5 — NOT auto-fixed, in 065_human_review_notes.md)

- m1: "p≈0" informal notation in abstract and intro; recommend citing exact p-value (1.4×10⁻²⁴)
- m2: h-m2/04_validation.md labels negative control "FAIL" (threshold direction error); paper is correct but should add clarifying note
- m3: "seven corpus configurations" phrasing imprecise (Spearman computed across C1-C5, not all 7)
- m4: DoReMi "+6.5% few-shot accuracy" claim in related work needs citation verification
- m5: Citation format inconsistency between 01_introduction.md and 06_paper.md for Soldaini et al.

---

## Convergence Assessment

| Criterion | R1 | R2 |
|-----------|----|----|
| FATAL issues | 0 | 0 |
| MAJOR issues | 2 | 0 |
| Round | 1 | 2 |
| Persuasiveness | Adequate | Adequate |
| CONVERGED | No | **Yes** |

---

## Final Assessment

The paper's core contributions are valid and well-supported:
1. -22.41% entropy reduction at production threshold — verified
2. ρ=1.0 log-odds monotonic correlation — verified
3. Negative control passes — verified
4. Limitations honestly stated — confirmed

The paper correctly scopes claims to corpus-level effects and does not overstate model-level or benchmark-level findings. Post-revision, all numerical claims in the paper are consistent with actual experimental outputs.
