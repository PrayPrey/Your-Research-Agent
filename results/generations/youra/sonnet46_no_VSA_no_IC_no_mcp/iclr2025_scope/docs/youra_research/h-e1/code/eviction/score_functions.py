import torch


def score_M1(attn_weights: torch.Tensor, window_size: int = 16) -> torch.Tensor:
    """SnapKV-style: average attention from last window_size query tokens."""
    obs_window = attn_weights[:, :, -window_size:, :]  # (B, H, W, S)
    return obs_window.mean(dim=2)                        # (B, H, S)


def score_M2(attn_weights: torch.Tensor) -> torch.Tensor:
    """H2O-style: cumulative attention summed over all query positions."""
    return attn_weights.sum(dim=2)  # (B, H, S)


def score_M6(seq_len: int, keep_n: int, sink_size: int = 4) -> torch.Tensor:
    """StreamingLLM: attention sinks + sliding window tail. Shape (1, 1, S) — broadcasts over H."""
    scores = torch.zeros(1, 1, seq_len)
    scores[:, :, :sink_size] = 1.0
    recent_count = keep_n - sink_size
    if recent_count > 0:
        recent_start = max(sink_size, seq_len - recent_count)
        scores[:, :, recent_start:] = 1.0
    return scores  # (B=1, H=1, S) — apply_kv_eviction broadcasts to actual H
