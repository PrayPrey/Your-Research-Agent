# Product Requirements Document: H-M2

**Hypothesis:** Bidirectional models (T1-T4) achieve higher held-out IFEval strict accuracy than baselines (B1, B2, B3) by ≥2pp
**Type:** MECHANISM
**Date:** 2026-08-28

---

## Executive Summary

This PRD defines requirements for evaluating whether bidirectional reward training (combined helpfulness + IFEval constraint signal) improves held-out instruction-following performance compared to baseline approaches. Building on H-M1's validated PPO infrastructure, this experiment measures IFEval strict accuracy on a held-out test split across 7 model variants.

---

## Problem Statement

Current RLHF approaches optimize for either helpfulness (AlpacaEval) or explicit constraint satisfaction (IFEval) separately. H-M1 validated that combined reward training is stable; H-M2 tests whether this translates to improved held-out constraint-following performance.

**Hypothesis Gate:** SHOULD_WORK - at least one Ti must exceed max(B1, B2, B3) by ≥2pp on IFEval strict accuracy.

---

## Functional Requirements

### FR-1: Baseline Model Evaluation

**FR-1.1: B1 (SFT-only)**
- Load meta-llama/Meta-Llama-3-8B-Instruct
- No RLHF training
- Evaluate on IFEval test split

**FR-1.2: B2 (AlpacaEval RLHF)**
- Train with R_helpfulness only (α=1.0, β=0.0)
- PPO with 1000 steps
- Evaluate on IFEval test split

**FR-1.3: B3 (Quality-only RLHF)**
- Train with UltraFeedback preference optimization
- No IFEval signal
- Evaluate on IFEval test split

### FR-2: Proposed Model Training (T1-T4)

**FR-2.1: T1 Configuration**
- α=0.2 (helpfulness), β=0.8 (IFEval)
- Combined reward: R = 0.2·R_help + 0.8·R_ifeval

**FR-2.2: T2 Configuration**
- α=0.4, β=0.6

**FR-2.3: T3 Configuration**
- α=0.6, β=0.4

**FR-2.4: T4 Configuration**
- α=0.8, β=0.2

### FR-3: Dataset Requirements

**FR-3.1: IFEval Dataset**
- Source: google/IFEval (HuggingFace)
- Split: 70% train (reward signal), 30% test (held-out evaluation)
- Size: ~500 test prompts
- Constraint types: 25 categories

**FR-3.2: UltraFeedback (for B3)**
- Source: HuggingFace datasets
- Purpose: Quality-only baseline training

### FR-4: Evaluation Requirements

**FR-4.1: Primary Metrics**
- IFEval strict accuracy: % prompts where ALL constraints satisfied
- IFEval loose accuracy: % prompts where ANY constraint satisfied

**FR-4.2: Gate Evaluation**
- Compute max(B1, B2, B3) strict accuracy
- Check if any Ti > max_baseline + 0.02

**FR-4.3: Visualization**
- Bar chart: IFEval strict accuracy for all 7 variants
- Threshold line at max(baseline) + 2pp

### FR-5: Infrastructure Reuse (from H-M1)

- PPO training infrastructure (validated)
- Combined reward function
- IFEvalRewardSignal integration
- Training hyperparameters (lr=1.41e-5, batch=64, KL=0.02)

---

## Non-Functional Requirements

### NFR-1: Compute Efficiency
- Single GPU (A100 80GB) sufficient
- Training time: ~2-3 hours per variant

### NFR-2: Reproducibility
- Fixed seed: 1
- Deterministic evaluation

### NFR-3: Code Quality
- Extend H-M1 codebase
- Modular evaluation harness

---

## Success Criteria

| Criterion | Metric | Target |
|-----------|--------|--------|
| **Gate (SHOULD_WORK)** | max(Ti) - max(Bi) | ≥ 0.02 (2pp) |
| **Direction** | Ti vs Bi trend | Ti > Bi |
| **Completeness** | Variants evaluated | 7/7 |

---

## Dependencies

- **H-M1**: VALIDATED - provides PPO infrastructure, combined reward function
- **IFEval**: Official constraint checkers
- **trl**: PPOTrainer

---

## Out of Scope

- Multiple seeds (PoC only)
- Hyperparameter tuning
- AlpacaEval win rate measurement
- Production deployment

---

## Appendix: Traceability

| Requirement | Source |
|-------------|--------|
| B1-B3 baselines | 02c_experiment_brief.md Section "Baseline Models" |
| T1-T4 configs | 02c_experiment_brief.md Section "Proposed Models" |
| IFEval dataset | 02c_experiment_brief.md Section "Dataset" |
| Success threshold | 02c_experiment_brief.md "Gate Condition" |
