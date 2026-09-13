import torch
import numpy as np
from scipy import stats
from torch import Tensor


def measure_state_variance(
    tc_model, inputs: Tensor, task_embeddings_list: list[Tensor]
) -> dict:
    """Measure state variance across different task embeddings via ANOVA."""
    if len(task_embeddings_list) < 2:
        raise ValueError("need >=2 task embeddings for ANOVA")

    states = []
    for task_emb in task_embeddings_list:
        with torch.no_grad():
            state = tc_model.get_state(inputs, task_emb)
        states.append(state.flatten().cpu().numpy())

    f_stat, p_value = stats.f_oneway(*states)

    return {
        "state_variances": [float(s.var()) for s in states],
        "f_statistic": float(f_stat),
        "p_value": float(p_value),
        "significant": bool(p_value < 0.05),
    }
