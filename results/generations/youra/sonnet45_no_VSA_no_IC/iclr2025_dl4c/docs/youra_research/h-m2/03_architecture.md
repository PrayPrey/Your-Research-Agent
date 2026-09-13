# System Architecture: h-m2 Training Dynamics Measurement

**Date:** 2026-08-19  
**Hypothesis:** h-m2 (MECHANISM - Low-granularity feedback signal concentration)  
**Base Hypothesis:** h-e1 (GRPO training pipeline)  
**Applied Patterns:** Training instrumentation, gradient variance tracking

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Reusing h-e1 core training infrastructure  
**Analyzed Path**: docs/youra_research/h-e1/code/  
**Findings**: h-e1 provides SFTTrainer, GRPOTrainer, ExecutionSandbox, HumanEval loader. New: dynamics logging + error+trace reward.

---

## System Overview

Extend h-e1 GRPO pipeline with training dynamics instrumentation. Measures convergence speed and gradient variance across 3 feedback types (binary 1-bit, error-type 2.3-bit, error+trace 5.6-bit). No changes to core training logic.

**Training Flow:**
```
HumanEval → SFT Baseline → GRPO Training (3 feedback types) → Per-epoch Evaluation
                                ↓
                        DynamicsLogger (per-batch + per-epoch)
                                ↓
                        JSON files (gradient variance, eval metrics)
```

---

## Module Structure

### 1. DynamicsLogger (`dynamics_logger.py`)

**Dependencies**: None (stdlib json)

```python
class DynamicsLogger:
    def __init__(self, output_path: str, experiment_id: str): ...
    def log_batch(self, metrics: dict) -> None: ...
    def log_epoch(self, metrics: dict) -> None: ...
    def save(self) -> None: ...
    def _validate_schema(self, data: dict) -> bool: ...
```

### 2. RewardFunctions (`rewards.py`)

**Dependencies**: ExecutionSandbox (h-e1)

```python
ERROR_TYPES: List[str] = ["SyntaxError", "TypeError", "NameError", "IndexError", "ValueError"]
STACK_DEPTH_BUCKETS: List[float] = [0, 1, 2, 3, 5, 10, 20, 50, 100, 200, float('inf')]

def compute_error_trace_reward(code: str, test: str, entry_point: str, sandbox) -> float: ...
def parse_stack_depth(traceback: str) -> int: ...
```

### 3. GradientMetrics (`train.py` - addition)

**Dependencies**: torch

```python
def compute_gradient_variance(model: nn.Module) -> float: ...
def compute_gradient_norm(model: nn.Module) -> float: ...
```

### 4. Modified GRPOTrainer (`train.py` - extension)

**Dependencies**: GRPOTrainer (h-e1), DynamicsLogger

```python
class GRPOTrainerWithDynamics(GRPOTrainer):
    def __init__(self, *args, dynamics_logger: DynamicsLogger, **kwargs): ...
    def training_step(self, batch: dict) -> float: ...
    def evaluation_loop(self, eval_dataset: Dataset) -> dict: ...
    def _log_batch_metrics(self, loss: float, rewards: List[float]) -> None: ...
```

### 5. ConfigManager (`config.py`)

**Dependencies**: yaml

```python
class ExperimentConfig:
    def __init__(self, config_path: str): ...
    def validate(self) -> bool: ...
    def get_logging_config(self) -> dict: ...
    def get_grpo_config(self) -> dict: ...
```

---

## External Dependencies (h-e1)

### Module Paths (Verified from Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| GRPOTrainer | `from train import GRPOTrainer` | `h-e1/code/train.py` |
| ExecutionSandbox | `from sandbox import ExecutionSandbox` | `h-e1/code/sandbox.py` |
| HumanEvalLoader | `from dataset import HumanEvalLoader` | `h-e1/code/dataset.py` |
| ModelManager | `from model import ModelManager` | `h-e1/code/model.py` |
| Evaluator | `from eval import Evaluator` | `h-e1/code/eval.py` |

**Reuse Pattern**: Copy h-e1/code/ modules to h-m2/code/, modify train.py only.

---

## Data Flow

### Training Loop (Per Batch)

```
1. GRPOTrainerWithDynamics.training_step()
2. Generate rollouts (8 samples per prompt)
3. Compute rewards via sandbox.compute_error_trace_reward() [NEW]
4. Compute advantages (GRPO)
5. loss.backward()
6. → compute_gradient_variance(model) [INJECT]
7. → compute_gradient_norm(model) [INJECT]
8. → dynamics_logger.log_batch({step, grad_variance, grad_norm, ...}) [INJECT]
9. optimizer.step()
```

### Evaluation Loop (Per Epoch)

```
1. GRPOTrainerWithDynamics.evaluation_loop()
2. Run HumanEval evaluation (164 problems)
3. Compute eval_loss, eval_reward_mean, eval_pass@1
4. → dynamics_logger.log_epoch({epoch, eval_loss, eval_reward_mean, eval_pass@1}) [INJECT]
5. dynamics_logger.save() [auto-save JSON]
```

### Output Data

```
h-m2/logs/
├── binary_350m_dynamics.json
│   └── {experiment_id, feedback_type, epochs[{epoch, eval_loss, eval_pass@1, batches[{step, grad_variance, grad_norm, ...}]}]}
├── error_type_350m_dynamics.json
├── error_trace_350m_dynamics.json
├── binary_1b_dynamics.json
├── error_type_1b_dynamics.json
└── error_trace_1b_dynamics.json
```

---

## File Structure

```
h-m2/
├── code/
│   ├── train.py                      # Modified GRPOTrainer with dynamics logging
│   ├── dynamics_logger.py            # DynamicsLogger class
│   ├── rewards.py                    # Error+trace reward function
│   ├── config.py                     # Config validation
│   ├── dataset.py                    # [COPIED from h-e1]
│   ├── model.py                      # [COPIED from h-e1]
│   ├── sandbox.py                    # [COPIED from h-e1]
│   ├── eval.py                       # [COPIED from h-e1]
│   └── run_experiment.py             # Orchestrator with 6 training runs
├── configs/
│   ├── binary_350m.yaml
│   ├── error_type_350m.yaml
│   ├── error_trace_350m.yaml
│   ├── binary_1b.yaml
│   ├── error_type_1b.yaml
│   └── error_trace_1b.yaml
├── logs/                             # Output directory
└── checkpoints/                      # Model checkpoints
```

---

## Integration Points

### 1. Gradient Variance Computation Hook

**Location**: `train.py::GRPOTrainerWithDynamics.training_step()` after `loss.backward()`, before `optimizer.step()`

**Implementation**:
```python
grad_variance = compute_gradient_variance(self.policy)
grad_norm = compute_gradient_norm(self.policy)
```

**Constraint**: <5% overhead (verified: torch.std() on 16M params = ~50ms)

### 2. Evaluation Loop Hook

**Location**: `train.py::GRPOTrainerWithDynamics.evaluation_loop()` after eval metrics computation

**Implementation**:
```python
eval_metrics = self.evaluator.evaluate(self.policy, num_samples=164)
self.dynamics_logger.log_epoch({
    'epoch': self.state.epoch,
    'eval_loss': eval_loss,
    'eval_reward_mean': eval_metrics['mean_reward'],
    'eval_pass@1': eval_metrics['pass@1']
})
```

### 3. Error+Trace Reward Integration

**Location**: `sandbox.py` - add new method (no modification to existing methods)

**Implementation**:
```python
# In sandbox.py
from rewards import compute_error_trace_reward

class ExecutionSandbox:
    # Existing methods unchanged
    def compute_error_trace_reward_wrapper(self, code: str, test: str, entry_point: str) -> float:
        return compute_error_trace_reward(code, test, entry_point, self)
```

---

## Configuration Schema

**Example**: `configs/error_trace_350m.yaml`

```yaml
experiment_id: h-m2_error_trace_350m
model:
  name: Salesforce/codegen-350M-mono
  lora_r: 16
  lora_alpha: 32
  precision: fp16

training:
  algorithm: grpo
  feedback_type: error_trace
  epochs: 5
  batch_size: 8
  samples_per_problem: 8
  learning_rate: 5.0e-6
  kl_penalty: 0.04
  max_grad_norm: 1.0
  gradient_accumulation_steps: 2

logging:
  dynamics_log: h-m2/logs/error_trace_350m_dynamics.json
  checkpoint_dir: h-m2/checkpoints/error_trace_350m
  save_every_epoch: true
  log_batch_metrics: true

dataset:
  name: openai_humaneval
  cache_path: /home/PrayPrey/.cache/huggingface/datasets/openai_humaneval
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Implement DynamicsLogger | JSON schema + batch/epoch logging + validation | 8 | 2 (class) + 2 (batch) + 2 (epoch) + 2 (save/validate) |
| A-2 | Implement Gradient Metrics | compute_gradient_variance + compute_gradient_norm | 6 | 3 (variance) + 2 (norm) + 1 (edge cases) |
| A-3 | Implement Error+Trace Reward | Stack depth parsing + bucket mapping + reward computation | 10 | 3 (depth parsing) + 2 (buckets) + 3 (reward calc) + 2 (integration) |
| A-4 | Extend GRPOTrainer | Add dynamics_logger, inject hooks in training_step + evaluation_loop | 12 | 4 (class extension) + 4 (training_step hook) + 4 (evaluation hook) |
| A-5 | Create 6 Config Files | YAML files for 3 feedback types × 2 models, validation logic | 7 | 2 (template) + 3 (6 configs) + 2 (validation) |
| A-6 | Implement Orchestrator | run_experiment.py to execute 6 training runs sequentially | 9 | 3 (config loading) + 4 (training loop) + 2 (checkpoint management) |

**Distribution**: High(12-15): [A-4], Medium(9-11): [A-3, A-6], Low(6-8): [A-1, A-2, A-5]

---

## Validation

### Code Validation

- [ ] DynamicsLogger JSON schema matches spec (experiment_id, epochs, batches)
- [ ] Gradient variance returns -1.0 for NaN/missing gradients
- [ ] Error+trace reward in range [0.0, 1.0] for all test cases
- [ ] Stack depth parsing handles None traceback (default depth=0)
- [ ] Config validation rejects invalid feedback_type

### Runtime Validation

- [ ] Dynamics logging overhead ≤5% (measured via batch timing)
- [ ] JSON files written after each epoch (auto-save)
- [ ] No training crashes with dynamics logging enabled
- [ ] Gradient variance stable (no exponential growth)
- [ ] All 6 configs validated before training

### Output Validation

- [ ] JSON files parseable (no malformed JSON)
- [ ] Convergence epochs computable (90% plateau reached)
- [ ] Gradient variance aggregated (no NaN values)
- [ ] Checkpoints saved every epoch (30 total)

---

## Performance Constraints

| Metric | Target | Verification |
|--------|--------|--------------|
| Gradient variance computation | ≤100ms/batch | Profile torch.std() on synthetic tensors |
| JSON write | Async (non-blocking) | Use `json.dump()` with file buffer |
| Dynamics logging overhead | ≤5% training time | Compare identical run with/without logging |
| Per-epoch evaluation | ≤10 minutes | 164 problems × 3s timeout = 492s + overhead |

---

## Error Handling

### Dynamics Logging Failures

**Strategy**: Graceful degradation - training continues even if logging fails

```python
try:
    self.dynamics_logger.log_batch(metrics)
except Exception as e:
    logger.warning(f"Dynamics logging failed: {e}. Continuing training.")
```

### Missing Traceback Fields

**Strategy**: Default to depth=0, log warning

```python
depth = len(result.traceback.split('\n')) if result.traceback else 0
if result.traceback is None:
    logger.warning(f"Missing traceback for {entry_point}. Using depth=0.")
```

### NaN Gradient Variance

**Strategy**: Log sentinel value -1.0, continue training

```python
grad_variance = compute_gradient_variance(model)
if np.isnan(grad_variance):
    grad_variance = -1.0
    logger.warning(f"NaN gradient variance at step {step}. Logging -1.0.")
```

---

## Dependency Management

**From h-e1 (No New Dependencies):**
- transformers==4.50.0
- trl==0.15.1
- peft==0.14.0
- datasets==3.2.0
- torch==2.5.0

**Stdlib (New Usage):**
- json (DynamicsLogger)
- bisect (Error+trace bucket mapping)
- yaml (Config loading)

---

## Rollout Plan

**Phase 1: Implementation (2 hours)**
1. Copy h-e1/code/ modules to h-m2/code/
2. Implement dynamics_logger.py (A-1)
3. Implement rewards.py (A-3)
4. Modify train.py with GRPOTrainerWithDynamics (A-4)
5. Add gradient metrics to train.py (A-2)
6. Create 6 config YAML files (A-5)
7. Implement run_experiment.py orchestrator (A-6)

**Phase 2: Validation (1 hour)**
1. Unit test DynamicsLogger (synthetic metrics)
2. Unit test gradient variance (synthetic model)
3. Dry run: 1 epoch of binary_350m (verify logging)
4. Validate JSON schema correctness

**Phase 3: Execution (18 hours)**
1. Run 6 training jobs (3 feedback types × 2 models)
2. Monitor dynamics logs (check for NaN, crashes)

**Total**: 21 hours
