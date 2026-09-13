# Adversarial Review Changelog

## Round 1 Revisions

**Date**: 2026-08-31
**Source paper**: paper/06_paper.md
**Output paper**: paper/06_paper_r1.md

### FATAL-001 Fix: p-value Directional Standardization

**Section**: Introduction, Contribution 1
**Change**: Replaced `p=0.996 one-sided` with clarified p=0.004 statement plus complementary framing.

Before:
> "Pythia achieves significantly higher ratio (p=0.996 one-sided, d=−2.732)"

After:
> "Pythia achieves significantly higher ratio (one-sided p=0.004 for the test that OLMo ≥ Pythia, d=−2.732; equivalently, only 0.4% of bootstrap iterations show OLMo exceeding Pythia)"

**Rationale**: Paper used p=0.996 in Introduction and p=0.004 in Results for descriptions that sounded identical. These are complementary values (1−0.996=0.004). Standardized to p=0.004 which matches ground_truth.yaml and provides intuitive framing for the refutation.

---

### MAJOR-001 Fix: Abstract HellaSwag Convergence Caveat

**Section**: Abstract, paragraph 3
**Change**: Added fast-eval qualification and reframed as hypothesis-consistent finding rather than confirmed fact.

Before:
> "both models converge to identical HellaSwag commonsense scores at this training scale, collapsing the ratio... This reveals that the MMLU/HellaSwag metric loses discriminative power when its denominator saturates — a condition that holds for 6-8B models at ~300B tokens."

After:
> "both models achieve effectively identical HellaSwag commonsense scores at this training scale (0.458 each under 500-sample fast evaluation; full evaluation recommended to confirm), collapsing the ratio... This is consistent with a scale-dependent saturation of HellaSwag for 6-8B models at ~300B tokens — a hypothesis supported by the denominator's near-zero sensitivity to deduplication observed in prior work."

**Rationale**: Original Abstract overstated the fast-eval finding as a confirmed structural fact. Added fast-eval caveat, and reframed saturation as a hypothesis supported by evidence (consistent with MEDIUM confidence in ground truth YAML).

---

### MAJOR-002 Fix: "First Evaluation" Novelty Claim Scoped

**Section**: Introduction, Contribution 1
**Change**: Added *systematic* and *corpus-quality discriminator* qualifiers to the novelty claim.

Before:
> "the first evaluation of MMLU/HellaSwag generalization balance ratios comparing Pythia-6.9B... and OLMo-7B"

After:
> "the first *systematic* evaluation of MMLU/HellaSwag generalization balance ratios as a *corpus-quality discriminator*, comparing Pythia-6.9B... and OLMo-7B"

**Rationale**: Bare "first evaluation" claim cannot be verified without exhaustive prior search. Scoping to "systematic" + "corpus-quality discriminator" preserves novelty claim while grounding it in what is specifically novel about the study design.

---

### MAJOR-003 Fix: Results §5.1 Saturation Claim Softened

**Section**: Results, §5.1 (Table 1 comment)
**Change**: Removed assertive "not coincidence" language; added explicit caveat about fast-eval sampling.

Before:
> "This exact convergence is not coincidence — it reflects a scale-dependent saturation effect that is central to interpreting all other results."

After:
> "As we argue in Section 5.3, this convergence is most plausibly explained by a scale-dependent saturation effect — though we note that sampling variance with 500 examples could also produce this exact match."

**Rationale**: The paper itself rated fast-eval coincidence as "MEDIUM plausibility" in §5.3 — inconsistent with "not coincidence" assertion in §5.1. Fixed to be internally consistent.

---

## Issues Addressed

| Issue | Severity | Status |
|-------|----------|--------|
| FATAL-001: p-value directional confusion | FATAL | RESOLVED |
| MAJOR-001: Abstract HellaSwag overclaim | MAJOR | RESOLVED |
| MAJOR-002: Novelty claim unsupported | MAJOR | RESOLVED |
| MAJOR-003: Saturation claim over-asserted | MAJOR | RESOLVED |
| MINOR-001 through MINOR-006 | MINOR | Collected in human_review_notes.md |

**Sections modified**: Abstract, Introduction (Contribution 1), Results §5.1
**Sections unchanged**: Related Work, Methodology, Experimental Setup, Results §5.2-5.5, Discussion, Conclusion
**Word count delta**: +8 words (net additions from clarifying language)

---

## Round 2 Revisions

**Date**: 2026-08-31
**Source paper**: paper/06_paper_r1.md
**Output paper**: paper/06_paper_r2.md

### R2-MINOR-001 Fix: Cohen's d Magnitude Explanation

**Section**: Results §5.2
**Change**: Added parenthetical explaining why Cohen's d = −2.732 is large.

After:
> "Cohen's d = −2.732, indicating a large effect in the direction opposite to the prediction. (The large d reflects the small variance of MMLU subject-level ratio estimates across bootstrap iterations; full-evaluation CI width may be somewhat larger, but the directional refutation is unlikely to reverse given d = −2.732.)"

**Rationale**: Proactive clarification prevents reviewer confusion about an unusual effect size magnitude.

### R2 Numerical Verification

All paper claims verified against `h-e1/experiment_results.json`:
- All numerical values confirmed correct (rounded from raw JSON)
- p-value consistency confirmed (0.004 = correct fraction of bootstraps where OLMo > Pythia)
- Ratio calculations verified by hand
- No fabricated numbers detected

**R2 FATAL**: 0 | **R2 MAJOR**: 0 | **R2 MINOR**: 2 (collected for human review)

**Convergence status after R2**: CONVERGE — all criteria met (FATAL=0, MAJOR=0, persuasiveness PASSED, rounds ≥ 2)

---

## Final Summary

**Total Revisions Made**: 5
**Sections Modified**: Abstract, Introduction (Contribution 1), Results §5.1, Results §5.2
**Word Count Change**: ~6832 → ~6858 (+26 words net)

**Review Process**:
- Started: 2026-08-31T00:00:00+00:00
- Completed: 2026-08-31T00:00:00+00:00
- Rounds: 2 (R1: Three-Persona, R2: Numerical Verification)
- Personas Used: accuracy_checker, bored_reviewer, skeptical_expert

**Files Generated**:
- 06_paper_final.md (final paper)
- paper/review/065_review_summary.md (review summary)
- paper/review/065_human_review_notes.md (MINOR issues for human review)
- paper/review/065_changelog.md (this file)

**Next Phase**: Phase 6.5.1 (Overleaf LaTeX/PDF generation)
