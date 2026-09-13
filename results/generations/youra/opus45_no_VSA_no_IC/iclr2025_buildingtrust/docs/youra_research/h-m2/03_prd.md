# Product Requirements Document: H-M2

**Date:** 2026-08-24
**Hypothesis:** HaluEval measures generation coherence and consistency maintenance, capabilities distinct from TruthfulQA's misconception resistance
**Type:** MECHANISM | Gate: SHOULD_WORK
**Tier:** LIGHT (correlation analysis, no GPU)

---

## 1. Objective

Validate that HaluEval and TruthfulQA measure distinct constructs by computing Spearman correlations across N=50 models from Open LLM Leaderboard.

## 2. Success Criteria

| Metric | Threshold | Priority |
|--------|-----------|----------|
| r(HaluEval_agg, TruthfulQA) | < 0.7 | PRIMARY (gate) |
| r(HaluEval_intra) > r(cross) | True | SECONDARY |
| Code executes | No errors | REQUIRED |

## 3. Scope

### In Scope
- Fetch/load model scores (TruthfulQA, HaluEval subtasks)
- Compute Spearman correlations (cross-benchmark + intra-HaluEval)
- Bootstrap confidence intervals
- Generate visualization (heatmap, scatter, bar chart)
- Gate evaluation and report

### Out of Scope
- Model inference (use cached leaderboard scores)
- New benchmark evaluation runs
- Model fine-tuning

## 4. Data Requirements

| Dataset | Source | Size | Usage |
|---------|--------|------|-------|
| TruthfulQA scores | Open LLM Leaderboard | N=50 | Correlation baseline |
| HaluEval scores | Open LLM Leaderboard / lm-eval | N=50 | Target benchmark |

**Note:** If HaluEval not on leaderboard, run lm-evaluation-harness on model subset.

## 5. Technical Constraints

- **Compute:** CPU only (~1 min)
- **Dependencies:** pandas, scipy, numpy, matplotlib, seaborn
- **Outputs:** h-m2/04_validation.md, h-m2/figures/

## 6. Deliverables

1. `run_experiment.py` — Main analysis script
2. `04_validation.md` — Results report
3. `figures/correlation_heatmap.png`
4. `figures/scatter_halueval_truthfulqa.png`
5. `figures/gate_metrics.png`

## 7. Dependencies

- **Prerequisite:** H-M1 validated (r(TruthfulQA, MMLU) = 0.189)
- **Data:** Model scores from H-M1 + HaluEval scores

---

*Phase 3 Implementation Planning*
