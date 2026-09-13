# Logic: H-M3 (Dense Credit Assignment — Convergence Efficiency)

**Applied**: Periodic-evaluation learning-curve pattern (Archon KB search "PPO training loop convergence measurement" returned unrelated diffusers/consistency_models results — no specific pattern found; used standard RL practice from experiment brief).

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M2)
**Status**: API signatures verified from actual H-M2 code (not from 02c_experiment_brief.md pseudo-code, which uses different/incorrect signatures — e.g. brief's `fgo_ppo_loss(model, generated, rewards, masks)` vs actual `fgo_ppo_loss(logprobs, old_logprobs, advantages, mask, clip_eps)`; brief's `evaluate_pass1(model, eval_data)` vs actual `pass_at_k(n, c, k)` + `evaluate_samples(samples, problems_dict, dataset)`).
**Analyzed Path**: `docs/youra_research/h-m2/code/`
**Relevant Symbols**: `fgo.py::{create_fgo_mask, fgo_ppo_loss, standard_ppo_loss}`, `trace_collector.py::ExecutionTraceCollector.collect_trace`, `token_mapper.py::LineToTokenMapper.{map_offsets_to_lines, get_token_line_pairs}`, `evaluate.py::{pass_at_k, evaluate_samples}`, `model.py::{load_policy_model, build_ppo_trainer}`, `data_loader.py::{load_problems, generate_batch_samples}`, `config.py::TRAINING_CONFIG`

**Critical divergence found**: `LineToTokenMapper.map_offsets_to_lines` returns `Dict[int, int]` (token_idx -> line_num), but `create_fgo_mask` expects `token_to_line: List[int]`. Must convert dict to list before calling `create_fgo_mask` (see `_build_token_to_line_list` below). `ExecutionTraceCollector.collect_trace` has no `tokens_to_mask` helper (brief assumed one) — must compose `collect_trace` + `map_offsets_to_lines` + `create_fgo_mask` manually.

---

## External Dependencies (Base Hypothesis)

```python
# From: h-m2/code/fgo.py (ACTUAL CODE)
def create_fgo_mask(token_ids: torch.Tensor, token_to_line: List[int], executed_lines: Set[int]) -> torch.Tensor:
    """mask: [seq_len] float, 1=executed."""

def fgo_ppo_loss(logprobs: Tensor, old_logprobs: Tensor, advantages: Tensor, mask: Tensor, clip_eps: float = 0.2) -> Tensor:
    """All [B, seq_len]. Returns scalar."""

def standard_ppo_loss(logprobs: Tensor, old_logprobs: Tensor, advantages: Tensor, clip_eps: float = 0.2) -> Tensor:
    """calls fgo_ppo_loss with mask=torch.ones_like(logprobs)."""

# From: h-m2/code/trace_collector.py
class ExecutionTraceCollector:
    def collect_trace(self, code_str: str, test_input: str = "", timeout: float = 5.0) -> Set[int]:
        """Executes code_str+test_input under sys.settrace. Returns executed line numbers (1-indexed). Never raises."""

# From: h-m2/code/token_mapper.py
class LineToTokenMapper:
    def __init__(self, tokenizer): ...
    def map_offsets_to_lines(self, code_str: str, offset_mapping: List[Tuple[int,int]]) -> Dict[int, int]:
        """token_idx -> line_num (1-indexed), special tokens excluded."""

# From: h-m2/code/evaluate.py
def pass_at_k(n: int, c: int, k: int) -> float: ...  # unbiased pass@k estimator
def evaluate_samples(samples: List[Dict], problems_dict: Dict[str, Dict], dataset: str = "humaneval") -> Dict[str, float]:
    """samples: [{"task_id":.., "completions": [...]}]. Returns {"pass@1":.., "pass@10":.., "num_problems":.., "details":[...]}"""

# From: h-m2/code/model.py
def load_policy_model(model_id: str = "meta-llama/CodeLlama-7b-Instruct-hf", torch_dtype: str = "float16") -> Tuple: ...  # (model, tokenizer)
def build_ppo_trainer(model, tokenizer, ppo_config=None, ref_model=None) -> PPOTrainer: ...

# From: h-m2/code/data_loader.py
def load_problems(include_humaneval: bool = True, include_mbpp: bool = True) -> List[Dict[str, Any]]: ...  # 664 total (HumanEval 164 + MBPP test 500)
def generate_batch_samples(model, tokenizer, problems, max_new_tokens=512, temperature=0.2, top_p=0.95, seed=42, max_samples=None) -> List[Dict[str, Any]]: ...

# From: h-m2/code/config.py
TRAINING_CONFIG = {"learning_rate": 1e-5, "batch_size": 16, "per_device_batch": 4, "clip_epsilon": 0.2,
                    "gae_lambda": 0.95, "gamma": 1.0, "max_grad_norm": 1.0, "weight_decay": 0.01}
```

**Verified from**: `h-m2/code/*.py` (actual implementation, not brief/spec pseudo-code).

---

## File Organization

```
h-m3/code/
  config.py              # H-M2 TRAINING_CONFIG values + max_steps=5000, eval_interval=100, target_pass1=0.5, seeds=[42,123,456]
  convergence.py          # measure_convergence_efficiency() - core H-M3 mechanism
  train_condition.py       # run_condition(): standard vs fgo loss dispatch, mask building
  data_loader.py             # re-export of H-M2 load_problems/generate_batch_samples
  evaluate.py                  # re-export of H-M2 pass_at_k/evaluate_samples
  stats.py                       # steps_to_target_ratio, learning_curve_slope, sample_efficiency, aggregate_seeds
  visualize.py                    # 1 required + 4 optional figures
  run_experiment.py                 # main entry: 2 conditions x 3 seeds, gate check
```

---

## A-1: Convergence Measurement (`convergence.py`) [Complexity: 11, Budget: 3+2+3+3]

**Applied**: Periodic-evaluation learning-curve pattern (standard RL practice; no specific KB match).

### API Signatures

```python
import torch
from typing import Optional
from h_m2.fgo import fgo_ppo_loss, standard_ppo_loss, create_fgo_mask
from h_m2.trace_collector import ExecutionTraceCollector
from h_m2.token_mapper import LineToTokenMapper
from h_m2.evaluate import pass_at_k, evaluate_samples

def measure_convergence_efficiency(
    model, tokenizer, ppo_trainer,
    train_data: list[dict], eval_data: list[dict],
    fgo_enabled: bool,
    trace_collector: ExecutionTraceCollector,
    token_mapper: LineToTokenMapper,
    max_steps: int = 5000,
    eval_interval: int = 100,
    target_pass1: float = 0.5,
    checkpoint_every: int = 500,
    checkpoint_dir: Optional[str] = None,
    seed: int = 42,
) -> dict:
    """Train with PPO (fgo or standard loss) and track pass@1 every eval_interval steps.

    Returns:
      {steps_to_target: int, final_pass1: float,
       learning_curve: list[(int,float)], loss_curve: list[(int,float)],
       grad_norms: list[dict]}  # grad_norms: first 5 eval points only
    """
    ...

def _build_token_to_line_list(code: str, response_ids: torch.Tensor, token_mapper: LineToTokenMapper) -> list[int]:
    """Dict->List adapter: map_offsets_to_lines returns Dict[int,int]; create_fgo_mask needs List[int]."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| response_ids | [seq_len] | per-sample, ragged (no batch padding, mirrors H-M2 loop) |
| logprobs, old_logprobs, advantages | [B, seq_len] | per PPO minibatch, padded to max seq_len in batch |
| mask | [B, seq_len] | 1=executed (fgo) or all-ones (standard) |
| learning_curve | `list[(step:int, pass1:float)]` | length = max_steps // eval_interval |
| loss_curve | `list[(step:int, loss:float)]` | one entry per training step |

### Pseudo-code

```
measure_convergence_efficiency(...):
    1. learning_curve, loss_curve, grad_norms = [], [], []
    2. steps_to_target = None
    3. for step in range(max_steps):
         batch = sample_batch(train_data, TRAINING_CONFIG["per_device_batch"])
         result = run_condition("fgo" if fgo_enabled else "standard", model, tokenizer,
                                 ppo_trainer, batch, trace_collector, token_mapper)
         loss_curve.append((step, result["loss"].item()))
         if step % eval_interval == 0:
             samples = generate_batch_samples(model, tokenizer, eval_data, seed=seed)
             eval_result = evaluate_samples(
                 [{"task_id": s["id"], "completions": [s["generated_code"]]} for s in samples],
                 {p["id"]: p for p in eval_data})
             pass1 = eval_result["pass@1"]
             learning_curve.append((step, pass1))
             if steps_to_target is None and pass1 >= target_pass1:
                 steps_to_target = step
             if len(grad_norms) < 5:
                 grad_norms.append(result["grad_norms"])
         if checkpoint_dir and step % checkpoint_every == 0:
             torch.save(model.state_dict(), f"{checkpoint_dir}/step_{step}.pt")
    4. return {steps_to_target: steps_to_target or max_steps, final_pass1: learning_curve[-1][1],
               learning_curve, loss_curve, grad_norms}
```

### Subtasks [11/11 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | Training step loop | Sample batch, call run_condition, accumulate loss_curve |
| L-1-2 | Periodic pass@1 eval | Every eval_interval, generate_batch_samples + evaluate_samples on eval_data |
| L-1-3 | steps_to_target tracking | First step where pass1 >= target_pass1 |
| L-1-4 | Checkpointing | torch.save every checkpoint_every steps (NFR-2) |

---

## A-2: Per-Condition Training (`train_condition.py`) [Complexity: 8, Budget: 2+3+2+1]

**Applied**: Standard PyTorch — loss dispatch by condition flag, reusing H-M2 fgo.py verbatim.

### API Signatures

```python
from h_m2.fgo import fgo_ppo_loss, standard_ppo_loss, create_fgo_mask

def run_condition(
    condition: str,  # "standard" | "fgo"
    model, tokenizer, ppo_trainer, batch: dict,
    trace_collector: ExecutionTraceCollector,
    token_mapper: LineToTokenMapper,
    clip_eps: float = 0.2,
) -> dict:
    """Generate responses, compute reward+trace, compute condition loss, backward+step.
    Returns {loss: Tensor (scalar), grad_norms: dict}
    """
    ...
```

### Pseudo-code

```
run_condition(condition, model, tokenizer, ppo_trainer, batch, trace_collector, token_mapper, clip_eps):
    1. responses = generate_batch_samples(model, tokenizer, batch["problems"])   # H-M2 data_loader.py
    2. logprobs, old_logprobs, advantages = ppo_trainer.compute_logprobs_and_advantages(responses)  # [B, seq_len]
    3. if condition == "fgo":
         masks = []
         for sample in responses:
             executed = trace_collector.collect_trace(sample["full_code"], batch.get("test_input", ""))
             token_to_line = _build_token_to_line_list(sample["full_code"], sample["response_ids"], token_mapper)
             masks.append(create_fgo_mask(sample["response_ids"], token_to_line, executed))
         mask = pad_stack(masks)   # [B, seq_len]
         loss = fgo_ppo_loss(logprobs, old_logprobs, advantages, mask, clip_eps)
       else:  # "standard"
         loss = standard_ppo_loss(logprobs, old_logprobs, advantages, clip_eps)
    4. ppo_trainer.optimizer.zero_grad(); loss.backward()
    5. grad_norms = {n: p.grad.norm().item() for n, p in model.named_parameters() if p.grad is not None}
    6. torch.nn.utils.clip_grad_norm_(model.parameters(), TRAINING_CONFIG["max_grad_norm"])
    7. ppo_trainer.optimizer.step()
    8. return {"loss": loss.detach(), "grad_norms": grad_norms}
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | Response generation + logprob/advantage compute | Reuse ppo_trainer internals (TRL) or H-M2 pattern |
| L-2-2 | FGO mask construction per sample | collect_trace + map_offsets_to_lines(dict->list) + create_fgo_mask, batch pad_stack |
| L-2-3 | Loss dispatch + backward | fgo_ppo_loss vs standard_ppo_loss |
| L-2-4 | Grad norm logging | Per-param norm dict, first 5 eval points only (passed up to convergence.py) |

---

## A-3: Data / Eval Re-export (`data_loader.py`, `evaluate.py`) [Complexity: 2, Budget: 1+1]

**Applied**: Thin re-export, no new logic.

```python
# data_loader.py
from h_m2.data_loader import load_problems, generate_batch_samples  # HumanEval 164 + MBPP train 374 / test 500

# evaluate.py
from h_m2.evaluate import pass_at_k, evaluate_samples
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | data_loader re-export | Import-only file |
| L-3-2 | evaluate re-export | Import-only file |

---

## A-4: Statistical Analysis (`stats.py`) [Complexity: 6, Budget: 2+1+2+1]

**Applied**: numpy mean/std aggregation, standard RL learning-curve metrics.

### API Signatures

```python
import numpy as np

def steps_to_target_ratio(fgo_steps: int, standard_steps: int) -> float:
    """FGO/Standard steps-to-target ratio. Success: < 0.6"""
    ...

def learning_curve_slope(curve: list[tuple[int, float]]) -> float:
    """avg pass@1 delta per 100 steps = mean of successive (curve[i+1][1]-curve[i][1])"""
    ...

def sample_efficiency(curve: list[tuple[int, float]], batch_size: int = 16) -> float:
    """pass@1 gain per 1000 samples = (curve[-1][1]-curve[0][1]) / ((curve[-1][0]-curve[0][0])*batch_size/1000)"""
    ...

def aggregate_seeds(results: list[dict]) -> dict:
    """results: per-seed measure_convergence_efficiency() outputs.
    Returns {steps_to_target_mean/std, final_pass1_mean/std}"""
    ...
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | steps_to_target_ratio | Simple division, guard div-by-zero |
| L-4-2 | learning_curve_slope | Mean of successive deltas over curve |
| L-4-3 | sample_efficiency | Normalize delta by total samples seen |
| L-4-4 | aggregate_seeds | np.mean/np.std across 3-seed list of dicts |

---

## A-5: Visualization (`visualize.py`) [Complexity: 6, Budget: 2+1+1+2]

**Applied**: matplotlib line/bar plots (H-M2 visualize.py pattern reused).

### API Signatures

```python
def plot_learning_curve_comparison(fgo_curves: list[list[tuple[int,float]]], standard_curves: list[list[tuple[int,float]]], save_path: str) -> None:
    """Required (FR-6.1). Mean+/-std band across 3 seeds per condition, step on x-axis, pass@1 on y-axis."""
    ...

def plot_steps_to_target_bar(results: dict, save_path: str) -> None:  # FR-6.2
    ...
def plot_sample_efficiency(results: dict, save_path: str) -> None:     # FR-6.3
    ...
def plot_training_loss(fgo_loss: list, standard_loss: list, save_path: str) -> None:
    ...
def plot_gradient_magnitude_hist(grad_logs: dict, save_path: str) -> None:
    ...
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | Learning curve comparison (required) | Mean+std shaded band, 2 conditions |
| L-5-2 | Steps-to-target bar chart | Side-by-side bars per condition |
| L-5-3 | Sample efficiency plot | Bar or line, per 1000 samples |
| L-5-4 | Loss curve + grad histogram | 2 remaining optional figures |

---

## A-6: Orchestration (`run_experiment.py`) [Complexity: 7, Budget: 2+3+1+1]

**Applied**: Standard experiment-runner loop (condition x seed nested loop).

### API Signatures

```python
def main(config_path: str = "config.py") -> None:
    """for condition in ["standard","fgo"]: for seed in [42,123,456]: run + aggregate + gate check."""
    ...
```

### Pseudo-code

```
main():
    1. cfg = load config.py (h_m2.config.TRAINING_CONFIG + h-m3 additions)
    2. problems = load_problems(); train_data, eval_data = split(problems)
    3. results = {"standard": [], "fgo": []}
    4. for condition in ["standard", "fgo"]:
         for seed in cfg.seeds:
             set_seed(seed)
             model, tokenizer = load_policy_model()
             ppo_trainer = build_ppo_trainer(model, tokenizer)
             trace_collector = ExecutionTraceCollector()
             token_mapper = LineToTokenMapper(tokenizer)
             r = measure_convergence_efficiency(model, tokenizer, ppo_trainer, train_data, eval_data,
                     fgo_enabled=(condition=="fgo"), trace_collector=trace_collector, token_mapper=token_mapper,
                     max_steps=cfg.max_steps, eval_interval=cfg.eval_interval, target_pass1=cfg.target_pass1, seed=seed)
             results[condition].append(r)
    5. agg = {c: aggregate_seeds(results[c]) for c in results}
    6. ratio = steps_to_target_ratio(agg["fgo"]["steps_to_target_mean"], agg["standard"]["steps_to_target_mean"])
    7. gate_pass = (ratio < 0.6) and (agg["fgo"]["final_pass1_mean"] > agg["standard"]["final_pass1_mean"])
    8. plot_learning_curve_comparison(...); plot_steps_to_target_bar(...); plot_sample_efficiency(...)
    9. write results.json + gate_pass (SHOULD_WORK — log limitation if fails, do not block)
```

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | Config + data load | load_problems, train/eval split |
| L-6-2 | 2x3 run loop | condition x seed, model/trainer/collector setup per run |
| L-6-3 | Aggregation + gate check | aggregate_seeds, steps_to_target_ratio, SHOULD_WORK gate |
| L-6-4 | Results + viz write | results.json + required/optional figures to `figures/` |

---

## Total Subtask Count: 40/40 used, 6 epics
