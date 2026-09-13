# Logic: H-M1 Adversarial BAI Probing

**Type:** MECHANISM (MUST_WORK, AUROC ≥0.7)
**Applied:** pytorch-revgrad GRL + ariahw/rl-rewardhacking linear probe pattern

---

## Codebase Analysis (Serena)

**Project Type:** green-field (H-E1 code is TF-IDF/sklearn text classifiers — no transformer/GRL/probe symbols to reuse)
**Status:** green-field — new API design; only BAI label logic reused from H-E1 at the data level (not code level)
**Analyzed Path:** docs/youra_research/h-e1/code/
**Relevant Symbols:** `AgencyProxyDetector.predict_proba` (H-E1 `model.py`) — reused as a function call to produce proxy scores for BAI label computation, not extended/subclassed.

---

## A-1: Hidden State Extraction [Complexity: 6]

**Applied:** HF `output_hidden_states=True` + last-token pooling

### API Signatures

```python
def extract_hidden_states(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    texts: list[str],
    layer_idx: int = -1,
    batch_size: int = 32,
    device: str = "cuda",
) -> torch.Tensor:
    """Extract pooled hidden states at layer_idx for all texts. Returns [N, H]."""
    ...

def pool_last_token(hidden: Tensor, attention_mask: Tensor) -> Tensor:
    """hidden: [B, S, H], attention_mask: [B, S] -> [B, H] (last non-pad token)."""
    ...

def cache_activations(acts: Tensor, path: str) -> None:
    """torch.save(acts, path)."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, S] | tokenized, padded, left-truncated to max_len |
| attention_mask | [B, S] | 1=real token, 0=pad |
| hidden_states (all layers) | tuple(L+1) of [B, S, H] | H=4096 (Llama/Mistral), 3584 (Qwen2) |
| pooled | [N, H] | one vector per sample, all layers cached |

### Pseudo-code

```
extract_hidden_states(model, tokenizer, texts, layer_idx, batch_size):
    all_pooled = []
    for batch in chunk(texts, batch_size):
        enc = tokenizer(batch, padding=True, truncation=True, max_length=512, return_tensors="pt").to(device)
        with torch.no_grad():
            out = model(**enc, output_hidden_states=True)
        h = out.hidden_states[layer_idx]              # [B, S, H]
        pooled = pool_last_token(h, enc["attention_mask"])  # [B, H]
        all_pooled.append(pooled.cpu())
    return torch.cat(all_pooled, dim=0)                # [N, H]

pool_last_token(hidden, attention_mask):
    last_idx = attention_mask.sum(dim=1) - 1           # [B], index of last real token
    return hidden[torch.arange(hidden.size(0)), last_idx]  # [B, H]
```

### Edge Cases
- Empty string input -> skip sample (attention_mask.sum()==0 guard, raise ValueError if any).
- Sequence > max_length -> truncate right side (keep prompt+start of response).
- OOM at batch_size=32 -> fallback batch_size=8, log warning.

---

## A-2: BAI Label Computation [Complexity: 4]

**Applied:** Direct reuse of H-E1 `AgencyProxyDetector.predict_proba` output, aggregated + median split.

### API Signatures

```python
def compute_bai_scores(texts: list[str], proxy_detectors: dict[str, "AgencyProxyDetector"]) -> np.ndarray:
    """Composite BAI = mean of 4 proxy P(label=1) scores. Returns [N] float in [0,1]."""
    ...

def binarize_bai(bai_scores: np.ndarray) -> np.ndarray:
    """Median split -> [N] int labels {0,1}."""
    ...
```

### Pseudo-code

```
compute_bai_scores(texts, proxy_detectors):
    scores = [proxy_detectors[p].predict_proba(texts) for p in PROXY_TYPES]  # 4 x [N]
    return np.mean(np.stack(scores, axis=0), axis=0)   # [N]

binarize_bai(bai_scores):
    thresh = np.median(bai_scores)
    return (bai_scores > thresh).astype(int)            # [N], ~balanced by construction
```

### Edge Cases
- All scores identical (degenerate median) -> fallback to `bai_scores >= 0.5`.

---

## A-3: Gradient Reversal Layer [Complexity: 5]

**Applied:** pytorch-revgrad pattern (identity forward, `-alpha * grad` backward)

### API Signatures

```python
class RevGradFn(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x: Tensor, alpha: Tensor) -> Tensor: ...   # x: [B, H] -> [B, H]
    @staticmethod
    def backward(ctx, grad_output: Tensor) -> tuple[Tensor, None]: ...

class GradientReversalLayer(nn.Module):
    def __init__(self, alpha: float = 0.0):
        """alpha mutable via self.alpha for scheduling."""
        ...
    def forward(self, x: Tensor) -> Tensor: ...   # [B, H] -> [B, H], identity fwd
```

### Pseudo-code

```
RevGradFn.forward(ctx, x, alpha):
    ctx.alpha = alpha
    return x.view_as(x)                # [B, H], identity

RevGradFn.backward(ctx, grad_output):
    return -ctx.alpha * grad_output, None   # reversed + scaled gradient

GradientReversalLayer.forward(x):
    return RevGradFn.apply(x, torch.tensor(self.alpha, device=x.device))
```

### Edge Cases
- alpha=0.0 -> pure identity, zero gradient to upstream (epoch-1 warmup start).
- alpha must be detached scalar tensor (no grad tracking on alpha itself).

---

## A-4: Adversarial Probe Architecture [Complexity: 7]

**Applied:** Two-head linear probe on frozen hidden states (ariahw/rl-rewardhacking `Probe` pattern)

### API Signatures

```python
class AdversarialProber(nn.Module):
    def __init__(self, hidden_dim: int):
        """BAI head (direct) + reward head (behind GRL)."""
        ...

    def forward(self, h: Tensor) -> tuple[Tensor, Tensor]:
        """h: [B, H] -> (bai_logits [B], reward_logits [B])"""
        ...

    def set_alpha(self, alpha: float) -> None:
        """Update GRL alpha in-place for scheduling."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| h | [B, H] | pooled hidden state, frozen (no grad through LLM) |
| bai_logits | [B] | pre-sigmoid |
| reward_logits | [B] | pre-sigmoid, gradient reversed into `h` |

### Pseudo-code

```
class AdversarialProber:
    __init__(hidden_dim):
        self.bai_probe = nn.Linear(hidden_dim, 1)
        self.grl = GradientReversalLayer(alpha=0.0)
        self.reward_probe = nn.Linear(hidden_dim, 1)

    forward(h):                          # h: [B, H]
        bai_logits = self.bai_probe(h).squeeze(-1)          # [B]
        reward_logits = self.reward_probe(self.grl(h)).squeeze(-1)  # [B]
        return bai_logits, reward_logits

    set_alpha(alpha):
        self.grl.alpha = alpha
```

---

## A-5: Joint Training Loop [Complexity: 7]

**Applied:** BCEWithLogitsLoss dual-head, GRL alpha scheduled via DANN formula

### API Signatures

```python
def grl_alpha_schedule(step: int, total_steps_epoch1: int) -> float:
    """DANN schedule: 2/(1+exp(-10*p)) - 1, p=step/total_steps_epoch1, clamped to epoch 1."""
    ...

def train_adversarial_probe(
    prober: AdversarialProber,
    h_train: Tensor,          # [N, H]
    bai_labels: Tensor,       # [N]
    reward_labels: Tensor,    # [N]
    lam: float = 1.0,
    epochs: int = 3,
    batch_size: int = 32,
    lr: float = 1e-4,
) -> AdversarialProber:
    ...
```

### Pseudo-code

```
grl_alpha_schedule(step, total_steps_epoch1):
    if step >= total_steps_epoch1:
        return 1.0
    p = step / total_steps_epoch1
    return 2.0 / (1.0 + exp(-10 * p)) - 1.0     # 0 -> ~1 over epoch 1

train_adversarial_probe(prober, h_train, bai_labels, reward_labels, lam, epochs, batch_size, lr):
    opt = AdamW(prober.parameters(), lr=lr, weight_decay=0.01)
    sched = warmup(100 steps) + cosine_decay
    steps_per_epoch = ceil(N / batch_size)
    global_step = 0
    for epoch in range(epochs):
        for h_b, bai_b, rew_b in batches(h_train, bai_labels, reward_labels, batch_size, shuffle=True):
            alpha = grl_alpha_schedule(global_step, steps_per_epoch)  # only ramps during epoch 0
            prober.set_alpha(alpha)

            bai_logits, reward_logits = prober(h_b)              # [b], [b]
            bai_loss = BCEWithLogitsLoss()(bai_logits, bai_b.float())
            reward_loss = BCEWithLogitsLoss()(reward_logits, rew_b.float())
            loss = bai_loss + lam * reward_loss

            opt.zero_grad(); loss.backward(); opt.step(); sched.step()
            global_step += 1
    return prober
```

### Edge Cases
- `h_train` must be detached (`requires_grad=False`) — LLM stays frozen, only probe params trained.
- Class imbalance in reward_labels (chosen/rejected naturally balanced 1:1 by pair construction) — no reweighting needed.
- lam sweep (e.g. {0.1, 1.0, 10.0}) if default lam=1.0 fails secondary R² gate.

---

## A-6: Evaluation [Complexity: 5]

**Applied:** sklearn `roc_auc_score` / `r2_score` (ariahw/rl-rewardhacking eval pattern)

### API Signatures

```python
def evaluate_bai_auroc(prober: AdversarialProber, h_test: Tensor, bai_labels: Tensor) -> float:
    """Sigmoid(bai_logits) vs bai_labels -> AUROC."""
    ...

def evaluate_reward_r2(reward_probe: nn.Linear, h_test: Tensor, reward_labels: Tensor) -> float:
    """No-GRL reward probe R² baseline, for degradation comparison."""
    ...

def compute_r2_degradation(r2_baseline: float, r2_after_grl: float) -> float:
    """r2_baseline - r2_after_grl."""
    ...
```

### Pseudo-code

```
evaluate_bai_auroc(prober, h_test, bai_labels):
    with torch.no_grad():
        bai_logits, _ = prober(h_test)          # [N_test]
        probs = sigmoid(bai_logits).cpu().numpy()
    return roc_auc_score(bai_labels.cpu().numpy(), probs)

# Two reward probes trained: (a) baseline, no GRL (alpha=0 fixed); (b) after full GRL (alpha=1)
# Both same architecture, R² computed on held-out reward_labels.
compute_r2_degradation(r2_baseline, r2_after_grl):
    return r2_baseline - r2_after_grl            # target < 0.02 (per PRD "degradation <2%")
```

### Gate Logic

```
main_eval():
    bai_auroc = evaluate_bai_auroc(prober, h_test, bai_test_labels)
    r2_base = evaluate_reward_r2(baseline_reward_probe, h_test, reward_test_labels)
    r2_grl = evaluate_reward_r2(prober.reward_probe, h_test, reward_test_labels)
    degradation = compute_r2_degradation(r2_base, r2_grl)
    PASS if bai_auroc >= 0.7 else FAIL             # primary gate (MUST_WORK)
    log degradation < 0.02                          # secondary
```

### Edge Cases
- If `bai_test_labels` all same class in a fold -> AUROC undefined; drop fold, log warning, require ≥2 folds valid.
- Per-layer AUROC (secondary figure): loop A-1 extraction over `layer_idx in range(L)`, repeat A-5/A-6 per layer — reuse same functions, no new logic.

---

## Subtasks [0/0 used]

No subtasks — budget sufficient for direct implementation; all signatures fully specified above.
