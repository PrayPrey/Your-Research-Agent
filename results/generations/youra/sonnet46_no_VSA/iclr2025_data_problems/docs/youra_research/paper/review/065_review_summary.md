# Adversarial Review Summary

**Paper**: "Language-Family Retention Bias from Global CCNet Perplexity Thresholding: A Calibrated Measurement on RedPajama-V2"
**Review Completed**: 2026-07-30
**Rounds Completed**: 2 (R1 + R2)
**Final Status**: CONVERGED
**Persuasiveness Check**: PASSED

---

## Executive Summary

This paper underwent 2 rounds of adversarial review with three-persona analysis (accuracy_checker, bored_reviewer, skeptical_expert). All FATAL and MAJOR issues were resolved by R2.

| Severity | Found | Resolved | Remaining |
|----------|-------|----------|-----------|
| FATAL | 0 | 0 | 0 |
| MAJOR | 3 | 3 | 0 |

**MINOR Issues**: 7 collected in `065_human_review_notes.md` (NOT auto-fixed)

---

## Persuasiveness Assessment

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | "86% Spanish vs 16% English" concrete and surprising — compels reading |
| Problem clear in paragraph 2? | PASS | First two paragraphs of Introduction state problem cleanly with numbers |
| Novelty clear by page 1? | PASS | Four contributions explicitly enumerated in Introduction |
| Figure 1 self-explanatory? | PASS | Caption describes V with gate bounds and n adequately |
| Hook avoids "X is important"? | PASS | Opens with counterintuitive finding, not generic motivation |
| Would bored reviewer continue reading? | YES | Attention held through Section 5; interrupted at 5.5 (pipeline IDs — in human review) |

---

## Round-by-Round Summary

### Round 1: Three-Persona Review (R1)

**Focus**: Logical conflicts, methodology contradictions, novelty overclaims, attention loss

#### Accuracy Checker Findings
| Category | Issues Found | Resolved |
|----------|--------------|---------|
| Numerical accuracy | 0 | — |
| Methodology consistency | 0 | — |
| Table values | 0 (all V values verified correct) | — |

#### Bored Reviewer Findings
| Category | Issues Found | Resolved |
|----------|--------------|---------|
| Abstract overclaim | 1 (BR-MAJOR-001) | ✅ Fixed in R1 |
| Hook quality | 0 | — |
| Pipeline ID narrative break | 1 (MINOR) | Collected for human review |

#### Skeptical Expert Findings
| Category | Issues Found | Resolved |
|----------|--------------|---------|
| Contingency table dimension | 1 (SE-MAJOR-001) | ✅ Fixed in R1 |
| Missing limitations | 0 (all 4 present) | — |
| Citation accuracy | 2 (MINOR) | Collected for human review |
| Novelty questions | 0 | — |

**Key Issues Addressed in R1**:

1. **BR-MAJOR-001** — Abstract sentence "never been precisely quantified" overclaimed. Narrowed to: "the magnitude of the language-group retention disparity produced by applying a single global threshold to pre-computed ccnet_perplexity scores on RedPajama-V2 has not been precisely quantified using a standard association metric." This aligns with the more specific claim already present in Section 2.5.

2. **SE-MAJOR-001** — "2×5 contingency table" transposed to "5×2 contingency table (5 languages × 2 outcomes: retained/removed)" with formula notation clarified: r=5 (languages, row dimension), c=2 (retained/removed, column dimension). Computation was always correct; only the text description was inverted.

### Round 2: Numerical Verification (R2)

**Focus**: Mathematical validity, baseline claims, chi² consistency with actual code output

**Verification method**: Direct results.json reading + Bash pattern search (Serena MCP unavailable; equivalent coverage achieved)

#### Accuracy Checker Findings (R2)
| Category | Issues Found | Resolved |
|----------|--------------|---------|
| Chi² values in Table 1 | 1 (NUM-MAJOR-001) | ✅ Fixed in R2 |
| Cramér's V values | 0 (all verified correct) | — |
| Retention rate percentages | 0 (all verified correct) | — |
| Prior estimate claim | 0 (25-40% verified) | — |

#### Skeptical Expert Findings (R2)
| Category | Issues Found | Resolved |
|----------|--------------|---------|
| Mathematical validity | 0 (formula checks pass) | — |
| Baseline fairness | 0 (measurement paper, no baselines) | — |
| Holm correction for correlated tests | 0 (conservative, valid) | — |

**Key Issue Addressed in R2**:

3. **NUM-MAJOR-001** — Chi² values in Table 1 were from h-e1-v3 (prior iteration), not the authoritative h-e1-v3-v4 run. Root cause: 065_ground_truth.yaml carried forward stale chi² values. Corrected to authoritative values:

| k | Before | After |
|---|--------|-------|
| 10 | 33,674 | 33,675 |
| 20 | 56,076 | 56,153 |
| 30 | 66,156 | 66,000 |
| 40 | 67,752 | 67,572 |
| 50 | 58,570 | 58,342 |

Cramér's V values were correct throughout and unchanged.

---

## Sections Modified

| Section | Modifications |
|---------|---------------|
| Abstract | Narrowed "never been precisely quantified" to dataset+signal+threshold specific scope |
| Methodology (Sec 3.4) | Fixed "2×5" → "5×2" contingency table description; clarified r/c notation |
| Results (Table 1) | Updated chi² values to match authoritative h-e1-v3-v4/results.json |
| Introduction | Unchanged |
| Related Work | Unchanged |
| Experiments | Unchanged |
| Discussion | Unchanged |
| Conclusion | Unchanged |

---

## Quality Improvements

- **Logical Consistency**: Improved (Abstract now matches Section 2.5 claim scope)
- **Numerical Accuracy**: Improved (chi² values now match code output)
- **Methodology Description**: Improved (contingency table dimensions correct)
- **Novelty Claims**: Refined (Abstract scope narrowed)
- **Baseline Comparison**: N/A (measurement paper)
- **Persuasiveness**: Unchanged (already strong)
- **Hook Quality**: Unchanged (strong counterintuitive opening)

---

## Reviewer Preparation Notes

Potential remaining attack surfaces:

1. **Sample size generalization**: 208k (~0.0002% of full corpus) — acknowledged in L2. Response: Statistical power is high (Holm p ≈ 0); structural mechanism is corpus-agnostic; three runs confirm consistency.

2. **Missing correction mechanism**: Paper does not test whether per-language calibration fixes the bias — acknowledged in L1. Response: Existence finding is independently publishable and necessary for correction studies to be properly powered; h-m1 is the designated next step.

3. **Document-length confound**: Acknowledged in L3. Response: 72.7pp gap substantially exceeds plausible length confound; KDE plots show structural distributional differences.

4. **Five languages only**: Acknowledged in L4. Response: Covers two full language families; finding is structurally driven by CCNet KenLM training, not language-specific.

5. **Jansen et al. 2022 citation accuracy**: In human review notes (HRN-007) — verify before submission.

6. **Singh et al. year discrepancy** (2024 vs 2026): In human review notes (HRN-006) — verify and add to References.

---

## Human Review Notes Location

7 MINOR issues collected in: `docs/youra_research/paper/review/065_human_review_notes.md`

Priority items before submission:
- HRN-001: Remove pipeline IDs (h-e1, h-e1-v3, h-e1-v3-v4) from Section 5.5
- HRN-006: Add missing Singh et al. citation to References (year: 2024 or 2026)
- HRN-007: Verify Jansen et al. 2022 characterization accuracy

---

## Final Outputs

| File | Path |
|------|------|
| Final Paper | `docs/youra_research/paper/06_paper_final.md` |
| R1 Review | `docs/youra_research/paper/review/065_review_r1.md` |
| R2 Review | `docs/youra_research/paper/review/065_review_r2.md` |
| Review Summary | `docs/youra_research/paper/review/065_review_summary.md` |
| Changelog | `docs/youra_research/paper/review/065_changelog.md` |
| Human Review Notes | `docs/youra_research/paper/review/065_human_review_notes.md` |
| Checkpoint | `docs/youra_research/paper/review/065_review_checkpoint.yaml` |

**Next Phase**: Phase 6.5.1 (Overleaf LaTeX/PDF generation)
