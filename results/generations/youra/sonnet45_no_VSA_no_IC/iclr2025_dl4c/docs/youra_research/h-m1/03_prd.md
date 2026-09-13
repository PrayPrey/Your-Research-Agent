# Product Requirements Document (PRD)
# Hypothesis h-m1: Feedback Efficiency Mechanism

**Version:** 1.0  
**Date:** 2026-08-19  
**Hypothesis ID:** h-m1  
**Type:** MECHANISM  
**Gate:** MUST_WORK

---

## Executive Summary

This PRD defines the implementation requirements for testing the capacity limits hypothesis (h-m1): whether small models (350M-1B params) show decreasing feedback efficiency as granularity increases from binary → error-type → error+trace. The implementation extends h-e1's binary/error-type framework with a new error+trace condition, trains 4 conditions (SFT, Binary, Error-Type, Error+Trace), and evaluates feedback efficiency (pass@1 gain per bit) to test for monotonic decrease.

**Success Criteria:**
- Monotonic efficiency decrease: Binary ≥7 pp/bit, Error-Type 4-6 pp/bit, Error+Trace 2-3 pp/bit
- Statistical significance (p < 0.0167, Bonferroni correction)

---

## Problem Statement

### Context

h-e1 demonstrated that binary feedback achieves dual-threshold sufficiency (≥8pp gain, ≥80% retention ratio). The mechanism hypothesis (h-m1) asks whether this efficiency advantage holds as feedback granularity increases. If small model capacity constrains high-dimensional feedback utilization, efficiency should decrease monotonically.

### Objectives

1. Extend h-e1 with error+trace feedback condition (5.64 bits: error type × stack depth)
2. Train 4 conditions with matched compute (500 GRPO steps each)
3. Compute feedback efficiency for each condition
4. Test monotonic decrease hypothesis with statistical rigor

### Out of Scope

- Larger models (>1B params) — separate hypothesis
- Alternative feedback modalities (compiler warnings, linter output)
- Multi-task evaluation beyond HumanEval

---

## Functional Requirements

### FR1: Dataset Preparation

**HumanEval Dataset Loading**
- Load OpenAI HumanEval from HuggingFace Hub (openai/openai_humaneval)
- Extract 164 programming problems with test suites
- Cache locally to `./data/humaneval/`
- No preprocessing required (use as-is)

**Acceptance Criteria:**
- Dataset loads successfully offline from cache
- All 164 problems have prompts (signature + docstring) and test suites
- Cache verification: file hash check or size validation

### FR2: Model Loading and Configuration

**Base Model Loading**
- Primary: CodeGen-350M-mono from HuggingFace
- Fallback: StarCoder-1B (if CodeGen shows saturation)
- Precision: FP16 mixed precision
- LoRA Configuration: r=16, alpha=32, target_modules=[q_proj, v_proj]

**Acceptance Criteria:**
- Model loads on GPU (H100 NVL) within 10GB VRAM
- LoRA adapter initializes correctly with 16-rank decomposition
- Same pretrained checkpoint used for all 4 conditions

### FR3: SFT Baseline Training

**Supervised Fine-Tuning**
- Training Data: (prompt, canonical_solution) pairs from HumanEval
- Objective: Causal language modeling loss
- Epochs: 5 epochs over 164 problems
- Batch Size: 8
- Learning Rate: 5e-5
- No test execution during training

**Acceptance Criteria:**
- Checkpoint saves to `checkpoints/sft/`
- Serves as reference model for KL penalty in GRPO conditions
- Generates valid Python code (syntax check on 10 random samples)

### FR4: Binary GRPO Training (Reuse from h-e1)

**Binary Feedback Reward**
- Reward Function: 1.0 (all tests pass), 0.0 (any test fails)
- Training Method: GRPO (Group Relative Policy Optimization)
- Steps: 500 training steps
- Batch Size: 8
- KL Penalty Coefficient: 0.05 (relative to SFT baseline)

**Acceptance Criteria:**
- Reuses h-e1 implementation (code/train_binary.py)
- Checkpoint saves to `checkpoints/binary/`
- Training log shows reward progression

### FR5: Error-Type GRPO Training (Reuse from h-e1)

**Error-Type Reward Mapping**
- Pass: 1.0
- AssertionError: 0.4 (closest to correct)
- TypeError: 0.3
- ValueError: 0.25
- NameError: 0.2
- OtherError: 0.1 (SyntaxError, IndexError, etc.)

**Information Content:** log₂(5) = 2.32 bits per problem

**Acceptance Criteria:**
- Reuses h-e1 implementation (code/train_error_type.py)
- Checkpoint saves to `checkpoints/error_type/`
- Error distribution logged (verify 5 categories populated)

### FR6: Error+Trace GRPO Training (NEW)

**Error+Trace Reward Function**
- Stack Depth Extraction: `len(traceback.extract_tb(exc_info[2]))`
- Depth Buckets: [0-9] levels (clamped at 9 for deep recursion)
- Depth Penalty: `1.0 - (depth / 20.0)`, clamped to [0.5, 1.0]
- Combined Reward: `error_type_reward × depth_penalty`

**Example Calculations:**
- TypeError at depth 0: 0.3 × 1.0 = 0.30
- TypeError at depth 3: 0.3 × 0.85 = 0.255
- AssertionError at depth 1: 0.4 × 0.95 = 0.38
- NameError at depth 9: 0.2 × 0.55 = 0.11

**Information Content:** log₂(5 error types × 10 depth levels) = log₂(50) ≈ 5.64 bits

**Acceptance Criteria:**
- New module: `code/sandbox_trace.py` with `compute_error_trace_reward()`
- Handles all exception types (including SyntaxError with no traceback → depth=0)
- Training: 500 steps, batch size 8, same KL penalty as other conditions
- Checkpoint saves to `checkpoints/error_trace/`
- Depth distribution logged (verify depths 0-9 populated)

### FR7: Evaluation Pipeline

**pass@1 Computation**
- Method: Greedy decoding (temperature=0), 1 sample per problem
- Execution: Run generated code against HumanEval test suite in sandbox
- Aggregation: (# problems passed) / 164
- Compute for all 4 checkpoints: SFT, Binary, Error-Type, Error+Trace

**Efficiency Calculation**
- Formula: `Efficiency = (pass@1_condition - pass@1_SFT) / bits_per_problem`
- Units: Percentage points per bit
- Bits per condition:
  - Binary: 1.0 bit
  - Error-Type: 2.32 bits
  - Error+Trace: 5.64 bits

**Statistical Testing**
- Pairwise t-tests: Binary vs Error-Type, Error-Type vs Error+Trace, Binary vs Error+Trace
- Multiple testing correction: Bonferroni (α = 0.05 / 3 = 0.0167)
- Bootstrap confidence intervals (1000 samples) for robustness check

**Acceptance Criteria:**
- All 4 checkpoints evaluate successfully (no runtime errors)
- Efficiency values computed with correct bit denominators
- p-values < 0.0167 for significance claims

### FR8: Gradient Variance Logging (Secondary)

**Training Dynamics Tracking**
- Metric: Per-batch gradient standard deviation across all LoRA parameters
- Logging Frequency: Every 10 training steps
- Computation: `torch.std(torch.cat([p.grad.flatten() for p in lora_params]))`
- Storage: CSV file per condition (`logs/gradient_variance_{condition}.csv`)

**Purpose:** Secondary evidence for H-M2 signal concentration hypothesis

**Acceptance Criteria:**
- Variance logged for all 4 conditions
- No missing batches (verify row count = steps / 10)
- Mean variance computed over full training for each condition

### FR9: Convergence Rate Tracking (Secondary)

**Convergence Metric**
- Definition: Steps to reach 90% of final eval performance
- Tracking: Evaluation loss every 25 steps during training
- Purpose: Test if simpler feedback converges faster (concentrated signal)

**Acceptance Criteria:**
- Eval loss curves saved for all 4 conditions
- Convergence step identified for each condition
- Visualization: Line plot of eval loss over training steps

---

## Non-Functional Requirements

### NFR1: Computational Efficiency

**Training Time Budget**
- SFT: 0.5 GPU-hours (5 epochs × 164 problems)
- Binary GRPO: 2.0 GPU-hours (reuse from h-e1)
- Error-Type GRPO: 2.0 GPU-hours (reuse from h-e1)
- Error+Trace GRPO: 2.0 GPU-hours (new training)
- Evaluation: 0.5 GPU-hours (4 checkpoints × 164 problems)
- **Total:** 7 GPU-hours

**Resource Constraints:**
- GPU: NVIDIA H100 NVL (verified available from h-e1)
- VRAM: <10 GB per condition (CodeGen-350M + LoRA)
- Storage: 5 GB (4 checkpoints + logs + dataset cache)

### NFR2: Reproducibility

**Deterministic Execution**
- Set random seeds: `torch.manual_seed(42)`, `np.random.seed(42)`
- CUDA deterministic mode: `torch.backends.cudnn.deterministic = True`
- Save hyperparameters with checkpoints (JSON metadata file)

**Checkpoint Metadata**
- Model name, LoRA config, training steps, reward function ID
- Timestamp, GPU type, library versions (transformers, trl, peft)

### NFR3: Code Reusability

**Modular Architecture**
- Reuse h-e1 modules: `dataset.py`, `model.py`, `eval.py`, `sandbox.py`
- Extend (not replace) `sandbox.py` with `compute_error_trace_reward()`
- New modules: `sandbox_trace.py`, `train_error_trace.py`, `analysis_efficiency.py`

**Configuration Management**
- Single config file: `config.py` with dataclass for all hyperparameters
- Override via CLI args for batch jobs

### NFR4: Statistical Rigor

**Multiple Testing Correction**
- Bonferroni correction for 3 pairwise tests (α = 0.0167)
- Report both raw and corrected p-values for transparency

**Robustness Checks**
- Bootstrap confidence intervals (1000 resamples)
- Flag if CI overlap contradicts t-test results
- Effective entropy calculation for error distribution skew detection

---

## Success Criteria

### MUST_WORK Gate Conditions

**Condition 1: Monotonic Efficiency Decrease**
- Binary efficiency > Error-Type efficiency (one-sided t-test, p < 0.0167)
- Error-Type efficiency > Error+Trace efficiency (one-sided t-test, p < 0.0167)

**Condition 2: Target Efficiency Ranges**
- Binary: ≥7 pp/bit
- Error-Type: 4-6 pp/bit
- Error+Trace: 2-3 pp/bit

**Gate Logic:**
```
IF (binary_eff > error_type_eff > error_trace_eff) AND
   (binary_eff >= 7.0) AND
   (4.0 <= error_type_eff <= 6.0) AND
   (2.0 <= error_trace_eff <= 3.0) AND
   (all pairwise tests p < 0.0167)
THEN
   gate = PASS
ELSE
   gate = FAIL → Capacity constraint mechanism refuted
```

### Validation Metrics

**Code Quality**
- All 4 training conditions complete without runtime errors
- Evaluation pipeline runs without crashes
- Stack depth extraction handles edge cases (SyntaxError, recursion)

**Data Quality**
- Error distribution spans all 5 categories (no <5% skew)
- Stack depth distribution spans 0-9 (verify with histogram)
- Gradient variance logs complete (no missing batches)

---

## Dependencies

### Internal Dependencies

**Prerequisite Hypothesis:**
- h-e1: Provides SFT, Binary, Error-Type checkpoints (reuse)
- h-e1: Validates dual-threshold sufficiency baseline

**Shared Codebase:**
- dataset.py: HumanEval loading
- model.py: CodeGen + LoRA setup
- eval.py: pass@1 evaluation
- sandbox.py: Execution sandbox (extend for trace depth)

### External Dependencies

**Python Libraries:**
- transformers==4.46.3 (model loading)
- trl==0.13.0 (GRPO trainer)
- peft==0.15.0 (LoRA)
- datasets==3.2.0 (HumanEval)
- torch==2.5.1 (GPU compute)
- matplotlib==3.10.0 (plotting)
- scipy (statistical tests)
- numpy (numerical operations)

**No new dependencies** beyond h-e1 setup.

---

## Risks and Mitigations

### R1: Error Distribution Skew

**Risk:** If 90% errors are TypeError, effective entropy drops from 2.32 → ~0.5 bits, distorting efficiency comparison.

**Mitigation:**
- Log error type frequencies during training
- Compute effective entropy: `H = -Σ p(i) log₂ p(i)`
- Re-calculate efficiency with effective bits
- Report skew detection in validation report

**Detection Criterion:** Flag if any error type >70% of total errors.

### R2: Stack Trace Depth Saturation

**Risk:** Most errors at depth 0-1 (top-level failures), trace depth adds <1 bit effective information.

**Mitigation:**
- Histogram stack depths in validation report
- Compute effective entropy of depth distribution
- If effective depth bits <1.5, adjust Error+Trace total bits to 3.5 (2.32 + 1.5)

**Detection Criterion:** Flag if depths 0-1 account for >80% of errors.

### R3: Gradient Variance Noise

**Risk:** Per-batch variance high noise (batch size 8), obscures signal for H-M2 secondary evidence.

**Mitigation:**
- Apply moving average (window=20 batches) for smoothed curves
- Report mean variance over full training (aggregate metric)
- Treat as secondary metric (H-M2 has separate experiment)

**Acceptance:** Inconclusive gradient variance findings do not block h-m1 gate.

### R4: Checkpoint Reuse Invalidation

**Risk:** h-e1 checkpoints corrupted or incompatible.

**Mitigation:**
- Verify checkpoint loading in smoke test (load + forward pass)
- If corrupted, re-train SFT/Binary/Error-Type (+4 GPU-hours)

**Probability:** Low (h-e1 completed successfully per injected state).

---

## Timeline

**Phase 3 (Implementation Planning):** Current step  
**Phase 4 (PoC Implementation):** 3 days
- Day 1: Implement `sandbox_trace.py`, smoke test error+trace reward
- Day 2: Train Error+Trace GRPO (2 GPU-hours)
- Day 3: Evaluate 4 conditions, compute efficiency, statistical tests

**Total:** Phase 2C → Phase 4 validation in 5 days.

---

## Outputs and Deliverables

### Code Artifacts

**New Files:**
- `h-m1/code/sandbox_trace.py`: Error+trace reward computation
- `h-m1/code/train_error_trace.py`: GRPO trainer for error+trace condition
- `h-m1/code/analysis_efficiency.py`: Efficiency frontier analysis + stats

**Modified Files:**
- `h-m1/code/run_experiment.py`: Orchestrate 4-condition training

**Reused from h-e1:**
- `dataset.py`, `model.py`, `eval.py`, `sandbox.py` (extended, not replaced)

### Data Artifacts

**Checkpoints:**
- `checkpoints/sft/` (reused from h-e1)
- `checkpoints/binary/` (reused from h-e1)
- `checkpoints/error_type/` (reused from h-e1)
- `checkpoints/error_trace/` (NEW)

**Logs:**
- `logs/gradient_variance_{condition}.csv` (4 files)
- `logs/efficiency_metrics.json`

### Visualizations

**Mandatory:**
- `efficiency_frontier.png`: Bar chart (3 bars: Binary, Error-Type, Error+Trace efficiency)
  - X-axis: Feedback granularity
  - Y-axis: Efficiency (pp/bit)
  - Error bars: Bootstrap 95% CI
  - Horizontal lines: Target thresholds (7, 5, 2.5 pp/bit)

**Optional:**
- `gradient_variance_curves.png`: Line plot of variance over training steps
- `error_distribution.png`: Histogram of error types + stack depths

### Reports

**04_validation.md:**
- Section 1: Efficiency frontier results (table + plot reference)
- Section 2: Statistical tests (pairwise t-tests, p-values, Bonferroni correction)
- Section 3: Gate verdict (PASS/FAIL with logic)
- Section 4: Risk analysis (error skew detection, depth saturation check)
- Section 5: Gradient variance secondary findings
- Section 6: Interpretation (mechanism confirmed or refuted)

---

## Appendix

### A. Information Content Calculations

**Binary Feedback:**
- 2 outcomes: {Pass, Fail}
- Entropy: log₂(2) = 1.0 bit

**Error-Type Feedback:**
- 5 categories: {Pass, TypeError, NameError, ValueError, AssertionError}
- Entropy (uniform): log₂(5) = 2.32 bits
- Effective entropy: Compute from observed distribution

**Error+Trace Feedback:**
- 5 error types × 10 depth levels = 50 combinations
- Entropy (uniform): log₂(50) = 5.64 bits
- Effective entropy: Product of error-type effective entropy × depth effective entropy

### B. Efficiency Calculation Example

**Scenario:**
- SFT: 40.0% pass@1
- Binary: 48.0% pass@1 → Efficiency = (48 - 40) / 1.0 = 8.0 pp/bit
- Error-Type: 50.0% pass@1 → Efficiency = (50 - 40) / 2.32 = 4.31 pp/bit
- Error+Trace: 52.0% pass@1 → Efficiency = (52 - 40) / 5.64 = 2.13 pp/bit

**Monotonic Decrease:** 8.0 > 4.31 > 2.13 ✓  
**Target Ranges:** Binary ≥7 ✓, Error-Type 4-6 ✓, Error+Trace 2-3 ✓  
**Gate:** PASS

---

**End of PRD**
