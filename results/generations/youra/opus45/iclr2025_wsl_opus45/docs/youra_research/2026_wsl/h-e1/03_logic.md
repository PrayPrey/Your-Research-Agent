# Logic Document: H-E1

**Hypothesis**: LoRA Adapter Geometric Signatures Existence Proof
**Type**: EXISTENCE (PoC)
**Date**: 2026-04-13

Applied: QR-SVD Grassmann distance pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-3: LoRA Training Pipeline [Complexity: 17, Budget: 2 subtasks]

### API Signatures

```python
# code/train.py

def verify_base_model_sha256(model_id: str) -> str:
    """Compute SHA-256 of model weight files; return hex digest."""
    ...

def load_base_model(model_id: str) -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    """Load Llama-3.2-1B-Instruct with bfloat16. Returns (model, tokenizer)."""
    ...

def build_lora_model(base_model: AutoModelForCausalLM, lora_cfg: dict) -> PeftModel:
    """Wrap base_model with PEFT LoraConfig from lora_cfg dict. Returns PeftModel."""
    ...

def set_deterministic(seed: int) -> None:
    """Set torch, cuda, cudnn seeds for reproducibility."""
    ...

def train_single_adapter(
    task_name: str,
    seed: int,
    output_dir: str,
    train_cfg: dict = None,
) -> dict:
    """
    Train one LoRA adapter. Returns metadata dict with keys:
    {task, seed, output_dir, sha256, train_loss}.
    """
    ...

def run_training_pipeline(hypothesis_folder: str) -> list[dict]:
    """
    Train all 200 adapters (8 tasks x 20 seeds each + 5 control seeds x 4 tasks).
    Returns list of metadata dicts. Skips already-saved adapters.
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, L] | B=batch_size=8, L=512 |
| lora_B (per layer) | [d_out, r] | r=32; d_out varies by layer |

### Pseudo-code: train_single_adapter

```
1. set_deterministic(seed)
2. model, tokenizer = load_base_model(BASE_MODEL_ID)
3. model = build_lora_model(model, LORA_CONFIG)
4. dataset = load_and_format_dataset(task_name)
5. tokenized = tokenize_dataset(dataset, tokenizer, max_length=512)
6. trainer = Trainer(model, AdamW lr=2e-4, warmup_ratio=0.1, epochs=3, batch=8)
7. trainer.train()
8. model.save_pretrained(output_dir)
9. return {task, seed, output_dir, sha256=verify_base_model_sha256(...), train_loss}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Model Load + SHA256 | verify_base_model_sha256, load_base_model, build_lora_model |
| L-3-2 | Deterministic Training Loop | set_deterministic, train_single_adapter, run_training_pipeline |

---

## A-4: Grassmann Distance Computation [Complexity: 14, Budget: 3 subtasks]

### API Signatures

```python
# code/analyze.py

def extract_b_matrices(adapter_path: str) -> dict[str, np.ndarray]:
    """
    Load PEFT adapter safetensors; extract all lora_B weight tensors.
    Returns {layer_name: B_matrix} e.g. {"model.layers.0.self_attn.q_proj": array}
    """
    # B_matrix shape: [d_out, r] where r=32
    ...

def compute_orthonormal_basis(B: np.ndarray) -> np.ndarray:
    """QR decomposition of B. Returns Q with orthonormal columns."""
    # B: [d_out, r] -> Q: [d_out, r]
    ...

def grassmann_distance(B1: np.ndarray, B2: np.ndarray) -> float:
    """
    Grassmann geodesic distance between column spaces of B1 and B2.
    Returns sqrt(sum(theta_i^2)) where theta_i are principal angles.
    """
    # B1, B2: [d_out, r] -> scalar float
    ...

def compute_pairwise_matrix(
    adapter_paths: list[str],
    aggregate: str = "mean",
) -> tuple[np.ndarray, list[dict]]:
    """
    Compute pairwise Grassmann distances aggregated across all target layers.
    Returns (distance_matrix, adapter_meta).
    distance_matrix: [n_adapters, n_adapters] symmetric, zero diagonal
    adapter_meta: list of {adapter_path, task, seed, category}
    """
    # adapter_paths: list of 200 paths -> (200, 200)
    ...

def split_within_between(
    distance_matrix: np.ndarray,
    adapter_meta: list[dict],
) -> tuple[np.ndarray, np.ndarray]:
    """
    Split upper-triangle distances into within-cluster and between-cluster.
    Cluster = TASK_CATEGORIES value ("reasoning" or "nlu").
    Returns (within_distances, between_distances) as 1D arrays.
    """
    # distance_matrix: [200, 200] -> within: [n_w,], between: [n_b,]
    ...

def compute_cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
    """Pooled-variance Cohen's d. Returns (mean1 - mean2) / pooled_std."""
    ...

def run_statistical_tests(
    within: np.ndarray,
    between: np.ndarray,
) -> dict:
    """
    Mann-Whitney U (alternative='less') + Cohen's d + 95% CI bootstrap.
    Returns {p_value, cohens_d, ci_95, within_mean, between_mean, passed}.
    passed = (p_value < 0.05) and (cohens_d > 0.5) and (within_mean < between_mean)
    """
    ...

def run_analysis(hypothesis_folder: str) -> dict:
    """
    Top-level: discover adapter paths, compute pairwise matrix, run stats.
    Saves pairwise_distances.npy, within_distances.npy, between_distances.npy,
    statistical_results.json to {hypothesis_folder}/results/.
    Returns stats dict from run_statistical_tests.
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| B (per layer) | [d_out, r] | r=32; d_out=2048 for attn, 8192 for MLP in Llama-3.2-1B |
| Q (after QR) | [d_out, r] | orthonormal columns |
| M = Q1.T @ Q2 | [r, r] | cross-gram matrix, r=32 |
| singular values S | [r,] = [32,] | singular values of M, in [0,1] |
| principal angles theta | [r,] = [32,] | arccos(S), in [0, pi/2] |
| per-layer distance | scalar | sqrt(sum(theta^2)) |
| pairwise_matrix | [200, 200] | symmetric, zero diagonal |
| within_distances | [n_w,] | n_w = pairs in same category |
| between_distances | [n_b,] | n_b = pairs across categories |

### Pseudo-code: grassmann_distance (critical algorithm)

```
Input: B1 [d_out, r], B2 [d_out, r]
1. Q1, _ = np.linalg.qr(B1)          # Q1: [d_out, r]
2. Q2, _ = np.linalg.qr(B2)          # Q2: [d_out, r]
3. M = Q1.T @ Q2                      # M:  [r, r]
4. S = np.linalg.svd(M, compute_uv=False)  # S: [r,], clamp to [-1,1]
5. S = np.clip(S, -1.0, 1.0)
6. thetas = np.arccos(S)              # principal angles: [r,]
7. return float(np.sqrt(np.sum(thetas ** 2)))
```

### Pseudo-code: compute_pairwise_matrix (aggregation strategy)

```
Input: adapter_paths [list of 200 str]
1. For each path, extract_b_matrices -> {layer: B}  # 7 target layers each
2. adapter_meta = [{path, task, seed, category}, ...]
3. distance_matrix = zeros(200, 200)
4. For i in range(200):
     For j in range(i+1, 200):
       layer_distances = [grassmann_distance(B_i[layer], B_j[layer])
                          for layer in target_layers]
       distance_matrix[i,j] = mean(layer_distances)
       distance_matrix[j,i] = distance_matrix[i,j]
5. return distance_matrix, adapter_meta
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | B Matrix Extraction | extract_b_matrices: load safetensors, filter lora_B keys |
| L-4-2 | QR + Grassmann Core | compute_orthonormal_basis, grassmann_distance |
| L-4-3 | Pairwise Matrix + Split | compute_pairwise_matrix, split_within_between, run_analysis |

---

## A-5: Statistical Analysis [Complexity: 11, Budget: 0 subtasks]

### API Signatures

```python
# Included in code/analyze.py (see A-4 signatures above)
# compute_cohens_d and run_statistical_tests fully specified there.

# 95% CI via bootstrap:
def _bootstrap_ci(
    within: np.ndarray,
    between: np.ndarray,
    n_boot: int = 10000,
    alpha: float = 0.05,
) -> tuple[float, float]:
    """Bootstrap 95% CI for (between_mean - within_mean). Returns (lo, hi)."""
    ...
```

---

## A-2/A-6: Low-Complexity Modules (no subtask budget)

### A-2: Dataset Preparation API

```python
# code/data.py
def load_and_format_dataset(task_name: str, max_samples: int = 2000) -> Dataset:
    """Load HF dataset for task_name, format as text prompts, return Dataset."""
    ...

def format_example(task_name: str, example: dict) -> str:
    """Format a single example as instruction prompt string."""
    ...

def tokenize_dataset(
    dataset: Dataset,
    tokenizer: AutoTokenizer,
    max_length: int = 512,
) -> Dataset:
    """Tokenize dataset. Returns Dataset with input_ids [L,] per example."""
    ...
```

### A-6: Visualization API

```python
# code/visualize.py
def plot_cluster_bar(stats: dict, out_dir: str) -> None:
    """Bar chart: within vs between means with std error bars + p/d annotation."""
    ...

def plot_distance_distributions(
    within: np.ndarray, between: np.ndarray, out_dir: str
) -> None:
    """KDE/histogram overlay of within vs between distance distributions."""
    ...

def plot_distance_heatmap(
    distance_matrix: np.ndarray, adapter_meta: list[dict], out_dir: str
) -> None:
    """Annotated heatmap [200, 200] with category color blocks on axes."""
    ...

def plot_per_category_boxplot(
    distance_matrix: np.ndarray, adapter_meta: list[dict], out_dir: str
) -> None:
    """Box plot of distances grouped by task category pairs."""
    ...

def generate_all_figures(
    hypothesis_folder: str,
    stats: dict,
    distance_matrix: np.ndarray,  # [200, 200]
    adapter_meta: list[dict],
) -> None:
    """Call all four plot functions; save PNGs to {hypothesis_folder}/figures/."""
    ...
```

---

*Generated by Phase 3 Logic Workflow | Anonymous Research Pipeline*
