# Architecture: H-M1 Noise-Dilution Mechanism

**Type:** MECHANISM | **Applied:** CCNet/RedPajama perplexity-filter pattern (reused from H-E1), loss-curve convergence-analysis pattern (steps-to-threshold + AUC)

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Actual H-E1 code found at `docs/youra_research/h-e1/code/`. Read directly (Serena MCP unavailable in this session; used Read tool on actual source as fallback per "trust the code" rule).
**Analyzed Path:** `docs/youra_research/h-e1/code/`
**Findings:** H-E1 provides reusable `build_dataset()` (data pipeline), `build_model()`/`train()` (trainer, no loss-history return), `evaluate()`/`compute_ensemble_score()` (eval), `fit_and_select()`/`plot_dose_response()` (analysis, not needed for M1). H-E1's `train()` only prints loss, does not return a loss history — H-M1 must wrap/extend it to capture `(step, tokens, loss)` for convergence analysis. `CurationConfig` requires a `dedup` field (H-M1 fixes it to `"none"`).

---

## 1. System Components

- **config.py** — 7 `CurationConfig` entries (M1-C0..C6, dedup="none" fixed) + reuse of H-E1 `MODEL_CONFIG`/`TRAIN_CONFIG`/`DATA_CONFIG`/`EVAL_CONFIG`
- **train_logged.py** — wraps H-E1 `train()` to additionally return `loss_history: list[dict]`
- **convergence.py** — steps-to-threshold, convergence AUC, loss-at-checkpoint, bootstrap comparison, Cohen's d
- **sweep.py** — orchestrates 7 configs (data → train+log → eval), incremental save (same pattern as H-E1)
- **figures.py** — loss-curve overlay, steps-to-threshold bar chart, quality-diversity scatter

## 2. Data Flow

1. `sweep.py` iterates `M1_CONFIGS` (7 entries)
2. `data_pipeline.build_dataset(config)` (H-E1, reused as-is) → filtered/tokenized stream
3. `train_logged.train_with_history(model, data, ckpt_dir, config_id)` → checkpoint + `loss_history` list, saved to `results/{config_id}/loss_history.json`
4. `eval.evaluate(checkpoint_path)` (H-E1, reused as-is) → benchmark scores
5. `sweep.py` aggregates into `results/all_configs.json` (scores + loss_history per config)
6. `convergence.py` reads `all_configs.json` → computes steps-to-threshold, AUC, loss@{1B,5B,10B}, bootstrap p-value, Cohen's d → `results/convergence_metrics.json`
7. `figures.py` reads both result files → 3 required + 1 optional figure

## 3. Module Interfaces

### M1Config (`config.py`)

**Dependencies**: none (mirrors H-E1 `config.py` structure)

```python
from h_e1.code.config import MODEL_CONFIG, TRAIN_CONFIG, DATA_CONFIG, EVAL_CONFIG
from dataclasses import dataclass
from typing import Optional

@dataclass
class CurationConfig:              # identical shape to H-E1's, dedup fixed to "none"
    config_id: str
    perplexity_pct: Optional[int]
    dedup: str = "none"

M1_CONFIGS: list[CurationConfig]   # M1-C0(None) .. M1-C6(90): [None,20,40,50,60,80,90]
LOSS_THRESHOLD: float = 3.5
CHECKPOINT_TOKENS: list[int] = [1_000_000_000, 5_000_000_000, 10_000_000_000]
```

### Logged Trainer (`train_logged.py`)

**Dependencies**: H-E1 `train.trainer` (`build_model`, `get_cosine_schedule`, `save_checkpoint`, `load_checkpoint`)

```python
def train_with_history(
    model, data, ckpt_dir: str, config_id: str,
    batch_size: int = None, total_steps: int = None,
    log_interval: int = 100, device: str = "cuda",
) -> tuple[str, list[dict]]:
    # same loop as h_e1.train.trainer.train(), plus:
    #   if step % log_interval == 0:
    #       loss_history.append({"step": step, "tokens_seen": step*batch_size*seq_len, "loss": loss.item()})
    # returns (checkpoint_model_path, loss_history)
```

### Convergence Analysis (`convergence.py`)

**Dependencies**: numpy, scipy.stats (bootstrap)

```python
def steps_to_threshold(loss_history: list[dict], threshold: float = 3.5) -> float: ...
    # first step where loss < threshold, else inf

def convergence_auc(loss_history: list[dict]) -> float: ...
    # np.trapz(losses, steps); lower = faster convergence

def loss_at_checkpoints(loss_history: list[dict], token_checkpoints: list[int]) -> dict[int, float]: ...
    # interpolated loss at each token checkpoint

def bootstrap_compare(auc_a: list[float], auc_b: list[float], n_boot: int = 10000) -> dict: ...
    # returns {"p_value": float, "cohens_d": float}

def analyze_convergence(all_results: dict) -> dict: ...
    # per-config: {steps_to_threshold, final_loss, convergence_auc, loss_at_checkpoints}
    # plus pairwise bootstrap_compare(p50 vs p0), Cohen's d
```

### Sweep Orchestrator (`sweep.py`)

**Dependencies**: config, H-E1 `data.build_dataset`, `train_logged.train_with_history`, H-E1 `eval.evaluate`

```python
def run_config(config: CurationConfig, base_dir: str, tokenizer) -> dict: ...
    # data -> train_with_history -> eval; returns
    # {config_id, scores, loss_history, checkpoint_path}
    # resume: skip stage if results/{config_id}/benchmark_results.json exists

def run_sweep(configs: list[CurationConfig] = M1_CONFIGS, base_dir: str = "."): ...
    # sequential loop over 7 configs, incremental save to results/all_configs.json
```

### Figures (`figures.py`)

**Dependencies**: matplotlib, convergence.py output

```python
def plot_loss_curves(all_results: dict, save_path: str): ...
    # overlay of 7 loss curves (loss vs tokens_seen)

def plot_steps_to_threshold(convergence_metrics: dict, save_path: str): ...
    # bar chart, one bar per config

def plot_quality_diversity_scatter(convergence_metrics: dict, ensemble_scores: dict, save_path: str): ...
    # x=convergence_auc, y=ensemble_score, one point per config

def plot_loss_at_checkpoints(convergence_metrics: dict, save_path: str): ...  # optional
```

---

## 4. Configuration Sweep Orchestration

- Same pattern as H-E1: sequential loop, single GPU, idempotent `run_config` (checks `benchmark_results.json` before recompute)
- 7 configs vs H-E1's 15 — no dedup dimension varies (fixed to `"none"`)
- `loss_history` persisted per-config (`results/{config_id}/loss_history.json`) in addition to benchmark results, needed by `convergence.py`

## 5. Checkpoint / Artifact Management

```
{hypothesis_folder}/
  checkpoints/{config_id}/                    # final checkpoint only
  results/{config_id}/benchmark_results.json
  results/{config_id}/loss_history.json       # NEW: (step, tokens_seen, loss) list
  results/all_configs.json                    # aggregated, incremental
  results/convergence_metrics.json            # NEW: steps_to_threshold, AUC, bootstrap stats
  figures/loss_curves_overlay.png
  figures/steps_to_threshold_bar.png
  figures/quality_diversity_scatter.png
  figures/loss_at_checkpoints.png             (optional)
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual H-E1 Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| build_dataset | `from data.data_pipeline import build_dataset` | `h-e1/code/data/data_pipeline.py` |
| build_model, get_cosine_schedule, save_checkpoint, load_checkpoint | `from train.trainer import build_model, get_cosine_schedule, save_checkpoint, load_checkpoint` | `h-e1/code/train/trainer.py` |
| evaluate, compute_ensemble_score, save_results, load_results | `from eval.evaluator import evaluate, compute_ensemble_score, save_results, load_results` | `h-e1/code/eval/evaluator.py` |
| MODEL_CONFIG, TRAIN_CONFIG, DATA_CONFIG, EVAL_CONFIG | `from config.config import MODEL_CONFIG, TRAIN_CONFIG, DATA_CONFIG, EVAL_CONFIG` | `h-e1/code/config/config.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation, not spec).

**Note**: H-E1's `train()` in `trainer.py` does NOT return loss history (only prints). H-M1's `train_logged.train_with_history()` is a modified copy of that function (cannot import-and-extend cleanly since loss capture requires an internal loop change) — same signature/config usage otherwise.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config definitions | 7 M1_CONFIGS + reuse H-E1 MODEL/TRAIN/DATA/EVAL_CONFIG | 3 | 1+1+1+0 |
| A-2 | Reuse data pipeline | Wire H-E1 build_dataset (no changes) | 3 | 1+2+0+0 |
| A-3 | Logged trainer | Copy+extend H-E1 train() to capture loss_history at 100-step intervals | 9 | 3+2+2+2 |
| A-4 | Reuse eval pipeline | Wire H-E1 evaluate() + compute_ensemble_score (no changes) | 3 | 1+2+0+0 |
| A-5 | Convergence analysis | steps_to_threshold, AUC, loss_at_checkpoints, bootstrap+Cohen's d | 12 | 3+2+4+3 |
| A-6 | Sweep orchestrator | Loop over 7 configs, resume support, persist loss_history | 7 | 2+3+1+1 |
| A-7 | Figure generation | Loss overlay, steps-to-threshold bar, quality-diversity scatter | 6 | 2+1+2+1 |
| A-8 | End-to-end run | Execute full 7-config sweep + convergence analysis, validate MUST_WORK gate | 8 | 2+2+3+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3, A-5, A-8], Low(4-8): [A-1, A-2, A-4, A-6, A-7]
