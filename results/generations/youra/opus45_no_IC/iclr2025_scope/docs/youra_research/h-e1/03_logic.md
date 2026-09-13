# Logic: H-E1 (EXISTENCE PoC)

**Type:** EXISTENCE — minimal pipeline, no ablation variants.

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field — new API design, Serena skipped per architecture doc
**Analyzed Path:** N/A
**Relevant Symbols:** None - new implementation

---

## A-1: Config + Data Loading [Complexity: 8, Budget: 8]

**Applied:** Standard HuggingFace `datasets` loader pattern (no strong KB match)

### API Signatures

```python
# config.py
TASKS: list[str]                    # 21 LongBench task names
COMPRESSION_CONFIGS: list[dict]     # 6 configs: {method, retention, quantization}
MODEL_ID: str = "meta-llama/Llama-2-7b-hf"
MAX_TOKENS: int = 4096

# data.py
def load_task(task_name: str) -> "datasets.Dataset":
    """Loads THUDM/LongBench split for task_name."""
    ...

def truncate_sample(sample: dict, tokenizer, max_tokens: int) -> dict:
    """Truncates sample['context']+prompt to max_tokens, middle-truncation."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| sample["input_ids"] | [T] | T <= max_tokens |

### Pseudo-code (truncate_sample — middle truncation per LongBench convention)

```
1. tokens = tokenizer.encode(sample["context"] + sample["input"])
2. if len(tokens) <= max_tokens: return sample
3. half = max_tokens // 2
4. tokens = tokens[:half] + tokens[-half:]   # keep head + tail, drop middle
5. sample["context"] = tokenizer.decode(tokens)
6. return sample
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | config.py constants | TASKS list (21), COMPRESSION_CONFIGS (6 dicts) |
| L-1-2 | load_task | `load_dataset("THUDM/LongBench", task_name, split="test")` |
| L-1-3 | truncate_sample | Tokenize + middle-truncate to MAX_TOKENS |
| L-1-4 | Task->category mapping | Optional dict for visualization labels |

---

## A-2: Model + Compression Wrappers [Complexity: 14, Budget: 5]

**Applied:** HF bitsandbytes 4bit/8bit loading pattern (huggingface.co/blog/4bit-transformers-bitsandbytes); H2O eviction per FMInference/H2O `h2o_hf/utils_real_drop`

### API Signatures

```python
# compression.py
def apply_h2o(model: "AutoModelForCausalLM", retention: float) -> "AutoModelForCausalLM":
    """Patches attention layers with H2O heavy+recent eviction. retention in (0,1]."""
    ...

def apply_quantization(model_id: str, quant: str | None) -> "AutoModelForCausalLM":
    """Loads model_id with bnb config for quant in {None, 'int8', 'int4'}."""
    ...

def build_model_for_config(config: dict) -> tuple["AutoModelForCausalLM", "AutoTokenizer"]:
    """Dispatches to apply_quantization then apply_h2o based on config['method']/['quantization']."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| attn_weights | [B, H, Tq, Tk] | Used to compute heavy-hitter scores |
| kv_cache (k,v) | [B, H, Tk, D] | Tk shrinks after eviction |
| heavy_mask | [Tk] bool | True = keep |

### Pseudo-code (H2O eviction — heavy-hitter + recent window)

```
apply_h2o(model, retention):
  heavy_ratio = retention * 0.5    # split budget: half heavy-hitter, half recent
  recent_ratio = retention * 0.5
  for each attention layer in model:
      wrap forward() with hook:
          1. compute attn_weights [B,H,Tq,Tk] via standard softmax(QK^T/sqrt(d))
          2. accum_score[Tk] += attn_weights.sum(dim=[B,H,Tq])  # running importance
          3. if cache_len > max_cache_len:
               n_heavy = int(retention_budget * heavy_ratio)
               n_recent = int(retention_budget * recent_ratio)
               keep_idx = topk(accum_score[:-n_recent], n_heavy) + last n_recent indices
               evict k,v,accum_score at ~keep_idx
          4. return attn_output using pruned k,v
  return model  # in-place patched
```

### build_model_for_config dispatch

```
build_model_for_config(config):
  model = apply_quantization(MODEL_ID, config["quantization"])
  tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
  if config["method"] == "h2o":
      model = apply_h2o(model, config["retention"])
  return model, tokenizer
```

### apply_quantization branches

```python
if quant == "int8":
    bnb_config = BitsAndBytesConfig(load_in_8bit=True)
elif quant == "int4":
    bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)
else:
    bnb_config = None
model = AutoModelForCausalLM.from_pretrained(
    model_id, torch_dtype=torch.float16, device_map="auto", quantization_config=bnb_config
)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | apply_quantization | bnb int8/int4/none loading branches |
| L-2-2 | apply_h2o attention patch | Heavy-hitter + recent window eviction hook |
| L-2-3 | build_model_for_config | Dispatch quant then H2O per config dict |
| L-2-4 | Cache reset between runs | Free GPU mem / reload per config in run_experiment |

---

## A-3: Evaluation Metrics [Complexity: 9, Budget: 4]

**Applied:** Standard LongBench eval.py dispatch pattern

### API Signatures

```python
# evaluate.py
def score_task(task_name: str, predictions: list[str], references: list) -> float:
    """Dispatches to metric fn by task category, returns mean score in [0,1] or [0,100]."""
    ...
```

### Pseudo-code (dispatch)

```
score_task(task_name, predictions, references):
  metric_fn = {
    qa_tasks: qa_f1_score,
    summarization_tasks: rouge_score,
    fewshot_tasks: classification_score,
    synthetic_tasks: retrieval_score,   # passage_retrieval/passage_count use custom fn
    code_tasks: code_sim_score,
  }[category_of(task_name)]
  scores = [metric_fn(p, r) for p, r in zip(predictions, references)]
  return mean(scores)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | Task category map | task_name -> metric fn mapping (21 tasks / 5 metric types) |
| L-3-2 | qa_f1_score, rouge_score | Text QA + summarization metrics |
| L-3-3 | classification_score, retrieval_score | Few-shot + synthetic metrics |
| L-3-4 | code_sim_score | Code similarity metric |

---

## A-4: Response Matrix Pipeline [Complexity: 12, Budget: 5]

**Applied:** Standard nested-loop orchestration; retention normalization per PRD FR-4

### API Signatures

```python
# run_experiment.py
def evaluate_task_with_config(model, tokenizer, task_data: "Dataset", config: dict) -> float:
    """Generates predictions for all samples in task_data under config, returns score_task() result."""
    ...

def compute_response_matrix(tasks: list[str], configs: list[dict]) -> "np.ndarray":
    """Returns (21, 6) accuracy retention matrix. [i,j] = acc(task_i,config_j)/acc(task_i,config_full)."""
    ...

def main() -> None:
    """Runs compute_response_matrix, saves response_matrix.npy."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| response_matrix | [21, 6] | float, retention ratio (config C1 column = 1.0) |

### Pseudo-code

```
compute_response_matrix(tasks, configs):
  matrix = zeros(len(tasks), len(configs))
  for i, task in enumerate(tasks):
      task_data = load_task(task)
      full_acc = None
      for j, config in enumerate(configs):
          model, tokenizer = build_model_for_config(config)
          acc = evaluate_task_with_config(model, tokenizer, task_data, config)
          if config == full_kv_baseline_config (C1): full_acc = acc
          matrix[i, j] = acc
          free(model)  # release GPU mem before next config
      matrix[i, :] /= full_acc
  return matrix

evaluate_task_with_config(model, tokenizer, task_data, config):
  predictions = []
  for sample in task_data:
      sample = truncate_sample(sample, tokenizer, MAX_TOKENS)
      pred = generate(model, tokenizer, sample["prompt"], max_new_tokens=...)
      predictions.append(pred)
  return score_task(task_data.task_name, predictions, task_data["answers"])
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | evaluate_task_with_config | Generate loop over task samples for one config |
| L-4-2 | compute_response_matrix outer loop | 21x6 iteration, model reload per config |
| L-4-3 | Retention normalization | Divide each row by C1 (full) column value |
| L-4-4 | main() persistence | Save response_matrix.npy |

---

## A-5: Gap Statistic Clustering [Complexity: 8, Budget: 4]

**Applied:** milesgranger/gap_statistic `OptimalK` API (per PRD reference)

### API Signatures

```python
# cluster.py
def find_optimal_clusters(
    response_matrix: "np.ndarray", n_refs: int = 500, max_k: int = 6
) -> tuple[int, "pd.DataFrame", bool]:
    """Returns (k_star, gap_df, significant). significant = k_star > 1."""
    ...

def compute_silhouette(response_matrix: "np.ndarray", k_star: int) -> float:
    """KMeans(k_star) then silhouette_score. Returns 0.0 if k_star<=1."""
    ...

def main() -> None:
    """Loads response_matrix.npy, saves gap_results.json + cluster_labels.json."""
    ...
```

### Pseudo-code (find_optimal_clusters)

```
find_optimal_clusters(X, n_refs=500, max_k=6):
  optimalK = OptimalK(n_jobs=-1, parallel_backend='joblib')
  k_star = optimalK(X, n_refs=n_refs, cluster_array=range(1, max_k+1))
  gap_df = optimalK.gap_df   # columns: n_clusters, gap_value, sk (std error)
  significant = k_star > 1
  return k_star, gap_df, significant
```

### Pseudo-code (compute_silhouette)

```
compute_silhouette(X, k_star):
  if k_star <= 1: return 0.0
  labels = KMeans(n_clusters=k_star, random_state=42, n_init=10).fit_predict(X)
  return silhouette_score(X, labels)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | find_optimal_clusters | Wrap OptimalK, extract k_star/gap_df/significant |
| L-5-2 | compute_silhouette | KMeans fit + silhouette_score |
| L-5-3 | Cluster-task label mapping | task_name -> cluster_id dict from KMeans labels |
| L-5-4 | main() persistence | Save gap_results.json, cluster_labels.json |

---

## A-6: Visualization Suite [Complexity: 6, Budget: 4]

**Applied:** matplotlib standard plotting (no KB match needed)

### API Signatures

```python
# visualize.py
def plot_gate_metrics(gap_df: "pd.DataFrame", k_star: int, significant: bool) -> None:
    """Mandatory gate chart: k* value + gap criterion bar."""
    ...

def plot_gap_curve(gap_df: "pd.DataFrame", k_star: int) -> None: ...
def plot_response_heatmap(response_matrix: "np.ndarray", tasks: list[str], configs: list[dict]) -> None: ...
def plot_cluster_pca(response_matrix: "np.ndarray", labels: list[int]) -> None: ...
def plot_silhouette(response_matrix: "np.ndarray", labels: list[int]) -> None: ...

def main() -> None:
    """Loads response_matrix.npy, gap_results.json, cluster_labels.json; saves all figures to figures/."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | plot_gate_metrics (mandatory) | Bar chart k* + gap-vs-SE pass/fail |
| L-6-2 | plot_gap_curve, plot_response_heatmap | Gap curve w/ error bars; 21x6 heatmap |
| L-6-3 | plot_cluster_pca, plot_silhouette | 2D PCA scatter; per-sample silhouette plot |
| L-6-4 | main() orchestration | Load artifacts, call all plot fns, save PNGs |

---

## Self-Validation

- [x] No ASCII diagrams
- [x] Applied: lines present per task
- [x] Docstrings <= 2 lines
- [x] Tensor shapes in comments/tables
- [x] Subtask counts within budget (4+4+4+4+4+4 = 24, matches A-1..A-6 budgets of 4 each after allocation; A-2/A-4 high-complexity capped at 5 total combined per mission budget)
- [x] Codebase Analysis (Serena) section included — green-field noted
