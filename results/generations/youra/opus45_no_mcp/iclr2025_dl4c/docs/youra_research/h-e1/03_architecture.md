# Architecture: h-e1 (Error-Type Gating) — EXISTENCE PoC

**Applied:** RLTF multi-granularity reward pattern (paper equations 4-5) with error-type gating extension.

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field project - no existing code to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch, following RLTF paper structure (no local base hypothesis code, no existing src/).

---

## File Structure (Minimal — EXISTENCE tier)

```
h-e1/code/
  data.py          # APPS loading + tokenization
  reward.py        # error classification + gated reward calculator
  model.py         # CodeT5-large wrapper + PPO policy/value heads
  train.py         # PPO training loop, runs both conditions (fine_always, fine_gated)
  evaluate.py       # pass@1 execution-based eval + steps-to-30% tracking
  config.py         # single fixed config (seed=42, hyperparams)
  visualize.py       # 4 required figures
h-e1/figures/
h-e1/results/
```

---

## Module Interfaces

### data.py

**Dependencies**: config.py

```python
def load_apps(split: str, n: int) -> list[dict]: ...  # HF codeparrot/apps
def tokenize_batch(problems: list[dict], tokenizer) -> dict: ...
```

### reward.py

**Dependencies**: none (pure functions, executes generated code in sandbox)

```python
U_LINE_ERRORS: set[str]
U_IGNORE_ERRORS: set[str]

def execute_code_safely(code: str, test_cases: list) -> tuple[str, str | None]: ...  # (PASS/FAIL, traceback)
def classify_error(traceback_str: str) -> str: ...  # 'U_line' | 'U_ignore'
def parse_traceback_line(traceback_str: str) -> int: ...
def compute_gated_reward(code_tokens: list, traceback: str | None, gating: str) -> "Tensor": ...
    # gating: 'fine_always' | 'fine_gated'
```

### model.py

**Dependencies**: config.py

```python
class PolicyModel:
    def __init__(self, pretrained: str = "Salesforce/codet5-large"): ...
    def generate(self, prompt: str) -> str: ...
    def forward(self, input_ids, decoder_input_ids) -> "logits": ...

class ValueHead:
    def __init__(self, hidden_size: int = 1024): ...
    def forward(self, hidden_states) -> "value": ...
```

### train.py

**Dependencies**: data.py, reward.py, model.py, config.py, evaluate.py

```python
def ppo_step(policy: PolicyModel, value: ValueHead, batch: dict, gating: str) -> dict: ...  # returns loss dict
def run_condition(gating: str, seed: int = 42) -> dict: ...  # returns {steps_to_30pct, pass@1_curve}
def main(): ...  # runs both fine_always and fine_gated sequentially
```

### evaluate.py

**Dependencies**: data.py, model.py

```python
def compute_pass_at_1(model: PolicyModel, test_problems: list[dict]) -> float: ...
def track_steps_to_threshold(pass_at_1_log: list[tuple[int, float]], threshold: float = 0.30) -> int | None: ...
```

### visualize.py

**Dependencies**: results from train.py/evaluate.py (reads results/*.json)

```python
def plot_gate_metrics_comparison(steps_gated: int, steps_always: int, path: str): ...  # required figure
def plot_training_curves(curves: dict, path: str): ...
def plot_error_distribution(error_counts: dict, path: str): ...
def plot_efficiency_ratio(steps_gated: int, steps_always: int, path: str): ...
```

### config.py

```python
SEED = 42
MODEL_NAME = "Salesforce/codet5-large"
LR = 5e-5
BATCH_SIZE = 8
TOTAL_STEPS = 50_000
WARMUP_STEPS = 500
MAX_INPUT_LEN = 512
MAX_OUTPUT_LEN = 256
PASS_THRESHOLD = 0.30
```

---

## Data Flow

```
APPS dataset (data.py)
  -> tokenized batch
  -> PolicyModel.generate (model.py) -> candidate code
  -> execute_code_safely (reward.py) -> PASS/traceback
  -> classify_error + compute_gated_reward (reward.py)
       [gating='fine_always' -> RLTF default fine-grained]
       [gating='fine_gated'  -> proposed: coarse-only if U_ignore]
  -> ppo_step (train.py): policy + value loss update
  -> periodic evaluate.compute_pass_at_1 -> log (step, pass@1)
  -> track_steps_to_threshold per condition
  -> visualize.py reads both conditions' logs -> 4 figures
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data pipeline | Load APPS 5K/5K, tokenize with CodeT5 tokenizer | 6 | 2+1+2+1 |
| A-2 | Sandbox execution | Safe code exec + test case runner | 9 | 3+2+3+1 |
| A-3 | Error classification | classify_error + parse_traceback_line, U_line/U_ignore sets | 5 | 2+1+1+1 |
| A-4 | Gated reward calculator | compute_gated_reward, both gating modes | 8 | 2+2+3+1 |
| A-5 | Model + PPO core | CodeT5-large policy/value heads, ppo_step | 12 | 3+3+4+2 |
| A-6 | Training loop (2 conditions) | run_condition for fine_always & fine_gated, seed=42 | 10 | 3+3+3+1 |
| A-7 | Evaluation + threshold tracking | pass@1 execution eval, steps-to-30% | 7 | 2+2+2+1 |
| A-8 | Visualization | 4 figures incl. required gate metrics comparison | 5 | 1+1+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-4, A-5, A-6], Low(4-8): [A-1, A-3, A-7, A-8]

**Total tasks: 8 (within LIGHT tier max 15, 4-8 epics range)**

---

## Self-Validation

- No ASCII diagrams (text arrows only) - OK
- Interface-only module code - OK
- 8 epic tasks with complexity - OK
- Green-field: Serena skip documented - OK
