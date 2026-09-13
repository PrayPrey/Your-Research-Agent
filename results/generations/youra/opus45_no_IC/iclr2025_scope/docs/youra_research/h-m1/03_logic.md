# Logic: H-M1 (Attention Entropy Task Discrimination)

**Applied**: No strong KB match for attention entropy — used experiment brief reference pattern (bertology.py / entropy-guided-attention-llm).

## Codebase Analysis (Serena)

**Project Type**: green-field (h-m1/code/ does not exist yet)
**Status**: Green-field project - designing new APIs. Architecture doc already verified H-E1's `load_task` pattern via Serena for data.py consistency; no base_hypothesis code dependency exists (H-M1 only reads `h-e1/cluster_labels.json` as a JSON artifact, not code).
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Config + Data Loading [Complexity: 7, Budget: 7]

**Applied**: Standard PyTorch/HF dataset loading, reuses H-E1 `load_task` pattern.

### API Signatures

```python
# config.py
TASKS: list[str]                    # 21 LongBench task names
CATEGORIES: dict[str, str]          # task_name -> one of 6 categories
MODEL_ID: str = "meta-llama/Llama-2-7b-hf"
N_TOKENS: int = 100
N_SAMPLES_PER_TASK: int = 10
SEED: int = 42

# data.py
def load_task(task_name: str) -> Dataset:
    """THUDM/LongBench split='test', trust_remote_code=True (H-E1 pattern)."""
    ...

def sample_task(task_name: str, n: int, seed: int) -> list[str]:
    """Deterministic sample of n raw 'context' strings from task."""
    ...

def tokenize_probe(text: str, tokenizer: AutoTokenizer, n_tokens: int) -> dict:
    """Tokenize + truncate. Returns {'input_ids': [1, <=n_tokens], 'attention_mask': [1, <=n_tokens]}"""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | TASKS/CATEGORIES constants | Hardcode 21 tasks -> 6 categories mapping from PRD |
| L-1-2 | load_task | Wrap load_dataset with trust_remote_code=True |
| L-1-3 | sample_task | random.Random(seed).sample on dataset['context'], fallback to first n if <n items |
| L-1-4 | tokenize_probe | tokenizer(text, return_tensors='pt', truncation=True, max_length=n_tokens) |

---

## A-2: Model Loading + Mechanism Verification [Complexity: 10, Budget: 10]

**Applied**: Standard PyTorch/HF fp16 causal LM load with output_attentions.

### API Signatures

```python
# entropy.py
def load_model() -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    """fp16, device_map='auto', output_attentions=True."""
    ...

def verify_mechanism(model: AutoModelForCausalLM, sample_input: dict) -> bool:
    """Checks: attentions not None, 32 layers, attn.shape[1]==32,
    entropy finite, entropy >= 0. Raises AssertionError on failure."""
    ...
```

### Pseudo-code

```
1. model = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=fp16, device_map="auto", output_attentions=True)
2. tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
3. outputs = model(**sample_input, output_attentions=True)
4. assert outputs.attentions is not None and len(outputs.attentions) == 32
5. assert outputs.attentions[0].shape[1] == 32
6. entropy = compute_attention_entropy(outputs.attentions[0])
7. assert torch.isfinite(entropy).all() and entropy.min() >= 0
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | load_model (3) | from_pretrained fp16 + device_map=auto + output_attentions=True |
| L-2-2 | verify_mechanism structure (3) | shape/layer/head assertion checks |
| L-2-3 | verify_mechanism numerics (2) | finite + non-negative entropy checks |
| L-2-4 | wiring into run_experiment (2) | call before main extraction loop, abort on AssertionError |

---

## A-3: Entropy Computation [Complexity: 12, Budget: 12]

**Applied**: Shannon entropy per bertology.py / entropy-guided-attention-llm pattern.

### API Signatures

```python
def compute_attention_entropy(attention_weights: Tensor) -> Tensor:
    """attention_weights: [B, H, S, S] (already softmaxed) -> entropy: [B, H].
    eps=1e-10 for numerical stability, mean over query positions (dim=-2)."""
    ...

def extract_task_entropy(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    samples: list[str],
    n_tokens: int = 100,
) -> Tensor:
    """Runs forward pass per sample, stacks per-layer entropy.
    Returns: [n_samples, 32, 32]  (n_samples, layers, heads)"""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| attention_weights (per layer) | [1, 32, S, S] | S <= 100 (n_tokens) |
| entropy (per layer) | [1, 32] | mean over key dim, then over query dim |
| sample_entropy (stacked layers) | [1, 32, 32] | layers x heads |
| extract_task_entropy output | [n_samples, 32, 32] | per task |
| full entropy_matrix.npy | [210, 32, 32] | all tasks concatenated |

### Pseudo-code

```
def compute_attention_entropy(attention_weights):
    eps = 1e-10
    p = attention_weights + eps                       # [B,H,S,S]
    log_p = torch.log(p)
    entropy = -(p * log_p).sum(dim=-1)                 # [B,H,S] sum over keys
    return entropy.mean(dim=-1)                        # [B,H] mean over queries

def extract_task_entropy(model, tokenizer, samples, n_tokens=100):
    all_entropies = []
    for text in samples:
        inputs = tokenize_probe(text, tokenizer, n_tokens)
        with torch.no_grad():
            outputs = model(**inputs.to(model.device), output_attentions=True)
        layer_entropies = [compute_attention_entropy(a).cpu() for a in outputs.attentions]  # 32 x [1,32]
        all_entropies.append(torch.stack(layer_entropies, dim=1))  # [1,32,32]
    return torch.cat(all_entropies, dim=0)  # [n_samples,32,32]
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | compute_attention_entropy (3) | eps-stabilized Shannon entropy, mean over query dim |
| L-3-2 | extract_task_entropy loop (2) | per-sample forward pass, no_grad |
| L-3-3 | batched extraction across 21 tasks x 10 samples (4) | orchestration in run_experiment, dict[task_name] -> Tensor[10,32,32] |
| L-3-4 | assemble entropy_matrix.npy (3) | concat all tasks in TASKS order -> [210,32,32], save via np.save |

---

## A-4: Statistical Analysis [Complexity: 9, Budget: 9]

**Applied**: scipy.stats.f_oneway one-way ANOVA.

### API Signatures

```python
# stats.py
def aggregate_task_means(entropy_by_task: dict[str, Tensor]) -> dict[str, float]:
    """entropy_by_task[task]: [n_samples,32,32] -> scalar mean per task."""
    ...

def compute_variance_ratio(
    task_means: dict[str, float], categories: dict[str, str]
) -> tuple[float, float]:
    """Groups task_means by category, runs f_oneway. Returns (f_stat, p_value)."""
    ...

def compute_eta_squared(task_means: dict[str, float], categories: dict[str, str]) -> float:
    """eta^2 = SS_between / SS_total across category groups."""
    ...

def evaluate_gate(p_value: float, threshold: float = 0.05) -> bool:
    """PASS if p_value < threshold."""
    ...
```

### Pseudo-code

```
def aggregate_task_means(entropy_by_task):
    return {task: ent.mean().item() for task, ent in entropy_by_task.items()}  # (21,) -> scalars

def compute_variance_ratio(task_means, categories):
    groups_by_cat = {}
    for task, mean in task_means.items():
        groups_by_cat.setdefault(categories[task], []).append(mean)
    f_stat, p_value = scipy.stats.f_oneway(*groups_by_cat.values())
    return f_stat, p_value

def compute_eta_squared(task_means, categories):
    grand_mean = mean(task_means.values())
    ss_between = sum(len(g) * (mean(g) - grand_mean)**2 for g in groups_by_cat.values())
    ss_total = sum((v - grand_mean)**2 for v in task_means.values())
    return ss_between / ss_total
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | aggregate_task_means (2) | per-task scalar mean over [n_samples,32,32] |
| L-4-2 | compute_variance_ratio (2) | group by category, f_oneway |
| L-4-3 | compute_eta_squared (3) | SS_between/SS_total computation |
| L-4-4 | evaluate_gate + save stats_results.json (2) | {f_stat, p_value, eta_squared, gate_pass} |

---

## A-5: Visualization Suite [Complexity: 8, Budget: 8]

**Applied**: matplotlib standard plotting, reads saved npy/json artifacts.

### API Signatures

```python
# visualize.py
def plot_gate_metrics(f_stat: float, p_value: float, threshold: float = 0.05) -> None:
    """Mandatory. Bar/line chart with p=0.05 threshold marker."""
    ...

def plot_entropy_heatmap(entropy_matrix: np.ndarray, tasks: list[str]) -> None:
    """entropy_matrix: [n_samples,32,32] -> mean over samples & heads -> [21,32] heatmap."""
    ...

def plot_category_boxplot(task_means: dict[str, float], categories: dict[str, str]) -> None:
    """Boxplot of task_means grouped by 6 categories."""
    ...

def plot_layer_discrimination(
    entropy_matrix: np.ndarray, tasks: list[str], categories: dict[str, str]
) -> None:
    """Per-layer F-stat across categories -> [32] line plot."""
    ...

def plot_cluster_correlation(task_means: dict[str, float], cluster_labels_path: str) -> None:
    """Scatter/bar of task_means vs h-e1 cluster_labels.json assignment."""
    ...

def main() -> None:
    """Loads entropy_matrix.npy, task_means.json, stats_results.json; calls all plot_* ; saves to figures/."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | plot_gate_metrics (2) | mandatory gate chart |
| L-5-2 | plot_entropy_heatmap + plot_category_boxplot (2) | 21x32 heatmap, category boxplot |
| L-5-3 | plot_layer_discrimination (2) | per-layer F-stat line plot |
| L-5-4 | plot_cluster_correlation + main() (2) | read h-e1 artifact, orchestrate saves to figures/ |

---

## A-6: Pipeline Orchestration [Complexity: 6, Budget: 6]

**Applied**: Standard PyTorch/HF orchestration.

### API Signatures

```python
# run_experiment.py
def run_pipeline() -> dict:
    """Full pipeline. Returns results dict:
    {f_stat, p_value, eta_squared, gate_pass, task_means, runtime_sec}"""
    ...

def main() -> None:
    """CLI entrypoint, calls run_pipeline(), prints gate result."""
    ...
```

### Pseudo-code

```
def run_pipeline():
    model, tokenizer = load_model()
    verify_mechanism(model, tokenize_probe(sample_task(TASKS[0],1,SEED)[0], tokenizer, N_TOKENS))

    entropy_by_task = {}
    for task in TASKS:
        samples = sample_task(task, N_SAMPLES_PER_TASK, SEED)
        entropy_by_task[task] = extract_task_entropy(model, tokenizer, samples, N_TOKENS)

    entropy_matrix = torch.cat([entropy_by_task[t] for t in TASKS], dim=0)  # [210,32,32]
    np.save("entropy_matrix.npy", entropy_matrix.numpy())

    task_means = aggregate_task_means(entropy_by_task)
    f_stat, p_value = compute_variance_ratio(task_means, CATEGORIES)
    eta_sq = compute_eta_squared(task_means, CATEGORIES)
    gate_pass = evaluate_gate(p_value)

    save_json("stats_results.json", {f_stat, p_value, eta_sq, gate_pass})
    save_json("task_means.json", task_means)
    visualize.main()
    return {f_stat, p_value, eta_sq, gate_pass, task_means}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | run_pipeline stage 1-2 (2) | load_model, verify_mechanism, per-task extraction loop |
| L-6-2 | run_pipeline stage 3 (2) | entropy_matrix assembly + save |
| L-6-3 | run_pipeline stage 4-5 (1) | stats + gate eval + save json |
| L-6-4 | main() + visualize call (1) | CLI wiring, print PASS/FAIL |
