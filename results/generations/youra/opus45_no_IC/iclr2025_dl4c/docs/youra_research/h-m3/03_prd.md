# Product Requirements Document: H-M3

**Hypothesis:** Dense credit assignment enables faster and more precise policy learning  
**Type:** MECHANISM  
**Date:** 2026-08-10  
**Author:** Anonymous  
**Status:** DRAFT

---

## Executive Summary

This PRD defines requirements for validating H-M3: that FGO (Fine-Grained Optimization) token masking provides dense credit assignment leading to faster convergence and higher final performance compared to standard PPO with sparse (sequence-level) credit assignment.

**Key Deliverable:** Training efficiency comparison between FGO-PPO and Standard-PPO on code generation tasks.

---

## Problem Statement

Standard PPO for code generation RL uses sequence-level rewards, providing sparse credit assignment. All tokens receive equal gradient signal regardless of whether they contributed to execution success. FGO masks non-executed tokens, providing dense credit assignment to executed code only.

**Research Question:** Does dense credit assignment (FGO) enable faster learning and better final performance than sparse credit assignment (Standard PPO)?

---

## Functional Requirements

### FR-1: Training Infrastructure

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.1 | Implement convergence measurement framework with periodic evaluation | P0 |
| FR-1.2 | Support both FGO-PPO and Standard-PPO training modes | P0 |
| FR-1.3 | Log learning curves (step, pass@1) at 100-step intervals | P0 |
| FR-1.4 | Track steps-to-target (50% pass@1 threshold) | P0 |

### FR-2: Model Configuration

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.1 | Base model: CodeLlama-7B-Instruct (meta-llama/CodeLlama-7b-Instruct-hf) | P0 |
| FR-2.2 | Support FGO token masking from H-M2 implementation | P0 |
| FR-2.3 | Standard PPO baseline with sequence-level loss | P0 |

### FR-3: Dataset Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.1 | HumanEval: 164 problems (full evaluation) | P0 |
| FR-3.2 | MBPP: 374 train, 500 test problems | P0 |
| FR-3.3 | Tokenization: CodeLlama tokenizer, max_length=512 | P0 |

### FR-4: Evaluation Metrics

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-4.1 | Primary: Steps to reach 50% pass@1 (FGO < 60% of Standard) | P0 |
| FR-4.2 | Primary: Final pass@1 at end of training (FGO > Standard) | P0 |
| FR-4.3 | Secondary: Learning curve slope (avg improvement per 100 steps) | P1 |
| FR-4.4 | Secondary: Sample efficiency (pass@1 improvement per sample) | P1 |

### FR-5: Experimental Conditions

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-5.1 | Condition 1: Standard PPO (sequence-level rewards, no masking) | P0 |
| FR-5.2 | Condition 2: FGO PPO (token-level masking via execution traces) | P0 |
| FR-5.3 | Run 3 seeds per condition (42, 123, 456) | P0 |

### FR-6: Visualization

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-6.1 | Learning curve comparison plot (FGO vs Standard PPO) | P0 |
| FR-6.2 | Steps-to-target bar chart | P1 |
| FR-6.3 | Sample efficiency plot | P1 |

---

## Non-Functional Requirements

### NFR-1: Performance
- Training: Max 5000 steps per condition
- Evaluation interval: 100 steps
- Total runtime target: <24 hours per condition on single A100

### NFR-2: Reproducibility
- Fixed random seeds (42, 123, 456)
- Deterministic training where possible
- Checkpoint every 500 steps

### NFR-3: Dependencies
- Reuse H-M1 trace collection infrastructure
- Reuse H-M2 FGO masking implementation
- No new model architecture changes

---

## Success Criteria

| Criterion | Threshold | Gate Type |
|-----------|-----------|-----------|
| Steps to 50% pass@1 | FGO < 60% of Standard | SHOULD_WORK |
| Final pass@1 | FGO > Standard | SHOULD_WORK |
| Learning curves | Plottable, comparable | MUST |

**Gate:** SHOULD_WORK - If fails, document limitation and proceed. Dense credit assignment efficiency is desirable but not blocking for overall FGO mechanism validation.

---

## Dependencies

| Dependency | Source | Status |
|------------|--------|--------|
| Trace collection | H-M1 | CONDITIONAL_PASS |
| Token masking | H-M2 | CONDITIONAL_PASS |
| CodeLlama-7B | HuggingFace | Available |
| HumanEval/MBPP | Datasets | Available |

---

## Out of Scope

- Full-scale training (deferred to Phase 5)
- Multi-GPU distributed training
- Curriculum learning (CCCS component)
- Alternative model architectures

---

## Appendix: Phase 2C Completeness Checklist

- [x] Baseline models: Standard PPO (CodeLlama-7B)
- [x] Proposed model: FGO PPO (CodeLlama-7B + token masking)
- [x] Datasets: HumanEval, MBPP
- [x] Metrics: Steps-to-target, final pass@1, learning curve slope
- [x] Ablation: 2 conditions (Standard vs FGO)
- [x] Seeds: 3 per condition

---

*Generated from Phase 2C Experiment Brief: h-m3/02c_experiment_brief.md*
