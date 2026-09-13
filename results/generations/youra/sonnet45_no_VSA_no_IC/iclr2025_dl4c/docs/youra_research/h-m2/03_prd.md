# Product Requirements Document: h-m2 Training Dynamics Measurement

**Hypothesis ID:** h-m2  
**Type:** MECHANISM  
**Gate:** MUST_WORK  
**Date:** 2026-08-19  
**Version:** 1.0  

---

## 1. Executive Summary

Extend h-e1 GRPO training pipeline with training dynamics instrumentation to validate the signal concentration mechanism hypothesis. Measure convergence speed and gradient variance across three feedback granularity levels (binary 1-bit, error-type 2.3-bit, error+trace 5.6-bit) to demonstrate that low-granularity feedback provides faster learning with lower optimization noise.

**Core Product:** Training dynamics logger + error+trace reward function integration into existing h-e1 codebase.

**Success Metrics:**
- Binary and error-type feedback converge ≥20% faster than error+trace (epochs to 90% plateau)
- Binary and error-type feedback show ≥30% lower gradient variance than error+trace

---

## 2. Product Goals

### 2.1 Primary Goal

Instrument h-e1 training loop to collect convergence and gradient variance metrics without modifying core training logic, enabling mechanistic validation of feedback signal concentration hypothesis.

### 2.2 Non-Goals

- Improving h-e1 baseline performance (reuse exact same hyperparameters)
- Extending feedback types beyond the three specified (binary, error-type, error+trace)
- Real-time training visualization (post-hoc analysis only)
- Model architecture changes (keep LoRA config from h-e1)

---

## 3. User Scenarios

**User:** ML researcher validating h-m2 hypothesis  
**Input:** Trained h-e1 model checkpoint (SFT baseline)  
**Action:** Run GRPO training with dynamics logging enabled  
**Output:** JSON file with per-batch gradient variance and per-epoch eval metrics  

**Success Case:**
```bash
$ python train.py --config h-m2/binary_350m.yaml --dynamics-log h-m2/logs/binary_350m_dynamics.json
Training started with dynamics logging...
Epoch 1/5 | Eval Loss: 2.145 | Grad Var: 0.0042 | Pass@1: 15.2%
Epoch 2/5 | Eval Loss: 1.823 | Grad Var: 0.0038 | Pass@1: 18.9%
...
Training complete. Dynamics saved to h-m2/logs/binary_350m_dynamics.json
```

**Failure Case:**
```bash
$ python train.py --config h-m2/error_trace_1b.yaml --dynamics-log ...
Error: Stack trace depth computation failed (traceback field missing)
Aborting training. Check sandbox.py execute_with_timeout() output schema.
```

---

## 4. Functional Requirements

### FR1: Dynamics Logger Module

**Component:** `dynamics_logger.py`

**Capabilities:**
- Per-batch logging: step, grad_variance, grad_norm, reward_variance, kl_divergence
- Per-epoch logging: epoch, eval_loss, eval_reward_mean, eval_pass@1
- Automatic JSON file persistence after each epoch
- Schema validation on write (ensure no missing fields)

**API:**
```python
logger = DynamicsLogger(output_path='logs/binary_350m.json', experiment_id='h-m2_binary_350m')
logger.log_batch({'step': 1, 'grad_variance': 0.0042, 'grad_norm': 1.23, ...})
logger.log_epoch({'epoch': 1, 'eval_loss': 2.145, 'eval_reward_mean': 0.234, ...})
logger.save()  # Explicit save (also auto-saves on log_epoch)
```

**Edge Cases:**
- Disk full during write → raise IOError with clear message
- NaN gradient variance → log -1.0 (sentinel value), continue training
- Missing traceback field in error+trace → default depth=0, log warning

### FR2: Gradient Variance Computation

**Component:** `train.py` (modify GRPOTrainer)

**Capability:** Compute mean std of gradients across all LoRA parameters after loss.backward(), before optimizer.step().

**Implementation:**
```python
def compute_gradient_variance(model: nn.Module) -> float:
    grad_stds = []
    for name, param in model.named_parameters():
        if param.requires_grad and param.grad is not None:
            grad_stds.append(param.grad.std().item())
    return np.mean(grad_stds) if grad_stds else -1.0  # -1.0 = no gradients
```

**Performance Constraint:** Must add <5% overhead to training time (simple tensor ops, no graph modifications).

### FR3: Error+Trace Reward Function

**Component:** `rewards.py` (new module)

**Capability:** Compute 5.6-bit reward from error type (2.3 bits) + stack trace depth (3.3 bits).

**Implementation:**
```python
ERROR_TYPES = ["SyntaxError", "TypeError", "NameError", "IndexError", "ValueError"]
STACK_DEPTH_BUCKETS = [0, 1, 2, 3, 5, 10, 20, 50, 100, 200, float('inf')]

def compute_error_trace_reward(code: str, test_suite: str) -> float:
    result = execute_with_timeout(code, test_suite, timeout=3.0)
    if result.all_passed:
        return 1.0
    
    # Error-type component (2.3 bits)
    error_reward = 0.0
    if result.error_type in ERROR_TYPES:
        idx = ERROR_TYPES.index(result.error_type)
        error_reward = 0.15 * idx  # 0.0 to 0.6
    
    # Stack trace depth component (3.3 bits)
    depth = len(result.traceback.split('\n')) if result.traceback else 0
    bucket_idx = bisect.bisect_right(STACK_DEPTH_BUCKETS, depth) - 1
    depth_reward = 0.05 * bucket_idx  # 0.0 to 0.45
    
    return error_reward + depth_reward
```

**Input Validation:**
- traceback=None → depth=0 (no stack trace available)
- Unknown error_type → error_reward=0.0
- Depth > 200 → bucket_idx=9 (capped at max bucket)

### FR4: Per-Epoch Evaluation Loop

**Component:** `train.py` (modify GRPOTrainer.evaluation_loop)

**Capability:** Run full HumanEval evaluation after each epoch, compute eval_loss, eval_reward_mean, eval_pass@1.

**Implementation:**
```python
def evaluation_loop(self, dataloader):
    eval_loss = super().evaluation_loop(dataloader)  # Cross-entropy loss
    
    # Run pass@1 evaluation on full HumanEval test set
    eval_metrics = self.evaluator.evaluate(self.model, num_samples=164)
    eval_reward = eval_metrics['mean_reward']
    eval_pass_at_1 = eval_metrics['pass@1']
    
    self.dynamics_logger.log_epoch({
        'epoch': self.state.epoch,
        'eval_loss': eval_loss,
        'eval_reward_mean': eval_reward,
        'eval_pass@1': eval_pass_at_1
    })
    
    return eval_loss
```

**Performance:** Full HumanEval eval takes ~10 minutes (164 problems × 3s timeout), acceptable overhead for per-epoch logging.

### FR5: Configuration Management

**Component:** Config YAML files (6 total: 3 feedback types × 2 model sizes)

**Example:** `h-m2/binary_350m.yaml`
```yaml
experiment_id: h-m2_binary_350m
model:
  name: Salesforce/codegen-350M-mono
  lora_r: 16
  lora_alpha: 32
  precision: fp16

training:
  algorithm: grpo
  feedback_type: binary
  epochs: 5
  batch_size: 8
  group_size: 8
  learning_rate: 5.0e-6
  kl_penalty: 0.04
  clip_eps: 0.2
  gradient_accumulation_steps: 2
  max_length: 512

logging:
  dynamics_log: h-m2/logs/binary_350m_dynamics.json
  checkpoint_dir: h-m2/checkpoints/binary_350m
  save_every_epoch: true

dataset:
  name: openai_humaneval
  cache_path: /home/PrayPrey/.cache/huggingface/datasets/openai_humaneval
```

**Validation:**
- feedback_type ∈ {binary, error_type, error_trace}
- epochs ∈ [1, 10]
- batch_size × group_size ≤ 128 (GPU memory constraint)

---

## 5. Non-Functional Requirements

### NFR1: Performance

- Dynamics logging overhead: ≤5% increase in training time
- Gradient variance computation: ≤100ms per batch (negligible)
- JSON file write: async to avoid blocking training loop

### NFR2: Reliability

- Training must complete even if dynamics logging fails (graceful degradation)
- Checkpoint saving independent of dynamics logging
- All metrics stored with timestamp for reproducibility

### NFR3: Usability

- Single command to launch training with dynamics logging enabled
- JSON output schema documented with example
- Clear error messages for configuration validation failures

### NFR4: Maintainability

- Dynamics logging code isolated in separate module (single-responsibility)
- No breaking changes to h-e1 codebase (backward compatible)
- Unit tests for gradient variance computation (synthetic tensors)

---

## 6. Data Requirements

### DR1: Input Data

**Dataset:** HumanEval (cached from h-e1)
- Location: `/home/PrayPrey/.cache/huggingface/datasets/openai_humaneval`
- Size: 164 problems
- Split: No train/test split (full set for evaluation)

**Pretrained Models:**
- CodeGen-350M-mono (Salesforce)
- StarCoder-1B (BigCode)
- Cache: `/home/PrayPrey/.cache/huggingface/hub/`

### DR2: Output Data

**Dynamics Logs (6 files):**
- Path: `h-m2/logs/{feedback_type}_{model_size}_dynamics.json`
- Size estimate: 50MB per file (5 epochs × 500 batches × 200 bytes/batch)
- Schema: See Appendix A (JSON schema)

**Checkpoints (30 files):**
- Path: `h-m2/checkpoints/{feedback_type}_{model_size}_epoch{1-5}.pt`
- Size: 500MB per checkpoint (LoRA weights only)
- Total: 30 checkpoints × 500MB = 15GB

---

## 7. Success Criteria

### Gate Metrics (from 02c_experiment_brief.md)

**Convergence Speed:**
- Binary feedback: epochs_to_90% ≤ 0.8 × error+trace epochs
- Error-type feedback: epochs_to_90% ≤ 0.8 × error+trace epochs

**Gradient Variance:**
- Binary feedback: mean_grad_variance ≤ 0.7 × error+trace variance
- Error-type feedback: mean_grad_variance ≤ 0.7 × error+trace variance

**Statistical Significance:**
- Two-sample t-test: p < 0.0167 (Bonferroni corrected)
- Effect size: Cohen's d ≥ 0.8 (large effect)

### Validation Checklist

**Code Validation:**
- [ ] Dynamics logger unit tests pass (100% coverage)
- [ ] Gradient variance computation matches manual calculation (synthetic data)
- [ ] Error+trace reward function returns values in [0.0, 1.0]
- [ ] All 6 config files validated (no schema errors)

**Runtime Validation:**
- [ ] Training completes without crashes (all 6 models)
- [ ] Dynamics JSON files parseable (no malformed JSON)
- [ ] Eval loss decreases monotonically (no divergence)
- [ ] Gradient variance stable (no exponential growth)

**Gate Validation:**
- [ ] Convergence epochs computable (90% plateau reached)
- [ ] Gradient variance aggregated (no NaN values)
- [ ] Statistical tests run (p-values, effect sizes)
- [ ] Gate result: PASS/FAIL determined

---

## 8. Dependencies

**From h-e1 (Reuse):**
- transformers==4.50.0
- trl==0.15.1
- peft==0.14.0
- datasets==3.2.0
- torch==2.5.0

**New Dependencies:**
- None (use stdlib json, bisect, numpy)

**Hardware:**
- GPU: NVIDIA H100 NVL (80GB VRAM) — Available
- Training time: 3 hours × 6 models = 18 GPU-hours

---

## 9. Timeline

**Phase 1: Code Modification (2 hours)**
- Implement dynamics_logger.py
- Modify train.py (add gradient variance computation)
- Implement rewards.py (error+trace reward function)
- Create 6 config YAML files

**Phase 2: Validation (1 hour)**
- Unit tests for dynamics logger
- Dry run: 1 epoch of binary_350m training
- Verify JSON schema correctness

**Phase 3: Experiment Execution (18 hours)**
- Train 6 models (3 feedback types × 2 model sizes)
- Monitor for crashes, log anomalies

**Phase 4: Analysis (2 hours)**
- Compute convergence epochs
- Aggregate gradient variance
- Run statistical tests
- Generate visualizations (3 figures)

**Total:** 23 hours

---

## 10. Risk Mitigation

**R1: Gradient Variance Noise**
- **Risk:** Per-batch variance too stochastic to detect differences
- **Mitigation:** Aggregate over 2500+ batches, skip warmup (first 20%)
- **Fallback:** Use exponential moving average (EMA α=0.9)

**R2: Convergence Detection Failure**
- **Risk:** Eval loss never reaches 90% plateau in 5 epochs
- **Mitigation:** Increase epochs to 7 if plateau not reached by epoch 5
- **Fallback:** Use "epochs to 80% plateau" as secondary metric

**R3: Stack Trace Depth Uninformative**
- **Risk:** All errors have depth ≈ 1-2 lines (no variation)
- **Mitigation:** Validate depth distribution on h-e1 error logs first
- **Fallback:** Replace depth buckets with line number buckets

**R4: Statistical Power Insufficient**
- **Risk:** Only 2 models (350M, 1B) → low power for t-tests
- **Mitigation:** Run 3 random seeds per condition (6 data points)
- **Fallback:** Use paired t-test (within-model comparison)

---

## 11. Appendix

### A. JSON Schema (Dynamics Log)

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

### B. Convergence Epoch Calculation

```python
def compute_convergence_epochs(eval_losses: List[float]) -> float:
    final_loss = eval_losses[-1]
    initial_loss = eval_losses[0]
    threshold = final_loss + 0.1 * (initial_loss - final_loss)
    
    for epoch, loss in enumerate(eval_losses):
        if loss <= threshold:
            return epoch + 1  # 1-indexed
    return len(eval_losses)  # Never converged
```

### C. Gradient Variance Aggregation

```python
def aggregate_gradient_variance(dynamics: dict) -> float:
    all_variances = []
    for epoch in dynamics['epochs']:
        # Skip first 20% of batches (warmup)
        batches = epoch['batches'][int(len(epoch['batches']) * 0.2):]
        all_variances.extend([b['grad_variance'] for b in batches])
    return np.mean(all_variances)
```

---

**End of PRD**
