# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-08-25T01:07:01Z
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_GATE_FAIL

## Performance Gap

| Metric | Ours | Baseline | Gap |
|--------|------|----------|-----|
| Pairwise Config Similarity | 1.0000 (all pairs) | Required: <0.9 | +0.1000 (100% over threshold) |

## Root Cause Analysis

- **Degenerate Optimization:** BO converged to identical local optimum for all 3 stages (pre-training, RAG, agent)
- **Weak Objective Signal:** PoC scale (50 training steps, 100K tokens, mock eval) insufficient to show stage-specific differences
- **Boundary Collapse:** Perplexity pushed to max (49.9), dedup to near-min (0.55) — optimizer favored "keep more documents" for all noisy objectives
- **Insufficient Training:** 1 epoch vs required 5 epochs in spec — model didn't learn enough from filtered corpus
- **Mock Evaluation Flaw:** RAG/Agent metrics used `random.normal(baseline, 0.05)` instead of real BEIR/ToolBench evaluation

## Lessons Learned

1. **Stage semantics are indirect:** "Pre-training/RAG/Agent" don't directly parameterize quality thresholds — metric-driven formulation (optimize for accuracy vs F1 vs success_rate) is clearer
2. **PoC scale factors matter:** Training steps <100 → insufficient to learn; mock eval → no signal; boundary collapse → search space needs tighter bounds
3. **Validated pipeline correctness:** Modular architecture (data/filter/train/BO/eval), BoTorch integration, similarity analysis all functional — failure is hypothesis premise, not implementation bug
4. **Threshold-stage coupling assumption wrong:** At PoC scale, different lifecycle stages don't impose distinct quality semantics exploitable through stage-conditioned parameterization

## Feedback for Next Phase

### Suggested Modifications
- Transfer to H-E2: Metric-conditioned thresholds (accuracy-optimized vs F1-optimized) instead of stage-conditioned
- Scale up to full experiment: 10M tokens, 5 epochs, real BEIR/ToolBench evaluation (60 GPU-hours)
- Reformulate as H-E1': Correlation hypothesis (threshold-metric correlations differ by stage, Spearman ρ divergence >0.3)

### What NOT To Do
- Don't assume 100K tokens + 50 steps sufficient to show stage differences
- Don't use mock evaluation for stage-specific metrics
- Don't rely on weak stage filters (fact density, imperative ratio heuristics)

### What Showed Promise
- Modular pipeline architecture with clear separation: data → filter → train → evaluate → BO
- BoTorch multi-objective optimization integration functional
- Cosine similarity analysis for configuration comparison correct

---
*For cross-phase reference*
*Written at: 2026-08-25T01:07:01Z*
