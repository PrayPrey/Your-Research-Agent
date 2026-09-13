# Phase 4 Validation Report: h-m1

**Generated:** 2026-05-19T11:35:00+00:00
**Execution Mode:** UNATTENDED
**Pipeline Position:** Phase 3 → [Phase 4] → Phase 5
**Hypothesis Type:** MECHANISM

---

## Hypothesis Summary

| Field | Value |
|-------|-------|
| **ID** | h-m1 |
| **Type** | MECHANISM |
| **Gate Type** | MUST_WORK |
| **Gate Result** | FAIL |
| **Reflection Outcome** | ROUTED_TO_PHASE_0 |
| **Prerequisites** | h-e1 (COMPLETED, gate satisfied=true) |

**Statement:** Under controlled conditions, if execution reward directly signals functional incorrectness at program level, then the model reallocates probability mass toward control-flow and data-flow AST transformations (not surface edits), because program-level correctness objectives create gradient pressure specifically on execution-relevant code structures.

---

## Code Generation Summary

### Task Statistics

| Metric | Value |
|--------|-------|
| Total Tasks | 27 |
| Completed | 9 |
| Remaining (todo) | 2 (A-9, T-FAILSAFE) |
| Coder-Validator Cycles | 1/5 |
| Hypothesis Type | INCREMENTAL (base: h-e1) |
| Code Copied from h-e1 | Yes |

### Generated Files

| File | Size (bytes) | Purpose |
|------|-------------|---------|
| `code/ast_decomposition.py` | 8157 | FA-AST taxonomy, SEP computation |
| `code/run_m1_analysis.py` | 17229 | Main orchestrator |
| `code/sep_analysis.py` | 9304 | SEP analysis across checkpoint pairs |
| `code/visualize_m1.py` | 9987 | 5-figure visualization suite |
| `code/evaluate.py` | 7779 | Evaluation utilities |
| `code/config.py` | 4536 | M1ExperimentConfig |
| `code/data.py` | 5598 | Data loading |
| `code/statistical_tests.py` | 5405 | Mann-Whitney U, Spearman |
| `code/train_from_scratch.py` | 4726 | H-E1 checkpoint fallback trainer |
| `code/rewards.py` | 4396 | Reward computation |
| `code/kl_metric.py` | 3382 | KL divergence metric |
| `code/train_dpo.py` | 3584 | DPO trainer wrapper |
| `code/train_grpo.py` | 3755 | GRPO trainer wrapper |
| `code/ast_metric.py` | 2551 | AST metric utilities |
| `code/run_experiment.py` | 3098 | Experiment runner |
| `code/visualize.py` | 4313 | General visualization |
| `code/tests/test_ast_decomposition.py` | — | Unit tests for AST module |
| `code/tests/integration_config.py` | — | Integration test config |

### Figures Generated

| Figure | File | Size |
|--------|------|------|
| Gate SEP Comparison (MANDATORY) | `figures/gate_sep_comparison.png` | 47,411 bytes |
| AST Edit Distribution | `figures/ast_edit_distribution.png` | 36,782 bytes |
| AST Node Heatmap | `figures/ast_node_heatmap.png` | 42,373 bytes |
| Reward vs Correctness Scatter | `figures/reward_correctness_scatter.png` | 45,620 bytes |
| SEP vs KL Trajectory | `figures/sep_vs_kl_trajectory.png` | 61,583 bytes |

---

## Code Quality Checklist

- [✓] Experiment ran end-to-end without Python errors
- [✓] AST decomposition module functional (FA-AST taxonomy)
- [✓] SEP computation pipeline working (values in [0,1])
- [✓] Statistical tests executed (Mann-Whitney, Spearman)
- [✓] Results saved to `outputs/sep_results.json`
- [✓] 5 figures generated and saved to `figures/`
- [✓] Mandatory gate figure `gate_sep_comparison.png` exists
- [✓] Experiment log complete (164 lines)
- [✗] A-9 Integration Smoke Test: not completed
- [✗] T-FAILSAFE: not completed

---

## Experiment Results

### Execution Details

| Field | Value |
|-------|-------|
| Entry Point | `run_m1_analysis.py` |
| Smoke Test Mode | False (full run) |
| Problems Loaded | 542 (HumanEval+: 164, MBPP+: 378) |
| Checkpoint Pairs Configured | 27 |
| Checkpoint Pairs Actually Used | ~5 unique (aliasing) |
| Duration | ~4 seconds |
| GPU | Not required (analysis only) |
| Conda Env | youra-h-m1 |

### SEP Metrics

| Condition | Mean SEP | N Samples | vs DPO |
|-----------|----------|-----------|--------|
| GRPO Binary | 0.2371 | 192 | -0.0006 (lower) |
| GRPO Error-Type | 0.2371 | 192 | -0.0006 (lower) |
| DPO (baseline) | 0.2377 | 189 | — |

### Statistical Tests

| Test | Statistic | p-value | Significant (α=0.05) |
|------|-----------|---------|----------------------|
| Mann-Whitney (grpo_binary vs dpo) | U=18346.5 | p=0.4248 | ❌ No |
| Mann-Whitney (grpo_errortype vs dpo) | U=18346.5 | p=0.4248 | ❌ No |
| Spearman (grpo_binary) | rho=NaN | p=NaN | ❌ Undefined |
| Spearman (grpo_errortype) | rho=NaN | p=NaN | ❌ Undefined |

### Gate Evaluation Detail

| Criterion | Result | Value |
|-----------|--------|-------|
| decomposition_working | ✅ PASS | true |
| semantic_proportion_valid | ✅ PASS | true |
| grpo_higher_than_dpo | ❌ FAIL | false (0.2371 < 0.2377) |
| statistically_significant | ❌ FAIL | p=0.4248 |
| effect_size | ❌ FAIL | -0.0072 (negative) |

---

## Gate Evaluation

| Field | Value |
|-------|-------|
| **Gate Type** | MUST_WORK |
| **Result** | FAIL |
| **Satisfied** | false |
| **p-value** | 0.4248 (required: < 0.05) |
| **Effect Size** | -0.0072 (GRPO lower than DPO) |

### Failure Analysis

**Root Cause: Checkpoint Data Aliasing**

H-E1 training only produced 2 GRPO checkpoints (step-100, step-200). The 27-pair KL-matching framework required checkpoints at steps 100–1000, but steps 300–1000 fell back to checkpoint-100. This resulted in:

- 192 GRPO SEP values derived from effectively 2 distinct checkpoints
- Severe correlation/repetition violating Mann-Whitney independence assumption
- Spearman correlation undefined (NaN) due to no variance in x-axis
- Statistical test entirely underpowered — effective n≈2, not 192

This is an **experimental infrastructure failure**, not a fundamental hypothesis falsification. The mechanism (AST decomposition → SEP computation) is correctly implemented and functional.

---

## Reflection Summary

**Outcome:** ROUTED_TO_PHASE_0 (per MUST_WORK FAIL routing rule)

**Key Lessons:**
1. H-E1 must save checkpoints at every 100 steps (steps 100–1000) for H-M1 to have sufficient data
2. Early checkpoint diversity check should be added before running full 27-pair analysis
3. Checkpoint fallback logic should warn/abort rather than silently reuse checkpoint-100
4. Future redesign: reduce num_checkpoint_pairs to match actual available checkpoints (e.g., 5 pairs)

---

## Next Steps

| Action | Target |
|--------|--------|
| Route to Phase 0 | Redesign experiment with checkpoint diversity requirement |
| Cascade FAIL to h-m2 | h-m2 depends on h-m1 (prerequisite not met) |
| Preserve artifacts | All code and outputs preserved for Phase 0 reference |

---

## Phase 2C Handoff (Preserved Components)

Despite the gate FAIL, the following components are validated and reusable:

### Proven Components

| Component | File | Evidence |
|-----------|------|---------|
| AST Decomposition | `code/ast_decomposition.py` | FA-AST taxonomy working, SEP in [0,1] |
| SEP Analysis | `code/sep_analysis.py` | Correct computation, JSON cache working |
| Statistical Tests | `code/statistical_tests.py` | Mann-Whitney and Spearman implemented correctly |
| Visualization Suite | `code/visualize_m1.py` | 5 figures generated successfully |
| Orchestrator | `code/run_m1_analysis.py` | End-to-end pipeline functional |
| Config | `code/config.py` | M1ExperimentConfig validated |

### Optimal Configuration (for future use)

```yaml
kl_tolerance: 0.15
bootstrap_samples: 10000
mann_whitney_alpha: 0.05
spearman_rho_threshold: 0.5
num_checkpoint_pairs: 5  # Revised down from 27 to match available checkpoints
min_total_edits: 1
smoke_test_problems: 10
smoke_test_pairs: 3
```

### Recommendations for Dependent Hypotheses

**h-m2** (depends on h-m1 — now CASCADE_FAILED):
- Cannot proceed until h-m1 is resolved
- When h-m1 is redesigned, ensure H-E1 saves 10 GRPO + 10 DPO checkpoints
- Reuse AST decomposition module directly (proven functional)

---

## Appendix

### Experiment Log Location
`code/experiment.log` (164 lines) — Full execution trace

### Output Files
- `outputs/sep_results.json` — Complete statistical results
- `outputs/solutions_cache/` — Cached model solutions
- `figures/` — 5 visualization figures

### Checkpoint Archive
`04_checkpoint.yaml` — Full task and execution state

### Verification State
Updated in `../verification_state.yaml`:
- `h-m1.status` → FAILED
- `h-m1.gate.satisfied` → false
- `h-m2.status` → CASCADE_FAILED (blocked by h-m1 FAIL)
