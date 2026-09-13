# Limitation Record: h-m2 (Run 1)

**Date:** 2026-05-11T11:18:00+00:00
**Hypothesis:** h-m2
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

SHOULD_WORK gate failed: aggregation_rate=0.272 (95% CI: [0.253, 0.292]) is below the 0.50 threshold.
deberta-large-mnli NLI clustering does NOT produce meaningful semantic aggregation on HaluEval-QA responses.
This is an A2 violation — the NLI model does not generalize to HaluEval-QA short factual QA response style.

## Failed Checks

- aggregation_rate=0.272 < threshold=0.50 (PASS criterion)
- ci_lower=0.253 < threshold=0.30 (secondary criterion)
- gate_pass=False

## Partial Results

| Metric | Value |
|--------|-------|
| aggregation_rate | 0.272 |
| bootstrap_ci_lower | 0.253 |
| bootstrap_ci_upper | 0.292 |
| mean_cluster_count | 4.644 |
| std_cluster_count | 0.657 |
| median_cluster_count | 5.0 |
| collapse_rate | 0.002 |
| gate_result | PIVOT |
| cluster_count_source | hm1_summary |
| n_examples | 2000 |

## Experiment Summary

H-M2 analyzed NLI clustering aggregation behavior on 2,000 HaluEval-QA examples using
deberta-large-mnli (lorenzkuhn/semantic_uncertainty). Cluster counts loaded from H-M1
experiment_results.json (hm1_summary path). Mean cluster count=4.644 (close to maximum N=5),
indicating that 72.8% of examples had all 5 responses assigned to distinct clusters.
Only 27.2% of examples showed any aggregation (cluster_count < 5).
This is consistent with the degenerate case predicted from H-M1 findings (mean_clusters=4.644).

The NLI model (deberta-large-mnli, fine-tuned on MNLI) does not reliably detect semantic
equivalence in short factual QA responses from LLaMA-2-7B-chat on HaluEval-QA, likely because:
1. Short QA answers use informal language not well-represented in MNLI training data
2. Lexically diverse but semantically equivalent answers are not recognized as entailing
3. The model was not fine-tuned on QA-style response pairs

Pipeline action: PIVOT (SHOULD_WORK gate — does not halt pipeline). H-M3 proceeds.

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded to H-M3 with this limitation noted.

Future research attempts should consider:
1. Fine-tuning the NLI model on QA-style response pairs
2. Using a more permissive entailment threshold (e.g., NEUTRAL counts as partial aggregation)
3. Alternative clustering methods (e.g., embedding cosine similarity threshold)
4. Using a QA-specific NLI model instead of general MNLI fine-tuned models

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0 (from Phase 5 PARTIAL),
  this limitation informs brainstorming to avoid similar issues
- **Phase 6 Discussion:** Limitation is included in paper's Limitations section

---
*Limitation recorded at: 2026-05-11T11:18:00+00:00*
*For cross-phase reference*
*MCP status: Unavailable (TEST no-MCP environment) — written to local serena_memory/ folder*
