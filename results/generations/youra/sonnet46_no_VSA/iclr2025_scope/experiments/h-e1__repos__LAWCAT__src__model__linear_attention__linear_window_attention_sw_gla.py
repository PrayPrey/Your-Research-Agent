"""
Subquadratic attention combining sliding window and linear attentions
- Using "standard" sliding windows
- Didactically computes outputs with n^2 attention weights for now
- Copied + adapted from linear_window_attention_tk.py for single-file reference

For each layer: 
- We first compute (softmax) attention over sliding windows
- We then compute standard linear attention to "fill in" the earlier parts
- We combine to model the entire sequence
"""
from typing import List, Any, Dict, Tuple, Optional, Callable
import math
import copy
import torch
import torch.nn as nn
import torch.nn.functional as F
from einops import rearrange, repeat

from .linear_attention import (
    LolcatsLinearAttention, 
    softmax_attention
)
from src.model.rotary import get_rotary_embeddings, apply_rotary_pos_emb, apply_rotary_pos_emb_phi
from fla.layers.gla import GatedLinearAttention
from fla.models.utils import Cache
from omegaconf import OmegaConf, DictConfig
from fla.modules import FusedRMSNormSwishGate, RMSNorm, ShortConvolution, RotaryEmbedding
from fla.modules.activations import ACT2FN
from fla.ops.gla import chunk_gla, fused_chunk_gla, fused_recurrent_gla
from flash_attn import flash_attn_func, flash_attn_varlen_func


# Copied from transformers.models.mistral.modeling_mistral (llama.modeling_llama at v4.36)
def repeat_kv(hidden_states: torch.Tensor, n_rep: int) -> torch.Tensor:
    """
    This is the equivalent of torch.repeat_interleave(x, dim=1, repeats=n_rep). 
    The hidden states go from: 
       (batch, num_key_value_heads, seqlen, head_dim) to 
       (batch, num_attention_heads, seqlen, head_dim)
    """
    batch, num_key_value_heads, slen, head_dim = hidden_states.shape
    if n_rep == 1:
        return hidden_states
    hidden_states = hidden_states[:, :, None, :, :].expand(
        batch, num_key_value_heads, n_rep, slen, head_dim)
    return hidden_states.reshape(batch, num_key_value_heads * n_rep, slen, head_dim)

class MyIdentity(nn.Module):
    def forward(self, x, **kwargs):
        return x, None

class MultiShortConv(nn.Module):
    def __init__(self, hidden_size, kernel_size, activation=None, mid_silu=False):
        super(MultiShortConv, self).__init__()
        self.conv1 = ShortConvolution(hidden_size=hidden_size, kernel_size=kernel_size, activation=activation)
        self.conv2 = ShortConvolution(hidden_size=hidden_size, kernel_size=kernel_size, activation=activation)
        self.mid_act = nn.SiLU() if mid_silu else nn.Identity()

    def forward(self, x, mask, cache, output_final_state, seq_idx):
        x, conv_state_1 = self.conv1(x, mask, cache, output_final_state, seq_idx)
        x = self.mid_act(x)
        x, conv_state_2 = self.conv2(x, mask, cache, output_final_state, seq_idx)
        return x, conv_state_2

def get_masks(window_size: int, q_len: int, k_len: int, 
              device: torch.device) -> tuple[torch.Tensor]:
    """
    Return masks for softmax and linear attention terms
    -> 1 is include, 0 is ignore
    """
    kwargs = {'device': device, 'dtype': int}
    causal_mask = torch.ones((q_len, k_len), **kwargs).tril(k_len - q_len)
    linear_mask = torch.ones((q_len, k_len), **kwargs).tril(k_len - q_len - window_size)
    window_mask = causal_mask - linear_mask
    # Return softmax mask (window), linear attention mask
    # -> shapes broadcast over (b, h, q_len, k_len)
    return window_mask[None, None, ...], linear_mask[None, None, ...]
# ---------------------
# Attention layer class
# ---------------------
class GLASlidingWindowAttention(LolcatsLinearAttention):
    """
    LAWCAT attention combining Conv1d and GLA
    """
    def __init__(self, 
                 feature_map = None,
                 window_size: int = 64, 
                 sink_size: int = 0,
                 decode_window_size: int = None,
                 affine_attention_factors: bool = False,
                 init_window_factor: float = 0,
                 train_window_factor: bool = True,
                 state_grad_enabled: bool = False,

                 mode: str = 'chunk',
                 expand_k: float = 1.0, # 0.5
                 expand_v: float = 1.0,
                 gla_num_heads: int = 32,
                 gla_num_kv_heads: int = 8,
                 gla_feature_map: Optional[str] = "relu",
                 use_short_conv: bool = False,
                 conv_size: int = 4,
                 conv_bias: bool = False,
                 use_output_gate: bool = False, # True for small model
                 gate_fn: str = 'swish',
                 elementwise_affine: Optional[bool] = True,
                 norm_eps: float = 1e-5,
                 gate_logit_normalizer: int = 16,
                 gate_low_rank_dim: int = 16,
                 clamp_min: Optional[float] = None,
                 fuse_norm: bool = True,
                 **kwargs):
        try:
            from utils.global_vars import get_global_args
            model_config = get_global_args()
            self.window_size = model_config.attention.window_size
        except:
            from src.utils.global_vars import get_global_args
            model_config = get_global_args()
            self.window_size = model_config.attention.window_size
        self.sink_size = model_config.attention.sink_size

        self.decode_window_size = (
            decode_window_size if decode_window_size is not None else window_size
        )
        self.window_kwargs = {'dimension': 2, 'size': window_size, 'step': 1}
        # Initialize GLA attention part
        self.feature_map_v = model_config.attention.feature_map_v if hasattr(model_config.attention, 'feature_map_v') else False
        feature_map = model_config.attention.feature_map if hasattr(model_config.attention, 'feature_map') else None
        self.original_attn_type = model_config.model.pretrained_model_name_or_path
        if 'lama' in self.original_attn_type or 'istral' in self.original_attn_type:
            self.apply_rotary_pos_emb_wrapper = apply_rotary_pos_emb
            self.rotary_ndims = None
        elif 'hi' in self.original_attn_type:
            self.apply_rotary_pos_emb_wrapper = apply_rotary_pos_emb_phi

        else:
            raise NotImplementedError(f"Not supported model `{self.original_attn_type}`.")
        
        super().__init__(feature_map=feature_map,apply_rotary_pos_emb_wrapper=self.apply_rotary_pos_emb_wrapper, **kwargs)
        self.la_init = model_config.attention.la_init if hasattr(model_config.attention, 'la_init') else 'idt'
        self.norm_la_kv = model_config.attention.norm_la_kv if hasattr(model_config.attention, 'norm_la_kv') else False
        self.fixed_linear_factors = model_config.attention.fixed_linear_factors if hasattr(model_config.attention, 'fixed_linear_factors') else 1.0
        self.attention_type = kwargs['attention_type']

        self.affine_attention_factors = affine_attention_factors
        device, dtype = self.q_proj.weight.device, self.q_proj.weight.dtype
        if train_window_factor:
            self.window_factors = nn.Parameter(
                init_window_factor * torch.ones(1, self.num_heads, 1, 1, device=device, dtype=dtype))
        else:
            self.register_buffer(
                "window_factors", init_window_factor * torch.ones(1, self.num_heads, 1, 1, device=device, dtype=dtype)
            )
        # Whether we use original flash attention 2 inference (use during attention transfer)
        self.base_inference = False
        self.state_grad_enabled = state_grad_enabled


        # Initialize GLA attention part
        self.mode = mode
        self.expand_k = expand_k
        self.expand_v = expand_v
        self.gla_num_heads = model_config.attention.gla_num_heads if hasattr(model_config.attention, 'gla_num_heads') else self.num_heads
        self.gla_num_kv_heads = model_config.attention.gla_num_kv_heads if hasattr(model_config.attention, 'gla_num_kv_heads') else self.num_key_value_heads
        # self.gla_num_kv_heads = gla_num_kv_heads if gla_num_kv_heads is not None else gla_num_heads
        self.gla_num_kv_groups = self.gla_num_heads // self.gla_num_kv_heads
        assert self.gla_num_kv_groups == self.num_key_value_groups, f"GLA num_kv_groups must be equal to num_key_value_groups of base model of {self.num_key_value_groups}"
        self.feature_map_fn = ACT2FN[gla_feature_map] if gla_feature_map is not None else None

        self.use_short_conv = model_config.attention.use_short_conv if hasattr(model_config.attention, 'use_short_conv') else use_short_conv
        self.share_qk_conv = model_config.attention.share_qk_conv if hasattr(model_config.attention, 'share_qk_conv') else False
        self.qk_activation = model_config.attention.qk_activation if hasattr(model_config.attention, 'qk_activation') else qk_activation
        self.conv_init_coeff = model_config.attention.conv_init_coeff if hasattr(model_config.attention, 'conv_init_coeff') else 0.001
        self.conv_size = model_config.attention.conv_size if hasattr(model_config.attention, 'conv_size') else conv_size
        self.conv_bias = conv_bias
        self.use_output_gate = model_config.attention.use_output_gate if hasattr(model_config.attention, 'use_output_gate') else False

        self.key_dim = int(self.hidden_size * expand_k)
        self.value_dim = int(self.hidden_size * expand_v)
        self.key_dim_per_group = self.key_dim // self.gla_num_kv_groups
        self.value_dim_per_group = self.value_dim // self.gla_num_kv_groups
        self.clamp_min = clamp_min

        assert mode in ['chunk', 'fused_recurrent', 'fused_chunk'], f"Not suppoerted mode `{mode}`."
        assert self.key_dim % self.gla_num_heads == 0, f"key dim must be divisible by num_heads of {gla_num_heads}"
        assert self.value_dim % self.gla_num_heads == 0, f"value dim must be divisible by num_heads of {gla_num_heads}"

        self.head_qk_dim = self.key_dim // self.gla_num_heads
        self.head_v_dim = self.value_dim // self.gla_num_heads

        if self.use_short_conv == 2 or self.use_short_conv == 3:
            # breakpoint()
            self.conv_size = conv_size
            mid_silu = self.use_short_conv == 3
            self.q_conv1d = MultiShortConv(hidden_size=self.key_dim, kernel_size=conv_size, activation='silu' if self.qk_activation == 'silu' else None, mid_silu=mid_silu).to(device)
            self.k_conv1d = copy.deepcopy(self.q_conv1d).to(device)
            self.v_conv1d = MyIdentity().to(device)
        else:
            if self.use_short_conv:
                self.conv_size = conv_size
                self.q_conv1d = ShortConvolution(
                    hidden_size=self.key_dim,
                    kernel_size=conv_size,
                    activation='silu' if self.qk_activation == 'silu' else None
                ).to(device)
                if self.share_qk_conv:
                    self.k_conv1d = self.q_conv1d
                else:
                    self.k_conv1d = ShortConvolution(
                        hidden_size=self.key_dim,
                        kernel_size=conv_size,
                        activation='silu' if self.qk_activation == 'silu' else None
                    ).to(device)
                self.v_conv1d = MyIdentity().to(device)
            else:
                print("Warning: ShortConvolution is not used. ")
                # raise UserWarning(
                #     "ShortConvolution is crucial to the performance. "
                #     "Do not turn it off, i.e., setting `use_short_conv=False` unless you know what you are doing."
                # )

        if self.use_output_gate:
            self.g_proj = nn.Linear(self.hidden_size, self.value_dim, bias=False, dtype=dtype)
            self.g_proj.to(device)
        full_rank_gk = model_config.attention.full_rank_gk if hasattr(model_config.attention, 'full_rank_gk') else False
        if type(full_rank_gk) == int:
            self.gk_proj = nn.Sequential(nn.Linear(self.hidden_size, full_rank_gk, bias=False, dtype=dtype),
                                       nn.Linear(full_rank_gk, self.key_dim_per_group, bias=True, dtype=dtype))
        else:
            if full_rank_gk:
                self.gk_proj = nn.Linear(self.hidden_size, self.key_dim_per_group, bias=True, dtype=dtype) # 4096, 1024
            else:
                self.gk_proj = nn.Sequential(nn.Linear(self.hidden_size, gate_low_rank_dim, bias=False, dtype=dtype),
                                            nn.Linear(gate_low_rank_dim, self.key_dim_per_group, bias=True, dtype=dtype))
        self.gk_proj.to(device)

        if self.norm_la_kv or self.window_size == 0:
            self.g_norm = nn.Identity().to(device)
        else:
            if gate_fn == 'swish' and fuse_norm and use_output_gate:
                self.g_norm_swish_gate = FusedRMSNormSwishGate(self.head_v_dim, elementwise_affine, norm_eps)
                self.fuse_norm_and_gate = True
                self.g_norm_swish_gate.to(device)
            else:
                self.fuse_norm_and_gate = False
                self.g_norm = RMSNorm(hidden_size=self.head_v_dim, elementwise_affine=elementwise_affine, eps=norm_eps)
                self.gate_fn = ACT2FN[gate_fn]
                self.g_norm.to(device)

        self.gate_logit_normalizer = gate_logit_normalizer
        self.max_position_embeddings = model_config.model.max_position_embeddings if hasattr(model_config.model, 'max_position_embeddings') else None

        self.win_attn = self.win_attn_base
        self.output_attentions = False

        self.apply(self._initialize_gla_weights)

    def _initialize_gla_weights(self, module: nn.Module):
        if getattr(module, "_is_hf_initialized", False):
            return
        if isinstance(module, (nn.Linear, nn.Conv1d)):
            if self.la_init == 'xavier':
                nn.init.xavier_uniform_(module.weight, gain=2 ** -2.5)
            elif self.la_init == 'normal':
                nn.init.normal_(module.weight, mean=0.0, std=0.006)
            elif self.la_init == 'mix_inv':
                if isinstance(module, nn.Conv1d):
                    nn.init.xavier_uniform_(module.weight, gain=2 ** -2.5)
                else:
                    nn.init.normal_(module.weight, mean=0.0, std=0.006)
            elif self.la_init == 'idt':
                if isinstance(module, nn.Conv1d):
                    new_weight = torch.ones_like(module.weight)
                    new_weight = self.conv_init_coeff * new_weight
                    new_weight[:, :, -1] = 1.0
                    module.weight = nn.Parameter(new_weight)
                else:
                    nn.init.normal_(module.weight, mean=0.0, std=0.006)
            elif self.la_init == 'default':
                pass
            else:
                raise NotImplementedError
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        module._is_hf_initialized = True

    def _initialize_gla_weights_zero(self, module: nn.Module):
        """
        Initialize weights to identity matrix if no skip connection
        """
        if getattr(module, "_is_hf_initialized", False):
            return
        if isinstance(module, nn.Linear):
            if module.bias is not None:
                nn.init.zeros_(module.bias)
            if module.weight.shape[0] == module.weight.shape[1]:
                nn.init.eye_(module.weight)
            else:
                nn.init.xavier_uniform_(module.weight, gain=2 ** -2.5)
        module._is_hf_initialized = True


    def gla_attn(self, q, k, v, gk, g: Optional[torch.Tensor] = None,
                    attention_mask: Optional[torch.Tensor] = None,
                    position_ids: Optional[torch.LongTensor] = None,
                    use_cache: Optional[bool] = False,
                    past_key_values: Optional[Cache] = None,):  # "legacy" cache approach
        """
        Compute queries, keys, and values
        """        
        # launching the triton kernel for just one token will actually be slower
        q_seq_len = q.shape[1]
        mode = 'fused_recurrent' if q_seq_len <= 64 else self.mode

        if attention_mask is not None:
            assert len(attention_mask.shape) == 2, (
                "Expected attention_mask as a 0-1 matrix with shape [batch_size, seq_len] "
                "for padding purposes (0 indicating padding). "
                "Arbitrary attention masks of shape [batch_size, seq_len, seq_len] are not allowed."
            )
            v = v.mul_(attention_mask[:, -v.shape[-2]:, None])
        last_state = None
        if past_key_values is not None and len(past_key_values) > self.layer_idx and past_key_values[self.layer_idx]['conv_state'] is not None:
            last_state = past_key_values[self.layer_idx]

        conv_state_q, conv_state_k, conv_state_v = None, None, None
        if last_state is not None:
            conv_state_q, conv_state_k, conv_state_v = last_state['conv_state']
        conv_mask = attention_mask[:, -q_seq_len:] if attention_mask is not None else None
        position_ids = None

        k, v, gk = (repeat(x, 'b t (h d) -> b t (h g) d', h=self.gla_num_kv_heads, g=self.gla_num_kv_groups) for x in (k, v, gk))
        k, v = (rearrange(x, 'b t h d -> b t (h d)') for x in (k, v))

        if self.use_short_conv:
            q, conv_state_q = self.q_conv1d(x=q,
                                            mask=conv_mask,
                                            cache=conv_state_q,
                                            output_final_state=use_cache,
                                            seq_idx=position_ids)
            k, conv_state_k = self.k_conv1d(x=k,
                                            mask=conv_mask,
                                            cache=conv_state_k,
                                            output_final_state=use_cache,
                                            seq_idx=position_ids)
            v, conv_state_v = self.v_conv1d(x=v,
                                            mask=conv_mask,
                                            cache=conv_state_v,
                                            output_final_state=use_cache,
                                            seq_idx=position_ids)

        q, k, v = map(lambda x: rearrange(x, 'b t (h d) -> b t h d', h=self.gla_num_heads), (q, k, v))
        f_q, f_k = self.feature_map_q(q.transpose(1,2).contiguous()), self.feature_map_k(k.transpose(1,2).contiguous())
        q, k = f_q.transpose(1,2).contiguous(), f_k.transpose(1,2).contiguous()
        # q, k = self.feature_map_q(q), self.feature_map_k(k)
        gk = F.logsigmoid(gk) / self.gate_logit_normalizer

        if self.clamp_min is not None:
            gk = torch.clamp_min(gk, self.clamp_min)

        recurrent_state = last_state['recurrent_state'] if last_state is not None else None
        ones = torch.ones_like(v[..., :1], dtype=v.dtype, device=v.device)
        v_aug = torch.cat([v, ones], dim=-1)  # (b, l, h, d+1)
        if mode == 'fused_recurrent':
            o, recurrent_state = fused_recurrent_gla(
                q=q,
                k=k,
                v=v_aug,
                gk=gk,
                initial_state=recurrent_state,
                output_final_state=use_cache,
                head_first=False
            )
        elif mode == 'chunk':
            o, recurrent_state = chunk_gla(
                q=q,
                k=k,
                v=v_aug,
                g=gk,
                initial_state=recurrent_state,
                output_final_state=use_cache,
                head_first=False
            ) 
        else:
            raise NotImplementedError(f"Not supported mode `{mode}`.")
          
        if past_key_values is not None:
            past_key_values.update(
                recurrent_state=recurrent_state,
                conv_state=(conv_state_q, conv_state_k, conv_state_v) if self.use_short_conv else None,
                layer_idx=self.layer_idx,
                offset=q_seq_len
            )
        o, o_qk = o[..., :-1], o[..., -1:]
        o, o_qk = map(lambda x: rearrange(x, 'b t h d -> b h t d'), (o, o_qk))
        return o, None, past_key_values, o_qk
    
    def win_attn_base(self, b, l, q, k, v,
                 attention_mask: Optional[torch.Tensor] = None,
                 position_ids: Optional[torch.LongTensor] = None,
                 past_key_value: Optional[Tuple[int, torch.Tensor, torch.Tensor]] = None,):
        # Shape is (batch_size, seq_len, num_heads, head_dim)
        q_seq_len = q.shape[1]
        q = rearrange(q, 'b t (h d) -> b h t d', h=self.num_heads, d=self.head_dim)
        k, v = (rearrange(x, 'b t (h d) -> b h t d', h=self.num_key_value_heads, d=self.head_dim) for x in (k, v))

        cos, sin = self.rotary_emb(v, position_ids)
        q, k = self.apply_rotary_pos_emb_wrapper(q, k, cos, sin, self.rotary_ndims)

        if past_key_value is not None:
            k, v = map(lambda x: rearrange(x, 'b h t d -> b t (h d)'), (k, v))
            updated_k, updated_v = past_key_value.update(
                attn_state=(k.float(), v.float()),
                layer_idx=self.layer_idx,
                offset=0,
                cache_kwargs=dict(window_size=self.window_size)
            )['attn_state']
            if q_seq_len == 1:
                k, v = updated_k, updated_v # for generation, during the prefill stage, do not need to update the key and value
            k, v = map(lambda x: rearrange(x, 'b t (h d) -> b h t d', h=self.gla_num_kv_heads), (k, v))

        k = repeat_kv(k, self.num_key_value_groups)
        v = repeat_kv(v, self.num_key_value_groups)
        y_true = a_true = _y_true = None

        if self.train_attention:
            # 1. Compute "ground-truth" attention output and weights
            with torch.no_grad():
                _y_true = flash_attn_func(q.transpose(1, 2), k.transpose(1, 2), v.transpose(1, 2), causal=True, window_size=(-1, -1))
                _y_true = rearrange(_y_true, 'b l h d -> b l (h d)')
                y_true = self.o_proj(_y_true)
                a_true = None
        else:
            y_true = a_true = _y_true = None

        win_attn = sum_sm = 0.0
        if self.window_size > 0:
            a_sm = torch.einsum('bhmd,bhnd->bhmn', q.float(), k.float()) * (k.shape[-1] ** -0.5)
            if past_key_value is None or q_seq_len > 1:
                mask_window, _ = get_masks(self.window_size, q.shape[-2], k.shape[-2], q.device)
                a_sm = a_sm.masked_fill(~mask_window.bool(), -1e8)

            # torch.softmax(a_sm, dim=-1), but we account for the max when combining
            a_sm   = torch.exp(a_sm - torch.amax(a_sm, dim=-1, keepdim=True))
            sum_sm = a_sm.sum(dim=-1, keepdim=True)
            win_attn = torch.einsum('bhmn,bhnd->bhmd', a_sm, v.float())

        return y_true, a_true, _y_true, win_attn, past_key_value, sum_sm

    def normalized_attn(self, win_attn, gla_attn, win_sum, gla_sum):
        window_factors = F.sigmoid(self.window_factors)
        linear_factors = 1 - window_factors if self.affine_attention_factors else self.fixed_linear_factors
        try:
            win_attn, win_sum = win_attn.float(), win_sum.float()
        except:
            pass
        epsilon = 1e-10 
        # avg_attn = (linear_factors * gla_attn.float())/ (linear_factors * gla_sum.float() + epsilon)
        if self.norm_la_kv:
            avg_attn = (window_factors * win_attn + linear_factors * gla_attn.float()) / (window_factors * win_sum + linear_factors * gla_sum.float() + epsilon)
        else:
            avg_attn = gla_attn
        return avg_attn
    
    def forward(self,
                hidden_states: torch.Tensor,
                attention_mask: Optional[torch.Tensor] = None,
                position_ids: Optional[torch.LongTensor] = None,
                past_key_value: Optional[Cache] = None,
                output_attentions: bool = False,
                use_cache: bool = False,
                cur_steps: Optional[int] = None,
                total_steps: Optional[int] = None,
                **kwargs,
               ) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor]]]:
        """
        Forward pass with the option to compute attention weights multiple ways
        if self.train_attention is True
        -> Consistent with HuggingFace Transformers for easy use with their pretrained models
        """

        b, l, _ = hidden_states.size()

        q = self.q_proj(hidden_states)
        k = self.k_proj(hidden_states)
        v = self.v_proj(hidden_states)
        gk = self.gk_proj(hidden_states)
        g = None

        if self.train_attention:
            y_true, a_true, _y_true, win_attn, past_key_value, win_sum = self.win_attn(b, l, q, k, v, attention_mask, position_ids, past_key_value)
            gla_attn, recurrent_state, past_key_value, gla_sum = self.gla_attn(q, k, v, gk, g, attention_mask, position_ids, use_cache, past_key_value)
            # breakpoint()
            # 2. Compute "predicted" attention outputs
            # compute attn weights under sliding window
            y_pred = self.normalized_attn(win_attn, gla_attn, win_sum, gla_sum).to(q.dtype)
            y_pred = rearrange(y_pred, "b h l d -> b l (h d)")
            attn_weights = ((a_true, a_true), (y_pred, _y_true))
        else:
            attn_weights = None
            _, _, _, win_attn, past_key_value, win_sum = self.win_attn(b, l, q, k, v, attention_mask, position_ids, past_key_value)
            gla_attn, _, past_key_value, gla_sum = self.gla_attn(q, k, v, gk, g, attention_mask, position_ids, use_cache, past_key_value)

            y_true = self.normalized_attn(win_attn, gla_attn, win_sum, gla_sum).to(q.dtype)  
            attn_weights = None       

            y_true = rearrange(y_true, "b h l d -> b l (h d)")
            y_true = self.o_proj(y_true)
        return y_true, attn_weights, past_key_value