# Product Requirements Document: h-m3

**Hypothesis:** Under Phase 3 training (70-100% progress), if human feedback weight increases, then edge case performance improves (conflict cases resolve to intermediate preference scores [0.1-0.4], not extreme collapse to execution-only behavior), because human feedback corrects systematic AI biases and fine-tunes quality on difficult cases.

**Type:** MECHANISM
**Gate:** SHOULD_WORK
**Date:** 2026-07-12
**Author:** Anonymous

---

## Executive Summary

This PRD specifies the implementation requirements for validating hypothesis h-m3, which extends the tri-modal RL framework (h-e1, h-m1, h-m2) into Phase 3 training (70-100% progress). The system must implement Phase 3-specific weight scheduling where human feedback weight increases to correct AI biases and improve edge case handling, particularly for conflict cases where execution passes but human quality is low.

**Key Requirements:**
- Extend Phase2TriModalAggregator (validated in h-m2) to Phase 3 range (70-100%)
- Implement human feedback weight increase schedule
- Evaluate conflict case preference scores (target: [0.1, 0.4] range, not collapsed)
- Maintain correctness (pass@1 ratio ≥ 0.95)

**Success Criteria:**
1. Human weight at 100% > human weight at 70% (positive correlation)
2. Conflict case median preference ∈ [0.1, 0.4]
3. pass@1 maintained (100% checkpoint ≥ 0.95 × 70% checkpoint)

---

## Problem Statement

### Research Question
Does increasing human feedback weight during late-stage training (Phase 3: 70-100%) improve edge case performance and prevent collapse to execution-only behavior in conflict cases?

### Current State (h-m2 Validated)
- Phase 1 (0-30%): Execution-heavy weighting → basic correctness (h-m1 PASS)
- Phase 2 (30-70%): AI-heavy weighting → quality improvement (h-m2 PASS)
- **Gap:** Phase 3 (70-100%) human feedback scheduling not validated
- **Risk:** Without human feedback, edge cases may collapse to execution-only behavior (preference < 0.1)

### Proposed Solution
Extend h-m2's tri-modal aggregator framework to Phase 3:
- **Human weight increases:** 0.400 (at 70%) → ~0.700 (at 100%)
- **Execution weight decays:** 0.400 (at 70%) → ~0.200 (at 100%)
- **AI weight maintains:** Mid-level support (~0.200-0.300)
- **Evaluation:** Conflict cases (pass@1=1.0, preference<0.3 from execution-only baseline)

### Success Impact
- **If PASS:** Validates full 3-phase tri-modal training sequence (h-e1 → h-m1 → h-m2 → h-m3)
- **If FAIL:** Documents limitation, informs Phase 4.5 synthesis (SHOULD_WORK gate, not blocking)

---

## Functional Requirements

### FR-1: Phase 3 Weight Scheduling Module
**Priority:** P0 (Core Mechanism)

**Description:** Implement Phase 3 tri-modal weight scheduling that increases human feedback weight from 70% to 100% training progress.

**Acceptance Criteria:**
- Extend `Phase2TriModalAggregator` class from h-m2 validated code
- Implement `compute_weights(training_progress)` for Phase 3 range (0.70-1.00)
- Weight schedule:
  - At 70%: (w_exec=0.400, w_ai=0.200, w_human=0.400)
  - At 100%: (w_exec≈0.200, w_ai≈0.250, w_human≈0.700)
  - Normalized to sum=1.0
- Weights must be differentiable (no discrete jumps)

**Dependencies:** h-m2 validated code (Phase2TriModalAggregator)

**Input:** `training_progress` (float in [0.70, 1.00])
**Output:** `(w_execution, w_ai, w_human)` normalized weights

---

### FR-2: Conflict Case Dataset Preparation
**Priority:** P0 (Gate Validation)

**Description:** Prepare conflict case dataset for edge case evaluation.

**Acceptance Criteria:**
- Filter 50 samples from HumanEval+MBPP with:
  - pass@1 = 1.0 (execution succeeds)
  - human_preference < 0.3 (from execution-only baseline in h-m1)
- Store as separate dataset for evaluation
- Document conflict case characteristics (why execution passes but quality low)

**Dependencies:** HumanEval + MBPP datasets (validated in h-m1, h-m2)

**Input:** HumanEval + MBPP test sets + h-m1 execution-only baseline results
**Output:** `conflict_cases.json` (50 samples)

---

### FR-3: Phase 3 PPO Training Loop
**Priority:** P0 (Core Implementation)

**Description:** Extend h-m2 PPO training loop to Phase 3 range (70-100% progress).

**Acceptance Criteria:**
- Reuse h-m2 validated PPO trainer
- Training range: 70% → 100% progress (4000 episodes in Phase 3)
- Checkpoints at [70%, 80%, 90%, 100%] for weight trajectory monitoring
- Same optimizer config: Adam, lr=3e-4
- Same model: CodeGen-350M (smoke test from h-m2)
- Fixed seed: 42 (reproducibility)

**Dependencies:** 
- FR-1 (Phase 3 weight scheduling)
- h-m2 validated PPO trainer

**Input:** Model checkpoint at 70% (from h-m2 Phase 2 endpoint)
**Output:** Model checkpoints at [80%, 90%, 100%]

---

### FR-4: Gate Validation Metrics
**Priority:** P0 (Success Criteria)

**Description:** Implement metrics computation for SHOULD_WORK gate validation.

**Acceptance Criteria:**
1. **Human Weight Trajectory:**
   - Compute w_human at [70%, 80%, 90%, 100%]
   - Verify positive correlation (Pearson r > 0)
   
2. **Conflict Case Preference Score:**
   - Evaluate 50 conflict cases at 100% checkpoint
   - Compute median preference score
   - Target: ∈ [0.1, 0.4] (not collapsed to [0.0, 0.1])
   
3. **Correctness Maintenance:**
   - Compute pass@1 at [70%, 100%] checkpoints
   - Verify ratio: pass@1(100%) / pass@1(70%) ≥ 0.95

**Dependencies:** 
- FR-2 (Conflict case dataset)
- FR-3 (Checkpoints)

**Input:** Checkpoints + conflict case dataset
**Output:** `gate_metrics.json` with all 3 criteria results

---

### FR-5: Baseline: Execution-Only (from h-m1)
**Priority:** P1 (Comparison Reference)

**Description:** Use h-m1 execution-only baseline results for comparison.

**Acceptance Criteria:**
- Load h-m1 execution-only baseline checkpoint
- Evaluate on conflict cases
- Expected: median preference < 0.1 (collapsed behavior)
- Store for comparison with tri-modal Phase 3 results

**Dependencies:** h-m1 validated code and checkpoints

**Input:** h-m1 execution-only checkpoint
**Output:** `baseline_conflict_scores.json`

---

### FR-6: Baseline: Phase 2 Endpoint (from h-m2)
**Priority:** P1 (Continuation Reference)

**Description:** Use h-m2 Phase 2 endpoint (70% checkpoint) as starting point for Phase 3.

**Acceptance Criteria:**
- Load h-m2 checkpoint at 70% progress
- Extract metrics: pass@1=0.636, quality=0.520 (from h-m2 validation)
- Use as Phase 3 initialization

**Dependencies:** h-m2 validated checkpoint at 70%

**Input:** h-m2 checkpoint at 70% progress
**Output:** Starting point for Phase 3 training

---

### FR-7: Figure Generation (Gate Report)
**Priority:** P0 (Validation Report)

**Description:** Generate figures for 04_validation.md gate report.

**Acceptance Criteria:**
1. **Weight Trajectory Plot:**
   - Line plot: All 3 weights (execution, AI, human) vs checkpoints [70%, 80%, 90%, 100%]
   - Highlight human weight increase
   
2. **Conflict Case Preference Distribution:**
   - Histogram: Tri-modal Phase 3 vs Execution-only baseline
   - Show median lines and target range [0.1, 0.4]
   
3. **Gate Metrics Bar Chart:**
   - Target vs actual for all 3 gate criteria
   - Color code: green=pass, red=fail

**Dependencies:** FR-4 (Gate metrics)

**Input:** gate_metrics.json + baseline results
**Output:** 3 figures saved to `figures/` folder

---

## Data Requirements

### Input Data

| Dataset | Source | Size | Purpose |
|---------|--------|------|---------|
| **HumanEval** | HuggingFace `openai_humaneval` | 164 problems | Code generation evaluation |
| **MBPP** | HuggingFace `mbpp` | 500 problems | Code generation evaluation |
| **Combined Test Set** | HumanEval + MBPP | ~66 problems (10% split) | Full evaluation |
| **Conflict Cases** | Filtered from combined | 50 samples | Edge case evaluation |

**Preprocessing:**
- Prompt formatting: Function signature + docstring
- Test case execution: Python exec() with timeout
- Conflict case filtering: pass@1=1.0 AND preference<0.3

### Model Checkpoints

| Checkpoint | Source | Purpose |
|------------|--------|---------|
| **h-m2 at 70%** | h-m2 Phase 2 validation | Phase 3 starting point |
| **h-m1 execution-only** | h-m1 baseline | Comparison baseline for conflict cases |

### Output Data

| Artifact | Format | Content |
|----------|--------|---------|
| **Checkpoints** | PyTorch .pt | Model states at [80%, 90%, 100%] |
| **Conflict dataset** | JSON | 50 filtered samples |
| **Gate metrics** | JSON | All 3 criteria results |
| **Figures** | PNG | 3 plots for validation report |

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seed: 42 for all random operations
- Deterministic evaluation (no sampling during metrics)
- Document all hyperparameters in config file

### NFR-2: Code Reuse (Incremental Extension)
- **MUST reuse:** h-m2 validated Phase2TriModalAggregator framework
- **MUST extend:** Only Phase 3 weight schedule (0.70-1.00 range)
- **MUST NOT:** Rewrite validated components from h-m1/h-m2

### NFR-3: Performance Constraints
- Training time: Target < 8 hours on single GPU (A100)
- Model size: CodeGen-350M (smoke test) or StarCoder-1B (full scale)
- Memory: Fit in 40GB GPU memory

### NFR-4: Gate Validation
- All 3 success criteria MUST be evaluated
- Results MUST be saved to 04_validation.md
- SHOULD_WORK gate: Document limitations if FAIL, continue pipeline

---

## Success Criteria

### Gate Validation (SHOULD_WORK)

**Primary Criteria:**
1. ✅ **Human Weight Increase:** w_human(100%) > w_human(70%) (positive correlation)
2. ✅ **Conflict Case Non-Collapse:** Median preference ∈ [0.1, 0.4]

**Secondary Criteria:**
3. ✅ **Correctness Maintenance:** pass@1(100%) / pass@1(70%) ≥ 0.95

**Gate Result:**
- **PASS:** All 3 criteria met → Hypothesis validated
- **FAIL:** ≥1 criteria failed → Document limitation, continue to Phase 4.5 (SHOULD_WORK, not blocking)

### Code Quality
- All code extends h-m2 validated framework (no rewrites)
- Checkpoints saved and loadable
- Figures generated automatically
- 04_validation.md report complete

---

## Dependencies & Constraints

### Code Dependencies
- **h-m1 validated code:** Execution-only baseline, PPO framework
- **h-m2 validated code:** Phase2TriModalAggregator, Phase 2 checkpoints
- **External libraries:** PyTorch, HuggingFace transformers/datasets

### Data Dependencies
- **HumanEval + MBPP:** Standard code generation benchmarks
- **h-m1 baseline results:** For conflict case identification

### Constraints
- **Incremental design:** MUST extend h-m2, NOT rewrite from scratch
- **PoC scale:** CodeGen-350M for smoke test (350M params, not 1.5B)
- **Gate type:** SHOULD_WORK → Document failures, don't block pipeline
- **Budget:** FULL tier (max 30 tasks)

---

## Technical Architecture (High-Level)

```
Phase 3 Training Pipeline:
  Input: h-m2 checkpoint at 70%
  ├─ Phase3TriModalAggregator (extend h-m2)
  │   ├─ compute_weights(0.70-1.00) → (w_e, w_a, w_h)
  │   └─ aggregate_rewards(r_exec, r_ai, r_human)
  ├─ Phase3PPOTrainer (reuse h-m2)
  │   ├─ Episodes: 4000 (70% → 100%)
  │   ├─ Checkpoints: [80%, 90%, 100%]
  │   └─ Optimizer: Adam lr=3e-4
  └─ Output: Checkpoints at [80%, 90%, 100%]

Evaluation Pipeline:
  Input: Checkpoints + Conflict cases (50 samples)
  ├─ Metrics:
  │   ├─ Human weight trajectory
  │   ├─ Conflict case preference scores
  │   └─ Correctness (pass@1) maintenance
  ├─ Baselines:
  │   ├─ h-m1 execution-only (for conflict cases)
  │   └─ h-m2 at 70% (for correctness)
  └─ Output: gate_metrics.json + 3 figures
```

---

## Evaluation Plan

### Test Cases

| Test ID | Description | Success Criteria |
|---------|-------------|------------------|
| **T-1** | Weight trajectory | w_human increases from 70% to 100% |
| **T-2** | Weight normalization | sum(w_e, w_a, w_h) = 1.0 at all checkpoints |
| **T-3** | Conflict case median | Median preference ∈ [0.1, 0.4] |
| **T-4** | Correctness maintenance | pass@1 ratio ≥ 0.95 |
| **T-5** | Checkpoint loading | All checkpoints loadable and runnable |
| **T-6** | Figure generation | 3 figures saved to figures/ folder |

### Validation Protocol
1. Run Phase 3 training (70% → 100%)
2. Evaluate gate metrics at each checkpoint
3. Generate figures for validation report
4. Write 04_validation.md with gate result (PASS/FAIL)
5. Update verification_state.yaml

---

## Appendix

### Phase 2C Source
- **File:** `docs/youra_research/h-m3/02c_experiment_brief.md`
- **Level:** 1.5 (Concrete + Pseudo-code)
- **Research Backing:** Archon KB (RLHF principles), h-m1/h-m2 validated implementations

### Hypothesis Chain
- **h-e1 (EXISTENCE):** Tri-modal RL framework achieves ≥3% improvement (PASS)
- **h-m1 (MECHANISM):** Phase 1 execution-heavy weighting (0-30%) (PASS)
- **h-m2 (MECHANISM):** Phase 2 AI-heavy weighting (30-70%) (PASS)
- **h-m3 (MECHANISM):** Phase 3 human-heavy weighting (70-100%) (current)

### Task Budget
- **Tier:** FULL (MECHANISM hypothesis)
- **Total Max:** 30 tasks
- **Epic Range:** 6-12 epic tasks
- **Infrastructure:** Standard (data prep, environment, epic implementation, failsafe)

### Traceability

| PRD Section | Phase 2C Source | Notes |
|-------------|-----------------|-------|
| FR-1 Weight Scheduling | Section "Proposed Model" pseudo-code | Direct extension of h-m2 |
| FR-2 Conflict Cases | Section "Evaluation" metrics | 50 samples specified |
| FR-3 Training Loop | Section "Training Protocol" | Reuse h-m2 validated config |
| FR-4 Gate Metrics | Section "Evaluation" success criteria | All 3 criteria from Phase 2C |
| FR-5/6 Baselines | Section "Continuation Context" h-m1/h-m2 | Validated prior hypotheses |
| FR-7 Figures | Section "Visualization Requirements" | 3 mandatory figures |

---

**End of PRD**
