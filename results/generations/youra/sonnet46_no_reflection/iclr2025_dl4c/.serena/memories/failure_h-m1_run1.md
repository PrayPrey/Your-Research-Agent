# Phase 4 Failure Record: h-m1 (Run 1)

**Date:** 2026-05-19T09:45:00
**Hypothesis:** h-m1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** STATISTICAL_INSIGNIFICANCE / DATA_ALIASING

## Performance Gap

| Metric | Ours (GRPO) | Baseline (DPO) | Gap |
|--------|-------------|----------------|-----|
| Mean SEP | 0.2371 | 0.2377 | -0.0006 (negligible) |
| p-value | 0.4248 | — | required p<0.05 |

## Gate Evaluation

- **Gate Type:** MUST_WORK
- **Gate Result:** FAIL
- **Criterion:** p < 0.05 (statistical significance)
- **Actual p-value:** 0.4248 → NOT significant
- **Routing:** ROUTED_TO_PHASE_0

## Root Cause Analysis

- H-E1 only produced 2 GRPO checkpoints (insufficient diversity)
- 25 out of 27 comparison pairs reused checkpoint-100 → data aliasing
- Mechanism infrastructure is functional (AST decomposition, SEP computation, 5 figures generated)
- The aliased data produced near-identical SEP values for GRPO and DPO, making meaningful comparison impossible
- Statistical test could not detect true difference due to lack of independent samples

## Lessons Learned

1. Prerequisite hypothesis checkpoints must be verified for diversity BEFORE running incremental h-m1 analysis
2. Data aliasing from reusing the same checkpoint N times produces artificially low variance and invalid p-values
3. Infrastructure (AST decomposition, SEP pipeline, visualization) works correctly — the failure is in data diversity, not mechanism
4. Future attempts must ensure H-E1 produces sufficient checkpoint diversity (at least 5+ independent checkpoints)
5. GRPO training runs should checkpoint at multiple epochs/steps to enable valid pairwise comparison

## Feedback for Next Phase (Phase 0)

### Suggested Modifications
- Redesign H-E1 to produce more checkpoints (e.g., checkpoint every 50 steps, min 10 checkpoints)
- Consider direct GRPO vs DPO training with matching seeds and multiple independent runs
- Alternatively, restructure h-m1 to not depend on h-e1 checkpoint diversity

### What NOT To Do
- Do not reuse the same checkpoint for multiple pairs in statistical comparison
- Do not proceed to SEP analysis with < 5 independent GRPO checkpoints

### What Showed Promise
- AST decomposition module works correctly
- SEP (Structural Edit Profile) computation pipeline is functional
- Visualization (5 figures) generated successfully
- The measurement infrastructure is ready — only data diversity needs fixing

## Infrastructure Status (Reusable)

The following code modules are functional and can be reused in future attempts:
- `code/ast_decomposition.py` — AST decomposition
- `code/sep_analysis.py` — SEP computation
- `code/statistical_tests.py` — Wilcoxon signed-rank test
- `code/visualize_m1.py` — Visualization (5 figures)
- `code/run_m1_analysis.py` — Orchestrator

---
*For cross-phase reference*
*Written at: 2026-05-19T09:45:00*
