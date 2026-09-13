# Architecture: H-E1 Dose-Response Curation

**Type:** EXISTENCE (PoC) | **Applied:** CCNet/RedPajama perplexity-filter + MinHash-dedup pattern, sklearn AIC model-selection pattern

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - no existing code to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch. No base hypothesis, no existing `src/`/`code/` directory found in repo.

---

## 1. System Components

- **data_pipeline.py** — streams RedPajama-v2, applies perplexity/dedup filter, tokenizes, yields training batches
- **train.py** — trains GPT-2 125M from scratch on a filtered dataset for one config, checkpoints result
- **evaluate.py** — runs lm-evaluation-harness on a checkpoint, computes ensemble score
- **sweep.py** — orchestrates all 15 configs (data → train → eval), manages artifacts
- **analyze.py** — polynomial regression + AIC/BIC model selection, generates dose-response figures
- **config.py** — the 15 `CurationConfig` definitions (C0-C9, D0-D4) + shared training/eval hyperparameters

## 2. Data Flow

1. `sweep.py` iterates `CURATION_CONFIGS` (15 entries)
2. For each config: `data_pipeline.build_dataset(config)` streams RedPajama-v2 → filters by `ccnet_perplexity` percentile and/or MinHash dedup level → tokenizes with GPT-2 BPE → truncates to 10B tokens → writes/streams to `train.py`
3. `train.py` trains GPT-2 125M on the filtered stream → saves checkpoint to `checkpoints/{config_id}/`
4. `evaluate.py` loads checkpoint → runs lm-eval-harness (hellaswag, arc_easy, piqa, winogrande) → writes `results/{config_id}/benchmark_results.json`
5. `sweep.py` aggregates all 15 results into `results/all_configs.json`
6. `analyze.py` reads `all_configs.json` → fits degree 1/2/3 polynomial per parameter dimension (perplexity, dedup) → selects via AIC → saves figures to `figures/`

## 3. Module Interfaces

### CurationConfig (`config.py`)

```python
@dataclass
class CurationConfig:
    config_id: str                # "C0".."C9", "D0".."D4"
    perplexity_percentile: int | None   # None or 0-90
    dedup_level: str | None       # None, "fuzzy_0.7", "fuzzy_0.85", "exact", "exact_plus_fuzzy"

CURATION_CONFIGS: list[CurationConfig]   # all 15, defined per PRD table
TRAIN_CONFIG: dict   # optimizer/lr/batch/tokens (shared across all 15 runs)
```

### DataPipeline (`data_pipeline.py`)

**Dependencies**: CurationConfig, datasets, text_dedup

```python
def compute_percentile_threshold(sample_ppl: list[float], percentile: int) -> float: ...
def apply_perplexity_filter(dataset, threshold: float): ...
def apply_deduplication(dataset, dedup_level: str): ...
def build_dataset(config: CurationConfig, tokenizer, max_tokens: int = 10_000_000_000): ...
    # returns tokenized, filtered, dedup'd streaming dataset capped at max_tokens
```

### Trainer (`train.py`)

**Dependencies**: DataPipeline, GPT2Config, GPT2LMHeadModel

```python
def build_model() -> GPT2LMHeadModel: ...   # fresh init, 12L/768H/12A
def train(config: CurationConfig, dataset, out_dir: str) -> str: ...
    # returns checkpoint path: checkpoints/{config_id}/
```

### Evaluator (`evaluate.py`)

**Dependencies**: lm_eval

```python
TASKS = ["hellaswag", "arc_easy", "piqa", "winogrande"]

def evaluate_checkpoint(checkpoint_path: str) -> dict: ...
    # returns {task: accuracy, ...}
def compute_ensemble_score(results: dict) -> float: ...
    # PC1 of the 4 task accuracies
```

### Sweep Orchestrator (`sweep.py`)

**Dependencies**: config, data_pipeline, train, evaluate

```python
def run_config(config: CurationConfig, base_dir: str) -> dict: ...
    # data -> train -> eval for one config; returns {config_id, ensemble_score, per_task, checkpoint_path}
    # skips stages whose output artifact already exists (resume support)

def run_sweep(configs: list[CurationConfig] = CURATION_CONFIGS, base_dir: str = "."): ...
    # sequential loop over all 15 (single A100 per PRD resource estimate)
    # writes results/all_configs.json after each config completes (incremental save)
```

### Analyzer (`analyze.py`)

**Dependencies**: sklearn, numpy, matplotlib

```python
def fit_and_select(x: np.ndarray, y: np.ndarray) -> dict: ...
    # {degree, aic, model} - lowest AIC wins, per code template in 03_prd.md

def find_peak(model, x_range: tuple) -> float | None: ...
    # None if peak at boundary or model is linear

def run_analysis(results_path: str = "results/all_configs.json", fig_dir: str = "figures/"): ...
    # splits configs into perplexity-dim (C0-C9) and dedup-dim (D0-D4)
    # fits both, saves dose_response_perplexity.png, dose_response_dedup.png
```

---

## 4. Configuration Sweep Orchestration

- Single sequential loop, no parallelism (PoC scope, single A100 per PRD)
- Each config is independent: `run_config()` is idempotent — checks for existing checkpoint/results file before recomputing (resume on crash)
- Config ID is the sole key across all artifact paths (`checkpoints/{id}/`, `results/{id}/`)
- Shared `TRAIN_CONFIG` hyperparameters (lr, batch, warmup, tokens) applied identically to all 15 — only data filtering varies

## 5. Checkpoint / Artifact Management

```
{hypothesis_folder}/
  checkpoints/{config_id}/          # model weights, final step only (no intermediate ckpts - PoC)
  results/{config_id}/benchmark_results.json
  results/all_configs.json          # aggregated, appended incrementally by sweep.py
  figures/dose_response_perplexity.png
  figures/dose_response_dedup.png
  figures/per_benchmark_breakdown.png     (optional)
  figures/aic_model_comparison.png        (optional)
```

- No intermediate training checkpoints saved (10B tokens, single seed, PoC) — only final checkpoint per config, ~50GB total storage per PRD estimate
- `sweep.py` writes `results/all_configs.json` after each config finishes, so partial sweep progress survives crashes

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config definitions | Define 15 CurationConfig entries + TRAIN_CONFIG | 4 | 2+1+1+0 |
| A-2 | Data pipeline | RedPajama-v2 streaming + perplexity filter + MinHash dedup + tokenize | 14 | 4+4+4+2 |
| A-3 | GPT-2 training loop | Model init, AdamW+cosine schedule, checkpoint save | 10 | 3+2+3+2 |
| A-4 | Evaluation harness integration | lm-eval-harness wrapper + ensemble PC1 score | 6 | 2+2+1+1 |
| A-5 | Sweep orchestrator | Loop over 15 configs with resume support | 8 | 2+3+2+1 |
| A-6 | Polynomial regression analyzer | AIC/BIC fit + peak detection | 6 | 2+2+1+1 |
| A-7 | Figure generation | Dose-response plots (2 required + optional) | 4 | 1+1+1+1 |
| A-8 | End-to-end run | Execute full 15-config sweep, produce final artifacts | 8 | 2+2+3+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-2], Medium(9-13): [A-3, A-5, A-8], Low(4-8): [A-1, A-4, A-6, A-7]
