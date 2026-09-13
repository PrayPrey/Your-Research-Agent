# Architecture: H-E1 (EXISTENCE PoC)

**Hypothesis:** Unified Phi-Mamba framework supports both MOHAWK (matrix) and CAB (token) distillation objectives.

Applied: No relevant KB pattern found (search returned unrelated diffusers docs) — design follows PRD/brief spec directly.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; will vendor minimal pieces from `goombalab/phi-mamba` (Mamba-2 mixer + transfer matrix) as static code, no external repo dependency at runtime.

---

## File Organization

- `code/config.py` — single fixed config (dataclass)
- `code/data.py` — C4 streaming dataloader
- `code/model.py` — Teacher wrapper, Phi-Mamba student (Mamba-2 mixer), CAB bridges
- `code/objectives.py` — MOHAWK loss + CAB loss (switchable)
- `code/train.py` — training loop for both objectives, metrics, NaN checks
- `code/evaluate.py` — loss curve plotting, gate criteria check
- `figures/` — output plots

---

## Modules

### Config (`code/config.py`)

**Dependencies**: None

```python
@dataclass
class ExperimentConfig:
    teacher_name: str = "microsoft/phi-1_5"
    seq_len: int = 2048
    batch_size: int = 8
    grad_accum: int = 4
    num_layers: int = 24
    lr_stage12: float = 1e-4
    lr_stage3: float = 5e-5
    warmup_steps: int = 1000
    grad_clip: float = 1.0
    seed: int = 42
    total_tokens: int = 100_000_000
```

### Data (`code/data.py`)

**Dependencies**: Config

```python
def get_dataloader(config: ExperimentConfig, tokenizer) -> Iterator[dict]: ...
def tokenize_batch(examples: dict, tokenizer, seq_len: int) -> dict: ...
```

### Model (`code/model.py`)

**Dependencies**: Config

```python
class Teacher:
    def __init__(self, config: ExperimentConfig): ...
    def forward(self, input_ids: Tensor) -> "TeacherOutput":  # attentions, hidden_states, k_proj, q_proj
        ...

class PhiMambaLayer(nn.Module):
    def __init__(self, hidden_size: int, num_heads: int, d_state: int): ...
    def forward(self, hidden_states: Tensor, return_mixer_matrix: bool = False,
                return_bc: bool = False) -> dict:  # {"hidden_states", "transfer_matrix"?, "B"?, "C"?}
        ...

class PhiMambaStudent(nn.Module):
    def __init__(self, config: ExperimentConfig): ...
    def forward(self, hidden_states: Tensor, layer_idx: int, **kwargs) -> dict: ...

class Bridge(nn.Module):
    def __init__(self, d_state: int, d_head: int): ...
    def forward(self, x: Tensor) -> Tensor: ...
```

### Objectives (`code/objectives.py`)

**Dependencies**: Model

```python
def mohawk_loss(teacher_out, student_layer_out, stage: int) -> Tensor: ...
def cab_loss(teacher_K: Tensor, teacher_Q: Tensor, B: Tensor, C: Tensor,
             phi_B: Bridge, phi_C: Bridge) -> Tensor: ...

class UnifiedDistillationFramework:
    def __init__(self, teacher: Teacher, student: PhiMambaStudent, objective_type: str): ...
    def compute_loss(self, input_ids: Tensor, layer_idx: int, stage: int) -> Tensor: ...
```

### Train (`code/train.py`)

**Dependencies**: Config, Data, Model, Objectives

```python
def run_stage(framework, dataloader, config, stage: int, token_budget: int,
              lr: float, metrics: dict) -> dict: ...
def train_mohawk(framework, dataloader, config) -> dict:  # runs stages 1-3
def train_cab(framework, dataloader, config) -> dict:  # runs stages 1-2
def check_nan_inf(loss: Tensor, grad_norm: float, metrics: dict) -> None: ...
def main() -> None: ...
```

### Evaluate (`code/evaluate.py`)

**Dependencies**: Train (metrics dict)

```python
def plot_loss_curves(matrix_history: list, token_history: list, out_dir: str) -> None: ...
def plot_grad_norm_hist(matrix_norms: list, token_norms: list, out_dir: str) -> None: ...
def check_gate_criteria(metrics: dict) -> dict:  # {"pass": bool, "reasons": [...]}
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup config & data pipeline | ExperimentConfig, C4 streaming loader, tokenization | 8 | 2+2+2+2 |
| A-2 | Teacher model wrapper | Load Phi-1.5, extract attentions/K/Q per layer | 7 | 2+2+1+2 |
| A-3 | Phi-Mamba student + Mamba-2 mixer | Implement layer with transfer_matrix and B/C outputs | 16 | 4+3+5+4 |
| A-4 | CAB bridges (phi_B, phi_C) | MLP modules, MSE alignment loss | 6 | 2+1+2+1 |
| A-5 | MOHAWK loss + 3-stage training | Frobenius loss, hidden-state L2, KL stage | 14 | 3+3+4+4 |
| A-6 | CAB loss + 2-stage training | Bridge training stage, KL distillation stage | 12 | 3+3+3+3 |
| A-7 | Training loop, metrics, NaN guards | Unified loop, grad norm tracking, NaN/Inf counters | 10 | 3+3+2+2 |
| A-8 | Evaluation & figures | Loss curves, grad norm histogram, gate check | 6 | 2+1+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3, A-5], Medium(9-13): [A-1, A-6, A-7], Low(4-8): [A-2, A-4, A-8]
