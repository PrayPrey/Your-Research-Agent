# Architecture: H-M2 (FGO Token Masking for PPO)

**Type:** MECHANISM validation (PPO training + gradient verification)
**Applied:** TRL PPOTrainer custom-loss-masking pattern (no dedicated FGO/StepCoder KB entry found; standard mask-multiply-then-normalize PPO loss pattern used per experiment brief Algorithm 1)

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** H-M1 `code/` folder does not exist yet (only `03_architecture.md` spec present, no implementation to import from). Serena skipped per rules (green-field acceptable — nothing to analyze).
**Analyzed Path:** N/A
**Findings:** New implementation from scratch. H-M2 reimplements trace collection inline (per H-M1 spec: `sys.settrace` + tokenizer `offset_mapping`) since no importable base code exists.

---

## File Organization

```
h-m2/code/
  trace_mask.py          # ExecutionTraceCollector + TokenClassifier (ported from H-M1 spec) -> execution_mask
  fgo_loss.py             # compute_fgo_masked_loss, verify_gradient_exclusion
  masking_conditions.py   # build_mask() dispatch: no_mask / random_mask / trace_mask
  ppo_trainer.py           # PPOTrainerFGO wrapping TRL PPOTrainer with custom loss
  data_loader.py           # HumanEval/MBPP loading
  evaluate.py               # pass@1 execution-based eval
  stats.py                   # paired t-test across seeds
  visualize.py                # required + optional figures
  config.py                    # fixed training/eval config (3 conditions x 3 seeds)
  run_experiment.py             # main entry point, orchestrates train+eval+stats+viz
```

---

## Modules

### ExecutionTraceCollector / TokenClassifier (`trace_mask.py`)

**Dependencies**: stdlib `sys`, transformers tokenizer

```python
class ExecutionTraceCollector:
    def __init__(self): ...
    def collect_trace(self, code_str: str, test_input: str, timeout: float = 5.0) -> set[int]: ...

class TokenClassifier:
    def __init__(self, tokenizer): ...
    def build_execution_mask(self, code_str: str, tokens: list, executed_lines: set[int]) -> torch.Tensor: ...  # [seq_len]
```

### FGO Loss (`fgo_loss.py`)

**Dependencies**: torch

```python
def compute_fgo_masked_loss(
    logits: torch.Tensor, labels: torch.Tensor, execution_mask: torch.Tensor,
    advantages: torch.Tensor, old_log_probs: torch.Tensor, clip_epsilon: float = 0.2
) -> torch.Tensor: ...

def verify_gradient_exclusion(model: nn.Module, loss: torch.Tensor, execution_mask: torch.Tensor) -> dict: ...
    # {"executed_grad_norm": float, "non_executed_grad_norm": float, "gradient_exclusion_verified": bool}
```

### Masking Conditions (`masking_conditions.py`)

**Dependencies**: ExecutionTraceCollector, TokenClassifier

```python
def build_mask(condition: str, tokens: list, code_str: str, test_input: str, seed: int) -> torch.Tensor: ...
    # condition in {"no_mask", "random_mask", "trace_mask"}
    # no_mask -> all ones; random_mask -> matched sparsity to trace_mask; trace_mask -> TokenClassifier output
```

### PPOTrainerFGO (`ppo_trainer.py`)

**Dependencies**: TRL PPOTrainer, fgo_loss, masking_conditions

```python
class PPOTrainerFGO:
    def __init__(self, model, tokenizer, config: dict, condition: str): ...
    def train_step(self, batch: dict) -> dict: ...          # returns {loss, grad_verification}
    def run(self, dataset, num_steps: int, seed: int) -> dict: ...  # returns checkpoint path + logs
```

### Data (`data_loader.py`)

**Dependencies**: datasets, transformers

```python
def load_problems() -> list[dict]: ...  # HumanEval(164) + MBPP test(500)
```

### Evaluation (`evaluate.py`)

**Dependencies**: subprocess (sandboxed exec)

```python
def evaluate_pass_at_k(model, tokenizer, dataset: list[dict], k: int = 1, num_samples: int = 1) -> float: ...
def execute_tests(code: str, tests: str, timeout: float = 5.0) -> bool: ...
```

### Stats (`stats.py`)

**Dependencies**: scipy.stats

```python
def paired_ttest(trace_scores: list[float], random_scores: list[float]) -> dict: ...  # {t_stat, p_value}
```

### Visualization (`visualize.py`)

**Dependencies**: matplotlib

```python
def plot_gate_metrics(results: dict) -> None: ...          # required: pass@1 bar chart, 3 conditions
def plot_gradient_distribution(grad_logs: dict) -> None: ...
def plot_learning_curves(training_logs: dict) -> None: ...
def plot_masking_coverage(mask_stats: dict) -> None: ...
```

### Orchestration (`run_experiment.py`)

**Dependencies**: all modules above

```python
def main(config_path: str = "config.py") -> None: ...
    # for condition in [no_mask, random_mask, trace_mask]:
    #   for seed in [42, 123, 456]: train -> eval -> log grad verification
    # stats.paired_ttest(trace, random); visualize.*; gate check
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data loading | Load HumanEval(164) + MBPP(500) test splits | 5 | 2+1+1+1 |
| A-2 | Trace + token classifier | Port H-M1 sys.settrace + offset_mapping mask builder | 9 | 2+2+3+2 |
| A-3 | FGO masked loss | Implement compute_fgo_masked_loss per Algorithm 1 | 8 | 2+1+3+2 |
| A-4 | Gradient verification | verify_gradient_exclusion: hook grads, assert masked=0, unmasked>0 | 9 | 2+2+2+3 |
| A-5 | Masking conditions dispatch | no_mask / random_mask (sparsity-matched) / trace_mask | 6 | 2+2+1+1 |
| A-6 | PPOTrainerFGO wrapper | Wrap TRL PPOTrainer, inject custom loss + mask per batch | 12 | 3+3+3+3 |
| A-7 | Training loop x3 conditions x3 seeds | Run 1000-step PPO for 9 (condition,seed) combos, checkpoint | 10 | 2+3+2+3 |
| A-8 | Evaluation pipeline | pass@1 via sandboxed execution on 664 problems | 8 | 2+2+2+2 |
| A-9 | Statistical comparison | Paired t-test trace vs random across 3 seeds, p<0.05 gate | 4 | 1+1+1+1 |
| A-10 | Visualization | 4 figures: gate bar chart, gradient histogram, learning curves, mask coverage | 6 | 2+1+1+2 |
| A-11 | Pipeline orchestration + gate check | Wire all modules, run full pipeline, compute PASS/FAIL | 7 | 2+3+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-6], Medium(9-13): [A-2, A-4, A-7], Low(4-8): [A-1, A-3, A-5, A-8, A-9, A-10, A-11]

---

## Notes

- H-M1 code folder not present; trace/token-mapping logic reimplemented in `trace_mask.py` following H-M1's spec (`sys.settrace` + tokenizer `offset_mapping`), no import dependency.
- Sandboxed exec via subprocess with timeout for both trace collection and eval, consistent with H-M1 safety pattern.
- Fixed seeds {42,123,456} per NFR-2; 1000 steps, batch 16, ctx 4096 per NFR-1.
