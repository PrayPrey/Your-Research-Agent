# Human Review Notes
# Phase 6.5 Adversarial Review v2.0

> **Purpose:** Minor issues collected during adversarial review for human review.
> **v2.0 Policy:** These issues are NOT auto-fixed by AI. Author review required.

**Generated**: 2026-05-10T00:00:00+00:00
**Rounds Completed**: R1 (R2 issues will be appended)

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 3 |
| Clarity | 4 |
| Formatting | 0 |
| **Total** | **7** |

---

## Round 1 Issues

### Style

**HRN-002** — Abstract, sentence 3  
"Our central finding is a clean null result" — "clean" is informal. Suggest: "principled null result" or "definitive null result."

**HRN-006** — Section 6.4 Discussion  
"The Three-Method Pipeline Reduces to Two" — the framing may be read as self-critical. Consider rephrasing as "The Active Pipeline for This Setting: SynCode + Z3" which is more descriptive and positive.

**HRN-003** — Section 5.3 Results  
F_SynCode→✓ = 2 transitions from 20×20=400 problem-sample pairs (0.5%) and delta_ast=0.075 (7.5% population-level improvement) are related but different metrics. A sentence reconciling these — population rate vs. discrete transition count — would help readers understand why a 7.5% rate improvement corresponds to only 2 counted transitions. (Possible explanation: delta_ast is a continuous AST failure rate improvement, not equivalent to binary pass@1 transitions.)

### Clarity

**HRN-001** — Abstract  
"Z3 eligibility 33% of HumanEval" is the full-benchmark figure. The 20-problem experiments use 25%. Consider adding "(full benchmark)" to disambiguate: "Z3 eligibility 33% of HumanEval (full 164 problems)."

**HRN-005** — Section 3, Experimental Protocol  
The text states "SynCode generates a separate pool; mypy and Z3 operate on the baseline pool." This may confuse readers: if the baseline pool is frozen and SynCode is a generation-time constraint, how do we know SynCode is comparable? A sentence clarifying: "SynCode requires re-running generation with the constraint active; the resulting SynCode pool uses the same seeds as the baseline pool, enabling direct comparison of AST failure rates while acknowledging that completions differ."

**HRN-007** — Sections 5.3 and 6.2  
"estimated power is approximately 25%" — the basis for this estimate is not given. What formula or tool was used? A power calculation citation or brief formula (e.g., via a paired sign test or bootstrap power analysis) would strengthen this.

**HRN-004** — Table 2  
The `*` footnote marker in the "Functional" row (11.0%*) connects to the footnote explanation but in the original paper this was formatted inline as a table Note row. The R1 revision moved to a proper footnote format, which is better, but authors should verify table rendering in the ICML template (LaTeX footnotes in tables require `\footnote{}` within tabular environment).

---

## Recommended Priority

1. **Fix First**: HRN-001 (Abstract 33% disambiguation — high visibility, easy fix)
2. **Fix Second**: HRN-007 (Power analysis basis — affects credibility with statistical reviewers)
3. **Consider**: HRN-003 (F_SynCode→✓ vs. delta_ast reconciliation — moderately important for technical readers)
4. **Consider**: HRN-005 (Frozen pool vs. SynCode pool distinction — helpful for reproducibility)
5. **Optional**: HRN-002, HRN-006 (Style preferences — subjective)
6. **LaTeX check**: HRN-004 (Formatting — template-specific)

---

## Round 2 Issues (Added)

### Clarity

**HRN-008** — Table 2 (Section 5.2)  
The R1 footnote states "~367 non-success samples" (with approximation tilde). The exact count should be verifiable from `h-m2/results/fmd_results.json`. Authors should replace "~367" with the precise figure. This ensures full numerical transparency for reproducibility.

**HRN-009** — Section 6.2 (informational)  
MAJOR-R2-001 fix addressed constraint_active=False disclosure. This note remains as documentation: authors should verify that the explanation in the added §6.2 paragraph accurately reflects the implementation behavior (partial enforcement explanation). Consider adding the h-e1 validation report as supplementary material or footnote reference.

---

## Summary by Category (Updated — All Rounds)

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 3 |
| Clarity | 6 |
| Formatting | 0 |
| **Total** | **9** |

---

*Note: These issues do not block paper acceptance but improve overall quality and reviewer experience.*
