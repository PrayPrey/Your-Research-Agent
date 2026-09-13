# Logic: H-M1

**Type:** MECHANISM
**Scope:** M-3 (SAM sharpness), M-4 (Hessian eigenvalues)

---

## Codebase Analysis

**Project Type:** base_hypothesis
**Status:** API signatures verified from actual H-E1 code (drift found vs h-e1/03_logic.md spec)
**Analyzed Path:** `docs/youra_research/h-e1/code/`
**Relevant Symbols:** `load_baseline_model`, `load_proposed_model`, `MambaWithLoRA`, `load_benchmark`, `format_for_causal_lm`, `LORA_CONFIG_TRANSFORMER`, `LORA_CONFIG_MAMBA`, `BENCHMARKS`

**Drift found:** `load_benchmark(name: str) -> DatasetDict` takes **only `name`**, no split-slicing kwarg. `BENCHMARKS[name]["split"]` = full split (e.g. `"test"`), not `"test[:500]"`. H-M1's `data.py` must call `.select(range(500))` on the returned split after `load_benchmark`, not rely on a sliced split string.

---

## M-3: SAM Sharpness Measurement [Complexity: 9, Budget: 9]

**Applied:** SAM (Sharpness-Aware Minimization) single-step worst-case perturbation (davda54/sam pattern)

### API Signatures

```python
# landscape.py
def compute_grad_norm(model: nn.Module) -> Tensor:
    """L2 norm over all param grads. Returns scalar tensor."""
    ...

def compute_loss(model: nn.Module, dataloader: DataLoader, max_batches: Optional[int] = None) -> Tensor:
    """Avg loss over dataloader (or max_batches). Returns scalar tensor, no grad by default caller controls."""
    ...

def measure_sharpness_sam(
    model: nn.Module,
    dataloader: DataLoader,
    epsilon: float = 0.05,
) -> float:
    """SAM sharpness = L(w+eps*grad/||grad||) - L(w). Restores original params in-place."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B=16, L=512] | from format_for_causal_lm |
| base_loss / perturbed_loss | scalar | mean CE over batch |
| param.grad (per tensor) | same as param | used for perturbation direction |
| grad_norm | scalar | global L2 norm across all params |

### Pseudo-code

```
1. model.eval()
2. original = {n: p.detach().clone() for n, p in model.named_parameters()}
3. base_loss = compute_loss(model, dataloader)              # no_grad
4. model.zero_grad()
5. loss = compute_loss(model, dataloader)                    # grad-enabled
6. loss.backward()
7. grad_norm = compute_grad_norm(model)                      # sqrt(sum ||g||^2)
8. for n, p in model.named_parameters():
       if p.grad is not None: p.data.add_(epsilon * p.grad / (grad_norm + 1e-12))
9. perturbed_loss = compute_loss(model, dataloader)           # no_grad
10. for n, p in model.named_parameters(): p.data.copy_(original[n])
11. return (perturbed_loss - base_loss).item()
```

### Subtasks [3/9 used within this task's 3 pseudo-code subtasks slot]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M3-1 | compute_loss + compute_grad_norm | Batched avg CE loss, global grad norm helper |
| L-M3-2 | measure_sharpness_sam core | Perturb-eval-restore cycle per pseudo-code above |
| L-M3-3 | Param restore safety | try/finally around perturb+restore to avoid corrupted state on exception |

---

## M-4: Hessian Eigenvalue Analysis [Complexity: 10, Budget: 10]

**Applied:** PyHessian power-iteration eigenvalue/trace estimation

### API Signatures

```python
# landscape.py
def compute_hessian_eigenvalues(
    model: nn.Module,
    dataloader: DataLoader,
    top_k: int = 50,
    cuda: bool = True,
) -> dict:
    """
    PyHessian power iteration over dataloader.
    Returns {'eigenvalues': List[float] (len top_k, desc),
             'trace': float, 'spectral_norm': float}
    """
    ...
```

### Tensor Shapes (Hessian computation flow)

| Variable | Shape | Note |
|----------|-------|------|
| input_ids, labels | [B=16, L=512] | one batch or accumulated grad_accum=4 batches |
| hessian_comp | PyHessian `hessian` object | wraps model + criterion + dataloader |
| top_eigenvalues | list[float], len=50 | from `hessian_comp.eigenvalues(top_n=50)` |
| trace_estimate | float | Hutchinson trace estimator, `hessian_comp.trace()` |

### Pseudo-code

```
1. criterion = nn.CrossEntropyLoss()
2. hessian_comp = hessian(model, criterion, dataloader=dataloader, cuda=cuda)
3. top_eigenvalues, top_eigenvectors = hessian_comp.eigenvalues(top_n=top_k)  # power iteration
4. trace = hessian_comp.trace()  # avg of Hutchinson estimates
5. return {'eigenvalues': top_eigenvalues, 'trace': float(np.mean(trace)),
           'spectral_norm': max(top_eigenvalues)}
```

### Subtasks [3/10 used within this task's 3 pseudo-code subtasks slot]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M4-1 | hessian_comp construction | Wrap model+criterion+dataloader, handle MambaWithLoRA custom output (`.loss` attr) vs HF causal LM output |
| L-M4-2 | eigenvalues + trace extraction | Call `.eigenvalues(top_n=50)`, `.trace()`, reduce trace list to scalar mean |
| L-M4-3 | Result dict assembly | Package eigenvalues/trace/spectral_norm, cast tensors to float/list for JSON serialization |

---

## metrics.py (context only, not in scope budget)

```python
def compute_kl_divergence(eig_pre: np.ndarray, eig_post: np.ndarray,
                           num_bins: int = 50, eps: float = 1e-10) -> float:
    """Bin both eigenvalue arrays on shared range, scipy.stats.entropy(hist_pre, hist_post)."""
    ...
```

---

## External Dependencies API (Base Hypothesis H-E1)

**Verified from**: `docs/youra_research/h-e1/code/model.py`, `data.py`, `config.py` (actual implementation)

```python
# From: h-e1/code/model.py
def load_baseline_model(lora_config: dict = None):
    """Llama-2-7B + LoRA(q/k/v/o_proj). Returns PEFT-wrapped nn.Module."""
    ...

def load_proposed_model(lora_config: dict = None):
    """MambaWithLoRA + LoRA(in_proj/out_proj). Returns PEFT-wrapped nn.Module."""
    ...

class MambaWithLoRA(nn.Module):
    def forward(self, input_ids: Tensor, attention_mask: Tensor = None, labels: Tensor = None):
        """input_ids: [B, L] -> Output(loss: Optional[Tensor], logits: [B, L, vocab_size])"""
        ...

# From: h-e1/code/data.py
def load_benchmark(name: str) -> DatasetDict:
    """name in {'gsm8k','nq'}. NOTE: split is FULL split (e.g. 'test'), no built-in slicing."""
    ...

def format_for_causal_lm(dataset, tokenizer, max_length: int = 512):
    """Tokenizes 'question'/'text' field, sets labels=input_ids.copy(). Returns HF Dataset."""
    ...

# From: h-e1/code/config.py
LORA_CONFIG_TRANSFORMER = dict(r=16, lora_alpha=32,
    target_modules=["q_proj","k_proj","v_proj","o_proj"], lora_dropout=0.0)
LORA_CONFIG_MAMBA = dict(r=16, lora_alpha=32,
    target_modules=["in_proj","out_proj"], lora_dropout=0.0)
BENCHMARKS = {"gsm8k": {...split:"test"...}, "nq": {...split:"validation"...}}  # no slicing
```

**Usage note for h-m1/code/data.py**: call `ds = load_benchmark(name)[BENCHMARKS[name]["split"]].select(range(500))` before `format_for_causal_lm`.
