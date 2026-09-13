"""H-C1: Uniqueness and idempotency audit loop."""
import torch
from canonicalize import canonicalize_sign_flip_m2


def self_check_idempotency(W1: torch.Tensor, W2: torch.Tensor) -> None:
    """Assert idempotency on one model before full audit."""
    W1c, W2c, _ = canonicalize_sign_flip_m2(W1, W2)
    W1cc, W2cc, _ = canonicalize_sign_flip_m2(W1c, W2c)
    assert torch.allclose(W1c, W1cc), "Idempotency violated on W1"
    assert torch.allclose(W2c, W2cc), "Idempotency violated on W2"


def run_audit(models):
    """
    Run uniqueness and idempotency audit on all models.
    Returns (results, summary).
    results: list of dicts with {model_idx, degenerate, idempotent, tied_neuron_count}
    summary: {fraction_unique, fraction_idempotent, degenerate_count, n_total}
    """
    results = []
    for i, (W1, W2) in enumerate(models):
        W1c, W2c, is_degenerate = canonicalize_sign_flip_m2(W1, W2)

        # Idempotency check
        W1cc, W2cc, _ = canonicalize_sign_flip_m2(W1c, W2c)
        is_idempotent = (
            torch.allclose(W1c, W1cc, atol=1e-6) and
            torch.allclose(W2c, W2cc, atol=1e-6)
        )

        # Count tied neurons if degenerate
        tied_count = 0
        if is_degenerate:
            from canonicalize import exact_majority_sign
            majority = exact_majority_sign(W1)
            tied_count = int((majority == 0).sum().item())

        results.append({
            "model_idx": i,
            "degenerate": is_degenerate,
            "idempotent": is_idempotent,
            "tied_neuron_count": tied_count,
        })

    n = len(results)
    degenerate_count = sum(r["degenerate"] for r in results)
    idempotent_count = sum(r["idempotent"] for r in results)
    summary = {
        "n_total": n,
        "degenerate_count": degenerate_count,
        "idempotent_count": idempotent_count,
        "fraction_unique": (n - degenerate_count) / n,
        "fraction_idempotent": idempotent_count / n,
    }
    return results, summary


def compute_degeneracy_stats(results):
    """Characterize degenerate cases. Returns empty dict if none."""
    degenerate = [r for r in results if r["degenerate"]]
    if not degenerate:
        return {}
    tied_counts = [r["tied_neuron_count"] for r in degenerate]
    return {
        "mean_tied_neurons_per_degenerate_model": float(sum(tied_counts) / len(tied_counts)),
        "max_tied_neurons": int(max(tied_counts)),
        "degenerate_indices": [r["model_idx"] for r in degenerate],
        "degenerate_count": len(degenerate),
    }


def weight_stats_tied_neurons(models, degenerate_indices):
    """Weight L1-norm and std for tied neurons in degenerate models."""
    from canonicalize import exact_majority_sign
    l1_norms = []
    weight_stds = []
    for idx in degenerate_indices:
        W1, _ = models[idx]
        majority = exact_majority_sign(W1)
        tied_mask = (majority == 0)
        if tied_mask.any():
            tied_rows = W1[tied_mask]
            l1_norms.append(tied_rows.abs().mean().item())
            weight_stds.append(tied_rows.std().item())
    if not l1_norms:
        return {}
    return {
        "mean_l1_norm_tied": float(sum(l1_norms) / len(l1_norms)),
        "std_l1_norm_tied": float(sum((x - sum(l1_norms)/len(l1_norms))**2 for x in l1_norms)**0.5),
        "mean_weight_std_tied": float(sum(weight_stds) / len(weight_stds)),
    }
