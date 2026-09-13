# Product Requirements Document: h-m2

## Metadata
- **Hypothesis ID**: h-m2
- **Type**: MECHANISM
- **Gate**: MUST_WORK
- **Prerequisites**: h-e1
- **Generated**: 2026-08-24

## Executive Summary

Measure rank sensitivity (∂accuracy/∂log(r)) across Pythia model scales to test whether 12B models exhibit >2x higher sensitivity than 1B models, indicating a phase transition in rank importance for larger models.

## Problem Statement

h-e1 establishes that optimal LoRA rank scales sub-linearly with model size. h-m2 investigates the mechanism: do larger models become increasingly sensitive to rank choice, suggesting a phase transition where rank optimization becomes critical at scale?

## Functional Requirements

### FR-1: Data Pipeline Extension
- Reuse h-e1 SQuAD-v2 data loading infrastructure
- Add HotpotQA dataset support (distractor setting, 7,405 validation examples)
- F1 scoring for both datasets

### FR-2: Rank Sweep Execution
- Train LoRA adapters at ranks [4, 8, 16, 32, 64, 128]
- 4 Pythia models × 6 ranks × 3 seeds × 2 datasets = 144 total runs
- Reuse 72 runs from h-e1 (SQuAD-v2 portion)

### FR-3: Sensitivity Calculation Module
- Compute rank sensitivity: S = |β₁| where F1 = β₀ + β₁·log₂(r)
- Per (model, dataset, seed) tuple
- Output: sensitivity values with metadata

### FR-4: Statistical Analysis
- One-sided t-test: H₀: S(12B) ≤ 2·S(1B)
- Bootstrap 95% CI for sensitivity ratio
- Fit S = a·N^γ to test for super-linear scaling

### FR-5: Visualization
- Sensitivity vs log(N) plot with error bars
- Rank curves (F1 vs rank) overlay for all models
- Phase transition boundary visualization

## Non-Functional Requirements

### NFR-1: Computational Efficiency
- ~79 GPU-hours (A100) for new HotpotQA runs
- Reuse h-e1 artifacts where possible

### NFR-2: Reproducibility
- Fixed seeds (3 per configuration)
- Deterministic training pipeline

### NFR-3: Statistical Rigor
- α = 0.05 significance level
- 1000 bootstrap samples for CI

## Success Criteria

| Criterion | Threshold |
|-----------|-----------|
| Point estimate S(12B)/S(1B) | > 2.0 |
| 95% CI lower bound | > 1.5 |
| p-value (one-sided) | < 0.05 |

## Dependencies

- h-e1: Must pass validation (provides SQuAD-v2 runs + infrastructure)
- Models: EleutherAI/pythia-{1b,2.8b,6.9b,12b}
- Datasets: SQuAD-v2, HotpotQA

## Output Artifacts

- `results/h-m2_rank_sweep_hotpotqa.csv`
- `results/h-m2_sensitivities.csv`
- `results/h-m2_phase_transition.json`
- `figures/h-m2_sensitivity_vs_scale.png`
- `figures/h-m2_rank_curves.png`

---
*Phase 3 PRD for h-m2*
