# Architecture: H-M3 (Dense Credit Assignment — Convergence Efficiency)

**Type:** MECHANISM (training efficiency: FGO-PPO vs Standard-PPO convergence)
**Applied:** No specific KB pattern found for PPO convergence tracking (KB search returned unrelated PEFT/LoRA results); used standard periodic-eval learning-curve pattern from experiment brief Algorithm.

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-M2)
**Status:** Real H-M2 code differs from its own 03_architecture.md spec (file names changed: `train_masked.py` not `ppo_trainer.py`, `fgo.py` not `fgo_loss.py`, `token_mapper.py` not part of `trace_mask.py`). Verified via `get_symbols_overview` + `find_symbol` on actual files.
**Analyzed Path:** `docs/youra_research/h-m2/code/`
**Findings:** `fgo.py` has ready-to-reuse `fgo_ppo_loss(logprobs, old_logprobs, advantages, mask, clip_eps)` and `standard_ppo_loss(...)` (calls fgo_ppo_loss with all-ones mask) and `create_fgo_mask(token_ids, token_to_line, executed_lines)`. `trace_collector.py` has `ExecutionTraceCollector`. `token_mapper.py` has `LineToTokenMapper`. `data_loader.py` has `load_problems`, `generate_batch_samples`. `evaluate.py` has `pass_at_k`, `evaluate_samples`. `model.py` has `load_policy_model`, `build_ppo_trainer`. `config.py` has `TRAINING_CONFIG` (lr=1e-5, batch=16, clip=0.2, gae_lambda=0.95) reusable as-is per NFR-3 ("no new model architecture changes").

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| fgo_ppo_loss, standard_ppo_loss, create_fgo_mask | `from h_m2.fgo import fgo_ppo_loss, standard_ppo_loss, create_fgo_mask` | `h-m2/code/fgo.py` |
| ExecutionTraceCollector | `from h_m2.trace_collector import ExecutionTraceCollector` | `h-m2/code/trace_collector.py` |
| LineToTokenMapper | `from h_m2.token_mapper import LineToTokenMapper` | `h-m2/code/token_mapper.py` |
| load_problems, generate_batch_samples | `from h_m2.data_loader import load_problems, generate_batch_samples` | `h-m2/code/data_loader.py` |
| pass_at_k, evaluate_samples | `from h_m2.evaluate import pass_at_k, evaluate_samples` | `h-m2/code/evaluate.py` |
| load_policy_model, build_ppo_trainer | `from h_m2.model import load_policy_model, build_ppo_trainer` | `h-m2/code/model.py` |

**Verified from**: `h-m2/code/` (actual implementation, not spec)

**Note for Phase 4**: If cross-hypothesis package import is not wired up, copy/symlink these 6 files into `h-m3/code/` instead of importing across folders — Phase 4 Coder decides based on project import conventions.

---

## File Organization

```
h-m3/code/
  config.py            # training/eval config: reuse H-M2 TRAINING_CONFIG values + max_steps=5000, eval_interval=100, target_pass1=0.5
  convergence.py        # measure_convergence_efficiency() - the new H-M3 mechanism
  train_condition.py     # per-condition training loop (standard vs fgo), wraps H-M2 loss fns
  data_loader.py           # thin re-export or copy of H-M2 load_problems/generate_batch_samples
  evaluate.py               # thin re-export or copy of H-M2 pass_at_k
  stats.py                   # steps-to-target ratio check, learning curve slope, sample efficiency
  visualize.py                # learning curve comparison + 3 optional figures
  run_experiment.py             # main entry: run both conditions x 3 seeds, gate check
```

---

## Modules

### Convergence Measurement (`convergence.py`)

**Dependencies**: h_m2.fgo (fgo_ppo_loss, standard_ppo_loss, create_fgo_mask), h_m2.trace_collector, h_m2.token_mapper, h_m2.evaluate.pass_at_k

```python
def measure_convergence_efficiency(
    model, tokenizer, train_data: list[dict], eval_data: list[dict],
    fgo_enabled: bool, trace_collector: "ExecutionTraceCollector",
    token_mapper: "LineToTokenMapper", max_steps: int = 5000,
    eval_interval: int = 100, target_pass1: float = 0.5, seed: int = 42
) -> dict: ...
    # returns {steps_to_target, final_pass1, learning_curve: list[(step,pass1)], loss_curve: list[(step,loss)]}
```

### Per-Condition Training (`train_condition.py`)

**Dependencies**: h_m2.fgo, h_m2.model (build_ppo_trainer), convergence.py

```python
def run_condition(condition: str, model, tokenizer, ppo_trainer, batch: dict,
                   trace_collector, token_mapper) -> dict: ...
    # condition in {"standard", "fgo"}; computes mask via create_fgo_mask only if fgo
    # returns {loss: Tensor, grad_norms: dict}
```

### Data / Eval (`data_loader.py`, `evaluate.py`)

**Dependencies**: h_m2.data_loader, h_m2.evaluate (re-exported, no new logic)

```python
# data_loader.py
from h_m2.data_loader import load_problems, generate_batch_samples  # HumanEval 164 + MBPP train 374 / test 500

# evaluate.py
from h_m2.evaluate import pass_at_k  # pass@1 on eval_data
```

### Stats (`stats.py`)

**Dependencies**: numpy

```python
def steps_to_target_ratio(fgo_steps: int, standard_steps: int) -> float: ...  # FGO/Standard, target <0.6
def learning_curve_slope(curve: list[tuple[int, float]]) -> float: ...        # avg pass@1 delta per 100 steps
def sample_efficiency(curve: list[tuple[int, float]], batch_size: int) -> float: ...  # pass@1 gain per sample
def aggregate_seeds(results: list[dict]) -> dict: ...  # mean/std across 3 seeds per condition
```

### Visualization (`visualize.py`)

**Dependencies**: matplotlib

```python
def plot_learning_curve_comparison(fgo_curves: list, standard_curves: list) -> None: ...  # required (FR-6.1)
def plot_steps_to_target_bar(results: dict) -> None: ...       # FR-6.2
def plot_sample_efficiency(results: dict) -> None: ...          # FR-6.3
def plot_training_loss(fgo_loss: list, standard_loss: list) -> None: ...
def plot_gradient_magnitude_hist(grad_logs: dict) -> None: ...
```

### Orchestration (`run_experiment.py`)

**Dependencies**: all modules above, h_m2.model

```python
def main(config_path: str = "config.py") -> None: ...
    # for condition in ["standard", "fgo"]:
    #   for seed in [42, 123, 456]:
    #     measure_convergence_efficiency(...) -> checkpoint every 500 steps
    # stats.aggregate_seeds; stats.steps_to_target_ratio; visualize.*; gate check (SHOULD_WORK)
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| B-1 | Reuse wiring | Import/copy H-M2 fgo.py, trace_collector.py, token_mapper.py, data_loader.py, evaluate.py, model.py into h-m3/code | 5 | 1+2+1+1 |
| B-2 | Config | Extend H-M2 TRAINING_CONFIG with max_steps=5000, eval_interval=100, target_pass1=0.5, 2 conditions x 3 seeds | 3 | 1+1+1+0 |
| B-3 | Convergence measurement loop | Implement measure_convergence_efficiency: train step + periodic pass@1 eval + steps_to_target tracking | 11 | 3+2+3+3 |
| B-4 | Per-condition training | run_condition: standard vs fgo loss dispatch using H-M2 fgo_ppo_loss/standard_ppo_loss + create_fgo_mask | 8 | 2+3+2+1 |
| B-5 | Checkpointing | Save/restore every 500 steps per NFR-2 | 4 | 1+1+1+1 |
| B-6 | Full run: 2 conditions x 3 seeds | Execute 6 training runs up to 5000 steps each, collect learning curves | 10 | 2+2+3+3 |
| B-7 | Statistical analysis | steps_to_target_ratio, learning_curve_slope, sample_efficiency, aggregate_seeds | 6 | 2+1+2+1 |
| B-8 | Visualization | Required learning curve plot + 4 optional figures | 6 | 2+1+1+2 |
| B-9 | Pipeline orchestration + gate check | Wire training+eval+stats+viz, compute SHOULD_WORK gate (FGO<60% steps, FGO>Standard pass@1) | 7 | 2+3+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [B-3, B-6], Low(4-8): [B-1, B-2, B-4, B-5, B-7, B-8, B-9]

---

## Notes

- No new model/architecture code: H-M3 reuses H-M2's FGO mask + loss functions verbatim (NFR-3).
- `standard_ppo_loss` in H-M2 already implemented as `fgo_ppo_loss` with all-ones mask — no reimplementation needed for the Standard PPO baseline condition.
- Sample budget: max 5000 steps x eval_interval 100 x 2 conditions x 3 seeds = 60 evaluations total; within NFR-1 <24h/condition on single A100 (out of scope to verify wall-clock in PoC).
