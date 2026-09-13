# Architecture: H-C1 (CPDR vs RedPajama Defaults Comparison)

**Type**: COMPARISON | **Applied**: A/B pipeline comparison pattern (reuse trainer + evaluator, vary only curation config)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1 has actual reusable pipeline; H-M3 is analysis-only, not reusable)
**Status**: Existing patterns found in H-E1 implementation (verified via direct read, not spec)
**Analyzed Path**: `h-e1/code/{config,data,train,eval}/`
**Findings**: H-E1 provides complete `CurationConfig` dataclass, `build_dataset()` (perplexity filter + MinHash dedup + tokenize), `build_model()`/`train()` (GPT-2 125M BF16 training), and `evaluate()` (lm-eval-harness wrapper). All directly reusable — no reimplementation needed. `SWEEP_CONFIGS` already contains D2=`CurationConfig("D2", 50, "fuzzy_0.85")` matching CPDR config exactly. RedPajama-default config (p30, exact dedup) is not predefined but trivially constructed as `CurationConfig("RP", 30, "exact")`.

---

## Module Structure

### Reused from H-E1 (import directly, zero modification)

- `config.py` → `MODEL_CONFIG`, `TRAIN_CONFIG`, `DATA_CONFIG`, `EVAL_CONFIG`, `CurationConfig`, `DEDUP_MINHASH_PARAMS`
- `data/data_pipeline.py` → `build_dataset(config, tokenizer, max_tokens) -> Iterator[Tensor]`
- `train/trainer.py` → `build_model(seed) -> GPT2LMHeadModel`, `train(model, data, ckpt_dir, config_id, ...) -> str`
- `eval/evaluator.py` → `evaluate(checkpoint_path, tasks, batch_size) -> dict`

### New Modules (`h-c1/code/`)

#### `config.py`

**Dependencies**: h-e1 `config.py` (re-export + extend)

```python
from h_e1_config import CurationConfig, MODEL_CONFIG, TRAIN_CONFIG, DATA_CONFIG, EVAL_CONFIG

CPDR_CONFIG = CurationConfig("CPDR", 50, "fuzzy_0.85")
REDPAJAMA_CONFIG = CurationConfig("RP", 30, "exact")
SEEDS = [42, 43, 44]
IMPROVEMENT_THRESHOLD = 0.01
```

#### `run_comparison.py`

**Dependencies**: config.py, h-e1 data_pipeline, trainer, evaluator

```python
def run_single_seed(seed: int, ckpt_root: str) -> dict:
    """Train+eval CPDR and RP configs for one seed. Returns {'cpdr': scores, 'redpajama': scores}."""
    ...

def run_comparison_experiment(seeds: list = SEEDS, ckpt_root: str = "checkpoints") -> dict:
    """Loop seeds, aggregate ensemble scores, compute improvement + pass/fail."""
    ...
```

#### `analysis.py`

**Dependencies**: numpy, scipy.stats

```python
def compute_ensemble_mean(per_seed_scores: list[dict], tasks: list) -> float: ...
def paired_ttest(cpdr_scores: list[float], rp_scores: list[float]) -> dict: ...
def gate_check(cpdr_mean: float, rp_mean: float, threshold: float = 0.01) -> dict: ...
```

#### `figures.py`

**Dependencies**: matplotlib, analysis.py output

```python
def plot_ensemble_comparison(results: dict, out_path: str): ...      # required gate figure
def plot_per_benchmark_breakdown(results: dict, out_path: str): ...
def plot_training_curves(loss_logs: dict, out_path: str): ...
def plot_improvement_waterfall(results: dict, out_path: str): ...
```

#### `run_experiment.py` (entrypoint)

**Dependencies**: run_comparison, analysis, figures

```python
def main():
    """Orchestrate: run_comparison_experiment -> analysis -> save JSON -> generate figures."""
    ...
```

---

## File Organization

```
h-c1/code/
  config.py
  run_comparison.py
  analysis.py
  figures.py
  run_experiment.py
  output/
    results.json
  figures/
    gate_ensemble_comparison.png
    per_benchmark_breakdown.png
    training_curves.png
    improvement_waterfall.png
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| CurationConfig | `from config import CurationConfig` | `h-e1/code/config/config.py` |
| build_dataset | `from data.data_pipeline import build_dataset` | `h-e1/code/data/data_pipeline.py` |
| build_model, train | `from train.trainer import build_model, train` | `h-e1/code/train/trainer.py` |
| evaluate | `from eval.evaluator import evaluate` | `h-e1/code/eval/evaluator.py` |

**Verified from**: `h-e1/code/` (actual implementation, read directly)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| C-1 | Setup & config | Create h-c1/config.py, wire CPDR/RP CurationConfig, path setup for h-e1 imports | 6 | 2+2+1+1 |
| C-2 | Dataset build for both configs | Call build_dataset() for CPDR (p50/fuzzy_0.85) and RP (p30/exact) via H-E1 pipeline | 8 | 2+3+2+1 |
| C-3 | Training loop integration | run_single_seed(): train both models per seed with checkpointing via H-E1 trainer | 10 | 3+3+2+2 |
| C-4 | Multi-seed orchestration | run_comparison_experiment(): loop 3 seeds, collect scores, handle failures | 8 | 2+2+2+2 |
| C-5 | Benchmark evaluation | Wire evaluate() for 4 tasks per model, ensemble mean computation | 7 | 2+2+2+1 |
| C-6 | Statistical comparison | Paired t-test across seeds, improvement % calc, gate pass/fail logic | 9 | 2+2+4+1 |
| C-7 | Required gate figure | Bar chart CPDR vs RP ensemble score with error bars (3 seeds) | 6 | 2+1+2+1 |
| C-8 | Additional figures | Per-benchmark grouped bars, training loss curves, improvement waterfall | 8 | 3+2+2+1 |
| C-9 | Experiment entrypoint & results | run_experiment.py orchestration, JSON output, end-to-end integration test | 7 | 2+2+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [C-3, C-6], Low(4-8): [C-1, C-2, C-4, C-5, C-7, C-8, C-9]
