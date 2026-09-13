"""
Linear and linear attention + sliding window classes
"""
from .linear_attention import (
    LolcatsLinearAttention, LinearAttentionState
)

from .linear_window_attention_sw import (
    LolcatsSlidingWindowAttention, LinearAttentionSlidingWindowCache
)

from .linear_window_attention_sw_gla import (
    GLASlidingWindowAttention,
)
