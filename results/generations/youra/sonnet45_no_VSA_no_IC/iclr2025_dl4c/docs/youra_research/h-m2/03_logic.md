# Logic Design: h-m2 Training Dynamics Measurement

**Hypothesis ID:** h-m2  
**Type:** MECHANISM  
**Date:** 2026-08-19  

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase  
**Status:** API patterns verified from h-e1 code  
**Analyzed Path:** code/h-e1/  
**Relevant Symbols:** PPOTrainer, ErrorExtractor, ConditionRunner, ErrorCritic  

---

## A-1: Gradient Variance Computation [Complexity: 2, Budget: 10]

**Applied:** Standard PyTorch gradient introspection

### API Signatures

```python
def compute_gradient_variance(model: torch.nn.Module) -> float:
    """Compute mean std of gradients across LoRA parameters.
    
    Called after loss.backward(), before optimizer.step().
    Returns -1.0 if no gradients present (sentinel for NaN).
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| param.grad | varies | Per-parameter gradient tensor |
| grad_stds | [num_params] | Std per parameter |
| return | scalar | Mean of stds |

### Pseudo-code

```
grad_stds = []
for name, param in model.named_parameters():
    if param.requires_grad and param.grad is not None:
        std = param.grad.std().item()
        grad_stds.append(std)

if len(grad_stds) == 0:
    return -1.0  # Sentinel: no gradients
return mean(grad_stds)
```

### Subtasks [3/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | LoRA parameter filter | Filter named_parameters() for LoRA-specific params |
| L-1-2 | NaN/Inf guard | Check for invalid gradients before std() |
| L-1-3 | Sentinel logging | Log warning when returning -1.0 |

---

## A-2: Error+Trace Reward Function [Complexity: 4, Budget: 15]

**Applied:** Reward shaping with multi-component signals

### API Signatures

```python
ERROR_TYPES = ["SyntaxError", "TypeError", "NameError", "IndexError", "ValueError"]
STACK_DEPTH_BUCKETS = [0, 1, 2, 3, 5, 10, 20, 50, 100, 200, float('inf')]

def compute_error_trace_reward(
    result: ExecutionResult,
    error_types: List[str] = ERROR_TYPES,
    depth_buckets: List[float] = STACK_DEPTH_BUCKETS
) -> float:
    """Compute 5.6-bit reward from error type (2.3 bits) + stack depth (3.3 bits).
    
    result: Execution result with error_type, traceback fields
    Returns: reward in [0.0, 1.0], where 1.0 = all tests passed
    """
    ...

class ExecutionResult:
    all_passed: bool
    error_type: Optional[str]
    traceback: Optional[str]
```

### Pseudo-code

```
if result.all_passed:
    return 1.0

# Error-type component (2.3 bits)
error_reward = 0.0
if result.error_type in error_types:
    idx = error_types.index(result.error_type)
    error_reward = 0.15 * idx  # 0.0 to 0.6 (5 types × 0.15)

# Stack trace depth component (3.3 bits)
depth = 0
if result.traceback is not None:
    depth = len(result.traceback.split('\n'))
else:
    log_warning("traceback=None, defaulting depth=0")

bucket_idx = bisect_right(depth_buckets, depth) - 1
depth_reward = 0.05 * bucket_idx  # 0.0 to 0.45 (10 buckets × 0.05)

return error_reward + depth_reward  # Total: [0.0, 1.05]
```

### Edge Cases

| Case | Input | Output | Action |
|------|-------|--------|--------|
| All passed | all_passed=True | 1.0 | Skip error computation |
| Unknown error | error_type="RuntimeError" | 0.0 + depth_reward | error_reward=0.0 |
| Missing traceback | traceback=None | error_reward + 0.0 | depth=0, log warning |
| Deep trace | depth=500 | error_reward + 0.45 | Capped at max bucket |

### Subtasks [5/15 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | ExecutionResult schema | Define dataclass with validation |
| L-2-2 | Depth parsing | Split traceback by newline, handle None |
| L-2-3 | Bucket search | Use bisect_right for O(log n) lookup |
| L-2-4 | Unknown error logging | Log unrecognized error_type instances |
| L-2-5 | Reward bounds check | Assert final reward in [0.0, 1.0] |

---

## A-3: Convergence Epoch Calculation [Complexity: 2, Budget: 8]

**Applied:** 90% plateau threshold detection

### API Signatures

```python
def compute_convergence_epochs(eval_losses: List[float]) -> float:
    """Compute epochs to reach 90% of final performance.
    
    eval_losses: Per-epoch eval loss trajectory [epoch_0, ..., epoch_N]
    Returns: First epoch (1-indexed) where loss ≤ 90% threshold
             Returns len(eval_losses) if never reached
    """
    ...
```

### Pseudo-code

```
final_loss = eval_losses[-1]
initial_loss = eval_losses[0]
threshold = final_loss + 0.1 * (initial_loss - final_loss)

for epoch_idx, loss in enumerate(eval_losses):
    if loss <= threshold:
        return epoch_idx + 1  # 1-indexed epochs

return len(eval_losses)  # Never converged
```

### Edge Cases

| Case | Input | Output | Behavior |
|------|-------|--------|----------|
| Immediate convergence | eval_losses[0] ≤ threshold | 1 | First epoch matches |
| Never converges | All losses > threshold | len(eval_losses) | Return total epochs |
| Single epoch | eval_losses=[2.3] | 1 | threshold=2.3, matches epoch 0 |

### Subtasks [2/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Threshold computation | Validate 90% interpolation math |
| L-3-2 | Empty list guard | Raise ValueError if eval_losses empty |

---

## A-4: Dynamics Logger State Machine [Complexity: 3, Budget: 12]

**Applied:** Per-batch/per-epoch structured logging with auto-save

### API Signatures

```python
class DynamicsLogger:
    def __init__(self, output_path: str, experiment_id: str):
        """Initialize logger with output file path.
        
        output_path: JSON file path (e.g., 'logs/binary_350m.json')
        experiment_id: Unique ID (e.g., 'h-m2_binary_350m')
        """
        ...

    def log_batch(self, metrics: Dict[str, float]) -> None:
        """Log per-batch metrics. metrics: {step, grad_variance, grad_norm, ...}"""
        ...

    def log_epoch(self, metrics: Dict[str, float]) -> None:
        """Log per-epoch metrics. metrics: {epoch, eval_loss, eval_reward, ...}
        
        Auto-saves to disk after logging.
        Finalizes current epoch and starts new batch list.
        """
        ...

    def save(self) -> None:
        """Explicit save to JSON file. Called automatically by log_epoch()."""
        ...
```

### State Transitions

```
INIT → batch_logging:
    current_epoch = {'batches': []}
    epochs = []

batch_logging → batch_logging:
    on log_batch(metrics):
        current_epoch['batches'].append(metrics)

batch_logging → epoch_logging:
    on log_epoch(metrics):
        current_epoch.update(metrics)
        epochs.append(current_epoch)
        current_epoch = {'batches': []}
        save()

epoch_logging → file_writing:
    on save():
        json.dump(data, file, indent=2)

file_writing → batch_logging:
    save complete
```

### JSON Schema

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
        {"step": 1, "grad_variance": 0.0042, "grad_norm": 1.23, ...}
      ]
    }
  ]
}
```

### Error Handling

| Error | Trigger | Action | Recovery |
|-------|---------|--------|----------|
| IOError | Disk full during save() | Log warning with errno | Continue training, skip save |
| NaN variance | grad_variance is NaN | Replace with -1.0 | Log sentinel, continue |
| Missing field | Missing required key in metrics | Raise KeyError | Abort training (config error) |

### Subtasks [4/12 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Schema validation | Validate required fields on log_batch/log_epoch |
| L-4-2 | Atomic write | Write to temp file, then rename (prevent corruption) |
| L-4-3 | NaN filter | Replace NaN/Inf metrics with -1.0 sentinel |
| L-4-4 | Error log | Separate error log for failed saves |

---

## Integration Points

### A-5: GRPO Training Loop Instrumentation

**Context:** Modify h-e1 PPOTrainer to inject gradient variance computation

### Pseudo-code

```
class GRPOTrainerWithDynamics(PPOTrainer):
    def __init__(self, *args, dynamics_logger: DynamicsLogger, **kwargs):
        super().__init__(*args, **kwargs)
        self.dynamics_logger = dynamics_logger

    def training_step(self, batch):
        # Standard PPO forward + backward
        loss = self.compute_loss(batch)
        loss.backward()
        
        # INJECT: Compute gradient variance BEFORE optimizer.step()
        grad_variance = compute_gradient_variance(self.actor)
        grad_norm = compute_gradient_norm(self.actor)
        reward_variance = batch['rewards'].std().item()
        kl_div = self.compute_kl_divergence(batch)
        
        self.dynamics_logger.log_batch({
            'step': self.global_step,
            'grad_variance': grad_variance,
            'grad_norm': grad_norm,
            'reward_variance': reward_variance,
            'kl_divergence': kl_div
        })
        
        self.optimizer.step()
        self.optimizer.zero_grad()
        return loss

    def evaluation_loop(self, eval_dataloader):
        # Run full HumanEval evaluation
        eval_loss = self.compute_eval_loss(eval_dataloader)
        eval_metrics = self.evaluate_humaneval_full()
        
        self.dynamics_logger.log_epoch({
            'epoch': self.current_epoch,
            'eval_loss': eval_loss,
            'eval_reward_mean': eval_metrics['mean_reward'],
            'eval_pass@1': eval_metrics['pass@1']
        })
        
        return eval_loss
```

### Helper: Gradient Norm Computation

```python
def compute_gradient_norm(model: torch.nn.Module) -> float:
    """Compute L2 norm of full gradient vector. Returns: ||∇θ||_2"""
    total_norm = 0.0
    for param in model.parameters():
        if param.grad is not None:
            total_norm += param.grad.norm(2).item() ** 2
    return total_norm ** 0.5
```

---

## Validation Checklist

### Algorithm Correctness
- [ ] Gradient variance handles param.grad=None (skip parameter)
- [ ] Error+trace reward sums to ≤ 1.0 (0.6 + 0.45 = 1.05 max, need fix!)
- [ ] Convergence epochs returns total epochs if never reached
- [ ] Dynamics logger atomically writes JSON (no corruption)

### Edge Case Coverage
- [ ] Empty eval_losses list raises ValueError
- [ ] traceback=None defaults to depth=0 with warning
- [ ] Unknown error_type sets error_reward=0.0
- [ ] NaN gradient variance logged as -1.0 sentinel

### Integration Compatibility
- [ ] GRPOTrainerWithDynamics extends h-e1 PPOTrainer API
- [ ] log_batch() called BEFORE optimizer.step() (fresh gradients)
- [ ] log_epoch() called AFTER full eval (complete metrics)

**Critical Fix Required:**
Error+trace reward max = 0.15×4 + 0.05×9 = 0.6 + 0.45 = 1.05 (exceeds 1.0!)
Fix: Scale error_reward to 0.1×idx (0.0-0.4) and depth_reward to 0.06×idx (0.0-0.54) → max=0.94 < 1.0

---

## Budget Summary

| Task | Complexity | Budget | Used | Remaining |
|------|------------|--------|------|-----------|
| A-1: Gradient Variance | 2 | 10 | 3 | 7 |
| A-2: Error+Trace Reward | 4 | 15 | 5 | 10 |
| A-3: Convergence Epochs | 2 | 8 | 2 | 6 |
| A-4: Dynamics Logger | 3 | 12 | 4 | 8 |
| **Total** | **11** | **45** | **14** | **31** |

---

**End of Logic Design**
