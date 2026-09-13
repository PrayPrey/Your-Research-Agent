# Experiment Brief: h-m2 Low-Granularity Feedback Signal Concentration

**Date:** 2026-08-19  
**Hypothesis ID:** h-m2  
**Type:** MECHANISM  
**Gate:** MUST_WORK  
**Prerequisites:** h-e1 (COMPLETED)  

---

## 1. Hypothesis Statement

**Full Statement:**  
Low-granularity feedback concentrates learning signal with reduced noise: binary and error-type feedback show monotonically decreasing efficiency (gain-per-bit) as information budget increases, validating diminishing returns hypothesis.

**Testable Claim:**  
Under small model capacity constraints (350M-1B parameters), if we analyze learning dynamics during training with different feedback granularity levels, then low-granularity feedback (binary, error-type) shows faster convergence and lower gradient variance compared to high-granularity feedback (error+trace), because concentrated supervision signals have higher signal-to-noise ratio in gradient updates.

**Success Criteria (from 02b_verification_plan.md):**
1. **Convergence Speed:** Binary and error-type show ≥20% faster convergence (epochs to 90% of final performance) than error+trace
2. **Gradient Variance:** Binary and error-type show ≥30% lower gradient variance than error+trace

---

## 2. Experimental Design

### 2.1 Overview

Extend h-e1 training pipeline with **training dynamics logging** to measure convergence rates and gradient variance across three feedback conditions:

1. **Binary feedback** (1 bit): pass/fail
2. **Error-type feedback** (2.3 bits): 5-category Python exceptions
3. **Error+trace feedback** (5.6 bits): error-type + stack trace depth buckets (10 levels)

**Key Addition:** Per-epoch eval loss tracking + per-batch gradient statistics logging during GRPO training.

### 2.2 Dataset & Models (Reuse from h-e1)

**Dataset:**
- Primary: HumanEval (164 problems, standard split)
- Type: `standard` (real dataset, not synthetic)
- Cache: `/home/PrayPrey/.cache/huggingface/datasets/openai_humaneval`
- Verified: Full test suites available, branch coverage pre-computed

**Models:**
- CodeGen-350M-mono (Salesforce)
- StarCoder-1B (BigCode)
- Both models: LoRA (r=16, alpha=32), fp16 precision

**Rationale:** Reuse h-e1 infrastructure to isolate training dynamics measurement from implementation variability.

### 2.3 Feedback Signal Design

#### Binary Feedback (1 bit)
```python
def compute_binary_reward(code: str, test_suite: str) -> float:
    result = execute_with_timeout(code, test_suite, timeout=3.0)
    return 1.0 if result.all_passed else 0.0
```

#### Error-Type Feedback (2.3 bits)
```python
ERROR_TYPES = ["SyntaxError", "TypeError", "NameError", "IndexError", "ValueError"]

def compute_error_type_reward(code: str, test_suite: str) -> float:
    result = execute_with_timeout(code, test_suite, timeout=3.0)
    if result.all_passed:
        return 1.0
    # Map error type to reward in [0, 1)
    if result.error_type in ERROR_TYPES:
        idx = ERROR_TYPES.index(result.error_type)
        return 0.2 + (idx * 0.15)  # 0.2, 0.35, 0.5, 0.65, 0.8
    return 0.0  # Unknown error type
```

Entropy: log₂(5) ≈ 2.3 bits for 5 error categories

#### Error+Trace Feedback (5.6 bits) — NEW
```python
STACK_DEPTH_BUCKETS = [0, 1, 2, 3, 5, 10, 20, 50, 100, 200, float('inf')]  # 10 buckets

def compute_error_trace_reward(code: str, test_suite: str) -> float:
    result = execute_with_timeout(code, test_suite, timeout=3.0)
    if result.all_passed:
        return 1.0
    
    # Error-type component (2.3 bits)
    error_reward = 0.0
    if result.error_type in ERROR_TYPES:
        idx = ERROR_TYPES.index(result.error_type)
        error_reward = 0.15 * idx  # 0.0 to 0.6
    
    # Stack trace depth component (3.3 bits for 10 buckets)
    depth = len(result.traceback.split('\n')) if result.traceback else 0
    bucket_idx = bisect.bisect_right(STACK_DEPTH_BUCKETS, depth) - 1
    depth_reward = 0.05 * bucket_idx  # 0.0 to 0.45
    
    return error_reward + depth_reward  # Total range [0.0, 1.0)
```

Entropy: log₂(5) + log₂(10) ≈ 2.3 + 3.3 = 5.6 bits

**Information Budget:**
- Binary: 1.0 bit/problem
- Error-type: 2.3 bits/problem  
- Error+trace: 5.6 bits/problem

### 2.4 Training Protocol

**Baseline (Reuse from h-e1):**
- SFT on (prompt, canonical_solution) pairs
- 3 epochs, batch_size=8, lr=2e-5
- No execution feedback

**GRPO Training (All three conditions):**
- Group size G=8 (8 rollouts per prompt)
- Epochs: 5 (sufficient to reach convergence based on h-e1)
- Batch size: 8 prompts (64 total rollouts per batch)
- Learning rate: 5e-6
- KL penalty: β=0.04
- Clip parameter: ε=0.2
- Gradient accumulation: 2 steps
- Max generation length: 512 tokens

**Control Variables:**
- Same random seed (42) across conditions
- Same GPU hours per condition (compute-matched)
- Same number of gradient steps (500 steps × 5 epochs = 2500 total)
- Same LoRA configuration (r=16, alpha=32)

### 2.5 Metrics Collection — CRITICAL

#### Convergence Metrics (Per-Epoch)

**Primary Metric: Epochs to 90% Plateau**
```python
def compute_convergence_epochs(eval_losses: List[float]) -> float:
    """
    Compute epochs required to reach 90% of final performance.
    
    Final performance = eval_loss at epoch 5
    90% target = final_loss + 0.1 * (initial_loss - final_loss)
    
    Returns: first epoch where eval_loss ≤ 90% target
    """
    final_loss = eval_losses[-1]
    initial_loss = eval_losses[0]
    threshold = final_loss + 0.1 * (initial_loss - final_loss)
    
    for epoch, loss in enumerate(eval_losses):
        if loss <= threshold:
            return epoch + 1  # 1-indexed epochs
    return len(eval_losses)  # Never reached threshold
```

**Collection Protocol:**
- Run evaluation on full HumanEval test set after each epoch
- Compute eval loss (cross-entropy on held-out generations)
- Log: epoch, eval_loss, eval_reward_mean, eval_pass@1
- Store in `training_dynamics_{condition}.json`

#### Gradient Variance Metrics (Per-Batch)

**Primary Metric: Mean Parameter Gradient Std**
```python
def compute_gradient_variance(model: nn.Module) -> float:
    """
    Compute mean standard deviation of gradients across all LoRA parameters.
    
    Called after loss.backward(), before optimizer.step().
    """
    grad_stds = []
    for name, param in model.named_parameters():
        if param.requires_grad and param.grad is not None:
            grad_stds.append(param.grad.std().item())
    
    return np.mean(grad_stds)  # Mean std across all parameters
```

**Collection Protocol:**
- Log gradient variance every batch (not just epoch end)
- Compute variance BEFORE gradient clipping
- Store: step, batch_idx, grad_variance, grad_norm
- Aggregate per-epoch: mean, std, min, max of batch-level variances

**Secondary Metrics:**
- Gradient norm (L2 norm of full gradient vector)
- Reward variance per group (std of 8 rollout rewards)
- KL divergence from reference model

### 2.6 Logging Infrastructure

**File Structure:**
```
h-m2/
├── logs/
│   ├── binary_350m_dynamics.json          # Per-batch + per-epoch metrics
│   ├── error_type_350m_dynamics.json
│   ├── error_trace_350m_dynamics.json
│   ├── binary_1b_dynamics.json
│   ├── error_type_1b_dynamics.json
│   └── error_trace_1b_dynamics.json
└── checkpoints/
    ├── binary_350m_epoch{1-5}.pt
    ├── error_type_350m_epoch{1-5}.pt
    └── error_trace_350m_epoch{1-5}.pt
```

**JSON Schema:**
```json
{
  "experiment_id": "h-m2_binary_350m",
  "feedback_type": "binary",
  "model_size": "350M",
  "epochs": [
    {
      "epoch": 1,
      "eval_loss": 2.145,
      "eval_reward_mean": 0.234,
      "eval_pass@1": 0.152,
      "batches": [
        {
          "step": 1,
          "grad_variance": 0.0042,
          "grad_norm": 1.23,
          "reward_variance": 0.156,
          "kl_divergence": 0.012
        }
      ]
    }
  ],
  "convergence_epochs": 3.2,
  "mean_grad_variance": 0.0038
}
```

### 2.7 Analysis Protocol

**Step 1: Convergence Comparison**
```python
# For each model size (350M, 1B):
epochs_binary = compute_convergence_epochs(binary_eval_losses)
epochs_error_type = compute_convergence_epochs(error_type_eval_losses)
epochs_error_trace = compute_convergence_epochs(error_trace_eval_losses)

# Success criterion: binary and error-type ≥20% faster than error+trace
speedup_binary = (epochs_error_trace - epochs_binary) / epochs_error_trace
speedup_error_type = (epochs_error_trace - epochs_error_type) / epochs_error_trace

assert speedup_binary >= 0.20, f"Binary speedup {speedup_binary:.2%} < 20%"
assert speedup_error_type >= 0.20, f"Error-type speedup {speedup_error_type:.2%} < 20%"
```

**Step 2: Gradient Variance Comparison**
```python
# Aggregate gradient variance across all batches (post-warmup)
# Skip first 20% of steps (warmup period)
def aggregate_gradient_variance(dynamics: dict) -> float:
    all_variances = []
    for epoch in dynamics['epochs']:
        batches = epoch['batches'][int(len(epoch['batches']) * 0.2):]  # Skip warmup
        all_variances.extend([b['grad_variance'] for b in batches])
    return np.mean(all_variances)

variance_binary = aggregate_gradient_variance(binary_dynamics)
variance_error_type = aggregate_gradient_variance(error_type_dynamics)
variance_error_trace = aggregate_gradient_variance(error_trace_dynamics)

# Success criterion: binary and error-type ≥30% lower variance than error+trace
reduction_binary = (variance_error_trace - variance_binary) / variance_error_trace
reduction_error_type = (variance_error_trace - variance_error_type) / variance_error_trace

assert reduction_binary >= 0.30, f"Binary variance reduction {reduction_binary:.2%} < 30%"
assert reduction_error_type >= 0.30, f"Error-type variance reduction {reduction_error_type:.2%} < 30%"
```

**Step 3: Statistical Significance**
- Two-sample t-test: binary vs error+trace convergence epochs
- Two-sample t-test: error-type vs error+trace gradient variance
- Bonferroni correction: α = 0.0167 (0.05 / 3 comparisons)
- Report: t-statistic, p-value, effect size (Cohen's d)

### 2.8 Visualization

**Mandatory Figures:**

1. **Learning Curves (convergence_curves.png)**
   - X-axis: Epoch (0-5)
   - Y-axis: Eval loss
   - 3 lines: Binary (blue), Error-type (green), Error+trace (red)
   - Horizontal dashed line: 90% plateau threshold
   - Vertical markers: convergence epoch for each condition
   - Separate subplots for 350M and 1B models

2. **Gradient Variance Trajectories (gradient_variance.png)**
   - X-axis: Training step (0-2500)
   - Y-axis: Batch gradient variance (log scale)
   - 3 lines: Binary, Error-type, Error+trace
   - Shaded regions: ±1 std across batches within epoch
   - Separate subplots for 350M and 1B models

3. **Gate Metrics Bar Chart (gate_metrics.png)**
   - 4 bars: Binary convergence speedup, Error-type convergence speedup, Binary variance reduction, Error-type variance reduction
   - Horizontal line: Success threshold (20% for convergence, 30% for variance)
   - Error bars: 95% confidence intervals (bootstrapped)

**Optional Figures:**
- Reward distribution histograms per feedback type
- KL divergence trajectories
- Pass@1 evolution over epochs

---

## 3. Implementation Plan

### 3.1 Code Reuse from h-e1

**Reusable Components (No Changes):**
- `dataset.py`: HumanEval loader
- `model.py`: Model manager with LoRA
- `sandbox.py`: Code execution sandbox
- `eval.py`: Pass@1 evaluation

**Modified Components:**

**`train.py` — Add Dynamics Logging**
```python
class GRPOTrainerWithDynamics(GRPOTrainer):
    def __init__(self, *args, dynamics_logger, **kwargs):
        super().__init__(*args, **kwargs)
        self.dynamics_logger = dynamics_logger
    
    def training_step(self, model, inputs):
        # Standard GRPO step
        loss = super().training_step(model, inputs)
        
        # Log gradient variance BEFORE optimizer.step()
        grad_variance = compute_gradient_variance(model)
        grad_norm = compute_gradient_norm(model)
        reward_variance = inputs['rewards'].std().item()
        kl_div = self.compute_kl_divergence(model, inputs)
        
        self.dynamics_logger.log_batch({
            'step': self.state.global_step,
            'grad_variance': grad_variance,
            'grad_norm': grad_norm,
            'reward_variance': reward_variance,
            'kl_divergence': kl_div
        })
        
        return loss
    
    def evaluation_loop(self, dataloader):
        # Run full HumanEval evaluation
        eval_loss = super().evaluation_loop(dataloader)
        eval_reward, eval_pass_at_1 = self.evaluate_humaneval()
        
        self.dynamics_logger.log_epoch({
            'epoch': self.state.epoch,
            'eval_loss': eval_loss,
            'eval_reward_mean': eval_reward,
            'eval_pass@1': eval_pass_at_1
        })
        
        return eval_loss
```

**New Component: `dynamics_logger.py`**
```python
class DynamicsLogger:
    def __init__(self, output_path: str, experiment_id: str):
        self.output_path = output_path
        self.data = {
            'experiment_id': experiment_id,
            'epochs': []
        }
        self.current_epoch = {'batches': []}
    
    def log_batch(self, metrics: dict):
        self.current_epoch['batches'].append(metrics)
    
    def log_epoch(self, metrics: dict):
        self.current_epoch.update(metrics)
        self.data['epochs'].append(self.current_epoch)
        self.current_epoch = {'batches': []}
        self.save()
    
    def save(self):
        with open(self.output_path, 'w') as f:
            json.dump(self.data, f, indent=2)
```

**New Component: `rewards.py` — Error+Trace Reward**
```python
def compute_error_trace_reward(code: str, test_suite: str, 
                                error_types: List[str], 
                                depth_buckets: List[float]) -> float:
    """Compute 5.6-bit reward from error type + stack trace depth."""
    result = execute_with_timeout(code, test_suite, timeout=3.0)
    
    if result.all_passed:
        return 1.0
    
    # Error-type component (2.3 bits)
    error_reward = 0.0
    if result.error_type in error_types:
        idx = error_types.index(result.error_type)
        error_reward = 0.15 * idx
    
    # Stack trace depth component (3.3 bits)
    depth = len(result.traceback.split('\n')) if result.traceback else 0
    bucket_idx = bisect.bisect_right(depth_buckets, depth) - 1
    depth_reward = 0.05 * bucket_idx
    
    return error_reward + depth_reward
```

### 3.2 Experiment Execution Workflow

**Phase 1: Training (18 hours total, 6 models × 3 hours each)**

For each model size (350M, 1B):
1. Train Binary GRPO with dynamics logging
2. Train Error-Type GRPO with dynamics logging
3. Train Error+Trace GRPO with dynamics logging

**Phase 2: Analysis (2 hours)**

1. Compute convergence epochs from eval_loss trajectories
2. Aggregate gradient variance across batches
3. Run statistical tests (t-tests with Bonferroni correction)
4. Generate visualizations (3 mandatory figures)

**Phase 3: Validation (1 hour)**

1. Check gate criteria (convergence ≥20% faster, variance ≥30% lower)
2. Generate 04_validation.md report
3. Update verification_state.yaml

**Total Duration:** 21 hours (within 24-hour budget)

### 3.3 Resource Requirements

**Compute:**
- Single GPU: NVIDIA H100 NVL (80GB VRAM) — Available
- Training time: 3 hours × 6 models = 18 GPU-hours
- Memory: LoRA + fp16 keeps models under 8GB VRAM

**Storage:**
- Checkpoints: 6 models × 5 epochs × 500MB = 15GB
- Logs: 6 dynamics JSON files × 50MB = 300MB
- Total: ~16GB

**Dependencies (from h-e1):**
- transformers==4.50.0
- trl==0.15.1
- peft==0.14.0
- datasets==3.2.0
- torch==2.5.0

---

## 4. Success Criteria & Gate Logic

### 4.1 MUST_WORK Gate Conditions

**Convergence Criterion:**
```python
# For BOTH model sizes (350M, 1B):
binary_speedup = (epochs_trace - epochs_binary) / epochs_trace >= 0.20
error_type_speedup = (epochs_trace - epochs_error_type) / epochs_trace >= 0.20

convergence_pass = binary_speedup and error_type_speedup
```

**Gradient Variance Criterion:**
```python
# For BOTH model sizes (350M, 1B):
binary_reduction = (variance_trace - variance_binary) / variance_trace >= 0.30
error_type_reduction = (variance_trace - variance_error_type) / variance_trace >= 0.30

variance_pass = binary_reduction and error_type_reduction
```

**Gate Result:**
```python
if convergence_pass and variance_pass:
    gate_result = "PASS"
    # Mechanism hypothesis confirmed
    # Proceed to h-m3 (coverage moderation)
else:
    gate_result = "FAIL"
    # Signal concentration mechanism invalid
    # Challenge noise-reduction rationale for lightweight feedback
```

### 4.2 Reporting Format

**04_validation.md Structure:**
```markdown
# Validation Report: h-m2

## Gate Result: PASS / FAIL

## Convergence Metrics

| Model | Binary (epochs) | Error-Type (epochs) | Error+Trace (epochs) | Binary Speedup | Error-Type Speedup |
|-------|-----------------|---------------------|----------------------|----------------|---------------------|
| 350M  | 2.8             | 3.1                 | 4.2                  | 33.3%          | 26.2%               |
| 1B    | 2.5             | 2.9                 | 3.8                  | 34.2%          | 23.7%               |

**Success Threshold:** ≥20% speedup  
**Result:** PASS (both models exceed 20%)

## Gradient Variance Metrics

| Model | Binary (std) | Error-Type (std) | Error+Trace (std) | Binary Reduction | Error-Type Reduction |
|-------|--------------|------------------|-------------------|------------------|----------------------|
| 350M  | 0.0034       | 0.0041           | 0.0062            | 45.2%            | 33.9%                |
| 1B    | 0.0029       | 0.0038           | 0.0058            | 50.0%            | 34.5%                |

**Success Threshold:** ≥30% reduction  
**Result:** PASS (all conditions exceed 30%)

## Statistical Tests

- Binary vs Error+Trace convergence: t=-4.23, p=0.003, d=1.89 (significant)
- Error-Type vs Error+Trace variance: t=-3.87, p=0.007, d=1.64 (significant)

## Key Findings

1. Low-granularity feedback (binary, error-type) converges 25-35% faster than high-granularity (error+trace)
2. Gradient variance reduced by 35-50% with low-granularity feedback
3. Effect consistent across both model sizes (350M, 1B)
4. Mechanism: Signal concentration reduces noise in gradient updates

## Next Steps

Gate PASSED → Proceed to h-m3 (coverage moderation hypothesis)
```

---

## 5. Risk Mitigation

### 5.1 Identified Risks

**R1: Gradient Variance Measurement Noise**
- **Risk:** Per-batch variance highly stochastic, may not converge
- **Mitigation:** Aggregate over 2000+ batches, skip warmup period (first 20%)
- **Fallback:** Use smoothed variance (EMA with α=0.9)

**R2: Convergence Detection Failure**
- **Risk:** Eval loss never reaches 90% plateau (early stopping)
- **Mitigation:** Increase epochs from 5 to 7 if plateau not reached by epoch 5
- **Fallback:** Use "epochs to 80% plateau" as secondary metric

**R3: Error+Trace Reward Signal Too Weak**
- **Risk:** Stack trace depth provides minimal additional information
- **Mitigation:** Validate depth buckets on h-e1 error logs (check distribution)
- **Fallback:** Replace depth buckets with line number buckets if depth uninformative

**R4: Statistical Power Insufficient**
- **Risk:** Only 2 models (350M, 1B) may lack power for t-tests
- **Mitigation:** Run 3 seeds per condition (6 data points total)
- **Fallback:** Use paired t-test (within-model comparison)

### 5.2 Abort Conditions

**Abort Experiment If:**
1. Binary feedback shows SLOWER convergence than error+trace (inverted effect)
2. Gradient variance increases monotonically (optimization instability)
3. Eval loss diverges after epoch 3 (training collapse)

**Abort Action:** Report FAIL, document anomaly, request hypothesis revision

---

## 6. Validation Checklist

**Pre-Experiment:**
- [ ] h-e1 completed with PASS result (prerequisite)
- [ ] HumanEval dataset cached and verified
- [ ] GPU availability confirmed (H100 NVL)
- [ ] Error+trace reward function tested on sample problems

**During Training:**
- [ ] Dynamics logging functional (JSON files updating per batch)
- [ ] Eval loss decreasing monotonically (no divergence)
- [ ] Gradient variance stable (no exponential growth)
- [ ] Checkpoint saving every epoch

**Post-Training:**
- [ ] All 6 models trained to completion (no crashes)
- [ ] Dynamics JSON files valid (parseable, no missing fields)
- [ ] Convergence epochs computable (90% plateau reached)
- [ ] Gradient variance aggregated (no NaN values)

**Analysis:**
- [ ] Statistical tests run (p-values < 0.0167 for significance)
- [ ] Visualizations generated (3 mandatory figures)
- [ ] Gate criteria checked (convergence ≥20%, variance ≥30%)

**Reporting:**
- [ ] 04_validation.md written with gate result
- [ ] verification_state.yaml updated
- [ ] Figures committed to h-m2/ directory

---

## 7. Appendix

### A. Information Budget Calculation

**Binary Feedback:**
- Outcome space: {pass, fail}
- Entropy: log₂(2) = 1.0 bit

**Error-Type Feedback:**
- Outcome space: {pass, SyntaxError, TypeError, NameError, IndexError, ValueError}
- Assuming uniform distribution: log₂(6) ≈ 2.58 bits
- Adjusted for natural distribution (TypeError 40%, others 15% each): H ≈ 2.3 bits

**Error+Trace Feedback:**
- Outcome space: 6 error types × 10 depth buckets = 60 states
- Error component: 2.3 bits
- Depth component: log₂(10) ≈ 3.3 bits
- Total: 2.3 + 3.3 = 5.6 bits

### B. Gradient Variance Computation Details

**Why Mean Std Across Parameters:**
- Alternative: Variance of full gradient vector (single scalar)
- Problem: Scales with model size, not comparable across 350M and 1B
- Solution: Per-parameter std, then average (size-invariant)

**Why Skip Warmup:**
- First 20% of training has high variance due to policy initialization
- Warmup distorts comparison between conditions
- Post-warmup variance more stable and representative

### C. Convergence Metric Justification

**Why 90% Plateau (Not 95% or 99%):**
- 95%: Too strict, small noise can delay convergence epoch
- 90%: Standard in RL literature (GRPO papers, PPO benchmarks)
- 99%: Overfits to final noisy fluctuations

**Why Eval Loss (Not Reward):**
- Reward is binary (0/1) → coarse signal, high variance
- Eval loss is continuous → smooth trajectory, easier to detect plateau
- Both correlate (Pearson r > 0.9 in h-e1), but loss more stable

---

**End of Experiment Brief**
