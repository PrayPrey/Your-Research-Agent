"""
H-M1 JointLoRAKVModel: joint LoRA + Locret training with soft/hard KV budget.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional

from config import ExperimentConfig
from locret_heads import LocretHeadCollection, load_locret_heads, freeze_locret_heads
from data_loader import get_num_labels


class JointLoRAKVModel(nn.Module):
    def __init__(
        self,
        base_model,
        locret_heads: LocretHeadCollection,
        num_labels: int,
        config: ExperimentConfig,
    ):
        super().__init__()
        self.base_model = base_model
        self.locret_heads = locret_heads
        self.config = config
        self.num_labels = num_labels
        hidden = config.hidden_size
        self.classifier = nn.Linear(hidden, num_labels)

        # Storage for hook-captured Q/K/V tensors per layer
        self._layer_qkv: Dict[int, Dict[str, torch.Tensor]] = {}
        self._hooks = []
        self._register_hooks()

    def _register_hooks(self):
        for h in self._hooks:
            h.remove()
        self._hooks = []
        # Hook q_proj/k_proj/v_proj outputs directly for reliable gradient flow.
        # LlamaAttention passes args as kwargs so forward_hook inputs tuple is empty;
        # hooking the projection modules avoids that issue entirely.
        llama_layers = self.base_model.base_model.model.model.layers
        for layer_idx, layer in enumerate(llama_layers):
            def make_proj_hook(idx, proj_name):
                def hook(module, inputs, output):
                    if idx not in self._layer_qkv:
                        self._layer_qkv[idx] = {}
                    self._layer_qkv[idx][proj_name] = output  # keep in graph
                return hook
            h_q = layer.self_attn.q_proj.register_forward_hook(make_proj_hook(layer_idx, 'q'))
            h_k = layer.self_attn.k_proj.register_forward_hook(make_proj_hook(layer_idx, 'k'))
            h_v = layer.self_attn.v_proj.register_forward_hook(make_proj_hook(layer_idx, 'v'))
            self._hooks.extend([h_q, h_k, h_v])

    def _compute_token_importance(self) -> List[torch.Tensor]:
        """Compute CIS scores for all layers using hook-captured Q/K/V projections."""
        importance_per_layer = []
        for i in range(self.config.num_layers):
            if i not in self._layer_qkv:
                continue
            qkv = self._layer_qkv[i]
            if 'q' not in qkv or 'k' not in qkv or 'v' not in qkv:
                continue
            q = qkv['q']  # (B, L, hidden_size) — in autograd graph
            k = qkv['k']  # (B, L, kv_dim)
            v = qkv['v']  # (B, L, kv_dim)
            cis = self.locret_heads[i](q, k, v)  # (B, L, 8) — float32
            token_imp = cis.mean(dim=-1)  # (B, L)
            importance_per_layer.append(token_imp)
        return importance_per_layer

    def _apply_soft_budget_mask(
        self,
        hidden_states: torch.Tensor,
        token_importance: torch.Tensor,
        budget_ratio: float,
    ) -> torch.Tensor:
        """Soft differentiable budget masking via straight-through estimator."""
        B, L, H = hidden_states.shape
        k = max(1, int(L * budget_ratio))
        # Straight-through: soft weights for gradient, hard mask for forward
        importance = token_importance.float()  # (B, L)
        # Soft weights (normalized)
        soft_weights = torch.softmax(importance * 10.0, dim=-1)  # (B, L)
        # Hard mask (top-k)
        _, topk_idx = importance.topk(k, dim=-1)
        hard_mask = torch.zeros(B, L, device=hidden_states.device)
        hard_mask.scatter_(1, topk_idx, 1.0)
        # Straight-through: forward uses hard, backward uses soft gradient
        mask = hard_mask + (soft_weights * k - soft_weights.detach() * k)
        # Apply mask
        mask = mask.unsqueeze(-1).to(hidden_states.dtype)  # (B, L, 1)
        return hidden_states * mask

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        labels: Optional[torch.Tensor] = None,
        budget_ratio: float = 0.5,
        training_mode: bool = True,
        collect_cis_samples: bool = False,
    ) -> Dict:
        self._layer_qkv.clear()

        outputs = self.base_model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            output_hidden_states=True,
        )

        hidden_states = outputs.hidden_states[-1]  # (B, L, hidden_size)

        # Compute CIS scores after hooks have captured Q/K/V
        cis_scores = self._compute_token_importance()  # List of (B, L)

        # Budget masking
        tokens_retained_ratio = budget_ratio
        if cis_scores:
            avg_importance = torch.stack(cis_scores, dim=0).mean(dim=0)  # (B, L)
            if training_mode:
                hidden_states = self._apply_soft_budget_mask(
                    hidden_states, avg_importance, budget_ratio
                )
            else:
                # Hard eviction at inference: zero out evicted tokens
                B, L, H = hidden_states.shape
                k = max(1, int(L * budget_ratio))
                _, topk_idx = avg_importance.topk(k, dim=-1)
                hard_mask = torch.zeros(B, L, device=hidden_states.device, dtype=hidden_states.dtype)
                hard_mask.scatter_(1, topk_idx, 1.0)
                hidden_states = hidden_states * hard_mask.unsqueeze(-1)
                tokens_retained_ratio = k / L

        # Classification: use last non-padding token representation
        if attention_mask is not None:
            seq_lengths = attention_mask.sum(dim=-1) - 1
            batch_idx = torch.arange(hidden_states.size(0), device=hidden_states.device)
            pooled = hidden_states[batch_idx, seq_lengths]
        else:
            pooled = hidden_states[:, -1]

        logits = self.classifier(pooled.float())  # (B, num_labels)

        result = {
            "logits": logits,
            "tokens_retained_ratio": tokens_retained_ratio,
        }

        if collect_cis_samples:
            # Grab raw CIS tensors per layer (detached, for shape verification)
            raw_cis = []
            for i in range(self.config.num_layers):
                if i in self._layer_qkv:
                    qkv = self._layer_qkv[i]
                    if 'q' in qkv and 'k' in qkv and 'v' in qkv:
                        with torch.no_grad():
                            cis = self.locret_heads[i](qkv['q'], qkv['k'], qkv['v'])
                        raw_cis.append(cis.detach())
            result["cis_scores"] = raw_cis

        if labels is not None:
            loss = F.cross_entropy(logits, labels)
            result["loss"] = loss

        return result

    def remove_hooks(self):
        for h in self._hooks:
            h.remove()
        self._hooks = []


def build_joint_model(
    config: ExperimentConfig,
    num_labels: int,
    device: str = "cuda",
    freeze_locret: bool = False,
) -> JointLoRAKVModel:
    import torch
    from transformers import AutoModelForCausalLM
    from peft import LoraConfig, get_peft_model, TaskType

    base = AutoModelForCausalLM.from_pretrained(
        config.base_model_name,
        torch_dtype=torch.float16,
        attn_implementation=config.attn_implementation,
        device_map=None,
    ).to(device)

    lora_config = LoraConfig(
        r=config.lora_r,
        lora_alpha=config.lora_alpha,
        lora_dropout=config.lora_dropout,
        target_modules=config.lora_target_modules,
        task_type=TaskType.CAUSAL_LM,
        inference_mode=False,
    )
    base = get_peft_model(base, lora_config)

    locret_heads = load_locret_heads(config, device=device)
    if freeze_locret:
        freeze_locret_heads(locret_heads)

    model = JointLoRAKVModel(base, locret_heads, num_labels, config).to(device)
    return model
