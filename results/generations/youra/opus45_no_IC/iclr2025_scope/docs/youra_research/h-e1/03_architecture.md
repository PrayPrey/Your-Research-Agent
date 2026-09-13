# Architecture: H-E1 (EXISTENCE PoC)

**Type:** EXISTENCE — minimal pipeline to test "does k*>1 exist?"
**Budget Tier:** LIGHT

Applied: no strong KB match for KV-cache/gap-statistic pipelines (generic diffusion/attention docs only) — architecture based on PRD reference implementations (milesgranger/gap_statistic, FMInference/H2O, THUDM/LongBench) instead.

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field — no existing code to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch; Serena skipped per green-field rule.

---

## File Organization

```
h-e1/code/
  config.py          # task list, 6 compression configs, paths
  data.py             # LongBench loading + truncation
  compression.py      # H2O eviction + int8/int4 quant wrappers
  model.py            # Llama-2-7B load + generate w/ config applied
  evaluate.py         # LongBench per-task metric scoring
  run_experiment.py   # orchestrates 21x6 runs -> response_matrix.npy
  cluster.py           # gap statistic + silhouette
  visualize.py         # figures
h-e1/figures/
h-e1/response_matrix.npy
h-e1/gap_results.json
h-e1/cluster_labels.json
```

---

## Modules

### config.py

```python
TASKS: list[str]  # 21 LongBench task names
COMPRESSION_CONFIGS: list[dict]  # 6 configs: method/retention/quantization
MODEL_ID = "meta-llama/Llama-2-7b-hf"
MAX_TOKENS = 4096
```

### data.py (`code/data.py`)

**Dependencies**: config

```python
def load_task(task_name: str) -> Dataset: ...
def truncate_sample(sample: dict, tokenizer, max_tokens: int) -> dict: ...
```

### compression.py (`code/compression.py`)

**Dependencies**: config

```python
def apply_h2o(model, retention: float): ...          # sets heavy/recent ratio via H2O attn patch
def apply_quantization(model_id: str, quant: str | None) -> AutoModelForCausalLM: ...  # bnb int8/int4 load
def build_model_for_config(config: dict) -> tuple[model, tokenizer]: ...
```

### model.py (`code/model.py`)

**Dependencies**: compression

```python
def generate(model, tokenizer, prompt: str, max_new_tokens: int) -> str: ...
```

### evaluate.py (`code/evaluate.py`)

**Dependencies**: data

```python
def score_task(task_name: str, predictions: list[str], references: list) -> float: ...
# dispatches to qa_f1_score / rouge_score / classification_score / retrieval_score / code_sim_score
```

### run_experiment.py (`code/run_experiment.py`)

**Dependencies**: config, data, compression, model, evaluate

```python
def evaluate_task_with_config(model, tokenizer, task_data, config: dict) -> float: ...
def compute_response_matrix(tasks: list[str], configs: list[dict]) -> np.ndarray: ...  # (21,6)
def main() -> None: ...  # saves response_matrix.npy
```

### cluster.py (`code/cluster.py`)

**Dependencies**: none (numpy/sklearn/gap_statistic)

```python
def find_optimal_clusters(response_matrix: np.ndarray, n_refs: int = 500, max_k: int = 6) -> tuple[int, "pd.DataFrame", bool]: ...
def compute_silhouette(response_matrix: np.ndarray, k_star: int) -> float: ...
def main() -> None: ...  # loads response_matrix.npy, saves gap_results.json, cluster_labels.json
```

### visualize.py (`code/visualize.py`)

**Dependencies**: cluster (reads saved json/npy)

```python
def plot_gate_metrics(gap_df, k_star: int, significant: bool) -> None: ...      # mandatory
def plot_gap_curve(gap_df, k_star: int) -> None: ...
def plot_response_heatmap(response_matrix, tasks, configs) -> None: ...
def plot_cluster_pca(response_matrix, labels) -> None: ...
def plot_silhouette(response_matrix, labels) -> None: ...
def main() -> None: ...  # saves all to figures/
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config + data loading | TASKS list, 6 configs, LongBench loader/truncation | 8 | 2+2+2+2 |
| A-2 | Model + compression wrappers | Llama-2-7B load, H2O eviction, int8/int4 quant | 14 | 4+3+4+3 |
| A-3 | Evaluation metrics | LongBench per-task scoring (5 metric types) | 9 | 2+2+3+2 |
| A-4 | Response matrix pipeline | 126 runs orchestration, retention normalization, save npy | 12 | 3+3+3+3 |
| A-5 | Gap statistic clustering | OptimalK, silhouette, cluster labels | 8 | 2+2+3+1 |
| A-6 | Visualization suite | 5 figures incl. mandatory gate chart | 6 | 2+1+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-2], Medium(9-13): [A-3, A-4], Low(4-8): [A-1, A-5, A-6]

---

## Dependencies (execution order)

A-1 -> A-2 -> A-3 -> A-4 -> A-5 -> A-6
