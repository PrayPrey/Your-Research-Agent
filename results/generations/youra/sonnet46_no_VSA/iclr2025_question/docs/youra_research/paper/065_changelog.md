# Phase 6.5 Changelog

**Generated:** 2026-08-03
**Rounds:** 2 (R1 → R2 → Converged)

---

## FATAL Fix (R2): Numerical Corrections from experiment_results.json

All metrics corrected from stale 04_validation.md values to authoritative experiment_results.json values.

**Files modified:**
- `paper/06_paper.md` — all instances updated
- `paper/06_paper_final.md` — generated from corrected 06_paper.md
- `paper/sections/00_abstract.md`
- `paper/sections/01_introduction.md`
- `paper/sections/03_methodology.md`
- `paper/sections/04_experiments.md`
- `paper/sections/05_results.md`
- `paper/sections/06_discussion.md`
- `paper/sections/07_conclusion.md`

**Numerical changes:**
| Metric | Before | After |
|--------|--------|-------|
| N | 300 ("PoC") | 2500 (full run) |
| Pearson \|r\| | 0.049 | 0.026 |
| Spearman ρ | -0.081 | -0.026 |
| Partial R²(SE) | 0.0101 | 0.0005 |
| LRT p-value | 0.1504 | 0.442 |
| LRT chi² | (not reported) | 1.632 |
| SE variance | 0.133 | 0.100 |
| min_logprob mean | -2.415 | -2.435 |
| Correctness rate | 34.3% (103/300) | 34.8% (870/2500) |

**Narrative changes:**
- Paper no longer framed as "N=300 PoC smoke test with results pending N=2500"
- RQ2 status changed from PARTIALLY CONFIRMED → NOT CONFIRMED (genuine null)
- Partial R² interpretation changed from "underpowered" → "well-powered null result at N=2500"
- Discussion revised to explain dissociation: signals are independent but predictively redundant on this benchmark
- Conclusion revised to include null result as a primary contribution

---

## MAJOR Fixes (R1)

1. **Abstract** — Added "20× lower than first-token signals" contrast and partial R² null result. Previously buried the key comparative finding.

2. **Introduction para 1** — Added null result to opening paragraph. Previously intro claimed "near-orthogonality" as the sole finding; now accurately describes dual finding (independence + null conditional contribution).

3. **Introduction para 4** — Restructured gap/novelty paragraph to: (a) identify both independence AND conditional predictive contribution as the questions being answered, (b) add "min_logprob is not first-token confidence" with "20× lower" contrast, (c) report partial R² null inline.

4. **Contribution 3** — Changed from "Power boundary characterization" (reframing a limitation as a contribution) to "Conditional predictive null result at full scale" (honest characterization of the actual finding).

5. **Table 5.2 (LR coefficients)** — Removed misleading "95% CI" column header that appeared to promise CI values without providing them. Replaced with "Direction / Significance" columns. Added note pointing to stats.json and Figure 4 for exact values.

6. **Introduction para 3 (AUROC ~0.825)** — Added explicit caveat: "this figure is from prior internal runs on the same dataset configuration, not replicated at N=2500 in the present evaluation" to prevent misattribution of an unreplicated prior result.

---

## MINOR Issues (collected for human review — not auto-fixed)

See `065_human_review_notes.md`:
1. "bidirectional NLI" ambiguity — should clarify means two asymmetric NLI calls (A→B and B→A).
2. Gabriel (2026) timeline inconsistency — arXiv:2605.05166 dates to 2026, potentially after an ICML 2025 submission deadline.
3. "Late-position tokens where factual information is concentrated" — empirical claim without citation or verification in this work.
4. LM-judge calibration not independently validated beyond the circularity check.
5. LRT chi²=1.632 not reported in the main text (only p=0.442); table shows only p-value.
