# Architecture: H-E1 (EXISTENCE / PoC)

**Hypothesis:** FGO token masking improves code generation vs Standard PPO, across 3 feedback types (compile/test/combined)
**Tier:** EXISTENCE — minimal architecture, 4-8 Epic tasks

Applied: No directly relevant KB pattern found (search returned diffusion/LoRA results, not applicable) — architecture based on PRD/brief pseudo-code (StepCoder FGO + TRL PPOTrainer).

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field project - no existing code to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch; no base hypothesis, no prior codebase.

---

## File Structure

```
h-e1/code/
  data.py          # HumanEval/MBPP loading + prompt formatting
  execution.py      # sandboxed exec, reward, trace collection, token-line mapping
  fgo.py             # FGO mask construction + masked PPO loss
  model.py           # CodeLlama load + PPOTrainer wrapper (Standard vs FGO)
  train.py           # training loop, 6-condition factorial runner
  evaluate.py         # pass@1 / pass@10 on HumanEval + MBPP
  config.py           # fixed hyperparams (PRD FR-4)
  visualize.py         # 2x3 bar chart + training curves
```

## Modules

### data.py

**Dependencies**: none

```python
def load_humaneval() -> list[dict]: ...          # 164 problems
def load_mbpp() -> list[dict]: ...                 # indices 11-510, 500 problems
def format_prompt(problem: dict) -> str: ...
```

### execution.py

**Dependencies**: data.py

```python
def collect_execution_trace(code: str, test_cases: list[str]) -> set[int]: ...  # sys.settrace line numbers
def map_tokens_to_lines(token_ids: Tensor, code: str, tokenizer) -> list[int]: ...
def compute_reward(code: str, test_cases: list[str], feedback_type: str) -> float: ...
    # feedback_type in {"compile", "test", "combined"}; values per PRD FR-4.5
def check_compiles(code: str) -> bool: ...
```

### fgo.py

**Dependencies**: execution.py

```python
def create_fgo_mask(token_ids: Tensor, token_to_line: list[int], executed_lines: set[int]) -> Tensor: ...
def fgo_ppo_loss(logprobs: Tensor, old_logprobs: Tensor, advantages: Tensor,
                  mask: Tensor, clip_eps: float = 0.2) -> Tensor: ...
def standard_ppo_loss(logprobs: Tensor, old_logprobs: Tensor, advantages: Tensor,
                       clip_eps: float = 0.2) -> Tensor: ...  # mask=ones equivalent
def verify_fgo_mechanism(mask: Tensor, logprobs: Tensor) -> None: ...  # asserts + log line
```

### model.py

**Dependencies**: fgo.py

```python
def load_policy_model(model_id: str = "meta-llama/CodeLlama-7b-Instruct-hf") -> tuple: ...  # (model, tokenizer)
def build_ppo_trainer(model, tokenizer, use_fgo: bool) -> "PPOTrainer": ...  # trl.PPOTrainer wrapper
```

### train.py

**Dependencies**: data.py, execution.py, fgo.py, model.py, config.py

```python
def train_condition(condition: str, feedback_type: str, use_fgo: bool,
                     problems: list[dict], cfg: "Config") -> dict: ...  # returns run metrics/paths
def run_factorial_experiment(cfg: "Config") -> dict: ...  # loops 6 conditions (FR-7.1-7.6)
```

### evaluate.py

**Dependencies**: data.py, execution.py, model.py

```python
def generate_samples(model, tokenizer, problems: list[dict], n: int = 10) -> list[dict]: ...
def pass_at_k(samples: list[dict], k: int) -> float: ...
def evaluate_condition(model_path: str, dataset: str) -> dict: ...  # {"pass@1":.., "pass@10":..}
```

### config.py

**Dependencies**: none

```python
class Config:
    lr: float = 3e-6
    weight_decay: float = 0.01
    batch_size: int = 64
    per_device_batch: int = 16
    grad_accum: int = 4
    episodes: int = 10_000
    seed: int = 1
    model_id: str = "meta-llama/CodeLlama-7b-Instruct-hf"
```

### visualize.py

**Dependencies**: evaluate.py

```python
def plot_gate_metrics(results: dict) -> None: ...       # 2x3 bar chart -> figures/
def plot_training_curves(logs: dict) -> None: ...
def plot_masking_stats(logs: dict) -> None: ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data pipeline | Load HumanEval (164) + MBPP (500) via `human_eval`/`datasets` | 6 | 2+1+1+2 |
| A-2 | Execution sandbox + reward | exec-based sandbox, reward per feedback type, compile check | 9 | 3+2+2+2 |
| A-3 | Trace collection + token-line mapping | `sys.settrace`, map tokens to source lines | 8 | 2+2+3+1 |
| A-4 | FGO mask + masked PPO loss | mask construction, masked/standard loss fns, verify mechanism | 10 | 3+2+3+2 |
| A-5 | Model + PPOTrainer wrapper | load CodeLlama-7B, wrap TRL PPOTrainer for both conditions | 9 | 3+3+2+1 |
| A-6 | Training loop (single condition) | run PPO training for one (mask, feedback) pair, checkpointing | 9 | 3+2+2+2 |
| A-7 | 2x3 factorial runner | loop 6 conditions, orchestrate train+eval, aggregate results | 7 | 2+3+1+1 |
| A-8 | Evaluation + visualization | pass@1/pass@10 harness, 2x3 bar chart + curves | 7 | 2+2+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-4, A-5, A-6], Low(4-8): [A-1, A-3, A-7, A-8]

---

## Notes (EXISTENCE constraints)

- No LoRA/PEFT module — full fine-tune per brief (optional peft dep unused unless OOM).
- No curriculum/ablation infra beyond the required 6 conditions (FR-7).
- Single seed (seed=1), no multi-seed orchestration.
