# coding=utf-8
# Copyright 2022 EleutherAI and the HuggingFace Inc. team. All rights reserved.
#
# This code is based on EleutherAI's GPT-NeoX library and the GPT-NeoX
# and OPT implementations in this library. It has been modified from its
# original forms to accommodate minor architectural differences compared
# to GPT-NeoX and OPT used by the Meta AI team that trained the model.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Thin wrappers and replacement classes for LlamaForCausalLM
"""
from typing import Optional, Tuple, List, Union

import warnings
import torch
import pickle
import torch.nn as nn
import torch.nn.functional as F

from transformers.models.llama.modeling_llama import (
    LlamaModel, LlamaForCausalLM, LLAMA_INPUTS_DOCSTRING,
)
from transformers.modeling_outputs import BaseModelOutputWithPast, CausalLMOutputWithPast
from transformers.cache_utils import Cache, DynamicCache
from transformers.utils import (
    add_start_docstrings_to_model_forward, logging,
)
from transformers.utils.deprecation import deprecate_kwarg

from .convert_model import get_attention_cache

logger = logging.get_logger(__name__)

# Modified from transformers.models.llama.modeling_llama.LlamaModel (v4.43)
class LolcatsLlamaModel(LlamaModel):
    """
    Wrapper for Llama or Mistral-like base model

    Modified from transformers.models.llama.modeling_llama.LlamaModel
    -> Only difference is using KV state for past_key_values instead of cache
    """
    def __init__(self, *args: any, **kwargs: any):
        super().__init__(*args, **kwargs)
        self.layerwise_cpu = False

    @add_start_docstrings_to_model_forward(LLAMA_INPUTS_DOCSTRING)
    def forward(
        self,
        input_ids: torch.LongTensor = None,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        past_key_values: Optional[Union[Cache, List[torch.FloatTensor]]] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        use_cache: Optional[bool] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
        cache_position: Optional[torch.LongTensor] = None,
        cur_steps: Optional[int] = None,
    ) -> Union[Tuple, BaseModelOutputWithPast]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (
            output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states
        )
        use_cache = use_cache if use_cache is not None else self.config.use_cache
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict

        if (input_ids is None) ^ (inputs_embeds is not None):
            raise ValueError(
                "You cannot specify both input_ids and inputs_embeds at the same time, and must specify either one"
            )

        if self.gradient_checkpointing and self.training and use_cache:
            logger.warning_once(
                "`use_cache=True` is incompatible with gradient checkpointing. Setting `use_cache=False`."
            )
            use_cache = False

        batch_size, seq_length = input_ids.shape

        if inputs_embeds is None:
            inputs_embeds = self.embed_tokens(input_ids)

        return_legacy_cache = False   
        if use_cache:
            if past_key_values is None or isinstance(past_key_values, DynamicCache): # Determine and setup our KV cache or state
                attention_type = getattr(self.layers[0].self_attn, 'attention_type', None)
                past_key_values = get_attention_cache(attention_type)
            else:
                # past_key_values.get_usable_length(seq_length)   
                past_key_values.get_seq_length(seq_length)   
                
        if cache_position is None:
            past_seen_tokens = past_key_values.get_seq_length() if past_key_values is not None else 0
            cache_position = torch.arange(
                past_seen_tokens, past_seen_tokens + inputs_embeds.shape[1], device=inputs_embeds.device
            )
        if position_ids is None:
            position_ids = cache_position.unsqueeze(0)

        # causal_mask = self._update_causal_mask(
        #     attention_mask, inputs_embeds, cache_position, past_key_values, output_attentions
        # )
        causal_mask = None
        hidden_states = inputs_embeds

        # create position embeddings to be shared across the decoder layers
        position_embeddings = self.rotary_emb(hidden_states, position_ids)

        # decoder layers
        all_hidden_states = () if output_hidden_states else None
        all_self_attns = () if output_attentions else None
        next_decoder_cache = None

        for decoder_layer in self.layers:
            if output_hidden_states:
                all_hidden_states += (hidden_states,)

            if self.gradient_checkpointing and self.training:
                layer_outputs = self._gradient_checkpointing_func(
                    decoder_layer.__call__,
                    hidden_states,
                    causal_mask,
                    position_ids,
                    past_key_values,
                    output_attentions,
                    use_cache,
                    cache_position,
                    position_embeddings,
                )
            else:
                layer_outputs = decoder_layer(
                    hidden_states,
                    attention_mask=causal_mask,
                    position_ids=position_ids,
                    past_key_value=past_key_values,
                    output_attentions=output_attentions,
                    use_cache=use_cache,
                    cache_position=cache_position,
                    position_embeddings=position_embeddings,
                )

            hidden_states = layer_outputs[0]

            if use_cache:
                next_decoder_cache = layer_outputs[2 if output_attentions else 1]

            if output_attentions:
                all_self_attns += (layer_outputs[1],)

        hidden_states = self.norm(hidden_states)

        # add hidden states from the last decoder layer
        if output_hidden_states:
            all_hidden_states += (hidden_states,)

        next_cache = next_decoder_cache if use_cache else None
        if return_legacy_cache:
            next_cache = next_cache.to_legacy_cache()

        if not return_dict:
            return tuple(v for v in [hidden_states, next_cache, all_hidden_states, all_self_attns] if v is not None)
        return BaseModelOutputWithPast(
            last_hidden_state=hidden_states,
            past_key_values=next_cache,
            hidden_states=all_hidden_states,
            attentions=all_self_attns,
        )


class LolcatsLlamaForCausalLM(LlamaForCausalLM):
    """
    Wrapper for Llama-like autoregressive language model
    """
    def __init__(self, config):
        # Adapt config to LlamaConfig
        if getattr(config, 'attention_bias', None) is None:
            config.attention_bias = False
        if getattr(config, 'rope_scaling', None) is None:
            config.rope_scaling = None
        if getattr(config, 'pretraining_tp', None) is None:
            config.pretraining_tp = 1
        super().__init__(config)
        self.model = LolcatsLlamaModel(config)
        self.vocab_size = config.vocab_size
        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)

        # Initialize weights and apply final processing
        self.post_init()

    def forward(self, *args: any, labels: Optional[torch.LongTensor] = None, logits_to_keep: Optional[int] = 0, **kwargs: any):
        # decoder outputs consists of (dec_features, layer_state, dec_hidden, dec_attn)
        outputs = self.model(*args, **kwargs)
        hidden_states = outputs[0]
        # if False:  # getattr(self.model.layers[0].self_attn, 'train_attention', False):
        #     logits = None  # MZ 8/25: Sorry, was trying stuff
        # regular training
        if getattr(self.config, 'pretraining_tp', 1) > 1:
            lm_head_slices = self.lm_head.weight.split(self.vocab_size // self.config.pretraining_tp, dim=0)
            logits = [F.linear(hidden_states, lm_head_slices[i]) 
                        for i in range(self.config.pretraining_tp)]
            logits = torch.cat(logits, dim=-1)
        else:
            # if labels is None and not self.training:
            #     # print('logits_to_keep:', logits_to_keep, hidden_states.shape)
            #     logits = self.lm_head(hidden_states if logits_to_keep is None else hidden_states[:, -1:])
            # else:
            logits = self.lm_head(hidden_states)
        logits = logits.float()
        return CausalLMOutputWithPast(
            logits=logits,
            past_key_values=outputs.past_key_values,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )