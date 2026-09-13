"""Verification functions: identity check, overhead, memory profiling, gate check."""

import torch
from hooks import HiddenStateExtractor


def check_output_identity(outputs_a: list, outputs_b: list) -> tuple:
    """Returns (identity_rate in [0,1], mismatch_indices)."""
    assert len(outputs_a) == len(outputs_b), "Output lists must have same length"
    mismatches = [i for i, (a, b) in enumerate(zip(outputs_a, outputs_b)) if a != b]
    rate = 1.0 - len(mismatches) / len(outputs_a) if outputs_a else 0.0
    return rate, mismatches


def compute_overhead_pct(time_without: float, time_with: float) -> float:
    """(time_with - time_without) / time_without * 100"""
    if time_without == 0:
        return 0.0
    return (time_with - time_without) / time_without * 100


def profile_memory(model, tokenizer, prompt: str, layer_idx: int) -> dict:
    """Profile GPU memory usage with hooks."""
    torch.cuda.reset_peak_memory_stats()

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with HiddenStateExtractor(model, [layer_idx]) as extractor:
        with torch.no_grad():
            _ = model.generate(**inputs, max_new_tokens=32, do_sample=False, pad_token_id=tokenizer.eos_token_id)
        cpu_tensor_size = extractor.hidden_states[layer_idx].numel() * 4 / (1024 * 1024)

    gpu_peak_mb = torch.cuda.max_memory_allocated() / (1024 * 1024)

    return {
        "gpu_peak_mb": gpu_peak_mb,
        "cpu_tensor_mb": cpu_tensor_size
    }


def gate_check(identity_rate: float, overhead_pct: float, cfg) -> bool:
    """Check if gate passes: identity >= 1.0 AND overhead < 10%."""
    return identity_rate >= cfg.identity_gate and overhead_pct < cfg.overhead_gate_pct
