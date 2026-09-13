# Logic: H-E1 — Eviction-Aware LoRA Weight Divergence (EXISTENCE PoC)

**Applied**: HuggingFace PEFT LoRA pattern + H2O cumulative-score eviction mask pattern

---

## Executive Summary

Logic design for modules A-3 (H2OEvictionAwareAttention, complexity 12) and A-4 (ModelBuilder, complexity 10). Total budget: 3 subtasks. H2O mask is applied at attention logit level before softmax, training-only, using cumulative-score thresholding to retain top-`kv_budget_ratio` tokens. Wrappers injected per attention layer before LoRA is applied.

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field - no existing codebase to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-3: H2OEvictionAwareAttention [Complexity: 12, Budget: 2 subtasks]

**Applied**: H2O cumulative attention score eviction pattern

### API Signatures

```python
class H2OEvictionAwareAttention(nn.Module):
    def __init__(self, base_attention: nn.Module, kv_budget_ratio: float = 0.5):
        """Wrap base attention with H2O eviction mask, training-only."""
        ...

    def h2o_mask(self, attn_scores: torch.Tensor) -> torch.Tensor:
        """Build binary keep-mask via cumulative score thresholding.

        Args:
            attn_scores: [B, H, T_q, T_k]  (pre-softmax logits)
        Returns:
            mask: [B, H, T_q, T_k]  bool, True = keep, False = evict
        """
        ...

    def forward(
        self,
        hidden_states: torch.Tensor,   # [B, T, D]
        **kwargs
    ) -> tuple:
        """Delegate to base_attention; inject H2O mask when training."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| hidden_states | [B, T, D] | Input to attention layer |
| attn_scores (pre-softmax) | [B, H, T_q, T_k] | Raw QK^T/sqrt(d_k) logits |
| cumsum_scores | [B, H, T_q, T_k] | Cumulative sum along T_k dim |
| mask | [B, H, T_q, T_k] | bool keep-mask |
| masked_logits | [B, H, T_q, T_k] | logits with evicted positions = -inf |

### Subtask L-3-1: h2o_mask() — Cumulative Score Thresholding

**Pseudo-code:**

```
def h2o_mask(attn_scores):  # attn_scores: [B, H, T_q, T_k]
    # 1. Convert logits to probability proxy via softmax (no grad)
    with torch.no_grad():
        scores = F.softmax(attn_scores, dim=-1)          # [B, H, T_q, T_k]

    # 2. Aggregate importance per key position across queries
    #    Sum over T_q to get per-key accumulated weight
    importance = scores.sum(dim=2)                        # [B, H, T_k]

    # 3. Sort keys by importance descending; compute cumsum
    sorted_imp, sorted_idx = importance.sort(dim=-1, descending=True)
    cumsum = sorted_imp.cumsum(dim=-1)                    # [B, H, T_k]
    total   = cumsum[..., -1:].clamp(min=1e-9)

    # 4. Keep tokens where cumulative fraction <= kv_budget_ratio
    keep = (cumsum / total) <= self.kv_budget_ratio       # [B, H, T_k] bool

    # 5. Restore original ordering
    keep_original = torch.zeros_like(keep).scatter_(-1, sorted_idx, keep)

    # 6. Expand to [B, H, T_q, T_k]
    return keep_original.unsqueeze(2).expand_as(attn_scores)
```

### Subtask L-3-2: forward() — Logit-Level Mask Injection

**Implementation notes:**

- Retrieve `attn_scores` by monkey-patching or hooking into the base attention's internal softmax call, OR call base attention's internal compute step if the architecture exposes pre-softmax logits.
- Practical approach for HuggingFace LlamaAttention/MistralAttention: subclass stores a hook on `nn.functional.scaled_dot_product_attention` or overrides `_attn` / `forward` to intercept logits before softmax.
- Simpler PoC approach: call `base_attention` with a custom `attention_mask` override.

**Pseudo-code (PoC approach via mask override):**

```
def forward(self, hidden_states, attention_mask=None, **kwargs):
    if not self.training:
        # Pass-through at inference — no mask injection
        return self.base_attention(hidden_states,
                                   attention_mask=attention_mask, **kwargs)

    # Step 1: dry-run to get attn logits
    #   Use base attention's q/k/v projections to build scores
    q = self.base_attention.q_proj(hidden_states)   # [B, T, H*d_k]
    k = self.base_attention.k_proj(hidden_states)
    # reshape to [B, H, T, d_k] (model-specific)
    scale = q.size(-1) ** -0.5
    attn_scores = torch.matmul(q, k.transpose(-2, -1)) * scale  # [B, H, T, T]

    # Step 2: build eviction mask
    evict_mask = ~self.h2o_mask(attn_scores)        # [B, H, T_q, T_k] True=evict

    # Step 3: build additive attention_mask (-inf at evicted positions)
    additive = attention_mask.clone() if attention_mask is not None \
               else torch.zeros_like(attn_scores)
    additive = additive.masked_fill(evict_mask, float('-inf'))

    # Step 4: delegate full forward with modified mask
    return self.base_attention(hidden_states,
                               attention_mask=additive, **kwargs)
```

**Training-only guard**: `if not self.training: return self.base_attention(...)` ensures zero overhead and identical behavior at inference.

---

## A-4: ModelBuilder [Complexity: 10, Budget: 1 subtask]

**Applied**: HuggingFace PEFT get_peft_model pattern

### API Signatures

```python
def load_base_model(model_name: str) -> AutoModelForCausalLM:
    """Load model in float16; disable cache for training."""
    ...

def inject_h2o_wrappers(model: nn.Module, kv_budget_ratio: float) -> nn.Module:
    """Replace each attention module with H2OEvictionAwareAttention wrapper."""
    ...

def apply_lora(model: nn.Module, lora_cfg: "LoRAConfig") -> PeftModel:
    """Wrap model with PEFT LoRA; return PeftModel."""
    ...

def build_model(cfg: "TrainingConfig") -> PeftModel:
    """Orchestrate load -> inject (if eviction-aware) -> apply_lora."""
    ...
```

### Subtask L-4-1: inject_h2o_wrappers() — Per-Layer Wrapper Injection

**Pseudo-code:**

```
def inject_h2o_wrappers(model, kv_budget_ratio):
    # Identify attention layer class (LlamaAttention or MistralAttention)
    attn_classes = (LlamaAttention, MistralAttention)

    for name, module in model.named_modules():
        if isinstance(module, attn_classes):
            # Build wrapper around existing module
            wrapper = H2OEvictionAwareAttention(
                base_attention=module,
                kv_budget_ratio=kv_budget_ratio
            )
            # Navigate parent and replace child attribute
            parent, child_name = _get_parent(model, name)
            setattr(parent, child_name, wrapper)

    return model

def _get_parent(model, full_name):
    parts = full_name.split('.')
    parent = model
    for part in parts[:-1]:
        parent = getattr(parent, part)
    return parent, parts[-1]
```

**build_model orchestration:**

```
def build_model(cfg):
    model = load_base_model(cfg.model_name)          # fp16, use_cache=False

    if cfg.condition == "eviction-aware":
        model = inject_h2o_wrappers(model, cfg.kv_budget_ratio)
    # baseline: no injection, wrappers absent

    peft_model = apply_lora(model, cfg.lora)         # get_peft_model(...)
    return peft_model
```

**load_base_model notes:**
- `torch_dtype=torch.float16` (bfloat16 if available)
- `use_cache=False` (required for gradient checkpointing compatibility)
- `device_map="auto"` or explicit single-GPU

**apply_lora notes:**
- `LoraConfig(r=cfg.lora.rank, lora_alpha=cfg.lora.alpha, lora_dropout=cfg.lora.dropout, target_modules=cfg.lora.target_modules, task_type="CAUSAL_LM")`
- Injection order MUST be: `inject_h2o_wrappers` BEFORE `get_peft_model` so LoRA wraps the already-wrapped attention

---

## Subtask Summary

| ID | Subtask | Module | Description |
|----|---------|--------|-------------|
| L-3-1 | h2o_mask | A-3 | Cumulative-score thresholding, importance aggregation over T_q, keep top-kv_budget_ratio fraction |
| L-3-2 | forward | A-3 | Training-only mask injection at logit level via additive -inf mask; pass-through at inference |
| L-4-1 | inject_h2o_wrappers | A-4 | named_modules traversal, isinstance check on LlamaAttention/MistralAttention, setattr replacement before LoRA |
