import torch
from models import VanillaMambaWrapper, TaskConditionedMamba
from analysis import measure_overhead, measure_state_variance


def run_rank_ablation(
    ranks: list[int],
    d_model: int,
    d_state: int,
    task_emb_dim: int,
    inputs: torch.Tensor,
    task_embeddings_list: list[torch.Tensor],
    n_iters: int = 50,
) -> dict:
    """Sweep rank values and measure overhead + state variance."""
    device = inputs.device
    results = {}

    vanilla = VanillaMambaWrapper(d_model, d_state).to(device).eval()

    for r in ranks:
        tc_model = TaskConditionedMamba(
            d_model, d_state, task_emb_dim, rank=r, variant="all_matrices"
        ).to(device).eval()

        with torch.no_grad():
            overhead = measure_overhead(
                vanilla, tc_model, inputs, task_embeddings_list[0], n_iters=n_iters
            )
            variance_result = measure_state_variance(tc_model, inputs, task_embeddings_list)

        results[r] = {"overhead": overhead, "state_variance": variance_result}
        print(f"Rank {r}: overhead={overhead:.3f}x, p={variance_result['p_value']:.4f}")

    return results


def run_matrix_ablation(
    variants: list[str],
    d_model: int,
    d_state: int,
    task_emb_dim: int,
    rank: int,
    inputs: torch.Tensor,
    task_embedding: torch.Tensor,
    n_iters: int = 50,
) -> dict:
    """Sweep modulation variants (delta_only vs all_matrices)."""
    device = inputs.device
    results = {}

    vanilla = VanillaMambaWrapper(d_model, d_state).to(device).eval()

    for v in variants:
        tc_model = TaskConditionedMamba(
            d_model, d_state, task_emb_dim, rank=rank, variant=v
        ).to(device).eval()

        with torch.no_grad():
            overhead = measure_overhead(vanilla, tc_model, inputs, task_embedding, n_iters=n_iters)

        results[v] = {"overhead": overhead}
        print(f"Variant {v}: overhead={overhead:.3f}x")

    return results
