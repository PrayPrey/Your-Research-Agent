# Logic: H-E1 (EXISTENCE PoC)

**Hypothesis:** IFEval constraint satisfaction as continuous, differentiable reward signal

Applied: reward-model-wrapper-pattern (nn.Module scoring head over frozen policy text outputs)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-4: IFEvalRewardSignal [Complexity: 12, Budget: 2]

**Applied**: soft-scoring-via-sigmoid-margin (differentiable relaxation of hard boolean checks)

### API Signatures

```python
class IFEvalRewardSignal(nn.Module):
    def __init__(self, soft_margin: float = 0.1):
        """soft_margin controls sigmoid steepness for soft thresholds."""
        ...

    def check_length_constraint(self, text: str, target: int, op: str) -> torch.Tensor:
        """op in {'at_least','at_most','exactly'}. Returns scalar tensor [1] in [0,1]."""
        ...

    def check_keyword_constraint(self, text: str, keyword: str, must_include: bool) -> torch.Tensor:
        """Returns scalar tensor [1] in [0,1]."""
        ...

    def check_format_constraint(self, text: str, fmt: str) -> torch.Tensor:
        """fmt e.g. 'json','bullet_list','markdown_heading'. Returns scalar tensor [1]."""
        ...

    def check_structural_constraint(self, text: str, spec: dict) -> torch.Tensor:
        """spec e.g. {'type':'num_paragraphs','count':3}. Returns scalar tensor [1]."""
        ...

    def forward(self, response: str, constraints: list[dict]) -> torch.Tensor:
        """
        response: single generated string
        constraints: list of {'type': str, **params} (from parse_constraints)
        Returns: reward tensor [1], mean of per-constraint scores, requires_grad=True
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| per-check output | [1] | scalar tensor per constraint |
| forward() output | [1] | mean over constraints, one prompt |
| rewards (train.py) | [541] | stacked across dataset |

### Pseudo-code (soft scoring core)

```
# Convert discrete measurement into differentiable [0,1] score via sigmoid margin.
def soft_threshold(value: float, target: float, op: str, margin: float) -> Tensor:
    diff = (value - target) if op == "at_least" else (target - value)
    if op == "exactly":
        diff = margin - abs(value - target)
    return sigmoid(diff / margin)   # [1], differentiable proxy for hard >=/<=/==

forward(response, constraints):
    scores = []
    for c in constraints:
        dispatch by c['type'] to check_length/check_keyword/check_format/check_structural
        scores.append(score)  # each [1]
    return torch.stack(scores).mean()  # [1], requires_grad via sigmoid ops
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A4-1 | Soft check primitives | length/keyword/format/structural checkers using `soft_threshold` (sigmoid-based), each returns grad-carrying `torch.Tensor([1])` built from float ops (avoid `.item()`/python bool short-circuits that break autograd) |
| L-A4-2 | forward() aggregation | dispatch per constraint type, `torch.stack(scores).mean()`; assert `output.requires_grad` |

---

## A-1: Config + IFEval Data Loading [Complexity: 9]

**Applied**: dataclass-config + HF-datasets-standard-loader

```python
def load_ifeval(cfg: Config) -> list[dict]:
    """datasets.load_dataset(cfg.dataset_id, split='train'). Returns 541 raw examples."""
    ...

def parse_constraints(example: dict) -> list[dict]:
    """
    Maps IFEval's instruction_id_list/kwargs into unified schema:
    [{'type': 'length'|'keyword'|'format'|'structural', **params}, ...]
    """
    ...
```

No subtask breakdown needed (medium complexity, straightforward I/O).

---

## A-2: Response Generation [Complexity: 8]

**Applied**: HF-AutoModelForCausalLM-standard-generate

```python
def load_generator(cfg: Config) -> tuple[PreTrainedModel, PreTrainedTokenizer]:
    """AutoModelForCausalLM.from_pretrained(cfg.model_id), AutoTokenizer likewise."""
    ...

def generate_responses(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    prompts: list[str],
    cfg: Config,
) -> list[str]:
    """Batched model.generate(do_sample=True, temperature=cfg.temperature). Returns len(prompts) strings."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, T] | tokenized batch |
| generated_ids | [B, T+G] | includes prompt + new tokens |

---

## A-3, A-5, A-6, A-7: Low Complexity — Signatures Only

```python
class BaselineChecker:
    def check(self, response: str, constraints: list[dict]) -> float:
        """Hard 0/1 pass rate, mean over constraints. No grad."""
        ...

def run(cfg: Config) -> dict:
    """
    1. load_ifeval(cfg) -> prompts, constraints[541]
    2. generate_responses(...) -> responses[541]
    3. IFEvalRewardSignal()(response, constraints) per prompt -> rewards[541]
    4. rewards.sum().backward()
    Returns {'rewards': Tensor[541], 'per_constraint': dict[str, list[float]]}
    """
    ...

def check_gate_metrics(results: dict) -> dict:
    """Returns {'range_ok': bool, 'variance': float, 'grad_flow_ok': bool}."""
    ...

def plot_score_distribution(rewards: torch.Tensor, out_dir: str) -> None: ...
def plot_per_constraint_breakdown(per_constraint: dict, out_dir: str) -> None: ...
def plot_gate_comparison(gate_results: dict, out_dir: str) -> None: ...
```
