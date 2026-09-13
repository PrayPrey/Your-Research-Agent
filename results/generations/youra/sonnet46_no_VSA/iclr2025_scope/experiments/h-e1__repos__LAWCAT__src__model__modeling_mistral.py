# coding=utf-8
# Copyright 2023 Mistral AI and the HuggingFace Inc. team. All rights reserved.
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
Thin wrappers and replacement classes for MistralForCausalLM
"""
from typing import Optional, Tuple, List, Union

import warnings
import torch
import torch.nn as nn
from transformers import MistralModel, MistralForCausalLM
from transformers.modeling_outputs import CausalLMOutputWithPast

from .modeling_llama import LolcatsLlamaModel
from .convert_model import get_attention_cache


# Modified from transformers.models.llama.modeling_llama.LlamaModel
class LolcatsMistralModel(LolcatsLlamaModel, MistralModel):
    """
    Wrapper for Mistral-like autoregressive language model
    """
    def forward(self, *args, **kwargs):
        return super().forward(*args, **kwargs)


class LolcatsMistralForCausalLM(MistralForCausalLM):
    """
    Wrapper for Llama or Mistral-like autoregressive language model
    """
    def __init__(self, config):
        # Adapt config to LlamaConfig
        if getattr(config, 'attention_bias', None) is None:
            config.attention_bias = False
        if getattr(config, 'rope_scaling', None) is None:
            config.rope_scaling = None
        if getattr(config, 'pretraining_tp', None) is None:
            config.pretraining_tp = 1
        if getattr(config, 'pretraining_tp', None) is None:
            config.pretraining_tp = 1
        if getattr(config, 'mlp_bias', None) is None:
            config.mlp_bias = False
        super().__init__(config)
        self.model = LolcatsMistralModel(config)
        self.vocab_size = config.vocab_size
        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)

        # Initialize weights and apply final processing
        self.post_init()