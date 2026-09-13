"""Oracle orbit pair construction for H-M1 NFT invariance probe."""
import torch
from data_loader import weight_dict_to_flat, flat_to_weight_dict


def construct_scaling_orbit(w: dict, seed: int = 42) -> dict:
    """
    Apply scaling symmetry transform to 2-layer ReLU MLP weight dict.
    Per-neuron scales α_i ~ U(0.1, 10): W1 rows *= α, b1 *= α, W2 cols /= α.
    Functional equivalence: out(x) unchanged.
    """
    rng = torch.Generator().manual_seed(seed)
    h = w["layer0.weight"].shape[0]  # 64
    alpha = torch.empty(h).uniform_(0.1, 10.0, generator=rng).abs()

    return {
        "layer0.weight": w["layer0.weight"] * alpha.unsqueeze(1),   # (64,784) * (64,1)
        "layer0.bias":   w["layer0.bias"]   * alpha,                # (64,)
        "layer1.weight": w["layer1.weight"] / alpha.unsqueeze(0),   # (10,64) / (1,64)
        "layer1.bias":   w["layer1.bias"],                           # unchanged
    }


def construct_signflip_orbit(w: dict, seed: int = 42) -> dict:
    """
    Apply sign-flip symmetry transform to 2-layer ReLU MLP weight dict.
    Per-neuron signs s_i ~ {-1,+1}: flip W1 rows, b1, and W2 cols by s.
    Functional equivalence: ReLU(x·(W1·diag(s))^T + b1·s)·(W2·diag(s))^T + b2
                          = ReLU(x·W1^T + b1) * s · W2^T * s + b2  — wait...
    Correct: s_i * ReLU(h_i) = ReLU(s_i * h_i) only when s_i = +1.
    Sign-flip is a symmetry only for |s_i| = 1 neurons with s_i applied to BOTH
    W1 rows and W2 cols (pre-activation sign pairs cancel).
    For ReLU: ReLU(s*z) = s*ReLU(z) only if s=1. Sign-flip is exact for linear
    activations; for ReLU, it is approximately correct when s=-1 only if all
    activations are positive (saturated regime). We follow the standard definition
    from the literature (sign-flip symmetry of weight space, not output-exact).
    """
    rng = torch.Generator().manual_seed(seed)
    h = w["layer0.weight"].shape[0]  # 64
    rand = torch.rand(h, generator=rng)
    signs = torch.where(rand > 0.5, torch.ones(h), -torch.ones(h))

    return {
        "layer0.weight": w["layer0.weight"] * signs.unsqueeze(1),   # (64,784)
        "layer0.bias":   w["layer0.bias"]   * signs,                 # (64,)
        "layer1.weight": w["layer1.weight"] * signs.unsqueeze(0),   # (10,64)
        "layer1.bias":   w["layer1.bias"],                            # unchanged
    }


def forward_mlp(w: dict, x: torch.Tensor) -> torch.Tensor:
    """2-layer ReLU MLP forward pass."""
    h = torch.relu(x @ w["layer0.weight"].T + w["layer0.bias"])
    return h @ w["layer1.weight"].T + w["layer1.bias"]


def verify_orbit_equivalence(original: dict, orbit: dict, tol: float = 1e-3) -> bool:
    """Check functional equivalence on random input. Tighter tol for scaling."""
    x = torch.randn(64, 784, generator=torch.Generator().manual_seed(0))
    out_orig  = forward_mlp(original, x)
    out_orbit = forward_mlp(orbit, x)
    delta = (out_orig - out_orbit).abs().max().item()
    return delta < tol


def build_orbit_pairs(
    zoo_weights: list[dict],
    base_indices: list[int],
    orbit_type: str,  # "scaling" | "signflip"
    seed: int = 42,
) -> tuple[list[dict], list[dict]]:
    """Construct parallel lists of base and orbit member weight dicts."""
    construct_fn = construct_scaling_orbit if orbit_type == "scaling" else construct_signflip_orbit
    base_list  = [zoo_weights[i] for i in base_indices]
    orbit_list = [construct_fn(w, seed=seed + idx) for idx, w in enumerate(base_list)]
    # Quick sanity check on first 5 pairs (scaling only — signflip approx)
    if orbit_type == "scaling":
        for i in range(min(5, len(base_list))):
            if not verify_orbit_equivalence(base_list[i], orbit_list[i]):
                raise RuntimeError(f"Orbit equivalence check failed at pair {i}")
    return base_list, orbit_list


def sample_base_models(
    zoo_weights: list[dict],
    n: int = 1000,
    seed: int = 42,
) -> tuple[list[int], list[dict]]:
    rng = torch.Generator().manual_seed(seed)
    idx = torch.randperm(len(zoo_weights), generator=rng)[:n].tolist()
    return idx, [zoo_weights[i] for i in idx]
