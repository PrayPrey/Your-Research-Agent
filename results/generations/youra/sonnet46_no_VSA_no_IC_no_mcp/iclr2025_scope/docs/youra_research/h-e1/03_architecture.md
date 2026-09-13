# Architecture: H-E1
## Query-Aware KV Eviction — Existence (PoC)

**Applied: SnapKV prefill-observation pattern**
**Applied: H2O cumulative-attention pattern**
**Applied: LongBench eval.py F1 integration pattern**

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. Serena called on `src/` — path does not exist. No patterns to inherit.

---

## File Structure

```
h-e1/code/
  data/longbench_loader.py
  eviction/score_functions.py
  eviction/eviction.py
  evaluation/metrics.py
  evaluation/bootstrap.py
  experiment/config.py
  experiment/runner.py
  visualization/figures.py
  results/aggregator.py
h-e1/run_experiment.py
h-e1/requirements.txt
```

---

## Modules

### LongBenchLoader (`data/longbench_loader.py`)

**Dependencies**: datasets, transformers

```python
def load_task(task_name: str, tokenizer, n: int = 100, seed: int = 42,
              max_tokens: int = 4096) -> list[dict]: ...
# Returns list of {"input_ids": Tensor, "answers": list[str], "task": str}
# Shuffles with seed, takes first n, left-truncates to max_tokens, wraps in llama-2-chat template
```

---

### ScoreFunctions (`eviction/score_functions.py`)

**Dependencies**: torch

```python
def score_M0(attn_weights, **_) -> None: ...
# Returns None — signals no eviction

def score_M1(attn_weights: Tensor, window_size: int = 16) -> Tensor: ...
# attn_weights: (B, H, S, S) -> scores: (B, H, S)
# obs_window = attn_weights[:, :, -window_size:, :].mean(dim=2)

def score_M2(attn_weights: Tensor) -> Tensor: ...
# attn_weights: (B, H, S, S) -> scores: (B, H, S)
# scores = attn_weights.sum(dim=2)

def score_M6(seq_len: int, keep_n: int, sink_size: int = 4) -> Tensor: ...
# Returns positional index mask: sinks + sliding window tail
# No attn_weights needed
```

---

### Eviction (`eviction/eviction.py`)

**Dependencies**: torch, ScoreFunctions

```python
def apply_kv_eviction(
    past_key_values: tuple,
    scores: Tensor | None,
    retention_ratio: float = 0.5,
) -> tuple: ...
# per-layer: gather top-k by score; returns evicted past_key_values
# logs: "KV eviction applied: retained {keep_n}/{total} per head (layer {i})"

def verify_mechanism_activated(
    kv_before: tuple,
    kv_after: tuple,
    results_m1: dict,
    results_m0: dict,
    retention_ratio: float = 0.5,
) -> tuple[bool, dict]: ...
# Raises RuntimeError on failure
```

---

### Metrics (`evaluation/metrics.py`)

**Dependencies**: THUDM/LongBench eval.py (vendored or cloned)

```python
def compute_f1(prediction: str, answers: list[str], task: str) -> float: ...
# Thin wrapper: from eval import scorer; return scorer(prediction, answers, dataset=task)

def macro_f1(per_task_f1: dict[str, list[float]]) -> float: ...
# mean of per-task means across 4 tasks
```

---

### Bootstrap (`evaluation/bootstrap.py`)

**Dependencies**: numpy

```python
def bootstrap_delta(
    m1_scores: list[float],
    m2_scores: list[float],
    n_resamples: int = 1000,
    seed: int = 42,
) -> dict: ...
# Returns {"ci_lower": float, "ci_upper": float, "samples": ndarray}
# Resamples at example level across all 400 examples; computes macro-F1 delta per resample
```

---

### Config (`experiment/config.py`)

**Dependencies**: dataclasses

```python
@dataclass
class ExperimentConfig:
    model_id: str = "meta-llama/Llama-2-7b-chat-hf"
    tasks: list[str] = field(default_factory=lambda: ["narrativeqa","hotpotqa","2wikimqa","musique"])
    methods: list[str] = field(default_factory=lambda: ["M0","M1","M2","M6"])
    n_examples: int = 100
    seed: int = 42
    retention_ratio: float = 0.5
    window_size: int = 16
    max_tokens: int = 4096
    max_new_tokens: int = 50
    n_bootstrap: int = 1000
    output_dir: str = "h-e1"
```

---

### Runner (`experiment/runner.py`)

**Dependencies**: torch, transformers, Config, LongBenchLoader, ScoreFunctions, Eviction, Metrics

```python
def run_method(
    method: str,
    model,
    tokenizer,
    tasks_data: dict[str, list[dict]],
    cfg: ExperimentConfig,
) -> dict[str, list[float]]: ...
# Returns {task_name: [f1_per_example]}
# For each example: prefill forward with output_attentions=True,
#   compute scores, apply_kv_eviction, generate, decode, compute_f1

def run_all(cfg: ExperimentConfig) -> dict: ...
# Loads model once; iterates methods then tasks; calls run_method
# Returns {method: {task: [f1]}}
```

---

### Aggregator (`results/aggregator.py`)

**Dependencies**: json, Bootstrap, Metrics

```python
def build_results_json(
    raw: dict[str, dict[str, list[float]]],
    cfg: ExperimentConfig,
) -> dict: ...
# Computes per-task mean, macro-F1, bootstrap CI, gate check
# Saves to {cfg.output_dir}/results.json

def gate_check(results: dict) -> bool: ...
# m1_minus_m2 >= 2.0 AND bootstrap_ci_lower > 0
```

---

### Figures (`visualization/figures.py`)

**Dependencies**: matplotlib, seaborn, numpy

```python
def fig1_macro_f1_bar(results: dict, save_dir: str) -> None: ...
# Bar chart: macro-avg F1 for M0,M1,M2,M6 with 95% CI error bars

def fig2_pertask_grouped_bar(results: dict, save_dir: str) -> None: ...
# Grouped bar: per-task F1 x method (M0,M1,M2)

def fig3_bootstrap_histogram(bootstrap_samples: np.ndarray, save_dir: str) -> None: ...
# Histogram of (M1-M2) delta F1; vertical lines at 0 and 2.0

def fig4_score_heatmap(
    m1_scores: list[np.ndarray],
    m2_scores: list[np.ndarray],
    save_dir: str,
    n_examples: int = 5,
) -> None: ...
# Side-by-side heatmap: M1 vs M2 retained positions for 5 representative examples

def save_all_figures(results: dict, bootstrap_data: dict, score_samples: dict, save_dir: str) -> None: ...
```

---

### Entry Point (`run_experiment.py`)

**Dependencies**: all modules

```python
def main() -> None: ...
# torch.manual_seed(42)
# cfg = ExperimentConfig()
# raw = run_all(cfg)
# results = build_results_json(raw, cfg)
# save_all_figures(...)
# print gate result
```

---

## External Dependencies (Base Hypothesis)

None — H-E1 is the root hypothesis. No base hypothesis code to import.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data & Config | LongBenchLoader + ExperimentConfig; HF dataset loading, tokenization, llama-2-chat template, left-truncation | 9 | 2+2+2+3 |
| A-2 | Score Functions | score_M0/M1/M2/M6 in score_functions.py; attention tensor slicing logic, M6 positional mask | 10 | 2+2+4+2 |
| A-3 | KV Eviction + Verification | apply_kv_eviction() + verify_mechanism_activated(); gather ops, shape checks, logging | 11 | 2+3+3+3 |
| A-4 | Evaluation + Bootstrap | metrics.py (THUDM eval.py integration) + bootstrap.py (CI computation) | 10 | 2+3+3+2 |
| A-5 | Experiment Runner | runner.py: full prefill→evict→generate loop per method×task×example; model load once | 14 | 3+4+3+4 |
| A-6 | Results + Figures + Entry | aggregator.py, figures.py (4 figs), run_experiment.py; gate check, JSON output | 12 | 3+2+3+4 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-5], Medium(9-13): [A-1, A-2, A-3, A-4, A-6], Low(4-8): []

---

## Module Dependencies

```
run_experiment.py
  → runner.py → config.py, longbench_loader.py, score_functions.py, eviction.py, metrics.py
  → aggregator.py → bootstrap.py, metrics.py
  → figures.py
```

## Critical Implementation Notes

- `model.forward(input_ids, output_attentions=True)` — returns `(logits, past_key_values, attentions)`; attentions shape `(32_layers, B, H, S, S)`
- `model.generate(input_ids=None, past_key_values=evicted_kv, max_new_tokens=50)` — pass evicted KV directly; input_ids for generation is the last prompt token only (or empty if full prompt already processed)
- M6 score_fn does not use attn_weights; runner must handle this dispatch without calling forward with `output_attentions=True` (saves compute)
- THUDM/LongBench `eval.py` must be vendored into `h-e1/code/evaluation/` or installed; import path: `from evaluation.longbench_eval import scorer`
- Bootstrap resamples all 400 examples jointly (not per-task), then recomputes macro-F1 per resample to get delta distribution
