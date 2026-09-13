# Experiment Design Brief: h-m1 Capacity Limits Feedback Efficiency

**Date:** 2026-08-19  
**Hypothesis ID:** h-m1  
**Type:** MECHANISM  
**Gate:** MUST_WORK  
**Prerequisites:** h-e1 (COMPLETED)

---

## 1. Hypothesis Statement

Under small model capacity constraints (350M-1B parameters), if we compare feedback efficiency (pass@1 gain per bit) across granularity levels, then efficiency decreases as feedback richness increases (binary > error-type > error+trace), because small models cannot extract actionable gradients from high-dimensional supervision signals and suffer from noise-dominated learning.

**Success Criteria:**
- Monotonic decrease in efficiency: Binary ≥7 pp/bit, Error-type 4-6 pp/bit, Error+trace 2-3 pp/bit
- Statistical significance in pairwise comparisons (binary vs error-type, error-type vs trace)

---

## 2. Experimental Design

### 2.1 Core Methodology

**Approach:** Extend h-e1 experiment with error+trace feedback condition. Train 4 conditions: (1) SFT baseline, (2) Binary GRPO, (3) Error-Type GRPO, (4) Error+Trace GRPO. Compute efficiency = (pass@1 - SFT) / bits-per-problem. Test monotonic decrease.

**Variables:**
- **IV (Independent):** Feedback granularity level
  - Binary: 1.0 bit (pass/fail)
  - Error-Type: 2.3 bits (log₂(5) for 5 error categories)
  - Error+Trace: 5.6 bits (2.3 + 3.3 bits for stack depth buckets)
- **DV (Dependent):** Feedback efficiency (percentage points per bit)
  - Efficiency = (pass@1_condition - pass@1_SFT) / bits_per_problem
- **CV (Control):** Model size, training compute (GPU-hours), base checkpoint, dataset

**Information Content Calculation:**
- Binary: 1.0 bit (2 outcomes: pass/fail)
- Error-Type: log₂(5) = 2.32 bits (5 categories: Pass, TypeError, NameError, ValueError, AssertionError)
- Error+Trace: 2.32 + log₂(10) = 2.32 + 3.32 = 5.64 bits (error type × stack depth 0-9)

### 2.2 Dataset Specification

**Dataset:** HumanEval (STANDARD)
- **Source:** OpenAI HumanEval benchmark (openai/openai_humaneval)
- **Type:** standard (real, established benchmark)
- **Size:** 164 hand-written programming problems
- **Test Coverage:** Comprehensive unit test suites per problem
- **Split:** Full test set (no train/val split needed for RL from execution)
- **Cache:** `./data/humaneval/`

**Justification:**
- Real dataset with established test suites (no synthetic data)
- Same dataset as h-e1 (controls for dataset variability)
- 164 problems = statistically meaningful sample size
- Algorithm-focused problems test model capacity under feedback
- Standard benchmark enables comparison with prior work

**Data Preparation:**
1. Load from HuggingFace Hub (no preprocessing needed)
2. Extract prompts: function signature + docstring
3. Extract test suites: unit tests + entry points
4. Cache locally for offline training

### 2.3 Baseline Experiments

**Experiment Matrix:**

| Condition | Feedback Type | Bits/Problem | Training Method | Checkpoint |
|-----------|---------------|--------------|-----------------|------------|
| SFT | None (supervised) | 0 | Causal LM on canonical solutions | `checkpoints/sft/` |
| Binary | Pass/Fail | 1.0 | GRPO + binary reward | `checkpoints/binary/` |
| Error-Type | 5 error categories | 2.32 | GRPO + error-type reward | `checkpoints/error_type/` |
| Error+Trace | Error × stack depth | 5.64 | GRPO + error+trace reward | `checkpoints/error_trace/` |

**Control Matching:**
- **Model:** CodeGen-350M-mono (primary), StarCoder-1B (fallback if saturation detected)
- **Training Compute:** 500 GRPO steps per condition (matched across Binary/Error-Type/Error+Trace)
- **Base Checkpoint:** Same pretrained weights for all conditions
- **LoRA Config:** r=16, alpha=32 (consistent across conditions)
- **Batch Size:** 8 per condition (memory-matched)

**SFT Baseline:**
- Purpose: Establish "no execution feedback" performance floor
- Training: 5 epochs on (prompt, canonical_solution) pairs
- No test execution during training
- Checkpoint serves as reference model for KL penalty in GRPO

**Binary GRPO:**
- Reward: 1.0 (all tests pass), 0.0 (any test fails)
- Same as h-e1 implementation (reuse code)

**Error-Type GRPO:**
- Reward mapping (5 categories):
  - Pass: 1.0
  - TypeError: 0.3
  - NameError: 0.2
  - ValueError: 0.25
  - AssertionError: 0.4 (closest to correct - failed assertion)
  - OtherError: 0.1 (rare errors - SyntaxError, IndexError, etc.)

**Error+Trace GRPO (NEW for h-m1):**
- Reward = error_type_reward × trace_depth_penalty
- Stack trace depth buckets: [0-9] levels (10 categories)
- Depth extraction: `len(traceback.extract_tb(sys.exc_info()[2]))`
- Trace depth penalty: `1.0 - (depth / 20.0)` (clamped to [0.5, 1.0])
  - Shallow errors (depth 0-2): high penalty (likely simple mistakes)
  - Deep errors (depth 8-9): low penalty (complex call chains)
- Total bits: log₂(5 error types × 10 depth levels) = log₂(50) ≈ 5.64 bits
- Example: TypeError at depth 3 → reward = 0.3 × (1.0 - 3/20) = 0.3 × 0.85 = 0.255

### 2.4 Evaluation Metrics

**Primary Metric: Feedback Efficiency**
- Definition: Efficiency = (pass@1_condition - pass@1_SFT) / bits_per_problem
- Units: Percentage points per bit
- Interpretation: How much performance gain per bit of feedback information
- Expected values:
  - Binary: (48% - 40%) / 1.0 = 8.0 pp/bit (from h-e1 dual threshold)
  - Error-Type: (50% - 40%) / 2.32 = 4.3 pp/bit (assuming 10pp gain)
  - Error+Trace: (52% - 40%) / 5.64 = 2.1 pp/bit (assuming 12pp gain, but 2.4x more bits)

**Secondary Metrics:**

1. **Absolute Performance (pass@1)**
   - Method: Greedy decoding (temperature=0), 1 sample per problem
   - Execution: Run generated code against test suite
   - Aggregation: (# problems passed) / 164

2. **Gradient Variance (learning dynamics)**
   - Logging: Per-batch gradient std across all LoRA parameters
   - Frequency: Every 10 training steps
   - Purpose: Test H-M2 signal concentration hypothesis
   - Expected: Binary/Error-Type < Error+Trace variance

3. **Convergence Rate**
   - Metric: Steps to reach 90% of final eval performance
   - Tracking: Eval loss every 25 steps
   - Purpose: Secondary evidence for H-M2 (faster convergence = concentrated signal)

### 2.5 Implementation Requirements

**Code Modifications from h-e1:**

1. **New Sandbox Method: `compute_error_trace_reward()`**
   - Extract stack trace depth on exception
   - Bucket depth into [0-9] levels
   - Compute combined reward: error_type × depth_penalty
   - Return float in [0.0, 1.0]

2. **GRPO Trainer Extension: Error+Trace Condition**
   - New training loop: `train_grpo_error_trace()`
   - Use `sandbox.compute_error_trace_reward()` instead of binary/error-type
   - Same GRPO algorithm (policy gradient + KL penalty)
   - Log gradient variance per batch

3. **Evaluation Pipeline: Efficiency Computation**
   - Load 4 checkpoints: SFT, Binary, Error-Type, Error+Trace
   - Compute pass@1 for each
   - Calculate efficiency: (pass@1 - SFT) / bits
   - Statistical test: Pairwise t-tests with Bonferroni correction (α=0.0167)

4. **Logging Enhancements**
   - Track gradient variance: `grad_var = torch.std(torch.cat([p.grad.flatten() for p in lora_params]))`
   - Log per-batch variance to CSV
   - Compute mean variance over training for each condition

**New Files:**
- `code/sandbox_trace.py`: Extended sandbox with trace depth extraction
- `code/train_error_trace.py`: GRPO trainer for error+trace condition
- `code/analysis_efficiency.py`: Efficiency frontier plotting + stats

**Reused from h-e1:**
- `dataset.py`, `model.py`, `eval.py` (no changes)
- `sandbox.py` (extend, not replace)
- `train.py` (add new trainer, keep existing)

---

## 3. Success Criteria & Gates

### 3.1 MUST_WORK Gate Conditions

**Condition 1: Monotonic Efficiency Decrease**
- Binary efficiency > Error-Type efficiency
- Error-Type efficiency > Error+Trace efficiency
- Statistical test: One-sided t-tests (p < 0.0167 after Bonferroni)

**Condition 2: Target Efficiency Ranges**
- Binary: ≥7 pp/bit
- Error-Type: 4-6 pp/bit
- Error+Trace: 2-3 pp/bit

**Gate Logic:**
```
IF (binary_eff > error_type_eff > error_trace_eff) AND
   (binary_eff >= 7.0) AND
   (error_type_eff in [4.0, 6.0]) AND
   (error_trace_eff in [2.0, 3.0]) AND
   (all pairwise tests p < 0.0167)
THEN
   gate = PASS
ELSE
   gate = FAIL → Capacity constraint mechanism invalid
```

### 3.2 Failure Interpretation

**If Gate Fails:**
- Capacity constraint hypothesis refuted
- Richer feedback may be equally/more efficient for small models
- Challenges efficiency frontier claim
- Does NOT block Phase 5 baseline comparison (MUST_WORK gate)
- Requires re-evaluation of main hypothesis rationale

**Possible Failure Modes:**
1. **Flat efficiency:** All conditions similar efficiency → semantic value matters more than entropy
2. **Reversed order:** Error+Trace > Binary → rich feedback extracts more value despite noise
3. **Below targets:** Binary < 7 pp/bit → h-e1 didn't achieve strong enough gains

---

## 4. Resource Requirements

### 4.1 Computational Budget

**Training Time:**
- SFT: 5 epochs × 164 problems × 8 batch = ~100 steps → 0.5 GPU-hours
- Binary GRPO: 500 steps × 8 batch → 2.0 GPU-hours (from h-e1)
- Error-Type GRPO: 500 steps × 8 batch → 2.0 GPU-hours (from h-e1)
- Error+Trace GRPO: 500 steps × 8 batch → 2.0 GPU-hours (same compute)

**Total:** 6.5 GPU-hours for 1 model size (CodeGen-350M)

**Evaluation Time:**
- 4 checkpoints × 164 problems × greedy decode → 0.5 GPU-hours

**Total Experiment:** 7 GPU-hours (within h-e1 budget, reuses SFT/Binary/Error-Type checkpoints)

### 4.2 Hardware Requirements

**GPU:** NVIDIA H100 NVL (verified available from h-e1)
- VRAM: 80 GB (CodeGen-350M + LoRA fits in <10 GB)
- Precision: FP16 mixed precision

**Storage:**
- Checkpoints: 4 conditions × 1 GB = 4 GB
- Dataset cache: 0.1 GB (HumanEval)
- Logs: 0.5 GB (gradient variance CSV)

**Total:** 5 GB storage

### 4.3 Software Dependencies

**Reuse from h-e1:**
- `transformers==4.46.3` (model loading)
- `trl==0.13.0` (GRPO trainer)
- `peft==0.15.0` (LoRA)
- `datasets==3.2.0` (HumanEval)
- `torch==2.5.1` (GPU compute)
- `matplotlib==3.10.0` (plotting)

**No new dependencies** (all features achievable with existing stack)

---

## 5. Validation Plan

### 5.1 Static Analysis Checks

**Code Quality:**
- Error+trace reward function returns float in [0.0, 1.0]
- Stack depth extraction handles all exception types
- Gradient variance logging doesn't crash training loop
- Efficiency calculation handles division by zero (SFT baseline)

**Configuration Validation:**
- All 4 conditions use same base model
- Same number of GRPO steps (500)
- Same LoRA config (r=16, alpha=32)
- Same batch size (8)

### 5.2 Runtime Validation

**Sanity Checks:**
1. Error+trace rewards span expected range [0.0, 1.0]
2. Stack depth buckets populated (not all depth=0)
3. Gradient variance logged every batch (no missing data)
4. All 4 checkpoints save successfully

**Smoke Test:**
- Run 10 GRPO steps for error+trace condition
- Verify reward computation executes without crash
- Check gradient variance logs populate

### 5.3 Statistical Validation

**Pairwise Comparisons:**
- Binary vs Error-Type: t-test on efficiency
- Error-Type vs Error+Trace: t-test on efficiency
- Binary vs Error+Trace: t-test on efficiency (redundant check)

**Multiple Testing Correction:**
- Bonferroni correction: α = 0.05 / 3 = 0.0167
- Require p < 0.0167 for each pairwise test

**Robustness Checks:**
- Bootstrap confidence intervals (1000 samples) on efficiency
- Check if CI overlap contradicts t-test results

---

## 6. Expected Outcomes & Interpretation

### 6.1 PASS Scenario (Gate Satisfied)

**Expected Results:**
- Binary: 8.0 pp/bit (8pp gain from h-e1 / 1 bit)
- Error-Type: 4.3 pp/bit (10pp gain / 2.32 bits)
- Error+Trace: 2.1 pp/bit (12pp gain / 5.64 bits)

**Interpretation:**
- Capacity constraint mechanism confirmed
- Small models (350M) efficiently use low-dimensional feedback
- High-dimensional feedback (trace depth) adds minimal value
- Supports efficiency frontier hypothesis

**Next Steps:**
- Proceed to H-M2 (signal concentration mechanism)
- Use efficiency frontier as design principle for Phase 5 baseline

### 6.2 FAIL Scenario (Gate Not Satisfied)

**Possible Outcomes:**

1. **Flat efficiency (all ~5 pp/bit):**
   - Semantic value dominates entropy
   - Bit-counting invalid proxy for information content
   - Revise information-theoretic framework

2. **Reversed order (Error+Trace > Binary):**
   - Rich feedback provides non-obvious value
   - Stack traces contain actionable debugging hints
   - Small models CAN utilize high-dimensional signals

3. **All below targets:**
   - h-e1 gains insufficient for efficiency calculation
   - Absolute performance too low
   - Model capacity or training compute insufficient

**Mitigation:**
- Analyze per-problem efficiency variance
- Stratify by error type frequency (detect skew)
- Check gradient variance correlation with efficiency

---

## 7. Risks & Mitigations

### 7.1 Critical Risks

**R1: Error Distribution Skew**
- **Risk:** If 90% errors are TypeError, error-type degenerates to near-binary (2.3 → 0.5 bits effective entropy)
- **Impact:** Underestimates error-type efficiency, distorts comparison
- **Mitigation:** Log error type frequencies from training. Compute effective entropy: H = -Σ p(i) log₂ p(i). Re-calculate efficiency with effective bits.
- **Detection:** Frequency table in validation report

**R2: Stack Trace Depth Saturation**
- **Risk:** Most errors at depth 0-1 (top-level failures), trace depth adds <1 bit effective information
- **Impact:** Error+trace bits overstated (5.64 → 3.0 bits)
- **Mitigation:** Histogram stack depths. Compute effective entropy of depth distribution.
- **Detection:** Depth histogram in validation report

**R3: Gradient Variance Noise**
- **Risk:** Per-batch variance high noise (batch size 8), obscures signal
- **Impact:** H-M2 secondary evidence inconclusive
- **Mitigation:** Moving average (window=20 batches). Report mean variance over full training.
- **Acceptance:** Gradient variance is secondary metric (H-M2 has separate experiment)

### 7.2 Secondary Risks

**R4: Checkpoint Reuse Invalidation**
- **Risk:** h-e1 checkpoints corrupted or incompatible
- **Impact:** Must re-train SFT/Binary/Error-Type (+4 GPU-hours)
- **Probability:** Low (h-e1 completed successfully)
- **Mitigation:** Verify checkpoint loading in smoke test

**R5: HumanEval Download Failure**
- **Risk:** HuggingFace Hub unavailable
- **Impact:** Cannot load dataset
- **Probability:** Low (cached from h-e1)
- **Mitigation:** Use h-e1 cached dataset

---

## 8. Timeline & Milestones

**Phase 3 (Implementation Planning):** 2 days
- Day 1: Generate PRD, Architecture, Logic docs
- Day 2: Create Archon task breakdown, initialize project

**Phase 4 (PoC Implementation):** 3 days
- Day 1: Implement error+trace sandbox, smoke test
- Day 2: Train Error+Trace GRPO (2 GPU-hours)
- Day 3: Evaluate 4 conditions, compute efficiency, validate gate

**Total:** 5 days (Phase 2C → Phase 4)

---

## 9. Outputs & Deliverables

### 9.1 Code Artifacts

**New Files:**
- `h-m1/code/sandbox_trace.py`: Error+trace reward computation
- `h-m1/code/train_error_trace.py`: GRPO trainer for error+trace
- `h-m1/code/analysis_efficiency.py`: Efficiency frontier analysis

**Modified Files:**
- `h-m1/code/run_experiment.py`: Orchestrate 4-condition training

### 9.2 Data Artifacts

**Checkpoints:**
- `checkpoints/sft/` (reused from h-e1)
- `checkpoints/binary/` (reused from h-e1)
- `checkpoints/error_type/` (reused from h-e1)
- `checkpoints/error_trace/` (NEW)

**Logs:**
- `logs/gradient_variance.csv`: Per-batch variance for all conditions
- `logs/efficiency_metrics.json`: Final efficiency values + stats

### 9.3 Visualizations

**Mandatory:**
- `efficiency_frontier.png`: Bar chart (3 bars: Binary, Error-Type, Error+Trace efficiency)
  - X-axis: Feedback granularity
  - Y-axis: Efficiency (pp/bit)
  - Error bars: Bootstrap 95% CI
  - Horizontal lines: Target thresholds (7, 5, 2.5)

**Optional:**
- `gradient_variance_curves.png`: Line plot of variance over training steps
- `error_distribution.png`: Histogram of error types + stack depths

### 9.4 Reports

**04_validation.md:**
- Section 1: Efficiency frontier results (table + plot)
- Section 2: Statistical tests (pairwise t-tests, p-values)
- Section 3: Gate verdict (PASS/FAIL with logic)
- Section 4: Risk analysis (error skew, depth saturation)
- Section 5: Gradient variance secondary findings
- Section 6: Interpretation (mechanism confirmed or refuted)

---

## 10. Implementation Notes

### 10.1 Stack Trace Depth Extraction

**Python Implementation:**
```python
import sys
import traceback

def extract_stack_depth(exc_info):
    """Extract stack trace depth from exception."""
    tb = exc_info[2]  # Traceback object
    if tb is None:
        return 0
    depth = len(traceback.extract_tb(tb))
    return min(depth, 9)  # Clamp to [0-9]
```

**Edge Cases:**
- SyntaxError: No traceback (depth=0)
- Top-level exceptions: depth=1
- Recursive calls: depth capped at 9

### 10.2 Reward Computation Formula

**Error+Trace Reward:**
```python
def compute_error_trace_reward(code, test, entry_point):
    try:
        exec_program(code, test, entry_point)
        return 1.0  # Pass
    except Exception as e:
        error_type_reward = get_error_type_reward(type(e).__name__)
        depth = extract_stack_depth(sys.exc_info())
        depth_penalty = 1.0 - (depth / 20.0)
        depth_penalty = max(0.5, depth_penalty)  # Clamp to [0.5, 1.0]
        return error_type_reward * depth_penalty
```

**Example Calculations:**
- TypeError at depth 0: 0.3 × 1.0 = 0.30
- TypeError at depth 3: 0.3 × 0.85 = 0.255
- AssertionError at depth 1: 0.4 × 0.95 = 0.38
- NameError at depth 9: 0.2 × 0.55 = 0.11

### 10.3 Efficiency Calculation

**Python Implementation:**
```python
def compute_efficiency(pass_at_1, sft_baseline, bits_per_problem):
    """Compute feedback efficiency in pp/bit."""
    gain = (pass_at_1 - sft_baseline) * 100  # Convert to percentage points
    if bits_per_problem == 0:
        return float('inf')  # SFT has no feedback
    return gain / bits_per_problem
```

**Example:**
- Binary: (0.48 - 0.40) × 100 / 1.0 = 8.0 pp/bit
- Error-Type: (0.50 - 0.40) × 100 / 2.32 = 4.31 pp/bit
- Error+Trace: (0.52 - 0.40) × 100 / 5.64 = 2.13 pp/bit

---

## 11. Connection to Other Hypotheses

**Prerequisite: h-e1 (COMPLETED)**
- Provides SFT, Binary, Error-Type checkpoints
- Establishes baseline performance levels
- Validates dual-threshold sufficiency (≥8pp gain for Binary)

**Enables: h-m2 (Signal Concentration)**
- Gradient variance logs from h-m1 provide secondary evidence
- Efficiency frontier shapes H-M2 convergence predictions
- Shared codebase (same training loops)

**Informs: h-m3 (Coverage Moderation)**
- If h-m1 PASS: Coverage correlation may explain efficiency differences
- If h-m1 FAIL: Coverage less likely to be primary moderator

---

## 12. Summary

**Experiment Type:** Mechanism validation (MUST_WORK gate)

**Core Question:** Does feedback efficiency decrease monotonically as granularity increases?

**Key Innovation:** Error+trace feedback (5.64 bits) extends h-e1's binary/error-type comparison to test capacity constraint hypothesis.

**Resource Efficiency:** Reuses h-e1 checkpoints, adds only 2 GPU-hours for error+trace training.

**Statistical Rigor:** Pairwise t-tests with Bonferroni correction, bootstrap CI, robustness checks for error distribution skew.

**Success Metric:** Monotonic efficiency decrease with target ranges (Binary ≥7, Error-Type 4-6, Error+Trace 2-3 pp/bit).

**Deliverable:** Efficiency frontier plot, statistical validation, gate verdict in 04_validation.md.

---

**End of Experiment Design Brief**
