# Architecture: H-E1 (EXISTENCE PoC)

**Hypothesis:** IFEval constraint satisfaction rate as continuous reward signal for RLHF
**Type:** EXISTENCE — minimal architecture, 4 files, no ablation modules

Applied: reward-model-wrapper-pattern (nn.Module reward head over frozen policy outputs)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - no existing code to analyze (no `h-e1/code/` or `src/` present)
**Analyzed Path:** N/A
**Findings:** New implementation from scratch

---

## File Structure

```
h-e1/code/
├── config.py       # fixed experiment config
├── model.py         # IFEvalRewardSignal (baseline binary + proposed soft scoring)
├── data.py          # IFEval loading + constraint parsing
├── train.py          # generation + reward computation driver (no optimization)
└── evaluate.py       # metrics + figures
```

---

## Modules

### Config (`config.py`)

**Dependencies**: none

```python
@dataclass
class Config:
    dataset_id: str = "google/IFEval"
    model_id: str = "mistralai/Mistral-7B-Instruct-v0.2"
    temperature: float = 0.7
    seed: int = 1
    soft_margin: float = 0.1
    output_dir: str = "h-e1/figures"
```

### Data (`data.py`)

**Dependencies**: Config, datasets

```python
def load_ifeval(cfg: Config) -> list[dict]: ...
def parse_constraints(example: dict) -> list[dict]: ...
```

### Model (`model.py`)

**Dependencies**: torch, transformers

```python
class BaselineChecker:
    """Binary constraint satisfaction (hard 0/1), for comparison."""
    def check(self, response: str, constraints: list[dict]) -> float: ...

class IFEvalRewardSignal(nn.Module):
    def __init__(self, soft_margin: float = 0.1): ...
    def check_length_constraint(self, text: str, target: int, op: str) -> float: ...
    def check_keyword_constraint(self, text: str, keyword: str, must_include: bool) -> float: ...
    def check_format_constraint(self, text: str, fmt: str) -> float: ...
    def check_structural_constraint(self, text: str, spec: dict) -> float: ...
    def forward(self, response: str, constraints: list[dict]) -> torch.Tensor: ...

def load_generator(cfg: Config):
    """AutoModelForCausalLM + tokenizer, standard HF loading."""
    ...

def generate_responses(model, tokenizer, prompts: list[str], cfg: Config) -> list[str]: ...
```

### Train (`train.py`)

**Dependencies**: Config, data, model

```python
def run(cfg: Config) -> dict:
    """
    1. load_ifeval -> prompts + constraints
    2. generate_responses (batched)
    3. IFEvalRewardSignal.forward per prompt -> rewards tensor
    4. rewards.sum().backward() -> verify grad flow
    Returns: {"rewards": Tensor[541], "per_constraint": dict}
    """
    ...
```

### Evaluate (`evaluate.py`)

**Dependencies**: matplotlib, train output

```python
def check_gate_metrics(results: dict) -> dict:
    """score range [0,1], variance>0, grad flow bool"""
    ...
def plot_score_distribution(rewards: torch.Tensor, out_dir: str) -> None: ...
def plot_per_constraint_breakdown(per_constraint: dict, out_dir: str) -> None: ...
def plot_gate_comparison(gate_results: dict, out_dir: str) -> None: ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config + IFEval data loading | `config.py`, `data.py`: load dataset, parse 25 constraint types into unified dict schema | 9 | 3+2+2+2 |
| A-2 | Response generation | Load Mistral-7B-Instruct, batch generate 541 responses at temp=0.7, seed=1 | 8 | 2+3+1+2 |
| A-3 | Baseline binary checker | `BaselineChecker`: hard pass/fail per constraint (reference for comparison) | 5 | 2+1+1+1 |
| A-4 | Soft reward module (core mechanism) | `IFEvalRewardSignal`: length/keyword/format/structural soft checks, tensor output with grad | 12 | 3+2+4+3 |
| A-5 | Training driver | `train.py`: wire data+model, aggregate rewards, run backward() for grad verification | 6 | 2+3+1+0 |
| A-6 | Evaluation + gate check | `evaluate.py` gate metrics: range, variance, grad-flow boolean checks | 5 | 2+1+1+1 |
| A-7 | Visualization | Score histogram, per-constraint bar chart, gate comparison bar chart | 6 | 2+1+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-1, A-2, A-4], Low(4-8): [A-3, A-5, A-6, A-7]
