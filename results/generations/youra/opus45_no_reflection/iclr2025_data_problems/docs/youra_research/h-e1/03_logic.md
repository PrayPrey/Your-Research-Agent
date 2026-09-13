# Logic: H-E1 (EXISTENCE PoC)

**Applied:** unified-attribution-API-pattern (single dispatch fn over TRAK/EK-FAC/TracIn)

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - no existing code to analyze, designing new APIs
**Analyzed Path:** N/A
**Relevant Symbols:** None - new implementation

---

## A-1: Data pipeline [Complexity: 6]

```python
def load_sst2() -> DatasetDict: ...

def inject_label_noise(
    dataset: Dataset, rate: float = 0.05, seed: int = 42
) -> tuple[Dataset, set[int]]:
    """Flip `rate` fraction of labels. Returns (noisy_dataset, mislabeled_indices)."""
    ...

def tokenize_dataset(
    dataset: Dataset, tokenizer: PreTrainedTokenizer, max_length: int = 128
) -> Dataset:
    """Adds input_ids [N, L], attention_mask [N, L]."""
    ...

def get_loaders(
    train_ds: Dataset, val_ds: Dataset, batch_size: int = 32
) -> tuple[DataLoader, DataLoader]: ...
```

---

## A-2: Model builders [Complexity: 4]

```python
def build_bert(num_labels: int = 2) -> tuple[PreTrainedModel, PreTrainedTokenizer]:
    """AutoModelForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=num_labels)."""
    ...

def build_gpt2(num_labels: int = 2) -> tuple[PreTrainedModel, PreTrainedTokenizer]:
    """GPT2ForSequenceClassification; sets tokenizer.pad_token = tokenizer.eos_token,
    model.config.pad_token_id = tokenizer.eos_token_id."""
    ...
```

---

## A-3: Training loop [Complexity: 9, Budget: 2 subtasks]

**Applied:** standard HF fine-tuning loop (AdamW + linear schedule), per-seed checkpointing

### API Signatures

```python
def train_model(
    model: PreTrainedModel,
    train_loader: DataLoader,
    seed: int,
    epochs: int = 3,
    lr: float = 2e-5,
    device: str = "cuda",
) -> PreTrainedModel:
    """Fine-tunes in place with AdamW. Sets torch/numpy/random seed before init."""
    ...

def run_all_seeds(
    model_name: str,          # "bert" | "gpt2"
    train_loader: DataLoader,
    seeds: list[int] = [42, 43, 44, 45, 46],
    ckpt_dir: str = "checkpoints",
) -> dict[int, PreTrainedModel]:
    """Loops train_model per seed, saves checkpoints/{model_name}_seed{seed}.pt."""
    ...
```

### Pseudo-code

```
run_all_seeds(model_name, train_loader, seeds):
  models = {}
  for seed in seeds:
    set_seed(seed)
    model, _ = build_bert() if model_name == "bert" else build_gpt2()
    model = train_model(model, train_loader, seed, epochs=3, lr=2e-5)
    torch.save(model.state_dict(), f"{ckpt_dir}/{model_name}_seed{seed}.pt")
    models[seed] = model
  return models

train_model(model, train_loader, seed, epochs, lr):
  set_seed(seed)
  optimizer = AdamW(model.parameters(), lr=lr)
  scheduler = get_linear_schedule_with_warmup(optimizer, 0, epochs * len(train_loader))
  for epoch in range(epochs):
    for batch in train_loader:                     # input_ids [B, L], labels [B]
      logits = model(**batch).logits                # [B, 2]
      loss = cross_entropy(logits, batch["labels"])
      loss.backward(); optimizer.step(); scheduler.step(); optimizer.zero_grad()
  return model
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, L] | L=128 |
| logits | [B, 2] | binary sentiment |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | `train_model` | Single-seed fine-tune loop (AdamW, linear schedule, 3 epochs) |
| L-3-2 | `run_all_seeds` | Seed loop wrapper + checkpoint I/O for one architecture |

---

## A-4: TRAK integration [Complexity: 8]

```python
def compute_trak_scores(
    model: PreTrainedModel, train_loader: DataLoader, train_size: int
) -> np.ndarray:
    """traker.TRAKer(model=model, task='text_classification', train_set_size=train_size).
    Featurize all train batches, finalize_features(), score self vs train -> diagonal.
    Returns self_influence [N]."""
    ...
```

---

## A-5: EK-FAC integration [Complexity: 8]

```python
def compute_ekfac_scores(model: PreTrainedModel, train_loader: DataLoader) -> np.ndarray:
    """kronfluence.Analyzer: fit_covariance_matrices -> fit_lambda_matrices (EK-FAC factors)
    -> compute_self_scores. Returns self_influence [N]."""
    ...
```

---

## A-6: TracIn integration [Complexity: 6]

```python
def compute_tracin_scores(
    model: PreTrainedModel, train_loader: DataLoader, checkpoint: dict
) -> np.ndarray:
    """captum.influence.TracInCPFast(model, final_fc_layer=model.classifier,
    checkpoints=[checkpoint], loss_fn=cross_entropy).
    self_influence(train_loader) -> [N]."""
    ...
```

### Dispatch (A-4/5/6 shared entry)

```python
def compute_attribution(
    model: PreTrainedModel, train_loader: DataLoader, method: str, **kwargs
) -> np.ndarray:
    """method in {'trak','ekfac','tracin'}; dispatches to compute_*_scores. Returns [N]."""
    ...
```

---

## A-7: Evaluation + stats [Complexity: 7]

```python
def mislabeled_auc(scores: np.ndarray, mislabeled_indices: set[int]) -> float:
    """roc_auc_score(y_true=[i in mislabeled_indices for i in range(N)], y_score=scores)."""
    ...

def paired_ttest(bert_aucs: list[float], gpt2_aucs: list[float]) -> tuple[float, float]:
    """scipy.stats.ttest_rel(bert_aucs, gpt2_aucs) -> (t_stat, p_value)."""
    ...

def cohens_d(x: list[float], y: list[float]) -> float:
    """(mean(x) - mean(y)) / pooled_std(x, y)."""
    ...

def run_gate_check(results: dict) -> dict:
    """Per method: PASS if |auc_diff| > 0.05 and p < 0.05 and |d| > 0.3.
    Returns {method: {'pass': bool, 'auc_diff': float, 'p': float, 'd': float}}."""
    ...
```

---

## A-8: Visualization + orchestration [Complexity: 6]

```python
def plot_auc_comparison(results: dict, out_path: str) -> None: ...
def plot_method_arch_heatmap(results: dict, out_path: str) -> None: ...
def plot_diff_significance(results: dict, stats: dict, out_path: str) -> None: ...

def run_experiment() -> None:
    """data -> {train_model,run_all_seeds}x2 arch -> compute_attribution x3 methods
    -> mislabeled_auc -> paired_ttest/cohens_d -> run_gate_check -> plots -> results.json."""
    ...
```
