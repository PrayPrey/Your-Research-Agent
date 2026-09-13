# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review. NOT auto-fixed. Requires human judgment.

**Date**: 2026-08-31
**Rounds Completed**: 2 (R1, R2)

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 2 |
| Clarity | 4 |
| Formatting | 1 |
| Reproducibility | 1 |
| **Total** | **8** |

---

## Round 1 Issues

### Clarity

**MINOR-001** — Introduction, paragraph 1
"one of the most carefully curated pre-training corpora to date" — superlative without inline citation. Consider adding `[Soldaini et al., 2024]` directly after this phrase rather than relying on later citation.

**MINOR-002** — Results §5.2
The one-sided p-value sentence is confusing without first stating the null hypothesis. Suggested rewrite: first sentence of p-value paragraph states "The one-sided test asks: what fraction of bootstrap iterations does OLMo exceed Pythia? Answer: 0.004 (0.4%), far below α=0.05 — but in the wrong direction for the hypothesis."

**MINOR-004** — Methodology §3
"ID/OOD" (in-distribution/out-of-distribution) abbreviations used without definition at first occurrence. Define on first use.

**MINOR-005** — Discussion §3 (Explanation 3)
"original contamination concern was in the opposite direction" — slightly confusing. Add one sentence explaining: "The original concern was that Dolma's deduplication might inadvertently remove MMLU-adjacent content, harming OLMo. Finding that Pythia (The Pile) outperforms OLMo reverses this concern."

### Style

**MINOR-003** — Methodology §3
The paper uses "ID/OOD" and Miller et al. [2021] / Koh et al. [2021] in the Related Work section to justify ratio metrics. The connection to generalization balance could be made more explicit: "Following the OOD generalization literature, where ratio metrics characterize a model's in-distribution vs. out-of-distribution performance gap [Miller et al., 2021]..."

**MINOR-006** — Related Work, end of §2
Related Work ends abruptly with "Positioning Our Contribution" subsection. Adding a single transition sentence ("With this context, we now describe our experimental methodology") would improve flow into Section 3.

### Formatting

**MINOR-003 (Formatting)** — Results §5.2
Table 2 appears in the paper without a preceding "Table 2:" caption or label line in some rendering contexts. Verify rendering produces "**Table 2: Primary Metric Summary**" as a visible caption in PDF output.

---

## Round 2 Issues

### Reproducibility

**R2-MINOR-002** — Code: `h-e1/experiment_results.json`
The `p_value` field in experiment_results.json is stored as 0.996, but the paper uses 0.004. These are complements representing different null hypothesis framings. Recommend adding a comment in the code: `# p_value = fraction of bootstraps where OLMo > Pythia (0.004); stored complement: 0.996 = fraction where Pythia >= OLMo`. This prevents future confusion when re-running or extending the analysis.

---

## Recommended Priority

1. **Fix First**: MINOR-004 (ID/OOD definition) — readers unfamiliar with OOD literature may be confused
2. **Fix Second**: MINOR-001 (inline citation) — easy, adds precision
3. **Fix Third**: MINOR-002 (p-value sentence clarity) — reduces reader confusion about statistical framing
4. **Consider**: MINOR-005, MINOR-006 (flow improvements)
5. **Optional**: Formatting and style tweaks

---

*Note: These issues do not block paper acceptance. The core research is sound, all critical issues were resolved in R1, and numerical accuracy is confirmed by R2 verification.*
