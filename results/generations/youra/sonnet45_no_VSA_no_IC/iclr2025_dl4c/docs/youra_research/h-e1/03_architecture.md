# System Architecture: h-e1 Binary Feedback Sufficiency

**Date:** 2026-08-19  
**Hypothesis:** h-e1 (EXISTENCE - Binary feedback dual-threshold sufficiency)  
**Source Documents:** 03_prd.md, 02c_experiment_brief.md  

---

## Architecture Overview

Modular RLVR training pipeline with 7 core components for single-GPU execution. Sequential training flow: SFT baseline → Binary RLVR → Error-Type RLVR → Evaluation → Validation.

```
┌─────────────────────────────────────────────────────────────┐
│                    Orchestrator (run_experiment.py)         │
│         Progress Logging │ Error Handling │ Checkpointing   │
└────────┬────────────────────────────────────────────────────┘
         │
         ├─► Dataset Loader ──► HumanEval (164 problems)
         │       │
         │       └─► Training Prompts (function signature + docstring)
         │       └─► Test Suites (unit tests per problem)
         │
         ├─► Model Manager
         │       ├─► Load Pretrained (CodeGen-350M / StarCoder-1B)
         │       ├─► Configure LoRA (r=16, alpha=32)
         │       └─► Freeze Reference Model (for KL penalty)
         │
         ├─► Training Engine
         │       ├─► SFT Trainer ──► SFT Checkpoint
         │       │       └─► Causal LM Loss on (prompt, canonical_solution)
         │       │
         │       ├─► GRPO Binary Trainer ──┐
         │       │       └─► Policy Gradient + KL Penalty │
         │       │                                         ├─► Execution Sandbox
         │       ├─► GRPO Error-Type Trainer ──┘              │
         │                                                     │
         │                                                     ├─► Binary Reward (1.0 / 0.0)
         │                                                     └─► Error-Type Reward (5 categories)
         │
         ├─► Evaluation Pipeline
         │       ├─► Load Checkpoints (SFT, Binary, Error-Type)
         │       ├─► Generate Completions (greedy, temp=0)
         │       ├─► Execute + Test Suites ──► Pass/Fail per Problem
         │       └─► Compute pass@1 (# passed / 164)
         │
         └─► Validation Reporter
                 ├─► Gate Threshold Checking
                 │       ├─► Absolute: pass@1_binary - pass@1_sft ≥ 8.0
                 │       └─► Retention: (binary - sft) / (error_type - sft) ≥ 0.80
                 ├─► Visualization Generation
                 │       ├─► Mandatory: gate_metrics.png (bar chart)
                 │       └─► Optional: training_curves.png, reward_distribution.png
                 └─► State Update (verification_state.yaml)
```

---

## Component Specifications

### 1. Dataset Loader (`dataset.py`)

**Responsibility:** HumanEval dataset loading and preprocessing.

**Interface:**
```python
class HumanEvalLoader:
    def load_dataset() -> Dataset:
        """Load HumanEval from HuggingFace Hub."""
        # Returns: datasets.Dataset with 164 problems
        
    def prepare_training_prompts(dataset: Dataset) -> List[str]:
        """Extract function signature + docstring for training."""
        # Returns: List of 164 prompts
        
    def prepare_test_suites(dataset: Dataset) -> List[Dict]:
        """Extract test cases and entry points for evaluation."""
        # Returns: List of {test: str, entry_point: str, task_id: str}
```

**Dependencies:**
- `datasets` library (HuggingFace)
- `openai/openai_humaneval` dataset identifier

**Data Flow:**
- Input: Dataset identifier string
- Output: Training prompts + Test suites

**Error Handling:**
- Network failure → Retry 3x with exponential backoff
- Cache miss → Download from HF Hub
- Malformed data → Log warning, skip problem

---

### 2. Model Manager (`model.py`)

**Responsibility:** Pretrained model loading, LoRA configuration, reference model freezing.

**Interface:**
```python
class ModelManager:
    def load_pretrained(model_name: str, precision: str) -> CausalLM:
        """Load CodeGen-350M or StarCoder-1B with specified precision."""
        # Returns: AutoModelForCausalLM in fp16/bf16
        
    def configure_lora(model: CausalLM, r: int, alpha: int) -> LoRAModel:
        """Add LoRA adapters to q_proj, v_proj."""
        # Returns: PEFT model with trainable LoRA weights
        
    def freeze_reference(model: CausalLM) -> CausalLM:
        """Create frozen copy for KL penalty computation."""
        # Returns: Model with requires_grad=False
```

**Dependencies:**
- `transformers` (AutoModel, AutoTokenizer)
- `peft` (LoRAConfig, get_peft_model)
- `torch` (device management)

**Data Flow:**
- Input: Model name, precision, LoRA config
- Output: Trainable model + Frozen reference

**Memory Management:**
- Load in fp16/bf16 to fit 16GB VRAM
- LoRA reduces trainable params by ~100x
- Reference model shares weights (no duplication)

**Error Handling:**
- CUDA OOM → Fallback to gradient checkpointing
- Model not found → Raise with suggested alternatives

---

### 3. Execution Sandbox (`sandbox.py`)

**Responsibility:** Safe code execution with timeout and reward computation.

**Interface:**
```python
class ExecutionSandbox:
    def compute_binary_reward(code: str, test: str, entry_point: str) -> float:
        """Execute code + test, return 1.0 if pass, 0.0 if fail."""
        # Timeout: 3 seconds
        # Returns: {0.0, 1.0}
        
    def compute_error_type_reward(code: str, test: str, entry_point: str) -> float:
        """Execute code + test, return reward based on error type."""
        # 5 categories: SyntaxError=0.0, TypeError=0.2, NameError=0.4, ValueError=0.6, AssertionError=0.8, Pass=1.0
        # Returns: {0.0, 0.2, 0.4, 0.6, 0.8, 1.0}
```

**Dependencies:**
- `signal` (timeout enforcement via SIGALRM)
- `exec` (code execution in isolated globals)

**Data Flow:**
- Input: Generated code, test suite, entry point
- Output: Scalar reward {0.0, 0.2, 0.4, 0.6, 0.8, 1.0}

**Safety Mechanisms:**
- Timeout: `signal.alarm(3)` before exec, raises TimeoutError
- Isolated globals: `exec(code, {})` (no access to module scope)
- No file I/O or network access allowed

**Error Handling:**
- Timeout → Return 0.0
- SyntaxError → Return 0.0 (binary) or 0.0 (error-type)
- TypeError/NameError/ValueError → Return 0.0 (binary) or category reward
- AssertionError → Return 0.0 (binary) or 0.8 (error-type)
- Other exceptions → Return 0.0

**Throughput Target:** ≥10 executions/second

---

### 4. Training Engine (`train.py`)

**Responsibility:** SFT baseline and GRPO RLVR training loops.

**Interface:**
```python
class SFTTrainer:
    def train(model: CausalLM, prompts: List[str], solutions: List[str]) -> Checkpoint:
        """Supervised fine-tuning on (prompt, solution) pairs."""
        # Causal LM loss, AdamW lr=2e-5, 3-5 epochs
        # Returns: Checkpoint path
        
class GRPOTrainer:
    def train_binary(model: LoRAModel, ref_model: CausalLM, prompts: List[str], 
                     test_suites: List[Dict], sandbox: ExecutionSandbox) -> Checkpoint:
        """GRPO training with binary execution rewards."""
        # Sample 4 completions per problem
        # Compute binary rewards via sandbox
        # Group advantages: (rewards - mean) / std
        # Policy gradient + KL penalty (coef=0.1)
        # AdamW lr=2e-7, 500-1000 steps
        # Returns: Checkpoint path
        
    def train_error_type(model: LoRAModel, ref_model: CausalLM, prompts: List[str],
                         test_suites: List[Dict], sandbox: ExecutionSandbox) -> Checkpoint:
        """GRPO training with error-type rewards."""
        # Same as train_binary but uses compute_error_type_reward
        # Returns: Checkpoint path
```

**Dependencies:**
- `transformers` (Trainer API)
- `trl` (PPOTrainer for GRPO)
- `torch` (optimizer, loss computation)

**Data Flow:**
- SFT: Prompts + Solutions → SFT Checkpoint
- GRPO: Prompts + Test Suites + Sandbox → RLVR Checkpoint

**Hyperparameters:**
| Parameter | SFT | GRPO |
|-----------|-----|------|
| Optimizer | AdamW | AdamW |
| Learning Rate | 2e-5 | 2e-7 |
| Batch Size | 8 | 4 problems × 4 samples |
| Epochs/Steps | 3-5 | 500-1000 |
| KL Coef | N/A | 0.1 |

**Error Handling:**
- CUDA OOM → Reduce batch size to 4 (SFT) or 2 problems (GRPO)
- Reward degeneration (mean reward < 0.1 after 200 steps) → Early stop with warning
- KL divergence > 2.0 → Increase KL coef to 0.2

**Logging:**
- Training loss every 10 steps
- Mean reward every 50 steps
- KL divergence every 50 steps
- Checkpoints every 100 steps

---

### 5. Evaluation Pipeline (`eval.py`)

**Responsibility:** HumanEval pass@1 metric computation for all model variants.

**Interface:**
```python
class Evaluator:
    def evaluate_checkpoint(checkpoint_path: str, test_suites: List[Dict]) -> Dict:
        """Generate completions and compute pass@1."""
        # Greedy decoding (temperature=0)
        # Execute completions + test suites
        # Returns: {
        #   "pass@1": float,
        #   "results": List[{task_id: str, passed: bool}]
        # }
```

**Dependencies:**
- `transformers` (model.generate)
- `human_eval.evaluation` (evaluate_functional_correctness)
- Execution sandbox for test execution

**Data Flow:**
- Input: Checkpoint path, test suites
- Output: pass@1 metric + per-problem results

**Generation Config:**
- Temperature: 0 (greedy)
- Max tokens: 512 (sufficient for HumanEval functions)
- Stop tokens: ["\n\n", "def ", "class "]

**Error Handling:**
- Generation timeout (>30s per problem) → Log warning, mark as failed
- Malformed output → Mark as failed
- Test execution error → Handled by sandbox

---

### 6. Validation Reporter (`validate.py`)

**Responsibility:** Gate threshold checking, visualization, state updates.

**Interface:**
```python
class ValidationReporter:
    def check_gate(sft_pass1: float, binary_pass1: float, error_type_pass1: float) -> Dict:
        """Verify dual-threshold success criteria."""
        # Threshold 1: binary - sft ≥ 8.0
        # Threshold 2: (binary - sft) / (error_type - sft) ≥ 0.80
        # Returns: {
        #   "gate_passed": bool,
        #   "absolute_improvement": float,
        #   "retention_ratio": float
        # }
        
    def generate_visualizations(results: Dict, output_dir: str) -> List[str]:
        """Create gate metrics bar chart + optional figures."""
        # Mandatory: gate_metrics.png
        # Optional: training_curves.png, reward_distribution.png, error_breakdown.png
        # Returns: List of generated figure paths
        
    def update_verification_state(gate_result: Dict, state_file: str):
        """Update verification_state.yaml with gate decision."""
        # Sets: gate.satisfied, gate.result, validation.result
```

**Dependencies:**
- `matplotlib` (visualization)
- `pyyaml` (state file updates)

**Data Flow:**
- Input: Evaluation results (pass@1 for all three models)
- Output: Gate status + Figures + Updated state file

**Visualization Specs:**
- Gate metrics bar chart:
  - X-axis: [Absolute Improvement, Retention Ratio]
  - Y-axis: Metric value
  - Threshold lines: 8.0 (absolute), 0.80 (retention)
  - Colors: Green if ≥threshold, Red if <threshold
  - Resolution: 300 DPI, size 8x6 inches

**Error Handling:**
- Division by zero (error_type - sft = 0) → Report retention as undefined
- Negative retention → Valid result (binary worse than SFT)
- Visualization failure → Log error, continue with state update

---

### 7. Orchestrator (`run_experiment.py`)

**Responsibility:** End-to-end pipeline coordination, progress logging, error handling.

**Interface:**
```python
def main(hypothesis_id: str):
    """Run full pipeline for given hypothesis."""
    # 1. Dataset setup
    # 2. Model loading
    # 3. SFT training
    # 4. GRPO Binary training
    # 5. GRPO Error-Type training
    # 6. Evaluation (all three checkpoints)
    # 7. Validation reporting
    # 8. State update
```

**Dependencies:**
- All 6 components above
- `argparse` (CLI argument parsing)
- `logging` (progress logging)

**Data Flow:**
```
CLI Args → Dataset Loader → Model Manager → SFT Trainer → GRPO Trainers → Evaluator → Validator → State File
```

**Checkpoint Resumption:**
- Check for existing checkpoints before training
- Skip completed stages (SFT/Binary/Error-Type)
- Resume from latest incomplete stage

**Logging:**
- INFO: Stage transitions, checkpoint saves, metric values
- WARNING: Retry attempts, threshold failures
- ERROR: Component failures, pipeline abort

**Error Handling:**
- Component failure → Log error, attempt recovery (e.g., retry with reduced batch size)
- Irrecoverable error → Save partial results, update state with FAILED status, exit with code 1
- Keyboard interrupt → Save checkpoint, clean exit

**Progress Reporting:**
```
[INFO] Stage 1/7: Loading HumanEval dataset...
[INFO] Stage 2/7: Configuring CodeGen-350M with LoRA...
[INFO] Stage 3/7: Training SFT baseline (epoch 1/5)...
[INFO] Stage 4/7: Training GRPO Binary (step 50/500, mean_reward=0.15)...
[INFO] Stage 5/7: Training GRPO Error-Type (step 50/500, mean_reward=0.20)...
[INFO] Stage 6/7: Evaluating checkpoints on HumanEval...
[INFO] Stage 7/7: Validating gate thresholds...
[INFO] RESULT: Gate PASSED (absolute=9.2pp, retention=0.85)
```

---

## Deployment Architecture

### Single-GPU Execution

**Hardware Requirements:**
- NVIDIA GPU with 16GB VRAM (A100, V100, L4)
- 50GB disk space (models + checkpoints)
- CUDA 11.8+

**Resource Allocation:**
| Component | VRAM | Disk | Time |
|-----------|------|------|------|
| Model (fp16) | ~2GB | 700MB | N/A |
| LoRA adapters | ~200MB | 50MB | N/A |
| Reference model (shared weights) | 0GB | 0GB | N/A |
| Training batch (8 samples) | ~8GB | 0GB | N/A |
| Optimizer states | ~4GB | 0GB | N/A |
| Total (peak) | **~14GB** | **2GB** | **12 hours** |

**Sequential Execution (No Parallelism):**
1. SFT training: 2 hours
2. GRPO Binary training: 4 hours
3. GRPO Error-Type training: 4 hours
4. Evaluation: 1 hour
5. Validation: <10 minutes

**Memory Optimization:**
- fp16 precision (halves memory footprint)
- LoRA (reduces trainable params by 100x)
- Gradient accumulation (effective batch size > physical batch size)
- No multi-GPU needed (single model fits in 16GB)

---

## Data Flow Diagram

```
┌──────────────┐
│ HumanEval    │
│ (HF Hub)     │
└───────┬──────┘
        │
        ▼
┌──────────────────┐
│ Dataset Loader   │
│ - 164 problems   │
│ - Prompts        │
│ - Test suites    │
└────────┬─────────┘
         │
         ├────────────────────────────────────┐
         │                                    │
         ▼                                    ▼
┌────────────────┐                   ┌──────────────┐
│ SFT Trainer    │                   │ Model Manager│
│ - (P, S) pairs │◄──────────────────│ - CodeGen    │
│ - Causal LM    │                   │ - LoRA       │
│ - 3-5 epochs   │                   │ - Reference  │
└───────┬────────┘                   └──────────────┘
        │
        ▼
┌──────────────────┐
│ SFT Checkpoint   │
└────────┬─────────┘
         │
         ├──────────────────────────────────┐
         │                                  │
         ▼                                  ▼
┌───────────────────┐             ┌─────────────────┐
│ GRPO Binary       │             │ GRPO Error-Type │
│ - Sample 4/prob   │             │ - Sample 4/prob │
│ - Binary reward   │             │ - Error reward  │
│ - KL penalty      │             │ - KL penalty    │
└────────┬──────────┘             └────────┬────────┘
         │                                 │
         │        ┌────────────────┐       │
         └───────►│ Exec Sandbox   │◄──────┘
                  │ - Timeout 3s   │
                  │ - Reward calc  │
                  └────────────────┘
         │                                 │
         ▼                                 ▼
┌────────────────┐              ┌──────────────────┐
│ Binary Ckpt    │              │ Error-Type Ckpt  │
└────────┬───────┘              └────────┬─────────┘
         │                               │
         └───────┬───────────────────────┘
                 │
                 ▼
         ┌──────────────┐
         │  Evaluator   │
         │  - Generate  │
         │  - Execute   │
         │  - pass@1    │
         └───────┬──────┘
                 │
                 ▼
         ┌──────────────────────┐
         │ Validation Reporter  │
         │ - Gate check         │
         │ - Visualizations     │
         │ - State update       │
         └───────┬──────────────┘
                 │
                 ▼
         ┌──────────────────────┐
         │ verification_state   │
         │ - gate.satisfied     │
         │ - validation.result  │
         └──────────────────────┘
```

---

## Error Recovery Strategies

### Strategy 1: Checkpoint Resumption
- Save checkpoints every 100 training steps
- On restart, detect existing checkpoints and skip completed stages
- Resume from last incomplete stage

### Strategy 2: Graceful Degradation
- CUDA OOM → Reduce batch size (8→4 for SFT, 4→2 problems for GRPO)
- Low baseline performance (<5% pass@1) → Switch to StarCoderBase-1B
- Reward degeneration → Early stop, report partial results

### Strategy 3: Retry with Backoff
- Network failures (dataset download) → 3 retries with exponential backoff
- Timeout errors (sandbox) → Mark as failed, continue with next sample

### Strategy 4: Partial Results Preservation
- Pipeline abort → Save completed checkpoints
- Evaluation failure → Save partial results (e.g., only SFT + Binary evaluated)
- Update verification_state with PARTIAL status

---

## Configuration Management

All hyperparameters centralized in `config.yaml`:

```yaml
model:
  name: "Salesforce/codegen-350M-mono"  # or bigcode/starcoderbase-1b
  precision: "fp16"

lora:
  r: 16
  alpha: 32
  target_modules: ["q_proj", "v_proj"]

sft:
  optimizer: "adamw"
  learning_rate: 2e-5
  epochs: 5
  batch_size: 8

grpo:
  optimizer: "adamw"
  learning_rate: 2e-7
  steps: 500
  samples_per_problem: 4
  kl_coef: 0.1

sandbox:
  timeout: 3.0
  error_categories:
    - {type: "SyntaxError", reward: 0.0}
    - {type: "TypeError", reward: 0.2}
    - {type: "NameError", reward: 0.4}
    - {type: "ValueError", reward: 0.6}
    - {type: "AssertionError", reward: 0.8}

evaluation:
  temperature: 0.0
  max_tokens: 512
  stop_tokens: ["\n\n", "def ", "class "]

gate:
  absolute_threshold: 8.0
  retention_threshold: 0.80

reproducibility:
  seed: 42
```

---

## Integration Points

### HuggingFace Hub
- Pretrained models: `Salesforce/codegen-350M-mono`, `bigcode/starcoderbase-1b`
- Dataset: `openai/openai_humaneval`
- Authentication: Not required (all resources public)

### OpenAI Human-Eval Harness
- GitHub: `git+https://github.com/openai/human-eval`
- API: `evaluate_functional_correctness(samples_file)`
- Input format: JSONL with {task_id, completion}

### Verification State File
- Path: `docs/youra_research/verification_state.yaml`
- Fields updated: `sub_hypotheses.h-e1.gate.satisfied`, `sub_hypotheses.h-e1.validation.result`
- Update method: YAML load → modify → dump (atomic write)

---

## Testing Strategy

### Unit Tests (Per Component)
- Dataset Loader: Verify 164 problems loaded, prompt format correct
- Model Manager: Verify LoRA config applied, reference model frozen
- Execution Sandbox: Verify timeout enforced, error categories correct
- Training Engine: Verify loss decreases, checkpoints saved
- Evaluator: Verify pass@1 computation correct
- Validator: Verify gate threshold arithmetic correct

### Integration Test (End-to-End)
- Run pipeline on minimal dataset (10 problems)
- Verify all stages complete without errors
- Verify output files created (checkpoints, figures, state update)

### Acceptance Test (Full Experiment)
- Run pipeline on full HumanEval (164 problems)
- Verify gate metrics computed correctly
- Verify state file updated with final result

---

## File Structure

```
h-e1/
├── code/
│   ├── run_experiment.py      # Orchestrator (main entry point)
│   ├── dataset.py              # Dataset Loader
│   ├── model.py                # Model Manager
│   ├── sandbox.py              # Execution Sandbox
│   ├── train.py                # Training Engine (SFT + GRPO)
│   ├── eval.py                 # Evaluation Pipeline
│   ├── validate.py             # Validation Reporter
│   ├── config.yaml             # Hyperparameters
│   └── requirements.txt        # Dependencies
├── checkpoints/
│   ├── sft/                    # SFT baseline checkpoint
│   ├── binary/                 # GRPO Binary checkpoint
│   └── error_type/             # GRPO Error-Type checkpoint
├── figures/
│   ├── gate_metrics.png
│   ├── training_curves.png
│   └── reward_distribution.png
└── logs/
    └── experiment.log          # Training logs
```

---

**Architecture Version:** 1.0  
**Next Steps:** Logic design (03_logic.md), Configuration schema (03_config.md), Task breakdown (03_tasks.yaml)
