# Phase 4 Validation Report: h-m2

**Generated:** 2026-08-03T15:30:00+00:00
**Execution Mode:** UNATTENDED
**Pipeline Position:** Phase 3 → [Phase 4] → Phase 5

---

## Hypothesis Summary

| Field | Value |
|-------|-------|
| **ID** | h-m2 |
| **Type** | MECHANISM |
| **Gate Type** | SHOULD_WORK |
| **Statement** | ContractEval tasks stratified by postcondition complexity (AST-based) show oracle-isolation gap scales with contract richness tier (Spearman ρ ≥ 0.30, p < 0.05), validating the universal-property mechanism. |
| **Prerequisites** | h-m1 (VALIDATED) |

---

## Code Generation Summary

### Task Statistics

| Metric | Value |
|--------|-------|
| Total Tasks | 21 |
| Core Modules | 4 (score_richness.py, analyze_correlation.py, visualize.py, run_h_m2.py) |
| Test Files | 2 (test_score_richness.py, test_analyze_correlation.py) |
| Tests Passing | 13/13 (100%) |
| Coder-Validator Cycles | 1 |

### Generated Files

| File | Purpose |
|------|---------|
| `code/score_richness.py` | AST scoring, tier assignment, data loading |
| `code/analyze_correlation.py` | Spearman + KW + bootstrap CI + ablations |
| `code/visualize.py` | 5 publication figures |
| `code/run_h_m2.py` | Orchestrator |
| `code/tests/test_score_richness.py` | Unit tests for scoring |
| `code/tests/test_analyze_correlation.py` | Unit tests for statistics |
| `results/h_m2_results.json` | Complete results |
| `results/richness_scores.csv` | Per-task richness scores |
| `figures/figure_*.png` | 5 visualization figures |

---

## Code Quality Checklist

- [✓] Syntax validation passed (pytest 13/13)
- [✓] API signatures match 03_logic.md
- [✓] AST scoring handles malformed clauses gracefully
- [✓] Tier assignment logic correct (1=simple, 2=structural, 3=relational, 4=compound)
- [✓] Data loading uses actual H-M1 per_task_results.csv
- [✓] Contract clause extraction uses `# $_CONTRACT_$` marker to exclude procedural code

---

## Experiment Results

### Dataset Statistics

| Metric | Value |
|--------|-------|
| Tasks analyzed | 364/364 |
| Tier 1 (Simple) | 178 tasks (48.9%) |
| Tier 2 (Structural) | 40 tasks (11.0%) |
| Tier 3 (Relational) | 117 tasks (32.1%) |
| Tier 4 (Compound) | 29 tasks (8.0%) |

### Primary Statistical Results

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Spearman ρ | 0.1360 | ≥ 0.30 | ✗ BELOW THRESHOLD |
| p (asymptotic) | 4.69e-03 | < 0.05 | ✓ Significant |
| p (exact permutation) | 5.30e-03 | < 0.05 | ✓ Significant |
| 95% CI lower | 0.034 | > 0 | ✓ Positive |
| 95% CI upper | 0.235 | — | — |
| Kruskal-Wallis H | 11.22 | — | — |
| Kruskal-Wallis p | 0.0106 | < 0.05 | ✓ Significant |

### Tier Mean Oracle Gaps

| Tier | Label | Mean Gap | Tasks |
|------|-------|----------|-------|
| 1 | Simple | 0.339 | 178 |
| 2 | Structural | 0.523 | 40 |
| 3 | Relational | 0.436 | 117 |
| 4 | Compound | 0.473 | 29 |

**Note:** Non-monotonic pattern (T2 > T4 > T3 > T1) explains the low ρ despite statistical significance. Tier 2 (structural, `BoolOp` chaining) shows unexpectedly high gap.

### Ablation Results

| Ablation | ρ | p | n |
|----------|---|---|---|
| Discrete tier (integer IV) | 0.135 | 0.0051 | 364 |
| Node-count only IV | 0.127 | 0.0086 | 364 |
| HumanEval+ subset | 0.164 | 0.0383 | 117 |
| MBPP+ subset | 0.096 | 0.0671 | 247 |
| claude-3-haiku | 0.136 | 0.0047 | 364 |
| CodeLlama-13b | 0.136 | 0.0047 | 364 |
| CodeLlama-34b | 0.085 | 0.0645 | 317 |

---

## Gate Evaluation

| Field | Value |
|-------|-------|
| **Gate Type** | SHOULD_WORK |
| **Result** | FLAT_GRADIENT (ρ = 0.136 < 0.15 threshold; below ρ = 0.30 target) |
| **Gate Satisfied** | false |
| **Proceed to Phase 5** | YES (SHOULD_WORK gate — failure records limitation, pipeline continues) |

### Gate Rationale

The Spearman ρ = 0.136 is statistically significant (p = 0.005, exact permutation test) with CI excluding zero [0.034, 0.235]. The correlation direction is correct (positive). However:

1. ρ = 0.136 is below the ρ ≥ 0.30 gate threshold
2. The FLAT_GRADIENT flag activates because ρ < 0.15
3. Tier means are non-monotonic (Tier 2 jumps ahead of Tier 3 and 4)
4. The hypothesis that gap *scales* with richness tier in a strong linear fashion is **not validated**

This is consistent with the experiment brief's prediction: "Failure (ρ < 0.15) is a publishable negative finding that weakens but does not invalidate H-M1."

The finding is substantively interesting: **a weak but real correlation exists** between AST richness and oracle gap, but the tier system does not produce a clean gradient, likely because:
- ContractEval contracts are mostly input validation (pre-conditions), not rich post-conditions
- AST complexity of input-checking contracts correlates imperfectly with oracle distinguishing power
- The Tier 2 → 3 ordering issue suggests `BoolOp` chaining captures richer contracts than `any()`/`all()` for this dataset

---

## Next Steps

**SHOULD_WORK gate failure** → Continue to Phase 5 with limitation note:

> **Limitation Note:** h-m2 SHOULD_WORK gate not satisfied (ρ = 0.136 < 0.30). A weak but statistically significant correlation exists (p = 0.005). The oracle-isolation gap does not scale strongly with AST-based contract richness tier. This finding weakens but does not invalidate H-M1: the oracle-isolation gap is large and consistent (40%) regardless of tier.

---

## Mechanism Verification

| Indicator | Status |
|-----------|--------|
| richness_computed | ✓ True |
| all_tiers_present | ✓ True (1, 2, 3, 4) |
| gap_loaded | ✓ True (364 tasks) |
| gradient_direction | ✓ True (T1 < T4, overall positive) |
| spearman_computed | ✓ True |

**Mechanism activated:** True (all indicators passed)

---

## Phase 2C Handoff

### Proven Components

| Component | File | Status |
|-----------|------|--------|
| AST richness scorer | score_richness.py | ✓ Validated |
| Spearman + permutation test | analyze_correlation.py | ✓ Validated |
| Bootstrap CI | analyze_correlation.py | ✓ Validated |
| Kruskal-Wallis | analyze_correlation.py | ✓ Validated |
| 4-tier system | score_richness.py | ✓ Implemented |

### Lessons Learned

**What Worked:**
- AST-based scoring is fast, deterministic, and covers all 364 tasks
- The `# $_CONTRACT_$` marker extraction correctly isolates assert clauses from helper code
- Permutation test and bootstrap CI provide robust statistics on n=364

**What Didn't Work:**
- ρ < 0.30 — AST richness is a weak predictor of oracle gap
- Non-monotonic tier gradient suggests tier assignments don't cleanly separate contract power
- ContractEval contracts are primarily input validation (preconditions), limiting postcondition richness variation

**Key Insight:**
Oracle gap is driven more by the presence of *any* contract than by contract richness tier. The gap is uniformly high (~0.40) across all tiers, with only modest tier-to-tier variation. This suggests the oracle-isolation gap is a property of contract existence, not complexity.

### Recommendations for Dependent Hypotheses

- **h-m3** (if downstream): Consider alternative complexity metrics — number of distinct assertion clauses, presence of output constraints (not input), or semantic complexity via NL embeddings
- Contract richness stratification may need to focus on *postcondition* assertions specifically, filtered out from input validation
- The HumanEval+ subset shows stronger correlation (ρ = 0.164) than MBPP+ (ρ = 0.096) — HumanEval+ tasks tend to have richer postconditions

---

## Appendix

### Files Generated

```
h-m2/
  code/
    score_richness.py
    analyze_correlation.py
    visualize.py
    run_h_m2.py
    requirements.txt
    experiment.log
    tests/
      test_score_richness.py
      test_analyze_correlation.py
  results/
    h_m2_results.json
    richness_scores.csv
  figures/
    figure_gate_metrics.png
    figure_scatter.png
    figure_boxplot.png
    figure_heatmap.png
    figure_violin.png
  04_validation.md
```

### Raw Result JSON

```json
{
  "rho": 0.1360,
  "p_asymptotic": 4.69e-03,
  "p_exact": 5.30e-03,
  "ci_lower": 0.0345,
  "ci_upper": 0.2345,
  "kw_stat": 11.22,
  "kw_p": 0.0106,
  "FLAT_GRADIENT": true,
  "gate_passed": false,
  "gate_result": "FLAT_GRADIENT",
  "gate_type": "SHOULD_WORK"
}
```
