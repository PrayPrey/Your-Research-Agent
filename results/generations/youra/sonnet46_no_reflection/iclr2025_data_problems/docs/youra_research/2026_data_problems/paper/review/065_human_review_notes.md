# Human Review Notes
# Phase 6.5 Adversarial Review — MINOR Issues for Human Review
# v2.0: These issues are NOT auto-fixed by AI.
# Generated: 2026-05-13T10:10:00Z

> **Purpose:** Minor issues collected during adversarial review for human review.
> **v2.0:** These issues are NOT auto-fixed — they require human judgment on style, clarity, and formatting.

**Generated**: 2026-05-13T10:10:00Z
**Rounds Completed**: 2 (R1 + R2)

---

## Summary by Category

| Category | Count |
|----------|-------|
| Style    | 1     |
| Clarity  | 1     |
| Formatting | 1   |
| Typo     | 0     |
| Grammar  | 0     |
| **Total** | **3** |

---

## Round 1 Issues

### Style

1. **Section 1 (Introduction), paragraph 3**: The phrase "We hypothesize — and attempt to verify —" uses em-dash hedging that slightly undersells the contribution. The paper has a clear finding and the abstract already states it. Consider rephrasing to: "We designed and executed an experiment to verify that logistic regression trained on geometry features can predict which detector will perform best..." (or similar active framing that doesn't position the paper as "still trying to verify" when the finding is documented).
   - **Impact**: Minor — does not affect scientific content, purely rhetorical.
   - **Priority**: Low.

### Clarity

2. **Section 2.3 (Benchmark Contamination Audits), final paragraph**: The subsection ends with the Hidayat et al. [2025] citation without a bridge sentence connecting back to the paper's main argument. The section discusses prior contamination audit work but doesn't explicitly motivate why benchmark heterogeneity (the MMLU/GSM8K contrast found in §5.2) was expected and important. Suggested addition (one sentence): "This benchmark heterogeneity motivates our cross-corpus overlap characterization in §5.2, where MMLU and GSM8K exhibit opposite recall profiles against the same pretraining corpora."
   - **Impact**: Minor — a reader who skips §2.3 will not be confused by §5.2, but the bridge improves flow.
   - **Priority**: Low.

### Formatting

3. **Figure references and numbering (all sections)**: Figures are referenced by number throughout (Figure 1 in §5.3, Figure 2 in §5.1, Figure 3/4/5 in §5.4/§5.3) but exist as external PNG files. The figure numbering in the text should be verified against insertion order in the final LaTeX document (Phase 6.5.1). Specifically:
   - §5.3 references "Figure 1 visualizes gate metric values" — confirm gate_metrics.png is Figure 1 in LaTeX.
   - §5.1 references "Figure 2 shows the 2D contamination geometry phase diagram" — confirm phase_diagram.png is Figure 2.
   - §5.4 references "Figure 3 (stratum_f1_heatmap.png) and Figure 4 (minkpp_variance.png)" and §5.3 references "Figure 5 (indeterminacy_pie.png)".
   - **Action required in Phase 6.5.1**: Ensure LaTeX figure insertion order matches these references.
   - **Impact**: Will cause figure reference errors in PDF if not reconciled.
   - **Priority**: Medium (must be fixed before submission, but not in markdown review phase).

---

## Round 2 Issues

*(See Round 2 section below — populated after R2 review)*

---

## Recommended Priority

1. **Fix First**: Formatting/figure numbering (Issue 3) — must be resolved in Phase 6.5.1 LaTeX generation to avoid broken references.
2. **Consider**: Clarity bridge sentence in §2.3 (Issue 2) — low effort, improves flow.
3. **Optional**: Style rephrasing in Introduction (Issue 1) — subjective, author may prefer current hedging tone for accuracy.

---

*Note: These issues do not block paper acceptance. FATAL and MAJOR issues were resolved in Rounds 1 and 2. This file represents the remaining polish items.*
