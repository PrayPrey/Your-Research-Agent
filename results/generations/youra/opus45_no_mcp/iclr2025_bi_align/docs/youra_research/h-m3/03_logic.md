# H-M3 Logic: Bidirectional Representation Separation

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1)
**Status**: API signatures verified from actual H-M1 code (not spec)
**Analyzed Path**: docs/youra_research/h-m1/code/
**Relevant Symbols**: `data.Task` (TypedDict), `data.load_all_tasks`, `inference.load_model`, `outputs/results.json["per_task"]` (task_id, task_type)

**Note**: H-M1 does not persist prompts, only `task_id` + `task_type` in `results.json`. H-M3 must reload raw tasks via `data.load_all_tasks()` and join on `task_id` to recover `question`/`correct_answer` text for hidden-state extraction.

---

## External Dependencies (Base Hypothesis)

```python
# From: h-m1/code/data.py (ACTUAL CODE)
class Task(TypedDict):
    task_id: str
    source_dataset: str
    question: str
    correct_answer: str
    incorrect_answers: List[str]
    category: Optional[str]

def load_all_tasks() -> List[Task]: ...

# From: h-m1/code/inference.py (ACTUAL CODE)
def load_model(model_id: str) -> Tuple:
    """fp16, device_map='auto', trust_remote_code=True, eval mode."""
    ...

# From: h-m1/code/outputs/results.json (ACTUAL DATA, not spec)
# per_task: List[{"task_id": str, "task_type": "A"|"B", "confidence_*": float}]
```

**Verified from**: `h-m1/code/data.py`, `h-m1/code/inference.py`, `h-m1/code/outputs/results.json`

---

## A-1: Data Loading & Label Join [Complexity: 2, Budget: 2]

**Applied**: Standard join on cached labels

### API Signatures

```python
def load_task_classifications(h_m1_results_path: str) -> Tuple[List[str], List[str], np.ndarray]:
    """Join h-m1 results.json per_task labels with data.load_all_tasks() prompts.
    Returns: (task_ids, prompts, labels) where labels: 0=TypeA(A), 1=TypeB(B)
    """

def build_prompt(task: Task) -> str:
    """prompt = task['question']. (question-only, matches H-M1 inference input)"""
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | load_task_classifications | Load results.json, load_all_tasks(), join on task_id |
| L-1-2 | build_prompt | Extract question text per task |

---

## A-2: Hidden State Extraction [Complexity: 4, Budget: 5]

**Applied**: Standard PyTorch — output_hidden_states forward pass, last-token pooling

### API Signatures

```python
def load_model_with_hidden_states(model_name: str) -> Tuple:
    """Wraps h-m1 inference.load_model; forces output_hidden_states=True.
    Returns: (model, tokenizer)
    """

def extract_hidden_states(
    model, tokenizer, prompts: List[str], batch_size: int = 8
) -> torch.Tensor:
    """Extract last-layer, last-token hidden states.
    Returns: Tensor [N, hidden_dim] (float32, on CPU)
    """
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, T] | Padded batch (left-pad for last-token extraction) |
| hidden_states[-1] | [B, T, H] | Last layer, H=4096 (Llama/Mistral-7B), 5120 (Llama-13B) |
| pooled | [B, H] | Last non-pad token per sequence |
| hidden_states (out) | [N, H] | N=2212 |

### Pseudo-code

```
1. tokenizer.padding_side = "left"  # so last token = index -1
2. for batch in chunks(prompts, batch_size):
3.     enc = tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=512).to(model.device)
4.     with torch.no_grad(): out = model(**enc, output_hidden_states=True)
5.     last_layer = out.hidden_states[-1]  # [B, T, H]
6.     pooled = last_layer[:, -1, :]       # left-padded -> last token real
7.     append pooled.float().cpu()
8. return torch.cat(all_pooled, dim=0)     # [N, H]
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | load_model_with_hidden_states | Load model per model_name via h-m1 load_model |
| L-2-2 | extract_hidden_states | Batched forward pass, last-token pool |
| L-2-3 | run per model | Loop over Llama-7B, Llama-13B, Mistral-7B |

---

## A-3: Separation Score & Linear Probe [Complexity: 3, Budget: 4]

**Applied**: sklearn LinearSVC + cosine_similarity (standard)

### API Signatures

```python
def compute_separation_score(
    type_a_hidden: torch.Tensor, type_b_hidden: torch.Tensor
) -> Dict[str, float]:
    """Cosine sim: intra (within A, within B) vs inter (A-B).
    Returns: {"intra_mean": float, "inter_mean": float, "separation_score": float}
    """

def train_linear_probe(hidden_states: np.ndarray, labels: np.ndarray, cv: int = 5) -> float:
    """LinearSVC + StandardScaler, StratifiedKFold cross_val_score.
    Returns: mean accuracy across folds
    """

def evaluate_gate_condition(separation_score: float, probe_accuracy: float) -> Tuple[bool, str]:
    """Gate: pass if separation_score < 0.1 OR probe_accuracy < 0.6."""
```

### Pseudo-code

```
# separation_score
intra_a = mean(cosine_sim(type_a_hidden, type_a_hidden))  # exclude diagonal
intra_b = mean(cosine_sim(type_b_hidden, type_b_hidden))  # exclude diagonal
inter   = mean(cosine_sim(type_a_hidden, type_b_hidden))
intra_mean = (intra_a * n_a + intra_b * n_b) / (n_a + n_b)
separation_score = intra_mean - inter

# probe
X = StandardScaler().fit_transform(hidden_states)
clf = LinearSVC(max_iter=5000)
scores = cross_val_score(clf, X, labels, cv=StratifiedKFold(cv), scoring="accuracy")
return scores.mean()

# gate
pass_ = (separation_score < 0.1) or (probe_accuracy < 0.6)
fail_ = (separation_score > 0.3) and (probe_accuracy > 0.8)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | compute_separation_score | Pairwise cosine sim via F.cosine_similarity |
| L-3-2 | train_linear_probe | LinearSVC 5-fold CV accuracy |
| L-3-3 | evaluate_gate_condition | Apply PRD gate thresholds |

---

## A-4: Visualization & Export [Complexity: 2, Budget: 3]

**Applied**: sklearn TSNE, matplotlib (standard)

### API Signatures

```python
def generate_tsne_plot(hidden_states: np.ndarray, labels: np.ndarray, output_path: str) -> None:
    """TSNE(n_components=2) fit_transform, scatter colored by label, save PNG."""

def generate_gate_metrics_plot(results: Dict, output_path: str) -> None:
    """Bar chart: separation_score & probe_accuracy vs thresholds, per model."""

def export_results(results: Dict, output_path: str) -> None:
    """Dump results dict to results.json."""
```

### Pseudo-code

```
1. embed = TSNE(n_components=2, random_state=42, perplexity=30).fit_transform(hidden_states)
2. scatter(embed[labels==0], color="blue", label="Type A")
3. scatter(embed[labels==1], color="red", label="Type B")
4. savefig(output_path)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | generate_tsne_plot | Per-model t-SNE scatter |
| L-4-2 | generate_gate_metrics_plot | Gate threshold bar chart |
| L-4-3 | export_results | Write results.json |

---

## A-5: Orchestration [Complexity: 2, Budget: 3]

### API Signatures

```python
def run_experiment(
    h_m1_results_path: str,
    model_names: List[str] = [
        "meta-llama/Llama-2-7b-chat-hf",
        "meta-llama/Llama-2-13b-chat-hf",
        "mistralai/Mistral-7B-Instruct-v0.2",
    ],
    output_dir: str = "h-m3/code/outputs",
    seed: int = 42,
) -> Dict:
    """Run full H-M3 pipeline across all models, return aggregate + per-model results."""
```

### Pseudo-code

```
1. task_ids, prompts, labels = load_task_classifications(h_m1_results_path)
2. for model_name in model_names:
3.     model, tok = load_model_with_hidden_states(model_name)
4.     hidden = extract_hidden_states(model, tok, prompts)  # [N, H]
5.     type_a_hidden, type_b_hidden = hidden[labels==0], hidden[labels==1]
6.     sep = compute_separation_score(type_a_hidden, type_b_hidden)
7.     probe_acc = train_linear_probe(hidden.numpy(), labels)
8.     gate_pass, reason = evaluate_gate_condition(sep["separation_score"], probe_acc)
9.     generate_tsne_plot(hidden.numpy(), labels, f"figures/tsne_{model_name}.png")
10.    store per-model results
11. generate_gate_metrics_plot(all_results, "figures/gate_metrics.png")
12. export_results(all_results, f"{output_dir}/results.json")
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | run_experiment | Main orchestration loop |
| L-5-2 | seed control | torch.manual_seed(42), np.random.seed(42) |

---

## Tensor Shapes Summary

| Variable | Shape | Description |
|----------|-------|--------------|
| hidden_states | (2212, 4096) | All task hidden states (7B models; 5120 for 13B) |
| type_a_hidden | (1977, 4096) | Type A task hidden states |
| type_b_hidden | (235, 4096) | Type B task hidden states |
| labels | (2212,) | 0=TypeA, 1=TypeB |
| tsne_embed | (2212, 2) | 2D projection for plotting |
