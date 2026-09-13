# Architecture: H-E1 (EXISTENCE PoC)

**Applied**: HuggingFace Trainer + REINFORCE fine-tuning pattern (KB relevance low; used CodeRL/self-refine repos from experiment brief instead)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; no base hypothesis or existing `src/`/`code/` directory found.

---

## File Structure (Minimal - EXISTENCE)

```
h-e1/code/
  model.py         # CodeT5+ loading, LoRA wrap, RLCodeTrainer
  refine.py         # self-refine inference protocol
  train.py          # CE + RL training loops, 4-condition orchestration
  evaluate.py        # evalplus pass@1 scoring, interaction effect calc
  config.py          # single fixed hyperparameter config
  visualize.py        # 2x2 bar chart + interaction plot
h-e1/figures/         # output figures
```

---

## Modules

### config.py

```python
@dataclass
class Config:
    model_id: str = "Salesforce/codet5p-220m"
    lora_r: int = 16
    lora_target_modules: list = field(default_factory=lambda: ["q_proj","k_proj","v_proj"])
    lr: float = 2e-5
    weight_decay: float = 0.05
    warmup_steps: int = 200
    batch_size: int = 8
    ce_epochs: int = 10
    rl_epochs: int = 5
    refine_k: int = 3
    seed: int = 42
```

### model.py (`h-e1/code/model.py`)

**Dependencies**: config.py, peft, transformers

```python
def load_base_model(cfg: Config) -> tuple[PreTrainedModel, PreTrainedTokenizer]: ...
def wrap_lora(model: PreTrainedModel, cfg: Config) -> PeftModel: ...

class RLCodeTrainer:
    def __init__(self, model, tokenizer, cfg: Config): ...
    def compute_reward(self, code: str, tests: list[str]) -> tuple[float, str]: ...
    def rl_step(self, prompt: str, tests: list[str]) -> float: ...
```

### refine.py (`h-e1/code/refine.py`)

**Dependencies**: model.py

```python
def execute_and_get_feedback(code: str, tests: list[str]) -> tuple[float, str]: ...
def self_refine(model, tokenizer, prompt: str, tests: list[str], k: int = 3) -> str: ...
def single_shot(model, tokenizer, prompt: str) -> str: ...
```

### train.py (`h-e1/code/train.py`)

**Dependencies**: model.py, config.py

```python
def train_ce(model, tokenizer, dataset, cfg: Config) -> PreTrainedModel: ...
def train_rl(model, tokenizer, dataset, cfg: Config) -> PreTrainedModel: ...
def run_all_conditions(cfg: Config) -> dict[str, PreTrainedModel]:
    """Produces {'CE': model, 'RL': model} after CE warmup + RL phase."""
```

### evaluate.py (`h-e1/code/evaluate.py`)

**Dependencies**: refine.py, evalplus

```python
def generate_samples(model, tokenizer, problems: dict, inference_fn) -> dict: ...
def compute_pass_at_1(samples: dict, dataset: str) -> float: ...
def run_2x2_eval(models: dict, cfg: Config) -> dict[str, float]:
    """Returns {'CE-Single':x, 'CE-Refine':x, 'RL-Single':x, 'RL-Refine':x}."""
def interaction_effect(results: dict) -> float: ...
```

### visualize.py (`h-e1/code/visualize.py`)

**Dependencies**: evaluate.py, matplotlib

```python
def plot_2x2_bar(results: dict, out_path: str) -> None: ...
def plot_interaction(results: dict, out_path: str) -> None: ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data + config setup | Load HumanEval+/MBPP+, Config dataclass | 5 | 1+1+1+2 |
| A-2 | Model + LoRA loading | CodeT5+-220M load, LoRA wrap | 6 | 2+2+1+1 |
| A-3 | CE training | CE fine-tune loop, HF Trainer | 8 | 2+2+2+2 |
| A-4 | RL training (RLCodeTrainer) | REINFORCE w/ execution reward, reward logging | 14 | 3+3+4+4 |
| A-5 | Self-refine inference | K=3 refine loop w/ execution feedback | 10 | 2+3+3+2 |
| A-6 | 2x2 evaluation | evalplus pass@1 across 4 conditions | 9 | 2+3+2+2 |
| A-7 | Interaction effect + visualization | Compute effect, bar/interaction plots | 6 | 2+1+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-4], Medium(9-13): [A-5,A-6], Low(4-8): [A-1,A-2,A-3,A-7]

7 tasks — within EXISTENCE range (4-8).
