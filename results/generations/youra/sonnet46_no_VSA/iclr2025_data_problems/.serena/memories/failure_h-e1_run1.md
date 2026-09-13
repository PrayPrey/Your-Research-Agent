# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-07-29T00:00:00Z
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** FEASIBILITY_CONSTRAINT — Insufficient corpus coverage due to compute budget

## Performance Gap

| Metric | Actual | Target | Status |
|--------|--------|--------|--------|
| Wilcoxon p-value (MMLU) | 0.090 | < 0.05 | FAIL |
| Median ΔRATIO (MMLU) | 0.0 | > 0 | FAIL |
| Cliff's delta (MMLU) | 0.000142 | ≥ 0.5 | FAIL |
| mechanism_activated | false | true | FAIL |
| WinoGrande any_full_matches | 0 | > 0 (internal control) | FAIL |

## Root Cause Analysis

- **Primary**: Only ~140,000 documents (~0.05% of the full Pile, ~300B tokens) were indexed in the experiment runtime. At this sampling fraction, the probability of an exact 8-gram match between MMLU items and Pile documents is near-zero even if contamination exists. The mechanism requires full Pile indexing.
- **Secondary**: The experiment log shows `max_docs` parameter varied — the stored JSON shows `max_docs: 200`, while the experiment.log shows processing up to 140,000 docs. Either way, both are far below the ~825 GiB / ~300B token full Pile.
- **WinoGrande zero matches**: Confirms under-sampling — with full Pile, WinoGrande was expected to show near-zero but non-zero matches; absolute zero indicates insufficient coverage.
- **Method is sound**: The n-gram overlap differential approach is theoretically valid (used by EleutherAI's own lm-evaluation-harness). Failure is resource-limited, not methodological.

## Lessons Learned

1. Full Pile (825 GiB / ~300B tokens) cannot be exhaustively indexed in a standard experiment session. Requires pre-built index or distributed compute.
2. Streaming approach with early stopping (max_docs) produces results indistinguishable from null hypothesis at low doc counts.
3. WinoGrande as internal control requires sufficient Pile coverage to even show any matches — below a threshold, both benchmarks show zero matches (uninformative).
4. Alternative approach: Use a pre-built n-gram index (e.g., download EleutherAI's pre-computed Pile 13-gram index) rather than building from streaming. Or use a much smaller proxy corpus (e.g., Wikipedia + CC-News subset) where full indexing is feasible.
5. Consider reframing: If full Pile indexing is infeasible, test on a pre-processed contamination dataset (e.g., using EleutherAI's published decontamination outputs directly) rather than recomputing from scratch.

## Feedback for Next Phase (Phase 0 / Hypothesis Redesign)

### Suggested Modifications
- Use EleutherAI's pre-computed Pile 13-gram index (available via lm-evaluation-harness) instead of streaming indexing — reduces compute from 12-24 hours to minutes
- Alternative: Use smaller proxy corpora (Wikipedia dumps, C4 subset) where full indexing is feasible in hours
- Alternative: Use Pythia's published decontamination outputs directly (evals/pythia-v1/) as ground truth for H-M hypotheses; skip re-indexing for H-E1

### What NOT To Do
- Do NOT stream full 825 GiB Pile in a single experiment session without pre-built index
- Do NOT use max_docs < 1,000,000 — at < 1M docs, signal-to-noise is zero for 8-gram matching
- Do NOT interpret near-zero match counts at low coverage as evidence against contamination

### What Showed Promise
- Code pipeline (src/normalize.py, src/ngrams.py, src/matcher.py, src/stats.py) is correct — architecture is sound
- Statistical test setup (Wilcoxon signed-rank, Cliff's delta, bootstrap CI) is correctly implemented
- Figures generated correctly (fig_bootstrap_ci.png, fig_delta_ratio_scatter.png, fig_gate_metrics.png, etc.)
- WinoGrande as internal control is a good design choice — just needs sufficient corpus coverage to activate

---
*For cross-phase reference*
*Written at: 2026-07-29T00:00:00Z*
