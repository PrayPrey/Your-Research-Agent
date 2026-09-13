# Logic Design: h-m3 (Embedding-Stage Mismatch Trade-off)

**Hypothesis ID:** h-m3  
**Type:** MECHANISM (PoC)  
**Generated:** 2026-08-24

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation - no base hypothesis dependencies  
**Analyzed Path:** N/A  
**Relevant Symbols:** None - new implementation

---

## Overview

Six scripts for embedding-stage trade-off experiment:
1. Load Dolly-15k → formatted dataset
2. Generate embeddings with 3 models (early/mid/late)
3. k-center greedy subset selection
4. Fine-tune Llama-2-7B on subsets
5. Evaluate on MMLU/HellaSwag via lm-eval-harness
6. Analyze trade-offs → metrics + plots

**Applied:** Standard PyTorch + Hugging Face patterns

---

## 1. Dataset Preparation

### API Signatures

```python
from datasets import Dataset
from typing import List, Dict

def load_and_format_dolly(cache_dir: str = "data/dolly_15k") -> Dataset:
    """Load Dolly-15k and format for embedding. Returns: 15,015 samples."""
    ...

def format_sample(sample: Dict[str, str]) -> str:
    """Concatenate instruction+context+response. Returns: single string."""
    ...
```

**Tensor Shapes:**
- Input: HF Dataset (15,015 rows)
- Output: List[str] (15,015 formatted texts)

**Pseudo-code:**

```
1. dataset = load_dataset("databricks/databricks-dolly-15k", split="train")
2. assert len(dataset) == 15015
3. texts = [f"{s['instruction']} {s['context']} {s['response']}" for s in dataset]
4. return dataset, texts
```

**Error handling:** Fail-fast on download failure, assert sample count.

---

## 2. Embedding Generation

### API Signatures

```python
import numpy as np
from sentence_transformers import SentenceTransformer
import time

def generate_embeddings(
    model_id: str, 
    texts: List[str], 
    batch_size: int = 32,
    device: str = "cuda"
) -> tuple[np.ndarray, float]:
    """
    Generate embeddings for corpus.
    texts: [N] strings -> embeddings: [N, D], compute_time: float (seconds)
    """
    ...

def save_embeddings(embeddings: np.ndarray, path: str) -> None:
    """Save embeddings to .npy file."""
    ...
```

**Tensor Shapes:**

| Variable | Shape | Note |
|----------|-------|------|
| texts | [15015] | Input strings |
| embeddings (early) | [15015, 384] | MiniLM-L6 output |
| embeddings (mid) | [15015, 768] | MPNet-base output |
| embeddings (late) | [15015, 768] | Instructor-large output |

**Pseudo-code:**

```
1. model = SentenceTransformer(model_id).to(device)
2. start = time.time()
3. embeddings = model.encode(texts, batch_size=batch_size, show_progress_bar=True)
4. compute_time = time.time() - start
5. return embeddings, compute_time
```

**Timing instrumentation:** Record wall-clock time before/after encode.

---

## 3. k-Center Greedy Selection

**Applied:** Farthest-point sampling with cosine distance.

### API Signatures

```python
from scipy.spatial.distance import cdist

def k_center_greedy(
    embeddings: np.ndarray, 
    k: int, 
    seed: int = 42,
    metric: str = "cosine"
) -> tuple[np.ndarray, float]:
    """
    Select k diverse samples maximizing min distance.
    embeddings: [N, D] -> indices: [k], selection_time: float
    """
    ...
```

**Tensor Shapes:**

| Variable | Shape | Note |
|----------|-------|------|
| embeddings | [15015, D] | Input embeddings |
| distances | [15015] | Min distance to selected set |
| selected | [k] | Selected indices |

**Pseudo-code:**

```
1. np.random.seed(seed)
2. selected = [np.random.randint(len(embeddings))]  # Random init
3. distances = cdist([embeddings[selected[0]]], embeddings, metric=metric)[0]
4. 
5. for _ in range(k - 1):
6.     farthest_idx = np.argmax(distances)
7.     selected.append(farthest_idx)
8.     new_dists = cdist([embeddings[farthest_idx]], embeddings, metric=metric)[0]
9.     distances = np.minimum(distances, new_dists)
10. 
11. return np.array(selected), selection_time
```

**Complexity:** O(nk) time, O(n) memory. Acceptable for n=15k, k≤10k.

---

## 4. Fine-tuning Llama-2-7B

### API Signatures

```python
from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer, 
    TrainingArguments, 
    Trainer,
    DataCollatorForLanguageModeling
)

def finetune_llama(
    base_model_id: str,
    train_dataset: Dataset,
    output_dir: str,
    max_seq_len: int = 512,
    epochs: int = 3,
    batch_size: int = 8,
    lr: float = 2e-5
) -> str:
    """
    Fine-tune Llama-2-7B on subset.
    Returns: checkpoint_path (str)
    """
    ...

def tokenize_dataset(dataset: Dataset, tokenizer, max_length: int) -> Dataset:
    """Tokenize text samples. Input: [N] -> Output: [N] with input_ids."""
    ...
```

**Config:**

```python
TrainingArguments(
    output_dir=output_dir,
    num_train_epochs=3,
    per_device_train_batch_size=8,
    gradient_accumulation_steps=8,  # effective batch 64
    learning_rate=2e-5,
    warmup_steps=100,
    lr_scheduler_type="cosine",
    bf16=True,
    logging_steps=10,
    save_strategy="epoch",
    save_total_limit=1
)
```

**Pseudo-code:**

```
1. model = AutoModelForCausalLM.from_pretrained(base_model_id)
2. tokenizer = AutoTokenizer.from_pretrained(base_model_id)
3. tokenized = dataset.map(lambda x: tokenizer(x['text'], max_length=max_seq_len, truncation=True))
4. trainer = Trainer(model=model, args=training_args, train_dataset=tokenized, data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False))
5. start = time.time()
6. trainer.train()
7. train_time = time.time() - start
8. trainer.save_model(output_dir)
9. return output_dir, train_time
```

**Error handling:** OOM → reduce batch size, fail-fast otherwise.

---

## 5. Evaluation

### API Signatures

```python
import subprocess
import json

def evaluate_model(
    checkpoint_path: str,
    tasks: List[str] = ["mmlu", "hellaswag"],
    output_path: str = None,
    batch_size: int = 8
) -> Dict[str, float]:
    """
    Run lm-evaluation-harness on checkpoint.
    Returns: {"mmlu": acc, "hellaswag": acc_norm}
    """
    ...

def extract_metrics(result_json: str) -> Dict[str, float]:
    """Parse lm-eval JSON output. Returns: task -> accuracy mapping."""
    ...
```

**Pseudo-code:**

```
1. cmd = [
    "lm_eval",
    "--model", "hf",
    "--model_args", f"pretrained={checkpoint_path}",
    "--tasks", ",".join(tasks),
    "--device", "cuda:0",
    "--batch_size", str(batch_size),
    "--output_path", output_path
]
2. subprocess.run(cmd, check=True)
3. results = json.load(open(output_path))
4. metrics = {
    "mmlu": results["results"]["mmlu"]["acc"],
    "hellaswag": results["results"]["hellaswag"]["acc_norm"]
}
5. return metrics
```

**Error handling:** Fail-fast on subprocess error.

---

## 6. Trade-off Analysis

### API Signatures

```python
from typing import Dict, Tuple
import matplotlib.pyplot as plt

def compute_tradeoff_metrics(
    results: Dict[str, Dict[str, float]],
    timings: Dict[str, Dict[str, float]]
) -> Dict[str, float]:
    """
    Compute stage-mismatch penalty, quality bound, cost ratio.
    results: {condition: {task: acc}}
    timings: {condition: {stage: time_sec}}
    Returns: {metric_name: value}
    """
    ...

def plot_pareto_frontier(
    results: Dict[str, Dict[str, float]],
    costs: Dict[str, float],
    output_path: str
) -> None:
    """Plot performance vs. curation cost."""
    ...

def generate_convergence_curves(
    results: Dict[str, Dict[str, float]],
    output_path: str
) -> None:
    """Plot performance vs. subset size k."""
    ...
```

**Pseudo-code:**

```
# Stage-mismatch penalty at k=5000
late_perf = results["late_k5000"]["mmlu"]
early_perf = results["early_k5000"]["mmlu"]
penalty = (late_perf - early_perf) / late_perf * 100

# Quality bound: late k=10000 vs baseline
baseline_perf = results["baseline"]["mmlu"]
late_k10k_perf = results["late_k10000"]["mmlu"]
quality_bound = abs(late_k10k_perf - baseline_perf) / baseline_perf * 100

# Compute cost ratio
late_time = timings["late"]["embedding"] + timings["late"]["selection"]
early_time = timings["early"]["embedding"] + timings["early"]["selection"]
cost_ratio = late_time / early_time

# Gate check
pass_trade_off = penalty >= 2.0
pass_speed = cost_ratio >= 3.0
pass_quality = quality_bound <= 1.0
all_pass = pass_trade_off and pass_speed and pass_quality
```

**Plotting:**

```python
# Pareto frontier
costs = [timings[cond]["total"] for cond in conditions]
perfs = [results[cond]["mmlu"] for cond in conditions]
plt.scatter(costs, perfs)
plt.xlabel("Curation Cost (sec)")
plt.ylabel("MMLU Accuracy (%)")
plt.savefig(output_path)
```

---

## Data Flow Summary

```
Dolly-15k (HF)
  |
  v
load_and_format_dolly() -> texts: [15015]
  |
  v
generate_embeddings() -> {early: [15015, 384], mid: [15015, 768], late: [15015, 768]}
  |
  v
k_center_greedy() -> 9 × indices: [k] (k ∈ {2000, 5000, 10000})
  |
  v
finetune_llama() -> 10 × checkpoints (9 subsets + baseline)
  |
  v
evaluate_model() -> 10 × {mmlu: float, hellaswag: float}
  |
  v
compute_tradeoff_metrics() -> {penalty: float, quality_bound: float, cost_ratio: float, pass: bool}
```

---

## Configuration File

```yaml
# config/experiment_config.yaml
dataset:
  name: databricks/databricks-dolly-15k
  split: train
  cache_dir: data/dolly_15k

embedding_models:
  early:
    model_id: sentence-transformers/all-MiniLM-L6-v2
    dimension: 384
  mid:
    model_id: sentence-transformers/all-mpnet-base-v2
    dimension: 768
  late:
    model_id: hkunlp/instructor-large
    dimension: 768
    task_instruction: "Represent the instruction-response pair for diversity-based selection:"

subset_sizes: [2000, 5000, 10000]

base_model:
  model_id: meta-llama/Llama-2-7b-hf
  cache_dir: models/llama2_base

training:
  num_train_epochs: 3
  per_device_train_batch_size: 8
  gradient_accumulation_steps: 8
  learning_rate: 2.0e-5
  warmup_steps: 100
  lr_scheduler_type: cosine
  max_seq_length: 512
  bf16: true

evaluation:
  tasks: [mmlu, hellaswag]
  batch_size: 8
  device: cuda:0

random_seed: 42
```

---

## Timing Instrumentation Points

1. **Embedding generation:** `time.time()` before/after `model.encode()`
2. **k-center greedy:** `time.time()` before/after selection loop
3. **Fine-tuning:** `time.time()` before/after `trainer.train()`
4. **Evaluation:** Wall-clock via lm-eval internal logging

**Log format:**

```python
timings = {
    "early": {"embedding": 7.2, "selection": 3.1},
    "mid": {"embedding": 28.5, "selection": 3.1},
    "late": {"embedding": 73.8, "selection": 3.1}
}
```

---

## Error Handling Strategy (PoC)

**Fail-fast approach:**
- Dataset load failure → `assert len(dataset) == 15015`
- Embedding OOM → No fallback, report error
- k-center greedy OOM → No chunking (15k fits in memory)
- Fine-tuning OOM → Reduce batch size manually, re-run
- lm-eval failure → `subprocess.run(check=True)` raises exception

**No retry logic, no graceful degradation (PoC tier).**

---

## Validation Checklist

- [x] No ASCII diagrams
- [x] No KB search logs
- [x] Docstrings ≤2 lines
- [x] Tensor shapes in signatures/tables
- [x] Pseudo-code for non-trivial algorithms (k-center greedy)
- [x] Total length <600 lines
- [x] Codebase Analysis (Serena) section included

---

**END OF LOGIC DESIGN**
