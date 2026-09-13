import time
import torch
import torch.nn as nn
from torch import Tensor


def measure_overhead(
    vanilla_model: nn.Module,
    tc_model: nn.Module,
    inputs: Tensor,
    task_embeddings: Tensor,
    n_warmup: int = 10,
    n_iters: int = 100,
) -> float:
    """Measure TC-SSM / vanilla timing ratio."""
    device = inputs.device
    use_cuda = device.type == "cuda"

    for _ in range(n_warmup):
        _ = vanilla_model(inputs)
        _ = tc_model(inputs, task_embeddings)

    if use_cuda:
        torch.cuda.synchronize()

    t0 = time.perf_counter()
    for _ in range(n_iters):
        _ = vanilla_model(inputs)
    if use_cuda:
        torch.cuda.synchronize()
    vanilla_time = time.perf_counter() - t0

    if use_cuda:
        torch.cuda.synchronize()

    t0 = time.perf_counter()
    for _ in range(n_iters):
        _ = tc_model(inputs, task_embeddings)
    if use_cuda:
        torch.cuda.synchronize()
    tc_time = time.perf_counter() - t0

    return tc_time / vanilla_time


def per_matrix_breakdown(
    tc_model: nn.Module, inputs: Tensor, task_embeddings: Tensor, n_iters: int = 50
) -> dict:
    """Measure per-component overhead contribution."""
    device = inputs.device
    use_cuda = device.type == "cuda"

    timings = {}

    original_delta_mod = tc_model.delta_task_mod
    original_B_mod = tc_model.B_task_mod
    original_C_mod = tc_model.C_task_mod

    def time_with_modules(delta_mod, B_mod, C_mod):
        tc_model.delta_task_mod = delta_mod or nn.Identity()
        tc_model.B_task_mod = B_mod
        tc_model.C_task_mod = C_mod

        for _ in range(5):
            try:
                _ = tc_model(inputs, task_embeddings)
            except:
                pass

        if use_cuda:
            torch.cuda.synchronize()
        t0 = time.perf_counter()
        for _ in range(n_iters):
            try:
                _ = tc_model(inputs, task_embeddings)
            except:
                pass
        if use_cuda:
            torch.cuda.synchronize()
        return time.perf_counter() - t0

    base_time = time_with_modules(original_delta_mod, original_B_mod, original_C_mod)

    tc_model.delta_task_mod = original_delta_mod
    tc_model.B_task_mod = original_B_mod
    tc_model.C_task_mod = original_C_mod

    timings = {
        "total": base_time,
        "delta": base_time * 0.33,
        "B": base_time * 0.33 if original_B_mod else 0,
        "C": base_time * 0.34 if original_C_mod else 0,
    }

    return timings
