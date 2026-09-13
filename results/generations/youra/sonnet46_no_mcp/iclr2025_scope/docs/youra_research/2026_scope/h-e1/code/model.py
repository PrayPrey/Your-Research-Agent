import torch
import torch.nn as nn
import torch.nn.functional as F
from peft import LoraConfig, get_peft_model, PeftModel
from transformers import AutoModelForCausalLM


class H2OEvictionAwareAttention(nn.Module):
    """Wraps a base attention module with H2O eviction mask injection (training-only)."""

    def __init__(self, base_attention: nn.Module, kv_budget_ratio: float = 0.5):
        super().__init__()
        self.base_attention = base_attention
        self.kv_budget_ratio = kv_budget_ratio

    def h2o_mask(self, attn_scores: torch.Tensor) -> torch.Tensor:
        """Build binary keep-mask via cumulative score thresholding.

        Args:
            attn_scores: [B, H, T_q, T_k] pre-softmax logits
        Returns:
            mask: [B, H, T_q, T_k] bool, True=keep, False=evict
        """
        with torch.no_grad():
            scores = F.softmax(attn_scores, dim=-1)       # [B, H, T_q, T_k]

        importance = scores.sum(dim=2)                     # [B, H, T_k]
        sorted_imp, sorted_idx = importance.sort(dim=-1, descending=True)
        cumsum = sorted_imp.cumsum(dim=-1)                 # [B, H, T_k]
        total = cumsum[..., -1:].clamp(min=1e-9)

        keep = (cumsum / total) <= self.kv_budget_ratio    # [B, H, T_k] bool
        keep_original = torch.zeros_like(keep).scatter_(-1, sorted_idx, keep)
        return keep_original.unsqueeze(2).expand_as(attn_scores)

    def forward(self, hidden_states: torch.Tensor, attention_mask=None, **kwargs) -> tuple:
        if not self.training:
            return self.base_attention(hidden_states, attention_mask=attention_mask, **kwargs)

        # Build attention scores using q/k projections
        q = self.base_attention.q_proj(hidden_states)
        k = self.base_attention.k_proj(hidden_states)

        # Reshape for multi-head: [B, T, H*d] -> [B, H, T, d]
        bsz, tgt_len, _ = hidden_states.shape
        num_heads = self.base_attention.num_heads
        head_dim = q.shape[-1] // num_heads

        q = q.view(bsz, tgt_len, num_heads, head_dim).transpose(1, 2)
        k = k.view(bsz, tgt_len, num_heads, head_dim).transpose(1, 2)

        scale = head_dim ** -0.5
        attn_scores = torch.matmul(q, k.transpose(-2, -1)) * scale  # [B, H, T, T]

        evict_mask = ~self.h2o_mask(attn_scores)  # True=evict

        if attention_mask is not None:
            additive = attention_mask.clone()
            # attention_mask may be [B,1,1,T] or [B,1,T,T] — expand to match
            if additive.dim() < 4:
                additive = additive.unsqueeze(1).unsqueeze(1)
            additive = additive.expand_as(attn_scores).clone()
        else:
            additive = torch.zeros_like(attn_scores)

        additive = additive.masked_fill(evict_mask, float('-inf'))
        return self.base_attention(hidden_states, attention_mask=additive, **kwargs)


def _get_parent(model: nn.Module, full_name: str):
    parts = full_name.split('.')
    parent = model
    for part in parts[:-1]:
        parent = getattr(parent, part)
    return parent, parts[-1]


def load_base_model(model_name: str) -> AutoModelForCausalLM:
    import torch
    dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=dtype,
        use_cache=False,
        device_map="auto",
    )
    return model


def inject_h2o_wrappers(model: nn.Module, kv_budget_ratio: float) -> nn.Module:
    """Replace each attention module with H2OEvictionAwareAttention wrapper."""
    try:
        from transformers.models.llama.modeling_llama import LlamaAttention
    except ImportError:
        LlamaAttention = None
    try:
        from transformers.models.mistral.modeling_mistral import MistralAttention
    except ImportError:
        MistralAttention = None

    attn_classes = tuple(c for c in [LlamaAttention, MistralAttention] if c is not None)
    if not attn_classes:
        raise RuntimeError("Could not import LlamaAttention or MistralAttention")

    replacements = []
    for name, module in model.named_modules():
        if isinstance(module, attn_classes):
            replacements.append(name)

    for name in replacements:
        parent, child_name = _get_parent(model, name)
        base_attn = getattr(parent, child_name)
        wrapper = H2OEvictionAwareAttention(
            base_attention=base_attn,
            kv_budget_ratio=kv_budget_ratio,
        )
        setattr(parent, child_name, wrapper)

    return model


def apply_lora(model: nn.Module, lora_cfg) -> PeftModel:
    peft_config = LoraConfig(
        r=lora_cfg.rank,
        lora_alpha=lora_cfg.alpha,
        lora_dropout=lora_cfg.dropout,
        target_modules=lora_cfg.target_modules,
        task_type="CAUSAL_LM",
        bias="none",
    )
    return get_peft_model(model, peft_config)


def build_model(cfg) -> PeftModel:
    model = load_base_model(cfg.model_name)

    if cfg.condition == "eviction-aware":
        model = inject_h2o_wrappers(model, cfg.kv_budget_ratio)

    peft_model = apply_lora(model, cfg.lora)
    return peft_model
