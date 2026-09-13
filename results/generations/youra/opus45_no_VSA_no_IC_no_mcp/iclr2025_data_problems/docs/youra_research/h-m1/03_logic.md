# Logic: H-M1 Noise-Dilution Mechanism

**Applied**: CCNet perplexity-filter pattern (reused H-E1); loss-curve steps-to-threshold/AUC convergence pattern; bootstrap two-sample effect-size pattern (scipy.stats.bootstrap + Cohen's d)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Archon MCP and Serena MCP unavailable in this session (no MCP servers connected). Fallback: Read tool used directly on actual H-E1 source files (trust-the-code rule) — equivalent verification to `find_symbol`/`get_symbols_overview`.
**Analyzed Path**: `docs/youra_research/h-e1/code/{config,data,train,eval}/`
**Relevant Symbols**: `CurationConfig`, `MODEL_CONFIG`, `TRAIN_CONFIG`, `DATA_CONFIG`, `EVAL_CONFIG` (config.py); `build_dataset` (data_pipeline.py); `build_model`, `get_cosine_schedule`, `save_checkpoint`, `load_checkpoint`, `train` (trainer.py); `evaluate`, `compute_ensemble_score`, `save_results`, `load_results` (evaluator.py)

**Key finding**: H-E1 `train()` does NOT return loss history (prints only, every 100 steps). `train_with_history()` is a modified copy — not a wrapper — since loss capture requires an internal loop change. All other signatures (params, dtypes, optimizer/scheduler setup) copied exactly.

---

## External Dependencies (Base Hypothesis)

```python
# From: h-e1/code/config/config.py (ACTUAL CODE)
@dataclass
class CurationConfig:
    config_id: str
    perplexity_pct: Optional[int]
    dedup: str                      # H-M1 fixes this to "none" always

MODEL_CONFIG: dict   # vocab_size, n_positions, n_embd, n_layer, n_head
TRAIN_CONFIG: dict   # total_tokens, batch_size, seq_len, max_steps, adam_beta1/2,
                     # weight_decay, grad_clip, lr_peak, lr_min, warmup_steps, precision, seed
DATA_CONFIG: dict    # dataset, subset, split, streaming, quality_field, val_holdout_fraction
EVAL_CONFIG: dict    # library, tasks, metrics, batch_size, ensemble_method

# From: h-e1/code/data/data_pipeline.py (ACTUAL CODE)
def build_dataset(
    config: CurationConfig,
    tokenizer: Optional[GPT2Tokenizer] = None,
    max_tokens: int = None,
) -> Iterator[torch.Tensor]: ...          # yields [seq_len] token id tensors

# From: h-e1/code/train/trainer.py (ACTUAL CODE)
def build_model(seed: int = None) -> GPT2LMHeadModel: ...
def get_cosine_schedule(optimizer, warmup_steps=None, total_steps=None, min_lr_ratio=None) -> LambdaLR: ...
def save_checkpoint(ckpt_dir: str, model, optimizer, scheduler, step: int, config_id: str): ...
def load_checkpoint(ckpt_dir: str, model, optimizer, scheduler) -> int: ...  # returns resume_step

# From: h-e1/code/eval/evaluator.py (ACTUAL CODE)
def evaluate(checkpoint_path: str, tasks: list = None, batch_size: int = None) -> dict: ...
def compute_ensemble_score(all_config_scores: dict) -> dict: ...   # PC1, min-max normalized [0,1]
def save_results(results: dict, path: str): ...
def load_results(path: str) -> dict: ...
```

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation).

---

## A-3: Logged Trainer [Complexity: 9, Budget: 9]

**Applied**: Modified-copy pattern (cannot cleanly wrap `train()` — loss capture needs internal loop access)

### API Signatures

```python
# train_logged.py
from typing import Iterator
import os
import torch
from torch.optim import AdamW
from transformers import GPT2LMHeadModel

from train.trainer import build_model, get_cosine_schedule, save_checkpoint, load_checkpoint
from config import TRAIN_CONFIG

def train_with_history(
    model: GPT2LMHeadModel,
    data: Iterator[torch.Tensor],
    ckpt_dir: str,
    config_id: str,
    batch_size: int = None,
    total_steps: int = None,
    log_interval: int = 100,
    ckpt_every: int = 2000,
    device: str = "cuda",
) -> tuple[str, list[dict]]:
    """Train + log loss every log_interval steps. Returns (model_path, loss_history)."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [batch_size, seq_len] | stacked from `data` iterator |
| outputs.loss | scalar | GPT2LMHeadModel CE loss |

### Pseudo-code

```
1. batch_size/total_steps default from TRAIN_CONFIG (same as H-E1 train())
2. model -> device, bf16 if TRAIN_CONFIG["precision"]=="bf16"
3. optimizer = AdamW(model.params, lr=lr_peak, betas=(beta1,beta2), wd=weight_decay)
4. scheduler = get_cosine_schedule(optimizer)
5. resume_step = load_checkpoint(...)
6. loss_history = []
7. for chunk in data:
     accumulate batch to batch_size -> input_ids [B, seq_len]
     forward+backward, clip_grad_norm_, optimizer.step(), scheduler.step()
     if step % log_interval == 0:
         loss_history.append({
             "step": step,
             "tokens_seen": step * batch_size * seq_len,
             "loss": loss.item(),
         })
     if step % ckpt_every == 0 or step == total_steps-1: save_checkpoint(...)
     step += 1
8. save_checkpoint(...) final
9. return (os.path.join(ckpt_dir, "model"), loss_history)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | Copy train loop | Duplicate H-E1 `train()` body (model setup, optimizer, scheduler, resume) |
| L-3-2 | Add loss logging | Insert `loss_history.append(...)` at `step % log_interval == 0` |
| L-3-3 | Persist per-config | `json.dump(loss_history, open(f"results/{config_id}/loss_history.json","w"))` in sweep.py caller |

---

## A-5: Convergence Analysis [Complexity: 12, Budget: 12]

**Applied**: steps-to-threshold + trapezoidal AUC (loss-curve convergence pattern); bootstrap resampling + Cohen's d for effect size (scipy.stats)

### API Signatures

```python
# convergence.py
import numpy as np
from scipy import stats

LOSS_THRESHOLD: float = 3.5
CHECKPOINT_TOKENS: list[int] = [1_000_000_000, 5_000_000_000, 10_000_000_000]

def steps_to_threshold(loss_history: list[dict], threshold: float = LOSS_THRESHOLD) -> float:
    """First step where loss < threshold, else inf."""
    ...

def convergence_auc(loss_history: list[dict]) -> float:
    """np.trapz(losses, x=tokens_seen); lower = faster convergence."""
    ...

def loss_at_checkpoints(
    loss_history: list[dict], token_checkpoints: list[int] = CHECKPOINT_TOKENS
) -> dict[int, float]:
    """Linear-interpolated loss at each token checkpoint (np.interp)."""
    ...

def bootstrap_compare(
    values_a: list[float], values_b: list[float], n_boot: int = 10000, seed: int = 42
) -> dict:
    """Bootstrap p-value (two-sided, resampled mean diff) + Cohen's d.
    Returns {"p_value": float, "cohens_d": float, "mean_diff": float}."""
    ...

def analyze_convergence(all_results: dict) -> dict:
    """all_results: {config_id: {"loss_history": [...], "ensemble_score": float, ...}}
    Returns per-config metrics + pairwise stats. See pseudo-code."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| losses | [len(loss_history)] | 1D np.array from `[d["loss"] for d in loss_history]` |
| tokens_seen | [len(loss_history)] | 1D np.array, x-axis for AUC/interp |

### Pseudo-code

```
steps_to_threshold(loss_history, threshold):
    for entry in loss_history:
        if entry["loss"] < threshold: return entry["step"]
    return float("inf")

convergence_auc(loss_history):
    tokens = np.array([d["tokens_seen"] for d in loss_history])
    losses = np.array([d["loss"] for d in loss_history])
    return float(np.trapz(losses, tokens))

loss_at_checkpoints(loss_history, token_checkpoints):
    tokens = np.array([d["tokens_seen"] for d in loss_history])
    losses = np.array([d["loss"] for d in loss_history])
    return {tc: float(np.interp(tc, tokens, losses)) for tc in token_checkpoints}

bootstrap_compare(values_a, values_b, n_boot, seed):
    rng = np.random.default_rng(seed)
    obs_diff = np.mean(values_a) - np.mean(values_b)
    boot_diffs = []
    for _ in range(n_boot):
        ra = rng.choice(values_a, size=len(values_a), replace=True)
        rb = rng.choice(values_b, size=len(values_b), replace=True)
        boot_diffs.append(np.mean(ra) - np.mean(rb))
    boot_diffs = np.array(boot_diffs)
    p_value = 2 * min((boot_diffs >= 0).mean(), (boot_diffs < 0).mean())
    pooled_std = np.sqrt((np.var(values_a, ddof=1) + np.var(values_b, ddof=1)) / 2)
    cohens_d = obs_diff / pooled_std if pooled_std > 0 else 0.0
    return {"p_value": float(p_value), "cohens_d": float(cohens_d), "mean_diff": float(obs_diff)}

analyze_convergence(all_results):
    metrics = {}
    for config_id, r in all_results.items():
        lh = r["loss_history"]
        metrics[config_id] = {
            "steps_to_threshold": steps_to_threshold(lh),
            "final_loss": lh[-1]["loss"],
            "convergence_auc": convergence_auc(lh),
            "loss_at_checkpoints": loss_at_checkpoints(lh),
        }
    # pairwise: p50 (M1-C3) vs p0 (M1-C0), single-sample -> compare per-checkpoint loss lists
    p50_losses = [d["loss"] for d in all_results["M1-C3"]["loss_history"]]
    p0_losses = [d["loss"] for d in all_results["M1-C0"]["loss_history"]]
    metrics["p50_vs_p0"] = bootstrap_compare(p50_losses, p0_losses)
    return metrics
```

**Note**: single-seed PoC (NFR out-of-scope: multi-seed) → bootstrap resamples over loss-curve *points* (not multi-seed runs), giving a distributional comparison from the single trajectory per config.

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | steps_to_threshold + convergence_auc | First-crossing scan + `np.trapz` |
| L-5-2 | loss_at_checkpoints | `np.interp` at 1B/5B/10B tokens |
| L-5-3 | bootstrap_compare | Resample mean-diff p-value + Cohen's d |
| L-5-4 | analyze_convergence orchestration | Per-config loop + p50-vs-p0 pairwise, write `convergence_metrics.json` |

---

## Self-Validation

- [x] No ASCII diagrams
- [x] No KB search logs (Archon unavailable — noted, no fabricated logs)
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes in tables/comments
- [x] Subtask count within budget (3+4=7, budget A-3=9 subtask-slots but architecture allocates 3 breakdown items for A-3 top complexity bucket / 4 for A-5 per architecture's `3+2+2+2` / `3+2+4+3` split — logic doc consolidates into 3 and 4 top-level subtasks respectively, matching architecture's largest sub-bucket count)
- [x] Total length < 600 lines
- [x] Codebase Analysis (Serena) section included
- [x] External Dependencies API section with verified H-E1 signatures
