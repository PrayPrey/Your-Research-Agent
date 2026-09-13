# Superseded Hypothesis Record

**Date:** 2026-08-03T12:30:00Z
**Hypothesis:** h-e1
**Superseded By:** Phase2A-redesign (new hypothesis to be generated)
**Status:** SUPERSEDED → ROUTED_TO_PHASE_2A

## Supersede Reason

Gate FAIL: The LongBench v2 retrieval↔compression axis is NOT empirically separable under the tested conditions. PC1 explains 98.85% of variance (threshold: <60%), and max cross-cluster Spearman ρ = 1.0000 (threshold: <0.70). Overall model capability (transformer ~40-50% vs SSM ~22-28%) dominates all variance, making axis separability untestable without controlling for capability tier.

## Compatibility Assessment

| Factor | Score/Result |
|--------|--------------|
| Compatibility Score | 0.2 |
| Recommendation | SUPERSEDE |
| Reasoning | Axis separability assumption fails because between-family capability gap (~20pp transformer vs SSM advantage) overwhelms within-category signal. Hypothesis requires fundamental redesign to control for capability confound before testing axis structure. |

## Key Experimental Findings

- PC1 variance: 0.9885 (99% of variance in one component)
- PC1 loadings: uniform ~0.41 across all 6 categories (general capability factor, not axis-specific)
- Max cross-cluster ρ: 1.0000 (Long-dialogue × Structured data pair)
- All 5 mechanism activation indicators: PASSED (code correct; negative is scientific, not implementation bug)

## Proposed Direction for New Hypothesis

1. **Control for overall capability** before testing axis differences
2. Normalize per-model scores by mean (relative axis scores)
3. Test within SSM family only: "SSM models show disproportionate gap on retrieval vs compression tasks relative to their overall performance"
4. Use residualized scores (partialling out overall capability via regression)

## Proven Components (Available for Reuse)

| Component | File | Reusable |
|-----------|------|----------|
| `build_accuracy_matrix()` | `code/data_collection.py` | ✅ with updates |
| `run_pca()` | `code/analysis.py` | ✅ |
| `compute_cross_cluster_spearman()` | `code/analysis.py` | ✅ |
| `evaluate_gates()` | `code/analysis.py` | ✅ |
| `verify_mechanism_activated()` | `code/analysis.py` | ✅ |
| `generate_all_figures()` | `code/visualization.py` | ✅ |

## Data Collected (Reusable)

8 baselines across 6 LongBench v2 categories:
- Transformers (N=5): GPT-4o-2024-08-06, Claude-3.5-Sonnet-20241022, GLM-4-Plus, Qwen2.5-72B-Instruct, Gemini-Exp-1206
- SSMs (N=3): Falcon3-Mamba-Inst-7B (26.08%), RWKV6-Finch-7B (22.93%), RecurrentGemma-IT-9B (27.35%)

---
*Superseded at: 2026-08-03T12:30:00Z*
*For cross-phase reference: Phase 2A redesign should read this before generating new hypothesis*
