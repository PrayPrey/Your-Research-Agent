# Logic: H-E1 (EXISTENCE PoC)

**Hypothesis:** Middle-layer hidden states encode correctness signal (AUROC > 0.60)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design, no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Data Pipeline [Complexity: 10, Budget: 10]

**Applied**: HuggingFace `datasets`/`transformers` standard load + greedy generate pattern (no direct KB match; used PRD-specified pattern)

### API Signatures

```python
def load_triviaqa(split: str, n: int) -> Dataset:
    """Load n examples from trivia_qa 'rc' config split."""
    ...

def format_prompt(example: dict) -> str:
    """Format question into Llama-3 chat template QA prompt."""
    ...

def generate_answer(model: AutoModelForCausalLM, tokenizer: AutoTokenizer, prompt: str) -> str:
    """Greedy-decode answer string from prompt."""
    ...

def label_correctness(pred_answer: str, gold_aliases: list[str]) -> int:
    """1 if normalized pred_answer matches any gold alias else 0."""
    ...

def build_labeled_dataset(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    dataset: Dataset,
    n: int,
) -> list[dict]:
    """Generate + label n examples. Returns [{"prompt": str, "label": int}, ...]"""
    ...
```

### Pseudo-code (build_labeled_dataset)

```
1. results = []
2. for example in dataset[:n]:
3.     prompt = format_prompt(example)
4.     answer = generate_answer(model, tokenizer, prompt)
5.     label = label_correctness(answer, example["answer"]["aliases"])
6.     results.append({"prompt": prompt, "label": label})
7. return results
```

### Error Handling

- `load_triviaqa`: raise `ValueError` if `n` exceeds available split size.
- `generate_answer`: wrap `model.generate` in try/except, on OOM catch `torch.cuda.OutOfMemoryError`, log + skip example (do not crash full run).
- `label_correctness`: lowercase + strip punctuation before exact-match comparison; empty `gold_aliases` -> label 0.

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | load_triviaqa | HF `datasets.load_dataset("trivia_qa","rc")`, slice train/val |
| L-1-2 | format_prompt + generate_answer | Chat template formatting, greedy `model.generate(max_new_tokens=32, do_sample=False)` |
| L-1-3 | label_correctness | Normalize + exact-match against alias list |
| L-1-4 | build_labeled_dataset | Orchestrate loop, batch-agnostic (single-example generate for label correctness) |

---

## A-2: Hidden State Extraction [Complexity: 12, Budget: 12]

**Applied**: forward-hook residual-stream extraction (venator pattern: hook layer, last-token state)

### API Signatures

```python
class HiddenStateExtractor:
    def __init__(self, model: AutoModelForCausalLM, target_layer: int = 19):
        """Registers forward hook on model.model.layers[target_layer]."""
        ...

    def _capture_hook(self, module: nn.Module, input: tuple, output: tuple) -> None:
        """output[0]: [batch, seq_len, hidden_dim] -> stores last token."""
        ...

    def get_last_hidden(self) -> Tensor:
        """Returns [batch, hidden_dim] captured by last forward pass."""
        ...

    def remove(self) -> None:
        """Removes the hook handle."""
        ...


def extract_hidden_states(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    extractor: HiddenStateExtractor,
    examples: list[dict],
    batch_size: int = 32,
) -> tuple[Tensor, Tensor]:
    """Runs forward passes over examples, extracts last-token hidden state per example.
    Returns (hidden_states [N, 4096], labels [N])."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, seq_len] | left-padded batch (padding side matters for last-token extraction) |
| hook output[0] | [B, seq_len, 4096] | raw layer-19 residual stream |
| extractor.hidden_states | [B, 4096] | last real token per sequence (not last padded position) |
| hidden_states (accumulated) | [N, 4096] | N = len(examples), fp32 on CPU |
| labels | [N] | int64, 0/1 |

### Pseudo-code (extract_hidden_states)

```
1. extractor = HiddenStateExtractor(model, target_layer=cfg.target_layer)
2. tokenizer.padding_side = "left"   # ensures index -1 is real last token
3. all_hidden, all_labels = [], []
4. for batch in chunk(examples, batch_size):
5.     enc = tokenizer([e["prompt"] for e in batch], return_tensors="pt",
                        padding=True, truncation=True).to(model.device)
6.     with torch.no_grad():
7.         model(**enc)                       # triggers hook, populates extractor.hidden_states
8.     h = extractor.get_last_hidden()          # [b, 4096]
9.     all_hidden.append(h.float())
10.    all_labels.extend(e["label"] for e in batch)
11. extractor.remove()
12. return torch.cat(all_hidden, dim=0), torch.tensor(all_labels)
```

### Error Handling

- `HiddenStateExtractor.__init__`: raise `IndexError` with clear message if `target_layer >= len(model.model.layers)`.
- `get_last_hidden`: raise `RuntimeError("No forward pass captured")` if called before any hook trigger.
- `extract_hidden_states`: always call `extractor.remove()` in `finally` block to avoid leaking hooks on exception.
- Use `tokenizer.padding_side = "left"` (mandatory) — right-padding would make `output[0][:, -1, :]` capture pad-token state, corrupting the signal.

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | HiddenStateExtractor class | Hook registration, capture, remove |
| L-2-2 | Model/tokenizer loading | bfloat16, device_map="auto", left-padding config |
| L-2-3 | extract_hidden_states batching | Chunked forward passes, hidden state accumulation to CPU |
| L-2-4 | Persistence | Save (hidden_states, labels) tensors to disk (torch.save) to avoid re-extraction |

---

## A-3: Linear Probe + Training [Complexity: 7, Budget: 7]

**Applied**: sigmoid(w^T h + b) probe, BCE + Adam (venator/aragorn-w pattern)

### API Signatures

```python
class LinearProbe(nn.Module):
    def __init__(self, hidden_dim: int = 4096):
        """Single linear layer -> sigmoid."""
        ...

    def forward(self, hidden_states: Tensor) -> Tensor:
        """[N, 4096] -> [N, 1] sigmoid probabilities."""
        ...


def train_probe(
    hidden_states: Tensor, labels: Tensor, cfg: Config
) -> tuple[LinearProbe, list[float]]:
    """Full-batch Adam/BCE training loop.
    Returns (trained probe, loss_per_epoch)."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| hidden_states | [N, 4096] | train split |
| labels | [N] | float for BCE target |
| preds | [N, 1] -> squeeze [N] | sigmoid output |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | LinearProbe module | `nn.Linear(hidden_dim, 1)` + sigmoid forward |
| L-3-2 | Adam/BCE setup | `torch.optim.Adam(lr=cfg.lr)`, `nn.BCELoss()` |
| L-3-3 | Training loop | Mini-batch (batch_size=256) over 10 epochs, shuffle each epoch |
| L-3-4 | Loss tracking | Append mean epoch loss to `loss_per_epoch` list |

---

## A-4: Evaluation + Gate Check [Complexity: 5, Budget: 5]

**Applied**: sklearn roc_auc_score standard usage

### API Signatures

```python
def evaluate_auroc(probe: LinearProbe, hidden_states: Tensor, labels: Tensor) -> float:
    """No-grad forward on val hidden_states, returns roc_auc_score(labels, preds)."""
    ...
```

### Pseudo-code

```
1. probe.eval()
2. with torch.no_grad(): preds = probe(hidden_states).squeeze().numpy()
3. auroc = roc_auc_score(labels.numpy(), preds)
4. gate_pass = auroc > cfg.auroc_gate  # 0.60
5. return auroc
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | evaluate_auroc | Val-set forward pass + sklearn AUROC |
| L-4-2 | Gate comparison | Compare against `cfg.auroc_gate` (0.60) and baseline (0.50), log PASS/FAIL |
| L-4-3 | main() orchestration | Load saved hidden states, run eval, print gate decision |

---

## A-5: Visualization [Complexity: 6, Budget: 6]

**Applied**: matplotlib + sklearn.roc_curve standard plotting

### API Signatures

```python
def plot_gate_comparison(auroc: float, baseline: float, out_path: str) -> None: ...
def plot_roc_curve(labels: Tensor, preds: Tensor, auroc: float, out_path: str) -> None: ...
def plot_loss_curve(losses: list[float], out_path: str) -> None: ...
def plot_hidden_state_pca(hidden_states: Tensor, labels: Tensor, out_path: str) -> None: ...
```

### Pseudo-code (plot_hidden_state_pca)

```
1. pca = sklearn.decomposition.PCA(n_components=2)
2. coords = pca.fit_transform(hidden_states.numpy())  # [N, 2]
3. scatter(coords[:,0], coords[:,1], c=labels, cmap="coolwarm")
4. savefig(out_path)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | plot_gate_comparison | Bar chart: probe AUROC vs 0.50 baseline |
| L-5-2 | plot_roc_curve | `sklearn.metrics.roc_curve` + AUROC annotation |
| L-5-3 | plot_loss_curve | Loss vs epoch line plot |
| L-5-4 | plot_hidden_state_pca | PCA-2D scatter colored by label, all saved to `figures/` |
