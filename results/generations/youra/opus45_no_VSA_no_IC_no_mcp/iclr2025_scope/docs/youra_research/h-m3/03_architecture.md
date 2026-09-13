# Architecture: H-M3 (MECHANISM)

**Applied**: Low-rank modulation of SSM Δ/B/C (H-M2 pattern) + KD-style conversion training (KL + MSE + adaptation regularizer)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no code to analyze
**Analyzed Path**: N/A
**Findings**: No `h-m3/code/` exists yet. H-M1/H-M2 results are consumed as config values (rank=32, n_tasks) and task-embedding *design*, not as importable code — no base_hypothesis code folder was provided for either. New implementation from scratch, using `transformers.MambaForCausalLM` as the underlying pretrained backbone.

---

## System Architecture

```
Transformer teacher (BERT-base/GPT-2-small)
        |
        | logits, hidden_states
        v
ConversionTrainer --------> TC-SSM (Mamba-130M + TaskConditionedSSMBlock x24)
        |                          ^
        | KL + MSE + AdaptReg      | task_ids (from H-M1 task taxonomy, n_tasks=8)
        v                          |
   [checkpoint: converted TC-SSM] -+
        |
        v
FewShotEvaluator (k=8,16, SuperGLUE x5 tasks, 3 seeds)
        |
        +--> BaselineRunner (Standard Mamba-130M + LoRA r16/a32)
        +--> Transformer baseline (fine-tuned reference)
        v
   Gate metrics + figures (h-m3/figures/)
```

---

## Module Structure

- `h-m3/code/models/tc_ssm.py` - TaskConditionedSSMBlock, TCSSMForCausalLM
- `h-m3/code/models/baseline_mamba.py` - Standard Mamba + LoRA wrapper
- `h-m3/code/training/conversion_trainer.py` - Transformer -> TC-SSM conversion loop
- `h-m3/code/training/adaptation.py` - Few-shot gradient-step adaptation loop (shared by all 3 model variants)
- `h-m3/code/data/superglue.py` - SuperGLUE loading + k-shot stratified sampling
- `h-m3/code/eval/few_shot_eval.py` - FewShotEvaluator, adaptation-speed measurement
- `h-m3/code/eval/mechanism_check.py` - Activation/verification asserts from experiment brief
- `h-m3/code/config.py` - Config dataclass
- `h-m3/code/visualize.py` - Gate bar chart, learning curves, per-task breakdown
- `h-m3/code/main.py` - Orchestration entrypoint

---

## Module Interfaces

### TaskConditionedSSMBlock (`models/tc_ssm.py`)

**Dependencies**: transformers (MambaBlock internals), torch.nn

```python
class TaskConditionedSSMBlock(nn.Module):
    def __init__(self, d_model: int = 768, d_state: int = 16, rank: int = 32, n_tasks: int = 8): ...
    def forward(self, x: Tensor, task_ids: Tensor) -> Tensor: ...  # (B,L,D), (B,) -> (B,L,D)

class TCSSMForCausalLM(nn.Module):
    def __init__(self, mamba_config: dict, rank: int = 32, n_tasks: int = 8): ...
    def from_pretrained_mamba(cls, model_name: str = "state-spaces/mamba-130m", **kwargs) -> "TCSSMForCausalLM": ...
    def forward(self, input_ids: Tensor, task_ids: Tensor) -> ModelOutput: ...  # .logits, .hidden_states
```

### BaselineMambaLoRA (`models/baseline_mamba.py`)

**Dependencies**: transformers.MambaForCausalLM, peft

```python
def build_baseline_mamba_lora(model_name: str = "state-spaces/mamba-130m", r: int = 16, alpha: int = 32) -> PeftModel: ...
```

### ConversionTrainer (`training/conversion_trainer.py`)

**Dependencies**: TCSSMForCausalLM, transformer teacher (AutoModelForCausalLM)

```python
class ConversionTrainer:
    def __init__(self, teacher: nn.Module, student: TCSSMForCausalLM,
                 kl_weight: float = 1.0, mse_weight: float = 0.5, adapt_reg_weight: float = 0.1): ...
    def compute_loss(self, batch: dict, task_ids: Tensor) -> Tensor: ...  # KL(logits) + MSE(hidden) + adapt_reg
    def adaptation_regularizer(self, student: TCSSMForCausalLM, task_ids: Tensor) -> Tensor: ...  # penalizes collapse of modulation across tasks
    def train(self, dataloader, steps: int) -> TCSSMForCausalLM: ...
```

### AdaptationLoop (`training/adaptation.py`)

**Dependencies**: torch.optim.AdamW

```python
def run_few_shot_adaptation(
    model: nn.Module, support_set: dict, task_id: int,
    max_steps: int = 100, lr: float = 2e-5, batch_size: int = 8,
) -> dict: ...  # {"steps_to_95pct": int, "final_acc": float, "curve": list[float]}
```

### SuperGLUEData (`data/superglue.py`)

**Dependencies**: datasets (HF)

```python
TASKS = ["boolq", "cb", "copa", "rte", "wic"]

def load_superglue_task(task: str) -> dict: ...  # {"train":..., "validation":...}
def stratified_k_shot(dataset, k: int, seed: int) -> dict: ...
```

### FewShotEvaluator (`eval/few_shot_eval.py`)

**Dependencies**: AdaptationLoop, sklearn.metrics, evaluate

```python
class FewShotEvaluator:
    def __init__(self, tasks: list[str] = TASKS, k_shots: list[int] = [8, 16], seeds: list[int] = [1, 2, 3]): ...
    def evaluate_model(self, model_builder: Callable, task_ids_map: dict) -> dict: ...
        # -> {task: {k: {"acc_mean": float, "acc_std": float, "steps_to_95pct": float}}}
    def compare_models(self, results: dict[str, dict]) -> dict: ...  # gap vs transformer baseline
```

### MechanismCheck (`eval/mechanism_check.py`)

**Dependencies**: torch

```python
def verify_mechanism_activation(model: TCSSMForCausalLM, batch: dict) -> bool: ...  # per brief's verify_mechanism_activation
def log_activation(task_id: int) -> None: ...  # "TC-SSM: Task conditioning applied, task_id={id}"
```

### Config (`config.py`)

```python
@dataclass
class Config:
    base_model: str = "state-spaces/mamba-130m"
    teacher_model: str = "bert-base-uncased"
    d_model: int = 768
    d_state: int = 16
    rank: int = 32          # from H-M2
    n_tasks: int = 8        # from H-M1
    lora_r: int = 16
    lora_alpha: int = 32
    conversion_steps: int = 2000
    adapt_max_steps: int = 100
    adapt_lr: float = 2e-5
    adapt_batch_size: int = 8
    grad_clip: float = 1.0
    dropout: float = 0.1
    seeds: tuple = (1, 2, 3)
    checkpoint_every: int = 25
```

### Visualizer (`visualize.py`)

**Dependencies**: matplotlib

```python
def plot_gate_comparison(tc_ssm_acc: float, transformer_acc: float, std_mamba_acc: float, out_path: str) -> None: ...
def plot_learning_curves(curves: dict[str, list[float]], out_path: str) -> None: ...
def plot_per_task_breakdown(results: dict, out_path: str) -> None: ...
def plot_adaptation_speed(steps_to_95: dict[str, float], out_path: str) -> None: ...
```

---

## Data Flow

1. `superglue.py` loads SuperGLUE (BoolQ/CB/COPA/RTE/WiC), builds stratified 8-/16-shot support sets + full validation sets.
2. `conversion_trainer.py`: teacher (BERT-base/GPT-2-small) + student (`TCSSMForCausalLM.from_pretrained_mamba`) trained jointly with task_ids sampled per batch; loss = KL(logits) + MSE(hidden) + adaptation_regularizer. Checkpoint every 25 steps.
3. Converted TC-SSM checkpoint passed to `mechanism_check.py` to assert conditioning is active (different task_ids -> different logits, modulation mean > 1e-3).
4. Three model variants prepared for evaluation: TC-SSM (converted), BaselineMambaLoRA (`build_baseline_mamba_lora`), Transformer baseline (fine-tuned reference).
5. `few_shot_eval.py` runs `run_few_shot_adaptation` per (model, task, k, seed) -> accuracy curves + steps-to-95%-ceiling.
6. `compare_models` computes accuracy gap vs transformer and TC-SSM vs Standard-Mamba delta.
7. `visualize.py` renders gate bar chart (mandatory) + learning curves + per-task breakdown + adaptation-speed chart -> `h-m3/figures/`.

---

## Integration Points with Mamba

- `TCSSMForCausalLM.from_pretrained_mamba` loads `state-spaces/mamba-130m` via `transformers.MambaForCausalLM`, then replaces each layer's Mamba mixer with `TaskConditionedSSMBlock`, copying pretrained weights into the wrapped `mamba_block`.
- Modulation injected between `x_proj` (produces raw Δ, B, C) and `dt_proj` — matches brief's identified integration point.
- `forward_with_modulation(x, delta_mod, bc_mod)` is the required extension point on the underlying Mamba mixer; must be implemented as a thin wrapper around the original selective-scan call, additively modulating Δ and (B,C) before the scan.
- LoRA baseline uses `peft.get_peft_model` targeting `out_proj`, `in_proj` — no core Mamba modification needed.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Mamba loading + wrapper scaffold | Load pretrained Mamba-130M, wrap mixer with modulation hook | 10 | 3+2+3+2 |
| A-2 | TaskConditionedSSMBlock | Low-rank Δ/B/C modulation module, rank=32 | 12 | 3+3+3+3 |
| A-3 | Baseline Mamba+LoRA | PEFT LoRA wrapper on standard Mamba | 6 | 1+2+2+1 |
| A-4 | SuperGLUE data + k-shot sampling | 5 tasks, stratified 8/16-shot, full val sets | 8 | 2+2+2+2 |
| A-5 | ConversionTrainer | KL+MSE+adaptation regularizer, teacher-student loop | 15 | 4+4+4+3 |
| A-6 | Mechanism verification | Activation checks, modulation magnitude asserts | 5 | 1+1+2+1 |
| A-7 | Few-shot AdaptationLoop | AdamW, <=100 steps, 3 seeds, curve tracking | 10 | 3+2+3+2 |
| A-8 | FewShotEvaluator + comparison | Run all 3 variants x 5 tasks x 2 k x 3 seeds, gap metrics | 11 | 3+3+3+2 |
| A-9 | Visualization | Gate chart, learning curves, per-task, adaptation-speed | 7 | 2+2+2+1 |
| A-10 | Main entrypoint + config + checkpointing | Wire pipeline, checkpoint every 25 steps, reproducibility | 7 | 2+2+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-5], Medium(9-13): [A-1, A-2, A-4, A-7, A-8], Low(4-8): [A-3, A-6, A-9, A-10]
