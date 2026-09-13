# Logic: H-M2 (Layer-wise Probe Sweep)

Applied: sonde LayerProbeSweepRunner pattern (val-based layer selection, per-layer independent probes)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1, H-E1)
**Status**: Serena has no active project registered for this workspace; used direct `Read`/`Glob` on actual code files instead (same fallback as architecture doc).
**Analyzed Path**: `docs/youra_research/h-m1/code/hooks.py`, `docs/youra_research/h-e1/code/{model,data,evaluate}.py`
**Relevant Symbols (verified from actual code)**:
- `h-m1/code/hooks.py::HiddenStateExtractor.__init__(self, model, layer_indices: list = None)` — already multi-layer, context-managed (`__enter__`/`__exit__`), `self.hidden_states: dict[int, Tensor]` holds `(B, seq, 4096)` per layer. **Reused verbatim.**
- `h-e1/code/model.py::LinearProbe.__init__(self, hidden_dim: int = 4096)`, `forward(self, hidden_states)` — reused verbatim.
- `h-e1/code/model.py::train_probe(hidden_states, labels, cfg)` uses `torch.optim.Adam(probe.parameters(), lr=cfg.lr)` — **H-M2 must switch to `AdamW` with `weight_decay=cfg.weight_decay` per PRD FR-2**; loop structure otherwise reused.
- `h-e1/code/evaluate.py::evaluate_auroc(probe, hidden_states, labels) -> (auroc, preds, labels_np)` — reused verbatim, exact 3-tuple return.
- `h-e1/code/data.py::load_triviaqa(split, n)`, `format_prompt(example)`, `label_correctness(pred_answer, gold_aliases)`, `build_labeled_dataset_batched(model, tokenizer, dataset, n, batch_size=8, max_new_tokens=32)` — reused verbatim (note default `batch_size=8`, `max_new_tokens=32`).

---

## External Dependencies (Base Hypothesis)

```python
# From: h-m1/code/hooks.py (ACTUAL CODE — use this signature, not architecture doc paraphrase)
class HiddenStateExtractor:
    def __init__(self, model, layer_indices: list = None): ...
    def __enter__(self) -> "HiddenStateExtractor": ...
    def __exit__(self, *exc) -> None: ...
    hidden_states: dict[int, torch.Tensor]  # {layer_idx: (B, seq, 4096)}, cleared on __enter__

# From: h-e1/code/model.py (ACTUAL CODE)
class LinearProbe(nn.Module):
    def __init__(self, hidden_dim: int = 4096): ...
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor: ...  # sigmoid(logits), (N,1)

# From: h-e1/code/evaluate.py (ACTUAL CODE)
def evaluate_auroc(probe, hidden_states: torch.Tensor, labels: torch.Tensor) -> tuple:
    ...  # returns (auroc: float, preds: np.ndarray, labels_np: np.ndarray)

# From: h-e1/code/data.py (ACTUAL CODE)
def load_triviaqa(split: str, n: int): ...  # "train" or else -> validation
def format_prompt(example: dict) -> str: ...
def label_correctness(pred_answer: str, gold_aliases: list) -> int: ...
def build_labeled_dataset_batched(model, tokenizer, dataset, n: int, batch_size: int = 8, max_new_tokens: int = 32) -> list: ...
    # returns list[{"prompt": str, "label": int, "answer": str}]
```

**Note**: H-M2's own `extract_all_layers` does NOT call `h-e1/code/model.py::extract_hidden_states` (single-layer, incompatible) — it is new code built on `HiddenStateExtractor` (multi-layer) directly.

---

## A-1: Multi-Layer Extraction Pipeline [Complexity: 10, Budget: 10] (S-4)

**Applied**: sonde batched extraction + H-M1 context-managed hook pattern

### API Signatures

```python
def extract_all_layers(
    model,
    tokenizer,
    layer_indices: list[int],
    examples: list[dict],          # [{"prompt": str, "label": int, "answer": str}, ...]
    batch_size: int = 32,
) -> tuple[dict[int, torch.Tensor], torch.Tensor]:
    """Forward-pass batches through model w/ HiddenStateExtractor; collect last-token state per layer."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| enc.input_ids | [B, L] | left-padded |
| extractor.hidden_states[idx] | [B, L, 4096] | per layer, raw hook output |
| last_token[idx] | [B, 4096] | selected via `[:, -1, :]` (left-padding safe) |
| train_states[idx] | [N_train, 4096] | after `torch.cat` over batches |
| labels | [N] | int64, 0/1 |

### Pseudo-code

```
1. tokenizer.padding_side = "left"; set pad_token if missing
2. layer_buffers = {idx: [] for idx in layer_indices}; all_labels = []
3. with HiddenStateExtractor(model, layer_indices) as extractor:
     for batch in chunks(examples, batch_size):
       enc = tokenizer([e["prompt"] for e in batch], padding=True, truncation=True, max_length=512, return_tensors="pt").to(model.device)
       with torch.no_grad(): model(**enc)
       for idx in layer_indices:
         h = extractor.hidden_states[idx][:, -1, :].float()   # [B, 4096], left-pad -> last col is real last token
         layer_buffers[idx].append(h)
       all_labels.extend(e["label"] for e in batch)
4. states = {idx: torch.cat(layer_buffers[idx], dim=0) for idx in layer_indices}
5. return states, torch.tensor(all_labels, dtype=torch.long)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | Tokenizer setup | left-padding, pad_token fallback |
| L-4-2 | Extractor wiring | instantiate `HiddenStateExtractor(model, layer_indices)` as context manager |
| L-4-3 | Batched forward + per-layer collect | loop batches, index `[:, -1, :]`, append to per-layer lists |
| L-4-4 | Concat + label tensor | `torch.cat` per layer, build label tensor |

---

## A-2: Per-Layer Probe Training Loop [Complexity: 9, Budget: 9] (S-5)

**Applied**: H-E1 `train_probe` loop adapted to AdamW + per-layer iteration

### API Signatures

```python
def train_probe(
    hidden_states: torch.Tensor,   # [N, 4096]
    labels: torch.Tensor,          # [N]
    cfg,                            # cfg.lr, cfg.weight_decay, cfg.epochs, cfg.batch_size
) -> tuple[LinearProbe, list[float]]:
    """AdamW-trained per-layer probe. Returns (probe.cpu(), loss_per_epoch)."""
    ...

def run_layer_sweep(
    train_states: dict[int, torch.Tensor],
    train_labels: torch.Tensor,
    val_states: dict[int, torch.Tensor],
    val_labels: torch.Tensor,
    cfg,
) -> dict[int, dict]:
    """Train+eval one LinearProbe per layer. Returns {layer_idx: {"auroc", "probe", "losses", "preds", "labels_np"}}."""
    ...
```

### Pseudo-code (train_probe — differs from H-E1 base: AdamW not Adam)

```
1. probe = LinearProbe(hidden_dim=hidden_states.shape[1]).to(device)
2. optimizer = torch.optim.AdamW(probe.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)
3. criterion = nn.BCELoss()
4. for epoch in range(cfg.epochs):
     shuffle indices; for each batch: zero_grad -> probe(x).squeeze() -> BCE -> backward -> step
     record avg epoch loss
5. return probe.cpu(), loss_per_epoch
```

### Pseudo-code (run_layer_sweep)

```
1. results = {}
2. for idx in layer_indices:
     probe, losses = train_probe(train_states[idx], train_labels, cfg)
     auroc, preds, labels_np = evaluate_auroc(probe, val_states[idx], val_labels)
     results[idx] = {"auroc": auroc, "probe": probe, "losses": losses, "preds": preds, "labels_np": labels_np}
3. return results
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | train_probe AdamW adaptation | swap Adam->AdamW, add weight_decay |
| L-5-2 | Batched epoch loop | reuse H-E1 shuffling/batching logic verbatim |
| L-5-3 | run_layer_sweep loop | iterate 8 layers, call train_probe + evaluate_auroc |
| L-5-4 | Result dict assembly | pack per-layer auroc/probe/losses/preds |

---

## A-3: Bootstrap AUROC CI [Complexity: 8 subset, Budget: shared w/ S-6] (S-6)

**Applied**: Standard percentile bootstrap (numpy)

### API Signatures

```python
def bootstrap_auroc_ci(
    labels: np.ndarray,     # [N]
    preds: np.ndarray,      # [N]
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> tuple[float, float]:
    """Percentile bootstrap 95% CI on AUROC. Returns (ci_low, ci_high)."""
    ...
```

### Pseudo-code

```
1. rng = np.random.default_rng(seed)
2. n = len(labels); scores = []
3. for _ in range(n_bootstrap):
     idx = rng.integers(0, n, size=n)
     if len(np.unique(labels[idx])) < 2: continue  # skip degenerate resample
     scores.append(roc_auc_score(labels[idx], preds[idx]))
4. return np.percentile(scores, 2.5), np.percentile(scores, 97.5)
```

---

## A-4: Inverted-U Gate Verification [Complexity: 6, Budget: 6] (S-7)

**Applied**: Direct port of PRD reference `verify_inverted_u_pattern`

### API Signatures

```python
def verify_inverted_u_pattern(
    layer_aurocs: dict[int, float],   # {layer_idx: auroc}, 8 entries
    num_layers: int = 32,
) -> dict:
    """Gate check: layers[1]=early(~25%), layers[4]=middle(~60%), layers[-1]=final(100%)."""
    ...
```

### Pseudo-code (verbatim from experiment brief — sorted-key indexing depends on exact 8-layer ordering)

```
1. layers = sorted(layer_aurocs.keys())     # e.g. [3,7,11,15,18,23,27,31]
2. early, middle, final = layers[1], layers[4], layers[-1]   # 25%, 60%, 100%
3. auroc_early, auroc_middle, auroc_final = layer_aurocs[early], layer_aurocs[middle], layer_aurocs[final]
4. middle_beats_final = auroc_middle > auroc_final
5. middle_beats_early = auroc_middle > auroc_early
6. peak_layer = argmax(layer_aurocs); peak_depth_pct = (peak_layer+1)/num_layers * 100
7. return {middle_beats_final, middle_beats_early, peak_layer, peak_depth_pct,
           inverted_u_detected: middle_beats_final and middle_beats_early,
           gate_satisfied: middle_beats_final}
```

**Caution**: `layers[1]` and `layers[4]` assume the 8-index layer list is sorted ascending and matches PRD depths `[0.125,0.25,0.375,0.5,0.6,0.75,0.875,1.0]` exactly — do not reorder `layer_depths` in config.

---

## Supporting Signatures (low complexity, reused/simple — no dedicated subtask budget)

```python
def get_layer_indices(num_layers: int, depths: list[float]) -> list[int]:
    return [max(0, int(d * num_layers) - 1) for d in depths]

def set_seed(seed: int = 42) -> None: ...

def load_triviaqa_splits(n_train: int, n_val: int) -> tuple["Dataset", "Dataset"]:
    # train = load_triviaqa("train", n_train); val = load_triviaqa("validation", n_val)
    ...

def build_labeled_dataset(model, tokenizer, dataset, n: int, batch_size: int) -> list[dict]:
    # thin wrapper around build_labeled_dataset_batched (H-E1, verbatim)
    ...

def plot_gate_comparison(layer_aurocs: dict, cfg) -> None: ...   # bar: L25/L60/L100
def plot_layer_auroc_curve(layer_aurocs: dict, cis: dict, cfg) -> None: ...  # line + error bars
def plot_inverted_u(layer_aurocs: dict, cfg) -> None: ...  # np.polyfit deg=2 over depth% vs auroc
```
