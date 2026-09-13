# Architecture: H-M1 (Attention Entropy Task Discrimination)

**Type:** MECHANISM
**Gate:** MUST_WORK (F-test p < 0.05)

Applied: no strong KB match for attention-entropy/LLM-probing pipelines (generic diffusion attention docs only) — architecture based on experiment brief reference implementations (bertology.py, entropy-guided-attention-llm) instead.

## Codebase Analysis (Serena)

**Project Type:** existing_codebase (H-E1 sibling, not a base_hypothesis extension — H-M1 reuses only H-E1's `cluster_labels.json` artifact, not its code)
**Status:** Verified `h-e1/code/data.py` LongBench loading pattern for consistency
**Analyzed Path:** `docs/youra_research/h-e1/code/data.py`
**Findings:** `load_task(task_name)` uses `load_dataset("THUDM/LongBench", task_name, split="test", trust_remote_code=True)`. H-M1 reuses this exact pattern; no other H-E1 modules apply (compression/eviction logic is irrelevant here).

---

## File Organization

```
h-m1/code/
  config.py           # tasks, categories, model id, paths
  data.py              # LongBench loading + tokenization (100 tokens)
  entropy.py           # attention extraction + Shannon entropy
  stats.py              # task aggregation + F-test (ANOVA)
  visualize.py          # heatmap, boxplot, gate chart
  run_experiment.py     # orchestrates full pipeline
h-m1/figures/
h-m1/entropy_matrix.npy      # (n_samples, 32, 32) raw
h-m1/task_means.json         # task -> mean entropy
h-m1/stats_results.json      # F-stat, p-value, eta^2
```

---

## Modules

### config.py

```python
TASKS: list[str]  # 21 LongBench task names
CATEGORIES: dict[str, str]  # task_name -> category (6 categories)
MODEL_ID = "meta-llama/Llama-2-7b-hf"
N_TOKENS = 100
N_SAMPLES_PER_TASK = 10
SEED = 42
```

### data.py (`code/data.py`)

**Dependencies**: config

```python
def load_task(task_name: str) -> Dataset: ...  # reuses h-e1 pattern (THUDM/LongBench, trust_remote_code=True)
def sample_task(task_name: str, n: int, seed: int) -> list[str]: ...  # returns raw text inputs
def tokenize_probe(text: str, tokenizer, n_tokens: int) -> dict: ...  # truncate to first n_tokens
```

### entropy.py (`code/entropy.py`)

**Dependencies**: config

```python
def load_model() -> tuple[AutoModelForCausalLM, AutoTokenizer]: ...  # fp16, device_map=auto, output_attentions=True
def compute_attention_entropy(attention_weights: Tensor) -> Tensor: ...  # (B,H,S,S) -> (B,H), eps=1e-10
def extract_task_entropy(model, tokenizer, samples: list[str], n_tokens: int) -> Tensor: ...  # (n_samples, 32, 32)
def verify_mechanism(model, tokenizer) -> bool: ...  # shape/finite/non-negative checks
```

### stats.py (`code/stats.py`)

**Dependencies**: config

```python
def aggregate_task_means(entropy_by_task: dict[str, Tensor]) -> dict[str, float]: ...
def compute_variance_ratio(task_means: dict[str, float], categories: dict[str, str]) -> tuple[float, float]: ...  # f_oneway -> (F, p)
def compute_eta_squared(task_means: dict[str, float], categories: dict[str, str]) -> float: ...
def evaluate_gate(p_value: float, threshold: float = 0.05) -> bool: ...
```

### visualize.py (`code/visualize.py`)

**Dependencies**: stats (reads saved json/npy)

```python
def plot_gate_metrics(f_stat: float, p_value: float, threshold: float) -> None: ...  # mandatory
def plot_entropy_heatmap(entropy_matrix: np.ndarray, tasks: list[str]) -> None: ...  # 21 tasks x 32 layers
def plot_category_boxplot(task_means: dict, categories: dict) -> None: ...
def plot_layer_discrimination(entropy_matrix: np.ndarray, tasks: list[str], categories: dict) -> None: ...
def plot_cluster_correlation(task_means: dict, cluster_labels_path: str) -> None: ...  # vs h-e1 clusters
def main() -> None: ...  # saves all to figures/
```

### run_experiment.py (`code/run_experiment.py`)

**Dependencies**: config, data, entropy, stats, visualize

```python
def run_pipeline() -> None: ...
# 1. load_model, verify_mechanism
# 2. for each task: sample_task -> tokenize -> extract_task_entropy
# 3. save entropy_matrix.npy
# 4. aggregate_task_means -> compute_variance_ratio -> compute_eta_squared
# 5. save stats_results.json, evaluate_gate
# 6. visualize.main()
def main() -> None: ...
```

---

## External Dependencies (H-E1 Artifact Reuse)

| Artifact | Path | Usage |
|----------|------|-------|
| cluster_labels.json | `h-e1/cluster_labels.json` | Read-only in `visualize.plot_cluster_correlation` for secondary correlation figure |

No H-E1 code modules imported — H-M1 is an independent measurement pipeline.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config + data loading | Task/category lists, LongBench sampling, tokenization | 7 | 2+1+2+2 |
| A-2 | Model loading + mechanism verification | Llama-2-7B fp16 load, output_attentions, verify_mechanism checks | 10 | 3+3+2+2 |
| A-3 | Entropy computation | Shannon entropy per head, batched extraction across 21 tasks x 10 samples | 12 | 3+2+4+3 |
| A-4 | Statistical analysis | Task aggregation, one-way ANOVA F-test, eta-squared, gate evaluation | 9 | 2+2+3+2 |
| A-5 | Visualization suite | Gate chart (mandatory) + heatmap + boxplot + layer analysis + cluster correlation | 8 | 2+2+2+2 |
| A-6 | Pipeline orchestration | run_experiment.py wiring all stages, artifact saving | 6 | 2+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-3, A-4], Low(4-8): [A-1, A-5, A-6]

---

## Dependencies (execution order)

A-1 -> A-2 -> A-3 -> A-4 -> A-5 -> A-6
