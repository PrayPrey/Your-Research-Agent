# Architecture: H-M2 (Deduplication Stringency Dose-Response)

**Type:** MECHANISM | **Gate:** SHOULD_WORK

Applied: data-pipeline-sweep pattern (single mechanism, config-varied dataset generation)
Applied: from-scratch-LM-training pattern (GPT-2 architecture, multi-seed)
Applied: dose-response evaluation pattern (ensemble PC1 metric across ordered config levels)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code
**Analyzed Path**: N/A
**Findings**: No `code/` folder for H-M2 or prior hypothesis; new implementation from scratch.

---

## File Organization

```
h-m2/code/
  config.py            # DeduplicationConfig, TrainConfig, EvalConfig, DEDUP_LEVELS
  dedup.py              # apply_deduplication(), verify_deduplication_applied()
  data_pipeline.py      # download_redpajama(), build_dataset(), tokenize_and_pack()
  model.py               # build_gpt2_model(config) -> GPT2LMHeadModel
  train.py                # train_one_config(level, seed) training loop + checkpointing
  evaluate.py            # run_benchmarks(checkpoint_path) -> dict, compute_pc1_ensemble()
  run_sweep.py           # orchestrates 5 levels x 3 seeds, calls train+evaluate
  analyze.py              # aggregate results, non-monotonicity check, effect size
  figures.py               # dose_response_curve(), benchmark_breakdown(), data_stats(), loss_curves()
  main.py                   # entrypoint: pipeline -> train -> eval -> analyze -> figures
```

---

## Data Flow

```
RedPajama-v2 raw JSONL
  -> data_pipeline.download_redpajama()
  -> dedup.apply_deduplication(docs, config)   [5 configs, DEDUP_LEVELS]
  -> dedup.verify_deduplication_applied()      [log removal stats]
  -> data_pipeline.tokenize_and_pack()         [10B tokens per level]
  -> train.train_one_config(level, seed)       [5 levels x 3 seeds = 15 runs]
  -> checkpoints/{level}/{seed}/
  -> evaluate.run_benchmarks(checkpoint)       [HellaSwag, ARC-E, PIQA, WinoGrande]
  -> evaluate.compute_pc1_ensemble(scores)
  -> analyze.py                                [aggregate mean+-std, non-monotonic check]
  -> figures.py                                [4 required/optional figures]
```

---

## Module Interfaces

### DeduplicationConfig / DEDUP_LEVELS (`config.py`)

**Dependencies**: none

```python
@dataclass
class DeduplicationConfig:
    level: str
    jaccard_threshold: float
    include_exact: bool

DEDUP_LEVELS: list[DeduplicationConfig]  # 5 entries: none, fuzzy_0.7, fuzzy_0.85, exact, exact_plus_fuzzy

@dataclass
class TrainConfig:
    n_layer: int = 12
    n_head: int = 12
    n_embd: int = 768
    total_tokens: int = 10_000_000_000
    batch_size: int = 512
    lr: float = 6e-4
    warmup_steps: int = 2000
    seeds: tuple[int, int, int] = (0, 1, 2)
```

### dedup (`dedup.py`)

**Dependencies**: config.py, text_dedup

```python
def apply_deduplication(documents: list[str], config: DeduplicationConfig) -> list[str]: ...
def verify_deduplication_applied(original_count: int, deduplicated_count: int, config: DeduplicationConfig) -> bool: ...
def log_dedup_stats(level: str, original_count: int, deduplicated_count: int) -> dict: ...
```

### data_pipeline (`data_pipeline.py`)

**Dependencies**: dedup.py, config.py, datasets, transformers.tokenizer

```python
def download_redpajama(sample: bool = True) -> list[str]: ...
def build_dataset(documents: list[str], config: DeduplicationConfig) -> list[str]: ...
def tokenize_and_pack(documents: list[str], total_tokens: int, seq_len: int = 1024) -> "torch.Tensor": ...
```

### model (`model.py`)

**Dependencies**: transformers, config.py

```python
def build_gpt2_model(cfg: TrainConfig) -> "GPT2LMHeadModel": ...
```

### train (`train.py`)

**Dependencies**: model.py, data_pipeline.py, config.py

```python
def train_one_config(level: str, seed: int, tokens: "torch.Tensor", cfg: TrainConfig, ckpt_dir: str) -> str: ...
def save_checkpoint(model, step: int, ckpt_dir: str) -> None: ...
def resume_from_checkpoint(ckpt_dir: str) -> tuple: ...
```

### evaluate (`evaluate.py`)

**Dependencies**: lm_eval, train.py

```python
def run_benchmarks(checkpoint_path: str, tasks: list[str] = None) -> dict: ...
def compute_pc1_ensemble(benchmark_scores: dict[str, list[float]]) -> float: ...
```

### run_sweep (`run_sweep.py`)

**Dependencies**: dedup.py, data_pipeline.py, train.py, evaluate.py, config.py

```python
def run_full_sweep(dedup_levels: list[DeduplicationConfig], cfg: TrainConfig) -> dict: ...
```

### analyze (`analyze.py`)

**Dependencies**: run_sweep.py output (dict)

```python
def aggregate_results(results: dict) -> "pd.DataFrame": ...
def check_non_monotonicity(df: "pd.DataFrame") -> bool: ...
def compute_effect_size(df: "pd.DataFrame", level_a: str, level_b: str) -> float: ...
```

### figures (`figures.py`)

**Dependencies**: analyze.py output, matplotlib

```python
def dose_response_curve(df: "pd.DataFrame", out_path: str) -> None: ...
def benchmark_breakdown(df: "pd.DataFrame", out_path: str) -> None: ...
def data_stats_figure(dedup_stats: dict, out_path: str) -> None: ...
def loss_curves_figure(loss_logs: dict, out_path: str) -> None: ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config module | DeduplicationConfig, TrainConfig, DEDUP_LEVELS | 4 | 1+1+1+1 |
| A-2 | Dedup module | apply_deduplication + verification via text-dedup MinHash | 10 | 3+3+3+1 |
| A-3 | Data pipeline | RedPajama download, tokenize, pack to 10B tokens x 5 levels | 12 | 3+4+3+2 |
| A-4 | Model module | GPT-2 125M build via transformers config | 3 | 1+1+1+0 |
| A-5 | Training loop | AdamW+cosine, checkpoint/resume, 15 runs (5 levels x 3 seeds) | 14 | 4+3+3+4 |
| A-6 | Evaluation module | lm-eval-harness integration, PC1 ensemble computation | 9 | 2+3+3+1 |
| A-7 | Sweep orchestration | Wire dedup->data->train->eval across 15 configs | 11 | 2+4+2+3 |
| A-8 | Analysis module | Aggregate mean+-std, non-monotonicity check, effect size | 8 | 2+2+3+1 |
| A-9 | Figures module | 4 required/optional figures (dose-response, breakdown, stats, loss) | 7 | 2+2+1+2 |
| A-10 | Main entrypoint | End-to-end pipeline wiring + CLI | 5 | 1+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-5], Medium(9-13): [A-2, A-3, A-6, A-7, A-8], Low(4-8): [A-1, A-4, A-9, A-10]
