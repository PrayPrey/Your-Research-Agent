"""
Locret CIS score extractor.
Locret stores only retaining head weights (fc1, fc2) in a .bin file.
We load base LLaMA-3.1-8B-instruct and inject retaining heads as forward hooks.
CIS = sigmoid([Q;K;V] @ fc1.T) @ fc2.T  per layer, shape (L, 8)
Reference: huangyuxiang03/Locret paper + hyx21/Locret-llama-3.1-8B-instruct weights
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import hf_hub_download
from typing import Optional, List
from config import ExperimentConfig


class RetainingHead(nn.Module):
    """Per-layer Locret retaining head: CIS = sigmoid([Q;K;V] @ fc1.T) @ fc2.T"""
    def __init__(self, fc1_weight: Tensor, fc2_weight: Tensor):
        super().__init__()
        # fc1: [hidden_r, q_dim+k_dim+v_dim] = [1024, 6144]
        # fc2: [num_kv_heads, hidden_r] = [8, 1024]
        self.fc1 = nn.Linear(fc1_weight.shape[1], fc1_weight.shape[0], bias=False)
        self.fc2 = nn.Linear(fc2_weight.shape[1], fc2_weight.shape[0], bias=False)
        self.fc1.weight.data = fc1_weight.float()
        self.fc2.weight.data = fc2_weight.float()

    def forward(self, q: Tensor, k: Tensor, v: Tensor) -> Tensor:
        """
        q: (1, L, Q_dim=4096)  [after reshape from (1,32,L,128)]
        k: (1, L, K_dim=1024)  [after reshape from (1,8,L,128)]
        v: (1, L, V_dim=1024)
        returns: (1, L, 8) CIS scores
        """
        qkv = torch.cat([q, k, v], dim=-1)  # (1, L, 6144)
        h = F.sigmoid(self.fc1(qkv))         # (1, L, 1024)
        cis = self.fc2(h)                    # (1, L, 8)
        return cis


class LocretExtractor:
    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.model: Optional[object] = None
        self.retaining_heads: List[RetainingHead] = []
        self._hooks = []
        self._cis_buffer: List[Optional[Tensor]] = []

    def load_model(self):
        """Load LLaMA-3.1-8B-instruct + inject Locret retaining heads."""
        print(f"Loading base model: meta-llama/Meta-Llama-3.1-8B-Instruct")
        model = AutoModelForCausalLM.from_pretrained(
            "meta-llama/Meta-Llama-3.1-8B-Instruct",
            torch_dtype=torch.float16,
            device_map="auto",
        )
        model.eval()

        # Download retaining head weights
        print(f"Loading Locret retaining heads from: {self.config.locret_checkpoint}")
        bin_path = hf_hub_download(self.config.locret_checkpoint, "llama-3.1-8B-instruct.bin")
        state_dict = torch.load(bin_path, map_location="cpu")

        # Build retaining heads for each layer
        self.retaining_heads = []
        for layer_idx in range(self.config.num_layers):
            fc1_w = state_dict[f"model.layers.{layer_idx}.self_attn.fc1.weight"]
            fc2_w = state_dict[f"model.layers.{layer_idx}.self_attn.fc2.weight"]
            head = RetainingHead(fc1_w, fc2_w)
            # Move to same device as model
            device = next(model.parameters()).device
            head = head.to(device=device, dtype=torch.float32)
            head.eval()
            self.retaining_heads.append(head)

        self.model = model
        self._cis_buffer = [None] * self.config.num_layers
        print(f"✓ Locret: {self.config.num_layers} retaining heads injected")
        return model

    def extract_cis_scores(
        self,
        model,
        input_ids: Tensor,
        attention_mask: Tensor,
    ) -> List[Tensor]:
        """
        Extract CIS scores per layer by running base model with output_attentions
        and computing CIS from Q, K, V projections via hooks.
        Returns list of 32 tensors, each (num_kv_heads, L) = (8, L).
        """
        self._cis_buffer = [None] * self.config.num_layers

        # Register hooks to capture Q, K, V from each attention layer
        hooks = []
        layer_inputs = {}  # layer_idx -> (q, k, v)

        def make_hook(layer_idx):
            def hook(module, args, kwargs):
                # In newer transformers, hidden_states passed as kwarg
                hidden_states = kwargs.get('hidden_states')
                if hidden_states is None and len(args) > 0:
                    hidden_states = args[0]
                if hidden_states is None:
                    return
                with torch.no_grad():
                    q = module.q_proj(hidden_states)  # (1, L, 4096)
                    k = module.k_proj(hidden_states)  # (1, L, 1024)
                    v = module.v_proj(hidden_states)  # (1, L, 1024)
                    cis = self.retaining_heads[layer_idx](
                        q.float(), k.float(), v.float()
                    )  # (1, L, 8)
                    cis_t = cis.squeeze(0).T.contiguous()  # (8, L)
                    self._cis_buffer[layer_idx] = cis_t.cpu()
            return hook

        for layer_idx in range(self.config.num_layers):
            attn_module = model.model.layers[layer_idx].self_attn
            h = attn_module.register_forward_pre_hook(make_hook(layer_idx), with_kwargs=True)
            hooks.append(h)

        try:
            with torch.no_grad():
                model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                )
        finally:
            for h in hooks:
                h.remove()

        # Validate all layers captured
        seq_len = input_ids.shape[1]
        for layer_idx, cis in enumerate(self._cis_buffer):
            assert cis is not None, f"CIS not captured for layer {layer_idx}"
            assert cis.shape == (self.config.num_kv_heads, seq_len), \
                f"CIS shape mismatch layer {layer_idx}: {cis.shape} vs ({self.config.num_kv_heads}, {seq_len})"

        return list(self._cis_buffer)  # list[32] of (8, L)

    def get_layer_scores(self, all_layer_scores: List[Tensor], layer_idx: int) -> Tensor:
        return all_layer_scores[layer_idx]

    def unload(self) -> None:
        if self.model is not None:
            del self.model
            self.model = None
        self.retaining_heads = []
        self._cis_buffer = []
        torch.cuda.empty_cache()
        print("✓ Locret model unloaded")
