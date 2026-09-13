# Product Requirements Document: H-M3

**Hypothesis:** Bidirectional models maintain ≥95% of baseline B2 AlpacaEval win rate
**Type:** MECHANISM
**Date:** 2026-08-28
**Phase 2C Source:** 02c_experiment_brief.md

---

## Executive Summary

This PRD specifies requirements for validating H-M3: testing whether multi-objective RLHF (combined helpfulness + controllability) maintains helpfulness quality. The experiment sweeps α/β weights to find configurations that preserve ≥95% of baseline AlpacaEval performance while gaining controllability.

---

## Problem Statement

Multi-objective RLHF risks degrading helpfulness when adding controllability objectives. H-M3 tests whether the Pareto frontier includes configurations maintaining near-baseline helpfulness.

**Success Condition:** At least one α configuration achieves AlpacaEval LC ≥ 0.95 × B2_baseline

---

## Functional Requirements

### FR-1: Baseline Training (B2)

Train helpfulness-only baseline for comparison.

| Attribute | Value |
|-----------|-------|
| Model | Llama-3-8B-Instruct |
| Training | PPO with α=1.0, β=0.0 (helpfulness only) |
| Reward | DeBERTa helpfulness reward model |
| Output | Checkpoint + AlpacaEval win rate |

### FR-2: Alpha Sweep Training (T1-T4)

Train 4 configurations with varying α/β weights.

| Config | α (helpfulness) | β (controllability) |
|--------|-----------------|---------------------|
| T1 | 0.2 | 0.8 |
| T2 | 0.4 | 0.6 |
| T3 | 0.6 | 0.4 |
| T4 | 0.8 | 0.2 |

**Reuse from H-M1:**
- PPOTrainer configuration
- CombinedRewardModel
- IFEvalRewardSignal

### FR-3: AlpacaEval Evaluation

Evaluate all checkpoints (B2 + T1-T4) on AlpacaEval 2.0.

| Attribute | Value |
|-----------|-------|
| Dataset | tatsu-lab/alpaca_eval (805 prompts) |
| Metric | LC (Length-Controlled) win rate |
| Judge | GPT-4 Turbo |
| API | OPENAI_API_KEY required |

### FR-4: IFEval Evaluation

Evaluate controllability on IFEval test set.

| Attribute | Value |
|-----------|-------|
| Dataset | IFEval (162 test prompts, 30% split) |
| Metric | Strict accuracy (all constraints satisfied) |
| Reuse | IFEvalEvaluator from H-E1 |

### FR-5: Gate Verification

Compute gate condition.

```python
def verify_gate(b2_win_rate: float, t_results: dict) -> bool:
    best_t = max(t_results.values())
    return best_t >= 0.95 * b2_win_rate
```

### FR-6: Visualization

Generate required figures:
- Bar chart: B2 vs T1-T4 AlpacaEval win rates
- Pareto frontier: IFEval strict accuracy vs AlpacaEval LC
- Line chart: Win rate vs α value

---

## Non-Functional Requirements

### NFR-1: Performance
- Training: ~4 hours per configuration (4x A100 80GB)
- AlpacaEval: ~$20 API cost per evaluation (805 × ~$0.025)

### NFR-2: Reproducibility
- Fixed seed: 42
- Deterministic training mode
- Logged hyperparameters

### NFR-3: Reusability
- Extend H-M1 codebase (no rewrite)
- Modular α/β configuration

---

## Data Requirements

### Training Data
- **UltraFeedback:** ~60k preference pairs (from H-M1)
- **IFEval Train:** 379 instructions (70% split, from H-E1)

### Evaluation Data
- **AlpacaEval:** 805 prompts (standard benchmark)
- **IFEval Test:** 162 instructions (30% split)

---

## Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Primary | best(T1-T4) ≥ 0.95 × B2 | AlpacaEval LC win rate |
| Secondary | Clear Pareto frontier | IFEval vs AlpacaEval plot |

---

## Dependencies

| Dependency | Source | Status |
|------------|--------|--------|
| PPO infrastructure | H-M1 | Validated |
| IFEvalRewardSignal | H-E1 | Validated |
| CombinedRewardModel | H-M1 | Validated |
| Helpfulness RM | External | Required |
| OPENAI_API_KEY | User | Required |

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| High API cost | Run PoC with 100 prompts first |
| All T* below threshold | Log Pareto frontier for partial insight |
| Training instability | Reuse H-M1 validated PPO config |

---

## Traceability

| Requirement | Phase 2C Source |
|-------------|-----------------|
| FR-1 B2 | Models → Baseline Model |
| FR-2 T1-T4 | Models → Proposed Models |
| FR-3 AlpacaEval | Evaluation → Primary Metric |
| FR-4 IFEval | Evaluation → Secondary tracking |
| FR-5 Gate | Mechanism Verification Protocol |
| FR-6 Figures | Visualization Requirements |
