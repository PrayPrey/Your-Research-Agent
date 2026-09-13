"""Cosine similarity computation and cross-orbit pair sampling for H-M1."""
import torch
import torch.nn.functional as F


def compute_accuracy_deciles(zoo_properties: torch.Tensor) -> torch.Tensor:
    """Bucket test_accuracy into 10 deciles. Returns (N,) ∈ {0,...,9}."""
    acc = zoo_properties[:, 0]
    boundaries = torch.quantile(acc, torch.linspace(0, 1, 11, device=acc.device)[1:-1])
    return torch.bucketize(acc, boundaries)


def build_cross_orbit_pairs(
    zoo_weights: list[dict],
    zoo_properties: torch.Tensor,
    base_indices: list[int],
    seed: int = 42,
) -> tuple[list[dict], list[int]]:
    """For each base[i], sample j ≠ i from same test_accuracy decile."""
    rng = torch.Generator().manual_seed(seed + 999)
    decile_labels = compute_accuracy_deciles(zoo_properties)
    cross_weights = []
    cross_indices = []
    for i in base_indices:
        target = decile_labels[i].item()
        same_decile = (decile_labels == target).nonzero(as_tuple=True)[0]
        candidates  = same_decile[same_decile != i]
        if len(candidates) == 0:
            # fallback: use any other model
            candidates = torch.tensor([k for k in range(len(zoo_weights)) if k != i])
        k = torch.randint(len(candidates), (1,), generator=rng).item()
        j = candidates[k].item()
        cross_indices.append(j)
        cross_weights.append(zoo_weights[j])
    return cross_weights, cross_indices


def compute_similarity_vectors(
    emb_base:  torch.Tensor,
    emb_orbit: torch.Tensor,
    emb_cross: torch.Tensor,
) -> dict:
    """Pairwise cosine similarities. Returns dict of (N,) tensors."""
    bn = F.normalize(emb_base,  dim=-1, eps=1e-8)
    on = F.normalize(emb_orbit, dim=-1, eps=1e-8)
    cn = F.normalize(emb_cross, dim=-1, eps=1e-8)
    within_sim = (bn * on).sum(dim=-1)
    cross_sim  = (bn * cn).sum(dim=-1)
    gap        = cross_sim - within_sim
    return {"within_sim": within_sim, "cross_sim": cross_sim, "gap": gap}


def probe_orbit_invariance(
    nft_encoder,
    zoo_weights: list[dict],
    zoo_properties: torch.Tensor,
    orbit_type: str,
    n_pairs: int = 1000,
    seed: int = 42,
    device: str = "cpu",
) -> dict:
    """Full probe pipeline for one orbit type. Returns similarity tensors."""
    from orbit_construction import build_orbit_pairs, sample_base_models
    from nft_encoder import extract_embeddings

    base_idx, _ = sample_base_models(zoo_weights, n=n_pairs, seed=seed)
    base_list, orbit_list = build_orbit_pairs(zoo_weights, base_idx, orbit_type, seed)
    cross_list, cross_idx = build_cross_orbit_pairs(zoo_weights, zoo_properties, base_idx, seed)

    print(f"[{orbit_type}] Extracting base embeddings ({n_pairs})...")
    emb_base  = extract_embeddings(nft_encoder, base_list,  device=device)
    print(f"[{orbit_type}] Extracting orbit embeddings...")
    emb_orbit = extract_embeddings(nft_encoder, orbit_list, device=device)
    print(f"[{orbit_type}] Extracting cross embeddings...")
    emb_cross = extract_embeddings(nft_encoder, cross_list, device=device)

    sims = compute_similarity_vectors(emb_base, emb_orbit, emb_cross)
    return {
        "orbit_type":    orbit_type,
        "within_sim":    sims["within_sim"],
        "cross_sim":     sims["cross_sim"],
        "gap":           sims["gap"],
        "base_indices":  base_idx,
        "cross_indices": cross_idx,
    }
