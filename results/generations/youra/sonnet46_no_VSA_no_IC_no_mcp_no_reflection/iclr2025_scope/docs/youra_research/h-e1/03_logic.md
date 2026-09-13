---
title: "Logic: h-e1 — Mamba-130m LoRA GLUE Fine-tuning"
hypothesis_id: h-e1
type: EXISTENCE
date: "2026-08-31"
author: yoon303@ust.ac.kr
---

Applied: MambaPEFT projection-layer LoRA pattern (in_proj/out_proj/x_proj, conv1d exclusion, last-token pooling)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field — no existing codebase to analyze.
**Analyzed Path**: N/A
**Relevant Symbols**: None — new implementation

---

## E2-1: MambaForSequenceClassification.__init__ [Complexity: 4, Budget: 1]

### API Signatures

```python
class MambaForSequenceClassification(nn.Module):
    def __init__(
        self,
        cfg: ExperimentConfig,
        num_labels: int,
        backbone: nn.Module = None,  # pre-built (possibly PEFT-wrapped) backbone
    ) -> None:
        """Init classifier with backbone + linear head."""
        # backbone: AutoModelForCausalLM or get_peft_model result
        # classifier: nn.Linear(768, num_labels)
        # device: inferred from backbone parameters
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, L] | B=batch, L=seq_len (≤128) |
| hidden_states[-1] | [B, L, 768] | last layer, d_model=768 |
| pooled | [B, 768] | last-token: hidden[:, -1, :] |
| logits | [B, num_labels] | classifier output |

### Pseudo-code

```
1. self.backbone = backbone  # passed in (LoRA-wrapped or plain)
2. self.classifier = nn.Linear(768, num_labels)
3. self.num_labels = num_labels
4. nn.init.normal_(self.classifier.weight, std=0.02)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E2-1 | init | Backbone + classifier init, weight init |

---

## E2-2: MambaForSequenceClassification.forward [Complexity: 4, Budget: 1]

### API Signatures

```python
def forward(
    self,
    input_ids: torch.Tensor,          # [B, L]
    labels: Optional[torch.Tensor] = None,  # [B] long
    output_hidden_states: bool = True, # MUST be True for pooling
) -> dict:
    """Forward pass. Returns dict with 'logits' and optionally 'loss'."""
    # Returns: {"logits": Tensor[B, num_labels], "loss": Tensor scalar (if labels)}
```

### Pseudo-code

```
1. out = self.backbone(input_ids, output_hidden_states=True)
2. hidden = out.hidden_states[-1]          # [B, L, 768]
3. pooled = hidden[:, -1, :]              # [B, 768] last-token
4. logits = self.classifier(pooled)       # [B, num_labels]
5. if labels: loss = F.cross_entropy(logits, labels)
6. return {"logits": logits, "loss": loss} (loss omitted if no labels)
```

### Invariants

- `output_hidden_states=True` is mandatory; assert it or hardcode inside forward.
- `hidden_states[-1]` is the final SSM layer output.

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E2-2 | forward | Last-token pool, CE loss branch, return dict |

---

## E2-3: build_lora_model + build_zero_shot_model [Complexity: 4, Budget: 1]

### API Signatures

```python
def build_lora_model(
    cfg: ExperimentConfig,
    num_labels: int,
) -> MambaForSequenceClassification:
    """Load backbone, apply LoRA, wrap in classifier."""

def build_zero_shot_model(
    cfg: ExperimentConfig,
    num_labels: int,
) -> MambaForSequenceClassification:
    """Load backbone, freeze all params, wrap in classifier (no LoRA)."""
```

### Pseudo-code (build_lora_model)

```
1. assert "conv1d" not in cfg.target_modules, "conv1d breaks PEFT — remove it"
2. base = AutoModelForCausalLM.from_pretrained(cfg.model_name)
3. lora_cfg = LoraConfig(r=cfg.lora_r, lora_alpha=cfg.lora_alpha,
       lora_dropout=cfg.lora_dropout, target_modules=list(cfg.target_modules),
       bias="none", task_type="FEATURE_EXTRACTION")
4. peft_model = get_peft_model(base, lora_cfg)
5. peft_model.print_trainable_parameters()
6. return MambaForSequenceClassification(cfg, num_labels, backbone=peft_model)
```

### Pseudo-code (build_zero_shot_model)

```
1. base = AutoModelForCausalLM.from_pretrained(cfg.model_name)
2. for p in base.parameters(): p.requires_grad = False
3. return MambaForSequenceClassification(cfg, num_labels, backbone=base)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E2-3 | builders | LoRA + zero-shot factory functions |

---

## E4-1: get_dataloaders [Complexity: 4, Budget: 1]

### API Signatures

```python
TASK_TEXT_FIELDS: dict[str, tuple[str, ...]] = {
    "sst2": ("sentence",),
    "mnli": ("premise", "hypothesis"),
    "qnli": ("question", "sentence"),
    "qqp":  ("question1", "question2"),
}

def get_dataloaders(
    task: str,
    tokenizer,
    cfg: ExperimentConfig,
) -> tuple[DataLoader, DataLoader]:
    """Tokenize GLUE task, return (train_loader, val_loader)."""
```

### Pseudo-code

```
1. ds = load_dataset("glue", task)
2. fields = TASK_TEXT_FIELDS[task]
3. def tokenize(batch):
       if len(fields) == 1: text = batch[fields[0]]
       else: text, text_pair = batch[fields[0]], batch[fields[1]]
       return tokenizer(text, text_pair, max_length=cfg.max_length,
                        truncation=True, padding="max_length")
4. ds = ds.map(tokenize, batched=True, remove_columns=ds["train"].column_names - {"label"})
5. ds.set_format("torch", columns=["input_ids", "attention_mask", "label"])
6. val_split = "validation_matched" if task == "mnli" else "validation"
7. return DataLoader(ds["train"], batch_size=cfg.batch_size, shuffle=True),
           DataLoader(ds[val_split], batch_size=cfg.batch_size)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E4-1 | dataloaders | Multi-field tokenization, DataLoader construction |

---

## E4-2: train_one_task [Complexity: 5, Budget: 1]

### API Signatures

```python
def train_one_task(
    task: str,
    cfg: ExperimentConfig,
) -> tuple[MambaForSequenceClassification, dict, list[float]]:
    """Train LoRA model on one GLUE task. Returns (model, val_metrics, loss_history)."""
```

### Pseudo-code

```
1.  set_seed(cfg.seed)
2.  device = "cuda" if torch.cuda.is_available() else "cpu"
3.  tokenizer = AutoTokenizer.from_pretrained(cfg.model_name)
4.  model = build_lora_model(cfg, TASK_LABEL_COUNTS[task]).to(device)
5.  train_loader, val_loader = get_dataloaders(task, tokenizer, cfg)
6.  optimizer = AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)
7.  total_steps = len(train_loader) * cfg.epochs
8.  warmup_steps = int(total_steps * cfg.warmup_ratio)
9.  scheduler = get_linear_schedule_with_warmup(optimizer, warmup_steps, total_steps)
10. loss_history = []
11. for epoch in range(cfg.epochs):
12.     model.train()
13.     for batch in train_loader:
14.         input_ids, labels = batch["input_ids"].to(device), batch["label"].to(device)
15.         out = model(input_ids, labels=labels)
16.         out["loss"].backward()
17.         optimizer.step(); scheduler.step(); optimizer.zero_grad()
18.         loss_history.append(out["loss"].item())
19.     val_metrics = eval_model(model, val_loader, task, device)
20. return model, val_metrics, loss_history
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E4-2 | training loop | AdamW + warmup schedule, 3-epoch loop, per-epoch eval |

---

## E4-3: eval_model [Complexity: 3, Budget: 1]

### API Signatures

```python
def eval_model(
    model: MambaForSequenceClassification,
    val_loader: DataLoader,
    task: str,
    device: str,
) -> dict:
    """Run inference on val_loader, compute GLUE metric. Returns {task: score}."""
```

### Pseudo-code

```
1. model.eval()
2. all_preds, all_labels = [], []
3. with torch.no_grad():
4.     for batch in val_loader:
5.         logits = model(batch["input_ids"].to(device))["logits"]  # [B, C]
6.         preds = logits.argmax(dim=-1).cpu().tolist()
7.         all_preds.extend(preds); all_labels.extend(batch["label"].tolist())
8. return compute_glue_metric(task, all_preds, all_labels)
```

### Invariants

- Returns `{task: float}` e.g. `{"sst2": 0.923}` or `{"qqp": {"f1": 0.88, "accuracy": 0.86}}`.
- Caller (gate logic) reads `result[task]` → normalize QQP to F1 at call site.

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E4-3 | eval loop | Inference, argmax, metric delegation |
