# Logic: H-M2 — Projection-Only LoRA Eigenvalue Preservation

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending H-M1)
**Status**: API signatures verified from actual code (filesystem read)
**Analyzed Path**: `docs/youra_research/20260327_scope/h-m1/code/model.py`
**Relevant Symbols**:
- `MambaProbe.__init__(self, config: ExperimentConfig)`
- `MambaProbe.load_model(self, model_id: str)` — param is `model_id`, appends `-hf` internally
- `MambaProbe.extract_layer_A_log(self)` → `List[Tensor]` each `[d_inner, d_state]`
- `MambaProbe.compute_h_spec(self, input_ids=None)` → `float` using `1/min(exp(A_log))`
- `MambaProbe.get_per_layer_h_spec(self)` → `List[float]`
- `MambaProbe.get_per_layer_lambda_max(self)` → `List[float]`
- `MambaProbe.unload(self)`
- **CRITICAL**: H-M1 has NO `get_model()` / `get_tokenizer()` — H-M2 must add these
- H_spec formula is `1/min(exp(A_log))` NOT `-1/log(lambda_max)` — H-M2 must use same formula

---

## External Dependencies API

### Verified from H-M1 Actual Code

```python
# From: docs/youra_research/20260327_scope/h-m1/code/model.py (ACTUAL CODE)

class MambaProbe:
    def __init__(self, config: ExperimentConfig) -> None: ...

    def load_model(self, model_id: str) -> None:
        # model_id e.g. "state-spaces/mamba-1.4b" -> loads f"{model_id}-hf"
        # Sets self.model (AutoModelForCausalLM) and self.tokenizer
        ...

    def extract_layer_A_log(self) -> List[Tensor]:
        # List[num_layers=48], each Tensor[d_inner, d_state] float32
        ...

    def compute_h_spec(self, input_ids: Optional[Tensor] = None) -> float:
        # H_spec = 1.0 / min(exp(A_log))
        ...

    def get_per_layer_h_spec(self) -> List[float]: ...
    def get_per_layer_lambda_max(self) -> List[float]: ...
    def unload(self) -> None: ...
    # get_model() and get_tokenizer() DO NOT EXIST — H-M2 adds them
```

---

## A-2: Port MambaProbe from H-M1 [Complexity: 7]

Applied: Standard PyTorch

### API Signatures

```python
class MambaProbe:
    """Eigenvalue extraction from Mamba-1.4B. Ported from H-M1 + added accessors."""

    def __init__(self, config: ExperimentConfig) -> None: ...

    def load_model(self, model_id: str) -> None:
        # model_id: "state-spaces/mamba-1.4b" (appends "-hf" internally)
        ...

    def extract_layer_A_log(self) -> List[Tensor]:
        # Returns List[Tensor[d_inner, d_state]], len=48
        ...

    def compute_h_spec(self, input_ids: Optional[Tensor] = None) -> float:
        # H_spec = 1.0 / min(exp(A_log)) — identical to H-M1
        ...

    def get_per_layer_h_spec(self) -> List[float]: ...
    def get_per_layer_lambda_max(self) -> List[float]: ...

    def get_model(self):
        """Return self.model (AutoModelForCausalLM) for LoRA wrapping."""
        ...

    def get_tokenizer(self):
        """Return self.tokenizer."""
        ...

    def unload(self) -> None: ...
```

---

## A-3: LoRAAdapter [Complexity: 10, Budget: 2 subtasks]

Applied: PEFT frozen-weights LoraConfig pattern

### API Signatures

```python
class LoRAAdapter:
    """Wraps base model with projection-only LoRA via PEFT."""

    def __init__(self, model, config: ExperimentConfig) -> None:
        # model: raw AutoModelForCausalLM from MambaProbe.get_model()
        ...

    def apply(self) -> any:
        """Apply LoraConfig to in_proj/out_proj; return PEFT model.

        r=config.lora_r, lora_alpha=config.lora_alpha,
        target_modules=list(config.lora_target_modules), bias="none"
        Stores result as self.peft_model.
        """
        ...

    def verify_mechanism(self) -> bool:
        """Assert A_log NOT in trainable params; assert proj+lora ARE.

        Raises AssertionError on failure. Returns True on success.
        """
        ...

    def get_trainable_param_count(self) -> int:
        """Count of parameters with requires_grad=True."""
        ...
```

### Pseudo-code

```
apply():
    cfg = LoraConfig(r, lora_alpha, target_modules, lora_dropout, bias="none")
    self.peft_model = get_peft_model(self.model, cfg)
    return self.peft_model

verify_mechanism():
    trainable = [n for n,p in peft_model.named_parameters() if p.requires_grad]
    assert not any('A_log' in n for n in trainable)
    assert any('proj' in n and 'lora' in n for n in trainable)
    return True
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | apply() | Build LoraConfig, call get_peft_model(), store peft_model |
| L-3-2 | verify_mechanism() | Two assertions: A_log frozen, proj+lora trainable |

---

## A-5: Training Loop [Complexity: 11, Budget: 2 subtasks]

Applied: Standard PyTorch AdamW + cosine scheduler

### API Signatures

```python
# train.py

def load_wikitext103_train(config: ExperimentConfig) -> any:
    """Load + tokenize WikiText-103 train split; chunk to max_seq_length.
    Returns HuggingFace Dataset with 'input_ids' column.
    """
    ...

def build_dataloader(tokenized_dataset, config: ExperimentConfig) -> DataLoader:
    """DataLoader: batch={'input_ids': Tensor[B, L]}, shuffle=True."""
    ...

def build_optimizer_and_scheduler(
    model,
    config: ExperimentConfig,
    num_training_steps: int,
) -> Tuple[AdamW, LambdaLR]:
    """AdamW(lr=config.learning_rate, weight_decay=config.weight_decay)
    + cosine schedule with warmup_steps=config.warmup_steps.
    """
    ...

def train(
    model,
    dataloader: DataLoader,
    optimizer: AdamW,
    scheduler,
    config: ExperimentConfig,
) -> List[float]:
    """Run training; return per-step loss list.
    Uses config.num_epochs, config.gradient_accumulation_steps.
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, L] | B=batch_size=8, L=1024 |
| logits | [B, L, V] | V=vocab_size |
| shift_logits | [B, L-1, V] | next-token CE input |
| shift_labels | [B, L-1] | input_ids[:, 1:] |

### Pseudo-code (train)

```
losses = []
for epoch in range(num_epochs):
    for step, batch in enumerate(dataloader):
        input_ids = batch["input_ids"]  # [B, L]
        outputs = model(input_ids, labels=input_ids)
        loss = outputs.loss / gradient_accumulation_steps
        loss.backward()
        losses.append(loss.item() * gradient_accumulation_steps)
        if (step+1) % gradient_accumulation_steps == 0:
            optimizer.step(); scheduler.step(); optimizer.zero_grad()
return losses
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | data pipeline | load_wikitext103_train + build_dataloader with chunking |
| L-5-2 | train() loop | gradient accumulation, loss recording, scheduler step |

---

## A-6: EigenvaluePreservationValidator [Complexity: 10, Budget: 2 subtasks]

Applied: Standard PyTorch + scipy.stats.pearsonr

### API Signatures

```python
class EigenvaluePreservationValidator:
    """Compare pre/post A_log tensors; compute preservation metrics."""

    def __init__(
        self,
        baseline_a_logs: List[Tensor],   # List[Tensor[d_inner, d_state]], len=48
        post_a_logs: List[Tensor],        # List[Tensor[d_inner, d_state]], len=48
        config: ExperimentConfig,
    ) -> None: ...

    def compute_delta_h_spec(self) -> float:
        """Return |ΔH_spec| as percentage.
        H_spec = 1/min(exp(A_log)) — same formula as H-M1.
        delta = |post - baseline| / baseline * 100
        """
        ...

    def compute_eigenvalue_correlation(self) -> float:
        """Pearson r between flattened pre/post discrete eigenvalues.
        eigenvalue = exp(-exp(A_log)) per element; cat all layers.
        """
        ...

    def compute_a_log_max_diff(self) -> float:
        """max|A_log_post - A_log_pre| across all layers. Expected ~0.0."""
        ...

    def validate(self) -> dict:
        """Return full metrics dict with hypothesis_pass bool.

        Keys: baseline_h_spec, post_h_spec, delta_h_spec_percent,
              eigenvalue_correlation, a_log_max_diff, hypothesis_pass
        hypothesis_pass = delta_h_spec_percent < config.delta_h_spec_threshold
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| baseline_a_logs[i] | [d_inner, d_state] = [4096, 16] | per layer |
| eigenvalues_flat | [48 * 4096 * 16] | concatenated for pearsonr |

### Pseudo-code

```
_h_spec(a_logs):
    all_a = cat([a.float().flatten() for a in a_logs])
    return 1.0 / exp(all_a.min().item())

compute_delta_h_spec():
    return abs(_h_spec(post) - _h_spec(baseline)) / _h_spec(baseline) * 100

compute_eigenvalue_correlation():
    pre_eig = cat([exp(-exp(a.float())).flatten() for a in baseline]).numpy()
    post_eig = cat([exp(-exp(a.float())).flatten() for a in post]).numpy()
    return float(pearsonr(pre_eig, post_eig)[0])

compute_a_log_max_diff():
    return max(abs(post-pre).max().item() for pre,post in zip(baseline, post_a_logs))
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | compute_delta_h_spec + compute_a_log_max_diff | H_spec via H-M1 formula; element-wise max diff |
| L-6-2 | compute_eigenvalue_correlation + validate() | pearsonr on discrete eigenvalues; full dict |

---

## Subtask Budget Summary

| Task | Budget | Used |
|------|--------|------|
| A-3 LoRAAdapter | 2 | 2 |
| A-5 Training loop | 2 | 2 |
| A-6 EigenvaluePreservationValidator | 2 | 2 |
| **Total** | **6** | **6** |
